# Change: 2026-10-30-saga-closure-and-baml-repair-v1

> **Status (added 2026-10-30, per the platform-reset saga closure):** This
> change is the **saga-closure + follow-on-issue-repair** change for the
> 4-umbrella 2026-10-30 platform-reset saga (`openspec/plans/2026-10-30-platform-reset-saga-v1.md`).
> All 4 umbrella PRs merged on main 2026-10-30 (#209 housekeeping + #210
> BAML repair + #211 openspec triage + #212 lakehouse bring-up). This
> change addresses the 4 follow-on issues the merge exposed:
>
> 1. Duplicate `[tasks."core:lint:skills"]` in `mise.toml` (both Umbrella 1
>    and Umbrella 4 added the same block; TOML parser rejected the file)
> 2. Bash syntax error in `scripts/lint_skills.sh` (malformed case statement
>    + off-by-one in the `--limit N` check)
> 3. Lakehouse Umbrella 3 task count discrepancy (the saga plan's 20-task
>    breakdown didn't match the actual 4-file work; reconciled to 7 done /
>    14 deferred / 21 total)
> 4. Saga-deferred STATUS.md + AGENTS.md + CHEATSHEET.md updates (the 3
>    merged umbrellas had E1/G2/F3 boxes marked DEFERRED; PRs all merged
>    so those boxes are now ticked, plus the actual STATUS.md + saga plan
>    + AGENTS.md/CHEATSHEET.md doc updates ship here)

## Why

After the 4 platform-reset PRs (#209–#212) merged to main, a quick smoke
test exposed 4 housekeeping issues:

- `mise` failed to parse `mise.toml` because of the duplicate task block,
  blocking every `mise run core:*` invocation
- `bash scripts/lint_skills.sh` failed with a bash syntax error at line 38,
  blocking the skill conformance check that Umbrella 4 just added
- The lakehouse umbrella's `tasks.md` showed 0/20 tasks even though the
  umbrella shipped 4 files + the PR merged; honest reconciliation was needed
- The 3 merged umbrellas (housekeeping, BAML repair, openspec triage) all
  had `STATUS.md update` + `skill doc reference` + `PR merge` boxes
  marked DEFERRED; those need ticking now that all PRs merged, plus the
  actual doc updates need to ship

This change is the single housekeeping change that closes all 4 issues,
ticks the deferred boxes, and ships the closure doc updates. No BAML
files are touched (a separate subagent owns BAML repair).

This is the **5th umbrella** of the
[2026-10-30 platform-reset saga](../plans/2026-10-30-platform-reset-saga-v1.md)
(not in the original saga plan; added post-merge to close the 4
follow-on issues).