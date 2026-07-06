# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///
# Marimo notebook for teacher view of the 5 NCCA root-level programme PDFs.
#
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
# ncca-leaving-cert-root-pdfs/spec.md Requirement R6.
#
# Renders:
# - A tab per root PDF (Key Competencies / Online Learning / Certification /
#   SCR Advisory / Programme Statement)
# - Each tab shows the extracted content + the source PDF reference +
#   the BGE-M3 embedding visualised as a 2D scatter plot (UMAP projection)
#
# The actual embeddings are loaded from the LanceDB-backed table
# `oideachais.lc.root.key_competencies_en` (and the 4 sibling variants)
# via DuckDB's `lance_scan()` function.
#
# Run: `uv run marimo edit notebooks/root_pdfs_explorer.py`

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Root PDFs Explorer — Teacher View

        The 5 NCCA root-level programme PDFs at
        `cianfhoghlaim/leaving_certificate/*.pdf` are the
        cross-subject foundation of the entire Leaving Cert
        curriculum. Their BGE-M3 embeddings land in the
        `oideachais.lc.root.<key>.<lang>` LanceDB tables (queryable
        from DuckDB via `lance_scan()`).

        Select a tab below to explore each PDF.
        """
    )
    return


@app.cell
def _(mo):
    tabs = mo.ui.tabs(
        {
            "Key Competencies": mo.md(
                """
                ## NCCA Senior Cycle Key Competencies

                The 5 NCCA Senior Cycle Key Competencies (Information
                Processing, Communicating, Working with Others, Personal
                Effectiveness, Critical & Creative Thinking) are the
                foundation of the cross-subject mastery matrix.

                LanceDB backing: `oideachais.lc.root.key_competencies_en`
                (`lance_scan('s3://garage/lance/oideachais.lc.root.key_competencies_en/*.lance')`).

                See `docs/CIANFHLOGHLAIM_LORE.md` for the mapping to the
                Tuatha Dé Danann deities (Ogma + Brigid + the Trí Dé Dána).
                """
            ),
            "Online Learning": mo.md(
                """
                ## Online Learning Pedagogy

                The pedagogical principles for online learning extracted
                from `the-potential-of-online-learning-environments_en.pdf`.
                Backed by `oideachais.lc.root.online_learning_en`.
                """
            ),
            "Certification": mo.md(
                """
                ## Online Certification + Reporting Guidance

                The certification mechanisms + reporting recommendations
                extracted from `the-potential-of-technology-to-support-online-certification-and-reporting.pdf`.
                Backed by `oideachais.lc.root.online_certification_en`.
                """
            ),
            "SCR Advisory": mo.md(
                """
                ## State Examinations Commission Advisory

                The Chief Examiner commentary extracted from
                `scr-advisory-report_en.pdf`. Used by the Practice page
                "Exam Layout Tips" section. Backed by
                `oideachais.lc.root.scr_advisory_en`.
                """
            ),
            "Programme Statement": mo.md(
                """
                ## Senior Cycle L1 + L2 Programme Statement

                The aims + expectations for students at L1 (Foundation)
                and L2 (Ordinary) levels extracted from
                `SC-L1-L2-Programme-Statement.pdf`. Backed by
                `oideachais.lc.root.programme_statement_en`.
                """
            ),
        }
    )
    tabs
    return (tabs,)


_LANCE_ROOT_PREFIX = (
    "s3://garage/lance/oideachais.lc.root.{key}_{lang}"
)
_LANCE_TAB_KEY = {
    "Key Competencies": "key_competencies",
    "Online Learning": "online_learning",
    "Certification": "online_certification",
    "SCR Advisory": "scr_advisory",
    "Programme Statement": "programme_statement",
}


@app.cell
def _(tabs):
    import duckdb
    key = _LANCE_TAB_KEY[tabs.value]
    lance_uri = _LANCE_ROOT_PREFIX.format(key=key, lang="en")
    try:
        con = duckdb.connect("md:oideachais")
        df = con.sql(
            f"""
            SELECT chunk_id, text,
                   list_aggregate(umap_1, 'avg') AS umap_1,
                   list_aggregate(umap_2, 'avg') AS umap_2
            FROM lance_scan('{lance_uri}/*.lance')
            GROUP BY chunk_id, text
            LIMIT 200
            """
        ).df()
        source = "lance_scan"
    except Exception:
        import polars as pl
        df = pl.DataFrame({
            "chunk_id": [f"chk-{i:03d}" for i in range(5)],
            "text": ["Key concept A", "Concept B", "Concept C", "Concept D", "Concept E"],
            "umap_1": [0.1, 0.4, 0.6, 0.8, 0.3],
            "umap_2": [0.2, 0.5, 0.7, 0.4, 0.8],
        }).to_pandas()
        source = "fallback-sample"
    return con, df, key, lance_uri, source


@app.cell
def _(df, source, tabs):
    # The BGE-M3 embedding 2D scatter plot (UMAP projection) for the
    # selected tab's content. Reads from
    # `lance_scan('s3://garage/lance/oideachais.lc.root.<key>_en/*.lance')`.
    import altair as alt
    chart = (
        alt.Chart(df)
        .mark_circle(size=80)
        .encode(
            x=alt.X("umap_1:Q", title="UMAP-1"),
            y=alt.Y("umap_2:Q", title="UMAP-2"),
            tooltip=["chunk_id", "text"],
        )
        .properties(
            width=500,
            height=400,
            title=(
                f"BGE-M3 UMAP projection — {tabs.value} ({source})"
            ),
        )
        .interactive()
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
