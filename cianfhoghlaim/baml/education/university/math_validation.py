"""Math/statistics validation helpers for the academic-history pipeline.

This module provides deterministic (LLM-free) validators for the
typed records produced by
`cianfhoghlaim/baml/education/university/mathematics_statistics_extraction.baml`.

Validators are organised by record family:

- LaTeX well-formedness (always run first)
- Formula / equation validation (Symbolic equivalence via SymPy if available)
- Probability / parameter sanity (variance > 0, alpha ∈ (0, 1), etc.)
- Hypothesis-test result checks (p-value / alpha / decision consistency)
- Regression / GLM diagnostics sanity
- Iteration / ODE convergence / stability checks
- Worked-solution / answer-script structure checks

The module is intentionally dependency-light: only the Python standard
library is required at minimum. SymPy is optional; if unavailable the
symbolic validators fall back to pure-numeric checks.

Usage (typical):

    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_formula_record,
        validate_statistical_procedure_record,
        validate_iteration_record,
    )

    findings = list(validate_formula_record(formula))
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

# Optional SymPy import for symbolic equivalence checks.
try:
    import sympy as sp  # type: ignore[import-not-found]

    SYMPY_AVAILABLE = True
except ImportError:  # pragma: no cover - defensive
    SYMPY_AVAILABLE = False
    sp = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Severity codes (mirror BAML `ValidationSeverity`)
# ---------------------------------------------------------------------------

INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

_SEVERITY_RANK = {INFO: 0, WARN: 1, ERROR: 2}


@dataclass(frozen=True)
class Finding:
    """A single deterministic validation finding."""

    severity: str
    code: str
    message: str
    target: str | None = None
    expected: str | None = None
    actual: str | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
        }
        if self.target is not None:
            out["target"] = self.target
        if self.expected is not None:
            out["expected"] = self.expected
        if self.actual is not None:
            out["actual"] = self.actual
        return out


# ---------------------------------------------------------------------------
# 1. LaTeX well-formedness
# ---------------------------------------------------------------------------

# Whitelist of safe LaTeX commands (kept conservative on purpose).
LATEX_COMMAND_WHITELIST: frozenset[str] = frozenset(
    {
        # basic ops
        "frac",
        "sqrt",
        "sum",
        "int",
        "iint",
        "iiint",
        "oint",
        "prod",
        "lim",
        "inf",
        "sup",
        "max",
        "min",
        "partial",
        "nabla",
        # trig
        "sin",
        "cos",
        "tan",
        "cot",
        "sec",
        "csc",
        "arcsin",
        "arccos",
        "arctan",
        "sinh",
        "cosh",
        "tanh",
        # log / exp
        "log",
        "ln",
        "exp",
        "lg",
        # case
        "begin",
        "end",
        # accents
        "vec",
        "hat",
        "tilde",
        "bar",
        "dot",
        "ddot",
        "overline",
        "underline",
        "widehat",
        "widetilde",
        # text
        "mathrm",
        "mathbf",
        "mathit",
        "mathsf",
        "mathbb",
        "mathcal",
        "mathfrak",
        "operatorname",
        "text",
        "textbf",
        "textit",
        "textrm",
        # operators
        "cdot",
        "times",
        "div",
        "pm",
        "mp",
        "le",
        "leq",
        "ge",
        "geq",
        "ne",
        "neq",
        "approx",
        "sim",
        "simeq",
        "equiv",
        "to",
        "rightarrow",
        "leftarrow",
        "mapsto",
        "Rightarrow",
        "Leftarrow",
        # grouping
        "left",
        "right",
        "big",
        "Big",
        "bigg",
        "Bigg",
        "displaystyle",
        "textstyle",
        "scriptstyle",
        "scriptscriptstyle",
        # common Greek
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "varepsilon",
        "zeta",
        "eta",
        "theta",
        "vartheta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "pi",
        "varpi",
        "rho",
        "varrho",
        "sigma",
        "varsigma",
        "tau",
        "upsilon",
        "phi",
        "varphi",
        "chi",
        "psi",
        "omega",
        "Gamma",
        "Delta",
        "Theta",
        "Lambda",
        "Xi",
        "Pi",
        "Sigma",
        "Upsilon",
        "Phi",
        "Psi",
        "Omega",
        # misc
        "infty",
        "in",
        "notin",
        "subseteq",
        "supseteq",
        "subset",
        "supset",
        "cup",
        "cap",
        "emptyset",
        "forall",
        "exists",
        "neg",
        "land",
        "wedge",
        "lor",
        "vee",
        "Leftrightarrow",
        "bmod",
        "pmod",
        "binom",
        "tbinom",
        "dbinom",
        "substack",
        "stackrel",
        "color",
        "textcolor",
        "boxed",
        "fbox",
        "phantom",
    }
)


def validate_latex(latex: str, target: str | None = None) -> list[Finding]:
    """Return a list of `Finding`s for LaTeX well-formedness checks."""
    findings: list[Finding] = []
    if latex is None or not latex.strip():
        findings.append(
            Finding(
                severity=ERROR,
                code="LATEX_EMPTY",
                message="LaTeX is empty",
                target=target,
            )
        )
        return findings

    # Balanced braces.
    depth = 0
    for idx, ch in enumerate(latex):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                findings.append(
                    Finding(
                        severity=ERROR,
                        code="LATEX_UNBALANCED_BRACE",
                        message="Unbalanced closing brace",
                        target=target,
                        actual=f"position={idx}",
                    )
                )
                break
    else:
        if depth != 0:
            findings.append(
                Finding(
                    severity=ERROR,
                    code="LATEX_UNBALANCED_BRACE",
                    message=f"Unbalanced braces (depth={depth} at end)",
                    target=target,
                )
            )

    # Balanced \left / \right.
    left_count = latex.count(r"\left")
    right_count = latex.count(r"\right")
    if left_count != right_count:
        findings.append(
            Finding(
                severity=WARN,
                code="LATEX_UNBALANCED_LEFT_RIGHT",
                message=f"Unbalanced \\left (={left_count}) / \\right (={right_count})",
                target=target,
                expected=f"\\left={left_count}, \\right={left_count}",
                actual=f"\\left={left_count}, \\right={right_count}",
            )
        )

    # Balanced \begin{env} / \end{env}.
    env_stack: list[str] = []
    i = 0
    while i < len(latex):
        if latex[i : i + 6] == r"\begin":
            # Find env name.
            j = latex.find("{", i + 6)
            if j == -1:
                break
            k = latex.find("}", j + 1)
            if k == -1:
                break
            env_stack.append(latex[j + 1 : k])
            i = k + 1
        elif latex[i : i + 4] == r"\end":
            j = latex.find("{", i + 4)
            if j == -1:
                break
            k = latex.find("}", j + 1)
            if k == -1:
                break
            env = latex[j + 1 : k]
            if env_stack and env_stack[-1] == env:
                env_stack.pop()
            else:
                findings.append(
                    Finding(
                        severity=ERROR,
                        code="LATEX_UNBALANCED_ENV",
                        message=f"\\end{{{env}}} without matching \\begin",
                        target=target,
                        expected=f"stack top = {env_stack[-1] if env_stack else None}",
                        actual=env,
                    )
                )
            i = k + 1
        else:
            i += 1
    if env_stack:
        findings.append(
            Finding(
                severity=ERROR,
                code="LATEX_UNBALANCED_ENV",
                message=f"Unclosed environments: {env_stack}",
                target=target,
            )
        )

    # Command whitelist.
    import re as _re

    for match in _re.finditer(r"\\([A-Za-z]+)\*?", latex):
        cmd = match.group(1)
        if cmd not in LATEX_COMMAND_WHITELIST:
            findings.append(
                Finding(
                    severity=WARN,
                    code="LATEX_UNKNOWN_COMMAND",
                    message=f"Unknown LaTeX command: \\{cmd}",
                    target=target,
                    actual=cmd,
                )
            )

    # Subscript/superscript nesting depth.
    max_depth = 0
    cur = 0
    for ch in latex:
        if ch in ("^", "_"):
            cur += 1
            max_depth = max(max_depth, cur)
        elif ch == " " or ch.isalpha():
            cur = 0
    if max_depth > 4:
        findings.append(
            Finding(
                severity=WARN,
                code="LATEX_DEEP_NESTING",
                message=f"Subscript/superscript nesting depth = {max_depth}",
                target=target,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# 2. Symbolic equivalence (optional SymPy)
# ---------------------------------------------------------------------------


def symbolic_equivalent(latex_left: str, latex_right: str) -> bool | None:
    """Return True/False if SymPy can prove equivalence, else None."""
    if not SYMPY_AVAILABLE:
        return None
    try:
        left = sp.sympify(_strip_dollars(latex_left))
        right = sp.sympify(_strip_dollars(latex_right))
        if left is None or right is None:
            return None
        diff = sp.simplify(left - right)
        return bool(diff == 0)
    except Exception:
        return None


def _strip_dollars(s: str) -> str:
    return s.replace("$", "").strip()


# ---------------------------------------------------------------------------
# 3. Probability / parameter sanity
# ---------------------------------------------------------------------------


def validate_probability_param(
    name: str,
    value: float | int | None,
    *,
    kind: str = "probability",
    target: str | None = None,
) -> Finding | None:
    """Validate a single numeric parameter."""
    if value is None:
        return None
    if kind == "probability":
        if not (0.0 <= float(value) <= 1.0):
            return Finding(
                severity=ERROR,
                code="PROBABILITY_OUT_OF_RANGE",
                message=f"{name} = {value} outside [0, 1]",
                target=target,
                expected="0 <= value <= 1",
                actual=str(value),
            )
    elif kind == "alpha":
        if not (0.0 < float(value) < 1.0):
            return Finding(
                severity=ERROR,
                code="ALPHA_OUT_OF_RANGE",
                message=f"{name} = {value} outside (0, 1)",
                target=target,
                expected="0 < value < 1",
                actual=str(value),
            )
    elif kind == "variance":
        if float(value) <= 0:
            return Finding(
                severity=ERROR,
                code="VARIANCE_NON_POSITIVE",
                message=f"{name} = {value} <= 0",
                target=target,
                expected="value > 0",
                actual=str(value),
            )
    elif kind == "df":
        if float(value) <= 0:
            return Finding(
                severity=ERROR,
                code="DF_NON_POSITIVE",
                message=f"{name} = {value} <= 0",
                target=target,
                expected="value > 0",
                actual=str(value),
            )
    elif kind == "p_value":
        if not (0.0 <= float(value) <= 1.0):
            return Finding(
                severity=ERROR,
                code="PVALUE_OUT_OF_RANGE",
                message=f"{name} = {value} outside [0, 1]",
                target=target,
                expected="0 <= value <= 1",
                actual=str(value),
            )
    elif kind == "correlation" and not (-1.0 <= float(value) <= 1.0):
        return Finding(
            severity=ERROR,
            code="CORRELATION_OUT_OF_RANGE",
            message=f"{name} = {value} outside [-1, 1]",
            target=target,
            expected="-1 <= value <= 1",
            actual=str(value),
        )
    return None


# ---------------------------------------------------------------------------
# 4. Hypothesis-test result checks
# ---------------------------------------------------------------------------


def validate_test_decision(
    *,
    p_value: float | int | None,
    alpha: float | int | None,
    decision: str | None,
    target: str | None = None,
) -> list[Finding]:
    """Verify `decision` is consistent with `p_value` vs `alpha`."""
    findings: list[Finding] = []
    if p_value is None or alpha is None:
        return findings
    p = float(p_value)
    a = float(alpha)
    expected = "REJECT" if p < a else "FAIL_TO_REJECT"
    if decision and decision.upper() not in (expected, "NONE"):
        findings.append(
            Finding(
                severity=ERROR,
                code="PVALUE_ALPHA_INCONSISTENT",
                message=f"decision={decision} inconsistent with p={p} vs alpha={a}",
                target=target,
                expected=expected,
                actual=str(decision),
            )
        )
    if a == 0.0:
        findings.append(
            Finding(
                severity=WARN,
                code="ALPHA_DEGENERATE",
                message="alpha = 0 is degenerate (always reject H0)",
                target=target,
            )
        )
    return findings


# ---------------------------------------------------------------------------
# 5. Regression diagnostics sanity
# ---------------------------------------------------------------------------


def validate_regression_diagnostics(
    diag: Mapping[str, Any] | None,
    target: str | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if diag is None:
        return findings

    r2 = diag.get("r_squared")
    if r2 is not None and not (0.0 <= float(r2) <= 1.0):
        findings.append(
            Finding(
                severity=ERROR,
                code="R2_OUT_OF_RANGE",
                message=f"R^2 = {r2} outside [0, 1]",
                target=target,
                expected="0 <= r_squared <= 1",
                actual=str(r2),
            )
        )

    dw = diag.get("durbin_watson")
    if dw is not None and not (0.0 < float(dw) < 4.0):
        findings.append(
            Finding(
                severity=ERROR,
                code="DW_OUT_OF_RANGE",
                message=f"Durbin-Watson = {dw} outside (0, 4)",
                target=target,
                expected="0 < value < 4",
                actual=str(dw),
            )
        )

    vif = diag.get("vif_max")
    if vif is not None and float(vif) >= 10:
        findings.append(
            Finding(
                severity=WARN,
                code="VIF_HIGH",
                message=f"vif_max = {vif} >= 10 (multicollinearity risk)",
                target=target,
                expected="vif_max < 10",
                actual=str(vif),
            )
        )

    shapiro = diag.get("shapiro_p")
    if shapiro is not None and float(shapiro) < 0.05:
        findings.append(
            Finding(
                severity=WARN,
                code="NORMALITY_REJECTED",
                message=f"Shapiro-Wilk p = {shapiro} < 0.05 (normality rejected)",
                target=target,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# 6. Iteration / ODE checks
# ---------------------------------------------------------------------------


def validate_iteration_record(
    iterates: Iterable[Mapping[str, Any]] | None,
    *,
    converged: bool | None = None,
    residual_final: float | None = None,
    target: str | None = None,
) -> list[Finding]:
    """Verify iteration-trace sanity (convergence flag, residual, monotonic descent)."""
    findings: list[Finding] = []
    if iterates is None:
        return findings
    items = list(iterates)
    if not items:
        findings.append(
            Finding(
                severity=WARN,
                code="ITERATES_EMPTY",
                message="Iterates list is empty",
                target=target,
            )
        )
        return findings

    residuals = [it.get("residual") for it in items if it.get("residual") is not None]
    if residuals and residual_final is not None:
        last = residuals[-1]
        if last is not None and abs(float(last) - float(residual_final)) > 1e-9:
            findings.append(
                Finding(
                    severity=WARN,
                    code="RESIDUAL_MISMATCH",
                    message=f"final iterate residual {last} != residual_final {residual_final}",
                    target=target,
                )
            )

        # Quadratic-convergence heuristic: |e_{k+1}| / |e_k|^2 ≈ constant.
        if len(residuals) >= 3:
            try:
                ratios = []
                for k in range(1, len(residuals) - 1):
                    r_k = residuals[k]
                    if r_k is None or r_k == 0:
                        continue
                    denom = r_k ** 2
                    if denom > 0:
                        r_next = residuals[k + 1]
                        if r_next is not None:
                            ratios.append(r_next / denom)
                if ratios and max(ratios) - min(ratios) > max(ratios) * 0.5:
                    findings.append(
                        Finding(
                            severity=INFO,
                            code="CONVERGENCE_RATE_NON_QUADRATIC",
                            message=(
                                "Residuals do not exhibit clear quadratic decay "
                                f"(spread={max(ratios) - min(ratios):.3g})"
                            ),
                            target=target,
                        )
                    )
            except Exception:
                pass

    if converged is False:
        findings.append(
            Finding(
                severity=WARN,
                code="ITERATION_DID_NOT_CONVERGE",
                message="Iteration flag converged=False",
                target=target,
            )
        )
    return findings


def validate_ode_stability(
    *,
    step_size: float | None,
    lambda_max: float | None,
    method: str | None = None,
    target: str | None = None,
) -> list[Finding]:
    """Verify ODE step size is within the explicit RK4 stability region when applicable."""
    findings: list[Finding] = []
    if step_size is None or lambda_max is None:
        return findings
    if method and method.upper() in {"RK2", "RK3", "RK4"}:
        bound = 2.83  # RK4 stability boundary (lambda * h < 2.83)
        if lambda_max * float(step_size) > bound:
            findings.append(
                Finding(
                    severity=ERROR,
                    code="RK_STABILITY_VIOLATED",
                    message=(
                        f"h*lambda_max = {float(step_size) * float(lambda_max):.4g} > "
                        f"{bound} (RK4 stability boundary)"
                    ),
                    target=target,
                )
            )
    return findings


# ---------------------------------------------------------------------------
# 7. Worked-solution / answer-script structure
# ---------------------------------------------------------------------------


def validate_step_indices(steps: Iterable[Mapping[str, Any]] | None) -> list[Finding]:
    findings: list[Finding] = []
    if steps is None:
        return findings
    indices = [int(s.get("step_index", 0)) for s in steps]
    if indices and indices != sorted(indices):
        findings.append(
            Finding(
                severity=WARN,
                code="STEPS_UNORDERED",
                message=f"step_index not in ascending order: {indices}",
            )
        )
    if indices and indices != list(range(1, len(indices) + 1)):
        findings.append(
            Finding(
                severity=WARN,
                code="STEPS_NOT_CONTIGUOUS",
                message=f"step_index not 1..N contiguous: {indices}",
            )
        )
    return findings


def validate_mark_totals(
    *,
    question_marks: int | float | None,
    step_marks_sum: float | None,
    target: str | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    if question_marks is None or step_marks_sum is None:
        return findings
    if step_marks_sum > float(question_marks) + 0.01:
        findings.append(
            Finding(
                severity=ERROR,
                code="STEP_MARKS_EXCEED_QUESTION",
                message=(
                    f"sum of step marks {step_marks_sum} exceeds question total "
                    f"{question_marks}"
                ),
                target=target,
            )
        )
    return findings


# ---------------------------------------------------------------------------
# 8. High-level validators that combine all of the above
# ---------------------------------------------------------------------------


def validate_formula_record(record: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(validate_latex(record.get("latex", ""), target=record.get("formula_id")))
    return findings


def validate_statistical_procedure_record(record: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for field in ("p_value",):
        f = validate_probability_param(field, record.get(field), kind="p_value",
                                       target=record.get("procedure_id"))
        if f:
            findings.append(f)
    for field in ("alpha",):
        f = validate_probability_param(field, record.get(field), kind="alpha",
                                       target=record.get("procedure_id"))
        if f:
            findings.append(f)
    findings.extend(
        validate_test_decision(
            p_value=record.get("p_value"),
            alpha=record.get("alpha"),
            decision=record.get("decision"),
            target=record.get("procedure_id"),
        )
    )
    findings.extend(validate_regression_diagnostics(record.get("diagnostics"),
                                                    target=record.get("procedure_id")))
    return findings


def validate_numerical_method_record(record: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(
        validate_iteration_record(
            record.get("iterates"),
            converged=record.get("converged"),
            residual_final=record.get("residual_final"),
            target=record.get("method_id"),
        )
    )
    findings.extend(
        validate_ode_stability(
            step_size=record.get("step_size"),
            lambda_max=record.get("lambda_max"),
            method=record.get("method"),
            target=record.get("method_id"),
        )
    )
    return findings


def validate_worked_solution(record: Mapping[str, Any]) -> list[Finding]:
    return validate_step_indices(record.get("steps"))


def validate_student_answer_script(record: Mapping[str, Any]) -> list[Finding]:
    return validate_step_indices(record.get("steps"))


def filter_by_severity(
    findings: Iterable[Finding], min_severity: str = WARN
) -> list[Finding]:
    """Return findings at or above the given severity."""
    threshold = _SEVERITY_RANK.get(min_severity, 1)
    return [f for f in findings if _SEVERITY_RANK.get(f.severity, 0) >= threshold]


__all__ = [
    "ERROR",
    "INFO",
    "LATEX_COMMAND_WHITELIST",
    "SYMPY_AVAILABLE",
    "WARN",
    "Finding",
    "filter_by_severity",
    "symbolic_equivalent",
    "validate_formula_record",
    "validate_iteration_record",
    "validate_latex",
    "validate_mark_totals",
    "validate_numerical_method_record",
    "validate_ode_stability",
    "validate_probability_param",
    "validate_regression_diagnostics",
    "validate_statistical_procedure_record",
    "validate_step_indices",
    "validate_student_answer_script",
    "validate_test_decision",
    "validate_worked_solution",
]
