# Aiveilix Qdrant

Qdrant stores vector search data for:

- document text retrieval
- image retrieval
- conversation memory retrieval

This local setup uses Qdrant embedded mode through the Python client so development can run without Docker or a separate Qdrant server binary.

## Collections

- `text_chunks`
- `image_chunks`
- `conversation_chunks`

## Local paths

- Data dir: `backend/database/qdrant/data/local`
- Bootstrap script: `backend/database/qdrant/bootstrap_collections.py`
- Setup script: `backend/database/qdrant/scripts/setup-env.sh`
- Bootstrap runner: `backend/database/qdrant/scripts/bootstrap-local.sh`
- Verify runner: `backend/database/qdrant/scripts/verify-local.sh`

## Local flow

```bash
./backend/database/qdrant/scripts/setup-env.sh
./backend/database/qdrant/scripts/bootstrap-local.sh
./backend/database/qdrant/scripts/verify-local.sh
```

## Notes

- Keep the Qdrant client version aligned with `backend/requirements.txt` so the embedded local store metadata stays compatible with the backend runtime.
- `text_chunks` uses dense + sparse search support
- `image_chunks` uses dense vectors for image embeddings
- `conversation_chunks` stores thread-level conversation memory vectors
- the same bootstrap script can be pointed at a remote Qdrant instance later
