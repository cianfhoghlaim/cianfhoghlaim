# Change: centralize-agent-context-and-automate

> **Change 3 of 3 in the observability + graph + agent-context
> consolidation series.** Anchors to the new
> `indexing-and-cognition` capability spec. Implements Phase 4
> (Cognee v1), Phase 5 (OpenCode agent scope), and Phase 6 (CCC
> v0→v1 retirement + git hooks + CI gate) of the audit's findings.

## Why

The 2026-06-26 audit identified four structural gaps in the
agent-context stack:

1. **CCC v0 → v1 retirement is incomplete** — 10 deprecated v0
   modules still live in `cocoindex_flows/_v0_archive/`; the
   `ccc search` CLI is still wired; no hard retirement scheduled.
2. **No CCC index-freshness CI gate** — the 2.1 GB SQLite index
   silently degrades when it goes stale.
3. **No git hook for CCC refresh** — a pre-commit hook (best-effort)
   that calls the freshness check would surface staleness early.
4. **Cognee v1 transition to Postgres+pgvector is partially
   wired** — the 7 cluster `graph_model_file`s documented in
   `INDEXING_AND_COGNITION.md` §2.3 do not exist on disk.
5. **OpenCode agent + skill + MCP registry is over-scoped** — all
   7 agents see all 123 skills; the 10 MCP servers are not
   documented as the canonical inventory anywhere.

## What Changes

### Phase 4 — Cognee v1: Postgres+pgvector consolidation

- **`infrastructure/stacks/cognee/compose.yaml`**: confirm
  `VECTOR_DB_PROVIDER: pgvector`, `DB_PROVIDER: postgres`,
  `GRAPH_DATABASE_PROVIDER: postgres`, single `cognee-postgres`
  service. (No code change — the audit confirmed this is
  already wired correctly.)
- **`opencode.json` `mcp.cognee.env`**: confirm the env block
  has exactly the 3 canonical keys (`COGNEE_API_URL`,
  `COGNEE_API_KEY`, `LLM_API_KEY`) and no `NEO4J_*` keys. (No
  code change — the audit confirmed this is already wired
  correctly; the requirement is a guard against future
  regressions.)
- **`infrastructure/scripts/cognee-graph-models/`** (NEW dir,
  7 files): the 7 `graph_model_file`s for the 7 typed cognify
  clusters — `data_platform_graph.py`,
  `infrastructure_graph.py`, `agents_graph.py`, `ml_graph.py`,
  `celtic_language_graph.py`, `web_graph.py`, `tuatha_graph.py`.
  Each file declares the entity types (nodes) + edge types
  (relationships) for its cluster, matching the 7-cluster table
  in `.agents/skills/INDEXING_AND_COGNITION.md` §2.3.
- **`infrastructure/scripts/cognee-ingest-docs.py`** (NEW):
  1-call helper that ingests all 7 clusters into the in-house
  cognee stack: `cognify --datasets docs-data-eng,docs-bonneagar,
  docs-agents,docs-ml,docs-teanga,docs-web,docs-tuatha`.

### Phase 5 — OpenCode agent scope + skill gate + MCP registry

- **`opencode.json`**: add the `skill_filter` field to each
  sruth-subagent (oideachais, infrastructure, meaisinfhoghlaim,
  croilar, tuatha), limiting each to the skills that are
  actually relevant to its quadrant. The `build` and `plan`
  agents keep the no-filter behaviour (they need every skill).
- **`opencode.json` `mcp.cognee.env`**: drop the legacy
  `NEO4J_*` env vars (Phase 4 cleanup that also touches
  `opencode.json`).
- **`.agents/skills/INDEXING_AND_COGNITION.md` §3**: update
  the MCP inventory table to list 10 servers
  (browserbase, firecrawl, infisical, motherduck, chrome,
  cocoindex-code, cognee, graphiti, langfuse, croilar-devtools),
  declare the canonical registry at `opencode.json` as the
  source of truth, and document the agent + skill + MCP
  loading contract.
- **`.agents/skills/agent-fleet-orchestration/SKILL.md`** (1
  line): add a cross-link to the new
  `indexing-and-cognition` spec.
- **`sruth/meaisinfhoghlaim/agents/__init__.py`**: re-export the
  13 model-layer agents in a `MODEL_LAYER_AGENTS` tuple
  (canonical registry at the import surface, per the audit
  finding that the inventory was implicit).

### Phase 6 — CCC v0 → v1 retirement + git hooks + CI gate

- **`scripts/validate-ccc-freshness.ts`** (NEW): a CI gate that
  reads `.cocoindex_code/cocoindex.db` and returns exit 1
  (with a clear message) when the index is older than the
  threshold (default 7 days main, 24h feature).
- **`package.json` + `mise.toml`**: add the
  `validate-ccc-freshness` task alias.
- **`.git/hooks/pre-commit`** (NEW): a best-effort pre-commit
  hook that runs `bun run ccc:index` (incremental refresh,
  <10s) on staged files. The hook is `best-effort` — it warns
  but never blocks the commit.
- **`scripts/install-hooks.sh`** (NEW): idempotent installer
  that copies `.git/hooks/pre-commit` from a checked-in
  template at `scripts/templates/pre-commit`. Re-runs safely.
- **`scripts/templates/pre-commit`** (NEW): the hook template
  (the file installed by `scripts/install-hooks.sh`).
- **`sruth/oideachais/cocoindex_flows/_v0_archive/`**:
  schedule the 10 deprecated v0 modules for deletion on
  2026-07-15 (matches the existing `ccc` deprecation banner in
  `mise.toml`). Add a `DEPRECATED.md` file at the root of
  `_v0_archive/` that documents the retirement timeline +
  points at the v1 replacement.
- **`package.json` + `mise.toml`**: change
  `ccc:search` to print a deprecation warning ("use
  `ccc:v1:search` instead") but keep the legacy `ccc search`
  CLI call as the fallback. The 2026-07-15 hard-removal is
  deferred to a follow-up change.

## Impact

- **Affected specs:**
  - NEW `indexing-and-cognition` (this change's anchor)
  - `cocoindex-v1-migration` (gains 1 ADDED Requirement: CCC
    v0 retirement timeline)
  - `agent-memory-systems` (1 MODIFIED Requirement: Cognee
    graph model files canonical location)
  - `meaisinfhoghlaim-agent-frameworks` (1 ADDED Requirement:
    13-agent model-layer registry at
    `sruth/meaisinfhoghlaim/agents/__init__.py`)
- **Affected code:**
  - `opencode.json` — drop 3 `NEO4J_*` env vars; add
    `skill_filter` to 5 sruth-subagents
  - `infrastructure/scripts/cognee-graph-models/*.py` — NEW
    (7 files)
  - `infrastructure/scripts/cognee-ingest-docs.py` — NEW
  - `scripts/validate-ccc-freshness.ts` — NEW
  - `scripts/install-hooks.sh` — NEW
  - `scripts/templates/pre-commit` — NEW
  - `.git/hooks/pre-commit` — NEW (the installed hook;
    gitignored by default but the installer copies it from
    the template)
  - `sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md` — NEW
  - `sruth/meaisinfhoghlaim/agents/__init__.py` — add
    `MODEL_LAYER_AGENTS` tuple
  - `package.json` + `mise.toml` — 2 new task aliases
    (`validate-ccc-freshness`, `hooks:install`)
- **Affected agent skills:**
  - `.agents/skills/INDEXING_AND_COGNITION.md` — §3 MCP
    inventory updated to 10 servers; new §8 OpenCode agent
    scope/skill/MCP registry section
  - `.agents/skills/agent-fleet-orchestration/SKILL.md` — 1
    line cross-link
- **Affected CI:**
  - `mise run lint:skills` — passes (no new skills)
  - `bun run validate-ccc-freshness` — new gate, can fail
    (intentionally) on stale indexes
  - `mise run py:typecheck` — covers the new
    `infrastructure/scripts/cognee-graph-models/*.py` modules
  - `mise run turbo typecheck` — unchanged

## Non-Goals

- This change does **not** boot the cognee, graphiti, mlflow, or
  falkordb Docker containers. Deploy is a separate operational
  task that needs the Docker daemon on `bunchloch` and the
  Infisical vault to be seeded (`bun run scripts/init-vault.ts`).
- This change does **not** cognify the 7 clusters into the
  in-house cognee stack (that's a separate `cognify-clusters`
  follow-up). The `cognee-ingest-docs.py` helper is added but
  not run.
- This change does **not** hard-delete the 10 v0 CocoIndex
  modules in `sruth/oideachais/cocoindex_flows/_v0_archive/`.
  The hard-deletion is scheduled for 2026-07-15 in a follow-up
  change (`ccc-v0-hard-removal`).
- This change does **not** wire up RAGAS eval assets for the
  CCC v1 index. That's a separate `ragas-ccc-eval` change
  once we have ≥ 7 days of stable v1 runs to compare against.
- This change does **not** add a Slack/Discord notification
  for stale CCC indexes. The `validate-ccc-freshness` script
  exits with a clear message; ops catches it from the CI
  logs.

## Open Questions

- **Should the `croilar-devtools` MCP server be in the
  always-on list?** The current proposal keeps all 10 servers
  always-on. If we wanted to scope MCPs by sruth (similar to
  `skill_filter`), we'd add a per-agent `mcp_filter`. Deferred
  to a follow-up; the current change keeps the existing
  "always-on" model.
- **Should the 7 cluster graph model files be Python or
  Cognee-specific JSON?** Python (with TypedDict-style
  declarations) for tooling-ability — matches the existing
  `infrastructure/scripts/` pattern.

## Validation Plan

```bash
# 1. openspec validate --strict
openspec validate centralize-agent-context-and-automate --strict

# 2. New spec exists
openspec list --specs | grep indexing-and-cognition

# 3. mise run lint:skills
mise run lint:skills

# 4. validate-ccc-freshness gate works
bun run validate-ccc-freshness  # should exit 0 (index is fresh)

# 5. cognee compose still uses pgvector
grep VECTOR_DB_PROVIDER infrastructure/stacks/cognee/compose.yaml
# Should print: VECTOR_DB_PROVIDER: pgvector

# 6. opencode.json: 10 MCP servers + 7 agents
python3 -c "import json; cfg=json.load(open('opencode.json'));
print('MCPs:', len(cfg['mcp'])); print('Agents:', len(cfg['agent']))"
# Should print: MCPs: 10, Agents: 7

# 7. 7 cluster graph model files exist
ls infrastructure/scripts/cognee-graph-models/*.py | wc -l
# Should print: 7

# 8. pre-commit hook installs
bash scripts/install-hooks.sh
cat .git/hooks/pre-commit  # should print the hook template
```

## Migration Plan

1. **Step 1**: write this proposal + tasks + spec delta.
2. **Step 2**: validate --strict.
3. **Step 3**: implement in 3 phases (4 → 5 → 6). Each phase
   ends with a self-contained commit (no monolithic PR).
4. **Step 4**: `mise run lint:skills` + `openspec validate
   centralize-agent-context-and-automate --strict` + the 8
   checks in the validation plan.
5. **Step 5**: commit + push + archive.

## Risk

- **Low risk.** No production runtime is touched. The
  pre-commit hook is best-effort and never blocks. The CCC
  v0 retirement is a documentation + comment update, not a
  code change. The MCP server list change is a no-op
  (NEO4J_* env vars are simply ignored by the cognee MCP
  client).
- **Medium risk on the skill_filter change.** If a sruth
  subagent's `skill_filter` accidentally excludes a skill it
  needs, the agent's quality degrades silently. Mitigation:
  the `build` and `plan` agents keep the no-filter behaviour
  (they're the escape hatch). The sruth subagent prompts
  explicitly list the skills they need.
- **Medium risk on the cognee-ingest-docs.py helper.** If the
  graph model files have a typo (e.g. wrong entity name),
  cognify will silently build a bad graph. Mitigation: the
  helper is documented as a "run-once-on-fresh-stack" tool;
  the graph is rebuilt from scratch on every run.
