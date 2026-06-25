## Why

The 4 Build-Small-2026 hackathon BAML functions (`ExtractCircularMeta`,
`CompareCelticNations`, `GenerateExitCardQuestions`, `GenerateNpcDialogue`)
lived only in `spaces/_common/baml/hackathon_schemas.baml`, with the
hand-rolled `BAML_HACKATHON_CHAINED` client (3-tier raw HF Inference).
This is the **OLD** pattern — the rest of the monorepo has moved to
the canonical `LitellmClient` (LiteLLM gateway at `http://litellm:4000/v1`)
and to the canonical BAML locations (`sruth/oideachais/baml_src/` and
`sruth/tuatha/baml_src/`).

The duplication creates 3 problems:
1. The 4 Spaces cannot easily consume the canonical lakehouse data
   (the production sruth/oideachais/tuatha BAML extractions produce richer
   output than the hackathon versions).
2. The hand-rolled `BAML_HACKATHON_CHAINED` client bypasses the BAML
   compiler, losing schema validation, retries, and observability.
3. The cross-quadrant code agents (in `sruth/oideachais/agents/`,
   `sruth/tuatha/agents/`) cannot call these functions without importing
   from `spaces/_common/`.

This change promotes the 4 BAML functions to their canonical
locations and replaces the OLD client with the canonical `LitellmClient`:

| Function | New canonical location |
|:--|:--|
| `ExtractCircularMeta` | `sruth/oideachais/baml_src/circular_extraction.baml` (new file) |
| `CompareCelticNations` | `sruth/tuatha/baml_src/celtic_curriculum.baml` (append) |
| `GenerateExitCardQuestions` | `sruth/tuatha/baml_src/player_assessment.baml` (append) |
| `GenerateNpcDialogue` | `sruth/tuatha/baml_src/mythology_extraction.baml` (append) |

The `BAML_HACKATHON_CHAINED` client is removed from
`spaces/_common/baml/`. The 4 Spaces will switch to the canonical
`LitellmClient` in a follow-up change (A2: replace hand-rolled
baml_client.py with real BAML).

## What changes

- New file `sruth/oideachais/baml_src/circular_extraction.baml` (the
  CircularReference + TopicDistribution + MarkingSchemeSummary +
  CircularExtraction classes + ExtractCircularMeta function)
- 3 existing tuatha BAML files extended with the new functions
  (`CompareCelticNations`, `GenerateExitCardQuestions`,
  `GenerateNpcDialogue`) and their supporting classes
- `spaces/_common/baml/` directory deleted (the
  `hackathon_schemas.baml` file is the only file in it)
- 2 spec deltas (1 ADDED on oideachais-baml-schemas for the
  new circular_extraction.baml + 3 MODIFIED on tuatha-platform
  for the 3 new tuatha functions)

## Out of scope

- A2: replace hand-rolled baml_client.py with real BAML (next
  change)
- Per-Space modernization (C1-C4) — separate changes
- Regenerating the baml_client/ from the new BAML files — done
  by A2
