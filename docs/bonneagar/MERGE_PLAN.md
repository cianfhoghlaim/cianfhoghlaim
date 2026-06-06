# MERGE_PLAN.md — Phase 1 Subdirectory Flattening

**Goal**: Merge 32 subdirectories into ~11 concatenated `.md` files at the `docs/bonneagar/` root, while keeping all existing flat `.md` files (~140) untouched.

**Date**: 2026-06-06  
**Status**: Plan — implementation pending

---

## Methodology

1. **Read**: Every `.md` file in numbered topic dirs (18 dirs, ~78 files) and tool subdirs (14 dirs, ~400+ files incl. vendored content).
2. **Firecrawl**: Supplementary research for Komodo (`komo.do/docs` returned 404; GitHub README scraped), Pangolin (`github.com/fosrl/pangolin` README scraped; `docs.pangolin.sh` DNS failed), GitHub Komodo (`github.com/moghtech/komodo` README scraped).
3. **Merge**: Concatenate files within each group into a single `output.md`, preserving original filenames as section headers. KCG_SUMMARY.md goes first in each tool group.
4. **Preserve**: All existing flat `.md` files (~140) remain where they are. Subdirs can be removed after merge.

---

## Merge Groups

### Group 1: `overview.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `00-overview/` | 3 | Architecture patterns, web tech tutorials, research index |
| `00-infra-overview/` | 3 | Infrastructure architecture (Dagger, Komodo, Pangolin, 1Password, Pulumi, Ansible) |
| `00-ml-overview/` | 5 | AI compute allocation, multi-agent systems, MCP research, OpenSpec research |

**Output**: `docs/bonneagar/overview.md`  
**Firecrawl context**: Komodo GitHub README (v2.2.0, Rust 63%); Pangolin GitHub README (21k stars, WireGuard-based ZTNA)  
**Total source files**: 11  
**Rationale**: All three `00-` dirs provide introductory/overview context. They describe the platform's architecture, AI/ML strategy, and web development patterns at a high level.

---

### Group 2: `celtic-platform.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `01-celtic-language-ai-resources/` | 6 | Scottish/Welsh/Irish NLP resources, bilingual ML, model comparison |
| `01-irish-edtech-platform/` | 5 | Leaving Cert tutoring, BAML schemas, frontend stack, data architecture |
| `01-selfhosting/` | 3 | Pangolin registration, LiteLLM hosting, bunchloch MacBook setup |

**Output**: `docs/bonneagar/celtic-platform.md`  
**Firecrawl context**: N/A (platform-specific docs)  
**Total source files**: 14  
**Rationale**: All three `01-` dirs cover Celtic language AI + Irish EdTech platform + self-hosting infrastructure — the core "platform" story.

---

### Group 3: `data-acquisition.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `02-celtic-data-acquisition/` | 6 | Gaois APIs, pan-Celtic scraping, bilingual scraper, acquisition pipeline |
| `02-integrations/` | 4 | Effect-TS, Convex, MCP UI, dlt/BAML/oRPC integration |
| `02-multimodal-document-intelligence/` | 5 | VLM/OCR comparison, Gaelic heritage pipeline, Apple Silicon deployment |

**Output**: `docs/bonneagar/data-acquisition.md`  
**Firecrawl context**: N/A  
**Total source files**: 15  
**Rationale**: All three `02-` dirs cover data input: Celtic source acquisition, tool integrations, and multimodal document extraction pipeline.

---

### Group 4: `ai-pipelines.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `03-ai-native-data-pipelines/` | 5 | BAML-dlt integration, Dagster orchestration, lakehouse (OLake/Iceberg), metadata control plane |
| `03-bilingual-dataset-creation/` | 5 | TMX processing, alignment tools, parallel corpus sources, education subject inventory |

**Output**: `docs/bonneagar/ai-pipelines.md`  
**Firecrawl context**: N/A  
**Total source files**: 10  
**Rationale**: Both `03-` dirs cover AI-native data engineering — pipelines, datasets, and ETL for Celtic curriculum content.

---

### Group 5: `specialized-pipelines.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `04-geospatial-linguistics/` | 4 | MapLibre visualization, DuckDB spatial, geospatial data sources |
| `04-web-automation-archival/` | 4 | Irish archives workflow, agentic scraping, stealth browser stack |

**Output**: `docs/bonneagar/specialized-pipelines.md`  
**Firecrawl context**: N/A  
**Total source files**: 8  
**Rationale**: Both `04-` dirs cover specialized pipeline domains — geospatial language data and autonomous web archival.

---

### Group 6: `education-kg.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `05-education-policy-context/` | 4 | Teacher supply, enrollment stats, policy frameworks |
| `05-knowledge-graph-infrastructure/` | 4 | Graphiti temporal graphs, Cognee entity resolution, graph visualization |

**Output**: `docs/bonneagar/education-kg.md`  
**Firecrawl context**: N/A  
**Total source files**: 8  
**Rationale**: Both `05-` dirs cover education context and the knowledge graph infrastructure that models it.

---

### Group 7: `engineering.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `06-document-processing/` | 3 | Celtic language OCR, open-source VLMs for PDF extraction |
| `06-platform-engineering/` | 4 | Docker Compose patterns, Komodo deployment, Apple Silicon deployment |

**Output**: `docs/bonneagar/engineering.md`  
**Firecrawl context**: N/A  
**Total source files**: 7  
**Rationale**: Both `06-` dirs cover engineering implementation — document processing pipelines and platform/deployment engineering.

---

### Group 8: `technical-implementation.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `07-technical-implementation/` | 3 | Diverse data source management, anti-bot crawling stack |

**Output**: `docs/bonneagar/technical-implementation.md`  
**Firecrawl context**: N/A  
**Total source files**: 3  
**Rationale**: Smallest group — stands alone as the implementation-focused wrap-up.

---

### Group 9: `infrastructure-tools.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `komodo/` | ~32 (KCG_SUMMARY + 31 docs) | Core-Periphery architecture, GitOps sync, Resource Sync, Ansible role, FAQ, backup/restore, webhooks |
| `pangolin/` | ~27 (KCG_SUMMARY + 26 docs) | Zero-trust networking, WireGuard, Newt/Olm/Gerbil, Pocket ID OIDC, Traefik, CrowdSec, blueprints, multi-site HA |
| `locket/` | ~22 (KCG_SUMMARY + public docs, locket subdir) | Secret injection sidecar, Infisical provider, tmpfs, watch mode, compose integration |
| `infisical/` | ~6 (KCG_SUMMARY + docs) | Secret vault, three-way contract, machine identity, template hydration |

**Output**: `docs/bonneagar/infrastructure-tools.md`  
**Firecrawl context**:  
- Komodo: Built by Moghtech, Rust 63% + TypeScript 34%, `komodo-core` + `komodo-periphery` container images, v2.2.0 latest (May 2026), GPL-3.0, 11.3k stars. Core/Periphery architecture with web UI, CLI, REST API, WebSocket.  
- Pangolin: Built by Fosrl, TypeScript 98.2% + Go 0.8%, AGPL-3 + Fossorial Commercial License, 21k stars, v1.18.4 latest. Identity-aware VPN + tunneled reverse proxy on WireGuard. Browser-based reverse proxy + client-based private resource access.  
**Total source files**: ~87  
**Note**: Full source code previously removed (2026-06-05). KCG_SUMMARY.md in each subdir provides authoritative summaries. Every Pangolin subdir doc (Blueprints, Middleware Manager, Integration API, OAuth, etc.) and Komodo subdir doc (Procedures, Resource Sync, Webhooks, FAQ, etc.) is concatenated.

---

### Group 10: `development-tools.md`
| Subdir | Files | Key Topics |
|--------|-------|------------|
| `beads/` | ~12 (KCG_SUMMARY + AGENTS, README, CHANGELOG, etc.) | Issue tracking CLI, JSONL-based, Git-native, offline-first |
| `dagger/` | KCG_SUMMARY + patterns docs | CI/CD pipeline engine, BuildKit, polyglot Go/TS/Python |
| `OpenSpec/` | KCG_SUMMARY + arch. docs | Spec-driven development, proposal→tasks→deltas→validate→archive |
| `consolidation/` | 13 | Consolidated research: platform-engineering, knowledge-graphs, celtic-language-ai, etc. |
| `cloudflare/` | KCG_SUMMARY | Workers, D1, R2, better-auth, TanStack Start edge |
| `crawl4ai/` | KCG_SUMMARY | Firecrawl LLMs.txt generator pattern |
| `crypto/` | README | Scaffold-ETH, Arbitrum, SpacetimeDB for Túatha MMO |
| `data-pipeline/` | 5 (README + 4 docs) | Celtic data sources, federated learning, geospatial viz, knowledge base |
| `ducklake/` | KCG_SUMMARY + duck-ui/docs + duckdb-api + frozen-ducklake + sql-workbench-embedded | DuckDB browser UI, REST API, immutable archives, embedded SQL workbench |
| `oh-my-opencode/` | KCG_SUMMARY + multilingual READMEs + AGENTS | Agent orchestration plugin, Sisyphus/oracle/librarian agents, Claude Code compat |

**Output**: `docs/bonneagar/development-tools.md`  
**Firecrawl context**: N/A (all tool-specific, summaries in KCG_SUMMARY.md)  
**Total source files**: ~60 (excluding vendored `rawkode-academy` content and archived OpenSpec change specs)  
**Note**:  
- Dagger's `rawkode-academy/` vendored content (~200+ video/course markdown files) is **EXCLUDED** — it's external reference material, not project documentation.  
- OpenSpec's `openspec/changes/archive/` (~75 archived change specs) is **EXCLUDED** — it's historical spec-driven development artifacts, not documentation.  
- Data-pipeline/ contains pipeline architecture docs (federated learning, geospatial viz) that are distinct from the `03-ai-native-data-pipelines` research group.  
- Ducklake subdirs (duck-ui, duckdb-api, frozen-ducklake, sql-workbench-embedded) each have their own documentation trees that get concatenated inline.

---

## Summary Table

| # | Merged File | Source Subdirs | Source Files | Output Path |
|---|-------------|---------------|-------------|-------------|
| 1 | overview.md | 00-overview, 00-infra-overview, 00-ml-overview | 11 | `docs/bonneagar/overview.md` |
| 2 | celtic-platform.md | 01-celtic-language-ai-resources, 01-irish-edtech-platform, 01-selfhosting | 14 | `docs/bonneagar/celtic-platform.md` |
| 3 | data-acquisition.md | 02-celtic-data-acquisition, 02-integrations, 02-multimodal-document-intelligence | 15 | `docs/bonneagar/data-acquisition.md` |
| 4 | ai-pipelines.md | 03-ai-native-data-pipelines, 03-bilingual-dataset-creation | 10 | `docs/bonneagar/ai-pipelines.md` |
| 5 | specialized-pipelines.md | 04-geospatial-linguistics, 04-web-automation-archival | 8 | `docs/bonneagar/specialized-pipelines.md` |
| 6 | education-kg.md | 05-education-policy-context, 05-knowledge-graph-infrastructure | 8 | `docs/bonneagar/education-kg.md` |
| 7 | engineering.md | 06-document-processing, 06-platform-engineering | 7 | `docs/bonneagar/engineering.md` |
| 8 | technical-implementation.md | 07-technical-implementation | 3 | `docs/bonneagar/technical-implementation.md` |
| 9 | infrastructure-tools.md | komodo, pangolin, locket, infisical | ~87 | `docs/bonneagar/infrastructure-tools.md` |
| 10 | development-tools.md | beads, dagger, OpenSpec, consolidation, cloudflare, crawl4ai, crypto, data-pipeline, ducklake, oh-my-opencode | ~60 | `docs/bonneagar/development-tools.md` |

**Total subdirs flattened**: 32 → 10 merged files  
**Existing flat files preserved**: ~140 (unchanged)

---

## Exclusions

| Content | Reason |
|---------|--------|
| `dagger/rawkode-academy/` | ~200+ vendored external video/course markdown — not project docs |
| `OpenSpec/openspec/changes/archive/` | ~75 archived spec-driven development change artifacts — historical, not documentation |
| All `.DS_Store`, non-`.md` files | Not documentation |
| Deeply nested tool subdirs beyond 1 level (e.g., `locket/locket/docs/`) | Already contained in the parent merge — duplicates of the top-level tool docs |

## Post-Merge

After all 10 files are produced and verified:

1. **Delete source subdirectories** — All 32 subdirs can be removed after merge verification.
2. **Update `INDEX.md`** — Replace subdirectory references with links to the 10 merged `.md` files.
3. **Run `bun run ccc:index`** — Rebuild the codebase semantic index with the flattened structure.
4. **Git commit** — Commit all changes atomically.

---

## Existing Comprehensive Guides (Preserved)

These already-flat files remain at `docs/bonneagar/` root and provide consolidated reference:
- `KOMODO_COMPLETE_GUIDE.md` (21 files merged)
- `PANGOLIN_COMPLETE_GUIDE.md` (27 files merged)
- `SECRETS_MANAGEMENT_GUIDE.md` (30 files merged)
- `ARCHITECTURE.md` — Primary infrastructure reference
- `DECISION_MATRICES.md` — Tool selection decision matrices
- `IMPLEMENTATION_GUIDE.md` — Implementation walkthrough
- `INDEX.md` + `INDEX1.md` — Project navigation
