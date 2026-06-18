"""
Dump everything about the bitcoin_whitepaper.pdf ingest into a single
folder for human validation.

Writes:
  raw/bitcoin_whitepaper.pdf       — original file (copied from corpus)
  manifest.json                    — files row: page_count, image_count, section_outline
  summary.txt                      — pre-computed AI summary
  layout.json                      — the full structured export from R2
  chunks.jsonl                     — every chunk (page, content, block_id) in reading order
  file_stats.json                  — exact bytes returned by fetch_file_stats
  section_Verify.json              — fetch_section('Verify') output
  pages_1_to_4.json                — fetch_pages(1, 4) output
  README.md                        — quick map of the files
"""
from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT_DIR = Path("/Volumes/KIOXIA/AIveilix/phase1_3_validation_output")
CORPUS_PDF = Path("/Volumes/KIOXIA/AIveilix/benchmark/corpus/bitcoin_whitepaper.pdf")


def _jdump(obj, path: Path) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


async def main() -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.chunk import Chunk
    from app.models.file import File
    from app.models.summary import Summary
    from app.services.mcp.tools import fetch_file_stats, fetch_pages, fetch_section
    from app.services.storage.r2 import download_file

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)

    # 1. Copy the raw PDF
    shutil.copy2(CORPUS_PDF, OUT_DIR / "raw" / CORPUS_PDF.name)

    async with AsyncSessionLocal() as db:
        row = (await db.execute(
            select(File)
            .where(File.name == "bitcoin_whitepaper.pdf", File.status == "ready")
            .order_by(File.created_at.desc())
        )).scalars().first()
        if row is None:
            raise SystemExit("File not found — run test_small_file_e2e.py first")

        file_id = row.id
        bucket_id = row.bucket_id

        # 2. Manifest from Postgres
        manifest = {
            "file_id": str(row.id),
            "name": row.name,
            "type": row.type,
            "size_bytes": row.size,
            "status": row.status,
            "r2_path": row.r2_path,
            "layout_json_path": row.layout_json_path,
            "page_count": row.page_count,
            "image_count": row.image_count,
            "section_outline": row.section_outline,
            "created_at": row.created_at.isoformat(),
            "updated_at": row.updated_at.isoformat(),
        }
        _jdump(manifest, OUT_DIR / "manifest.json")

        # 3. Summary
        summary = (await db.execute(
            select(Summary.content).where(Summary.file_id == file_id)
            .order_by(Summary.created_at.desc()).limit(1)
        )).scalar_one_or_none() or ""
        (OUT_DIR / "summary.txt").write_text(summary)

        # 4. Layout JSON (from R2)
        if row.layout_json_path:
            layout_bytes = await asyncio.to_thread(download_file, row.layout_json_path)
            (OUT_DIR / "layout.json").write_bytes(layout_bytes)

        # 5. Chunks (Postgres)
        chunks = (await db.execute(
            select(Chunk).where(Chunk.file_id == file_id, Chunk.status == "embedded")
            .order_by(Chunk.page.asc(), Chunk.id)
        )).scalars().all()
        with (OUT_DIR / "chunks.jsonl").open("w") as f:
            for c in chunks:
                f.write(json.dumps({
                    "chunk_id": str(c.id),
                    "page": c.page,
                    "block_id": c.block_id,
                    "token_count": c.token_count,
                    "content": c.content,
                }, ensure_ascii=False) + "\n")

        # 6. New-tool outputs
        _jdump(await fetch_file_stats(db, bucket_id, file_id), OUT_DIR / "file_stats.json")
        _jdump(await fetch_section(db, bucket_id, file_id, "Verify"), OUT_DIR / "section_Verify.json")
        _jdump(await fetch_pages(db, bucket_id, file_id, 1, 4), OUT_DIR / "pages_1_to_4.json")

    # 7. README
    readme = f"""# Phase 1+2+3 validation bundle — bitcoin_whitepaper.pdf

Source PDF:  {CORPUS_PDF}
File ID:     {manifest['file_id']}

## What's in this folder

| File | What it contains |
|------|------------------|
| raw/bitcoin_whitepaper.pdf | The original PDF (byte-identical copy from corpus). |
| manifest.json              | The `files` row in Postgres: page_count, image_count, section_outline, etc. |
| summary.txt                | Pre-computed AI summary (fell back to heuristic — Gemini key invalid). |
| layout.json                | Full structured layout export (every page → every element with bbox/type/content). The raw layout the LLM never used to see. |
| chunks.jsonl               | Every persisted text chunk in reading order — one JSON per line. {len(chunks)} chunks total. |
| file_stats.json            | Bytes returned by the new `get_file_stats` MCP tool. |
| section_Verify.json        | Bytes returned by the new `get_section('Verify')` MCP tool. |
| pages_1_to_4.json          | Bytes returned by the new `get_pages(1, 4)` MCP tool. |

## How to validate

* Open `manifest.json` → check `page_count` (should be 9), `image_count` (3), `section_outline` length (14).
* Open `layout.json` → spot-check elements per page against the PDF visually.
* Spot-check 2-3 chunks in `chunks.jsonl` against the PDF (page numbers should be correct, content should match).
* `section_Verify.json` should show `matched_heading: "Verify"`, `page_start: 2`, `page_end: 2`, and chunks from page 2.
* `pages_1_to_4.json` should contain only chunks where `page` ∈ [1, 4].
"""
    (OUT_DIR / "README.md").write_text(readme)

    print(f"\nWrote validation bundle → {OUT_DIR}")
    print("Files:")
    for p in sorted(OUT_DIR.rglob("*")):
        if p.is_file():
            size = p.stat().st_size
            print(f"  {p.relative_to(OUT_DIR)}  ({size:,} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
