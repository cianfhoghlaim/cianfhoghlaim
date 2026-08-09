# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///

"""Celtic Languages - the canonical Celtic languages operator dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 06_celtic_languages_01_gaois_terminology_explorer.py
- 06_celtic_languages_02_duchas_folklore_with_bboxes.py
- 06_celtic_languages_03_heritage_sites_map.py
- 06_celtic_languages_04_canuint_dialect_player.py
- 06_celtic_languages_05_ud_celtic_treebank_viewer.py
- 06_celtic_languages_06_local_documents_subject_viewer.py
- 06_celtic_languages_07_celtic_curriculum_browser.py

Into a single 7-tab grouped marimo notebook following the canonical
marimo v14 patterns.

## The 7 tabs

1. Gaois - Irish terminology database
2. Dúchas - Schools' Collection folklore archive
3. Heritage Sites - Gaeltacht + heritage locations
4. Canúint - Dialect audio archive
5. UD Treebank - Universal Dependencies treebank
6. Local Documents - Local Irish documents
7. Celtic Curriculum - Cross-linguistic curriculum

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
from notebooks._shared.area_shims.celtic_languages import CELTIC_LANGUAGES_TABS


@app.cell(hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🌐 Celtic Languages

        The **canonical Celtic languages operator dashboard**. Consolidates
        the 7 legacy Celtic language sub-notebooks into a single 7-tab
        grouped marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in CELTIC_LANGUAGES_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Celtic Languages assistant. You have access to the "
            "Gaois terminology database, the Dúchas folklore archive, the "
            "UD Celtic treebank, and the cross-linguistic Celtic curriculum."
        ),
        prompts=[
            "📚 Translate the Irish term 'leabhar' to English",
            "🏛️ Find heritage sites in county Galway",
            "🎙️ Find Canúint audio recordings from county Kerry",
            "🌲 Show me UD treebank parses for the Irish sentence 'Tá an lá grianmhar'",
            "🎓 Compare Irish and Welsh curricula for primary mathematics",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Celtic Languages (via litellm)"), _chat])


def _cli_main(argv=None):
    parser = cli_argparser_biep("celtic_languages")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "celtic_languages",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "languages": ["Irish", "Welsh", "Scottish Gaelic", "Breton", "Manx"],
        "note": (
            "Run via `marimo edit notebooks/celtic_languages.py` for the "
            "interactive console with 7 tabs."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)