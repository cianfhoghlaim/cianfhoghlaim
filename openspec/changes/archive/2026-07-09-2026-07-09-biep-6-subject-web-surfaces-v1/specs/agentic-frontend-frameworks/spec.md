## ADDED Requirements

### Requirement: BIEP 6-subject web surfaces (the 6 per-subject landing pages + 6 Hono API endpoints) (R-AGENTIC-BIEP-WS-1)

The system SHALL expose 6 per-subject BIEP web surfaces (one per NCCA
priority subject: Mathematics, Chemistry, Geography, Gaeilge, English,
Computer Science) under the 5th surface
(`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`). Each surface
SHALL consist of:

1. **A concrete TanStack Start route** at
   `/en/subjects/{slug}.tsx` (and the Irish mirror at
   `/ga/subjects/{ga_slug}.tsx`).
2. **A BIEP subject card** rendering the NCCA code, level, éraic tier,
   primary agent, and BAML / DLT / marimo pipeline-integration card.
3. **The 5×8 mastery matrix** for the per-subject row, plus the
   cross-subject 5-column context panel.
4. **The 5 BIEP visualisations** per subject:
   - Topic frequency (per-year line chart, BAML `ExtractCurriculumSyllabus`)
   - Exam paper difficulty (per-year bar chart, BAML `ExtractExamPaperLayout`)
   - Marking scheme complexity (heatmap, BAML `ExtractMarkingSchemeGuideline`)
   - Cross-linguistic mapping (GA ↔ EN topic graph, BAML `ExtractCrossLinguisticConcept`)
   - Asset generator (per-topic 3D + 2D gallery)
5. **A live marimo embed** of the corresponding per-subject BIEP
   notebook (the 6 notebooks at
   `cianfhoghlaim/notebooks/03_leaving_cert/18..23_*_biep_v1.py`).
6. **A bilingual EN ↔ GA toggle** with the cross-link to the Irish
   mirror at `/ga/subjects/{ga_slug}`.
7. **The 6 Hono API endpoints** under
   `apps/api/src/routers/bi-ep-subjects.ts` mounted at
   `/api/bi-ep-subjects`: `GET /` + `GET /manifest` + `GET /:slug` +
   `GET /:slug/syllabus` + `GET /:slug/papers` +
   `GET /:slug/marking-schemes` + `GET /:slug/topics`. Each endpoint
   returns the live BIEP table contents (empty until the BIEP v1
   Dagster `lc5_<subject>_extract` + `lc6_<subject>_marking_schemes`
   assets materialise; run `mise run dagster:oideachais` then
   `Materialize all`).

The 6 concrete routes take precedence over the existing dynamic
`/en/subjects/$subject.tsx` for the 6 BIEP slugs;
`applied_mathematics` + `history` continue to fall through to the
dynamic fallback. The 6 Irish-mirror routes are additive (no dynamic
fallback).

The theming for the public surface SHALL be professional + minimal —
the mythology / historical-sources layer is deferred to BIEP-v2 per
the `2026-07-09-remove-brown-ajah-theming-v1` change. The public
tagline SHALL be "Cianfhoghlaim — Coláiste na Déisigh" (no mythology).

#### Scenario: A student opens Mathematics BIEP surface

- **GIVEN** the dev servers are up (`bun run dev` from
  `apps/cianfhoghlaim-leaving-cert/`)
- **WHEN** the user navigates to `/en/subjects/mathematics`
- **THEN** the page renders the 5×8 mastery matrix row
- **AND** the 5 BIEP visualisations render as CiTextbookPanels with
  the BAML function tagged
- **AND** the live marimo embed loads from `/_notebooks/mathematics.html`
- **AND** the bilingual EN↔GA toggle shows the Irish mirror link to
  `/ga/subjects/mata`

#### Scenario: A student opens the Irish mirror

- **GIVEN** the dev servers are up
- **WHEN** the user navigates to `/ga/subjects/mata`
- **THEN** the page renders in Irish (lang="ga")
- **AND** the BIEP subject card reads "Mata — BIEP v1" + "Mata"
- **AND** the 5×8 mastery matrix uses the Irish KC labels
  ("Cumarsáid", "Próiseáil Faisnéise", …)
- **AND** the bilingual toggle links to the EN mirror at
  `/en/subjects/mathematics`

#### Scenario: The Hono API serves the BIEP manifest

- **WHEN** the operator runs `curl http://localhost:8787/api/bi-ep-subjects/manifest`
- **THEN** the API returns JSON with the 6 BIEP subjects
- **AND** each subject has `slug` + `en_route` + `ga_route` +
  `notebook` + `table` + `primary_agent`

#### Scenario: The Hono API serves a single subject

- **WHEN** the operator runs
  `curl http://localhost:8787/api/bi-ep-subjects/mathematics/syllabus`
- **THEN** the API returns JSON with the syllabus rows from
  `oideachais.leaving_cert.mathematics_syllabus`
- **AND** the `baml_function` field reports
  `ExtractCurriculumSyllabus`

#### Scenario: The Brown Ajah / WoT theming is fully removed from the 5th surface

- **WHEN** `ccc search "Brown Ajah"` runs against
  `cianfhoghlaim/web/`
- **THEN** 0 matches are returned (except the workbench vendored
  copy at `dlthub-ai-workbench/`)
- **AND** `ccc search "Aes Sedai"` returns 0 matches
- **AND** the Header does not show "Aes Sedai — servants of all"
- **AND** the Sidebar does not show `Theming=Brown Ajah`
