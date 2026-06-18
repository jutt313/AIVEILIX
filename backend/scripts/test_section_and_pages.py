"""
Phase 2 + 3 end-to-end test: calls fetch_section and fetch_pages against the
apple_env_2023.pdf row created by test_asset_manifest.py. Prints the matched
section page range + content head, then a page range fetch.

Run:
    set -a; source .env; set +a
    .venv/bin/python scripts/test_section_and_pages.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _trim(text: str, n: int = 240) -> str:
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[:n].rstrip() + "…"


async def main() -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.file import File
    from app.services.mcp.registry import BUCKET_TOOLS
    from app.services.mcp.tools import fetch_pages, fetch_section

    print("Registered bucket tools:")
    for name in BUCKET_TOOLS:
        print(f"  - {name}")
    for required in ("get_file_stats", "get_section", "get_pages"):
        marker = "✓" if required in BUCKET_TOOLS else "✗ MISSING"
        print(f"  {marker} {required}")

    async with AsyncSessionLocal() as db:
        row = (await db.execute(
            select(File).where(File.name == "apple_env_2023.pdf", File.status == "ready")
            .order_by(File.created_at.desc())
        )).scalars().first()
        if row is None:
            raise SystemExit("apple_env_2023.pdf not found — run test_asset_manifest.py first")
        file_id = row.id
        bucket_id = row.bucket_id
        print(f"\nTarget file: {file_id}  page_count={row.page_count}  sections={len(row.section_outline or [])}")

        print("\n── fetch_section('Water') ───────────────────────────")
        section = await fetch_section(db, bucket_id, file_id, "Water")
        print(f"  matched_heading : {section['matched_heading']!r}")
        print(f"  page_range      : {section['page_start']} → {section['page_end']}")
        print(f"  total_chunks    : {section.get('total_chunks')}")
        print(f"  total_images    : {section.get('total_images')}")
        for ch in section["chunks"][:3]:
            print(f"    p.{ch['page']:>3}  {_trim(ch['content'])}")
        if len(section["chunks"]) > 3:
            print(f"    … {len(section['chunks']) - 3} more chunks")

        print("\n── fetch_section('Carbon') ──────────────────────────")
        section2 = await fetch_section(db, bucket_id, file_id, "Carbon")
        print(f"  matched_heading : {section2['matched_heading']!r}")
        print(f"  page_range      : {section2['page_start']} → {section2['page_end']}")
        print(f"  total_chunks    : {section2.get('total_chunks')}")

        print("\n── fetch_section('nonexistent banana') ──────────────")
        miss = await fetch_section(db, bucket_id, file_id, "nonexistent banana")
        print(f"  matched_heading : {miss['matched_heading']!r}  (expected None)")
        print(f"  total_chunks    : {len(miss['chunks'])}")

        print("\n── fetch_pages(40, 42) ──────────────────────────────")
        pages = await fetch_pages(db, bucket_id, file_id, 40, 42)
        print(f"  page_range      : {pages['page_start']} → {pages['page_end']}")
        print(f"  total_chunks    : {pages['total_chunks']}")
        print(f"  total_images    : {pages['total_images']}")
        for ch in pages["chunks"][:3]:
            print(f"    p.{ch['page']:>3}  {_trim(ch['content'])}")
        for img in pages["images"][:2]:
            print(f"    [img p.{img['page']}] {_trim(img['description'], 120)}")

        print("\n── fetch_pages(999, 9999) — clamp test ──────────────")
        clamp = await fetch_pages(db, bucket_id, file_id, 999, 9999)
        print(f"  page_range      : {clamp['page_start']} → {clamp['page_end']}  (clamped to file)")
        print(f"  total_chunks    : {clamp['total_chunks']}  (expected 0)")


if __name__ == "__main__":
    asyncio.run(main())
