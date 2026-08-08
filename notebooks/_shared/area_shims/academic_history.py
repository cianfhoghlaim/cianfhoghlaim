"""Academic history per-tab overview helpers.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this module provides the 6 per-tab overview helpers for the
`notebooks/academic_history.py` grouped dashboard, which consolidates:
- `17_academic_history_01_uog_maths_corpus_overview.py`
- `17_academic_history_02_module_syllabus_assessment_map.py`
- `17_academic_history_03_statistics_methods_lab.py`
- `17_academic_history_04_numerical_analysis_lab.py`
- `17_academic_history_05_nonlinear_systems_lab.py`
- `17_academic_history_06_formulas_theorems_worked_solutions.py`
- `17_academic_history_07_assignments_exams_answers.py`
- `17_academic_history_08_academic_history_chat.py`
"""
from __future__ import annotations


def uog_maths_overview() -> str:
    """UoG Maths corpus overview (from 17_01)."""
    return """
    ## 🎓 UoG M.Sc. AI Mathematics Corpus

    Browse the 250-document UoG Mathematics corpus covering:
    - 50 Algebra textbooks
    - 40 Calculus textbooks
    - 30 Statistics textbooks
    - 30 Linear Algebra textbooks
    - 30 Discrete Mathematics textbooks
    - 70 Misc (real analysis, complex analysis, ODE, PDE, etc.)
    """


def module_syllabus_overview() -> str:
    """Module syllabus assessment map overview (from 17_02)."""
    return """
    ## 📋 Module Syllabus Assessment Map

    The M.Sc. AI 25/26 syllabus — 12 modules across 2 semesters:
    - Semester 1: CT511, MA511, ST511, MA512, CT512, CT513
    - Semester 2: MA521, ST521, MA522, CT521, MA523, ST522

    Each module: syllabus + learning outcomes + assessment breakdown +
    reading list + ECTS weighting.
    """


def statistics_overview() -> str:
    """Statistics methods lab overview (from 17_03)."""
    return """
    ## 📊 Statistics Methods Lab

    Interactive statistics — descriptive + inferential + Bayesian +
    regression + time series + survival analysis.
    """


def numerical_overview() -> str:
    """Numerical analysis lab overview (from 17_04)."""
    return """
    ## 🔢 Numerical Analysis Lab

    Interactive numerical methods — root finding + interpolation +
    numerical integration + ODE solvers + PDE solvers + linear algebra.
    """


def nonlinear_overview() -> str:
    """Nonlinear systems lab overview (from 17_05)."""
    return """
    ## 〰️ Nonlinear Systems Lab

    Interactive nonlinear dynamics — bifurcations + chaos + limit
    cycles + stability + Lyapunov exponents + strange attractors.
    """


def formulas_overview() -> str:
    """Formulas theorems overview (from 17_06)."""
    return """
    ## 🔣 Formulas & Theorems

    Searchable index of 1,000+ formulas + theorems across all 12 M.Sc.
    AI modules. Filter by module + topic + difficulty.
    """


def assignments_overview() -> str:
    """Assignments & exams overview (from 17_07)."""
    return """
    ## 📝 Assignments & Exam Answers

    Browse the 250+ past assignments + exam papers + worked solutions
    across all 12 M.Sc. AI modules.
    """


def academic_chat_overview() -> str:
    """Academic history chat overview (from 17_08)."""
    return """
    ## 💬 Academic History Chat

    LLM-powered chat over the M.Sc. AI corpus. Ask questions about
    any topic + get citations to the relevant Leabharlann documents.
    """


ACADEMIC_HISTORY_TABS = [
    ("UoG Maths Corpus", uog_maths_overview),
    ("Module Syllabus", module_syllabus_overview),
    ("Statistics", statistics_overview),
    ("Numerical Analysis", numerical_overview),
    ("Nonlinear Systems", nonlinear_overview),
    ("Formulas & Theorems", formulas_overview),
    ("Assignments & Exams", assignments_overview),
    ("Academic Chat", academic_chat_overview),
]


__all__ = [
    "uog_maths_overview",
    "module_syllabus_overview",
    "statistics_overview",
    "numerical_overview",
    "nonlinear_overview",
    "formulas_overview",
    "assignments_overview",
    "academic_chat_overview",
    "ACADEMIC_HISTORY_TABS",
]