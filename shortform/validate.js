// 저비용 검수 도구 — 가장 싼 검증 수단부터 쓴다 (docs/PRODUCTION_SYSTEM.md §13)
//
//   node validate.js scenes                 장면 ID · 구간 목록 (렌더 없음)
//   node validate.js still <scene-id|초>... 정지 프레임 540x960 (텍스트 · 정적 위치)
//   node validate.js storyboard             키프레임 12장 contact sheet 1장 (구도 · 위계 · 타이포)
//   node validate.js section <scene-id>     해당 장면 ±1박 · 540x960 · 음성 포함 (장면 모션)
//   node validate.js animatic               전체 540x960 · 15fps · 음성 포함 (타이밍 · 리듬 · 사운드)
//   node validate.js final --approved       1080x1920 최종 렌더 = bash make.sh (최종 승인 후에만)
//
//   옵션: --ep episodes/<에피소드> (기본 ep01-inquiry) · --no-audio
//
// 결과는 모두 out/<episode>/validate/ 에만 쓴다 (gitignore). final 결과물(out/<episode>/*)은 건드리지 않는다.
// 화면·타임라인은 engine/template.html, 음악은 engine/music.py 를 그대로 호출하므로 final 과 같은 결과의 저해상도판이다.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { spawn, execSync, spawnSync } = require('child_process');

const argv = process.argv.slice(2);
const opt = k => { const i = argv.indexOf(k); return i < 0 ? null : argv.splice(i, 2)[1]; };
const flag = k => { const i = argv.indexOf(k); if (i < 0) return false; argv.splice(i, 1); return true; };
const epDir = path.resolve(opt('--ep') || 'episodes/ep01-inquiry');
const noAudio = flag('--no-audio'), approved = flag('--approved');
const [cmd, ...rest] = argv;

const cfg = JSON.parse(fs.readFileSync(path.join(epDir, 'config.json'), 'utf8'));
const fps = cfg.fps || 30;
const out = path.resolve('out', cfg.episode, 'validate');
const work = path.join(out, '.work');
const tpl = path.resolve('engine/template.html');
const LOW = { width: 1080, height: 1920, deviceScaleFactor: 0.5 };   // 레이아웃은 1080x1920 그대로, 출력만 540x960

// 장면 ID → 구간. 시각은 복사하지 않고 템플릿 타임라인(T)의 키 이름만 참조한다.
const SCENES = {
  hook: ['hook', 'stop'], stop: ['stop', 'before'], before: ['before', 'chaos'], overload: ['chaos', 'turnMorph'],
  turn: ['turnMorph', 'after'], after: ['after', 'gather'], result: ['gather', 'compare'],
  compare: ['compare', 'core'], core: ['core', 'cta'], cta: ['cta', 'end'],
};
// 스토리보드 키프레임: [id, scene, T 키(배열이면 'key.i'), 박자 오프셋]
const KEYFRAMES = [
  ['hook', 'hook', 'hookLine2', 1], ['stop', 'stop', 'stopHit', 1], ['before', 'before', 'before', 3],
  ['overload', 'overload', 'chaos', 2], ['freeze', 'overload', 'turn', 0.25], ['snap', 'turn', 'snap', 1],
  ['climax', 'turn', 'turnText', 1], ['after', 'after', 'afterWords.2', 1], ['result', 'result', 'result', 1.5],
  ['compare', 'compare', 'cmpAfter', 1.5], ['core', 'core', 'core2', 1.5], ['cta', 'cta', 'cta', 3],
];

const tKey = (T, k) => { const [a, i] = k.split('.'); return i == null ? T[a] : T[a][+i]; };
const sceneAt = (T, t) => Object.keys(SCENES).find(id => t >= T[SCENES[id][0]] && t < T[SCENES[id][1]]) || 'cta';
const hash = (...xs) => { const h = crypto.createHash('sha256'); xs.forEach(x => h.update(x)); return h.digest('hex').slice(0, 16); };
const run = (bin, args, o) => { const r = spawnSync(bin, args, { stdio: 'inherit', ...o }); if (r.status) throw new Error(`${bin} failed`); };
const fmt = s => s.toFixed(2) + 's';

async function openPage(viewport) {
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, deviceScaleFactor: viewport.deviceScaleFactor || 1 });
  page.on('pageerror', e => console.log('PAGEERR', e.message));
  await page.addInitScript(c => { window.CONFIG = c; }, cfg);
  await page.goto('file://' + tpl + '?render=1');
  const T = await page.evaluate(() => window.CUES.T);
  return { browser, page, T };
}

// 실사 배경 프레임 (render.js 와 같은 필터 · 같은 540x960). 설정이 같으면 재사용.
async function withBackgrounds(page, T) {
  const spans = { hook: [T.hook, T.stop], before: [T.before, T.turn], cta: [T.cta, T.end], 'compare.before': [T.compare, T.cmpAfter], 'compare.after': [T.cmpAfter, T.core] }, BG = {};
  for (const key of Object.keys(spans)) {
    const bg = (key.split('.').reduce((o, k) => o && o[k], cfg) || {}).background; if (!bg || !bg.src) continue;
    const dir = path.join(work, 'bg_' + key), len = spans[key][1] - spans[key][0] + 0.2;
    const vf = [`fps=${fps}`, 'scale=540:960:force_original_aspect_ratio=increase', 'crop=540:960',
      `eq=saturation=${bg.saturation ?? 0.6}`, bg.blur ? `gblur=sigma=${bg.blur / 2}` : null].filter(Boolean).join(',');
    const stamp = hash(JSON.stringify([bg, len, vf])), stampFile = path.join(dir, '.stamp');
    if (!fs.existsSync(stampFile) || fs.readFileSync(stampFile, 'utf8') !== stamp) {
      fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
      execSync(`ffmpeg -loglevel error -y -ss ${bg.start || 0} -i "${path.resolve(bg.src)}" -t ${len.toFixed(3)} -vf "${vf}" -q:v 4 "${path.join(dir, '%03d.jpg')}"`);
      fs.writeFileSync(stampFile, stamp);
    }
    BG[key] = { count: fs.readdirSync(dir).filter(f => f.endsWith('.jpg')).length, fps, dim: bg.dim, base: 'file://' + dir + '/' };
  }
  await page.addInitScript(b => { window.BG = b; }, BG);
  await page.goto('file://' + tpl + '?render=1');
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => window.ASSETS_READY);
  return page.evaluate(() => window.CUES);
}

// 음악: engine/music.py 를 작업 폴더에서 그대로 실행 (out/<ep>/music.wav 는 건드리지 않음). cues·config·music.py 가 같으면 재사용.
function music(cues) {
  const cuesJson = JSON.stringify(cues, null, 1), mp = path.resolve('engine/music.py');
  const epOut = path.join(work, 'out', cfg.episode), wav = path.join(epOut, 'music.wav');
  const stamp = hash(cuesJson, fs.readFileSync(path.join(epDir, 'config.json')), fs.readFileSync(mp)), stampFile = wav + '.stamp';
  if (fs.existsSync(stampFile) && fs.readFileSync(stampFile, 'utf8') === stamp) return wav;
  fs.mkdirSync(epOut, { recursive: true }); fs.writeFileSync(path.join(epOut, 'cues.json'), cuesJson);
  run('python3', [mp, epDir], { cwd: work });
  fs.writeFileSync(stampFile, stamp);
  return wav;
}

// 저해상도 프레임을 ffmpeg 로 흘려 mp4 생성. 좌상단에 시각 · 박자 표시.
async function encode(page, T, file, t0, t1, rate, wav) {
  const font = execSync("fc-match -f '%{file}' 'DejaVu Sans Mono'").toString();
  const label = `drawtext=fontfile=${font}:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.55:x=8:y=8:` +
    `text='%{pts\\:hms\\:${t0.toFixed(3)}}  beat %{eif\\:floor((t+${t0.toFixed(3)})/${T.beat})\\:d}'`;
  const args = ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(rate), '-c:v', 'mjpeg', '-i', '-'];
  if (wav) args.push('-ss', t0.toFixed(3), '-t', (t1 - t0).toFixed(3), '-i', wav);
  args.push('-vf', label, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '26', '-preset', 'veryfast');
  if (wav) args.push('-c:a', 'aac', '-b:a', '128k', '-shortest');
  args.push(file);
  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round((t1 - t0) * rate);
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => render(t), t0 + f / rate);
    const buf = await page.screenshot({ type: 'jpeg', quality: 85 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
  return n;
}

const commands = {
  async scenes() {
    const { browser, T } = await openPage(LOW); await browser.close();
    for (const [id, [a, b]] of Object.entries(SCENES)) console.log(id.padEnd(9), fmt(T[a]).padStart(7), '→', fmt(T[b]).padStart(7), `  beat ${(T[a] / T.beat).toFixed(1)}–${(T[b] / T.beat).toFixed(1)}`);
  },

  async still() {
    if (!rest.length) throw new Error('still <scene-id|초> ...');
    const { browser, page, T } = await openPage(LOW); await withBackgrounds(page, T);
    for (const x of rest) {
      const t = SCENES[x] ? (T[SCENES[x][0]] + T[SCENES[x][1]]) / 2 : +x;
      await page.evaluate(t => render(t), t);
      const file = path.join(out, `still_${String(x).replace(/[^\w.-]/g, '')}.png`);
      await page.screenshot({ path: file }); console.log(file, fmt(t));
    }
    await browser.close();
  },

  async storyboard() {
    const { browser, page, T } = await openPage(LOW); await withBackgrounds(page, T);
    const dir = path.join(out, 'storyboard'); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const frames = [];
    for (const [i, [id, scene, key, beats]] of KEYFRAMES.entries()) {
      const t = tKey(T, key) + beats * T.beat, file = `${String(i + 1).padStart(2, '0')}_${id}.png`;
      await page.evaluate(t => render(t), t);
      const buf = await page.screenshot({ path: path.join(dir, file) });
      frames.push({ n: i + 1, id, scene, anchor: key, beat_offset: beats, beat: +(t / T.beat).toFixed(2), t: +t.toFixed(3), file: 'storyboard/' + file, sha256: hash(buf) });
    }
    // contact sheet 1장: 4열 × 3행, 각 칸에 번호 · 장면 ID · 박자 · 시각
    const cells = frames.map(f => `<figure><img src="${f.file}"><figcaption><b>#${String(f.n).padStart(2, '0')} ${f.id}</b><span>${f.scene} · beat ${f.beat} · ${fmt(f.t)}</span></figcaption></figure>`).join('');
    const sheet = await browser.newPage({ viewport: { width: 1480, height: 800 } });
    const sheetHtml = path.join(out, 'storyboard.html');
    fs.writeFileSync(sheetHtml, `<meta charset="utf-8"><style>body{margin:0;background:#111;color:#ddd;font:13px 'DejaVu Sans Mono',monospace;padding:20px}
      h1{font-size:18px;margin:0 0 14px;color:#fff}.g{display:grid;grid-template-columns:repeat(4,350px);gap:14px}
      figure{margin:0}img{width:350px;height:622px;display:block;border:1px solid #333}
      figcaption{padding:6px 2px;display:flex;justify-content:space-between}b{color:#fff}</style>
      <h1>${cfg.episode} · STORYBOARD · ${cfg.bpm || 110} BPM · ${cfg.duration || 25}s · config ${hash(JSON.stringify(cfg))}</h1><div class="g">${cells}</div>`);
    await sheet.goto('file://' + sheetHtml);
    await sheet.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
    await sheet.screenshot({ path: path.join(out, 'storyboard.png'), fullPage: true });
    fs.writeFileSync(path.join(out, 'storyboard.json'), JSON.stringify({ episode: cfg.episode, config_hash: hash(JSON.stringify(cfg)), beat: T.beat, keyframes: frames }, null, 1));
    await browser.close();
    console.log(path.join(out, 'storyboard.png'), `(${frames.length} keyframes)`);
  },

  async section() {
    const id = rest[0]; if (!SCENES[id]) throw new Error(`section <scene-id>: ${Object.keys(SCENES).join(' | ')}`);
    const { browser, page, T } = await openPage(LOW); const cues = await withBackgrounds(page, T);
    const t0 = Math.max(0, T[SCENES[id][0]] - T.beat), t1 = Math.min(T.end, T[SCENES[id][1]] + T.beat);
    const wav = noAudio ? null : music(cues), file = path.join(out, `section_${id}.mp4`);
    const n = await encode(page, T, file, t0, t1, fps, wav);
    await browser.close(); console.log(file, `${fmt(t0)}–${fmt(t1)} · ${n} frames @${fps}fps · 540x960${wav ? ' · audio' : ''}`);
  },

  async animatic() {
    const { browser, page, T } = await openPage(LOW); const cues = await withBackgrounds(page, T);
    const wav = noAudio ? null : music(cues), file = path.join(out, 'animatic.mp4');
    const n = await encode(page, T, file, 0, cfg.duration || T.end, 15, wav);
    await browser.close(); console.log(file, `${n} frames @15fps · 540x960${wav ? ' · audio' : ''}`);
  },

  async final() {
    if (!approved) throw new Error('final 은 최종 승인 후에만 실행합니다: node validate.js final --approved  (= bash make.sh)');
    run('bash', ['make.sh', path.relative(process.cwd(), epDir)]);
  },
};

(async () => {
  if (!commands[cmd]) { console.log(fs.readFileSync(__filename, 'utf8').split('\n').slice(0, 11).join('\n')); process.exit(1); }
  fs.mkdirSync(out, { recursive: true });
  const t = Date.now(); await commands[cmd]();
  console.log(`[${cmd}] ${((Date.now() - t) / 1000).toFixed(1)}s`);
})().catch(e => { console.error(e.message); process.exit(1); });
