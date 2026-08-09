"""cianfhoghlaim.notebooks — the BIEP Marimo notebook package.

The 52 active marimo notebooks are organised in a flat layout (post-v7):

    00_biep_v3_dashboard_template.py   # The canonical 8-cell template
    00_control_panel.py                # The 5-tab deployment control panel
    00_marimo_patterns_tour.py          # The educative marimo-patterns tour
    01_overview_setup.py                # Legacy BIEP v1 overview (Tier 4, pending refactor)
    02_education_overview.py            # Education stage overview
    05_england_aqa_ocr_edexcel.py       # England AQA + OCR + Edexcel
    07_junior_cycle_ireland.py          # Ireland Junior Cycle
    08_ocr_ensemble_audit.py            # 4-path OCR ensemble audit
    10_biep_pipeline_lakehouse_*.py     # 17 BIEP v3 lakehouse explorers
    13_official_media_*.py               # 7 official-media dashboards
    18_cianfhoghlaim_subject_registry.py
    19..27_*.py                         # 6 BIEP v3 jurisdiction dashboards
    23_8_jurisdiction_overview.py       # 8-jurisdiction overview
    24_deployment_control_panel.py      # Sync health dashboard
    40_leaving_cert_subject_panel.py    # 7-tab grouped marimo panel
    meaisin_ops_console.py              # Tier 3 grouped (12-agent fleet)
    celtic_languages.py                 # Tier 3 grouped (7 Celtic languages)
    corpus_overview.py                  # Tier 3 grouped (BIEP + Leabharlann)
    speedrun_mmo.py                     # Tier 3 grouped (Túatha MMO)
    academic_history.py                 # Tier 3 grouped (M.Sc. AI)
    irish_law.py                        # Tier 3 grouped (Irish law)
    sync_health.py                      # Tier 4 grouped (11 sync layers)

Legacy (deprecated, retained for back-compat):
    legacy/v7_consolidation/            # 80 deprecated sub-notebooks

Helpers (re-exported from `_shared/`):
    notebooks._shared.marimo_patterns        # R1+P1-P6 helpers
    notebooks._shared.area_shims.*          # 10 area_shim modules
    notebooks._shared.schema                # 5 introspection helpers
    notebooks._shared.db                    # ibis-first connect helpers
    notebooks._shared.ragas_gauge            # P5 RAGASGaugeWidget

Legacy helpers (DEPRECATED, kept for back-compat):
    notebooks.nb_utils                      # marked @deprecated — use _shared.marimo_patterns

Reference: openspec/changes/2026-08-10-marimo-v14-cascading-effects-verification-v1/
"""
from notebooks._shared.marimo_patterns import (
    LITELLM_BASE_URL,
    RAGAS_PASS_THRESHOLD,
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    form_gated_run_button,
    llm_chat_with_prompts,
    progress_bar_with_eta,
    ragas_color,
    ragas_status_emoji,
    run_dagster_asset_check,
    setup_biep_registry_header,
    tabbed_biep_operator_console,
    three_column_grid_app,
)

# ragas_gauge_widget requires anywidget (only available inside marimo runtime)
try:
    from notebooks._shared.marimo_patterns import ragas_gauge_widget
except ImportError:
    ragas_gauge_widget = None  # type: ignore[misc,assignment]
from notebooks._shared.area_shims.biiep_v3_dashboard import (
    build_biep_v3_dashboard,
    build_overview_cell,
    build_ibis_conn_cell,
    build_commands_cell,
    build_cohort_matrix_cell,
    build_drill_down_cell,
    build_schedule_cell,
    build_asset_check_cell,
    build_dive_link_cell,
    build_llm_tab_cell,
)
from notebooks._shared.area_shims.leaving_cert import (
    biiep_v3_overview,
    BIEP_V3_OPERATOR_COMMANDS,
    BIEP_V3_CRON_SCHEDULE,
)
from notebooks._shared.ragas_gauge import (
    ragas_color as ragas_color_lib,
    ragas_status_emoji as ragas_status_emoji_lib,
    RAGAS_EXCELLENT_THRESHOLD,
)

# RAGASGaugeWidget requires anywidget (only available inside marimo runtime)
try:
    from notebooks._shared.ragas_gauge import RAGASGaugeWidget
except ImportError:
    RAGASGaugeWidget = None  # type: ignore[misc,assignment]
from notebooks._shared.db import (
    connect_md,
    connect_local,
    connect_local_lakehouse,
    connect_lance,
    format_snake_case_cohort_path,
    compute_ragas_distribution,
    lakehouse_uri,
    LAKEHOUSE_URI_DEFAULT,
)

# Legacy back-compat (DEPRECATED — use the _shared.* helpers above)
from notebooks.nb_utils import (
    BIEP_LANGUAGES,
    BIEP_LEVELS,
    BIEP_SUBJECTS,
    LAKEHOUSE_DUCKDB,
    ROOT,
    REPO_ROOT,
    cl_argument_parser,
    connect_biep_lakehouse,
    connect_md_oideachais,
    import_dev_env_tool,
    lc_subject_query,
    leabharlann_join_to_lc,
    run_as_script,
)


def list_active_notebooks() -> list[str]:
    """List all 52 active (non-legacy) marimo notebook paths.

    Returns paths relative to the notebooks/ directory, sorted.
    """
    from pathlib import Path

    NB_ROOT = Path(__file__).resolve().parent
    paths = []
    for p in sorted(NB_ROOT.glob("*.py")):
        if p.name.startswith("_"):
            continue
        if "__pycache__" in str(p):
            continue
        if "legacy" in str(p):
            continue
        paths.append(str(p.relative_to(NB_ROOT)))
    return paths


__all__ = [
    # v14 helpers (canonical)
    "LITELLM_BASE_URL",
    "RAGAS_PASS_THRESHOLD",
    "setup_biep_registry_header",
    "tabbed_biep_operator_console",
    "progress_bar_with_eta",
    "form_gated_run_button",
    "run_dagster_asset_check",
    "llm_chat_with_prompts",
    "three_column_grid_app",
    "ragas_gauge_widget",
    "ragas_color",
    "ragas_status_emoji",
    "cli_argparser_biep",
    "cli_payload_to_output",
    "cli_main_if_argv",
    # BIEP v3 jurisdiction dashboard builder
    "build_biep_v3_dashboard",
    "build_overview_cell",
    "build_ibis_conn_cell",
    "build_commands_cell",
    "build_cohort_matrix_cell",
    "build_drill_down_cell",
    "build_schedule_cell",
    "build_asset_check_cell",
    "build_dive_link_cell",
    "build_llm_tab_cell",
    # BIEP v3 jurisdiction helpers (leaving_cert.py)
    "biiep_v3_overview",
    "BIEP_V3_OPERATOR_COMMANDS",
    "BIEP_V3_CRON_SCHEDULE",
    "BIEP_V3_MILESTONES",
    "BIEP_V3_MILESTONES_BY_JURISDICTION",
    "COHORT_COUNTS_BY_JURISDICTION",
    # RAGAS gauge anywidget (P5)
    "RAGASGaugeWidget",
    "RAGAS_EXCELLENT_THRESHOLD",
    # ibis-first connection helpers
    "connect_md",
    "connect_local",
    "connect_local_lakehouse",
    "connect_lance",
    "format_snake_case_cohort_path",
    "compute_ragas_distribution",
    "lakehouse_uri",
    "LAKEHOUSE_URI_DEFAULT",
    # Notebook inventory
    "list_active_notebooks",
    # Legacy back-compat (DEPRECATED — use _shared.*)
    "BIEP_LANGUAGES",
    "BIEP_LEVELS",
    "BIEP_SUBJECTS",
    "LAKEHOUSE_DUCKDB",
    "ROOT",
    "REPO_ROOT",
    "cl_argument_parser",
    "connect_biep_lakehouse",
    "connect_md_oideachais",
    "import_dev_env_tool",
    "lc_subject_query",
    "leabharlann_join_to_lc",
    "run_as_script",
]