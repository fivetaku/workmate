---
title: macOS/Windows/WSL 호환성 체크리스트
category: lessons
created: 2026-05-06
updated: 2026-05-06
tags: [wsl, windows, macos, cross-platform, ms-office, environment, compatibility]
status: active
---

# macOS/Windows/WSL 호환성 체크리스트

## Summary
workmate 스킬을 다중 OS(macOS/Windows native/WSL)에서 안정 동작시키기 위한 의존성·경로·인코딩 함정과 해결책 정리. 2026-05-06 호환성 패치(LibreOffice 의존 제거, MS Office 단일화) 결과 반영.

## Detail

### 핵심 결정 (2026-05-06)
- **LibreOffice 의존 완전 제거**. 사용자 환경에서 잘 사용되지 않고, MS Office는 모든 데스크톱에 보편적.
- **MS Office 단일 의존**. xlwings(Python) 우선, 환경별 fallback 자동 선택.
- **OS-specific 명령어**(pbcopy, open 등)는 자동 감지 분기로 교체.

### 1. 시스템 의존성 (사전 설치)

| 의존성 | macOS | Windows native | WSL |
|--------|-------|----------------|-----|
| MS Office (Excel) | App Store / MS 다운로드 | MS Office 설치 | Windows 호스트에 설치 |
| Python xlwings | `pip install xlwings` | `pip install xlwings` | Windows Python에 설치 권장 |
| Python (workmate 자체) | brew/python3 | python.org | apt install python3 |
| Node.js | brew install node | nodejs.org | apt install nodejs npm |
| pandoc | brew install pandoc | choco install pandoc | apt install pandoc |
| 한글 폰트 | 시스템 기본 (Apple SD Gothic Neo) | 시스템 기본 (맑은 고딕) | apt install fonts-nanum |
| 클립보드 도구 | pbcopy (기본) | clip.exe (기본) | clip.exe 자동 사용 또는 xclip |
| 브라우저 오픈 | open (기본) | start (기본) | wslview (apt install wslu) |

### 2. 자동 fallback이 적용된 영역

**recalc.py (재무 모델 4종 — dcf/lbo/comps/3-statement)**:
1. xlwings (Python) — 1순위
2. WSL → Windows Excel.exe (`/mnt/c/Program Files/Microsoft Office/...`)
3. macOS Excel.app via osascript (AppleScript)
4. 친절한 설치 안내 에러

**geeknews (글로벌 스킬)**:
- 클립보드: `pbcopy` → `clip.exe` → `xclip` → `xsel`
- 브라우저 오픈: `open` → `wslview` → `xdg-open` → `explorer.exe`
- 헬퍼 함수 `__copy_and_open` 추가됨

**excel-to-report 한글 폰트**:
1. Windows malgun.ttf (`/mnt/c/Windows/Fonts/`)
2. macOS Apple SD Gothic Neo
3. Linux Nanum Gothic
4. DejaVu Sans (한글 깨짐 경고)

### 3. WSL 사용 시 권장 alias (~/.bashrc)

```bash
# macOS 명령어 호환성
alias pbcopy='clip.exe'
alias pbpaste='powershell.exe -Command Get-Clipboard'
alias open='wslview'  # 또는 explorer.exe

# Windows 경로 헬퍼
alias winpath='wslpath -w'
alias unixpath='wslpath -u'
```

### 4. 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| recalc.py "MS Office not found" | xlwings 미설치 + Office 경로 못 찾음 | `pip install xlwings` 또는 환경별 가이드 따라 설치 |
| 차트의 한글이 □□□ 로 표시 | 한글 폰트 미감지 | WSL: `apt install fonts-nanum`, Windows: 맑은 고딕 자동 사용 |
| `open: command not found` (WSL) | macOS 명령 그대로 사용 | `wslview` 사용 또는 위 alias 적용 |
| `pbcopy: command not found` (WSL) | macOS 명령 그대로 사용 | `clip.exe` 사용 또는 위 alias 적용 |
| Stat 차이 (file size) | BSD vs GNU stat | `stat -f%z 2>/dev/null \|\| stat -c%s` 패턴 사용 |
| LibreOffice 관련 에러 | 옛날 코드/문서 잔재 | 2026-05-06 패치 이후 발생하면 issue 등록 |

### 5. 새 스킬 작성 시 호환성 체크리스트

스킬 추가 시 다음을 확인:
- [ ] macOS 전용 명령어(`pbcopy`, `open`, `say`, `osascript`, `mdfind`) 사용 시 fallback 분기 필수
- [ ] 절대 경로(`/Applications/`, `/opt/homebrew`, `/mnt/c/`) 하드코딩 금지 — `shutil.which()` 또는 환경 감지 우선
- [ ] BSD vs GNU 차이가 있는 명령(`stat`, `date`, `readlink`, `sed -i`) → 양쪽 시도 fallback
- [ ] 한글 폰트 사용 시 위 4단계 fallback 적용
- [ ] Python `pip install` 시 venv 또는 `--break-system-packages` 검토
- [ ] 외부 CLI 의존 시 SKILL.md 상단에 preflight 체크 추가

## Cross-references
- 관련 룰: [40-tooling.md](../../../.claude/rules/40-tooling.md) — 도구 선택 순서
- 관련 룰: [50-memory-policy.md](../../../.claude/rules/50-memory-policy.md) — 위키 작성 표준
- 관련 룰: [80-skill-self-healing.md](../../../.claude/rules/80-skill-self-healing.md) — 스킬 패치 프로토콜

## Changelog
- 2026-05-06: 초안 작성. LibreOffice 의존성 제거, MS Office 단일화 패치 후속 정리. recalc.py 4종, geeknews, excel-to-report 패치 결과 반영.
