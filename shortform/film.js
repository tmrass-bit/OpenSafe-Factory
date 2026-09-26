// 브랜드 필름 렌더러 (음악 없음 · 영상만)
// 사용법: node film.js episodes/ep02-moody-salon [--res 540] [--frames 0,60,120]
//   --res  출력 가로 해상도 (기본 540 = 저해상도 프리뷰, 1080 = 최종)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { spawn, execSync } = require('child_process');
const arg = (k, d) => process.argv.includes(k) ? process.argv[process.argv.indexOf(k) + 1] : d;
const epDir = path.resolve(process.argv[2] || 'episodes/ep02-moody-salon');
const cfg = JSON.parse(fs.readFileSync(path.join(epDir, 'config.json'), 'utf8'));
const W = Number(arg('--res', 540)), H = Math.round(W * 16 / 9), fps = cfg.fps || 30, BEAT = 60 / cfg.bpm;
const out = path.resolve('out', cfg.episode); fs.mkdirSync(out, { recursive: true });
const frames = arg('--frames') && arg('--frames').split(',').map(Number);

// 1) 컷마다 필요한 길이만큼 실사 프레임 추출 (9:16 크롭 · 흑백/웜 그레이드 · 슬로모션)
const GRADE = {
  bw: 'hue=s=0,eq=contrast=1.35:brightness=-0.04',
  warm: 'eq=contrast=1.12:saturation=1.18:gamma_r=1.04:gamma_b=0.95',
};
const FR = {};
cfg.shots.forEach((s, i) => {
  if (!s.clip) return;
  const c = cfg.clips[s.clip], end = (cfg.shots[i + 1] || { b: cfg.beats }).b;
  const len = (end - s.b) * BEAT + 0.1, dir = path.join(out, 'shots', String(i));
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const vf = [s.speed ? `setpts=PTS/${s.speed}` : null, `fps=${fps}`,
    `crop=ih*9/16:ih:(iw-ih*9/16)*${c.x ?? 0.5}:0`, `scale=${W}:${H}`, GRADE[s.grade]].filter(Boolean).join(',');
  execSync(`ffmpeg -loglevel error -y -ss ${s.t || 0} -i "${path.resolve(c.src)}" -t ${len.toFixed(3)} -vf "${vf}" -q:v 3 "${dir}/%03d.jpg"`);
  FR[i] = { count: fs.readdirSync(dir).length, base: 'file://' + dir + '/' };
});

(async () => {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: W / 1080 });
  page.on('pageerror', e => console.log('PAGEERR', e.message));
  await page.addInitScript(([c, f]) => { window.CONFIG = c; window.FRAMES = f; }, [cfg, FR]);
  await page.goto('file://' + path.resolve(cfg.template || 'engine/film.html') + '?render=1');
  await page.evaluate(() => document.fonts.ready);
  const total = Math.round(cfg.beats * BEAT * fps);
  if (frames) {
    for (const f of frames) { await page.evaluate(t => render(t), f / fps); await page.screenshot({ path: path.join(out, `still_${String(f).padStart(4, '0')}.png`) }); }
    await browser.close(); return;
  }
  const file = path.join(out, `${cfg.episode}_${W < 1080 ? 'preview' : 'final'}.mp4`);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', W < 1080 ? '22' : '17', '-preset', 'medium', '-movflags', '+faststart', file], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < total; f++) {
    await page.evaluate(t => render(t), f / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 90 === 0) console.log(`frame ${f}/${total}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  await browser.close(); console.log('완성: ' + path.relative(process.cwd(), file));
})();
