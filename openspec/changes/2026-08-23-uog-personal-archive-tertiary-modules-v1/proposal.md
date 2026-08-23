# 2026-08-23-uog-personal-archive-tertiary-modules-v1

> Lift `leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG
> courses' artefacts: BA Maths & Education, HDip Software Design,
> Diploma in Irish C1) + `cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf`
> to **full feature parity with the Leaving Cycle subject pipeline**.
>
> The source is the folder as-is, auto-discovered (no curated drop-PDF
> UI as primary entry). The pipeline produces typed artefacts →
> assignments → questions → topics → code cells → reading items →
> CA marks → transcript rows at **F-granularity** (per-question),
> joins to the transcript for ground truth, embeds in LanceDB, draws
> typed Cognee edges, and surfaces via marimo + Convex + CopilotKit
> + Genie + ADK agent — **transferable to any user** (the same
> factory runs against any other student's
> `leabharlann/<university>/` corpus).

## Why

The Cianfhoghlaim platform has:

- A **public** UoG deep-extraction pipeline
  (`openspec/changes/2026-07-15-cianfhoghlaim-university-deep-extraction-v1` /
  `dlt_sources/british_isles/ireland/education/_university_deep_factory.py`).
- An **authenticated** UoG exam-papers pipeline
  (`openspec/changes/2026-08-23-uog-exam-papers-sso-v1` /
  `dlt_sources/british_isles/ireland/education/university/exam_papers/`)
  with VLM extraction, CocoIndex embeddings, Cognee cross-archive edges.
- A **leabharlann** filesystem DLT source
  (`dlt_sources/filesystem/university_of_galway.py`) that emits
  `author_archive_uog_documents` rows from
  `leabharlann/ollscoil_na_gaillimhe/`, but **only** as untyped
  file-system metadata + the legacy single-class `ExtractUoGArtifact`
  BAML function.

The **remaining gap** between the user's personal UoG archive and
the leaving-cycle subject pipeline — and between UoG and the
post-v7 typed-pipeline paradigm more broadly — has five facets:

1. **No F-granularity decomposition.** The leaving-cycle subject
   pipeline yields typed artefacts → exam questions → topics →
   reading-list items at the *individual-question* level (so a
   student can ask "show me every question on Laplace transforms I
   ever got wrong"). The personal-archive source yields one row
   per file with no decomposition.
2. **No transcript join.** The user has
   `cian_mac_an_déisigh_uí_liatháin/achievement/2013_2023_transcript_nuig.pdf`
   — the canonical ground-truth document. The current source does
   not link CA marks (typed from assignment front-pages) to
   transcript rows (typed from the transcript PDF).
3. **No code-cell / reading-list / topic-graph layer.** The
   leaving-cycle pipeline has typed Topics + ReadingItems + CodeCells
   (for the programming subjects). The personal-archive source
   only emits artefact rows.
4. **No typed Cognee edges.** The 6 leabharlann cognify rules
   (`scripts/graph_storage/cognify/rules/leabharlann_*.py`) emit
   cross-archive edges, but the personal archive lacks the
   10 typed edges that the leaving-cycle pipeline draws
   (`Artefact-DESCRIBES-Module`,
   `Question-ANSWERED_BY-Response`,
   `Response-GRADED_AS-TranscriptGrade`, etc.).
5. **No transferability.** Every other tertiary source is keyed
   on `ie-university-galway` (the case study). The personal archive
   should be parameterised on a generic `UniversityPersonalArchiveConfig`
   so any student (any future user, not just Cian) can point the
   pipeline at their own `leabharlann/<university>/` directory.

## What changes

| Layer | New artefact |
|---|---|
| Openspec contract | this change (1 sub-spec + tasks + proposal) |
| BAML schema | `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml` (10 new classes + 3 new enums + 7 new functions) |
| DLT source | `dlt_sources/filesystem/uog_personal_archive.py` (8 resources: artefacts, assignments, questions, topics, reading_lists, code_cells, ca_marks, transcripts) |
| DLT factory | `dlt_sources/british_isles/ireland/education/university/personal_archive/uog_personal_archive_source.py` (parameterised on `UniversityPersonalArchiveConfig`) |
| HTR ensemble | `dlt_sources/filesystem/_htr_ensemble.py` (the 4-VLM consensus router used by every resource) |
| DuckLake destination | `dlt_sources/_lakehouse/personal_archive_destinations.py` (9 typed tables under `cianfhoghlaim.education.ie.personal_archive.*` + `student_transcripts`) |
| Typed DuckLake tables | 9 new tables: `personal_archive_{artefacts,assignments,questions,topics,reading_lists,code_cells,ca_marks,modules}` + `student_transcripts` |
| Cognee edges | 10 typed edge rules at `scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py` (created by the parallel subagent) — wired in via `scripts/graph_storage/cognify/rules/__init__.py` |
| Env vars | 9 new vars on `.env.example` (the `UNIVERSITY_PERSONAL_ARCHIVE_*` set + `DUCKLAKE_DESTINATION`) |

## Non-goals

- **No curated drop-PDF UI as primary entry.** The pipeline
  auto-discovers the directory; users may add files freely.
- **Do NOT touch `ExtractUoGArtifact`.** The legacy
  `ExtractUoGArtifact` BAML function (defined in
  `baml_src/british_isles/ireland/education/junior_cycle/author_archive.baml`)
  remains the case-study extract for the leaving-cert pipeline;
  it is not the per-question typed extractor for the personal
  archive. The new functions in `personal_archive_extraction.baml`
  are the canonical per-question / per-topic / per-cell /
  per-reading extractors.
- **No change to the in-flight `2026-08-23-uog-exam-papers-sso-v1`
  and `2026-08-23-uog-official-docs-and-nui-superset-v1` changes.**
  The personal-archive change is **additive** — the 2 in-flight
  changes remain untouched. Their dagster assets, CocoIndex apps,
  BAML functions, and DuckLake tables are not modified.
- **No ethics / GDPR signoff change.** The artefacts are the
  student's own work + the official transcripts the student owns.

## Receipt of approver feedback

N/A — first proposal.
