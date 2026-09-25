"""배경음악 + 효과음 자동 작곡기 (저작권 걱정 없는 100% 코드 합성)
사용법: python3 engine/music.py episodes/ep01-inquiry
- 렌더러가 뽑은 out/<ep>/cues.json 의 박자 타임라인(T)과 화면 이벤트(모듈 등장·스냅·카드 착지 등)를 읽어
  화면 변화 자체가 음악이 되도록 같은 박자 격자 위에 소리를 놓는다.
- 감정 흐름: Tension → Overload → Silence → Precision → Resolution → Calm Control
"""
import json, sys, os, wave
import numpy as np

ep = sys.argv[1] if len(sys.argv) > 1 else 'episodes/ep01-inquiry'
cfg = json.load(open(os.path.join(ep, 'config.json'), encoding='utf-8'))
out = os.path.join('out', cfg['episode'])
cues = json.load(open(os.path.join(out, 'cues.json')))
SR = 44100
DUR = cfg.get('duration', 25)
TL = cues['T']                      # 화면과 같은 타임라인 (템플릿이 박자 단위로 계산)
BEAT = TL['beat']; BPM = 60 / BEAT
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

# ---------------- 전환부 효과음 (모두 음높이가 있는 짧은 소리 — 무작위 효과음 대신) ----------------
def rim():
    n = int(SR * 0.05); t = np.arange(n) / SR
    return (bp_fast(rs.randn(n), 1800, 2.0) * np.exp(-t * 90) * 0.6 + np.sin(2 * np.pi * 820 * t) * np.exp(-t * 120) * 0.35)
def shaker():
    n = int(SR * 0.07); t = np.arange(n) / SR
    return hp_fast(rs.randn(n), 6000) * np.sin(np.pi * t / t[-1]) ** 2 * 0.35
def tonal_hit(m):                   # 모듈 등장: 음높이 있는 짧은 타격
    t = t_(0.5); f = mtof(m)
    body = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 18) + 0.15 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 30)
    tr = hp_fast(rs.randn(len(t)), 2500) * np.exp(-t * 400) * 0.3
    return (body * np.exp(-t * 9) + tr) * 0.5
def snap_sfx():                     # 격자 정렬: 기계적인 '착'
    t = t_(0.12)
    clk = hp_fast(rs.randn(len(t)), 3000) * np.exp(-t * 900)
    thunk = np.sin(2 * np.pi * np.cumsum(90 + 90 * np.exp(-t * 80)) / SR) * np.exp(-t * 45)
    ring = bp_fast(rs.randn(len(t)), 5200, 4) * np.exp(-t * 70) * 0.4
    return (clk * 0.7 + thunk * 0.8 + ring) * 0.6
def mag_click():                    # 조립: 자석처럼 맞물리는 두 번의 클릭
    out_ = np.zeros(int(SR * 0.2))
    for o, g in ((0.0, 0.5), (0.028, 1.0)):
        c = snap_sfx() * g; i = int(o * SR); out_[i:i + len(c)] += c[:len(out_) - i]
    t = np.arange(len(out_)) / SR
    return out_ + np.sin(2 * np.pi * 60 * t) * np.exp(-t * 25) * 0.4
def thud():                         # "아니요." — 작고 단단한 저음 (큰 임팩트는 구조 완성에만)
    t = t_(0.7)
    return (np.sin(2 * np.pi * np.cumsum(55 + 40 * np.exp(-t * 40)) / SR) * np.exp(-t * 7) + hp_fast(rs.randn(len(t)), 2000) * np.exp(-t * 300) * 0.2) * 0.8
def bloom(ms, d=1.4):               # 완성 직후 짧은 쉬머
    t = t_(d); s_ = sum(np.sin(2 * np.pi * mtof(m) * t + k) for k, m in enumerate(ms)) / len(ms)
    return s_ * np.minimum(1, t / 0.012) * np.exp(-t * 3.2) * 0.45
def swell(d, m=36):                 # 분해 구간: 아주 낮은 공기감 (거의 들리지 않게)
    t = t_(d); x = lp_fast(rs.randn(len(t)), 500) * 0.3 + np.sin(2 * np.pi * mtof(m) * t) * 0.5
    return x * (t / d) ** 1.5 * 0.35
RIM, SHK = rim(), shaker()

def beats(a, b, every):
    t = a
    while t < b - 1e-6:
        yield t
        t += every

A = 45  # A1
C_MAJ9 = [48, 55, 59, 62, 64]
# ---------- 1) HOOK : Tension ----------
for i, t in enumerate(beats(0, TL['stop'], BEAT / 2)):
    if i % 2 == 0: add(dry, t, KICK, 0.8)
    add(dry, t, HATC, 0.28 if i % 2 else 0.18, pan=0.2)
bassline(0, TL['stop'], A, BEAT / 2, 380, 0.7)
add(dry, 0, pad([57, 60, 64, 71], TL['stop'] + 0.05, 1200), 0.25)
for h in cues['hits']:
    if h['k'] == 'stab':
        add(dry, h['t'], stab([69, 72, 76, 83]), 0.5); add(wet, h['t'], stab([69, 72, 76, 83]), 0.3)
for t in cues['ticks']:
    if t < TL['stop']: add(dry, t, tick(), 0.35, pan=rs.uniform(-.5, .5))
# ---------- 2) STOP : 스매시 컷 → 무음 → 작은 저음 ----------
for h in cues['hits']:
    if h['k'] == 'thud': add(dry, h['t'], thud(), 0.85); add(wet, h['t'], thud(), 0.25)

# ---------- 3) BEFORE : 미니멀 일렉트로닉 펄스 (드라이 · 촘촘 · 멜로디 최소) ----------
b0, b1 = TL['before'], TL['chaos']
for i, t in enumerate(beats(b0, b1, BEAT / 4)):
    if i % 4 == 0: add(dry, t, KICK, 0.7)
    if i % 8 == 4: add(dry, t, RIM, 0.35)
    add(dry, t, HATC, 0.22 if i % 2 == 0 else 0.1, pan=0.25)
bassline(b0, b1, [A, A, A, A + 12, A, A, A + 7, A], BEAT / 2, 520, 0.6)
for i, w in enumerate(cues['words'][:5]):
    add(dry, w, tonal_hit(69 if i % 2 == 0 else 64), 0.3)
for c in cues['clicks']: add(dry, c, click(), 0.3, pan=rs.uniform(-.3, .3))

# ---------- 4) OVERLOAD : 서브디비전·밀도 증가 + 짧은 라이저 ----------
c0, c1 = TL['chaos'], TL['turn']
for t in beats(c0, c1, BEAT): add(dry, t, KICK, 0.85)
for i, t in enumerate(beats(c0, c1, BEAT / 4)):
    add(dry, t, HATC, 0.25 if i % 2 == 0 else 0.14, pan=0.25); add(dry, t + BEAT / 8, SHK, 0.12, pan=-0.3)
for t in beats(c1 - BEAT, c1, BEAT / 8): add(dry, t, HATC, 0.16, pan=-0.2)      # 마지막 한 박: 32분음표
for i, t in enumerate(beats(c0 + BEAT, c1, BEAT / 2)):
    if i % 2: add(dry, t, RIM, 0.3)
bassline(c0, c1, [A, A, A + 12, A, A + 1, A, A + 12, A + 3], BEAT / 4, 700, 0.65)
roll_step = [(c0 + BEAT, BEAT / 2), (c0 + 2 * BEAT, BEAT / 4), (c1 - 0.75 * BEAT, BEAT / 8)]
for k, (a, st) in enumerate(roll_step):
    b = roll_step[k + 1][0] if k + 1 < len(roll_step) else c1
    for t in beats(a, b, st): add(dry, t, SNR, 0.18 + 0.35 * (t - c0) / (c1 - c0))
add(dry, c1 - 1.5 * BEAT, riser(1.5 * BEAT), 0.5)
for t in cues['ticks']:
    if c0 <= t < c1: add(dry, t, tick(), 0.22, pan=rs.uniform(-.6, .6))
for w in cues['words'][5:7]:
    add(dry, w, stab([68, 71, 75]), 0.35)

# ---------- 5) TRANSITION : Silence → Precision ----------
m0, tt = TL['turnMorph'], TL['turnText']
add(dry, m0, swell(tt - m0), 0.5)
TONES = [72, 74, 76, 79, 81, 84]                      # 모듈마다 한 음씩 올라가는 C 펜타토닉
for h in cues['tonal']:
    add(dry, h['t'], tonal_hit(TONES[h['n'] % 6]), 0.5, pan=-0.3 + 0.12 * h['n']); add(wet, h['t'], tonal_hit(TONES[h['n'] % 6]), 0.25)
for i, t in enumerate(cues['snaps']): add(dry, t, snap_sfx(), 0.6, pan=(-0.35 if i % 2 else 0.35))
for t in beats(cues['snaps'][0] - BEAT, tt, BEAT / 4): add(dry, t, HATC, 0.08, pan=0.4)   # 정밀함: 아주 작은 16분 틱
for t in cues['mag']: add(dry, t, mag_click(), 0.7)
# 구조 완성: Sub Impact 는 영상 전체에서 이 한 번만 + 짧은 쉬머
for h in cues['hits']:
    if h['k'] == 'impact': add(dry, h['t'], impact(True), 0.9); add(wet, h['t'], impact(True), 0.35)
    if h['k'] == 'bloom': add(dry, h['t'], bloom([84, 88, 91, 95]), 0.25); add(wet, h['t'], bloom([84, 88, 91, 95]), 0.55)
add(dry, tt, pad([m + 12 for m in C_MAJ9], TL['after'] - tt + 0.3, 1800), 0.35)
add(wet, tt, pad([m + 12 for m in C_MAJ9], TL['after'] - tt + 0.3, 1800), 0.3)
add(dry, tt, bass(36, TL['after'] - tt, 260), 0.45)

# ---------- 6) AFTER / RESULT / COMPARE : 따뜻한 코드 · 깨끗한 베이스 펄스 · 가벼운 싱코페이션 ----------
PROG = [(48, [60, 64, 67, 71]), (43, [59, 62, 67, 74]), (45, [60, 64, 69, 72]), (41, [60, 65, 69, 72])]  # Cmaj7 G Am7 Fmaj7
bar = 4 * BEAT
t0 = TL['after']; k = 0
while t0 < TL['core'] - 1e-6:
    root, ch = PROG[k % 4]; b = min(t0 + bar, TL['core'])
    add(dry, t0, pad(ch, b - t0 + 0.15, 1300), 0.2); add(wet, t0, pad(ch, b - t0 + 0.15, 1300), 0.22)
    for j, t in enumerate(beats(t0, b, BEAT)):
        if not silent(t):
            add(dry, t, bass(root, BEAT * 0.8, 340), 0.55)
            if j % 2 == 0: add(dry, t, KICK, 0.55)
            if j == 3: add(dry, t, RIM, 0.22)
            if j == 1: add(dry, t + BEAT / 2, RIM, 0.2, pan=0.3)       # 2박 뒤 엇박
        add(dry, t + BEAT / 2, SHK, 0.08, pan=-0.3)
    t0 += bar; k += 1
LANE_NOTE = [76, 79, 84]
for c in cues['chipLand']:
    add(dry, c['t'], pluck(LANE_NOTE[c['lane'] % 3]), 0.3, pan=(-0.4, 0, 0.4)[c['lane'] % 3]); add(wet, c['t'], pluck(LANE_NOTE[c['lane'] % 3]), 0.2)
for h in cues['hits']:
    if h['k'] == 'word': add(wet, h['t'], bell(79), 0.35); add(dry, h['t'], bell(79), 0.15)
    if h['k'] == 'soft' and h['t'] < TL['core']: add(wet, h['t'], bell(84), 0.4)
    if h['k'] == 'resolve' and h['t'] < TL['cta']: add(dry, h['t'], stab([60, 64, 67, 72], 0.5), 0.3); add(wet, h['t'], bell(84), 0.35)

# ---------- 7) CORE : 사일런스 드롭 → 밝은 코드로 올라섬 (임팩트 없이) ----------
cs, c2 = TL['core'], TL['core2']
add(dry, cs, pad([45, 57, 64, 67, 72], c2 - cs - 0.2, 1100), 0.3); add(wet, cs, pad([45, 57, 64, 67, 72], c2 - cs - 0.2, 1100), 0.3)
add(wet, cs, bell(76), 0.3)
add(dry, c2, pad([m + 12 for m in C_MAJ9], TL['cta'] - c2 + 0.3, 2200), 0.4); add(wet, c2, pad([m + 12 for m in C_MAJ9], TL['cta'] - c2 + 0.3, 2200), 0.35)
add(dry, c2, bass(36, TL['cta'] - c2, 280), 0.55); add(wet, c2, bloom([84, 88, 91]), 0.35)
for t in beats(c2 + BEAT, TL['cta'], 2 * BEAT): add(dry, t, KICK, 0.35)

# ---------- 8) CTA : 단순하고 해결된 코드 · 리듬 최소 · 신뢰감 있는 마무리 ----------
ca, ends = TL['cta'], DUR
rs_ = ca + 2 * BEAT                                       # 두 박 뒤 C 로 해결
add(dry, ca, pad([53, 57, 60, 64, 67], rs_ - ca + 0.25, 1500), 0.3); add(wet, ca, pad([53, 57, 60, 64, 67], rs_ - ca + 0.25, 1500), 0.3)   # Fmaj9
add(dry, rs_, pad([48, 55, 60, 64, 67, 71], ends - rs_ + 0.5, 1500), 0.32); add(wet, rs_, pad([48, 55, 60, 64, 67, 71], ends - rs_ + 0.5, 1500), 0.32)  # Cmaj7 해결
add(dry, ca, bass(41, rs_ - ca, 240), 0.45); add(dry, rs_, bass(36, ends - rs_, 240), 0.45)
for t in beats(ca, ends - BEAT, 2 * BEAT): add(dry, t, KICK, 0.28)
for h in cues['hits']:
    if h['k'] == 'bell': add(wet, h['t'], bell(84, 2.0), 0.45); add(dry, h['t'], bell(84, 2.0), 0.15)
    if h['k'] == 'resolve' and h['t'] >= TL['cta']: add(wet, h['t'], bell(79, 2.0), 0.3)

# ---------- reverb + master ----------
irn = int(SR * 1.6); ti = np.arange(irn) / SR
ir = np.stack([lp_fast(rs.randn(irn), 6000) * np.exp(-ti * 3.2) for _ in range(2)], 1)
ir /= np.sqrt((ir ** 2).sum(0))
L = N + irn; nfft = 1 << (L - 1).bit_length()
rev = np.stack([np.fft.irfft(np.fft.rfft(wet[:, c], nfft) * np.fft.rfft(ir[:, c], nfft), nfft)[:N] for c in range(2)], 1)
mix = dry + rev * 0.5
# 스피드 램프: 화면이 슬로모션이 되는 구간은 테이프가 멈추듯 음정·속도가 함께 떨어짐
ra, rb = int(TL['ramp'] * SR), int(TL['turn'] * SR)
if rb > ra:
    n = rb - ra; rate = 1 - 0.65 * (np.arange(n) / n); pos = ra + np.cumsum(rate)
    for ch in range(2): mix[ra:rb, ch] = np.interp(pos, np.arange(N), mix[:, ch])
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
