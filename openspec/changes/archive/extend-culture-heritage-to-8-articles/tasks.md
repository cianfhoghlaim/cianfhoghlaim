# Tasks — `extend-culture-heritage-to-8-articles`

5 tasks. Run in order. Validate at the end with `openspec validate extend-culture-heritage-to-8-articles --strict`.

**Status (2026-06-25):** 5/5 tasks complete; awaiting `openspec validate extend-culture-heritage-to-8-articles --strict`.

## 1. ✅ Save 5 second-batch Wikipedia clippings with Obsidian frontmatter

**Files (5 new):**

- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/leath_cuinn_and_leath_moga-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/cian-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/aos_si-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/tuatha_de_danann-wikipedia.md`
- `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/deisi-wikipedia.md`

**Method:** `firecrawl_scrape` with `formats: ["markdown"]` against each Wikipedia URL.

**Frontmatter:** 7-field YAML matching the first-batch precedent (title, source, author, published, created, description, tags).

**Acceptance:** Each file has the 7-field YAML frontmatter; the first 50+ lines of the article body are present; SHA-256 matches the value in the corresponding DLT fixture.

**SHA-256 hashes:**

- `leath_cuinn_and_leath_moga-wikipedia.md`: `572d816536846034be8d9bbcbf2ecb87032ec632cead40c5ff45cd93f28c7653`
- `cian-wikipedia.md`: `0e0981d37dfd4c4cb8ac60b9e79f68f09b47c6586d778712332ee317409bdc20`
- `aos_si-wikipedia.md`: `c9bd3a7713d467cce3bb8b6f29ebe921a8eaa889d818d9b74a2b37a92f619815`
- `tuatha_de_danann-wikipedia.md`: `aabf4cd64276a787c28e7687f8bab12b9aec2bf05fd8b75e782c5b1d166a4ee7`
- `deisi-wikipedia.md`: `3f670c56ca966825979c123ea6b606f242e68a152a2b1331b5b9d4457197d3e6`

## 2. ✅ Save 5 second-batch Wikipedia DLT fixtures (JSON)

**Files (5 new):**

- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_leath_cuinn_and_leath_moga.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_cian.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_aos_si.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_tuatha_de_danann.json`
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_deisi.json`

**Schema per fixture (matches first-batch precedent):**

```json
{
  "title": "...",
  "url": "https://en.wikipedia.org/wiki/...",
  "extract": "<first paragraph>",
  "sha256": "<sha256 of full article body>",
  "retrieved_at": "2026-06-25T00:00:00Z",
  "asset_key": "ie.culture.<slug>",
  "domain": "culture",
  "nation": "ie",
  "kind": "wikipedia_fixture",
  "clipping_path": "cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/<slug>-wikipedia.md"
}
```

**Acceptance:** Each JSON has the 9 fields; resolves via the DLT `wikipedia_fixtures` resource (path-glob of `identity_*.json`); `sha256` is a valid 64-character hex digest matching the clipping file SHA-256.

## 3. ✅ Path-correct 3 existing fixtures (`deacy/` → `lineage/`)

**Files (3 modified):**

- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_ui_liathain.json` — `clipping_path` updated.
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_delbhna.json` — `clipping_path` updated.
- `sruth/oideachais/dlt_sources/official_media/fixtures/identity_eamonn_deacy_park.json` — `clipping_path` updated.

**Reason:** The user moved the clippings from `identity/deacy/references/clippings/` to `identity/lineage/references/clippings/` between the first-batch commit (`4444d468f`) and this change. The 3 fixtures still pointed at the legacy `deacy/` path.

**Acceptance:** All 8 fixtures (3 first-batch + 5 second-batch) have `clipping_path` starting with `cian_mac_an_déisigh_uí_liatháin/identity/lineage/...`.

## 4. ✅ Restructure README personal section (5 subsections → 6 subsections)

**File (1 modified):** `README.md`

**Restructured sections (lines 312–596):**

| § | Title | Change |
|:-:|:--|:--|
| A | On the username — *cianfhoghlaim* | Kept; tightened |
| B | On the family — *Mac an Déisigh Uí Liatháin (Deacy-Lyons)* | Restructured (4 lineages enumerated; Wikipedia citations) |
| C | On the claim — *Rí na Gaillimhe, Rí Chonnachta* | REPLACED — removed "lighthearted", "tongue-in-cheek", "playful homage"; added 8 Wikipedia + 6 PDF citations |
| D | On the joint claim — *Leath Cuinn and the dual-monarchy framework* | **NEW** — 4-bullet joint-claim framework |
| E | On the verified qualifications | Kept verbatim |
| F | On the repository name — *Kings' College Galway* | Restructured — removed "Coláiste na Ríoga" alternative; added "In memory of" dedication to Neil Deacy, Éamonn Deacy, and the Déssi class |

**Byline (line 596) updated:**

> Built by Cian Mac an Déisigh Uí Liatháin (Deacy-Lyons) of the Deacy-Morris-Conroy tribe of Galway — qualified Mathematics & Applied Mathematics teacher (Teaching Council of Ireland), NUI Galway graduate (Applied Statistics, Software Development, Irish Language Studies), dual Irish-British citizen, born a British citizen and obliged by oath of allegiance to King Charles the Third.

**Acceptance:** `grep -n 'Coláiste na Ríoga\|lighthearted\|tongue-in-cheek\|playful homage' README.md` returns no results. Title block (line 1) is `# Kings' College Galway || Coláiste na Déisigh`. Byline (line 596) contains the verbatim oath-of-allegiance phrase.

## 5. ✅ File tracking issue for 2 unread PDFs

**File (1 new):** `openspec/changes/extend-culture-heritage-to-8-articles/tracking_issues/unread-pdfs.md`

**Content:** Lists both unread PDFs with paths, byte sizes, why they matter, and the expected action for a follow-up agent with PDF input support.

**The 2 unread PDFs:**

1. `leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf` — August 1986 *Galway Advertiser* article on the inaugural Streets of Galway 8 km road race.
2. `cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf` — Dual ROI/UK citizenship scan.

**Acceptance:** Tracking issue file exists; both PDFs are listed with paths, sizes, and reasons; expected action for the follow-up agent is documented.

## 6. ✅ Run `openspec validate extend-culture-heritage-to-8-articles --strict`

**Command:**

```bash
openspec validate extend-culture-heritage-to-8-articles --strict
```

**Acceptance:** Exit code 0; all spec deltas have ≥1 Scenario per ADDED/MODIFIED Requirement; no parse errors.