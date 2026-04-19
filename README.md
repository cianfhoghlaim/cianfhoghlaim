# Oideachais (Kings' College Galway) by Cianfhoghlaim - Unified Celtic Education Platform

*v0.5 A unified data platform and research repository for education and cultural preservation.*

> ⚠️ **Project Status & Disclaimer**
> 
> This repository is a **work in progress**. It is being actively set up to automatically update as syllabus and exam papers change over time. The goal is to have a working prototype prior to this year's secondary school Leaving Certificate Computer Science exam, though this is not guaranteed.
> 
> Please note that folder structures, README files, packages used, and architectural decisions are all subject to change. This project is being developed publicly as an attempt to demonstrate how to coalesce various open-source repositories and documentation (as found in our `docs/` folder) into a workable, large-scale project.
> 
> This is made possible thanks to massive improvements in the development process brought about by breakthroughs in large language coding models assisting a lone developer. The primary AI agent toolchain driving this project includes **Gemini CLI**, **Roo Code**, **GitHub Copilot**, assorted **MCP (Model Context Protocol) servers**, and open-source **HuggingFace models**.

### 📥 Downloading Specific Research Data (Sparse Checkout)

This repository contains massive amounts of data, models, and PDFs. If you only want to download a specific directory, such as the University of Galway research archives, you can use Git's sparse-checkout feature to save time and disk space:

```bash
# 1. Clone the repository without downloading the files
git clone --no-checkout https://github.com/cianfhoghlaim/kings_college_galway.git
cd kings_college_galway

# 2. Initialize sparse-checkout
git sparse-checkout init --cone

# 3. Specify the directory you want to download
git sparse-checkout set bunchloch/university_of_galway

# 4. Checkout the files
git checkout main
```

Oideachais is an advanced, AI-driven educational data platform designed to standardize curriculums across the British Isles. Beginning with a focus on English-language curriculums (GCSE, A-Level, Junior Cycle, Leaving Certificate), the platform's ultimate mission is to evolve into a comprehensive digital sanctuary for Celtic language educational nations (Ireland, Scotland, Wales, Isle of Man, Cornwall, Brittany).

## 🗣️ A Note on the Name: Cianfhoghlaim & Celtic Linguistic Roots

The domain `cianfhoghlaim.ie` || `cian.lyons.co.uk` is a deliberate linguistic play on words that highlights the mechanics of the Irish language while pointing to the broader Celtic linguistic traditions this repository aims to protect:
*   **Cian:** The author's name, which also serves as the Irish prefix for "distance," "remote," or "long-enduring."
*   **Foghlaim:** The Irish word for "learning."

This digital sanctuary will ensure the inter-generational transmission of Goidelic and Brythonic languages and protect our shared cultural heritage against monolingual algorithmic manipulations.

## 👨‍🏫 Author, Paternity & Legal Disclaimers

**Author Identity & Moral Rights:**
This platform is developed entirely by **Cian Pierce Lyons** (Irish Passport Name: **Cian Mac Liatháin**). The author explicitly asserts their moral right of paternity under the Copyright and Related Rights Act 2000 (Ireland) and the Copyright, Designs and Patents Act 1988 (UK) to be permanently identified as the creator of this work.

**Institutional Nomenclature Disclaimer:**
While this platform embraces the structural and historical reference of "Kings' College Galway" to reflect its academic rigor, "Kings' College Galway" operates exclusively as an artistic and thematic project identifier. It does not represent an accredited, regulated, or statutorily recognized degree-awarding higher education institution in any jurisdiction.

---

## 🏗️ Core Architecture: Sruthanna & Pangolin Convergence

The project is organized into domain-specific 'streams' (**sruthanna**) within the `sruth/` directory. This architecture utilizes a **Convergence Model** that balances local high-performance compute with cloud-based orchestration.

### 🌊 The Streams (Sruthanna)

| Stream | Domain | Key Technologies |
| :--- | :--- | :--- |
| `bonneagar/` | **Infrastructure** | Pangolin (Routing), Komodo (Deployment), Locket (Secrets) |
| `oideachais/` | **Education** | FastAPI, TanStack, Dagster, DuckDB (The Core Platform) |
| `meaisínfhoghlaim/` | **Intelligence** | Cognee (GraphRAG), Langfuse, Crawl4AI, MLflow |
| `códeolas/` | **Code Intel** | Beads, Chunkhound, MCP, Dagger |
| `crypteolas/` | **Finance/Agents** | Agent OS, Federated Learning, DLT, Crypto-payments |
| `tuatha/` | **Identity** | Pocket-ID, Forgejo (Community & Sovereignty) |
| `web/` | **Interface** | React, TanStack Start, Agentic UIs |
| `hmgcc/` | **Security** | Government-grade security standards and compliance |

### 🛰️ Pangolin Convergence (Hybrid Strategy)

To maximize performance while maintaining security, the architecture is split across two primary nodes:

1.  **OCI (Control Plane - `arm1-oci`)**: Hosted on Oracle Cloud. Runs **Pangolin** for secure service discovery/routing, **Komodo Core** for orchestration, and core identity services.
2.  **Local (Workload Host - `bunchloch`)**: Powered by a 48GB MacBook M4 Max. Hosts memory-intensive operations including **Vector/Graph DBs** (LanceDB, Cognee), **LLM Inference**, and heavy data analytics (**Dagster**, **LakeFS**).

This hybrid approach ensures that sensitive data and heavy compute remain local ('Bunchloch'), while maintaining global accessibility and zero-trust security via the cloud control plane.

---

## 📜 Usage Policies & Licensing

This repository operates under a highly restrictive **Business Source License (BSL) 1.1**. 

By downloading, copying, or utilizing this codebase, you agree to the following core tenets (see `LICENSE.md` for full legal terms):
1.  **Geographic Restrictions:** Production deployment is legally restricted to Ireland, Northern Ireland, the Republic of Ireland, the United Kingdom of Great Britain and Northern Ireland, Ukraine, the European Union, the British Isles, The Commonwealth of Nations, The Crown, and those in the United States of America aligned with Apple and the Duke and Duchess of Sussex, Taiwan, Tibet, Nepal, South Korea, Japan, China.
2.  **Non-Commercial Use Only:** The software is provided exclusively for non-profit, cultural preservation, and academic research. Commercial monetization—including for-profit AI training, DeFi analytics, and ed-tech SaaS platforms—is strictly prohibited.
3.  **Acceptable Use:** Usage by entities affiliated with sanctioned organizations, paramilitary groups, or those in violation of international human rights conventions is fundamentally banned and will result in immediate technological and legal revocation of access.

