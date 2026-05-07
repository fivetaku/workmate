---
description: 이물 혼입 사고 분석 및 재발방지 대책서 자동 생성. "/foreign-matter-car"으로 실행. 초기보고 → SEM-EDX 해석 → DB 대조 → 작업지시서 교차검증 → 대책서(md/docx/pptx) 일괄 생성.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, Agent, Skill
---

foreign-matter-car 스킬을 실행합니다.

$ARGUMENTS가 있으면 (파일 경로 등) 바로 Phase 1(자료 수집)부터 실행하고, 없으면 필요한 파일(초기보고서, SEM-EDX 결과)을 질문합니다.
