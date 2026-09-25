# CLAUDE.md — CONTROL PLANE

25초 · 9:16 숏폼 광고를 코드로 생산하는 저장소. 목표는 **같은 판단·같은 작업을 두 번 하지 않는 것**.
세부 원칙은 `docs/PRODUCTION_SYSTEM.md`. 이 파일에는 위치와 핵심 제어 규칙만 둔다.

## 위치
- 제작 규칙: `docs/PRODUCTION_SYSTEM.md` · PRE-STORYBOARD 양식: `docs/PRE_STORYBOARD_TEMPLATE.md`
- 다음 PHASE 설계안 (DRAFT · 미구현): `docs/PATTERN_CONTRACT.md`
- 코드: `shortform/` — `engine/template.html`(연출·박자 타임라인 `TB`), `engine/music.py`(음악), `render.js`, `make.sh`
- Episode config: `shortform/episodes/<ep>/config.json` (내용·문구·footage)
- Episode 결정 상태: `shortform/episodes/<ep>/DECISIONS.md` (LOCKED / APPROVED / REJECTED / OPEN)
- Golden Master: `shortform/golden/` · 출처/저작권: `shortform/SOURCES.md`
- 검수·렌더 명령: `shortform/validate.js` (파일 상단 사용법). 모든 명령은 `shortform/` 에서 실행

## 판단 우선순위 (낮은 순위는 높은 순위를 덮어쓸 수 없다)
1. CURRENT_CHANGE — 사용자가 이번에 명시적으로 바꾸라고 한 것
2. HARD_LOCK — DECISIONS.md 의 LOCKED 항목
3. PRODUCTION_HARD_RULE — copyright · approval gate · scope · revision protocol · stop
4. STYLE_DEFAULT — BPM 권장값 · 실사/UI 비율 · transition · sound grammar
5. OPTIONAL_AI_JUDGMENT — 자동 구현 금지. `OPTIONAL_SUGGESTION:` 으로 보고만

timing LOCKED 이후: VISUAL / MESSAGE TIMELINE = MASTER, SOUND = FOLLOWER.

## 작업 시작 전
- 요청을 LOCAL / SYSTEM CHANGE 로 분류한다.
  - LOCAL: 관련 파일·scene 만 읽고 수정. 전체 repo 재분석·다른 scene 자발적 개선 금지.
  - SYSTEM (template 구조 · config schema · music engine · pattern · pipeline): 영향 범위 + 설계안 보고 → STOP.
- 해당 episode 의 `DECISIONS.md` 를 먼저 읽는다. 이전 대화를 재구성하지 않는다 — repo 가 source of truth.
- 요청 형식: CONFIRMED / CHANGE / DO NOT TOUCH / CHANGE TYPE / VALIDATION.

## 검수 (가장 싼 수단부터)
| 확인 대상 | 명령 |
|---|---|
| 텍스트 · 정적 위치 | `node validate.js still <scene-id\|초>` |
| 구도 · 위계 · 타이포 | `node validate.js storyboard` |
| 장면 모션 | `node validate.js section <scene-id>` |
| 전체 timing · sound | `node validate.js animatic` |
| 최종 (승인 후에만) | `node validate.js final --approved` |

## STOP (자동으로 다음 단계로 넘어가지 않는다)
설계안 · PRE-STORYBOARD · storyboard · preview 완성 시 / 예상 못한 dependency / LOCKED 수정 필요 /
SYSTEM CHANGE 영향 발견 → 보고 후 승인 대기. 신규 episode·pattern 은 PRE-STORYBOARD 승인 전 구현 금지.
LOCKED episode 가 쓰는 pattern V1 은 수정하지 않고 V2 를 만든다.
