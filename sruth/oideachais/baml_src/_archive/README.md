# BAML Archive

This directory contains BAML files whose functions have **no
current Python consumer** in the oideachais quadrant. The files
are preserved here for future re-activation when their planned
consumers are built.

## Contents

| File | Function count | Intended consumer | Re-activation triggers |
|---|--:|---|---|
| `cognates.baml` | 5 | `meaisinfhoghlaim/agents/celtic_linguistics.py` | When Celtic cognate agent is built |
| `celtic_linguistics.baml` | 3 | `meaisinfhoghlaim/agents/celtic_linguistics.py` (or wire `IdentifyDialect` into `oideachais/dagster_defs/assets/canuint_alignment_assets.py`) | When Celtic-linguistic agent is built |
| `morphology.baml` | 4 | `meaisinfhoghlaim/agents/celtic_morphology.py` | When morphology agent is built |
| `grammar_patterns.baml` | 6 | `meaisinfhoghlaim/agents/celtic_grammar.py` | When grammar agent is built |
| `named_entities.baml` | 5 | `meaisinfhoghlaim/agents/celtic_ner.py` (or wire into `oideachais/dagster_defs/assets/duchas_assets.py`) | When NER agent is built |
| `portfolio_extraction.baml` | 6 | `croilar/dagster_assets/profile_extraction.py` (or `meaisinfhoghlaim/agents/croilar_cv_extraction.py`) | When croilar persona profiles go dynamic |

**Total:** 6 files, 29 orphan functions, ~3,000 lines of preserved BAML.

## Why an archive (not deletion)?

Each function represents substantial domain expertise (Celtic
linguistic structures, cognate sets, NER patterns, portfolio
schemas). Deleting them would lose weeks of design work. The
archive keeps them compilable by `baml-cli generate` so that
re-activation is a `git mv` + a Python import + a STATUS.md
update — not a BAML redesign.

## Re-activation procedure

For any file in this directory:

1. **Build the consumer** (e.g. `meaisinfhoghlaim/agents/celtic_linguistics.py`)
2. **Move the file back to `baml_src/`** — `git mv oideachais/baml_src/_archive/<name>.baml oideachais/baml_src/<name>.baml`
3. **Remove the ARCHIVED header** (the 17-line block at the top of the file)
4. **Add the consumer to the docstring** — change `ARCHIVED` to `# PLANNED — wired to meaisinfhoghlaim/agents/celtic_linguistics.py`
5. **Update `oideachais/STATUS.md`** to mark the function as wired
6. **Remove the entry from `oideachais/REFACTORING.md`**
7. **Add the consumer to `oideachais/dagster_defs/definitions.py`** so the agent is registered

## What is NOT in this archive

The 5 functions in `oideachas.baml` (`ExtractSyllabus`,
`ExtractExamPaper`, `ExtractMarkingScheme`, `BuildCurriculumGraph`,
`ExtractCelticLanguageContent`) are also orphans, but they remain
in the working `baml_src/` directory because:

- They are in a working BAML file (not a dedicated Celtic-linguistic
  module)
- They are tracked by the `leaving-cert-2026` openspec change
  (0/28 tasks; the change is in-flight)
- They are similar to the 4 leaving_cert_*_extraction.baml
  functions which have a clear consumer (the LC 2026 per-subject
  asset graph)

When `leaving-cert-2026` lands, those 5 will be wired or deleted
in the same change. They are NOT in this archive.

## Reference

- `openspec/changes/archive-celtic-baml-orphans/proposal.md` —
  the change that created this archive
- `oideachais/STATUS.md` § Archived BAML functions — the live
  status table
- `oideachais/REFACTORING.md` — the re-activation plan
