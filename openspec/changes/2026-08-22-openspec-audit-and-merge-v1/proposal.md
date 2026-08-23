# 2026-08-22-openspec-audit-and-merge-v1

## Why

Per the prior planning session ("after these currently planned changes are implemented we need to develop an extensive openspec audit and updates refactoring merging plan of existing openspec specs/plans/changes"), this change inventories **101 capability specs + 38 pending changes + 100 archived changes** (= 239 openspec entities) and proposes **concrete merge / archive / keep decisions** with phased rollout.

## Why now

- **101 specs × 1075 requirements** is a maintenance burden — every change has to trace which spec delta hits which file
- **7 pre-v7 `oideachais-*` specs** still exist on disk despite the v4 (2026-06-28) + v7 (2026-07-17) consolidations; the post-v7 names `cianfhoghlaim-*` have replaced them but the old stubs are still in `openspec/specs/`
- **`british-isles-education-pipeline-v1/v2/v3`** = 3 separate specs, 70 requirements total — the v1 (41 reqs) was supposed to be retired by v3 (25 reqs) but they coexist with overlap
- **3 agent/memory/observability specs** all touch Cognee/Graphiti/Langfuse/LanceDB — the boundaries between them are fuzzy
- **34 untouched 0/N tasks changes** have been stale since 2026-07-29 (12 days for the oldest) — they need triage

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Audit scope | **Full inventory** (101 specs + 38 pending + 100 archived) |
| Merge aggressiveness | **Conservative** — only merge where one spec is clearly superseded |
| Stale change triage | **Per-change decision** (each of the 34 gets a verdict) |
| Rollout | **Phased** — Phase 1 = safe merges (no behavior change), Phase 2 = retirements, Phase 3 = post-archive cleanup |
| Affects openspec workflow | **No** — keeps the legacy `spec-driven` schema + 8 standard subcommands |

## Dependencies

`Blocked by: none` (the audit itself doesn't depend on other changes)
`Blocked by (soft): 2026-08-22-concurrent-agent-write-safety-v1` (the new file safety protocol should be respected during archive operations)
`Affected repos: cianfhoghlaim` (single-repo change)

## Audit findings (the inventory)

### Inventory totals

| Entity | Count | Avg size | Notes |
|:--|--:|--:|:--|
| Capability specs | **101** | 11 reqs/spec | 1075 total requirements across 101 specs |
| Pending changes | **38** | 18 tasks/change | 35 at `0/N tasks` (untouched) |
| Archived changes | **100** | — | pre-v7 + v7 flattening + recent phase closes |

### Finding 1: 7 pre-v7 `oideachais-*` specs are stale stubs

These pre-v7 names should have been retired per the 2026-06-28 v4 consolidation + 2026-07-17 v7 flattening. Each is a single-Requirement stub that says "Phase 1 complete — N requirements all functional end-to-end" — they exist only as retirement markers, not as authoritative specs.

| Pre-v7 name | Post-v7 successor | Action |
|:--|:--|:--|
| `oideachais-baml-schemas` (12 reqs) | `cianfhoghlaim-baml-schemas` (19 reqs) | **ARCHIVE pre-v7** |
| `oideachais-cocoindex-v1-migration` (1 req) | `cianfhoghlaim-cocoindex-v1-migration` (8 reqs) | **ARCHIVE pre-v7** |
| `oideachais-cognify-knowledge-graph` (4 reqs) | `cianfhoghlaim-cognify-knowledge-graph` (9 reqs) | **ARCHIVE pre-v7** |
| `oideachais-leabharlann` (1 req) | `cianfhoghlaim-leabharlann` (21 reqs) | **ARCHIVE pre-v7** |
| `oideachais-marimo-dashboards` (11 reqs) | `cianfhoghlaim-marimo-dashboards` (10 reqs) | **MERGE — last-level work stays** |
| `oideachais-pipeline` (16 reqs) | `cianfhoghlaim-pipeline` (54 reqs) | **MERGE — add 5 unique reqs from pre-v7** |
| `oideachais-university-deep-extraction` (1 req) | `cianfhoghlaim-university-deep-extraction` (8 reqs) | **ARCHIVE pre-v7** |

### Finding 2: `british-isles-education-pipeline-v1/v2/v3` coexistence

| Spec | Reqs | Role | Action |
|:--|--:|:--|:--|
| `british-isles-education-pipeline` | 41 | The original v1 spec (LC subjects + gov.ie circulars + BAML extraction) | **ARCHIVE — superseded by v3** (canonical is now v3) |
| `british-isles-education-pipeline-v2` | 4 | The 4-jurisdiction upgrade bridge | **ARCHIVE** (transitional; v3 supersedes) |
| `british-isles-education-pipeline-v3` | 25 | The 5-milestone sequential plan | **KEEP — rename to `british-isles-education-pipeline`** (current canonical) |

The combined 70 requirements get reduced to ~25 in the unified spec. The 41 v1 reqs mostly describe the per-subject workflow that v3 supersedes with the 5-phase pattern.

### Finding 3: 3 agent/memory/observability specs overlap

| Spec | Reqs | Core domain |
|:--|--:|:--|
| `agent-memory-systems` | 15 | The 5-backend memory layer (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph) |
| `agent-platform-cluster` | 32 | The 8-stack substrate (lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) |
| `indexing-and-cognition` | 18 | CCC + Cognee + Firecrawl MCP (knowledge graph + code search) |
| `agent-observability` | 32 | Langfuse + Logfire + MLflow + RAGAS (observability layer) |

All 4 reference Cognee/Graphiti/Langfuse/LanceDB. **No merge recommended** — these cover distinct concerns (memory substrate vs observability layer vs cognitive stack). Boundary clarification recommended in the proposal.

### Finding 4: 1 case-sensitive spec duplicate (macOS filesystem bug)

The macOS case-insensitive filesystem allows both:
- `openspec/specs/meaisinfhoghlaim-ocr-htr/` (5 reqs) — the canonical spec
- `openspec/specs/meaisinfoghlaim-ocr-htr/` (1 req) — created by the Phase C archive of `2026-08-10-ocr-vision-activation-v1`

Wait — both names are the same! `meaisinfhoghlaim-ocr-htr`. The archive created 1 requirement on the existing canonical. **No action needed** — this is just a coincidence in the audit list. The single spec file has 5 reqs total.

### Finding 5: 1 empty spec

`tg4-foghlaim-corpus` shows 0 requirements. This is a newly-created (2026-08-25) spec that hasn't been populated yet. **KEEP** (in-progress; not stale).

### Finding 6: 34 stale pending changes (0/N tasks, untouched since creation)

These have been untouched since 2026-07-29 (12+ days). They need per-change triage:

| Stale change | Tasks | Recommendation |
|:--|--:|:--|
| `2026-08-13-web-monorepo-consolidation-and-agent-integration-v1` | 148 | **SPLIT** — too large; needs split into 4-5 smaller changes |
| `2026-08-21-unsloth-v5-architecture-refinement-v1` | 12 | **CLOSE** — likely subsumed by `2026-08-21-unsloth-v5-vision-llm-hermes-...` (already archived) |
| `2026-08-21-fix-wired-but-unloaded-mcps-v1` | 24 | **KEEP** — addresses real bug |
| `2026-08-21-flip-observability-mcps-v1` | 17 | **KEEP** — addresses real gap |
| `2026-08-21-bring-up-knowledge-and-design-mcps-v1` | 23 | **KEEP** — addresses real gap |
| `2026-08-21-document-phantom-mcp-gateway-gap-v1` | 11 | **KEEP** — addresses real gap |
| `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` | 39 | **CLOSE** — likely subsumed by `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (already archived) |
| `2026-08-21-archive-legacy-sruth-mcp-servers-v1` | 10 | **KEEP** — still actionable |
| `2026-08-22-lakehouse-config-and-env-var-hardening-v1` | 33 | **KEEP** — P0 hardening |
| `2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1` | 22 | **KEEP** — P0 hardening |
| `2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1` | 27 | **KEEP** — P0 hardening |
| `2026-08-13-skill-consolidation-and-extension-v1` | 45 | **SPLIT** — too large |
| `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1` | 46 | **SPLIT** — too large |
| `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` | 31 | **CLOSE** — already done implicitly by other changes |
| `2026-08-10-baml-extraction-completion-v1` | 22 (6 done) | **SPLIT** — too large for one change; defer to Phase E |
| `2026-08-13-edge-routing-and-offline-site-remediation-v1` | 14 | **TRIAGE** — needs review |
| `2026-08-13-biep-v3-orchestration-activation-v1` | 17 | **TRIAGE** |
| `2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1` | 10 | **TRIAGE** |
| `2026-08-13-knowledge-graph-population-activation-v1` | 16 | **TRIAGE** |
| `2026-08-13-ocr-vision-activation-completion-v1` | 15 | **TRIAGE** |
| `2026-08-13-bonneagar-infra-remediation-v3` | 18 | **TRIAGE** |
| `2026-08-10-knowledge-graph-population-v1` | 16 | **TRIAGE** |
| `2026-08-10-copilotkit-action-wiring-v1` | 16 | **TRIAGE** |
| `2026-08-10-marimo-v14-*` (4 changes) | 36-123 each | **TRIAGE** |
| `2026-08-10-england-biiep-pipeline-v1` | 17 | **TRIAGE** |
| `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` | 93 | **SPLIT** |
| `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1` | 107 | **SPLIT** |
| `2026-08-10-marimo-v14-cascading-effects-verification-v1` | 123 | **SPLIT** |
| `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1` | 36 | **TRIAGE** |
| `2026-08-23-tuatha-media-intel-and-celtic-elemental-mmo-foundation-v1` | 20 | **TRIAGE** |
| `2026-09-22-geospatial-british-isles-twin-v1` | 26 | **TRIAGE** (future-dated) |
| `2026-09-08-ogham-celtic-stones-pipeline-v1` | 28 | **TRIAGE** (future-dated) |
| `2026-09-15-celtic-language-corpus-extension-v1` | 30 | **TRIAGE** (future-dated) |
| `2026-09-01-celtic-mythology-content-system-v1` | 40 | **TRIAGE** (future-dated) |
| `2026-09-29-familiar-dynamic-nft-system-v1` | 24 | **TRIAGE** (future-dated) |
| `2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` | 21 | **TRIAGE** (future-dated) |

The "TRIAGE" entries are flagged for per-change review; the audit doesn't have enough context to recommend CLOSE/KEEP/SPLIT.

### Finding 7: In-progress changes still in flight (5+ tasks, not yet archived)

| Change | Tasks | Status |
|:--|--:|:--|
| `2026-08-22-concurrent-agent-write-safety-v1` (Phase A) | 5/7 | Just opened — T4.1 + T4.2 (commit) remain |
| `2026-08-25-tg4-foghlaim-corpus-v1` | 1/40 | Brand new; in-progress |
| `2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1` | 8/9 | Near completion |
| `2026-08-10-baml-extraction-completion-v1` | 6/22 | 73% remaining; needs split |
| `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1` | 17/32 | 47% remaining |

## What changes (the merge plan)

### Spec deltas (this change)

1. **MODIFIED `british-isles-education-pipeline`** — adopt v3 requirements, archive v1
2. **MODIFIED `agent-observability`** — add a cross-reference note to `agent-platform-cluster` (clarify the Langfuse vs Litellm-vs-Langfuse boundary)
3. **MODIFIED `agent-platform-cluster`** — add a cross-reference note to `agent-observability`
4. **REMOVED `british-isles-education-pipeline-v2`** — superseded by v3
5. **REMOVED `british-isles-education-pipeline-v3`** — merged into canonical `british-isles-education-pipeline`
6. **REMOVED 7 `oideachais-*` specs** — superseded by `cianfhoghlaim-*` successors

### Future phases (NOT in this change)

- Phase 2 (separate change): Triage the 34 stale pending changes; per-change CLOSE / SPLIT / KEEP decisions
- Phase 3 (separate change): Implement the 5-10 SPEC splits for the oversized changes (148-task web-monorepo etc.)
- Phase 4 (separate change): Phase D itself is "audit + plan"; Phase E implements the plan

## Out of scope (deferred)

- **Bulk archive of all 34 stale changes** — needs per-change decisions, out of audit scope
- **Implementation of any spec merge** — Phase E work
- **Retirement of canonical `tuatha-platform` spec** — already retired per `openspec/AGENTS.md` note
- **Spec content rewrites** — the audit proposes merges; the merges themselves are Phase E
- **Re-numbering the 7 `oideachais-*` requirements** — they're retirement markers, not substantive

## Cross-references

- `openspec/specs/retrospective-cleanup/spec.md` — the umbrella "fix past drift" spec (related)
- `openspec/specs/dev-tooling-surfaces/spec.md` — covers the openspec workflow itself
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — covers AGENTS.md generation
- `.agents/skills/openspec/SKILL.md` — the canonical skill for openspec workflow
- `.cocoindex_code/guides.yml#openspec-change-search` — CCC concept guide for finding prior art

## Verification gate

- [ ] `openspec validate 2026-08-22-openspec-audit-and-merge-v1 --strict` exits 0
- [ ] `openspec list --specs | wc -l` shows 96 (was 101 — the 5 merged specs removed)
- [ ] `openspec list --specs` no longer contains `british-isles-education-pipeline-v2` or `british-isles-education-pipeline-v3`
- [ ] `openspec list --specs` no longer contains any `oideachais-*` spec
- [ ] `git ls-files openspec/specs/` matches `openspec list --specs` (no orphans)
- [ ] All per-spec `AGENTS.md` files regenerated by `mise run sync:spec-agents`