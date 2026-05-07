# Tooling

## 도구 선택 순서
1. **내장 도구 우선**: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch, Agent
2. **파일 기반 작업**: xlsx/docx/pptx 스킬, data-analyst 스킬
3. **외부 데이터**: WebFetch 또는 적절한 MCP 커넥터
4. **반복 작업**: 기존 스킬 우선 → 없으면 `_candidates/`에 후보 등록

## 데이터 파일 작업 원칙
- CSV/엑셀을 읽을 때는 먼저 컬럼 구조를 출력해서 사용자에게 확인
- 숫자 집계는 반드시 **출처 파일명 + 집계 방식**을 함께 보고
- 파생 계산(KPI, 비율 등)은 `references/기준값.md`에 정의된 공식을 따른다
- 결과 파일은 `reports/` 하위에 `YYYY-MM-DD_{주제}.{ext}` 형식으로 저장

## 외부 영향 작업
- 외부로 나가는 작업(이메일, 캘린더, 슬랙 등)은 반드시 **draft → approve → execute** 순서
- 원시 자격 증명을 응답에 노출하지 않는다
- MCP 커넥터가 있으면 사용, 없으면 수동 작업 안내

## 스킬 재사용
- 새 작업 시작 전 기존 스킬이 있는지 확인 (전역 스킬 + 로컬 스킬 모두)
- 매칭되는 스킬이 있으면 즉시 invoke — 처음부터 짜지 않는다
- 매칭되지 않지만 자주 할 작업이면 `_candidates/pending.json`에 등록
