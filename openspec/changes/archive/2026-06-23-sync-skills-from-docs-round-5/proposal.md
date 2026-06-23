# Change: sync-skills-from-docs-round-5

## Why

A fifth round of `docs/*` consolidation. The user listed 17
files (6,498 lines total) covering the `01-patterns/` and
`01-platform-architecture/` directories. Four patterns
emerge:

1. **Mostly redundant with just-expanded skills.** `AGENTS.md`
   (282), `DATA_PIPELINE.md` (524), `BONNEAGAR_OVERVIEW.md`
   (482), `m2m-100.md` (54), `TECH_STACK.md` (302) — all
   duplicate content now in `google-adk`, `agno`, `dlt`,
   `dagster`, `lancedb`, `celtic-language-ai`, `stack-ops`,
   `tanstack-start` skills.

2. **KCG-specific patterns missing from skills.** The existing
   `stack-ops`, `pangolin`, `komodo` skills are upstream-vendor
   docs (generic) — they need a KCG-specific rewrite layer.
   `secrets-management.md` (498) and `monorepo-strategy.md`
   (446) document KCG-specific patterns that have no skill.

3. **New skills genuinely needed.** 5 new skills emerge:
   - `embedding-pipeline` — embedding pipeline patterns
     (BatchedEmbeddingService, MultiModelEmbedder, tree-sitter
     code-aware chunking)
   - `agent-observability` — Datadog + MLflow + Langfuse +
     Ragas + structlog unified stack (no current skill)
   - `kubernetes` — Talos + Hetzner + Pulumi K8s (KCG's
     documented but currently Komodo-first)
   - `monorepo` — bun + uv + turbo polyglot patterns
   - `secrets-management` — Infisical + Locket + mise
     three-way contract

4. **Live status snapshots.** `DEPLOYMENT_STATUS.md` (133) and
   `services-roadmap.md` (195) are point-in-time snapshots that
   will rot; they should be deleted (or marked `.superseded`).

## What Changes

### New skills (5)

- `.agents/skills/embedding-pipeline/SKILL.md` — embedding
  pipeline patterns: BatchedEmbeddingService,
  EmbeddingAccumulator, MultiModelEmbedder, semantic +
  code-aware chunking (tree-sitter for `códeolas`),
  HNSW lifecycle.
- `.agents/skills/agent-observability/SKILL.md` — unified
  observability stack: Datadog APM + LLMObs (`@llm`,
  `@agent`, `@workflow`), MLflow, Langfuse, Ragas, structlog.
  The KCG agent layer (Tuatha, croilar, oideachais) is
  monitored end-to-end.
- `.agents/skills/kubernetes/SKILL.md` — Talos + Hetzner +
  Pulumi/OTF K8s (KCG's documented but Komodo-first; 120
  lines).
- `.agents/skills/monorepo/SKILL.md` — bun + uv + turbo
  polyglot monorepo. mise.toml polyglot toolchain, turbo.json
  pipeline, Inner/Outer loop (mise = inner, Dagger = outer),
  "Astral Stack" performance rationale.
- `.agents/skills/secrets-management/SKILL.md` — Infisical
  + Locket + mise three-way contract. Add/rotate secrets,
  Locket sidecar pattern, provider reference (Infisical,
  1Password, Bitwarden).

### Skills rewritten (2)

- `.agents/skills/komodo/SKILL.md` — rewrite from generic
  upstream to KCG-specific: 5-stage deploy procedure, 88-stack
  inventory, `mise run komodo:sync` integration, Resource Sync
  paths.
- `.agents/skills/pangolin/SKILL.md` — rewrite to KCG-specific:
  Pocket ID OIDC, CrowdSec, 6-label Docker pattern with
  `*.cianfhoghlaim.ie` domains, multi-site HA, tunneled
  Periphery access.

### Skills expanded (5)

- `.agents/skills/stack-ops/SKILL.md` — append KCG context:
  Quadrant Model primer (Section 0), technology stack table,
  multi-network isolation, port allocation map, service
  dependency graph, health check patterns, storage architecture,
  deployment order, scripts/stack.sh wrapper.
- `.agents/skills/tanstack-start/SKILL.md` — append "Forms"
  section (TanStack Form + Zod, useForm, zodValidator,
  form.Field render-prop pattern) from `WEB.md` Pattern 2.
- `.agents/skills/celtic-language-ai/SKILL.md` — append
  `facebook/m2m100_418M` row to Translation table (1 line).
- `.agents/skills/lancedb/SKILL.md` — reconcile BGE-M3 vs GaBERT
  (resolve the conflict raised by `EMBEDDINGS.md`).
- `.agents/skills/google-adk/SKILL.md` + `.agents/skills/agno/SKILL.md`
  — append a "Framework comparison" cross-link table at the end.

### Docs to delete (17 files)

- `docs/01-patterns/AGENTS.md` (282) — folded into skills
- `docs/01-patterns/DATA_PIPELINE.md` (524) — folded
- `docs/01-patterns/EMBEDDINGS.md` (651) — promoted to
  `embedding-pipeline` skill
- `docs/01-patterns/OBSERVABILITY.md` (598) — promoted to
  `agent-observability` skill
- `docs/01-patterns/WEB.md` (635) — Forms pattern folded into
  `tanstack-start`
- `docs/01-platform-architecture/BONNEAGAR_OVERVIEW.md` (482)
  — folded into `stack-ops`
- `docs/01-platform-architecture/DEPLOYMENT_STATUS.md` (133)
  — dated snapshot
- `docs/01-platform-architecture/infrastructure-stacks.md`
  (461) — folded
- `docs/01-platform-architecture/komodo-gitops.md` (102) —
  folded into rewritten `komodo` skill
- `docs/01-platform-architecture/kubernetes-deployment.md` (350)
  — promoted to `kubernetes` skill
- `docs/01-platform-architecture/m2m-100.md` (54) — 1 line
  added to `celtic-language-ai`
- `docs/01-platform-architecture/monorepo-strategy.md` (446)
  — promoted to `monorepo` skill
- `docs/01-platform-architecture/pangolin-networking.md` (514)
  — folded into rewritten `pangolin` skill
- `docs/01-platform-architecture/platform-overview.md` (271)
  — folded into `stack-ops` Section 0
- `docs/01-platform-architecture/secrets-management.md` (498)
  — promoted to `secrets-management` skill
- `docs/01-platform-architecture/services-roadmap.md` (195)
  — dated snapshot
- `docs/01-platform-architecture/TECH_STACK.md` (302) —
  cross-link from `tanstack-start`

### Project rules PRESERVED (not changed)

- All KCG deployment patterns — preserved
- The 3-way secret contract — preserved
- The 6-label Pangolin pattern — preserved
- All monorepo / mise.toml conventions — preserved

## Impact

- **Affected specs (1)**: `infrastructure-stacks` adds 2 new
  requirements (embedding-pipeline + monorepo-as-infrastructure);
  `agent-observability` adds 1 new requirement (Datadog +
  Ragas + Dagster asset_check integration)
- **Affected code**: none. Skills are documentation.
- **Affected skills** (12 total): 5 new + 2 rewritten + 5 expanded

## Success criteria

- `openspec validate sync-skills-from-docs-round-5 --strict`
  passes
- The 5 new skills exist at
  `.agents/skills/{embedding-pipeline,agent-observability,
  kubernetes,monorepo,secrets-management}/SKILL.md`
- The 2 rewritten skills (`komodo`, `pangolin`) are KCG-specific
- The 5 expanded skills have new sections
- The 17 listed docs files are removed

## Rollback

Skills-only. Rollback = restore the 17 docs files from git.
No data, code, or runtime state is affected.
