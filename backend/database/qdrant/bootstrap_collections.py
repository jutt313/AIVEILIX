from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


def build_client(mode: str, path: Path | None, url: str | None, api_key: str | None):
    try:
        from qdrant_client import QdrantClient
    except ImportError as exc:
        raise SystemExit(
            "qdrant-client is not installed. Run ./backend/database/qdrant/scripts/setup-env.sh first."
        ) from exc

    if mode == "local":
        if path is None:
            raise SystemExit("--path is required for local mode")
        path.mkdir(parents=True, exist_ok=True)
        return QdrantClient(path=str(path))

    if not url:
        raise SystemExit("--url is required for remote mode")
    return QdrantClient(url=url, api_key=api_key)


def ensure_collection(client, name: str, recreate: bool = False) -> None:
    from qdrant_client import models

    existing = {collection.name for collection in client.get_collections().collections}

    config: dict[str, object]
    payload_indexes: Iterable[tuple[str, object]]

    if name == "text_chunks":
        config = {
            "vectors_config": models.VectorParams(size=1024, distance=models.Distance.COSINE),
            "sparse_vectors_config": {
                "text_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        }
        payload_indexes = (
            ("file_id", models.PayloadSchemaType.KEYWORD),
            ("bucket_id", models.PayloadSchemaType.KEYWORD),
            ("page", models.PayloadSchemaType.INTEGER),
            ("status", models.PayloadSchemaType.KEYWORD),
            ("nearby_image_id", models.PayloadSchemaType.KEYWORD),
        )
    elif name == "image_chunks":
        config = {
            "vectors_config": models.VectorParams(size=512, distance=models.Distance.COSINE),
        }
        payload_indexes = (
            ("file_id", models.PayloadSchemaType.KEYWORD),
            ("bucket_id", models.PayloadSchemaType.KEYWORD),
            ("page", models.PayloadSchemaType.INTEGER),
            ("image_id", models.PayloadSchemaType.KEYWORD),
            ("nearby_text_id", models.PayloadSchemaType.KEYWORD),
            ("status", models.PayloadSchemaType.KEYWORD),
        )
    elif name == "conversation_chunks":
        config = {
            "vectors_config": models.VectorParams(size=1024, distance=models.Distance.COSINE),
            "sparse_vectors_config": {
                "text_sparse": models.SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            },
        }
        payload_indexes = (
            ("conversation_id", models.PayloadSchemaType.KEYWORD),
            ("message_id", models.PayloadSchemaType.KEYWORD),
            ("bucket_id", models.PayloadSchemaType.KEYWORD),
            ("user_id", models.PayloadSchemaType.KEYWORD),
            ("role", models.PayloadSchemaType.KEYWORD),
            ("chunk_index", models.PayloadSchemaType.INTEGER),
            ("status", models.PayloadSchemaType.KEYWORD),
        )
    else:
        raise SystemExit(f"Unknown collection: {name}")

    if recreate and name in existing:
        client.delete_collection(name)
        existing.remove(name)

    if name not in existing:
        client.create_collection(collection_name=name, **config)

    for field_name, schema in payload_indexes:
        try:
            client.create_payload_index(
                collection_name=name,
                field_name=field_name,
                field_schema=schema,
            )
        except Exception:
            # Qdrant will reject duplicate payload indexes; that is fine for idempotent bootstrap.
            pass


_DEFAULT_LOCAL_PATH = Path(__file__).resolve().parent / "data" / "local"


def main() -> None:
    parser = argparse.ArgumentParser(description="Bootstrap Aiveilix Qdrant collections.")
    parser.add_argument("--mode", choices=("local", "remote"), default="local")
    parser.add_argument(
        "--path",
        default=str(_DEFAULT_LOCAL_PATH),
        help="Local Qdrant data path for embedded mode.",
    )
    parser.add_argument("--url", help="Remote Qdrant URL.")
    parser.add_argument("--api-key", help="Remote Qdrant API key.")
    parser.add_argument("--recreate", action="store_true", help="Recreate collections if they exist.")
    args = parser.parse_args()

    path = Path(args.path) if args.path else None
    client = build_client(args.mode, path, args.url, args.api_key)

    try:
        for collection_name in ("text_chunks", "image_chunks", "conversation_chunks"):
            ensure_collection(client, collection_name, recreate=args.recreate)

        collections = client.get_collections().collections
        print("Qdrant collections ready:")
        for collection in collections:
            print(f"- {collection.name}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
