---
description: workmate 업무공간을 처음 세팅하는 인터뷰 커맨드. 사람 정보 + 실제 자료 + 직무 맞춤 폴더까지 한 번에 세팅. "--reset", "--preset-reset", "--edit" 인수 지원.
allowed-tools: Read, Write, Edit, Bash, Glob, Skill, AskUserQuestion
---

`onboarding` 스킬을 실행합니다.

## 인수 처리

- `/onboarding` (인수 없음) → 기본 흐름 (상태 체크 후 Phase 0부터)
- `/onboarding --reset` → state 완전 초기화 후 Phase 0부터
- `/onboarding --preset-reset` → Phase 5만 단독 재실행 (폴더 프리셋 재제안)
- `/onboarding --edit` → Phase 1~2만 재실행 (담당자 정보 수정)

사용자가 입력한 인수를 그대로 `onboarding` 스킬에 전달하여 해당 모드로 진입합니다.

## 워크플로우

이 커맨드는 `.claude/skills/onboarding/SKILL.md`의 6 Phase 인터뷰를 그대로 실행합니다.

상세 흐름:
- Phase -1: `memory/state/onboarding.yaml` 상태 확인 및 분기 (재개/재온보딩/신규)
- Phase 0: 시작 안내
- Phase 1: 사람 정보 (이름, 소속, 직무, 직급, 보고 대상)
- Phase 2: 업무 맥락 (반복 업무, 보고 주기, 톤, 금기)
- Phase 3: `00-inbox/` 문서 연결 + `inbox-sorter` 체인 호출
- Phase 4: 직무 기준 재해석 + 확인
- Phase 5: 직무 맞춤 폴더 프리셋 제안 (한 번만)
- Phase 6: CLAUDE.md + memory/wiki/ + state YAML 저장

## 핵심 원칙

1. **3-패턴 분리**: 선택지 질문(AskUserQuestion) / 자유 입력(텍스트) / 작업 게이트("완료" 대기)
2. **폴더 프리셋 재제안 금지**: 한 번 승인하면 `re_prompt_on_start: false`로 차단
3. **중간 저장**: 각 Phase 완료 시 state 저장하여 세션 중단 시 재개 가능
4. **`.kkirikkiri/` 직접 참조 금지**: 직무별 레퍼런스는 `.claude/skills/onboarding/references/`의 가공된 문서만 사용
