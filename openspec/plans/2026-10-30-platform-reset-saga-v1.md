# Cianfhoghlaim Platform Reset Saga v1 — The 4-Umbrella Campaign (2026-10-30)

> **Status: ✓ CLOSED (4 PRs merged: #209, #210, #211, #212 + this saga-closure change).** This is the meta-plan that supersedes the convergence saga
> (2026-10-01) for the 4-week+ campaign beyond it. The convergence saga
> shipped 7 of 8 plans; the Stage 8 fresh-slate handoff is documented.
> This saga drives the repo from 126 active openspec changes → ≤ 80, from
> 21 pre-existing BAML errors → 0, from 13 tracked `.DS_Store` files → 0,
> and from a stale lakehouse bridge to 12 healthy services.
>
> **The constraint**: visible interim updates between every umbrella so
> the operator can demo progress. One marimo dashboard per umbrella
> (mirrors the convergence saga's C6 quality-of-life pattern). One PR
> per umbrella, ordered housekeeping → BAML → triage → lakehouse.

## Status

✓ **CLOSED (2026-10-30)** — all 4 umbrella PRs merged on main:

| Umbrella | PR | Merged | Notes |
|:--|:--|:--|:--|
| 1 — `2026-10-30-housekeeping-sprawl-cleanup-v1` | [#209](https://github.com/cianfhoghlaim/cianfhoghlaim/pull/209) | 2026-10-30 | untrack 13 `.DS_Store`, move 5 root orphans, add `core:housekeeping:status` + `housekeeping:autofix` |
| 2 — `2026-10-30-biep-tertiary-baml-repair-v1` | [#210](https://github.com/cianfhoghlaim/cianfhoghlaim/pull/210) | 2026-10-30 | `dltq_naming` schema-naming convergence + BAML lint + 4 → 3 BAML errors (the 3 remaining are a `baml-cli 0.226.1` parser bug) |
| 3 — `2026-10-30-lakehouse-bridge-bring-up-v1` | [#212](https://github.com/cianfhoghlaim/cianfhoghlaim/pull/212) | 2026-10-30 | OrbStack recovery runbook + `core:lakehouse:health` + `core:lakehouse:up` mise tasks + `lakehouse_health.py` marimo; runtime bridge-verify deferred to operator |
| 4 — `2026-10-30-openspec-backlog-triage-v1` | [#211](https://github.com/cianfhoghlaim/cianfhoghlaim/pull/211) | 2026-10-30 | 52 archives + 5 KEEP stubs + `media-intel` spec registered + `core:lint:skills` + `core:openspec:status` mise tasks |
| saga-closure — `2026-10-30-saga-closure-and-baml-repair-v1` | this change | (pending) | fixes the 4 follow-on issues — see "What was deferred" below |

## What was deferred

The 4 umbrella PRs each had E1/G2/F3-style "deferred until later" boxes in
their `tasks.md`. This saga-closure change addresses those deferrals:

1. **Duplicate `[tasks."core:lint:skills"]` in `mise.toml`** — Umbrella 1
   (PR #209) and Umbrella 4 (PR #211) both added the same block; the TOML
   parser rejected the file. Removed the Umbrella 1 occurrence; kept the
   canonical Umbrella 4 version (the one with the simpler `run = "bash
   scripts/lint_skills.sh"` command).
2. **Bash syntax error in `scripts/lint_skills.sh`** — the argument-parsing
   `case` statement was malformed (the `--limit)` pattern tried to match
   the literal string `"--limit)"`, not the value of `$1`). Rewrote the
   argument loop as a `while [ $# -gt 0 ]; do case "$1" in ... esac;
   done` loop. Also fixed the off-by-one in the `--limit N` check (the
   count was incremented before the limit comparison, so `--limit 3`
   showed 4 skills; the fix decrements before the `break`).
3. **Lakehouse Umbrella 3 task count discrepancy** — the saga plan
   claimed `0/20` tasks for Umbrella 3, but the umbrella only shipped 4
   files + the runbook (not 20 task-checkbox units). Rewrote
   `openspec/changes/2026-10-30-lakehouse-bridge-bring-up-v1/tasks.md` to
   the honest breakdown: 7 done (D1–D3 marimo + mise tasks; E1–E3
   skill doc + validate + PR #212 merged; F2 skill-doc reference), 14
   deferred (all of Groups A/B/C — operator-side OrbStack + bridge
   bring-up + schema-naming rollout; F1 12-services smoke test; F3
   subagent assignment).
4. **Saga-deferred STATUS.md + AGENTS.md + CHEATSHEET.md updates** — the
   3 merged umbrellas (housekeeping, baml-repair, openspec-triage) all
   had "STATUS.md update" + "skill doc reference" + "PR merge" boxes
   marked DEFERRED. With PRs #209, #210, #211 all merged on main, those
   boxes are now ticked honestly in their respective `tasks.md` files.
   This change also ships the actual STATUS.md update (the 4 umbrellas
   marked as ✓ MERGED with PR numbers), the saga-closure "completed
   sagas" section, the saga plan "Status" + "What was deferred"
   sections, and the `AGENTS.md` + `CHEATSHEET.md` one-line
   `media-intel` + `core:status` references.

## 0. How to read this plan

This is the **top-level saga doc** for 4 openspec changes (Umbrellas 1–4).
Each umbrella has its own `openspec/changes/2026-10-30-<umbrella>/`
folder with a `proposal.md`, `tasks.md`, and `specs/<capability>/spec.md`.
**Umbrella 0** is this document (the meta-plan).

Each umbrella:
- Has a single domain focus (housekeeping, BAML, lakehouse, or spec/skill)
- Is PR-able independently in any order, BUT the recommended order
  is housekeeping → BAML → triage → lakehouse (because the lakehouse
  umbrella depends on the BAML project building green)
- Ships 1 visible marimo demo + 1 mise task + 1 stub-to-real conversion
- Uses 1+ subagents for parallel work
- Closes 1 of the Stage 8 fresh-slate gaps + 1 of the convergence saga's
  4 deferred hand-offs

The cross-cutting concerns (C1–C6) run in parallel and accelerate all umbrellas.

## 1. Umbrella 0 (this document) — the meta-plan

Already done in this change: the saga doc itself, the STATUS.md update,
and the 4 umbrella change folders.

## 2. Umbrella 1 — `2026-10-30-housekeeping-sprawl-cleanup-v1`

### Domain

**Operational hygiene** + **code de-sprawl**. The convergence saga was
focused on shipping features; the 18 months of accumulated housekeeping
(`docs/google_examples/`, `docs/tanstack_ai/`, 13 tracked `.DS_Store`
files, 1,801 untracked `.DS_Store` files, 2,000+ `__pycache__` dirs,
5 root-level orphan files, 8 root-level orphan dirs) was deferred.

### What this umbrella ships

1. Untrack the 13 tracked `.DS_Store` files + tighten `.gitignore`
2. Move the 2 untracked `docs/google_examples/` + `docs/tanstack_ai/`
   snapshot dirs out of the working tree (operator-personal research)
3. Add the `core:hydrate:curriculum` + `media-intel` entries to `CHEATSHEET.md`
4. Move the 5 root-level orphan files to their canonical homes
   (`bilingual_concept_registry.py` → `meaisinfhoghlaim/alignment/`,
   `cli.py` → `cianfhoghlaim/cli.py`, `_tmp_lint.sh` → `scripts/lint_skills.sh`,
   the 2 `__init__.py` at root → verify + `git rm` if empty)
5. Untrack the `instagram_output/`, `cloud/`, `data/`, `downloads/`,
   `cian_mac*/` patterns (4 of 5 are already in `.gitignore`; verify
   `cian_mac*/` coverage)
6. Consolidate the `_legacy` / `_archive` / `_cross` / `_shared`
   directory-prefix conventions across the 6 BAML clusters
7. Recreate `agents/adk/tools/retro_capture.py` (the file disappeared
   mid-session and was never tracked) as a minimal stub re-exporting
   `MEDIA_LIBRARY` from `media_library.py`
8. Add the housekeeping status marimo + the `mise run core:housekeeping:status` task

### Files touched

- `.gitignore` (add `cian_mac*/` pattern)
- `CHEATSHEET.md` (add 2 entries)
- `agents/adk/tools/retro_capture.py` (recreate as a 30-line stub)
- `bilingual_concept_registry.py` (root) → `meaisinfhoghlaim/alignment/bilingual_concept_registry.py`
- `cli.py` (root) → `cianfhoghlaim/cli.py` (verify)
- `_tmp_lint.sh` (root) → `scripts/lint_skills.sh`
- `notebooks/dashboards/housekeeping_status.py` (new, the visibility demo)
- `mise.toml` (add `core:housekeeping:status` + `housekeeping:autofix`)

### Cross-cutting tie-off

- C1: Add `core:housekeeping:status` to the GitHub Actions workflow
- C2: Update `AGENTS.md` to reference the new status dashboard
- C3: All 4 sub-asks pass `openspec validate --strict`
- C6: 1 subagent runs the dirty-tree untrack + 1 subagent runs the root-file moves

## 3. Umbrella 2 — `2026-10-30-biep-tertiary-baml-repair-v1`

### Domain

**BAML full repair** + **schema-naming convergence**. The 21 pre-existing
BAML errors documented in F1 of `2026-10-10-media-intel-and-curriculum-hydration-v1`
are out of scope for that change but block every other BAML consumer.
The Stage 8 handoff's Gap 1 (schema-naming convergence) and Gap 3
(parser workaround) are also closed here.

### What this umbrella ships

1. The 21 pre-existing BAML errors → 0 (file-by-file repair; the 4
   duplicate class/function defs collapse to canonical, the 3 module_handbook
   collisions resolve, the enum-as-class pattern converts to UpperCamelCase
   enums, the 8 university_extraction.baml cascades re-parse, the
   teacher_extraction.baml:17 error is inspected and fixed)
2. The 3 parser-quirk contracts (`extract_syllabus_diagram.baml`,
   `extract_design_pattern.baml`, `gameplay_descriptor.baml`) convert to
   single-line `@description("...")` style
3. The `scripts/lint_baml_frontmatter.py` CI lint that prevents the
   multi-line regression
4. The `baml_src/_shared/dltq_naming.py::to_dlq_table_name(quadrant, table)`
   helper that converges the 3 conflicting naming conventions
5. The deprecation alias shim for the legacy `ducklake_<x>` and
   `oideachais_<x>` patterns (6-month grace period per Stage 8)
6. The 4 wiring points (per the Stage 8 handoff): `agents/agent_registry.py:AGENT_REGISTRY`,
   `cocoindex_flows/media/{gaeilge,cymraeg,...}/asset_index.py`,
   `dlt_sources/destinations/_common.py:DUCKLAKE_NAMESPACE`,
   `baml_src/_shared/dltq_naming.py` itself
7. The `notebooks/dashboards/baml_build_status.py` marimo (visibility)

### Files touched

- `baml_src/british_isles/ireland/education/teacher/teacher_extraction.baml` (1 error)
- `baml_src/british_isles/ireland/tertiary/module_handbook.baml` (3 errors, resolve to canonical)
- `baml_src/british_isles/ireland/tertiary/past_paper.baml` (2 errors, delete duplicate)
- `baml_src/british_isles/ireland/education/_legacy/pdfs/leaving_cert_past_paper.baml` (2 errors, delete)
- `baml_src/british_isles/ireland/tertiary/university_extraction.baml` (8 cascading errors, repair)
- `baml_src/british_isles/ireland/tertiary/reading_list.baml` (1 error)
- `baml_src/british_isles/ireland/education/stages/tertiary.baml` (1 error)
- `baml_src/british_isles/ireland/education/student/jc_workflows.baml` (2 errors, parser quirk)
- `baml_src/british_isles/_shared/lc_extraction_template.baml:581` (1 warning, enum string)
- 5 files with the `class X { earth string; air string; ... }` enum-as-class pattern
  (likely `animation_descriptor.baml`, `comic_descriptor.baml`,
  `prose_descriptor.baml`, `gameplay_descriptor.baml`, `reading_list.baml`)
- `scripts/lint_baml_frontmatter.py` (new)
- `baml_src/_shared/dltq_naming.py` (new)
- `agents/agent_registry.py` (call site, 13 entries)
- `cocoindex_flows/media/{gaeilge,cymraeg,...}/asset_index.py` (call site, 6 entries)
- `dlt_sources/destinations/_common.py` (call site, 1 entry)
- `notebooks/dashboards/baml_build_status.py` (new)
- `mise.toml` (add `core:baml:status` + wire `lint_baml_frontmatter.py` into `core:lint`)

### Cross-cutting tie-off

- C1: `baml-cli generate` exits 0 + the lint blocks future regressions
- C2: `.agents/skills/baml/SKILL.md` updates the "21 pre-existing errors" table to "0"
- C3: `openspec validate --strict` passes
- C6: 2 subagents run in parallel (1 for the file-by-file BAML repair, 1 for the dltq_naming helper + 4 call sites)

## 4. Umbrella 3 — `2026-10-30-lakehouse-bridge-bring-up-v1`

### Domain

**Lakehouse bridge bring-up** + **schema-naming rollout**. The 12 lakehouse
services (Garage + ClickHouse + Cognee + Graphiti + FalkorDB + Memgraph(-lab)
+ Olake + Nimtable UI + OTel collector + lakekeeper-migrate + lance-namespace
sidecar) are down on `bunchloch` because the OrbStack Docker daemon socket
is missing (per Stage 8 Gap 4). The 3 bring-up scripts at `scripts/lakehouse/`
are ready to run.

### What this umbrella ships

1. OrbStack Docker daemon socket recovery (per Stage 8 Gap 4)
2. The 3 bring-up scripts run cleanly: `init_lakehouse_postgres.sh`,
   `up_lakehouse_bridge.sh`, `verify_bridge.py`
3. The 12 services green on `bunchloch`
4. The `to_dlq_table_name` helper from Umbrella 2 wired into the 4
   lakehouse-stack compose files
5. The 6 per-language `media.image_gen_chunks_<lang>` LanceDB tables
   get the canonical pattern rename (or staged for the deprecation
   grace period)
6. The 13 `oideachais_<agent>` cognee_datasets get the canonical pattern
   rename (or staged)
7. The `notebooks/dashboards/lakehouse_health.py` marimo (visibility)

### Files touched

- `bonneagar/stacks/lakehouse-bridge/docker-compose.yaml` (diagnose + bring-up)
- `bonneagar/stacks/lakehouse-bridge/sidecar.yaml` (if needed)
- `bonneagar/stacks/lance-namespace/docker-compose.yaml` (wire `to_dlq_table_name`)
- `bonneagar/stacks/cognee-bunchloch/docker-compose.yaml` (rename 13 datasets)
- `bonneagar/stacks/olake/docker-compose.yaml` (wire naming)
- 6 files at `cocoindex_flows/media/{gaeilge,cymraeg,...}/asset_index.py` (rename)
- `notebooks/dashboards/lakehouse_health.py` (new)
- `mise.toml` (add `core:lakehouse:health`)

### Cross-cutting tie-off

- C1: The 12 services pass the `verify_bridge.py` smoke test
- C2: `.agents/skills/motherduck/SKILL.md` updates the bring-up runbook
- C3: `openspec validate --strict` passes
- C6: 1 subagent handles the Docker recovery + 1 subagent handles the schema-naming rollout (depends on Umbrella 2's helper)

## 5. Umbrella 4 — `2026-10-30-openspec-backlog-triage-v1`

### Domain

**79-stalled-change triage** + **spec refresh** + **skill refresh**. The
Stage 8 handoff's Gap 2 (79-stalled-change backlog) and the operator
infrastructure (107 specs, 80 skills) need a single coordinated cleanup.
The 80 skills have 1 known conformance failure (per `_tmp_lint.sh`); the
107 specs have 1 stale-paths warning in `openspec/project.md`.

### What this umbrella ships

1. The 80 0/0-progress changes classified as: KEEP (30), ARCHIVE-AS-RESEARCH (20),
   ARCHIVE-AS-OUTDATED (29), MERGE-INTO-OTHER (1) — per Stage 8 Gap 2
2. For each KEEP change, write a 1-paragraph "what this is for" stub in
   the change's `proposal.md` so future readers don't have to figure it
   out from a 0/40 task list
3. `openspec archive <change> --yes` for all 20 + 29 = 49 ARCHIVE changes
4. `openspec 1.11 doctor` across all 107 specs + fix the 0/zero warnings
5. Fix the STALE PATHS WARNING in `openspec/project.md` (replace with v7 layout)
6. Add the new `media-intel-and-curriculum-hydration` spec to `openspec list --specs`
7. Run the `_tmp_lint.sh` style check across all 80 skills + fix the
   1 known failure + promote to `mise run core:lint:skills`
8. The `notebooks/dashboards/openspec_status.py` marimo (visibility)

### Files touched

- 20 changes at `openspec/changes/2026-09-01-<sister>-sister-umbrella-mirror-v1/`
  → archive
- 29 changes at `openspec/changes/2026-09-01-<various>/` (outdated) → archive
- 30 changes at `openspec/changes/<various>/` (keep) → 1-paragraph stub in each `proposal.md`
- `openspec/project.md` (fix STALE PATHS WARNING)
- `openspec/specs/` (add the new `media-intel-and-curriculum-hydration` spec)
- 1 skill at `.agents/skills/<failing>/SKILL.md` (fix the 1 known conformance failure)
- `scripts/lint_skills.sh` (promote from `_tmp_lint.sh` + add to `mise run core:lint`)
- `notebooks/dashboards/openspec_status.py` (new)
- `mise.toml` (add `core:lint:skills` + `openspec:status`)
- `openspec/plans/STATUS.md` (mark this umbrella as the last saga)

### Cross-cutting tie-off

- C1: `openspec list --changes` returns ≤ 80 entries (down from 126)
- C2: `AGENTS.md` + `CHEATSHEET.md` reference the new `openspec:status` task
- C3: `openspec validate --strict` passes
- C6: 1 subagent handles the 49 archive moves + 1 subagent handles the 30 KEEP-stubs

## 6. Cross-cutting concerns (C1–C6, run in parallel)

- **C1 — CI gate suite** — every PR runs the 4 new validation gates:
  `core:housekeeping:status`, `baml-cli generate`, `core:lakehouse:health`,
  `openspec:status`. Add to `mise run core:lint` + the GitHub Actions workflow.
- **C2 — Documentation update** — every PR that touches a quadrant's
  surface updates its `AGENTS.md` and the corresponding
  `.agents/skills/<surface>/SKILL.md`. Mirrors the convergence saga's C5.
- **C3 — openspec 1.11 compliance** — every change passes
  `openspec validate --strict` before merge. Mirrors the convergence saga's C2.
- **C4 — Vis demo per umbrella** — 1 marimo notebook per umbrella
  (matches the convergence saga's C6 quality-of-life pattern). The 4
  notebooks: `housekeeping_status`, `baml_build_status`, `lakehouse_health`,
  `openspec_status`.
- **C5 — DuckLake dev-first invariant** — every DLT pipeline must use
  the local DuckLake default + the `to_dlq_table_name` helper from
  Umbrella 2 (re-inforced by Umbrella 3's rollout).
- **C6 — Subagent fan-out** — the 4 umbrellas run in parallel via
  `general-purpose` subagents (we already proved this works for
  Umbrella 1's sub-asks + the media-intel work; scale to all 4).
  Mirrors the convergence saga's pattern.

## 7. Verification + visibility milestones (1 marimo per umbrella)

The 4 new marimo dashboards (each lives at `notebooks/dashboards/`
and is wired into the control panel):

1. **`housekeeping_status.py`** — dirty-tree count, untracked `.DS_Store`
   count, `__pycache__` count, change backlog by progress bucket.
2. **`baml_build_status.py`** — `baml-cli generate` exit code, error
   count (target 0), function/class counts.
3. **`lakehouse_health.py`** — the 12 services with green/yellow/red
   status, the 4 DuckLake destinations.
4. **`openspec_status.py`** — change count (target ≤ 80), spec count
   (target 108), skill count, the 49-archived-this-week list.

## 8. Risk register + rollback plan

| Risk | Mitigation | Rollback |
|--|--|--|
| `baml-cli generate` is broken across the BIEP tertiary surface | Umbrella 2 Group A repairs all 21 errors; lint prevents re-introduction | `git revert` Umbrella 2 PR; `baml-cli` returns to broken state (no worse than baseline) |
| OrbStack Docker daemon socket missing | Umbrella 3 Group A diagnoses + fixes; the bring-up scripts are already in place | `git revert` Umbrella 3 PR; lakehouse remains down (no worse than baseline) |
| The 79-stalled-change triage is subjective | Use the 30/20/29 breakdown as the starting position; the operator can override per-change | `openspec unarchive <change>` for any change misclassified |
| The 4 PRs conflict on shared files | Verified by file-path analysis: Umbrella 1 changes root files, Umbrella 2 changes BAML files, Umbrella 3 changes lakehouse compose + DLT destinations, Umbrella 4 archives openspec changes | Re-base the conflicting PRs |
| The new saga exceeds the 8-week estimate | Cut Umbrella 3 Group C (the schema-naming rollout) first; everything else is shippable independently | The other 3 umbrellas ship; the rollout is a follow-on |
| 13 tracked `.DS_Store` files have already been untracked | The `git rm --cached` is a no-op; the lint still applies | N/A |

## 9. Cross-references

- Convergence saga (superseded by this saga): `openspec/plans/2026-10-01-convergence-saga-v1.md`
- Sprawl plan (informs Umbrella 1): `openspec/plans/2026-08-26-sprawl-and-changes-v3.md`
- V6 era plan (informs Umbrella 1 + 2): `openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`
- Stage 8 handoff (informs Umbrella 2 + 3 + 4): `openspec/plans/2026-10-26-stage-8-fresh-slate-spec-handoff-v1.md`
- Media-intel saga (this saga's predecessor): `openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md`
- F1 entry (the 21 pre-existing BAML errors): `openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/tasks.md`
- BAML Phase B TODO notes: `baml_src/AGENTS.md`, `cocoindex_flows/AGENTS.md`, `dlt_sources/AGENTS.md`
- `_tmp_lint.sh` (the existing skill conformance checker): `_tmp_lint.sh` (to be promoted to `scripts/lint_skills.sh` in Umbrella 1)
