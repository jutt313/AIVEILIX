from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.services.agent.retrieval import (
    RetrievedDocumentChunk,
    _category_match_score,
    _has_standalone_image_intent,
    _is_document_like_file,
    search_bucket_documents_with_file_coverage,
)


def _chunk(file_id: uuid.UUID, file_name: str) -> RetrievedDocumentChunk:
    return RetrievedDocumentChunk(
        chunk_id=uuid.uuid4(),
        file_id=file_id,
        file_name=file_name,
        page=1,
        content=f"evidence from {file_name}",
        score=0.9,
    )


def test_category_match_scores_ai_and_physics_summaries_without_matching_finance():
    query = "Compare the AI papers with the physics paper in this bucket."
    assert _category_match_score(query, "attention.pdf", "Transformer neural machine translation paper") > 0
    assert _category_match_score(query, "0704.0001v2.pdf", "QCD diphoton production at LHC collider energies") > 0
    assert _category_match_score(query, "apple_q4_2023.pdf", "Apple financial revenue earnings report") == 0


def test_document_like_filter_excludes_images():
    assert _is_document_like_file("attention.pdf", "application/pdf")
    assert not _is_document_like_file("Screenshot 2026-06-01 at 23.06.49.png", "image/png")


def test_standalone_image_intent_detects_image_file_queries():
    assert _has_standalone_image_intent("What is shown in the three screenshot image files?")
    assert _has_standalone_image_intent("Summarize the 3 images in this bucket.")
    assert not _has_standalone_image_intent("What charts are in the attention paper?")


@pytest.mark.asyncio
async def test_cross_doc_query_forces_evidence_from_each_matched_file():
    bucket_id = uuid.uuid4()
    gpt_id = uuid.uuid4()
    llama_id = uuid.uuid4()

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        if file_ids == [gpt_id]:
            return [_chunk(gpt_id, "gpt3.pdf")]
        if file_ids == [llama_id]:
            return [_chunk(llama_id, "llama2.pdf")]
        return []

    general = [_chunk(llama_id, "llama2.pdf")]

    with (
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[gpt_id, llama_id]),
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch("app.services.agent.retrieval.search_bucket_documents", new=AsyncMock(return_value=general)) as standard_search,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "Compare GPT-3's largest variant with Llama 2's largest variant.",
            limit=5,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert {"gpt3.pdf", "llama2.pdf"} <= returned_files
    assert standard_search.await_args.kwargs["allowed_file_ids"] == [gpt_id, llama_id]


@pytest.mark.asyncio
async def test_non_cross_doc_query_uses_standard_search_only():
    bucket_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    standard = [_chunk(doc_id, "ibm-annual-report-2025.pdf")]

    with (
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=standard),
        ) as standard_search,
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[]),
        ) as resolve_targets,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "What was IBM revenue?",
            limit=5,
        )

    assert chunks == standard
    standard_search.assert_awaited_once()
    resolve_targets.assert_not_awaited()


@pytest.mark.asyncio
async def test_cross_doc_query_fans_out_to_document_files_when_names_are_vague():
    bucket_id = uuid.uuid4()
    attention_id = uuid.uuid4()
    physics_id = uuid.uuid4()

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        if file_ids == [attention_id]:
            return [_chunk(attention_id, "attention.pdf")]
        if file_ids == [physics_id]:
            return [_chunk(physics_id, "0704.0001v2.pdf")]
        return []

    with (
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[]),
        ),
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=[attention_id, physics_id]),
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ),
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "Compare the AI papers with the physics paper in this bucket.",
            limit=5,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert {"attention.pdf", "0704.0001v2.pdf"} <= returned_files


@pytest.mark.asyncio
async def test_all_documents_query_uses_every_document_file_even_when_two_match_strongly():
    bucket_id = uuid.uuid4()
    apple_id = uuid.uuid4()
    physics_id = uuid.uuid4()
    attention_id = uuid.uuid4()

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        names = {
            apple_id: "apple_q4_2023.pdf",
            physics_id: "0704.0001v2.pdf",
            attention_id: "attention.pdf",
        }
        return [_chunk(file_ids[0], names[file_ids[0]])]

    with (
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=[apple_id, physics_id, attention_id]),
        ) as fallback,
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[apple_id, physics_id]),
        ) as resolve_targets,
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ) as standard_search,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "List the key numbers and metrics across all documents in this bucket.",
            limit=6,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert {"apple_q4_2023.pdf", "0704.0001v2.pdf", "attention.pdf"} <= returned_files
    fallback.assert_awaited_once()
    resolve_targets.assert_not_awaited()
    assert standard_search.await_args.kwargs["allowed_file_ids"] == [apple_id, physics_id, attention_id]


@pytest.mark.asyncio
async def test_any_documents_risk_query_uses_every_document_file():
    bucket_id = uuid.uuid4()
    apple_id = uuid.uuid4()
    physics_id = uuid.uuid4()
    attention_id = uuid.uuid4()

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        names = {
            apple_id: "apple_q4_2023.pdf",
            physics_id: "0704.0001v2.pdf",
            attention_id: "attention.pdf",
        }
        return [_chunk(file_ids[0], names[file_ids[0]])]

    with (
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=[apple_id, physics_id, attention_id]),
        ) as fallback,
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[physics_id]),
        ) as resolve_targets,
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ) as standard_search,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "What risks or limitations are mentioned across any of the documents in this bucket?",
            limit=6,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert {"apple_q4_2023.pdf", "0704.0001v2.pdf", "attention.pdf"} <= returned_files
    fallback.assert_awaited_once()
    resolve_targets.assert_not_awaited()
    assert standard_search.await_args.kwargs["allowed_file_ids"] == [apple_id, physics_id, attention_id]


@pytest.mark.asyncio
async def test_natural_risks_query_uses_every_document_file():
    bucket_id = uuid.uuid4()
    apple_id = uuid.uuid4()
    physics_id = uuid.uuid4()
    attention_id = uuid.uuid4()

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        names = {
            apple_id: "apple_q4_2023.pdf",
            physics_id: "0704.0001v2.pdf",
            attention_id: "attention.pdf",
        }
        return [_chunk(file_ids[0], names[file_ids[0]])]

    with (
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=[apple_id, physics_id, attention_id]),
        ) as fallback,
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[physics_id]),
        ) as resolve_targets,
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ) as standard_search,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "What are the risks and limitations?",
            limit=6,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert {"apple_q4_2023.pdf", "0704.0001v2.pdf", "attention.pdf"} <= returned_files
    fallback.assert_awaited_once()
    resolve_targets.assert_not_awaited()
    assert standard_search.await_args.kwargs["allowed_file_ids"] == [apple_id, physics_id, attention_id]


@pytest.mark.asyncio
async def test_generic_roi_query_fetches_from_all_company_documents():
    bucket_id = uuid.uuid4()
    company_ids = [uuid.uuid4() for _ in range(10)]
    company_names = {
        file_id: f"company_{index}_financials.pdf"
        for index, file_id in enumerate(company_ids, start=1)
    }

    async def fake_search_for_files(db, bucket_id_arg, query, file_ids, limit=5):
        assert bucket_id_arg == bucket_id
        return [_chunk(file_ids[0], company_names[file_ids[0]])]

    with (
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=company_ids),
        ) as fallback,
        patch(
            "app.services.agent.retrieval._resolve_query_target_files",
            new=AsyncMock(return_value=[]),
        ) as resolve_targets,
        patch(
            "app.services.agent.retrieval.search_bucket_documents_for_files",
            new=fake_search_for_files,
        ),
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ) as standard_search,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "Tell me the ROI",
            limit=10,
        )

    returned_files = {chunk.file_name for chunk in chunks}
    assert set(company_names.values()) <= returned_files
    fallback.assert_awaited_once()
    resolve_targets.assert_not_awaited()
    assert standard_search.await_args.kwargs["allowed_file_ids"] == company_ids


@pytest.mark.asyncio
async def test_standalone_image_query_fetches_each_image_file():
    bucket_id = uuid.uuid4()
    image_ids = [uuid.uuid4() for _ in range(3)]
    image_chunks = [
        _chunk(image_ids[0], "Screenshot 1.png"),
        _chunk(image_ids[1], "Screenshot 2.png"),
        _chunk(image_ids[2], "Screenshot 3.png"),
    ]

    with (
        patch(
            "app.services.agent.retrieval.search_bucket_standalone_images",
            new=AsyncMock(return_value=image_chunks),
        ) as image_search,
        patch(
            "app.services.agent.retrieval.search_bucket_documents",
            new=AsyncMock(return_value=[]),
        ) as standard_search,
        patch(
            "app.services.agent.retrieval._resolve_cross_doc_fallback_files",
            new=AsyncMock(return_value=[]),
        ) as fallback,
    ):
        chunks = await search_bucket_documents_with_file_coverage(
            None,
            bucket_id,
            "What is shown in the three screenshot image files in this bucket?",
            limit=6,
        )

    assert chunks == image_chunks
    image_search.assert_awaited_once()
    standard_search.assert_not_awaited()
    fallback.assert_not_awaited()
