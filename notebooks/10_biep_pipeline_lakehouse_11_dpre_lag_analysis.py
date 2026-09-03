from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)
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


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import setup_biep_registry_header


__generated_with = "0.14.10"
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
    lag_is_synthetic = False
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
        # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change:
        # this used to fall back to fabricated data with no visible
        # signal to the reader that the chart isn't showing real
        # materialization lags -- now flagged via lag_is_synthetic,
        # surfaced in the _synthetic_warning footer cell below.
        lag_is_synthetic = True
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
    return df, lag_is_synthetic


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
    corr_is_synthetic = False
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
        corr_is_synthetic = True
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
    return df_corr, corr_is_synthetic


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


@app.cell
def _synthetic_warning(mo, lag_is_synthetic, corr_is_synthetic):
    # Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: a
    # connection failure used to silently render fabricated data with
    # no visible signal — this makes it loud instead.
    if lag_is_synthetic or corr_is_synthetic:
        _which = []
        if lag_is_synthetic:
            _which.append("materialization-lag")
        if corr_is_synthetic:
            _which.append("BAML-confidence-vs-WER")
        mo.md(
            f"> ⚠️ **Synthetic data**: the real `cianfhoghlaim."
            f"ocr_materialization_lags` / `oideachais_dbt."
            f"ocr_confidence_by_model` table(s) were unreachable, so the "
            f"{' and '.join(_which)} chart(s) above are rendering "
            f"deterministic synthetic data, not real pipeline metrics."
        )
    return


if __name__ == "__main__":
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

def _llm_tab():
    """Return an LLM chat widget wired to the canonical litellm proxy (P3).

    Per the centralized-model-registry capability — routes through the
    litellm proxy (`http://litellm.cianfhoghlaim.ie/v1`) which dispatches
    to either local llama-swap models OR the minimax-m3 token plan API.
    """
    from notebooks._shared.marimo_patterns import llm_chat_with_prompts
    import marimo as mo

    return mo.vstack([
        mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"),
        llm_chat_with_prompts(
            system_message=(
                "You are the BIEP v3 lakehouse explorer assistant. You help "
                "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
                "When the user asks about a table or column, refer to the DLT "
                "schema introspection in information_schema.tables."
            ),
            prompts=[
                "📚 How many tables are in this schema?",
                "🔍 Show me the schema for the most recently materialised table",
                "📊 What are the top 10 most frequent values in <column_name>?",
                "🎯 How do I query for a specific subject's curriculum_pages?",
            ],
        ),
    ])


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    import subprocess
    from notebooks._shared.marimo_patterns import (
        cli_argparser_biep, cli_payload_to_output,
    )

    parser = cli_argparser_biep(__name__)
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    from notebooks._shared.marimo_patterns import cli_main_if_argv
    cli_main_if_argv(_cli_main, app)
