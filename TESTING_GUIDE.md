# AI-Driven Source Citation System - Testing Guide

## Quick Start

### 1. Run Unit Tests
```bash
cd /Volumes/KIOXIA/AIveilix/backend
source venv/bin/activate
python test_citation_system.py
```

Expected output: All 5 tests pass ✅

### 2. Start Backend
```bash
cd /Volumes/KIOXIA/AIveilix/backend
source venv/bin/activate
python run.py
```

Backend should start on http://localhost:7223

### 3. Start Frontend
```bash
cd /Volumes/KIOXIA/AIveilix/frontend
npm run dev
```

Frontend should start on http://localhost:6677

---

## Manual Testing Scenarios

### Test Case 1: Empty Sources (General Knowledge)
**Goal**: Verify AI returns empty sources when not using documents

**Steps**:
1. Create a bucket with some files
2. Ask: "What is 2 + 2?"
3. Check response

**Expected**:
- AI responds with "4"
- No sources section appears below message
- Database check: `sources: []` in messages table

**Log Check**:
```
📦 AI cited 0 sources
```

---

### Test Case 2: Single File Citation
**Goal**: Verify AI cites only the file it uses

**Steps**:
1. Upload file "report.pdf" with content about sales data
2. Upload file "notes.txt" with unrelated content
3. Ask: "What are the sales figures in the report?"

**Expected**:
- AI responds with sales data
- Only 1-2 sources shown (analysis + maybe chunk from report.pdf)
- notes.txt NOT cited
- Sources section shows "report.pdf"

**Log Check**:
```
📦 AI cited 1 sources
📦 Returning 1 sources (web: 0, files: 1)
```

---

### Test Case 3: Multiple File Citations
**Goal**: Verify AI can cite multiple files when needed

**Steps**:
1. Upload "q1_report.pdf" with Q1 data
2. Upload "q2_report.pdf" with Q2 data
3. Ask: "Compare Q1 and Q2 performance"

**Expected**:
- AI uses both files in response
- 2-4 sources shown (analyses + chunks from both files)
- Sources section shows both files

**Log Check**:
```
📦 AI cited 3 sources
📦 Returning 3 sources (web: 0, files: 3)
```

---

### Test Case 4: Web Search + Files
**Goal**: Verify mixed source citations

**Steps**:
1. Upload file about Python
2. Ask: "What's the latest Python version in 2026?"

**Expected**:
- Web search triggered (check for 🌐 in logs)
- AI cites both web results AND file
- Sources section shows:
  - Blue web links (clickable)
  - Gray file badges
- Mixed citation types

**Log Check**:
```
🔍 Web search check: True
🌐 TRIGGERING WEB SEARCH
🌐 Web search returned 5 results
📦 AI cited 3 sources
📦 Returning 3 sources (web: 2, files: 1)
```

---

### Test Case 5: No Matching Content
**Goal**: Verify AI doesn't cite files when they're not relevant

**Steps**:
1. Upload file about cooking recipes
2. Ask: "Explain quantum physics"

**Expected**:
- AI responds with general knowledge (or web search)
- Cooking file NOT cited
- Empty or web-only sources

**Log Check**:
```
📦 AI cited 0 sources
```
OR
```
📦 AI cited 1 sources (web: 1, files: 0)
```

---

## Debugging Checklist

### If AI Citations Seem Wrong

1. **Check Logs for JSON Parsing**:
   ```
   ✅ Good: "📦 AI cited X sources"
   ❌ Bad: "JSON parsing failed: ..., using fallback"
   ```

2. **Check for Invalid Source IDs**:
   ```
   ⚠️  "AI cited invalid source: xyz_123"
   ```
   This means AI invented an ID not in inventory

3. **Inspect Source Inventory**:
   Look for `[AVAILABLE SOURCES - Reference by ID when citing]` in context
   Verify all sources have unique IDs

4. **Check Database**:
   ```sql
   SELECT
     content,
     sources,
     created_at
   FROM messages
   WHERE role = 'assistant'
   ORDER BY created_at DESC
   LIMIT 5;
   ```

5. **Verify AI Response Format**:
   Enable debug logging to see raw AI response:
   ```python
   logger.info(f"Raw AI response: {ai_response_raw}")
   ```

---

## Expected Log Flow

### Successful Chat Request:
```
🔍 Web search check: False for message: 'What is in my files?'
📦 AI cited 2 sources
📦 Returning 2 sources (web: 0, files: 2)
```

### With Web Search:
```
🔍 Web search check: True for message: 'Latest news about AI?'
🌐 TRIGGERING WEB SEARCH for: Latest news about AI?
🌐 Web search returned 5 results
✅ Web search context prepared with 5 results
📦 AI cited 3 sources
📦 Returning 3 sources (web: 2, files: 1)
```

### With Fallback Parsing:
```
⚠️  JSON parsing failed: Expecting ',' delimiter: ..., using fallback
📦 AI cited 0 sources
📦 Returning 0 sources (web: 0, files: 0)
```

---

## Common Issues & Fixes

### Issue 1: All Sources Still Appearing
**Symptom**: Every file shown in sources, like before

**Fix**:
- Check if old code still active
- Verify automatic source tracking removed
- Check git diff to confirm changes

### Issue 2: No Sources Ever
**Symptom**: Always empty sources array

**Possible Causes**:
1. JSON parsing always failing
   - Check logs for "JSON parsing failed"
   - Inspect raw AI response
   - Verify DeepSeek JSON mode enabled

2. AI not following format
   - Check system prompt loaded
   - Verify source inventory in context
   - Try adjusting prompt clarity

### Issue 3: Invalid Source IDs
**Symptom**: Warnings about invalid source IDs

**Possible Causes**:
1. AI inventing IDs
   - Make prompt stricter
   - Show clearer examples in inventory

2. ID format mismatch
   - Verify inventory builder IDs match parser expectations
   - Check for special characters in IDs

### Issue 4: Frontend Not Showing Sources
**Symptom**: Backend returns sources but UI doesn't show

**Fix**:
- Check browser console for errors
- Verify API response format unchanged
- Check ChatPanel.jsx source rendering logic

---

## Performance Monitoring

### Key Metrics to Track:

1. **Citation Accuracy**:
   - % of responses with appropriate sources
   - False positives (cited but not used)
   - False negatives (used but not cited)

2. **Response Time**:
   - Before: ~2-3s average
   - After: Should be similar (JSON mode adds minimal overhead)

3. **Token Usage**:
   - Source inventory adds ~100-200 tokens
   - JSON response format adds ~50 tokens
   - Total increase: ~150-250 tokens per request

4. **API Costs**:
   - Monitor DeepSeek API usage
   - Should be similar to before (slight increase from JSON mode)

---

## Rollback Procedure

If critical issues occur:

1. **Quick Revert**:
   ```bash
   git diff backend/app/routers/chat.py
   git checkout backend/app/routers/chat.py
   ```

2. **Verify Revert**:
   ```bash
   python test_citation_system.py
   # Should fail (functions removed)
   ```

3. **Restart Backend**:
   ```bash
   python run.py
   ```

4. **Test Original Behavior**:
   - All read sources appear in citations
   - No JSON parsing

---

## Success Criteria

✅ Implementation successful if:

1. Unit tests pass (all 5 tests)
2. Backend starts without errors
3. Chat responses include intelligent citations
4. Empty sources for general knowledge questions
5. Multiple sources for multi-file questions
6. Web + file mixing works
7. No regression in response quality
8. Frontend displays sources correctly

---

## Next Steps (Future Enhancements)

1. **Citation Confidence Scores**:
   - AI returns confidence per citation
   - UI shows strength of evidence

2. **Citation Context**:
   - AI includes quote/snippet for each source
   - Hover shows relevant excerpt

3. **Citation Analytics**:
   - Track most-cited files
   - Identify unused files

4. **Smart Re-ranking**:
   - Order sources by relevance
   - Group by type (files vs web)

5. **Citation Validation**:
   - Verify cited content actually used in response
   - Flag hallucinated citations
