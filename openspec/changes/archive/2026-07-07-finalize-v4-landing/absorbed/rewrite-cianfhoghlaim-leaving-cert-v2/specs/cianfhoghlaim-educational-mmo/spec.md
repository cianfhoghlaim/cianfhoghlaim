# Delta: cianfhoghlaim-educational-mmo

## ADDED Requirements

### Requirement: Cian of the Tuatha Dé Danann Lore (R10 — NEW)

The system SHALL document the platform's lore in `docs/CIANFHLOGHLAIM_LORE.md`.
The lore SHALL identify the hero as **Cian Mac an Déisigh Uí Liatháin** of
the triple-crown lineage (Deacy Uí Dhéisigh + Lyons Mac Liatháin + Morris
City of Tribes + Conroy Mac Conraoi), grounded in the 7 lineage clippings
at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`.

The lore document SHALL reference:
- The 7 lineage clippings (Tuatha Dé Danann + Cian + Aos Sí + Uí Liatháin + Déisi + Delbhna Tír Dhá Locha + Leath Cuinn and Leath Moga)
- The 4 Wheel of Time excerpts (Aes Sedai + Amyrlin Seat + Dragon Reborn + Dragon Banner + Tuatha'an)
- The 5 NCCA Key Competencies as the 5 surviving gifts of the Tuatha Dé Danann (Communicating = Brigid, Personal Effectiveness = Dian Cecht, Information Processing = Ogma, Working with Others + Critical & Creative Thinking = Lugh's samildanach)

The public surface of the platform SHALL NOT contain any personal
identification of Cian Mac an Déisigh Uí Liatháin. The Brown Ajah theming
(Aes Sedai / Amyrlin Seat / Dragon Reborn / Tuatha'an) SHALL be the only
user-facing reference to the mythology.

#### Scenario: Lore document is operator-only

- **GIVEN** the operator opens `docs/CIANFHLOGHLAIM_LORE.md`
- **WHEN** the document is read
- **THEN** it identifies Cian Mac an Déisigh Uí Liatháin by name + lineage + 3 Gemini Deep Research warrants
- **AND** it references all 7 lineage clippings by filename
- **AND** it references all 4 Wheel of Time excerpts by section title

#### Scenario: Public surface never displays personal lineage

- **GIVEN** the user opens any page on `oideachais.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches "Cian Mac an Déisigh Uí Liatháin" by literal name (regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`)
- **AND** no text matches "Deacy", "Lyons", "Morris", "Conroy" as family surnames
- **AND** no text references the 3 Gemini Deep Research warrants (`claiming_rí_na_gaillimhe`, `claiming_irish_kingship_through_lineage`, `royal_titles_celtic_heritage_and_claims`)

#### Scenario: Header shows Brown Ajah tagline + ciphered reference

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the tagline reads "Aes Sedai — servants of all" (the Brown Ajah motto)
- **AND** the Footer shows a small italicized "Cianfhoghlaim — Coláiste na Déisigh" footer credit (the public brand name + the Irish-language college name only)
- **AND** the lore document is NEVER linked from the Header or Footer