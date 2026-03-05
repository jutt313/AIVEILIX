# Investigation UX Implementation Plan

## Goal
Make investigation feel like a live analyst (human narration), not a backend log stream.

User uploads a file + sends a prompt in one flow, then sees:
1. Natural investigation narration (what is being checked, what is seen)
2. Intent-aware focus (layout copy vs fact-check vs general)
3. Automatic final answer when processing finishes

No internal pipeline terms should be shown to users (`chunking`, `embedding`, `saving chunks`, etc.).

---

## Current Problems
1. Investigation text is too technical/robotic.
2. Internal implementation details leak into user-facing stream.
3. Chat can end with "still processing, ask again" before auto-answer handoff.
4. Investigation appears as reasoning-like text, not a clean investigation experience.

---

## Target UX
Example style:
- "Opening your PDF..."
- "I can see this is a skincare landing page."
- "Checking hero section and headline claims."
- "I found 62 visuals; reviewing them section by section."
- "In section 1, visuals emphasize before/after proof."
- "Now validating the main claims against the copy."
- "I have enough context. Preparing your answer."

If user intent is explicit:
- `layout_copy`: focus on structure, hierarchy, sections, CTA design
- `fact_check`: trigger web verification and evidence notes
- `general`: balanced read

---

## Architecture (Backend -> Frontend)

### 1) Intent Extraction (from user message)
File: `backend/app/routers/chat.py`

Add a lightweight intent classifier before streaming:
- `layout_copy`
- `fact_check`
- `general`

Store in request-local variable and attach to investigation events.

### 2) Investigation Event Model (User-Safe)
Files:
- `backend/app/services/file_processor.py`
- `backend/app/routers/files.py`

Emit structured investigation events from extraction/OCR:
- `stage_start`
- `observation`
- `progress`
- `stage_complete`
- `investigation_ready`

Event payload (user-safe):
- `type`
- `label` (user-facing sentence)
- `current`, `total` (optional)
- `section` (optional)
- `image_index` (optional)
- `intent` (optional)

Do not emit backend internals to UI labels.

### 3) Natural Narration Layer
File: `backend/app/routers/chat.py`

Create a translator function that maps raw stage/meta -> human narration.

Rules:
1. Keep grounded in real progress/meta only.
2. Never invent claims not observed.
3. Never expose technical internals.
4. Dedupe repeated lines.
5. Emit at controlled cadence (avoid spam).

### 4) Stream Behavior (Single Request)
File: `backend/app/routers/chat.py`

When file is `pending/processing`:
1. Start investigation stream immediately.
2. Continue sending narration updates while file processes.
3. When file is `ready`, continue in same stream into final AI answer.
4. Only send fallback wait message on hard timeout/error.

No "ask again" during normal completion path.

### 5) Frontend Rendering Separation
Files:
- `frontend/src/components/ChatPanel.jsx`
- `frontend/src/components/InvestigationCanvas.jsx`
- `frontend/src/services/api.js`

Render investigation updates in investigation UI area, not assistant reasoning block.

Recommended SSE event handling:
- `investigation_update` -> InvestigationCanvas timeline/state
- `phase_change/thinking/response/done` -> assistant message flow

If backend keeps using `thinking` for investigation temporarily, route those lines into InvestigationCanvas by marker/metadata and keep assistant reasoning clean.

---

## Implementation Checklist

### Backend
- [ ] Add intent extraction helper in `chat.py`
- [ ] Add user-safe narration formatter in `chat.py`
- [ ] Emit investigation observation/progress events from `file_processor.py`
- [ ] Replace technical labels with user-facing labels in investigation path
- [ ] Keep stream alive until `ready` then auto-continue to answer
- [ ] Remove normal-path "ask again" fallback
- [ ] Add timeout/error fallback with clear user-safe message
- [ ] Add logs for investigation lifecycle (`start`, `updates`, `ready`, `handoff`)

### Frontend
- [ ] Add dedicated investigation event handler in `api.js` parser
- [ ] Route investigation events to `InvestigationCanvas`
- [ ] Keep assistant message area for final answer (and optional reasoning), not progress spam
- [ ] Dedupe repeated investigation lines in UI
- [ ] Preserve chip attach-on-send flow
- [ ] Show intent-aware investigation header (Layout/Fact-check/General)

### UX/Content Rules
- [ ] No `chunking/embedding` in user-facing text
- [ ] Narration is observation-first, sequential, and concise
- [ ] Show counters where useful (`image 12/62`) without technical jargon

### QA
- [ ] Upload heavy PDF (many images) -> narration starts quickly and stays live
- [ ] User prompt with `layout_copy` -> structure-focused narration and answer
- [ ] User prompt with `fact_check` -> verification-focused narration and answer
- [ ] Fast text-only file -> short 2-4 step narration then answer
- [ ] No final "ask again" if processing completed within timeout

---

## Acceptance Criteria
1. Investigation feels like analyst commentary, not backend tracing.
2. No internal implementation terms visible to users.
3. Same message flow: upload+prompt -> investigation -> final answer (no manual re-ask).
4. Investigation UI and answer UI are clearly separated.
5. Works for both large PDFs and small text files.

---

## Suggested Rollout
1. Ship behind flag: `INVESTIGATION_NARRATION_V2=true`
2. Internal test on large PDF + 3 intent types
3. Enable for all users after 24h clean logs
