# Agent Progressive Retrieval TODO

Goal: one chat path that answers quickly when top matches are enough, but deepens retrieval when the request needs fuller evidence.

## Todo

- [x] Keep one user-facing chat. Hide the manual Agent mode split.
- [x] Always stream visible work steps while the assistant is responding.
- [x] Start normal questions with fast top-match retrieval.
- [x] If top matches are weak, expand retrieval before answering.
- [x] If a file is mentioned, prioritize that file and expand inside it before bucket-wide search.
- [x] If page, section, count, or visual/object structure is requested, use stored manifest/page data as authoritative context.
- [x] If the user asks for all/every/each/full/detailed coverage, retrieve broader evidence instead of relying on top 5 chunks.
- [x] Preserve the no-guessing rule: say found, partial, or not found based on evidence.

## Implementation Shape

The backend now follows a progressive path:

1. Save user message and read conversation memory.
2. Fetch URLs and current file list when needed.
3. Read structural manifest data when the user asks about pages, sections, counts, or visual elements.
4. Run fast top-match retrieval.
5. If the request asks for broad coverage or the top matches are weak, expand retrieval.
6. Generate the answer only from gathered evidence, then cite the evidence that was actually used.

This keeps simple questions fast while giving exhaustive questions a deeper pass.
