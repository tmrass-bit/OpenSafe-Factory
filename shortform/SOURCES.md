# 사용 소스 · 저작권 기록

| 구분 | 소스 | 라이선스 |
|---|---|---|
| 영상/그래픽 | 아래 실사 배경 3개를 제외한 전부 코드로 직접 제작 (HTML/CSS/SVG) | 자체 제작 |
| hook 배경 실사 영상 (0~1.5초) | Pexels · "Businessman Working in an Office" · 촬영 **Mizuno K** · https://www.pexels.com/video/businessman-working-in-an-office-12894337/ · 파일 `assets/stock/pexels-12894337-mizuno-k.mp4` (1440×2560, 10초 중 3.0~4.8초 구간 사용) · 2026-09-25 다운로드 | Pexels License — 상업 이용·수정 가능, 출처 표기 불필요 |
| BEFORE 배경 실사 영상 (약 2.7~7.1초) | Pexels · "Man Typing on the Laptop on his Desk" (노트북 키보드를 치는 손 클로즈업) · 촬영 **Darlene Alderson** · https://www.pexels.com/video/man-typing-on-the-laptop-on-his-desk-7967182/ · 파일 `assets/stock/pexels-7967182-darlene-alderson.mp4` (1080×1920, 10초 중 1.0~5.6초 구간 사용) · 2026-09-25 다운로드 | Pexels License — 상업 이용·수정 가능, 출처 표기 불필요 |
| CTA 배경 실사 영상 (약 21.8~25초) | Pexels · "Male Hands Typing on Laptop" (정돈된 흰 책상 · 손만 등장) · 촬영 **Cup of Couple** · https://www.pexels.com/video/male-hands-typing-on-laptop-6177738/ · 파일 `assets/stock/pexels-6177738-cup-of-couple.mp4` (1080×1920, 11초 중 2.0~5.4초 구간 사용) · 2026-09-25 다운로드 | Pexels License — 상업 이용·수정 가능, 출처 표기 불필요 |
| 배경음악·효과음 | `engine/music.py` 로 직접 합성 (신스·드럼·효과음 전부 수학적 생성) — 외부 음원·샘플 미사용 | 자체 제작 |
| 폰트 | Noto Sans CJK KR (Google/Adobe) | SIL Open Font License 1.1 — 상업 이용 가능 |
| 알림/UI 목업 | 카카오톡·Excel 등은 실제 로고가 아닌 색상+글자 아이콘으로 표현 | 자체 제작 |

※ 크몽 로고는 사용하지 않았고 CTA 문구에 이름만 들어갑니다.

### Pexels 라이선스 준수 메모 (실사 배경 3개 공통)
- 라이선스: https://www.pexels.com/license/ (2026-09-25 확인)
- 허용: 상업적 이용, 수정·편집, 출처 표기 없이 사용
- 금지 사항과 이 영상에서의 처리
  - 식별 가능한 인물을 나쁘게/불쾌하게 묘사 금지 → hook 인물은 평범하게 휴대폰을 보는 모습만 쓰고, 채도를 낮추고 블러·어둡게 처리한 **배경**으로만 사용. BEFORE·CTA 클립은 **손만** 나오고 얼굴이 없음
  - 인물이 제품·브랜드를 보증하는 것처럼 암시 금지 → 식별 가능한 인물(hook) 옆에는 브랜드명·추천 문구를 붙이지 않음 (hook 문구는 질문형 카피). 브랜드·버튼이 나오는 CTA 에는 얼굴 없는 손·책상 클립만 사용
  - 원본 그대로 재판매·스톡 사이트 재배포 금지 → 원본 파일은 제작용으로만 보관
  - 상표·로고로 사용 금지 → 해당 없음

## ep02-zapier (Zapier 편) — 공식 Zapier asset

| 구분 | 소스 | 파일 | 비고 |
|---|---|---|---|
| END wordmark | Zapier 공식 브랜드 사이트 · https://brand.zapier.com/ (press kit https://zapier.com/press 에서 링크) · 파일명 `zapier-logo_frost.svg` (흰 텍스트 + 오렌지 볼트, 어두운 배경용 공식 컬러 배리언트) | `assets/official/zapier-logo-frost.svg` · 2026-09-25 다운로드 | 공식 로고 그대로 사용, 변형 없음 |
| PROOF (Trigger → Action → Action) | Zapier 공식 Help Center · "Zaps quick start guide" · https://help.zapier.com/hc/en-us/articles/22234847450893-Zaps-quick-start-guide · 원본 이미지 alt="Zap editor layout" (cdn.zappy.app/babd482c8371899f1b7663d4d6b575d2.png) | `assets/official/proof-trigger-action-action.png` · 2026-09-25 다운로드 | 공식 스크린샷 원본에서 위쪽 3단계(1. New Form Response in Google Forms → 2. Create Spreadsheet Row in Google Sheets → 3. Create Draft in Gmail)만 **크롭**. 픽셀 합성·텍스트 추가 없음. 원본은 전체 12단계 Zap 이었고 뒤쪽 Paths 분기는 이 영상 스코프(Trigger→Action→Action)에 불필요해 제외 |

※ 두 asset 모두 Zapier 소유 자산이며, 이 프로젝트가 Zapier 공식 의뢰가 아니라면 광고 제작·배포 전 Zapier 브랜드 가이드라인(https://brand.zapier.com/) 상 사용 승인 여부를 확인해야 한다 (PREPRODUCTION 문서에 이미 명시된 사항).

### ep02-zapier — Pexels 실사 footage (EP01과 별도로 확보한, 이 편 전용 소스)

| 구분 | 소스 | 파일 | 비고 |
|---|---|---|---|
| CLOSE 배경 | Pexels · "A Person Putting Sticky Notes on a Wall" · 촬영 **Cup of Couple** · https://www.pexels.com/video/a-person-putting-sticky-notes-on-a-wall-6632967/ · 1080×1920, 9.68초 중 2.6~3.0초 구간(손이 빠지고 메모만 남는 순간) 사용 · 2026-09-25 다운로드 | `assets/stock/pexels-6632967-cup-of-couple.mp4` | Pexels License. EP01과 무관한 이 편 전용 확보 소스 |
| BEFORE 배경 | Pexels · "Person Sticking Sticky Notes on a Whiteboard" · 촬영 **cottonbro studio** · https://www.pexels.com/video/person-sticking-sticky-notes-on-a-whiteboard-7429487/ · 2732×1440, 35초 중 13.0~13.8초 구간 사용 · 2026-09-25 다운로드 | `assets/stock/pexels-7429487-cottonbro.mp4` | Pexels License. EP01과 무관한 이 편 전용 확보 소스 |

※ AFTER 배경은 EP01 footage(`pexels-6177738-cup-of-couple.mp4`)를 임시로 재사용했다가 제거함 — 이 편 전용 새 source로 교체 예정(별도 후보 검토 중, 미확정).
※ Pexels 라이선스 준수 메모(위 "Pexels 라이선스 준수 메모" 섹션)는 이 두 클립에도 동일하게 적용 — 손만 나오는 구도, 식별 가능한 인물 없음.
