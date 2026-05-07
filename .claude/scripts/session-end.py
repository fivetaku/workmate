#!/usr/bin/env python3
"""세션 종료 후 자동 실행 — Claude로 업무 패턴 분석 + pending.json 업데이트"""

import json, glob, os, re, subprocess
from datetime import date
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]  # workmate/
PENDING = WORKSPACE / ".claude/skills/_candidates/pending.json"
# 워크스페이스 절대경로에서 Claude Code 프로젝트 디렉터리를 동적으로 생성
# ~/.claude/projects/-{sanitized_cwd}/
_sanitized = str(WORKSPACE).replace("/", "-").lstrip("-")
_project_dir = os.path.expanduser(f"~/.claude/projects/-{_sanitized}")
PROJECT_PATTERN = os.path.join(_project_dir, "*.jsonl")

today = date.today().isoformat()


def find_latest_log():
    logs = sorted(glob.glob(PROJECT_PATTERN), key=os.path.getmtime, reverse=True)
    return logs[0] if logs else None


def read_last_lines(path, n=300):
    with open(path) as f:
        return f.readlines()[-n:]


def extract_session_summary(raw):
    """세션에서 사용자 메시지 + 도구 체인 추출"""
    # 도구 호출 수
    tool_calls = len(re.findall(r'"tool_name"', raw))
    if tool_calls < 3:
        return None

    # 도구 이름 추출
    tool_names = re.findall(r'"tool_name":"([^"]+)"', raw)
    unique_tools = list(dict.fromkeys(tool_names))
    if len(set(tool_names)) < 3:
        return None

    tool_chain = " → ".join(unique_tools[:8])

    # 사용자 메시지 추출 (최대 500자)
    user_msgs = re.findall(r'"role":"user"[^}]*"content":"([^"]{1,200})"', raw)
    user_text = " | ".join(user_msgs[-5:])[:500]  # 최근 5개, 500자 제한

    return {
        "tool_chain": tool_chain,
        "user_text": user_text,
        "unique_tools": len(set(tool_names)),
        "total_calls": tool_calls,
    }


def generate_pattern_name(summary):
    """claude -p 로 업무 패턴명 자연어 생성"""
    prompt = (
        "아래 세션 정보를 보고, 이 작업을 한국어 업무명 7단어 이내로 요약해줘. "
        "설명 없이 업무명만 출력해.\n\n"
        f"사용자 요청: {summary['user_text']}\n"
        f"사용된 도구: {summary['tool_chain']}\n\n"
        "예시: '불량 데이터 분석 및 대책서 작성', '납기 지연 거래처 현황 정리', '주간 생산 보고서 엑셀 생성'"
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True, timeout=30,
            cwd=str(WORKSPACE),
        )
        name = result.stdout.strip().strip('"').strip("'")
        if name and len(name) < 50:
            return name
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  ⚠ claude -p 실패 ({e}), 도구 기반 이름으로 fallback")

    # fallback: 도구 이름 기반
    tools = summary["tool_chain"].replace(" → ", "-").lower()[:40]
    return tools


def check_user_keywords(raw):
    """사용자가 '매번'/'반복'/'항상'/'자동화' 명시적 언급 체크"""
    user_blocks = re.findall(r'"role":"user"[^}]*"content":"([^"]*)"', raw)
    user_text = " ".join(user_blocks)
    keywords = re.findall(r"(자동화|매번|반복|항상|automate|every time|always)", user_text)
    return len(keywords) > 0


def update_pending(pattern_name, summary, has_keyword):
    """3단계 성숙 모델로 pending.json 업데이트"""
    try:
        with open(PENDING) as f:
            pending = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pending = []

    # 이름 유사도로 기존 항목 매칭 (정확히 같지 않아도 도구 체인이 같으면 매칭)
    tool_key = "-".join(sorted(summary["tool_chain"].replace(" → ", " ").split())[:4])
    existing = next(
        (p for p in pending if p.get("_tool_key") == tool_key),
        None
    )

    if existing:
        existing["count"] = existing.get("count", 1) + 1
        sessions = existing.get("sessions", [])
        if today not in sessions:
            sessions.append(today)
        existing["sessions"] = sessions
        existing["last_seen"] = today
        # 더 좋은 이름이 생기면 업데이트
        if pattern_name and len(pattern_name) > len(existing.get("name", "")):
            existing["name"] = pattern_name

        if existing["count"] >= 5:
            existing["status"] = "strong"
        elif existing["count"] >= 3:
            existing["status"] = "candidate"

        print(f"  ↑ {existing['name']}: count={existing['count']}, status={existing['status']}")
    else:
        status = "candidate" if has_keyword else "observed"
        pending.append({
            "name": pattern_name,
            "trigger": "",
            "description": f"도구: {summary['tool_chain']}",
            "status": status,
            "count": 1,
            "sessions": [today],
            "first_seen": today,
            "last_seen": today,
            "evidence": f"{summary['unique_tools']} unique tools, {summary['total_calls']} total calls",
            "confidence": 0.3,
            "_tool_key": tool_key,  # 내부 매칭용
        })
        print(f"  + {pattern_name}: status={status} (new)")

    with open(PENDING, "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    return pending


def main():
    print("\n📊 workmate session-end: 스킬 후보 감지 중...")

    log_path = find_latest_log()
    if not log_path:
        print("  (세션 로그 없음 — 스킵)")
        return

    lines = read_last_lines(log_path)
    raw = "".join(lines)

    summary = extract_session_summary(raw)
    if not summary:
        tool_calls = len(re.findall(r'"tool_name"', raw))
        print(f"  (도구 {tool_calls}회 — 패턴 감지 기준 미달, 스킵)")
        return

    print(f"  도구 체인: {summary['tool_chain']}")
    print(f"  사용자 요청: {summary['user_text'][:80]}...")

    # Claude로 자연어 패턴명 생성
    print("  🤖 업무명 생성 중...")
    pattern_name = generate_pattern_name(summary)
    print(f"  → {pattern_name}")

    has_keyword = check_user_keywords(raw)
    pending = update_pending(pattern_name, summary, has_keyword)

    # 요약
    candidates = [p for p in pending if p["status"] in ("candidate", "strong")]
    observed = [p for p in pending if p["status"] == "observed"]
    print(f"\n  총 {len(pending)}개 항목 (candidate/strong: {len(candidates)}, observed: {len(observed)})")
    if candidates:
        print("  🔔 다음 세션에서 후보 제안됨:")
        for c in candidates:
            print(f"     - {c['name']} (count={c['count']}, status={c['status']})")
    print()


if __name__ == "__main__":
    main()
