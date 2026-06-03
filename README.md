# Oideachais — Kings' College Galway

*A unified Celtic education platform, infrastructure mesh, and AI research laboratory by Cian Mac an Déisigh Uí Liatháin.*

---

## Personal Foundation & Modularity Rationale

This project is the direct product of lived academic experience across two University of Galway postgraduate programmes — the **Higher Diploma in Applied Mathematics** (analytics, modelling, numerical methods) and the **HDip/MSc in Software Development & Entrepreneurship** (algorithms, databases, enterprise Java, internet programming). The modularity of this monorepo mirrors the modularity of that education: each directory is a self-contained domain that maps to specific mathematical, statistical, or software-engineering competencies, yet all are orchestrated to serve a single purpose — pan-Celtic educational equity.

### University of Galway — Mathematics (`university_of_galway/mata/`)

| Module | Key Content | How It Informs This Project |
|:--|:--|:--|
| **MA311 Applied Statistics I** | Linear regression, t-tests, group comparisons, RStudio | Statistical analysis of exam results, grade distributions across 18,641 CSO Small Areas; `R`/`numpy`/`scipy` pipelines in `oideachais/` |
| **MA378 Numerical Analysis II** | Suli & Mayers, root-finding, interpolation, error bounds | Underpins the numerical methods used in geospatial interpolation (GeoHive boundaries) and test-score normalisation |
| **MP307 Modelling II** | Discrete/continuous population models, Maple labs | Directly models curriculum progression as prerequisite chains in `baml_src/` — the BAML `IdentifyPrerequisiteChain` function encodes these dependency graphs |
| **CS4423 Networks** | Graph theory, network topology, assignment sets | Foundation for the knowledge-graph architecture (Neo4j/Memgraph/FalkorDB) and the `graphiti-core` temporal knowledge graph in `meaisínfhoghlaim/` |
| **CS402 Cryptography** | Koblitz, ElGamal, elliptic curves, number theory | Informs the zero-trust infrastructure (`infrastructure/pangolin/`), WireGuard tunnel design, and CrowdSec WAF rule logic |
| **ISLP Labs** | Statistical learning, regression, classification | Directly feeds the `meaisínfhoghlaim/anti-phish/` classical ML pipeline (scikit-learn classifiers) and RAGAS evaluation metrics |

### University of Galway — Software Development (`university_of_galway/software_development/`)

| Module | Key Content | How It Informs This Project |
|:--|:--|:--|
| **CT874 Programming I** | Java fundamentals, 7 assignments from basics to collections | The structured, incremental assignment pattern directly inspired the DLT pipeline module architecture (`dlt_sources/`) — each source is a self-contained, testable unit |
| **CT511 Databases** | SQL, relational design, normalisation | Foundation for DuckDB/DuckLake analytical schema design and the LanceDB vector-layer separation in `oideachais/storage/` |
| **CT545 Enterprise Java** | Spring, JPA, enterprise patterns | The service-layer pattern (FastAPI in `oideachais/`, Hono in `tuatha/`) and the repository/gateway separation in `infrastructure/stacks/` mirror enterprise Java convention |
| **CT853 Algorithmics** | Correctness proofs (bubble sort), mergesort, algorithm analysis | Directly influences the content-deduplication hashing in `oideachais/dlt_sources/ireland/content_deduplication.py` and the HNSW indexing strategy in LanceDB |
| **CT861 Computer Architecture & OS** | Architecture, OS internals, memory management | Informs the ARM-optimised Docker stack design (Hetzner CAX41 ARM, Oracle Ampere A1) and the `mise.toml` task orchestration |
| **CT870 Internet Programming** | Web development, client-server architecture | Foundation for the TanStack Start frontend (`oideachais/web/`) and the multi-protocol server (MCP/AG-UI/SSE) in `infrastructure/browser/` |
| **Software Engineering I** | SDLC, project management, past exams | The Dagster asset-based orchestration and CI/CD Dagger pipeline are structured software-engineering processes applied at infrastructure scale |

### University of Galway — Education (`university_of_galway/education/`)

| Module | Key Content | How It Informs This Project |
|:--|:--|:--|
| **ED116 History of Irish Education** | Historical evolution of the Irish education system | Contextual knowledge for the `dlt_sources/ireland/` pipeline module taxonomy |
| **ED305/ED411 Action Research** | Plickers, creative coding, critical incident analysis | Directly shapes the AI tutor's pedagogical strategy — the `curriculum_agent.py` uses action-research patterns |
| **PGCE Placement** | Teaching practice, lesson planning, psychology | The `oideachais/` learning-outcome models (`CurriculumSpecification` in BAML) are designed by a qualified teacher (Teaching Council ID 6c60e730...) |

### University of Galway — Irish (`university_of_galway/irish/`)

| Module | Key Content | How It Informs This Project |
|:--|:--|:--|
| **GA101 An Cheart** | Irish grammar correctness | Feeds the `alignment/irish_g2P.py` grapheme-to-phoneme alignment and BAML bilingual extraction |
| **GA114 Saoithúlacht** | Irish literature/scholarship | Source material for `leabharlann/` Irish-language corpus curation |
| **GF101 An Prós** | Contemporary Irish prose | Drives the `meaisínfhoghlaim/language/gaeilge/` fine-tuning datasets |
| **GA81010 Éisteacht & Labhairt** | Listening & speaking (Diploma) | Foundation for the `canuint_exporter.py` (TTS dataset generation in LJSpeech format) and Whisper/wav2vec2 ASR fine-tuning |

### University of Galway — Past Achievements (`university_of_galway/past/`)

Transcripts, degree parchments (BA, HDip), and reference letters documenting:
- **BA & HDip transcripts** — Applied Statistics, Mathematics, and Software Development results
- **Apple Award** — recognition of academic excellence
- **Cybersecurity reference** — directly feeds the `anti-phish/` module
- **Irish language results** (`torthaí_ghaeilge.pdf`) — validating bilingual curriculum expertise

---

## Repository Architecture

### Directory Map

```
kings_college_galway/
├── university_of_galway/       # Academic transcripts, notes, and past work
│   ├── mata/                   # Mathematics modules (statistics, networks, crypto, modelling)
│   ├── software_development/   # CS modules (Java, databases, algorithms, internet programming)
│   ├── education/              # Education modules (history, psychology, action research)
│   ├── irish/                  # Irish language modules (grammar, prose, listening)
│   └── past/                   # Transcripts, awards, references
│
├── oideachais/                 # Education platform — Dagster pipelines, DLT sources, FastAPI
├── meaisínfhoghlaim/           # AI/ML — agents, OCR, alignment, pipelines, anti-phish
├── leabharlann/                # Library — 37+ curated Celtic language & heritage PDFs
├── infrastructure/             # Bonneagar — multi-cloud, zero-trust, Komodo orchestration
├── gemini_deep_research/        # Research vault — law, technology, culture, politics, medical
├── docs/                       # Documentation — architecture, data engineering, meaisínfhoghlaim
├── cian_mac_an_déisigh_uí_liatháin/  # Identity — achievements, vetting, teaching credentials
├── tuatha/                     # Educational MMO — Rust backend, Dagster assets, game engine
├── baml_src/                   # BAML schemas — curriculum extraction, exam parsing
└── .agents/                    # Agent skills — 70+ specialised skill definitions
```

---

## Key Directories in Detail

### `oideachais/` — Education Data Platform

The core data engine. Turns raw curriculum PDFs from 5 Irish government sources into structured, deduplicated, bilingual learning outcomes stored in DuckDB/DuckLake and vector-embedded via LanceDB.

**Languages & Patterns:**
- **Python 3.12** — primary language; `pyproject.toml` workspace with `hatchling`
- **Dagster v1.13+** — asset-based orchestration (`data_platform/dagster_defs/`)
- **DLT v1.4+** — streaming data ingestion (`dlt_sources/ireland/`, `dlt_sources/northern_ireland/`, `dlt_sources/great_britain/`)
- **DuckDB/DuckLake** — analytical storage persisted to Cloudflare R2 via Garage S3
- **LanceDB v0.15+** — HNSW vector indexing with MVCC safety
- **BAML** — type-safe curriculum extraction schemas (`baml_src/`)
- **LiteLLM** — model routing (Gemini, Claude, GPT-4o via `litellm_config.yaml`)
- **CocoIndex** — vector embedding orchestration flowing into LanceDB
- **SQLMesh** — virtual data warehouse with DuckDB integration

**Key Modules:**
| Module | Path | Purpose |
|:--|:--|:--|
| Curriculum source | `dlt_sources/ireland/curriculum_source.py` | Unified entry point — merges NCCA, SEC, curriculumonline.ie |
| Subject sources | `dlt_sources/ireland/subjects/` | 18 Junior Cycle + 34 Leaving Certificate DLT resources |
| Exam source | `dlt_sources/ireland/exam_source.py` | SEC examinations (200+ PDFs, marking schemes, Chief Examiner reports) |
| Agentic discovery | `dlt_sources/ireland/agentic_discovery.py` | Firecrawl agent for autonomous URL discovery |
| Geospatial | `dlt_sources/ireland/statistics/` | CSO PxStat (18,641 areas), GeoHive boundaries, UK Met Office |
| ADK agents | `agents/` | Google-ADK multi-agent orchestration (RootAgent, Curriculum, Geospatial, Translation) |

---

### `meaisínfhoghlaim/` — AI & Machine Learning

The intelligence layer. Handles LLM orchestration, vision-language models, OCR, alignment, and federated learning.

**Languages & Patterns:**
- **Python 3.12** — primary; **Rust** (`tuatha/api-rs/`) for performance-critical paths
- **LiteLLM** — centralised model routing with BAML integration
- **BAML** — type-safe extraction schemas for curriculum, exam, and marking-scheme parsing
- **PyTorch + Unsloth** — model fine-tuning (Gemma 3, Qwen 3.6VL, DeepSeek-OCR)
- **MLflow + Langfuse** — experiment tracking and LLM observability
- **Flower (flwr)** — federated learning framework (see `anti-phish/5_Flower_Federated_Learning.ipynb`)
- **Gradio** — model deployment and UI (see `anti-phish/6_Gradio_Front_End.ipynb`)

**Key Subdirectories:**

| Directory | Purpose | Key Technologies |
|:--|:--|:--|
| `agents/` | Multi-agent orchestration (RootAgent, Curriculum, Geospatial, Translation, Corpus, Statistics) | google-adk, agno, LiteLLM |
| `alignment/` | Text alignment, ColPali visual alignment, Irish G2P, character interpolation | vidore/colpali, phonetisaurus |
| `ocr/` | Gaelic document OCR, VLM comparison, PyLaia comparison, observability | Docling, PaddleOCR, PyLaia |
| `pipelines/` | LLM router, VLM bridge, dialect classifier, audio slicing | LiteLLM, canuint_exporter |
| `language/` | Per-Celtic-language resources: `gaeilge/`, `gaidhlig/`, `cymraeg/`, `gaelg/`, `kernowek/`, `brezhoneg/` + `cognates.yaml` | Custom datasets per language |
| `catalog/` | Model registry (`models.yaml`) and source registry (`sources.yaml`) | YAML manifests, HuggingFace references |
| `anti-phish/` | Reference ML project — classical ML → PyTorch → Transformers → Federated → Gradio | scikit-learn, PyTorch, HuggingFace, Flower, Gradio |

**Model Strategy (MacBook Pro M4 Max, 48GB unified memory):**

| Model | Format | Role | Memory | Suitability |
|:--|:--|:--|:--|:--|
| **ColPali v1.3** | MLX/GGUF | Visual document retrieval for SEC multi-column marking schemes | ~2GB | Both M4 Max & M1 Air 8GB |
| **Qwen 3.6VL** | GGUF (llama.cpp) | Vision-language OCR for Irish manuscript and exam paper parsing | ~6-14GB (Q4/Q8) | M4 Max: Q8; M1 Air 8GB: Q2_K unsafe, Q4 possible if solo |
| **GLM 4.6V Flash** | GGUF | Fast vision-language for document layout analysis | ~4-8GB | M4 Max comfortable; M1 Air 8GB: Q4 possible |
| **DeepSeek-OCR** | GGUF (unsloth) | Specialised OCR for Irish handwritten manuscripts | ~3-6GB | Both platforms feasible |
| **Gemma 3 270M / 1B** | GGUF | Mobile-optimised on-device inference (iPhone 16e target) | <1GB | Suitable for iPhone GGUF via llama.cpp Swift |
| **Unsloth Llama 3.2 3B Irish** | LoRA | Irish text generation — target mobile (2GB on-device) | ~2GB | iPhone 16e feasible via ExecuTorch |
| **BGE-M3** | PyTorch | Dense + sparse + multi-vector embeddings (1024d) | ~2GB | Both platforms |
| **FLUX.2-dev** | GGUF | Image generation for educational asset creation | ~12GB+ | M4 Max only; M1 Air impossible |

**iPhone 16e On-Device Strategy:**
- **Gemma 3 270M** via llama.cpp Swift framework for on-device text generation
- **ExecuTorch** for converting Qwen 3.6VL small variants to Core ML models
- **Flower (flwr)** federated learning for privacy-preserving model updates across student devices
- Reference: `anti-phish/5_Flower_Federated_Learning.ipynb` demonstrates full flwr pipeline

**HuggingFace Spaces Deployment Path:**
- Fine-tuned models (Irish OCR, math reasoning, Gaelic ASR) packaged as Gradio apps
- Reference: `anti-phish/6_Gradio_Front_End.ipynb` demonstrates the deployment pattern
- `docs/meaisínfhoghlaim/` contains 200+ notebooks covering Gemma 3, Qwen 3 VL, DeepSeek-OCR, ColPali, LoRA/GRPO fine-tuning, and MLflow tracing

---

### `infrastructure/` — Bonneagar (Multi-Cloud Zero-Trust Platform)

The backbone — 50+ containerised services across Oracle Cloud, Hetzner, and local ARM hardware.

**Languages & Patterns:**
- **TypeScript** — Pulumi IaC (`pulumi/cloudflare/`, `pulumi/hetzner/`, `pulumi/oci/`)
- **TOML** — Komodo orchestration procedures (`komodo/procedures/`, 60+ procedures)
- **Docker Compose** — ~45 stacks following Gold Standard 5-file convention
- **Rust** — Locket sidecar (secret injection from 1Password Connect)
- **Ansible** — post-provisioning configuration
- **Shell** — deployment scripts

**Key Components:**

| Component | Technology | Purpose |
|:--|:--|:--|
| **Pulumi IaC** | TypeScript, `@pulumi/hcloud`, `@pulumi/oci` | Provisions ARM servers (Hetzner CAX41 + Oracle Ampere A1), Cloudflare WAF (31 rules), DNS |
| **Komodo** | TOML DSL, GitOps | 25 stack definitions, 60+ procedures (deploy, rollback, health-check, staged-rollout) |
| **Pangolin** | WireGuard, Traefik v3, Pocket ID | Zero-trust tunneled reverse proxy with SSO, CrowdSec WAF, multi-tenant routing |
| **Komodo Stacks** | Docker Compose x ~45 | Engineering (7), Infrastructure (3), ML (5), Storage (18), Tools (9) |
| **Browser Automation** | Stagehand, Crawl4AI, Skyvern, Patchright | Hunter-Gatherer-Operator pattern for web scraping |
| **Secrets** | 1Password Connect + Locket + Infisical | Zero-disk-secret deployment; `mise.toml` auto-hydrates `.env` from `.infisical.env` |
| **Observability** | Logfire, MLflow, Langfuse v3, Datadog APM | Three-tier: app tracing, ML/LLM observability, infra monitoring |

---

### `leabharlann/` — Library (Celtic Language & Heritage Resources)

37+ curated PDFs spanning language learning, cultural heritage, and academic research across all six Celtic nations.

**Key Resources:**
- **Fuaimeanna na Gaeilge** — Complete phonetics textbook (Brian Ó Raghallaigh, Cois Life)
- **College des Irlandais Paris** — Irish Studies scholarly work (199 pages)
- **A Gaelic History of East Belfast** — Gordon McCoy's maps of Gaelic East Belfast
- **Carn 190** — Celtic nations magazine (Kernow, Mannin, Alba, Breizh, Éire, Cymru)
- **Languages of Ulster** — Links between Gaelic and Scots in Ulster
- **Contemporary Protestant Learners of Irish** — McCoy & Ní Bhraonáin research
- **Turas** materials — East Belfast Mission's Irish language initiative

---

### `gemini_deep_research/` — Deep Research Vault

Structured research reports organised by domain:

| Directory | Contents |
|:--|:--|
| `law/` | 50 PDFs — dual citizenship, medical malpractice, University of Galway complaints, cross-border legal strategy, GDPR, teaching council disputes |
| `technology/` | 23 PDFs — AI career/funding, crypto investigation, Lime bike safety, Instagram regulation, UK intelligence jobs, regulating big tech |
| `culture/`` | 31 PDFs — Celtic language digital revitalisation, British Isles unity, genealogy, royal heraldry, Kneecap investigation, education policy comparison |
| `medical/` | Health-related research documents |

---

### `docs/` — Documentation Hub

| Directory | Contents |
|:--|:--|
| `agents/` | Agentic framework analysis (Agno, PydanticAI, Smolagents, MCP servers) |
| `teanga/` | Irish language preservation, Escriptorium, TTS dataset generation |
| `meaisínfhoghlaim/` | 200+ ML notebooks and research notes (Gemma 3, Qwen VL, DeepSeek-OCR, ColPali, LoRA/GRPO, federated learning, HuggingFace Spaces deployment) |
| `data_engineering/` | Lakehouse strategies (DuckDB, Iceberg, LakeFS) |
| `bonneagar/` | Infrastructure documentation |
| `hmgcc/` | Government-grade security standards (Bailo, CyberChef, Gaffer, Stroom) |

---

### `cian_mac_an_déisigh_uí_liatháin/` — Identity & Credentials

Personal documentation directory:
- **Transcripts** — BA, HDip, and 2013–2023 records from University of Galway
- **Teaching Council** — Registration documentation (Teaching Council ID verified)
- **Apple Award** — Academic recognition
- **Cybersecurity Reference** — Professional recommendation letter
- **Irish Language Results** — Validation of bilingual capability
- **Identity** — Name assertion documentation (Irish: Cian Mac Liatháin; English: Cian Pierce Lyons)

---

### `tuatha/` — Educational MMO (Túatha)

A gamified educational platform combining Rust backend performance with Dagster data pipelines.

**Languages & Patterns:**
- **Rust** — `api-rs/` high-performance backend, `crates/` workspace modules
- **TypeScript** — `ui/` frontend (TanStack Start)
- **Python** — `dagster_assets/`, `dlt_sources/`, `dlt_utils/`
- **Dagster** — Asset orchestration for game-world data
- **BAML** — `baml_src/` structured extraction for game content
- **CocoIndex** — `cocoindex_flows/` vector embeddings for in-game search
- **Knowledge Graph** — `knowledge_graph/` (Memgraph/FalkorDB)
- **Game Assets** — `asset_generation/`, `fibo_generation/` (procedural content)

---

### `.agents/` — Skill Framework

70+ specialised skill definitions for AI agent orchestration, including:
- **Data Engineering**: `dagster`, `dlt`, `duckdb`, `ducklake`, `motherduck`, `sqlmesh`
- **AI/ML**: `unsloth`, `ragas`, `langfuse`, `mlflow`, `huggingface`, `lancedb`
- **Infrastructure**: `pangolin`, `komodo`, `pulumi`, `docker-compose`
- **Browser**: `browser`, `firecrawl`, `crawl4ai`
- **Frontend**: `tanstack-start`, `convex`, `copilotkit`
- **Agent Frameworks**: `google-adk`, `agno`, `graphiti-core`

---

### `baml_src/` — BAML Extraction Schemas

Type-safe curriculum extraction definitions:
- **Curriculum specifications** — `CurriculumSpecification`, `CurriculumStrand`, `EnhancedLearningOutcome`
- **Exam papers** — `ExamPaper`, `ExamSection`, `ExamQuestion` with full question-type taxonomy
- **Marking schemes** — `MarkingScheme`, `MarkingCriteria`, `MarkingPoint` with partial-credit rules
- **Chief Examiner reports** — `ExaminerReport` with `QuestionAnalysis` and `ExamStatistics`
- **Relationship extraction** — `ExtractLearningOutcomeRelationships`, `IdentifyPrerequisiteChain`
- **Skill extraction** — `ExtractSkillsFromOutcome` with `SkillCategory` taxonomy
- **Document metadata** — `ExtractAllPdfMetadata` for autonomous URL discovery

---

### Configuration Files

| File | Purpose |
|:--|:--|
| `pyproject.toml` | Python workspace — `oideachais` package, Dagster, DLT, LanceDB, agents |
| `package.json` | Node.js workspace — Stagehand, Convex, TanStack, Pulumi, Hono |
| `mise.toml` | Task runner — Python 3.12, uv, bun, Dagger, Pulumi, Dagster tasks |
| `.infisical.env` | Secret template — 660 lines of Infisical references (never manual `.env`) |
| `opencode.json` | Agent configuration — 5 specialist sub-agents (explorer, data-engineer, ai-engineer, frontend-dev, devops-architect) |
| `Go.md` | OpenCode Go subscription documentation |
| `LICENSE.md` | Business Source License 1.1 → AGPL v3 after 4 years |

---

## Technology Stack Summary

### Infrastructure Layer (`infrastructure/`)

| Pattern | Technology | Academic Root |
|:--|:--|:--|
| Multi-cloud IaC | Pulumi (TypeScript), Oracle Cloud, Hetzner, Cloudflare | CT861 Computer Architecture — resource management patterns |
| GitOps orchestration | Komodo (60+ procedures, 25 stacks) | CT545 Enterprise Java — service-oriented architecture |
| Zero-trust networking | Pangolin, WireGuard, Traefik v3, Pocket ID | CS402 Cryptography — identity-aware tunnel design |
| Secret injection | Infisical + 1Password Connect + Locket (Rust) | CS402 — key management principles |
| Browser automation | Stagehand, Crawl4AI, Skyvern, Patchright | CT870 Internet Programming — client-server web interaction |
| Observability | Logfire, MLflow, Langfuse v3, Datadog APM | MA311 Applied Statistics — statistical monitoring of distributed systems |

### Data Platform Layer (`oideachais/`)

| Pattern | Technology | Academic Root |
|:--|:--|:--|
| Asset orchestration | Dagster v1.13 | CT874 Programming I — structured, incremental pipeline design |
| Data ingestion | DLT v1.4+ (8 Ireland, 12 UK, 6 Celtic sources) | CT511 Databases — ETL from heterogeneous sources |
| Analytical storage | DuckDB + DuckLake (Garage S3) | MA378 Numerical Analysis — efficient numerical operations on columnar data |
| Vector search | LanceDB v0.15+ (HNSW, MVCC) | CS4423 Networks — graph-based nearest-neighbour search |
| Knowledge graph | Neo4j, Memgraph, FalkorDB, Graphiti | CS4423 Networks — relational topology for curriculum prerequisite chains |
| Structured extraction | BAML (742-line schema) | CS402 — formal specification of complex types |
| Model routing | LiteLLM | CT545 — enterprise service routing patterns |
| Geospatial stats | CSO PxStat (18,641 areas), GeoHive, Met Office | MA311 — statistical analysis of spatially-correlated education outcomes |
| Bilingual support | 6 Celtic languages (ga, gd, cy, gv, kw, br) | GA101/GA114/GF101 — direct application of Irish-language modules |

### AI Layer (`meaisínfhoghlaim/`)

| Pattern | Technology | Academic Root |
|:--|:--|:--|
| Classical ML | scikit-learn (Naive Bayes, SVM, RF, Gradient Boosting) | `anti-phish/` — HDip ML project (85% score) |
| Deep Learning | PyTorch (LSTM, CNN, Transformer) | `anti-phish/3_PyTorch_Deep_Learning_Models.ipynb` |
| Transformer models | HuggingFace Transformers (BERT, RoBERTa, DistilBERT) | `anti-phish/4_Huggingface_Transformers.ipynb` |
| Federated learning | Flower (flwr) with FedAvg | `anti-phish/5_Flower_Federated_Learning.ipynb` |
| Model deployment | Gradio (Spaces deployment pattern) | `anti-phish/6_Gradio_Front_End.ipynb` |
| VLM fine-tuning | Unsloth, Qwen 3.6VL, DeepSeek-OCR, ColPali | `docs/meaisínfhoghlaim/` 200+ notebooks |
| On-device inference | llama.cpp (GGUF), ExecuTorch (Core ML) | Mobile deployment for iPhone 16e (8GB RAM) |
| LLM routing | LiteLLM (Gemini, Claude, GPT-4o) | CT545 — enterprise gateway patterns |
| Alignment & TTS | Irish G2P, phonetisaurus, LJSpeech format | GA81010 — listening & speaking module |
| Observability | MLflow (experiments), Langfuse (tracing), RAGAS (eval) | MA311 — statistical evaluation methodology |

### Frontend Layer (`oideachais/web/`, `tuatha/ui/`)

| Pattern | Technology | Academic Root |
|:--|:--|:--|
| Web framework | TanStack Start (React Server Components) | CT870 Internet Programming |
| AI chat | CopilotKit, AG-UI protocol | CT874 — structured interactive systems |
| Real-time backend | Convex | CT511 — reactive data subscriptions |
| Notebook analytics | Marimo | MA311 — interactive statistical exploration |
| Design system | Tailwind CSS, Radix UI | CT870 — responsive web design |

---

## Deployment Architecture

```
                        ┌─────────────────────────────────────┐
                        │         Cloudflare WAF (31 rules)    │
                        │    *.cianfhoghlaim.ie (Education)   │
                        │         *.aleyum.com (Portfolio)     │
                        └──────────────┬──────────────────────┘
                                       │
                        ┌──────────────┴──────────────────────┐
                        │     Pangolin Zero-Trust Gateway       │
                        │   (WireGuard + Traefik v3 + SSO)     │
                        └──────┬──────────┬──────────┬────────┘
                               │          │          │
                    ┌──────────┴──┐  ┌─────┴────┐  ┌┴───────────┐
                    │  arm1-oci   │  │cax41-hetz │  │  bunchloch │
                    │  (Control) │  │(Workloads)│  │(M4 Max Dev) │
                    │  4ARM/24GB │  │ 16v/32GB  │  │ 48GB RAM   │
                    └─────────────┘  └───────────┘  └────────────┘
```

**Server Fleet:**
| Server | Role | Key Services |
|:--|:--|:--|
| `arm1-oci` (Oracle Cloud London) | Control Plane | Pangolin, Komodo, 1Password Connect, Garage S3, Forgejo, Qdrant |
| `cax41-hetzner` (Nuremberg) | Primary Workloads | Memgraph, FalkorDB, MLflow, Langfuse, LanceDB, Cognee, Graphiti, Dagster, Browser Grid |
| `bunchloch` (MacBook M4 Max) | Dev & Analytics | LakeFS, Lakekeeper, Convex, Crawl4AI, Aleyum portal, ML inference (llama-swap) |

---

## Multi-Agent Architecture

```
                        ┌─────────────────────────────────────┐
                        │          Google-ADK RootAgent         │
                        │   (Orchestrates all sub-agents)      │
                        └──────┬──────────┬──────────┬────────┘
                               │          │          │
                 ┌─────────────┤    ┌─────┴────┐  ┌──┴───────────┐
                 │ Curriculum   │    │Geospatial│  │  Translation │
                 │ Agent        │    │Agent     │  │  Agent        │
                 │ (BAML + DLT) │    │(CSO/Geo) │  │(6 Celtic lang)│
                 └──────┬───────┘    └──────────┘  └──────────────┘
                        │
              ┌─────────┴──────────┐
              │   Statistics Agent  │
              │  (MA311 + R + scipy) │
              └────────────────────┘
```

**Agent Configuration** (`opencode.json`):
| Agent | Model | Focus |
|:--|:--|:--|
| Explorer | DeepSeek V4 Flash | Codebase search and context mapping |
| Data Engineer | Qwen 3.7 Max | Dagster, DLT, DuckDB, MotherDuck pipelines |
| AI Engineer | DeepSeek V4 Pro | BAML, LiteLLM, OCR, Graphiti, Celtic language AI |
| Frontend Dev | Kimi K2.6 | TanStack, Convex, Marimo, UI design |
| DevOps Architect | GLM 5.1 | Docker Compose, Komodo, Pangolin, Pulumi |

---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation, and academic research use permitted within Ireland, UK, EU, Commonwealth, and aligned jurisdictions. Transitions to AGPL v3.0 after 4 years. See [`LICENSE.md`](LICENSE.md).

---

*Built by Cian Mac an Déisigh Uí Liatháin — a qualified Mathematics & Applied Mathematics teacher (Teaching Council of Ireland) with dual Irish-British citizenship, holding degrees from the University of Galway in Applied Statistics, Software Development, and Irish Language Studies.*