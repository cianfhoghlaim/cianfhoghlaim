# Cross-Nation Content Audit — British-Isles Education Pipeline v2

**Author:** T5 / 2026-07-09-cross-nation-content-audit-v1
**Status:** v2 precondition (Ireland v1 ships without cross-nation
ingestion per
[`british-isles-education-pipeline`](../openspec/specs/british-isles-education-pipeline/spec.md)
**"Cross-nation extension deferred to v2"** requirement).
**Date:** 2026-07-09.

## 1. Executive summary

The British Isles comprises 5 distinct education jurisdictions — each
with its own awarding body, qualification framework, and language
convention. The Irish Republic's BIEP v1 ships for 6 priority Leaving
Certificate subjects + `gov.ie` education circulars. v2 extends the
same architecture (NCCA + SEC + BAML + CocoIndex v1 + DuckLake + DLT
+ MotherDuck) to the 5 other jurisdictions:

| Nation | Exam board(s) | Levels | Languages | Partition cycle key | Awarding body since |
|:--|:--|:--|:--|:--|:--|
| **Scotland** | SQA | National 5 / Higher / Advanced Higher | `en`, `gd` (Scots Gaelic) | `scottish_senior_phase` | 1997 (CfE reform: 2010) |
| **Wales** | WJEC + CBAC | GCSE / A-Level | `en`, `cy` (Welsh) | `gcse_a_level` (with `cy` for CBAC) | WJEC founded 1948; Curriculum for Wales 2022 reform |
| **England** | AQA / OCR / Pearson Edexcel / WJEC Eduqas | GCSE / A-Level / International GCSE | `en` (only) | `gcse_a_level` (with `board` axis) | AQA 2000 (3 boards + 1 Eduqas) |
| **Northern Ireland** | CCEA | GCSE / A-Level | `en`, `ga` (Irish) | `gcse_a_level` (with `ga` for Irish-medium) | CCEA 1994 (sole NI board) |
| **Crown Dependencies** (IoM / Jersey / Guernsey) | Mostly AQA + Pearson Edexcel | GCSE / A-Level | `en`; IoM has Manx `gv`; Jersey has Jèrriais | `gcse_a_level` (re-uses English board matrix) | Follows English NC |

The **canonical BAML schema for cross-nation comparison is already in
place** at
`cianfhoghlaim/baml/education/cross_nation/multi_nation_curriculum.baml`
— it declares the 5 `Nation` enum values, the 12
`NationEducationLevel` enum values, the 8 `QualificationBoard` enum
values, and the 5 functions
(`ExtractCrossNationSpec`, `AlignOutcomes`, `CompareCurricula`,
`TranslateEducationalContent`, `IdentifyResourceSharing`) that v2 will
re-use unchanged. The 6 Irish LC BAML extraction functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`,
`ExtractSyllabusDiagram`, `ExtractCircular`,
`LinkCircularToSyllabus`) at
`cianfhoghlaim/baml/education/lc_extraction/*.baml` apply to the
5-nation matrix with **only 2 new function requirements** that v2
will need to add (see § 4 below).

The **5 scaffolded DLT sources** at
`cianfhoghlaim/dlt/british_isles/{scotland,wales,england,england,northern_ireland}/education/{sqa,wjec,aqa,pearson,ccea}/syllabus_source.py`
are the proof-of-concept preconditions for v2 production-isation.
Each source reads from
`stedding/site_scrape_samples/<board>/<lang>/<subject>/sample.json`,
yields 1 row when the cache file exists, and 0 rows otherwise.

## 2. Per-nation breakdown

### 2.1 Scotland / SQA / Curriculum for Excellence

**Canonical exam-board URL:** `https://www.sqa.org.uk/sqa/56983.html`
(SQA National Qualifications finder). The SQA publishes course
specifications as PDF documents at `https://www.sqa.org.uk/sqa/files_*/...`
URLs. The Education Scotland curriculum area is at
`https://education.gov.scot/curriculum-for-excellence/` and the CfE
benchmarks at
`https://education.gov.scot/improvement/learning-resources/curriculum-for-excellence-benchmarks/`.

**Syllabus / paper / marking-scheme file layout.** SQA course
specifications are linked from the qualification index pages. The PDF
URL pattern is `https://www.sqa.org.uk/sqa/files_YYYY/<level>/<subject>/<course_code>.pdf`.
Past papers + marking schemes + course reports are at
`https://www.sqa.org.uk/pastpapers/` and the verified-grade archive at
`https://www.sqa.org.uk/sqa/48528.html`.

**EN / GA-equivalent language convention.** English is the default
language of instruction. Scots Gaelic (`gd`; ISO 639-1) is the second
language; the `Foghlam tron Ghàidhlig` programme
(`education.gov.scot/improvement/learning-resources/foghlam-tron-ghaidhlig/`)
publishes Gàidhlig-medium course materials for the same syllabuses.
SQA does not publish Gàidhlig-only syllabuses — the Gàidhlig subject
itself follows the same Higher / Advanced Higher structure as other
language subjects.

**Partition pattern.**
`MultiPartitionsDefinition(cycle=["national_5", "higher", "advanced_higher"], subject, language=["en", "gd"])`.
The `cycle` axis is distinct from the Irish `senior_cycle` — Scottish
senior phase covers S4-S6, with the 3 levels corresponding to S4 (N5),
S5 (Higher), S6 (Advanced Higher).

**BIEP-equivalent topic overlap with Ireland.** Mathematics, Chemistry,
Physics, Biology, English, History, Geography, Computing Science all
share topics with the 6 Irish LC priority subjects. The Scottish CfE
does NOT have a direct equivalent of Irish Gaeilge; the closest match
is the Gàidhlig subject but the syllabuses are language-content
(grammars, literature, translations) rather than the Irish Gaeilge
syllabus which integrates language + literature + oral.

### 2.2 Wales / WJEC / Curriculum for Wales

**Canonical exam-board URL:** `https://www.wjec.co.uk/` (WJEC
qualification finder). The Welsh-language brand is `CBAC`
(`Cyd-bwyllgor Addysg Cymru`); the same awarding body publishes under
both names, with `cy` URLs at `https://www.cbac.co.uk/`.

**Syllabus / paper / marking-scheme file layout.** WJEC publishes PDF
specifications at
`https://www.wjec.co.uk/media/<hash>/<filename>.pdf` (URL pattern from
2020+; older specifications at `/library/`). The Welsh-medium
(CBAC) versions live at `https://www.cbac.co.uk/media/...`. Past
papers and marking schemes are at
`https://www.wjec.co.uk/qualifications/<level>/<subject>-<level>/` with
PDFs at `/past-papers/` and `/mark-schemes/`.

**EN / GA-equivalent language convention.** Welsh (`cy`; ISO 639-1) is
the second language and is the only language with statutory protection
in Wales (the Welsh Language (Wales) Measure 2011 + the Curriculum for
Wales 2022). WJEC publishes parallel `en` and `cy` editions of every
GCSE and A-Level specification. Welsh-medium schools (Ysgolion
Cymraeg) follow the same syllabus but teach through the medium of
Welsh.

**Partition pattern.**
`MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, language=["en", "cy"])`.
The `cycle` axis is shared with England + NI but the `language` axis
differs — Wales has `cy` as a statutory second language whereas England
+ NI do not.

**Curriculum for Wales 2022.** Distinct from the English National
Curriculum or the older Welsh National Curriculum. CfW is organised
into 6 Areas of Learning and Experience (AoLE): Expressive Arts,
Health & Well-being, Humanities, Languages / Literacy /
Communication, Mathematics & Numeracy, Science & Technology. The
"Mathematics & Numeracy" AoLE is the direct equivalent of the
Irish LC Mathematics subject. v2 should note that the new CfW
qualifications are phasing in through 2025-2028 and that WJEC GCSE
Mathematics (the current qualification) will be replaced by the new
CfW Mathematics during the v2 implementation window.

**BIEP-equivalent topic overlap with Ireland.** Mathematics, English,
Welsh (2nd language), Chemistry, Biology, Physics, Geography, History,
Computer Science, Religious Studies all share topics with the 6 Irish
LC priority subjects + Gaeilge (Welsh 2nd language is the direct
analogue).

### 2.3 England / AQA / Pearson Edexcel / National Curriculum

**Canonical exam-board URLs.**

- AQA: `https://www.aqa.org.uk/subjects/gcse` (GCSE) +
  `https://www.aqa.org.uk/subjects/a-level` (A-Level). The AQA
  specification PDFs are at
  `https://filestore.aqa.org.uk/resources/<subject>/specifications/<code>-<version>.PDF`.
- Pearson Edexcel: `https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html`
  (GCSE) + `https://qualifications.pearson.com/en/qualifications/edexcel-a-levels.html`
  (A-Level) + `https://qualifications.pearson.com/en/qualifications/edexcel-international-gcses.html`
  (International GCSE). The Pearson specification PDFs are at
  `https://qualifications.pearson.com/downloads/<qual>/<subject>/Specification/<filename>.pdf`.
- OCR: `https://www.ocr.org.uk/qualifications/gcse/` +
  `https://www.ocr.org.uk/qualifications/as-a-level/`. (Not
  scaffolded in this change; v2 should add a 4th board.)
- WJEC Eduqas: `https://www.eduqas.co.uk/qualifications/`. (The
  English-specific brand of WJEC, separate from the Welsh WJEC;
  same body, different administrative structure.)

**Syllabus / paper / marking-scheme file layout.** Each board has its
own PDF URL pattern. AQA uses `/resources/<subject>/specifications/`,
Pearson uses `/downloads/<qual>/`, OCR uses `/Images/...`, Eduqas uses
`/qualifications/<code>/...`. The cross-board pattern is:
`<board-root>/<level>/<subject>` for the index page, with PDFs at
`<board-specific-path>/<filename>.pdf`. Past papers are at
`<board>/find-past-papers-and-mark-schemes` (AQA) or
`<board>/Past-papers` (Pearson).

**EN / GA-equivalent language convention.** English only. England has
no statutory second language at GCSE / A-Level. (Welsh-medium
provision exists in England as an MFL subject — the WJEC Eduqas
Welsh-second-language GCSE — but the language of instruction is
English.) The 2 international qualifications (Cambridge International,
Edexcel International) are in English.

**Partition pattern.**
`MultiPartitionsDefinition(cycle=["gcse", "a_level", "international_gcse"], subject, board=["aqa", "pearson", "ocr", "eduqas"], language=["en"])`.
The `board` axis is the key England-specific dimension — v2 should add
OCR + WJEC Eduqas as the 3rd + 4th board partition values. The
`international_gcse` value is Pearson-specific (the only English
board that offers iGCSE as a distinct qualification).

**BIEP-equivalent topic overlap with Ireland.** Mathematics, English,
Chemistry, Biology, Physics, Geography, History, Computer Science all
share topics with the 6 Irish LC priority subjects. The Pearson
Edexcel International GCSE Mathematics is a particularly strong match
for the Irish LC Mathematics (Ordinary level).

### 2.4 Northern Ireland / CCEA / NI Curriculum

**Canonical exam-board URL:** `https://ccea.org.uk/` (CCEA
qualification finder). The CCEA specifications are at
`https://ccea.org.uk/downloads/<filename>.pdf` (the URL pattern
varies by subject but follows `ccea.org.uk/<level>/<subject>/`).
CCEA also publishes the NI Curriculum at
`https://www.education-ni.gov.uk/topics/curriculum-and-learning`.

**Syllabus / paper / marking-scheme file layout.** CCEA follows a
single canonical pattern — `ccea.org.uk/<level>/<subject>/<specification>.pdf`
for the syllabus + `ccea.org.uk/<level>/<subject>/past-papers/` for
the papers. CCEA also has a dedicated `Irish-medium` portal at
`https://ccea.org.uk/irish-medium/` for the 18 Gaeltacht + Irish-medium
schools.

**EN / GA-equivalent language convention.** English is the default
language. Irish (`ga`; shared ISO 639-1 with the Republic of Ireland)
is the second language and is taught as a subject at GCSE + A-Level
following the same syllabus as the Irish Leaving Certificate Gaeilge.
The CCEA Irish-medium syllabuses are aligned with the NCCA
Gaeltacht-school syllabuses and the topics are near-identical.

**Partition pattern.**
`MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, language=["en", "ga"])`.
The `language` axis shares the `ga` code with the Republic of Ireland
— v2's cross-archive joins between `cianfhoghlaim.leaving_cert.gaeilge`
(Republic) and `ccea.gaeilge` (NI) are direct joins on
`(subject="gaeilge", language="ga")` with the `nation` dimension
distinguishing the source.

**BIEP-equivalent topic overlap with Ireland.** This is the
**strongest cross-nation overlap** in the entire matrix. Mathematics,
English, Irish (Gaeilge — the same subject as the Irish LC), Chemistry,
Biology, Physics, Geography, History, Computer Science, Religious
Studies all share topics. CCEA Gaeilge = Irish LC Gaeilge, modulo
the cross-jurisdiction grading scale (CCEA uses A*-G; Irish LC uses
H1-H7 at Higher, O1-O8 at Ordinary).

### 2.5 Crown Dependencies — Isle of Man / Jersey / Guernsey

**Canonical exam-board URL.** All 3 Crown Dependencies follow the
**English National Curriculum** and offer the same GCSE / A-Level
suite. The 3 jurisdictions do not have their own awarding body;
schools select from the English boards (mostly AQA + Pearson Edexcel
+ OCR) on a per-subject basis.

- **Isle of Man** (IoM): the Department of Education, Sport and
  Culture is at `https://www.gov.im/`. The Manx Gaelic (`gv`; ISO
  639-1) subject is offered at GCSE / A-Level via the Bunscoill
  Ghaelgagh schools.
- **Jersey**: the Department for Children, Young People, Education
  and Skills is at `https://www.gov.je/`. Jersey follows the
  English NC + offers French + Jèrriais (`roa-jersey`) at GCSE.
- **Guernsey**: the Committee for Education, Sport & Culture is at
  `https://gov.gg/`. Guernsey follows the English NC + offers
  French at GCSE (no distinct language of instruction).

**Partition pattern.** The same as England's: `gcse_a_level` cycle
with the `board` axis. The `language` axis is mostly `en`, with
`gv` (IoM), `fr` + `roa-jersey` (Jersey), `fr` (Guernsey) as
second-language subjects.

**BIEP-equivalent topic overlap with Ireland.** The 3 Crown
Dependencies are English-National-Curriculum-aligned, so the topic
overlap is identical to England. The Celtic-language additions
(Manx, Jèrriais) have no direct Irish LC equivalent, but
linguistically the closest match is Irish Gaeilge — v2 should treat
Manx + Irish as a shared Goidelic-language family for the
`TranslateEducationalContent` function.

## 3. Shared vs nation-specific topics

The cross-nation topic matrix below lists 12 of the most common
subject areas + how each is treated in each jurisdiction. The
columns are: `IE` (Republic of Ireland), `SC` (Scotland), `WA`
(Wales), `EN` (England), `NI` (Northern Ireland).

| Topic | IE | SC | WA | EN | NI |
|:--|:-:|:-:|:-:|:-:|:-:|
| Algebra | LC Maths | N5/Higher Maths | GCSE Maths | GCSE Maths | GCSE Maths |
| Probability + statistics | LC Maths | N5/Higher Maths | GCSE Maths | GCSE Maths | GCSE Maths |
| Calculus | LC Maths | Higher Maths | A-Level Maths | A-Level Maths | A-Level Maths |
| Mechanics | LC Maths / Applied Maths | N5/Higher Maths | A-Level Maths | A-Level Maths | A-Level Maths |
| Atomic structure | LC Chemistry | N5/Higher Chemistry | GCSE Chemistry | GCSE Chemistry | GCSE Chemistry |
| Organic chemistry | LC Chemistry | Higher Chemistry | A-Level Chemistry | A-Level Chemistry | A-Level Chemistry |
| British political history | LC History | Higher History | GCSE/A-Level History | GCSE/A-Level History | GCSE/A-Level History |
| Irish political history | LC History | (no equivalent) | (no equivalent) | (no equivalent) | GCSE History (cross-ref) |
| Physical geography | LC Geography | Higher Geography | GCSE Geography | GCSE Geography | GCSE Geography |
| Fieldwork (geography) | LC Geography | Higher Geography (mandatory) | GCSE Geography (mandatory) | GCSE Geography (mandatory) | GCSE Geography (mandatory) |
| Algorithm design | LC Computer Science | N5/Higher Computing Science | GCSE Computer Science | GCSE Computer Science | GCSE Computer Science |
| Programming (text-based) | LC Computer Science (Python) | N5/Higher Computing Science (Python + others) | GCSE Computer Science (Python + others) | GCSE Computer Science (Python + others) | GCSE Computer Science (Python + others) |

The **unique-to-one-nation** topics (i.e., the ones v2 needs
nation-specific extraction for) are:

- **IE-only**: Irish political history, Irish-language literature
  (Gaeilge subject — Litríocht + Úrsceal + Filíocht breakdown in
  the v1 Gaeilge notebook), the 8 distinct Irish LC subjects.
- **SC-only**: Gàidhlig (Scots Gaelic) — linguistically related to
  Irish Gaeilge but syllabuses are different (no Irish-medium
  programme in Scotland).
- **WA-only**: Welsh-language literature (Cyfres y Llyfr Glas — the
  prescribed Welsh-language set texts for GCSE/A-Level Welsh).
- **EN-only**: British imperial history 1688-2020 (a specific
  English A-Level History period study).
- **NI-only**: Irish-medium Gaeilge — content overlaps with IE
  Gaeilge (see § 2.4).
- **Crown-only**: Manx Gaelic (IoM) and Jèrriais (Jersey) — both
  no Irish LC equivalent.

The **shared-across-all-5** topics are the STEM core (algebra,
calculus, atomic structure, organic chemistry, algorithms) + the
humanities core (British political history, physical geography). The
`CompareCurricula` function in
`multi_nation_curriculum.baml:335-362` is the v2 entry point for
producing the cross-nation coverage matrix automatically.

## 4. BAML function reuse

The 7 lc_extraction + 5 cross_nation functions split into 3 buckets
based on v2 applicability:

**Bucket A — directly reusable (no changes needed):**

- `b.ExtractCurriculumSyllabus` (lc_extraction/curriculum_syllabus.baml)
  — works for any syllabus PDF. The NCCA + SEC training data
  generalises to SQA + WJEC + AQA + Pearson + CCEA.
- `b.ExtractExamPaperLayout` (lc_extraction/exam_paper_layout.baml)
  — works for any exam paper PDF.
- `b.ExtractMarkingSchemeGuideline`
  (lc_extraction/marking_scheme.baml) — works for any marking
  scheme PDF.
- `b.ExtractCrossLinguisticConcept`
  (lc_extraction/cross_linguistic.baml) — works for any
  EN↔Celtic-language pair (EN↔GA for Republic Ireland / NI;
  EN↔CY for Wales; EN↔GD for Scotland).
- `b.ExtractSyllabusDiagram` (lc_extraction/syllabus_diagram.baml)
  — works for any syllabus PDF with diagrams.
- `b.ExtractCircular` + `b.LinkCircularToSyllabus`
  (lc_extraction/circular_extraction.baml) — works for the
  cross-cutting circulars surface (each nation has its own — see
  v2 extension note below).
- `b.ExtractCrossNationSpec`
  (cross_nation/multi_nation_curriculum.baml:273-302) — the
  v2 BAML function for cross-nation extraction, already present.
- `b.AlignOutcomes` (multi_nation_curriculum.baml:304-333) —
  cross-nation outcome alignment, already present.
- `b.CompareCurricula` (multi_nation_curriculum.baml:335-362)
  — the coverage matrix producer, already present.
- `b.TranslateEducationalContent`
  (multi_nation_curriculum.baml) — cross-language translation,
  already present.
- `b.IdentifyResourceSharing`
  (multi_nation_curriculum.baml:364-387) — the v2 resource-sharing
  advisor, already present.

**Bucket B — needs minor extension in v2:**

- `b.ExtractCrossSubjectTopics`
  (lc_extraction/lc_topic_extraction.baml) — the
  `LCLevel` enum currently has only the Irish levels. v2 should
  add `SC_NATIONAL_5`, `SC_HIGHER`, `SC_ADVANCED_HIGHER` to
  `NationEducationLevel` (already done — see
  `multi_nation_curriculum.baml:18-58`) and call
  `ExtractCrossSubjectTopics` with the cross-nation level.

**Bucket C — needs NEW BAML functions in v2:**

- `b.ExtractSqaNationalQualification` (to be added) — for the SQA
  CfE-specific 3-level outcome structure (Experiences and Outcomes
  + Benchmarks + Course Specifications are 3 separate documents;
  the Irish schema assumes a single SyllabusDocument).
- `b.ExtractWelshMediumLesson` (to be added) — for the
  Curriculum for Wales 2022 AoLE (Areas of Learning and
  Experience) structure, which is fundamentally different from
  the Irish subject-based schema.

## 5. Hand-off to data-platform

The 5 scaffolded DLT sources are ready for v2 production-isation.
v2's work items:

1. **Replace the cache-only read path with a Firecrawl-crawl** of
   the 5 exam-board finder pages. The existing v1 BIEP crawl
   pattern (`cianfhoghlaim/dlt/british_isles/ireland/education/curriculumonline_syllabi.py`)
   is the template. Each of the 5 sources has a TODO marker in
   the docstring.
2. **Wire the partition pattern** as documented in § 2.1-2.4.
   v2's Dagster defs at
   `orchestration/defs/1_ingestion/curriculum/cross_nation/` will
   use `MultiPartitionsDefinition` for each of the 5 nations.
3. **Add OCR + BAML extraction** for the 5 nations. The
   `ExtractCurriculumSyllabus` function in
   `lc_extraction/curriculum_syllabus.baml` is the v2 entry
   point; v2 should add the 2 new BAML functions
   `ExtractSqaNationalQualification` + `ExtractWelshMediumLesson`
   to handle the SQA CfE 3-document split and the CfW AoLE
   structure respectively.
4. **Wire the CocoIndex v1 flow** for each nation (the existing
   `_lifespan.py` shared embedder + `lancedb.mount_table_target`
   pattern is the template).
5. **Add MotherDuck Dives** for the cross-nation coverage
   matrix — `CompareCurricula` produces the matrix as a
   `CoverageMatrix` JSON; v2 should expose this as a Dive.
6. **Wire `gov.ie`-equivalent circulars** for each nation
   (Scotland: `gov.scot`; Wales: `gov.wales`; England: `gov.uk`;
   NI: `education-ni.gov.uk`).

The 5 scaffolded sources in this change are the canonical
"proves the architecture works" preconditions for v2 — each one
passes the 1-row smoke test (see the ACCEPTANCE gates in
`openspec/changes/2026-07-09-cross-nation-content-audit-v1/proposal.md`).
