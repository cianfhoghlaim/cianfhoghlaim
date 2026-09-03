# dev-tooling-surfaces Specification

## Purpose
TBD - created by archiving change 2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1. Update Purpose after archive.
## Requirements
### Requirement: mise-task-canonical-shape

The `mise.toml` task catalogue SHALL be organized by **domain** into
exactly 6 namespaces:

1. **`core`** — the dev environment + cross-cutting CI gates
   (lint, sync, doctor, test, format, ci omnibus)
2. **`openspec`** — change management (orthogonal to all 4 product
   domains)
3. **`devops`** — IaC + 89 Docker stacks + Komodo/Pangolin/Locket/
   Infisical + deploy
4. **`data`** — the lakehouse + BIEP + Dagster + baml_src + CocoIndex +
   motherduck + notebooks + observability
5. **`ml`** — meaisinfhoghlaim (OCR/HTR/Alignment/Celtic) + 12-agent
   fleet + MODEL_REGISTRY + HF watchdog
6. **`web`** — web/apps + web/packages + web/hono-api + Turborepo

Each domain SHALL ship with an **omnibus task** (e.g. `mise run devops`)
that runs the canonical workflow for that domain in one command, plus
surgical subcommands per package. The catalogue SHALL contain no
more than 90 TOML tasks across these 6 namespaces, plus a
`[task_templates]` block for repeating patterns.

#### Scenario: namespace count check

- **WHEN** `grep -E '^\[tasks\."' mise.toml | sed -E 's/^\[tasks\.([^"]+)?"\]$/\1/' | awk -F':' '{print $1}' | sort -u | wc -l` runs
- **THEN** the result MUST be ≤ 6
- **AND** the unique namespace prefixes MUST be one of: core, openspec, devops, data, ml, web

#### Scenario: omnibus tasks exist

- **WHEN** `mise tasks` runs
- **THEN** the following omnibus tasks MUST exist: `core`, `core:ci`, `devops`, `data`, `ml`, `web`
- **AND** running `mise run <domain>` MUST exit 0

#### Scenario: alias-pair deduplication

- **WHEN** any pair of task names (`old:colon` and `new:domain:colon`)
  shares the same `run` body
- **THEN** the new domain form MUST be the canonical task
- **AND** the old form MUST be preserved for 1 release cycle via
  `alias = "new:domain:colon"` on the canonical task
- **AND** no two `[tasks.*]` blocks SHALL differ only by the old vs
  new naming form

#### Scenario: task_templates coverage

- **WHEN** a repeating task pattern exists (per-instance repeating
  pattern such as one wrapper per OCR model, per document converter,
  per agent extractor)
- **THEN** the pattern MUST be expressed as a `[task_templates."<prefix>"]`
  block in `mise.toml`
- **AND** the per-instance script MUST live in
  `mise-tasks/<namespace>/<name>.sh` with `#MISE` frontmatter

#### Scenario: dead-task elimination

- **WHEN** a task has zero references in `**/*.md`, `**/*.yaml`,
  `**/*.sh`, `**/*.ts`, `**/*.py`, `**/*.toml`, OR `AGENTS.md` files
  across the repository
- **THEN** the task SHALL be dropped (not aliased) in the new catalogue
- **AND** the only exceptions SHALL be tasks that are referenced in
  CI workflows (`.github/workflows/*.yaml`) or in skills
  (`.agents/skills/*/SKILL.md`)

#### Scenario: depends DAG construction

- **WHEN** any quality-gate task depends on prerequisite tasks
- **THEN** the dependency MUST be declared via `depends = [...]` on
  the gating task
- **AND** `mise tasks --depends <task>` MUST show the DAG

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
(proposal + tasks + spec deltas under `openspec/changes/<id>/`); the
experimental `OPSX` schema (YAML + Markdown templates, DAG dependencies)
SHALL NOT be adopted in this capability.

#### Scenario: schema non-migration

- **WHEN** `openspec schemas` runs
- **THEN** the result MUST NOT show a fork or fork-derivative of `opsx`
  as the active schema for this repo
- **AND** the legacy `spec-driven` schema MUST remain the canonical
  workflow for all 78 pending + 96 archived changes

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

