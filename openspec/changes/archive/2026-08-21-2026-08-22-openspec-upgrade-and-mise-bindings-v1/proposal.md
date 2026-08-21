# 2026-08-22 — openspec 1.10.0 upgrade + mise bindings

## Why

Latest openspec is 1.10.0 (we run 1.4.1 — that's 5.9 minor versions of
accumulated changes). The 1.10 release line adds:

- **Stores Beta** — separates specs, changes, and planning context from a single repository
- **/opsx:explore** — brownfield adoption mode (think before you commit)
- **/opsx:onboard** — first-time walkthrough skill
- **Improved change inference in `opsx apply`** — auto-detects target change from context
- **"Prevent implementation during explore mode" guardrail** — keeps the focus on thinking/discovery
- **More tool integrations and compatibility fixes** (per the 1.10 changelog)

The spec-driven schema (our current workflow) is **stable** and
backward-compatible. Upgrading to 1.10.0 should not break our existing
78 pending + 96 archived changes.

## What changes

1. **Upgrade the global openspec install** — `bun add -g @fission-ai/openspec@1.10.0` (the install is done by the user; the change documents the version)

2. **Add 1 new task in the `openspec` namespace**:
   - `openspec:upgrade` (alias `openspec:version:upgrade`) — `bun add -g @fission-ai/openspec@latest` (one-command upgrade)

3. **Update `.agents/skills/openspec/SKILL.md`** — add a new section on openspec 1.10 features (Stores Beta, OPSX, the new subcommands)

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-22-openspec-schemas-feedback-instructions-v1` (the previous openspec refactor)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `openspec --version` shows 1.10.0 (after running `bun add -g @fission-ai/openspec@1.10.0`)
2. `mise run openspec:upgrade` exits 0
3. `openspec schemas` lists the new schemas (spec-driven + opsx + workspace-planning)
4. `.agents/skills/openspec/SKILL.md` documents the 1.10 features
5. `openspec validate --all --strict` exits 0

## Out of scope

- Migrating to the OPSX schema (separate change: `opsx-schema-migration-plan-v1`)
- Activating Stores Beta (requires config + repo restructuring)
- The /opsx:* slash commands (would require `.opencode/commands/*.md`)

## Rollback plan

Single commit. To rollback the openspec upgrade, run `bun add -g @fission-ai/openspec@1.4.1`. The mise task and skill updates are also reversible.
