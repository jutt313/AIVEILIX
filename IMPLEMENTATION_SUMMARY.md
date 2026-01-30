# AI-Driven Source Citation Implementation Summary

## Date: 2026-01-30

## Overview
Successfully implemented AI-driven source citation system where the AI intelligently chooses which sources to cite based on actual usage, replacing the previous automatic source tracking system.

## Files Changed
- `/Volumes/KIOXIA/AIveilix/backend/app/routers/chat.py`

## Changes Made

### 1. Added Two New Helper Functions (lines 20-97)

#### `build_source_inventory()`
- Creates a structured inventory of all available sources
- Generates unique IDs for each source (e.g., `analysis_abc123`, `chunk_xyz789`, `web_0`)
- Returns both a dictionary mapping IDs to metadata and formatted text for AI context
- Handles: file analyses, file chunks, and web search results

#### `parse_ai_response_with_citations()`
- Parses AI's JSON response to extract message and citations
- Maps citation IDs back to full source metadata
- Implements fallback: if JSON parsing fails, returns full response with empty sources array
- Logs warnings for invalid source IDs cited by AI

### 2. Updated System Prompt (lines 108-134)
- Removed automatic source listing instructions
- Added JSON response format requirement
- Specified citation rules:
  - Only cite sources actually used
  - Use exact source IDs from inventory
  - Return empty array if no sources used
  - Don't invent source IDs

### 3. Removed Automatic Source Tracking
Removed automatic source append operations at:
- Lines 138-142: Analysis sources
- Lines 155-159: Chunk sources
- Lines 172-174, 183-185: Full file sources
- Lines 214-219: Web search sources

### 4. Updated Context Building (lines 318-339)
- Build source inventory using new helper function
- Add inventory text to context message (shows AI available sources)
- Changed instruction from "DO NOT write 'Sources'" to "Answer based on the available sources above"

### 5. Updated DeepSeek API Call (lines 352-367)
- Added `response_format={"type": "json_object"}` to enable JSON mode
- Parse raw response to extract message text and citations
- Log number of sources cited by AI

### 6. Updated Response Handling (lines 381-395)
- Save `message_text` instead of raw `ai_response`
- Save `cited_sources` instead of automatic `sources`
- Return parsed message and citations to frontend

## How It Works

1. **Build Inventory**: System creates a map of all available sources with unique IDs
2. **Provide Context**: AI receives both the content AND the source inventory
3. **AI Decides**: AI analyzes the query and chooses which sources to cite
4. **JSON Response**: AI returns structured JSON with message and cited source IDs
5. **Parse & Map**: Backend extracts citations and maps IDs to full metadata
6. **Return**: Frontend receives message + only the sources AI actually used

## Benefits

1. **Accuracy**: Only sources actually used in the answer are shown
2. **Less Noise**: No more showing all 10 files when only 2 were relevant
3. **Smart Citations**: AI can choose not to cite anything for general knowledge questions
4. **Flexible**: Works with analyses, chunks, full files, and web search results
5. **Robust**: Fallback handling if AI doesn't follow JSON format

## Frontend Compatibility
- No frontend changes needed
- API response format unchanged (message + sources array)
- Sources display logic remains the same
- Empty sources array properly handled (no Sources section shown)

## Testing Recommendations

1. **Empty sources test**: Ask general question → verify `cited_sources: []`
2. **Single file test**: Ask about specific document → verify 1-2 sources
3. **Multi-file test**: Ask question needing multiple docs → verify multiple sources
4. **Web + files test**: Trigger web search + files → verify mixed sources
5. **JSON failure test**: Check logs for fallback handling
6. **Invalid ID test**: Monitor logs for warnings about invalid source IDs

## Rollback Plan
If issues occur, can quickly restore by:
1. Uncommenting deleted source append lines
2. Reverting system prompt changes
3. Removing JSON mode and parsing logic

## Database Impact
None - schema unchanged, still uses same `sources` JSONB field in messages table.
