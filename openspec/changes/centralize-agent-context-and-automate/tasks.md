# Tasks — Centralize Agent Context + Automate

## Phase 4 — Cognee v1: Postgres+pgvector consolidation

- [ ] 4.1 Verify `infrastructure/stacks/cognee/compose.yaml` uses `VECTOR_DB_PROVIDER: pgvector` + `DB_PROVIDER: postgres` + `GRAPH_DATABASE_PROVIDER: postgres` (no code change expected)
- [ ] 4.2 Create `infrastructure/scripts/cognee-graph-models/` directory
- [ ] 4.3 Create `infrastructure/scripts/cognee-graph-models/data_platform_graph.py` (DagsterAsset, DltPipeline, LakehouseTable, CocoIndexFlow, LanceDBIndex, SqlMeshModel)
- [ ] 4.4 Create `infrastructure/scripts/cognee-graph-models/infrastructure_graph.py` (KomodoStack, PangolinTunnel, DaggerPipeline, PulumiResource, AnsibleRole)
- [ ] 4.5 Create `infrastructure/scripts/cognee-graph-models/agents_graph.py` (McpServer, AgentTool, LlmAgent, BamlSchema, BrowserSession)
- [ ] 4.6 Create `infrastructure/scripts/cognee-graph-models/ml_graph.py` (FineTunedModel, TrainingDataset, MlflowExperiment, UnslothConfig, LanceDBCollection)
- [ ] 4.7 Create `infrastructure/scripts/cognee-graph-models/celtic_language_graph.py` (LanguageDataset, HuggingFaceModel, GaeltachtBoundary, CensusTable)
- [ ] 4.8 Create `infrastructure/scripts/cognee-graph-models/web_graph.py` (TanStackRoute, ConvexQuery, BetterAuthProvider, EffectService)
- [ ] 4.9 Create `infrastructure/scripts/cognee-graph-models/tuatha_graph.py` (GameAsset, SpacetimeDBTable, X402Payment, NpcCharacter)
- [ ] 4.10 Create `infrastructure/scripts/cognee-ingest-docs.py` (1-call helper that cognifies all 7 clusters)
- [x] 4.11 Verify `opencode.json` `mcp.cognee.env` has exactly the 3 canonical keys (`COGNEE_API_URL`, `COGNEE_API_KEY`, `LLM_API_KEY`) and no `NEO4J_*` keys. **Audit correction**: the cognee MCP env block is already clean; the legacy `NEO4J_*` vars are correctly consumed by the `graphiti` MCP server (which IS the Neo4j service). No code change needed.

## Phase 5 — OpenCode agent scope + skill gate + MCP registry

- [ ] 5.1 Edit `opencode.json` `agent.oideachais` — add `skill_filter: ["dlt", "dagster", "baml", "cognee", "ccc", "oideachais-pipeline", "oideachais-storage", "oideachais-cocoindex-v1", "motherduck"]`
- [ ] 5.2 Edit `opencode.json` `agent.infrastructure` — add `skill_filter: ["stack-ops", "infrastructure-stacks", "secrets-management", "kcg-pangolin-stack", "kcg-locket-sidecar", "kcg-infrastructure-audit", "kcg-bunchloch", "kcg-convergence", "kcg-deploy-runbooks", "pangolin", "komodo", "docker-compose", "dagger", "dagger-pipelines", "pulumi", "kubernetes"]`
- [ ] 5.3 Edit `opencode.json` `agent.meaisinfhoghlaim` — add `skill_filter: ["baml", "litellm", "document-intelligence", "celtic-language-ai", "irish-llm-on-device", "agent-fleet-orchestration", "agent-observability", "kcg-ml-models", "langfuse", "mlflow", "ragas", "cognee", "graphiti", "graphiti-core", "lancedb", "falkordb", "memgraph", "embedding-pipeline", "peft", "trl", "unsloth", "huggingface"]`
- [ ] 5.4 Edit `opencode.json` `agent.croilar` — add `skill_filter: ["tanstack-start", "copilotkit", "hono", "convex", "better-auth", "baml", "dagster", "dlt", "croilar-stream-registry", "croilar-stream-registry", "agentic-frontend-frameworks", "frontend-topology", "webapp-testing"]`
- [ ] 5.5 Edit `opencode.json` `agent.tuatha` — add `skill_filter: ["babylonjs", "tuatha-mmo", "pent-elemental-cosmology", "tuatha-achievement-ledger", "tuatha-mcp-server-tools", "tuatha-platform", "british-isles-formative-assessment", "baml", "dagger", "tanstack-start", "copilotkit", "celtic-language-ai"]`
- [ ] 5.6 Edit `sruth/meaisinfhoghlaim/agents/__init__.py` — add `MODEL_LAYER_AGENTS` tuple (13 .py modules) for canonical registry
- [ ] 5.7 Edit `.agents/skills/INDEXING_AND_COGNITION.md` §3 — update MCP inventory to 10 servers, declare `opencode.json` as the source of truth
- [ ] 5.8 Edit `.agents/skills/INDEXING_AND_COGNITION.md` — add new §8 OpenCode agent + skill + MCP registry section
- [ ] 5.9 Edit `.agents/skills/agent-fleet-orchestration/SKILL.md` — add 1-line cross-link to `indexing-and-cognition` spec

## Phase 6 — CCC v0→v1 retirement + git hooks + CI gate

- [ ] 6.1 Create `scripts/validate-ccc-freshness.ts` — reads `.cocoindex_code/cocoindex.db`, returns exit 1 if stale (>7d main, >24h feature)
- [ ] 6.2 Create `scripts/templates/pre-commit` — the hook template (runs `bun run ccc:index`, best-effort)
- [ ] 6.3 Create `scripts/install-hooks.sh` — idempotent installer that copies the template to `.git/hooks/pre-commit`
- [ ] 6.4 Add `validate-ccc-freshness` + `hooks:install` task aliases to `package.json` + `mise.toml`
- [ ] 6.5 Create `sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md` — document the 2026-07-15 hard-removal timeline + the v1 replacement
- [ ] 6.6 Edit `package.json` `ccc:search` script — add a deprecation warning to stdout before the legacy CLI call
- [ ] 6.7 Edit `mise.toml` `ccc:search` task description — add "(deprecated, see ccc:v1:search)" suffix

## Quality gates

- [ ] 7.1 `openspec validate centralize-agent-context-and-automate --strict` → pass
- [ ] 7.2 `mise run lint:skills` → 123/123 pass (no new skills)
- [ ] 7.3 `bun run validate-ccc-freshness` → exits 0 (current index is fresh)
- [ ] 7.4 `python3 -c "import json; cfg=json.load(open('opencode.json')); print(len(cfg['mcp']), len(cfg['agent']))"` → prints "10 7"
- [ ] 7.5 `ls infrastructure/scripts/cognee-graph-models/*.py | wc -l` → prints 7
- [ ] 7.6 `bash scripts/install-hooks.sh && cat .git/hooks/pre-commit` → prints the hook template
- [ ] 7.7 `git status` → only intended files changed

## Commit + push + archive

- [ ] 8.1 Stage only intended files
- [ ] 8.2 Commit with: `chore(infrastructure): centralize agent context + automate CCC refresh`
- [ ] 8.3 `git pull --rebase && git push`
- [ ] 8.4 `openspec archive centralize-agent-context-and-automate --yes` — archive the change

## Out of scope (deferred)

- Booting the cognee, mlflow, graphiti, falkordb, lakehouse-garage Docker containers (needs Docker daemon on `bunchloch` + Infisical vault seeded)
- Cognifying the 7 clusters into the in-house cognee stack (separate `cognify-clusters` follow-up)
- Hard-deleting the 10 v0 CocoIndex modules in `_v0_archive/` (scheduled for 2026-07-15 in a `ccc-v0-hard-removal` follow-up)
- Per-agent MCP filter (deferred; current change keeps the always-on model)
- RAGAS eval assets for the CCC v1 index (deferred; need ≥ 7 days of stable v1 runs)
- Slack/Discord notification on stale CCC indexes (deferred; CI logs are the first-line check)
