# Proposal: CopilotKit Action Wiring + Agent Chat Routes

**Change ID:** `2026-08-10-copilotkit-action-wiring-v1`
**Date:** 2026-08-10
**Author:** Build agent
**Status:** Draft

## Why

Of the 14 CopilotKit actions in `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts`, **12 are stubs** returning placeholder data. Only `lookupKeyCompetency` returns real results. The chat UX on `leaving-cert.cianfhoghlaim.ie` is degraded because 12/14 actions return `"TBD"` placeholders.

This change:
1. Wires all 13 remaining stub actions to real handlers (BAML calls, DuckLake queries, Convex queries, FalkorDB lookups)
2. Replaces `/en/agents/$agent.tsx` metadata display with inline `<CopilotKit agent={$agent}>` chat surface
3. Adds a 6th tab "Knowledge Graph Health" to `notebooks/00_control_panel.py` showing last-ingest timestamps per Cognee dataset

## What changes

### Code (5 new + 4 modified)

| File | Status | What |
|---|---|---|
| `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/{syllabus,marking,ocr,learning_outcome,student_progress}.ts` | **NEW ×5** | Real handlers for 5 action categories (split for readability) |
| `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/agents/$agent.tsx` | modified | Replace metadata display with `<CopilotKit agent={$agent}>` inline chat |
| `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` | modified | Wire all 13 actions to real handlers |
| `notebooks/28_knowledge_graph_health.py` | **NEW** | 5-tab marimo notebook for the Knowledge Graph Health tab |
| `notebooks/00_control_panel.py` | modified | Add "Knowledge Graph Health" tab |

### Spec (1 spec delta, +3 ADDED Requirements)

- `openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` — 3 ADDED Requirements (13 actions wired + agent chat route + KG health tab)

### Openspec (this change)

- `openspec/changes/2026-08-10-copilotkit-action-wiring-v1/proposal.md` (this file)
- `openspec/changes/2026-08-10-copilotkit-action-wiring-v1/tasks.md`
- `openspec/changes/2026-08-10-copilotkit-action-wiring-v1/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (delta)

## Dependencies

- **Blocked by:** C1 (uses `md:cianfhoghlaim.ocr_results` for lookupOcrResult) — ✓ shipped
- **Blocked by:** C2 (uses Cognee for lookupLearningOutcome + searchBilingualLOPair) — ✓ shipped
- **Blocks:** None (terminal change for the v4 BIEP v3 rollout)

## Success criteria

1. `openspec validate 2026-08-10-copilotkit-action-wiring-v1 --strict` returns 0 errors
2. All 14 CopilotKit actions return real data (not placeholder)
3. `/en/agents/math_agent` renders inline chat (not just metadata)
4. Control panel "Knowledge Graph Health" tab shows last-ingest timestamps
