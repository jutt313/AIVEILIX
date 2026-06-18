# Aiveilix — System Flow

> This document describes the complete system flow for how files are uploaded, processed, stored, and retrieved in Aiveilix. Every service used is referenced with links and includes examples.

---

## Services Reference

| Service | Purpose | Link |
|---|---|---|
| **Cloudflare R2** | Raw file and processed file storage | [cloudflare.com/r2](https://www.cloudflare.com/developer-platform/r2/) |
| **Docling** | Text and structure extraction from files | [github.com/DS4SD/docling](https://github.com/DS4SD/docling) |
| **Gemini Flash** | Visual understanding and OCR inside images | [ai.google.dev](https://ai.google.dev/) |
| **LlamaIndex** | Intelligent document chunking | [llamaindex.ai](https://www.llamaindex.ai/) |
| **BGE-M3** | Text embedding model | [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) |
| **CLIP** | Image embedding model | [github.com/openai/CLIP](https://github.com/openai/CLIP) |
| **Qdrant** | Vector database for storing embeddings | [qdrant.tech](https://qdrant.tech/) |
| **PostgreSQL** | Metadata, users, and bucket data | [postgresql.org](https://www.postgresql.org/) |
| **BGE Reranker** | Re-ranking retrieved results for accuracy | [huggingface.co/BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) |
| **Claude API** | Final answer generation | [anthropic.com](https://www.anthropic.com/) |
| **FastAPI** | Python backend framework | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) |

---

## Phase 1 — File Upload

When a user uploads a file, the first step is to safely store the raw file and register it in the database.

**Supported file types:** PDF, DOCX, PPTX, XLSX, images (PNG, JPG), and more.

**What happens:**
- User uploads a file through the React frontend
- FastAPI backend receives the file
- Raw file is saved to **Cloudflare R2**
- A unique file ID is generated and a record is saved to **PostgreSQL**

**Example PostgreSQL record:**
```json
{
  "file_id": "f_abc123",
  "user_id": "u_xyz789",
  "bucket_id": "b_001",
  "file_name": "company-report.pdf",
  "file_type": "pdf",
  "r2_path": "raw/f_abc123/company-report.pdf",
  "status": "processing",
  "created_at": "2026-03-26T10:00:00Z"
}
```

---

## Phase 2 — Text Extraction with Docling

**Docling** reads the file and extracts all text blocks with their exact positions on each page.

**What Docling extracts:**
- Headings, paragraphs, and lists
- Tables as structured data
- Page number and coordinates (x, y) for every block

**Example Docling output:**
```json
{
  "page": 1,
  "blocks": [
    {
      "id": "text_1",
      "type": "heading",
      "content": "Q3 Financial Report",
      "x": 50,
      "y": 80
    },
    {
      "id": "text_2",
      "type": "paragraph",
      "content": "Total revenue increased by 23% this quarter.",
      "x": 50,
      "y": 150
    },
    {
      "id": "table_1",
      "type": "table",
      "content": "| Month | Revenue |\n|---|---|\n| July | $200k |\n| August | $230k |",
      "x": 50,
      "y": 300
    }
  ]
}
```

---

## Phase 3 — Visual Extraction with Gemini Flash

**Gemini Flash** analyzes every page as an image. It understands charts, diagrams, screenshots, and any text embedded inside visuals.

**What Gemini Flash extracts:**
- Image type and description (colors, layout, visual style)
- Text found inside the image (chart labels, captions, annotations)
- Position context on the page
- Reference to nearby text blocks

**Example Gemini Flash output:**
```json
{
  "page": 1,
  "images": [
    {
      "id": "img_1",
      "type": "bar_chart",
      "x": 50,
      "y": 500,
      "description": "A blue bar chart showing monthly revenue growth from July to September 2025.",
      "text_inside": "July: $200k, August: $230k, September: $260k",
      "colors": ["#3B82F6", "#1E40AF"],
      "nearby_text_id": "text_2"
    }
  ]
}
```

---

## Phase 4 — Layout JSON Map Creation

A custom **Python merger function** inside FastAPI combines the Docling output and Gemini Flash output into one unified **Layout JSON Map**.

This map stores every block — text, table, or image — sorted by page number and vertical position (y coordinate) so the exact reading order of the original document is fully preserved.

**Example Layout JSON Map:**
```json
{
  "file_id": "f_abc123",
  "total_pages": 10,
  "pages": [
    {
      "page": 1,
      "blocks": [
        {
          "id": "text_1",
          "type": "heading",
          "content": "Q3 Financial Report",
          "x": 50,
          "y": 80
        },
        {
          "id": "text_2",
          "type": "paragraph",
          "content": "Total revenue increased by 23% this quarter.",
          "x": 50,
          "y": 150
        },
        {
          "id": "table_1",
          "type": "table",
          "content": "| Month | Revenue |\n|---|---|\n| July | $200k |\n| August | $230k |",
          "x": 50,
          "y": 300
        },
        {
          "id": "img_1",
          "type": "bar_chart",
          "description": "A blue bar chart showing monthly revenue growth.",
          "text_inside": "July: $200k, August: $230k, September: $260k",
          "colors": ["#3B82F6", "#1E40AF"],
          "nearby_text_id": "text_2",
          "x": 50,
          "y": 500
        }
      ]
    }
  ]
}
```

> The Layout JSON Map is saved to **Cloudflare R2** and its path is referenced in **PostgreSQL**.

---

## Phase 5 — Intelligent Chunking with LlamaIndex

**LlamaIndex** chunks the text blocks intelligently. Images are not chunked — they are kept whole and attached as metadata to their nearest text chunk.

**Chunking rules:**
- Text chunks are approximately 512 tokens each with overlap
- Each chunk carries its `file_id`, `page`, `block_id`, and nearby image references
- Images stay attached to their nearest text chunk as metadata

**Example chunk:**
```json
{
  "chunk_id": "chunk_001",
  "file_id": "f_abc123",
  "page": 1,
  "content": "Total revenue increased by 23% this quarter.",
  "block_id": "text_2",
  "nearby_image": "img_1",
  "image_description": "A blue bar chart showing monthly revenue growth.",
  "image_text_inside": "July: $200k, August: $230k, September: $260k"
}
```

---

## Phase 6 — Embedding with BGE-M3 and CLIP

Each chunk and image is converted into a vector for semantic search.

- **Text chunks and image descriptions** are embedded using **BGE-M3**
- **Image visuals** are embedded using **CLIP**
- Both are stored in **Qdrant** with their full metadata payload

**Example Qdrant record:**
```json
{
  "id": "chunk_001",
  "vector": [0.012, 0.843, 0.231, "..."],
  "payload": {
    "file_id": "f_abc123",
    "page": 1,
    "content": "Total revenue increased by 23% this quarter.",
    "nearby_image": "img_1",
    "image_description": "A blue bar chart showing monthly revenue growth.",
    "image_text_inside": "July: $200k, August: $230k, September: $260k"
  }
}
```

---

## Phase 7 — Query and Retrieval

When a user asks a question, the system retrieves the most relevant chunks and generates an accurate answer.

**Step by step:**

1. User sends a query: *"What was the revenue in August?"*
2. **BGE-M3** embeds the query into a vector
3. **Qdrant** searches for the most semantically similar vectors
4. **BGE Reranker** re-ranks the top results for higher accuracy
5. The **Layout JSON Map** adds full positional and relational context to results
6. **Claude API** receives the ranked chunks with context and generates the final answer

**Example context sent to Claude:**
```
Page 1 — Paragraph:
"Total revenue increased by 23% this quarter."

Nearby Chart (img_1):
"A blue bar chart showing monthly revenue growth.
 Text inside chart: July: $200k, August: $230k, September: $260k"
```

**Claude's answer:**
> "Revenue in August was $230,000, showing continued growth from July's $200,000."

---

## Full System Flow Diagram

```
User uploads file
        |
        v
FastAPI receives file
        |
        v
Save raw file ──────────────────> Cloudflare R2
        |
        v
Save file metadata ─────────────> PostgreSQL (status: processing)
        |
        v
   +----+----+
   |         |
Docling   Gemini Flash
(text +   (visuals +
structure) text in images)
   |         |
   +----+----+
        |
        v
Custom Python Merger (FastAPI)
        |
        v
Layout JSON Map created
(every block has: ID, type, position, relationships)
        |
        v
Save Layout JSON ───────────────> Cloudflare R2
        |
        v
LlamaIndex intelligent chunking
        |
        v
   +----+----+
   |         |
BGE-M3     CLIP
(text      (image
chunks)    visuals)
   |         |
   +----+----+
        |
        v
Save vectors ───────────────────> Qdrant
        |
        v
Update file status: "ready" ────> PostgreSQL
        |
        v
File is live in user bucket ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User sends query
        |
        v
FastAPI receives query
        |
        v
BGE-M3 embeds the query
        |
        v
Qdrant semantic search
        |
        v
BGE Reranker re-ranks results
        |
        v
Layout JSON adds full context
        |
        v
Claude API generates answer
        |
        v
Answer returned to user ✅
```

---

## Multi-Page Files

For files with multiple pages such as a 10-page PDF:
- Each page is processed individually by Docling and Gemini Flash
- All pages are combined into one single Layout JSON Map
- Pages are clearly separated in the map by page number
- All chunks in Qdrant are tagged with their page number for precise retrieval

---

## File Versioning

Every time a file is updated or re-uploaded:
- A new version record is created in **PostgreSQL**
- Old embeddings in **Qdrant** are marked as `deprecated`
- New embeddings are processed and marked as `active`
- Original raw files remain in **Cloudflare R2** for full version history

---

*Document version: 1.0 — March 2026*
