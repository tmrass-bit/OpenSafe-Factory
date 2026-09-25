// 사용법: node render.js episodes/ep01-inquiry [--preview-only] [--frames 0,60,120]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { spawn, execSync } = require('child_process');
const epDir = path.resolve(process.argv[2] || 'episodes/ep01-inquiry');
const cfg = JSON.parse(fs.readFileSync(path.join(epDir, 'config.json'), 'utf8'));
const out = path.resolve('out', cfg.episode); fs.mkdirSync(out, { recursive: true });
// config.template === "minimal" → EP01 엔진과 무관한 별도 template 사용 (engine/template.html 은 손대지 않음)
const tpl = path.resolve(cfg.template === 'minimal' ? 'engine/template_minimal.html' : 'engine/template.html');
const argFrames = process.argv.includes('--frames') ? process.argv[process.argv.indexOf('--frames') + 1].split(',').map(Number) : null;
(async () => {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.log('PAGEERR', e.message)); page.on('console', m => { if (m.type()==='error') console.log('CONSOLE', m.text()); });
  await page.addInitScript(c => { window.CONFIG = c; }, cfg);
  // 1차 로드: 박자 타임라인(T)을 읽어 실사 배경을 각 장면 길이만큼만 추출
  await page.goto('file://' + tpl + '?render=1');
  const T = await page.evaluate(() => window.CUES.T);
  const fps = cfg.fps || 30, BG = {};
  const spans = { hook: [T.hook, T.stop], before: [T.before, T.turn], cta: [T.cta, T.end] };
  for (const key of Object.keys(spans)) {
    const bg = cfg[key] && cfg[key].background; if (!bg || !bg.src) continue;
    const dir = path.join(out, 'bg_' + key); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
    const len = spans[key][1] - spans[key][0] + 0.2;
    // 배경은 얕은 심도로 흐리게 쓰므로 절반 해상도로 추출해 용량을 줄임
    const vf = [`fps=${fps}`, 'scale=540:960:force_original_aspect_ratio=increase', 'crop=540:960',
      `eq=saturation=${bg.saturation ?? 0.6}`, bg.blur ? `gblur=sigma=${bg.blur / 2}` : null].filter(Boolean).join(',');
    execSync(`ffmpeg -loglevel error -y -ss ${bg.start || 0} -i "${path.resolve(bg.src)}" -t ${len.toFixed(3)} -vf "${vf}" -q:v 4 "${path.join(dir, '%03d.jpg')}"`);
    BG[key] = { count: fs.readdirSync(dir).filter(f => f.endsWith('.jpg')).length, fps, dim: bg.dim };
  }
  const bgFor = base => Object.fromEntries(Object.entries(BG).map(([k, v]) => [k, { ...v, base: base + 'bg_' + k + '/' }]));
  // 2차 로드: 배경 프레임을 넘겨주고 로딩 완료까지 대기
  await page.addInitScript(b => { window.BG = b; }, bgFor('file://' + out + '/'));
  await page.goto('file://' + tpl + '?render=1');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.ASSETS_READY);
  const cues = await page.evaluate(() => window.CUES);
  fs.writeFileSync(path.join(out, 'cues.json'), JSON.stringify(cues, null, 1));
  // 미리보기용 HTML (설정 내장)
  const html = fs.readFileSync(tpl, 'utf8').replace('<script>', `<script>window.CONFIG=${JSON.stringify(cfg)};window.BG=${JSON.stringify(bgFor(''))};window.AUDIO_SRC='music.wav';</script>\n<script>`);
  fs.writeFileSync(path.join(out, 'preview.html'), html);
  if (process.argv.includes('--preview-only')) { await browser.close(); return; }
  const dur = cfg.duration || 25;
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
