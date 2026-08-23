# dev-tooling-surfaces Specification

## Purpose
The dev-tooling surfaces capability codifies the surface-refactor pattern (Firecrawl research → mise tasks → openspec spec deltas → docs roll-up) used for every dev-environment tool/library update. It defines 18 requirements across 4 categories: the canonical mise.toml shape (9 task namespaces), the opencode.json agent structure (4 primary + 11 subagents), the openspec CLI surface (18+ subcommands), and the version-pinning policy (exact versions for pipeline-critical tools).

## Requirements
### Requirement: mise-task-canonical-shape

The `mise.toml` task catalogue SHALL be organized by **domain** into
exactly 6 namespaces (core, openspec, devops, data, ml, web), plus
the modern mise features (task_templates, monorepo_root, etc.) and
the new tool-specific gates (uv audit, ccc grep, bun prune, etc.).

The `core:lint` aggregate gate SHALL include the 4 new tool-specific
audit/check gates so downstream CI catches regressions automatically.

#### Scenario: core:lint includes the uv audit + check gates

- **WHEN** `mise run core:lint` runs
- **THEN** the depends DAG MUST include: `lint:skills`, `lint:registry`,
  `core:typecheck`, `core:uv:audit:strict`, `core:uv:check`
- **AND** all 5 gates MUST pass before `core:lint` exits 0

### Requirement: opencode-agent-markdown-split

The `opencode.json` agent catalogue SHALL define ≤5 agents inline; all
domain-specific subagents MUST live as `.md` files under
`.opencode/agents/<name>.md` with YAML frontmatter and a `prompt` field
that references canonical files via direct path (`./AGENTS.md`,
`./openspec/AGENTS.md`, etc.).

#### Scenario: agent count by location

- **WHEN** `find .opencode/agents -name "*.md" | wc -l` runs
- **THEN** the result MUST be ≥ 9
- **AND** `grep -cE '^\s+"[a-z-]+":\s+\{' opencode.json | grep -v provider` MUST be ≤ 5

#### Scenario: prompt truncation prevention

- **WHEN** any agent's `prompt` string would exceed 2000 chars
- **THEN** that string MUST live in a `.opencode/agents/<name>.md` file
- **AND** `opencode.json` MUST reference it via
  `prompt = "{file:./.opencode/agents/<name>.md}"`

#### Scenario: guides.yml alignment

- **WHEN** an agent's prompt references a domain surface
- **THEN** the prompt MUST cite at least one entry from
  `.cocoindex_code/guides.yml` via `#<entry-title>` anchor
- **AND** the cited guide MUST resolve in the CCC index after
  `bun run ccc:index`

### Requirement: opencode-permission-api-migration

Every opencode agent SHALL use the `permission` field (not the deprecated
`tools` field) for access control. `permission.task` SHALL be set on
every primary agent to control which subagents it may invoke.

#### Scenario: deprecated API absence

- **WHEN** `grep -E '"tools":\s*\{' opencode.json` runs
- **THEN** the result MUST be empty (no agent uses the deprecated API)

#### Scenario: plan-agent read-only enforcement

- **WHEN** the `plan` agent is invoked
- **THEN** `permission.edit` MUST equal `deny`
- **AND** `permission.bash` MUST default to `ask` for `*`
- **AND** `permission.bash` MUST `allow` the safe read-only commands
  (`git status`, `git log*`, `git diff`, `openspec *`, `mise tasks`,
  `mise run lint*`)
- **AND** `permission.task` MUST `deny` `*` except `research` and
  `deep-cuts` (which MUST be `allow`)

#### Scenario: domain-agent scope enforcement

- **WHEN** a domain-specific subagent (e.g. `data-platform`) is invoked
- **THEN** `permission.bash` MUST `allow` only the commands within its
  scope (e.g. `uv run *`, `mise run *`)
- **AND** `permission.external_directory` MUST equal `deny`
- **AND** `permission.task` MUST allow only its sibling subagents

### Requirement: openspec-skill-canonical-reference

The `.agents/skills/openspec/SKILL.md` file SHALL exist, SHALL have valid
YAML frontmatter passing `mise run lint:skills`, and SHALL document the
8 canonical subcommands (`list`, `view`, `show`, `status`, `validate`,
`archive`, `instructions`, `schemas`).

#### Scenario: skill lint pass

- **WHEN** `bash .agents/skills/lint-skills.sh` runs
- **THEN** the openspec skill MUST appear in the pass list
- **AND** the skill MUST mention all 8 subcommands
- **AND** the skill MUST document the spec-delta format (ADDED/MODIFIED/
  REMOVED Requirements + Scenario blocks)

#### Scenario: priority command registered

- **WHEN** an agent reads `openspec/AGENTS.md`
- **THEN** the file MUST reference `.agents/skills/openspec/SKILL.md`
- **AND** the file MUST list `openspec view` + `openspec status` +
  `openspec validate --all` as new priority commands
- **AND** the file MUST include a 1-section "OPSX vs legacy schema" note

### Requirement: ccc-guides-coverage

The `.cocoindex_code/guides.yml` file MUST contain at least 30 entries,
including the 3 new entries `opencode-agent-search`, `mise-task-search`,
and `openspec-change-search`.

#### Scenario: guide count check

- **WHEN** `mise run lint:guides-yml` runs
- **THEN** the guide count MUST be ≥ 30
- **AND** the 3 new guides MUST be present
- **AND** every file path referenced in each guide MUST resolve on disk

#### Scenario: guides.yml domain alignment

- **WHEN** any new concept guide is appended
- **THEN** it MUST carry a `domain: "00-tooling"` tag (or a more
  specific domain if the concept is domain-specific)
- **AND** it MUST include a `tags: [...]` array with at least 3 keywords
  for semantic search matching
- **AND** it MUST follow the canonical schema (`title`, `description`,
  `files`, `tags`, `domain`)

### Requirement: openspec-schema-stability

The repository SHALL remain on the legacy `spec-driven` schema
(proposal + tasks + spec deltas under `openspec/changes/<id>/`).
The OPSX schema (YAML + Markdown templates, DAG dependencies, status
command) is **documented as the future migration target** but is
**time-boxed**: the next 3 changes following this one SHALL pilot
the OPSX schema in a subdirectory (e.g. `openspec/changes/opsx-pilot/`),
and a follow-up change SHALL adopt OPSX as the default schema for
all NEW changes.

#### Scenario: legacy spec-driven remains the default

- **WHEN** a new openspec change is created
- **THEN** the canonical structure SHALL be `proposal.md` + `tasks.md` + `specs/<capability>/spec.md` (the legacy spec-driven schema)
- **AND** the change SHALL pass `openspec validate --strict`

#### Scenario: OPSX pilot subdirectory is the time-box

- **WHEN** the next 3 changes are created after this change is archived
- **THEN** at least 1 of them SHALL pilot the OPSX schema (using `openspec schema fork spec-driven my-pilot-schema`)
- **AND** the pilot change SHALL be in a clearly-marked subdirectory (e.g. `openspec/changes/opsx-pilot/`)

#### Scenario: OPSX adoption is the follow-up

- **WHEN** a follow-up change evaluates the pilot
- **THEN** the follow-up SHALL either:
  - Adopt OPSX as the default schema for all NEW changes (if pilot succeeded), OR
  - Iterate on the pilot (if pilot had issues)

### Requirement: web-namespace-tooling-coverage

The web package MUST receive a dedicated web namespace in mise.toml
that exposes at least 6 tasks covering the 12 web apps, the 3 shared
packages, and the Hono API gateway.

The web namespace MUST contain: web omnibus, web:install, web:build,
web:typecheck, web:lint, web:dev <app> (Turbo filter), and web:cf-deploy.

#### Scenario: web namespace exists

- **WHEN** `mise tasks web` runs
- **THEN** at least 6 tasks MUST be listed under the `web` prefix
- **AND** the web omnibus MUST run web:install + web:build +
  web:typecheck + web:lint + web:format

#### Scenario: web:dev invokes turbo filter

- **WHEN** `mise run web:dev cianfhoghlaim-web` runs
- **THEN** the command MUST invoke `bunx turbo run dev --filter=cianfhoghlaim-web`
- **AND** no per-app tasks SHALL exist (the filter is the canonical
  surface)

### Requirement: ml-namespace-tooling-coverage

The meaisinfhoghlaim package + 12-agent fleet + MODEL_REGISTRY MUST
receive a dedicated ml namespace in mise.toml with at least 10 tasks.

The ml namespace MUST contain: ml omnibus, ml:registry:list,
ml:registry:audit, ml:litellm:regenerate, ml:agents:smoke,
ml:agents:audit, ml:agents:reproduce, and 3 task templates
(ml:ocr:test, ml:converter:test, ml:agent:test).

#### Scenario: ml namespace exists

- **WHEN** `mise tasks ml` runs
- **THEN** at least 10 tasks MUST be listed under the `ml` prefix
- **AND** 3 task_templates MUST be defined for the per-instance OCR /
  converter / agent patterns

#### Scenario: ml task templates expand correctly

- **WHEN** `mise run "ml:ocr:test:qwen3-vl-8b"` runs
- **THEN** the template MUST expand to invoke
  `uv run python scripts/meaisin_ocr_htr_tests/ocr_model_qwen3_vl_8b_extract.py`
- **AND** the safe-name translation (qwen3-vl-8b to qwen3_vl_8b) MUST
  be applied to match the script filename

### Requirement: data-namespace-tooling-coverage

The data plane MUST receive a dedicated data namespace in mise.toml
covering the 5 KCG Component layers with at least 12 tasks.

The data plane spans: dlt_sources + orchestration + baml_src +
cocoindex_flows + motherduck + notebooks + observability.

The data namespace MUST contain: data omnibus, data:up, data:down,
data:setup, data:status, data:dagster:up, data:schema:generate,
data:schema:validate, data:biep:milestone <n>, data:biep:gate,
data:marimo:wasm:export, and data:cocoindex:conformance.

#### Scenario: data namespace exists

- **WHEN** `mise tasks data` runs
- **THEN** at least 12 tasks MUST be listed under the `data` prefix
- **AND** the data omnibus MUST run data:up + data:setup + data:status

#### Scenario: data:biep:milestone template expansion

- **WHEN** `mise run "data:biep:milestone" -- 1` runs
- **THEN** the template MUST expand to invoke
  `.venv/bin/python3 scripts/m1_*.py`
- **AND** the glob MUST match exactly one script (no ambiguity)

### Requirement: devops-namespace-tooling-coverage

The IaC mesh MUST receive a dedicated devops namespace in mise.toml
covering the full IaC lifecycle with at least 14 tasks.

The IaC mesh spans: bonneagar with 89 Docker stacks +
Komodo/Pangolin/Locket/Infisical.

The devops namespace MUST contain: devops omnibus, devops:health,
devops:plan, devops:bootstrap, devops:bootstrap-pangolin-client,
devops:validate-stacks, devops:validate-stacks:strict,
devops:secrets:env, devops:secrets:init, devops:locket:exec,
devops:stack <name> <action>, devops:preflight:arm-oci,
devops:bring-up:smoke-test, and devops:deploy:full.

#### Scenario: devops namespace exists

- **WHEN** `mise tasks devops` runs
- **THEN** at least 14 tasks MUST be listed under the `devops` prefix
- **AND** the devops omnibus MUST run devops:health +
  devops:bootstrap-pangolin-client + devops:validate-stacks +
  devops:validate-stacks:strict

#### Scenario: devops:stack dispatches per-stack lifecycle

- **WHEN** `mise run devops:stack goodforms up` runs
- **THEN** the command MUST invoke `cd bonneagar && ./scripts/stack.sh goodforms up -d`
- **AND** the dispatch SHALL support up, down, and logs actions

### Requirement: core-namespace-tooling-coverage

The dev environment and cross-cutting CI gates MUST receive a
dedicated core namespace in mise.toml with at least 7 omnibus +
cross-cutting tasks.

The core namespace MUST contain: core omnibus, core:doctor,
core:sync, core:install, core:test, core:format, core:lint, and
core:ci.

#### Scenario: core namespace exists

- **WHEN** `mise tasks core` runs
- **THEN** at least 7 tasks MUST be listed under the `core` prefix
- **AND** the core omnibus MUST run core:sync + core:install +
  core:lint + core:test + core:format

#### Scenario: core:ci gates

- **WHEN** `mise run core:ci` runs
- **THEN** the depends DAG MUST include: core:lint, core:test,
  openspec:validate-all, devops:validate-stacks
- **AND** all 4 gates MUST pass before core:ci exits 0

### Requirement: uv-audit-and-check-gates

The dev environment SHALL provide 4 uv-audit-related gate tasks in
the `core` namespace, all opt-in via `mise run` and wired into the
aggregate `core:lint` gate where appropriate.

The uv audit gates SHALL cover at minimum:

1. `core:uv:audit` — the relaxed audit (informational; default uv audit)
2. `core:uv:audit:strict` — the CI gate (exits 1 on any known vuln)
3. `core:uv:check` — the `ty` type checker (uv 0.11.18+ preview)
4. `core:uv:audit-malware` — malware scan via `UV_MALWARE_CHECK=1`

#### Scenario: uv audit strict is the CI gate

- **WHEN** `mise run core:uv:audit:strict` runs
- **THEN** the command MUST invoke `uv audit --strict`
- **AND** exit 1 if `uv.lock` contains any known OSV vulnerability
- **AND** exit 0 if the lock is clean

#### Scenario: uv check runs ty

- **WHEN** `mise run core:uv:check` runs
- **THEN** the command MUST invoke `uv check`
- **AND** exit 1 if Astral's `ty` reports any type error
- **AND** exit 0 if the codebase is type-clean

#### Scenario: uv audit malware is opt-in

- **WHEN** `mise run core:uv:audit-malware` runs
- **THEN** the command MUST invoke `UV_MALWARE_CHECK=1 uv sync --dry-run`
- **AND** exit 1 if any package in the dependency graph is flagged by
  the malware database
- **AND** exit 0 if the graph is clean or the check is not available

### Requirement: ccc-grep-doctor-version-gates

The dev environment SHALL provide 4 cocoindex-code-related tasks
in the `core` namespace, all reachable via `mise run` and reflecting
the canonical ccc 0.2.40+ surface.

The ccc gates SHALL cover at minimum:

1. `core:ccc:grep` — structural search by example (no daemon needed)
2. `core:ccc:doctor` — system health check (index freshness + daemon)
3. `core:ccc:version` — print the installed cocoindex-code version
4. `core:ccc:search:json` — semantic search emitting JSON on stdout

#### Scenario: ccc grep is daemon-free

- **WHEN** `mise run core:ccc:grep "def <pattern>(" orchestration/` runs
- **THEN** the command MUST invoke `ccc grep` with the pattern + path
- **AND** it MUST NOT require the daemon to be running
- **AND** it MUST return matches in <2 seconds for repos <100k LOC

#### Scenario: ccc doctor is the health gate

- **WHEN** `mise run core:ccc:doctor` runs
- **THEN** the command MUST invoke `ccc doctor`
- **AND** exit 1 if the index is >7d stale
- **AND** exit 1 if the daemon has unhandled exceptions
- **AND** exit 0 if the system is healthy

#### Scenario: ccc version is the canonical version probe

- **WHEN** `mise run core:ccc:version` runs
- **THEN** the command MUST invoke `ccc version`
- **AND** print the exact installed version (e.g. `0.2.41`)
- **AND** exit 0

#### Scenario: ccc search:json emits structured JSON

- **WHEN** `mise run core:ccc:search:json "dagster asset"` runs
- **THEN** the command MUST invoke `ccc search --json`
- **AND** emit a JSON array of results on stdout
- **AND** each result MUST include `file_path`, `start_line`, `end_line`, `score`

#### Scenario: agent .md files reference ccc grep

- **WHEN** any of the 9 domain-specific agent `.md` files are read
- **THEN** the "Direct references (mirrors guides.yml)" section MUST
  mention `ccc grep` as the recommended tool for structural code searches
- **AND** the `mise run core:ccc:grep` invocation example MUST be present

### Requirement: bun-1-4-and-outdated-gate

The dev environment SHALL pin `bun@1.4` (or higher) in `package.json` and
provide 2 bun-related tasks in the `core` namespace:

1. `core:bun:outdated` — list outdated dependencies per workspace
2. `core:bun:upgrade` — one-command bun upgrade (uses `bun upgrade`)

#### Scenario: bun version pin is current

- **WHEN** the `package.json` is read
- **THEN** `packageManager` MUST be `bun@1.4` or higher
- **AND** the engines field MUST require `bun >= 1.4`

#### Scenario: bun outdated is the freshness gate

- **WHEN** `mise run core:bun:outdated` runs
- **THEN** the command MUST invoke `bun outdated`
- **AND** exit 0 with a list of outdated dependencies per workspace
- **AND** exit 1 if any critical dependency is >2 majors behind

#### Scenario: bun upgrade is the one-command update

- **WHEN** `mise run core:bun:upgrade` runs
- **THEN** the command MUST invoke `bun upgrade`
- **AND** exit 0 with the new bun version printed

### Requirement: openspec-new-subcommands-gates

The dev environment SHALL provide 5 openspec-related tasks in the
`openspec` namespace that surface the new 1.4+ subcommands:

1. `openspec:schemas` — list available workflow schemas (spec-driven, opsx, tdd)
2. `openspec:schemas:json` — same as `schemas` but JSON output
3. `openspec:feedback` — submit feedback to OpenSpec maintainers
4. `openspec:instructions` — emit enriched artifact templates
5. `openspec:templates` — show resolved template paths for a schema

#### Scenario: openspec schemas lists available schemas

- **WHEN** `mise run openspec:schemas` runs
- **THEN** the command MUST invoke `openspec schemas`
- **AND** exit 0 with a list of available workflow schemas
- **AND** each schema MUST include name, description, and artifacts

#### Scenario: openspec schemas JSON is programmatic

- **WHEN** `mise run openspec:schemas:json` runs
- **THEN** the command MUST invoke `openspec schemas --json`
- **AND** exit 0 with a JSON array on stdout

#### Scenario: openspec feedback is the feedback channel

- **WHEN** `mise run openspec:feedback --help` runs
- **THEN** the command MUST invoke `openspec feedback --help`
- **AND** show the usage for submitting feedback

#### Scenario: openspec instructions emits enriched templates

- **WHEN** `mise run openspec:instructions proposal` runs
- **THEN** the command MUST invoke `openspec instructions proposal`
- **AND** exit 0 with an enriched template for the proposal artifact

#### Scenario: openspec templates shows resolved paths

- **WHEN** `mise run openspec:templates` runs
- **THEN** the command MUST invoke `openspec templates`
- **AND** exit 0 with the resolved template paths for each artifact in the schema

#### Scenario: skill + agent docs reference the new subcommands

- **WHEN** `.agents/skills/openspec/SKILL.md` is read
- **THEN** the "Quick start" section MUST list all 5 new subcommands
- **AND** `.opencode/agents/proposal-author.md` MUST reference them in the agent prompt

### Requirement: mise-monorepo-mode-and-subprojects

The monorepo SHALL enable `monorepo_root = true` + `[monorepo] config_roots`
to get first-class subproject task support, with at least 2 subprojects
owning their own `mise.toml`:

1. `bonneagar/` — IaC subproject (89 Docker stacks + Komodo + Pangolin + Locket + Infisical)
2. `agents/` — Agent-fleet subproject (12-agent fleet + 8 NCCA subjects + 3 educational agents)

#### Scenario: monorepo_root is enabled

- **WHEN** the root `mise.toml` is read
- **THEN** `[settings]` MUST contain `monorepo_root = true`
- **AND** `[monorepo] config_roots` MUST include `bonneagar` and `agents`

#### Scenario: subproject tasks inherit from root

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command MUST invoke `bun run --cwd bonneagar iac:health`
- **AND** the subproject MUST inherit tools + env from the root
- **AND** the subproject MUST inherit `[task_templates]` from the root

#### Scenario: subproject tasks are addressable from root

- **WHEN** `mise tasks --all` runs from the repo root
- **THEN** the output MUST include both root tasks AND subproject tasks
- **AND** subproject tasks MUST be prefixed with `//devops:` or `//ml:agents:` per the mise monorepo path syntax

#### Scenario: back-compat aliases preserve old names

- **WHEN** `mise run devops:health` runs from the repo root
- **THEN** the command MUST resolve to the same execution as the pre-monorepo version
- **AND** every migrated task MUST retain its old name as an alias for 1 release cycle

#### Scenario: subproject tasks can also live under their domain namespace

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command MUST invoke the bonneagar-specific task
- **AND** the command MUST be equivalent to `mise run //devops:health` from the repo root

### Requirement: bun-1-4-completion-tasks

The dev environment SHALL provide 6 new bun-related tasks in the
`core` namespace + 1 new task in the `web` namespace, all reachable
via `mise run` and reflecting the canonical bun 1.4+ surface.

The bun 1.4 completion tasks SHALL cover at minimum:

1. `core:bun:prune` — `bun prune` (remove unused packages from node_modules)
2. `core:bun:audit:fix` — `bun audit fix` (auto-upgrade vulnerable packages)
3. `core:bun:audit:fix:dry-run` — dry-run variant of the above
4. `core:bun:dedupe` — `bun dedupe` (remove duplicate versions from bun.lock)
5. `core:bun:format` — `bunx prettier --write .` (the missing formatter)
6. `core:bun:parallel` — `bun run --parallel` (parallel script runner)
7. `web:test:parallel` — `bunx turbo run test --parallel` (parallel test runner)

#### Scenario: bun prune is the unused-deps gate

- **WHEN** `mise run core:bun:prune` runs
- **THEN** the command MUST invoke `bun prune`
- **AND** exit 0 with a list of removed packages
- **AND** exit 0 (no-op) if no packages to prune

#### Scenario: bun audit fix is the auto-remediation gate

- **WHEN** `mise run core:bun:audit:fix:dry-run` runs
- **THEN** the command MUST invoke `bun audit fix --dry-run`
- **AND** exit 0 if no fixes needed
- **AND** exit 0 (with a list of planned changes) if fixes are possible

#### Scenario: bun dedupe deduplicates the lockfile

- **WHEN** `mise run core:bun:dedupe` runs
- **THEN** the command MUST invoke `bun dedupe`
- **AND** exit 0 with the lockfile deduplicated

#### Scenario: bun format is the formatter

- **WHEN** `mise run core:bun:format` runs
- **THEN** the command MUST invoke `bunx prettier --write .`
- **AND** exit 0

#### Scenario: bun parallel is the parallel runner

- **WHEN** `mise run core:bun:parallel --bun-run="echo 1; echo 2"` runs
- **THEN** the command MUST invoke `bun run --parallel` with the rest of the args
- **AND** execute the scripts in parallel

#### Scenario: agent docs reference the Bun API surface

- **WHEN** `.opencode/agents/mise.md` is read
- **THEN** the "Direct references" section MUST mention at least 4 of the
  Bun 1.4+ API surface (Bun.cron, Bun.markdown, Bun.Image, Bun.serve)

### Requirement: mise-fmt-and-generate-tasks

The dev environment SHALL provide 5 new mise-related tasks in the
`core` namespace, all reachable via `mise run` and reflecting the
new mise subcommands.

The mise fmt + generate tasks SHALL cover at minimum:

1. `core:mise:fmt` — `mise fmt` (auto-formats mise.toml)
2. `core:mise:fmt:check` — `mise fmt --check` (CI gate, exits 1 on diff)
3. `core:mise:fmt:all` — `mise fmt --all` (formats all subprojects)
4. `core:mise:generate:pre-commit` — generate a git pre-commit hook
5. `core:mise:generate:devcontainer` — generate a devcontainer config

#### Scenario: mise fmt formats mise.toml

- **WHEN** `mise run core:mise:fmt` runs
- **THEN** the command MUST invoke `mise fmt`
- **AND** sort keys + clean up whitespace in the mise.toml file
- **AND** exit 0

#### Scenario: mise fmt check is the CI gate

- **WHEN** `mise run core:mise:fmt:check` runs
- **THEN** the command MUST invoke `mise fmt --check`
- **AND** exit 0 if the file is formatted correctly
- **AND** exit 1 if the file needs formatting

#### Scenario: mise fmt all formats subprojects

- **WHEN** `mise run core:mise:fmt:all` runs
- **THEN** the command MUST invoke `mise fmt --all`
- **AND** format mise.toml in root + all subproject config_roots

#### Scenario: mise generate creates files

- **WHEN** `mise run core:mise:generate:pre-commit` runs
- **THEN** the command MUST invoke `mise generate git-pre-commit`
- **AND** print the path to the generated file

#### Scenario: mise generate devcontainer

- **WHEN** `mise run core:mise:generate:devcontainer` runs
- **THEN** the command MUST invoke `mise generate devcontainer`
- **AND** print the path to the generated devcontainer config

#### Scenario: skill docs document the new tasks

- **WHEN** `.agents/skills/mise/SKILL.md` is read
- **THEN** the file MUST include a "fmt + generate" section
- **AND** document the 5 new tasks

### Requirement: uv-0-12-features-tasks

The dev environment SHALL provide 5 new uv-related tasks in the `core`
namespace, all reachable via `mise run` and reflecting the uv 0.12+
surface.

The uv 0.12 features tasks SHALL cover at minimum:

1. `core:uv:lock:refresh` — `uv lock --refresh` (re-resolve from scratch)
2. `core:uv:lock:upgrade` — `uv lock --upgrade` (upgrade all packages)
3. `core:uv:lock:upgrade-package` — `uv lock --upgrade-package <name>`
4. `core:uv:tree:json` — `uv tree --format=json` (uv 0.12+)
5. `core:uv:format` — `uv format` (Python formatter, uv 0.12+)

#### Scenario: uv lock refresh updates the lockfile

- **WHEN** `mise run core:uv:lock:refresh` runs
- **THEN** the command MUST invoke `uv lock --refresh`
- **AND** exit 0

#### Scenario: uv lock upgrade upgrades all packages

- **WHEN** `mise run core:uv:lock:upgrade` runs
- **THEN** the command MUST invoke `uv lock --upgrade`
- **AND** exit 0 (or warn if no upgrades)

#### Scenario: uv tree JSON is the programmatic tree

- **WHEN** `mise run core:uv:tree:json` runs
- **THEN** the command MUST invoke `uv tree --format=json`
- **AND** emit a JSON dependency tree on stdout

#### Scenario: uv format is the canonical formatter

- **WHEN** `mise run core:uv:format` runs
- **THEN** the command MUST invoke `uv format`
- **AND** format the Python codebase

### Requirement: openspec-extra-subcommands-tasks

The dev environment SHALL provide 7 new openspec-related tasks in
the `openspec` namespace, all reachable via `mise run` and reflecting
the canonical openspec 1.4+ subcommands we missed in the previous
refactor.

The 7 new subcommands SHALL cover:

1. `openspec:update` — `openspec update` (re-emit instruction files)
2. `openspec:change` — `openspec change` (interactive subcommand)
3. `openspec:spec` — `openspec spec` (interactive subcommand)
4. `openspec:config` — `openspec config` (global config viewer)
5. `openspec:workspace` — `openspec workspace` (subcommand)
6. `openspec:context-store` — `openspec context-store` (subcommand)
7. `openspec:initiative` — `openspec initiative` (subcommand)

#### Scenario: openspec update re-emits instruction files

- **WHEN** `mise run openspec:update` runs
- **THEN** the command MUST invoke `openspec update`
- **AND** exit 0 (or print help)

#### Scenario: openspec change is the interactive manager

- **WHEN** `mise run openspec:change --help` runs
- **THEN** the command MUST invoke `openspec change --help`
- **AND** print the usage for managing change proposals

#### Scenario: openspec spec is the interactive spec manager

- **WHEN** `mise run openspec:spec --help` runs
- **THEN** the command MUST invoke `openspec spec --help`
- **AND** print the usage for managing specs

#### Scenario: openspec config views global config

- **WHEN** `mise run openspec:config` runs
- **THEN** the command MUST invoke `openspec config`
- **AND** print the global openspec config

#### Scenario: openspec workspace + context-store + initiative

- **WHEN** `mise run openspec:workspace` or `openspec:context-store` or `openspec:initiative` runs
- **THEN** the command MUST invoke the corresponding openspec subcommand
- **AND** exit 0 (or print help)

### Requirement: mise-upgrade-and-monorepo-activation

The dev environment SHALL pin mise >= 2026.8 in `[tools]` so that:

1. The `[settings] monorepo_root = true` setting is recognized (not silently ignored)
2. The `[monorepo] config_roots = [...]` setting is processed
3. Root-level aliases for the devops/ml:agents tasks (that moved to subprojects in the previous refactor) resolve via monorepo path syntax
4. The new `core:mise:upgrade` task works

#### Scenario: mise is upgraded to 2026.8+

- **WHEN** the user runs `mise install`
- **THEN** mise SHALL be installed at version 2026.8.10 or later
- **AND** the `settings.monorepo_root` warning SHALL NOT appear

#### Scenario: monorepo_root is recognized

- **WHEN** `mise tasks --all` runs from the repo root
- **THEN** the output SHALL include subproject tasks (with `//` prefix per the monorepo path syntax)
- **AND** the output SHALL NOT include the `unknown field in settings: monorepo_root` warning

#### Scenario: root aliases resolve to subproject tasks

- **WHEN** `mise run devops:health` runs from the repo root
- **THEN** the command SHALL resolve to the subproject task (via the root alias)
- **AND** exit 0 (after the subproject task completes)

#### Scenario: subproject task works directly

- **WHEN** `cd bonneagar && mise run devops:health` runs
- **THEN** the command SHALL invoke `bun run iac:health` from inside the bonneagar subproject
- **AND** exit 0

#### Scenario: core:mise:upgrade works

- **WHEN** `mise run core:mise:upgrade` runs
- **THEN** the command SHALL invoke `mise upgrade`
- **AND** upgrade mise to the latest version

### Requirement: openspec-1-10-upgrade

The dev environment SHALL expose a 1-command upgrade path for
openspec (currently installed globally via `bun add -g @fission-ai/openspec`).

#### Scenario: openspec upgrade task exists

- **WHEN** `mise run openspec:upgrade` runs
- **THEN** the command MUST print the install command
  (`bun add -g @fission-ai/openspec@latest`)
- **AND** exit 0 (the actual install is user-initiated)

#### Scenario: openspec is at 1.10+ after upgrade

- **WHEN** the user runs `bun add -g @fission-ai/openspec@1.10.0`
- **THEN** `openspec --version` MUST show `1.10.0` or later
- **AND** `openspec schemas` MUST list spec-driven + opsx + workspace-planning
- **AND** all existing pending + archived changes MUST still validate

#### Scenario: skill docs document 1.10 features

- **WHEN** `.agents/skills/openspec/SKILL.md` is read
- **THEN** the file MUST include a "New in 1.10" section
- **AND** document Stores Beta, /opsx:explore, /opsx:onboard
- **AND** document the upgrade task

### Requirement: Stale openspec changes MUST have a documented triage decision

The system SHALL ensure that any pending openspec change that has been at `0/N tasks` for more than 7 days has a documented triage decision (KEEP / CLOSE / SPLIT / TRIAGE) in either:
- The change's own `proposal.md` (a "Triage" section)
- A separate triage change (e.g. `2026-08-22-stale-changes-triage-v1`)

The triage decision MAY be reversed later (a KEEP can become a CLOSE). The decision MUST cite the per-change rationale (e.g. "superseded by archived change X", "real work, in-flight", "oversized, needs split").

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-stale-changes-triage-v1 triage change.

#### Scenario: A change is 0/N tasks for 14 days

- **GIVEN** a pending openspec change has been at `0/N tasks` for 14+ days
- **WHEN** the openspec CI gate runs (or a developer inspects the change list)
- **THEN** the change MUST have a documented triage decision
- **AND** the decision MUST be either KEEP / CLOSE / SPLIT / TRIAGE
- **AND** the rationale MUST cite at least 1 specific reason

#### Scenario: A change is added to the triage change

- **GIVEN** a pending openspec change is added to `2026-08-22-stale-changes-triage-v1/proposal.md` Group B (CLOSE) or Group C (SPLIT) or Group D (TRIAGE)
- **THEN** the triage change is the authoritative source for the decision
- **AND** the original change does NOT need a separate "Triage" section in its own `proposal.md`

### Requirement: `2026-08-21-unsloth-v5-architecture-refinement-v1` superseded

The system SHALL recognize that the unsloth-v5 architecture refinement change is superseded by the archived `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` change. The refined topology (direct host + Pangolin private resource) is documented in the latter.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up Unsloth v5 architecture

- **WHEN** an agent looks up the Unsloth v5 architecture
- **THEN** the agent SHOULD load `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (archived)
- **AND** the refinement change is preserved as a historical reference

### Requirement: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1` superseded

The system SHALL recognize that the browserbase + crawl4ai MCP archive change is superseded by the active `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP). The latter covers the same scope (6 legacy MCP servers including browserbase + crawl4ai).

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up the legacy MCP archive

- **WHEN** an agent looks up the legacy MCP archive
- **THEN** the agent SHOULD load `2026-08-21-archive-legacy-sruth-mcp-servers-v1` (KEEP)
- **AND** the older browserbase+ crawl4ai change is preserved as a historical reference

### Requirement: `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` superseded

The system SHALL recognize that the count-drift rebase + INDEXING_AND_COGNITION cleanup change is already done implicitly by the linter. `mise run lint:drift-docs` reports 0 drift; the per-area AGENTS.md regeneration (`mise run sync:spec-agents`) is idempotent.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Lint drift is zero

- **WHEN** an agent runs `mise run lint:drift-docs`
- **THEN** the linter reports 0 drift
- **AND** no manual rebase is needed

### Requirement: `2026-08-10-england-biiep-pipeline-v1` superseded

The system SHALL recognize that the England BIEP pipeline change is superseded by the canonical `british-isles-education-pipeline-v3` (the 5-milestone sequential plan + the 6-deferred-jurisdiction plan). The England ChangeDetection freshness guarantee is covered by the `upstream-package-monitoring` spec.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Agent looks up the England BIEP pipeline

- **WHEN** an agent looks up the England BIEP pipeline
- **THEN** the agent SHOULD load `british-isles-education-pipeline-v3` (the canonical)
- **AND** the older England-specific change is preserved as a historical reference

