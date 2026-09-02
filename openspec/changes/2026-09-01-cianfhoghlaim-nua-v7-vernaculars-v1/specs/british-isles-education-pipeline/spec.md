## ADDED Requirements

### Requirement: The 7 British Isles vernacular languages MUST each have a BAML Extract<Vernacular>SubjectSpec function

The Cianfhoghlaim british-isles-education-pipeline capability MUST
expose a BAML `Extract<Vernacular>SubjectSpec(pdf_text, subject_slug,
stage, source_url)` function for each of the 7 British Isles
vernacular languages (beyond the canonical EN + GA pair):

1. **Welsh (cy)** — `ExtractWelshSubjectSpec` (WJEC + CBAC sources)
2. **Scottish Gaelic (gd)** — `ExtractScottishGaelicSubjectSpec` (SQA sources)
3. **Breton (br)** — `ExtractBretonSubjectSpec` (sister-repo lift target)
4. **Cornish (kw)** — `ExtractCornishSubjectSpec` (sister-repo lift target)
5. **Manx (gv)** — `ExtractManxSubjectSpec` (IoM Government sources)
6. **Channel Islands French (Jersey)** — `ExtractJerseyFrenchSubjectSpec` (States of Jersey sources)
7. **Channel Islands French (Guernsey)** — `ExtractGuernseyFrenchSubjectSpec` (States of Guernsey sources)
8. **Ulster Scots (sco)** — `ExtractUlsterScotsSubjectSpec` (DENI/NI sources)

Each `<Vernacular>SubjectSpec` MUST have:
- `display_name: string` (the vernacular language name)
- `display_name_en: string` (English translation)
- `display_name_ga: string` (Irish/Gaeilge translation)
- `language: VernacularLanguage` (the canonical enum)
- `jurisdiction_code: string` (WL/SC/IM/JE/GG/NI)

#### Scenario: A Welsh-medium school queries the Welsh syllabus

- **WHEN** a Welsh-medium school invokes
  `b.ExtractWelshSubjectSpec(pdf_text="...", subject_slug="mathematics", stage="gcse", source_url="https://...")`
- **THEN** the response is a `VernacularSubjectSpec` with:
  - `language: CY`
  - `jurisdiction_code: "WL"`
  - `display_name: "Mathemateg"` (Welsh)
  - `display_name_en: "Mathematics"`
  - `display_name_ga: "Matamaitic"` (Irish)