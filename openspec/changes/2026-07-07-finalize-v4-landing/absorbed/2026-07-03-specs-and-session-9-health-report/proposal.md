# Change: 2026-07-03-specs-and-session-9-health-report

## Why

After Changes A (infrastructure-foundation), B (LC5-subject pipeline
+ 16 notebooks), and C (Gemini 6-corpus pipeline + 9 notebooks), the
canonical Cianfhoghlaim specs need to be updated to reflect the v4
state. In particular:

- `meaisinfhoghlaim-ocr-htr` references the legacy 10-model/6-backend
  schema; needs to be rewritten to the v4 24-model/4-backend schema.
- `meaisinfhoghlaim-platform` doesn't declare the 12 new Python
  packages from Change A or the 25 new dev notebooks from Changes B+C.
- `agent-memory-systems` doesn't list the LC5 + Gemini consumers.
- `oideachais-pipeline` doesn't list the new LC5 + Gemini pipelines.
- `HEALTH_REPORT.md` Session 7 is the latest entry; Session 9 (this
  one) needs to be prepended for the 4 changes above.

## What changes

### 1 — 4 spec updates (4 files)

| File | Update |
|:--|:--|
| `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` | **REWRITE** — full content from 190 lines (legacy 10-model) to v4 24-model/4-backend schema; reference the v4 registry; document the 13 llama-swap GGUF entries; document the 6 TRANSFORMERS-backend inline models; cross-reference Change B (LC5) + Change C (Gemini) |
| `openspec/specs/meaisinfhoghlaim-platform/spec.md` | **APPEND** an `## ADDED Requirements (v4 extension — 2026-07-03)` section with 3 Requirements: 12 Python packages, `ocr-vision-full` extra, 25 dev marimo notebooks |
| `openspec/specs/agent-memory-systems/spec.md` | **APPEND** an `## ADDED Requirements (v4 extension — 2026-07-03)` section with 1 Requirement: LC5 + Gemini as Cognee + Graphiti + FalkorDB consumers (11 datasets + 11 streams + 2 falkordb labels) |
| `openspec/specs/oideachais-pipeline/spec.md` | **APPEND** an `## ADDED Requirements (v4 extension — 2026-07-03)` section with 1 Requirement: LC5 (72 rows) + Gemini (224 rows) pipelines sharing the v4 OCR/VLM registry |

### 2 — HEALTH_REPORT prepended (1 file)

| File | Update |
|:--|:--|
| `bonneagar/stacks/HEALTH_REPORT.md` | **PREPEND** Session 9 entry documenting the 4 changes above + 12-row smoke test table + 3 new known issues (dagster-local rebuild, GGUF cache population, pipeline DAGs materialisation) + cross-references to the 4 openspec change folders |

### 3 — Openspec change files (3 files)

| File | Action |
|:--|:--|
| `openspec/changes/2026-07-03-specs-and-session-9-health-report/proposal.md` | **CREATE** (this file) |
| `openspec/changes/2026-07-03-specs-and-session-9-health-report/tasks.md` | **CREATE** (4 phases: spec edits → HEALTH_REPORT → openspec files → commit) |
| `openspec/changes/2026-07-03-specs-and-session-9-health-report/specs/{meaisinfhoghlaim-ocr-htr,meaisinfhoghlaim-platform,agent-memory-systems,oideachais-pipeline}/spec.md` | **CREATE** × 4 (each with `## ADDED Requirements` + Scenarios) |

## Impact

- **Affected specs:** `meaisinfhoghlaim-ocr-htr`, `meaisinfhoghlaim-platform`, `agent-memory-systems`, `oideachais-pipeline`
- **Affected code:** 4 spec files + 1 HEALTH_REPORT file + 7 openspec change files
- **Affected hosts:** none (all docs + spec updates)
- **Risk:** very low — spec content only; no runtime behavior changes
- **Audit gates:** `openspec validate --strict` × 4 + `bun run validate-stacks` + `mise run lint:skills`

## Non-goals

- **No runtime changes** — this is documentation/spec work only.
- **No new containers** — existing 27 containers from Sessions 6+7 are unchanged.
- **No dagster-local image rebuild** — the new Python packages from Change A are picked up on next `docker build`.

## Cross-references

- Per openspec/changes/2026-07-03-infrastructure-foundation/
- Per openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/
- Per openspec/changes/2026-07-03-gemini-6-corpus-pipeline/
- Per the v4 OCR/VLM registry at `cianfhoghlaim/meaisinfhoghlaim/models/registry.py`.
