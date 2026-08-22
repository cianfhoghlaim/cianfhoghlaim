---
name: mise
description: mise-en-place task authoring + tool management for the cianfhoghlaim monorepo. Use when adding/modifying tasks in mise.toml, designing DAG dependencies, choosing between TOML tasks vs file tasks vs task_templates, writing usage specs for task arguments, or migrating legacy colon-form task aliases. Covers mise 2026.5+ features: task_templates, depends DAG, alias =, usage =, redactions, monorepo_root, mise-tasks/ directory with #MISE frontmatter.
when_to_use: "mise task author | DAG designer | CI gate author | shell scripter | IaC task author"
---

# mise-en-place — task authoring for the cianfhoghlaim monorepo

[mise](https://mise.jdx.dev/) is the canonical tool manager + task
runner for this repo. The `mise.toml` at the repo root defines the 9
task namespaces + ~60 file tasks in `mise-tasks/`. Local install:
**`mise 2026.5.6`** (latest 2026.8.10 available).

## First-time mise install (CRITICAL — read this before running anything)

The `[settings] monorepo_root = true` flag in this repo's `mise.toml`
**requires mise 2026.8.10+**. On older versions (like the 2026.5.6
that ships with macOS via Homebrew) you will see this warning on every
`mise` invocation:

```
mise WARN  unknown field in ~/dev/kings_college_galway/mise.toml: settings.monorepo_root
```

The flag is silently ignored — your tasks still work, but the
`bonneagar/` + `agents/` subprojects don't get their inherited tools
or per-subproject tasks. **Install the standalone 2026.8.10 build to
unlock monorepo mode.**

### Install steps (one-time, ~30s)

```bash
# 1. Uninstall the Homebrew/system version (if any)
brew uninstall mise 2>/dev/null || true

# 2. Install via the standalone installer (mise cannot self-install via [tools])
curl https://mise.run | sh
# OR via cargo: cargo install mise

# 3. Activate in your shell (~/.zshrc or ~/.bashrc)
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc  # or bash

# 4. Reload + verify
source ~/.zshrc
mise --version  # MUST print 2026.8.10 or later

# 5. Now `cd` into the repo; mise will see the [tools] + [settings] blocks
cd ~/dev/kings_college_galway
mise install     # installs the pinned python + uv + bun + dagger + etc.
mise doctor      # confirms everything is healthy
```

### Why not just `mise use python@3.13`?

The standalone installer is the only way to get a mise version newer
than your package manager ships. The mise CLI itself can't upgrade
itself (the `[tools] mise = "..."` field doesn't work — try it and
you'll get a chicken-and-egg error). The version pinned in this
repo's `mise.toml` (per the 2026-08-22-mise-upgrade-monorepo-root-activation-v1
change) is a *target* version, not an *install* version.

### Verify the monorepo is active

After install + `mise install`, you should see (in `mise tasks --all`):

```
//devops:health               DEVOPS health (subproject root alias)
devops:health                 DEVOPS health (root alias)
```

The `//devops:health` entry means the subproject is being picked up.
If you only see `devops:health` (without `//`), the monorepo mode
isn't active — your mise is too old.

## Quick start — the 6 domain namespaces

The cianfhoghlaim `mise.toml` is organized by **domain** so a
developer's mental model "I'm working on X today" maps directly to
`mise run X` (post the 2026-08-19-domain-driven-mise-task-catalog-v1
change). The 6 namespaces:

| Namespace | Count | Purpose |
|:--|:--|:--|
| **`core`** | 8 + omnibus | The dev environment (sync, install, test, format, typecheck, doctor, lint, clean, reset) + cross-cutting CI gates (lint:*, sync:*) |
| **`openspec`** | 8 | Change management (list, list-specs, view, validate, validate-all, status, show, archive) |
| **`devops`** | 13 + omnibus | IaC + 89 Docker stacks + Komodo/Pangolin/Locket/Infisical + deploy (health, plan, bootstrap, validate-stacks, secrets:*, locket:exec, stack, preflight:arm-oci, bring-up:smoke-test, deploy:full) |
| **`data`** | 11 + omnibus | The lakehouse + BIEP + Dagster + baml_src + CocoIndex + motherduck + notebooks (up, down, setup, status, dagster:up, schema:*, biep:milestone, biep:gate, marimo:wasm:export, cocoindex:conformance) |
| **`ml`** | 6 + omnibus + 3 templates | meaisinfhoghlaim (OCR/HTR/Alignment/Celtic) + 12-agent fleet + MODEL_REGISTRY (registry:list, registry:audit, litellm:regenerate, agents:smoke, agents:audit, agents:reproduce, + ocr:test / converter:test / agent:test templates) |
| **`web`** | 6 + omnibus | web/apps (12 apps) + web/packages (3 shared) + web/hono-api + Turborepo (install, build, typecheck, lint, format, dev) |

**Total: ~89 TOML tasks** + 3 `[task_templates]` + ~17 file tasks in
`mise-tasks/<domain>/` (down from 119 TOML + 9 file + 3 templates
pre-refactor).

### Daily "I'm working on X" workflow

| Mental model | Command | What it does |
|:--|:--|:--|
| "I'm setting up the dev env" | `mise run core` | sync + install + lint + test + format |
| "I'm working on CI" | `mise run core:ci` | lint + test + openspec:validate-all + devops:validate-stacks |
| "I'm working on IaC" | `mise run devops` | health + bootstrap-pangolin-client + validate-stacks + validate-stacks:strict |
| "I'm working on the data plane" | `mise run data` | setup + status + marimo-wasm-export + cocoindex-conformance |
| "I'm working on OCR / agents / models" | `mise run ml` | registry:audit + agents:smoke + litellm:regenerate |
| "I'm working on the web apps" | `mise run web` | install + build + typecheck + lint + format |

### Back-compat aliases (1 release cycle)

The old bare/colon task names remain valid as aliases:

- `sync` → `core:sync` · `test` → `core:test` · `lint` → `core:lint` · `format` → `core:format` · `doctor` → `core:doctor`
- `dagster:dev` → `data:dagster:up` · `dagster:oideachais` → `data:dagster:up` · `cic:dagster:dev` → `data:dagster:up`
- `iac:bootstrap` → `devops:bootstrap` · `iac:health` → `devops:health` · `iac:plan` → `devops:plan` · `iac-bootstrap` → `devops:bootstrap` (etc.)
- `cic:stack-doctor` → `devops:validate-stacks` · `stack-doctor` → `devops:validate-stacks` · `stack-doctor:strict` → `devops:validate-stacks:strict`
- `cic:ocr:registry-lint` → `ml:registry:audit` · `cic:meaisin:litellm-regenerate` → `ml:litellm:regenerate`
- `baml:generate` → `data:schema:generate` · `baml:test` → `data:schema:validate`
- `schema:generate` → `data:schema:generate` · `schema:validate` → `data:schema:validate`
- `biep:v3:setup` → `data:setup` · `biep:v3:status` → `data:status` · `biep:v3:m<n>` → `data:biep:milestone -- <n>`
- `agents:smoke` → `ml:agents:smoke` · `agents:audit` → `ml:agents:audit` · `agents:reproduce` → `ml:agents:reproduce`
- `secrets:init` → `devops:secrets:init` · `secrets:env` → `devops:secrets:env` · `locket:exec` → `devops:locket:exec`
- `preflight:arm-oci` → `devops:preflight:arm-oci` · `bring-up:smoke-test` → `devops:bring-up:smoke-test` · `deploy:full` → `devops:deploy:full`
- `ts:install` → `web:install` · `ts:build` → `web:build` · `ts:typecheck` → `web:typecheck` · `ts:lint` → `web:lint` · `turbo` → (use `bunx turbo run` directly)
- `sync:all` → `core:sync:all` · `sync:paths` → `core:sync:paths` · ... · `sync:firecrawl` → `core:sync:firecrawl`
- `lint:skills` → `core:lint:skills` · `lint:registry` → `core:lint:registry` · ... · `lint:firecrawl-budget` → `core:lint:firecrawl-budget`

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

## `mise fmt` + `mise generate` (the newer subcommands)

Mise 2026.5+ shipped two new top-level subcommands we use now:

- **`mise fmt`** — auto-formats `mise.toml` (sorts keys, cleans whitespace). Would catch the manual TOML issues like escape conflicts and multi-line array problems.
- **`mise generate`** — generates files for various tools/services (bootstrap scripts, devcontainer configs, GitHub Actions, git pre-commit hooks).

### Tasks for the new subcommands

| Task | Command | Purpose |
|:--|:--|:--|
| `core:mise:fmt` | `mise fmt` | Auto-format root `mise.toml` |
| `core:mise:fmt:check` | `mise fmt --check` | CI gate (exits 1 on diff) |
| `core:mise:fmt:all` | `mise fmt --all` | Format all subproject `mise.toml` files |
| `core:mise:generate:pre-commit` | `mise generate git-pre-commit` | Generate a git pre-commit hook |
| `core:mise:generate:devcontainer` | `mise generate devcontainer` | Generate a devcontainer config |

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
- `mise fmt`: <https://mise.jdx.dev/cli/fmt.html>
- `mise generate`: <https://mise.jdx.dev/cli/generate.html>
- This skill: `.agents/skills/mise/SKILL.md`
