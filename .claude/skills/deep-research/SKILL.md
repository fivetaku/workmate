---
name: deep-research
description: This skill should be used when the user asks to "research this", "investigate", "market analysis", "competitive analysis", "technical research", "deep research", "리서치해줘", "조사해줘", "경쟁 분석", "기술 조사", "딥리서치", or any structured research request.
arguments:
  - name: topic
    description: Research topic or question.
    default: ""
  - name: depth
    description: "lite" (3-5 questions, quick) or "deep" (parallel agents, triangulation). Default is "lite".
    default: "lite"
  - name: output_dir
    description: Output directory for research files.
    default: "./research"
tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Agent
---

# Deep Research

> If you do not know, research first. Do not pretend to know.

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

If topic is provided, start with Step 1. If not, ask what to research.

---

## Workflow

### Step 1: Scope the research
**Type**: prompt

From `$ARGUMENTS`, define:
- **Topic**: what exactly to research
- **Key questions**: 3-5 specific questions to answer
- **Boundaries**: what is in scope vs out of scope
- **Depth**: lite or deep mode

If topic is vague, ask ONE clarifying question before proceeding.

### Step 2: Plan retrieval (Deep mode only)
**Type**: prompt

For deep mode, design a retrieval plan:
- Assign each question to a search strategy (web, academic, documentation, code)
- Identify 2-3 source types per question (official docs, blog posts, papers, repos)
- Plan parallel agent assignments

### Step 3: Execute research
**Type**: script + prompt

**Lite mode:**
- Use WebSearch for each key question
- WebFetch top 2-3 results per question
- Extract relevant evidence and note sources

**Deep mode:**
- Spawn 2-3 research agents in parallel using Agent tool
- Each agent handles a subset of questions
- Each agent returns: findings, sources, confidence level, gaps

```bash
# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"
```

### Step 4: Triangulate sources
**Type**: review

For each finding:
- Check if 2+ independent sources confirm it
- Mark single-source claims as "unverified"
- Flag contradictions between sources
- Note recency — prefer sources from last 12 months

### Step 5: Synthesize and output
**Type**: generate

Write findings to `{output_dir}/`:

**Main report** (`{topic-slug}-research.md`):
```markdown
# Research: {topic}
Date: {date}
Depth: {lite/deep}

## Key Findings
1. {finding with source}
2. {finding with source}

## Detailed Analysis
### {Question 1}
{evidence and analysis}

### {Question 2}
{evidence and analysis}

## Sources
- [{title}]({url}) — {relevance note}

## Gaps and Uncertainties
- {what we couldn't confirm}
```

Report to user:
```
Research complete: {topic}
Depth: {lite/deep}
Questions answered: {N}/{total}
Sources consulted: {N}
Output: {output_dir}/{filename}
```

---

## Edge Cases

**No relevant results**: Report "Limited sources found for this topic" and suggest alternative search terms or narrower scope.

**Conflicting sources**: Present both sides clearly. Do not pick a winner without evidence. Mark as "contested."

**Rate-limited search**: If WebSearch fails, wait and retry once. If still failing, use cached/known information and mark as "incomplete."

**Very broad topic**: Suggest narrowing. "This topic is too broad for {depth} mode. Suggested sub-topics: ..."

**Sensitive/controversial topics**: Present facts neutrally. Cite all sides. Do not take positions.

---

## Integration Points

- **content-draft**: Research → content pipeline. Research output feeds into blog posts, presentations.
- **data-analyst**: If research involves data files, delegate to data-analyst for statistical analysis.
- **meeting-notes**: Research findings can be prepared as meeting discussion material.
- **memory-capture**: Promote key research findings to durable memory if they inform ongoing project decisions.
- **morning-briefing**: Scheduled research updates can feed into daily briefings via Cloud Tasks.
