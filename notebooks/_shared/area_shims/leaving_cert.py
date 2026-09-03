"""Leaving Cert + BIEP v3 notebooks per-area shim.

Re-exports the canonical ``connect_*()`` helpers from
``notebooks/_shared/db.py`` for use by every
``notebooks/19_*.py`` + ``notebooks/20_*.py`` + Ireland/England jurisdiction
dashboard notebook.

Also provides the canonical ``biiep_v3_overview()`` helper that returns
the 5-milestone systematic download plan + the BIEP v3 scheduling
policy + the snake_case file naming contract as a marimo-compatible
markdown string. The BIEP jurisdiction dashboards (notebooks 19, 20,
21, 22, 23) use this to render their consistent intro cells.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — use ``connect_md()``
  instead of raw ``duckdb.connect``.
- marimo (per `.agents/skills/marimo/SKILL.md`).

Reference: openspec/changes/2026-07-25-nb-utils-ibis-first-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

from notebooks._shared.db import (
    compute_ragas_distribution,
    connect_lance,
    connect_local,
    connect_local_lakehouse,
    connect_md,
    format_snake_case_cohort_path,
    lakehouse_uri,
)

__all__ = [
    "connect_md",
    "connect_local",
    "connect_local_lakehouse",
    "connect_lance",
    "format_snake_case_cohort_path",
    "compute_ragas_distribution",
    "lakehouse_uri",
    "biiep_v3_overview",
    "biiep_v3_milestone_progress",
    "BIEP_V3_MILESTONES",
    "BIEP_V3_CRON_SCHEDULE",
    "BIEP_V3_OPERATOR_COMMANDS",
]


# -----------------------------------------------------------------------------
# BIEP v3 systematic download + iterate: the 5 milestones
# -----------------------------------------------------------------------------

BIEP_V3_MILESTONES = (
    {
        "id": "M0",
        "title": "Foundation unblock",
        "cohorts": 0,
        "cron": "weekly (Mon 06:00 UTC)",
        "open_spec_change": "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "primary_test": "lakehouse_smoke_test + baml_codegen_gate + registry_seed_count >= 210 + lance_namespace_ready",
    },
    {
        "id": "M1",
        "title": "Ireland Leaving Cycle (EN + GA)",
        "cohorts": 12,
        "cron": "yearly (1st Sep 00:00 UTC)",
        "open_spec_change": "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "primary_test": "ireland_lc_documents_ingested >= 12 + ireland_lc_extractions_ragas >= 0.70 + ireland_lc_lance_chunks >= 12_000",
    },
    {
        "id": "M2",
        "title": "Ireland Junior Cycle (EN + GA)",
        "cohorts": 88,
        "cron": "yearly (1st Sep 00:00 UTC)",
        "open_spec_change": "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "primary_test": "ireland_jc_documents_ingested >= 88 + ireland_jc_extractions_ragas >= 0.65 + ireland_jc_lance_chunks >= 88_000",
    },
    {
        "id": "M3",
        "title": "England A-Level (AQA + OCR + Edexcel)",
        "cohorts": 147,
        "cron": "yearly (1st Sep 00:00 UTC)",
        "open_spec_change": "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "primary_test": "england_a_level_documents_ingested >= 147 + england_a_level_extractions_ragas >= 0.70 + england_a_level_lance_chunks >= 147_000",
    },
    {
        "id": "M4",
        "title": "England GCSE (AQA + OCR + Edexcel)",
        "cohorts": 129,
        "cron": "yearly (1st Sep 00:00 UTC)",
        "open_spec_change": "2026-08-13-biep-v3-systematic-download-ireland-england-v1",
        "primary_test": "england_gcse_documents_ingested >= 129 + england_gcse_extractions_ragas >= 0.70 + england_gcse_lance_chunks >= 129_000",
    },
)


# -----------------------------------------------------------------------------
# BIEP v3 scheduling policy (per the 2026-07-28 user direction)
# -----------------------------------------------------------------------------

BIEP_V3_CRON_SCHEDULE = (
    {
        "document_class": "NCCA + SEC + AQA + OCR + Edexcel education content (LC, JC, A-Level, GCSE)",
        "cadence": "Yearly",
        "cron": "0 0 1 9 *",
        "rationale": "Academic year starts in September; NCCA, SEC, AQA, OCR, and Edexcel publish updated syllabi in the weeks leading up to this date",
    },
    {
        "document_class": "gov.ie education circulars",
        "cadence": "Monthly",
        "cron": "0 0 1 * *",
        "rationale": "Circulars are published irregularly but at high frequency; a monthly poll covers the typical cadence",
    },
    {
        "document_class": "M0 foundation assets (smoke test, BAML codegen, registry seed, lance namespace)",
        "cadence": "Weekly",
        "cron": "0 6 * * 1",
        "rationale": "Smoke tests weekly on Monday 06:00 UTC; BAML codegen runs on BAML file change",
    },
    {
        "document_class": "BIEP v3 RAGAS + audit + asset checks",
        "cadence": "Nightly",
        "cron": "0 0 * * *",
        "rationale": "Cheap to run nightly; surfaces stale RAGAS scores, missed ingestion windows, 4-path ensemble drift",
    },
    {
        "document_class": "ChangeDetection.io sensors (NCCA, SEC, AQA, OCR, Edexcel, WJEC, CCEA, JCQ, IoM, Jersey, Guernsey)",
        "cadence": "Event-driven (eager)",
        "cron": "n/a",
        "rationale": "Triggers on every external spec change; event-driven ingestion",
    },
)


# -----------------------------------------------------------------------------
# BIEP v3 operator commands (canonical mise run + dagster + openspec commands)
# -----------------------------------------------------------------------------

BIEP_V3_OPERATOR_COMMANDS = (
    "# Foundation entrypoint (Docker + lakehouse stack + BAML codegen + registry seed + lance namespace)",
    "mise run biep:v3:m0",
    "",
    "# Per-milestone entrypoints (one at a time, in order)",
    "mise run biep:v3:m1   # Ireland Leaving Cycle (12 cohorts, EN+GA)",
    "mise run biep:v3:m2   # Ireland Junior Cycle (88 cohorts, EN+GA)",
    "mise run biep:v3:m3   # England A-Level (147 cohorts, AQA+OCR+Edexcel)",
    "mise run biep:v3:m4   # England GCSE (129 cohorts, AQA+OCR+Edexcel)",
    "",
    "# Per-milestone acceptance gate (verify the 3 asset checks pass)",
    "mise run biep:v3:gate --milestone=m<N>",
    "",
    "# ibis-first contract lint (verify no raw duckdb.connect() in BIEP v3 paths)",
    "mise run biep:v3:lint",
    "",
    "# snake_case filename validator (verify every PDF matches the canonical pattern)",
    "mise run biep:v3:filename-validate",
    "",
    "# Dagster asset operations (re-extract a specific asset)",
    "uv run dagster asset materialize --select <asset> -m orchestration.definitions",
    "uv run dagster asset check --select <check> -m orchestration.definitions",
    "",
    "# Per-subject backfill job (e.g. re-extract ireland_lc_mathematics_higher_en)",
    "uv run dagster job execute -j ireland_lc_mathematics_higher_en_backfill_job",
    "",
    "# OpenSpec validation + archive",
    "openspec validate 2026-08-13-biep-v3-systematic-download-ireland-england-v1 --strict",
    "openspec archive 2026-08-13-biep-v3-systematic-download-ireland-england-v1 --yes",
)


# -----------------------------------------------------------------------------
# Canonical helpers (used by the BIEP jurisdiction dashboards)
# -----------------------------------------------------------------------------

def biiep_v3_overview(jurisdiction: str = "all") -> str:
    """Return the canonical BIEP v3 overview markdown for a jurisdiction.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

    Parameters
    ----------
    jurisdiction : str
        One of: `ireland`, `england`, `scotland+wales+ni`, `crown`, `all`,
        or a specific milestone id (`M0`, `M1`, `M2`, `M3`, `M4`).
        Default: `all` (returns the full overview).

    Returns
    -------
    str
        A marimo-compatible markdown string with the BIEP v3 milestone
        summary, the scheduling policy, and the operator commands.
    """
    if jurisdiction in ("M0", "M1", "M2", "M3", "M4"):
        # Render a single-milestone summary
        milestone = next(m for m in BIEP_V3_MILESTONES if m["id"] == jurisdiction)
        return _render_single_milestone(milestone)

    if jurisdiction == "all":
        return _render_full_overview()

    # Jurisdiction-specific: filter the milestones to the relevant jurisdiction
    jurisdiction_milestones = {
        "ireland": ("M1", "M2"),
        "england": ("M3", "M4"),
        "scotland+wales+ni": ("M5", "M6"),  # reserved for the follow-up change
        "crown": ("M7", "M8"),  # reserved for the follow-up change
    }
    milestone_ids = jurisdiction_milestones.get(jurisdiction, ())
    relevant = [m for m in BIEP_V3_MILESTONES if m["id"] in milestone_ids]
    if not relevant:
        return _render_full_overview()
    return _render_jurisdiction_overview(jurisdiction, relevant)


def biiep_v3_milestone_progress(current_milestone: str = "M0") -> dict[str, Any]:
    """Return the milestone progress (used by the M0 foundation asset checks).

    Parameters
    ----------
    current_milestone : str
        The latest milestone that's been archived (M0..M4).

    Returns
    -------
    dict
        - `current_milestone`: the input current_milestone
        - `milestones_total`: 5
        - `milestones_complete`: count of milestones <= current_milestone
        - `progress_pct`: milestones_complete / milestones_total
        - `cohorts_total`: total cohorts across all 5 milestones (12 + 88 + 147 + 129 + 0)
        - `cohorts_complete`: sum of cohorts in completed milestones
        - `ready_for_m1`: current_milestone in ("M0", "M1")
    """
    milestone_order = {"M0": 0, "M1": 1, "M2": 2, "M3": 3, "M4": 4}
    current_idx = milestone_order.get(current_milestone, -1)
    completed = [m for m in BIEP_V3_MILESTONES if milestone_order[m["id"]] <= current_idx]
    return {
        "current_milestone": current_milestone,
        "milestones_total": 5,
        "milestones_complete": len(completed),
        "progress_pct": len(completed) / 5,
        "cohorts_total": sum(m["cohorts"] for m in BIEP_V3_MILESTONES),
        "cohorts_complete": sum(m["cohorts"] for m in completed),
        "ready_for_m1": current_milestone in ("M0", "M1"),
    }


# -----------------------------------------------------------------------------
# Internal rendering helpers
# -----------------------------------------------------------------------------

def _render_full_overview() -> str:
    """Render the full BIEP v3 overview (5 milestones + scheduling + commands)."""
    md = "# 🌐 BIEP v3 — Systematic Download & Iteration\n\n"
    md += "Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1` change.\n\n"
    md += "## 5 Milestones (M0 → M4, sequentially gated)\n\n"
    for m in BIEP_V3_MILESTONES:
        md += f"- **{m['id']}**: {m['title']} ({m['cohorts']} cohorts, {m['cron']})\n"
    md += "\n## 4-cadence Scheduling Policy\n\n"
    for s in BIEP_V3_CRON_SCHEDULE:
        md += f"- **{s['document_class']}** — {s['cadence']} (`{s['cron']}`)\n"
    md += "\n## Canonical Operator Commands\n\n"
    md += "```bash\n"
    for cmd in BIEP_V3_OPERATOR_COMMANDS:
        md += f"{cmd}\n"
    md += "```\n"
    return md


def _render_jurisdiction_overview(jurisdiction: str, milestones: list[dict]) -> str:
    """Render a jurisdiction-specific overview."""
    jurisdiction_labels = {
        "ireland": "🇮🇪 Ireland",
        "england": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 England",
        "scotland+wales+ni": "🏴󠁧󠁢󠁳󠁣󠁴󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿🇬🇧 SCT + WLS + NI",
        "crown": "🇯🇪🇬🇬🇮🇲 Crown Dependencies",
    }
    label = jurisdiction_labels.get(jurisdiction, jurisdiction)
    md = f"# {label} — BIEP v3 Pipelines\n\n"
    md += f"Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1` change.\n\n"
    md += "## Milestones\n\n"
    for m in milestones:
        md += f"- **{m['id']}**: {m['title']} ({m['cohorts']} cohorts, {m['cron']})\n"
    md += "\n## Primary test gate\n\n"
    for m in milestones:
        md += f"- **{m['id']}**: {m['primary_test']}\n"
    md += "\n## 4-cadence Scheduling Policy\n\n"
    for s in BIEP_V3_CRON_SCHEDULE:
        md += f"- **{s['document_class']}** — {s['cadence']} (`{s['cron']}`)\n"
    md += "\n## Canonical Operator Commands\n\n"
    md += "```bash\n"
    for cmd in BIEP_V3_OPERATOR_COMMANDS:
        md += f"{cmd}\n"
    md += "```\n"
    return md


def _render_single_milestone(milestone: dict) -> str:
    """Render a single-milestone summary."""
    md = f"# {milestone['id']} — {milestone['title']}\n\n"
    md += f"**Cohorts**: {milestone['cohorts']}\n\n"
    md += f"**Schedule**: {milestone['cron']}\n\n"
    md += f"**Primary test gate**: `{milestone['primary_test']}`\n\n"
    md += f"**OpenSpec change**: `{milestone['open_spec_change']}`\n\n"
    md += "## Canonical Operator Commands\n\n"
    md += "```bash\n"
    for cmd in BIEP_V3_OPERATOR_COMMANDS:
        md += f"{cmd}\n"
    md += "```\n"
    return md
