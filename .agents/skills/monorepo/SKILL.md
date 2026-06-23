---
name: monorepo
description: Polyglot monorepo (bun + uv + turbo) for the Cianfhoghlaim platform — mise.toml polyglot toolchain, turbo.json pipeline definition, Inner/Outer loop (mise = inner, Dagger = outer), Dagger + Infisical secret pattern, "Astral Stack" performance rationale. Use when adding a workspace member, running tasks across the monorepo, debugging turbo cache misses, or wiring Dagger.
---

# Monorepo — bun + uv + turbo

## When to use this skill

Use when you need to:

- "Add a new workspace member (TypeScript or Python)"
- "Run a task across the whole monorepo"
- "Debug why turbo is not caching"
- "Wire a Dagger call for CI"
- "Understand the Inner/Outer loop pattern"
- "Choose the right tool (bun vs uv) for a new sub-project"

## Overview

The Cianfhoghlaim monorepo is **polyglot**: TypeScript graph
managed by `bun` + `turbo`, Python graph managed by `uv`. The
two language graphs are orchestrated by `mise.toml` (the
polyglot toolchain) and `turbo.json` (the cross-language task
graph).

```
   ┌──────────────────────┐
   │  mise.toml           │  ← polyglot toolchain (Python 3.12,
   │  (mise = inner)     │     bun, uv, turbo, dagger, pulumi,
   │                      │     komodo, duckdb, sops, opencode)
   └────────┬─────────────┘
            │
            ▼
┌──────────────────────┐    ┌──────────────────────┐
│  TypeScript graph     │    │  Python graph         │
│  package.json         │    │  pyproject.toml       │
│  (bun workspaces)     │    │  (uv workspaces)      │
│  turbo.json pipeline  │    │  (uv sync per member) │
└────────┬─────────────┘    └────────┬─────────────┘
         │                              │
         └──────────────┬───────────────┘
                        ▼
   ┌──────────────────────────────────────┐
   │  Dagger (outer)                       │
   │  → hermetic CI parity                 │
   │  → "works on my machine" prevention   │
   └──────────────────────────────────────┘
```

## Workspace topology

### TypeScript graph (bun workspaces)

```json
// package.json
{
  "workspaces": [
    "oideachais/web",
    "oideachais/mcp/filesystem",
    "tuatha/ui"
  ]
}
```

Only 3 TypeScript workspaces (all in `oideachais/` and
`tuatha/` quadrants).

### Python graph (uv workspaces)

```toml
# pyproject.toml (root)
[tool.uv.workspace]
members = [
    "oideachais",
    "meaisinfhoghlaim",
    "tuatha",
    "códeolas",
    "infrastructure/browser",
    "oideachais/mcp/mcpo",
]
```

6 Python workspaces (one per quadrant + 2 infrastructure
modules).

## mise.toml polyglot toolchain

```toml
# mise.toml
[tools]
python = "3.12"
uv = "latest"
bun = "latest"
dagger = "latest"
pulumi = "latest"
duckdb = "latest"
sops = "latest"
opencode = "latest"

[env]
_.path = ["./scripts", "./node_modules/.bin"]
```

The polyglot toolchain is the **single source of truth** for
which Python/bun/turbo/dagger versions are used. `mise install`
hydrates everything.

## turbo.json pipeline definition

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "test": { "dependsOn": ["build"], "outputs": ["coverage/**"] },
    "lint": { "dependsOn": ["^build"] },
    "typecheck": { "dependsOn": ["^build"] },
    "format": { "outputs": [] },
    "clean": { "cache": false },
    "dagster": { "cache": false },
    "ccc:index": { "cache": false },
    "spec:validate": { "cache": false }
  }
}
```

Run `turbo run build test lint` to run across the whole
monorepo. Cache hits are automatic.

## The Inner/Outer loop

| Loop | Tool | Use case |
|:--|:--|:--|
| **Inner** | `mise run <task>` | Dev machine, fast iteration, < 1s feedback |
| **Outer** | `dagger call <module>` | CI, hermetic, content-addressable cache |

**Rule**: `mise run ci` ≡ `dagger call test`. The Dagger call
uses the same tools (via `mise.toml`) and runs the same
scripts. If they disagree, the Dagger version wins (CI is the
source of truth).

## Dagger + Infisical secret pattern

```python
# dagger/src/main.py
import dagger
from dagger import function, object_type


@function
async def test(source: dagger.Directory, env_secret: dagger.Secret) -> str:
    """Run the test suite with the Infisical secret."""
    return await (
        dag.container()
        .from_("oven/bun:1.1.0")
        .with_directory("/app", source)
        .with_secret_variable("INFISICAL_TOKEN", env_secret)
        .with_workdir("/app")
        .with_exec(["bun", "test"])
        .stdout()
    )
```

```bash
dagger call test \
  --source=. \
  --env-secret=env_secret:"INFISICAL_TOKEN"
```

## Adding a new workspace member

### TypeScript (bun)

```bash
mkdir -p oideachais/<new-member>
cd oideachais/<new-member>
bun init
# Add to root package.json:
#   "workspaces": ["oideachais/<new-member>"]
bun install
```

### Python (uv)

```bash
mkdir -p oideachais/<new-member>
cd oideachais/<new-member>
uv init --package
# Add to root pyproject.toml:
#   [tool.uv.workspace]
#   members = ["oideachais/<new-member>"]
uv sync
```

## Caching strategy

| Tool | Cache key | When invalid |
|:--|:--|:--|
| `mise` | mtime | When `mise.toml` changes |
| `turbo` | content hash | When source files change |
| `Dagger` | content-addressable | When source files change |
| `bun install` | lockfile | When `package.json` changes |
| `uv sync` | lockfile | When `pyproject.toml` changes |

**`mise.toml` invalidates everything** — it's the root of
the polyglot toolchain.

## "Astral Stack" performance rationale

The KCG monorepo uses the **Astral Stack** (uv + ruff + ty)
for Python and **Bun** for TypeScript. The Astral Stack is
10-100× faster than the legacy stack (pip + setuptools + mypy):

| Task | Legacy (pip + setuptools + mypy) | Astral Stack (uv + ruff + ty) |
|:--|:--|:--|
| `install` | 30-60s | < 1s |
| `lint` | 10-30s | < 1s |
| `typecheck` | 30-120s | 5-10s |

For the KCG monorepo with 6 Python workspaces, the cumulative
speedup is **> 1 hour saved per developer per day**.

## KCG conventions

- Every Python sub-project MUST have a `pyproject.toml` with
  `[project]` and `[tool.uv]` sections
- Every TypeScript sub-project MUST have a `package.json` with
  `name` and `version`
- The root `mise.toml` is the source of truth for tool
  versions
- The root `turbo.json` is the source of truth for task
  pipeline
- Dagger calls MUST use the same `mise.toml` tools as local
  dev (no tool drift)

## When NOT to use this skill

- The sub-project is a one-off script (use a single file, no
  workspace)
- The sub-project is in a different language (e.g. Rust — use
  Cargo workspaces)
- The sub-project has no shared code (use a separate repo)

## Related skills

- `.agents/skills/stack-ops/SKILL.md` — 6-file GOLD_STANDARD
  stack pattern
- `.agents/skills/dagger/SKILL.md` — Dagger CI/CD pipeline
- `.agents/skills/secrets-management/SKILL.md` — Infisical
  + Locket + mise
- `.agents/skills/ccc/SKILL.md` — codebase semantic search
- `.agents/skills/openspec/` — spec-driven changes

## Resources

- mise: <https://mise.jdx.dev/>
- uv: <https://github.com/astral-sh/uv>
- Turborepo: <https://turbo.build/>
- Dagger: <https://dagger.io/>
- Astral Stack: <https://astral.sh/>
- bun: <https://bun.sh/>
