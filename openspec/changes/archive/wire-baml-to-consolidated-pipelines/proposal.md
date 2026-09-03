# wire-baml-to-consolidated-pipelines — Wire the new `baml/` cluster taxonomy to dlt/dagster/cocoindex/agents consumers

## Why

The `openspec/changes/baml-reorganize-by-cluster/` change (just archived) moved
60+ BAML files into a 3-cluster taxonomy (`education/`, `celtic/`,
`processing/`) with `_shared/` homes per cluster. The 5 NCCA stage duplicates
were merged into single files at `education/stages/`, the
`curriculum_extraction.baml` 1114-LOC mega-file was split into 5 files at
`education/_shared/`, and 5 dead files were deleted.

**The BAML-generated client (`baml_client/`) is the consumer interface.**
The BAML compiler emits a single namespace `b` that exposes ALL functions
from ALL source `.baml` files, regardless of which file or cluster they
came from. Consumer code does:

```python
from cianfhoghlaim.baml_client import b   # canonical (new)
# or:
from baml_client import b                  # legacy (works)
```

and then calls any of the 250+ functions like `b.ExtractAistearFramework(text, language)`
or `b.GenerateMathQuestPack(syllabus, papers, schemes, "hl")`.

**Because the BAML client is a flat namespace, the move of BAML files into
clusters does NOT require any consumer code rewrites.** The consumer imports
remain valid. The function calls (`b.ExtractAistearFramework`, etc.) remain valid.
The only thing that changes is where the BAML source files live — and the
BAML compiler re-generates the client with the same function surface.

However, several consumer files DO need attention:

1. **Outdated string references in docstrings + comments** — many
   consumer files reference `baml_src/curriculum_extraction.baml` or
   similar paths in their module docstrings. These references are now stale.
2. **Direct BAML module imports** — a few consumer files do
   `from cianfhoghlaim.baml_src.early_childhood import ...` or similar
   (the `baml_src` namespace, NOT the `baml_client` namespace). These
   references the BAML module structure pre-baml-py 0.74 and are stale.
3. **The BAML compiler config** — there is no `baml_src/baml_src.toml` or
   `baml/baml.toml` config file. The pre-existing `baml_client/` was
   hand-edited or generated from a long-since-deleted config. A new
   `baml_src/baml_src.toml` (or `baml/baml.toml`) config must be created
   so that future regenerations pick up the new cluster taxonomy.

This change:

1. **Sweeps the 13+ consumer files** that reference stale `baml_src/`
   paths in docstrings/comments, fixing them to point at the new
   `baml/education/`, `baml/celtic/`, `baml/processing/` paths.
2. **Sweeps the consumer files** that do direct
   `from cianfhoghlaim.baml_src.X import Y` imports, fixing them to
   use the canonical `from cianfhoghlaim.baml_client import b` form
   (which is the actual runtime interface).
3. **Creates the BAML project config** at `baml_src/baml_src.toml`
   (with `baml_src/` as a symlink to `baml/`) so the BAML compiler can
   discover the new cluster taxonomy.
4. **Documents the pre-existing baml_client gap** — the generated
   client at `baml/shared/baml_client/` was a stub (152 LOC) that did
   NOT include the 250+ BAML functions. Re-generating it now fails
   because 1480+ pre-existing BAML syntax errors block the build
   (the original `.baml` files used Python-style colon syntax
   `name: string` instead of BAML syntax `name string`). This is
   tracked as a follow-up issue (`fix-pre-existing-baml-syntax-errors`)
   that is OUT OF SCOPE for this change.

## What

### Phase 1 — Create the BAML project config + symlink

- [ ] 1.1 Create `baml/baml.toml` with the 2-generator config (lang_py →
      `baml/shared/baml_client/`, lang_ts → `baml/shared/baml_client_ts/`)
- [ ] 1.2 Create `baml_src/` symlink → `baml/` so the BAML CLI (which
      hardcodes `baml_src/` as the source directory) can discover the
      new cluster taxonomy without renaming any files
- [ ] 1.3 `baml_src/baml_src.toml` is auto-discovered from the symlink;
      verify the BAML compiler picks up the 60+ `.baml` files at the
      new paths (NOTE: actual regen is BLOCKED by pre-existing syntax
      errors — see Phase 4 below)

### Phase 2 — Sweep consumer docstrings + comments for stale `baml_src/` references

The 13+ consumer files contain references like `baml_src/curriculum_extraction.baml`,
`baml_src/early_childhood.baml`, `sruth/oideachais/baml_src/aistear.baml`, etc.
These references are now stale. Replace with the canonical new paths:

| Old reference | New reference |
|:--|:--|
| `baml_src/curriculum_extraction.baml` | `baml/education/_shared/curriculum_relationships.baml` (or whichever _shared/ file holds the relevant function) |
| `baml_src/early_childhood.baml` | `baml/education/stages/aistear.baml` (the merged file) |
| `baml_src/aistear.baml` | `baml/education/stages/aistear.baml` |
| `baml_src/primary.baml` | `baml/education/stages/primary.baml` |
| `baml_src/junior_cycle.baml` | `baml/education/stages/junior_cycle.baml` |
| `baml_src/tertiary.baml` | `baml/education/stages/tertiary.baml` |
| `baml_src/senior_cycle.baml` | `baml/education/stages/senior_cycle.baml` |
| `baml_src/email.baml` | `baml/processing/email.baml` |
| `baml_src/official_media.baml` | `baml/processing/official_media.baml` |
| `baml_src/upstream_monitoring.baml` | `baml/processing/upstream_monitoring.baml` |
| `baml_src/circular_extraction.baml` | `baml/processing/circular_extraction.baml` |
| `baml_src/identity_verification.baml` | `baml/processing/identity_verification.baml` |
| `baml_src/author_archive.baml` | `baml/processing/author_archive.baml` |
| `baml_src/cv_extraction.baml` | `baml/processing/cv_extraction.baml` |
| `baml_src/portfolio_extraction.baml` | `baml/processing/portfolio_extraction.baml` |
| `baml_src/researchgate_extraction.baml` | `baml/processing/researchgate_extraction.baml` |
| `baml_src/linkedin_profile_extraction.baml` | `baml/processing/linkedin_profile_extraction.baml` |
| `baml_src/audio_extraction.baml` | `baml/processing/audio_extraction.baml` |
| `baml_src/ocr_extraction.baml` | `baml/processing/ocr_extraction.baml` |
| `baml_src/ocr_validation.baml` | `baml/processing/ocr_validation.baml` |
| `baml_src/image_generation.baml` | `baml/processing/image_generation.baml` |
| `baml_src/style_transfer.baml` | `baml/processing/style_transfer.baml` |
| `baml_src/game_content.baml` | `baml/processing/game_content.baml` |
| `baml_src/player_assessment.baml` | `baml/processing/player_assessment.baml` |
| `baml_src/generators.baml` | `baml/processing/generators.baml` |
| `baml_src/culture_extraction.baml` | `baml/processing/culture_extraction.baml` |
| `baml_src/named_entities.baml` | `baml/processing/named_entities.baml` |
| `baml_src/site_analysis.baml` | `baml/processing/site_analysis.baml` |
| `baml_src/ui_components.baml` | `baml/processing/ui_components.baml` |
| `baml_src/teaching_extraction.baml` | `baml/processing/teaching_extraction.baml` |
| `baml_src/celtic_sources.baml` | `baml/celtic/sources.baml` |
| `baml_src/celtic_curriculum.baml` | `baml/celtic/curriculum/celtic_curriculum.baml` |
| `baml_src/celtic_linguistics.baml` | `baml/celtic/_archive/celtic_linguistics.baml` |
| `baml_src/cognates.baml` | `baml/celtic/_archive/cognates.baml` |
| `baml_src/mythology_extraction.baml` | `baml/celtic/curriculum/mythology_extraction.baml` |
| `baml_src/morphology.baml` | `baml/celtic/morphology.baml` |
| `baml_src/grammar_patterns.baml` | `baml/celtic/grammar_patterns.baml` |
| `baml_src/isles_education.baml` | `baml/education/cross_nation/isles_education.baml` |
| `baml_src/multi_nation_curriculum.baml` | `baml/education/cross_nation/multi_nation_curriculum.baml` |
| `baml_src/education_statistics.baml` | `baml/education/statistics/education_statistics.baml` |
| `baml_src/university_extraction.baml` | `baml/education/university/university_extraction.baml` |
| `baml_src/leaving_cert_syllabus_extraction.baml` | `baml/education/pdfs/leaving_cert_syllabus.baml` |
| `baml_src/leaving_cert_past_paper_extraction.baml` | `baml/education/pdfs/leaving_cert_past_paper.baml` |
| `baml_src/leaving_cert_marking_scheme_extraction.baml` | `baml/education/pdfs/leaving_cert_marking_scheme.baml` |
| `baml_src/qpack_*.baml` | `baml/education/subjects/qpack_*.baml` |
| `baml_src/educational_clients.baml` | (deleted — clients moved to `baml/clients.baml`) |

### Phase 3 — Sweep consumer direct imports

Consumer files that do `from cianfhoghlaim.baml_src.X import Y` (the
old `baml_src` Python module, NOT the `baml_client` runtime namespace)
need updating. These are pre-baml-py 0.74 patterns that reference the
BAML module structure as a Python module. The canonical pattern is:

```python
from cianfhoghlaim.baml_client import b
result = b.ExtractAistearFramework(text=text, language=language)
```

Not:

```python
from cianfhoghlaim.baml_src.early_childhood import ExtractAistearFramework
result = ExtractAistearFramework(pdf_text=pdf_text)
```

**Consumer files with `from cianfhoghlaim.baml_src.X import Y` to sweep**:
- `dlt/leabharlann/university_of_galway.py` — uses `b.ExtractUoGArtifact(...)` (already correct; just sweep docstring references)
- `dlt/leabharlann/gemini_deep_research.py` — uses `b.ExtractGeminiReport(...)` (already correct; just sweep docstring references)
- `agents/baml_integration.py` — uses `b.ExtractCurriculumSpecification` + `b.ExtractMarkingScheme` (already correct; sweep docstring)
- `agents/adk/email_triage_agent.py` — uses `baml.ClassifyEmail(...)` (correct; sweep docstring)
- All `dlt/subjects/*/sources.py` — use `b.ExtractLeavingCertSyllabus` + `b.ExtractLeavingCertPastPaper` + `b.ExtractLeavingCertMarkingScheme` (correct; sweep docstring)
- All `dlt/british_isles/ie/education/*` files — use `b.ExtractAistearFramework` / `b.ExtractPrimaryFramework` / `b.ExtractJCSpec` (correct; sweep docstring)
- All `dagster/assets/*` files using BAML — sweep docstrings
- All `notebooks/leaving_cert/*.py` files — sweep docstrings
- All `cocoindex/*.py` files using BAML — sweep docstrings

### Phase 4 — Document the pre-existing baml_client gap

The generated client at `baml/shared/baml_client/` was a stub that did
NOT include the 250+ BAML functions. This is a **PRE-EXISTING** issue,
NOT caused by this change or the `baml-reorganize-by-cluster` change.

**Root cause**: the original `.baml` files used Python-style colon syntax
(`name: string` instead of `name string`). The BAML compiler rejects
this and the regen fails with 1480+ validation errors.

**Workaround in place**: most consumer code uses
`try/except ImportError` graceful degradation, so they no-op when the
BAML client is not generated. This is the pattern documented in
`fix-broken-imports-and-baml/proposal.md`.

**Follow-up issue** (out of scope for this change):
`fix-pre-existing-baml-syntax-errors` — rewrites the ~51 BAML files
that use colon syntax to use BAML syntax (drop the colon, add space).
This unblocks BAML regeneration and restores the runtime BAML client.

This change adds a STATUS note to `openspec/specs/oideachais-baml-schemas/spec.md`
documenting the pre-existing gap so future readers understand the
state of the system.

## Impact

| Metric | Before | After |
|--|--|--|
| Stale `baml_src/X.baml` references in docstrings | ~50+ (across 13+ consumer files) | 0 |
| Direct `from cianfhoghlaim.baml_src.X import Y` imports | 0 (none exist in current code — verified) | 0 |
| `baml/baml.toml` project config | None | Created |
| `baml_src/` symlink → `baml/` | None | Created |
| `openspec/specs/oideachais-baml-schemas/spec.md` STATUS notes | None | Added (pre-existing baml_client gap) |

### Affected files
- **NEW:** `cianfhoghlaim/baml/baml.toml` (the BAML project config)
- **NEW:** `cianfhoghlaim/baml_src` (a symlink to `baml/`)
- **MODIFIED:** ~13+ consumer files in `dlt/`, `dagster/`, `agents/`,
  `notebooks/`, `cocoindex/` with stale `baml_src/X.baml` reference
  updates in docstrings + comments
- **MODIFIED:** `openspec/specs/oideachais-baml-schemas/spec.md`
  (added STATUS note about pre-existing baml_client gap)

### Backward compatibility
- All consumer code continues to work: the `baml_client` namespace is
  unchanged (when regenerated, all functions are preserved)
- The `try/except ImportError` pattern in consumers remains valid
- No Python imports change (only docstring updates)

### Non-Goals
- No actual BAML regeneration (blocked by pre-existing syntax errors —
  see follow-up issue `fix-pre-existing-baml-syntax-errors`)
- No consumer logic changes (only docstring/comment updates)
- No new BAML functions
- No DAG pipeline changes (that is the parallel
  `consolidate-cianfhoghlaim-subdirs` change)

### Risk Assessment

| Risk | Mitigation |
|:--|:--|
| Docstring updates break CI tools that grep for specific paths | Run `ccc search "baml_src/"` before/after to verify the count decreases |
| The `baml_src/` symlink confuses git | Add the symlink to `.gitignore` so it's not tracked (it's only used at regen time, not at runtime) |
| The BAML regeneration test fails again (pre-existing issue) | Out of scope — documented as a follow-up |

## Validation

1. `ccc search "baml_src/"` — returns hits only in:
   - `openspec/changes/wire-baml-to-consolidated-pipelines/` (the change itself)
   - `openspec/specs/oideachais-baml-schemas/spec.md` (the STATUS note)
   - NOT in any `.py` file
2. `ls cianfhoghlaim/baml/baml.toml` exists
3. `ls -la cianfhoghlaim/baml_src` shows the symlink → `baml/`
4. `git check-ignore cianfhoghlaim/baml_src` returns 0 (the symlink is gitignored)
5. `openspec validate wire-baml-to-consolidated-pipelines --strict` passes