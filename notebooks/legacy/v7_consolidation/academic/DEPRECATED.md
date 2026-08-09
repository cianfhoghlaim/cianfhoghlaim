# DEPRECATED — Migrated to `notebooks/academic_history.py`

Per the **2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1**
OpenSpec change, the 8 academic history sub-notebooks + the common file
have been consolidated into the single grouped marimo dashboard
[`notebooks/academic_history.py`](../../academic_history.py).

## Migration map

| Old file | New tab |
|:--|:--|
| `17_academic_history_01_uog_maths_corpus_overview.py` | UoG Maths Corpus |
| `17_academic_history_02_module_syllabus_assessment_map.py` | Module Syllabus |
| `17_academic_history_03_statistics_methods_lab.py` | Statistics |
| `17_academic_history_04_numerical_analysis_lab.py` | Numerical Analysis |
| `17_academic_history_05_nonlinear_systems_lab.py` | Nonlinear Systems |
| `17_academic_history_06_formulas_theorems_worked_solutions.py` | Formulas & Theorems |
| `17_academic_history_07_assignments_exams_answers.py` | Assignments & Exams |
| `17_academic_history_08_academic_history_chat.py` | Academic Chat |
| `17_academic_history__common.py` | (shared helpers — now in `_shared/`) |

## How to run

```bash
marimo edit notebooks/academic_history.py
python notebooks/academic_history.py --milestone m0 --asset-check documents_ingested --output json
```

## Git history

Preserved via `git mv`.