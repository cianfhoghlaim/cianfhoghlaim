# Docs Index — Cianfhoghlaim Reference Corpus

> Navigable directory index for CCC (CocoIndex Code) semantic search and agent context loading.
> Archives of old research and large datasets are stored at `~/.cianfhoghlaim-docs-archive/`.

---

## Top-Level Structure

| Directory | Size | Purpose |
|:----------|:-----|:--------|
| `context/` | 22M | Structured agent context (00-core → 08-examples), mirrors AGENTS.md domain mapping |
| `data_engineering/` | 272M | DE patterns: Dagster, DLT, DuckDB, LanceDB, SQLMesh, Iceberg, MotherDuck, BAML, LakeFS |
| `meaisínfhoghlaim/` | 207M | ML model lifecycle: fine-tuning, OCR, federated learning, Celtic language models |
| `teanga/` | 160M | Irish/Gaelic language technology: HTR, OCR, TTS, corpora, spell-checkers, wordnets |
| `bonneagar/` | 159M | Infrastructure patterns: Pangolin, Komodo, Infisical, Locket, Dagger, Pulumi |
| `tuatha/` | 132M | Educational MMO: game design, crypto/web3, Godot, React Native, Celtic mythology |
| `agents/` | 121M | Agent frameworks & patterns: Agno, Google ADK, BAML, MCP, x402, SIWE |
| `web/` | 81M | Frontend patterns: TanStack Start, Convex, Cloudflare Workers, Hono, oRPC, AG-UI |
| `codebase_indexing/` | 28M | Code search & indexing: ChunkHound, OpenDeepWiki, repo-swarm |
| `marimo/` | 9.8M | Marimo reactive notebook examples: AI, SQL, Cloudflare, UI, math, layouts |
| `docs_examples_consolidated/` | 2.3M | Consolidated example projects (api-unified, cloudflare-unified, etc.) |
| `hackathons/` | 1.7M | Hackathon research & submissions |
| `openspec/` | 96K | OpenSpec tooling research |
| `dashboards/` | 140K | Dashboard screenshots (Dagster UI) |
| `images/` | 216K | Visual assets (Dagster UI, MotherDuck UI) |
| `screenshots/` | 1.5M | Browser screenshots |
| `media/` | 52K | Media analysis |
| `ui-inspiration/` | 12K | UI design guide (screenshots archived) |
| `chrome-devtools-mcp/` | 332K | Chrome DevTools MCP reference (pruned to essentials) |

---

## Critical Agent Context

### `context/` — Structured Domains
- `00-core/` — Project identity, mission, licensing
- `01-patterns/` — Design patterns, architecture decisions
- `02-architecture/` — System architecture, deployment topology
- `03-pipelines/` — Data pipelines, ETL/ELT patterns
- `04-agents/` — Agent orchestration, MCP servers
- `05-celtic-language/` — Irish/Gaelic language resources
- `06-infrastructure/` — Multi-cloud, Pangolin, Komodo
- `07-skills/` — Agent skill documentation
- `08-examples/` — Code examples, integration patterns

### `docs/data_engineering/` — Key Assets
- `dagster/` — Dagster asset patterns, workspace configs
- `dlt/` — DLT pipeline patterns, filesystem & REST sources
- `data-engineering/` — Internal reference: BigQuery → Dagster → DuckDB → MotherDuck → dbt → Evidence
- `lakefs/` — LakeFS integration patterns (Iceberg, Delta Lake, ML)
- `lance/` — LanceDB patterns: hybrid search, ColPali, multimodal
- `ducklake/` — DuckLake lakehouse patterns
- `baml/` — BAML extraction DSL patterns
- `cocoindex/` — CocoIndex flow patterns
- `sqlmesh-ibis/` — SQLMesh + Ibis transformation patterns
- `semantic_layer/` — Semantic layer patterns (Cube, boring-semantic-layer)
- `geoai/` — Geospatial AI patterns

### `docs/bonneagar/` — Preserved OSS Integration Context
Each preserved OSS clone has a `SKILL_CONTEXT.md` explaining our integration:
- `pangolin/pangolin/` — Self-hosted reverse proxy with SSO
- `komodo/komodo/` — Multi-server deployment orchestrator
- `infisical/` — Secret management platform
- `locket/locket/` — Secret injection sidecar
- `komodo/ansible-role-komodo/` — Ansible role for Komodo periphery

### `docs/tuatha/game/` — Game Development References
- `react-native-reusables/` — shadcn/ui for React Native
- `react-native-godot/` — Godot engine bridge for React Native
- `x402/MCPay/` — x402 micropayment protocol for MCP
- `gdext/` — Rust bindings for Godot 4

### `docs/agents/` — Agent Framework References
- `agno/agno/` — Agno framework documentation (concepts, examples, integrations)
- `google-adk/` — Google ADK integration patterns
- `browserbase/` — Browserbase automation patterns

---

## Archive Location

Archived content (old research, large datasets, OSS source code) is stored at:

```
~/.cianfhoghlaim-docs-archive/
├── old.tar.gz                          (1.2G — historical research documents)
├── sam3d-objects.tar.gz                (207M — 3D model generation assets)
├── kscanne-tesseract-gle-uncial.tar.gz (175M — OCR training data)
├── kscanne-social-app.tar.gz           (25M)
├── kscanne-voice-web.tar.gz            (26M)
├── kscanne-caighdean.tar.gz            (5.4M)
├── kscanne-kscanne.github.io.tar.gz    (7.7M)
├── kscanne-wordnet-gaeilge.tar.gz      (3.6M)
├── kscanne-gaelg.tar.gz                (3.3M)
├── kscanne-hunspell-gd.tar.gz          (1.7M)
└── kscanne-gaelspell.tar.gz            (2.1M)
```

---

## Search Quick Reference

| What you're looking for | Where to find it |
|:------------------------|:-----------------|
| Dagster asset patterns | `data_engineering/dagster/`, `data_engineering/data-engineering/` |
| DLT pipeline patterns | `data_engineering/dlt/` |
| DuckDB/MotherDuck | `data_engineering/ducklake/`, `data_engineering/data-engineering/` |
| LanceDB vector search | `data_engineering/lance/` |
| Agent framework docs | `agents/`, `context/04-agents/` |
| Infrastructure/GitOps | `bonneagar/`, `context/06-infrastructure/` |
| MMO game design | `tuatha/`, `tuatha/game/` |
| Celtic language AI | `meaisínfhoghlaim/`, `teanga/`, `context/05-celtic-language/` |
| Frontend patterns | `web/`, `web/tanstack/`, `web/convex/` |
| OpenSpec specs | `../openspec/specs/` |
| Agent skills | `../.agents/skills/` |
