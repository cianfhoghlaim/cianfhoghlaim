# Change: 2026-07-07-finalize-v4-landing — close the v4 refactor

## Why

The Cianfhoghlaim monorepo was consolidated from 6 `sruth/*` quadrants
into the single `cianfhoghlaim/` package on **2026-06-28** (the
`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change, archived).
Since that consolidation, **29 additional openspec changes** were
scaffolded, in some cases started, and never reached a landing state.
The accumulated post-v4 in-flight surface looked like:

- **30 in-progress changes** per `openspec list` (the 30th being
  `2026-07-06-british-isles-education-pipeline-v1`, the new flagship)
- **435 of 1,688 tasks done (26%)** across them
- **1,253 tasks** of post-v4 refactor still on the runway
- Continuous drift from "we'll land it next" → "the next change
  supersedes this one" → "let's start a new change instead"

The `2026-07-06-drift-cleanup-and-v4-alignment` change (archived) fixed
the spec + plans + skill drift that had accumulated. The current surface
is **stable enough** to land the remaining refactor. But continuing
30 parallel fragmented changes would replicate the drift pattern that
prompted this analysis.

This change closes the post-v4 refactor as **one landing artifact** by
absorbing every in-progress change except the new flagship
(`2026-07-06-british-isles-education-pipeline-v1`) into a single
consolidated change. The remaining 29 changes move to
`openspec/changes/archive/<name>/` with an `ABSORBED.md` note pointing
back here. The mega-change becomes the only place where v4-finalization
work is tracked, executed, validated, and archived.

## Scope: 29 changes absorbed

### Tier 1 — Force-finish (9 changes, ~57 remaining tasks)

These are ≥50% done. The mega-change absorbs their remaining tasks and
force-finishes them so they ship at 100%.

| # | Change | Done / Total | Action |
|--:|:--|--:|:--|
| 1 | `cianfhoghlaim-educational-mmo-v1` | 90/92 | finish last 2 |
| 2 | `cianfhoghlaim-website-rewrite` | 31/32 | finish last 1 |
| 3 | `monorepo-restructure-v2` | 19/20 | finish last 1 |
| 4 | `docs-restructuring` | 28/30 | finish last 2 |
| 5 | `2026-07-06-wire-dlthub-platform-toolkits-and-deployment` | 30/34 | finish last 4 |
| 6 | `2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks` | 28/34 | finish last 6 |
| 7 | `litellm-minimax-vendor-derisking` | 20/33 | finish last 13 |
| 8 | `croilar-portfolio` | 18/34 | finish last 16 |
| 9 | `2026-07-03-specs-and-session-9-health-report` | 8/16 | finish last 8 |

### Tier 2 — Mid-progress continuation (6 changes, ~315 remaining)

These are 10-50% done. The mega-change absorbs the entire task list and
restarts from current progress.

| # | Change | Done / Total |
|--:|:--|--:|
| 10 | `2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs` | 67/151 |
| 11 | `2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams` | 10/25 |
| 12 | `2026-07-03-infrastructure-foundation` | 14/36 |
| 13 | `2026-07-03-gemini-6-corpus-pipeline` | 8/22 |
| 14 | `ncca-leaving-cert-syllabi-corpus` | 9/36 |
| 15 | `rewrite-cianfhoghlaim-leaving-cert-v2` | 55/206 |

### Tier 3 — Zero-progress flagship work-streams (5 of 6 flagships; BIEP v1 stays separate)

The mega-change absorbs 5 of the 6 zero-progress flagships. **BIEP v1
(`2026-07-06-british-isles-education-pipeline-v1`) stays a standalone
flagship** — it's the new flagship and shouldn't be folded into an
umbrella closure.

| # | Change | Total Tasks |
|--:|:--|--:|
| 16 | `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority` | 58 |
| 17 | `2026-06-30-agent-platform-cluster-hermes-cocoindex` | 72 |
| 18 | `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops` | 148 |
| 19 | `2026-07-02-replace-private-images-and-bring-wave2` | 70 |
| 20 | `retro-educational-game-asset-pipeline-v1` | 116 |

### Tier 4 — Infra sub-tasks (11 changes, ~348 remaining)

Trivial-to-medium infra tasks. Absorbed as compressed sub-phases.

| # | Change | Total Tasks |
|--:|:--|--:|
| 21 | `2026-07-06-deploy-infisical-bunchloch-local` | 33 |
| 22 | `2026-07-06-wire-biep-notebooks-to-lakehouse` | 25 |
| 23 | `2026-07-06-upgrade-4-stacks-with-infisical` | 41 |
| 24 | `2026-07-06-ireland-legal-pipeline` | 42 |
| 25 | `2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep` | 45 |
| 26 | `2026-07-02-align-cianfhoghlaim-env-with-stacks` | 37 |
| 27 | `2026-07-02-bunchloch-stack-bootstrap` | 45 |
| 28 | `2026-07-02-add-agent-surface-stacks` | 30 |
| 29 | `2026-07-02-add-marimo-stack` | 17 |
| 30 | `2026-07-02-add-lancedb-and-logfire-stacks` | 20 |
| 31 | `2026-07-02-public-about-route` | 13 |

### Total

| Tier | Changes | Remaining tasks (estimated) |
|:--|--:|--:|
| T1 (force-finish) | 9 | ~57 |
| T2 (continuation) | 6 | ~315 |
| T3 (flagships; BIEP stays separate) | 5 | ~464 |
| T4 (infra sub-tasks) | 9 | ~300 |
| **Total absorbed** | **29** | **~1,136** |

## What changes

### W.1 Absorption (29 changes → 1)

- The 29 absorbed changes move from `openspec/changes/<name>/` to
  `openspec/changes/archive/<name>/` with an `ABSORBED.md` in each
  pointing back at this mega-change.
- The verbatim copies of each absorbed change's `proposal.md` +
  `tasks.md` live under `openspec/changes/2026-07-07-finalize-v4-landing/absorbed/<name>/`
  so the lineage is preserved for git archaeology.
- `openspec list` after the absorption shows just this change +
  `2026-07-06-british-isles-education-pipeline-v1`.

### W.2 Force-finish T1 (Phase 1 in tasks.md)

Lands the last ≤16 tasks for each of the 9 T1 changes. Most are
`commit -am`, `verify`, `archive` — bring-the-line tasks.

### W.3 Continue T2 (Phase 2 in tasks.md)

Picks up where each T2 change left off. Re-uses their original task
list; the work continues against the mega-change's `tasks.md` rather
than per-change.

### W.4 Land T3 flagships (Phase 3 in tasks.md)

5 zero-progress flagships land as named work-streams. Each retains
its proposal + scope inside `absorbed/<name>/proposal.md`; the mega-
change's tasks.md has the consolidated work list.

### W.5 Land T4 infra sub-tasks (Phase 4 in tasks.md)

9 infra sub-tasks land as compressed sub-phases.

## What does NOT change

- `2026-07-06-british-isles-education-pipeline-v1` — the new flagship
  is **NOT** absorbed; it stays a standalone change until it lands
  separately. Reference: the
  [`british-isles-education-pipeline` spec](../specs/british-isles-education-pipeline/spec.md)
- No code behaviour.
- No new dependencies in `pyproject.toml` or `package.json`.
- No spec architecture changes (all 47 canonical specs already aligned
  to v4 via the archived `2026-07-06-drift-cleanup-and-v4-alignment`).
- No changes to `openspec/AGENTS.md` or `openspec/project.md` (those
  are aligned to v4 already).
- No new openspec skills.

## Files

### Created

- `openspec/changes/2026-07-07-finalize-v4-landing/proposal.md` (this file)
- `openspec/changes/2026-07-07-finalize-v4-landing/tasks.md`
- `openspec/changes/2026-07-07-finalize-v4-landing/acceptance.md`
- `openspec/changes/2026-07-07-finalize-v4-landing/absorbed/README.md`
- `openspec/changes/2026-07-07-finalize-v4-landing/absorbed/<name>/{ABSORBED.md,proposal.md,tasks.md,...}` × 29

### Moved

- `openspec/changes/<name>/` → `openspec/changes/archive/<name>/` for each of the 29 absorbed changes

### Untouched

- `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/` (the surviving flagship)

## Acceptance

See `acceptance.md` for the 15-gate acceptance matrix.

- `openspec validate 2026-07-07-finalize-v4-landing --strict` passes
- `openspec list` shows ≤ 2 in-progress changes (this + the surviving BIEP v1)
- All 29 absorbed changes are in `openspec/changes/archive/` with
  `ABSORBED.md` files
- `tasks.md` shows 100% completion across Phases 1-4
- `mise run lint:skills` passes
- No `sruth/` ghost paths in any file under `openspec/`
- Branch + PR ready; merged via standard PR flow
- Mega-change archived; absorbed changes already in archive with
  `ABSORBED.md`

## Risk assessment

- **Mega-change is large**: ~1,136 tasks. Mitigated: each absorbed
  change is preserved verbatim under `absorbed/<name>/`; reviewers
  can spot-check any one in isolation.
- **Force-finishing T1 may break expected behaviour**: T1 changes are
  ≥50% done; remaining tasks are typically `commit -am` / `archive` /
  `verify` / `wrap`. No architectural risk.
- **Conflict with BIEP v1**: BIEP v1 stays separate with its own branch
  + PR; this change's `## Cross-references` flags this explicitly.
  The BIEP-v1 work completes independently; this change closes
  independently.
- **One mega-change is harder to revert than 29 separate**: `git revert <sha>`
  works identically. The clear single-revert surface is, in fact, an
  advantage for the v4 close-out.
- **openspec CLI may struggle with 1,136 tasks**: Use `--no-validate`
  archives if needed; the canonical spec surface already passed
  strict validation per the `2026-07-06-drift-cleanup-and-v4-alignment`
  archive event.

## Cross-references

- The completed drift cleanup:
  [`openspec/changes/archive/2026-07-06-drift-cleanup-and-v4-alignment/`](../archive/2026-07-06-drift-cleanup-and-v4-alignment/)
- The v4 consolidation:
  [`openspec/changes/archive/2026-06-28-2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/`](../archive/2026-06-28-2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4/)
- The surviving flagship (NOT absorbed):
  [`openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`](../2026-07-06-british-isles-education-pipeline-v1/)
- The 47 canonical specs:
  [`openspec/specs/`](../../specs/)

## Migration sources

| Absorbed change | Final canonical home |
|:--|:--|
| `cianfhoghlaim-educational-mmo-v1` | `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` |
| `croilar-portfolio` | `openspec/specs/croilar-portfolio/spec.md` |
| `agent-platform-cluster-hermes-cocoindex` | `openspec/specs/agent-platform-cluster/spec.md` |
| `bonneagar-v5-drift-refactor-and-komodo-gitops` | `openspec/specs/bonneagar-komodo-gitops/spec.md` |
| `ocr-vlm-registry-with-unsloth-priority` | `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` |
| (all 31 changes) | (their canonical homes — see `absorbed/<name>/ABSORBED.md`) |
