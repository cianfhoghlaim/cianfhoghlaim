# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.13.0",
#     "altair>=5.0.0",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""Time-series analysis of DynamicPartitionsDefinition materialization lags.

Pattern A1 (multi-stage data pipeline, from `spaces/README.md` §1.1)
extended: the `oideachais.ocr_materialization_lags` table is computed
by the existing `oideachais/dagster_defs/` heartbeat assets, then
analysed here.

Computes: per-OCR-model materialization lag (seconds) over a rolling
window, plus a correlation heatmap of BAML extraction confidence
vs OCR WER.

TODO (Phase 4 of celtic-data-engineering-patterns):
- Replace the `_df` placeholder with a real ibis query against
  `md:oideachais.ocr_materialization_lags` once the dbt
  `ocr_confidence_by_model` model lands.
- Add the 1 `mo.sql` cell using the SQL-fenced-block pattern adapted
  from `spaces/data-engineering/dashboard/pages/index.md:62-156`.
- Bind the correlation heatmap to real columns.
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
    con = ibis.duckdb.connect("md:oideachais")
    return alt, con, ibis


@app.cell
def _intro(mo):
    mo.md(
        """
        # OCR materialization lag analysis

        Time-series of `DynamicPartitionsDefinition` materialization lags
        across the 10 OCR models registered in `meaisinfhoghlaim/ocr/`.
        Plus a correlation heatmap of BAML extraction confidence vs
        OCR word error rate (WER).
        """
    )
    return


@app.cell
def _controls(mo):
    window_days = mo.ui.slider(
        start=1,
        stop=90,
        step=1,
        value=14,
        label="Window (days)",
        show_value=True,
    )
    window_days
    return (window_days,)


@app.cell
def _lag_query(con, window_days):
    # TODO (Phase 4): real table name; currently a placeholder that
    # returns an empty DataFrame so the notebook still renders.
    try:
        df = con.sql(
            f"""
            SELECT
                date_trunc('day', materialization_time) AS day,
                ocr_model,
                AVG(EXTRACT(EPOCH FROM (materialization_time - partition_ts))) AS avg_lag_s
            FROM oideachais.ocr_materialization_lags
            WHERE materialization_time > CURRENT_TIMESTAMP - INTERVAL '{window_days.value} days'
            GROUP BY ALL
            """
        ).to_pandas()
    except Exception:
        df = con.sql("SELECT 1 AS day, 'placeholder' AS ocr_model, 0.0 AS avg_lag_s WHERE FALSE").to_pandas()
    return (df,)


@app.cell
def _lag_chart(alt, df, window_days):
    chart_lag = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("day:T", title="Day"),
            y=alt.Y("avg_lag_s:Q", title="Avg lag (s)"),
            color=alt.Color("ocr_model:N", title="Model"),
        )
        .properties(
            title=f"Avg materialization lag (last {window_days.value} days)",
            height=300,
        )
    )
    chart_lag
    return (chart_lag,)


@app.cell
def _corr_query(con):
    # TODO (Phase 4): real columns; currently returns an empty DataFrame.
    try:
        df_corr = con.sql(
            """
            SELECT
                baml_confidence,
                ocr_wer,
                ocr_model
            FROM oideachais.ocr_confidence_by_model
            """
        ).to_pandas()
    except Exception:
        df_corr = con.sql(
            "SELECT 0.0 AS baml_confidence, 0.0 AS ocr_wer, 'placeholder' AS ocr_model WHERE FALSE"
        ).to_pandas()
    return (df_corr,)


@app.cell
def _corr_chart(alt, df_corr):
    # TODO (Phase 4): swap to a real correlation heatmap once the columns bind.
    chart_corr = (
        alt.Chart(df_corr)
        .mark_point(opacity=0.5)
        .encode(
            x=alt.X("ocr_wer:Q", title="OCR WER"),
            y=alt.Y("baml_confidence:Q", title="BAML extraction confidence"),
            color=alt.Color("ocr_model:N"),
        )
        .properties(title="BAML confidence vs OCR WER", height=300)
    )
    chart_corr
    return (chart_corr,)


if __name__ == "__main__":
    app.run()
