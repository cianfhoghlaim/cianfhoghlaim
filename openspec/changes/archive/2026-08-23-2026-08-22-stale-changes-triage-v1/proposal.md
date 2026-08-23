# 2026-08-22-stale-changes-triage-v1

## Why

The 2026-08-22-openspec-audit-and-merge-v1 audit identified **34 stale pending changes** that have been at `0/N tasks` for 1-14 days. This change documents the per-change triage decision for each (KEEP / CLOSE / SPLIT / TRIAGE), provides the rationale, and outlines a phased execution plan.

## Why now

- **34 stale changes** is a maintenance burden — every new change has to be checked against this backlog
- **Some changes may be superseded** by other archived changes (need to verify)
- **Some changes are oversized** (148-task web-monorepo consolidation, 123/107/93-task marimo v14 changes) — they should be split
- **Some are future-dated** (2026-09, 2026-10, 2026-12) — the dates suggest deliberate deferral; they may be aspirational rather than actionable

## Scope

This change does NOT modify any code or any other openspec change. It's a **planning document** that lives in the openspec system as a reference for future triage.

## Per-change triage (34 decisions)

### Group A: KEEP (12 changes) — real work, in-flight

| Change | Tasks | Days stale | Why KEEP |
|:--|--:|--:|:--|
| `2026-08-22-lakehouse-config-and-env-var-hardening-v1` | 33 | 2d | P0 hardening (referenced by PR #4 + #5) |
| `2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1` | 22 | 1d | P0 hardening (Lance sidecar) |
| `2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1` | 27 | 1d | P0 hardening (stack-doctor) |
| `2026-08-21-fix-wired-but-unloaded-mcps-v1` | 24 | 1d | Real bug — 2 MCPs broken at runtime |
| `2026-08-21-flip-observability-mcps-v1` | 17 | 1d | Real gap — 5 observability MCPs disabled |
| `2026-08-21-bring-up-knowledge-and-design-mcps-v1` | 23 | 1d | Real gap — cognee + graphiti MCPs |
| `2026-08-21-document-phantom-mcp-gateway-gap-v1` | 11 | 1d | Real gap — phantom /mcp/{server} route |
| `2026-08-21-archive-legacy-sruth-mcp-servers-v1` | 10 | 1d | Real cleanup — 6 legacy MCP servers |
| `2026-08-13-edge-routing-and-offline-site-remediation-v1` | 14 | 10d | Real gap — edge routing for arm1-oci |
| `2026-08-13-biep-v3-orchestration-activation-v1` | 17 | 10d | Real gap — BIEP v3 Dagster activation |
| `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1` | 10 | 10d | Real gap — per-jurisdiction sensors |
| `2026-08-13-knowledge-graph-population-activation-v1` | 16 | 10d | Real gap — Cognee cross-archive population |

### Group B: CLOSE (4 changes) — superseded by other changes

| Change | Tasks | Days stale | Superseded by |
|:--|--:|--:|:--|
| `2026-08-21-unsloth-v5-architecture-refinement-v1` | 12 | 11h | `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (archived) |
| `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` | 39 | 1d | `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP, covers most of this) |
| `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` | 31 | 9d | Already done implicitly by the linter (no count drift in current state) |
| `2026-08-10-england-biiep-pipeline-v1` | 17 | 3h | Superseded by BIEP v3 (canonical) + the England ChangeDetection sensor (KEEP) |

### Group C: SPLIT (7 changes) — oversized, needs split

| Change | Tasks | Days stale | Proposed split |
|:--|--:|--:|:--|
| `2026-08-13-web-monorepo-consolidation-and-agent-integration-v1` | **148** | 3h | Split into 5 sub-changes: (1) tanstack-start surface, (2) copilotkit surface, (3) convex schema, (4) hono API, (5) agent integration |
| `2026-08-13-skill-consolidation-and-extension-v1` | **45** | 9d | Split into 3: (1) canonical skill template, (2) per-area skill merges, (3) SKILL.md validation |
| `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1` | **46** | 9d | Split into 2: (1) guides.yml repair, (2) INTEGRATIONS_INDEX.md |
| `2026-08-10-marimo-v14-cascading-effects-verification-v1` | **123** | 14d | Split into 4: per-marimo-notebook-area verifications |
| `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1` | **107** | 14d | Split into 3: per-tier consolidations |
| `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` | **93** | 14d | Split into 2: Ireland + England |
| `2026-08-10-baml-extraction-completion-v1` | 22 | 10d | Split into 2: (1) factory pattern, (2) per-subject real prompts |

### Group D: TRIAGE (11 changes) — needs per-change review

| Change | Tasks | Days stale | Why TRIAGE |
|:--|--:|--:|:--|
| `2026-08-23-tuatha-media-intel-gameplay-capture-research-v1` | 20 | 14m | Tuatha-specific; needs subject-matter review |
| `2026-08-13-ocr-vision-activation-completion-v1` | 15 | 10d | OCR vision — likely related to `meaisinfoghlaim-ocr-htr` spec |
| `2026-08-13-bonneagar-infra-remediation-v3` | 18 | 10d | Bonneagar infrastructure — needs IaC review |
| `2026-08-10-knowledge-graph-population-v1` | 16 | 13d | KGraph — may relate to indexing-and-cognition spec |
| `2026-08-10-copilotkit-action-wiring-v1` | 16 | 14d | CopilotKit — needs frontend review |
| `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1` | 36 | 14d | Marimo — needs sub-splitting similar to other marimo v14 changes |
| `2026-09-22-geospatial-british-isles-twin-v1` | 26 | 3h | Future-dated — keep deferred |
| `2026-09-08-ogham-celtic-stones-pipeline-v1` | 28 | 3h | Future-dated — keep deferred |
| `2026-09-15-celtic-language-corpus-extension-v1` | 30 | 3h | Future-dated — keep deferred |
| `2026-09-01-celtic-mythology-content-system-v1` | 40 | 3h | Future-dated — keep deferred |
| `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` | 21 | 14d | Future-dated — keep deferred |
| `2026-09-29-familiar-dynamic-nft-system-v1` | 24 | 14d | Future-dated — keep deferred |

(The future-dated entries (2026-09, 2026-10) are counted as "TRIAGE" but functionally should stay deferred until the planned date.)

## Phased execution plan

### Phase 1: CLOSE the 4 superseded changes (next session)
- Archive `2026-08-21-unsloth-v5-architecture-refinement-v1` (superseded)
- Archive `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` (superseded)
- Archive `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` (done)
- Archive `2026-08-10-england-biiep-pipeline-v1` (superseded)

### Phase 2: SPLIT the 7 oversized changes (per-change effort, 4-6 hrs)
For each:
1. Read the current change's tasks.md
2. Identify natural split boundaries (e.g. by area: per-subject, per-stack, per-spec)
3. Create N smaller changes that each cover a coherent scope
4. Move the relevant tasks from the original change to each new change
5. Archive the original change as a coordination change

### Phase 3: TRIAGE the 11 needs-review changes (per-change effort)
For each:
1. Read the change's proposal.md
2. Determine if it should be: (a) KEEP (real work), (b) CLOSE (no longer relevant), (c) MERGE into another change
3. Apply the decision

### Phase 4: Future-dated changes
The 6 future-dated changes (2026-09, 2026-10) should be left as-is until the planned dates.

## What changes (this openspec change)

This change does NOT modify any canonical spec. It only documents the triage decisions for the 34 stale changes. The decisions are reversible (a KEEP can become a CLOSE later if new information surfaces).

## Dependencies

`Blocked by: none` (the audit was the only prerequisite — already archived)
`Blocked by (soft): 2026-08-22-openspec-audit-and-merge-v1` (this change implements finding 6 of the audit)
`Affected repos: cianfhoghlaim`

## Cross-references

- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — finding 6 of the audit
- `openspec/changes/2026-08-22-retire-pre-v7-oideachais-stubs-v1/` — Phase E1
- `openspec/changes/2026-08-22-archive-biep-v1-v2-retirement-v1/` — Phase E2
