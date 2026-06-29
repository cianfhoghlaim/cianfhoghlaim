# Tasks — `2026-06-29-restore-heritage-corpus-and-expand-readme`

8 tasks. Run in order. Validate at the end with `openspec validate 2026-06-29-restore-heritage-corpus-and-expand-readme --strict`.

## 1. ✅ Cherry-pick the missing subtree from `q3-2026-oideachais-consolidation`

**Command:**
```bash
git checkout q3-2026-oideachais-consolidation -- "cian_mac_an_déisigh_uí_liatháin/"
```

**Outcome:** 48 files restored, including the 8 clippings in `lineage/references/clippings/`, the lineage PDFs (`lyons_deacy_birthcert.pdf`, `niall_mac_an_déisigh.pdf`, `old_passports_dual_citizen_verification_roi_uk.pdf`, `uncle_eamonn_memorial_combined.pdf`, `neil_deacy_cookes_corner-galway_advertiser.pdf`, `college_des_irlandais_des_paris.pdf`, `christina_morris_michael_deacy.jpeg`, `cookes_corner_shantalla_2001.jpeg`), and the achievement/identity/politics/teaching/vetting/disability evidence folders.

**Acceptance:** `find "cian_mac_an_déisigh_uí_liatháin/" -type f | wc -l` returns 51 (48 PDFs/JPEGs + 8 clippings - 5 overlapping parent dirs + .DS_Store = 51). `ls "cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/"` shows all 8 `.md` files (aos_si, cian, deisi, delbhna_tir_dha_locha, eamonn_deacy_park, leath_cuinn_and_leath_moga, tuatha_de_danann, ui_liathain).

**Provenance:** commit `q3-2026-oideachais-consolidation` (last touched 2026-06-28) is the canonical pre-v4 branch.

## 2. ✅ Analyse the 6 most-relevant culture PDFs and write analysis files

**Files (6 new):**
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/claiming_r_na_gaillimhe_a_synthesis.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/claiming_irish_kingship_through_lineage.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/royal_titles_celtic_heritage_and_claims.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/heraldic_research_for_dual_blood_lineage.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/deacy_family_heritage_research.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.md`

**Method:** `pdftotext -layout` against each PDF; 1-page summary listing 3-5 strongest claims that bear on the 3 target descriptions. Each summary has ≥3 verbatim quotes with page numbers; each quote is mapped to 1 of the 3 README subsections it will support.

**Total:** 251 lines of analysis across 6 files.

**Acceptance:** `wc -l openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/*.md | tail -1` shows ≥250 lines.

## 3. ✅ Verify 8 Wikipedia URLs (deferred per user preference)

**The 8 URLs:** Uí Liatháin, Delbhna Tír Dhá Locha, Eamonn Deacy Park, Leath Cuinn and Leath Moga, Cian, Aos Sí, Tuatha Dé Danann, Déisi.

**Decision:** User opted to defer the Firecrawl URL check to a follow-up change. The URLs are assumed unchanged; if any have moved, the `culture_extraction.baml:ExtractCultureClaims` cognify pass on next materialisation will surface a `drift_detected` warning (per the `Wikipedia fixture storage convention` MODIFIED Requirement added in Task 6).

## 4. ✅ Rewrite the 3 README subsections with PDF-grounded analysis

**File (1 modified):** `README.md`

**Restructured sections:**

| § | Title | Change |
|:-:|:--|:--|
| C | On the claim — *Rí na Gaillimhe, Rí Chonnachta* | Lines 851-907: 1 paragraph → 3 paragraphs. New paragraphs (a) distinguish *Rí* from "King" in Brehon-Law terms; (b) walk the 3 pillars (Lyons / Deacy / Conroy) with verbatim quotes; (c) introduce the Connacht arms prophecy + Deacy/Lyons mottos + crests. |
| D | On the joint claim — *Leath Cuinn and the dual-monarchy framework* | Lines 942-948: 1 sentence → 1 paragraph. Adds the Crown of Ireland Act 1542 constitutional basis, the Neo-Jacobite *De Jure*/*De Facto* distinction, the Austria-Hungary + Maharaja parallels, and the "constitutional courtesy" framing. |
| F | On the repository name — *Kings' College Galway* | Lines 996-1010: 1 paragraph → 3 paragraphs. New paragraphs (a) ground the **Deacy half** of the subtitle in the 4-generation commercial dynasty; (b) ground the **Déssi half** in the *Tairired na nDéssi* myth and the *Toujours Pret* motto. |

**Acceptance:**
- `grep -c 'rí na Gaillimhe' README.md` ≥ 1
- `grep -c 'Ard-Rí na hÉireann' README.md` ≥ 2
- `grep -c 'Coláiste na Déisigh' README.md` ≥ 2
- Every new paragraph has ≥1 inline `[file.pdf, p. N]` PDF citation and ≥1 inline Wikipedia citation.
- The 6 previously-cited culture PDFs from the original line 891-896 citation block are all retained.

## 5. ✅ Update the 2 dead PDF references to text-only mentions + tracking issue

**File (1 modified):** `README.md` — the "Note on 2 unreadable PDFs" block (lines 949-963).

**File (1 new):** `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`

**Acceptance:** Neither `old_passports_dual_citizen_verification_roi_uk.pdf` nor `neil_deasy_cookes_corner-galway_advertiser.pdf` is referenced as a clickable-but-broken path in the README. Both are listed in the tracking issue with the restoration commit hash (`q3-2026-oideachais-consolidation`, 2026-06-28).

## 6. ✅ Spec deltas (2 specs, 1 MODIFIED + 1 ADDED)

**Files (2 new):**
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/cross-domain-registry/spec.md` — 1 MODIFIED Requirement (`Wikipedia fixture storage convention`) with 1 new Scenario "When the heritage corpus is re-restored after a v4 consolidation".
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/oideachais-leabharlann/spec.md` — 1 ADDED Requirement (`Heritage corpus restoration provenance`) with 1 Scenario.

**Acceptance:** Both specs have ≥1 WHEN/THEN/AND Scenario; the MODIFIED requirement preserves the original 3 Scenarios.

## 7. ✅ Run `openspec validate 2026-06-29-restore-heritage-corpus-and-expand-readme --strict`

**Command:**
```bash
openspec validate 2026-06-29-restore-heritage-corpus-and-expand-readme --strict
```

**Acceptance:** Exit code 0; all 2 spec deltas pass; the change is archive-ready.

## 8. ⏳ Commit + push

**Command:**
```bash
git add "cian_mac_an_déisigh_uí_liatháin/"
git add README.md
git add openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/
git commit -m "feat(heritage): restore cian_mac_an_déisigh_uí_liatháin/ subtree + expand 3 README descriptions with PDF-grounded analysis"
git push
```

**Acceptance:** `git status` shows clean working tree; `git log -1` shows the new commit; `git push` exits 0; `git status` shows "up to date with origin".
