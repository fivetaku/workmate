---
description: 오늘 날짜의 Daily Note 생성 또는 열기. "오늘 일지", "데일리 노트", "daily note" 등으로 호출.
allowed-tools: Read, Write, Edit, Bash
---

오늘 날짜의 Daily Note를 생성하거나 열어주세요.

**수행할 작업:**

1. 오늘 날짜 확인 (YYYY-MM-DD 형식)
2. 파일 경로: `./memory/daily/YYYY-MM-DD.md`
3. 파일이 없으면:
   - 템플릿 읽기: `./00-system/01-templates/daily-note-template.md`
   - 변수 치환:
     - `{{date}}`: 오늘 날짜 (2026-04-08)
     - `{{weekday}}`: 요일 (화요일)
     - `{{yesterday}}`: 어제 날짜
     - `{{tomorrow}}`: 내일 날짜
     - `{{week}}`: 주차 (2026-W15)
   - 새 파일 생성
4. 파일이 있으면:
   - 현재 내용 표시
   - "추가할 내용이 있으면 말씀하세요" 안내

**참고**: memory/daily/ 폴더는 훅(SessionStart, PreCompact)도 함께 사용합니다. 훅이 자동 기록한 내용이 이미 있을 수 있습니다.
