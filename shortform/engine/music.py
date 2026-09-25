"""배경음악 + 효과음 자동 작곡기 (저작권 걱정 없는 100% 코드 합성)
사용법: python3 engine/music.py episodes/ep01-inquiry
- config.json 의 bpm / duration 과, 렌더러가 뽑은 out/<ep>/cues.json (글자 등장·클릭·카드 이동 타이밍)을 읽어
  화면 전환에 박자가 정확히 맞는 음악을 만든다.
"""
import json, sys, os, wave
import numpy as np

ep = sys.argv[1] if len(sys.argv) > 1 else 'episodes/ep01-inquiry'
cfg = json.load(open(os.path.join(ep, 'config.json'), encoding='utf-8'))
out = os.path.join('out', cfg['episode'])
cues = json.load(open(os.path.join(out, 'cues.json')))
SR = 44100
DUR = cfg.get('duration', 25)
BPM = cfg.get('bpm', 120); BEAT = 60 / BPM
TL = dict(stop=1.5, stopHit=1.9, before=2.5, chaos=5.0, turn=7.0, turnMorph=7.3, turnText=8.0,
          after=10.0, gather=14.55, result=15.0, compare=17.0, core=18.5, core2=19.4, cta=21.0)
TL.update(cfg.get('timeline', {}))
N = int(SR * (DUR + 0.5))
rs = np.random.RandomState(7)

dry = np.zeros((N, 2)); wet = np.zeros((N, 2))   # wet → 리버브 버스

def t_(d): return np.arange(int(SR * d)) / SR
def add(buf, t0, sig, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i + len(sig) <= 0: return
    s = sig
    if i < 0: s = s[-i:]; i = 0
    s = s[:N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(s), 0] += s * gain * l * 1.414
    buf[i:i + len(s), 1] += s * gain * r * 1.414
def lp(x, fc):  # 1-pole lowpass
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); z = 0.0
    for i in range(len(x)):
        z = (1 - a) * x[i] + a * z; y[i] = z
    return y
def lp_fast(x, fc):  # 2x cascaded via FFT brickwall-ish soft
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** 4), len(x))
def hp_fast(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X * (1 - 1 / (1 + (f / fc) ** 4)), len(x))
def bp_fast(x, fc, q=1.5):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9
    return np.fft.irfft(X / (1 + (q * (f / fc - fc / f)) ** 2), len(x))
def env(n, a=0.002, d=0.2, curve=1.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d) ** curve
    return e
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, d, det=0.0):
    t = t_(d); s = 0
    for k in (-det, 0, det):
        ph = (f * (1 + k)) * t
        s = s + 2 * (ph - np.floor(ph + 0.5))
    return s / 3

# ---------------- instruments ----------------
def kick(g=1.0):
    t = t_(0.45); f = 48 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5) + 0.25 * np.sin(ph) * np.exp(-t * 40)
    click = hp_fast(rs.randn(len(t)), 3000) * np.exp(-t * 300) * 0.25
    return np.tanh((s + click) * 1.6) * g
def hat(open_=False):
    n = int(SR * (0.25 if open_ else 0.06)); x = hp_fast(rs.randn(n), 7000)
    return x * env(n, 0.0005, 0.08 if open_ else 0.018) * 0.5
def clap():
    n = int(SR * 0.35); x = bp_fast(rs.randn(n), 1500, 1.2); e = np.zeros(n); t = np.arange(n) / SR
    for o in (0, 0.009, 0.018): e += (t >= o) * np.exp(-np.maximum(t - o, 0) / (0.012 if o < 0.018 else 0.12))
    return x * e * 0.55
def snare():
    n = int(SR * 0.22); t = np.arange(n) / SR
    return (bp_fast(rs.randn(n), 2500, 0.8) * np.exp(-t * 22) * 0.5 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.5)
def bass(m, d, cutoff=500):
    s = saw(mtof(m), d, 0.004) + 0.6 * np.sin(2 * np.pi * mtof(m) * t_(d))
    s = lp_fast(s, cutoff); n = len(s)
    e = np.minimum(1, np.arange(n) / (SR * 0.004)) * np.minimum(1, (n - np.arange(n)) / (SR * 0.02))
    return np.tanh(s * e * 1.4) * 0.5
def pluck(m, d=0.35):
    s = saw(mtof(m), d, 0.006); n = len(s)
    s = lp_fast(s, 2600) * env(n, 0.002, 0.12)
    return s * 0.35
def pad(ms, d, bright=1600):
    s = sum(saw(mtof(m), d, 0.01) for m in ms) / len(ms)
    s = lp_fast(s, bright); n = len(s); t = np.arange(n) / SR
    e = np.minimum(1, t / 0.25) * np.minimum(1, (n - np.arange(n)) / (SR * 0.5))
    return s * e * 0.55
def stab(ms, g=1.0):
    d = 0.4; s = sum(saw(mtof(m), d, 0.012) for m in ms) / len(ms); n = len(s)
    return lp_fast(s, 3500) * env(n, 0.001, 0.09) * 0.8 * g
def impact(big=True):
    t = t_(2.2 if big else 1.2); f = 34 + 90 * np.exp(-t * 14)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.2 if big else 4.5))
    nz = lp_fast(rs.randn(len(t)), 5000) * np.exp(-t * (5 if big else 9)) * 0.45
    return np.tanh((sub * 1.3 + nz) * 1.3) * (1.0 if big else 0.6)
def riser(d):
    n = int(SR * d); t = np.arange(n) / SR; x = rs.randn(n)
    out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        fc = 400 + 7000 * (i / n) ** 2
        out[i:i + seg] = bp_fast(x[i:i + seg], fc, 1.0)[:len(out[i:i + seg])]
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.25
    return (out + tone) * (t / d) ** 2 * 0.8
def swish(d=0.2):
    n = int(SR * d); t = np.arange(n) / SR
    x = bp_fast(rs.randn(n), 3000, 0.7); e = np.sin(np.pi * t / d) ** 2
    return x * e * 0.35
def click():
    n = int(SR * 0.03); t = np.arange(n) / SR
    return (hp_fast(rs.randn(n), 2000) * np.exp(-t * 400) * 0.6 + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 300) * 0.4)
def tick():
    n = int(SR * 0.08); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 60) * 0.35 + np.sin(2 * np.pi * 1980 * t) * np.exp(-t * 90) * 0.2
def land():
    n = int(SR * 0.09); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (660 + 300 * np.exp(-t * 60)) * t) * np.exp(-t * 45) * 0.35
def bell(m, d=1.6):
    t = t_(d); f = mtof(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)) * np.exp(-t * 2.2) * 0.25

KICK, HATC, HATO, CLAP, SNR = kick(), hat(), hat(True), clap(), snare()

def silent(t):
    return any(a <= t < b for a, b in cues['silence'])
def drums(a, b, kick_every=1, hats=8, clap_on=True, kg=1.0, hg=0.35):
    t = a
    step = BEAT / (hats / 4) if hats else None
    k = 0
    while t < b - 1e-6:
        beat_idx = round(t / BEAT)
        if not silent(t):
            add(dry, t, KICK, 0.9 * kg)
            if clap_on and beat_idx % 2 == 1: add(dry, t, CLAP, 0.55); add(wet, t, CLAP, 0.25)
        t += BEAT * kick_every
    if hats:
        t = a; i = 0
        while t < b - 1e-6:
            if not silent(t): add(dry, t, HATO if (i % (hats // 2) == hats // 4 and hats >= 8) else HATC, hg * (1 if i % 2 == 0 else 0.6), pan=0.25)
            t += step; i += 1
def bassline(a, b, notes, per=BEAT / 2, cutoff=500, g=0.8):
    t = a; i = 0
    while t < b - 1e-6:
        if not silent(t): add(dry, t, bass(notes[i % len(notes)] if isinstance(notes, list) else notes, per * 0.9, cutoff), g)
        t += per; i += 1

A = 45  # A1
# ---------- HOOK 0 ~ 1.5 : 긴장 비트 ----------
drums(0, TL['stop'], hats=8, clap_on=False)
bassline(0, TL['stop'], A, BEAT / 2, 380)
add(dry, 0, pad([57, 60, 64, 71], TL['stop'] + 0.05, 1200), 0.35)
for h in cues['hits']:
    if h['k'] == 'stab':
        add(dry, h['t'], stab([69, 72, 76, 83]), 0.55); add(wet, h['t'], stab([69, 72, 76, 83]), 0.35)
    elif h['k'] == 'impact':
        add(dry, h['t'], impact(True), 0.95); add(wet, h['t'], impact(True), 0.5)
    elif h['k'] == 'impact2':
        add(dry, h['t'], impact(False), 0.7); add(wet, h['t'], impact(False), 0.4)
    elif h['k'] == 'soft':
        add(dry, h['t'], impact(False), 0.45); add(wet, h['t'], bell(81), 0.5)
for t in cues['ticks']:
    if t < TL['stop']: add(dry, t, tick(), 0.45, pan=rs.uniform(-.6, .6))

# ---------- BEFORE 2.5 ~ 5 : 빠른 16비트 ----------
drums(TL['before'], TL['chaos'], hats=16, clap_on=True, hg=0.3)
bassline(TL['before'], TL['chaos'], [A, A, A + 12, A, A, A + 10, A, A + 7], BEAT / 4, 600, 0.7)
for i, w in enumerate(cues['words'][:5]):
    add(dry, w, stab([69 + i, 72 + i, 76 + i]), 0.5); add(wet, w, stab([69 + i, 72 + i, 76 + i]), 0.25)
for c in cues['clicks']:
    if c < TL['turn']: add(dry, c, click(), 0.55, pan=rs.uniform(-.4, .4))

# ---------- CHAOS 5 ~ 7 : 상승 + 스네어 롤 ----------
drums(TL['chaos'], TL['turn'], hats=16, clap_on=True, hg=0.35)
bassline(TL['chaos'], TL['turn'], [A, A + 1, A, A + 3, A, A + 1, A + 6, A + 5], BEAT / 4, 900, 0.75)
add(dry, TL['chaos'], riser(TL['turn'] - TL['chaos']), 0.55)
t = TL['chaos'] + 1.0; step = BEAT / 2
while t < TL['turn'] - 1e-6:
    add(dry, t, SNR, 0.25 + 0.45 * (t - TL['chaos'] - 1) / 1.0); t += step
    step = max(BEAT / 8, step * 0.82)
for w in cues['words'][5:7]:
    add(dry, w, stab([68, 71, 75, 80], 1.1), 0.55); add(wet, w, stab([68, 71, 75, 80]), 0.3)
# 7.0: 완전 정지 → 7.3~8.0 역방향 스웰 → 8.0 임팩트
add(dry, TL['turnMorph'], riser(TL['turnText'] - TL['turnMorph']), 0.6)
add(wet, TL['turnMorph'], riser(TL['turnText'] - TL['turnMorph']), 0.3)
C_MAJ9 = [48, 55, 59, 62, 64]
add(dry, TL['turnText'], pad([m + 12 for m in C_MAJ9], TL['after'] - TL['turnText'] + 0.2, 2200), 0.55)
add(wet, TL['turnText'], pad([m + 12 for m in C_MAJ9], TL['after'] - TL['turnText'] + 0.2, 2200), 0.4)
add(dry, TL['turnText'], bass(36, TL['after'] - TL['turnText'], 300), 0.7)
add(wet, TL['turnText'], bell(76, 2.0), 0.6)
for k in range(4):
    add(dry, TL['turnText'] + 0.5 + k * BEAT, KICK, 0.35)

# ---------- AFTER / RESULT / COMPARE 10 ~ 18.5 : 깔끔한 그루브 ----------
PROG = [(48, [60, 64, 67, 71]), (43, [59, 62, 67, 74]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]  # Cmaj7 G Am F
bar = 4 * BEAT
t0 = TL['after']
while t0 < TL['core'] - 1e-6:
    k = int(round((t0 - TL['after']) / bar)) % 4
    root, ch = PROG[k]; b = min(t0 + bar, TL['core'])
    drums(t0, b, hats=8, clap_on=True, hg=0.3)
    bassline(t0, b, [root, root, root + 12, root, root, root + 7, root + 12, root], BEAT / 2, 520, 0.7)
    add(dry, t0, pad(ch, b - t0 + 0.1, 1400), 0.22); add(wet, t0, pad(ch, b - t0 + 0.1, 1400), 0.18)
    arp = ch + [ch[1] + 12]
    tt = t0; i = 0
    while tt < b - 1e-6:
        add(dry, tt, pluck(arp[(i * 3) % len(arp)] + 12), 0.28, pan=0.3 * np.sin(i)); add(wet, tt, pluck(arp[(i * 3) % len(arp)] + 12), 0.22)
        tt += BEAT / 4; i += 1
    t0 += bar
for w in cues['whoosh']:
    if w['k'] == 'swish': add(dry, w['t'], swish(w['d']), 0.35, pan=rs.uniform(-.5, .5))
for t in cues['chipLand']: add(dry, t, land(), 0.35, pan=rs.uniform(-.3, .3))
add(dry, TL['gather'], riser(TL['result'] - TL['gather']), 0.25)

# ---------- CORE 18.5 ~ 21 ----------
add(dry, TL['core'], pad([45, 57, 64, 67, 72], TL['core2'] - TL['core'] - 0.3, 1200), 0.35)
add(wet, TL['core'], pad([45, 57, 64, 67, 72], TL['core2'] - TL['core'] - 0.3, 1200), 0.3)
add(dry, TL['core2'], pad([m + 12 for m in C_MAJ9], TL['cta'] - TL['core2'] + 0.2, 2400), 0.5)
add(wet, TL['core2'], pad([m + 12 for m in C_MAJ9], TL['cta'] - TL['core2'] + 0.2, 2400), 0.4)
add(dry, TL['core2'], bass(36, TL['cta'] - TL['core2'], 300), 0.7)
for k in range(3):
    add(dry, TL['core2'] + 0.5 + k * BEAT * 2, KICK, 0.45)

# ---------- CTA 21 ~ 25 ----------
t0 = TL['cta']; ends = DUR - 0.5
for k, (root, ch) in enumerate([PROG[0], PROG[3]]):
    a = t0 + k * 2; b = min(a + 2, ends)
    drums(a, b, hats=8, clap_on=True, kg=0.8, hg=0.25)
    bassline(a, b, root, BEAT / 2, 450, 0.6)
    add(dry, a, pad(ch, b - a + 0.8, 1800), 0.3); add(wet, a, pad(ch, b - a + 0.8, 1800), 0.3)
    tt = a; i = 0
    while tt < b - 1e-6:
        add(dry, tt, pluck(ch[i % 4] + 12), 0.25); add(wet, tt, pluck(ch[i % 4] + 12), 0.2); tt += BEAT / 4; i += 1
add(dry, ends, stab([60, 64, 67, 72], 0.8), 0.5); add(wet, ends, bell(84, 2.0), 0.6)

# ---------- reverb + master ----------
irn = int(SR * 1.6); ti = np.arange(irn) / SR
ir = np.stack([lp_fast(rs.randn(irn), 6000) * np.exp(-ti * 3.2) for _ in range(2)], 1)
ir /= np.sqrt((ir ** 2).sum(0))
L = N + irn; nfft = 1 << (L - 1).bit_length()
rev = np.stack([np.fft.irfft(np.fft.rfft(wet[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[:N] for c in range(2)], 1)
mix = dry + rev * 0.5
# 정지 구간: 완전 무음 (잔향도 끊음)
for a, b in cues['silence']:
    i, j = int(a * SR), int(b * SR)
    mix[i:j] *= 0.0
    fade = int(SR * 0.004); mix[max(i - fade, 0):i] *= np.linspace(1, 0, min(fade, i))[:, None]
mix = mix[:int(SR * DUR)]
fo = int(SR * 0.4); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix = hp_fast(mix[:, 0], 28)[:, None] * [1, 0] + hp_fast(mix[:, 1], 28)[:, None] * [0, 1]
mix /= np.percentile(np.abs(mix), 99.9) + 1e-9
mix = np.tanh(mix * 0.95) * 0.92
pcm = (mix * 32767).astype(np.int16)
with wave.open(os.path.join(out, 'music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('music done', os.path.join(out, 'music.wav'))
