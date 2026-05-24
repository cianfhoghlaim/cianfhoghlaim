# Data Engineer Skill

## Context
When assuming the `data-engineer` persona (from `.roomodes`), your goal is to manage the extraction, loading, and transformation (ELT) pipelines specifically focusing on Irish Curriculum data and the DuckLake architecture.

## Core Mandates & Recursive Habits
1. **Zero Absolute Namespaces:** Never import using `from oideachais.data_platform...` inside the data platform itself. ALWAYS use relative or local package imports (e.g. `from dlt_sources.ireland...`). Failing this rule breaks the Dagster orchestrator.
2. **Respect the Cache:** Before executing live Firecrawl scrapes (which drain API credits), you MUST set `os.environ['USE_LOCAL_SCRAPES'] = 'true'`. This forces the pipeline to pull from `stedding/ingest_queue/`, yielding thousands of results safely and instantly.
3. **Unified Sinks:** All DLT pipelines should target the DuckLake (`curriculum.duckdb`) destination to ensure schemas remain joined, avoiding fragmented data silos across different domains.

## Working with MCPs
You have access to:
- `docling-mcp` and `marker-mcp`: Use these to parse complex PDFs (like State Exam marking schemes) into structured Markdown *before* they are sent to LanceDB.
- `chunkhound`: Use this to analyze and embed the resulting data.
