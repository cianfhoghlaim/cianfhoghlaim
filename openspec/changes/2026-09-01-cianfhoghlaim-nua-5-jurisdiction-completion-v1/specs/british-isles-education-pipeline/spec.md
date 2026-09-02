## ADDED Requirements

### Requirement: The 8 British Isles jurisdictions MUST each have a bilingual (EN + GA) Extract<Jurisdiction>SubjectSpec BAML function with a vernacular overlay class

The Cianfhoghlaim british-isles-education-pipeline capability MUST
expose an `Extract<Jurisdiction>SubjectSpec(pdf_text, subject_slug,
stage, source_url)` BAML function for each of the 8 British Isles
jurisdictions:

1. **IE (Ireland)** — `ExtractIrelandSubjectSpec` (already shipped)
2. **EN (England)** — `ExtractEnglandSubjectSpec` (Step 4)
3. **WL (Wales)** — `ExtractWalesSubjectSpec` (Step 5) + `WelshMediumOverlay` class
4. **NI (Northern Ireland)** — `ExtractNorthernIrelandSubjectSpec` (Step 6) + `GaeltachtOverlay` class
5. **IM (Isle of Man)** — `ExtractIsleOfManSubjectSpec` (Step 7) + `ManxOverlay` class
6. **SC (Scotland)** — `ExtractScotlandSubjectSpec` (Step 8) + `ScottishGaelicOverlay` class
7. **JE (Jersey)** — (future; Step 8 deferred)
8. **GG (Guernsey)** — (future; Step 8 deferred)

Each `<Jurisdiction>SubjectSpec` class MUST have:
- `display_name: string` (English)
- `display_name_ga: string` (Irish/Gaeilge translation)
- `display_name_local: string` (vernacular — Welsh / Manx / Gàidhlig)

Each jurisdiction with a vernacular language MUST also expose a
vernacular overlay class (e.g. `WelshMediumOverlay`,
`GaeltachtOverlay`, `ManxOverlay`, `ScottishGaelicOverlay`).

#### Scenario: A Welsh-medium school queries the Wales syllabus

- **WHEN** a Welsh-medium secondary school invokes
  `b.ExtractWalesSubjectSpec(pdf_text="...", subject_slug="mathematics", stage=ENStage.LEAVING_CERT, source_url="https://...")`
- **THEN** the response is a `WalesSubjectSpec` with:
  - `display_name: "Mathematics"`
  - `display_name_ga: "Matamaitic"`
  - `display_name_local: "Mathemateg"` (Welsh)
  - `language: "cy+en+ga"` (bilingual)
- **AND** the `WelshMediumOverlay` class flags `welsh_medium: true`