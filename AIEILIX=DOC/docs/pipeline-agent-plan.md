# Aiveilix — Pipeline Agent Plan

> This file is a direct handoff brief for the agent responsible for building the full document-processing pipeline from upload to `ready` status.

---

## Goal

Build the complete backend pipeline for Aiveilix so an uploaded file can move through this flow:

```text
upload -> save raw file to R2 -> create DB record -> process with Docling -> process with Gemini -> build Layout JSON -> store Layout JSON -> chunk -> embed -> write to Qdrant -> mark file ready
```

This agent owns the pipeline workstream while other agents continue building backend product APIs and frontend UI.

---

## Current State

The project already has:

- PostgreSQL running locally and connected to the backend
- Qdrant running locally in embedded mode and connected to the backend
- Valkey running locally and connected to the backend
- auth system already implemented by another agent
- frontend auth pages already implemented by another agent

The pipeline agent should **not** redo auth or frontend work.

---

## Ownership

This agent owns:

- file upload intake logic
- Cloudflare R2 storage integration
- processing orchestration
- Docling extraction
- Gemini visual extraction
- Layout JSON merge/build
- chunking logic
- embedding logic
- Qdrant write logic
- processing status updates
- investigation/event logging
- retry behavior for processing failures

This agent should avoid changing:

- auth logic
- JWT / login / 2FA code
- frontend files unless strictly needed for upload integration
- unrelated routes owned by the backend product agent

If endpoint changes are needed, keep them limited to the file pipeline area.

---

## Required Docs To Follow

Read and follow these project docs first:

- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/system-flow.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/rag-pipeline.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/database-schema.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/api-endpoints.md`
- `/Volumes/KIOXIA/AIveilix/AIEILIX=DOC/docs/tech-stack.md`

---

## Pipeline Scope

### Phase 1 — Upload Intake

Implement:

- `POST /v1/buckets/{bucket_id}/files`
- support one or more files in multipart upload
- create `files` row in PostgreSQL
- create `file_versions` row
- set initial file status to `uploading`, then `processing`
- save raw file to Cloudflare R2
- update `r2_path`

Expected DB tables involved:

- `files`
- `file_versions`
- `investigation_events`

Expected event log examples:

- `upload_started`
- `upload_completed`
- `file_processing_queued`

---

### Phase 2 — Processing Orchestration

Implement a processing service that takes a file from uploaded to processed.

Responsibilities:

- fetch file metadata from PostgreSQL
- download/read raw file
- determine file type
- call Docling
- call Gemini visual extraction
- build Layout JSON
- store Layout JSON in R2
- update `layout_json_path`
- create chunk records
- generate embeddings
- write vectors to Qdrant
- mark file `ready`

Failure handling:

- if a stage fails, set `files.status = failed`
- write `investigation_events`
- write `error_logs` when appropriate
- support retries

---

### Phase 3 — Docling Extraction

Implement a dedicated Docling service module.

Expected output:

- text blocks
- headings
- paragraphs
- tables
- coordinates
- page numbers

Output should be normalized into a consistent internal structure, not left as raw vendor-specific output.

---

### Phase 4 — Gemini Visual Extraction

Implement a dedicated Gemini service module.

Expected output:

- descriptions for charts, diagrams, screenshots, and images
- OCR-like extracted text inside visuals
- nearby page/location metadata where possible

This service should be isolated from the rest of the pipeline so it can be tested and replaced independently.

---

### Phase 5 — Layout JSON Builder

Implement a merger/builder that combines:

- Docling structured text output
- Gemini visual output

Produce one unified Layout JSON object in the documented format.

Requirements:

- preserve page order
- preserve vertical reading order
- preserve block IDs
- include image metadata
- include text/image relationships

Then:

- save Layout JSON to R2
- update PostgreSQL `files.layout_json_path`

---

### Phase 6 — Chunking

Implement chunking according to the docs.

Rules to follow:

- normal text chunked with overlap
- tables kept whole
- headings attached to following content
- images not chunked as standalone text chunks
- image context attached to nearby text chunks

Write metadata into PostgreSQL `chunks` table.

For each chunk store:

- `file_id`
- `bucket_id`
- `page`
- `content`
- `block_id`
- `nearby_image_id`
- `token_count`
- `status`

---

### Phase 7 — Embeddings

Implement embedding generation for:

- text chunks
- image chunks
- later compatibility with conversation chunks already prepared in schema

Use the documented model plan:

- BGE-M3 for text
- CLIP for image embeddings

The implementation should be modular so model providers can be swapped later.

---

### Phase 8 — Qdrant Writes

Write the pipeline outputs into these collections:

- `text_chunks`
- `image_chunks`

Use payload fields that match the docs and DB records.

Examples:

- `file_id`
- `bucket_id`
- `page`
- `content`
- `nearby_image_id`
- `image_description`
- `image_text_inside`
- `status`

Mark old embeddings deprecated if reprocessing a newer version later.

---

### Phase 9 — Finalization

When the full pipeline succeeds:

- set file status to `ready`
- add event logs to `investigation_events`
- optionally create file summary if included in the same workstream

When it fails:

- set file status to `failed`
- persist failure details
- keep retry-friendly state

---

## Where To Write Code

Preferred new backend locations:

- `backend/app/services/storage/`
- `backend/app/services/pipeline/`
- `backend/app/services/processing/`
- `backend/app/services/embeddings/`
- `backend/app/services/qdrant/`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/app/api/v1/endpoints/files.py`

Suggested concrete files:

- `backend/app/services/storage/r2.py`
- `backend/app/services/pipeline/upload.py`
- `backend/app/services/pipeline/orchestrator.py`
- `backend/app/services/processing/docling_service.py`
- `backend/app/services/processing/gemini_service.py`
- `backend/app/services/processing/layout_builder.py`
- `backend/app/services/processing/chunker.py`
- `backend/app/services/embeddings/text_embeddings.py`
- `backend/app/services/embeddings/image_embeddings.py`
- `backend/app/services/qdrant/file_indexer.py`
- `backend/app/models/file.py`
- `backend/app/models/file_version.py`
- `backend/app/models/chunk.py`
- `backend/app/models/investigation_event.py`
- `backend/app/models/error_log.py`
- `backend/app/schemas/files.py`

If naming differs, keep it consistent and easy to follow.

---

## Database Integration Requirements

Use the existing PostgreSQL schema already created.

At minimum, pipeline code must read/write:

- `files`
- `file_versions`
- `chunks`
- `investigation_events`
- `error_logs`

If new columns are truly required, document them clearly before changing schema.

Do not invent a new parallel schema if the current one already supports the flow.

---

## Qdrant Integration Requirements

Use the existing backend Qdrant client path:

- `backend/app/qdrant_client.py`

Do not build a second conflicting Qdrant connection layer.

All Qdrant writes for the pipeline should go through a clear service wrapper that uses the shared client factory.

---

## Valkey Integration Requirements

Use Valkey only for temporary processing support, for example:

- queueing file IDs
- embedding queue
- retry scheduling
- short-lived processing state

Do not use Valkey as permanent storage.

---

## API Surface Expected From This Agent

Minimum useful endpoints:

- `POST /v1/buckets/{bucket_id}/files`
- `GET /v1/buckets/{bucket_id}/files`
- `GET /v1/buckets/{bucket_id}/files/{file_id}`
- `GET /v1/buckets/{bucket_id}/files/{file_id}/layout`
- `GET /v1/buckets/{bucket_id}/files/{file_id}/chunks`

Optional if time allows:

- `GET /v1/buckets/{bucket_id}/files/{file_id}/summary`
- `DELETE /v1/buckets/{bucket_id}/files/{file_id}`
- `POST /v1/buckets/{bucket_id}/files/{file_id}/retry`

---

## Acceptance Criteria

This work is complete only when all of the following are true:

1. A file can be uploaded through the backend.
2. Raw file is stored in R2.
3. PostgreSQL gets the correct file metadata.
4. Processing runs from upload to completion.
5. Layout JSON is produced and stored.
6. Chunks are written to PostgreSQL.
7. Vectors are written to Qdrant.
8. File status becomes `ready`.
9. Failure path sets status to `failed` and logs events cleanly.
10. The implementation is modular enough that the main backend agent can connect UI/API work to it without refactoring the whole pipeline.

---

## Parallel-Work Safety

This agent is not alone in the repo.

Rules:

- do not revert other agents’ changes
- expect backend auth and frontend work to change in parallel
- keep write scope focused on pipeline-related backend files
- if touching shared files like `config.py`, `requirements.txt`, or `router.py`, do the smallest necessary change

---

## Recommended Delivery Order

Build in this order:

1. file models + schemas
2. R2 storage service
3. upload endpoint
4. processing orchestrator
5. Docling service
6. Gemini service
7. Layout JSON builder
8. chunker
9. embeddings
10. Qdrant writer
11. retry/error/event logging
12. verification tests

---

## Final Deliverables

When done, the agent should provide:

- the list of files changed
- the upload-to-ready flow it implemented
- any env vars added
- any commands needed to run the pipeline locally
- any blockers or remaining TODOs

---

## Short Mission

Build the Aiveilix document pipeline so the rest of the product can plug into a working backend flow:

```text
upload -> storage -> extraction -> layout -> chunk -> embed -> qdrant -> ready
```
