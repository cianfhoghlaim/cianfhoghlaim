from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Corpus Overview - the canonical BIEP + Leabharlann corpus operator dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 12_corpus_overview_01_biep_corpus_overview.py
- 12_corpus_overview_01_leabharlann_corpus_overview.py
- 12_corpus_overview_02_cognee_knowledge_graph.py
- 12_corpus_overview_02_leabharlann_subdir_matrix.py
- 12_corpus_overview_03_bge_m3_embedding_coverage.py
- 12_corpus_overview_03_cross_archive_navigation.py
- 12_corpus_overview_04_lakehouse_table_browser.py
- 12_corpus_overview_04_university_institution_matrix.py

Into a single 7-tab grouped marimo notebook.

## The 7 tabs

1. BIEP Corpus - 388 per-cohort LanceDB tables
2. Leabharlann Corpus - 216 documents across 6 subdirectories
3. Cognee Knowledge Graph - 11-cluster knowledge graph
4. BGE-M3 Embedding Coverage - 1024-d multilingual embedder
5. Cross-Archive Navigation - Unified search across 3 layers
6. Lakehouse Table Browser - 388+ DuckLake + 26 LanceDB tables
7. University Institutions - 7 Irish universities + 4 NUI + 4 IoT

Reference: openspec/changes/2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full")


from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
    tabbed_biep_operator_console,
)
from notebooks._shared.area_shims.corpus_overview import CORPUS_OVERVIEW_TABS


@app.cell(hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 📚 Corpus Overview

        The **canonical BIEP + Leabharlann corpus operator dashboard**.
        Consolidates the 8 legacy corpus overview sub-notebooks into a
        single 7-tab grouped marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in CORPUS_OVERVIEW_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Corpus Overview assistant. You have access to the "
            "BIEP corpus (388 per-cohort LanceDB tables), the Leabharlann "
            "corpus (216 documents), and the Cognee knowledge graph (11 clusters)."
        ),
        prompts=[
            "📚 How many BIEP tables cover Ireland LC Mathematics?",
            "🔍 Search Leabharlann for documents about 'Celtic Revival'",
            "🧠 What's in the Cognee 'baml_schemas' cluster?",
            "🧮 What % of BIEP tables have BGE-M3 embeddings?",
            "🧭 Navigate across BIEP + Leabharlann for 'atomic structure'",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Corpus Overview (via litellm)"), _chat])


def _cli_main(argv=None):
    parser = cli_argparser_biep("corpus_overview")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "corpus_overview",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "corpora": ["BIEP", "Leabharlann", "Cognee KG"],
        "note": (
            "Run via `marimo edit notebooks/corpus_overview.py` for the "
            "interactive console with 7 tabs."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)