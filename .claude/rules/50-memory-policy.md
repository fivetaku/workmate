# Memory Policy

- **durable 지식**은 `memory/wiki/{category}/` 에 위키 페이지로 저장
- **위키 인덱스**는 `memory/MEMORY.md`
- **세션 이어받기**는 `memory/daily/YYYY-MM-DD.md`
- **운영 state** (가드 플래그, 체크포인트, 스킬 상태)는 `memory/state/*.yaml` 또는 `*.json`
- 긴 세션을 마치기 전에는 반드시 이어받기 메모를 남긴다
- 안정화된 지식만 위키 페이지로 승격 (임시 메모는 Unsorted → 다음 세션에 정리)

## 위키 카테고리
| 카테고리 | 용도 |
|---------|------|
| `decisions/` | 확정된 결정(업무 방식, 분석 방법론, 보고 주기 등) |
| `preferences/` | 사용자 선호, 응답 스타일, 용어, 호칭 |
| `domain-context/` | 현재 도메인의 회사/제품/프로세스/조직 맥락 |
| `data-patterns/` | 반복 데이터 인사이트, 이상치 패턴, 계절성 |
| `lessons/` | 반복된 실수, 함정, 교훈 |

## 쓰기 프로토콜 (Ingest)
1. `memory/MEMORY.md` 인덱스 확인 — 이미 있는 페이지인가?
2. 있으면 → 기존 페이지 Edit, frontmatter의 `updated` 갱신
3. 없으면 → 템플릿으로 새 페이지 Write, 인덱스에 행 추가
4. 관련 페이지에 cross-reference 양방향 갱신
5. 인덱스 헤더의 페이지 수 갱신

## 읽기 프로토콜 (Query) — 의무 사항

사용자 질문이 **결정·선호·기준값·과거 교훈·도메인 맥락**에 해당하면 답변 전에 반드시 아래를 수행한다.

1. `memory/wiki/` 디렉터리를 **Grep**으로 능동 검색 — 사용자 질문에서 핵심 키워드 2~3개를 뽑아 직접 Grep 실행
2. 매칭 파일이 있으면 **1~3개 Read** (컨텍스트 예산 보호)
3. 매칭 없으면 → `memory/MEMORY.md` 인덱스 테이블 스캔 (SessionStart에 이미 로드됨)
4. 그래도 없으면 → "아직 기록되지 않은 지식"이라고 사용자에게 알림
5. **컨텍스트 안의 recall만으로 답하지 않는다** — 위키가 source of truth
6. 위키 페이지를 읽었으면 답변에 출처 표시: `(참조: memory/wiki/{path})`

**트리거 키워드**: "이전에", "원래", "규칙이", "기준이", "어떻게 하기로", "전에 정한", "선호", "톤", "양식"
이런 표현이 나오면 위키 검색 의무가 발동한다.

## 위키 페이지 템플릿
```markdown
---
title: Page Title
category: decisions|preferences|domain-context|data-patterns|lessons
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
status: active|draft|archived|superseded
---

# Page Title

## Summary
한 문단. 인덱스 테이블에 표시되는 요약.

## Detail
전체 내용.

## Cross-references
- 관련: [다른 페이지](../category/slug.md)

## Changelog
- YYYY-MM-DD: 변경 내용
```

## PreCompact 긴급 저장
컨텍스트 압축이 임박했을 때:
1. 위키 페이지를 새로 만들지 **않는다** (도구 예산 부족)
2. `memory/MEMORY.md`의 `## Unsorted` 섹션에 한 줄 요약만 append
3. 다음 세션에서 위키 페이지로 정식 승격

## 능동적 저장 트리거
| 트리거 | 동작 |
|-------|------|
| 사용자가 선호/컨벤션을 말함 | `preferences/`에 위키 페이지 생성 |
| 사용자가 중요한 결정을 확정함 | `decisions/`에 위키 페이지 생성 |
| 같은 실수 3회 반복 | `lessons/`에 위키 페이지 생성 |
| 10턴 넘게 저장 없음 | 체크포인트 실행 |
| 사용자가 "기억해줘"/"remember this" | 즉시 저장 |
| 컨텍스트 압축 임박 | `## Unsorted`에 flush |

## 파일명 표준
- 날짜는 `YYYY-MM-DD` (ISO 8601)
- 위키 슬러그는 소문자-하이픈: `weekly-report-format.md`, `safety-stock-rule.md`
- 개인 이름은 파일명에 넣지 않는다
