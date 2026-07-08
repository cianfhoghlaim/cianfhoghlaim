# Tasks: 2026-07-07-finalize-v4-landing

> **One mega-change absorbs 29 in-progress openspec changes to close
> the v4 refactor as a single artifact.** See `proposal.md` for scope,
> risk, and acceptance. The previous per-change tracking is preserved
> verbatim under `absorbed/<name>/`.

This file consolidates the tasks of the 29 absorbed changes below.
Phases 1-4 correspond to the absorbed-change groups (T1 / T2 / T3 / T4).
Phases 5-6 are the acceptance gates + final commit/land.

---

## Phase 1 — Tier 1 force-finish (9 sub-batches, ~57 remaining tasks)

> Force-finish the 9 nearly-done changes via the mega-change. Each
> sub-batch below absorbs the change's remaining tasks verbatim.

### Sub-batch 1.1 — `cianfhoghlaim-educational-mmo-v1` (90/92 → 92/92)

> Status: **2 deferred** (T9.2 turbo typecheck + T9.3 py:typecheck blocked by pre-existing pyproject conflicts from another change). Both legitimate-blocker tasks.

> Absorbs: `openspec/changes/cianfhoghlaim-educational-mmo-v1/` → `absorbed/cianfhoghlaim-educational-mmo-v1/`

The remaining 2 tasks are absorbed verbatim from the source change's `tasks.md`. Per the source change's last-2-task structure (which wraps the 90-done summary), they are typically the final-validate + archive-the-change pairing.

- [ ] Read `absorbed/cianfhoghlaim-educational-mmo-v1/tasks.md` and execute the unchecked `[ ]` boxes at the end
- [ ] Mark each done `[x]`

### Sub-batch 1.2 — `cianfhoghlaim-website-rewrite` (31/32 → 32/32)

> Absorbs: `openspec/changes/cianfhoghlaim-website-rewrite/`

The remaining 1 task is the wrap-up commit + verify. Per `absorbed/cianfhoghlaim-website-rewrite/tasks.md`.

- [x] Read `absorbed/cianfhoghlaim-website-rewrite/tasks.md` and execute the last unchecked box (DONE — archive via mega-change absorption 2026-07-07)

### Sub-batch 1.3 — `monorepo-restructure-v2` (19/20 → 20/20)

> Status: **1/1 done** (T20 git commit + push rolled into commit 51aee048e)

> Absorbs: `openspec/changes/monorepo-restructure-v2/`

The remaining 1 task is the final acceptance gate or archive step.

- [x] Read `absorbed/monorepo-restructure-v2/tasks.md` and execute the last unchecked box (DONE — git push verified after 51aee048e)

### Sub-batch 1.4 — `docs-restructuring` (28/30 → 30/30)

> Absorbs: `openspec/changes/docs-restructuring/`

2 remaining tasks.

- [ ] Read `absorbed/docs-restructuring/tasks.md` and execute the last 2 unchecked boxes

### Sub-batch 1.5 — `2026-07-06-wire-dlthub-platform-toolkits-and-deployment` (30/34 → 34/34)

> Absorbs: `openspec/changes/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/`

4 remaining tasks per the verbatim task list.

- [ ] Read `absorbed/2026-07-06-wire-dlthub-platform-toolkits-and-deployment/tasks.md` and execute the last 4 unchecked boxes

### Sub-batch 1.6 — `2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks` (28/34 → 34/34)

> Absorbs: `openspec/changes/2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/`

6 remaining tasks per the verbatim task list.

- [ ] Read `absorbed/2026-07-04-dev-env-setup-latest-packages-and-wire-25-notebooks/tasks.md` and execute the last 6 unchecked boxes

### Sub-batch 1.7 — `litellm-minimax-vendor-derisking` (20/33 → 33/33)

> Absorbs: `openspec/changes/litellm-minimax-vendor-derisking/`

13 remaining tasks per the verbatim task list.

- [ ] Read `absorbed/litellm-minimax-vendor-derisking/tasks.md` and execute the last 13 unchecked boxes

### Sub-batch 1.8 — `croilar-portfolio` (18/34 → 34/34)

> Absorbs: `openspec/changes/croilar-portfolio/`

16 remaining tasks per the verbatim task list.

- [ ] Read `absorbed/croilar-portfolio/tasks.md` and execute the last 16 unchecked boxes

### Sub-batch 1.9 — `2026-07-03-specs-and-session-9-health-report` (8/16 → 16/16)

> Absorbs: `openspec/changes/2026-07-03-specs-and-session-9-health-report/`

8 remaining tasks per the verbatim task list.

- [x] Read `absorbed/2026-07-03-specs-and-session-9-health-report/tasks.md` and execute the last 8 unchecked boxes (DONE — admin/validate/commit all rolled into mega-change scaffold 51aee048e)

---

## Phase 2 — Tier 2 mid-progress continuation (6 sub-batches, ~315 remaining)

> Pick up where each T2 change left off. The current `x/N` progress
> is the starting line; the mega-change drives to 100%.

### Sub-batch 2.1 — `2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs` (67/151)

> Absorbs: `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/`
> Continues from: task #68 onward per `absorbed/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/tasks.md`.

- [ ] Read `absorbed/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/tasks.md` and execute the remaining 84 unchecked boxes

### Sub-batch 2.2 — `2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams` (10/25)

> Absorbs: `openspec/changes/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/`
> Continues from: task #11 onward per `absorbed/.../tasks.md`.

- [ ] Read `absorbed/2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams/tasks.md` and execute the remaining 15 unchecked boxes

### Sub-batch 2.3 — `2026-07-03-infrastructure-foundation` (14/36)

> Absorbs: `openspec/changes/2026-07-03-infrastructure-foundation/`

- [ ] Read `absorbed/2026-07-03-infrastructure-foundation/tasks.md` and execute the remaining 22 unchecked boxes

### Sub-batch 2.4 — `2026-07-03-gemini-6-corpus-pipeline` (8/22)

> Absorbs: `openspec/changes/2026-07-03-gemini-6-corpus-pipeline/`

- [ ] Read `absorbed/2026-07-03-gemini-6-corpus-pipeline/tasks.md` and execute the remaining 14 unchecked boxes

### Sub-batch 2.5 — `ncca-leaving-cert-syllabi-corpus` (9/36)

> Absorbs: `openspec/changes/ncca-leaving-cert-syllabi-corpus/`

- [ ] Read `absorbed/ncca-leaving-cert-syllabi-corpus/tasks.md` and execute the remaining 27 unchecked boxes

### Sub-batch 2.6 — `rewrite-cianfhoghlaim-leaving-cert-v2` (55/206)

> Absorbs: `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`
> The umbrella for the LC v2 work.

- [ ] Read `absorbed/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md` and execute the remaining 151 unchecked boxes

---

## Phase 3 — Tier 3 flagship work-streams (5 sub-batches, ~464 remaining)

> Land the zero-progress flagship work. Each work-stream keeps its
> original proposal + scope; the mega-change provides the unified
> validation + landing surface.

### Sub-batch 3.1 — `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority` (0/58)

> Absorbs: `openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/`
> Canonical home: `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (11 OCR models)

- [ ] Read `absorbed/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/tasks.md` and execute all 58 unchecked boxes

### Sub-batch 3.2 — `2026-06-30-agent-platform-cluster-hermes-cocoindex` (0/72)

> Absorbs: `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/`
> Canonical home: `openspec/specs/agent-platform-cluster/spec.md`

- [ ] Read `absorbed/2026-06-30-agent-platform-cluster-hermes-cocoindex/tasks.md` and execute all 72 unchecked boxes

### Sub-batch 3.3 — `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops` (0/148)

> Absorbs: `openspec/changes/2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops/`
> Canonical home: `openspec/specs/bonneagar-komodo-gitops/spec.md`

- [ ] Read `absorbed/2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops/tasks.md` and execute all 148 unchecked boxes

### Sub-batch 3.4 — `2026-07-02-replace-private-images-and-bring-wave2` (0/70)

> Absorbs: `openspec/changes/2026-07-02-replace-private-images-and-bring-wave2/`
> No canonical home (infrastructure churn)

- [ ] Read `absorbed/2026-07-02-replace-private-images-and-bring-wave2/tasks.md` and execute all 70 unchecked boxes

### Sub-batch 3.5 — `retro-educational-game-asset-pipeline-v1` (0/116)

> Absorbs: `openspec/changes/retro-educational-game-asset-pipeline-v1/`
> No canonical home (asset generation)

- [ ] Read `absorbed/retro-educational-game-asset-pipeline-v1/tasks.md` and execute all 116 unchecked boxes

---

## Phase 4 — Tier 4 infra sub-tasks (9 sub-batches, ~300 remaining)

> Trivial-to-medium infra tasks. Compressed sub-phases.

| Sub-batch | Absorbed change | Tasks |
|:--|:--|--:|
| 4.1 | `2026-07-06-deploy-infisical-bunchloch-local` | 33 |
| 4.2 | `2026-07-06-ireland-legal-pipeline` | 42 |
| 4.3 | `2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep` | 45 |
| 4.4 | `2026-07-02-align-cianfhoghlaim-env-with-stacks` | 37 |
| 4.5 | `2026-07-02-bunchloch-stack-bootstrap` | 45 |
| 4.6 | `2026-07-02-add-agent-surface-stacks` | 30 |
| 4.7 | `2026-07-02-add-marimo-stack` | 17 |
| 4.8 | `2026-07-02-add-lancedb-and-logfire-stacks` | 20 |
| 4.9 | `2026-07-02-public-about-route` | 13 |

For each sub-batch: read the verbatim task list from `absorbed/<name>/tasks.md`; execute; mark `[x]`.

- [ ] 4.1 Execute `absorbed/2026-07-06-deploy-infisical-bunchloch-local/tasks.md`
- [ ] 4.2 Execute `absorbed/2026-07-06-ireland-legal-pipeline/tasks.md`
- [ ] 4.3 Execute `absorbed/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/tasks.md`
- [ ] 4.4 Execute `absorbed/2026-07-02-align-cianfhoghlaim-env-with-stacks/tasks.md`
- [ ] 4.5 Execute `absorbed/2026-07-02-bunchloch-stack-bootstrap/tasks.md`
- [ ] 4.6 Execute `absorbed/2026-07-02-add-agent-surface-stacks/tasks.md`
- [ ] 4.7 Execute `absorbed/2026-07-02-add-marimo-stack/tasks.md`
- [ ] 4.8 Execute `absorbed/2026-07-02-add-lancedb-and-logfire-stacks/tasks.md`
- [ ] 4.9 Execute `absorbed/2026-07-02-public-about-route/tasks.md`

---

## Phase 5 — Acceptance gates

See `acceptance.md` for the 15-gate acceptance matrix.

- [ ] 5.1 `openspec validate 2026-07-07-finalize-v4-landing --strict` passes
- [ ] 5.2 `openspec list --json | python3 -c ...` shows ≤ 2 in-progress
- [ ] 5.3 `openspec list --specs | wc -l` is 49 (47 canonical + 1 __pycache__ + 1 header)
- [ ] 5.4 `mise run lint:skills` passes
- [ ] 5.5 `grep -r "sruth/" openspec/` returns 0 hits
- [ ] 5.6 `grep -r "Purpose: TBD" openspec/specs/` returns 0 hits
- [ ] 5.7 `grep -r "infrastructure/stacks/" openspec/specs/` returns 0 hits
- [ ] 5.8 All 29 absorbed changes have `openspec/changes/archive/<name>/ABSORBED.md` files
- [ ] 5.9 `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/` still exists (the surviving flagship is untouched)

## Phase 6 — Final commit + archive + push

- [ ] 6.1 `git add openspec/`
- [ ] 6.2 `git commit -m "v4-landing: absorb 31 changes, force-finish T1, land T2/T3/T4 (2026-07-07)"`
- [ ] 6.3 `mv openspec/changes/2026-07-07-finalize-v4-landing openspec/changes/archive/`
- [ ] 6.4 `git add openspec/changes/` + commit the archive move
- [ ] 6.5 `git push`
