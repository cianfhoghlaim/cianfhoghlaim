---
name: opencode
description: OpenCode AI agent configuration for the cianfhoghlaim monorepo. Use when adding/modifying agents, writing agent prompts as markdown files in .opencode/agents/, migrating from the deprecated `tools` field to the current `permission` field, configuring MCP servers, wiring AGENTS.md + guides.yml into the instructions array, or setting up subagent dispatch with permission.task gating. Covers opencode 1.18+ schema (primary/subagent modes, watcher.ignore, compaction, disabled_providers).
when_to_use: "opencode agent author | MCP server configurer | permissions designer | agent dispatcher"
---

# OpenCode — agent + MCP configuration

[OpenCode](https://opencode.ai/) is the AI coding agent that drives this
repo. The config at `opencode.json` + `.opencode/agents/*.md` defines
the 4 primary agents (build, plan, research, orchestrator) + 9
domain-specific subagents. Local install: **`opencode 1.18.16`**.

> **API notice (2026-08-19):** The **`tools` field is deprecated**.
> Use the **`permission` field** for all access control. The
> `permission.task` sub-field controls which subagents each agent can
> invoke via the Task tool. See `## Permission API migration` below.

## Quick start — the 13 agents

| Agent | Mode | Location | Purpose |
|:--|:--|:--|:--|
| `build` | primary | `opencode.json` | Default — full read/write/exec; M3 direct coding plan |
| `plan` | primary | `opencode.json` | Read-only — design specs + proposals; denies edit |
| `research` | primary | `opencode.json` | Browser-driven investigation via firecrawl + browserbase |
| `orchestrator` | primary (hidden) | `opencode.json` | E2E BIEP + Túatha + Croílár pipeline orchestration |
| `data-platform` | subagent | `.opencode/agents/data-platform.md` | DLT + Dagster + BAML + DuckLake + MotherDuck + marimo |
| `infrastructure` | subagent | `.opencode/agents/infrastructure.md` | Komodo + Pangolin + Locket + Infisical + Pulumi + Dagger |
| `agent-platform` | subagent | `.opencode/agents/agent-platform.md` | 12-agent fleet + OCR models + Celtic languages + Langfuse |
| `frontend-apps` | subagent | `.opencode/agents/frontend-apps.md` | TanStack Start + Convex + Hono + CopilotKit + Babylon.js |
| `notebooks` | subagent | `.opencode/agents/notebooks.md` | marimo notebook authoring + debugging |
| `baml` | subagent | `.opencode/agents/baml.md` | BAML schema authoring (320 .baml files) |
| `dagster` | subagent | `.opencode/agents/dagster.md` | Dagster asset + component + job authoring |
| `mise` | subagent | `.opencode/agents/mise.md` | mise.toml task authoring |
| `proposal-author` | subagent | `.opencode/agents/proposal-author.md` | OpenSpec change author |

Plus the hidden internal ones (`dev-env-demo`, `deep-cuts`) used only
via programmatic invocation.

## Config file schema (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "snapshot": false,
  "subagent_depth": 2,
  "default_agent": "build",
  "watcher": {
    "ignore": ["node_modules/**", ".venv/**", "stedding/**"]
  },
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 16000
  },
  "instructions": [
    "AGENTS.md",
    "openspec/AGENTS.md",
    ".agents/skills/INDEXING_AND_COGNITION.md",
    ".cocoindex_code/guides.yml"
  ],
  "provider": {
    "qwen": {
      "name": "Qwen Token Plan",
      "api": "openai",
      "options": {
        "apiKey": "{env:DASHSCOPE_API_KEY}",
        "baseURL": "{env:DASHSCOPE_BASE_URL}"
      },
      "models": { ... }
    }
  },
  "mcp": {
    "firecrawl": {
      "type": "local",
      "command": ["bunx", "-y", "firecrawl-mcp"],
      "environment": { "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}" },
      "enabled": true
    }
  },
  "agent": {
    "build": {
      "prompt": "{file:./.opencode/agents/build.md}",
      "model": "minimax-coding-plan/MiniMax-M3"
    }
  }
}
```

## Precedence order (highest wins)

1. Remote config (`.well-known/opencode`)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var)
4. **Project config** (`opencode.json`) ← this repo
5. `.opencode/` directory (agents, commands, plugins)
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed config (`/Library/Application Support/opencode/` on macOS)
8. macOS managed preferences (`.mobileconfig` via MDM)

## Agent modes

| Mode | Use | Tab-cyclable | @mention |
|:--|:--|:--|:--|
| `primary` | Main conversation agents (build, plan, research) | yes | no |
| `subagent` | Specialized helpers invoked via Task tool | no | yes |
| `all` | Default if mode not specified | both | both |

For internal-only subagents (orchestrator, dev-env-demo, deep-cuts),
set `hidden: true` to remove from the `@` autocomplete menu.

## Permission API (current, replaces deprecated `tools`)

```json
{
  "agent": {
    "plan": {
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git status": "allow",
          "git log*": "allow",
          "git diff": "allow",
          "openspec *": "allow",
          "mise tasks": "allow",
          "mise run lint*": "allow"
        },
        "webfetch": "ask",
        "external_directory": "deny",
        "task": {
          "*": "deny",
          "research": "allow",
          "deep-cuts": "allow"
        }
      }
    }
  }
}
```

**Permission keys** (per opencode 1.18+):

| Key | Tools it gates |
|:--|:--|
| `read` | `read` |
| `edit` | `write`, `edit`, `apply_patch` |
| `glob` | `glob` |
| `grep` | `grep` |
| `list` | `list` |
| `bash` | `bash` (with glob/pattern → action support) |
| `task` | `task` (with glob/pattern → action for subagent invocation) |
| `external_directory` | Any tool that reads/writes outside the project worktree |
| `todowrite` | `todowrite`, `todoread` |
| `webfetch` | `webfetch` |
| `websearch` | `websearch` |
| `lsp` | `lsp` |
| `skill` | `skill` |
| `question` | `question` |
| `doom_loop` | Recovery prompts when an agent appears stuck |

Values: `"allow"` | `"ask"` | `"deny"` | `{}` for fine-grained per-pattern.

### Migration from `tools` to `permission`

| Old (`tools`) | New (`permission`) |
|:--|:--|
| `tools: { write: true, edit: true }` | `permission: { "*": "allow" }` |
| `tools: { write: false, edit: false }` | `permission: { edit: "deny" }` |
| `tools: { bash: false }` | `permission: { bash: "deny" }` |
| `tools: { mymcp_*: false }` | `permission: { "mcp__mymcp__*": "deny" }` |

## Markdown agent files (`.opencode/agents/<name>.md`)

```markdown
---
description: Functional subagent for the data plane (DLT + Dagster + BAML + DuckLake + MotherDuck + marimo notebooks). Routes to dlt_sources/, orchestration/, baml_src/, notebooks/. Owns the 5-layer Dagster defs/ tree, the 928 DLT sources, the 320 .baml files, and the 109 marimo notebooks.
mode: subagent
model: minimax-coding-plan/MiniMax-M3
temperature: 0.1
permission:
  edit: allow
  bash: { "*": "ask", "uv run *": "allow", "mise run *": "allow", "git status": "allow", "git diff": "allow" }
  webfetch: ask
  external_directory: deny
  task: { "research": "allow", "deep-cuts": "ask" }
skill_filter: [dlt, dagster, baml, motherduck, duckdb, ducklake, cocoindex, lancedb, cognee, ibis, marimo, dlthub, langfuse, mlflow, apple-photos, centralized-registry]
color: "#3a5f3a"
hidden: false
---

You are the data-platform functional subagent...

# Direct references (mirrors guides.yml)
- dlt_sources/AGENTS.md
- baml_src/AGENTS.md
- orchestration/AGENTS.md
- notebooks/_shared/db.py
- .cocoindex_code/guides.yml#data-platform
- .agents/skills/dlt/SKILL.md
...
```

The frontmatter fields: `description` (required), `mode`, `model`,
`temperature`, `permission`, `tools` (deprecated), `skill_filter`,
`color`, `top_p`, `steps`, `hidden`, `disable`.

## Variables in config files

```json
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": { "apiKey": "{env:ANTHROPIC_API_KEY}" }
    }
  },
  "instructions": ["{file:./custom-instructions.md}"],
  "agent": {
    "review": { "prompt": "{file:./prompts/review.txt}" }
  }
}
```

| Syntax | Meaning |
|:--|:--|
| `{env:VAR}` | Substitute environment variable (empty if unset) |
| `{file:path}` | Substitute file contents (relative or absolute) |

## Providers + allowlists

```json
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}",
        "timeout": 600000,
        "chunkTimeout": 30000,
        "setCacheKey": true
      },
      "models": { ... }
    }
  },
  "disabled_providers": ["gemini"],
  "enabled_providers": ["anthropic", "openai"]
}
```

If a provider appears in both lists, `disabled_providers` wins.

## MCP servers

```json
{
  "mcp": {
    "firecrawl": {
      "type": "local",
      "command": ["bunx", "-y", "firecrawl-mcp"],
      "environment": {
        "FIRECRAWL_API_KEY": "{env:FIRECRAWL_API_KEY}"
      },
      "enabled": true
    },
    "browserbase": {
      "type": "remote",
      "url": "https://mcp.browserbase.com/mcp",
      "headers": { "Authorization": "Bearer {env:BROWSERBASE_API_KEY}" },
      "enabled": false,
      "timeout": 60000
    }
  }
}
```

13 MCP servers are registered in this repo (3 enabled by default;
10 disabled — toggle via `enabled: true/false`).

## Custom commands (`.opencode/commands/*.md`)

```markdown
---
description: Run tests with coverage
agent: build
model: minimax-coding-plan/MiniMax-M3
subtask: true
---

Run the full test suite with coverage report.

Test results:
!`bun run test`

Based on these results, suggest fixes.
```

Then `/test` in the TUI invokes it.

Special placeholders: `$ARGUMENTS`, `$1`-`$9`, `` !`command` `` (shell
output), `@path/to/file` (file inclusion).

## Plugins

`.opencode/plugins/<name>.ts` extends OpenCode with custom tools +
hooks + integrations. Also loadable from npm:

```json
{
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

## Routing: when to use what

| Question | Tool |
|:--|:--|
| "Where do I add a new domain agent?" | `.opencode/agents/<name>.md` |
| "How do I change agent permissions?" | `permission` field in markdown frontmatter |
| "What agents are available?" | Tab key in TUI, or `opencode agent list` |
| "How do I invoke a subagent manually?" | `@<agent-name>` in the message |
| "How do I disable a noisy MCP server?" | `mcp.<name>.enabled = false` |

## Anti-patterns

- **NEVER** use the deprecated `tools` field — use `permission`.
- **NEVER** inline a >2 KB prompt in `opencode.json` — use
  `{file:./.opencode/agents/<name>.md}`.
- **NEVER** leave a subagent un-hidden if it's internal-only (orchestrator,
  dev-env-demo, deep-cuts).
- **NEVER** grant `external_directory: allow` to a domain subagent —
  it can read/write outside the project worktree.
- **NEVER** set `subagent_depth` > 2 — recursion gets expensive fast.

## Skill pointers

- `opencode.json` — canonical config (provider + MCP + 4 primary agents)
- `.opencode/agents/<name>.md` — domain-specific subagents
- `.opencode/commands/<name>.md` — slash commands (TUI)
- `.opencode/plugins/<name>.ts` — custom tool extensions
- `.cocoindex_code/guides.yml#opencode-agent-search` — CCC concept guide
- `.cocoindex_code/guides.yml#opencode-agent-search` — agent search

## References

- opencode docs: <https://opencode.ai/docs/>
- Config: <https://opencode.ai/docs/config>
- Agents: <https://opencode.ai/docs/agents>
- Commands: <https://opencode.ai/docs/commands>
- Permissions: <https://opencode.ai/docs/permissions>
- This skill: `.agents/skills/opencode/SKILL.md`
