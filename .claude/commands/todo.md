---
description: 빠르게 Todo를 추가하는 커맨드 (우선순위 자동 감지). "할 일 추가", "todo", "할일" 등으로 호출.
argument-hint: "[urgent] Todo 내용"
allowed-tools: Read, Write, Edit, Bash
---

빠르게 Todo를 추가해주세요.

**사용 예시:**
```
/todo 주간 보고서 작성
/todo [urgent] 대책서 제출
/todo [high] 거래처 확인
```

**수행할 작업:**

1. **우선순위 자동 감지**
   - `[urgent]` 또는 `[high]` → high priority
   - `[low]` → low priority
   - 없으면 → normal priority

2. **저장**
   - 경로: `./40-personal/46-todos/active-todos.md`
   - 섹션: "## Inbox" 아래에 추가
   - 형식:
     ```markdown
     - [ ] [Todo 내용]
       - added: YYYY-MM-DD HH:mm
       - priority: [high/normal/low]
     ```

3. **확인 메시지**
   ```
   Todo 추가됨: [내용]
   Priority: normal
   
   /todos 로 전체 목록을 확인하세요.
   ```
