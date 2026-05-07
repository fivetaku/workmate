---
name: content-draft
description: This skill should be used when the user asks to "write a blog post", "draft content", "write an SNS post", "newsletter draft", "write an article", "블로그 써줘", "콘텐츠 작성", "SNS 글 써줘", "뉴스레터 초안", "글 써줘", or any content creation request.
arguments:
  - name: type
    description: "blog", "sns", "newsletter", "article", "thread". Default is "blog".
    default: "blog"
  - name: topic
    description: What to write about.
    default: ""
  - name: tone
    description: "professional", "casual", "technical", "storytelling". Default is "professional".
    default: "professional"
tools:
  - Read
  - Write
  - WebSearch
  - WebFetch
---

# Content Draft

> Generate structured content drafts — blog posts, social media, newsletters, articles. Research-backed, tone-aware, format-ready.

---

## WHEN TRIGGERED - EXECUTE IMMEDIATELY

If topic is provided, start researching and drafting. If not, ask what to write.

---

## Workflow

### Step 1: Understand requirements
**Type**: prompt

From `$ARGUMENTS`, extract:
- **Type**: blog / sns / newsletter / article / thread
- **Topic**: subject matter
- **Tone**: professional / casual / technical / storytelling
- **Length**: short (300w) / medium (800w) / long (1500w+)
- **Audience**: who is reading this

If any are missing and not inferrable, ask ONE clarifying question.

### Step 2: Research (if needed)
**Type**: prompt

For topics requiring current information:
- Use WebSearch to find 3-5 relevant sources
- Read key points from each source
- Note facts, statistics, quotes to reference

For opinion/personal pieces, skip research.

### Step 3: Create outline
**Type**: prompt

Generate a structured outline based on content type:

**Blog post:**
```
1. Hook (opening line that grabs attention)
2. Context (why this matters)
3. Main points (3-5 sections)
4. Examples/evidence
5. Conclusion + CTA
```

**SNS post:**
```
1. Hook (first line = most important)
2. Core message (1-2 paragraphs)
3. CTA or question
4. Hashtags (if applicable)
```

**Newsletter:**
```
1. Subject line (3 options)
2. Opening
3. Main content (2-3 sections)
4. Links/resources
5. Closing + CTA
```

**Thread:**
```
1. Hook tweet
2. Context tweets (2-3)
3. Key points (3-5)
4. Summary + CTA
```

### Step 4: Write draft
**Type**: generate

Write the full draft following the outline. Apply tone guidelines:

- **Professional**: clear, authoritative, no slang
- **Casual**: conversational, contractions, relatable
- **Technical**: precise, jargon OK, code examples welcome
- **Storytelling**: narrative arc, anecdotes, emotional hooks

### Step 5: Review and present
**Type**: review

Self-review the draft for:
- Hook strength (would you keep reading?)
- Flow (does each section lead to the next?)
- Length (matches target?)
- Tone consistency

Present to user with:
```
Draft ready: {type} about "{topic}"
Length: {word count}
Tone: {tone}

---
{full draft}
---

Feedback? I can adjust tone, length, or restructure.
```

---

## Edge Cases

**No topic**: Ask "What would you like to write about?" with 3 example topics.
**Multiple languages**: Default to the language of the topic. If mixed, ask preference.
**SEO request**: Add meta description, suggested title tags, keyword placement notes.

---

## Integration Points

- **deep-research**: For research-heavy content, trigger deep-research first.
- **document-converter**: Export draft as PDF/DOCX for sharing.
- **/idea**: Content ideas captured via /idea can feed into this skill.
