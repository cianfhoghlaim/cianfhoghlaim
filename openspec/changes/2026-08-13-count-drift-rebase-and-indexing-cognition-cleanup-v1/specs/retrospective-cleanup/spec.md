# retrospective-cleanup — Change 3 Delta (2026-08-13)

## ADDED Requirements

### Requirement: every AGENTS.md count claim SHALL match ground truth

The system MUST keep every claim of the form
`<N> (specs|skills|stacks|models|notebooks)` in every
in-scope `AGENTS.md` file (the 16 files enumerated in
`scripts/lint_drift_docs.py:AGENTS_FILES`) matching the
live ground-truth count produced by
`scripts/lint_drift_docs.py:ground_truth()`.

A new `mise run lint:drift-docs:rebaseline` task
(implemented by `scripts/rebaseline_drift_docs.py`) MUST
walk every drift violation reported by
`mise run lint:drift-docs` and rewrite the count claim
in place. The script MUST support:

1. A default **dry-run mode** that prints the planned
   diff and exits 0
2. An `--apply` mode that writes the fix to disk

The script MUST emit a JSON report at
`stedding/sync-reports/drift-docs-rebaseline-{date}.json`
listing every planned/applied fix with the file path,
line number, old value, and new value.

#### Scenario: Operator rebaselines a stale count claim

- **GIVEN** an operator runs `mise run lint:drift-docs`
  and the report shows a violation (e.g.
  `AGENTS.md:20 specs: claimed 89, actual 92`)
- **WHEN** the operator runs
  `mise run lint:drift-docs:rebaseline:dry-run`
- **THEN** the script MUST print a diff showing the
  planned fix: "`AGENTS.md:20` `89` → `92`"
- **AND** the script MUST exit 0 without modifying any
  files
- **WHEN** the operator then runs
  `mise run lint:drift-docs:rebaseline` (with `--apply`)
- **THEN** the script MUST write the fix to disk
- **AND** a subsequent run of `mise run lint:drift-docs`
  MUST report 0 violations

#### Scenario: New AGENTS.md file is added with a stale count

- **GIVEN** a developer adds a new file
  `orchestration/defs/2_materials/_base/AGENTS.md` that
  claims `45 Dagster assets` but the actual count is 833
- **WHEN** the operator runs `mise run lint:drift-docs`
- **THEN** the script MUST report the violation
- **WHEN** the operator runs
  `mise run lint:drift-docs:rebaseline`
- **THEN** the script MUST fix the count to `833`
- **AND** the AGENTS_FILES list in
  `scripts/lint_drift_docs.py` MUST auto-include the new
  file (or the operator MUST add it manually if the
  in-scope list is curated)

### Requirement: INDEXING_AND_COGNITION.md SHALL reflect the current agent + skill + MCP counts

The system MUST keep the
`.agents/skills/INDEXING_AND_COGNITION.md` skill
(the 655-line consolidated doc that replaced the
`docs/01-cognee/*.md` files during the v4 consolidation)
reflecting the live ground truth of:

1. The number of MCP servers wired in `opencode.json`
2. The number of OpenCode agents wired in `opencode.json`
3. The number of skills discoverable via
   `bun run ccc:search` (recursive count of SKILL.md
   files under `.agents/skills/`)
4. The CCC chunk count (from `bun run ccc:status` or
   `ccc status`)
5. The Cognee cluster count (the 7 typed clusters from
   the per-cluster cognify model)

…matching the live ground truth at all times.

The file MUST NOT reference dead paths (e.g.
`sruth/cianfhoghlaim/STATUS.md`) that no longer exist on
disk.

#### Scenario: A new skill is added

- **GIVEN** a developer adds a new skill
  `.agents/skills/new-skill/SKILL.md` (e.g. the
  `firecrawl-research-index` skill)
- **WHEN** the operator runs `bun run ccc:status` and
  `mise run lint:skills`
- **THEN** the skill count MUST increment by 1
- **AND** the operator MUST update
  `.agents/skills/INDEXING_AND_COGNITION.md` to reflect
  the new count
- **OR** the `lint:drift-docs` gate MUST catch the
  inconsistency on the next CI run

#### Scenario: INDEXING_AND_COGNITION.md references a dead path

- **GIVEN** INDEXING_AND_COGNITION.md references
  `sruth/cianfhoghlaim/STATUS.md` (a path that no longer
  exists post-v7 flattening)
- **WHEN** an agent searches for that file
- **THEN** the search MUST fail
- **AND** `mise run lint:drift-docs` MUST NOT catch this
  (drift-docs only checks count claims, not path claims)
- **AND** the `lint:guides-yml` gate (from Change 2)
  MUST catch it if the path appears in `.cocoindex_code/guides.yml`
- **AND** the operator MUST manually delete the dead
  reference