"""
Public Demo Bucket layer — service code.

A thin, isolated layer on top of the existing document + chat + team + MCP
machinery. Demo visitors are never ``users``; they live in ``demo_leads`` and are
scoped (by a signed demo session token) to exactly one ``is_demo`` bucket.

See formarketing/DEMO_BUCKET_DEV_PLAN.md.
"""
