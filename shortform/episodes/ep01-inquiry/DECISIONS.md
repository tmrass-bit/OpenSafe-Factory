# EP01 inquiry — DECISIONS

STATUS: **LOCKED (final 승인 전)** · Golden 미선언
값은 여기에 복사하지 않는다. 값의 source of truth 는 아래에 적힌 위치다.
근거: 2026-09-25 PHASE 1 요청의 DO NOT TOUCH 목록 + commit d2f0ac0.

# LOCKED
명시적 CURRENT_CHANGE 없이는 변경 금지.

| 항목 | source of truth |
|---|---|
| runtime · fps | `config.json` `duration` · `fps` |
| BPM · scene timing (박자 격자) | `config.json` `bpm` · `engine/template.html` `TB` |
| CTA duration | `TB.cta` → `duration` |
| copy · CTA 문구 | `config.json` `hook` `stop` `before` `turn` `after` `result` `compare` `core` `cta` |
| message 순서 · 장면 구성 | `engine/template.html` `SCENES` |
| stock footage (클립 · 구간 · grade) | `config.json` `*.background` · `SOURCES.md` |
| visual design | `engine/template.html` 현재 연출 |
| music arrangement · sound 구조 | `engine/music.py` (cues 는 `template.html` 이 생성) |
| 기준 결과물 | `out/ep01-inquiry/` (final.mp4 · music.wav · cues.json) |

# APPROVED PATTERNS
현재 EP01 에서 사용 중. 향후 PHASE 3 에서 V1 으로 추출할 후보. (scene ID 는 `node validate.js scenes`)

- OVERLOAD_MONTAGE — overload: UI stacking · badge · rack focus · step zoom → speed ramp → hard freeze
- SMASH_INTERRUPT — stop: smash cut to black + 한 줄 카피 + silence
- STRUCTURE_REVEAL — turn: exploded view · beat-sync module reveal · snap-to-grid · 단 1회 sub impact → 3-lane morph
- THREE_LANE_WORKFLOW — after: 카드 8분음표 · 레인 rack focus
- DASHBOARD_PULLOUT — result
- SPLIT_COMPARE — compare: 같은 구도 split screen · hard/match cut
- CORE_COPY — core: silence drop → push-in, 임팩트 없음
- CTA_CALM — cta: 실사(손·책상) · 리듬 최소 · 장식선·버튼 흔들림 없음

# REJECTED
다시 제안하지 않는다.

- 엉킨 선 · 낙서형 혼란 표현 → UI 밀도로 대체 (f683833)
- 카드마다 whoosh · 반복 glow, 텍스트 bounce/shake, CTA 장식선 · 버튼 wobble (d2f0ac0)
- Sub impact 2회 이상 — CLIMAX 1회만

# OPEN
- message hierarchy 역할 라벨 확인 (repo 구조에서 도출한 제안): HOOK=hook · PROBLEM=stop/before/overload · TURN=turn · CLIMAX=`turnText` 구조 완성 · PROOF=after/result/compare · BRAND_MESSAGE=core · CTA=cta
- `brand.name` = "브랜드명" placeholder · `brand.logo` = null
- EP01 최종 승인 → `EP01_GOLDEN_v1` 선언 (`shortform/golden/README.md`)
