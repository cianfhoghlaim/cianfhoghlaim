# BAML+CocoIndex 5-notebook tutorial track v1

## Why

The parent mega-change `2026-07-11-baml-cocoindex-modernization-v1`
(commit `409898008`) scoped out **Phase C** — the 5 BAML+CocoIndex
tutorial notebooks at `notebooks/13_baml_cocoindex_tutorial/` — and
also delegated the **creation of the `end-to-end-llm-zoomcamp-style-tutorial`
capability spec** (which was supposed to be created by the 5-tangent
change at commit `1d94711c1` but did not survive the ie → ireland
namespace migration).

This follow-up ships **both** deliverables:

1. The `end-to-end-llm-zoomcamp-style-tutorial` capability spec
   (created from scratch; 8 requirements; the 6 original requirements
   from the `1d94711c1` blob are preserved, plus 2 ADDED requirements
   for the 5-notebook tutorial track + the `01_overview_setup.py`
   Step 0.5 pointer)
2. The 5 marimo tutorial notebooks at
   `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
   (the directory was reserved by commit `409898008`; this change
   fills it in)

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` | NEW (created from scratch; 8 requirements) | +~150 |
| `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` | NEW (proposal.md + tasks.md + 2 spec deltas) | +~250 |
| `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` | NEW (1 MODIFIED delta to add 2 ADDED requirements) | +~80 |
| `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/specs/oideachais-marimo-dashboards/spec.md` | NEW (1 ADDED requirement for the 5 tutorial notebooks) | +~40 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax.py` | NEW (BAML post-v4 syntax walkthrough) | +~600 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/02_qpack_8_subject_walkthrough.py` | NEW (8 qpack files walkthrough) | +~500 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline.py` | NEW (vision+PDF pipeline + side-by-side gemma-4 vs qwen3-vl) | +~500 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/04_cocoindex_baml_integration.py` | NEW (3 real CocoIndex+BAML patterns) | +~400 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/05_post_v4_duplicate_audit_and_migration.py` | NEW (42-renames audit notebook) | +~500 |
| `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/README.md` | MODIFY (replace the placeholder with the canonical 5-notebook README) | ~+60 |
| `cianfhoghlaim/notebooks/01_overview_setup.py` | NEW (welcome + Step 0.5 pointer + Steps 1-4 + nb_utils tour) | +~250 |
| `cianfhoghlaim/notebooks/cli.py` | MODIFY (add `13_baml_cocoindex_tutorial` to the GROUPS tuple so `cianfhoghlaim-marimo list` discovers the 5 entries) | ~+5 |

## The 5 tutorials (summary)

| # | File | Effort | What it teaches |
|:--|:--|--:|:--|
| 1 | `01_baml_post_v4_syntax.py` | 4h | Canonical post-v4 BAML 0.223.0 syntax (`generator` + `field Type` + `@@stream.*` + `image` + `?` optionality) |
| 2 | `02_qpack_8_subject_walkthrough.py` | 6h | The 8 `qpack_<subject>.baml` files (the `paragraph → LO[] → FormativeItem → Score → Validate` pattern; 40+ BAML calls) |
| 3 | `03_education_pdf_vision_pipeline.py` | 10h | The vision+PDF pipeline (`ExtractCurriculumSyllabus` → `ExtractExamPaperLayout` → `ExtractSyllabusDiagram` → `ExtractMarkingSchemeGuideline`) with **side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b`** |
| 4 | `04_cocoindex_baml_integration.py` | 8h | The 3 real CocoIndex+BAML integration patterns (`upstream_api_surface` / `upstream_blog_monitor` / `docs_skills_consolidation`) |
| 5 | `05_post_v4_duplicate_audit_and_migration.py` | 6h | Interactive audit of the duplicates from the 42-renames commit (`49e0259a0`) |
| **TOTAL** | | **34h** | |

## How

### Approach

Single coordinated commit per the AGENTS.md "Commit + push" template,
targeting `origin/pick-4-biep-v1` (NOT main). Each step is auditable
via a single `ls` / `openspec validate` / `python -c "import ast; ..."`
check.

1. Create the `end-to-end-llm-zoomcamp-style-tutorial` capability spec
   at `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
   (the original 6 requirements from commit `1d94711c1` blob
   `280c0aabe` + 2 ADDED requirements for the 5-notebook tutorial
   track).
2. Create the 5 marimo tutorial notebooks at
   `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
   (each 400-600 lines; dual-mode marimo + `uv run`; PEP 723 inline
   dependency blocks; substantive content per the snippet in the
   parent change proposal).
3. Add the Step 0.5 pointer in
   `cianfhoghlaim/notebooks/01_overview_setup.py` (a new welcome +
   architecture diagram + Step 0.5 BAML+CocoIndex tutorial pointer
   + Steps 1-4 + nb_utils tour).
4. Update the `README.md` placeholder in
   `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` to the
   canonical 5-notebook README.
5. Add `13_baml_cocoindex_tutorial` to the `GROUPS` tuple in
   `cianfhoghlaim/notebooks/cli.py` so `cianfhoghlaim-marimo list`
   discovers the 5 entries.
6. Verify each tutorial AST-parses under Python 3.13
   (`python -c "import ast; ast.parse(open(f).read())"`) and the
   CLI discovery returns 5 entries.
7. Write the 2 openspec spec deltas (1 MODIFIED on
   `end-to-end-llm-zoomcamp-style-tutorial` adding 2 ADDED
   requirements; 1 ADDED on `oideachais-marimo-dashboards`).
8. `openspec validate 2026-07-12-baml-cocoindex-tutorials-v1 --strict`
   must pass before commit.
9. Single commit + push to `origin/pick-4-biep-v1`.

### Why single-commit

The 5 tutorials + the spec + the Step 0.5 pointer + the CLI update
form a single logical unit: the 5 tutorials only make sense in the
context of the spec, the Step 0.5 pointer only makes sense if the
tutorials exist, and the CLI update is the gateway to the 5 tutorials.
A single commit is the smallest rebase-safe unit.

## Dependencies

`Blocked by: 2026-07-11-baml-cocoindex-modernization-v1` (commit
`409898008`; the parent mega-change must land first so the 5
tutorials have a stable BAML + CocoIndex + clients.baml base to
document).

`Blocked by (soft): 2026-07-12-baml-rename-42-duplicates-v1` (commit
`49e0259a0`; the 42-renames commit is the primary reference for
Tutorial 5's audit).

`Blocked by (soft): 2026-07-12-baml-stream-attributes-v1` (commit
`5e6734b57`; the `@stream.*` follow-up is the primary reference for
Tutorial 1 §5).

`Blocked by (soft): 2026-07-12-baml-type-builder-ncca-v1` (commit
`93df30ebb`; the TypeBuilder / `@@dynamic` follow-up is the primary
reference for Tutorial 1 §7 + Tutorial 2 §7).

`Affected repos: cianfhoghlaim` (single-repo; no `bonneagar/` or
`leabharlann/` cross-repo sync needed).

## Out of scope (acknowledged)

- The 7 `baml/education/lc_extraction/*.baml` files (owned by the
  BIEP v1 openspec change; the 4 vision extraction functions referenced
  by Tutorial 3 live here but are documented, not modified)
- The 50+ archived openspec changes under `openspec/changes/archive/*`
  — preserved unchanged
- The 50+ residual `baml-cli` validation errors in the `_shared/` /
  `pdfs/` / `celtic/` clusters — owned by separate openspec changes
- The leabharlann/ worktree — not touched (NCCA corpus data lives
  there, not in the baml/ tree)
- The baml-py / baml_client version skew — out of scope (the 5
  tutorials document the BAML syntax + the CocoIndex+BAML patterns;
  they do not unit-test the generated client)
- The Irish-language (Gaeilge) counterpart of the 5-tutorial track —
  planned as a separate follow-up change
  (`2026-07-12-baml-cocoindex-tutorials-v1-ga/`); not in scope

## Acceptance gates

- [x] `openspec validate 2026-07-12-baml-cocoindex-tutorials-v1
      --strict` passes
- [x] `end-to-end-llm-zoomcamp-style-tutorial` spec exists with 8
      requirements (6 original + 2 ADDED for the 5-notebook tutorial
      track)
- [x] `oideachais-marimo-dashboards` spec delta is well-formed
      (1 ADDED requirement for the 5 tutorial notebooks)
- [x] `notebooks/13_baml_cocoindex_tutorial/` contains 5 files
      (`01..05`)
- [x] All 5 tutorials + `01_overview_setup.py` AST-parse under
      `python -c "import ast; ast.parse(open(f).read())"`
- [x] `cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
      discovers the 5 entries
- [x] Tutorial 3 has the side-by-side `gemma-4-26B-A4B` + `qwen3-vl-8b`
      comparison cell
- [x] Step 0.5 pointer in `01_overview_setup.py` exists
- [x] Pushed to `origin/pick-4-biep-v1` (NOT `main`)