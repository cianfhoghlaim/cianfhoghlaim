# Spec Delta — `oideachais-marimo-dashboards` (modified)

## Purpose

`oideachais-marimo-dashboards` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/notebooks/` and
`cianfhoghlaim/notebooks/dashboards/`. See `docs/00_index.md` for the
quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

This delta adds the new `university_courses.py` marimo notebook
(per the `oideachais-university-deep-extraction` spec) to the
canonical marimo surface, bringing the total notebook count from 11
to 12. The new notebook has 4 tabs (M.Sc. AI 25/26 modules / All UoG
courses / Reading lists / Cross-archive) and is mounted at
`/dashboards/university-courses`.

## ADDED Requirements

### Requirement: University courses dashboard

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/_oideachais/university_courses.py`
served at `/dashboards/university-courses`. The notebook SHALL have
4 tabs (per the `oideachais-university-deep-extraction` spec):

1. **M.Sc. AI 25/26 modules** — pre-filtered to the user's upcoming programme
2. **All UoG courses** — searchable, filterable by school / NFQ level / ECTS
3. **Reading lists** — every reading-list item, with "Group by module" + "Group by ISBN-13" toggles
4. **Cross-archive** — the user's personal UoG artefacts joined to the matching scraped `CourseDescriptor` rows via the new Cognee edge

The notebook SHALL use `mo.sql(engine=md:oideachais)` (the MotherDuck
Postgres endpoint) for the underlying queries.

#### Scenario: User opens the M.Sc. AI 25/26 tab

- **WHEN** the user navigates to `/dashboards/university-courses` and clicks the "M.Sc. AI 25/26" tab
- **THEN** the notebook SHALL display a table of all 12+ modules in the M.Sc. AI 2025-26 programme
- **AND** each row SHALL show `module_code`, `module_title`, `ects`, `semester`, `lecturers[]`, `assessment_breakdown`, and a clickable `source_url`

#### Scenario: Cross-archive join renders

- **GIVEN** the `university_cross_archive` cognify pass has emitted the `CT511 → HDSD` and `MA335 → BScMS` edges
- **WHEN** the user opens the "Cross-archive" tab
- **THEN** the table SHALL show the user's CT511 + MA335 assignments on the left, the matching course descriptors on the right, and the `match_confidence` between them
- **AND** clicking a `course_descriptor.url` SHALL open the UoG programme page in a new tab

#### Scenario: Reading lists grouped by ISBN-13

- **WHEN** the user opens the "Reading lists" tab and selects the "Group by ISBN-13" radio button
- **THEN** the table SHALL be grouped by `isbn_13` (rows with the same ISBN are combined)
- **AND** each group SHALL show the count of modules referencing that book
- **AND** books appearing in ≥ 2 modules SHALL be highlighted (e.g. with a `📚` emoji prefix in the title)
