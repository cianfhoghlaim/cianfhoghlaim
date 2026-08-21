# 2026-08-22 — OPSX schema migration plan (documentation only)

## Why

The previous refactor (`2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1`)
explicitly deferred the OPSX schema migration because it would require
re-archiving 78 pending + 96 archived changes — too risky for one
change. We also kept the `openspec-schema-stability` requirement
(canonic) which says we stay on the legacy spec-driven schema.

After the upstream research for this round (`2026-08-22-openspec-upgrade-and-mise-bindings-v1`),
openspec 1.10.0 added the **OPSX schema** as a viable alternative
(separate from the spec-driven schema), with:
- Custom schemas via `openspec schema init my-workflow` / `openspec schema fork`
- **Stores Beta** (separates specs/changes/planning context)
- **`/opsx:explore`** (brownfield adoption mode)
- **DAG-based artifact dependencies** (vs. our current monolithic proposal+specs+design+tasks)

The user has chosen "Migration plan only" — this change is **documentation only** to lay out the path forward, with **no actual migration** of existing changes. A future change can implement the migration incrementally.

## What changes

This change contains **only documentation**:

1. **`proposal.md`** — the OPSX migration strategy:
   - Why OPSX matters (3 substantive benefits over spec-driven)
   - The 5 candidate changes to migrate as pilots (3 are recommended)
   - The migration order + rollback plan
   - The risks + mitigations

2. **`tasks.md`** — the meta-tasks for the actual migration (in follow-up changes)

3. **`specs/dev-tooling-surfaces/spec.md`** — a MODIFIED requirement clarifying that the legacy spec-driven schema is now time-boxed (not permanent)

## NO implementation

This change **does not**:
- Migrate any existing change to OPSX
- Adopt OPSX as the active schema
- Modify any openspec/specs/*/spec.md files
- Add any mise tasks

Those actions are deferred to follow-up changes that will be created AFTER this plan is reviewed.

## Dependencies

- **Blocked by:** none (this is a planning change)
- **Blocked by (soft):** `2026-08-22-openspec-upgrade-and-mise-bindings-v1` (the openspec 1.10 upgrade enables OPSX)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `proposal.md` exists and contains: motivation, 3+ candidate pilots, migration order, rollback plan
2. `tasks.md` exists and lists the meta-tasks for the actual migration
3. `specs/dev-tooling-surfaces/spec.md` has 1 MODIFIED requirement adding the time-box language
4. `openspec validate ... --strict` exits 0
5. `openspec validate --all --strict` exits 0

## Out of scope (these go in follow-up changes)

- Migrating any actual change to OPSX
- Activating Stores Beta
- Custom schema authoring (`openspec schema init`)
- The /opsx:* slash commands (would require `.opencode/commands/*.md`)

## Rollback plan

Single commit. Revert via `git revert` if the plan is rejected. The plan is purely documentation; no code changes to undo.
