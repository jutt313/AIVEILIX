# Aiveilix — Agent

> This document describes the complete design and behavior of the Aiveilix AI agent. It covers how the agent thinks, searches, responds, adapts to users, handles memory, and manages follow-up questions.

---

## Overview

The Aiveilix agent is the built-in AI assistant available inside every bucket. It combines three sources of intelligence to give the most accurate, refined, and personalized responses possible:

1. **Bucket RAG** — searches the user's uploaded documents using hybrid semantic search
2. **Web search** — fetches real-time information from the web using DuckDuckGo when needed
3. **Conversation memory** — all conversations are stored in RAG so the agent never loses context

The agent is not a simple chatbot. It thinks intelligently, adapts to the user, and always aims to give the most useful and honest response.

---

## LLM Options

The user selects their preferred LLM in settings. The selected LLM powers all agent responses in every thread.

| LLM | Provider | Link |
|---|---|---|
| **Claude** | Anthropic | [anthropic.com](https://www.anthropic.com/) |
| **Gemini** | Google | [ai.google.dev](https://ai.google.dev/) |
| **GPT-4o** | OpenAI | [openai.com](https://openai.com/) |
| **Kimi** | Moonshot AI | [moonshot.cn](https://www.moonshot.cn/) |

The LLM selection applies across all buckets and threads. The user can change it at any time in settings.

---

## Web Search Modes

Web search is configured **per conversation thread**. Each of the 20 threads in a bucket can have its own web search setting.

### Mode 1 — Smart Mode (Default)

The agent decides intelligently per message whether web search is needed.

```
User sends message
        |
        v
Agent checks bucket RAG first
        |
        v
Bucket has a complete answer?
        |
   Yes  |  No
        |
        v         v
   Use bucket    Search web
   only          + bucket
        |              |
        v              v
   Clean answer   Merged clean answer
```

- If the bucket has the answer → web search is skipped entirely
- If the bucket does not have the answer or the answer may be outdated → web search runs
- No unnecessary searches, no wasted API calls

---

### Mode 2 — Bucket Only Mode

The user fully blocks web search for this thread. The agent only replies from bucket data.

- No web access at all in this thread
- Useful for private or sensitive document workflows
- User sets this in thread settings

---

### Mode 3 — Always Search Mode

The agent searches both the bucket and the web on every single message in this thread.

- Both sources always used
- Results shown **separately** — bucket answer first, web results second
- Useful when the user wants real-time information alongside their documents

---

## How the Agent Thinks

The agent does not blindly answer. It thinks before responding.

```
User sends message
        |
        v
Is the question clear enough to answer correctly?
        |
   Yes  |  No
        |  |
        |  v
        | Ask follow-up question (see Follow-Up section)
        |
        v
Check web search mode for this thread
        |
        v
Search bucket RAG (always)
        |
        v
Search web if needed (based on mode)
        |
        v
Merge results intelligently
        |
        v
Adapt response to user tone and style
        |
        v
Generate refined, complete response
        |
        v
Attach sources at the bottom
        |
        v
Deliver response to user
```

---

## User Tone and Style Adaptation

The agent learns and adapts to each user automatically — no manual configuration needed.

### What the agent learns:

- **Tone** — formal, casual, technical, conversational
- **Detail level** — does the user prefer brief answers or deep explanations?
- **Question style** — how the user phrases questions
- **Language preferences** — vocabulary, sentence structure

### How it learns:

- By observing the conversation as it grows within the thread
- The more the user interacts, the more refined the agent becomes
- Every conversation is stored in RAG — zero memory loss across sessions

### Response length adaptation:

- User says "short" → agent gives a short answer but never cuts the reasoning — the explanation is condensed, not removed
- User asks a deep technical question → agent gives a full detailed response
- The agent never sacrifices quality — only adjusts style

### Thread fresh start:

- Every new thread starts fresh — no tone carried over from other threads
- The agent starts with the user's **profile context only** (name, language, timezone, preferences)
- Tone is learned fresh as the thread grows

---

## Conversation Memory

All conversations are stored in RAG — the agent never forgets.

```
User sends message
        |
        v
Agent generates response
        |
        v
Entire conversation (user messages + agent responses)
stored in RAG per thread (PostgreSQL + Qdrant)
        |
        v
On next message → agent retrieves relevant past context
from conversation RAG
        |
        v
Agent always has full history available
```

**Benefits:**
- No session limits — conversations can go 1000+ messages with no degradation
- Agent remembers what was discussed earlier in the thread
- Agent builds a deeper understanding of the user over time
- Zero memory loss — even after days or weeks away

---

## Sources Display

Every single agent response includes a sources section at the bottom — always, no exceptions.

### Source types:

**Bucket file used:**
```
📄 company-report.pdf — Page 4
📄 product-manual.docx — Page 12
```

**Web source used:**
```
🌐 [favicon] openai.com/blog/gpt-4o
🌐 [favicon] techcrunch.com/article/...
```

### Rules:
- Only sources actually used in the response are shown — never all files
- If 1000 files are in the bucket but only 3 were used → only 3 are shown
- All web links used are always shown in full
- Conversation memory supports the answer internally but is not shown as a separate source type
- Sources are always at the bottom, never inline

---

## Follow-Up Questions

The agent asks follow-up questions when the user's message is unclear, ambiguous, or could lead to an unwanted response.

### When the agent asks a follow-up:
- The question is unclear or too vague
- The answer could go in the wrong direction without clarification
- More context is needed to give a useful response

### Follow-up question style — user controlled:

On first interaction, the agent asks the user a hidden setup question:

```
"How would you like me to ask follow-up questions when I need clarification?"
- All at once
- One by one
```

**This preference message is never shown in the conversation.** It is a hidden system interaction that saves to the user's profile silently. The agent then follows this preference in every thread going forward.

**All at once:**
```
Agent: "Before I answer, I have a few quick questions:
1. Are you asking about Q3 or Q4 results?
2. Do you want the global numbers or region-specific?
3. Should I include projections or actuals only?"
```

**One by one:**
```
Agent: "Before I answer — are you asking about Q3 or Q4 results?"
[User answers]
Agent: "Got it. Do you want the global numbers or region-specific?"
[User answers]
Agent: "Perfect. Now I have everything I need."
[Agent answers]
```

---

## Agent Response Structure

Every agent response follows this clean structure:

```
[Answer]

Refined, complete response adapted to the user's tone and style.
Never cuts reasoning even when keeping it short.
Always gives the most useful and honest answer possible.

---

Sources:
📄 file-name.pdf — Page 3
📄 another-file.docx — Page 7
🌐 [favicon] example.com/article
```

---

## Full Agent Flow Diagram

```
User opens thread
        |
        v
Agent loads:
- User profile (name, language, timezone, preferences)
- Thread web search mode (smart / bucket only / always search)
- Follow-up style preference (all at once / one by one)
        |
        v
User sends message
        |
        v
Is message clear?
        |
   Yes  |  No → ask follow-up question(s)
        |
        v
Check thread web search mode
        |
        v
Search bucket RAG (always)
        |
        v
Web search needed? (based on mode + smart decision)
        |
   Yes  |  No
        v  |
Search web  |
        |   |
        +———+
        |
        v
Merge results intelligently
        |
        v
Adapt to user tone + style + detail level
        |
        v
Generate refined complete response
        |
        v
Attach sources (files used + web links)
        |
        v
Save conversation to RAG (PostgreSQL + Qdrant)
        |
        v
Deliver response to user
```

---

## Summary

| Feature | Behavior |
|---|---|
| LLM options | Claude, Gemini, GPT-4o, Kimi — user selects in settings |
| Web search | Per thread — smart mode, bucket only, or always search |
| Smart mode | Agent decides per message — no unnecessary searches |
| Tone adaptation | Learns automatically from conversation — no manual setup |
| Response length | Adapts to user — short when asked but never cuts reasoning |
| Memory | All conversations stored in RAG — zero memory loss |
| Thread start | Fresh start + user profile only — no cross-thread memory |
| Sources | Always shown — files used, web links, or memory label |
| Follow-up questions | Agent asks when unclear — style set by user (all at once or one by one) |
| Follow-up preference | Hidden system setting — never shown in conversation |

---

*Document version: 1.0 — March 2026*
