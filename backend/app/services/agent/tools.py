from __future__ import annotations

"""
Agent tools — callable actions the agent can take during a conversation turn.

Tools:
  fetch_url              — fetch a webpage and return cleaned text
  search_web_and_summarize — DuckDuckGo search + LLM summary
  write_file             — write a .md file to bucket storage + trigger RAG indexing
  read_file              — read raw .md content from bucket storage
  list_files             — list all files in a bucket
  get_file_summary       — return pre-computed AI summary for a file
"""

import re
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.models.summary import Summary


# ---------------------------------------------------------------------------
# fetch_url
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class FetchUrlResult:
    url: str
    title: str
    content: str
    success: bool
    error: str | None = None


async def fetch_url(url: str) -> FetchUrlResult:
    """Fetch a URL and return cleaned text content."""
    try:
        import asyncio
        import httpx

        def _fetch(url: str) -> tuple[str, str]:
            with httpx.Client(follow_redirects=True, timeout=15) as client:
                response = client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Aiveilix/1.0)"})
                response.raise_for_status()
                html = response.text

            # Try to extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else url

            # Strip HTML tags and collapse whitespace
            text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"&[a-z]+;", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            # Limit to first ~4000 chars to keep prompt manageable
            return title, text[:4000]

        title, content = await asyncio.to_thread(_fetch, url)
        return FetchUrlResult(url=url, title=title, content=content, success=True)

    except Exception as exc:
        return FetchUrlResult(url=url, title="", content="", success=False, error=str(exc))


# ---------------------------------------------------------------------------
# search_web_and_summarize
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class WebSummaryResult:
    query: str
    summary: str
    sources: list[dict[str, str]]


async def search_web_and_summarize(query: str, *, max_results: int = 5) -> WebSummaryResult:
    """Search the web and return an LLM-generated summary of findings."""
    from app.services.agent.web import search_web
    from app.services.agent.llm import select_provider, _generate_with_claude, _generate_with_gemini, _generate_with_openai
    from app.config import settings

    results = await search_web(query, max_results=max_results)
    if not results:
        return WebSummaryResult(query=query, summary="No web results found.", sources=[])

    context = "\n\n".join(
        f"[{i+1}] {r.title}\nURL: {r.url}\n{r.snippet}"
        for i, r in enumerate(results)
    )
    system_prompt = "You are a research assistant. Summarize the web results below into a concise, factual answer. Cite sources by number."
    user_prompt = f"Question: {query}\n\nWeb results:\n{context}\n\nProvide a clear summary."

    provider = select_provider(None)
    summary = None
    try:
        if provider == "claude":
            summary = await _generate_with_claude(system_prompt, user_prompt)
        elif provider == "gemini":
            summary = await _generate_with_gemini(system_prompt, user_prompt)
        else:
            summary = await _generate_with_openai(
                system_prompt, user_prompt,
                model="gpt-4o" if provider == "openai" else "deepseek-chat",
                api_key=settings.openai_api_key if provider == "openai" else settings.deepseek_api_key,
            )
    except Exception:
        pass

    if not summary:
        summary = results[0].snippet if results else "No summary available."

    sources = [{"title": r.title, "url": r.url} for r in results]
    return WebSummaryResult(query=query, summary=summary, sources=sources)


# ---------------------------------------------------------------------------
# write_file
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class WriteFileResult:
    file_id: uuid.UUID
    file_name: str
    r2_path: str
    success: bool
    error: str | None = None


async def write_file(
    db: AsyncSession,
    *,
    bucket_id: uuid.UUID,
    user_id: uuid.UUID,
    file_name: str,
    content: str,
) -> WriteFileResult:
    """Write a .md file to R2 storage, create a File record, and trigger RAG pipeline."""
    import asyncio
    from app.services.storage.r2 import upload_file as r2_upload

    # Ensure .md extension
    if not file_name.endswith(".md"):
        file_name = file_name + ".md"

    file_id = uuid.uuid4()
    r2_key = f"agent_written/{bucket_id}/{file_id}/{file_name}"

    try:
        await asyncio.to_thread(
            r2_upload,
            content.encode("utf-8"),
            r2_key,
            "text/markdown",
        )
    except Exception as exc:
        return WriteFileResult(file_id=file_id, file_name=file_name, r2_path=r2_key, success=False, error=str(exc))

    file_record = File(
        id=file_id,
        bucket_id=bucket_id,
        user_id=user_id,
        name=file_name,
        type="text/markdown",
        size=len(content.encode("utf-8")),
        r2_path=r2_key,
        status="processing",
        is_agent_written=True,
    )
    db.add(file_record)
    await db.flush()
    await db.commit()

    # Trigger RAG pipeline in background
    try:
        from app.services.processing_v3.orchestrator import process_file
        asyncio.create_task(process_file(str(file_id), trigger_source="agent_write"))
    except Exception:
        pass

    return WriteFileResult(file_id=file_id, file_name=file_name, r2_path=r2_key, success=True)


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ReadFileResult:
    file_id: uuid.UUID
    file_name: str
    content: str
    success: bool
    error: str | None = None


async def read_file(
    db: AsyncSession,
    *,
    bucket_id: uuid.UUID,
    file_id: uuid.UUID,
) -> ReadFileResult:
    """Read the raw content of a .md file from R2 storage."""
    import asyncio
    from app.services.storage.r2 import download_file as r2_download

    result = await db.execute(
        select(File).where(File.id == file_id, File.bucket_id == bucket_id)
    )
    file_record = result.scalar_one_or_none()
    if file_record is None:
        return ReadFileResult(file_id=file_id, file_name="", content="", success=False, error="File not found.")

    try:
        raw = await asyncio.to_thread(r2_download, file_record.r2_path)
        content = raw.decode("utf-8", errors="replace")
        return ReadFileResult(file_id=file_id, file_name=file_record.name, content=content, success=True)
    except Exception as exc:
        return ReadFileResult(file_id=file_id, file_name=file_record.name, content="", success=False, error=str(exc))


# ---------------------------------------------------------------------------
# list_files
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class FileListItem:
    file_id: uuid.UUID
    name: str
    status: str
    size: int
    is_agent_written: bool


async def list_files(db: AsyncSession, *, bucket_id: uuid.UUID) -> list[FileListItem]:
    """List all files in a bucket."""
    result = await db.execute(
        select(File.id, File.name, File.status, File.size, File.is_agent_written)
        .where(File.bucket_id == bucket_id)
        .order_by(File.created_at.desc())
    )
    return [
        FileListItem(file_id=row.id, name=row.name, status=row.status, size=row.size, is_agent_written=row.is_agent_written)
        for row in result.all()
    ]


# ---------------------------------------------------------------------------
# get_file_summary
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class FileSummaryResult:
    file_id: uuid.UUID
    file_name: str
    summary: str
    found: bool


async def get_file_summary(db: AsyncSession, *, file_id: uuid.UUID) -> FileSummaryResult:
    """Return the pre-computed AI summary for a file from the summaries table."""
    # Get file name
    file_result = await db.execute(select(File.name).where(File.id == file_id))
    file_name = file_result.scalar_one_or_none() or ""

    # Get latest summary
    summary_result = await db.execute(
        select(Summary.content)
        .where(Summary.file_id == file_id)
        .order_by(Summary.created_at.desc())
        .limit(1)
    )
    summary_content = summary_result.scalar_one_or_none()

    if summary_content:
        return FileSummaryResult(file_id=file_id, file_name=file_name, summary=summary_content, found=True)
    return FileSummaryResult(file_id=file_id, file_name=file_name, summary="", found=False)
