# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "numpy>=1.24",
#     "scipy>=1.10",
#     "pydantic>=2.13.4",
#     "pyyaml",
# ]
# ///
"""Statistics Methods Lab — academic-history notebook #03.

Interactive ST311/ST312-style statistical analysis over the user's
extracted artefacts. Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

The notebook ships an interactive sandbox for:

- Sample mean / variance / t-test
- Linear regression (OLS) with diagnostics
- Confidence intervals (z + t)
- Chi-squared goodness-of-fit
- Bootstrap resampling

Per academic-history manifest restrictions: the lab runs entirely
on the user's local environment. No external API calls.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import marimo

__generated_with_marimo__ = "0.23.13"

app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import (
        acad_engine_label,
        acad_health_md,
        load_manifest_or_default,
        pseudo_id,
    )
    return acad_engine_label, acad_health_md, load_manifest_or_default, mo, pseudo_id


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Statistics Methods Lab

        The 3rd of 8 notebooks in `notebooks/14_academic_history/`.

        Interactive ST311/ST312-style statistical sandbox. Choose a
        procedure on the left, tweak the parameters, and inspect the
        results. All computation runs locally — no external API calls.
        """
    )
    return


@app.cell
def _sandbox(mo):
    import math
    try:
        import numpy as np
    except ImportError:  # pragma: no cover
        np = None

    procedure = mo.ui.dropdown(
        options=["t_test", "linear_regression", "bootstrap_ci", "chi2_gof"],
        value="t_test",
        label="Procedure",
    )
    sample_size = mo.ui.slider(
        start=5, stop=200, step=5, value=25, label="Sample size"
    )
    seed = mo.ui.slider(start=0, stop=9999, step=1, value=42, label="Random seed")
    alpha = mo.ui.slider(start=0.001, stop=0.20, step=0.001, value=0.05, label="alpha")

    mo.vstack([procedure, sample_size, seed, alpha])
    return alpha, np, procedure, sample_size, seed


@app.cell
def _compute(alpha, np, procedure, sample_size, seed):
    """Run the chosen procedure deterministically."""
    if np is None:
        result = {
            "error": "numpy not installed; install `marimo run` to get deps"
        }
    else:
        rng = np.random.default_rng(seed)
        x = rng.normal(loc=50.0, scale=10.0, size=sample_size)
        if procedure.value == "t_test":
            xbar = float(np.mean(x))
            sd = float(np.std(x, ddof=1))
            t = (xbar - 50.0) / (sd / np.sqrt(sample_size))
            result = {
                "xbar": round(xbar, 4),
                "sd": round(sd, 4),
                "t_stat": round(t, 4),
                "df": sample_size - 1,
                "alpha": float(alpha.value),
                "reject_H0": abs(t) > 1.96,  # conservative z-bound for preview
            }
        elif procedure.value == "linear_regression":
            y = 2.0 * x + rng.normal(scale=5.0, size=sample_size)
            beta_1, beta_0 = np.polyfit(x, y, 1)
            r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
            result = {
                "beta_0": round(float(beta_0), 4),
                "beta_1": round(float(beta_1), 4),
                "r_squared": round(r2, 4),
                "n": sample_size,
            }
        elif procedure.value == "bootstrap_ci":
            xbar = float(np.mean(x))
            boots = [
                float(np.mean(rng.choice(x, size=sample_size, replace=True)))
                for _ in range(1000)
            ]
            lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
            result = {
                "xbar": round(xbar, 4),
                "ci_lo": round(lo, 4),
                "ci_hi": round(hi, 4),
                "alpha": float(alpha.value),
                "bootstraps": 1000,
            }
        elif procedure.value == "chi2_gof":
            # Equal-bins chi-squared against N(50, 10).
            counts, edges = np.histogram(x, bins=10)
            expected = np.full_like(counts, fill_value=sample_size / 10, dtype=float)
            chi2 = float(np.sum((counts - expected) ** 2 / expected))
            result = {
                "chi2": round(chi2, 4),
                "df": 9,
                "n": sample_size,
            }
        else:
            result = {"error": f"unknown procedure: {procedure.value}"}
    return (result,)


@app.cell
def _render(compute_result, mo, np, procedure, pseudo_id):
    from _common import acad_engine_label, acad_health_md
    import json as _json
    result = compute_result
    text = _json.dumps(result, indent=2)
    mo.md(f"### Result — `{procedure.value}`\n\n```json\n{text}\n```")
    health_md = mo.md(
        acad_health_md(acad_engine_label(), "live (local sandbox)", 1)
    )
    mo.vstack([mo.md(text), health_md])
    return


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📊 This notebook backs the
        `oideachais-academic-history-pipeline` spec R3.
        See `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.
        """
    )
    return


def _cli_main(argv=None):
    parser = argparse.ArgumentParser(
        prog="03_statistics_methods_lab",
        description="Statistics methods lab (CLI mode).",
    )
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--procedure", default="t_test")
    parser.add_argument("--limit", type=int, default=25)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            {
                "procedure": args.procedure,
                "module_code": args.module_code,
                "limit": args.limit,
                "note": "open the notebook to interactively run the procedure",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()