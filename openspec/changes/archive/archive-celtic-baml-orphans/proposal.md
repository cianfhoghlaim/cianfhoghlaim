# archive-celtic-baml-orphans — Mark ~25 BAML functions as deferred

## Why

The oideachais quadrant has ~25 BAML functions defined in
`sruth/oideachais/baml_src/` that are intended for the
`sruth/meaisinfhoghlaim/` (Celtic-linguistic) and `sruth/croilar/` (portfolio)
agents, but those agents do not exist yet. These functions:

- Are well-formed BAML (no `client "litellm"` errors after the
  C2.1 fixes)
- Have no Python consumer in the entire repo
  (verified by `grep` on every function name)
- Are documented as "orphans" in `STATUS.md:35` and the explore
  report

The 6 files with orphan functions are:
| File | Functions (count) | Intended consumer |
|---|--:|---|
| `cognates.baml` | 5 (IdentifyCognates, CompareCelticVocabulary, IdentifyFalseFriends, ExplainSoundChanges, GenerateCognateVocabulary) | meaisinfhoghlaim Celtic cognate agents |
| `celtic_linguistics.baml` | 3 (ExtractMorphology, AnalyzeSentence, IdentifyDialect) | meaisinfhoghlaim Celtic-linguistic agents |
| `morphology.baml` | 4 (ExtractVerbConjugation, ExtractNounDeclension, IdentifyMorphologicalClass, CompareAdjective) | meaisinfhoghlaim Celtic-linguistic agents |
| `grammar_patterns.baml` | 6 (ExtractGrammarPatterns, ExtractIrishCopula, AnalyzeVSOOrder, ExtractPossession, GeneratePrepositionalPronouns, DocumentMutationTriggers) | meaisinfhoghlaim Celtic-linguistic agents |
| `named_entities.baml` | 5 (ExtractCelticEntities, ExtractPersonEntities, ExtractPlaceEntities, ExtractSupernaturalEntities, ExtractFestivalEntities) | meaisinfhoghlaim Celtic-linguistic agents |
| `portfolio_extraction.baml` | 6 (ExtractProfileFromCV, ExtractProfileFromGitHubReadme, ExtractMusicProfile, ExtractGameProject, MergeProfiles, GenerateProfileSummary) | croilar portfolio surface |

**Total: 29 orphan functions across 6 files.**

Risk of leaving them in place: contributors will see the functions,
assume they're working code, and try to invoke them from agents
that don't exist (the 8th `oideachas.baml` function
`ExtractSyllabus` / `ExtractExamPaper` / `ExtractMarkingScheme` /
`BuildCurriculumGraph` / `ExtractCelticLanguageContent` orphans
are a separate concern — those are within the 6th file in
`oideachas.baml` and are planned to be either deleted or wired
to the `leaving-cert-2026` change).

## What

For each of the 6 orphan BAML files:
1. **Add a clear ARCHIVED header at the top** of the file:
   ```
   // === ARCHIVED 2026-06-24 ===
   // These functions have no current Python consumer in the
   // oideachais quadrant. They are intended for the
   // sruth/meaisinfhoghlaim/ Celtic-linguistic agents and the sruth/croilar/
   // portfolio surface, which are not yet built.
   //
   // To re-activate:
   // 1. Implement the consumer (e.g.
   //    sruth/meaisinfhoghlaim/agents/celtic_linguistics.py)
   // 2. Add a # PLANNED marker back to the function docstring
   // 3. Update STATUS.md to mark the function as wired
   //
   // Reference: openspec/changes/archive-celtic-baml-orphans
   // ==============================================================
   ```
2. **Add `@description("ARCHIVED 2026-06-24 — no current consumer")`**
   to each class in the file (so contributors can see the marker
   in `baml-cli generate` output)
3. **Move the 6 files to `baml_src/_archive/`** (git mv) so they
   are clearly separated from the working BAML files
4. **Add a `baml_src/_archive/README.md`** explaining the rationale
   and how to re-activate
5. **Update `STATUS.md` and `REFACTORING.md`** to reference the
   archive

The working BAML files (24 total) remain in `baml_src/`. The 6
archived files are still compiled by `baml-cli generate` (they
still need to be in the project) but are clearly marked.

## Impact

### Affected files
- **MOVED:** 6 BAML files from `baml_src/` to `baml_src/_archive/`
  - `cognates.baml` → `baml_src/_archive/cognates.baml`
  - `celtic_linguistics.baml` → `baml_src/_archive/celtic_linguistics.baml`
  - `morphology.baml` → `baml_src/_archive/morphology.baml`
  - `grammar_patterns.baml` → `baml_src/_archive/grammar_patterns.baml`
  - `named_entities.baml` → `baml_src/_archive/named_entities.baml`
  - `portfolio_extraction.baml` → `baml_src/_archive/portfolio_extraction.baml`
- **NEW:** `baml_src/_archive/README.md` (rationale + re-activation steps)
- **MODIFIED:** `sruth/oideachais/STATUS.md` (reference the archive)
- **MODIFIED:** `sruth/oideachais/REFACTORING.md` (add entry for the archive)

### Affected specs
- MODIFIED `oideachais-baml-schemas` — the rule that BAML functions
  without a Python consumer MUST be either wired (C3.1) or
  archived (C3.2). Orphan BAML functions in working BAML files
  are forbidden.

### Backward compatibility
- The 6 archived files still compile via `baml-cli generate`
  (the directory is still in the BAML project)
- No Python file imports the archived functions (zero callers
  verified)
- The archive is a documentation change, not a code change:
  callers would need to update their import paths if they want
  to invoke the functions, but no callers exist

## Non-Goals

- No deletion of the BAML functions. They are preserved in
  `_archive/` for future re-activation.
- No wiring of the orphan functions. The `sruth/meaisinfhoghlaim/`
  Celtic-linguistic and `sruth/croilar/` portfolio agents are out of
  scope for the oideachais quadrant.
- No change to the 5 oideachas.baml orphan functions
  (`ExtractSyllabus`, `ExtractExamPaper`, `ExtractMarkingScheme`,
  `BuildCurriculumGraph`, `ExtractCelticLanguageContent`) — those
  are in a working BAML file and will be handled by a separate
  openspec change (the leaving-cert-2026 change has 0/28 tasks
  and tracks its own follow-up).

## Risk Assessment

- **Risk: contributors re-import the archived functions in a
  working file.** Mitigation: the 6 files are now in `_archive/`,
  clearly separated; the new header comment at the top of each
  file documents the ARCHIVED status; the `_archive/README.md`
  documents the re-activation procedure.
- **Risk: baml-cli generate fails because the functions reference
  the canonical LitellmClient (after C2.1 fixes) but the
  functions are still defined.** Mitigation: this is the
  intended behaviour — the functions should still be compilable
  so that re-activation is a code-only change (no BAML
  recompilation needed).

## Validation

1. `ls sruth/oideachais/baml_src/_archive/` shows 6 .baml files
2. `ls sruth/oideachais/baml_src/_archive/README.md` shows 1 README
3. `grep -r "ARCHIVED 2026-06-24" sruth/oideachais/baml_src/_archive/` shows 6 hits (one per file)
4. `grep -r "b\.IdentifyCognates\|b\.ExtractMorphology\|b\.ExtractProfileFromCV" sruth/oideachais/` returns 0 hits (no callers)
5. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
6. `openspec validate archive-celtic-baml-orphans --strict` passes
