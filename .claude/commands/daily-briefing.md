---
description: Gmail과 Google Calendar에서 오늘의 일정·메일을 확인하고 데일리 브리핑을 제공합니다. "/daily-briefing"으로 실행.
allowed-tools: mcp__claude_ai_Gmail__gmail_search_messages, mcp__claude_ai_Gmail__gmail_read_message, mcp__claude_ai_Gmail__gmail_read_thread, mcp__claude_ai_Google_Calendar__gcal_list_events, mcp__claude_ai_Google_Calendar__gcal_list_calendars, Bash, Read
---

daily-briefing 스킬을 실행합니다.

$ARGUMENTS가 있으면 모드로 사용합니다:
- "detailed" 또는 "상세" → detailed 모드 (메일 본문 요약 포함)
- 그 외 또는 빈 값 → quick 모드 (기본값)

즉시 실행하세요. 추가 질문 없이 Gmail과 Google Calendar를 조회하여 오늘의 데일리 브리핑을 제공합니다.
