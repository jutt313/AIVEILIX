"""
Verify the structural router fires the right tool for the right question,
using bert.pdf and bitcoin_whitepaper.pdf as test fixtures.

Run:
    set -a; source .env; set +a
    .venv/bin/python scripts/test_structural_router.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _trim(text: str, n: int = 220) -> str:
    return (text or "")[:n].replace("\n", " ⏎ ")


async def main() -> None:
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.file import File
    from app.services.agent.structural_router import maybe_route_structural, _classify

    test_questions = [
        # Should hit count
        "how many pages in bitcoin_whitepaper.pdf?",
        "how many images or figures in bitcoin_whitepaper.pdf?",
        "tell me the total number of sections in bitcoin_whitepaper.pdf",
        # Should hit list_visuals
        "list every visual in bitcoin_whitepaper.pdf",
        "show me all the charts in bitcoin_whitepaper.pdf",
        "break down all figures in bitcoin_whitepaper.pdf",
        # Should hit nth_visual
        "what is the 3rd visual in bitcoin_whitepaper.pdf?",
        "describe figure #2 in bitcoin_whitepaper.pdf",
        # Should hit section
        "show me the Introduction section in bitcoin_whitepaper.pdf",
        # Should hit pages
        "what is on page 7 in bitcoin_whitepaper.pdf",
        "show me pages 4 to 6 in bitcoin_whitepaper.pdf",
        # Should NOT hit (general semantic)
        "explain why blockchain matters",
        "is this a good paper",
    ]

    print("─ Classifier pattern check ─")
    for q in test_questions:
        intents = _classify(q)
        kinds = [i.kind for i in intents] or ["(none — falls to RAG)"]
        print(f"  [{','.join(kinds):<24}]  {q}")

    async with AsyncSessionLocal() as db:
        row = (await db.execute(
            select(File).where(File.name == "bitcoin_whitepaper.pdf", File.status == "ready")
            .order_by(File.created_at.desc())
        )).scalars().first()
        if row is None:
            print("\n[skip live router test — bitcoin_whitepaper.pdf not ingested]")
            return

        bucket_id = row.bucket_id
        file_id = row.id
        # Simulate the production agent flow: it extracts mentioned filenames
        # and passes the resolved file_id list in.
        print(f"\n─ Router invocation (mentioned_file_ids=[{file_id}]) ─")
        for q in test_questions:
            blocks, hits = await maybe_route_structural(db, bucket_id, q, [file_id])
            preview = _trim(blocks[0]) if blocks else "(no blocks — RAG fallback)"
            print(f"  hits={hits!s:<35}  Q: {q}")
            if blocks:
                print(f"    block: {preview}")


if __name__ == "__main__":
    asyncio.run(main())
