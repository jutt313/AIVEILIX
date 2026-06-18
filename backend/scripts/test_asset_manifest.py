"""
Phase 1 end-to-end test: ingest apple_env_2023.pdf, print the file manifest
produced by the new orchestrator step, then call fetch_file_stats to confirm
the MCP-tool path returns the same values.

Run:
    set -a; source .env; set +a
    .venv/bin/python scripts/test_asset_manifest.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path

# Make `app` importable when running this script directly from backend/.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PDF_PATH = Path("/Volumes/KIOXIA/AIveilix/benchmark/corpus/apple_env_2023.pdf")


async def main() -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.bucket import Bucket
    from app.models.file import File
    from app.services.mcp.tools import fetch_file_stats
    from app.services.processing_v3.orchestrator import process_file
    from app.services.storage.r2 import build_raw_key, upload_file as r2_upload

    if not PDF_PATH.exists():
        raise SystemExit(f"PDF missing: {PDF_PATH}")

    file_bytes = PDF_PATH.read_bytes()
    print(f"Loaded {PDF_PATH.name}: {len(file_bytes):,} bytes")

    async with AsyncSessionLocal() as db:
        bucket = (await db.execute(select(Bucket).limit(1))).scalar_one()
        print(f"Target bucket: {bucket.id} ({bucket.name})")

        file_id = uuid.uuid4()
        r2_key = build_raw_key(str(file_id), PDF_PATH.name)
        await asyncio.to_thread(r2_upload, file_bytes, r2_key, "application/pdf")
        print(f"Uploaded to R2: {r2_key}")

        row = File(
            id=file_id,
            bucket_id=bucket.id,
            user_id=bucket.user_id,
            name=PDF_PATH.name,
            type="application/pdf",
            size=len(file_bytes),
            r2_path=r2_key,
            status="processing",
        )
        db.add(row)
        await db.commit()
        print(f"Created file row: {file_id}")

    print("\nRunning pipeline…")
    await process_file(str(file_id), trigger_source="manifest_test")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(File).where(File.id == file_id))
        row = result.scalar_one()
        print("\n── File row after ingest ─────────────────────────────")
        print(f"  status         : {row.status}")
        print(f"  page_count     : {row.page_count}")
        print(f"  image_count    : {row.image_count}")
        outline = row.section_outline or []
        print(f"  sections       : {len(outline)}")
        for i, s in enumerate(outline[:10]):
            print(f"    [{i}] p.{s['page']:>3}  {s['heading'][:80]}")
        if len(outline) > 10:
            print(f"    … {len(outline) - 10} more")

        print("\n── fetch_file_stats (MCP tool path) ─────────────────")
        stats = await fetch_file_stats(db, bucket.id, file_id)
        print(json.dumps(
            {**stats, "section_outline": stats["section_outline"][:5] + (["…"] if len(stats["section_outline"]) > 5 else [])},
            indent=2,
        ))


if __name__ == "__main__":
    asyncio.run(main())
