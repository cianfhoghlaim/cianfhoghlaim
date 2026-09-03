## ADDED Requirements

### Requirement: Public /about route (R11)

The system SHALL provide a publicly accessible About route at `/en/about`
(mirror: `/ga/about`) that renders the Brown Ajah Wheel of Time theming
summary, the 6 subnations, the 13 éraic treasures, and the 5 NCCA Key
Competencies — without exposing any operator-only lineage. The route
SHALL be served from the existing TanStack Router file-based routing
under `apps/web/src/routes/{en,ga}/about.tsx`.

#### Scenario: /en/about returns the public about page

- **GIVEN** the user navigates to `http://localhost:3082/en/about`
- **WHEN** the page loads
- **THEN** the Brown Ajah theming summary renders (4 Wheel of Time references: Aes Sedai, Amyrlin Seat, Dragon Reborn, Dragon Banner, Tuatha'an)
- **AND** the 6 subnations render with their v1-active / coming-soon badges
- **AND** all 13 éraic treasures render with their bilingual EN+GA names
- **AND** the 5 NCCA Key Competencies render with their Tuatha Dé Danann deity mapping
- **AND** no text on the page matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`
- **AND** no text on the page matches the family surnames `Deacy`, `Lyons`, `Morris`, `Conroy`

#### Scenario: /ga/about renders the Irish mirror

- **GIVEN** the user navigates to `http://localhost:3082/ga/about`
- **WHEN** the page loads
- **THEN** the page renders the same content as `/en/about` but with the Irish-language headings first
- **AND** the bilingual `name_en` + `name_ga` pairs are present (the Irish version flips the visual order, the English version keeps the English first)

#### Scenario: Header has an About link

- **GIVEN** the user is on any page of the Cianfhoghlaim OS
- **WHEN** the Header renders
- **THEN** the right-hand nav contains an `About` link
- **AND** the link targets `/en/about` when the active language is `en`
- **AND** the link targets `/ga/about` when the active language is `ga`
- **AND** the link is not a sibling to the operator-only lore document

#### Scenario: Lore constraint — no operator-only content on the public page

- **GIVEN** the user opens `/en/about` or `/ga/about`
- **WHEN** the page is parsed for the privacy-constraint regex set
- **THEN** the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]` matches zero substrings on the page
- **AND** the family surnames `Deacy`, `Lyons`, `Morris`, `Conroy` appear zero times
- **AND** the 3 Gemini Deep Research warrants (`claiming_rí_na_gaillimhe`, `claiming_irish_kingship_through_lineage`, `royal_titles_celtic_heritage_and_claims`) appear zero times
- **AND** no link on the page targets `docs/CIANFHLOGHLAIM_LORE.md`