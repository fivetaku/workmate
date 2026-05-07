---
description: 현재 세션을 wrap — daily 메모, MEMORY.md ## Unsorted, pending.json까지 한 번에 갱신. SessionEnd 훅과 동일한 작업을 수동으로 즉시 실행. 멱등 (같은 세션 여러 번 호출해도 중복 안 쌓임).
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

지금 진행 중인 세션을 **wrap 처리**합니다.

`.claude/scripts/session-end-prompt.md` 파일의 절차를 그대로 따라주세요. 단, **현재 대화 컨텍스트 자체**를 입력으로 사용합니다 (별도로 .jsonl 로그를 다시 읽지 마세요 — 토큰 낭비).

## 핵심 원칙: 멱등성

같은 세션을 여러 번 `/wrap` 호출해도 중복이 쌓이지 않아야 합니다. 매 단계에서 "이미 처리된 내용인지" 먼저 확인하고, 변경이 없으면 파일을 건드리지 마세요. **의심스러우면 보수적으로 no-op.**

## 수행 순서 요약

1. **현재 대화 분석** — 사용자가 이번 세션에서 수행한 업무 워크플로우, 결정, 선호, 인사이트, 도구 체인 식별

2. **데일리 메모 작성** — `memory/daily/{오늘 YYYY-MM-DD}.md`
   - 파일이 없으면 새로 Write (Done/Decisions/Verified/Open/References 5개 섹션)
   - 파일이 있으면 → 마지막 `## ` 시간 헤더 블록 확인:
     - 그 블록 이후 새 활동 **없음** → daily 건드리지 말고 `daily: no-op` 표시
     - 새 활동 **있음** → 그 부분만 `## {HH:MM} 추가 세션` 시간 헤더 블록으로 append (덮어쓰기 금지)

3. **MEMORY.md ## Unsorted 갱신** — `memory/MEMORY.md`
   - 결정/선호/맥락/교훈을 한 줄씩 append (80자 이내)
   - **이미 같은 내용이 Unsorted에 있으면 절대 추가 금지** (정확 매칭 + 의미 유사 둘 다 체크)
   - **위키 페이지 새로 만들지 마세요** — Unsorted 큐잉만
   - 추가할 게 없으면 건드리지 마세요 → `unsorted: no-op`

4. **wiki 승격** — `memory/MEMORY.md` `## Unsorted`에 항목이 있으면 `/wiki-promote` 로직 실행
   - Unsorted 항목마다: 카테고리 파싱 → `memory/wiki/{category}/` Grep으로 중복 검사 → 분기(new/partial/exact)
   - new → 위키 페이지 Write + MEMORY.md 인덱스 테이블 행 추가
   - partial → 기존 페이지 Edit (updated 갱신 + Changelog 추가)
   - exact → 스킵
   - 처리 완료 항목은 Unsorted에서 제거, Pages 카운트 갱신
   - Unsorted 비어 있으면 → `wiki: no-op`
   - 상세 절차는 `.claude/commands/wiki-promote.md` 참조

5. **pending.json 갱신** — `.claude/skills/_candidates/pending.json`
   - 3단계 성숙 모델: observed (count<3) → candidate (count≥3) → strong (count≥5)
   - 사용자가 "매번"/"반복"/"항상"/"자동화" 명시 → 즉시 candidate
   - 같은 도구 체인 항목 매칭 시:
     - **`sessions[]`에 오늘 날짜가 이미 있으면 → count 증가시키지 마라** (last_seen만 갱신, 승격 평가 스킵)
     - 오늘 날짜가 없으면 → count++ + sessions[]에 오늘 추가
   - 신규/카운트 변화 모두 없으면 → 파일 건드리지 마세요 → `pending: no-op`

6. **결과 한 줄 출력**
   - 모두 변경 없음: `wrap: 이미 처리됨 (no-op)`
   - 일부 변경: `wrap: daily {생성|append|no-op}, unsorted {+n|no-op}, wiki {+n 신규|~n 보강|no-op}, pending {신규명 (status)|count++|no-op}`

## 제약

- `session-end-prompt.md`의 모든 제약 동일 적용
- 데일리 메모 기존 내용 보존 (append만)
- pending.json 동일 패턴 + 같은 날짜는 count++ 금지 (멱등성 핵심)
- 의미 없는 trivial 세션이라도 데일리 한 줄은 남길 것 (단, 이미 있으면 no-op)
- 작업 끝나면 사용자에게 한 줄 보고만 (장황한 설명 금지)
