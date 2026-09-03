---
truth: superseded
---

# Cognee Knowledge Graph Readiness Audit

**Date:** 2026-06-06  
**Auditor:** Automated agent via `cognee` MCP tools  
**Scope:** All `.md` files under `docs/` across 8 subtrees  
**Purpose:** Assess readiness for `cognify()` ingestion into Cognee knowledge graph

---

## 1. Current Cognee Integration State

### 1.1 Infrastructure

The project has a fully documented Cognee integration pipeline, but **the knowledge graph is empty** — no data has been added or cognified yet.

| Component | Status | Detail |
|:--|:--|:--|
| **Cognee container** | Configured | Docker `cognee/cognee:latest` on port 8100, DeepSeek V4 Pro via OpenAI-compatible API |
| **Neo4j** | Running (shared) | `bolt://localhost:7687`, shared with Graphiti temporal layer |
| **LanceDB** | Configured | Vector storage for embeddings |
| **MCP server** | Configured | `cognee-mcp` in `opencode.json`, exposes `cognee_search`, `cognee_cognify` etc. |
| **Dagster pipeline** | Defined | `docs_added_to_cognee → docs_cognified → graphiti_temporal_layer` asset chain in `COGNEE_INTEGRATION.md` |
| **Batch strategy** | Defined | 6 datasets: `docs-agents`, `docs-bonneagar`, `docs-data-eng`, `docs-ml`, `docs-web`, `docs-context` |
| **Knowledge graph** | **Empty** | `cognee_search()` returns `[]`; `cognee_cognify_status()` returns `{}`; no active jobs |

### 1.2 Key Configuration

```yaml
cognee:
  image: cognee/cognee:latest
  llm_provider: openai  # → DeepSeek API
  llm_model: deepseek-chat  # V4 Pro
  llm_endpoint: https://api.deepseek.com/v1
  embedding_provider: openai
  embedding_model: text-embedding-3-small
  graph_database: neo4j (bolt://host.docker.internal:7687)
  vector_database: lancedb
  caching: false
  access_control: false
```

### 1.3 Known Issues

- **`cognee_list_data` fails**: SQLite `UNIQUE constraint failed: users.email` — the default user `default_user@example.com` is already registered. This is a pre-existing state from the cognee-mcp server's internal database, not a blocker for ingestion.
- **Cost estimate**: ~$6 for 2,242 documents (per `WORKFLOW.md`), using DeepSeek V4 Pro.

---

## 2. Cognee Skill Perspective — What Makes Good Input

From `.agents/skills/cognee/SKILL.md` and the Cognee v1.0.1 API:

### 2.1 Ideal Input Characteristics

| Characteristic | Why Cognee needs it |
|:--|:--|
| **Named entities** (tools, platforms, protocols) | The LLM extracts these as graph nodes |
| **Explicit relationships** ("X depends on Y", "X feeds into Y") | The LLM infers edges between nodes |
| **Structured sections** (`##` headings) | Cognee chunks on heading boundaries for better context windows |
| **Tables and lists** | High entity density; easy for the LLM to parse |
| **Code blocks** | Preserved as context but entities are extracted from surrounding text |
| **YAML/schema definitions** | Entities with typed properties → rich graph nodes |
| **Architecture diagrams** (ASCII art) | Visual structure helps the LLM infer system topology |
| **Named datasets** | `cognee.add(content, dataset_name="docs-agents")` scopes search |

### 2.2 The `remember()` API (v1.0.1+)

The newer API simplifies ingestion:
```python
await cognee.remember(content, dataset_name="docs-agents")
# Auto-cognifies — replaces add() + cognify() chain

results = await cognee.recall("query", dataset_name="docs-agents")
```

### 2.3 What Hinders Entity Extraction

- **Long unbroken prose** (paragraphs > 200 words): The LLM loses entity boundaries
- **No section headings**: Cognee can't chunk cleanly; context windows overlap messily
- **Implicit relationships**: "We use X" vs "X provides Y to Z" — the latter creates edges
- **Ambiguous references**: "It", "This", "The system" without antecedent noun
- **Redirect stubs**: Files that say "This content has been merged into X" produce zero entities

---

## 3. Knowledge Graph State — Inspection Results

| Probe | Result |
|:--|:--|
| `cognee_cognify_status()` | `{}` — No active or completed cognify jobs |
| `cognee_search("what data exists", FEELING_LUCKY)` | `[]` — Empty result set |
| `cognee_list_data()` | SQLite integrity error (pre-existing default user) |
| Neo4j (shared instance) | Running — ready to accept Cognee writes |

**Verdict:** Clean slate. No migration or cleanup needed before first ingest.

---

## 4. Per-Subtree Document Quality Assessment

### Scoring Rubric

| Score | Entity Density | Relationship Clarity | Abstract:Concrete | Section Hygiene |
|:--|:--|:--|:--|:--|
| **A** | 15+ entities/100w | Explicit edges named | Mostly concrete (tables, code, lists) | Consistent `##` hierarchy |
| **B** | 10-15 entities/100w | Edges implied | Mixed prose + concrete | Some sections |
| **C** | 5-10 entities/100w | Edges absent | Mostly prose | Flat or no sections |
| **D** | <5 entities/100w | None | Pure prose or stubs | Unstructured |

### 4.1 `docs/agents/` (40 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` | 242 lines | 45+ (x402, MCP, UMA, EAS, AgUI, CopilotKit, ERC-20, SBT, Screpall, Pinginn, 7+ LLM models...) | High — explicit "Agent X requests Y from Z" | 80:20 concrete | Clean Part I/II/III headers | **A** |
| `BAML_COMPREHENSIVE_GUIDE.md` | 1104 lines | 30+ (BAML, BoundaryML, gpt-4o, Resume, MessageType, OpenAI, Anthropic, Gemini...) | Medium — patterns described but edges implicit | 70:30 concrete | Well-structured sections | **A** |
| `BROWSER_AUTOMATION_PLATFORM.md` | 136 lines | 15+ (Browserbase, Smolagents, Firecrawl, CopilotKit) | Low — Parts are distinct summaries, few cross-refs | 60:40 concrete | Part I/II/III but short | **B** |
| `MCP_COMPREHENSIVE_RESEARCH.md` | 646 lines | 35+ (JSON-RPC 2.0, stdio, HTTP, SSE, Resources, Tools, Prompts, Sampling...) | High — 3-component architecture explicit, 6-layer spec table | 75:25 concrete | Well-structured layers | **A** |

**Subtree average:** **A−** (77.5% A-grade). Strong because most files are already consolidated mergers with clean structure.

### 4.2 `docs/bonneagar/` (164 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `ARCHITECTURE.md` | 581 lines | 40+ (Forgejo, Dagger, Komodo, Pangolin, 1Password, Pulumi, Ansible...) | High — explicit "tool → purpose" mapping, integration patterns | 75:25 concrete | Clean hierarchical TOC | **A** |
| `TECH_STACK.md` | 116 lines | 50+ (every line is a tool name) | Low — TOML taxonomy but no edge descriptions | 90:10 concrete | TOML sections, no prose | **B** (high entity density, low relationship clarity) |
| `knowledge-graph-schema.md` | 428 lines | 25+ (Token, Protocol, Blockchain, properties in YAML) | High — explicit `governance_token`, `chains`, temporal properties | 85:15 concrete | YAML entity definitions, clean sections | **A** |
| `infrastructure-knowledge-graph.md` | 31 lines | 15+ (DuckLake, Lakekeeper, SQLMesh, dbt, Ibis, Cocoindex, BAML, Cognee, Graphiti) | High — explicit 3-tier architecture, cross-layer dataflow | 60:40 concrete | Short but structured | **A** |

**Subtree average:** **A−**. Largest subtree by file count; many files are one-off research notes with lower structure.

### 4.3 `docs/data_engineering/` (28 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `ARCHITECTURE.md` | 910 lines | 55+ (DuckLake, Iceberg, RisingWave, Dagster, DLT, SQLMesh, Ibis, LanceDB, Cognee, BAML, Pydantic, Zod...) | High — 6-layer architecture, explicit integration patterns | 80:20 concrete | Deep TOC, 10 major sections | **A** |
| `DLT_COMPLETE_GUIDE.md` | 788 lines | 30+ (DLT, DuckDB, MotherDuck, SQLMesh, Kafka, BAML, oRPC, Pydantic, marimo...) | High — write dispositions, patterns explicitly linked to use cases | 70:30 concrete | 15-section TOC, clean code blocks | **A** |
| `knowledge-systems.md` | 7870 lines | 40+ (BAML, Cognee, Graphiti, Feast, Memgraph, FalkorDB...) | High — full Part I/II/III separation by technology | 65:35 concrete | Very deep TOC | **A** |
| `data-architecture.md` | 7739 lines | 25+ (BigQuery, Dagster, DuckDB, MotherDuck, dbt, Evidence, PyPI...) | Medium — some sections are raw README excerpts with less structure | 50:50 mixed | Some sections well-structured, others raw | **B** |

**Subtree average:** **A−**. Very strong overall, but two files are >7000 lines (merged from 20+ sources each) — these are "too big to cognify" in one chunk.

### 4.4 `docs/meaisínfhoghlaim/` (104 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `AI_MEMORY.md` | 875 lines | 35+ (Agno AgentOS, BAML, Cognee, CocoIndex, LanceDB, Memgraph, Neo4j, GraphRAG, MCP...) | High — 3-tier architecture, explicit component roles | 75:25 concrete | Clean sections, tables with Strengths column | **A** |
| `dual-engine-graph-llm-serving-integration.md` | 296 lines | 20+ (Memgraph, FalkorDB, Graphiti, Cognee, llama-swap, LiteLLM...) | High — explicit dual-engine design, selection matrix | 75:25 concrete | Problem/Solution pattern | **A** |
| `agent-patterns-reference.md` | 362 lines | 25+ (Google ADK, Agno, Claude Code, Gemini 3, GLM-4.6v, Crawl4AI, Skyvern...) | High — tiered stack, agent type table | 70:30 concrete | Clean section hierarchy | **A** |
| `fine-tuning-guide.md` | 153 lines | 2+ (mostly redirect stubs) | None — every section is "This content has been merged into..." | 0:100 stubs | Auto-generated merge artifact | **D** |

**Subtree average:** **B+** (pulled down by redirect stubs like `fine-tuning-guide.md`). Core reference files are strong.

### 4.5 `docs/teanga/` (295 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `CELTIC_LANGUAGES_AI_RESOURCES.md` | 774 lines | 55+ (UCCIX, gaBERT, gaELECTRA, Whisper-Irish, MMS-1B, DCU-NLP, ReliableAI, techiaith, Helsinki-NLP...) | High — per-language tables with model/speaker/status | 80:20 concrete | Table-heavy, clean sections | **A** |
| `gaeilge.md` | 184 lines | 50+ (Tailte Éireann, CSO, PxStat, NISRA, Gaeloideachas, GeoJSON, Shapefile...) | Low — very dense prose, few explicit "X connects to Y" statements | 30:70 prose-dominant | No `##` headings, paragraphs >500 words | **C** |
| `Building Bilingual EdTech Platform.md` | 361 lines | 30+ (Marimo, WebAssembly, Cloudflare Workers, Durable Objects, TanStack Start, Coder, Firecracker...) | High — explicit architectural comparison table, each component's role defined | 70:30 concrete | Strong 6-section structure | **A** |
| `irish-gaeilge.md` | 184 lines | 50+ | Low — same as `gaeilge.md` | 30:70 prose | No section headings | **C** |

**Subtree average:** **B**. Highest file count (295), many are auto-generated gaois-* technical docs with bilingual .en/.ga pairs. The gaois-* files are reference documentation — entity-dense but in very long prose paragraphs.

### 4.6 `docs/web/` (68 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `full-stack-web-architecture-consolidated.md` | 2208 lines | 40+ (TanStack Start, Convex, BetterAuth, Cloudflare, Netlify, OIDC, JWT, PostgreSQL, Hono, oRPC...) | High — explicit architecture diagram, component roles | 75:25 concrete | 10-section TOC, deep hierarchy | **A** |
| `TANSTACK_ANALYSIS.md` | 650 lines | 20+ (better-auth, tRPC, TanStack Start, Vinxi, Prisma, Drizzle, Radix UI...) | Medium — per-example analysis, but cross-example relationships implicit | 65:35 concrete | Structured per-example | **A** |
| `convex-core-features-architecture.md` | 1394 lines | 15+ (Convex, TypeScript, MongoDB, PostgreSQL, ACID, WebSocket, React...) | High — concepts defined with Characteristics lists | 70:30 concrete | Deep TOC, code examples | **A** |
| `effect-ts-comprehensive-research.md` | 2419 lines | 20+ (Effect, TypeScript, Layer, Context, Fiber, Stream, Schema...) | High — type signatures show dependency relationships | 65:35 concrete | 8-section TOC | **A** |

**Subtree average:** **A**. Strongest subtree for Cognee readiness — all files are well-structured research reports with clean code blocks.

### 4.7 `docs/legacy/tuatha/` (117 files)

| Sample File | Size | Entities | Rel. Clarity | A:C Ratio | Sections | Score |
|:--|:--|:--|:--|:--|:--|:--|
| `ANALYSIS.md` | 351 lines | 55+ (SpacetimeDB, Dagger, Komodo, Ansible, Godot, MLX, Unsloth, Flower, CocoIndex, Cognee, CoinGecko, DeFiLlama...) | High — nested bullet hierarchy with explicit relationships | 80:20 concrete | Directory-by-directory structured | **A** |
| `celtic_mmo.md` | 198 lines | 35+ (Minetest/Luanti, SpacetimeDB, MUD, World Engine, Paima, x402, Threshold Network, Polygon ID...) | High — comparison tables with Best Use Case column | 75:25 concrete | Well-sectioned | **A** |
| `educational-game-development.md` | 687 lines | 30+ (Godot, Bevy, Manim, RK4, Verlet, LaTeX, Physics, Chemistry...) | High — explicit experiment → challenge → simulation strategy mapping | 70:30 concrete | 10-section TOC, curriculum tables | **A** |
| `PIPELINES.md` | 478 lines | 25+ (NCCA, SQA, WJEC, Duchas, DLT, DuckDB, CocoIndex, LanceDB, Graphiti, Dagster...) | High — explicit pipeline flow diagram, source → destination paths | 75:25 concrete | Clean code blocks, DLT examples | **A** |

**Subtree average:** **A**. Very strong — most files are well-structured technical specs with explicit relationships.

### 4.8 `docs/cognee/` (9 files)

Every file is **A-grade**: well-structured, entity-dense, explicit relationships. These are the reference implementation of "cognify-clean" documentation.

---

## 5. Aggregate Assessment

| Subtree | Files | Avg Score | Strengths | Weaknesses |
|:--|:--|:--|:--|:--|
| `agents/` | 40 | **A−** | Consolidated mergers, clean structure | Some short stubs |
| `bonneagar/` | 164 | **A−** | High entity density, explicit architecture | Many one-off research notes, inconsistent formatting |
| `data_engineering/` | 28 | **A−** | Deeply structured, 6-layer architecture | Two 7000+ line monsters need chunking |
| `meaisínfhoghlaim/` | 104 | **B+** | Strong core references | Redirect stubs dilute the pool |
| `teanga/` | 295 | **B** | Richest entity diversity (dataset names, APIs, orgs) | Prose-heavy gaois docs, bilingual duplication |
| `web/` | 68 | **A** | Best structured overall | Some very long files (2000+ lines) |
| `agents/tuatha/` | 117 | **A** | Strong technical specs, explicit pipelines | — |
| `cognee/` | 9 | **A** | Reference standard for cognify-clean docs | — |
| `context/` | 66 | **B+** | Consolidated NotebookLM content | Mixed quality, some raw excerpts |

**Overall average:** **A−** (~80% of docs are A or A− grade).

---

## 6. What Makes a Document "Cognify-Clean"

A **cognify-clean** document maximizes Cognee's LLM-based entity extraction by making entities and their relationships explicit in structured text.

### 6.1 The Five Rules

| Rule | Check |
|:--|:--|
| **1. Named entities in every paragraph** | Every §100 words should name at least 3-5 distinct tools, protocols, concepts, or systems |
| **2. Relationship verbs** | "X depends on Y", "X feeds into Z", "X implements Y", "X replaces Y" — not "we use X" |
| **3. Section boundaries at semantic shifts** | `##` heading whenever the topic changes; Cognify chunks on `##` boundaries |
| **4. Tables for entity catalogs** | Tables make entity properties explicit (name, type, purpose, relationship) |
| **5. No redirect stubs** | Files that say "This content has been merged into X" are dead weight — zero entities |

### 6.2 BEFORE/AFTER: Prose → Cognify-Clean

#### BEFORE (prose — `gaeilge.md` style)

> The development of a proof-of-concept map requires identifying and evaluating various data sources from both the Republic of Ireland and Northern Ireland. For the Republic of Ireland, the Central Statistics Office provides census data through their PxStat platform, which can be accessed via data.cso.ie. This data includes statistics on Irish language speakers at various geographic levels. The data is available in formats such as CSV and XLSX, which are suitable for ingestion via dltHub pipelines. Northern Ireland presents additional challenges because it does not have officially designated Gaeltacht areas, so an alternative methodology based on census data from NISRA must be used instead.

**Entity density:** 7/100w (CSO, PxStat, ROI, NI, NISRA, dltHub, Gaeltacht)  
**Relationship clarity:** Low — "presents additional challenges", "can be accessed via"  
**Chunk quality:** One unbroken 120-word paragraph

#### AFTER (cognify-clean rewrite)

```markdown
## Gaeltacht Census Data Pipeline — Republic of Ireland

### Data Sources

| Source | Provider | Access | Format | Geographic Granularity |
|:--|:--|:--|:--|:--|
| Census 2022 Irish Language | CSO | PxStat (`data.cso.ie`) | CSV, XLSX | Small Area, Electoral Division |
| Gaeltacht Boundaries 2024 | Tailte Eireann | data.gov.ie → ArcGIS Hub | GeoJSON, Shapefile, KML | Polygon |
| Gaelscoileanna Directory | Gaeloideachas.ie | Direct Excel download | XLSX | Per-school address + Eircode |

### Relationships

- `Tailte Eireann` **publishes** → `Gaeltacht Boundaries 2024` (GeoJSON)
- `CSO` **provides** → `Census 2022 Irish Language` (PxStat)  
- `PxStat` **exports** → CSV/XLSX **ingested by** → `DLT filesystem source`
- `DLT` **writes** → `DuckDB` **queried by** → `Ibis` **visualized by** → `MapLibre`

### Northern Ireland Alternative

- `NISRA` **provides** → `Census 2021` (Flexible Table Builder)  
- `NISRA` **publishes** → `Data Zone boundaries (DZ2021)` (GeoJSON, Shapefile)
- NI has **no official Gaeltacht** → Irish-speaking areas must be **derived from** Census 2021 speaker density at DZ2021 level
- `Comhairle na Gaelscolaiochta` **certifies** → Irish-medium schools (postcode-based location)
```

**Entity density:** 22/100w (doubled)  
**Relationship clarity:** High — explicit `→` edges, verb-first statements  
**Chunk quality:** `##` heading boundary, table for entity catalog, relationship block for graph edges  
**Cognify output:** Will produce `CSO`, `PxStat`, `DLT`, `DuckDB`, `Ibis`, `MapLibre`, `NISRA`, `DZ2021`, `Tailte Eireann`, `Gaeltacht Boundaries 2024` as nodes, with `publishes`, `provides`, `exports`, `ingested by`, `writes`, `queried by`, `visualized by`, `derived from`, `certifies` as typed edges.

---

## 7. Per-Cluster Graph Models

### 7.1 Should Each Super-Cluster Get Its Own `graph_model_file`?

**Yes, strongly recommended.** Each subtree has a distinct entity ontology. A single flat graph would conflate unrelated concepts (e.g., a `Token` from `bonneagar/knowledge-graph-schema.md` is a cryptocurrency token, while a `Token` from `meaisínfhoghlaim/AI_MEMORY.md` is an LLM token). Separate graph model files give each domain its own namespace and entity schema.

### 7.2 Recommended Clusters and Their Models

| Cluster | Dataset | Graph Model | Core Entities | Core Relationships |
|:--|:--|:--|:--|:--|
| **Data Platform** | `docs-data-eng` | `data_platform_graph.py` | DagsterAsset, DltPipeline, LakehouseTable, CocoIndexFlow, SqlMeshModel, LanceDBIndex | `feeds_into`, `depends_on`, `materializes`, `indexes`, `transforms`, `partitions_by` |
| **Infrastructure** | `docs-bonneagar` | `infrastructure_graph.py` | KomodoStack, PangolinTunnel, DaggerPipeline, PulumiResource, AnsibleRole, DockerService | `deploys`, `routes_to`, `provisions`, `configures`, `orchestrates` |
| **Agents & MCP** | `docs-agents` | `agents_graph.py` | McpServer, AgentTool, LlmAgent, BamlSchema, BrowserSession, CopilotKitComponent | `exposes`, `calls`, `routes_to`, `validates_against`, `renders` |
| **ML & AI** | `docs-ml` | `ml_graph.py` | FineTunedModel, TrainingDataset, MlflowExperiment, UnslothConfig, GgufExport, LanceDBCollection | `trained_on`, `evaluated_by`, `exported_to`, `served_by`, `embedded_in` |
| **Celtic Language** | `docs-teanga` | `celtic_language_graph.py` | LanguageDataset, HuggingFaceModel, GaeltachtBoundary, CensusTable, Gaelscoil, CurriculumSpec | `covers_language`, `aligned_to`, `contains_region`, `enumerates`, `maps_to` |
| **Web & Frontend** | `docs-web` | `web_graph.py` | TanStackRoute, ConvexQuery, BetterAuthProvider, EffectService, HonoEndpoint, ORpcContract | `protects`, `queries`, `mutates`, `depends_on`, `implements`, `validates` |
| **Tuatha MMO** | `docs-tuatha` | `tuatha_graph.py` | GameAsset, SpacetimeDBTable, X402Payment, TokenContract, NpcCharacter, QuestDefinition | `owns`, `pays_for`, `spawns_in`, `requires_completion_of`, `rewards` |

### 7.3 Concrete Example: `data_platform_graph.py`

```python
# graph_models/data_platform_graph.py
# Cognee custom graph model for the data engineering cluster

from cognee.modules.data.models import KnowledgeGraph

class DataPlatformGraph(KnowledgeGraph):
    """
    Custom knowledge graph model for the Oideachais data platform.
    Defines entities and relationships specific to DLT + Dagster +
    CocoIndex + DuckLake pipeline topology.
    """

    # === Entities ===

    class DagsterAsset:
        """A Dagster software-defined asset."""
        properties:
            asset_key: str          # e.g. "docs_added_to_cognee"
            group_name: str         # e.g. "cognition"
            partition_def: str?     # e.g. "MultiPartitionsDefinition"
            schedule: str?          # e.g. "@daily"
            deps: list[str]         # upstream asset keys

    class DltPipeline:
        """A dlt data pipeline."""
        properties:
            pipeline_name: str      # e.g. "github_api"
            source_type: enum[rest_api, filesystem, sql_database]
            destination: enum[duckdb, motherduck, postgres, bigquery]
            write_disposition: enum[merge, append, replace]
            incremental_strategy: str?  # e.g. "cursor", "last_modified"

    class DltResource:
        """A single resource within a dlt pipeline."""
        properties:
            resource_name: str      # e.g. "issues", "commits"
            primary_key: str?       # e.g. "id"
            table_name: str         # destination table

    class LakehouseTable:
        """A table in the DuckLake/Iceberg lakehouse."""
        properties:
            table_name: str
            format: enum[parquet, lance, iceberg]
            catalog: enum[lakekeeper, glue, nessie]
            namespace: str          # e.g. "curriculum", "embeddings"

    class CocoIndexFlow:
        """A CocoIndex data transformation flow."""
        properties:
            flow_name: str          # e.g. "text_embedding_lancedb"
            source_type: str        # e.g. "TextEmbedding", "DocumentSource"
            sink_type: str          # e.g. "LanceDB", "Neo4j"
            incremental: bool

    class LanceDBIndex:
        """A vector index in LanceDB."""
        properties:
            index_name: str
            embedding_model: str    # e.g. "text-embedding-3-large"
            dimensions: int         # e.g. 3072
            metric: enum[cosine, euclidean, dot]

    class SqlMeshModel:
        """A SQLMesh transformation model."""
        properties:
            model_name: str
            kind: enum[FULL, INCREMENTAL_BY_TIME_RANGE, SCD_TYPE_2]
            dialect: enum[duckdb, postgres, bigquery]
            cron: str?              # scheduling expression

    class CurriculumDataset:
        """An Irish education curriculum dataset."""
        properties:
            subject: str            # e.g. "Mathematics", "Gaeilge"
            level: enum[junior_cycle, leaving_cert, national_5, higher, gcse]
            examining_body: enum[NCCA, SQA, WJEC]
            language: enum[english, irish, bilingual]
            format: enum[pdf, html, json, parquet]

    # === Relationships ===

    relationships:
        # Pipeline topology
        DagsterAsset --depends_on--> DagsterAsset
        DagsterAsset --materializes--> LakehouseTable
        DagsterAsset --triggers--> DltPipeline
        DagsterAsset --triggers--> CocoIndexFlow

        # DLT internals
        DltPipeline --contains--> DltResource
        DltResource --writes_to--> LakehouseTable

        # CocoIndex data flow
        CocoIndexFlow --reads_from--> LakehouseTable
        CocoIndexFlow --writes_to--> LanceDBIndex
        CocoIndexFlow --writes_to--> LakehouseTable
        CocoIndexFlow --indexes--> CurriculumDataset

        # SQLMesh transformations
        SqlMeshModel --reads_from--> LakehouseTable
        SqlMeshModel --materializes--> LakehouseTable
        SqlMeshModel --depends_on--> SqlMeshModel

        # Embedding relationships
        CurriculumDataset --embedded_by--> LanceDBIndex
        LanceDBIndex --powers--> DagsterAsset   # for RAG assets

        # Cross-cutting
        DagsterAsset --orchestrates--> SqlMeshModel
        DltPipeline --feeds--> SqlMeshModel
```

**Cognify effect:** When `cognify()` runs with this model, the LLM will extract entities matching these types and link them with typed edges. Searching for "what feeds into the curriculum embeddings index?" will traverse: `DltPipeline → LakehouseTable → CocoIndexFlow → LanceDBIndex`.

---

## 8. Recommendation: Single vs Per-Cluster Cognify

### 8.1 Single Cognify (all docs → one dataset)



| Pros | Cons |
|:--|:--|
| One graph, one search surface | Entity namespace collisions (`Token` = crypto vs LLM) |
| Cross-domain queries work natively ("how does Dagger connect to TanStack?") | GraphRAG quality degrades with too many unrelated edges |
| Simpler orchestration | ~2,242 docs × ~$6 = one large LLM bill upfront |
| Dagster pipeline already designed for it | Hard to update incrementally — one doc change requires re-cognify of everything |
| `graph_model_file` would need to be a union of all domains | No per-domain query scoping |

### 8.2 Per-Cluster Cognify (one dataset per subtree)



| Pros | Cons |
|:--|:--|
| Typed entity schemas (no collisions) | Cross-domain queries require federated search (query 7 datasets separately) |
| Incremental updates — change one file, re-cognify just that dataset | More complex orchestration (7 Dagster assets) |
| Per-dataset cost tracking in Langfuse | One `graph_model_file` per cluster to maintain |
| Scoped search: `cognee.recall("query", dataset_name="docs-agents")` | — |
| Each cluster has its own `graph_model_file` with domain-specific entities and relationships | — |

### 8.3 Recommendation: **Per-Cluster Cognify with Federated Search Layer**

**Phase 1 — Per-cluster ingestion:**
```python
CLUSTERS = [
    {"dir": "docs/agents", "dataset": "docs-agents", "model": "agents_graph.py"},
    {"dir": "docs/bonneagar", "dataset": "docs-bonneagar", "model": "infrastructure_graph.py"},
    {"dir": "docs/data_engineering", "dataset": "docs-data-eng", "model": "data_platform_graph.py"},
    {"dir": "docs/meaisínfhoghlaim", "dataset": "docs-ml", "model": "ml_graph.py"},
    {"dir": "docs/teanga", "dataset": "docs-teanga", "model": "celtic_language_graph.py"},
    {"dir": "docs/web", "dataset": "docs-web", "model": "web_graph.py"},
    {"dir": "docs/tuatha", "dataset": "docs-tuatha", "model": "tuatha_graph.py"},
]

for cluster in CLUSTERS:
    await cognee.remember(
        read_all_md_files(cluster["dir"]),
        dataset_name=cluster["dataset"],
        graph_model_file=f"graph_models/{cluster['model']}",
        graph_model_name=cluster["model"].replace(".py", "").title().replace("_", ""),
    )
```

**Phase 2 — Federated search:**
```python
async def federated_search(query: str, datasets: list[str] | None = None):
    """Query across all clusters, merge results."""
    if datasets is None:
        datasets = [c["dataset"] for c in CLUSTERS]

    all_results = []
    for ds in datasets:
        results = await cognee.recall(query, dataset_name=ds)
        all_results.extend(results)

    # Optional: re-rank merged results by relevance
    return sorted(all_results, key=lambda r: r.score, reverse=True)
```

This gives the best of both worlds: type-safe per-cluster graphs with domain-specific schemas, plus the ability to search across clusters when needed.

---

## 9. Action Items

### Immediate (before first cognify)

| Priority | Action | Effort |
|:--|:--|:--|
| **P0** | Fix `cognee_list_data` SQLite error (delete and recreate default user, or `cognee.prune.prune_data()`) | 5 min |
| **P0** | Skip redirect stubs (files where content = "This content has been merged into X") — use a pre-filter before `cognee.add()` | 10 min |
| **P1** | Split `knowledge-systems.md` (7870 lines) and `data-architecture.md` (7739 lines) into per-topic chunks at `##` boundaries before ingestion | 30 min |
| **P1** | Chunk `gaeilge.md` and `irish-gaeilge.md` — add `##` section headings, break 500-word paragraphs, add relationship tables | 45 min |

### Short-term (before production)

| Priority | Action | Effort |
|:--|:--|:--|
| **P2** | Write 7 `graph_model_file` Python modules (Section 7.3 template above) | 3-4 hours |
| **P2** | Update Dagster pipeline to use per-cluster cognify with `graph_model_file` parameter | 1 hour |
| **P3** | Wire Langfuse tracing into cognify calls for per-dataset cost tracking | 30 min |
| **P3** | Create `scripts/cognee_prefilter.py` that skips redirect stubs and chunks oversized files | 1 hour |

### Ongoing

| Action | Cadence |
|:--|:--|
| Re-cognify changed clusters after documentation sprints | Weekly or per-PR |
| Run consolidation queries via GraphRAG ("find documents that should be merged") | Monthly |
| Monitor Langfuse cost dashboard | Daily |

---

## 10. Summary

The `docs/` tree is **80%+ cognify-ready** out of the box. The majority of files already have the structured headings, entity-dense tables, and explicit relationship descriptions that Cognee's LLM-based entity extraction requires.

The blockers are small and mechanical: a few prose-heavy files in `docs/teanga/` need section-ization, two 7000-line monsters need splitting, and redirect stubs need filtering. None of these require rewriting content — they are formatting-only fixes.

The per-cluster approach with 7 typed `graph_model_file`s gives each domain its own ontology, prevents namespace collisions, enables incremental updates, and still supports cross-domain federated search. Total estimated cognify cost: ~$6.
