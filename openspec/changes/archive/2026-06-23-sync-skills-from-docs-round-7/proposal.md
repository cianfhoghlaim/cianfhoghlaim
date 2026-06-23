# Change: sync-skills-from-docs-round-7

## Why

A seventh round of `docs/*` consolidation. The user asked
to process `docs/06-infrastructure/` (125 .md files,
~7.2 MB), explicitly ignoring 1Password references (KCG has
moved to Infisical). The 5 prior rounds established a
pattern: identify content worth keeping, absorb it into
existing or new skills, delete the source.

This round is the **biggest so far** because `06-infrastructure/`
is the largest doc directory and the majority of files are
**upstream tool reference material** that was scraped (not
authored) and is now obsolete in light of the round-5
`stack-ops`, `komodo`, `pangolin`, `secrets-management`,
`dagger`, `monorepo`, `pulumi`, `cloudflare`, `docker-compose`
skills.

Four new skill gaps emerge:

1. **Bunchloch convergence architecture** — the 3-tier host
   topology (arm1-oci control / cax41-hetzner storage /
   bunchloch M4 workload) is described in `bunchloch.md` but
   no current skill captures it. The `pangolin` skill has the
   2-tier version; the `stack-ops` skill has the GOLD_STANDARD
   pattern; neither has the **multi-host** convergence reality.

2. **Leabharlann end-to-end pipeline** — the 5-stage PDF flow
   (secret injection → DLT SHA-256 scan → BAML extraction →
   CocoIndex v1 embedding → Cognee cognify) is documented in
   `leabharlann-stack-overview.md`. The `oideachas-pipeline`
   skill has the conceptual model but not the runtime flow.

3. **ML models registry + fallback chains** — the 70+ model
   catalog + 5 fallback chains (`vision: glm-4.6v-flash →
   qwen3-vl → moondream2`, etc.) is in `ML_MODELS_REGISTRY.md`.
   The `celtic-language-ai` skill has 6 langs × 4 tasks but
   not the full ML orchestration layer.

4. **6 docker-compose categories** — the leabharlann doc
   enumerates the 6 categories (control plane / storage /
   engineering / machine_learning / tools / browser) and
   which stacks sit in each. The `stack-ops` skill has the
   GOLD_STANDARD file pattern but not the category map.

The 1Password carve-out is clean: 5 dedicated files
(`Get started with a 1Password Connect server…`,
`integrating-1password-cli-connect-komodo-ansible-deployment.md`,
`integrating-1password-cli-komodo-ansible-deployment.md`,
`pulumi-typescript-guide-provisioning-cloudflare-d1-r2-1password-integration.md`,
`where-to-install-1password-cli-op.md`) plus the 1Password
provider section in `secrets-management/SKILL.md` (which
will be rewritten against Infisical only). The remaining
files have incidental 1Password references that the user
asked us to ignore.

## What Changes

### New skills (4)

- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier host
  convergence model. arm1-oci (control plane: Komodo +
  Pangolin + Pocket ID + CrowdSec), cax41-hetzner (storage:
  Garage + Lakekeeper + MotherDuck), bunchloch M4 (workload:
  Dagster + LiteLLM + CocoIndex). Component directory
  structure (`infrastructure/bunchloch/`), service
  relationships (Komodo↔Periphery, Pangolin↔Newt/OLM,
  Locket→Infisical), startup order, ports table.

- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` — the
  canonical 5-stage PDF flow. Stage 1 (secret injection
  via Komodo+Infisical+Locket), Stage 2 (DLT filesystem scan
  with SHA-256 dedup via FileHashTracker), Stage 3 (BAML
  extraction via ExtractEn/ExtractEnStrong), Stage 4
  (CocoIndex v1 embedding with BGE-large-en-v1.5), Stage 5
  (Cognee cognify + cross-archive edges). Includes the
  `rest://lance-api.cianfhoghlaim.ie:8181/leabharlann_zotero`
  output URL and the 6 docker-compose layer integration.

- `.agents/skills/kcg-ml-models/SKILL.md` — the 70+ model
  registry + 5 fallback chains. The 3 backends (GGUF /
  llama-swap :8080, MLX / mlx-omni-server :10240,
  safetensors / invokeai :9090), the 11 categories (OCR,
  Vision, Retrieval, Image Gen, Segmentation, Geospatial,
  Audio, Celtic LLMs, Celtic Encoders, Celtic Speech,
  General), the llama.cpp router mode (LRU eviction,
  on-demand loading), and the LiteLLM `litellm://` routing
  pattern from `orchestration-infrastructure.md`.

- `.agents/skills/kcg-convergence/SKILL.md` — the cross-host
  topology and the 6 docker-compose categories. Per
  `leabharlann-stack-overview.md` §"How the 6 docker-compose
  layers integrate" + `infrastructure/AGENTS.md`:
  1. Control plane (Pangolin, Komodo, PlanetScale, MotherDuck,
     R2, Pulumi, Forgejo)
  2. Storage (Garage, Lakehouse, LakeFS, Beszel)
  3. Engineering (LiteLLM, Dagster, oideachais, Convex,
     Windmill, n8n, Coder, DevDocs, MCPJungle)
  4. Machine learning (Cognee, Graphiti, Langfuse, MLflow,
     Qdrant, Memgraph, FalkorDB, LanceDB, olake, lmnr,
     logfire, nimtable)
  5. Tools (17 productivity / media / dev utilities)
  6. Browser (automation)

  Plus the port allocation map (3000-3499 user apps,
  3500-3999 APIs, 4000-4499 Dagster, 5000-5499 data,
  6000-6999 AI/ML, 7000-7999 dev, 8000-8999 MMO,
  9000-9999 infra).

### Skills expanded (5)

- `.agents/skills/stack-ops/SKILL.md` — add the
  "6 docker-compose categories" map from the leabharlann
  doc; the per-category stack inventory.

- `.agents/skills/pangolin/SKILL.md` — add the 3-tier
  convergence zones (replace the 2-tier section); the
  cax41-hetzner storage tier; the Pocket ID as the OIDC
  bridge across tiers.

- `.agents/skills/oideachais-storage/SKILL.md` — add the
  Lance vs Iceberg dual-format strategy (Lance for
  AI/multimodal, Iceberg-via-Lakekeeper for BI/analytics)
  from `From BI to AI_ A Modern Lakehouse Stack with Lance
  and Iceberg.md`.

- `.agents/skills/dagster/SKILL.md` — add the
  21-asset-module / 7-group inventory + the 5-stage
  leabharlann asset materialisation order.

- `.agents/skills/secrets-management/SKILL.md` — rewrite
  the provider section to Infisical-only; drop the
  1Password + 1Password Connect + Bitwarden mentions.
  Cite the migration history (1Password → Infisical
  2026-06) in a footnote.

- `.agents/skills/celtic-language-ai/SKILL.md` — add the
  KCG production model fallback chains from
  `ML_MODELS_REGISTRY.md` (`celtic_irish: qomhra-mistral →
  uccix → britllm`, etc.).

### Docs to delete (~75 files)

1Password carve-out (5 files, no KCG content):
- `Get started with a 1Password Connect server _ 1Password Developer.md`
- `integrating-1password-cli-connect-komodo-ansible-deployment.md`
- `integrating-1password-cli-komodo-ansible-deployment.md`
- `pulumi-typescript-guide-provisioning-cloudflare-d1-r2-1password-integration.md`
- `where-to-install-1password-cli-op.md`

Upstream-tool material absorbed by skills (~50 files):
- `komodo.md`, `komodo-api-summary.md`, `komodo-deployment.md`,
  `komodo-openapi-research.md`, `KOMODO_COMPLETE_GUIDE.md`
  (trim), all `komodo/*.md` sub-files (~20)
- `pangolin.md`, `pangolin-patterns.md`, all `pangolin/*.md`
  sub-files (~20)
- `cloudflare.md`, `cloudflare-r2.md`, all
  `cloudflare-*-research.md`, `cloudflare-backpine-summary.md`
- `docker-compose.md`, `docker-compose-patterns.md`,
  `Docker Provider.md`
- `dagger-unified-pipeline-architecture.md`,
  `dagger-pipeline-orchestration-komodo-pangolin-fullstack-deployment.md`,
  `dagger-docker-compose-workflow-komodo-periphery-pangolin-newt-olm.md`,
  `integrating-dagger-polyglot-monorepo-ci-cd-workflow.md`,
  `DAGGER_PATTERNS_ANALYSIS.md`
- `pulumi-infrastructure-as-code.md`, `pulumi.md`,
  `pulumi_1.md`, `Docker Provider.md` (dup),
  `Provision Resources on Hetzner Cloud with Pulumi.md`
- `Self-Hosted Stack Visualization & Management.md`,
  `Unified Scraping Swarm Stack Optimization.md`,
  `Open-Source Crawl4ai Anti-Bot Stack.md`,
  `Web-Scraping-Architecture-Analysis.md`
- `hosting-litellm-pangolin-public-vs-private-access-models.md`,
  `lancedb.md`, `memgraph.md`, `FROM BI TO AI_ A Modern
  Lakehouse Stack with Lance and Iceberg.md`
- `OPENSPEC_README.md`, `OPENSPEC_ANALYSIS.md.superseded`,
  `OPENAPI_SPECS_SUMMARY.md`, `INDEX.md`, `INDEX1.md`,
  `TECH_STACK.md`, `update-specs.md`
- `Using MCP in Roo Code _ Roo Code Documentation.md`
- `High-Availability Kubernetes on Hetzner with Talos 1.11.md`
- `FROM BI TO AI_ A Modern Lakehouse Stack with Lance and
  Iceberg.md`, `FROM BI TO AI_ A Modern Lakehouse Stack
  with Lance and Iceberg.md`
- All `*.superseded` files (already superseded):
  `ARCHITECTURE.md.superseded`, `Backend Strategy…superseded`,
  `Crawl4ai Scraping…superseded`, `DAGGER_GUIDE_INDEX.md.superseded`,
  `DAGGER_QUICK_REFERENCE.md.superseded`, `DECISION_MATRICES.md.superseded`,
  `ML_STACK.md.superseded`, `New in llama.cpp…superseded`,
  `OPENSPEC_ANALYSIS.md.superseded`,
  `Open-Source Web Scraping Architecture Analysis.md.superseded`,
  `infrastructure-tools.md.superseded`, `overview.md.superseded`,
  `data-acquisition.md.superseded`, `development-tools.md.superseded`

KCG content absorbed by new skills (~15 files):
- `bunchloch.md` → `kcg-bunchloch` skill
- `leabharlann-stack-overview.md` → `kcg-leabharlann-pipeline` skill
- `ML_MODELS_REGISTRY.md` → `kcg-ml-models` skill
- `apple-silicon-deployment.md` + `apple-silicon-deployment_1.md`
  → `kcg-ml-models` skill (the M4 Mac deployment playbook)
- `orchestration-infrastructure.md` → `kcg-ml-models` skill
- `celtic-platform.md` → split: §1-§3 to `celtic-language-ai`
  skill, §"Technical Architecture for Bilingual Math" to
  `irish-edtech` skill, the rest upstream (delete)
- `education-kg.md` → split: §1-§2 to `celtic-language-ai`,
  §3 upstream (delete)
- `engineering.md` → split: §1-§3 to `celtic-language-ai`,
  the rest upstream (delete)
- `celtic_ml_models.yaml`, `models_registry.yaml` → keep
  (live config, not docs)
- `cognee-entity-resolution.md` → expand `cognee` skill
- `graphiti-crypto-adaptation.md` → expand `graphiti` skill
- `gaelic-heritage-pipeline.md` → expand `celtic-language-ai`
- `gaois-api-reference.md` → keep as live reference
- `acquisition-pipeline.md`, `bilingual-scraper-implementation.md`
  → expand `oideachas-pipeline`
- `agentic-scraping-architecture.md` → expand `browser` skill
- `comparing-approaches-pangolin-registration-komodo-deployment.md`
  → expand `komodo` skill
- `generating-typescript-client-pangolin-api-openapi-spec.md`
  → expand `pangolin` skill
- `extending-komodo-pr-deploy-pangolin-integration-komodo-actions.md`
  → expand `komodo` skill
- `komodo/Komodo FAQ, Tips, and Tricks.md` → expand `komodo` skill
- `knowledge-graph-infrastructure.md` → expand `cognee` +
  `graphiti` skills

Live configs (NOT docs, kept verbatim):
- `auto-deploy-stacks.toml`, `compose.yaml`,
  `docker-compose(1).yaml`, `celtic_ml_models.yaml`,
  `models_registry.yaml`, `crawlai_vs_firecrawl.py`,
  `crypto_analysis_example.py`, `embedding_vs_statistical.py`,
  `llm_config_example.py`, `llm_extraction_openai_pricing.py`,
  `scraping_strategies_performance.py`, `summarize_page.py`,
  `docker_hooks_examples.py`, `docker_python_sdk.py`,
  `docker_webhook_example.py`, `demo_multi_config_clean.py`

Trivial or out-of-scope (delete, no skill extraction):
- `Register a GCP Instance.md`, `Register a Hetzner Server.md`,
  `termix.md`, `web-tech-tutorials-and-examples.md`,
  `Resource Maximization and Project Planning.md`,
  `SETUP.md` (1Password-only, 425 lines of `op` recipes),
  `SECRETS_MANAGEMENT_GUIDE.md` (predecessor to skill),
  `infrastructure-devops.md` (1Password-heavy, 1666 lines),
  `pan-celtic-scraping.md`, `pan-celtic-scraping.md`,
  `policy-frameworks.md`, `teacher-supply.md`,
  `unified-model-comparison.md`, `scottish-gaelic-resources.md`,
  `welsh-resources.md`, `irish-nlp-resources.md`,
  `parallel-corpus-sources.md`, `tmx-processing.md`,
  `alignment-tools.md`, `model-finetuning-strategy.md`,
  `vlm-ocr-comparison.md`, `web-scraping-automation.md`,
  `deploy.md`, `debug.md`, `automation_readme.md`,
  `acquisition-pipeline.md`, `irish-archives-workflow.md`,
  `backend.md`, `frontend-integration.md`,
  `enrollment-statistics.md`, `education-subject-inventory.md`,
  `Leaving Certificate Subject Analysis Plan.md`,
  `infrastructure-knowledge-graph.md`

## Impact

- **Affected specs (1)**: `infrastructure-stacks` adds 2 new
  requirements (6 docker-compose categories + 3-tier
  convergence zones)
- **Affected code**: none. Skills are documentation.
- **Affected skills** (10 total): 4 new + 6 expanded
- **Affected 1Password provider section** in
  `secrets-management/SKILL.md`: removed

## Success criteria

- `openspec validate sync-skills-from-docs-round-7 --strict`
  passes
- The 4 new skills exist at
  `.agents/skills/{kcg-bunchloch,kcg-leabharlann-pipeline,
  kcg-ml-models,kcg-convergence}/SKILL.md`
- The 6 expanded skills have new sections
- The ~75 listed docs files are removed
- `secrets-management/SKILL.md` no longer references 1Password

## Rollback

Skills-only. Rollback = restore the ~75 docs files from git.
No data, code, or runtime state is affected.
