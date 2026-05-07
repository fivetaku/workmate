---
description: 회의 전 Gmail+Calendar 교차 분석으로 사전 브리핑을 생성합니다. "/meeting-brief"으로 실행. 특정 회의명을 인자로 전달할 수 있습니다.
allowed-tools: mcp__claude_ai_Gmail__gmail_search_messages, mcp__claude_ai_Gmail__gmail_read_message, mcp__claude_ai_Google_Calendar__gcal_list_events, Read, Glob, Grep
---

meeting-brief 스킬을 실행합니다.

$ARGUMENTS가 있으면 해당 회의명을 타겟으로 브리핑을 생성하고, 없으면 오늘 가장 임박한 회의를 자동 선택합니다.
