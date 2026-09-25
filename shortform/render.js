// 사용법: node render.js episodes/ep01-inquiry [--preview-only] [--frames 0,60,120]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { spawn, execSync } = require('child_process');
const epDir = path.resolve(process.argv[2] || 'episodes/ep01-inquiry');
const cfg = JSON.parse(fs.readFileSync(path.join(epDir, 'config.json'), 'utf8'));
const out = path.resolve('out', cfg.episode); fs.mkdirSync(out, { recursive: true });
const tpl = path.resolve('engine/template.html');
const argFrames = process.argv.includes('--frames') ? process.argv[process.argv.indexOf('--frames') + 1].split(',').map(Number) : null;
// hook 실사 배경: 원본 클립에서 hook 구간만큼 프레임 추출 (색감·블러는 config 값으로)
let hookBg = null;
const hb = cfg.hook && cfg.hook.background;
if (hb && hb.src) {
  const fps = cfg.fps || 30, len = ((cfg.timeline && cfg.timeline.stop) || 1.5) + 0.1;
  const dir = path.join(out, 'hook_bg'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
  const vf = [`fps=${fps}`, 'scale=1080:1920:force_original_aspect_ratio=increase', 'crop=1080:1920',
    `eq=saturation=${hb.saturation ?? 0.6}`, hb.blur ? `gblur=sigma=${hb.blur}` : null].filter(Boolean).join(',');
  execSync(`ffmpeg -loglevel error -y -ss ${hb.start || 0} -i "${path.resolve(hb.src)}" -t ${len} -vf "${vf}" -q:v 3 "${path.join(dir, '%03d.jpg')}"`);
  hookBg = { count: fs.readdirSync(dir).filter(f => f.endsWith('.jpg')).length, fps, dim: hb.dim };
}
(async () => {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.log('PAGEERR', e.message)); page.on('console', m => { if (m.type()==='error') console.log('CONSOLE', m.text()); });
  await page.addInitScript(([c, hbg]) => { window.CONFIG = c; window.HOOK_BG = hbg; }, [cfg, hookBg && { ...hookBg, base: 'file://' + path.join(out, 'hook_bg') + '/' }]);
  await page.goto('file://' + tpl + '?render=1');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.ASSETS_READY);
  const cues = await page.evaluate(() => window.CUES);
  fs.writeFileSync(path.join(out, 'cues.json'), JSON.stringify(cues, null, 1));
  // 미리보기용 HTML (설정 내장)
  const html = fs.readFileSync(tpl, 'utf8').replace('<script>', `<script>window.CONFIG=${JSON.stringify(cfg)};window.HOOK_BG=${JSON.stringify(hookBg && { ...hookBg, base: 'hook_bg/' })};window.AUDIO_SRC='music.wav';</script>\n<script>`);
  fs.writeFileSync(path.join(out, 'preview.html'), html);
  if (process.argv.includes('--preview-only')) { await browser.close(); return; }
  const fps = cfg.fps || 30, dur = cfg.duration || 25;
  if (argFrames) {
    for (const f of argFrames) { await page.evaluate(t => render(t), f / fps); await page.screenshot({ path: path.join(out, `still_${String(f).padStart(4, '0')}.png`) }); }
    await browser.close(); return;
  }
  const total = Math.round(fps * dur);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', path.join(out, 'video_noaudio.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => render(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await browser.close(); console.log('video done');
})();
