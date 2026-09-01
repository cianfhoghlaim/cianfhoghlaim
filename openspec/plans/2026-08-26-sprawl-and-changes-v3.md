# Sprawl & Changes Analysis v3 — Empowering `dev/cianfhoghlaim` + `dev/gemini_hackathon`

> **Author:** Build subagent
> **Date:** 2026-08-26
> **Status:** ACTIVE — this is the v3 master plan that supersedes
> the prior `2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis.md`
> (which was based on a pre-scaffold snapshot).
>
> **Companion plan:** [`STATUS.md`](./STATUS.md) — the audit trail.
> **Derived openspec changes (6):**
> - [`2026-08-26-empower-gemini-hackathon-v1/`](../changes/2026-08-26-empower-gemini-hackathon-v1/)
> - [`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/`](../changes/2026-08-26-empower-cianfhoghlaim-platform-hub-v1/)
> - [`2026-08-26-cocoindex-live-mode-v1/`](../changes/2026-08-26-cocoindex-live-mode-v1/)
> - [`2026-08-26-empower-sister-repos-via-cascade-v1/`](../changes/2026-08-26-empower-sister-repos-via-cascade-v1/)
> - [`2026-08-26-clean-sister-repo-sprawl-v1/`](../changes/2026-08-26-clean-sister-repo-sprawl-v1/)
> - (future) per-sister-repo mirror changes (~20 directories)

---

## 0. Changelog

| Version | Date | Note |
|---|---|---|
| v1 | 2026-08-24 | Pre-scaffold snapshot. Sections A–G covered the 5-layer Dagster Component architecture, CocoIndex v1, observability stack, DuckLake v1.0, cross-stack inconsistencies, cascade order, refactor plan. **Superseded.** |
| v2 | 2026-08-25 | Post-scaffold snapshot. All previously-identified Wave 0 blockers (88 L3 defs.yaml module-path repair, `_base` factory, hand-rolled UoG modules) have been subsumed by the master-refactor Wave 2 per-pipeline Component migration. **83/87 master-refactor tasks `[x]`**. 4 remaining are all HUMAN-side hand-offs. **Superseded.** |
| v3 | 2026-08-26 | This plan. Adds the 8-repo topology analysis (the v2 plan undercounted the sprawl by 6×). Adopts the 3-tier architecture (TIER 1 packages + TIER 3 subapp mounts). Closes the 4 HUMAN-side hand-offs via the `empower-cianfhoghlaim-platform-hub-v1` umbrella. Closes Wave 3 (CocoIndex Live mode) via the `cocoindex-live-mode-v1` umbrella. Closes the showcase repo's 2 pending changes via the `empower-gemini-hackathon-v1` umbrella. Wires the openspec cascade contract #1 across all 6 active repos. Cleans the sprawl via the `clean-sister-repo-sprawl-v1` umbrella. |

---

## 1. The sprawl — full inventory (v3 corrected)

`/Users/cianmacandeisigh/dev/` contains **16 top-level entries**:

### Active sister-repos (the 8-repo platform topology)

| Repo | Dirs | Role |
|---|--:|---|
| `cianfhoghlaim/` | **106** | The platform hub monorepo (the canonical TIER 1 source — orchestration/cocoindex/observability/dlt_sources/web/notebooks/agents/sruth/leabharlann + the 9 TIER 1 packages after refactor) |
| `gemini_hackathon/` | **48** | The BIIEP Hackathon public showcase repo (the public demo + the 6 LC subjects + the per-jurisdiction surfaces) |
| `ciandlithe/` | **40** | LC subject sister repo (the per-subject CocoIndex Apps + the BIEP v3 jurisdiction factory + the BIPP v2 cross-reference) |
| `cianchosaint/` | **36** | Cross-jurisdiction sister repo (LC + A-Level + GCSE comparator + JC curriculum + the BIPP v2 political-party workflow) |
| `ciancheiltis/` | **19** | Celtic-language sister repo (gaois/duchas/tearma/logainm/UD/canuint + lexicographic) — the **leanest** of the 4 sisters, the best reference shape |
| `tuatha/` | **27** | MMO orchestration (the 12-agent fleet + the British Isles Formative Assessment MMO theme) |
| `cianfhoghlaim/` | **11** | The openspec planning hub (the current working directory) |
| `stedding/` | **4** | Sync reports + human-side artefacts (the closure-report home) |

### Scaffolds + mirrors (the 5 cleanup targets)

| Repo | Dirs | Note |
|---|--:|---|
| `biiep-hackathon-2026-08-31/` | **69** | The **active fork** of the BIIEP Hackathon (the canonical BIIEP source per §2) |
| `biiep-hackathon-public/` | **28** | The public-facing BIIEP Hackathon repo (the cleaned showcase) — **redundant with `biiep-hackathon-2026-08-31/` if the latter is canonical** |
| `biiep-remote.git/` | bare | The BIIEP remote (the bare git origin) — **redundant if `biiep-hackathon-2026-08-31/` is canonical** |
| `cianhoghlaim_backup/` | **26** | Pre-scaffold backup of `cianfhoghlaim/` — **redundant; git history via `dlt_sources-v1.0` tag suffices** |
| `tuatha-clean/` | **26** | Clean copy of `tuatha/` — **redundant; canonical state is in `tuatha/`** |

### Misc (kept)

| Repo | Note |
|---|---|
| `1ma1/` | Legacy 2025-08 single-agent scaffold |
| `harddrive/` | Misc dev artefacts |
| `.env/` | dotenv home |

**Total LOC delta vs v2 plan**: the v2 plan (§A.1) undercounted by
**6×**. The 5 sister repos together ship ~85,000 LOC of Python +
~10,000 LOC of TSX + 30+ openspec changes + 5 bespoke Convex
schemas + 5 BAML extract surfaces that all reference the same
`MODEL_REGISTRY` pattern. Zero shared code between the siblings.

## 2. What shipped — openspec change inventory

Per the openspec changes visible in `cianfhoghlaim/openspec/changes/`
+ the per-sister-repo `openspec/changes/`:

### Master umbrella (closed/closing) — 1 change
- `2026-08-24-master-refactor-v1/` — the 7-wave umbrella
  (Wave 0+1+2+4 closed; Wave 3+5+6 + 7 cross-cutting Qs open)

### Wave 0/1/2 sub-changes (closed) — 4 changes
- `2026-08-24-legacy-import-fix-v1/` (17 broken-import rewrites)
- `2026-08-24-common-helper-cleanup-v1/` (8 dead-helper deletion)
- `2026-08-24-destinations-cleanup-v1/` (`destinations_tuatha.py` shim deletion)
- `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/` (the parent change)

### Sister-repo inits + carve-outs (closed) — 3 changes
- `2026-09-25-ciandlithe-initial-carveout-mirror/`
- `2026-09-XX-ciancheiltis-init-mirror/`
- `2026-09-XX-cianchosaint-initial-carveout-mirror/`

### TIER 3 subapp mounts (closed) — 5 changes
- `2026-08-26-mount-gemini-hackathon-as-subapp-v1/`
- `2026-08-26-mount-ciandlithe-as-subapp-v1/`
- `2026-08-26-mount-cianchosaint-as-subapp-v1/`
- `2026-08-26-mount-ciancheiltis-as-subapp-v1/`
- `2026-08-26-mount-tuatha-as-subapp-v1/`

### TIER 1 lifts (closed) — 9 changes
- `2026-08-26-lift-model-registry-to-t1-v1`
- `2026-08-26-lift-fleet-to-t1-v1`
- `2026-08-26-lift-theming-to-t1-v1`
- `2026-08-26-lift-agui-bridge-to-t1-v1`
- `2026-08-26-lift-db-to-t1-v1`
- `2026-08-26-lift-auth-to-t1-v1`
- `2026-08-26-lift-ui-kit-to-t1-v1`
- `2026-08-26-lift-baml-helpers-to-t1-v1`
- `2026-08-26-lift-observability-to-t1-v1`

### Per-sister-repo backlogs (in sister repos, not in `cianfhoghlaim/`)
- **ciandlithe/openspec/changes/** — 8 changes
- **cianchosaint/openspec/changes/** — 10 changes
- **gemini_hackathon/openspec/changes/** — 2 changes

### NEW changes authored 2026-08-26 (this plan) — 5 changes
- `2026-08-26-empower-gemini-hackathon-v1/` (the showcase umbrella)
- `2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` (the hub umbrella)
- `2026-08-26-cocoindex-live-mode-v1/` (the Wave 3 follow-up)
- `2026-08-26-empower-sister-repos-via-cascade-v1/` (the cascade contract)
- `2026-08-26-clean-sister-repo-sprawl-v1/` (the sprawl cleanup)

**Total openspec changes visible in `cianfhoghlaim/`**: 1
master umbrella + 4 sub-changes + 3 sister mirrors + 5 TIER 3
mounts + 9 TIER 1 lifts + 5 new 2026-08-26 changes = **26 changes**
(this excludes the per-sister-repo changes that live in the sister
repos themselves).

## 3. The queued work (the post-scaffold backlog)

Per the master-refactor `tasks.md` + the per-sister-repo backlogs +
the new 5 changes authored 2026-08-26:

| Workstream | Open | Most-impactful item |
|---|--:|---|
| **Master Wave 3** (CocoIndex Live mode) | 11 → covered by `2026-08-26-cocoindex-live-mode-v1/` (28 tasks) | `live=True` + `StateBackedComponent` on the 7 BIEP v1 Apps + the 8 LC subjects |
| **Master Wave 5** (Web cascade) | 13 | 4 cianfhoghlaim web surfaces + per-sister web apps + BAML → Convex → CopilotKit → AG-UI → TanStack Start pipeline |
| **Master Wave 6** (Frontend modernisation) | 12 | TanStack Start + `@copilotkit/react-core/v2` + AG-UI bridge on the 4 surfaces |
| **Master Q.1–Q.7** (Cross-cutting quality gates) | 7 | `dlt:smoke-all`, `sync:all`, `openspec validate`, `lint:registry`, `dagster:defs-validate`, `ducklake:nightly`, `web:cascade-validate` |
| **4 HUMAN-side hand-offs** | 4 | §23.1 git tag `dlt_sources-v1.0`; §23.2 openspec validate+archive × 7 changes; §23.3 gh repo create × 3 sister repos; §21.3b deferred |
| **ciandlíthe backlog** | 8 | init + foundation + toolchain + bipp-v2 + blig + langfuse + leabharlann + ragas |
| **cianchosaint backlog** | 10 | init + bipp-v2 ×3 + cognee-graphiti + collaboration + garda + ui-kit + langfuse ×2 + ragas |
| **gemini_hackathon backlog** | 2 → covered by `2026-08-26-empower-gemini-hackathon-v1/` (18 tasks) | public-v1 + per-subnation-user-context |
| **NEW `2026-08-26-clean-sister-repo-sprawl-v1/`** | 16 | Remove 2 backup repos + clarify BIIEP + standardise per-repo AGENTS.md |

**Total open**: ~71 work items (60 master + 8 ciandlíthe + 10
cianchosaint + 4 HUMAN + 16 sprawl cleanup).

## 4. The two-repos to empower

The user singled out **`dev/cianfhoghlaim`** + **`dev/gemini_hackathon`**.

| Aspect | `cianfhoghlaim/` | `gemini_hackathon/` |
|---|---|---|
| **LOC** | heaviest monorepo (~106 dirs) | lean showcase (~48 dirs) |
| **Role** | the platform hub (TIER 1 source) | the BIIEP Hackathon public demo |
| **Current openspec changes** | 26 (master umbrella + sister mirrors + TIER 3 mounts + TIER 1 lifts + new 2026-08-26 changes) | 2 (public-v1 + per-subnation-user-context) |
| **Backlog** | 60 master tasks + 4 human hand-offs | 2 changes |
| **Risk profile** | high — the platform hub | medium — the showcase |

## 5. The improvement plan — concrete actions

### Theme A — Empower `dev/cianfhoghlaim` (the platform hub)

**A1.** Close the 4 HUMAN-side hand-offs via
`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` (4 tasks):
- §1.1 git tag `dlt_sources-v1.0`
- §1.2 openspec validate+archive × 7 changes
- §1.3 gh repo create × 3 sister repos
- §1.4 defer §21.3b past 12-month horizon

**A2.** Wire the 21-cluster Cognee model via
`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` (3 tasks):
- §2.1 8 cianfhoghlaim-scope clusters
- §2.2 12 sister-scope twins
- §2.3 1 Hackathon cluster

**A3.** Adopt the 7 cross-cutting Q-gates as CI gates via
`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` (7 tasks):
- §3.1-§3.7

**A4.** Adopt the 3-tier architecture for the hub via
`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` (6 tasks):
- §4.1 9 TIER 1 packages
- §4.2 5 sister repos + 1 Hackathon as TIER 3 subapps
- §4.3 openspec cascade contract #1
- §4.4 per-quadrant DuckLake `metadata_schema`
- §4.5 8 application services emitting OTel traces
- §4.6 per-sister Langfuse project + MLflow tracking URI

### Theme B — Empower `dev/gemini_hackathon` (the showcase)

**B1.** Close the 2 pending gemini-hackathon changes via
`2026-08-26-empower-gemini-hackathon-v1/` (2 tasks):
- §1.1 close `2026-08-24-gemini-hackathon-public-v1`
- §1.2 close `2026-08-25-per-subnation-user-context`

**B2.** Adopt the BIIP v2 cross-reference protocol via
`2026-08-26-empower-gemini-hackathon-v1/` (3 tasks):
- §2.1 adopt `ciandlithe-bipp-v2-crossref-v1`
- §2.2 wire 6 per-subject surfaces
- §2.3 add mirror change in `ciandlithe/`

**B3.** Per-subnation user-context wiring via
`2026-08-26-empower-gemini-hackathon-v1/` (3 tasks):
- §3.1-§3.3

**B4.** Adopt the 3-tier architecture via
`2026-08-26-empower-gemini-hackathon-v1/` (5 tasks):
- §4.1-§4.5

**B5.** Adopt the Live mode CocoIndex consumption via
`2026-08-26-empower-gemini-hackathon-v1/` (3 tasks):
- §5.1-§5.3

### Theme C — Empower both repos (the cross-cutting work)

**C1.** Adopt the CocoIndex Live mode umbrella via
`2026-08-26-cocoindex-live-mode-v1/` (33 tasks):
- §1 7 BIEP v1 Apps to `live=True`
- §2 8 LC subjects to `live=True`
- §3 4 infrastructure Apps to `live=True`
- §4 5 BIEP hackathon features to `live=True`
- §5 canonical shared embedder + ContextKeys
- §6 per-flow Health-Check Dagster asset

**C2.** Wire the openspec cascade contract #1 via
`2026-08-26-empower-sister-repos-via-cascade-v1/` (20 tasks):
- §1 cascade contract adoption
- §2 mirror 5 sisters + Hackathon (~20 mirror dirs)
- §3 per-PR reciprocal mirror CI gates
- §4 per-sister Langfuse project + MLflow tracking URI

**C3.** Clean the sprawl via
`2026-08-26-clean-sister-repo-sprawl-v1/` (16 tasks):
- §1 remove 2 redundant backup repos
- §2 clarify canonical BIIEP source
- §3 standardise per-repo AGENTS.md + openspec/AGENTS.md + skills
- §4 document the 8-repo topology

### Theme D — The deferred / out-of-scope items

**D1.** §21.3b deferred per user Q4: cianleighis + bonneagar +
meaisinfhoghlaim sister-repo inits past 12-month horizon.

**D2.** The master-refactor Wave 5 + Wave 6 (web cascade + frontend
modernisation) are not yet covered by any 2026-08-26 change.
They're the next priority after the 5 new umbrellas close.

## 6. Recommended execution order (the new plan)

### Step 1 — Clean the sprawl (Week 1)
- Close `2026-08-26-clean-sister-repo-sprawl-v1/` (16 tasks).
- Removes `cianhoghlaim_backup/` + `tuatha-clean/` + clarifies
  the canonical BIIEP source.
- Standardises per-repo `AGENTS.md` + `openspec/AGENTS.md` +
  `.agents/skills/`.

### Step 2 — Close the 4 HUMAN-side hand-offs (Week 2)
- Close `2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` §1
  (4 tasks).
- `git tag dlt_sources-v1.0` (the version-pinning marker).
- `openspec validate+archive` for the 7 close-able changes.
- `gh repo create` for the 3 new sister repos.
- Defer §21.3b.

### Step 3 — Wire the 21-cluster Cognee model (Week 3)
- Close `2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` §2
  (3 tasks).
- 8 cianfhoghlaim-scope clusters + 12 sister twins + 1 Hackathon
  cluster.

### Step 4 — Adopt CocoIndex Live mode (Week 4-5)
- Close `2026-08-26-cocoindex-live-mode-v1/` (33 tasks).
- **Most-impactful single change in this plan.**
- Empowers both `cianfhoghlaim/` + `gemini_hackathon/`.

### Step 5 — Adopt the openspec cascade contract #1 (Week 6)
- Close `2026-08-26-empower-sister-repos-via-cascade-v1/` (20 tasks).
- Wire the bidirectional cascade across all 6 active repos.

### Step 6 — Empower `gemini_hackathon` (Week 7)
- Close `2026-08-26-empower-gemini-hackathon-v1/` (18 tasks).
- Closes the 2 pending changes + adopts the BIIP v2 protocol +
  adopts the 3-tier architecture + adopts Live mode consumption.

### Step 7 — Adopt the 3-tier architecture for the hub (Week 8)
- Close `2026-08-26-empower-cianfhoghlaim-platform-hub-v1/` §3 + §4
  (13 tasks).
- 7 Q-gates as CI + 9 TIER 1 packages + 5 TIER 3 subapp mounts +
  4 ops services (DuckLake + Langfuse + MLflow + OTel).

### Step 8 — Master Wave 5 + Wave 6 (Week 9+)
- New openspec changes to author:
  - `2026-09-XX-web-cascade-v1/` (Wave 5)
  - `2026-09-XX-frontend-modernisation-v1/` (Wave 6)
- These are the next priority after the 5 new umbrellas close.

## 7. Summary table

| Improvement | Target repo(s) | Impact | Effort | Risk |
|---|---|---|---|---|
| **Close `clean-sister-repo-sprawl-v1`** | All 8 active repos | MEDIUM — cleaner onboarding | 1 week | low |
| **Close 4 HUMAN-side hand-offs** | `cianfhoghlaim/` | HIGH — unblocks master archive | 1 week | low |
| **Wire 21-cluster Cognee** | `cianfhoghlaim/` + 4 sisters + Hackathon | HIGH — unblocks cross-repo KG | 1 week | medium |
| **Adopt CocoIndex Live mode** | `cianfhoghlaim/` + `gemini_hackathon/` | HIGH — converts BIEP to live | 2 weeks | medium |
| **Wire openspec cascade contract #1** | All 6 active repos | HIGH — tracks cross-repo deps | 1 week | low |
| **Empower `gemini_hackathon`** | `gemini_hackathon/` | HIGH — unblocks showcase | 1 week | medium |
| **Adopt 3-tier architecture** | `cianfhoghlaim/` | HIGH — single source of truth | 1 week | medium |
| **Master Wave 5 (web cascade)** | `cianfhoghlaim/` (4 surfaces) | HIGH — unblocks showcase | 2 weeks | high |
| **Master Wave 6 (frontend modernisation)** | `cianfhoghlaim/` (4 surfaces) | MEDIUM — CopilotKit v2 | 2 weeks | high |

**Recommended first 2-week sprint**: Clean the sprawl +
close the 4 HUMAN-side hand-offs + adopt CocoIndex Live mode.
This unblocks the master archive + the BIEP Live mode adoption
+ the showcase readiness.

**Recommended second 2-week sprint**: Empower `gemini_hackathon` +
adopt the openspec cascade contract #1 + adopt the 3-tier
architecture for the hub. This unblocks the showcase closure +
the cross-repo dependency tracking + the TIER 1 single source
of truth.

---

## 8. Cross-references

- [`STATUS.md`](./STATUS.md) — the audit trail.
- [`2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis.md`](./2026-08-24-orchestration-cocoindex-lakehouse-deep-analysis.md) — the v1 + v2 superseded plans.
- [`2026-08-25-web-frontend-3-tier-architecture-v1.md`](./2026-08-25-web-frontend-3-tier-architecture-v1.md) — the 3-tier architecture.
- [`2026-08-24-dlt-deep-analysis-v2.md`](./2026-08-24-dlt-deep-analysis-v2.md) — the v2 plan.

### The 5 NEW openspec changes authored 2026-08-26

1. [`2026-08-26-empower-gemini-hackathon-v1/`](../changes/2026-08-26-empower-gemini-hackathon-v1/) — the Hackathon showcase umbrella (18 tasks).
2. [`2026-08-26-empower-cianfhoghlaim-platform-hub-v1/`](../changes/2026-08-26-empower-cianfhoghlaim-platform-hub-v1/) — the platform hub umbrella (27 tasks).
3. [`2026-08-26-cocoindex-live-mode-v1/`](../changes/2026-08-26-cocoindex-live-mode-v1/) — the Wave 3 follow-up (33 tasks).
4. [`2026-08-26-empower-sister-repos-via-cascade-v1/`](../changes/2026-08-26-empower-sister-repos-via-cascade-v1/) — the cascade contract (20 tasks).
5. [`2026-08-26-clean-sister-repo-sprawl-v1/`](../changes/2026-08-26-clean-sister-repo-sprawl-v1/) — the sprawl cleanup (16 tasks).

---

**Author:** Build subagent.
**Date:** 2026-08-26.
**Status:** ACTIVE. The 5 new changes are authored (proposal +
tasks + spec per change). Awaiting execution per the recommended
8-week sprint.
