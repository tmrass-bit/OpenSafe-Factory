# Golden Master

최종 승인된 episode 의 **동결 기준점**. 이후 LOCAL CHANGE 가 다른 장면을 건드리지 않았는지 비교하는 기준이 된다.
현재 선언된 Golden 없음. (EP01 은 final 승인 전 — `episodes/ep01-inquiry/DECISIONS.md` OPEN)

## 선언 절차 (최종 승인 후에만)
1. `node validate.js final --approved` 결과를 사용자가 승인
2. `node validate.js storyboard` 실행
3. `golden/<EP>_GOLDEN_v<N>/` 생성 후 아래 파일 배치, `DECISIONS.md` STATUS 에 Golden ID 기록
4. Golden 은 수정하지 않는다. 승인된 변경은 `_v<N+1>` 로 새로 만든다

## 구조
```
golden/EP01_GOLDEN_v1/
├─ manifest.json      ← 아래 스키마
├─ cues.json          ← approved timeline (out/<ep>/cues.json 복사: T · 이벤트)
├─ storyboard.json    ← approved keyframes (시각 · 박자 · sha256)
├─ keyframes/*.png    ← 540x960 키프레임 12장
└─ config.json        ← approved copy · CTA · footage 스냅샷 (현재 상태가 아닌 승인 시점 기록)
```

## manifest.json
```json
{
  "id": "EP01_GOLDEN_v1",
  "episode": "ep01-inquiry",
  "declared_at": "YYYY-MM-DD",
  "source_commit": "<git sha>",
  "hashes": { "config": "", "template": "", "music_py": "", "cues": "", "music_wav": "", "final_mp4": "" },
  "timeline": "cues.json",
  "keyframes": "storyboard.json",
  "copy": "config.json",
  "patterns": { "stop": "SMASH_INTERRUPT_V1", "overload": "OVERLOAD_MONTAGE_V1", "turn": "STRUCTURE_REVEAL_V1", "cta": "CTA_CALM_V1" },
  "final": { "path": "out/ep01-inquiry/ep01-inquiry_final.mp4" }
}
```
`patterns` 는 PHASE 3 에서 pattern 이 분리된 뒤 채운다 (`docs/PATTERN_CONTRACT.md`). 그 전에는 비워 둔다.
final mp4 는 복사하지 않고 경로와 hash 로만 연결한다.

## 비교 기준
- `cues.json` · `music.wav`: hash 일치 (결정적)
- 키프레임 PNG: **PROVISIONAL / CALIBRATION REQUIRED** — 통과 기준 미확정. sha256 은 기록용
  - 측정 사실: 동일 storyboard 재렌더에서 Chromium 래스터화 차이로 일부 프레임 hash 가 달라짐. 측정한 1 사례 ≈ 45 dB PSNR
  - 확정 방법: 동일 렌더의 자연 변동과 의미 있는 작은 visual change 를 모두 측정한 뒤 threshold 결정
