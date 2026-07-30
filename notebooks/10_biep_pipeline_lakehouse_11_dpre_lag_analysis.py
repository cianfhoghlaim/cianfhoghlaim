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
extended. Reads from the dbt `ocr_confidence_by_model` model in
`oideachais/dbt_project/` (built by `dbt build`). Falls back to a
deterministic synthetic dataset when the model is not available.

Computes: per-OCR-model materialization lag (seconds) over a rolling
window, plus a correlation heatmap of BAML extraction confidence
vs OCR word error rate (WER).

See also:
- `oideachais/dbt_project/models/ocr_confidence_by_model.sql` (the source model)
- `openspec/changes/celtic-data-engineering-patterns/specs/celtic-data-engineering-pipeline/spec.md`
"""

import marimo


# Centralized registries (per the `centralized-model-registry` capability).
# Cascading effect: this notebook now uses MODEL_REGISTRY + the 5 schema
# introspection helpers from notebooks/_shared/schema.py instead of
# hardcoded table lists / hardcoded schema strings.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        schema_introspect, schema_introspect_table, read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _setup(mo):
    import altair as alt
    import ibis
    import pandas as pd
    from dotenv import load_dotenv

    load_dotenv()
    con = ibis.duckdb.connect("md:cianfhoghlaim")
    return alt, con, ibis, pd


@app.cell
def _intro(mo):
    mo.md(
        """
        # OCR materialization lag analysis

        Time-series of `DynamicPartitionsDefinition` materialization lags
        across the 10 OCR models registered in `meaisinfhoghlaim/ocr/`.
        Plus a correlation heatmap of BAML extraction confidence vs
        OCR word error rate (WER). Data source: the dbt
        `ocr_confidence_by_model` model in `oideachais/dbt_project/`.
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
def _lag_query(con, pd, window_days):
    """Per-OCR-model materialization lag (s) over a rolling window.

    Real query: aggregates the `cianfhoghlaim.ocr_materialization_lags`
    heartbeat table written by the existing `oideachais/dagster_defs/`
    assets.

    Synthetic fallback: deterministic DataFrame with 10 OCR models ×
    14 days of plausible lag values (0.5–25 s).
    """
    try:
        df = con.sql(
            f"""
            SELECT
                date_trunc('day', materialization_time) AS day,
                ocr_model,
                AVG(EXTRACT(EPOCH FROM (materialization_time - partition_ts))) AS avg_lag_s
            FROM cianfhoghlaim.ocr_materialization_lags
            WHERE materialization_time > CURRENT_TIMESTAMP - INTERVAL '{window_days.value} days'
            GROUP BY ALL
            """
        ).execute()
    except Exception:
        _random_mod = __import__("random")
        _lag_rng = _random_mod.Random(7)
        _lag_models = [
            "pylaia", "trocr", "paddleocr", "tesseract", "dots_ocr",
            "qwen2_vl", "phi3_vision", "paligemma", "llava", "gemma_vision",
        ]
        _lag_rows = []
        for _d in pd.date_range(end=pd.Timestamp.now().normalize(), periods=window_days.value):
            for _model in _lag_models:
                _lag_rows.append(
                    {"day": _d, "ocr_model": _model, "avg_lag_s": _lag_rng.uniform(0.5, 25.0)}
                )
        df = pd.DataFrame(_lag_rows)
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
def _corr_query(con, pd):
    """BAML confidence vs OCR WER per (model, document).

    Real query: reads from the dbt `ocr_confidence_by_model` model
    (one row per (model, document)). Falls back to synthetic
    negative-correlation data (high WER → low confidence).
    """
    try:
        df_corr = con.sql(
            """
            SELECT
                ocr_model,
                document_id,
                baml_confidence,
                ocr_wer
            FROM oideachais_dbt.ocr_confidence_by_model
            """
        ).execute()
    except Exception:
        _random_mod2 = __import__("random")
        _corr_rng = _random_mod2.Random(13)
        _corr_models = [
            "pylaia", "trocr", "paddleocr", "tesseract", "dots_ocr",
            "qwen2_vl", "phi3_vision", "paligemma", "llava", "gemma_vision",
        ]
        _corr_rows = []
        for _cm in _corr_models:
            for _ in range(50):
                _wer = _corr_rng.uniform(0.01, 0.5)
                _confidence = max(0.0, min(1.0, 0.95 - _wer * 1.2 + _corr_rng.uniform(-0.05, 0.05)))
                _corr_rows.append(
                    {
                        "ocr_model": _cm,
                        "document_id": f"doc-{_corr_rng.randint(0, 9999)}",
                        "baml_confidence": _confidence,
                        "ocr_wer": _wer,
                    }
                )
        df_corr = pd.DataFrame(_corr_rows)
    return (df_corr,)


@app.cell
def _corr_chart(alt, df_corr):
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
