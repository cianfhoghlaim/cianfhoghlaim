# `docs/openspec/` — Historical Research Material

This directory contains the **historical research material** that informed the design of the cianfhoghlaim platform. It is **not** part of the active spec-driven development workflow. Active workflow lives in [`openspec/`](../openspec/).

## Contents

| File | Lines | What it is |
|:--|--:|:--|
| `openspec-comprehensive-research.md` | 558 | Reference material on the OpenSpec tool itself — workflow, spec delta format, capability organisation. |
| `opencode-comprehensive-research.md` | 1,897 | Reference material on the OpenCode CLI — features, agent modes, TUI, IDE integration, MCP integration. |
| `opencode-design-patterns-ontology.md` | 425 | OpenCode design patterns + programming patterns + conceptual ontology. |

## Why this is separate from `openspec/`

The `openspec/` directory is the **canonical change-management surface** for the active project. The 3 files in this directory are **historical research** — they were studied when the project was first set up and are referenced occasionally but are not part of any active spec, change, or task.

If you are looking for:
- How to write a new capability spec → [`openspec/AGENTS.md`](../openspec/AGENTS.md)
- The list of active capability specs → [`openspec/specs/`](../openspec/specs/)
- The list of in-flight changes → [`openspec/changes/`](../openspec/changes/)
- Project conventions and constraints → [`openspec/project.md`](../openspec/project.md)

## Should these files be updated?

Generally **no**. They are point-in-time research artifacts. If a newer version of OpenCode or OpenSpec is released, the **active specs** (not these research files) are what gets updated.

If you discover an inaccuracy in one of the research files, open an issue rather than editing the file directly. Outdated research is a documentation smell; replacing it with a newer version of the same research is a different exercise.

## Cross-references

- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — how to use OpenSpec for changes
- [`../openspec/project.md`](../openspec/project.md) — project conventions
- [`../AGENTS.md`](../../AGENTS.md) — root agent instructions
- [`../.agents/skills/stack-ops/`](../../.agents/skills/stack-ops/SKILL.md) — the operational skill for adding/fixing Docker Compose stacks
