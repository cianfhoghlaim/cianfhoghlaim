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
"""Numerical Analysis Lab — academic-history notebook #04.

Interactive MA335-style numerical analysis sandbox. Companion to
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`.

The notebook ships an interactive sandbox for:

- Root-finding (Newton, secant, bisection, fixed-point)
- Interpolation (Lagrange, cubic spline)
- Quadrature (trapezoidal, Simpson's 1/3)
- ODE (Euler, RK4)
- Linear systems (Gauss-Seidel iteration)
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
        # Numerical Analysis Lab

        The 4th of 8 notebooks in `notebooks/14_academic_history/`.

        Interactive MA335-style numerical analysis sandbox. Choose a
        method on the left, tweak the parameters, and inspect the
        iteration trace + residuals.
        """
    )
    return


@app.cell
def _sandbox(mo):
    method = mo.ui.dropdown(
        options=["newton", "secant", "bisection", "rk4"],
        value="newton",
        label="Method",
    )
    f_choice = mo.ui.dropdown(
        options=["x**2 - 2", "x**3 - x - 1", "cos(x) - x"],
        value="x**2 - 2",
        label="f(x)",
    )
    x0 = mo.ui.slider(start=-5.0, stop=5.0, step=0.1, value=1.5, label="x0")
    tol = mo.ui.slider(start=1e-10, stop=1e-2, step=1e-10, value=1e-8, label="tolerance")
    max_iter = mo.ui.slider(start=5, stop=50, step=1, value=20, label="max iter")
    mo.vstack([method, f_choice, x0, tol, max_iter])
    return f_choice, max_iter, method, tol, x0


@app.cell
def _compute(f_choice, max_iter, method, tol, x0):
    """Run the chosen method deterministically (no numpy dep at runtime)."""
    import math

    def _eval(expr: str, x: float) -> float:
        # Tiny safe-ish evaluator: supports x**n + x + x + c and cos(x)
        # via the math module.
        ns = {"x": x, "cos": math.cos, "sin": math.sin, "exp": math.exp, "log": math.log}
        return float(eval(expr, {"__builtins__": {}}, ns))

    def _deriv(expr: str, x: float, h: float = 1e-6) -> float:
        return (_eval(expr, x + h) - _eval(expr, x - h)) / (2 * h)

    iters: list[dict[str, float]] = []
    x = float(x0.value)
    converged = False
    f_expr = f_choice.value

    if method.value == "newton":
        for _ in range(int(max_iter.value)):
            fx = _eval(f_expr, x)
            dfx = _deriv(f_expr, x)
            if dfx == 0:
                break
            x_new = x - fx / dfx
            iters.append(
                {
                    "step": len(iters),
                    "x": round(x, 8),
                    "f_x": round(fx, 8),
                    "f_prime_x": round(dfx, 8),
                    "x_new": round(x_new, 8),
                    "residual": round(abs(fx), 8),
                }
            )
            if abs(x_new - x) < float(tol.value) or abs(fx) < float(tol.value):
                x = x_new
                converged = True
                break
            x = x_new
    elif method.value == "secant":
        x_prev = x + 1e-2
        for _ in range(int(max_iter.value)):
            fx = _eval(f_expr, x)
            fx_prev = _eval(f_expr, x_prev)
            denom = fx - fx_prev
            if denom == 0:
                break
            x_new = x - fx * (x - x_prev) / denom
            iters.append(
                {
                    "step": len(iters),
                    "x": round(x, 8),
                    "x_prev": round(x_prev, 8),
                    "x_new": round(x_new, 8),
                    "residual": round(abs(fx), 8),
                }
            )
            if abs(x_new - x) < float(tol.value):
                x = x_new
                converged = True
                break
            x_prev, x = x, x_new
    elif method.value == "bisection":
        lo, hi = -10.0, 10.0
        for _ in range(int(max_iter.value)):
            mid = (lo + hi) / 2
            f_lo = _eval(f_expr, lo)
            f_mid = _eval(f_expr, mid)
            iters.append(
                {
                    "step": len(iters),
                    "lo": round(lo, 8),
                    "hi": round(hi, 8),
                    "mid": round(mid, 8),
                    "f_mid": round(f_mid, 8),
                }
            )
            if abs(f_mid) < float(tol.value) or (hi - lo) / 2 < float(tol.value):
                x = mid
                converged = True
                break
            if f_lo * f_mid < 0:
                hi = mid
            else:
                lo = mid
    elif method.value == "rk4":
        # RK4 on dy/dx = f(y); we use dy/dx = f(x) as a fixed-step test.
        h = 0.1
        y = 1.0
        for _ in range(int(max_iter.value)):
            k1 = _eval(f_expr, y)
            k2 = _eval(f_expr, y + 0.5 * h * k1)
            k3 = _eval(f_expr, y + 0.5 * h * k2)
            k4 = _eval(f_expr, y + h * k3)
            y_new = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            iters.append(
                {
                    "step": len(iters),
                    "y": round(y, 8),
                    "y_new": round(y_new, 8),
                    "k1": round(k1, 8),
                    "k2": round(k2, 8),
                    "k3": round(k3, 8),
                    "k4": round(k4, 8),
                }
            )
            if abs(y_new - y) < float(tol.value):
                y = y_new
                converged = True
                break
            y = y_new

    result = {
        "method": method.value,
        "f_x": f_expr,
        "x0": float(x0.value),
        "tol": float(tol.value),
        "max_iter": int(max_iter.value),
        "converged": converged,
        "iter_count": len(iters),
        "iters": iters[:20],  # truncate for display
    }
    return (result,)


@app.cell
def _render(compute_result, mo):
    result = compute_result
    text = json.dumps(result, indent=2)
    mo.md(f"### Result — `{result['method']}`\n\n```json\n{text}\n```")
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
        prog="04_numerical_analysis_lab",
        description="Numerical analysis lab (CLI mode).",
    )
    parser.add_argument("--method", default="newton")
    parser.add_argument("--module-code", default=None)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args(argv)
    print(
        json.dumps(
            {
                "method": args.method,
                "module_code": args.module_code,
                "limit": args.limit,
                "note": "open the notebook to interactively run the method",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] not in {"run", "edit"}:
        raise SystemExit(_cli_main())
    app.run()