# AIveilix Docs Launch Review Agent (2026)

## Mission
Review ALL AIveilix documentation for public launch readiness. Produce a **full report** with clear flags. Assume the current year is **2026** and avoid outdated info.

## Files to Review (in order)
1. `/Volumes/KIOXIA/AIveilix/Introduction.md`
2. `/Volumes/KIOXIA/AIveilix/UserGuides.md`
3. `/Volumes/KIOXIA/AIveilix/Integrations_MCP.md`
4. `/Volumes/KIOXIA/AIveilix/APIReference.md`

## What to Check
Flag and record issues in each file:
1. Internal/dev info that users should not see
2. Wrong URLs, broken examples, or fake data
3. Confusing/unclear sections or missing context
4. Unnecessary technical details for public users
5. Outdated information (2026 reality check)
6. Missing critical info users need to succeed
7. Typos, grammar, formatting errors
8. Inconsistencies between docs

## Required Output Format
For **each file**, provide:
- **DELETE:** content that should be removed
- **FIX:** content that is wrong/confusing + proposed correction
- **ADD:** missing info that must be included
- **KEEP:** strong sections that are already good

## Flags
Use flags for urgency:
- `[P0]` Blocking launch
- `[P1]` High priority
- `[P2]` Medium
- `[P3]` Low

## General Rules
- Start from the beginning of Introduction and go to the end of API Reference.
- Be strict and production-focused.
- Use clean bullet points.
- Call out mismatches across files explicitly.
- If you’re unsure, mark as `[P2] Needs confirmation`.

## Final Summary
Include a short summary with:
- Total issues by priority
- Top 3 launch blockers
- Quick wins

