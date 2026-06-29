# Proposal — `2026-06-29-restore-heritage-corpus-and-expand-readme`

## Why

After the v4 consolidation (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`, the `q3-2026-oideachais-consolidation` worktree), the entire `cian_mac_an_déisigh_uí_liatháin/` subtree — 48 files: 8 Wikipedia `.md` clippings, 3 lineage PDFs, 4 identity-deacy PDFs, 1 disability PDF, 6 politics PDFs, 10 teaching PDFs, 1 BCS scholarship, 4 vetting PDFs, 9 achievement PDFs — was dropped from `main` (last touched 2026-06-25 on `q3-2026-oideachais-consolidation`; first absent on `main` from HEAD `132892a42` on 2026-06-29). The 8 DLT fixtures survived the v4 move and now live at `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/`.

The `README.md` personal-heritage section (lines 851-1018) — the project's de-facto "Wikipedia page" — is now broken in three ways:

1. The citation block at line 879 references
   `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
   (the 8 Wikipedia `.md` clippings) but the directory was dropped from
   `main` along with the rest of the subtree.
2. The "Note on 2 unreadable PDFs" block at line 900 references
   `leabharlann/gemini_deep_research/culture/neil_deasy_cookes_corner-galway_advertiser.pdf`
   (an August 1986 *Galway Advertiser* scan) which was *never committed
   to git* and remains missing.
3. The 3 subsection descriptions (Rí na Gaillimhe, Ard-Rí na hÉireann,
   Coláiste na Déisigh) are too short to ground the constitutional
   claim in the available Gemini Deep Research evidence.

This change restores the 48-file subtree from `q3-2026-oideachais-consolidation` (the canonical pre-v4 branch), updates the 2 dead PDF references in the README, and rewrites the 3 subsections with PDF-grounded analysis drawn from the 6 most-relevant culture PDFs.

## What

### 1. Cherry-pick the missing subtree from `q3-2026-oideachais-consolidation`

```bash
git checkout q3-2026-oideachais-consolidation -- "cian_mac_an_déisigh_uí_liatháin/"
```

48 files restored. The 8 Wikipedia clippings return to `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`, the lineage PDFs return to `cian_mac_an_déisigh_uí_liatháin/identity/lineage/`, and the achievement/disability/politics/teaching/vetting evidence folders return to their canonical locations.

### 2. Analyse the 6 most-relevant culture PDFs and write analysis files

6 of the 31 PDFs in `leabharlann/gemini_deep_research/culture/` are directly relevant to the 3 target descriptions. The 6 analyses live at `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/<pdf-slug>.md`:

- `claiming_r_na_gaillimhe_a_synthesis.md` (15 pages) — primary source for §C
- `claiming_irish_kingship_through_lineage.md` (13 pages) — primary source for the Ard-Rí paragraph
- `royal_titles_celtic_heritage_and_claims.md` (13 pages) — secondary source for the Ard-Rí paragraph (Aileach + Pan-Celtic strategy)
- `heraldic_research_for_dual_blood_lineage.md` (14 pages) — heraldic-visual backing for §C
- `deacy_family_heritage_research.md` (9 pages) — primary source for the Deacy half of §F
- `the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.md` (12 pages) — secondary source for §F (socio-economic + athletic + diaspora + Kenny's Bookshop)

Each analysis file contains 3-5 verbatim quotes with page numbers, mapped to one of the 3 README subsections it will support.

### 3. Verify the 8 Wikipedia URLs (deferred to follow-up)

The 8 Wikipedia URLs in the citation block at `README.md` lines 883-890 (Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn and Leath Moga, Cian, Aos Sí, Tuatha Dé Danann, Déisi) are not re-verified in this change. The user opted to defer the Firecrawl URL check to a follow-up change; the citations are assumed to still be 200 and the canonical slugs are unchanged. If any URL has moved between 2026-06-25 (when the clippings were last taken) and 2026-06-29 (the date of this change), the drift will be caught by the `culture_extraction.baml:ExtractCultureClaims` cognify pass on the next materialisation.

### 4. Rewrite the 3 README subsections with PDF-grounded analysis

**§C. On the claim — *Rí na Gaillimhe, Rí Chonnachta*** (lines 851-907, ~120 words → ~520 words): the existing 1-paragraph Triple Crown intro is now followed by 2 new paragraphs that (a) distinguish *Rí na Gaillimhe* from "King of Galway" in Brehon-Law terms, citing `claiming_r_na_gaillimhe_a_synthesis.pdf` p. 1-2; (b) walk the three pillars (Uí Liatháin maternal-line to Tara, Uí Dhéisigh Eamonn Deacy Park inauguration, Mac Conraoi Quay-Street maritime trade) with verbatim quotes from `claiming_irish_kingship_through_lineage.pdf` p. 5-7 and `deacy_family_heritage_research.pdf` p. 2; (c) introduce the Connacht arms prophecy (Eagle = Uí Liatháin, Arm = Uí Dhéisigh) with the blazon from `heraldic_research_for_dual_blood_lineage.pdf` p. 2-3, the Deacy *Toujours Pret* and dagger crest (p. 4), and the Lyons *Noli Irritare Leones* and lion crest (p. 6).

**§D. The Ard-Rí na hÉireann sentence** (line 942-948, 1 sentence → 1 paragraph, ~200 words): the 1-sentence mention of the *Ard-Rí* suspension is now expanded with the constitutional basis (Crown of Ireland Act 1542, the 1800 Act of Union, the "ghostly legal existence" of the Crown of Ireland), the Neo-Jacobite *De Jure* / *De Facto* distinction, the Austria-Hungary and Maharaja parallels, and the framing of the suspension as "constitutional courtesy parallel to King Charles III's continued *Rí Uladh* claim". Cites `claiming_irish_kingship_through_lineage.pdf` p. 4, 7 and `royal_titles_celtic_heritage_and_claims.pdf` p. 1, 6.

**§F. The *Coláiste na Déisigh* subtitle** (lines 996-1010, ~150 words → ~590 words): the existing "double meaning" paragraph is kept verbatim and is now followed by 2 new paragraphs that (a) ground the **Deacy half** of the subtitle in the 4-generation commercial dynasty (John Conroy → Polly Conroy + George Deacy → Miko Deacy → Neil Deacy) with verbatim quotes from `deacy_family_heritage_research.pdf` p. 2-3 and the topography PDF p. 3-4, including the Cookeʼs Corner 1986 opening, the Peggy Deacy bilingual strategy ("Niall Mac an Déisigh éisc úra agus glasraí"), and the Kenny's Bookshop extension under Paul Deacy; (b) ground the **Déssi half** of the subtitle in the *Tairired na nDéssi* foundation myth, the *Déisi Tuisceart* → Dál gCais → Brian Boru connection, and the *Toujours Pret* motto as a continuation of Déisi "conditional loyalty" — citing `claiming_r_na_gaillimhe_a_synthesis.pdf` p. 5-6 and `royal_titles_celtic_heritage_and_claims.pdf` p. 4.

### 5. Update the 2 dead PDF references + tracking issue

The "Note on 2 unreadable PDFs" block at `README.md` lines 949-963 is updated:

- The `cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf` link is now a working link to the restored file (cherry-picked from `q3-2026-oideachais-consolidation`).
- The `leabharlann/gemini_deep_research/culture/neil_deasy_cookes_corner-galway_advertiser.pdf` reference is preserved as a plain-text path; the file was never committed and remains missing. A new working link to the restored substitute at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf` is added.

A new tracking issue is filed at `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md` that documents both paths, the restoration provenance, the byte sizes, and the next-step action for a follow-up agent with PDF input support.

### 6. Spec deltas (2 specs)

**`openspec/specs/cross-domain-registry/spec.md`** — 1 MODIFIED Requirement (`Wikipedia fixture storage convention`): a new Scenario "When the heritage corpus is re-restored after a v4 consolidation" is added that asserts the drift-detector invariant (clipping SHA-256 === fixture SHA-256) holds for the restored corpus, and that the restoration MUST come from the canonical pre-v4 branch (`q3-2026-oideachais-consolidation`).

**`openspec/specs/oideachais-leabharlann/spec.md`** — 1 ADDED Requirement (`Heritage corpus restoration provenance`): a new Scenario that codifies the 4-step restoration contract (cherry-pick from `q3-2026-oideachais-consolidation`; never merge; openspec change required; cross-domain-registry drift-detector invariant asserted).

## Impact

- **Surface change:** 48 files restored, 3 README subsections rewritten (~660 words added), 2 dead PDF references fixed, 1 tracking issue filed, 2 spec deltas added.
- **Behaviour change:** The `culture_heritage` Cognee dataset will pick up the restored 8 Wikipedia clippings + the 6 lineage PDFs on the next cognify run.
- **Documentation change:** The 3 target descriptions are now grounded in 6 PDF citations + 8 Wikipedia citations, replacing the previous 1-paragraph + 6-citation format.
- **No new package, no new agent, no new infra.**
- **No new BAML extraction change** — the existing `culture_extraction.baml:ExtractCultureClaims` function already accepts the restored articles.
- **No new Dagster asset change** — the existing 4 `culture_heritage_*` assets + the `low_confidence_review` asset check already cover the restored clippings on next materialisation.
- **No merge from `q3-2026-oideachais-consolidation` into `main`** — the v4-consolidation history is intentionally separate; only the `cian_mac_an_déisigh_uí_liatháin/` subtree is restored.

## Non-goals

- **No new Wikipedia articles** beyond the existing 8.
- **No new DLT source** — the fixtures already exist; we are not adding more.
- **No new front-end surface** — no TanStack route, no Convex function, no marimo notebook.
- **No Firecrawl URL verification** — the 8 Wikipedia URLs are assumed unchanged; a follow-up change will verify them.
- **No PDF re-extraction for the 2 unread PDFs** — `old_passports_dual_citizen_verification_roi_uk.pdf` is now restored but the previous agent's PDF tooling could not extract its text; a follow-up agent with PDF input support will incorporate the scan.
- **No branch management beyond the cherry-pick** — we do not merge `q3-2026-oideachais-consolidation` into `main`.

## Files touched

### New (12)

- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/proposal.md` (this file)
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tasks.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/cross-domain-registry/spec.md` (1 MODIFIED Requirement + 1 new Scenario)
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/oideachais-leabharlann/spec.md` (1 ADDED Requirement)
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`
- 6× `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/<pdf-slug>.md`

### Restored (48)

- The full `cian_mac_an_déisigh_uí_liatháin/` subtree from `q3-2026-oideachais-consolidation`: 8 clippings + 8 lineage PDFs/JPEGs + 4 identity-deacy + 1 disability + 6 politics + 10 teaching + 1 BCS + 4 vetting + 9 achievement = 51 files including the 3 .DS_Store markers.

### Modified (1)

- `README.md` — 3 subsections rewritten (lines 851-907, 942-948, 996-1010); "Note on 2 unreadable PDFs" block updated (lines 949-963).

## Acceptance

- `openspec validate 2026-06-29-restore-heritage-corpus-and-expand-readme --strict` exits 0.
- 48 files restored under `cian_mac_an_déisigh_uí_liatháin/` (8 clippings + 3 lineage PDFs + 4 identity-deacy + 1 disability + 6 politics + 10 teaching + 1 BCS + 4 vetting + 9 achievement).
- 8 Wikipedia clippings present at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`.
- `README.md` §C "On the claim" now contains 3 paragraphs (intro + 2 new), each with ≥1 PDF citation and ≥1 Wikipedia citation.
- `README.md` §D "On the joint claim" contains an expanded Ard-Rí paragraph with ≥2 PDF citations.
- `README.md` §F "On the repository name" now contains 5 paragraphs (intro + 4 new), with the "Coláiste na Déisigh" subsection expanded to ~590 words across 3 paragraphs (intro + Deacy + Déssi).
- The 2 dead PDF references in lines 949-963 are updated: `old_passports_dual_citizen_verification_roi_uk.pdf` is a working link; `neil_deasy_cookes_corner-galway_advertiser.pdf` carries a plain-text path note + a working link to the restored substitute.
- The 2 spec deltas pass `openspec validate --strict`.

## Cross-references

- Originating changes: `openspec/changes/extend-culture-heritage-to-8-articles/` (the parent change that added the 8 clippings, last touched 2026-06-25) and `openspec/changes/ingest-culture-heritage/` (the parent change that established the `culture` domain).
- Originating branch: `q3-2026-oideachais-consolidation` (last touched 2026-06-28).
- Canonical specs: `openspec/specs/cross-domain-registry/spec.md` (the `Wikipedia fixture storage convention` Requirement, MODIFIED by this change) and `openspec/specs/oideachais-leabharlann/spec.md` (the `Heritage corpus restoration provenance` Requirement, ADDED by this change).
- Tracking issue (this change): `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`.
- Tracking issue (previous): `openspec/changes/extend-culture-heritage-to-8-articles/tracking_issues/unread-pdfs.md` (superseded for the 2 specific paths above).
- Skills: `.agents/skills/oideachais-leabharlann/SKILL.md` (the 4 dlt sources + 3 v1 CocoIndex Apps + 7 assets pattern that the restored clippings feed), `.agents/skills/oideachais-cocoindex-v1/SKILL.md` (the v1 CocoIndex App pattern for the `culture_heritage_embedding` App that the restored clippings embed).
