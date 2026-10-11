#!/usr/bin/env python3
"""SessionEnd hook — .jsonl 세션 전체를 요약 markdown으로 변환.

claude 호출 0회. 구조적 JSON 파싱.
다음 SessionStart에서 claude가 이 요약을 읽고 의미 분석 수행.
"""

import json, glob, os, re
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]  # workmate/
WRAP_QUEUE = WORKSPACE / ".claude/wrap-queue"
PENDING = WORKSPACE / ".claude/skills/_candidates/pending.json"
DAILY_DIR = WORKSPACE / "memory/daily"
# 세션별로 이미 처리한 이벤트 수 — 재개(resume)된 세션을 처음부터 다시 덤프하지 않기 위함
OFFSETS = WORKSPACE / "memory/state/wrap-offsets.json"
# 워크스페이스 절대경로에서 Claude Code 프로젝트 디렉터리를 동적으로 생성
# ~/.claude/projects/-{sanitized_cwd}/
_sanitized = str(WORKSPACE).replace("/", "-").lstrip("-")
PROJECT_DIR = os.path.expanduser(f"~/.claude/projects/-{_sanitized}")

today = date.today().isoformat()
now = datetime.now().strftime("%H:%M")


def find_latest_log():
    pattern = os.path.join(PROJECT_DIR, "*.jsonl")
    logs = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return logs[0] if logs else None


def parse_jsonl(path):
    """전체 .jsonl을 파싱. Claude Code 이벤트 로그 형식."""
    events = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def extract_user_messages(events):
    """type: user 이벤트에서 메시지 텍스트 추출."""
    msgs = []
    for ev in events:
        if ev.get("type") != "user":
            continue
        msg = ev.get("message", {})
        content = msg.get("content", "")

        texts = []
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(block.get("text", ""))

        for text in texts:
            # system-reminder 제거
            clean = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL).strip()
            # command-name 등 태그 제거
            clean = re.sub(r"<[^>]+>.*?</[^>]+>", "", clean, flags=re.DOTALL).strip()
            if clean and len(clean) > 3:
                msgs.append(clean[:500])
    return msgs


def extract_tool_calls(events):
    """type: assistant 이벤트에서 tool_use 블록 추출."""
    tools = []
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        msg = ev.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name = block.get("name", "unknown")
            inp = block.get("input", {})
            desc = ""
            if "file_path" in inp:
                desc = inp["file_path"]
            elif "command" in inp:
                desc = str(inp["command"])[:120]
            elif "pattern" in inp:
                desc = str(inp["pattern"])[:80]
            elif "query" in inp:
                desc = str(inp["query"])[:80]
            elif "prompt" in inp:
                desc = str(inp["prompt"])[:80]
            elif "skill" in inp:
                desc = str(inp["skill"])
            tools.append({"name": name, "desc": desc})
    return tools


def extract_assistant_texts(events):
    """어시스턴트 텍스트 응답 추출 (결정/변경 키워드 포함 라인)."""
    decisions = []
    keywords = ["완료", "변경", "추가", "삭제", "수정", "생성", "적용", "결정",
                "확정", "패치", "정정", "갱신", "등록", "설치", "업데이트"]
    for ev in events:
        if ev.get("type") != "assistant":
            continue
        msg = ev.get("message", {})
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = block.get("text", "")
            for line in text.split("\n"):
                line = line.strip()
                if any(kw in line for kw in keywords) and 10 < len(line) < 200:
                    decisions.append(line)

    seen = set()
    unique = []
    for d in decisions:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique[:30]


def build_summary_markdown(log_path, user_msgs, tools, decisions):
    """요약 markdown 생성."""
    tool_names = [t["name"] for t in tools]
    unique_tools = list(dict.fromkeys(tool_names))
    tool_chain = " → ".join(unique_tools[:15])

    md = []
    md.append(f"# Session Summary — {today} {now}")
    md.append("")
    md.append(f"**Source**: `{os.path.basename(log_path)}`")
    md.append(f"**Tool calls**: {len(tools)} ({len(unique_tools)} unique)")
    md.append(f"**User turns**: {len(user_msgs)}")
    md.append("")

    md.append("## User Requests")
    for i, msg in enumerate(user_msgs, 1):
        first_line = msg.split("\n")[0][:200]
        md.append(f"{i}. {first_line}")
    md.append("")

    md.append("## Tool Chain")
    md.append(f"```\n{tool_chain}\n```")
    md.append("")

    md.append("## Key Tool Calls")
    seen_desc = set()
    for t in tools:
        if t["desc"] and t["desc"] not in seen_desc:
            seen_desc.add(t["desc"])
            md.append(f"- `{t['name']}`: {t['desc']}")
        if len(seen_desc) >= 40:
            break
    md.append("")

    if decisions:
        md.append("## Decisions & Changes")
        for d in decisions:
            md.append(f"- {d}")
        md.append("")

    all_user_text = " ".join(user_msgs)
    repeat_kw = set(re.findall(r"(자동화|매번|반복|항상|automate|every time|always)", all_user_text))
    if repeat_kw:
        md.append("## Repeat Keywords Detected")
        md.append(f"사용자가 다음 키워드를 사용: {', '.join(repeat_kw)}")
        md.append("")

    return "\n".join(md)


def load_offsets():
    try:
        with open(OFFSETS) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_offsets(offsets):
    OFFSETS.parent.mkdir(parents=True, exist_ok=True)
    with open(OFFSETS, "w") as f:
        json.dump(offsets, f, indent=2)


def update_pending(tools, user_msgs, session_id):
    """pending.json 갱신 (3단계 성숙 모델, 멱등성)."""
    tool_names = [t["name"] for t in tools]
    unique_tools = list(dict.fromkeys(tool_names))

    if len(unique_tools) < 3 or len(tools) < 3:
        return

    tool_chain = " → ".join(unique_tools[:8])
    tool_key = "-".join(sorted(unique_tools[:4]))

    try:
        with open(PENDING) as f:
            pending = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pending = []

    existing = next((p for p in pending if p.get("_tool_key") == tool_key), None)
    all_user_text = " ".join(user_msgs)
    has_keyword = bool(re.search(r"(자동화|매번|반복|항상)", all_user_text))

    if existing:
        seen_ids = existing.setdefault("_session_ids", [])
        if session_id in seen_ids:
            # 같은 세션을 이어서 연 경우 — 다른 날이어도 반복으로 세지 않는다
            existing["last_seen"] = today
            seen_ids = None
        sessions = existing.get("sessions", [])
        if seen_ids is None:
            pass
        elif today in sessions:
            seen_ids.append(session_id)
            existing["last_seen"] = today
        else:
            existing["count"] = existing.get("count", 1) + 1
            sessions.append(today)
            seen_ids.append(session_id)
            existing["sessions"] = sessions
            existing["last_seen"] = today
            if existing["count"] >= 5:
                existing["status"] = "strong"
            elif existing["count"] >= 3:
                existing["status"] = "candidate"
    else:
        pattern_name = tool_chain.replace(" → ", "-").lower()[:40]
        pending.append({
            "name": pattern_name,
            "trigger": "",
            "description": f"도구: {tool_chain}",
            "status": "candidate" if has_keyword else "observed",
            "count": 1,
            "sessions": [today],
            "first_seen": today,
            "last_seen": today,
            "evidence": f"{len(unique_tools)} unique tools, {len(tools)} total calls",
            "confidence": 0.3,
            "_tool_key": tool_key,
            "_session_ids": [session_id],
        })

    with open(PENDING, "w") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)


def write_daily_footer(tool_count, unique_count, user_count):
    """daily 메모에 mechanical footer 추가."""
    daily_path = DAILY_DIR / f"{today}.md"
    footer = f"\n---\n_auto: {now} session ended — {tool_count} tools ({unique_count} unique), {user_count} user turns_\n"

    if daily_path.exists():
        content = daily_path.read_text()
        if f"_auto: {now}" in content:
            return  # 멱등
        with open(daily_path, "a") as f:
            f.write(footer)
    else:
        daily_path.parent.mkdir(parents=True, exist_ok=True)
        daily_path.write_text(f"# {today} Session Handoff\n{footer}")


def main():
    log_path = find_latest_log()
    if not log_path:
        return

    all_events = parse_jsonl(log_path)
    if not all_events:
        return

    session_full_id = os.path.basename(log_path).replace(".jsonl", "")
    offsets = load_offsets()
    offset = offsets.get(session_full_id, 0)
    if offset > len(all_events):
        offset = 0  # 로그가 새로 쓰였으면 처음부터
    events = all_events[offset:]
    offsets[session_full_id] = len(all_events)
    save_offsets(offsets)
    if not events:
        return  # 지난 wrap 이후 새 내용 없음

    user_msgs = extract_user_messages(events)
    tools = extract_tool_calls(events)
    decisions = extract_assistant_texts(events)

    tool_names = [t["name"] for t in tools]
    unique_tools = list(dict.fromkeys(tool_names))

    write_daily_footer(len(tools), len(unique_tools), len(user_msgs))

    if len(unique_tools) < 3:
        return  # trivial session — daily footer만

    summary_md = build_summary_markdown(log_path, user_msgs, tools, decisions)
    WRAP_QUEUE.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    session_id = session_full_id[:12]
    summary_path = WRAP_QUEUE / f"{ts}-{session_id}.md"
    summary_path.write_text(summary_md)

    update_pending(tools, user_msgs, session_full_id)
    print(f"wrap: {summary_path.name} ({len(tools)} tools, {len(user_msgs)} turns)")


if __name__ == "__main__":
    main()
