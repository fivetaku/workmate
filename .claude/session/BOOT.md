# 세션 시작 체크리스트

**workmate — 범용 업무 비서 프레임워크**

이 세션은 다음을 자동으로 로드했습니다:
- 이 BOOT.md (세션 시작 체크리스트)
- `memory/MEMORY.md` (위키 인덱스 — 누적 기억)
- `memory/daily/{오늘,어제}.md` (이어받기 메모)
- `.claude/skills/_candidates/pending.json` (자동 발굴된 스킬 후보)

## 세션 시작 시 자동 처리 (사용자 요청 전에 완료)
1. **wrap-queue 처리** (최우선): `.claude/wrap-queue/`에 `.md` 파일이 있으면 → 각 파일 Read → `memory/daily/{날짜}.md`에 Done/Decisions/Open 보강 → `memory/MEMORY.md ## Unsorted`에 결정/선호 append → 처리 완료 파일 삭제
2. **wiki 승격**: `## Unsorted`에 항목이 있으면 → `/wiki-promote` 로직 실행 (카테고리별 grep 중복 검사 → new/partial/exact 분기 → Write/Edit + MEMORY.md 인덱스 동기화)
3. 어제 일지에 이어받을 작업이 있는가?
4. 새로 올라온 스킬 후보가 있는가? → 사용자에게 검토 제안
5. 사용자 요청이 기존 스킬/커맨드로 처리 가능한가? → 새로 짜기 전에 확인

## 진입 규칙
- 데이터 분석/보고서 요청 → `CLAUDE.md`의 역할 원칙 + `references/` 확인
- "매번 반복" "자동화" 언급 → 스킬 후보로 기록 (SessionEnd 훅이 종료 시 자동 감지, 또는 수동 `/wrap`)
- 긴 대화 → 10턴마다 메모리 체크포인트

## 처음이라면
```
/onboarding
```
사용자 맥락(이름, 부서, 업무, 선호 스타일)을 수집하여 개인화합니다.

## 자주 쓰는 요청 예시
- "이 CSV 분석해줘"
- "보고서 초안 만들어줘"
- "엑셀/워드/PPT로 저장해줘"
- "이 작업 스킬로 만들어줘"
