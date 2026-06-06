---
title: "Cianfhoghlaim Documentation Index"
domain: standards
status: stable
description: "Master routing table for all canonical documentation. Auto-generated from frontmatter — do not edit manually."
read_when:
  - "starting any task in this codebase"
  - "looking for documentation on a specific topic"
  - "unsure which doc to read"
last_reviewed: 2026-06-06
---

# Cianfhoghlaim Documentation Index

> **1,038 source files consolidated into 36 canonical documents across 7 domains.**
> Every canonical file carries Cognee-clean frontmatter (`entities`, `related_skills`,
> `ccc_query_hints`, `supersedes`). Merged originals live in `docs/archive/`.

## Routing Table — I want to..., where do I go?

| When you need to... | Read this | Domain |
|:--|:--|:--|
| Understand the overall platform architecture | [Platform Overview](01-platform-architecture/platform-overview.md) | `architecture` |
| Set up or manage Docker Compose stacks | [Infrastructure Stacks](01-platform-architecture/infrastructure-stacks.md) | `architecture` |
| Configure secrets (Infisical, Locket, mise) | [Secrets Management](01-platform-architecture/secrets-management.md) | `architecture` |
| Deploy via Komodo GitOps | [Komodo GitOps](01-platform-architecture/komodo-gitops.md) | `architecture` |
| Configure Pangolin networking / VPN / Traefik | [Pangolin Networking](01-platform-architecture/pangolin-networking.md) | `architecture` |
| Deploy to Kubernetes (Talos, Pulumi) | [Kubernetes Deployment](01-platform-architecture/kubernetes-deployment.md) | `architecture` |
| Understand the bun+uv+turbo monorepo strategy | [Monorepo Strategy](01-platform-architecture/monorepo-strategy.md) | `architecture` |
| Design the data lakehouse architecture | [Data Architecture](02-data-platform/data-architecture.md) | `data_platform` |
| Write Dagster assets, sensors, schedules | [Dagster Orchestration](02-data-platform/dagster-orchestration.md) | `data_platform` |
| Write DLT pipelines (filesystem or REST API) | [DLT Pipelines](02-data-platform/dlt-pipelines.md) | `data_platform` |
| Build or understand an agent framework | [Agent Frameworks](03-agents/agent-frameworks.md) | `agents` |
| Design BAML extraction schemas | [BAML Extraction](03-agents/baml-extraction.md) | `agents` |
| Set up browser automation / scraping | [Browser Automation](03-agents/browser-automation.md) | `agents` |
| Build or consume an MCP server | [MCP Servers](03-agents/mcp-servers.md) | `agents` |
| Fine-tune an LLM (Unsloth, LoRA, TRL) | [Fine-Tuning Guide](04-ai-ml/fine-tuning-guide.md) | `ai_ml` |
| Set up OCR / HTR for documents | [OCR & HTR](04-ai-ml/ocr-htr.md) | `ai_ml` |
| Evaluate or improve RAG quality | [RAG Evaluation](04-ai-ml/rag-evaluation.md) | `ai_ml` |
| Work with knowledge graphs (Cognee, Graphiti) | [Knowledge Graphs](04-ai-ml/knowledge-graphs.md) | `ai_ml` |
| Design vector search / embeddings | [Vector Embeddings](04-ai-ml/vector-embeddings.md) | `ai_ml` |
| Work with Celtic language AI (Irish, Welsh, Gaelic) | [Celtic Language AI](04-ai-ml/celtic-language-ai.md) | `ai_ml` |
| Set up ML pipelines / observability | [ML Pipelines](04-ai-ml/ml-pipelines.md) | `ai_ml` |
| Understand the frontend stack (TanStack Start, React) | [Frontend Stack](05-web/frontend-stack.md) | `web` |
| Configure Convex + Hono + BetterAuth | [Convex, Hono & Auth](05-web/convex-hono-auth.md) | `web` |
| Build UI components / design system | [UI Components](05-web/ui-components.md) | `web` |
| Design the Celtic MMO game | [Celtic MMO](06-product/celtic-mmo.md) | `product` |
| Integrate crypto payments / Web3 | [Crypteolas](06-product/crypteolas.md) | `product` |
| Develop the game engine (Godot, wgpu) | [Game Development](06-product/game-development.md) | `product` |
| Design the educational platform experience | [Educational Platform](06-product/educational-platform.md) | `product` |
| Follow coding conventions and standards | [Project Conventions](07-standards/project-conventions.md) | `standards` |
| Set up observability (Datadog, MLflow, Langfuse) | [Observability Patterns](07-standards/observability-patterns.md) | `standards` |

## Documents by Domain

### Platform Architecture (8 docs)
| File | Description |
|:--|:--|
| [platform-overview.md](01-platform-architecture/platform-overview.md) | Cianfhoghlaim architecture: Pangolin convergence, Quadrant Model, sovereign infrastructure |
| [infrastructure-stacks.md](01-platform-architecture/infrastructure-stacks.md) | 89 Docker Compose stacks: categories, network topology, health checks, storage architecture |
| [komodo-gitops.md](01-platform-architecture/komodo-gitops.md) | Komodo deployment orchestration: Core/Periphery, GitOps, Procedures, Actions |
| [kubernetes-deployment.md](01-platform-architecture/kubernetes-deployment.md) | K8s deployment: Talos, Pulumi/OpenTofu, Ansible, Komodo Periphery bootstrap |
| [monorepo-strategy.md](01-platform-architecture/monorepo-strategy.md) | bun + uv + turbo polyglot monorepo: workspace topology, mise toolchain, Dagger CI/CD |
| [pangolin-networking.md](01-platform-architecture/pangolin-networking.md) | Zero-trust networking: Traefik, WireGuard, Pocket ID, CrowdSec, Blueprints |
| [secrets-management.md](01-platform-architecture/secrets-management.md) | Three-way secret contract: Infisical → .infisical.env → .env, Locket sidecar, mise hooks |
| [README.md](01-platform-architecture/README.md) | Platform architecture domain index |

### Data Platform (4 docs)
| File | Description |
|:--|:--|
| [data-architecture.md](02-data-platform/data-architecture.md) | Lakehouse: DuckDB, DuckLake, Iceberg, Garage S3, R2, MotherDuck, LanceDB, RisingWave |
| [dagster-orchestration.md](02-data-platform/dagster-orchestration.md) | Dagster: assets, partitions, schedules, sensors, jobs, dg workspace, testing |
| [dlt-pipelines.md](02-data-platform/dlt-pipelines.md) | DLT: filesystem/REST pipelines, sources, destinations, incremental, schema, safety |
| [README.md](02-data-platform/README.md) | Data platform domain index |

### Agents (5 docs)
| File | Description |
|:--|:--|
| [agent-frameworks.md](03-agents/agent-frameworks.md) | Agno AgentOS, Google ADK, CopilotKit, Convex, Pydantic AI, Restate, A2UI |
| [baml-extraction.md](03-agents/baml-extraction.md) | BAML schemas, Irish education extraction, DuckDB/Dragonfly, TypeBuilder |
| [browser-automation.md](03-agents/browser-automation.md) | Browserbase, Stagehand V3, Firecrawl, Smolagents deep research |
| [mcp-servers.md](03-agents/mcp-servers.md) | MCP protocol, Python/TS SDKs, OAuth/x402/SIWE auth, security |
| [README.md](03-agents/README.md) | Agents domain index |

### AI/ML (8 docs)
| File | Description |
|:--|:--|
| [fine-tuning-guide.md](04-ai-ml/fine-tuning-guide.md) | Unsloth, LoRA/QLoRA, QAT, GRPO/DPO, GGUF, TRL, HuggingFace, MLX |
| [ocr-htr.md](04-ai-ml/ocr-htr.md) | ColPali, Docling, DeepSeek-OCR, Qwen-VL, Gaelic script, eScriptorium, PyLaia |
| [rag-evaluation.md](04-ai-ml/rag-evaluation.md) | RAGAS metrics, federated RAG, IRLBench, Langfuse+RAGAS integration |
| [knowledge-graphs.md](04-ai-ml/knowledge-graphs.md) | Cognee, Graphiti, Memgraph, FalkorDB, dual-engine graph+LLM serving |
| [vector-embeddings.md](04-ai-ml/vector-embeddings.md) | LanceDB, Qdrant, embeddings pipeline, DuckLake lakehouse, Iceberg |
| [celtic-language-ai.md](04-ai-ml/celtic-language-ai.md) | Irish/Welsh/Gaelic NLP, GaBERT, BritLLM, Gaois, kscanne, bilingual datasets |
| [ml-pipelines.md](04-ai-ml/ml-pipelines.md) | MLflow, Langfuse, LiteLLM, experiment tracking, model registry |
| [README.md](04-ai-ml/README.md) | AI/ML domain index |

### Web (4 docs)
| File | Description |
|:--|:--|
| [frontend-stack.md](05-web/frontend-stack.md) | TanStack Start, React 19, SSR, Effect-TS, oRPC, Vite, isomorphic functions |
| [convex-hono-auth.md](05-web/convex-hono-auth.md) | Convex, Hono, BetterAuth, SIWE, multi-tenant, AG-UI protocol |
| [ui-components.md](05-web/ui-components.md) | shadcn/ui, CopilotKit, dnd-kit, MCP-UI, data viz, game UI patterns |
| [README.md](05-web/README.md) | Web domain index |

### Product (5 docs)
| File | Description |
|:--|:--|
| [celtic-mmo.md](06-product/celtic-mmo.md) | SpacetimeDB, Anam Cara system, mythology cycles, Ogham stones, world map zones |
| [crypteolas.md](06-product/crypteolas.md) | x402 protocol, Tuath token (ERC-20/2612/3009), SIWE, Learn-to-Earn, crypto agents |
| [game-development.md](06-product/game-development.md) | Godot+Rust (gdext), wgpu, Babylon.js, particle effects, AI asset pipeline |
| [educational-platform.md](06-product/educational-platform.md) | Curriculum scope, Leaving Cert mapping, AI tutoring, OCR pipeline, mobile strategy |
| [README.md](06-product/README.md) | Product domain index |

### Standards (2 docs)
| File | Description |
|:--|:--|
| [project-conventions.md](07-standards/project-conventions.md) | Naming conventions, technology constraints, Irish language requirements, BAML validation |
| [observability-patterns.md](07-standards/observability-patterns.md) | Datadog APM/LLMObs, MLflow, Langfuse, Ragas, structlog |

---

## Skill-to-Doc Mapping

| Agent Skill | Primary Doc(s) |
|:--|:--|
| `dagster` | [dagster-orchestration.md](02-data-platform/dagster-orchestration.md) |
| `dlt` | [dlt-pipelines.md](02-data-platform/dlt-pipelines.md) |
| `motherduck` | [data-architecture.md](02-data-platform/data-architecture.md) |
| `duckdb` / `ducklake` | [data-architecture.md](02-data-platform/data-architecture.md) |
| `agno` | [agent-frameworks.md](03-agents/agent-frameworks.md) |
| `google-adk` | [agent-frameworks.md](03-agents/agent-frameworks.md) |
| `copilotkit` | [agent-frameworks.md](03-agents/agent-frameworks.md), [ui-components.md](05-web/ui-components.md) |
| `mcp-builder` | [mcp-servers.md](03-agents/mcp-servers.md) |
| `browser` / `browserbase-cli` / `firecrawl` | [browser-automation.md](03-agents/browser-automation.md) |
| `unsloth` | [fine-tuning-guide.md](04-ai-ml/fine-tuning-guide.md) |
| `cognee` | [knowledge-graphs.md](04-ai-ml/knowledge-graphs.md) |
| `graphiti-core` | [knowledge-graphs.md](04-ai-ml/knowledge-graphs.md) |
| `lancedb` | [vector-embeddings.md](04-ai-ml/vector-embeddings.md) |
| `ragas` | [rag-evaluation.md](04-ai-ml/rag-evaluation.md) |
| `langfuse` | [ml-pipelines.md](04-ai-ml/ml-pipelines.md) |
| `mlflow` | [ml-pipelines.md](04-ai-ml/ml-pipelines.md) |
| `irish-edtech` | [celtic-language-ai.md](04-ai-ml/celtic-language-ai.md), [educational-platform.md](06-product/educational-platform.md) |
| `document-intelligence` / `huggingface` | [ocr-htr.md](04-ai-ml/ocr-htr.md) |
| `tanstack-start` | [frontend-stack.md](05-web/frontend-stack.md) |
| `hono` | [convex-hono-auth.md](05-web/convex-hono-auth.md) |
| `convex` | [convex-hono-auth.md](05-web/convex-hono-auth.md) |
| `pulumi` | [komodo-gitops.md](01-platform-architecture/komodo-gitops.md) |
| `pangolin` | [pangolin-networking.md](01-platform-architecture/pangolin-networking.md) |
| `komodo` | [komodo-gitops.md](01-platform-architecture/komodo-gitops.md) |
| `dagger` | [monorepo-strategy.md](01-platform-architecture/monorepo-strategy.md) |
| `stack-ops` | [infrastructure-stacks.md](01-platform-architecture/infrastructure-stacks.md) |

---

## Archive

All merged source files (851 files) live in `docs/archive/2026-06-06-*/` organised by
their original subtree. Each archived file's original path and content is preserved.
Canonical files reference superseded files in their frontmatter `supersedes` field.

## Consolidation Methodology

- **1,038 source files** → **36 canonical files** (96.5% reduction in file count)
- **Strategy**: Heavy merge — all files sharing >50% topic overlap folded into one canonical
- **No content deleted**: Every merged original lives in `docs/archive/`
- **Frontmatter on every file**: `title`, `domain`, `status`, `description`, `supersedes`, `entities`, `related_skills`, `ccc_query_hints`, `last_reviewed`
- **Cognee-ready**: Explicit entity names and relationships for graph extraction
- **ccc-indexed**: Already searchable via `bun run ccc:search`
- **Agent-skill-consumable**: Routing table maps every skill to its primary doc(s)

See `docs/audit/consolidation_plan.md` for the full methodology and migration map.
