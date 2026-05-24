#!/bin/bash

README_FILE="/Users/cianmacandeisigh/dev/kings_college_galway/README.md"
TEMP_FILE=$(mktemp)

awk '
/## Core Architecture: The Dual-Stack/ {
    print
    print ""
    print "### The Quadrant Architecture & Interoperability"
    print "The platform is heavily decoupled into four sovereign quadrants to isolate state, infrastructure, and inference:"
    print ""
    print "1. **`infrastructure/` (The Foundation)**: Provides zero-trust mesh ingress (`Pangolin`), fleet orchestration (`Komodo`), identity (`PocketID`), and secrets (`Infisical`)."
    print "2. **`oideachais/` (The Engine)**: Houses the `Dagster` orchestrator, `DLT` extractors, and the `TanStack` frontend UI."
    print "3. **`meaisínfhoghlaim/` (The Brain)**: Manages model routing (`LiteLLM`), extraction schemas (`BAML`), and AI memory graphs (`Cognee`, `Graphiti`)."
    print "4. **`tuatha/` (The Edge)**: Manages distributed node states, agent interactions, and cryptographic token tracking (`x402`)."
    print ""
    print "```mermaid"
    print "graph TD;"
    print "    subgraph Extraction & Orchestration"
    print "        A[oideachais/dlt_sources] -->|Extracts HTML/PDF| B(Firecrawl / Local Cache);"
    print "        B -->|Raw Text| C[Dagster Orchestrator];"
    print "    end"
    print "    subgraph The Brain: AI & Knowledge"
    print "        C -->|Raw Text| D[meaisínfhoghlaim/baml_src];"
    print "        D -->|Structured Schema via Claude/Gemma| E[Graphiti / Neo4j];"
    print "        D -->|Vector Embeddings via Colpali| F[LanceDB];"
    print "    end"
    print "    subgraph The Lakehouse: Storage"
    print "        C -->|Metadata| G[(DuckLake / DuckDB)];"
    print "        C -->|Binary PDFs| H[(Garage S3 / Cloudflare R2)];"
    print "    end"
    print "    G -.->|Query| I[TanStack Frontend];"
    print "    F -.->|Semantic Search| I;"
    print "```"
    print ""
    next
}
{print}
' "$README_FILE" > "$TEMP_FILE"

mv "$TEMP_FILE" "$README_FILE"
