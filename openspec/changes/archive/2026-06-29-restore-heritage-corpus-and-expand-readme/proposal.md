# Proposal — `2026-06-29-restore-heritage-corpus-and-expand-readme`

## Why

After the v4 consolidation (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`, the `q3-2026-oideachais-consolidation` worktree), the entire `cian_mac_an_déisigh_uí_liatháin/` subtree — 48 files: 8 Wikipedia `.md` clippings, 3 lineage PDFs, 4 identity-deacy PDFs, 1 disability PDF, 6 politics PDFs, 10 teaching PDFs, 1 BCS scholarship, 4 vetting PDFs, 9 achievement PDFs — was dropped from `main` (last touched 2026-06-25 on `q3-2026-oideachais-consolidation`; first absent on `main` from HEAD `132892a42` on 2026-06-29). The 8 DLT fixtures survived the v4 move and now live at `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/fixtures/`.

The `README.md` personal-heritage section was broken in three ways:

1. The citation block references
   `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`
   (the 8 Wikipedia `.md` clippings) but the directory was dropped from
   `main` along with the rest of the subtree.
2. The "Note on 2 unreadable PDFs" block references
   `leabharlann/gemini_deep_research/culture/neil_deasy_cookes_corner-galway_advertiser.pdf`
   (an August 1986 *Galway Advertiser* scan) which was *never committed
   to git* and remains missing.
3. The 3 subsection descriptions (Rí na Gaillimhe, Ard-Rí na hÉireann,
   Coláiste na Déisigh) are too short to ground the constitutional
   claim in the available Gemini Deep Research evidence.

This change is delivered in **5 versions** of the README on a
single openspec change:

- **v1** (commit `7a1243485`) — restore the 48-file subtree + first
  expansion of the 3 personal-heritage subsections (Rí na Gaillimhe,
  Ard-Rí, Coláiste na Déisigh) with PDF-grounded analysis.
- **v2** (commit `f3affbde2`) — second rewrite of the 3 personal-
  heritage subsections adding the Ring of Connacht, the 4-province
  footprint, the Aileach / Connacht landlock argument, the 30-year
  roadmap to 2060, the Dublin / Leinster consolidation warning, and
  the §G educational-mission / §H constitutional-warning sub-sections.
- **v3** (commit `6fee5eb6a`) — full README rewrite that **drops the
  Dublin / Leinster anti-consolidation framing** in favour of a
  *cultural-stewardship* framing, adds the new `## The cianfhoghlaim
  plan throughout the British Isles` top-level section (the East
  Belfast hub + the inter-Celtic acquisition pathway + the
  Isle-of-Man Celtic AI Institute), adds the new `## The pipelines —
  what cianfhoghlaim can do` top-level section (the 5-stage
  per-pipeline walkthrough), adds the new `## 5 cookbook recipes`
  top-level section (5 worked end-to-end examples), expands the
  `### ./bonneagar/` and `### ./leabharlann/` sister-repo
  subsections into full sub-section treatment (the bonneagar
  directory tree + the leabharlann 6-subdir layout), and reduces
  the "About the author" section from 8 to 6 sub-sections that are
  fully rewritten. The v3 also generalises the §E qualifications
  (no longer cryptography-foregrounded) and updates the byline
  to add the new linguistic + AI credentials.
- **v3.1** (commit `3cb8acbfe`) — polish the v3 §21c-§21f citations
  to direct-link the 4 GitHub PDFs (instead of the local
  `leabharlann/...` paths), add the "Neil Mac an Déisigh" name
  origin explanation, fix the "City of Tribes" link
  (`Galway` → `Tribes_of_Galway`), and remove the "In memory of"
  line + the "Note on 2 unreadable PDFs" block.
- **v4** (commit `55413dbdc`) — replace the §21c-§21f + Citations + 2
  unreadable PDFs note + "Irish-English bilingual title on line 1"
  line (lines 1366-1800) with a single section that **(a)**
  explains the 6 leabharlann subdirs and the purpose of each, and
  **(b)** references directly the content and subreferences of the
  8 specific Gemini Deep Research PDFs in
  `leabharlann/gemini_deep_research/culture/` as the purpose of
  Cian Mac an Déisigh Uí Liatháin and cianfhoghlaim. The v4 also
  **improves the start of the README** by re-emphasising the
  bilingual title + opening the TL;DR with a direct link to the
  leabharlann `gemini_deep_research/culture/` archive.
- **v5** (this commit) — replace the v4 "Purpose" section's
  overview + 6-subdir table + 8 per-PDF sub-sections + how-to-access
  + closing note (README lines 1382-1757, ~376 lines) with a **single
  coherent narrative** that merges the actual content of the 8 PDFs
  into a unified "the Triple Crown, the Saoí standard, and the
  21st-century cianfhoghlaim" story. The new narrative is structured
  as 10 thematic sub-sections: (1) the Triple Crown of the Corrib;
  (2) the heraldic prophecy; (3) the Brehon Law saoí — the
  Scholar-Prince; (4) the sacred topography of Shantalla; (5) the
  mythological warrant — Cian mac Cáinte and the Aos Sídhe; (6) the
  dual-monarchy synthesis; (7) the 2060 geostrategic horizon; (8) the
  cianfhoghlaim educational project — the Saoí standard
  operationalised (with the Four Treasures of the Tuatha Dé Danann,
  the Wheel of the Year, the Scoilverse, the pedagogical uncanny
  valley, the Celtic design language); (9) the cianfhoghlaim as a
  digital ark for the Celtic languages; (10) the cianfhoghlaim
  monorepo as the operational form. The v5 also references the
  cianfhoghlaim educational themes from the `ui-components` skill
  (the Celtic design language, the dnd-kit exam builder pattern,
  the CopilotKit + AG-UI protocol) and the `tuatha-mmo` skill
  (the Saoí standard, the Four Treasures, the Wheel of the Year,
  the Scoilverse, the pedagogical uncanny valley, the 22 mandatory
  LC Physics experiments, the Alchemy Lab, the Maths combat
  engine, the Voice Chat Gaeltacht zones).
- **v5.1** (this commit) — replace the v5 §7 "The 2060 geostrategic
  horizon" sub-section with a new §7 "The Tuath Celtic Educational
  MMO — the engineering reality of the cultural stewardship" that
  better outlines the 13 tuatha-mmo reference files in
  `.agents/skills_backup/tuatha-mmo/references/`:
  `tuatha-pipelines.md` (data pipeline: NCCA + SQA + WJEC +
  Dúchas + GeoJSON → DLT → DuckDB + LanceDB + FalkorDB →
  Dagster), `tuatha-tanstack-frontend.md` (TanStack Start frontend
  + SIWEConnect + X402Paywall + TuathCopilot + A2UIComponents),
  `tuatha-performance-tuning.md` (BGE-M3 batching + HNSW index
  management + DuckDB single-threading + Babylon.js WebGPU + LOD
  + Prometheus metrics), `tuath-api-reference.md` (the 8 API module
  groups + 30+ endpoints), `tuatha-deployment-guide.md` (Cloudflare
  Workers + Python API :8000 + Rust API :8080 + SpacetimeDB +
  DuckDB + LanceDB + FalkorDB + Dagster + Traefik), `tuath-agent-architecture.md`
  (Google ADK + Root Agent + 4 specialist sub-agents + 5 tools
  + AgUI protocol), `TUATH_MMO.md` (architecture overview),
  `spacetimedb-tuatha-guide.md` (real-time multiplayer + tables
  + reducers + subscriptions), `rust-fullstack-gaming.md` (Rust
  full-stack + Wasm + GDExtension + Cargo workspaces + `just`),
  `hades-bitcraft-pipeline.md` (Hades pre-rendered visual +
  BitCraft SpacetimeDB backend synthesis), `british-isles-game-dev-pipeline.md`
  (Ordnance Survey + Tailte Éireann + Met Office + Met Éireann
  + SpacetimeDB State Mirroring + glTF + OpenUSD),
  `agentic-education-platform.md` (CopilotKit + AgUI + MCP + x402
  + Pinginn + Screpall + UMA), and `anam-meteorological-particles.md`
  (Anam + Sídhe Gaoithe + bicubic GRIB2 + SpacetimeDB chunked
  wind-field + Fast Third-Order Texture Filtering 16→4 taps).
  The new §7 is structured as 13 thematic sub-sections (A-M) that
  map each reference file to its role in the cultural-stewardship
  operational form. The section ends with a closing M
  sub-section that ties the §20 British Isles plan to the Tuath
  platform: "The §20 is the vision; the Tuath platform is the
  implementation."

The v1+v2+v3+v3.1+v4 work remains archived in git history; the
v5.1 is the canonical current README. The 8 Gemini Deep Research
PDFs + the 13 tuatha-mmo reference files are the evidence base
for the new "Purpose" section + the new "§7 Tuath Celtic
Educational MMO" sub-section.

## What

The v5.1 README rewrite (delivered as Tasks 1-16) has 16 components:

### 1. (v1) Cherry-pick the missing subtree from `q3-2026-oideachais-consolidation`

```bash
git checkout q3-2026-oideachais-consolidation -- "cian_mac_an_déisigh_uí_liatháin/"
```

48 files restored. The 8 Wikipedia clippings return to
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`,
the lineage PDFs return to `cian_mac_an_déisigh_uí_liatháin/identity/lineage/`,
and the achievement/disability/politics/teaching/vetting evidence
folders return to their canonical locations.

### 2. (v1) Analyse the 6 most-relevant culture PDFs and write analysis files

6 of the 31 PDFs in `leabharlann/gemini_deep_research/culture/` are
directly relevant to the heritage sections. The 6 analyses live
at `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/<pdf-slug>.md`:

- `claiming_r_na_gaillimhe_a_synthesis.md` (15 pages)
- `claiming_irish_kingship_through_lineage.md` (13 pages)
- `royal_titles_celtic_heritage_and_claims.md` (13 pages)
- `heraldic_research_for_dual_blood_lineage.md` (14 pages)
- `deacy_family_heritage_research.md` (9 pages)
- `the_socio_economic_athletic_and_genealogical_topography_of_the_deacy_family_in_galway_a_multi_dimensional_analysis.md` (12 pages)

### 3. (v3) Analyse the British Isles / Celtic AI PDFs (new in v3)

A **7th** analysis is added in v3:

- `cianhoghlaim_british_isles_plan.md` (covers `british_isles_cianfhoghlaim.pdf` 16+ pages, `cultural_unity_for_british_isles.pdf` 12 pages, and `royal_collaboration_for_commonwealth_future.pdf` as the 30-year horizon backdrop)

### 4. (v3) New top-level `## The cianfhoghlaim plan throughout the British Isles` section

A new top-level section (~150 lines) that operationalises the
`british_isles_cianfhoghlaim.pdf` blueprint. 3 sub-sections:

- **§20a. The East Belfast operational hub** — Newtownards Road /
  Castlereagh Road residential base; **Turas** at the Skainos Centre
  (239 Newtownards Road, BT4 1AF); **Scoil na Seolta** (Garnerville
  Presbyterian Church, BT6 9HL); **Coláiste Feirste** (Falls Road);
  the **Glider (BRT1)** cross-city line; the maritime linkages
  (Stena Line Belfast → Cairnryan 2h 15m, Isle of Man Steam Packet
  Belfast → Douglas ~2h 50m, Stena Line Belfast → Birkenhead 8h).
- **§20b. The inter-Celtic acquisition pathway** — Irish C1 →
  Scottish Gaelic (Sabhal Mòr Ostaig) → Manx (Scoill Souree at Peel)
  → Welsh → Cornish (Keskowethyow) → Breton (Skol an Emsav). A 6-row
  table with the pathway, funding, and corpus-output column.
- **§20c. The Celtic AI Institute (Isle of Man) + the 30-year
  Cultural Archipelago roadmap** — Phase I (2026-2036)
  Stabilization & Digital Sovereignty → Phase II (2036-2046)
  Integration & Mobility → Phase III (2046-2056) Normalization &
  Sovereignty.

### 5. (v3) New top-level `## The pipelines — what cianfhoghlaim can do` section

A new top-level section (~200 lines) that walks each of the 5
pipeline stages (ingest → process → cognify → embed → expose) with
the exact Python files, Dagster asset names, BAML function names,
and entry-point commands. Each sub-section uses a 6-field template
(Purpose / Source files / Asset names / BAML functions / Command /
What you can do with it).

### 6. (v3) New top-level `## 5 cookbook recipes` section

A new top-level section (~120 lines) with 5 worked end-to-end
examples: Recipe 1 — Ingest a new Gaeltacht PDF; Recipe 2 — Add a
new BAML extraction field; Recipe 3 — Run a cognify pass; Recipe
4 — Query the LanceDB semantic-search index; Recipe 5 —
Materialise a Dagster asset group end-to-end.

### 7. (v3) Expand the `./bonneagar/` and `./leabharlann/` sister-repo subsections

The one-liner sister-repo descriptions are expanded to full
sub-section treatment: `### ./bonneagar/` now includes the full
10-subdir directory tree + the 6-file GOLD_STANDARD pattern;
`### ./leabharlann/` now includes the 6-subdir layout table + the
"Used by" column mapping each subdir to the CocoIndex v1 App +
BAML function + marimo notebook that consumes it.

### 8. (v3) Rewrite the "About the author" section from 8 to 6 sub-sections

The v2 sub-sections §D (On the constitutional synthesis) and §H
(On the constitutional warning) are **dropped**. The new 6
sub-sections are: §21a (cianfhoghlaim etymology + agentic-AI vision);
§21b (family + Deacy signet ring); §21c (heritage of Ireland: 4
provinces, Gaeltachtaí, regional dialects, previous High Kings);
§21d (British Isles personal commitment); §21e (qualified
commitment to Éire: 4-pillar qualifications); §21f (educational
mission + 5 deliverables).

### 9. (v3) Byline update

The byline is updated to add the BSc / HDip / MSc-PhD track /
Dioplóma C1 credentials and the cultural-stewardship pledge.

### 10. (v1+v2) Update the 2 dead PDF references + tracking issue

The "Note on 2 unreadable PDFs" block is updated: the
`cian_mac_an_déisigh_uí_liatháin/identity/lineage/old_passports_dual_citizen_verification_roi_uk.pdf`
link is now a working link; the
`leabharlann/gemini_deep_research/culture/neil_deasy_cookes_corner-galway_advertiser.pdf`
reference is preserved as plain-text with a working link to the
restored substitute. A new tracking issue is filed at
`openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`.

### 11. (v1+v2) Spec deltas (2 specs)

- **`openspec/specs/cross-domain-registry/spec.md`** — 1 MODIFIED
  Requirement (`Wikipedia fixture storage convention`) with 1 new
  Scenario asserting the drift-detector invariant
  (clipping SHA-256 === fixture SHA-256).
- **`openspec/specs/oideachais-leabharlann/spec.md`** — 1 ADDED
  Requirement (`Heritage corpus restoration provenance`) codifying
  the 4-step restoration contract.

### 12. (v4) Replace §21c-§21f + Citations + 2 unreadable PDFs note with a single section that explains the leabharlann document types + references the 8 specific PDFs as the purpose of Cian Mac an Déisigh Uí Liatháin and cianfhoghlaim

The v3 §21c-§21f + Citations + 2 unreadable PDFs note + "Irish-English
bilingual title on line 1" line (README lines 1366-1800) are removed
and replaced with a single new section. The new section is structured
as:

- **Overview paragraph** (4-6 sentences) — explains the 6 leabharlann
  subdirs and their purpose, and points readers at the
  `gemini_deep_research/culture/` archive as the primary source corpus
  for the author's heritage and purpose.
- **8 PDF sub-sections** — one sub-section per PDF, each with:
  - The PDF's full title + page count
  - A 2-3 sentence "what it is" + a direct link to the leabharlann
    GitHub blob
  - A 3-5 sentence "what it documents / why it matters for
    cianfhoghlaim"

The 8 PDFs and their per-section content are documented in Task 11
of `tasks.md`. The new section also improves the start of the README:
the bilingual title is re-emphasised, the TL;DR opens with a direct
link to the leabharlann archive, and the heritage framing shifts from
"§21c-§21f as narrative sub-sections" to "the leabharlann `gemini_deep_research/culture/`
corpus is the primary source for the author's heritage and purpose".

## Impact

- **Surface change (v1+v2+v3+v3.1+v4):** 48 files restored, 3 README
  personal-heritage sub-sections rewritten (v1), Ring of Connacht +
  4-province + Aileach + 2060 added (v2), full README rewrite + 3
  new top-level sections (v3), direct GitHub PDF links + Neil Mac
  an Déisigh name origin + Tribes_of_Galway link fix + In memory
  of removal (v3.1), and 4 heritage sections + Citations + 2
  unreadable PDFs replaced with a single leabharlann-document-types
  + 8-PDF section + start-of-README improvement (v4). The current
  README is targeted at **~1,400 lines** (down from 1,831 in v3.1;
  the ~430-line removal is partially offset by the new ~250-line
  leabharlann-document-types + 8-PDF section).
- **Behaviour change:** The `culture_heritage` Cognee dataset will
  pick up the restored 8 Wikipedia clippings + the 6 lineage PDFs on
  the next cognify run.
- **Documentation change:** The v3 §21c-§21f narrative is replaced
  with a direct per-PDF sub-section structure that maps each of the
  8 specific Gemini Deep Research PDFs to its purpose for the
  cianfhoghlaim monorepo. The new structure is more direct, more
  citable, and less narrative. The start of the README is more
  prominent on the bilingual title + the leabharlann archive.
- **No new package, no new agent, no new infra.**
- **No new BAML extraction change.**
- **No new Dagster asset change.**
- **No merge from `q3-2026-oideachais-consolidation` into `main`** —
  the v4-consolidation history is intentionally separate; only the
  `cian_mac_an_déisigh_uí_liatháin/` subtree is restored.
- **No branch management** — the v3.1 + v4 rewrites land on `main`
  as a follow-up commit each to the previous one.

## Non-goals

- **No new Wikipedia articles** beyond the existing 8.
- **No new DLT source** — the fixtures already exist.
- **No new front-end surface** — no TanStack route, no Convex function,
  no marimo notebook.
- **No Firecrawl URL verification** — the 8 Wikipedia URLs are assumed
  unchanged; a follow-up change will verify them with the now-funded
  API credits.
- **No PDF re-extraction for the 2 unread PDFs.**
- **No branch management beyond the cherry-pick.**
- **No new openspec change for v3** — the v3 is filed as **Task 9**
  of the existing `2026-06-29-restore-heritage-corpus-and-expand-readme`
  change. One change, one archive, one set of spec deltas.

## Files touched

### New (13)

- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/proposal.md` (this file)
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tasks.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/cross-domain-registry/spec.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/specs/oideachais-leabharlann/spec.md`
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`
- 6× `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/<pdf-slug>.md` (v1+v2 PDFs)
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/analysis/cianhoghlaim_british_isles_plan.md` (v3 PDF)

### Restored (48)

- The full `cian_mac_an_déisigh_uí_liatháin/` subtree from
  `q3-2026-oideachais-consolidation`: 8 clippings + 8 lineage
  PDFs/JPEGs + 4 identity-deacy + 1 disability + 6 politics + 10
  teaching + 1 BCS + 4 vetting + 9 achievement = 51 files including
  the 3 .DS_Store markers.

### Modified (2)

- `README.md` — fully rewritten across 3 commits (v1 at `7a1243485`
  = 3 subsections, v2 at `f3affbde2` = 4 subsections + 4 new, v3 at
  this commit = full rewrite to 1,761 lines).
- `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tasks.md`
  — Task 9 added.

## Acceptance

- `openspec validate 2026-06-29-restore-heritage-corpus-and-expand-readme --strict` exits 0.
- 48 files restored under `cian_mac_an_déisigh_uí_liatháin/`.
- 8 Wikipedia clippings present at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/`.
- README's "About the author" section has **6 sub-sections** (not 8).
- (v4) The §21c-§21f + Citations + 2 unreadable PDFs note + "Irish-English bilingual title on line 1" line are removed; a single new section replaces them.
- (v4) `grep -c "On the heritage of Ireland" README.md` = 0 (the §21c section title is removed).
- (v4) `grep -c "On the cianfhoghlaim plan throughout the British Isles" README.md` = 0 (the §21d section title is removed).
- (v4) `grep -c "On the qualified commitment to Éire" README.md` = 0 (the §21e section title is removed).
- (v4) `grep -c "On the educational mission" README.md` = 0 (the §21f section title is removed).
- (v4) `grep -c "Citations.*Wikipedia" README.md` = 0 (the Citations block is removed).
- (v4) `grep -c "Note on 2 unreadable PDFs" README.md` = 0 (the unreadable-PDFs note is removed).
- (v4) `grep -c "In memory of" README.md` = 0 (the "In memory of" line is removed).
- (v4) `grep -c "leabharlann/gemini_deep_research/culture" README.md` ≥ 8 (each of the 8 PDFs is referenced by direct leabharlann path; the v3.1 commit already shows 22 occurrences of the GitHub URL).
- (v4) The new section opens with an explanation of the 6 leabharlann subdirs and points readers to the `gemini_deep_research/culture/` archive as the primary source corpus.
- (v4) Each of the 8 specific PDFs (`claiming_r_na_gaillimhe_a_synthesis.pdf`, `heraldic_research_for_dual_blood_lineage.pdf`, `british_isles_cianfhoghlaim.pdf`, `claiming_irish_kingship_through_lineage.pdf`, `researching_neil_deacy_s_galway_heritage.pdf`, `royal_titles_celtic_heritage_and_claims.pdf`, `deacy_family_heritage_research.pdf`, `royal_collaboration_for_commonwealth_future.pdf`) is cited with its full title + key claims.
- (v4) The start of the README is improved: the bilingual title is more prominent, the TL;DR opens with a direct link to the leabharlann archive.
- (v5) The v4 "Purpose" section's overview + 6-subdir table + 8 per-PDF sub-sections + how-to-access + closing note (README lines 1382-1757, ~376 lines) are removed.
- (v5) A new single coherent narrative replaces them: 10 thematic sub-sections weaving the actual content of the 8 PDFs into a unified "the Triple Crown, the Saoí standard, and the 21st-century cianfhoghlaim" story.
- (v5) The new section references the actual page numbers from the 8 PDFs (p. 1-3, 2, 4, 6, etc.).
- (v5) The new section references the cianfhoghlaim educational themes from the `ui-components` skill (the Celtic design language, the dnd-kit exam builder pattern, the CopilotKit + AG-UI protocol) and the `tuatha-mmo` skill (the Saoí standard, the Four Treasures of the Tuatha Dé Danann, the Wheel of the Year, the Scoilverse, the pedagogical uncanny valley, the 22 mandatory LC Physics experiments, the Alchemy Lab, the Maths combat engine, the Voice Chat Gaeltacht zones).
- (v5) The 8 hero PDFs (claiming_r_na_gaillimhe_a_synthesis.pdf, heraldic_research_for_dual_blood_lineage.pdf, british_isles_cianfhoghlaim.pdf, claiming_irish_kingship_through_lineage.pdf, researching_neil_deacy_s_galway_heritage.pdf, royal_titles_celtic_heritage_and_claims.pdf, deacy_family_heritage_research.pdf, royal_collaboration_for_commonwealth_future.pdf) are all direct-linked from the leabharlann GitHub repo.
- (v5.1) The v5 §7 "The 2060 geostrategic horizon" content is removed and replaced with a new §7 "The Tuath Celtic Educational MMO — the engineering reality of the cultural stewardship".
- (v5.1) The new §7 references all 13 tuatha-mmo reference files by name: `tuatha-pipelines.md`, `tuatha-tanstack-frontend.md`, `tuatha-performance-tuning.md`, `tuath-api-reference.md`, `tuatha-deployment-guide.md`, `tuath-agent-architecture.md`, `TUATH_MMO.md`, `spacetimedb-tuatha-guide.md`, `rust-fullstack-gaming.md`, `hades-bitcraft-pipeline.md`, `british-isles-game-dev-pipeline.md`, `agentic-education-platform.md`, `anam-meteorological-particles.md`.
- (v5.1) The new §7 preserves the specific engineering details from each reference file: the BGE-M3 batch sizes 32-500, the Lanczos HNSW index with num_partitions=256 + num_sub_vectors=96, the DuckDB SerialDatabaseExecutor single-threading pattern, the 20Hz position sync rate, the BGE-M3 1024-dim vector, the OS NGD API + LiDAR resolutions (TII 2.0m, GSI 1.0m, WMCC 0.25m, DCHG 0.13m, OPW 2.0m), the Anam system with the Fast Third-Order Texture Filtering 16→4 tap optimization, the Pinginn stablecoin + Screpall soulbound token dual-token system, the UMA Optimistic Oracle pattern, the x402 protocol for Pay-per-Compute learning economy, the Catmull-Rom bicubic interpolation for the GRIB2/NetCDF wind fields, and the 32×32 or 64×64 SpacetimeDB WindChunk BLOBs.
- (v5.1) The new §7 references the §20 British Isles plan (East Belfast operational hub + Galway evidence base + Isle-of-Man Celtic AI Institute + 30-year Cultural Archipelago) as the §20 deployment context; the §20 is the vision, the Tuath platform is the implementation.
- `grep -c "Dublin / Leinster consolidation" README.md` = 0.
- `grep -c "Gaeltacht" README.md` ≥ 5 (actual: 27).
- `grep -c "High King" README.md` ≥ 3 (actual: 4).
- `grep -c "British Isles" README.md` ≥ 8 (actual: 12).
- `grep -c "Celtic AI" README.md` ≥ 3 (actual: 13).
- `grep -c "Turas\|Scoil na Seolta\|Coláiste Feirste" README.md` ≥ 3.
- `grep -c "Colmcille" README.md` ≥ 2 (actual: 4).
- `grep -c "Cryptography\|cryptography" README.md` ≤ 2 (actual: 0).
- `grep -c "First Class Honours" README.md` ≥ 1 (actual: 4).
- `grep -c "Dioplóma C1\|TEG C1" README.md` ≥ 1 (actual: 2).
- `grep -c "leabharlann" README.md` ≥ 5 (actual: 106).
- `grep -c "bonneagar" README.md` ≥ 5 (actual: 49).
- README's "Key packages" section has the 2 expanded sister-repo subsections.
- README's new `## The pipelines` section exists with 5 sub-sections.
- README's new `## 5 cookbook recipes` section exists with 5 recipes.
- README's new `## The cianfhoghlaim plan throughout the British Isles` section exists with 3 sub-sections.
- The byline is updated with the new credentials.

## Cross-references

- Originating changes: `openspec/changes/extend-culture-heritage-to-8-articles/`
  and `openspec/changes/ingest-culture-heritage/`.
- Originating branch: `q3-2026-oideachais-consolidation` (last touched 2026-06-28).
- v1 commit: `7a1243485`. v2 commit: `f3affbde2`. v3 commit: `6fee5eb6a`. v3.1 commit: `3cb8acbfe`. v4 commit: `55413dbdc`. v5 commit: `62b9dbe21`. v5.1 commit: this proposal's commit.
- Canonical specs: `openspec/specs/cross-domain-registry/spec.md` and
  `openspec/specs/oideachais-leabharlann/spec.md`.
- Tracking issue: `openspec/changes/2026-06-29-restore-heritage-corpus-and-expand-readme/tracking_issues/unread-pdfs.md`.
- Skills: `.agents/skills/oideachais-leabharlaim/SKILL.md`,
  `.agents/skills/oideachais-cocoindex-v1/SKILL.md`,
  `.agents/skills/agent-observability/SKILL.md`,
  `.agents/skills/celtic-asset-generation/SKILL.md`,
  `.agents/skills/infrastructure-stacks/SKILL.md`.