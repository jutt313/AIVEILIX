# Ingestion cleanup — dedup + name reconciliation

Fixes three RAG-quality issues found in processed docs:

1. **OCR/visual name errors** (`horse organics`, `Daniel Hoffman`) — rule-based
   canonicalization of obvious slips against a frequent dominant spelling.
2. **Conflicts surfaced silently** (`Hoftun` vs `Hoffman`) — kept BOTH and flagged
   with `name_conflict` instead of overwriting.
3. **Duplicate quotes/reviews/images** — collapsed at ingestion (stored layout
   JSON, summary, chunks) and again at retrieval as a backstop.

## Where the work happens

| Stage | File | Notes |
|---|---|---|
| dedup elements | `app/services/processing_v3/dedup.py` | within-modality, keeps `dup_count` |
| name reconcile | `app/services/processing_v3/reconcile.py` | Tier A canonicalize / Tier B flag |
| shared similarity | `app/services/processing_v3/text_sim.py` | normalize / similarity / edit_ratio |
| wired in (before summary) | `orchestrator.py` (after element assembly) | runs on RAW elements, never from summary |
| conflict → chunk + layout | `chunking.py` | text marker + `metadata.name_conflict` + doc-level `name_conflicts` |
| answer layer | `agent/prompts.py`, `mcp/tools.py` | prompt rule + `list_visuals`/`get_visual`/`get_file_layout` expose conflicts |
| retrieval backstop | `agent/reranker.py`, `agent/retrieval.py` | content dedup after rerank + image-merge overlap skip |

## Config (all in `app/config.py`, env-overridable)

```
ingest_dedup_enabled=True        ingest_dedup_threshold=0.90
name_reconcile_enabled=True      name_canonicalize_min_occurrences=3
name_canonicalize_ratio=3.0      name_variant_min_ratio=0.80
retrieval_dedup_enabled=True     retrieval_dedup_threshold=0.93
```

## Deploy + backfill order

1. Deploy the new code (new files become active for NEW uploads automatically).
2. Backfill existing files — **dry-run first**:
   ```
   cd backend
   python -m scripts.reprocess_files --mode rederive --dry-run
   python -m scripts.reprocess_files --mode rederive --file <one-file-uuid>   # validate one
   python -m scripts.reprocess_files --mode rederive --bucket <uuid>          # then a bucket
   ```
   `rederive` re-applies dedup + name rules to the already-stored text and
   re-indexes — **no re-OCR** (cheap). It cannot un-misread a pixel; if you later
   change the OCR/visual model, use `--mode full` (re-OCR, expensive).

## Validate against the live MCP (norseorganic page.pdf, file `d1b368e4-…`)

Before vs after backfill, hit the bucket MCP endpoint and confirm:

- `list_visuals` total drops from **79** (duplicate Fox/Glamour quote blocks and
  repeated review screenshots collapse).
- `search "horse organics"` / the product visuals no longer read `horse organics`.
- the signature visual (`Daniel Hoffman`) carries a `name_conflict` listing
  `Daniel Hoftun` / `Daniel Hoffman`; `get_file_layout` shows doc-level
  `name_conflicts`.

```bash
URL='https://aiveilix-api-…/v1/mcp/bucket/<token>'
curl -sS -X POST "$URL" -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_visuals","arguments":{"file_id":"d1b368e4-ad88-4f93-8e31-bb57479a4e6e"}}}'
```

## Tests

```
cd backend && python -m pytest tests/test_dedup_reconcile.py -q
```
