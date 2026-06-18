"""
Combined Phase 1+2+3 verification on a small file.

Cheap end-to-end test:
  - ingest bitcoin_whitepaper.pdf (~180KB, ~9 pages, has a figure + text)
  - verify file manifest (page_count, image_count, section_outline)
  - exercise fetch_file_stats, fetch_section, fetch_pages

Designed so the OCR / visual stages exit quickly because the PDF is native
text. Total budget: a couple of API calls (one summary, one embed batch),
not the multi-minute apple run.

Run:
    set -a; source .env; set +a
    .venv/bin/python scripts/test_small_file_e2e.py
"""
from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PDF_PATH = Path("/Volumes/KIOXIA/AIveilix/benchmark/corpus/bitcoin_whitepaper.pdf")


def _trim(text: str, n: int = 200) -> str:
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[:n].rstrip() + "…"


async def main() -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.bucket import Bucket
    from app.models.file import File
    from app.services.mcp.registry import BUCKET_TOOLS
    from app.services.mcp.tools import fetch_file_stats, fetch_pages, fetch_section
    from app.services.processing_v3.orchestrator import process_file
    from app.services.storage.r2 import build_raw_key, upload_file as r2_upload

    # ── 0. Tool registration check ───────────────────────────────────────────
    print("Step 0 — registered MCP tools:")
    required = ("get_file_stats", "get_section", "get_pages")
    for name in required:
        ok = "✓" if name in BUCKET_TOOLS else "✗ MISSING"
        print(f"  {ok} {name}")
    missing = [n for n in required if n not in BUCKET_TOOLS]
    if missing:
        raise SystemExit(f"Aborting — registry missing: {missing}")

    if not PDF_PATH.exists():
        raise SystemExit(f"PDF missing: {PDF_PATH}")
    file_bytes = PDF_PATH.read_bytes()
    print(f"\nStep 1 — loaded {PDF_PATH.name}: {len(file_bytes):,} bytes")

    # ── 1. Insert file + upload to R2 ────────────────────────────────────────
    async with AsyncSessionLocal() as db:
        bucket = (await db.execute(select(Bucket).limit(1))).scalar_one()
        print(f"  bucket: {bucket.id} ({bucket.name})")

        file_id = uuid.uuid4()
        r2_key = build_raw_key(str(file_id), PDF_PATH.name)
        await asyncio.to_thread(r2_upload, file_bytes, r2_key, "application/pdf")
        print(f"  uploaded to R2: {r2_key}")

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
        print(f"  created file row: {file_id}")

    # ── 2. Run pipeline ──────────────────────────────────────────────────────
    print("\nStep 2 — running pipeline (this should be fast for a 9-page PDF)…")
    await process_file(str(file_id), trigger_source="small_file_test")

    # ── 3. Verify manifest ───────────────────────────────────────────────────
    async with AsyncSessionLocal() as db:
        row = (await db.execute(select(File).where(File.id == file_id))).scalar_one()
        print("\nStep 3 — file manifest after ingest:")
        print(f"  status         : {row.status}")
        print(f"  page_count     : {row.page_count}")
        print(f"  image_count    : {row.image_count}")
        outline = row.section_outline or []
        print(f"  sections       : {len(outline)}")
        for i, s in enumerate(outline[:8]):
            print(f"    [{i}] p.{s['page']:>3}  {_trim(s['heading'], 80)}")
        if len(outline) > 8:
            print(f"    … {len(outline) - 8} more")

        if row.status != "ready":
            raise SystemExit(f"Pipeline did not finish — status={row.status}")

        # ── 4. fetch_file_stats ──────────────────────────────────────────────
        print("\nStep 4 — fetch_file_stats:")
        stats = await fetch_file_stats(db, bucket.id, file_id)
        assert stats["page_count"] == row.page_count
        assert stats["image_count"] == row.image_count
        assert stats["section_count"] == len(outline)
        print(f"  ✓ matches DB row (pages={stats['page_count']}, "
              f"images={stats['image_count']}, sections={stats['section_count']})")

        # ── 5. fetch_section ─────────────────────────────────────────────────
        # Pick a heading from the actual outline so we know it should match.
        if outline:
            first_heading = outline[0]["heading"]
            query = first_heading.split()[0] if first_heading.strip() else first_heading
            print(f"\nStep 5 — fetch_section({query!r}):")
            section = await fetch_section(db, bucket.id, file_id, query)
            print(f"  matched_heading : {section['matched_heading']!r}")
            print(f"  page_range      : {section['page_start']} → {section['page_end']}")
            print(f"  total_chunks    : {section['total_chunks']}")
            print(f"  total_images    : {section['total_images']}")
            for ch in section["chunks"][:2]:
                print(f"    p.{ch['page']:>3}  {_trim(ch['content'])}")
            assert section["matched_heading"] is not None, "section lookup should have matched"
            print("  ✓ section lookup returned content")

        # Miss case
        print("\nStep 5b — fetch_section('nonexistent_xyz_banana'):")
        miss = await fetch_section(db, bucket.id, file_id, "nonexistent_xyz_banana")
        print(f"  matched_heading : {miss['matched_heading']!r}  (expected None)")
        assert miss["matched_heading"] is None
        print("  ✓ miss returns empty match")

        # ── 6. fetch_pages ───────────────────────────────────────────────────
        mid = max(1, row.page_count // 2)
        print(f"\nStep 6 — fetch_pages(1, {mid}):")
        pages = await fetch_pages(db, bucket.id, file_id, 1, mid)
        print(f"  page_range      : {pages['page_start']} → {pages['page_end']}")
        print(f"  total_chunks    : {pages['total_chunks']}")
        print(f"  total_images    : {pages['total_images']}")
        for ch in pages["chunks"][:2]:
            print(f"    p.{ch['page']:>3}  {_trim(ch['content'])}")
        assert pages["total_chunks"] > 0
        print("  ✓ page range fetch returned content")

        # Clamp case
        print("\nStep 6b — fetch_pages(999, 9999) — clamp:")
        clamp = await fetch_pages(db, bucket.id, file_id, 999, 9999)
        print(f"  page_range      : {clamp['page_start']} → {clamp['page_end']}")
        print(f"  total_chunks    : {clamp['total_chunks']}  (expected 0)")
        assert clamp["total_chunks"] == 0
        print("  ✓ out-of-range clamps to empty")

    print("\nAll checks passed — Phase 1/2/3 verified on small file.")


if __name__ == "__main__":
    asyncio.run(main())
