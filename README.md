# Kings College Galway - Unified Celtic Education Platform

A unified data platform and research repository for education, beginning with a focus on English-language curriculums and evolving into a comprehensive ecosystem for Celtic language educational nations (Ireland, Scotland, Wales, Isle of Man, Cornwall, Brittany).

## 🚀 Version 1 Pivot: Gemini Live Agent Hackathon Submission

This repository is currently focused on **Version 1**, which is being actively developed as a submission for the **Gemini Live Agent Hackathon** (Deadline: March 16th at 5 PM PT / Midnight GMT). See the `hackathon/` directory for more context.

**Version 1 explicitly prioritizes the English language education systems of the Republic of Ireland and England**, specifically focusing on:
*   **A-Level**
*   **GCSE**
*   **Junior Cycle**
*   **Leaving Certificate**

### The V1 Goal
To build a multi-modal **live input Gemini API homework helper, syllabus helper, curriculum helper, and exam paper helper** for all current curriculum subjects. This AI agent utilizes extensive data orchestration to ingest curriculums, syllabi, and past exam papers, providing real-time, context-aware assistance to students and educators.

### Future Celtic Integration
Version 1 serves as the foundational architecture. Once this English-language foundation (web scraping, indexing syllabus/exams, identifying parallels) is established, **later versions will translate and expand this unified data platform to Celtic language educational nations** (Ireland, Scotland, Isle of Man, Cornwall, Brittany, etc.). This digital sanctuary will ensure the inter-generational transmission of Goidelic and Brythonic languages and protect against monolingual algorithmic manipulations.

---

## 👨‍🏫 Author & Credentials

This platform is developed by:
*   **English Legal Name:** Cian Pierce Lyons
*   **Irish Passport Name:** Cian Mac Liatháin
*   **Domains:** [cianfhoghlaim.ie](https://cianfhoghlaim.ie) and [cianlyons.co.uk](https://cianlyons.co.uk)

**Verified Experience & Credentials (see `cian/` directory):**
*   BA in Mathematics & Education
*   Official teaching registration
*   Cleared background checks
*   Right to restore PGCE progress

While the platform embraces the structural reference of "King's College Galway" for its academic rigor, it centers the author's actual validated credentials in the fields of Computer Science, Mathematics, and Gaeilge.

---

## 🏗️ Core Architecture & Repository Structure

The project is divided into the following core domains:

| Component | Directory | Description |
|-----------|-----------|-------------|
| **Data Orchestration** | `education/` | Data pipelines (Dagster + DLT + CocoIndex) for Irish and UK curriculum ingestion, geospatial data, and semantic indexing. |
| **Machine Learning** | `machine_learning/` | ML model registry and training notebooks (70+ models including OCR, Vision, Retrieval, and Celtic LLMs). |
| **Infrastructure** | `infrastructure/` | Modular Docker stacks (19+ services), CI/CD, and platform routing. |
| **Specifications** | `openspec/` | Formal specifications for capabilities (e.g., curriculum ingestion, bilingual content). |
| **Language Resources**| `irish_english/` | Curated documents, books, and language learning resources for Celtic studies. |
| **Research** | `gemini/`, `research/` | Deep-dive research documents, legal investigations, and AI analyses. |
| **Author Data** | `cian/` | Verified credentials, background checks, and professional documentation. |
| **Hackathon** | `hackathon/` | Context and assets for the Gemini Live Agent Hackathon. |

## ⚙️ Technical Platform (Oideachais)

The education platform merges multiple pipelines into a single observable system:
*   **Data Assets**: 37+ Dagster assets across domains (Ireland, UK, Celtic, Geospatial).
*   **Vector Search & LLM Extraction**: LanceDB semantic search with type-safe BAML schemas.
*   **AI Agents**: Multi-agent system powered by the Gemini Live API with domain routing (Curriculum, Exams, Homework, Statistics).
*   **Observability**: Complete integration with Datadog APM, MLflow, Langfuse, Ragas, and Confluent Kafka.
*   **Storage Ecosystem**: DuckDB (Analytics), LanceDB (Vector Embeddings), Memgraph (Knowledge Graph).

### Quick Start

**1. Install Dependencies**
```bash
uv sync --all-packages
```

**2. Start Infrastructure**
```bash
cd infrastructure
./scripts/stack.sh memgraph up -d
./scripts/stack.sh lancedb up -d
```

**3. Run Education Pipeline**
```bash
cd education
dagster dev
```

---

## 📜 Usage Policies & Moral Licensing

This repository operates under a **Creative Commons Non-Profit License** and a strict **Moral Usage License** designed to ensure the ethical use of digital resources. 

**1. Educational Purpose Only:**
All resources in this repository are provided exclusively for **research, education, and cultural preservation**. They are intended to facilitate inter-generational language transmission and defend the shared culture of the United Isles.

**2. Copyright Statement:**
The materials contained herein are either:
*   **Personal / Academic Work**: Created during academic studies and affiliated educational institutions.
*   **Orphan Works / Educational Fair Dealing**: Digitized for preservation under statutory exceptions permitting the use of such works for instruction, examination, and archival format-shifting.

**3. Prohibited Usage (Moral License):**
These resources and codebase must **not** be used by anyone who promotes, supports, or is affiliated with groups that engage in terroristic activities, glorify violence, or endanger children. Usage is strictly prohibited for groups or individuals promoting paramilitary imagery, drug culture, or terroristic rhetoric.

---
*Generated for Kings College Galway.*
