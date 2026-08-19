# 2026-08-19 — Dev tooling refactor (mise + opencode + openspec)

## Why

Three of the foundational developer surfaces have accumulated significant
sprawl between 2026-04 and 2026-08-19:

1. **`mise.toml`** has grown to **329 task blocks** across **50+ prefixes**
   (biep:49, meaisin:40, sync:41, cic:29, lint:15, lakehouse:9, iac:10,
   docs:8, llama-swap:7, dagger:5, ...). The catalogue shows:
   - **Alias-pair duplication** — `iac-bootstrap` ≡ `iac:bootstrap`,
     `preflight-arm-oci` ≡ `preflight:arm-oci`, `cic:sync` ≡ `sync`,
     `baml:cli-test` ≡ `baml:test`, `notebook:list` ≡ `sync:notebooks`,
     `secrets:sync` ≡ `secrets:init` — each pair occupies two `[tasks.*]`
     blocks with identical `run` bodies.
   - **50+ single-line Python entrypoints** for OCR models, document
     converters, and agent extractors — each is a one-line wrapper around
     `uv run python scripts/meaisin_ocr_htr_tests/<name>_extract.py`.
   - **0 `alias =`, 0 `depends =`, 0 `[task_templates]`** — the modern mise
     features for DAG construction and template reuse are unused.
   - **No monorepo mode** — `monorepo_root = true` and `config_roots` are
     not declared despite the repo having `bonneagar/` and `agents/`
     sub-trees with their own concerns.

2. **`opencode.json`** defines **13 agents all inlined** with multi-KB
   `prompt` strings. The data-platform, infrastructure, and agent-platform
   prompts are each truncated at the 2000-char display limit. Every agent
   uses the **deprecated `tools` field** (`tools: { write: false }`)
   instead of the current `permission` field. No `.opencode/agents/`
   markdown files exist; no `permission.task` gating controls which
   subagents each agent can invoke; `hidden: true` is unused despite
   `dev-env-demo` + `orchestrator` + `deep-cuts` being internal-only.

3. **`openspec/`** has **78 pending changes + 96 specs** but no
   `.agents/skills/openspec/SKILL.md` despite openspec being the canonical
   change-management surface. The new 1.4 subcommands (`view`, `status`,
   `instructions`, `schemas`, `show`) are not documented in
   `openspec/AGENTS.md`. The proposal-author agent lives only inline in
   `opencode.json`.

## What changes

1. **Skills surface** — Add 3 new canonical SKILL.md files:
   - `.agents/skills/mise/SKILL.md`
   - `.agents/skills/opencode/SKILL.md`
   - `.agents/skills/openspec/SKILL.md`

2. **CCC concept guides** — Append 3 new entries to
   `.cocoindex_code/guides.yml` (new `00-tooling` domain):
   - `opencode-agent-search` — 13 agents + provider/MCP inventory
   - `mise-task-search` — 8 task categories + ~60 file tasks
   - `openspec-change-search` — 78 pending + 96 archived + 1.4 subcommands

3. **`openspec/AGENTS.md`** — Add 3 new priority commands
   (`openspec view`, `openspec status`, `openspec validate --all`), the
   new `openspec` skill, and the `mise run openspec:validate-all` task.
   Add a "OPSX vs legacy" routing note.

4. **opencode agents** — Reduce inline agents from 13 → 4 (build, plan,
   research, orchestrator). Move 9 domain-specific subagents to
   `.opencode/agents/<name>.md` files with YAML frontmatter. Migrate every
   deprecated `tools:` block to the current `permission` API. Add
   `permission.task` gating + `hidden: true` for internal agents. Set
   `subagent_depth: 2`, `watcher.ignore`, `compaction.prune: true`, and an
   `instructions` array.

5. **`mise.toml`** — Reduce from 329 → ~75 TOML tasks. Add a
   `[task_templates]` block for the OCR/converter/agent/biep/marimo
   patterns. Move all repeating scripts to `mise-tasks/<namespace>/<name>.sh`
   files with `#MISE` frontmatter. Collapse alias pairs. Add `depends =`
   DAG. Add `usage =` arg specs.

6. **New capability spec** — `openspec/specs/dev-tooling-surfaces/spec.md`
   with 5 ADDED Requirements formalizing the canonical 3-tool surface.

## Out of scope (deferred)

- OpenSpec OPSX schema migration — would require re-archiving all 78
  changes; not worth the migration cost.
- Monorepo mode (`monorepo_root = true`) — would touch every sub-package;
  deferred to a follow-up.
- LSP/formatter plugin config in opencode.json — independent concern.
- Custom `.opencode/commands/*.md` files — deferred to a follow-up change.
- `opencode.json` → `opencode.jsonc` migration — comment support is a
  nice-to-have, not a refactor driver.

## Dependencies

- **Blocked by:** none
- **Blocked by (soft):** `2026-08-15-knowledge-sync-loop-v1` (the
  `sync:all` orchestrator references the mise task names that this change
  preserves as aliases for 1 release cycle)
- **Affected repos:** cianfhoghlaim (no cross-repo changes; the
  `leabharlann` and `bonneagar` worktrees are not touched)

## Acceptance criteria

1. `bash .agents/skills/lint-skills.sh` exits 0 with ≥65 skills passing
2. `mise run lint:guides-yml` exits 0 with ≥30 guides (3 new)
3. `openspec validate --all --strict --no-interactive` exits 0 with
   130+ items (was 129 + 1 new spec)
4. `mise run lint` exits 0 (ruff + skills + registry linters)
5. `mise run doctor` exits 0
6. `mise run openspec:validate-all` (new task) exits 0
7. `grep -E '"tools":\s*\{' opencode.json` returns 0 matches
8. `find .opencode/agents -name "*.md" | wc -l` returns ≥9
9. `grep -E '^\[tasks\."' mise.toml | wc -l` returns ≤100 (was 329)
10. `mise run sync:all` exits 0 (sync layers still work after refactor)

## Rollback plan

Each phase is a single git commit. Rollback via
`git revert --no-commit HEAD~N..HEAD` for any N phases. The openspec
change itself can be `rm -rf`'d before archive; after archive, requires a
follow-up openspec change.

## Cross-references

- `openspec/specs/knowledge-sync-loop/spec.md` — the sync:all gate
- `openspec/specs/indexing-and-cognition/spec.md` — CCC indexes these
  new files
- `openspec/specs/agent-platform-cluster/spec.md` — opencode agents + MCPs
- `openspec/specs/centralized-registry/spec.md` — model + schema
  registries (referenced from new agent prompts)
- `.agents/skills/mise/SKILL.md` (new)
- `.agents/skills/opencode/SKILL.md` (new)
- `.agents/skills/openspec/SKILL.md` (new)
