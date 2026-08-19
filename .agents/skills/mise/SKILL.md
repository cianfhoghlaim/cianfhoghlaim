---
name: mise
description: mise-en-place task authoring + tool management for the cianfhoghlaim monorepo. Use when adding/modifying tasks in mise.toml, designing DAG dependencies, choosing between TOML tasks vs file tasks vs task_templates, writing usage specs for task arguments, or migrating legacy colon-form task aliases. Covers mise 2026.5+ features: task_templates, depends DAG, alias =, usage =, redactions, monorepo_root, mise-tasks/ directory with #MISE frontmatter.
when_to_use: "mise task author | DAG designer | CI gate author | shell scripter | IaC task author"
---

# mise-en-place — task authoring for the cianfhoghlaim monorepo

[mise](https://mise.jdx.dev/) is the canonical tool manager + task
runner for this repo. The `mise.toml` at the repo root defines the 9
task namespaces + ~60 file tasks in `mise-tasks/`. Local install:
**`mise 2026.5.6`** (latest 2026.8.8 available).

## Quick start — the 9 task namespaces

| Namespace | Count | Purpose |
|:--|:--|:--|
| `core` | 7 | sync, test, lint, format, doctor, reset, clean |
| `ts` | 4 | ts:install, ts:build, ts:typecheck, ts:lint |
| `schema` | 2 | schema:generate, schema:validate |
| `py` | 2 | py:typecheck, py:test |
| `lint` | 4 | lint:skills, lint:registry, lint:guides-yml, lint:drift-docs |
| `opencode` | 3 | opencode:index, opencode:search, opencode:validate |
| `baml` | 3 | baml:generate, baml:test, baml:lint |
| `openspec` | 4 | openspec:list, openspec:validate, openspec:archive, openspec:view |
| `cic` | 10 | cic:dagster:dev, cic:stack-doctor, cic:baml:*, cic:lint, cic:test, cic:typecheck, cic:ocr:registry-lint, cic:cocoindex:conformance |

**Total: ~75 TOML tasks** (down from 329 pre-refactor).

## When to use which task type

| Pattern | Format |
|:--|:--|
| Single one-liner (e.g. `mise run sync`) | TOML `[tasks.sync]` block |
| Multi-line script with comments + linting | `mise-tasks/<name>` shell file with `#MISE` frontmatter |
| Repeating per-instance pattern (OCR models, agent extractors, BIEP milestones) | `[task_templates."<prefix>"]` block |
| Remote script (build.sh from a repo) | TOML `file = "https://example.com/build.sh"` |

**Heuristic:** if the script is >5 lines OR repeats >3 times, use a
file task or template. Single-line wrappers stay in TOML.

## TOML task anatomy

```toml
[tasks.build]
description = "Build the CLI"           # shown in `mise tasks` + `mise run`
alias = "b"                              # `mise run b` works too
depends = ["lint", "test"]               # DAG construction
run = "cargo build"                      # single command OR
run = [                                  # multi-command array (runs in series)
  "cargo build",
  "./scripts/test-e2e.sh",
]
usage = '''
arg "<file>" help="Test file to run" default="all"
flag "--format <format>" help="Output format" default="text"
flag "-v --verbose" help="Enable verbose output"
'''
env = { RUST_BACKTRACE = "1" }           # per-task env vars
sources = ["Cargo.toml", "src/**/*.rs"]  # skip if unchanged (with mise watch)
outputs = ["target/debug/mycli"]         # output file for up-to-date check
confirm = "Are you sure?"                # prompt before running
hide = true                              # hide from `mise tasks` listing
```

## File task anatomy (`mise-tasks/<name>`)

```bash
#!/usr/bin/env bash
#MISE description="Build the CLI"
#MISE alias="b"
#MISE depends=["lint", "test"]
#MISE sources=["Cargo.toml", "src/**/*.rs"]
#MISE outputs=["target/debug/mycli"]
#MISE env={RUST_BACKTRACE = "1"}
set -euo pipefail
cargo build "$@"
```

Multi-line values split across `#MISE` lines:

```bash
#MISE depends=[\
#MISE   "lint",\
#MISE   "test",\
#MISE ]
```

## `[task_templates]` for repeating patterns

```toml
[task_templates."meaisin:ocr:test"]
description = "Run meaisinfhoghlaim OCR entrypoint for {{arg(name=model)}}"
usage = 'arg "<model>" help="OCR model key (e.g. qwen3-vl-8b)"'
run = '''
SAFE_NAME=$(echo "{{arg(model)}}" | tr '.-' '__')
uv run python "scripts/meaisin_ocr_htr_tests/ocr_model_${SAFE_NAME}_extract.py" "$@"
'''
```

Then `mise run "meaisin:ocr:test:qwen3-vl-8b"` expands the template.

## `[env]` block — modern `_.*` directives

```toml
[env]
# Modern directives (recommended)
_.file = '.env'                                   # load .env (dotenv format)
_.path = ["{{config_root}}/node_modules/.bin"]    # prepend to PATH
_.source = "./scripts/env.sh"                     # source a bash script

# Plain env vars
NODE_ENV = "development"

# Redacted secrets (won't print in task output)
SECRET_KEY = { value = "...", redact = true }

# Required vars (validated but not assigned)
DATABASE_URL = { required = "Set DATABASE_URL to your Postgres connection string" }

# Redactions array (matches patterns)
# redactions = ["SECRET_*", "*_TOKEN", "PASSWORD"]
```

**Deprecated (will be removed 2026.12.0 / 2027.4.0):**

- `env_file = ".env"` → use `_.file = ".env"`
- `env_path = ["..."]` → use `_.path = ["..."]`
- `env.mise.*` → use `env._.*`
- Tera template functions (`{{arg()}}`, `{{option()}}`, `{{flag()}}`) →
  use the `usage` field (removed in mise 2027.5.0)

## Monorepo mode

For per-subdir task catalogues:

```toml
# Root mise.toml
monorepo_root = true

[monorepo]
config_roots = [
  "packages/frontend",
  "packages/backend",
  "services/*",          # Single-level glob
]

[settings]
task.monorepo_depth = 3  # search 3 levels deep
```

Then `mise run //frontend:test` invokes the test task in
`packages/frontend/`.

## CI gate pattern (depends DAG)

```toml
[tasks.lint]
description = "Aggregate lint gate"
depends = ["lint:skills", "lint:registry", "py:typecheck"]
run = "uv run ruff check ."

[tasks.ci]
description = "Full CI pipeline"
depends = ["sync:all", "lint", "test", "openspec:validate-all", "cic:stack-doctor"]
run = "echo 'CI complete'"
```

`mise run ci` runs all deps in topological order.

## Alias back-compat pattern (per 2026-08-19 refactor)

When migrating old task names, preserve them as aliases for 1 release:

```toml
[tasks."dagster:dev"]
description = "Canonical: dagster:dev (cic:dagster:dev + dagster:oideachais preserved as aliases)"
alias = ["dagster:oideachais", "cic:dagster:dev"]
run = "uv run dagster dev -m orchestration.definitions"
```

## Variables available in tasks

| Variable | Meaning |
|:--|:--|
| `MISE_ORIGINAL_CWD` | The cwd when `mise run` was invoked |
| `MISE_CONFIG_ROOT` | The directory containing the `mise.toml` |
| `MISE_PROJECT_ROOT` | The root of the project that defines the task |
| `MISE_MONOREPO_ROOT` | The monorepo root (only inside monorepo) |
| `MISE_TASK_NAME` | The name of the task being run |
| `MISE_TASK_DIR` | The directory containing the task script |
| `MISE_TASK_FILE` | The full path to the task script |

## Routing: when to use what

| Question | Tool |
|:--|:--|
| "What tasks exist?" | `mise tasks` (TUI picker) or `mise tasks --all` |
| "What's the DAG for task X?" | `mise tasks --depends X` |
| "What's the canonical name for old task X?" | `mise tasks X` (errors with suggestions) |
| "How do I add a new sync layer?" | New shell file in `mise-tasks/sync/` |
| "How do I migrate from colon-form to template?" | Read `[task_templates]` examples in mise.toml |

## Anti-patterns

- **NEVER** define the same task twice (colon vs bare form) — use `alias =`.
- **NEVER** inline a multi-line script in TOML — use a file task.
- **NEVER** use Tera `{{arg()}}` / `{{option()}}` / `{{flag()}}` — use
  the `usage` field.
- **NEVER** write `env_file = ".env"` — use `_.file = ".env"`.
- **NEVER** leave secrets un-redacted — set `redact = true` or use the
  `redactions` array pattern.
- **NEVER** put `uv run python <long-script.py>` as a TOML one-liner —
  move to `mise-tasks/<namespace>/<name>.sh`.

## Skill pointers

- `mise.toml` — canonical task catalogue
- `.opencode/agents/mise.md` — the mise-aware subagent
- `.cocoindex_code/guides.yml#mise-task-search` — CCC concept guide
- `openspec/AGENTS.md` — references the priority tasks

## References

- mise docs: <https://mise.jdx.dev/>
- TOML tasks: <https://mise.jdx.dev/tasks/toml-tasks.html>
- File tasks: <https://mise.jdx.dev/tasks/file-tasks.html>
- Monorepo tasks: <https://mise.jdx.dev/tasks/monorepo.html>
- Task configuration: <https://mise.jdx.dev/tasks/task-configuration.html>
- This skill: `.agents/skills/mise/SKILL.md`
