# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""04 — University institution matrix (oideachais-marimo-dashboards spec, R-v2-4).

Per-institution coverage view of the **Irish university / tertiary**
extraction — the 8 universities + 5 TUs + 3 colleges
(``UCD, UCG, UCC, UL, MU, TCD, DCU, RCSI`` +
``ATU, TUS, SETU, MTU, (TUDublin)`` + ``MIC, AUI, NCI``) loaded from
the canonical ``hei.json`` HEI catalogue.

Five visualisations:

- **Panel A** — institution-type distribution (UNIVERSITY / TU / COLLEGE pie)
- **Panel B** — institution × NFQ-max matrix (heatmap)
- **Panel C** — CAO-code-range coverage per institution
- **Panel D** — NUI constituent membership (bar chart)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.hei.institutions`` (populated by the
``hei_university`` DLT source from ``dlt/british_isles/ireland/education/hei.json``).
Falls back to the canonical 13-institution synthetic catalogue when
the lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-4 (Phase 2 — university extraction dashboard).
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # 🏛️ University institution matrix

        Per-institution coverage view of the **Irish university /
        tertiary** extraction — the 8 universities + 5 TUs + 3
        colleges loaded from the canonical ``hei.json`` HEI catalogue.

        Live data: ``md:cianfhoghlaim.hei.institutions`` (populated by
        the ``hei_university`` DLT source).

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os

    import altair as alt
    import duckdb
    import pandas as pd

    return alt, duckdb, os, pd


@app.cell
def _constants():
    """Canonical 13 Irish HEIs (per the ``oideachais-university-deep-extraction`` spec)."""
    HEI_CATALOG: tuple[dict[str, object], ...] = (
        {"code": "UCD", "name": "University College Dublin", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "NUI", "cao_codes": 8, "ga_slug": "ucd"},
        {"code": "UCG", "name": "University of Galway", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "NUI", "cao_codes": 6, "ga_slug": "ollscoil-na-gaillimhe"},
        {"code": "UCC", "name": "University College Cork", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "NUI", "cao_codes": 8, "ga_slug": "ucc"},
        {"code": "UL", "name": "University of Limerick", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "NUI", "cao_codes": 6, "ga_slug": "ollscoil-luimnigh"},
        {"code": "MU", "name": "Maynooth University", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "NUI", "cao_codes": 6, "ga_slug": "ollscoil-mha-nuad"},
        {"code": "TCD", "name": "Trinity College Dublin", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "Independent", "cao_codes": 7, "ga_slug": "colaiste-na-trionoide"},
        {"code": "DCU", "name": "Dublin City University", "type": "UNIVERSITY",
         "nfq_max": 10, "constituent": "Independent", "cao_codes": 6, "ga_slug": "dcu"},
        {"code": "RCSI", "name": "Royal College of Surgeons in Ireland", "type": "RCSI",
         "nfq_max": 10, "constituent": "Independent", "cao_codes": 1, "ga_slug": "rcsi"},
        {"code": "ATU", "name": "Atlantic Technological University", "type": "TU",
         "nfq_max": 9, "constituent": "Multi-campus", "cao_codes": 4, "ga_slug": "ollscoil-teicneolaiochta-an-atlantaigh"},
        {"code": "TUS", "name": "Technological University of the Shannon", "type": "TU",
         "nfq_max": 9, "constituent": "Multi-campus", "cao_codes": 2, "ga_slug": "ollscoil-teicneolaiochta-na-sionna"},
        {"code": "SETU", "name": "South East Technological University", "type": "TU",
         "nfq_max": 9, "constituent": "Multi-campus", "cao_codes": 2, "ga_slug": "ollscoil-teicneolaiochta-an-oirdheiscirt"},
        {"code": "MTU", "name": "Munster Technological University", "type": "TU",
         "nfq_max": 9, "constituent": "Multi-campus", "cao_codes": 2, "ga_slug": "ollscoil-teicneolaiochta-an-deiscirt"},
        {"code": "MIC", "name": "Mary Immaculate College", "type": "COLLEGE",
         "nfq_max": 10, "constituent": "NUI (linked to UL)", "cao_codes": 1, "ga_slug": "colaiste-mhuire-gan-smal"},
    )
    """The 13 canonical Irish HEIs (8 universities + 4 TUs + 1 college)."""

    return (HEI_CATALOG,)


@app.cell
def _lakehouse_connect(mo, duckdb, os):
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            engine_label = "md:cianfhoghlaim"
        except Exception as exc:
            con = ibis.duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = ibis.duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_hei_institutions ("
        "  code VARCHAR, name VARCHAR, type VARCHAR, nfq_max INTEGER,"
        "  constituent VARCHAR, cao_codes INTEGER, ga_slug VARCHAR"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(HEI_CATALOG, con, engine_label, mo, pd):
    """Read HEI institutions — live or synthetic fallback."""
    src = engine_label
    institutions = pd.DataFrame()

    if engine_label == "md:cianfhoghlaim":
        try:
            institutions = con.execute(
                "SELECT * FROM cianfhoghlaim.hei.institutions"
            ).fetchdf()
        except Exception:
            institutions = pd.DataFrame()

    if institutions.empty:
        institutions = pd.DataFrame(list(HEI_CATALOG))
        src = "synthetic (13 canonical HEIs from hei.json)"

    mo.md(f"**Source**: `{src}` — **{len(institutions)}** institutions")
    return institutions, src


@app.cell
def _viz_type_distribution(alt, mo, institutions):
    """Panel A — institution-type distribution (pie)."""
    by_type = (
        institutions.groupby("type", as_index=False)
        .size()
        .rename(columns={"size": "institution_count"})
    )
    chart = (
        alt.Chart(by_type)
        .mark_arc(innerRadius=80)
        .encode(
            theta=alt.Theta("institution_count:Q"),
            color=alt.Color("type:N", title="Type"),
            tooltip=["type", "institution_count"],
        )
        .properties(
            width=380,
            height=280,
            title="Panel A — institution-type distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return by_type, chart


@app.cell
def _viz_nfq_matrix(alt, mo, institutions):
    """Panel B — institution × NFQ-max matrix (heatmap)."""
    chart = (
        alt.Chart(institutions)
        .mark_rect()
        .encode(
            x=alt.X("code:N", title="Institution code"),
            y=alt.Y("nfq_max:O", title="NFQ max level"),
            color=alt.Color(
                "nfq_max:Q",
                title="NFQ max",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["code", "name", "nfq_max"],
        )
        .properties(
            width=620,
            height=200,
            title="Panel B — institution × NFQ-max coverage",
        )
    )
    mo.ui.altair_chart(chart)
    return (chart,)


@app.cell
def _viz_cao_coverage(alt, mo, institutions):
    """Panel C — CAO-code-range coverage per institution (horizontal bar)."""
    chart = (
        alt.Chart(institutions)
        .mark_bar()
        .encode(
            x=alt.X("cao_codes:Q", title="CAO code variants"),
            y=alt.Y(
                "code:N",
                title="Institution",
                sort=institutions["code"].tolist(),
            ),
            color=alt.Color(
                "type:N",
                title="Type",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["code", "name", "cao_codes", "type"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel C — CAO code-range coverage per institution",
        )
    )
    mo.ui.altair_chart(chart)
    return (chart,)


@app.cell
def _viz_constituent(alt, mo, institutions):
    """Panel D — NUI constituent membership (grouped bar)."""
    by_constituent = (
        institutions.groupby("constituent", as_index=False)
        .size()
        .rename(columns={"size": "institution_count"})
        .sort_values("institution_count", ascending=False)
    )
    chart = (
        alt.Chart(by_constituent)
        .mark_bar()
        .encode(
            x=alt.X("constituent:N", title="Constituent", sort="-y"),
            y=alt.Y("institution_count:Q", title="Institutions"),
            color=alt.Color("institution_count:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=["constituent", "institution_count"],
        )
        .properties(
            width=560,
            height=260,
            title="Panel D — NUI / TU / Independent constituent membership",
        )
    )
    mo.ui.altair_chart(chart)
    return by_constituent, chart


@app.cell
def _health_banner(mo, engine_label, institutions):
    if engine_label == "md:cianfhoghlaim":
        _n = len(institutions)
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n = 0
        status = "🟡 md unreachable"
    else:
        _n = len(institutions)
        status = "🟡 offline fallback (synthetic HEI catalogue)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | institutions | {_n} |
        | source | ``hei.json`` |
        """
    )
    return _n, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🏛️ This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-4 (Phase 2 — the
        university institution matrix). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()