import os

files_to_update = [
    "docs/codebase_indexing/chunkhound.md",
    ".skills/chunkhound/references/chunkhound.md"
]

append_text = """

## Recent Integrations & Environment Alignment

As of May 2026, ChunkHound provides optimal search performance when combined with:
- **Agno (v2.0+)**: Utilizing the AgentOS architecture and stateless execution to perform rapid, concurrent code searches and multi-hop queries.
- **Google ADK (v2.1+)**: Leveraging the Multi-Agent Workflow Engine to pass chunked ast results across distinct specialist agents via native Inter-Agent Routing.
- **Dagster (v1.13+) / dlt (v1.5+)**: Seamless orchestration and codebase updates via AI skills and dlt+ Cache caching mechanisms.
"""

for filepath in files_to_update:
    if os.path.exists(filepath):
        with open(filepath, 'a') as f:
            f.write(append_text)
        print(f"Updated {filepath}")
    else:
        print(f"File {filepath} not found")
