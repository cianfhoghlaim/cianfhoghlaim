# Tracking issue — unreadable / missing PDFs in the culture-heritage corpus

**Filed by:** `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/`
**Date:** 2026-06-29
**Status:** 1 of 2 issues resolved by Task 1 of this change; 1 still open.

## Issue 1 — Dual ROI/UK citizenship scan (RESOLVED)

**Path (now restored):**
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`

**Size:** 11,483,548 bytes (≈ 11.0 MB)
**Cherry-picked from:** `q3-2026-oideachais-conservation` branch, commit `67797aa3f` (2026-06-25)

**Resolution:** The file was present in the pre-v4-consolidation git
history but was dropped from `main` during the
`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` work. Task 1 of
this change restored the entire `cian_mac_an_déisigh_uí_liatháin/`
subtree via `git checkout q3-2026-oideachais-consolidation -- …`. The
file is now at the path above and is included in the
`culture_heritage` Cognee dataset on the next cognify run.

**Why it matters:** This scan is the primary evidence for the
"dual Irish-British citizen" claim in the byline on line 596 of
`README.md` and the "Dual Nationality" / Neo-Jacobite Federalism
argument developed in
`leabharlann/gemini_deep_research/culture/claiming_irish_kingship_through_lineage.pdf`.

**Next-step action:** A follow-up agent with PDF input support should
extract the text of the scan and incorporate any visible biographical
detail (e.g. date-of-issue, place-of-issue, MRZ data) into the
`ExtractCultureClaims` BAML extraction function at
`cianfhoghlaim/core/baml/_oideachais_src/culture_extraction.baml`.

## Issue 2 — August 1986 *Galway Advertiser* article (PARTIALLY RESOLVED)

**Originally referenced path (still missing on disk):**
`./leabharlann/gemini_deep_research/culture/neil_deacy_cookes_corner-galway_advertiser.pdf`

**Substitute path (now restored):**
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/neil_deacy_cookes_corner-galway_advertiser.pdf`

**Size of restored file:** (see `ls -la` after the cherry-pick)

**Resolution:** The `leabharlann/gemini_deep_research/culture/` copy of
the file was *never committed to git* (the `leabharlann/` subtree is
`.gitignore`-excluded per the v4 consolidation). A near-identical
copy, however, was committed at the `cian_mac_an_déisigh_uí_liatháin/identity/lineage/`
path in commit `67797aa3f` and is now restored. The README citation
block has been updated to point future agents at the
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/` path as the
canonical location.

**Why it matters:** This is the August 1986 *Galway Advertiser*
article that introduced the 8-km Streets of Galway road race and
publicised Neil Deacy's Cookeʼs Corner shop opening. It is the
primary-period evidence for the "two events of 1986" framing in
`leabharlann/gemini_deep_research/culture/the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.pdf`
(p. 5).

**Next-step action:** A follow-up agent with PDF input support
should extract the text of the restored file and add a Cognee
cross-dataset edge from `culture_heritage` to `leabharlann_inbox`
(the personal archive) so that future queries can find the article
from both sides. The `.gitignore` exclusion of the
`leabharlann/gemini_deep_research/` subtree should be reviewed at the
next `leabharlann` change to determine whether the canonical home
should be `leabharlann/` (after de-gitignoring) or
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/` (as the current
arrangement).

## Cross-references

- Originating openspec change: `openspec/changes/extend-culture-heritage-to-8-articles/tracking_issues/unread-pdfs.md` (the previous tracking issue, which this file supersedes for the 2 specific paths above).
- README updates: `README.md` lines 949-963 (the "Note on 2 unreadable PDFs" block, updated in this change).
- Restoration provenance: git commit `q3-2026-oideachais-consolidation` (last touched 2026-06-28) → restore via `git checkout q3-2026-oideachais-consolidation -- "cian_mac_an_déisigh_uí_liatháin/"`.
- Canonical spec: `openspec/specs/cross-domain-registry/spec.md` (the `Wikipedia fixture storage convention` Requirement, MODIFIED by this change to add a restoration-provenance Scenario).
