# PRODUCTION SYSTEM — 운영제어 원칙

이 문서는 이 저장소에서 작업하는 Claude Code(및 모든 작업자)가 따르는 운영제어 원칙이다.
영상·코드 작업보다 먼저 적용되며, 명시적인 변경 요청 없이 수정하지 않는다.

---

## 0. 목표: LESS REDUNDANT

목표는 단순히 CHEAPER가 아니라 **LESS REDUNDANT**다.
품질을 낮춰 비용을 줄이는 것이 아니라, 같은 품질을 더 적은 반복과 context로 만든다.

- 필요한 판단은 한 번 제대로 한다.
- 이미 끝난 판단은 다시 하지 않는다.
- 승인된 결과는 잠근다.
- 작은 수정은 작은 범위에서만 처리한다.
- 설계와 구현을 분리한다.
- 렌더 전에 판단을 끝낸다.
- AI가 자발적으로 작업 범위를 넓히지 않는다.

---

## 1. DECISION PRECEDENCE

모든 작업은 아래 우선순위를 따른다. **낮은 우선순위는 높은 우선순위를 변경할 수 없다.**

| 순위 | 레벨 | 내용 |
|---|---|---|
| 1 | `CURRENT_CHANGE` | 현재 사용자가 명시적으로 변경하라고 요청한 사항 |
| 2 | `HARD_LOCK` | 이미 승인된 episode 결정 — runtime, scene start/end, copy, CTA, message hierarchy, visual pattern, approved footage, approved timing |
| 3 | `PRODUCTION_HARD_RULE` | copyright, approval gate, scope control, revision protocol, stop condition |
| 4 | `STYLE_DEFAULT` | BPM 권장값, 실사/UI 비율, 추천 transition, 추천 sound grammar, 일반적인 미학적 가이드 |
| 5 | `OPTIONAL_AI_JUDGMENT` | Claude가 더 나아 보인다고 판단하는 개선 아이디어 |

예: STYLE_DEFAULT에서 100~115 BPM이 권장되어도, HARD_LOCK된 scene timing이나 CTA duration을 변경하면 안 된다.

더 좋은 방법이 보여도 LOCKED 항목은 자동 변경하지 않는다. 필요하면 `OPTIONAL_SUGGESTION`으로 제안하고 **STOP**한다.

---

## 2. MASTER TIMELINE RULE

- PREPRODUCTION 단계에서 timing이 아직 확정되지 않았다면 visual과 sound를 함께 설계할 수 있다.
- timing이 LOCKED된 이후:
  - **VISUAL / MESSAGE TIMELINE = MASTER**
  - **SOUND = FOLLOWER**
- 음악에 영상을 맞추기 위해 승인된 메시지 구조나 장면 시간을 바꾸지 않는다.
- LOCKED된 시간 안에서 beat subdivision, cue, percussion, impact 등을 조정한다.

---

## 3. CHANGE SCOPE

모든 수정 요청은 먼저 **LOCAL CHANGE** 또는 **SYSTEM CHANGE**로 분류한다.

### LOCAL CHANGE

예: 특정 문구 변경, 특정 scene 모션, 특정 transition, 특정 CTA, 특정 footage 교체, 특정 sound cue.

- 관련 파일만 읽는다.
- 관련 scene만 수정한다.
- 관련 dependency만 확인한다.
- 전체 repo 재분석 금지.
- 다른 scene 자발적 개선 금지.

### SYSTEM CHANGE

예: 공통 template 구조, config schema, music engine, pattern architecture, 공통 rendering pipeline, 공통 production rule.

- 먼저 영향 범위를 분석한다.
- 설계안을 보여준 뒤 **STOP**한다.
- 승인 전 구현하지 않는다.

---

## 4. REVISION PROTOCOL

수정 작업은 기본적으로 다음 구조를 따른다.

```
CONFIRMED / LOCKED:  이번 작업에서 이미 승인되어 유지해야 할 것
CHANGE:              이번에 실제로 수정할 것
DO NOT TOUCH:        이번 작업에서 절대로 변경하지 않을 것
```

- LOCKED 항목은 명시적인 변경 요청 없이는 수정하지 않는다.
- 수정 중 더 좋은 아이디어를 발견해도 자동 구현하지 않고, 별도로 보고한다:

```
OPTIONAL_SUGGESTION:
[제안]
```

---

## 5. STATUS

| 상태 | 의미 |
|---|---|
| `DRAFT` | 작업 중 |
| `REVIEW` | 검토 대기 |
| `APPROVED` | 승인됨 |
| `LOCKED` | 명시적 변경 요청 없이는 변경 금지 |
| `DEPRECATED` | 다시 사용하거나 제안하지 않는 패턴 |

---

## 6. DESIGN BEFORE IMPLEMENTATION

새로운 episode나 새로운 visual pattern은 가능하면 바로 구현하지 않는다.

```
STRATEGY
→ CUSTOMER ACTION
→ MESSAGE HIERARCHY
→ SCENE PURPOSE
→ VISUAL METAPHOR
→ PRE-STORYBOARD
→ APPROVAL
→ IMPLEMENTATION
→ STORYBOARD CHECK
→ SECTION / ANIMATIC
→ FINAL
```

"대본을 받고 바로 전체 영상을 구현"하는 것을 기본값으로 삼지 않는다.

### PRE-STORYBOARD

새 연출을 구현하기 전에는 필요할 경우 다음을 먼저 정의한다.

- scene purpose
- viewer reaction
- composition
- live action / UI
- visual metaphor
- transition
- approximate timing
- sound role

목표: 구현한 뒤 처음으로 연출을 판단하는 일을 줄인다.

---

## 7. MESSAGE HIERARCHY

광고 메시지는 다음 역할로 구분한다.

`HOOK` · `PROBLEM` · `TURN` · `CLIMAX` · `PROOF` · `BRAND_MESSAGE` · `CTA`

- 모든 장면을 같은 강도로 연출하지 않는다.
- **CLIMAX**는 영상 전체에서 가장 중요한 시각적·청각적 지점을 가진다.

---

## 8. SHORTFORM AD PHILOSOPHY

이 프로젝트의 광고는 전통적인 TV 브랜드 광고와 목적이 다르다.

```
Attention → Problem Recognition → Perception Shift → Proof → Next Action
```

= Performance objective + Brand-film visual language + Customer-journey structure + Clear behavioral CTA

- 저가형 퍼포먼스 광고처럼 보이면 안 된다.
- **"행동하게 만드는 광고이지만, 광고처럼 소리치는 영상은 만들지 않는다."**
- Urgency / FOMO는 "지금 안 사면 손해" 식의 과장보다,
  "지금도 이 비효율/기회비용은 계속 발생하고 있다"를 체감시키는 방향을 우선한다.

---

## 9. VIDEO / FILM LANGUAGE PRINCIPLE

효과를 예뻐 보여서 사용하지 않는다. 모든 영상 효과는 최소 하나의 기능을 가져야 한다.

- 시선을 이동
- 긴장 상승
- 정보 분리
- 구조 이해
- 전환점 강조
- BEFORE / AFTER 대비
- 다음 행동 유도

**사용 가능한 영상문법 (영화 / TV 광고 / 브랜드 필름):**
Hard Cut, Smash Cut, Match Cut, Push-in, Pull-out, Whip Pan, Freeze Frame, Speed Ramp, Rack Focus, Depth of Field, Parallax, Split Screen, Exploded View, Snap-to-Grid, Assembly Animation, Morph Transition, Kinetic Typography, Beat Sync

**매우 제한적으로 사용:**
excessive Glitch, RGB Split, Cyberpunk, excessive Neon, scribble chaos, tangled lines, meaningless zoom, excessive 3D rotation, excessive whoosh, decorative effects without function

**"혼란"의 표현:** 낙서나 엉킨 선이 아니라 다음을 우선한다.
UI stacking, notification density, window overlap, cursor hesitation, rack focus, pacing, status badge, blur, vignette, motion density

---

## 10. SOUND PRINCIPLE

음악은 배경음이 아니라 영상의 구조적 변화와 함께 작동한다.

**기본 감정 흐름:**

```
TENSION → OVERLOAD → INTERRUPTION → PRECISION → RESOLUTION → CALM CONTROL
```

**대표 sound language:**
Riser, Silence Drop, Tonal Hit, Mechanical Snap, Magnetic Click, Sub Impact, Impact Hit, Tonal Bloom, Shimmer, Resolved Chord, Minimal Pulse

**원칙:** 하나의 명확한 움직임 = 하나의 명확한 sonic event.
모든 움직임에 효과음을 붙이지 않는다.

---

## 11. FOOTAGE PRINCIPLE

| 구분 | 역할 |
|---|---|
| LIVE ACTION | 현실감, 공감, 인간 행동, 감정, CTA |
| UI / MOTION | 구조, 프로세스, 시스템, 분류, 비교, workflow 설명 |

실사와 그래픽의 비율은 `STYLE_DEFAULT`일 뿐, `HARD_LOCK`된 scene 구조보다 우선하지 않는다.

---

## 12. PATTERN REUSE

검증된 장면 연출은 매 episode마다 새로 발명하지 않는다.

향후 pattern 예:
`OVERLOAD_MONTAGE_V1`, `STRUCTURE_REVEAL_V1`, `THREE_LANE_WORKFLOW_V1`, `SPLIT_COMPARE_V1`, `CTA_CALM_V1`

- LOCKED episode에서 사용하는 V1을 다른 episode 개선을 위해 직접 바꾸지 않는다.
- 개선본은 `V2`처럼 새 version으로 만든다.

---

## 13. VALIDATION COST PRINCIPLE

항상 가장 싼 검증 수단부터 사용한다.

| 검증 대상 | 수단 |
|---|---|
| 정적 텍스트 / 위치 | Still |
| 구도 | Storyboard |
| Scene motion | Section Preview |
| 전체 rhythm / sound | Animatic |
| 최종 승인 | Final Render |

작은 수정 때문에 전체 Final Render를 반복하는 것을 기본값으로 삼지 않는다.

---

## 14. SESSION POLICY

모든 작은 수정마다 새 세션을 만들 필요는 없다.

**새 세션 권장:**
- PREPRODUCTION 승인 후 EXECUTION으로 넘어갈 때
- 큰 방향 변경
- 폐기된 설계가 대화에 많이 누적됨
- SYSTEM CHANGE 시작

같은 LOCAL CHANGE의 연속 수정은 같은 세션에서 진행할 수 있다.

---

## 15. CONTEXT PRINCIPLE

새 세션에서는 이전 긴 대화를 재구성하는 것을 기본값으로 삼지 않는다.
현재 repo에 저장된 다음을 **source of truth**로 사용한다.

- project control rules (이 문서)
- episode current state
- config
- decisions
- approved patterns

> "Claude가 이미 알고 있는 것을 왜 다시 읽고, 다시 생각하고, 다시 만드는가?"
> 를 계속 제거한다.

---

## 16. STOP CONDITIONS

다음 상황에서는 자동으로 다음 단계로 넘어가지 않는다.

| 상황 | 동작 |
|---|---|
| 설계안 완성 | STOP / 승인 대기 |
| PRE-STORYBOARD 완성 | STOP / 승인 대기 |
| Storyboard 완성 | STOP / 승인 대기 |
| Local Preview 완성 | STOP / 승인 대기 |
| 예상하지 못한 dependency 발견 | STOP / 보고 |
| LOCKED 영역 수정 필요 | STOP / 승인 요청 |
| SYSTEM CHANGE 영향 범위 발견 | STOP / 설계 보고 |

"좋아 보여서 다음 단계도 미리 해두었습니다" 식의 범위 확대는 하지 않는다.

---

## 17. HANDOFF FORMAT

작업 요청은 가능한 한 다음 형태를 사용하며, 이 정보를 우선적으로 따른다.

```
CONFIRMED:     [이미 승인된 것]
CHANGE:        [이번 수정]
DO NOT TOUCH:  [수정 금지]
CHANGE TYPE:   LOCAL / SYSTEM
VALIDATION:    still / storyboard / section / animatic / final
```
