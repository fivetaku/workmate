# Skill Candidates

자동 발굴된 스킬 후보와 자가 복구 백업을 모아두는 곳입니다.

## 구조

| 경로 | 용도 |
|------|------|
| `pending.json` | Stop 훅이 세션 로그에서 발굴한 스킬 후보 (자동 생성, gitignore) |
| `backups/` | 스킬 self-healing 패치 전 백업본 (자동 생성, gitignore) |

## 라이프사이클

1. **Detection** — Stop 훅이 최근 세션 로그를 스캔해 반복 워크플로우를 찾고 `pending.json`에 후보로 기록
2. **Review** — 다음 SessionStart에서 부트스트랩이 `pending.json`을 출력 → 사용자가 검토
3. **Promotion** — 승인된 후보는 `skill-builder` (전역) 또는 `skillers-suda`로 정식 스킬 생성 → 후보에서 제거
4. **Cleanup** — 거절된 후보는 pending.json에서 수동 제거 또는 세션 종료 시 정리
5. **Backups** — 스킬 self-healing 패치 적용 전 원본이 `backups/`에 복사됨. 개인 세션 데이터라 git에 올리지 않음.

## 주의
- `pending.json`과 `backups/`는 워크스페이스 `.gitignore`에 포함되어 있어야 함
- `pending.json`은 수동 편집 금지 — Stop 훅이 관리
- 후보 검토 시 `name` 중복은 자동으로 회피됨
