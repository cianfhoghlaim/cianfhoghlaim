# 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1

## Why

The Cianfhoghlaim repo has four overlapping documentation / sync surfaces that
have drifted out of sync with each other:

1. **AGENTS.md numbers are stale.** The root `AGENTS.md` (529 lines) claims
   *"75 specs"*, *"153 skills"*, *"88 Docker Compose stacks"* — ground truth
   today is **78 specs**, **155 skills**, **89 stacks**. Three categories,
   each drifting by ≥1 per week, with no lint to catch the drift.

2. **5 of 10 main in-repo areas have `README.md` but no `AGENTS.md`** —
   `orchestration/`, `baml_src/`, `meaisinfhoghlaim/`, `notebooks/`, `web/`.
   READMEs route humans; AGENTS.md files route the agent fleet (which is
   where most of the file edits now come from).

3. **No per-spec agent-routing convention.** All 78 specs in
   `openspec/specs/<name>/` have a `spec.md` but no `AGENTS.md`. An agent
   asked "how do I implement X for spec Y?" has to read the whole
   `spec.md` to find the right mise tasks, skills, and adjacent files.

4. **The knowledge-sync-loop is partially wired.** The 5-layer sync
   (`sync:paths`, `sync:ccc`, `sync:cognee`, `sync:skills`, `sync:mcp`) is
   in place per `openspec/changes/archive/2026-07-29-2026-08-15-knowledge-sync-loop-v1/`,
   but the daily `sync_health` Dagster asset (in `orchestration/defs/sync_assets.py`)
   is not on a cron schedule, no `Layer 6 — sync:dagster` requirement exists
   in the spec, and the stale-skill alert threshold (`< 0.95`) is documented
   in the asset docstring but not in the spec.

The user's choice (per the planning question) was "do all 4" — a single
coherent openspec change so the drift-correction lint, the cron wiring,
the spec-AGENTS convention, and the anti-drift contract all ship together
and are validated in one `--strict` pass.

## What changes

### Section A — Drift correction (the immediate, mechanical fix)

**A.1 — `mise run lint:drift-docs`** is the new anti-drift gate. It walks
the 10 in-repo `AGENTS.md` files + `openspec/AGENTS.md` + the root
`AGENTS.md`, regex-extracts claims of the form `(\d+) (specs|skills|stacks|models|notebooks)`,
and validates each against ground truth derived from `openspec list --specs`,
`find .agents/skills -name SKILL.md`, `ls -d bonneagar/stacks/*/`,
`MODEL_REGISTRY.summary()["total"]`, and `find notebooks -name "*.py"`.
Exits 1 on any mismatch; writes a JSON + Markdown report to
`stedding/sync-reports/docs-drift-{date}.md`.

**A.2 — Root `AGENTS.md` number fixes** (the 6 stale claims found in the
audit, all in the *Priority quick reference* + *CCC + Cognee dual-search
diagram* + *Best Practices* sections):

| Section | Old claim | New claim |
|:--|:--|:--|
| Priority skills header | `7 of 153` | `7 of 155` |
| Priority openspec commands | `75 specs` | `78 specs` |
| Infrastructure Stacks (3 sites) | `88 Compose stacks` | `89 Compose stacks` |
| `mise run lint:skills` task | `153 skills pass` | `155 skills pass` |
| Openspec `## Priority specs` header | `11 of 75` | `12 of 78` (after the 3 new specs land) |

**A.3 — 5 new per-area `AGENTS.md` files.** One each in
`orchestration/`, `baml_src/`, `meaisinfhoghlaim/`, `notebooks/`, `web/`.
Each follows the canonical 6-section outline (routing sentence, quick start,
key sources, adjacent specs, DO NOT, skill pointers) and ends with the
`<!-- generated: ISO date; do not hand-edit -->` footer from
the new `repo-hygiene-agent-routing` spec.

**A.4 — `web/README.md`** (a 20-line bridge so the `web/` directory is
not a black box — currently the only top-level area with neither README
nor AGENTS.md).

**A.5 — `openspec/AGENTS.md` refresh** to reference the 3 new specs
(`repo-hygiene-agent-routing`, `centralize-cross-cutting-docs`,
`knowledge-sync-loop`) and the new per-spec `AGENTS.md` convention.

### Section B — Knowledge-sync-loop wiring

**B.1 — Wire the daily `sync_health` cron.** Add
`orchestration/automation/sync_schedules.py` with
`@schedule(cron_schedule="0 */4 * * *", job=...)` referencing the
existing `sync_health` asset in `orchestration/defs/sync_assets.py`.
The cron already exists in the asset docstring; this change actually
attaches it.

**B.2 — Update `scripts/sync/all.sh`** to include the new
`sync:drift-docs` script so the unified report covers 7 layers
(paths / ccc / cognee / skills / mcp / drift-docs / dagster).

**B.3 — Create `scripts/sync/dagster.sh`** (Layer 6 from the
`2026-08-15-retroactive-pre-v7-cleanup-v1` change). Walks
`orchestration/defs/` and validates ~833 assets via `ast.parse`.

### Section C — Per-spec AGENTS.md convention (the new spec)

**C.1 — New `openspec/specs/repo-hygiene-agent-routing/spec.md`** with
3 ADDED Requirements:
- Every `openspec/specs/<name>/` MUST have a sibling `AGENTS.md` ≤30 lines
- Each per-spec `AGENTS.md` MUST list the 2 most relevant mise tasks
- Each per-spec `AGENTS.md` MUST end with the
  `<!-- generated: ISO date; do not hand-edit -->` footer

**C.2 — `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl`** —
the canonical 6-section outline template that the generator emits.

**C.3 — `scripts/sync/spec_agents.py`** — the generator. Walks
`openspec/specs/`, reads each `spec.md` first line (the one-line
purpose), and writes a sibling `AGENTS.md` if missing or older than
its `spec.md`.

**C.4 — Bootstrap pass** generates 78 per-spec `AGENTS.md` files.

### Section D — Cross-cutting anti-drift contract (the new spec)

**D.1 — New `openspec/specs/centralize-cross-cutting-docs/spec.md`** with
3 ADDED Requirements:
- The `lint:drift-docs` MUST exit non-zero on any number mismatch in
  the 12 audited `AGENTS.md` files
- The `spec_agents.py` generator MUST run on every PR that touches
  `openspec/specs/<x>/spec.md`
- The 6 priority `*` of `X` claims MUST be machine-checkable (no
  hand-edited numbers in the priority quick-reference blocks)

**D.2 — `.github/workflows/lint-drift-docs.yaml`** + the Forgejo
mirror `.forgejo/workflows/lint-drift-docs.yaml` — both install
mise, run `mise run lint:drift-docs`, fail the PR on exit 1.

**D.3 — Reuse the centralized-model-registry audit pattern**
(`scripts/registry_audit.py`) — the new lint inherits the same
exit-code + JSON-report + per-rule-result structure.

## Cross-references

- `openspec/changes/2026-07-29-complete-remaining-model-registry-migrations-v1`
  (sibling, in-flight) — provides the audit-pattern template
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1`
  (sibling, in-flight) — provides the Layer 6 (sync:dagster) script
- `openspec/changes/archive/2026-07-29-2026-08-15-knowledge-sync-loop-v1/`
  (archived) — provides the 5-layer sync scripts this change wires

## Out of scope

- **Renaming any of the 78 specs** — purely additive change
- **Rewriting the root `README.md`** (1231 lines; outside the agent-routing
  surface)
- **Removing the `.archive/` directory** (historical preservation; the
  `sync:paths` script already excludes it)
- **Touching `web/apps/*/AGENTS.md`** (per-app routing; each app has its own
  README + skills; out of scope for a repo-wide hygiene change)
- **Modifying the 318 archived openspec changes** — frozen history