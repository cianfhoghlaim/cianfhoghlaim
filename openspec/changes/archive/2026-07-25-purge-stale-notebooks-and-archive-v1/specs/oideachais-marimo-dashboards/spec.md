## REMOVED Requirements

### Requirement: notebooks/leaving_cert/03_leaving_cert/ stale subtree
**Reason:** Superseded by Change 4's `notebooks/40_leaving_cert_subject_panel.py` grouped marimo panel. The 23 files (analysis notebooks + PDF processing stubs + 2026-07-13 BIEP v1 stubs) are all redundant once the 7-tab grouped panel lands.
**Migration:** 23 stale files (~3,749 LOC) deleted in this change. Git history preserved.

### Requirement: notebooks/legacy/ stale corpora + _archive_* prefixed renamings
**Reason:** Folded into the canonical top-level notebooks (`12_corpus_overview_*.py` for the marimo_dashboards corpus, `40_leaving_cert_subject_panel.py` for the LC teacher view, `09_leabharlann_corpus.py` for the leabharlann corpus). The 26 files in `legacy/corpora/{medicine,law,culture,medical,other,politics,technology,author_archive}/` + `legacy/leaving_cert_teacher_view/` + 31 `_archive_*` prefixed renamings (subject_study_tools / vision_models / baml_cocoindex_tutorial / educational_stages / sources) are all subsumed.
**Migration:** 57 stale files (~7,500 LOC) deleted in this change. Reduced to `notebooks/legacy/README.md` redirect. Git history preserved.

### Requirement: 6 per-subject leaving_cert/<subject>.py notebooks + 1 en_vs_ga_comparison
**Reason:** Superseded by `notebooks/40_leaving_cert_subject_panel.py` (the 7-tab grouped marimo panel from Change 4). The 6 per-subject files were 90% identical scaffolding.
**Migration:** 7 files (~2,657 LOC) moved to `notebooks/leaving_cert/_archive/` then deleted in this change. Git history preserved.