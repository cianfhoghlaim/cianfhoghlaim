# Spec Delta — `oideachais-leabharlann` (modified)

## Purpose

`oideachais-leabharlann` is a capability of the Cianfhoghlaim platform
that covers the 4 dlt sources (books, zotero, takeout, UoG personal
archive), the 3 v1 CocoIndex Apps, the 7 Dagster assets, the 1
directory-watch sensor, the 3 cognify passes, and the 3 cross-archive
edge rules in the `leabharlann/` personal-archive subtree. See
`docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md`
for the project identity.

This delta adds a **4th cross-archive edge rule** that links the
user's `leabharlann/ollscoil_na_gaillimhe/` artefacts (B.Sc. Math &
Education, H.Dip Software Design & Development, etc.) to the
scraped `university_course_descriptor` rows produced by the new
`oideachais-university-deep-extraction` pipeline. The new rule lives
at `cianfhoghlaim/cognify/rules/university_cross_archive.py` and is
registered alongside the existing 3 rules in
`cianfhoghlaim/cognify/rules/leabharlann_cross_archive.py`.

## ADDED Requirements

### Requirement: 4 cross-archive edge rules

The system SHALL provide 4 cross-archive edge rules that link nodes
across the 4 leabharlann corpora (books, zotero, takeout, UoG personal
archive) AND the new `university_course_descriptor` corpus produced by
the `oideachais-university-deep-extraction` pipeline:

| # | Rule | Description | Source → Target |
|:--|:--|:--|:--|
| 1 | `GeminiReport-CITES-ZoteroPaper` | (existing) A `author_archive_gemini_report` cites a `leabharlann_zotero_paper` | match by `arxiv_id` |
| 2 | `UoGArtifact-TEACHES-ZoteroPaper` | (existing) A `uog_coursework_artifact` teaches a `leabharlann_zotero_paper` | match by fuzzy title similarity > 0.7 |
| 3 | `TakeoutDoc-CITES-GeminiReport` | (existing) A `leabharlann_takeout_doc` cites a `author_archive_gemini_report` | match by URL substring |
| 4 | `UoGArtifact-MATCHES-CourseDescriptor` | (new) A `uog_coursework_artifact` matches a `university_course_descriptor` | match by `course_code` exact OR fuzzy title > 0.85 |

#### Scenario: User's CT511 assignment maps to the scraped HDSD descriptor

- **GIVEN** a `uog_coursework_artifact` with `course_code = "CT511"`, `module_title = "Software Engineering"`
- **AND** a `university_course_descriptor` with `programme_code = "HDSD"`, `course_title = "Higher Diploma in Science (Software Design & Development)"`
- **WHEN** the `university_cross_archive` cognify pass runs
- **THEN** a `UoGArtifact-MATCHES-CourseDescriptor` edge SHALL be emitted
- **AND** the edge's `match_confidence = 1.0`
- **AND** the marimo `university_courses.py` "Cross-archive" tab SHALL display the join

#### Scenario: User's MA335 matches a BSc Mathematical Science descriptor

- **GIVEN** a `uog_coursework_artifact` with `course_code = "MA335"`, `module_title = "Mathematical Statistics"`
- **AND** a `university_course_descriptor` with `programme_code = "BScMS"`, `course_title = "Bachelor of Science (Mathematical Science)"`
- **WHEN** the `university_cross_archive` cognify pass runs
- **THEN** a `UoGArtifact-MATCHES-CourseDescriptor` edge SHALL be emitted
- **AND** the edge's `match_confidence ≥ 0.85` (fuzzy match on `Statistics`)

#### Scenario: A user artefact with no matching course descriptor

- **GIVEN** a `uog_coursework_artifact` with `course_code = "ED305"`, `module_title = "Action Research Project"`
- **AND** no `university_course_descriptor` with a matching `programme_code` or title similarity > 0.85
- **WHEN** the `university_cross_archive` cognify pass runs
- **THEN** no `UoGArtifact-MATCHES-CourseDescriptor` edge SHALL be emitted
- **AND** the pass SHALL log a debug message with the artefact's `file_hash` and the best-match confidence (0.0 - 0.85) for observability
