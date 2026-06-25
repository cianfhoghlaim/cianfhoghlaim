"""
oideachais.notebooks.dashboards.site_analysis — Marimo notebook
that visualises the firecrawl + browserbase-driven site analysis
table (CMS, captcha, screenshot paths).

Phase 8 of the openspec change.
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import duckdb
    return duckdb, mo


@app.cell
def _header(mo):
    mo.md(
        r"""
        # Site Analysis (Phase 8)

        Per-source software + layout fingerprint rendered from
        `oideachais.site_analysis.site_analyses`.
        """
    )
    return ()


@app.cell
def _summary(duckdb):
    con = duckdb.connect(":memory:")
    try:
        rows = con.execute(
            """
            SELECT source_id, url, software.cms AS cms, layout.cookie_banner AS cookie,
                   pages_sampled, screenshot_path
            FROM oideachais.site_analysis.site_analyses
            ORDER BY source_id
            """
        ).fetchall()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _render(rows, mo):
    mo.md(f"**Site analysis rows:** {len(rows)}")
    return ()


if __name__ == "__main__":
    app.run()
