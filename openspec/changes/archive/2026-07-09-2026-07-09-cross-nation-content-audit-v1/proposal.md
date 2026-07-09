# Proposal: 2026-07-09-cross-nation-content-audit-v1

## Why

The British-Isles Education pipeline (BIEP) v1 ships as an **Ireland-only**
capability covering the 6 priority Irish Leaving Certificate subjects +
`gov.ie` education circulars. v1's
[`british-isles-education-pipeline`](../specs/british-isles-education-pipeline/spec.md)
spec deliberately defers Scotland (SQA), Wales (WJEC), England (AQA / OCR
/ Pearson Edexcel), Northern Ireland (CCEA), and the Crown Dependencies
(Isle of Man, Jersey, Guernsey) to a future v2 change (see the
**"Cross-nation extension deferred to v2"** requirement in the v1 spec).

But before v2 can be specced, the data-platform team needs an
**authoritative cross-nation content audit** so the v2 design can be
informed by facts on the ground — the actual exam-board URL patterns,
the syllabus / paper / marking-scheme file layouts, the language
conventions, and the topic overlap with the Irish LC subjects.

The v1 spec already establishes the partition pattern
(`MultiPartitionsDefinition(cycle="senior_cycle", subject, language)`) and
the BAML cross-nation schema
(`baml/education/cross_nation/multi_nation_curriculum.baml` with
`ExtractCrossNationSpec`, `AlignOutcomes`, `CompareCurricula`,
`TranslateEducationalContent`, `IdentifyResourceSharing`). What v1 does
NOT have is a curated 5-nation audit + 5 scaffolded DLT sources as a
proof-of-concept that the partition + destination + local-scrape-cache
pattern works the same way for SQA, WJEC, CCEA, AQA, and Pearson as it
does for the Irish NCCA + SEC.

This change produces both:

1. **The canonical audit document** at
   `docs/agents/cross-nation-content-audit.md` (~2,000-3,000 words) —
   a fact-based reference that the v2 design will consume, covering all
   5 nations (SQA / WJEC / CCEA / AQA / Pearson) + the Crown
   Dependencies (IoM / Jersey / Guernsey) at the level of detail
   needed to scaffold production DLT sources, BAML extraction, and
   MotherDuck Dives.
2. **5 scaffolded DLT sources** as proof-of-concept — one per nation /
   exam board, each reading from a placeholder
   `stedding/site_scrape_samples/<board>/en/<subject>/sample.json`
   cache. Each source passes a 1-row smoke test.

The deliverable's primary audience is the v2 design lead, the data
platform's BIEP owners, and the agent fleet (Root + Curriculum agents
that consume the cross-nation topic map).

## What changes

### C.1 — Cross-nation audit document

The single new artifact `docs/agents/cross-nation-content-audit.md`
covers, in this order:

1. **Executive summary** — the 5-nation exam-board matrix
   (subject × nation × level × year × language).
2. **Per-nation breakdown** — for each of SQA / WJEC / CCEA / AQA /
   Pearson + a sub-section for the Crown Dependencies, the canonical
   exam board URL, the syllabus/paper/marking-scheme file layout, the
   language convention, the partition pattern, and a syllabus-topic
   overlap with Ireland.
3. **Shared vs nation-specific topics** — a table of which topics are
   common across nations (e.g. "algebra", "British political history")
   and which are nation-specific (e.g. "Welsh-language poetry", "Scots
   Gaelic-medium numeracy", "Irish-medium gaeltacht schools").
4. **BAML function reuse** — a mapping from each of the 5 nation
   sources to the 7 lc_extraction functions
   (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
   `ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`,
   `ExtractSyllabusDiagram`, `ExtractCircular`, `LinkCircularToSyllabus`),
   with the 3 cross-nation functions
   (`ExtractCrossNationSpec`, `AlignOutcomes`, `CompareCurricula`,
   `TranslateEducationalContent`, `IdentifyResourceSharing`) called out
   as already-prepared. Flags the 2 new BAML functions v2 will need
   (`ExtractSqaNationalQualification` for CfE, `ExtractWelshMediumLesson`).
5. **Hand-off to data-platform** — the 5 scaffolded DLT sources
   are ready for v2 production-isation; the v2 change consumes them
   unchanged.

### C.2 — 5 scaffolded DLT sources (one per nation / exam board)

For each of:

- `cianfhoghlaim/dlt/british_isles/scotland/education/sqa/syllabus_source.py`
  (Scotland / SQA / Curriculum for Excellence)
- `cianfhoghlaim/dlt/british_isles/wales/education/wjec/syllabus_source.py`
  (Wales / WJEC + CBAC / Curriculum for Wales)
- `cianfhoghlaim/dlt/british_isles/england/education/aqa/syllabus_source.py`
  (England / AQA / National Curriculum)
- `cianfhoghlaim/dlt/british_isles/england/education/pearson/syllabus_source.py`
  (England / Pearson Edexcel / National Curriculum)
- `cianfhoghlaim/dlt/british_isles/northern_ireland/education/ccea/syllabus_source.py`
  (Northern Ireland / CCEA / NI Curriculum)

… a minimal DLT source module that:

- Decorates a `@dlt.resource(name="<subject>_syllabus", write_disposition="merge", primary_key=["url"])`.
- Reads from `stedding/site_scrape_samples/<board>/<lang>/<subject>/sample.json`
  when the cache file exists (the `USE_LOCAL_SCRAPES=true` path).
- Yields 1 row with the cache file's metadata when the file is
  present, 0 rows otherwise (does NOT scrape live).
- Uses the existing `get_dlt_destination(namespace="<board>")`
  factory from `cianfhoghlaim/dlt/common/destinations_oideachais.py`
  (the `warehouse`-equivalent named destination — the v1 BIEP uses
  this for the 6 Irish LC subjects; this change extends the
  per-namespace pattern to the 5 cross-nation boards).
- Honours `USE_LOCAL_SCRAPES=true` to skip any future live network
  calls (the scaffolded sources never make a live call, but the env
  var is honoured for future-proofing).
- The `<subject>` for the scaffolded proof-of-concept is
  `mathematics` (the only subject common to all 5 nations at every
  level).

### C.3 — 5 placeholder cache files

For each of `sqa / wjec / aqa / pearson / ccea` × `en / mathematics`,
a placeholder JSON cache file at
`stedding/site_scrape_samples/<board>/en/mathematics/sample.json`
shaped like a Firecrawl scrape output (markdown content + metadata
block). The audit doc references these as the canonical
"what an empty cache looks like" examples.

### C.4 — Spec deltas (in `specs/british-isles-education-pipeline/spec.md`)

Two new ADDED Requirements, in the existing v1 spec:

- **`Requirement: cross-nation audit produced for SQA / WJEC / CCEA / AQA / Pearson`** —
  the canonical audit document exists; the 5 exam-board URLs are
  documented; the per-nation language + partition pattern is set.
- **`Requirement: 5 scaffolded DLT sources (one per nation) pass the smoke test`** —
  each source's `dlt.pipeline().run(source())` produces >=1 row when
  the cache file exists and 0 rows otherwise; each source's
  `@dlt.resource` decorator matches the v1 contract
  (`name=..._syllabus`, `write_disposition="merge"`,
  `primary_key=["url"]`).

The existing **"Cross-nation extension deferred to v2"** requirement
is updated (in a MODIFIED delta) to point at the v2 change that will
build on top of this scaffold.

## What does NOT change

- The existing 5 nation-level DLT directories
  (`cianfhoghlaim/dlt/british_isles/{scotland,wales,england,northern_ireland,jersey,guernsey,isle_of_man}/education/`)
  are NOT modified — the v1 BIEP crawl-based sources at
  `.../education/sqa_qualifications.py`,
  `.../education/wjec_qualifications.py`,
  `.../education/ccea_qualifications.py`,
  `.../education/aqa_qualifications.py`,
  `.../education/edexcel_qualifications.py` continue to work
  unchanged. The 5 new scaffolded sources live alongside them in
  new `<board>/` subdirectories.
- The 6 Irish LC priority subjects' BAML functions +
  `baml/education/cross_nation/multi_nation_curriculum.baml` schema
  are NOT modified — this change is purely audit + scaffold.
- No live web scrapes. All reads from local cache.

## Files (NEW + modified)

### New Python files (5 DLT sources)

- `cianfhoghlaim/dlt/british_isles/scotland/education/sqa/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/wales/education/wjec/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/england/education/aqa/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/england/education/pearson/syllabus_source.py`
- `cianfhoghlaim/dlt/british_isles/northern_ireland/education/ccea/syllabus_source.py`

### New cache files (5)

- `stedding/site_scrape_samples/sqa/en/mathematics/sample.json`
- `stedding/site_scrape_samples/wjec/en/mathematics/sample.json`
- `stedding/site_scrape_samples/aqa/en/mathematics/sample.json`
- `stedding/site_scrape_samples/pearson/en/mathematics/sample.json`
- `stedding/site_scrape_samples/ccea/en/mathematics/sample.json`

### New docs

- `docs/agents/cross-nation-content-audit.md` (the main deliverable;
  ~2,000-3,000 words)

### New openspec

- `openspec/changes/2026-07-09-cross-nation-content-audit-v1/`
  (this change)
- `openspec/changes/2026-07-09-cross-nation-content-audit-v1/specs/british-isles-education-pipeline/spec.md`
  (the 2 ADDED Requirements + 1 MODIFIED delta)

## Acceptance

- `openspec validate 2026-07-09-cross-nation-content-audit-v1 --strict` passes.
- `docs/agents/cross-nation-content-audit.md` exists, is 2,000-3,000 words.
- 5 scaffolded DLT sources each successfully read 1 cached fixture from
  their respective nation dirs (smoke test via
  `dlt.pipeline().run(source())`).
- `ccc search "cross-nation scaffold"` finds the 5 new sources.
- The 5 nations' exam board URLs are documented in the audit doc
  (with at least 1 working URL per nation).
- Push target: `origin/pick-4-biep-v1`.
