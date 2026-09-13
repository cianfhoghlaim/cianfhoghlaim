# Proposal: BAML Extraction Completion + LC Pilot Scale

**Change ID:** `2026-08-10-baml-extraction-completion-v1`
**Date:** 2026-08-10
**Author:** Build agent
**Status:** Draft

## Why

Of the 838 BAML classes across `baml_src/`, only **~6 have real extraction prompts** (aistear, primary, cross_linguistic, syllabus_diagram, plus 1 of 4 England functions). The other **832+ are stub prompts** ("Auto-generated extraction prompt" placeholder text).

This change:
1. Replaces the most impactful stub prompts with real ones for the 6 LC subjects + Aistear themes + Primary areas
2. Scales `lc_chemistry_pilot_assets.py` into a factory pattern (`lc_subject_pilot_factory(subject)`) for all 6 LC subjects
3. Adds an Irish-language BAML client path using `uccix-mistral-24b` for gaeilge
4. Wires the 6 subjects × 3 assets = 18 assets into Dagster

England BAML completion (376 prompts across 3 boards × 92 subjects) is deferred to a follow-up change (the engine to drive it is the same factory pattern).

## What changes

### Code (3 new + 3 modified)

| File | Status | What |
|---|---|---|
| `orchestration/defs/2_materials/lc_extraction/lc_subjects.py` | **NEW** | Factory `lc_subject_pilot_factory(subject)` returning 3 assets + 3 checks per subject |
| `orchestration/defs/2_materials/lc_extraction/lc_subjects/defs.yaml` | **NEW** | Registers the 6 subjects × 3 assets = 18 assets |
| `baml_src/clients.baml` | modified | Adds `gaeilge_lc_client` pointing at `uccix-mistral-24b` via LiteLLM |
| `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml` | modified | Adds real prompts for 6 LC subjects (chemistry already has 1; adds 5 more) |
| `baml_src/british_isles/ireland/education/lc_extraction/{exam_paper,marking_scheme,diagram,cross_linguistic}.baml` | modified | Adds real prompts for 6 LC subjects × 4 kinds = 24 prompts |
| `orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py` | modified | Refactored to delegate to factory |

### Spec (1 spec delta, +6 ADDED Requirements)

- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — 6 ADDED Requirements (real prompts + factory + Irish path)

### Openspec (this change)

- `openspec/changes/2026-08-10-baml-extraction-completion-v1/proposal.md` (this file)
- `openspec/changes/2026-08-10-baml-extraction-completion-v1/tasks.md`
- `openspec/changes/2026-08-10-baml-extraction-completion-v1/specs/british-isles-education-pipeline-v3/spec.md` (delta)

## Dependencies

- **Blocked by:** C2 (uses `bilingual_los` BAML function for the Irish-language path) — ✓ shipped
- **Blocked by:** litellm + llama-swap services running — verified ✓ in current session
- **Blocks:** C4 (England pipeline uses the same BAML extraction template)

## Success criteria

1. `openspec validate 2026-08-10-baml-extraction-completion-v1 --strict` returns 0 errors
2. `baml-cli generate --from baml_src` succeeds (no schema errors)
3. `dagster asset materialize --select lc_<subject>_pilot_loaded` succeeds for all 6 LC subjects
4. Irish-language path uses `uccix-mistral-24b` (not `minimax-m3`)
