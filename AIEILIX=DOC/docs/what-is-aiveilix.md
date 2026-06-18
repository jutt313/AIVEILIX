# What is Aiveilix?

> Aiveilix is a persistent knowledge infrastructure platform for AI. It solves one of the biggest limitations of modern AI tools — the inability to remember, store, and reliably retrieve large amounts of personal or professional knowledge across sessions.

---

## The Problem

Every time you use an AI tool like Claude, ChatGPT, or Gemini, you start from zero. You upload files, provide context, and explain your situation — and within 10 to 15 messages, the AI has already forgotten what you uploaded. There is no memory. There is no persistence. Every session is a blank slate.

For individuals and businesses that rely on documents — contracts, research, reports, manuals, financial records, product specs — this is a fundamental blocker. The AI is powerful, but it cannot hold your world in its mind.

---

## The Solution

Aiveilix gives you a **persistent knowledge bucket** — a private, intelligent vault where you upload your files once and they are always available, always searchable, and always ready for any AI to use.

You upload any file. Aiveilix processes it deeply — extracting text, understanding visuals, mapping every element to its exact position in the document — and transforms it into a fully searchable knowledge base using RAG (Retrieval-Augmented Generation).

Then, through a simple MCP URL, any AI tool can connect to your bucket and access your knowledge in real time. No re-uploading. No forgotten context. No limits.

---

## What Makes Aiveilix Different

Most "chat with your PDF" tools extract plain text and call it done. Aiveilix goes much deeper.

### 1. True Visual Understanding

Every file is processed by both **Docling** (text and structure extraction) and **Gemini Flash** (visual understanding). Charts, diagrams, screenshots, and any text embedded inside images are fully understood and indexed — not ignored.

### 2. Layout-Aware Processing

Every block of content — text, table, image, heading — is mapped to its exact position on the page using a **Layout JSON Map**. The AI does not just see words. It sees the document the way a human reads it — top to bottom, in context, with visuals and text together.

### 3. Persistent Knowledge Buckets

Your files live in Aiveilix permanently. Organize them into buckets by topic, project, or purpose. Every bucket is always ready — no session limits, no re-uploading, no forgetting.

### 4. Connect Any AI via MCP

Every bucket gets a unique **MCP URL**. Paste it into Claude, ChatGPT, or any MCP-compatible agent and your knowledge is instantly available. The AI can search, query, and retrieve from your bucket in real time.

### 5. High-Precision Retrieval

Aiveilix uses **hybrid search** (semantic + keyword), **BGE-M3 embeddings**, and a **BGE Reranker** to find the most relevant information with high precision. Not just keyword matching — true semantic understanding.

---

## Who is Aiveilix For?

**Individuals**
- Researchers who work with large volumes of papers and reports
- Professionals who need to query contracts, policies, and manuals
- Anyone who wants their documents to be permanently accessible to AI

**Businesses**
- Teams that need shared knowledge bases connected to AI tools
- Companies that want their internal documentation searchable by AI agents
- Organizations building AI workflows that need persistent, reliable document retrieval

**Developers and AI Builders**
- Developers building AI agents that need access to persistent document knowledge
- Teams integrating RAG into their products without building the pipeline themselves
- Anyone who wants a managed MCP server for their document knowledge

---

## Core Features

| Feature | Description |
|---|---|
| **Bulk file upload** | Upload any file type in batches — PDF, DOCX, PPTX, XLSX, images, and more |
| **Deep processing** | Text extraction, visual understanding, and Layout JSON Map creation per file |
| **Persistent buckets** | Your knowledge lives permanently — no session limits |
| **MCP integration** | Connect any AI to your bucket via a unique MCP URL |
| **Hybrid RAG search** | Semantic + keyword search with reranking for high-precision retrieval |
| **Built-in AI agent** | Native agent with access to your buckets and live web search |
| **Multi-LLM support** | Choose between Claude, Gemini, GPT-4o, and Kimi |
| **Team collaboration** | Share buckets with team members with role-based permissions |
| **Light and dark mode** | Full theme support saved to your profile |
| **Secure auth** | Email, Google, GitHub login with JWT and 2FA support |

---

## How it Works in 3 Steps

### Step 1 — Upload
Upload any file to your bucket. Aiveilix processes it automatically — extracting text, understanding visuals, and building a Layout JSON Map that preserves the exact structure of your document.

### Step 2 — Connect
Copy your bucket MCP URL and paste it into any AI tool. Claude, ChatGPT, or your own agent now has real-time access to your knowledge.

### Step 3 — Query
Ask any question. Aiveilix retrieves the most relevant information from your documents using hybrid RAG search and reranking, and your AI delivers a precise, sourced answer.

---

## The Name

**Aiveilix** — AI + Veil +lix

- **AI** — artificial intelligence at the core
- **Veil** — your knowledge is protected, private, and secure
- **lix** — flow, connection, the link between your knowledge and any AI

---

## Tech Philosophy

Aiveilix is built on the principle that **your knowledge should work for you — not disappear every session.**

Every technical decision prioritizes:
- **Accuracy** — high-precision retrieval over fast but shallow results
- **Privacy** — your files stay in your bucket, under your control
- **Openness** — connect to any AI, not just one ecosystem
- **Simplicity** — one URL, any AI, instant access

---

## Current Status

Aiveilix is currently in active development. The MVP covers the full pipeline from file upload to MCP integration, with billing, team collaboration, and multi-LLM support included from day one.

---

*Document version: 1.0 — March 2026*
