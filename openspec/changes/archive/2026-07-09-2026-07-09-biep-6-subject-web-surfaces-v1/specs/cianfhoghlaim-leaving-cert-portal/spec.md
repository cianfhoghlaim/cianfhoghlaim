## ADDED Requirements

### Requirement: BIEP 6-subject landing pages + GA mirror routes (R-LEAVING-CERT-BIEP-WS-1)

The system SHALL expose 6 concrete per-subject landing pages — one per
NCCA BIEP priority subject (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) — at `/en/subjects/{slug}.tsx` on
the 5th surface
(`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`). Each landing
page SHALL render:

- The NCCA subject card (code, level, éraic tier, primary agent)
- The 5×8 mastery matrix (per-subject row) +
  the cross-subject 5-column context panel
- The 5 BIEP visualisations (topic frequency, exam paper difficulty,
  marking scheme complexity, cross-linguistic mapping, asset generator)
- The live marimo embed of the corresponding per-subject BIEP notebook
- The bilingual EN ↔ GA toggle + the cross-link to the Irish mirror at
  `/ga/subjects/{ga_slug}`

The system SHALL also expose 6 Irish mirror routes at
`/ga/subjects/{ga_slug}.tsx` for the 6 priority subjects. The Irish
slug mapping is:

- `mathematics` ↔ `mata`
- `chemistry` ↔ `ceimic`
- `geography` ↔ `tireolaiocht`
- `gaeilge` ↔ `gaeilge`
- `english` ↔ `bearla`
- `computer_science` ↔ `riomheolaiocht`

The 6 concrete EN routes take precedence over the existing dynamic
`/en/subjects/$subject.tsx` for the 6 BIEP slugs;
`applied_mathematics` + `history` continue to fall through to the
dynamic fallback.

The public surface tagline SHALL be "Cianfhoghlaim — Coláiste na
Déisigh" (no mythology overlay). The mythology / historical-sources
layer is deferred to BIEP-v2 per the
`2026-07-09-remove-brown-ajah-theming-v1` change (R8 was REMOVED 2026-07-09).

#### Scenario: Mathematics BIEP landing page renders

- **WHEN** the user navigates to `/en/subjects/mathematics`
- **THEN** the page renders the BIEP subject card + 5 visualisations +
  the marimo embed + the bilingual toggle
- **AND** the `cc search "Brown Ajah"` finds 0 matches in the rendered
  HTML

#### Scenario: Gaeilge BIEP landing page renders in Irish

- **WHEN** the user navigates to `/ga/subjects/gaeilge`
- **THEN** the page renders in Irish (lang="ga")
- **AND** the BIEP subject card reads "Gaeilge — BIEP v1"
- **AND** the 5×8 mastery matrix uses the Irish KC labels

#### Scenario: About-page mirrors mirror the Clean professional theming

- **WHEN** the user navigates to `/en/about` or `/ga/about`
- **THEN** the public surface tagline reads "Cianfhoghlaim — Coláiste
  na Déisigh"
- **AND** no mythology-themed references appear (no "Aes Sedai", no
  "Brown Ajah", no "Amyrlin Seat", no "WoT", no "Tuatha'an")
- **AND** the 6 BIEP priority subjects are surfaced with EN+GA mirror
  links
