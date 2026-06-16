# Spec Delta — Bilingual Routes (Parallel /en/ and /ga/ Paths)

## MODIFIED Requirements

### Requirement: URL-Based Language Selection

The system SHALL serve parallel `/en/...` and `/ga/...` route trees via TanStack Start route groups. The slugs are language-neutral (`/en/subjects/$slug`, `/ga/ábhair/$slug` — same `$slug`); the UI chrome flips between English and Irish.

#### Scenario: English Path
- **GIVEN** the user navigates to `/en/stages/senior_cycle`
- **WHEN** the route is resolved
- **THEN** the English-language version of the Senior Cycle overview is rendered
- **AND** the page chrome is in English (header, footer, navigation labels)

#### Scenario: Irish Path
- **GIVEN** the user navigates to `/ga/céimeanna/scoil-daraigh`
- **WHEN** the route is resolved
- **THEN** the Irish-language version of the Senior Cycle overview is rendered
- **AND** the page chrome is in Irish (header, footer, navigation labels)
- **AND** the BAML extractions return `text_ga`, `name_ga`, `description_ga` fields where available
- **AND** the slugs are: `c\u00e9imeanna` (stages), `bunscoil` (primary), `iar-bhunscoil` (junior cycle), `scoil-daraigh` (senior cycle), `ardteistim\u00e9ireacht` (leaving cert), `\u00e1bhair` (subjects), `c\u00farsa\u00ed` (courses), `point\u00ed-\u00e1ireamh\u00e1in` (points calculator), `agallamh-inghlactha` (matriculation), `faoi` (about), `comhr\u00e1` (chat)

#### Scenario: Language Switcher
- **GIVEN** the user is on `/en/stages/senior_cycle`
- **WHEN** they click the `<TranslationToggle>` chip in the header
- **THEN** the URL is rewritten to `/ga/c\u00e9imeanna/scoil-daraigh`
- **AND** the page re-renders with Irish-language content
- **AND** the toggle chip flips to show "EN" as the destination

#### Scenario: Bilingual Inline Block
- **GIVEN** a page with a `<BilingualBlock en={...} ga={...}>`
- **WHEN** the user clicks the "GA" badge within the block
- **THEN** the block expands to show the Irish version inline
- **AND** the click is local (does not navigate)

## ADDED Requirements

### Requirement: Locale-Aware BAML Data Binding
The system SHALL bind BAML extraction results to the active locale.

#### Scenario: Senior Cycle Subject Render in GA
- **GIVEN** the SPA is on `/ga/ábhair/matamaitic` (mathematics)
- **WHEN** the page loads
- **THEN** the data fetcher queries `subjects.lc_subjects.json` for the `mathematics` slug
- **AND** the BAML extraction returns `name_ga: "Matamaitic"`, `description_ga: "…"`
- **AND** the rendered page shows the Irish version
- **AND** the citation chip links to the same SEC source URL regardless of locale

### Requirement: Per-Stage Slug Mapping
The system SHALL provide a slug mapping between the English and Irish URL paths for each of the 5 stages.

#### Scenario: Slug Map
- **GIVEN** the slug map in `oideachais/web/apps/web/src/i18n/stage_slugs.ts`
- **WHEN** the file is read
- **THEN** the map contains:
  - `aistear` → `aistear` (same in both)
  - `primary` → `bunscoil`
  - `junior_cycle` → `iar-bhunscoil`
  - `senior_cycle` → `scoil-daraigh`
  - `tertiary` → `ardteistim\u00e9ireacht`
- **AND** the map is consumed by `<TranslationToggle>` to navigate between EN/GA versions of the same logical page
