# Research Directory Index

Consolidated research documentation for the hackathon AI-native data platform.

## Directory Structure

```
research/
├── data/consolidated/              # Data layer research
│   ├── 00-overview/               # Architecture & integration guides
│   ├── 01-ingestion-pipelines/    # DLT, Crawl4AI, OLake patterns
│   ├── 02-storage-engines/        # DuckDB, LanceDB, Iceberg
│   ├── 03-transformation/         # Ibis, SQLMesh, feature engineering
│   └── 04-analytics/              # Visualization, BI, dashboards
│
├── infrastructure/consolidated/    # Infrastructure layer research
│   ├── 00-overview/               # Architecture & decision matrices
│   ├── 01-selfhosting/            # Bunchloch stack (Komodo, Pangolin)
│   ├── 02-cicd/                   # Dagger CI/CD patterns
│   └── 03-cloud-services/         # Cloudflare, Pulumi
│
├── machine_learning/consolidated/  # AI/ML layer research
│   ├── 00-overview/               # AI/ML systems architecture
│   ├── 01-agent-frameworks/       # MCP, multi-agent systems
│   ├── 02-model-serving/          # Model deployment patterns
│   └── 03-mlops/                  # ML operations
│
├── web/consolidated/               # Web application layer research
│   ├── 00-overview/               # Architecture patterns
│   ├── 01-frameworks/             # Framework-specific patterns
│   └── 02-integrations/           # Effect-TS, Convex, TanStack
│
├── cianfhoghlaim/consolidated/     # Celtic language education flow
│   ├── 01-celtic-language-ai-resources/
│   ├── 02-celtic-data-acquisition/
│   ├── 03-bilingual-dataset-creation/
│   ├── 04-geospatial-linguistics/
│   ├── 05-education-policy-context/
│   ├── 06-document-processing/    # OCR/VLM extraction
│   └── 07-technical-implementation/
│
└── archive/                        # Processed/archived research
    ├── data-skills/               # Archived data skill docs
    ├── infrastructure-skills/     # Archived infra skill docs
    ├── ml-skills/                 # Archived ML skill docs
    ├── web-skills/                # Archived web skill docs
    └── cianfhoghlaim-raw/         # Archived Celtic research
```

## Quick Navigation

### By Layer

| Layer | Path | Focus |
|-------|------|-------|
| **Data** | `data/consolidated/` | Pipelines, storage, transformation |
| **Infrastructure** | `infrastructure/consolidated/` | Selfhosting, CI/CD, cloud |
| **AI/ML** | `machine_learning/consolidated/` | Agents, models, MLOps |
| **Web** | `web/consolidated/` | Frameworks, integrations |

### By Domain Flow

| Flow | Research | Purpose |
|------|----------|---------|
| **aleyum** | Cross-layer | Developer portfolio analytics |
| **cianfhoghlaim** | `cianfhoghlaim/consolidated/` | Irish language education |
| **códeolas** | Cross-layer | GitHub intelligence |
| **crypteolas** | Cross-layer | DeFi analytics |
| **selfhost** | `infrastructure/consolidated/` | Platform infrastructure |

## Claude Skills Reference

Tool-specific documentation has been consolidated into `.claude/skills/`:

### Data Skills
- `dlt`, `crawl4ai`, `dagster`, `duckdb`, `lancedb`, `cognee`
- `ibis`, `feast`, `evidence`, `marimo`, `olake`, `risingwave`
- `memgraph`, `pydantic`, `cocoindex`, `ducklake`, `chunkhound`, `firecrawl`

### Infrastructure Skills
- `cloudflare`, `dagger`, `docker-compose`, `komodo`, `pangolin`, `pulumi`, `litellm`

### AI/ML Skills
- `agno`, `baml`, `cognee`, `huggingface`, `litellm`, `mlflow`

### Web Skills
- `tanstack-start`, `convex`, `effect-ts`, `hono`, `orpc`

## Index Files

Each consolidated directory contains an `INDEX.md` with:
- Directory structure overview
- Document descriptions
- Related skills mapping
- Quick reference links

## Archive Policy

Processed research files are archived to `/research/archive/` after:
1. Content is consolidated into category folders
2. Skill-specific docs are moved to `.claude/skills/`
3. Duplicates are identified and merged

Original files remain accessible in archive for reference.

## Contributing

When adding new research:
1. Place raw files in appropriate `raw/` directory
2. Run consolidation to merge into `consolidated/`
3. Move skill docs to `.claude/skills/*/references/`
4. Archive processed files
5. Update INDEX.md files
