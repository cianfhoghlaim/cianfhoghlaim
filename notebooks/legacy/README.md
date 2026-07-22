# Legacy Notebook Archive

This directory previously held the **preserved legacy corpora** from the
pre-2026-07-25 refactor (medicine / law / culture / politics / technology /
author_archive / leaving_cert_teacher_view / etc.).

Per the
**2026-07-25-purge-stale-notebooks-and-archive-v1** openspec change,
those 26 stale corpus files were **deleted** (git history preserved).
The content has been folded into the **flat top-level** notebooks:

| Topic | Canonical top-level notebook |
|---|---|
| Corpus overview (medicine / law / culture / politics / tech / author_archive) | `12_corpus_overview_*.py` (the marimo_dashboards series, renamed) |
| LC teacher view (per-subject diagrams) | `40_leaving_cert_subject_panel.py` (7-tab grouped marimo) |
| Legacy _archive_* renamings (subject_study_tools / vision_models / etc.) | Deleted in Change 5 |

## Where the legacy content lives now

The canonical cross-jurisdiction / cross-corpus view is at
`12_corpus_overview_*.py` (one of the 99 top-level notebooks). The
Leabharlann corpus continues to live at `09_leabharlann_corpus.py`.

## Git history

All deletions are preserved in git history. To inspect the deleted
content:

```bash
git log --all --diff-filter=D --name-only --pretty=format: | grep notebooks/legacy/
git show <commit-hash>:notebooks/legacy/corpora/...
```

## Reference

- `openspec/changes/2026-07-25-purge-stale-notebooks-and-archive-v1/`
- `openspec/changes/2026-07-25-flatten-notebooks-v1/`
- `openspec/specs/oideachais-marimo-dashboards/spec.md` (the parent spec)