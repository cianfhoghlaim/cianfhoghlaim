# Oideachais (Kings' College Galway) by Cianfhoghlaim - Unified Celtic Education Platform

*v0.5 A unified data platform and research repository for education and cultural preservation.*

> ⚠️ **Project Status & Disclaimer**
> 
> This repository is a **work in progress**. It is being actively set up to automatically update as syllabus and exam papers change over time. The goal is to have a working prototype prior to this year's secondary school Leaving Certificate Computer Science exam, though this is not guaranteed.
> 
> Please note that folder structures, README files, packages used, and architectural decisions are all subject to change. This project is being developed publicly as an attempt to demonstrate how to coalesce various open-source repositories and documentation (as found in our `docs/` folder) into a workable, large-scale project.
> 
> This is made possible thanks to massive improvements in the development process brought about by breakthroughs in large language coding models assisting a lone developer. The primary AI agent toolchain driving this project includes **Gemini CLI**, **Roo Code**, **GitHub Copilot**, assorted **MCP (Model Context Protocol) servers**, and open-source **HuggingFace models**.

Oideachais is an advanced, AI-driven educational data platform designed to standardize curriculums across the British Isles. Beginning with a focus on English-language curriculums (GCSE, A-Level, Junior Cycle, Leaving Certificate), the platform's ultimate mission is to evolve into a comprehensive digital sanctuary for Celtic language educational nations (Ireland, Scotland, Wales, Isle of Man, Cornwall, Brittany).

## 🏗️ Core Architecture: Sruthanna

The project is organized into domain-specific 'streams' (**sruthanna**) within the `sruth/` directory. This architecture utilizes a **Hybrid Strategy** that balances local high-performance compute with cloud-based orchestration.

### 🌊 The Streams (Sruthanna)

| Stream | Domain | Key Technologies & Architecture |
| :--- | :--- | :--- |
| `sruth/bonneagar/` | **Infrastructure (Taisce)** | **Modular Docker Stacks:** Manages 19+ services including PostgreSQL, Cognee (AI Memory), LakeFS (Versioning), and Langfuse (Observability). Utilizes **Locket** for 1Password secret injection and **Pangolin Blueprints** for declarative routing. |
| `sruth/oideachais/` | **Education Platform** | **Full-Stack AI Education:** TanStack Start (Frontend), FastAPI (API), Dagster v1.13 (Orchestration), and DuckLake/LanceDB (Storage). Transforms curriculums into interactive learning outcomes via Gemini 2.0/Claude 3.7. |
| `sruth/meaisínfhoghlaim/` | **Intelligence** | Opensource Huggingface.co model finetuning and educational asset generation in English and minority languages. |
| `sruth/códeolas/` | **Code Intel** | **Beads & Chunkhound:** Deep codebase analysis and indexing via MCP (Model Context Protocol) servers. |
| `sruth/crypteolas/` | **Finance Intel** | Agent OS, Federated Learning, DLT, Crypto-payments |
| `sruth/tuatha/` | **Educational MMO** | Pocket-ID, Forgejo (Community & Sovereignty) |
| `sruth/web/` | **Frontend UI** | Real-time, type-safe user interfaces and AI chat dashboards |
| `sruth/hmgcc/` | **Security Standards** | **HMGCC Compliance:** Implementation of government-grade security standards (Bailo, CyberChef, Gaffer, Stroom). |

---

## 🏛️ Knowledge & Research Vaults

Beyond the active code streams, this repository serves as a massive knowledge base for British Isles cultural and political research.

### 📚 Documentation Index (`docs/`)
The `docs/` folder contains comprehensive research and specifications across multiple domains:
*   **`docs/agents/`:** Analysis of agentic frameworks (Agno, PydanticAI, Smolagents) and MCP server implementations.
*   **`docs/teanga/`:** Resources for Irish language preservation, historical document analysis (Escriptorium), and TTS dataset generation.
*   **`docs/hmgcc/`:** Security configurations and guidance for government-grade system deployments.
*   **`docs/data_engineering/`:** Strategies for Lakehouse architectures using DuckDB, Iceberg, and LakeFS.
*   **`docs/meaisínfhoghlaim/`:** Machine learning workflows, model evaluation, and fine-tuning patterns.

### 🏛️ Political & Social Research (`bunchloch/gemini/`)
A massive collection of over 140 deep-dive research documents (PDFs) generated during the project's development. This "Gemini Vault" is organized into thematic subdirectories for clarity:

*   **`technology/`**: AI company analysis, Gemini/Google AI goals, Big Tech regulation, and cybersecurity job cycles.
*   **`politics/`**: Brexit impact, Sinn Féin/Fine Gael coalition strategy, election research, and Irish economic future planning.
*   **`law/`**: Dual citizenship jurisprudence, court forms/procedures, medical malpractice strategies, and data access inquiries.
*   **`medical/`**: TBI/C-PTSD recovery protocols, medical cannabis access, disability allowance assistance, and neuro-scientific trauma research.
*   **`culture/`**: Celtic language revitalization, Deacy family genealogy, Irish kingship claims, and Royal family research.
*   **`other/`**: Public service connectivity (Irish Rail), London borough cleanliness, and radicalization prevention strategies.

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

---

## 🎓 Cian CV: Academic, Professional & Civic Credentials

To ensure transparency and verify the author's background, high-resolution scans of key credentials and professional references are provided below:

### 📜 Academic & Professional Records
*   **[University Degree Transcript (BA & HDip)](./cian_cv/ba_and_hdip_transcript.pdf)** | **[Transcript of Results (Bilingual)](./cian_cv/tras_scribhinn_torthai_transcript_of_results.pdf)**
*   **[Academic Parchment 1](./cian_cv/parcment_1.jpeg)** | **[Academic Parchment 2](./cian_cv/parchment_2.jpeg)**
*   **[Leaving Certificate](./cian_cv/leaving_certificate.pdf)** | **[Junior Certificate](./cian_cv/junior_certificate.pdf)**
*   **[Torthaí Ghaeilge (Irish Results)](./cian_cv/torthai_ghaeilge.pdf)**
*   **[Coláiste na Coiribe](./cian_cv/colaiste_na_coiribe.pdf)** | **[Scoil Iognáid](./cian_cv/scoil_iognaid.pdf)**
*   **[Teaching Placement Reference](./cian_cv/placement_reference.pdf)** | **[Placement Feedback](./cian_cv/teaching_placement_feedback.pdf)**
*   **[Part-Time Teaching Reference](./cian_cv/part_time_teaching_reference.pdf)** | **[BME Reference](./cian_cv/bme_reference.pdf)**
*   **[Head of Counselling Reference](./cian_cv/head_of_counselling_reference.pdf)** | **[Apple Award](./cian_cv/apple_award.pdf)**
*   **[Teaching Council Registration](./cian_cv/teaching_registration.pdf)**

### 🛡️ Cybersecurity & Trust
*   **[Cybersecurity Professional Reference](./cian_cv/cybersecurity_reference.pdf)**
*   **[Threat Message Documentation (Evidence)](./cian_cv/threat_message.jpeg)**
*   **[Verified Lack of Criminality (Garda Vetting ROI)](./cian_cv/garda_vetting_roi.pdf)**
*   **[Children First Certificate (Safeguarding)](./cian_cv/children_first_certificate.pdf)**
*   **[Enhanced Disclosure (Northern Ireland)](./cian_cv/enhanced_cert_ni.pdf)** | **[Enhanced Disclosure (UCL/England)](./cian_cv/enhanced_cert_ucl.pdf)**

### 🏥 Medical & Trauma Verification
*   **[C-PTSD Diagnosis (Chronic & Complex)](./cian_cv/chronic_complex_ptsd_diagnosis.pdf)**
*   **[Generalized Anxiety Disorder (GAD) Diagnosis](./cian_cv/anxiety_disorder_diagnosis.pdf)**

### 🏛️ Civic, Political & Family Heritage
*   **[Fine Gael Party Membership](./cian_cv/fine_gael_member.pdf)**
*   **[Liberal Democrats Membership](./cian_cv/libdems_membership.png)**
*   **[Alliance Party Membership](./cian_cv/alliance_membership.pdf)**
*   **[Eamon Deacy Memorial & Family Heritage](./cian_cv/uncle_eamonn_memorial_combined.pdf)**
*   **[Royal Communication (Buckingham Palace)](./cian_cv/buckingham_letter.pdf)**
*   **[Dual Citizenship Verification (ROI & UK)](./cian_cv/old_passports_dual_citizen_verification_roi_uk.pdf)**

---

## 🛰️ Pangolin (Hybrid Strategy)

To maximize performance while maintaining security, the architecture is split across two primary nodes:

1.  **OCI (Control Plane - `arm1-oci`)**: Hosted on Oracle Cloud. Runs **Pangolin** for secure service discovery/routing, **Komodo Core** for orchestration, and core identity services.
2.  **Local (Workload Host - `bunchloch`)**: Powered by a 48GB MacBook M4 Max. Hosts memory-intensive operations including **Vector/Graph DBs** (LanceDB, Cognee), **LLM Inference**, and heavy data analytics (**Dagster**, **LakeFS**).

This hybrid approach ensures that sensitive data and heavy compute remain local ('Bunchloch'), while maintaining global accessibility and zero-trust security via the cloud control plane.

---

## 📂 Directory Description: `/Users/cliste/dev/cianfhoghlaim/cian_cv`

The `/Users/cliste/dev/cianfhoghlaim/cian_cv` directory contains the digital artifacts and verifiable proof of the author's academic and professional journey. It acts as a dedicated proof-of-paternity vault within the repository, housing high-resolution scans of degree parchments, civic memberships, and security clearances. This ensures that the project's lead developer is identifiable and their qualifications are transparently available to collaborators and stakeholders.

---

## 🗣️ A Note on the Name & Author

**Cianfhoghlaim & Celtic Linguistic Roots:**
The domain `cianfhoghlaim.ie` || `cian.lyons.co.uk` is a deliberate linguistic play on words that highlights the mechanics of the Irish language while pointing to the broader Celtic linguistic traditions this repository aims to protect:
*   **Cian:** The author's name, which also serves as the Irish prefix for "distance," "remote," or "long-enduring."
*   **Foghlaim:** The Irish word for "learning."

This digital sanctuary will ensure the inter-generational transmission of Goidelic and Brythonic languages and protect our shared cultural heritage against monolingual algorithmic manipulations.

**Author Identity:**
This platform is developed entirely by **Cian Lyons-Deacy** (Irish Passport Name: **Cian Mac Liatháin Uí Dhéisigh**).

---

## ⚖️ Paternity & Usage Policy

**Moral Rights & Paternity:**
The author explicitly asserts their moral right of paternity under the Copyright and Related Rights Act 2000 (Ireland) and the Copyright, Designs and Patents Act 1988 (UK) to be permanently identified as the creator of this work.

**Institutional Nomenclature Disclaimer:**
While this platform embraces the structural and historical reference of "Kings' College Galway" to reflect its academic rigor, "Kings' College Galway" operates exclusively as an artistic and thematic project identifier. It does not represent an accredited, regulated, or statutorily recognized degree-awarding higher education institution in any jurisdiction.

**Usage Policies & Licensing:**
This repository operates under a highly restrictive **Business Source License (BSL) 1.1**. 

By downloading, copying, or utilizing this codebase, you agree to the following core tenets (see `LICENSE.md` for full legal terms):
1.  **Geographic Restrictions:** Production deployment is legally restricted to Ireland, Northern Ireland, the Republic of Ireland, the United Kingdom of Great Britain and Northern Ireland, Ukraine, the European Union, the British Isles, The Commonwealth of Nations, The Crown, and those in the United States of America aligned with Apple and the Duke and Duchess of Sussex, Taiwan, Tibet, Nepal, South Korea, Japan, China.
2.  **Non-Commercial Use Only:** The software is provided exclusively for non-profit, cultural preservation, and academic research. Commercial monetization—including for-profit AI training, DeFi analytics, and ed-tech SaaS platforms—is strictly prohibited.
3.  **Acceptable Use:** Usage by entities affiliated with sanctioned organizations, paramilitary groups, or those in violation of international human rights conventions is fundamentally banned and will result in immediate technological and legal revocation of access.
