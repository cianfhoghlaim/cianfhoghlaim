# Sister-Repo Lift: `ciancheiltis-celtic-baml-lift-v1`

> **One-line summary:** Lift the canonical 8-entry CelticLanguage
> enum + the 7-vernacular BAML extractors + morphology + grammar
> + Duchas source BAML from cianfhoghlaim into ciancheiltis (the
> Celtic-language corpus sister repo).

## Source files (cianfhoghlaim)

| # | Source path | Bytes | Description |
|--:|---|--:|---|
| C.1 | `baml_src/celtic/sources.baml` | ~3 KB | The 8-entry `CelticLanguage` enum (ga + cy + gd + br + kw + gv + sga + non_celtic_indo_european) — the canonical Celtic taxonomy. |
| C.2 | `baml_src/british_isles/_cross/vernacular_languages.baml` | ~12 KB | The 7-vernacular BAML extractors (CY + GD + BR + KW + GV + FR_JE + FR_GG + SCO; 8 extraction functions) — the canonical cross-vernacular extraction surface. |
| C.3 | `baml_src/celtic/morphology.baml` | ~6 KB | The morphology schemas (noun cases, verb conjugations, mutations, lenition, eclipsis). |
| C.4 | `baml_src/celtic/grammar_patterns.baml` | ~7 KB | The grammar pattern extraction (VSO word order, preposition + pronoun concultation, relative clause formation). |
| C.5 | `baml_src/celtic/gaois/duchas.baml` | ~4 KB | The Duchas (Irish folklore + place-name) source BAML — gaois.ie is the canonical source. |

## Destination files (ciancheiltis)

| # | Destination path | Bytes | Source |
|--:|---|--:|---|
| C.1.dest | `~/dev/ciancheiltis/baml_src/celtic/sources.baml` | ~3 KB | C.1 (lift as-is — canonical taxonomy) |
| C.2.dest | `~/dev/ciancheiltis/baml_src/_cross/vernacular_languages.baml` | ~12 KB | C.2 (lift as-is — canonical cross-vernacular extraction) |
| C.3.dest | `~/dev/ciancheiltis/baml_src/celtic/morphology.baml` | ~6 KB | C.3 (lift as-is — corpus-specific morphology) |
| C.4.dest | `~/dev/ciancheiltis/baml_src/celtic/grammar_patterns.baml` | ~7 KB | C.4 (lift as-is — corpus-specific grammar) |
| C.5.dest | `~/dev/ciancheiltis/baml_src/celtic/gaois/duchas.baml` | ~4 KB | C.5 (lift as-is — corpus-specific Duchas source) |

## Transformation rules

### All 5 files — No transformation

The Celtic-language corpus IS the canonical taxonomy; ciancheiltis
is the home repo for these BAML files. The cianfhoghlaim versions
were authored here and lifted to the corpus repo. The
correspondence is exact:

| File | Why no transformation |
|---|---|
| C.1 | The `CelticLanguage` enum is the canonical 8-entry taxonomy used everywhere. |
| C.2 | The 7-vernacular BAML extractors are the canonical cross-vernacular surface. |
| C.3 | Morphology schemas are corpus-specific (cianfhoghlaim has no morphology consumer; ciancheiltis is the only consumer). |
| C.4 | Grammar patterns are corpus-specific. |
| C.5 | Duchas is corpus-specific (gaois.ie is the canonical source). |

The only transformation is the **path**: the cianfhoghlaim source
paths match the ciancheiltis destination paths exactly
(`baml_src/celtic/{sources,morphology,grammar_patterns}.baml` +
`baml_src/celtic/gaois/duchas.baml` + `baml_src/_cross/vernacular_languages.baml`).

## Per-PR step-by-step checklist

### PR #1 — Lift the canonical taxonomy + cross-vernacular extractors (3 items)

- [ ] **1.1** Copy `baml_src/celtic/sources.baml` → `~/dev/ciancheiltis/baml_src/celtic/sources.baml` (no transformation)
- [ ] **1.2** Copy `baml_src/british_isles/_cross/vernacular_languages.baml` → `~/dev/ciancheiltis/baml_src/_cross/vernacular_languages.baml` (no transformation)
- [ ] **1.3** Regenerate the ciancheiltis baml_client: `cd ~/dev/ciancheiltis && uv run baml-cli generate`

### PR #2 — Lift the morphology + grammar BAML (4 items)

- [ ] **2.1** Copy `baml_src/celtic/morphology.baml` → `~/dev/ciancheiltis/baml_src/celtic/morphology.baml` (no transformation)
- [ ] **2.2** Copy `baml_src/celtic/grammar_patterns.baml` → `~/dev/ciancheiltis/baml_src/celtic/grammar_patterns.baml` (no transformation)
- [ ] **2.3** Add the morphology + grammar extraction functions to the ciancheiltis `baml_client` call site (`ciancheiltis/corpus/extract.py`)
- [ ] **2.4** Run `cd ~/dev/ciancheiltis && uv run pytest corpus/tests/test_morphology.py corpus/tests/test_grammar.py -v`

### PR #3 — Lift the Duchas source BAML + wire to the gaois.ie scraper (5 items)

- [ ] **3.1** Copy `baml_src/celtic/gaois/duchas.baml` → `~/dev/ciancheiltis/baml_src/celtic/gaois/duchas.baml` (no transformation)
- [ ] **3.2** Regenerate the baml_client: `cd ~/dev/ciancheiltis && uv run baml-cli generate`
- [ ] **3.3** Wire the Duchas BAML to the gaois.ie scraper in `ciancheiltis/sources/gaois.py`
- [ ] **3.4** Author `ciancheiltis/sources/tests/test_gaois_duchas.py` with the canonical gaois.ie scraping + Duchas extraction tests
- [ ] **3.5** Run `cd ~/dev/ciancheiltis && uv run pytest sources/tests/test_gaois_duchas.py -v`

## What stays behind (explicit)

- **The Phase 1 study-plan + oral-study-plan + certificate
  pipeline** — those are BIEP-specific and stay in cianfhoghlaim.
  ciancheiltis is the Celtic-language corpus sister repo; the BIEP
  ops surface doesn't apply here.
- **The 16 LC Convex tables + 5 jurisdiction tables** — ciancheiltis
  uses a different Convex schema (per the ciancheiltis Web layer).

## Sister-repo hand-off

- Ciancheiltis maintainer receives this lift patch + openspec
  change `2026-09-XX-ciancheiltis-lift-v1.md` (authored in
  `~/dev/ciancheiltis/openspec/changes/`).
- Approximate LOC delta: 380 LOC (~3 KB sources + ~12 KB
  vernaculars + ~6 KB morphology + ~7 KB grammar + ~4 KB Duchas +
  ~20 KB of CI/test scaffolding).
