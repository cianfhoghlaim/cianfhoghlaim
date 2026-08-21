---
name: openspec
description: Spec-driven change management with OpenSpec 1.4 (Fission AI). Use when writing proposal.md/tasks.md/spec deltas, validating changes with --strict, archiving completed changes, navigating the 78 pending + 96 archived changes, or running the view/status/instructions subcommands. Covers both the legacy spec-driven schema (proposal + tasks + spec deltas) and the experimental OPSX schema (YAML+Markdown templates + DAG dependencies).
when_to_use: "proposal author | validator | archivist | spec author | openspec CLI user"
---

# OpenSpec — spec-driven change management

[OpenSpec](https://github.com/Fission-AI/OpenSpec) by Fission AI is the
canonical change-management surface for the cianfhoghlaim monorepo.
Every non-trivial change — refactor, capability, infrastructure stack,
skill consolidation — lives in `openspec/changes/<id>/` as a 3-artifact
bundle (`proposal.md` + `tasks.md` + `spec deltas`) before any code is
written. Local install: **`@fission-ai/openspec@1.4.1`** (per
`openspec --version`).

> **Schema notice (2026-08-19):** This repo uses the **legacy
> `spec-driven` schema** (proposal + tasks + spec deltas). The new
> `OPSX` schema (`YAML` templates + DAG dependencies + status command)
> is shipped in OpenSpec 1.4 but is **not adopted** here — migration
> would require re-archiving all 78 pending changes. See
> `openspec/AGENTS.md` § OPSX vs legacy for the full reasoning.

## Quick start — the 4 priority commands

```bash
openspec list --specs                    # list all 97 capability specs
openspec list                            # list all 78 pending changes
openspec view                            # interactive dashboard (NEW 1.4)
openspec status <change-id>              # artifact completion check (NEW 1.4)
openspec show <change-id|spec-id>        # formatted view (NEW 1.4)
openspec validate <change-id> --strict   # MUST pass before commit
openspec validate --all --strict         # validate everything (CI gate)
openspec archive <change-id> --yes       # after deploy
openspec schemas                         # NEW 1.4: list available workflow schemas (spec-driven, opsx, tdd)
openspec schemas --json                  # NEW 1.4: same as above, JSON output
openspec feedback <message>              # NEW 1.4: submit feedback to OpenSpec maintainers
openspec instructions --change <id>     # NEW 1.4: emit enriched template for an artifact
openspec templates                       # NEW 1.4: show resolved template paths for a schema
```

The new 1.4 subcommands (`view`, `status`, `show`, `instructions`,
`schemas`) work with the legacy schema without migration.

## The 8 standard subcommands

| Command | When to use |
|:--|:--|
| `openspec init` | One-time setup in a new repo (already done for cianfhoghlaim) |
| `openspec list [--specs]` | Discover what's pending (changes) or canonical (specs) |
| `openspec view` | Interactive dashboard; `q` to quit |
| `openspec show <id>` | Render a single change or spec to terminal |
| `openspec status <change-id>` | Per-artifact completion (proposal / tasks / specs / design) |
| `openspec validate <id> --strict` | The CI gate — every change MUST pass before commit |
| `openspec archive <id> --yes` | After deploy — merges deltas into canonical specs |
| `openspec instructions <artifact>` | Emit the enriched template for one artifact (NEW 1.4) |

Plus the experimental:

| Command | When to use |
|:--|:--|
| `openspec schemas` | List available workflow schemas (legacy `spec-driven`, experimental `opsx`, custom forks) |
| `openspec schema which --all` | Show all schemas with their resolution sources |
| `openspec schema fork <src> <new>` | Create a custom schema fork |
| `openspec change` | Manage change proposals (interactive) |
| `openspec spec` | Manage and view specs (interactive) |
| `openspec config` | View/modify global OpenSpec configuration |
| `openspec workspace` | Set up coordination workspaces |
| `openspec feedback <msg>` | Submit feedback to Fission AI |

## Spec delta format (legacy schema — REQUIRED)

```markdown
## ADDED Requirements
### Requirement: New Feature Name
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result
- **AND** additional expectation

## MODIFIED Requirements
### Requirement: Existing Feature Name
[Complete modified requirement with all scenarios]

## REMOVED Requirements
### Requirement: Old Feature Name
**Reason**: [Why removing]
**Migration**: [How to handle]
```

**Hard rules** (enforced by `openspec validate --strict`):

1. **SHALL/MUST** language in every Requirement body (not just headers).
2. Every Requirement MUST have **≥1 Scenario** with WHEN/THEN/AND blocks.
3. ADDED / MODIFIED / REMOVED markers are required (the deltas vs the
   canonical `openspec/specs/<capability>/spec.md`).
4. No editing of `openspec/specs/<capability>/spec.md` directly — only
   the deltas under `openspec/changes/<id>/specs/<capability>/spec.md`.

## Per-spec AGENTS.md convention (NEW 2026-07-29)

Per the `repo-hygiene-agent-routing` spec, every
`openspec/specs/<name>/` directory ships with a sibling `AGENTS.md`
file (≤30 lines) following the canonical 6-section outline (routing
sentence, quick start, key sources, adjacent specs, DO NOT, skill
pointers). Regenerate via:

```bash
mise run sync:spec-agents
```

The anti-drift contract (`centralize-cross-cutting-docs` spec) enforces
this via `mise run lint:drift-docs`.

## Cross-repo sync convention

For openspec changes that touch >1 repo (cianfhoghlaim + bonneagar +
leabharlann), include `cross-repo-sync.md` at
`openspec/changes/<id>/cross-repo-sync.md` listing the commit plan +
branch + push target for each repo. Order: **bonneagar first, then
cianfhoghlaim** (IaC tests are a prerequisite for archive).

## Dependencies field convention (NEW 2026-07-29)

Every `proposal.md` SHALL include a `## Dependencies` section:

```markdown
## Dependencies

`Blocked by: <change-id>` (topo ordering)
`Blocked by (soft): <change-id>` (extends but doesn't block)
`Affected repos: cianfhoghlaim, bonneagar, leabharlann`
```

The change CANNOT archive until blockers archive. Soft blockers
declare an informational dependency.

## Routing: when to use what

| Question | Tool |
|:--|:--|
| "What changes are pending?" | `openspec list` |
| "What does this change look like?" | `openspec show <id>` |
| "Is the change ready to archive?" | `openspec status <id>` |
| "Is the change valid?" | `openspec validate <id> --strict` |
| "What specs exist?" | `openspec list --specs` |
| "Where in the code is this implemented?" | `bun run ccc:search "X"` |
| "What does upstream say about this spec pattern?" | `firecrawl_search "OpenSpec schema delta format"` |

## Anti-patterns

- **NEVER skip `openspec validate --strict`** — it blocks merge.
- **NEVER edit `openspec/specs/<capability>/spec.md` directly** — only
  deltas under `openspec/changes/<id>/specs/` are editable.
- **NEVER use "should" or "may"** in Requirement bodies — SHALL/MUST only.
- **NEVER leave Scenarios empty** — at minimum a "WHEN X THEN Y AND Z"
  triple.
- **NEVER migrate to OPSX schema without an openspec change** — the
  legacy schema is the canonical workflow here.

## Skill pointers

- `openspec/AGENTS.md` — root routing + priority commands
- `openspec/project.md` — the capability list (8 quadrants)
- `.opencode/agents/proposal-author.md` — the openspec-aware subagent
- `.cocoindex_code/guides.yml#openspec-change-search` — CCC concept guide
- `.cocoindex_code/guides.yml#openspec archive search` — prior-art
  search across pending + archived

## New in openspec 1.10 (2026-08-22)

The latest openspec is **1.10.0** (we run 1.4.1). Upgrade via:

```bash
mise run openspec:upgrade  # prints the install command
bun add -g @fission-ai/openspec@latest
```

The 1.10 release line adds:

- **Stores Beta** — separates specs, changes, and planning context from a single repository (multi-repo support)
- **`/opsx:explore`** — brownfield adoption mode (think before you commit)
- **`/opsx:onboard`** — first-time walkthrough skill
- **Improved change inference in `opsx apply`** — auto-detects target change from context
- **"Prevent implementation during explore mode" guardrail** — keeps focus on thinking/discovery

The spec-driven schema (our current workflow) is **stable** and
backward-compatible. Upgrading to 1.10 should not break our existing
78 pending + 96 archived changes.

## References

- OpenSpec docs: <https://github.com/Fission-AI/OpenSpec>
- Spec-Driven Development intro: <https://openspec.pro/spec-driven-development/>
- This skill: `.agents/skills/openspec/SKILL.md`
