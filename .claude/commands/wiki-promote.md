---
description: memory/MEMORY.md Unsorted 큐의 항목을 정식 위키 페이지로 승격 (중복 감지 포함)
---

# /wiki-promote

`memory/MEMORY.md`의 `## Unsorted` 섹션에 쌓인 항목을 `memory/wiki/{category}/`의 정식 위키 페이지로 승격합니다. **검색-전-쓰기** 로직으로 기존 페이지와 의미가 겹치면 Edit, 없으면 Write합니다.

## 핵심 원칙

- **중복 쓰지 말 것.** 새 페이지 생성 전 반드시 해당 카테고리 디렉터리를 Grep → 관련 후보 Read → 의미 중복 판정
- **인덱스는 페이지와 한 쌍.** 새 페이지를 Write하면 반드시 `memory/MEMORY.md`의 해당 카테고리 테이블에도 행을 추가
- **Unsorted는 처리 완료 라인만 제거.** 실패한 라인은 남겨서 다음 번 재시도
- **최대 10개 항목만 한 번에 처리.** 토큰 예산 보호

## 수행 순서

### Step 1. Unsorted 큐 읽기

1. `memory/MEMORY.md` Read
2. `## Unsorted` 섹션의 각 라인 파싱
3. 라인 형식 기대값: `- {카테고리}: {내용} ({YYYY-MM-DD})`
4. 카테고리 → 폴더 매핑:

| 라인의 prefix | 폴더 |
|-------------|------|
| `선호:` | `preferences` |
| `결정:` | `decisions` |
| `맥락:` / `도메인:` | `domain-context` |
| `교훈:` / `실수:` / `함정:` | `lessons` |
| `패턴:` / `데이터:` | `data-patterns` |

prefix가 없거나 모호하면 사용자에게 1회 확인 후 진행.

### Step 2. 각 항목 순차 처리

각 Unsorted 라인에 대해:

#### 2-A. 키워드 추출
- 라인 내용에서 의미 있는 명사·키워드 2~4개
- 불용어 제거 (이것, 저것, 있는, 하는 등)

#### 2-B. 중복 검사 (검색-전-쓰기)

1. `memory/wiki/{category}/` 디렉터리를 **Grep**으로 스캔 — 키워드 OR 패턴
2. 매칭 파일 0~2개를 **Read**
3. 판정:

| 판정 | 조건 | 동작 |
|-----|------|-----|
| **exact_match** | 기존 페이지의 Summary/Detail이 의미 100% 동일 | 새로 만들지 않음. Unsorted에서만 제거 |
| **partial_match** | 같은 주제지만 새로운 맥락·근거·사례가 추가 | 기존 페이지 Edit |
| **new** | 매칭 없음 또는 주제가 다름 | 새 페이지 Write |

판정이 애매하면 **partial_match** 쪽으로 기울일 것. 쓸모 없는 새 페이지를 만드는 것보다 기존 페이지 보강이 안전.

#### 2-C. 분기 실행

**new 케이스**:
1. 파일 경로: `memory/wiki/{category}/{slug}.md`
   - slug: kebab-case 소문자. 한국어 키워드는 원문 그대로 + 하이픈 (예: `lecture-full-script.md`, `mic-learning-principle.md`)
   - 기존 파일과 이름 충돌 시 `{slug}-2.md`, `{slug}-3.md` 순으로
2. 파일 내용은 아래 **위키 페이지 템플릿**을 채워서 Write
3. `memory/MEMORY.md`의 해당 카테고리 테이블에 행 추가:
   ```
   | [{title}]({category}/{slug}.md) | {summary 한 문장} | {YYYY-MM-DD} |
   ```

**partial_match 케이스**:
1. 기존 페이지 Edit:
   - frontmatter의 `updated:` → 오늘 날짜
   - `## Detail` 섹션 끝에 새 맥락 한 문단 append
   - `## Changelog` 섹션에 `- {YYYY-MM-DD}: Unsorted 승격 보강 — {한 줄 요약}` 추가
2. `memory/MEMORY.md` 해당 행의 Updated 열만 오늘 날짜로 Edit

**exact_match 케이스**:
- 파일 변경 없음. Unsorted에서만 제거

#### 2-D. Unsorted 정리
- 처리 완료한 라인은 `memory/MEMORY.md`의 `## Unsorted` 섹션에서 Edit으로 제거

### Step 3. 인덱스 헤더 갱신
- `memory/MEMORY.md` 상단의 `> Last updated: YYYY-MM-DD | Pages: N`을 오늘 날짜 + 현재 페이지 수(전체 `memory/wiki/**/*.md` 파일 수)로 갱신

### Step 4. 결과 리포트 (한 줄)

```
wiki-promote: +{new}개 생성, ~{partial}개 보강, ={exact}개 스킵, Unsorted {before}→{after}
```

실패 항목이 있으면 한 줄 추가:
```
실패: {항목 내용 요약} ({사유})
```

## 위키 페이지 템플릿

```markdown
---
title: {짧은 제목 — 명사구}
category: {preferences|decisions|domain-context|lessons|data-patterns}
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tags: [{tag1}, {tag2}]
status: active
---

# {title}

## Summary
{한 문장 요약 — MEMORY.md 테이블에 그대로 표시될 것}

## Detail
{상세 설명 — Unsorted 라인의 맥락을 풀어서 2~5문단. 언제 이 규칙이 적용되는지, 왜 이렇게 결정했는지, 예시까지.}

## Cross-references
- (없음 — 다른 페이지와 교차 참조가 생기면 여기에 추가)

## Changelog
- {YYYY-MM-DD}: 초기 등록 (Unsorted 승격)
```

## 제약

| 규칙 | 세부 |
|------|------|
| 최대 처리 항목 | 한 번 실행당 10개 |
| 항목당 Read | 중복 검사용 최대 3회 |
| 슬러그 규칙 | kebab-case 소문자, 한국어는 원문 유지, 영문 단어는 소문자 |
| 인덱스 동기화 | 새 페이지 Write 시 MEMORY.md 테이블 행 추가 필수 |
| 파일 덮어쓰기 금지 | 기존 파일 이름 충돌 시 `-2`, `-3` 접미사 |
| Unsorted 부분 실패 | 실패 라인은 남겨두고 성공 라인만 제거 |
| 결과는 한 줄 | 장황한 설명 금지 |

## 왜 `/wrap`이 아닌 별도 커맨드인가

- `/wrap`은 **토큰 예산 빡빡** (최대 12 tool calls) — 승격 로직은 검색·판정·쓰기가 섞여 비용 큼
- 승격은 **주간 단위 cadence가 자연스러움** — 매 세션이 아니라 금요일/주말에 몰아서
- Unsorted를 중간 버퍼로 두면 "바로 승격 vs 관망" 판단을 나중에 해도 됨
