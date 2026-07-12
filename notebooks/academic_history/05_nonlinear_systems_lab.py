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
"""Nonlinear Systems Lab — academic-history notebook #05.

Interactive sandbox for fixed-point iteration, phase portraits, the
logistic map, and bifurcation analysis. Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

The notebook ships interactive sandboxes for:

- Fixed-point iteration (1D)
- Phase portrait of a 2D dynamical system (Lotka-Volterra)
- Logistic map (chaos / bifurcation)
- Bifurcation diagram (transcritical + period-doubling cascade)
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
        # Nonlinear Systems Lab

        The 5th of 8 notebooks in `notebooks/14_academic_history/`.

        Interactive sandbox for fixed-point iteration, phase portraits,
        the logistic map, and bifurcation diagrams.
        """
    )
    return


@app.cell
def _sandbox(mo):
    system = mo.ui.dropdown(
        options=["fixed_point_1d", "logistic_map", "lotka_volterra", "transcritical"],
        value="logistic_map",
        label="System",
    )
    n_iter = mo.ui.slider(start=10, stop=500, step=10, value=200, label="iterations")
    seed = mo.ui.slider(start=0, stop=9999, step=1, value=7, label="seed")
    mo.vstack([system, n_iter, seed])
    return n_iter, seed, system


@app.cell
def _compute(n_iter, seed, system):
    """Simulate the chosen system deterministically (no early-returns)."""
    import math
    import random
    rng = random.Random(seed)
    result: dict = {"system": system.value}

    if system.value == "fixed_point_1d":
        x = float(rng.random())
        out = []
        for _ in range(int(n_iter.value)):
            x_new = math.cos(x)
            out.append(round(x_new, 8))
            x = x_new
        result.update(
            {
                "iterations": int(n_iter.value),
                "converged_to": round(out[-1], 8) if out else None,
                "tail": out[-20:],
            }
        )
    elif system.value == "logistic_map":
        x = 0.5
        out = []
        r = 3.9
        for _ in range(int(n_iter.value)):
            x = r * x * (1 - x)
            out.append(round(x, 6))
        result.update(
            {
                "r": r,
                "iterations": int(n_iter.value),
                "tail": out[-30:],
                "lyapunov_estimate": round(
                    math.log(abs(r - 2 * r * out[-1])) if out else 0.0, 4
                ),
            }
        )
    elif system.value == "lotka_volterra":
        a, b, c, d = 1.1, 0.4, 0.4, 0.1
        x, y = 1.0, 1.0
        h = 0.01
        out = []
        for _ in range(int(n_iter.value)):
            dx = a * x - b * x * y
            dy = -c * y + d * x * y
            x = max(0.0, x + h * dx)
            y = max(0.0, y + h * dy)
            out.append((round(x, 6), round(y, 6)))
        result.update(
            {
                "a": a,
                "b": b,
                "c": c,
                "d": d,
                "h": h,
                "iterations": int(n_iter.value),
                "tail": out[-20:],
            }
        )
    elif system.value == "transcritical":
        rs = [-1 + 2 * i / 60 for i in range(61)]
        branches = []
        for r in rs:
            x_lo, x_hi = -2.0, 2.0
            for _ in range(200):
                dx_lo = r * x_lo - x_lo ** 2
                dx_hi = r * x_hi - x_hi ** 2
                x_lo += 0.02 * dx_lo
                x_hi += 0.02 * dx_hi
            branches.append((round(r, 4), round(x_lo, 4), round(x_hi, 4)))
        result["branches"] = branches[::5]
    else:
        result["error"] = f"unknown system: {system.value}"
    return (result,)


@app.cell
def _render(compute_result, mo):
    text = json.dumps(compute_result, indent=2)
    mo.md(f"### Result — `{compute_result['system']}`\n\n```json\n{text}\n```")
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
        prog="05_nonlinear_systems_lab",
        description="Nonlinear systems lab (CLI mode).",
    )
    parser.add_argument("--system", default="logistic_map")
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            {
                "system": args.system,
                "module_code": args.module_code,
                "limit": args.limit,
                "note": "open the notebook to interactively run the system",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()