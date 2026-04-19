# Meaisínfhoghlaim - Machine Learning & AI

This stream handles the data ingestion, model observation, and knowledge graph construction for the Celtic Education Platform.

## 🧠 Core Components & Benefits

### 🕸 Crawl4AI (Scraping & Ingestion)
- **Benefit**: High-performance, LLM-optimized web crawling. 
- **Role**: Automatically extracts curriculum content from NCCA and SEC websites, converting messy HTML into clean Markdown ready for RAG.
- **April 2026 Features (v0.8.6)**: Adaptive web crawling, deep crawl crash recovery persisting state, and the new Cloud API Beta.

### 🔭 Langfuse (Observability & Evaluation)
- **Benefit**: Full lifecycle tracking for LLM applications.
- **Role**: Traces every interaction with Gemini/GPT models, allowing us to monitor latency, cost, and output quality.
- **April 2026 Features (v3.169.0)**: "Experiments as a First-Class Concept" for qualitative evaluation, Hosted MCP Server for native model context protocol support, and specialized Agent Observability UI.

### 🌳 Cognee (AI Memory & GraphRAG)
- **Benefit**: Automated construction of queryable knowledge graphs.
- **Role**: Implements GraphRAG, allowing the system to understand the *relationships* between different curriculum topics (e.g., how "Irish History" relates to "Cultural Identity").
- **April 2026 Features (v1.0.1)**: Claude Code Memory Plugin for persistent memory across sessions and faster duplicate detection during data imports.

### 🔎 Perplexica / Vane (Research Engine)
- **Benefit**: Self-hosted, privacy-first AI search engine.
- **Role**: Provides a research interface for developers and educators to perform deep dives into Celtic linguistics and educational policy.

## 🚀 Infrastructure Strategy

All ML workloads are converged on the **48GB MacBook M4 Max (`bunchloch`)**.
- **Reason**: ML inference and vector graph processing are memory-intensive. The 48GB unified memory allows for large local embedding models and high-concurrency crawling without swapping.
