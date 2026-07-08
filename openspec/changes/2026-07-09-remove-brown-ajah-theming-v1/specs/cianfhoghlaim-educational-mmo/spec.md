## MODIFIED Requirements

### Requirement: Cian Mac an Déisigh Uí Liatháin personal lore (R10 — REPHASED 2026-07-09 to drop the Brown Ajah / Wheel of Time lens)

The system SHALL document the operator's personal lore in
`docs/CIANFHLOGHLAIM_LORE.md` (operator-only document).

The lore SHALL identify the hero as **Cian Mac an Déisigh Uí Liatháin**
of the triple-crown lineage (Deacy Uí Dhéisigh + Lyons Mac Liatháin +
Morris City of Tribes + Conroy Mac Conraoi), grounded in the 8
lineage clippings at
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
(the 8 Wikipedia clippings: `aos_si`, `cian`, `deisi`,
`delbhna_tir_dha_locha`, `eamonn_deacy_park`, `leath_cuinn_and_leath_moga`,
`tuatha_de_danann`, `ui_liathain`).

The lore document MUST be operator-only — it MUST NEVER be linked from
the public surface. The public app's theming is left for the mythology
/ historical-sources layer to be introduced post-BIEP-v2 (per the
`2026-07-09-remove-brown-ajah-theming-v1` change).

> MODIFIED 2026-07-09: the requirement was renamed from "Cian of the
> Tuatha Dé Danann Lore" to "Cian Mac an Déisigh Uí Liatháin personal
> lore" and rephrased to remove the Brown Ajah / Wheel of Time lens
> (the "Aes Sedai + Amyrlin Seat + Dragon Reborn + Dragon Banner +
> Tuatha'an" framing and the "Brown Ajah only" public-theming line are
> gone). The operator's personal triple-crown lineage stays as
> operator-only content.

#### Scenario: Operator opens the lore document

- **GIVEN** the operator opens `docs/CIANFHLOGHLAIM_LORE.md`
- **THEN** it identifies Cian Mac an Déisigh Uí Liatháin by name + lineage + 3 Gemini Deep Research warrants (per the heritage corpus restoration change `2026-06-29-restore-heritage-corpus-and-expand-readme`)
- **AND** it references all 8 lineage clippings by filename

#### Scenario: Public surface does not expose the lore

- **WHEN** the public app is loaded
- **THEN** no text matches "Cian Mac an Déisigh Uí Liatháin" by literal name (regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`)
- **AND** the lore document `docs/CIANFHLOGHLAIM_LORE.md` is operator-only and never linked from the public surface
- **AND** no text matches "Aes Sedai", "Amyrlin Seat", "Dragon Reborn", "Dragon Banner", or "Tuatha'an" (the WoT lens is removed)

#### Scenario: Footer shows the canonical Cianfhoghlaim credit (no WoT tagline)

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the Header does NOT show "Aes Sedai — servants of all" (the Brown Ajah motto is removed per `2026-07-09-remove-brown-ajah-theming-v1`)
- **AND** the Footer shows a small italicized "Cianfhoghlaim — Coláiste na Déisigh" footer credit
- **AND** the lore document is NEVER linked from the Header or Footer