# Aiveilix — RAG Pipeline

> This document describes the full Retrieval-Augmented Generation (RAG) pipeline used in Aiveilix. It covers chunking strategy, embedding, hybrid search, reranking, and failure handling — with examples for every step.

---

## Services Reference

| Service | Purpose | Link |
|---|---|---|
| **Docling** | Text and structure extraction | [github.com/DS4SD/docling](https://github.com/DS4SD/docling) |
| **Gemini Flash** | Visual understanding and OCR | [ai.google.dev](https://ai.google.dev/) |
| **LlamaIndex** | Intelligent document chunking | [llamaindex.ai](https://www.llamaindex.ai/) |
| **BGE-M3** | Text embedding model | [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3) |
| **CLIP** | Image embedding model | [github.com/openai/CLIP](https://github.com/openai/CLIP) |
| **Qdrant** | Vector database | [qdrant.tech](https://qdrant.tech/) |
| **BGE Reranker** | Re-ranking retrieved results | [huggingface.co/BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) |
| **Claude API** | Final answer generation | [anthropic.com](https://www.anthropic.com/) |

---

## Overview

The RAG pipeline is the core intelligence of Aiveilix. It transforms uploaded files into searchable knowledge and retrieves the most relevant information when a user asks a question.

The pipeline has two phases:
- **Indexing phase** — when a file is uploaded and processed
- **Retrieval phase** — when a user sends a query

---

## Phase 1 — Chunking Strategy

After Docling and Gemini Flash process the file and the Layout JSON Map is created, **LlamaIndex** splits the content into chunks for embedding.

### Settings

| Parameter | Value | Reason |
|---|---|---|
| Chunk size | **256 tokens** | Smaller chunks give high-precision retrieval |
| Overlap | **50 tokens** | Helps preserve sentence continuity between chunks |

### Rules by Content Type

| Content Type | Strategy | Reason |
|---|---|---|
| Normal text | 256 tokens + 50 overlap | Precise and clean retrieval |
| Tables | Keep whole, never split | Splitting breaks table meaning |
| Headings | Always attached to next chunk | A heading alone has no meaning |
| Images | Never chunked, stored as metadata | Images attach to nearest text chunk |
| Long paragraphs | 256 tokens + 50 overlap | Overlap keeps context intact |

### Example — Text Chunk

```json
{
  "chunk_id": "chunk_001",
  "file_id": "f_abc123",
  "page": 1,
  "content": "Total revenue increased by 23% this quarter driven by strong performance in the Asia-Pacific region.",
  "block_id": "text_2",
  "tokens": 24,
  "nearby_image": "img_1",
  "image_description": "A blue bar chart showing monthly revenue growth.",
  "image_text_inside": "July: $200k, August: $230k, September: $260k"
}
```

### Example — Table Chunk (kept whole)

```json
{
  "chunk_id": "chunk_002",
  "file_id": "f_abc123",
  "page": 1,
  "content": "| Month | Revenue | Growth |\n|---|---|---|\n| July | $200k | — |\n| August | $230k | +15% |\n| September | $260k | +13% |",
  "block_id": "table_1",
  "type": "table"
}
```

---

## Phase 2 — Embedding

Each chunk and image is converted into a vector so it can be searched semantically.

### Text Chunks — BGE-M3

All text chunks and image descriptions are embedded using **BGE-M3**.

BGE-M3 was chosen because:
- Free and open source (MIT license)
- Strong default for high-precision RAG systems
- Works well across multiple languages
- Supports hybrid search (dense + sparse)

**Reference:** [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)

**Example:**

```python
from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

chunk_text = "Total revenue increased by 23% this quarter."
embedding = model.encode(chunk_text)

# embedding['dense_vecs'] — dense vector for semantic search
# embedding['lexical_weights'] — sparse vector for keyword search
```

### Image Visuals — CLIP

All image visuals are embedded using **CLIP**.

**Reference:** [github.com/openai/CLIP](https://github.com/openai/CLIP)

**Example:**

```python
import clip
import torch
from PIL import Image

model, preprocess = clip.load("ViT-B/32")

image = preprocess(Image.open("img_1.png")).unsqueeze(0)
with torch.no_grad():
    image_embedding = model.encode_image(image)
```

### Storage in Qdrant

**Text collection example:**

```json
{
  "id": "chunk_001",
  "vector": [0.012, 0.843, 0.231, "..."],
  "payload": {
    "file_id": "f_abc123",
    "bucket_id": "b_001",
    "page": 1,
    "content": "Total revenue increased by 23% this quarter.",
    "nearby_image": "img_1",
    "image_description": "A blue bar chart showing monthly revenue growth.",
    "image_text_inside": "July: $200k, August: $230k, September: $260k"
  }
}
```

**Image collection example:**

```json
{
  "id": "img_001",
  "vector": [0.521, 0.134, 0.876, "..."],
  "payload": {
    "file_id": "f_abc123",
    "bucket_id": "b_001",
    "page": 1,
    "image_id": "img_1",
    "description": "A blue bar chart showing monthly revenue growth.",
    "text_inside": "July: $200k, August: $230k, September: $260k",
    "nearby_text_id": "text_2"
  }
}
```

---

## Phase 3 — Hybrid Search

When a user sends a query, Qdrant performs a **hybrid search** combining two methods for high-precision retrieval.

| Method | Type | What it finds |
|---|---|---|
| **Dense search** (BGE-M3) | Semantic | Meaning-based matches |
| **Sparse search** (BM25) | Keyword | Exact word matches |

**Example:**

```
User query: "What was revenue in August?"

Dense search finds: chunks about revenue growth and financial performance
Sparse search finds: chunks containing the exact word "August"

Combined result: chunks about revenue that specifically mention August
```

**Example hybrid search in Qdrant:**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import SparseVector

client = QdrantClient("localhost", port=6333)

results = client.query_points(
    collection_name="text_chunks",
    prefetch=[
        {"query": dense_vector, "limit": 50},
        {"query": SparseVector(indices=[101, 342], values=[0.8, 0.6]), "limit": 50},
    ],
    query=fusion_query,
    limit=50
)
```

---

## Phase 4 — Reranking

After Qdrant returns the top 50 results, **BGE Reranker** scores each result carefully and returns only the top 5 to Claude.

**Reference:** [huggingface.co/BAAI/bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)

### Flow

```
Qdrant returns top 50 results
        |
        v
BGE Reranker scores each result
against the original query
        |
        v
Top 5 highest scoring results selected
        |
        v
Layout JSON adds positional context
        |
        v
Claude receives top 5 chunks + context
```

**Example reranker code:**

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)

query = "What was revenue in August?"

pairs = [[query, result["content"]] for result in qdrant_results]
scores = reranker.compute_score(pairs)

# Sort by score, take top 5
top_5 = sorted(zip(scores, qdrant_results), reverse=True)[:5]
```

### Example — Context Sent to Claude After Reranking

```
Page 1 — Paragraph:
"Total revenue increased by 23% this quarter."

Nearby Chart (img_1):
Type: Bar chart
Description: "A blue bar chart showing monthly revenue growth from July to September 2025."
Text inside chart: "July: $200k, August: $230k, September: $260k"

Page 1 — Table:
| Month | Revenue | Growth |
|---|---|---|
| July | $200k | — |
| August | $230k | +15% |
| September | $260k | +13% |
```

**Claude's answer:**
> "Revenue in August was $230,000, representing a 15% increase from July's $200,000."

---

## Phase 5 — Failure Handling

If any step in the embedding process fails, the system retries automatically before alerting the user.

### Retry Strategy

| Parameter | Value |
|---|---|
| Max retries | **3 attempts** |
| Delay between retries | **3 seconds** |
| Action after all retries fail | Flag user with a clean message |

### Retry Flow

```
Embedding attempt fails
        |
        v
Wait 3 seconds — Retry attempt 2
        |
        v
Wait 3 seconds — Retry attempt 3
        |
        v
Still failing?
        |
        v
Flag user with clean message
```

### Clean User Message

```
"We had trouble processing one of your files.
 Please try uploading it again. If the issue continues, contact support."
```

### Example — Retry Logic in Python

```python
import time

def embed_with_retry(chunk, max_retries=3, delay=3):
    for attempt in range(1, max_retries + 1):
        try:
            embedding = model.encode(chunk["content"])
            return embedding
        except Exception as e:
            if attempt < max_retries:
                print(f"Attempt {attempt} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                notify_user(
                    file_id=chunk["file_id"],
                    message="We had trouble processing one of your files. Please try uploading it again."
                )
                return None
```

---

## Full RAG Pipeline Diagram

```
INDEXING PHASE (on file upload)

File processed by Docling + Gemini Flash
        |
        v
Layout JSON Map created
        |
        v
LlamaIndex chunks text
(256 tokens, 50 overlap)
Images kept whole as metadata
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
Store in Qdrant
(with full metadata payload)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RETRIEVAL PHASE (on user query)

User sends query
        |
        v
BGE-M3 embeds query
        |
        v
Qdrant hybrid search
(dense BGE-M3 + sparse BM25)
returns top 50 results
        |
        v
BGE Reranker scores top 50
selects top 5
        |
        v
Layout JSON adds context
(page, position, nearby images)
        |
        v
Claude API generates answer
        |
        v
Answer returned to user
```

---

*Document version: 1.0 — March 2026*
