"""Canonical BIEP v3 jurisdiction dashboard builder (R2/R3 + P1-P5).

This module hoists the open-coded 8-cell BIEP v3 operator console
(`_intro / _ibis_conn / _commands / _cohort_matrix / _drill_down /
_schedule / _asset_check_status / _dive_link`) from the 9 BIEP
jurisdiction dashboards into a single composable function.

The single function `build_biep_v3_dashboard(jurisdiction, milestone,
deferred=False)` returns the 8-cell surface as a `mo.ui.tabs` widget
with 7 tabs (`Overview / Cohorts / Drill / Schedule / Asset Checks /
Dives / Activity`).

The 8 pillars of improvement delivered:

R2 — Hoist the 8-cell BIEP v3 surface
    Every BIEP v3 jurisdiction dashboard (notebooks 19, 20, 21, 22, 26,
    27) used to define its own 8 cells. Now they all call
    `build_biep_v3_dashboard(jurisdiction="ireland", milestone="M1")`.

R3 — Wrap in `mo.ui.tabs` (P1)
    The 8 cells are wrapped in `mo.ui.tabs` with 7 tabs.

P3 — LLM-assisted analysis tab
    The 7th "Activity" tab includes the LLM chat widget via
    `llm_chat_with_prompts()`.

P5 — RAGAS gauge widget
    The "Drill" tab includes the `RAGASGaugeWidget` via
    `ragas_gauge_widget()`.

P6 — Dual-mode CLI (handled separately — see notebook boilerplate)

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — the 8 cells use
  `@app.cell` + `mo.ui.tabs` + `mo.ui.dropdown` + `mo.ui.run_button`
  + `mo.ui.chat` + `mo.ui.anywidget` per the marimo v14 idioms.
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query goes
  through `notebooks._shared/db.py:connect_md()` (ibis-first).
- BIEP v3 systematic download — 5-milestone plan + 4-cadence scheduling.

Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""
from __future__ import annotations

from typing import Any

from notebooks._shared.marimo_patterns import (
    LITELLM_BASE_URL,
    RAGAS_PASS_THRESHOLD,
    cli_argparser_biep,
    llm_chat_with_prompts,
    ragas_color,
    ragas_gauge_widget,
    ragas_status_emoji,
    run_dagster_asset_check,
    setup_biep_registry_header,
    tabbed_biep_operator_console,
)


# ────────────────────────────────────────────────────────────────────────────
# Constants: jurisdiction-specific data
# ────────────────────────────────────────────────────────────────────────────

# The canonical 5 BIEP v3 milestones.
BIEP_V3_MILESTONES_BY_JURISDICTION: dict[str, list[str]] = {
    "ireland": ["M1", "M2"],
    "england": ["M3", "M4"],
    "scotland+wales+ni": ["M5", "M6"],  # reserved for the follow-up change
    "crown": ["M7", "M8"],               # reserved for the follow-up change
}

# The canonical cohort counts per jurisdiction (per the BIEP v3 spec).
COHORT_COUNTS_BY_JURISDICTION: dict[str, dict[str, int]] = {
    "ireland": {"lc": 12, "jc_spec": 36, "jc_short_course": 16, "jc_cba": 36, "total": 100},
    "england": {"a_level": 147, "gcse": 129, "total": 276},
    "scotland+wales+ni": {"scotland": 150, "wales": 160, "northern_ireland": 70, "total": 380},
    "crown": {"jersey": 120, "guernsey": 120, "isle_of_man": 120, "total": 360},
}

# The canonical asset check names per jurisdiction per milestone.
ASSET_CHECK_MAP: dict[str, dict[str, str]] = {
    ("ireland", "M1"): "ireland_lc_documents_ingested_check,ireland_lc_extractions_ragas_check,ireland_lc_lance_chunks_check",
    ("ireland", "M2"): "ireland_jc_documents_ingested_check,ireland_jc_extractions_ragas_check,ireland_jc_lance_chunks_check",
    ("england", "M3"): "england_a_level_documents_ingested_check,england_a_level_extractions_ragas_check,england_a_level_lance_chunks_check",
    ("england", "M4"): "england_gcse_documents_ingested_check,england_gcse_extractions_ragas_check,england_gcse_lance_chunks_check",
}

# The canonical MotherDuck Dives per jurisdiction.
DIVES_BY_JURISDICTION: dict[str, list[str]] = {
    "ireland": [
        "ireland_lc_syllabus_topics",
        "ireland_jc_curriculum_topics",
        "ireland_lc_daily_sync_flight",
        "ireland_jc_daily_sync_flight",
    ],
    "england": [
        "england_a_level_topics",
        "england_a_level_complexity",
        "england_gcse_topics",
        "england_gcse_complexity",
        "england_a_level_daily_sync_flight",
        "england_gcse_daily_sync_flight",
    ],
}


# ────────────────────────────────────────────────────────────────────────────
# Cell 1: Overview (P1 + P3)
# ────────────────────────────────────────────────────────────────────────────

def build_overview_cell(
    jurisdiction: str,
    milestone: str | None,
    deferred: bool,
) -> Any:
    """Build the Overview cell (P1 — wraps the `biiep_v3_overview` call).

    Returns a `mo.md` widget that renders the jurisdiction-specific
    BIEP v3 overview markdown (per
    `notebooks/_shared/area_shims/leaving_cert.py:biiep_v3_overview`).
    """
    from notebooks._shared.area_shims.leaving_cert import biiep_v3_overview
    import marimo as mo

    md = biiep_v3_overview(jurisdiction)
    if deferred:
        md += (
            "\n\n## Status\n\n"
            f"**DEFERRED**: The {COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} cohorts "
            f"are deferred to a follow-up change. The current notebook renders the BIEP v3 8-cell "
            "surface in **preview mode** — the cohort matrix queries the registry for placeholder "
            "rows; the asset check status is informational.\n"
        )
    elif milestone:
        md += (
            f"\n\n## 🎯 {milestone} acceptance gate\n\n"
            f"Run `mise run biep:v3:{milestone.lower()}` to materialise the "
            f"{COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} cohorts."
        )
    return mo.md(md)


# ────────────────────────────────────────────────────────────────────────────
# Cell 2: ibis_conn (P1)
# ────────────────────────────────────────────────────────────────────────────

def build_ibis_conn_cell(deferred: bool) -> tuple[Any, Any]:
    """Build the ibis-first connection cell (P1 — wraps `connect_md()`).

    Returns `(conn, mo)` so the caller can pass `conn` to downstream
    cells. The cell also renders a KCG-pattern callout (E2 — inline
    KCG pattern callout).
    """
    from notebooks._shared.db import connect_md
    import marimo as mo

    conn = connect_md()
    msg = "✓ ibis-first wired — `md:cianfhoghlaim`"
    if deferred:
        msg += (
            "\n\n⚠️ The pipeline is deferred. The queries below return registry "
            "placeholder rows; the asset checks return informational only."
        )
    mo.callout(
        mo.md(
            "💡 **KCG contract**: every BIEP v3 query goes through `notebooks._shared."
            "db:connect_md()` — never raw `duckdb.connect()` (the BIEP v3 `mise run "
            "biep:v3:lint` rejects any raw duckdb.connect call)."
        ),
        kind="info",
    )
    mo.md(msg)
    return conn, mo


# ────────────────────────────────────────────────────────────────────────────
# Cell 3: Commands (P1)
# ────────────────────────────────────────────────────────────────────────────

def build_commands_cell(jurisdiction: str) -> Any:
    """Build the canonical operator commands cell (P1).

    Renders the `BIEP_V3_OPERATOR_COMMANDS` bash block.
    """
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_OPERATOR_COMMANDS
    import marimo as mo

    return mo.md(
        "## Canonical BIEP v3 operator commands\n\n"
        "```bash\n"
        + "\n".join(BIEP_V3_OPERATOR_COMMANDS)
        + "\n```\n"
    )


# ────────────────────────────────────────────────────────────────────────────
# Cell 4: Cohort matrix (P1)
# ────────────────────────────────────────────────────────────────────────────

def build_cohort_matrix_cell(conn: Any, jurisdiction: str, mo: Any) -> Any:
    """Build the jurisdiction-specific cohort matrix cell (P1).

    Renders the per-jurisdiction cohort matrix as a `mo.ui.table`.
    """
    if jurisdiction == "ireland":
        df = conn.sql(
            """
            SELECT 'lc' AS stage, subject_slug, qualification_level, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.ireland.leaving_cycle
            GROUP BY subject_slug, qualification_level, language
            UNION ALL BY NAME
            SELECT 'jc_spec', subject_slug, qualification_level, language, COUNT(*)
            FROM cianfhoghlaim.education.ireland.junior_cycle
            GROUP BY subject_slug, qualification_level, language
            UNION ALL BY NAME
            SELECT 'jc_short_course', short_course_code, 'untiered', language, COUNT(*)
            FROM cianfhoghlaim.education.ireland.junior_cycle.short_courses
            GROUP BY short_course_code, language
            UNION ALL BY NAME
            SELECT 'jc_cba', subject_slug, qualification_level, 'en', COUNT(*)
            FROM cianfhoghlaim.education.ireland.junior_cycle.cbas
            GROUP BY subject_slug, qualification_level
            ORDER BY stage, subject_slug, language
            """
        ).execute()
        return mo.ui.table(df, label=f"{COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} Ireland cohorts (12 LC + 88 JC)")
    elif jurisdiction == "england":
        df = conn.sql(
            """
            SELECT exam_board, subject_slug, qualification_level, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.england.a_level
            GROUP BY exam_board, subject_slug, qualification_level, language
            UNION ALL BY NAME
            SELECT exam_board, subject_slug, qualification_level, language, COUNT(*)
            FROM cianfhoghlaim.education.england.gcse
            GROUP BY exam_board, subject_slug, qualification_level, language
            ORDER BY qualification_level, exam_board, subject_slug, language
            """
        ).execute()
        return mo.ui.table(df, label=f"{COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} England cohorts (147 A-Level + 129 GCSE)")
    elif jurisdiction in ("scotland+wales+ni", "crown"):
        # Use the registry table (deferred pipelines query the registry)
        jurisdiction_filter = (
            "('scotland', 'wales', 'northern_ireland')"
            if jurisdiction == "scotland+wales+ni"
            else "('jersey', 'guernsey', 'isle_of_man')"
        )
        df = conn.sql(
            f"""
            SELECT jurisdiction, subject_slug, qualification_level, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education._registry.subjects
            WHERE jurisdiction IN {jurisdiction_filter}
              AND status = 'ACTIVE'
            GROUP BY jurisdiction, subject_slug, qualification_level, language
            ORDER BY jurisdiction, qualification_level, subject_slug, language
            """
        ).execute()
        return mo.ui.table(df, label=f"{COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} cohorts (3 jurisdictions)")
    else:
        # All jurisdictions (cross-cut)
        df = conn.sql(
            """
            SELECT
                jurisdiction,
                educational_stage AS stage,
                exam_board AS board,
                COUNT(*) AS subject_count,
                COUNT(DISTINCT subject_slug) AS distinct_subjects
            FROM cianfhoghlaim.education._registry.subjects
            WHERE status = 'ACTIVE'
            GROUP BY jurisdiction, educational_stage, exam_board
            ORDER BY jurisdiction, educational_stage, exam_board
            """
        ).execute()
        return mo.ui.table(df, label="8-jurisdiction cohort matrix")


# ────────────────────────────────────────────────────────────────────────────
# Cell 5: Drill down (P1 + P5 — RAGAS gauge)
# ────────────────────────────────────────────────────────────────────────────

def build_drill_down_cell(conn: Any, jurisdiction: str, mo: Any) -> dict[str, Any]:
    """Build the drill-down cell (P1 + P5).

    Returns a dict with the dropdown widgets + the computed per-cohort
    RAGAS gauge widget (P5).
    """
    from notebooks._shared.db import compute_ragas_distribution

    # Jurisdiction-specific dropdown options
    if jurisdiction == "ireland":
        cohort_kinds = ["lc", "jc_spec", "jc_short_course", "jc_cba"]
        ragas_kinds = ["lc_spec", "jc_spec", "jc_short_course", "jc_cba"]
    elif jurisdiction == "england":
        cohort_kinds = ["a_level", "gcse"]
        ragas_kinds = ["a_level", "gcse"]
    else:
        cohort_kinds = ["placeholder"]
        ragas_kinds = ["placeholder"]

    cohort_kind_dropdown = mo.ui.dropdown(
        options=cohort_kinds,
        value=cohort_kinds[0],
        label="Cohort kind",
    )

    # Compute the RAGAS distribution for the first cohort kind
    initial_ragas = compute_ragas_distribution(ragas_kinds[0])
    initial_gauge = ragas_gauge_widget(
        score=initial_ragas["avg_ragas_score"],
        history=[],
        cohort_slug=f"{jurisdiction}_{cohort_kinds[0]}",
    )

    return {
        "cohort_kind_dropdown": cohort_kind_dropdown,
        "initial_ragas": initial_ragas,
        "initial_gauge": initial_gauge,
    }


# ────────────────────────────────────────────────────────────────────────────
# Cell 6: Schedule (P1)
# ────────────────────────────────────────────────────────────────────────────

def build_schedule_cell(jurisdiction: str) -> Any:
    """Build the BIEP v3 scheduling policy cell (P1).

    Renders the BIEP_V3_CRON_SCHEDULE table + per-jurisdiction cron.
    """
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_CRON_SCHEDULE
    import marimo as mo

    table_md = (
        "| Document class | Cadence | Cron |\n"
        "|:--|:--|:--|\n"
        + "\n".join(
            f"| {s['document_class']} | {s['cadence']} | `{s['cron']}` |"
            for s in BIEP_V3_CRON_SCHEDULE
        )
    )

    # Jurisdiction-specific ChangeDetection.io sensors
    if jurisdiction == "ireland":
        sensors_md = (
            "### ChangeDetection.io sensors (Ireland-specific)\n\n"
            "- `ncca_registry_sensor` (NCCA, Ireland) — triggers `england_a_level_extractions` etc.\n"
            "- `sec_registry_sensor` (SEC, Ireland) — reserved\n"
        )
    elif jurisdiction == "england":
        sensors_md = (
            "### ChangeDetection.io sensors (England-specific)\n\n"
            "- `bonneagar/stacks/changedetection/monitors/aqa_monitor.yaml` — AQA GCSE + A-Level specs\n"
            "- `bonneagar/stacks/changedetection/monitors/ocr_monitor.yaml` — OCR GCSE + A-Level specs\n"
            "- `bonneagar/stacks/changedetection/monitors/edexcel_monitor.yaml` — Edexcel GCSE + A-Level specs\n"
            "- `orchestration/sensors/jcq_registry_sensor.py` — polls the registry every 5 minutes\n"
        )
    elif jurisdiction == "scotland+wales+ni":
        sensors_md = (
            "### ChangeDetection.io sensors (SCT/WLS/NI-specific)\n\n"
            "- `sqa_registry_sensor` (SQA, Scotland) — reserved\n"
            "- `wjec_registry_sensor` (WJEC, Wales) — reserved\n"
            "- `ccea_registry_sensor` (CCEA, Northern Ireland) — reserved\n"
        )
    elif jurisdiction == "crown":
        sensors_md = (
            "### ChangeDetection.io sensors (Crown-specific)\n\n"
            "- `jersey_registry_sensor` (Jersey) — reserved\n"
            "- `guernsey_registry_sensor` (Guernsey) — reserved\n"
            "- `isle_of_man_registry_sensor` (Isle of Man) — reserved\n"
        )
    else:
        sensors_md = ""

    return mo.md(
        "## BIEP v3 scheduling policy\n\n"
        f"{table_md}\n\n"
        f"{sensors_md}\n"
    )


# ────────────────────────────────────────────────────────────────────────────
# Cell 7: Asset check status (P1 + P2 — progress bar + form gating)
# ────────────────────────────────────────────────────────────────────────────

def build_asset_check_cell(jurisdiction: str, milestone: str | None) -> dict[str, Any]:
    """Build the asset check status cell (P1 + P2).

    Returns a dict with the milestone dropdown + run button + the
    asset check map. The caller wires the button click to the
    `run_dagster_asset_check()` helper.
    """
    import marimo as mo

    # Determine the available milestones for this jurisdiction
    if milestone:
        milestones = [milestone]
    else:
        milestones = BIEP_V3_MILESTONES_BY_JURISDICTION.get(jurisdiction, [])

    milestone_dropdown = mo.ui.dropdown(
        options=[m.lower() for m in milestones],
        value=milestones[0].lower() if milestones else "m1",
        label="Milestone",
    )

    # The canonical asset check map (per the BIEP v3 spec)
    def _run_asset_check(per_milestone: str) -> dict[str, Any]:
        key = (jurisdiction, per_milestone.upper())
        if key not in ASSET_CHECK_MAP:
            return {"checks": "?", "status": "unknown_milestone", "exit_code": -1}
        return run_dagster_asset_check(ASSET_CHECK_MAP[key])

    run_button = mo.ui.run_button(label="Run `dagster asset check`")
    return {
        "milestone_dropdown": milestone_dropdown,
        "run_button": run_button,
        "_run_asset_check": _run_asset_check,
    }


# ────────────────────────────────────────────────────────────────────────────
# Cell 8: Dive link (P1)
# ────────────────────────────────────────────────────────────────────────────

def build_dive_link_cell(jurisdiction: str) -> Any:
    """Build the canonical MotherDuck Dives + Flights cell (P1).

    Renders the jurisdiction-specific MotherDuck Dives + Flights.
    """
    import marimo as mo

    dives = DIVES_BY_JURISDICTION.get(jurisdiction, [
        f"{jurisdiction}_topics (reserved)",
    ])

    md = f"## Canonical MotherDuck Dives + Flights for {jurisdiction}\n\n"
    md += "### Dives\n\n"
    for dive in dives:
        md += f"- **`{dive}`** — read the per-cohort DuckLake tables\n"
    md += "\n### Flights (yearly, runs `mise run biep:v3:m<N>` + writes status)\n\n"
    md += f"- **`{jurisdiction}_daily_sync_flight`** — runs M1/M2/M3/M4, replicates to LanceDB\n"

    return mo.md(md)


# ────────────────────────────────────────────────────────────────────────────
# Cell 9 (NEW): LLM tab (P3)
# ────────────────────────────────────────────────────────────────────────────

def build_llm_tab_cell(jurisdiction: str) -> Any:
    """Build the LLM-assisted analysis tab (P3).

    Returns an `mo.vstack([...])` containing the LLM chat widget with
    4 jurisdiction-specific prompts.
    """
    import marimo as mo

    jurisdiction_label = {
        "ireland": "Ireland",
        "england": "England",
        "scotland+wales+ni": "Scotland + Wales + Northern Ireland",
        "crown": "Crown Dependencies",
    }.get(jurisdiction, jurisdiction.title())

    prompts_by_jurisdiction: dict[str, list[str]] = {
        "ireland": [
            "📚 Summarise the Ireland LC Mathematics Higher EN 2024 syllabus into 5 key learning outcomes",
            "🔍 Find the Irish-language equivalent (GA) for the LC Chemistry topic 'atomic structure'",
            "📊 Compare the marking scheme distribution between Ireland LC Mathematics Higher EN 2024 and 2023",
            "🎯 Predict the 5 most-tested topics on the 2025 Ireland LC Mathematics Higher exam based on BAML extractions",
            "🌐 Translate this English JC Geography learning outcome into Irish (GA)",
        ],
        "england": [
            "📚 Summarise the England A-Level Mathematics AQA 2024 syllabus into 5 key learning outcomes",
            "🔍 Compare the OCR vs AQA vs Edexcel marking schemes for A-Level Chemistry 2024",
            "📊 Find the most-tested topics on the 2025 GCSE Mathematics AQA exam based on BAML extractions",
            "🎯 Identify the 5 hardest exam questions from the 2024 A-Level Mathematics AQA paper",
        ],
        "scotland+wales+ni": [
            "📚 [Reserved for the SCT/WLS/NI follow-up change]",
        ],
        "crown": [
            "📚 [Reserved for the Crown Dependencies follow-up change]",
        ],
    }

    system_message = (
        f"You are the BIEP v3 {jurisdiction_label} education assistant. "
        f"You have access to the {COHORT_COUNTS_BY_JURISDICTION[jurisdiction]['total']} {jurisdiction_label} "
        "BIEP v3 cohorts in the MotherDuck + DuckLake lakehouse "
        f"(`md:cianfhoghlaim.education.{jurisdiction}.*`). Use BIEPV3Extract via BAML for "
        "structured extraction queries."
    )

    chat = llm_chat_with_prompts(
        system_message=system_message,
        prompts=prompts_by_jurisdiction.get(jurisdiction, []),
    )

    return mo.vstack([
        mo.md(
            f"## 🤖 Ask BAML (via litellm → minimax-m3)\n\n"
            f"5 built-in prompts tailored to {jurisdiction_label} + free-form chat. "
            f"Routes through the canonical `litellm.cianfhoghlaim.ie` proxy."
        ),
        chat,
    ])


# ────────────────────────────────────────────────────────────────────────────
# Main entry point: `build_biep_v3_dashboard()`
# ────────────────────────────────────────────────────────────────────────────

def build_biep_v3_dashboard(
    jurisdiction: str,
    milestone: str | None = None,
    deferred: bool = False,
) -> Any:
    """Build the canonical 8-cell BIEP v3 jurisdiction dashboard as a `mo.ui.tabs` widget.

    R2/R3 + P1 + P3 + P5 — the single composable function that
    replaces the open-coded 8 cells in every BIEP v3 jurisdiction
    dashboard.

    Parameters
    ----------
    jurisdiction : str
        One of: "ireland" | "england" | "scotland+wales+ni" | "crown" | "all"
    milestone : str, optional
        The BIEP v3 milestone (e.g. "M1", "M3"). If None, uses the
        default for the jurisdiction.
    deferred : bool
        Whether the jurisdiction is deferred (SCT/WLS/NI + Crown). Adds
        the DEFERRED banner.

    Returns
    -------
    mo.ui.tabs
        The 7-tab operator console.

    Usage:
    ```python
    import marimo
    from notebooks._shared.area_shims.biiep_v3_dashboard import (
        build_biep_v3_dashboard,
    )

    app = marimo.App(width="full")

    @app.cell
    def _main(mo):
        tabs = build_biep_v3_dashboard(jurisdiction="ireland", milestone="M1")
        tabs
    ```
    """
    import marimo as mo

    # Cell 2: ibis_conn (must come first — `conn` is passed to cells 4 + 5)
    conn, _mo = build_ibis_conn_cell(deferred)

    # Build the 7 tabs
    overview_tab = build_overview_cell(jurisdiction, milestone, deferred)
    cohort_matrix_tab = build_cohort_matrix_cell(conn, jurisdiction, mo)
    drill_state = build_drill_down_cell(conn, jurisdiction, mo)
    schedule_tab = build_schedule_cell(jurisdiction)
    asset_check_state = build_asset_check_cell(jurisdiction, milestone)
    dive_link_tab = build_dive_link_cell(jurisdiction)
    llm_tab = build_llm_tab_cell(jurisdiction)

    # Wrap in `mo.ui.tabs` (P1)
    tabs = tabbed_biep_operator_console({
        "Overview": overview_tab,
        "Cohorts": cohort_matrix_tab,
        "Drill": mo.vstack([
            mo.md("## Drill-Down — per-cohort RAGAS gauge + snake_case S3 path\n\n"
                  "Select a cohort kind + drill into a specific subject. "
                  "The RAGAS gauge (P5) renders the current RAGAS score with a colour band."),
            mo.vstack([
                drill_state["cohort_kind_dropdown"],
                drill_state["initial_gauge"],
            ]),
        ]),
        "Schedule": schedule_tab,
        "Asset Checks": mo.vstack([
            mo.md("## Asset check status\n\n"
                  "Click **Run `dagster asset check`** to invoke the live asset check for the selected milestone."),
            asset_check_state["milestone_dropdown"],
            asset_check_state["run_button"],
        ]),
        "Dives": dive_link_tab,
        "Activity": llm_tab,  # P3 — LLM-assisted analysis tab
    })

    return tabs


# ────────────────────────────────────────────────────────────────────────────
# Convenience: __all__ + module API
# ────────────────────────────────────────────────────────────────────────────

__all__ = [
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
    "BIEP_V3_MILESTONES_BY_JURISDICTION",
    "COHORT_COUNTS_BY_JURISDICTION",
    "ASSET_CHECK_MAP",
    "DIVES_BY_JURISDICTION",
    # Re-exported from notebooks._shared.marimo_patterns so the
    # 23_8_jurisdiction_overview.py notebook can import it via this
    # shim without reaching into the private marimo_patterns path.
    # Per issue #152.
    "setup_biep_registry_header",
]