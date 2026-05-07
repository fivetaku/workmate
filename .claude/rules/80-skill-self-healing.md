# Skill Self-Healing Protocol

스킬 실행 실패 시 이 프로토콜을 정확히 따른다.

## Error Response Flow

### 1. Diagnose
- 에러 메시지와 트레이스백을 전부 읽는다
- 근본 원인 식별: 누락 파일, 잘못된 경로, 문법 오류, API 변경, 권한 문제
- 이 스킬이 `memory/wiki/lessons/`에 이미 기록된 함정이 있는지 확인

### 2. Draft
- 패치를 diff 또는 교체 블록으로 초안 작성
- 무엇을 바꾸는지, 왜 바꾸는지 설명
- **사용자에게 제시하고 승인 요청**

### 3. Backup
- 패치 적용 전에 현재 스킬 파일을 복사:
  `.claude/skills/_candidates/backups/{skill-name}_{YYYY-MM-DD}.md`
- 같은 날 같은 스킬 백업이 이미 있으면 카운터 추가:
  `{skill-name}_{YYYY-MM-DD}_2.md`

### 4. Execute
- 사용자 승인 후에만 패치 적용
- 적용 후 에러 없이 실행되는지 검증

### 5. Record
- `memory/wiki/lessons/`에 한 줄 요약 추가
- 형식: `- {skill-name}: {무엇이 깨졌나} → {무엇이 고쳤나} ({날짜})`

## 제약
| 규칙 | 세부 |
|------|------|
| No auto-apply | 사용자 승인 없이 패치 적용 금지 |
| No hook patching | 훅 실행 중에는 스킬 패치 금지 |
| One per turn | 한 번의 대화 턴에서 최대 1개 스킬만 패치 |
| Draft-Approve-Execute | 반드시 3단계 사이클 |
| Backup required | 백업 없이 스킬 파일 덮어쓰기 금지 |
