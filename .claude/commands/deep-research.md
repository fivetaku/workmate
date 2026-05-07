---
description: 딥리서치 스킬 실행. "리서치해줘", "조사해줘", "딥리서치" 등으로도 자동 트리거.
allowed-tools: Read, Write, Bash, Glob, Agent, WebSearch, WebFetch
---

deep-research 스킬을 실행합니다.

$ARGUMENTS가 있으면 해당 주제로 바로 리서치를 시작합니다. 없으면 리서치 주제를 물어봅니다.
기본 모드는 lite (빠른 조사). "깊게", "deep", "상세하게" 등이 포함되면 deep 모드로 전환합니다.
