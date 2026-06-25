# Proposal — `extend-culture-heritage-to-8-articles`

## Why

The `ingest-culture-heritage` change (already validated and pushed at `4444d468f`) added the 6th `culture` domain to the cross-domain-registry and shipped 6 Gemini Deep Research PDFs + 3 first-batch Wikipedia clippings (Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park). The first-batch clippings cover the **paternal/maternal lineage anchor** of the Cianfhoghlaim claim, but the broader **joint-claim framework** (Cian = Connacht + Aileach; Charles III = Northern Ireland; jointly = Leath Cuinn) requires the **Tuatha Dé mythological genealogy** and the **Déisi vassal-class history** to be grounded in canonical Wikipedia sources.

This change adds 5 second-batch Wikipedia articles that close the genealogical loop:

1. **Leath Cuinn and Leath Moga** — the constitutional division of Ireland (Conn's Half vs Mogha's Half) that the joint-claim framework rests on.
2. **Cian** — the etymology of the Cianfhoghlaim identifier (*cian* = "enduring one"; father of Lugh Lámhfhada).
3. **Aos Sí** — the post-Milesian fate of the Tuatha Dé Danann (the *sídhe* = burial mounds).
4. **Tuatha Dé Danann** — the supernatural race of pre-Christian Irish mythology (Dian Cecht is Cian's father; Lugh is Cian's son).
5. **Déisi** — the ancient Irish vassal class that the Uí Dhéisigh (Deacy) descend from; colonised Wales alongside the Uí Liatháin (Lyons).

It also restructures the **README personal section** (`README.md` lines 312–474) from 5 lighthearted subsections into 6 citation-anchored subsections with a new "joint claim" framework grounded in Arthur Griffith's Neo-Jacobite Dual Monarchy theory, and notes 2 unread PDFs that must be re-read by a follow-up agent with PDF input support.

## What

### 1. Wikipedia dual-write (5 new clippings + 5 new DLT fixtures)

5 new Wikipedia articles are saved in the same Obsidian-frontmatter + DLT-fixture format as the first batch:

| # | Article | Clipping | Fixture | SHA-256 (truncated) |
|--:|:--|:--|:--|:--|
| 1 | Leath Cuinn and Leath Moga | `clippings/leath_cuinn_and_leath_moga-wikipedia.md` | `identity_leath_cuinn_and_leath_moga.json` | `572d8165…` |
| 2 | Cian | `clippings/cian-wikipedia.md` | `identity_cian.json` | `0e0981d3…` |
| 3 | Aos Sí | `clippings/aos_si-wikipedia.md` | `identity_aos_si.json` | `c9bd3a77…` |
| 4 | Tuatha Dé Danann | `clippings/tuatha_de_danann-wikipedia.md` | `identity_tuatha_de_danann.json` | `aabf4cd6…` |
| 5 | Déisi | `clippings/deisi-wikipedia.md` | `identity_deisi.json` | `3f670c56…` |

The `oideachais/dlt_sources/domains/culture/ie/heritage_source.py:wikipedia_fixtures` resource auto-discovers all `identity_*.json` files in the fixtures directory, so no `sources.yaml` edit is required.

The 3 existing fixtures (`identity_ui_liathain.json`, `identity_delbhna.json`, `identity_eamonn_deacy_park.json`) are updated to point to the canonical `lineage/` path (replacing the legacy `deacy/` path; the clippings themselves were moved from `deacy/` to `lineage/` by the user before this change).

### 2. README personal section restructure (5 subsections → 6 subsections)

The "About the author, the name, and the lineage" section at `README.md` lines 312–474 is restructured:

- **A. On the username — *cianfhoghlaim*** (kept; tightened with the Cian-of-Tuatha-Dé-Danann mythological reference now linked to the new `cian-wikipedia.md` clipping).
- **B. On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)*** (restructured: 4-lineage enumeration Deacy / Lyons / Morris / Conroy, each linked to its Wikipedia citation).
- **C. On the claim — *Rí na Gaillimhe, Rí Chonnachta*** (REPLACED the "lighthearted" / "tongue-in-cheek" / "playful homage" hedging with serious, citation-anchored claim; 8 Wikipedia citations + 6 PDF citations).
- **D. On the joint claim — *Leath Cuinn and the dual-monarchy framework*** (NEW subsection: 4-bullet framework — Cian / Charles III / jointly / Conn Cétchathach; Neo-Jacobite Dual Monarchy model grounded in Arthur Griffith + Māori King Movement).
- **E. On the verified qualifications** (kept verbatim).
- **F. On the repository name — *Kings' College Galway*** (kept; replaced the "Coláiste na Ríoga" alternative with an "In memory of" dedication to Neil Deacy, Éamonn Deacy, and the Déssi class; the *Coláiste na Déisigh* subtitle now carries the deliberate double meaning of genitive-of-Deacy and genitive-of-Déssi).

The byline (line 596) is updated to "Built by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) of the Deacy-Morris-Conroy tribe of Galway — …, born a British citizen and obliged by oath of allegiance to King Charles the Third." The verbatim "Born a British citizen and obliged by oath of allegiance to King Charles the Third" phrasing is preserved per the user's preference.

### 3. Tracking issue for 2 unread PDFs

2 PDFs cannot be read by the current agent's PDF input support and must be re-read by a follow-up agent:

- `leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf` — the August 1986 *Galway Advertiser* article on the inaugural Streets of Galway 8 km road race.
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf` — the dual ROI/UK citizenship scan.

A Forgejo/GitHub tracking issue is filed at `openspec/changes/extend-culture-heritage-to-8-articles/tracking_issues/unread-pdfs.md` so a follow-up agent can incorporate the missing content into the `culture_heritage` Cognee dataset on the next run.

## Impact

- **Surface change**: 5 new clippings + 5 new fixtures + 3 path-corrected fixtures + 1 README restructure + 1 tracking issue file.
- **Behaviour change**: `wikipedia_fixtures` DLT resource auto-discovers 8 identity fixtures (up from 3); `culture_heritage` Cognee dataset will pick up the 5 new articles on next cognify run.
- **Documentation change**: `README.md` personal section is restructured to ground the heritage claim as a serious, citation-anchored constitutional proposal rather than a tongue-in-cheek homage.
- **No new package, no new agent, no new infra.**

## Non-goals

- **No new front-end surface** (no x402, no crypteolas, no Tuatha quest) — this change is documentation + Wikipedia dual-write only.
- **No BAML extraction change** — the existing `culture_extraction.baml:ExtractCultureClaims` function already accepts the 5 new articles via the `wikipedia_fixtures` resource.
- **No Dagster asset change** — the 4 existing `culture_heritage_*` assets + the `low_confidence_review` asset check already cover the 5 new articles on next materialisation.
- **No new cross-dataset edge** — the existing `CROSS_DATASET_EDGES` in `culture_cognify.py` already emit `culture_heritage ↔ oideachais` and `culture_heritage ↔ leabharlann` edges on next cognify run.

## Files touched (15)

### New (10)

- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/{leath_cuinn_and_leath_moga,cian,aos_si,tuatha_de_danann,deisi}-wikipedia.md` (5 new clippings)
- `oideachais/dlt_sources/official_media/fixtures/identity_{leath_cuinn_and_leath_moga,cian,aos_si,tuatha_de_danann,deisi}.json` (5 new DLT fixtures)
- `openspec/changes/extend-culture-heritage-to-8-articles/tracking_issues/unread-pdfs.md` (1 tracking issue file)

### Modified (5)

- `oideachais/dlt_sources/official_media/fixtures/identity_ui_liathain.json` (path fix: `deacy/` → `lineage/`)
- `oideachais/dlt_sources/official_media/fixtures/identity_delbhna.json` (path fix)
- `oideachais/dlt_sources/official_media/fixtures/identity_eamonn_deacy_park.json` (path fix)
- `README.md` (restructure lines 312–474, update byline on line 596)
- `openspec/specs/cross-domain-registry/spec.md` (1 MODIFIED Requirement — fixture count `3` → `8`)

## Acceptance

- `openspec validate extend-culture-heritage-to-8-articles --strict` exits 0.
- 8 `identity_*.json` fixtures in `oideachais/dlt_sources/official_media/fixtures/`; 3 path-corrected to `lineage/`; 5 new for the second batch.
- 8 Wikipedia clippings in `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` (3 first-batch + 5 second-batch).
- `README.md` has 6 subsections under "About the author, the name, and the lineage"; no occurrence of "lighthearted", "tongue-in-cheek", "playful homage", or "Coláiste na Ríoga".
- Tracking issue file `tracking_issues/unread-pdfs.md` lists both unread PDFs with paths and reasons.

## Cross-references

- Originating change: `openspec/changes/ingest-culture-heritage/proposal.md` (already implemented and committed at `4444d468f`).
- Canonical spec: `openspec/specs/cross-domain-registry/spec.md`.
- Skills: `.agents/skills/celtic-asset-generation/SKILL.md`, `.agents/skills/oideachais-leabharlann/SKILL.md`, `.agents/skills/oideachais-cocoindex-v1/SKILL.md`.