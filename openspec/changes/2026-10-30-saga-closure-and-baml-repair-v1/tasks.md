# Tasks: 2026-10-30-saga-closure-and-baml-repair-v1

> The 5th umbrella of the 2026-10-30 platform-reset saga. Closes the
> 4 follow-on issues the 4 umbrella PRs (#209–#212) merged on main
> 2026-10-30.

## 1. Group A — TOML repair (1 task)

- [x] **A1** Remove the duplicate `[tasks."core:lint:skills"]` block from `mise.toml` (both Umbrella 1 + Umbrella 4 added the same block; TOML parser rejected the file). Keep the Umbrella 4 canonical version (the one with `run = "bash scripts/lint_skills.sh"`)

## 2. Group B — Bash lint repair (2 tasks)

- [x] **B1** Fix the bash syntax error in `scripts/lint_skills.sh` (the case statement at line 30-40 was malformed — `--limit)` was trying to match the literal string `"--limit)"`, not the value of `$1`; rewrote as a `while [ $# -gt 0 ]; do case "$1" in ... esac; shift || true; done` loop)
- [x] **B2** Fix the off-by-one in the `--limit N` check (the count was incremented before the limit comparison, so `--limit 3` showed 4 skills; the fix decrements before the `break`)

## 3. Group C — Lakehouse task reconciliation (1 task)

- [x] **C1** Rewrite `openspec/changes/2026-10-30-lakehouse-bridge-bring-up-v1/tasks.md` to the honest breakdown: 7 done (D1, D2, D3, E1, E2, E3, F2), 14 deferred (all of Groups A/B/C + F1 + F3), 21 total

## 4. Group D — Saga-deferred task tickings (3 tasks)

- [x] **D1** Tick the 3 PR-merge boxes (housekeeping D2 / baml-repair F3 / openspec-triage E3) — all PRs merged on main
- [x] **D2** Tick the STATUS.md-update box (openspec-triage E1) — this change ships the STATUS.md update
- [x] **D3** Tick the skill-doc-reference boxes (baml-repair G2 / openspec-triage F2) — this change ships the AGENTS.md + CHEATSHEET.md updates

## 5. Group E — Doc updates (4 tasks)

- [x] **E1** `openspec/plans/STATUS.md` — mark the 4 umbrellas as ✓ MERGED with PR numbers + add the saga-closure row + add the "Status: completed sagas" section
- [x] **E2** `openspec/plans/2026-10-30-platform-reset-saga-v1.md` — add the ✓ CLOSED Status line + the "What was deferred" section listing the 4 follow-on issues
- [x] **E3** `AGENTS.md` — add the "Top mise tasks (added 2026-10-30 — platform-reset saga #209–#212)" section listing the 8 new tasks + the 4 marimo dashboards that consume them
- [x] **E4** `CHEATSHEET.md` — flip the saga quick path from "(proposed)" to closed + add the 6 new task rows to the "Top 10 priority mise tasks" table

## 6. Group F — Spec + commit (2 tasks)

- [x] **F1** `openspec validate 2026-10-30-saga-closure-and-baml-repair-v1 --strict` passes
- [ ] **F2** PR merged (operator-gated; do not auto-push)

## 7. Group H — Validation (5 tasks)

- [x] **H1** `.venv/bin/python3 -c "import tomllib; tomllib.loads(open('mise.toml').read())"` exits 0
- [x] **H2** `bash -n scripts/lint_skills.sh` exits 0
- [x] **H3** `bash scripts/lint_skills.sh --limit 3` shows 3 skills with 0 failures
- [x] **H4** `ruff check` clean on the modified Python files (n/a — no Python files modified)
- [x] **H5** `openspec validate 2026-10-30-saga-closure-and-baml-repair-v1 --strict` passes

## Summary

- **Done: 17** (A1, B1, B2, C1, D1, D2, D3, E1, E2, E3, E4, F1, H1, H2, H3, H4, H5)
- **Deferred: 1** (F2 — operator-gated PR merge)
- **Total: 18**

## Files touched

1. `mise.toml` — remove duplicate `[tasks."core:lint:skills"]` (Issue 1)
2. `scripts/lint_skills.sh` — fix the bash syntax error + off-by-one (Issue 2)
3. `openspec/changes/2026-10-30-lakehouse-bridge-bring-up-v1/tasks.md` — reconcile to 7/14/21 (Issue 3)
4. `openspec/changes/2026-10-30-housekeeping-sprawl-cleanup-v1/tasks.md` — tick D2 PR-merge (Issue 4)
5. `openspec/changes/2026-10-30-biep-tertiary-baml-repair-v1/tasks.md` — tick F3 PR-merge + G2 skill-doc (Issue 4)
6. `openspec/changes/2026-10-30-openspec-backlog-triage-v1/tasks.md` — tick E1 STATUS + E3 PR-merge + F2 markdown-ref (Issue 4)
7. `openspec/plans/STATUS.md` — saga closure + completed sagas section (Issue 4)
8. `openspec/plans/2026-10-30-platform-reset-saga-v1.md` — ✓ CLOSED Status + What was deferred section (Issue 4)
9. `AGENTS.md` — Top mise tasks section (Issue 4)
10. `CHEATSHEET.md` — saga-closed entry + 6 new task rows (Issue 4)