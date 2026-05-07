---
description: 이번 주 일지를 종합해 주간 리뷰를 생성. "주간 정리", "weekly synthesis", "이번 주 요약" 등으로 호출.
allowed-tools: Read, Write, Bash, Glob
---

# Weekly Synthesis

이번 주의 daily notes를 종합하여 주간 리뷰를 생성합니다.

## 수행할 작업

1. **이번 주 데이터 수집**
   - `memory/daily/` 에서 이번 주 파일들 읽기 (월~오늘)
   - `40-personal/46-todos/active-todos.md` 현황 확인
   - `reports/` 에서 이번 주 생성된 파일 확인

2. **패턴 분석**
   - 반복된 테마
   - 주요 성과
   - 해결된 이슈 / 미해결 이슈
   - 많이 쓴 스킬/커맨드

3. **주간 리뷰 생성**

```markdown
# 주간 리뷰 — {{week}} ({{date_range}})

## 이번 주 한눈에
- 일지 작성: X일
- 완료한 일: [목록]
- 생성한 보고서: [목록]

## 주요 테마
### 테마 1: [이름]
- 어디서 나왔는지
- 왜 중요한지
- 다음 액션

## 주요 인사이트
1. [인사이트 + 맥락]
2. [인사이트 + 맥락]

## 이번 주 열린 질문
- [아직 답 못 찾은 것]

## 다음 주 포커스
1. [1순위]
2. [2순위]
3. [탐색할 것]
```

4. **저장**
   - 경로: `memory/daily/YYYY-WXX-synthesis.md`
   - 메모리에도 주요 인사이트 기록 (memory/MEMORY.md → Data Patterns 또는 Decisions)
