# Bonneagar — Infrastructure Research Index

Centralized hub for infrastructure, deployment, and platform engineering research for the Cianfhoghlaim platform.

---

## Comprehensive Merged Guides

These are the primary reference documents, consolidated from scattered files:

| Guide | Source Files | Topics |
|-------|-------------|--------|
| **[KOMODO_COMPLETE_GUIDE.md](./KOMODO_COMPLETE_GUIDE.md)** | 21 files from `komodo/` | Core/Periphery, GitOps, recursive deployment, Resource Sync, SDK, Ansible |
| **[PANGOLIN_COMPLETE_GUIDE.md](./PANGOLIN_COMPLETE_GUIDE.md)** | 27 files from `pangolin/` | Zero-trust, Newt, WireGuard, OIDC, Blueprints, multi-site HA, alerting |
| **[SECRETS_MANAGEMENT_GUIDE.md](./SECRETS_MANAGEMENT_GUIDE.md)** | 30 files from `locket/` + `infisical/` | Three-way contract, Infisical vault, Locket sidecar, tmpfs, providers |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Root-level research | Core stack overview, CI/CD, deployment, networking, secrets, IaC |

---

## Core Research Modules

### 1. Document Intelligence & VLM Fine-Tuning
- **File:** `consolidation-multimodal-document-intelligence.md`
- **Topics:** Qwen3-VL, Docling, STEM extraction, philological fine-tuning for Celtic scripts, ColPali alignment

### 2. Infrastructure & Knowledge Graph Platform
- **File:** `consolidation-knowledge-graphs.md`
- **Topics:** DuckLake (DuckDB/Iceberg), Cognee (OWL), Graphiti (Temporal), Komodo/Pangolin orchestration

### 3. Platform Engineering
- **File:** `consolidation-platform-engineering.md`
- **Topics:** Deployment infrastructure, MLOps practices, platform engineering patterns

### 4. Document Processing (OCR/VLM)
- **File:** `consolidation-document-processing.md`
- **Topics:** OCR, VLM, PDF extraction for Celtic language historical documents

### 5. AI-Native Data Pipelines
- **File:** `consolidation-ai-data-pipelines.md`
- **Topics:** ETL/ELT frameworks, orchestration patterns, real-time lakehouse architectures

### 6. Web Automation & Archival
- **File:** `consolidation-web-automation-archival.md`
- **Topics:** Autonomous web scraping, anti-bot evasion, AI-driven content extraction

### 7. Celtic Data Acquisition
- **File:** `consolidation-celtic-data-acquisition.md`
- **Topics:** API access, web scraping methodologies, pan-Celtic archive workflows

### 8. Celtic Language AI Resources
- **File:** `consolidation-celtic-language-ai.md`
- **Topics:** HuggingFace resources for Celtic languages, models, datasets, speech technologies

### 9. Irish EdTech Platform Architecture
- **File:** `consolidation-irish-edtech-platform.md`
- **Topics:** BAML schemas, marking scheme logic, bilingual platform strategy

### 10. Bilingual Dataset Creation
- **File:** `consolidation-bilingual-datasets.md`
- **Topics:** Irish-English parallel corpora, alignment tools, processing workflows

### 11. Technical Implementation
- **File:** `consolidation-technical-implementation.md`
- **Topics:** Pipeline architecture, anti-bot strategies, data source management

### 12. Education Policy Context
- **File:** `consolidation-education-policy.md`
- **Topics:** Celtic language education policies, enrollment statistics, teacher supply

### 13. Research Overview
- **File:** `consolidation-research-overview.md`
- **Topics:** Organized research documentation across 6 thematic categories

## Subdirectories

| Directory | Content |
|:--|:--|
| `komodo/` | Komodo deployment orchestrator patterns and SKILL_CONTEXT |
| `pangolin/` | Pangolin reverse proxy patterns and SKILL_CONTEXT |
| `infisical/` | Secret management platform integration |
| `locket/` | Secret injection sidecar patterns |
| `dagger/` | CI/CD pipeline orchestration patterns |
| `pulumi/` | Infrastructure as Code (not in this dir — see root `infrastructure/pulumi/`) |
| `beads/` | Issue tracking tool (dev utility) |
| `oh-my-opencode/` | OpenCode configuration patterns |
| `crawl4ai/` | Web crawling integration patterns |
| `OpenSpec/` | Spec-driven development research |

## Related Directories

- **Root infrastructure:** `../../infrastructure/` — Live Docker Compose stacks and Komodo configs
- **Platform docs:** `../data_engineering/` — Data pipeline patterns
- **Agent docs:** `../agents/` — Agent framework documentation
- **Skills:** `../../.agents/skills/` — Agent skill definitions
