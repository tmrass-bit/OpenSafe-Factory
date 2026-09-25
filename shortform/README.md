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
   | `hook.background` | (선택) hook 뒤에 깔 실사 영상. `src` 클립 경로, `start` 시작 초, `dim` 어둡게(0~1), `blur`, `saturation`. 빼면 검은 배경 |
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

## 타이밍 조정
장면 시각은 `engine/template.html` 상단 `T` 객체에 있고, config 에 `"timeline": {"cta": 20.5}` 처럼
넣으면 해당 편만 덮어쓸 수 있습니다. 음악도 같은 값을 읽어서 자동으로 박자가 맞춰집니다.

## 필요 환경
Node.js + `playwright`(Chromium), Python3 + numpy, ffmpeg, 한글 폰트(Noto Sans CJK KR)
