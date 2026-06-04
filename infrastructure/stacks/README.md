# Infrastructure Stacks

Reorganised per Phase 0 (2026-06-04). See `infrastructure/AGENTS.md` for the categorisation philosophy.

| Category | Stacks | Purpose |
|:--|--:|:--|
| `storage/` | 5 | Foundational substrates (Garage S3, Lakekeeper, LakeFS) |
| `infrastructure/` | 12 | Control plane (Pangolin, Komodo, PocketID, Forgejo, Backrest, Vaultwarden, Glance, Pulumi, Headscale, Headplane, DNS, Monitoring) |
| `engineering/` | 17 | Gateways + services (LiteLLM, llama-swap, MLX-Omni, InvokeAI, Dagster, Marimo, Bytebase, Gluetun, Pipecat, Dragonfly, Crawl4AI, Coder, Windmill, MCPJungle, DevDocs, N8n, Networking) |
| `machine_learning/` | 16 | AI services (Cognee, Graphiti, Langfuse, LMNR, Olake, Qdrant, Memgraph, FalkorDB, LanceDB, MLflow, Logfire, Nimtable, RisingWave, Docling-Serve, OlmOCR, Unstract) |
| `tools/` | 24 | Productivity + media (SearXNG, Karakeep, Termix, Paperless-NGX, IT-Tools) |
