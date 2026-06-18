"""
MCP tool registry — definitions (JSON Schema) + handlers for all 15 tools.

Two registries:
  BUCKET_TOOLS   — 10 tools, scoped to a single bucket
  ACCOUNT_TOOLS  —  5 tools, scoped to the whole user account

Each entry: {"definition": {name, description, inputSchema}, "handler": coro}

Bucket handler signature:  async (db, bucket_id, user_id, args) -> dict
Account handler signature: async (db, user_id, args) -> dict
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException

from app.services.mcp import account_tools as acct
from app.services.mcp import tools as bucket_data


# ── helpers ───────────────────────────────────────────────────────────────────

def _require(args: dict, key: str):
    value = args.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise HTTPException(status_code=400, detail=f"Missing required argument: '{key}'.")
    return value


def _as_uuid(value: str, label: str) -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {label}: '{value}'.")


def _not_found(data, label: str):
    if data is None:
        raise HTTPException(status_code=404, detail=f"{label} not found.")
    return data


# ── bucket tool handlers ──────────────────────────────────────────────────────

async def _h_search(db, bucket_id, user_id, args):
    from app.services.agent.retrieval import search_bucket_documents_with_file_coverage

    query = _require(args, "query")
    top_k = int(args.get("top_k") or 5)
    chunks = await search_bucket_documents_with_file_coverage(
        db, bucket_id, query, limit=min(max(top_k, 1), 10)
    )
    return {
        "results": [
            {
                "chunk_id": str(c.chunk_id),
                "file_id": str(c.file_id),
                "file_name": c.file_name,
                "page": c.page,
                "content": c.content,
                "is_summary": c.is_summary,
                "score": round(c.score, 4),
            }
            for c in chunks
        ]
    }


async def _h_query(db, bucket_id, user_id, args):
    from app.services.agent.service import answer_bucket_query

    question = _require(args, "question")
    resp = await answer_bucket_query(
        db, user_id=str(user_id), bucket_id=str(bucket_id), question=question
    )
    return {
        "answer": resp.answer,
        "sources": resp.sources,
        "used_web_search": resp.used_web_search,
    }


async def _h_list_files(db, bucket_id, user_id, args):
    files = await bucket_data.fetch_files_list(db, bucket_id)
    return {"files": files, "total": len(files)}


async def _h_get_file(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    return _not_found(await bucket_data.fetch_file_spread(db, bucket_id, fid), "File")


async def _h_get_file_summary(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    return _not_found(await bucket_data.fetch_file_summary(db, bucket_id, fid), "File")


async def _h_get_file_stats(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    return _not_found(await bucket_data.fetch_file_stats(db, bucket_id, fid), "File")


async def _h_get_section(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    heading = _require(args, "heading")
    return _not_found(
        await bucket_data.fetch_section(db, bucket_id, fid, heading), "File"
    )


async def _h_get_pages(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    try:
        page_start = int(_require(args, "page_start"))
        page_end = int(_require(args, "page_end"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="page_start and page_end must be integers.")
    return _not_found(
        await bucket_data.fetch_pages(db, bucket_id, fid, page_start, page_end), "File"
    )


async def _h_list_visuals(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    page = args.get("page")
    type_filter = args.get("type")
    try:
        limit = int(args.get("limit") or 200)
        offset = int(args.get("offset") or 0)
        page_val = int(page) if page is not None else None
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="page, limit, offset must be integers.")
    return _not_found(
        await bucket_data.fetch_visual_list(
            db, bucket_id, fid,
            page=page_val, type_filter=type_filter,
            limit=max(1, min(limit, 500)), offset=max(0, offset),
        ),
        "File",
    )


async def _h_get_visual(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    try:
        index = int(_require(args, "index"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="index must be an integer (1-based).")
    return _not_found(
        await bucket_data.fetch_visual(db, bucket_id, fid, index), "File"
    )


async def _h_list_categories(db, bucket_id, user_id, args):
    categories = await bucket_data.fetch_categories(db, bucket_id)
    return {"categories": categories, "total": len(categories)}


async def _h_get_bucket_info(db, bucket_id, user_id, args):
    return _not_found(await bucket_data.fetch_bucket_info(db, bucket_id), "Bucket")


async def _h_list_members(db, bucket_id, user_id, args):
    return _not_found(await bucket_data.fetch_bucket_members(db, bucket_id), "Bucket")


async def _h_get_file_layout(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    return _not_found(await bucket_data.fetch_file_layout(db, bucket_id, fid), "File")


async def _h_get_chunk(db, bucket_id, user_id, args):
    cid = _as_uuid(_require(args, "chunk_id"), "chunk_id")
    return _not_found(await bucket_data.fetch_chunk(db, bucket_id, cid), "Chunk")


async def _h_list_chunks(db, bucket_id, user_id, args):
    fid = _as_uuid(_require(args, "file_id"), "file_id")
    return _not_found(await bucket_data.fetch_chunks_list(db, bucket_id, fid), "File")


# ── account tool handlers (second arg is the AccountMcpToken) ─────────────────

async def _h_list_buckets(db, token, args):
    return await acct.acct_list_buckets(db, token)


async def _h_create_bucket(db, token, args):
    name = _require(args, "name")
    return await acct.acct_create_bucket(
        db, token, name, args.get("description"), args.get("color") or "#3B82F6"
    )


async def _h_get_bucket(db, token, args):
    bid = _as_uuid(_require(args, "bucket_id"), "bucket_id")
    return _not_found(await acct.acct_get_bucket(db, token, bid), "Bucket")


async def _h_delete_bucket(db, token, args):
    bid = _as_uuid(_require(args, "bucket_id"), "bucket_id")
    return _not_found(await acct.acct_delete_bucket(db, token, bid), "Bucket")


async def _h_get_account_info(db, token, args):
    return _not_found(await acct.acct_get_account_info(db, token), "Account")


# ── registry ──────────────────────────────────────────────────────────────────

_EMPTY_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": False}


BUCKET_TOOLS: dict[str, dict] = {
    "search": {
        "definition": {
            "name": "search",
            "description": "PRIMARY TOOL for AI agents answering a user. Semantic search across every document in the bucket — returns the most relevant RAW chunks (text + visual descriptions) with citations, straight from the indexed data with NO extra LLM in the loop (fast, and it cannot add model hallucination). Recommended path: call `search`, then compose the answer YOURSELF from these grounded, cited chunks. Prefer this over `get_file_summary` for specific information, and over `query` whenever you can write the answer yourself.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "top_k": {"type": "integer", "description": "Number of results (1-10).", "default": 5},
                },
                "required": ["query"],
            },
        },
        "handler": _h_search,
    },
    "query": {
        "definition": {
            "name": "query",
            "description": "Server-side answer (convenience). Runs retrieval + reranking + an INTERNAL LLM that returns a complete, cited answer string. Best for thin or non-AI clients that just want a finished answer. If you are already a capable agent (Claude, GPT, etc.), prefer `search` and compose the answer yourself — `query` adds latency and a second model that can err. Do NOT rely on `get_file_summary` for answering questions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question to answer."},
                },
                "required": ["question"],
            },
        },
        "handler": _h_query,
    },
    "list_files": {
        "definition": {
            "name": "list_files",
            "description": "List every file in the bucket with its file_id, name, type, size, page count and status. Call this first when you need a file_id for `get_file`, `list_chunks`, or `get_file_layout`.",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_list_files,
    },
    "get_file": {
        "definition": {
            "name": "get_file",
            "description": "READ A FILE IN FULL. Returns every chunk, every page, every visual description and the metadata + summary for the given file_id. Use this when the user wants to know what's in a specific file or you need the complete content (not just a snippet). This is the authoritative source of truth for a single file's contents — far more detailed than `get_file_summary`.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_id": {"type": "string", "description": "The file UUID."}},
                "required": ["file_id"],
            },
        },
        "handler": _h_get_file,
    },
    "get_file_summary": {
        "definition": {
            "name": "get_file_summary",
            "description": "SHORT OVERVIEW ONLY — returns a brief high-level summary (title, document type, a few bullet points). This is NOT the file's contents and may omit important details. Do NOT rely on this alone to answer questions or describe a file — call `get_file` for the full content, or `query` to answer a question across the bucket. Use this only when the user explicitly asks for a 'summary' or 'overview'.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_id": {"type": "string", "description": "The file UUID."}},
                "required": ["file_id"],
            },
        },
        "handler": _h_get_file_summary,
    },
    "get_file_stats": {
        "definition": {
            "name": "get_file_stats",
            "description": "AUTHORITATIVE STRUCTURAL FACTS for a file: total page count, total image/figure count, and the full section outline ({heading, page}). ALWAYS call this — never the semantic `search` or `query` — when the user asks counting or structural questions like 'how many images/figures', 'how many pages', 'what sections does this doc have', or 'what page does X start on'. Semantic search caps results and will undercount.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_id": {"type": "string", "description": "The file UUID."}},
                "required": ["file_id"],
            },
        },
        "handler": _h_get_file_stats,
    },
    "get_section": {
        "definition": {
            "name": "get_section",
            "description": "Read a NAMED SECTION of a file in full. Looks up the heading in the file's section_outline (call `get_file_stats` first to see available headings), computes the section's page range, and returns every chunk + image within it — in reading order, with no similarity-based truncation. Use this when the user asks 'show me the Water section', 'what does the Carbon chapter say', 'summarize the Appendix', or any question targeting a specific named region of a doc. Matching is case-insensitive and tolerates whitespace differences.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file UUID."},
                    "heading": {"type": "string", "description": "The section heading or a substring of it (e.g. 'Water', 'Scope 3', 'Appendix B')."},
                },
                "required": ["file_id", "heading"],
            },
        },
        "handler": _h_get_section,
    },
    "get_pages": {
        "definition": {
            "name": "get_pages",
            "description": "Read a CONTIGUOUS PAGE RANGE of a file in full — every chunk + image on pages [page_start, page_end], in order, with no similarity-based truncation. Use this for: (1) flat documents with no useful section structure ('what's on pages 40-50'), (2) drilling into a region you located via `get_file_stats`, (3) verifying claims across a known span. Pages are 1-indexed and the range is clamped to the file's actual page_count.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file UUID."},
                    "page_start": {"type": "integer", "description": "First page (1-indexed)."},
                    "page_end": {"type": "integer", "description": "Last page (inclusive)."},
                },
                "required": ["file_id", "page_start", "page_end"],
            },
        },
        "handler": _h_get_pages,
    },
    "list_visuals": {
        "definition": {
            "name": "list_visuals",
            "description": "ENUMERATE EVERY VISUAL ELEMENT in a file (images, charts, icons, logos, product photos, before/after shots — anything the visual-understanding stage extracted) in document order with a STABLE 1-based index. Each entry: {index, page, type, asset_type, description, text_inside, bbox}. Returns exact counts (image_count + text_block_count = total_visuals). ALWAYS call this for visual COUNTS or enumerations — never `search` or `query` (semantic retrieval caps results and undercounts) — when the user asks 'how many images/charts', 'list the visuals', 'show me every chart', or any per-visual enumeration. Use `page` to scope to one page, `type` to filter (e.g. type='chart', type='product_image'), and `limit`/`offset` to page through large docs. Index from this tool is what `get_visual` expects.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file UUID."},
                    "page": {"type": "integer", "description": "Optional — restrict to a single page."},
                    "type": {"type": "string", "description": "Optional — filter by element type or asset_type, e.g. 'chart', 'product_image', 'icon', 'logo'."},
                    "limit": {"type": "integer", "description": "Max entries to return (1-500, default 200).", "default": 200},
                    "offset": {"type": "integer", "description": "Skip the first N entries (for paging).", "default": 0},
                },
                "required": ["file_id"],
            },
        },
        "handler": _h_list_visuals,
    },
    "get_visual": {
        "definition": {
            "name": "get_visual",
            "description": "Return ONE SPECIFIC visual element by its 1-based index in document order — the same index `list_visuals` produces. Use this when the user asks 'what's the Nth image/chart/visual', 'show me visual #42', 'describe the 78th figure', etc. Returns the visual's page, type, full Gemini/Kimi description, text inside the visual, bounding box, AND the enclosing section so the agent knows where in the document it sits. If the index is out of range, returns an error message naming the actual total — call `list_visuals` first if you're not sure how many there are.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "The file UUID."},
                    "index": {"type": "integer", "description": "1-based ordinal index in document reading order."},
                },
                "required": ["file_id", "index"],
            },
        },
        "handler": _h_get_visual,
    },
    "list_categories": {
        "definition": {
            "name": "list_categories",
            "description": "List all categories inside the bucket with their file counts.",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_list_categories,
    },
    "get_bucket_info": {
        "definition": {
            "name": "get_bucket_info",
            "description": "Get general info about the bucket: name, description, total file count, storage usage. Use this when the user asks about the bucket as a whole — not for reading file contents (use `query` or `get_file` for that).",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_get_bucket_info,
    },
    "list_members": {
        "definition": {
            "name": "list_members",
            "description": "List the people with access to this bucket — the workspace owner plus every accepted team member, each with their permissions (upload, download, delete, mcp, see-other-members). Use this when the user asks 'who has access', 'how many users/people are in this bucket', 'who's on the team', or 'list the members'. Returns names and permissions only — no email addresses.",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_list_members,
    },
    "get_file_layout": {
        "definition": {
            "name": "get_file_layout",
            "description": "Get the full raw Layout JSON map of a file: every text and image block on every page, in reading order, each with its bbox, source, sort_order, image_uri and metadata. Use this for structural/layout questions and exact block enumeration — never `search` or `query` for those. Authoritative for 'what's the layout', 'where on the page is X', or counting blocks.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_id": {"type": "string", "description": "The file UUID."}},
                "required": ["file_id"],
            },
        },
        "handler": _h_get_file_layout,
    },
    "get_chunk": {
        "definition": {
            "name": "get_chunk",
            "description": "Get a specific chunk with its full metadata, including nearby image information.",
            "inputSchema": {
                "type": "object",
                "properties": {"chunk_id": {"type": "string", "description": "The chunk UUID."}},
                "required": ["chunk_id"],
            },
        },
        "handler": _h_get_chunk,
    },
    "list_chunks": {
        "definition": {
            "name": "list_chunks",
            "description": "List every chunk for a file in page order — useful when you need granular access to one file's content. For most uses, `get_file` is simpler since it returns chunks grouped by page along with metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {"file_id": {"type": "string", "description": "The file UUID."}},
                "required": ["file_id"],
            },
        },
        "handler": _h_list_chunks,
    },
}


ACCOUNT_TOOLS: dict[str, dict] = {
    "list_buckets": {
        "definition": {
            "name": "list_buckets",
            "description": "List all buckets in the user account with file counts and storage usage.",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_list_buckets,
    },
    "create_bucket": {
        "definition": {
            "name": "create_bucket",
            "description": "Create a new bucket in the user account.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The bucket name."},
                    "description": {"type": "string", "description": "Optional description."},
                    "color": {"type": "string", "description": "Optional hex color, e.g. #10B981.", "default": "#3B82F6"},
                },
                "required": ["name"],
            },
        },
        "handler": _h_create_bucket,
    },
    "get_bucket": {
        "definition": {
            "name": "get_bucket",
            "description": "Get the full details of a specific bucket in the account.",
            "inputSchema": {
                "type": "object",
                "properties": {"bucket_id": {"type": "string", "description": "The bucket UUID."}},
                "required": ["bucket_id"],
            },
        },
        "handler": _h_get_bucket,
    },
    "delete_bucket": {
        "definition": {
            "name": "delete_bucket",
            "description": "Delete a bucket and all of its files and embeddings. This cannot be undone.",
            "inputSchema": {
                "type": "object",
                "properties": {"bucket_id": {"type": "string", "description": "The bucket UUID."}},
                "required": ["bucket_id"],
            },
        },
        "handler": _h_delete_bucket,
    },
    "get_account_info": {
        "definition": {
            "name": "get_account_info",
            "description": "Get overall account information and usage stats.",
            "inputSchema": _EMPTY_SCHEMA,
        },
        "handler": _h_get_account_info,
    },
}


def bucket_tool_definitions(allowed: list[str] | None = None) -> list[dict]:
    """tools/list payload for a bucket token, optionally filtered to allowed names."""
    return [
        entry["definition"]
        for name, entry in BUCKET_TOOLS.items()
        if allowed is None or name in allowed
    ]


def account_tool_definitions() -> list[dict]:
    return [entry["definition"] for entry in ACCOUNT_TOOLS.values()]
