# 2026-08-22 — openspec new subcommands (schemas, feedback, instructions, templates)

## Why

We use 6 of openspec's 29 subcommands. The new openspec 1.4+ subcommands we ignore are exactly the ones that would most help our workflow:

- **`openspec schemas`** — lists available workflow schemas (spec-driven, opsx, tdd). Critical for evaluating the OPSX migration that was explicitly deferred from the previous refactor. Per the upstream docs: "List available workflow schemas with descriptions" + `--json` for programmatic use.
- **`openspec feedback`** — submit feedback to OpenSpec maintainers (GitHub Issue creation under the hood). We have no formal feedback channel today.
- **`openspec instructions`** — emit enriched templates for an artifact (proposal/tasks/spec). The static `proposal.md` example in our docs is fine, but `instructions` provides richer templates dynamically.
- **`openspec templates`** — show resolved template paths for all artifacts in a schema. Useful for debugging the OPSX migration.

These 4 subcommands are also the ones that the new `/opsx:onboard` and `/opsx:explore` slash commands rely on (per the upstream PRs #574 and #516).

## What changes

Add 4 new tasks to the `openspec` namespace in `mise.toml`:
1. `openspec:schemas` — list available schemas (with `--json` for tools)
2. `openspec:feedback` — submit feedback to OpenSpec maintainers
3. `openspec:instructions` — emit enriched artifact templates
4. `openspec:templates` — show resolved template paths for a schema

Update `.agents/skills/openspec/SKILL.md` to document all 4 (the skill currently only documents 8 of the 29 subcommands).

Update `.opencode/agents/proposal-author.md` to reference the new subcommands.

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-domain-driven-mise-task-catalog-v1` (extends the namespace)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `mise run openspec:schemas` lists available schemas (spec-driven + opsx + tdd)
2. `mise run openspec:schemas --json` emits JSON
3. `mise run openspec:feedback --help` shows usage
4. `mise run openspec:instructions proposal` emits enriched template
5. `mise run openspec:templates` shows resolved template paths
6. `.agents/skills/openspec/SKILL.md` documents all 4 new subcommands
7. `.opencode/agents/proposal-author.md` references all 4 new subcommands
8. `openspec validate --all --strict` exits 0

## Out of scope

- Migrating to the OPSX schema (deferred — would require re-archiving 78 changes)
- Updating openspec to v1.5 (the new schemas/feedback subcommands are available in 1.4)
- Adding the `/opsx:*` slash commands to `.opencode/commands/` (deferred to a follow-up)

## Rollback plan

Single commit. Revert via `git revert` if any task fails. The tasks are additive.
