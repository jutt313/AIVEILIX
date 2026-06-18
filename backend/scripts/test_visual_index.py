"""
Phase 4 verification: per-element visual addressing on the already-ingested
files (bitcoin_whitepaper.pdf and apple_env_2023.pdf if present).

Exercises:
  - tool registration check (list_visuals, get_visual)
  - fetch_visual_list returns ordered entries with stable indexes
  - filtering by page and by type
  - fetch_visual at a specific index (incl. the apple file's #78)
  - boundary conditions (index=0, index=N+1)

Run:
    set -a; source .env; set +a
    .venv/bin/python scripts/test_visual_index.py
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
    from app.services.mcp.tools import fetch_visual, fetch_visual_list

    print("Step 0 — tool registry:")
    for name in ("list_visuals", "get_visual"):
        ok = "✓" if name in BUCKET_TOOLS else "✗ MISSING"
        print(f"  {ok} {name}")

    for filename in ("bitcoin_whitepaper.pdf", "apple_env_2023.pdf"):
        async with AsyncSessionLocal() as db:
            row = (await db.execute(
                select(File).where(File.name == filename, File.status == "ready")
                .order_by(File.created_at.desc())
            )).scalars().first()
            if row is None:
                print(f"\n[skip] {filename} not ingested yet")
                continue

            file_id = row.id
            bucket_id = row.bucket_id
            print(f"\n── {filename}  (file_id={file_id}) ─────────────────────")
            print(f"   DB: page_count={row.page_count}  image_count={row.image_count}")

            full = await fetch_visual_list(db, bucket_id, file_id, limit=500)
            print(f"   list_visuals total_visuals={full['total_visuals']}  (returned {len(full['visuals'])} entries)")
            for v in full["visuals"][:3]:
                print(f"     #{v['index']:>3}  p.{v['page']:>3}  {v.get('type','?'):<14}  {_trim(v['description'], 120)}")
            if len(full["visuals"]) > 3:
                print(f"     … {len(full['visuals']) - 3} more")

            # Filter by page (use a page known to have visuals — first one in the list)
            if full["visuals"]:
                sample_page = full["visuals"][0]["page"]
                page_only = await fetch_visual_list(db, bucket_id, file_id, page=sample_page)
                print(f"   filter page={sample_page}: {page_only['filtered_count']} hits")

            # Type filter
            chart_only = await fetch_visual_list(db, bucket_id, file_id, type_filter="chart")
            print(f"   filter type='chart': {chart_only['filtered_count']} hits")

            # get_visual at a specific index
            target_idx = 78 if full["total_visuals"] >= 78 else 1
            single = await fetch_visual(db, bucket_id, file_id, target_idx)
            v = single["visual"]
            print(f"   get_visual(index={target_idx}) →")
            if v is None:
                print(f"     none — {single.get('error')}")
            else:
                print(f"     page {v['page']}, type={v.get('type')}, asset_type={v.get('asset_type')}")
                print(f"     description: {_trim(v['description'], 240)}")
                if v.get("text_inside"):
                    print(f"     text inside: {_trim(v['text_inside'], 140)}")
                sect = single.get("enclosing_section")
                if sect:
                    print(f"     enclosing section: {_trim(sect['heading'], 80)!r} (starts p.{sect['page']})")

            # Out-of-range
            oor_idx = full["total_visuals"] + 1
            oor = await fetch_visual(db, bucket_id, file_id, oor_idx)
            print(f"   get_visual(index={oor_idx}) → {oor.get('error') or 'no error?'}")

            # Index 0 (1-based, so 0 is invalid)
            zero = await fetch_visual(db, bucket_id, file_id, 0)
            print(f"   get_visual(index=0) → {zero.get('error') or 'no error?'}")


if __name__ == "__main__":
    asyncio.run(main())
