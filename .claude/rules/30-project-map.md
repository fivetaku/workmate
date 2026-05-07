# Project Map

## 루트 레벨
- `README.md` — 워크스페이스 소개, 빠른 시작
- `INDEX.md` — 전체 구조 지도
- `CLAUDE.md` — 컨트롤 플레인 (rules import + 현재 도메인 특화 정보)
- `.claude/` — Claude Code 설정 (훅, 세션 체크리스트, 룰, 커맨드, 스킬)
- `memory/` — 누적 기억 (`MEMORY.md` + `wiki/` + `daily/` + `state/`)
- `references/` — 참조 문서 (용어집, 기준값, 양식, 프로세스). `/onboarding` Phase 4에서 자동 생성
- `reports/` — AI가 생성한 결과물 저장소

## 사용자 작업 공간 (PARA 스타일)
- `00-inbox/` — 아직 분류되지 않은 받은 파일 임시 보관. `/inbox-sorter`가 PARA 트리로 분류
- `10-projects/` — 진행 중인 프로젝트 문서 + 데이터
- `20-operations/` — 운영/업무 자료 + 데이터
- `30-knowledge/` — 학습/지식 자료
- `40-personal/` — 개인 작업 공간
- `50-resources/` — 외부 참고 자료
- `90-archive/` — 완료/보관 자료

**업무 데이터는 별도 `data/` 폴더가 아니라 PARA 트리 안에 위치합니다.** `/inbox-sorter`가 분류한 결과가 곧 데이터 위치.

## `.claude/` 구조
- `settings.json` — 훅 설정 (SessionStart, SessionEnd, PreCompact 등)
- `session/BOOT.md` — 세션 시작 체크리스트 (SessionStart 훅이 자동 cat)
- `scripts/` — 훅 스크립트 (session-end-wrap.py 등)
- `wrap-queue/` — SessionEnd 덤프 → SessionStart 처리 대기열
- `rules/00~80-*.md` — 9개 모듈화된 운영 규칙
- `commands/` — 슬래시 커맨드 (`/onboarding`, `/inbox-sorter`, `/wiki-promote` 등)
- `skills/` — 로컬 스킬 모음 + `_candidates/` (자동 발굴)

## `memory/` 구조
- `MEMORY.md` — 위키 인덱스 (카테고리 테이블 + Unsorted)
- `wiki/decisions/` — 결정 사항
- `wiki/preferences/` — 사용자 선호/컨벤션
- `wiki/domain-context/` — 현재 도메인 맥락
- `wiki/data-patterns/` — 반복 데이터 인사이트
- `wiki/lessons/` — 실수/교훈/반복 함정
- `daily/YYYY-MM-DD.md` — 세션 이어받기 메모
- `state/*.yaml` / `state/*.json` — 온보딩 상태, 가드 플래그, 체크포인트 등 운영 상태

## 빠른 이해 포인트
- `references/` + `reports/`는 비서가 실제 업무를 수행하는 핵심 영역
- `.claude/`는 비서의 행동 규칙과 실행 도구가 있는 영역
- `memory/`는 세션 간 연속성을 유지하는 영역 (wiki 검색은 Claude가 직접 Grep 수행)
- `00-inbox/` ~ `90-archive/`는 사용자가 업무 자료를 정리하는 작업 공간. 데이터도 여기에
