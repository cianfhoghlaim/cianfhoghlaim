# 2026-08-19 — Domain-Driven mise.toml Task Catalog

## Why

The current `mise.toml` (post the 2026-08-19-dev-tooling-refactor) has **119 tasks across 11 namespaces** (core, ts, schema, py, lint, opencode, baml, openspec, cic, sync, biep, iac, lakeforce, etc.) with significant overlap and 37 tasks that are **not referenced anywhere** in docs, CI, or scripts (per the dev-tooling-surfaces spec audit).

Critically, the **task namespace boundaries don't match the actual domain boundaries** of the monorepo. The `web/` package (12 apps + 3 shared packages + Hono API) has **zero mise task references** in its AGENTS.md. The `observability/` package (13 py files) also has zero references. The `meaisinfhoghlaim/` package (104 py files + 12-agent fleet) has 42 unique references but no dedicated task namespace.

A developer working on `web/apps/tuatha-ui` has to discover via docs that they should run `mise run ts:typecheck` (which has no alias to web). A developer working on `agents/meaisinfhoghlaim/` has to discover that OCR model entrypoints are exposed via `mise run meaisin:ocr:test:qwen3-vl-8b` — buried 6+ levels deep.

This change re-organizes the task catalogue **by domain** so a developer's mental model "I'm working on X today" maps directly to `mise run X` — with surgical subcommands per package.

## What changes

1. **Drop 37 dead tasks** (the audit showed 82 referenced of 119; drop the other 37 — see `tasks.md`)
2. **Reorganize into 6 namespaces** by domain alignment with the monorepo:
   - `core` — the dev env + cross-cutting CI gates (lint, sync, doctor, test, format, ci omnibus)
   - `openspec` — change management (orthogonal to all 4 product domains)
   - `devops` — IaC + 89 Docker stacks + Komodo/Pangolin/Locket/Infisical + deploy
   - `data` — the lakehouse + BIEP + Dagster + baml_src + CocoIndex + motherduck + notebooks
   - `ml` — meaisinfhoghlaim (OCR/HTR/Alignment/Celtic) + 12-agent fleet + MODEL_REGISTRY
   - `web` — web/apps + web/packages + web/hono-api + Turborepo (NEW namespace)
3. **Regroup file tasks** under `mise-tasks/{core,devops,data,ml,web}/` (~22 scripts)
4. **3 task templates** under `[task_templates]`: `ml:ocr:test`, `ml:converter:test`, `ml:agent:test`
5. **Back-compat aliases** for 1 release cycle on every task that's referenced in CI/docs
6. **New omnibus tasks**: `core`, `core:ci`, `devops`, `data`, `ml`, `web` — each runs the canonical workflow for its domain in one command

## Domain mapping (the canonical alignment)

| Domain | Packages | Tasks |
|:--|:--|:--|
| **core** (dev env) | repo root + `.agents/skills/` + `mise-tasks/` + `scripts/sync/` | `core:doctor`, `core:sync`, `core:install`, `core:test`, `core:format`, `core:lint`, `core:ci` |
| **openspec** | `openspec/` | 8 subcommands (list/list-specs/view/validate/validate-all/status/show/archive) |
| **devops** | `bonneagar/` (IaC + 89 stacks) + `.infisical.env` + `.env` | `devops`, `devops:health`, `devops:plan`, `devops:bootstrap`, `devops:validate-stacks`, `devops:secrets:init`, `devops:stack <name> <action>`, `devops:deploy:full` |
| **data** | `dlt_sources/` + `orchestration/` (Dagster) + `baml_src/` + `cocoindex_flows/` + `motherduck/` + `notebooks/` + `observability/` | `data`, `data:up`, `data:dagster:up`, `data:schema:generate`, `data:schema:validate`, `data:biep:milestone <n>`, `data:biep:gate`, `data:marimo:wasm:export`, `data:cocoindex:conformance` |
| **ml** | `meaisinfhoghlaim/` (OCR/HTR/Alignment/Celtic) + `agents/meaisinfhoghlaim/` (12-agent fleet) + `meaisinfhoghlaim/models/` | `ml`, `ml:registry:list`, `ml:registry:audit`, `ml:litellm:regenerate`, `ml:agents:smoke`, `ml:agents:audit`, `ml:agents:reproduce`, `ml:ocr:test <model>`, `ml:converter:test <name>`, `ml:agent:test <name>` |
| **web** | `web/apps/*/` (12 apps) + `web/packages/*/` (3 shared) + `web/hono-api/` + `turbo.json` | `web`, `web:install`, `web:build`, `web:typecheck`, `web:lint`, `web:dev <app>`, `web:cf-deploy` |

## Out of scope (deferred)

- Monorepo mode (`monorepo_root = true`) — deferred to a follow-up change
- `mise en` shell activation — handled by the existing mise install
- `mise watch` for any task — deferred

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-19-dev-tooling-refactor-mise-opencode-openspec-v1` (this change extends the task catalogue shape established there)
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. `grep -E '^\[tasks\."' mise.toml | wc -l` returns ≤ 85 (was 119)
2. `find mise-tasks -type f | wc -l` returns ≥ 22 (was 9)
3. `grep -cE '^\[task_templates\.' mise.toml` returns ≥ 3
4. `mise tasks --all | wc -l` returns ≥ 80 (was 127)
5. `mise run core:doctor` exits 0
6. `mise run core:lint` exits 0
7. `mise run openspec:validate-all` exits 0 with 130+ items
8. `mise run devops:health` exits 0 OR returns a graceful "komodo CLI not in PATH" message
9. `mise run data:schema:validate` exits 0
10. `mise run ml:registry:list` exits 0 and prints MODEL_REGISTRY entries
11. All CI workflows (`.github/workflows/ci.yaml`, `baml-test.yaml`, `cocoindex-conformance.yaml`) still work after the rename (via aliases)
12. `AGENTS.md` priority mise tasks list updated to reference the new domain-based names
13. `openspec/AGENTS.md` priority mise tasks list updated
14. `.agents/skills/mise/SKILL.md` updated to document the 6-namespace shape

## Rollback plan

Single git commit per phase. Each phase is independently revertable:
1. Drop dead tasks (additive change — easy revert)
2. Write new mise.toml (big atomic swap — `git revert`)
3. Add new mise-tasks/ files (additive — easy revert)
4. Update docs (additive — easy revert)
5. Archive openspec change (creates a separate commit; pre-archive deletion is reversible)

The openspec change can be removed before archive via `rm -rf openspec/changes/2026-08-19-domain-driven-mise-task-catalog-v1/`. After archive, a follow-up change is required.

## Cross-references

- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
- `.agents/skills/mise/SKILL.md` — the mise reference (will be updated)
- `.cocoindex_code/guides.yml#mise-task-search` — the CCC concept guide
- `openspec/AGENTS.md` — the routing table
- `AGENTS.md` — the root routing table
