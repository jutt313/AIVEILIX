"""
Pipeline v3 — API-based document processing.

Ported from the standalone Aiveilix-pipline project and adapted to write into
the main backend's existing schema (files / chunks / summaries / text_chunks).

Processing chain: normalize → render pages → native text → Mistral OCR →
layout elements → visual element extraction (Kimi vision) → export JSON →
section chunking → Voyage embeddings → Qdrant text_chunks.

Entry point: app.services.processing_v3.orchestrator.process_file
"""
