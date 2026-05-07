# Flow Policy

- **Commands**는 사용자 진입점이다. 예: `/onboarding`, `/inbox-sorter`, `/daily-note`
- **Skills**는 재사용 가능한 능력이다. 예: `data-analyst`, `content-draft`, `xlsx`, `skill-builder`
- **Hooks**는 라이프사이클 nudge다. 핵심 로직을 담지 않는다
- 큰 작업 후에는 반드시: 검증 → 메모리 저장 → 이어받기 메모

## Command vs Skill
- 사용자가 명시적으로 슬래시 커맨드를 부르면 해당 command를 우선 실행한다
- 자연어 요청이 스킬 트리거와 맞으면 해당 skill을 우선 실행한다
- command는 주로 초기 세팅, 파일 정리, 보조 진입점에 사용한다
- skill은 분석, 문서 생성, 검증, 자동화 같은 재사용 흐름에 사용한다

## Skill Awareness
- 멀티스텝 작업을 시작하기 전, **기존 스킬 스캔**이 먼저다
- 매칭되는 스킬이 있으면 즉시 invoke — 임시로 새로 짜지 않는다
- 부분 매칭이면 기존 스킬을 확장한다. 복제 금지
- 사용자 요청이 스킬 트리거 키워드와 일치하면 즉시 해당 스킬 호출

## 대표 라우팅 예시
- 데이터 분석 요청 → `data-analyst`
- 보고서 초안 요청 → `content-draft`
- 엑셀/워드/PPT 생성 요청 → `xlsx` / `docx` / `pptx`
- 받은 파일 정리 요청 → `/inbox-sorter`
- 처음 세팅 / 내 비서 만들기 → `/onboarding`
- 검증 요청 → `/cross-check` 또는 `cross-check`
- 반복 업무 자동화 요청 → `skill-builder`

## Skill Candidate Lifecycle — 3단계 성숙 모델

스킬 후보는 **즉시 제안하지 않는다**. 충분한 관찰을 거쳐 성숙해야 제안한다.

### pending.json 항목 스키마
```json
{
  "name": "스킬 이름",
  "trigger": "한국어 활성화 문구",
  "description": "무엇을 하는 스킬인지",
  "status": "observed | candidate | strong",
  "count": 1,
  "sessions": ["2026-04-08"],
  "first_seen": "2026-04-08",
  "last_seen": "2026-04-08",
  "evidence": "세션 로그 근거",
  "confidence": 0.0
}
```

### 3단계

| 단계 | 조건 | status | 사용자에게 표시 |
|------|------|--------|----------------|
| **관찰 (Observed)** | 세션 1~2회에서 비슷한 패턴 감지 | `observed` | 표시 안 함 (조용히 누적) |
| **후보 (Candidate)** | 3회 이상 감지 OR 사용자가 "매번/반복/항상" 명시 | `candidate` | 다음 세션 시작 시 제안: "이 작업이 N회 반복됐습니다. 스킬로 만들까요?" |
| **강력 후보 (Strong)** | 5회 이상 OR 사용자가 "자동화해줘" 직접 요청 | `strong` | 적극 제안 |

### 승격 조건 상세

| 기준 | observed 유지 | candidate로 승격 |
|------|-------------|-----------------|
| 동일 패턴 감지 횟수 | 1~2회 | **3회 이상** |
| 도구 체인 복잡도 | 1~2개 도구 | **3개 이상 도구** |
| 세션 간 반복 | 같은 세션 안에서만 | **2개 이상 다른 세션에서** |
| 사용자 반복 키워드 | 없음 | "매번"/"반복"/"항상" 사용 시 → **즉시 candidate** |
| 사용자 명시 요청 | - | "자동화해줘"/"스킬로 만들어" → **단계 무시, 바로 skill-builder** |

### Stop 훅 동작
1. 패턴 감지 시 pending.json을 Read
2. 이름이 같은 기존 항목이 있으면 → `count++`, `sessions[]`에 오늘 날짜 추가, `last_seen` 갱신
3. 기존 항목이 없으면 → `status: "observed"`, `count: 1`로 신규 추가
4. `count >= 3` 이면 → `status: "candidate"`로 승격
5. `count >= 5` 이면 → `status: "strong"`으로 승격

### SessionStart 훅 표시 규칙
- `status: "observed"` → **표시하지 않음** (사용자를 방해하지 않는다)
- `status: "candidate"` → 간단히 제안: "N회 반복된 작업입니다. 스킬로 만들까요?"
- `status: "strong"` → 적극 제안: "이 작업은 스킬로 만들면 매번 한 마디로 끝납니다"

### Promotion (승격)
1. 사용자 승인 시 `skill-builder` 또는 `skillers-suda` 호출해서 정식 스킬 생성
2. 새 스킬 생성 완료 즉시 `SKILLS_INDEX.md`에 행 추가 (트리거, 입력, 출력, 적합 상황 포함). 이 단계를 건너뛰면 council이 새 스킬을 인식하지 못함
3. pending.json에서 해당 항목 제거

### Cleanup
- 거절된 후보: pending.json에서 제거 또는 `status: "rejected"` 표시 (재감지 방지)
- 60일 이상 count 변화 없는 observed: 자동 제거 대상 (주간 리뷰 시)

## Memory-aware Flow
- 과거 결정 / 선호 / 도메인 맥락 관련 질문 전에는 위키를 먼저 본다
  1. `memory/MEMORY.md` 인덱스 확인
  2. 관련 위키 페이지 최대 3개 Read
  3. 없으면 `memory/wiki/` Grep
- 지속 가능한 지식이 생성되면 위키 페이지 생성 또는 갱신
- 세션 종료 시 이어받기 메모 작성

## Skill Error Handling
- 스킬 실행 실패 시 `80-skill-self-healing.md` 프로토콜을 따른다
- 같은 스킬이 3회 이상 실패하면 pending.json에 `"reason": "repeated-failure"` 플래그를 단다

## Unused Skill Hygiene
- 주간 리뷰에서 30일 이상 미사용 스킬 감지
- `[dormant]` 플래그만 달고, 자동 삭제 금지 — 사용자 승인 필수
