#!/bin/bash
# workmate 세션 래퍼 — 단순 디렉토리 진입용
# alias wm='bash /path/to/workmate/.claude/scripts/start-workmate.sh'
#
# NOTE: 세션 종료 시 자동 wrap은 settings.json의 SessionEnd 훅이 처리합니다.
#       이제 `wm`이든 그냥 `claude`든 어떤 방식으로 띄워도 종료 시 wrap이 작동합니다.
#       수동으로 wrap하려면 세션 안에서 `/wrap` 슬래시 커맨드를 호출하세요.

cd "$(dirname "$(dirname "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")")")"
claude
