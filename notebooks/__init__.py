"""cianfhoghlaim.notebooks — the BIEP Marimo notebook package.

The 70+ notebook files are organised into 11 functional groups:

    01_dev_env/             6 dev_env demos (ccc, drift, firecrawl, hf, openspec, mise)
    02_vision_models/       6 OCR/VLM dispatch + layout/table/diagram
    03_leaving_cert/        17 BIEP LC subject + PDF + root-PDF analyses
    04_biep_motherduck/     11 MotherDuck + DuckLake BIEP analytics
    05_lakehouse_inspect/   4 DuckLake + Lance + CocoIndex + DLT inspection
    06_observability/       3 BAML drift + Irish fada + Cognee KG
    07_educational_stages/  7 5 NCCA stages + cross-domain + analysis_plan viewer
    08_sources/             1 sources.yaml federation
    09_official_media/      2 Instagram → gov resolver + email triage
    10_mmo/                 2 mission control + MMO progress
    11_speedrun/            9 SpeedRunEthereum tutorials (Celtic-creature NFT theme)

Legacy:
    legacy/                 1-cycle preservation window for v4 teacher views +
                            Gemini-6 corpus dashboards (auto-deleted at archive time)

Helpers (re-exported from nb_utils.py):

    from cianfhoghlaim.notebooks import (
        connect_biep_lakehouse,        # MotherDuck + local fallback
        lc_subject_query,              # per-subject topic query
        leabharlann_join_to_lc,        # cross-archive join
        cl_argument_parser,            # BIEP canonical CLI flags
        run_as_script,                 # exit-code wrapper for CLI mode
        import_dev_env_tool,           # Phase-1 convenience helper
        BIEP_SUBJECTS,                 # the 6 LC priority subjects
        BIEP_LEVELS,                   # higher | ordinary | foundation
        BIEP_LANGUAGES,                # en | ga
        REPO_ROOT,                     # monorepo root
    )

Reference: openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/
"""
from .nb_utils import (
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

__all__ = [
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
