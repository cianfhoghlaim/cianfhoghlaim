# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
#     "altair>=5.0.0",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Descriptive statistics on the leabharlann/ corpus.

Pattern A6 (DuckDB ⇄ MotherDuck swap, from `spaces/README.md` §1.1) +
pattern A8 (SQL-fenced-block in marimo, adapted to `mo.sql`).

Data source: `md:oideachais` (MotherDuck, read-only).
Computes: token length, fada-preservation rate, lexical diversity,
per-language counts.

TODO (Phase 4 of celtic-data-engineering-patterns):
- Replace the `_t = con.table("leabharlann_books")` placeholder with
  the real MotherDuck-attached table once the dbt `weekly_downloads`
  model lands in `oideachais/dbt_project/`.
- Wire the 4 altair cells to real columns (currently sketched with
  `token_count:Q` placeholders).
- Add 1 `mo.sql` cell using the SQL-fenced-block pattern adapted
  from `spaces/data-engineering/dashboard/pages/index.md:62-156`.
"""

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _setup(mo):
    import ibis
    import altair as alt
    from dotenv import load_dotenv

    load_dotenv()
    # Pattern A6: `md:oideachais?motherduck_token=$MOTHERDUCK_TOKEN` (prod) vs
    # local path (dev). The .infisical.env template hydrates MOTHERDUCK_TOKEN.
    con = ibis.duckdb.connect("md:oideachais")
    return alt, con, ibis


@app.cell
def _intro(mo):
    mo.md(
        """
        # Leabharlann descriptive statistics

        Reactive descriptive stats on the `leabharlann/` corpus. Drag the
        sample-size slider to re-run all 4 charts. The data source is
        `md:oideachais` (MotherDuck).
        """
    )
    return


@app.cell
def _slider(mo):
    sample_size = mo.ui.slider(
        start=100,
        stop=10_000,
        step=100,
        value=1_000,
        label="Sample size",
        show_value=True,
    )
    sample_size
    return (sample_size,)


@app.cell
def _data(con, sample_size):
    # TODO (Phase 4): replace with the real MotherDuck table once the
    # `oideachais/dbt_project/weekly_downloads` model lands.
    df = con.table("leabharlann_books").limit(sample_size.value).to_pandas()
    return (df,)


@app.cell
def _chart_token_length(alt, df):
    # TODO (Phase 4): bind `token_count` to the real column.
    chart_token = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("token_count:Q", bin=True, title="Token count"),
            y=alt.Y("count()", title="Rows"),
        )
        .properties(title="Token length distribution", height=200)
    )
    chart_token
    return (chart_token,)


@app.cell
def _chart_fada(alt, df):
    # TODO (Phase 4): bind `fada_preservation` to the real column.
    chart_fada = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("fada_preservation:Q", bin=True, title="Fada-preservation rate"),
            y=alt.Y("count()", title="Rows"),
            color=alt.Color("language:N", legend=None),
        )
        .properties(title="Fada-preservation rate by language", height=200)
    )
    chart_fada
    return (chart_fada,)


@app.cell
def _chart_lexdiv(alt, df):
    # TODO (Phase 4): bind `lexical_diversity` to the real column.
    chart_lexdiv = (
        alt.Chart(df)
        .mark_point(opacity=0.5)
        .encode(
            x=alt.X("token_count:Q", title="Token count"),
            y=alt.Y("lexical_diversity:Q", title="Lexical diversity (TTR)"),
            color=alt.Color("language:N"),
        )
        .properties(title="Lexical diversity vs token count", height=250)
    )
    chart_lexdiv
    return (chart_lexdiv,)


@app.cell
def _chart_language_counts(alt, df):
    chart_lang = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("count()", title="Rows"),
            y=alt.Y("language:N", sort="-x", title="Language"),
        )
        .properties(title="Per-language row counts", height=200)
    )
    chart_lang
    return (chart_lang,)


if __name__ == "__main__":
    app.run()
