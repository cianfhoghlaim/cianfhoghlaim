## Why

Four of the shared `openspec/specs/` capabilities had no
matching top-level skill:

| Spec | Spec quadrant | Has skill? |
|:--|:--|:--|
| `agent-memory-systems` | shared | NO |
| `dagger-pipelines` | shared | NO (only `dagger`) |
| `infrastructure-stacks` | shared | NO (only `stack-ops`) |
| `data-engineering-pipeline-documentation` | shared | NO |

Per the openspec workflow: every capability spec SHOULD have
either a matching `.agents/skills/<spec>/SKILL.md` or an
explicit "absorbed into <other-skill>" annotation in the
openspec `AGENTS.md`. The 4 specs above are "thin capability
pointers" (the openspec convention) — they have a 1-line
oneliner and point at the source code. Adding a thin
**router skill** for each one gives agents a single discoverable
entry point per capability.

The 4 new skills are deliberately thin (each is 50-150 lines)
and point at the existing umbrella skills. They are not full
re-implementations of the source code; they are routing tables
and decision trees.

## What changes

- 4 new router skills created at `.agents/skills/`:
  - `agent-memory-systems/SKILL.md` (Cognee + Graphiti + LanceDB
    + FalkorDB + Memgraph router)
  - `dagger-pipelines/SKILL.md` (8 callable functions + 4
    build pipelines + the Python root + TS submodule)
  - `infrastructure-stacks/SKILL.md` (6-file GOLD_STANDARD
    pattern + 3-tier host + 5-stage deploy)
  - `data-engineering-pipeline-documentation/SKILL.md` (STATUS.md
    + REFACTORING.md + per-area READMEs + 5-stage pipeline)
- 4 spec deltas added (one per spec) — each adds 1 Requirement
  to the spec pointing at the new skill

## Out of scope

- Migrating content from the source code to the skill (the
  skills are routers, not full reimplementations).
- Adding skills for the project-specific specs (oideachais-*,
  tuatha-*, croilar-*) — those already have skills.
