# Tasks — Count Drift Rebase + INDEXING_AND_COGNITION Cleanup

## 1. Rebaseline the 7 count violations in 4 AGENTS.md files

- [ ] 1.1 `AGENTS.md:20` — `89 specs` → `92 specs`
- [ ] 1.2 `AGENTS.md:81` — `92 stacks` → `93 stacks`
- [ ] 1.3 `agents/tuatha/AGENTS.md:61` — `89 specs` → `92 specs`
- [ ] 1.4 `bonneagar/AGENTS.md:29` — `92 stacks` → `93 stacks`
- [ ] 1.5 `bonneagar/AGENTS.md:89` — `92 stacks` → `93 stacks`
- [ ] 1.6 `bonneagar/AGENTS.md:155` — `92 stacks` → `93 stacks`
- [ ] 1.7 `notebooks/AGENTS.md:239` — `52 notebooks` → `54 notebooks`

## 2. Rebaseline the 8 internal inconsistencies in INDEXING_AND_COGNITION.md

- [ ] 2.1 §1 CCC chunk count — update to current numbers
- [ ] 2.2 §2 Cognee cluster count — update to current numbers
- [ ] 2.3 §3 the 9 MCP servers — update to 15 (per `opencode.json`)
- [ ] 2.4 §8 the 14 OpenCode agents — verify count
- [ ] 2.5 §8 the 9 MCP servers — update to 15
- [ ] 2.6 §8 the skill count claims — update from 123/153 to 162
- [ ] 2.7 §8 health-check snippets — update expected outputs
- [ ] 2.8 §9.1 directory migration map — drop the dead
      `sruth/cianfhoghlaim/STATUS.md` reference; replace with
      `dlt_sources/AGENTS.md` + the new `data-engineering`
      skill (from Change 1)

## 3. Add `mise run lint:drift-docs:rebaseline` task + script

- [ ] 3.1 Create `scripts/rebaseline_drift_docs.py` (~100 lines)
      - Loads the drift report JSON
      - For each violation, computes the corrected number
      - Writes the fix to disk (with `--apply` flag) or
        just prints the diff (default dry-run)
- [ ] 3.2 Add `[tasks."lint:drift-docs:rebaseline"]` block
- [ ] 3.3 Add `[tasks."lint:drift-docs:rebaseline:dry-run"]` block

## 4. Spec delta to `retrospective-cleanup`

- [ ] 4.1 Add an ADDED Requirement to
      `openspec/changes/2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1/specs/retrospective-cleanup/spec.md`
- [ ] 4.2 Add 2 Scenarios (WHEN the drift gate fails / THEN the
      rebaseline task fixes it; WHEN the rebaseline task is
      run with --apply / THEN the AGENTS.md count claims
      match ground truth)

## 5. Validation

- [ ] 5.1 `mise run lint:drift-docs` — 0 violations
- [ ] 5.2 `grep -E "153 skills|123 skills|12 Agents|MCPs: 12"`
      on INDEXING_AND_COGNITION.md — 0 matches
- [ ] 5.3 `mise run lint:drift-docs:rebaseline:dry-run` —
      "0 changes needed"
- [ ] 5.4 `openspec validate 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1 --strict`
- [ ] 5.5 `mise run lint:skills` — 61 skills pass (no regression)
- [ ] 5.6 `mise run lint:guides-yml` — all 26 guides valid
      (no regression from Change 2)

## 6. Commit + push (Landing the Plane)

- [ ] 6.1 `git status` — review
- [ ] 6.2 `git add openspec/changes/2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1/ AGENTS.md agents/tuatha/AGENTS.md bonneagar/AGENTS.md notebooks/AGENTS.md .agents/skills/INDEXING_AND_COGNITION.md scripts/rebaseline_drift_docs.py mise.toml`
- [ ] 6.3 `git commit -m "chore(docs): rebaseline count drift in 4 AGENTS.md + INDEXING_AND_COGNITION cleanup + lint:drift-docs:rebaseline gate"`
- [ ] 6.4 `git push`
- [ ] 6.5 `git status` — must show "up to date with origin"