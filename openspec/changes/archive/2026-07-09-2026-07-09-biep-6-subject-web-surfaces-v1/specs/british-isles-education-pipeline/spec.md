## ADDED Requirements

### Requirement: BIEP v1 per-subject marimo notebooks — web surface wiring (R-BIEP-V1-NOTEBOOK-MARIMO-EMBED)

The system SHALL wire the 6 per-subject BIEP v1 marimo notebooks (one
per NCCA priority subject: Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) into the **public web surface**
via the 6 concrete TanStack Start routes at
`apps/web/src/routes/en/subjects/{mathematics,chemistry,geography,gaeilge,english,computer_science}.tsx`.
Each route SHALL embed the corresponding per-subject marimo notebook via
the `<BIEPSubjectPage>` shared renderer (at
`apps/web/src/components/BIEPSubjectPage.tsx`). The marimo embed
SHALL be served from `/_notebooks/{slug}.html` (the R2-signed / local
HTML export of the corresponding BIEP v1 marimo notebook).

The 6 source notebooks live at:

- `cianfhoghlaim/notebooks/03_leaving_cert/18_chemistry_biep_v1.py`
- `cianfhoghlaim/notebooks/03_leaving_cert/19_computer_science_biep_v1.py`
- `cianfhoghlaim/notebooks/03_leaving_cert/20_english_biep_v1.py`
- `cianfhoghlaim/notebooks/03_leaving_cert/21_gaeilge_biep_v1.py`
- `cianfhoghlaim/notebooks/03_leaving_cert/22_geography_biep_v1.py`
- `cianfhoghlaim/notebooks/03_leaving_cert/23_mathematics_biep_v1.py`

The notebooks SHALL continue to default to the local `bunchloch-infra`
lakehouse via `ibis.duckdb.connect()` + `ibis.lancedb.connect()`, with
the per-subject `ducklake_<subject>` database name. The system SHALL
reject any raw `duckdb.connect()` call in these notebooks per the
ibis-first contract from the `oideachais-marimo-dashboards` spec.

The Hono API SHALL expose the same data via 7 routes under
`/api/bi-ep-subjects` (the manifest + per-subject syllabus / papers /
marking-schemes / topics endpoints). The browser SHALL hit the API
endpoints for SPA hydration.

The web surface SHALL continue to fall back gracefully when the 6
Dagster `lc5_<subject>_extract` + `lc6_<subject>_marking_schemes`
assets have not yet materialised (the API rows ship empty arrays).

#### Scenario: Mathematics marimo embed is wired

- **GIVEN** `marimo export html cianfhoghlaim/notebooks/03_leaving_cert/23_mathematics_biep_v1.py > _notebooks/mathematics.html`
- **WHEN** the user navigates to `/en/subjects/mathematics`
- **THEN** the iframe `src="/_notebooks/mathematics.html"` loads the
  marimo notebook
- **AND** the notebook reads `oideachais.leaving_cert.mathematics_*` via
  `mo.sql(engine="md:oideachais", ...)` (or via ibis)

#### Scenario: Hono API serves the BIEP syllabus row

- **WHEN** the operator runs
  `curl http://localhost:8787/api/bi-ep-subjects/chemistry/syllabus`
- **THEN** the API returns JSON with the syllabus row payload from
  `oideachais.leaving_cert.chemistry_syllabus`
- **AND** the `baml_function` field reports
  `ExtractCurriculumSyllabus`

#### Scenario: GA mirror preserves the bilingual parity

- **WHEN** the user navigates to `/ga/subjects/mata`
- **THEN** the marimo embed URL is identical
  (`/_notebooks/mathematics.html`, not `/ga/_notebooks/mata.html`)
- **AND** the BIEPSubjectPage component renders the page with
  `language="ga"` (Irish KC labels + Irish cell descriptions)
- **AND** the bilingual toggle links to the EN mirror at
  `/en/subjects/mathematics`
