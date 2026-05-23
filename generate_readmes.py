import os

base_dir = "oideachais"
directories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith("__") and not d.startswith(".")]

def get_description(dirname):
    mapping = {
        "adk": "Google ADK agent integration (v2.1+)",
        "agno": "Agno (v2.0+) multi-agent orchestration and AgentOS integration",
        "api": "FastAPI routes and API services",
        "agents": "Specialized AI agents definition",
        "dagster_assets": "Dagster (v1.13+) asset definitions",
        "dagster_defs": "Dagster pipeline definitions and repositories",
        "dlt_sources": "dlt (v1.5+) data extraction sources",
        "dlt_utils": "Utilities for dlt data loading",
        "sqlmesh": "SQLMesh virtual data warehouse transformations",
        "memory": "Knowledge graph memory integration (Graphiti, Cognee)",
        "graph": "Graph database schemas and models",
        "rag": "RAG pipelines and LanceDB integrations",
        "firecrawl_configs": "Firecrawl MCP and web scraping configurations",
        "browser": "Browserbase MCP and browser automation tools",
        "observability": "Langfuse and Ragas observability layers",
        "training": "LLM Fine-tuning (Unsloth)",
        "ui": "Frontend components (CopilotKit, Vinxi, TanStack Start)",
        "mcp": "Model Context Protocol tools and clients",
        "mcp_server": "Internal MCP server implementations",
    }
    return mapping.get(dirname, f"{dirname.capitalize()} module for the Oideachais platform.")

related_modules_template = """
## Cross-References

This module integrates with other components of the Oideachais platform:
- See the main [Agent Architecture](../../AGENTS.md) for global orchestration rules.
- View the [Skills Library](../../.skills/) for agent capability instructions.
- Relevant modules: {related_links}
"""

for d in directories:
    readme_path = os.path.join(base_dir, d, "README.md")
    
    # Pick a few related links randomly or heuristically
    related = [x for x in directories if x != d][:3] 
    related_links = ", ".join([f"[{r}](../{r}/README.md)" for r in related])
    
    content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            content = f.read()
    else:
        content = f"# {d.capitalize()}\n\n{get_description(d)}\n\n"
        
    if "## Cross-References" not in content:
        content += related_modules_template.format(related_links=related_links)
        
    with open(readme_path, 'w') as f:
        f.write(content)
        
print("Successfully generated/updated READMEs for all subdirectories with intra-references.")
