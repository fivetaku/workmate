# INDEX — workmate 구조 안내

> **workmate**는 범용 업무 비서 프레임워크입니다. 아래는 전체 파일/폴더 지도입니다.

---

## 루트

```
workmate/
├── README.md           ← 프레임워크 소개, 빠른 시작
├── INDEX.md            ← 이 파일 (전체 구조 안내)
├── CLAUDE.md           ← 컨트롤 플레인 (rules/ import + 현재 도메인 정보)
├── .gitignore          ← 세션 데이터 제외 규칙
├── .claude/            ← Claude Code 설정 (훅, 룰, 스킬, 부트스트랩)
├── memory/             ← 세션 간 기억 (위키 인덱스 + daily + wiki)
├── data/               ← 현재 도메인 데이터 (샘플 또는 본인 데이터)
├── references/         ← 참조 문서 (용어집, 기준값, 양식, 프로세스)
└── reports/            ← AI가 생성한 결과물 저장소
```

---

## `.claude/` — Claude Code 설정

```
.claude/
├── settings.json       ← 훅 설정 (SessionStart / PreCompact / SessionEnd / SubagentStop)
├── session/
│   └── BOOT.md         ← 세션 시작 체크리스트 (SessionStart 훅이 자동 cat)
├── rules/              ← 9개 모듈화된 계약 문서 (CLAUDE.md가 import)
│   ├── 00-operating-system.md    ← 워크스페이스 OS 철학
│   ├── 10-identity.md            ← workmate 정체성
│   ├── 20-user-contract.md       ← 사용자 계약 (한국어, 업무 담당자)
│   ├── 30-project-map.md         ← 폴더 구조 설명
│   ├── 40-tooling.md             ← 도구 선택 원칙
│   ├── 50-memory-policy.md       ← 메모리 저장/조회 프로토콜
│   ├── 60-flow-policy.md         ← 커맨드/스킬/에이전트 라우팅
│   ├── 70-orchestration-policy.md ← 복잡도 tier, 에이전트 선택
│   └── 80-skill-self-healing.md  ← 스킬 에러 시 자동 패치 프로토콜
├── commands/           ← 슬래시 커맨드
│   └── onboarding.md   ← `/onboarding` — 사용자 맥락 수집
└── skills/             ← 로컬 스킬 모음
    └── _candidates/
        ├── README.md   ← 스킬 후보 라이프사이클 설명
        ├── pending.json ← SessionEnd 훅이 자동 발굴 (gitignore)
        └── backups/    ← 스킬 self-healing 백업 (gitignore)
```

---

## `memory/` — 3-Lane 기억 시스템

```
memory/
├── MEMORY.md           ← 위키 인덱스 (5개 카테고리 + Unsorted)
├── wiki/               ← durable 지식 — 카테고리별 위키 페이지
│   ├── decisions/      ← 확정된 업무 방식, 방법론, 결정
│   ├── preferences/    ← 사용자 선호, 응답 스타일, 용어, 호칭
│   ├── domain-context/ ← 현재 도메인(회사/제품/조직/프로세스) 맥락
│   ├── data-patterns/  ← 반복 데이터 인사이트, 이상치 패턴
│   └── lessons/        ← 반복된 실수, 함정, 교훈
└── daily/              ← continuity 이어받기 메모
    └── YYYY-MM-DD.md
```

### 훅이 자동으로 하는 일

| 훅 | 시점 | 동작 |
|---|-----|-----|
| **SessionStart** | 세션 시작 | BOOT.md + MEMORY.md + 오늘/어제 daily + pending.json 자동 출력 |
| **PreCompact** | 컨텍스트 압축 직전 | 세션 요약을 `.claude/wrap-queue/`에 저장 (다음 세션에서 반영) |
| **Stop** | 세션 종료 | 반복 패턴 감지 → pending.json에 스킬 후보 merge |
| **SubagentStop** | 서브에이전트 종료 | findings/risks/next actions 포함 확인 nudge |

---

## `data/` — 현재 도메인 데이터

> `data/`에 샘플 데이터를 넣어 바로 시험할 수 있습니다. 본인 도메인 데이터로 교체 가능합니다.

> `data/` 폴더에 본인 업무 데이터(CSV, xlsx 등)를 넣으면 비서가 분석할 수 있습니다. 형식 제한 없음.

---

## `references/` — 참조 문서

```
references/
├── 용어집.md      ← 도메인 용어, 코드 체계
├── 기준값.md      ← 핵심 KPI 판정 기준 (정상/주의/경고)
├── 보고서양식.md  ← 보고서 템플릿 (주간/월간 등)
└── 프로세스.md    ← 주요 업무 프로세스
```

> 도메인 교체 시 이 폴더 내용도 함께 교체합니다.

---

## `reports/` — 결과물

AI가 생성한 파일(분석 결과, 보고서 초안, xlsx/docx/pptx)이 저장됩니다. 파일명은 `YYYY-MM-DD_{주제}.{ext}` 형식 권장.

---

## 도메인 교체

workmate를 다른 업무에 쓰려면:

1. `data/` 내용을 본인 도메인 데이터로 교체
2. `references/`의 용어집/기준값/양식/프로세스를 새로 작성
3. `memory/wiki/domain-context/`에 새 도메인 페이지 작성
4. `/onboarding` 으로 사용자 맥락 재설정
5. `.claude/rules/`, `.claude/session/`, `.claude/skills/_candidates/`, 훅, 메모리 시스템은 **그대로** 재사용
