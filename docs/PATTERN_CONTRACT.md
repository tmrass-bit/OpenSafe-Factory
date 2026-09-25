# PATTERN CONTRACT · VERSIONING · DEPENDENCY METADATA — 설계안

STATUS: **DRAFT (PHASE 1 제안 · 미구현)** — 승인 전 구현하지 않는다.
대상: PHASE 3 (장면 컴포넌트화) · PHASE 4 (사운드 상태화) 의 선행 인터페이스.

## 1. 현재 구조에서 출발점
- `engine/template.html` 한 파일에 장면별 `renderX(t)` 10개와 `SCENES` 표가 있다.
- 장면 간 공유 요소: 박자 타임라인 `T`(`TB` × beat), `CUES`(음악용 이벤트), `LANE_COLOR`, CSS 클래스, 배경 프레임 `BG`.
- `validate.js` 가 이미 scene ID ↔ `T` 키 구간표(`SCENES`)와 키프레임 앵커(`KEYFRAMES`)를 갖고 있다 → Pattern metadata 로 옮길 첫 데이터.

## 2. Pattern Contract
각 pattern 은 코드 옆에 **기계가 읽는** `pattern.json` 을 둔다 (주석 아님).

```
engine/patterns/STRUCTURE_REVEAL/V1/
├─ pattern.json   ← contract
├─ render.js      ← render(t, ctx) — ctx 로만 입력을 받는다
└─ style.css
```

```json
{
  "id": "STRUCTURE_REVEAL",
  "version": 1,
  "status": "LOCKED",
  "used_by": ["ep01-inquiry"],
  "role": ["TURN", "CLIMAX"],
  "inputs": {
    "config": ["turn.text", "turn.modules[6].label", "turn.modules[6].sub"],
    "timeline": ["turnMorph", "reveal", "snap", "assemble", "turnText", "turnOut", "after"],
    "constraints": { "turn.modules": { "count": 6 } }
  },
  "dependencies": {
    "core": ["timeline.beat", "easing"],
    "layout": ["LANE_GEOMETRY_V1"],
    "patterns": { "from": "OVERLOAD_MONTAGE_V1", "to": "THREE_LANE_WORKFLOW_V1" },
    "assets": []
  },
  "outputs": {
    "layer": "Lturn",
    "cues": { "tonal": 6, "snaps": 6, "mag": 1, "hits": ["impact", "bloom"] },
    "handoff": { "to": "THREE_LANE_WORKFLOW_V1", "shape": "3-lane module positions" }
  },
  "keyframes": [
    { "id": "snap", "anchor": "snap", "beat_offset": 1 },
    { "id": "climax", "anchor": "turnText", "beat_offset": 1 }
  ],
  "compatible_sound_states": ["INTERRUPT", "PRECISION", "ASSEMBLY", "RESOLUTION"]
}
```

| 필드 | 의미 | 쓰임 |
|---|---|---|
| `id` · `version` · `status` | 이름 · 정수 버전 · DRAFT…DEPRECATED | 승인 게이트 |
| `used_by` | 이 버전을 쓰는 episode | LOCKED 판정 |
| `inputs.config` | 읽는 config 경로 | 카피 변경 → 영향 pattern 역추적 |
| `inputs.timeline` | 읽는 `T` 키 | 타이밍 변경 영향 · section 구간 |
| `dependencies` | core/layout/인접 pattern/asset | 공통 코드 변경 영향 |
| `outputs.cues` | 음악으로 내보내는 이벤트 | sound follower 연결 |
| `outputs.handoff` | 다음 pattern 으로 넘기는 형태 (morph·match cut) | 경계 호환성 |
| `keyframes` | storyboard 앵커 | storyboard · golden 비교 |
| `compatible_sound_states` | 허용 감정 상태 (PHASE 4) | 사운드 조합 검증 |

episode config 는 장면별로 pattern 을 **버전까지 고정**해 참조한다: `"scenes": [{ "id": "turn", "pattern": "STRUCTURE_REVEAL_V1", ... }]` (PHASE 2 schema).

## 3. Versioning
- `used_by` 에 LOCKED episode 가 하나라도 있으면 그 버전 디렉터리는 **읽기 전용**. 개선은 `V2/` 새 디렉터리.
- 버그 수정도 예외 없음 — LOCKED 결과가 바뀌면 안 되므로 `V1` 은 그대로, 수정본은 `V2`.
- 공통 `core`/`layout` 변경은 SYSTEM CHANGE. 변경 전 해당 모듈에 의존하는 LOCKED pattern 목록을 보고.
- 검증: LOCKED episode 의 storyboard 키프레임이 Golden 과 같아야 한다 (`golden/README.md`). 판정은 sha256 일치가 아니라 PSNR 임계값(예: ≥ 40 dB) — Chromium 렌더는 실행마다 미세하게 달라질 수 있다 (PHASE 1 측정: 12장 중 0~5장 hash 불일치, 불일치 프레임 PSNR ≈ 45 dB).
- 더 쓰지 않을 버전은 `status: DEPRECATED` — 삭제하지 않고 새 episode 에서 선택 불가.

## 4. Dependency metadata → 자동 영향 분석 (interface 제안)
목표: LOCAL CHANGE 전에 사람이 아니라 metadata 가 영향 범위와 render 범위를 답한다.

```
node validate.js impact <변경 대상>
  변경 대상: config 경로 (cta.button) | T 키 (turnText) | 파일 (engine/core/easing.js) | pattern (SPLIT_COMPARE_V1)

→ {
    "change_type": "LOCAL",
    "affected_patterns": ["CTA_CALM_V1"],
    "affected_scenes": ["cta"],
    "locked_hits": [],                         // LOCKED 항목이면 STOP 사유
    "sound_affected": false,                   // outputs.cues 가 바뀌는가
    "render_scope": "still cta",               // 가장 싼 검증 수단
    "read_scope": ["episodes/ep01-inquiry/config.json#cta", "engine/patterns/CTA_CALM/V1/"]
  }
```

판정 규칙:
1. 변경 대상을 `inputs.config` / `inputs.timeline` / `dependencies` 에서 역색인 → affected patterns.
2. patterns → `used_by` × 장면 ID → affected scenes. LOCKED episode 이면 `locked_hits`.
3. affected scene 이 1개이고 `core`/`layout` 무관 → LOCAL, 아니면 SYSTEM.
4. render scope: 텍스트만 → `still` · 한 장면 모션 → `section <id>` · `T` 키나 `outputs.cues` 변경 → `animatic`.
5. `read_scope` 는 Claude 가 읽을 파일 범위 — 이 목록 밖은 읽지 않는다.

## 5. 제안하는 다음 PHASE 순서
1. PHASE 2: config 에 `scenes[]`(id · pattern · timing 앵커 · status) 추가. template 은 그대로 두고 schema 만 확장 → EP01 결과 동일성은 cues.json · music.wav hash 로 검증 (둘은 결정적: PHASE 1 에서 기준 결과물과 byte 일치 확인).
2. PHASE 3: pattern 1개(가장 독립적인 `CTA_CALM`)만 먼저 분리해 contract 검증 → 이후 순차 분리. 각 분리 후 EP01 storyboard 가 Golden 과 PSNR 임계값 이상인지 확인.
3. `validate.js impact` 는 pattern.json 이 2개 이상 생긴 뒤 구현.
