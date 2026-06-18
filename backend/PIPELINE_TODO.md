# File Pipeline Contract

Target runtime flow:

1. User uploads file
2. Backend saves raw file to R2
3. Postgres creates file row
4. Status = `processing`
5. Docling extracts text/layout
6. Gemini reads images/visual parts
7. Layout JSON is built
8. Layout JSON saved to R2
9. Content is chunked
10. Text embeddings are created
11. Image embeddings are created
12. Vectors saved to Qdrant
13. Postgres chunks updated
14. Status = `ready`
15. Agent can use the file

## Required Invariants

- A file is never agent-searchable until `files.status = 'ready'`.
- A failed run must not leave active Qdrant vectors behind.
- Retry or replace must not duplicate active vectors or chunk rows.
- Only one processing run may execute per file at a time.
- The file pipeline uses one execution trigger only: FastAPI background tasks.
- Layout and chunk metadata must be cleared when a file is reprocessed.
- If a file contains images, Gemini must succeed or the file must fail processing.
- Replace must preserve distinct raw-object paths for each stored version.

## Implementation Checklist

- [x] Save the raw file to R2 before creating the `files` row.
- [x] Set the file to `processing` immediately after row creation.
- [x] Keep Docling and Gemini before layout build.
- [x] Fail processing when visual extraction is required but Gemini is unavailable.
- [x] Save Layout JSON to R2 before chunk persistence.
- [x] Create text and image embeddings before Qdrant writes.
- [x] Write vectors to Qdrant before inserting embedded chunk rows.
- [x] Gate agent retrieval to `files.status = 'ready'`.
- [x] Deprecate old vectors on every processing run, not only version bumps.
- [x] Delete stale chunk rows before rebuilding a file.
- [x] Mark chunk rows failed and deprecate vectors on pipeline failure.
- [x] Remove unused Valkey queue writes from the upload path.
- [x] Reset layout metadata on retry and replace.
- [x] Prevent duplicate concurrent processing runs for the same file.
- [x] Reject retry unless the file is currently `failed`.
- [x] Generate searchable fallback text chunks for image-only files.
- [x] Create a new `file_versions` row on replace.
- [x] Store each replacement version at a distinct raw R2 key.

## Remaining Validation

- [ ] Run an end-to-end integration test against real Postgres, R2, Docling, Gemini, and Qdrant services.
- [ ] Verify production environment variables, especially `GEMINI_API_KEY` and R2 credentials.
