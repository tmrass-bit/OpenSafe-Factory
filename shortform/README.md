# 숏폼 광고 생산 템플릿 (업무 구조화 · AI 워크플로 설계)

25초 · 9:16 · 30fps 세로 광고를 **설정 파일(config.json) 하나로** 찍어내는 코드 템플릿입니다.
영상 편집 프로그램 없이, 글자·화면·음악이 모두 코드로 만들어집니다.

## 폴더 구조
```
shortform/
├─ engine/template.html   ← 연출(장면 순서·움직임). 보통 안 건드림
├─ engine/music.py        ← 배경음악·효과음 자동 작곡 (화면 타이밍에 박자 맞춤)
├─ episodes/
│   └─ ep01-inquiry/config.json   ← ★ 내용(문구·데이터). 이것만 바꾸면 새 영상
├─ assets/stock/           ← 외부 무료 소스 원본 (출처는 반드시 SOURCES.md 에 기록)
├─ render.js              ← 프레임 렌더러 (Chromium)
├─ make.sh                ← 한 줄 실행
└─ out/<episode>/         ← 결과물 (final.mp4, preview.html, music.wav)
```

## 새 편 만드는 법 (예: 견적/의뢰 편)
1. `episodes/ep01-inquiry` 폴더를 복사 → `episodes/ep02-quote`
2. `config.json` 에서 바꿀 것
   | 항목 | 의미 |
   |---|---|
   | `episode` | 결과 폴더 이름 (예: `ep02-quote`) |
   | `hook.lines` / `hook.notifications` | 첫 1.5초 문구 · 쏟아지는 알림 14개 |
   | `hook.background` · `before.background` · `cta.background` | (선택) 해당 장면 뒤에 깔 실사 영상. `src` 클립 경로, `start` 시작 초, `dim` 어둡게(0~1), `blur`, `saturation`. 빼면 기존 배경. 실사는 분위기, UI 는 설명 담당 |
   | `turn.modules` | "일의 구조입니다." 전환에서 분해→조립되는 모듈 6개 (라벨·보조문구). 순서대로 AFTER 의 문의·분류·3레인·(예외로 합쳐지는) 전달 자리로 모프 |
   | `bpm` | 템포 (기본 110). 모든 장면 타이밍이 이 박자 격자에서 계산됨 |
   | `before.words` / `before.windows` | 한 박자 단어 5개 · 업무창 4개(단톡/메일/엑셀/메모) 내용 |
   | `before.counterLabel/From/To` | 상단 "처리 대기 ○건" 카운터 |
   | `after.input/classifier/lanes/items` | 흐름도 노드 이름 · 3갈래 · 흘러가는 카드 12개 |
   | `after.words` | "나누고. / 판단하고. / 필요한 곳에만 AI." |
   | `result.*` | 대시보드 숫자·검토 목록 (KPI 합계 = counterTo 로 맞추면 자연스러움) |
   | `compare`, `core`, `cta` | 비교 문구 · 핵심 카피 · CTA 버튼 |
   | `brand.name`, `brand.logo` | 브랜드명 · 로고 이미지 경로(없으면 LOGO 자리 표시) |
3. `bash make.sh episodes/ep02-quote`

## 미리보기
`out/<episode>/preview.html` 을 브라우저로 열면 바로 재생됩니다 (클릭하면 처음부터 + 음악).

## 타이밍 조정 (박자 격자)
장면 시각은 `engine/template.html` 상단 `TB` 객체에 **박자 단위**로 적혀 있고, `bpm`(기본 110)으로 초가 계산됩니다.
화면 전환·텍스트 등장·카드 이동·모듈 스냅이 모두 이 격자 위에 있고, 렌더러가 계산된 타임라인(`T`)과 화면 이벤트를
`out/<episode>/cues.json` 에 저장하면 `music.py` 가 그대로 읽어 음악을 맞춥니다. 특정 편만 바꾸려면
config 에 `"timeline": {"cta": 21.5}` 처럼 **초 단위**로 넣으면 됩니다.

| 박자 | 초(110BPM) | 장면 · 영상문법 | 사운드 |
|---|---|---|---|
| 0–3 | 0–1.6 | HOOK · 실사(얕은 심도) + 알림 16분음표 | Tension 펄스 |
| 3–5 | 1.6–2.7 | 스매시 컷 → 검정 · "아니요." | 무음 → 작은 저음 |
| 5–10 | 2.7–5.5 | BEFORE · 실사 위 반투명 업무창 · 한 박자 한 단어 | 미니멀 일렉트로닉 펄스 |
| 10–13 | 5.5–7.1 | 과부하 몽타주 · 랙 포커스 · 스텝 줌 → 스피드 램프(슬로모션) | 서브디비전 증가 · 짧은 라이저 · 테이프 스톱 |
| 13–13.5 | 7.1–7.4 | 프리즈 프레임 | Silence Drop |
| 13.5–19 | 7.4–10.4 | 분해(Exploded View·패럴랙스) → 모듈 등장 → 격자 스냅 → 조립 | Tonal Hit ×6 · Mechanical Snap ×6 · Magnetic Click |
| 19 | 10.4 | 구조 완성 · 임팩트 프레임 · 라이트 스윕 | Sub Impact(영상 전체 1회) · Shimmer |
| 19–22 | 10.4–12.0 | 랙 포커스 + 푸시인 "일의 구조입니다." → AFTER 3레인으로 모프 | 따뜻한 패드 |
| 22–30 | 12.0–16.4 | AFTER 흐름 · 카드 8분음표 · 레인 랙 포커스 | 웜 코드 · 베이스 펄스 · 카드 착지 = 플럭 |
| 30–33.5 | 16.4–18.3 | 대시보드 풀아웃 | 〃 |
| 33.5–36.5 | 18.3–19.9 | 스플릿 스크린 · 하드 컷 매치 컷 | 〃 |
| 36.5–40 | 19.9–21.8 | 핵심 카피 · 사일런스 드롭 → 푸시인 | 밝은 코드 (임팩트 없음) |
| 40– | 21.8–25 | CTA · 정돈된 책상 실사 | 해결된 코드 · 리듬 최소 |

## 필요 환경
Node.js + `playwright`(Chromium), Python3 + numpy, ffmpeg, 한글 폰트(Noto Sans CJK KR)
