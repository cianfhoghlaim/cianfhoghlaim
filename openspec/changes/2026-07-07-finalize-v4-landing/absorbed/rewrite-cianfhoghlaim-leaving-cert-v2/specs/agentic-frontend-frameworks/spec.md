# Delta: agentic-frontend-frameworks

## ADDED Requirements

### Requirement: 5th canonical front-end surface — Cianfhoghlaim OS (R5 — NEW)

The system SHALL expose a 5th canonical front-end surface:
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`. The stack tuple is:

| Aspect | Choice |
|:--|:--|
| Front-end | TanStack Start (Vite plugin) + file-based routing |
| Agent UI | CopilotKit v2 Factory Mode + AG-UI SSE streaming |
| Realtime backend | Convex (fresh standalone `conic-leaving-cert` deployment) |
| API gateway | Hono + oRPC + BetterAuth + Pocket ID OIDC + optional SIWE |
| Diagram renderer | React Flow + D3 + Babylon.js + model-viewer |
| Data plane | MotherDuck (read-only lakehouse) + Convex (read-write persona) |
| Auth | BetterAuth (email/password + OAuth) backed by Pocket ID OIDC; optional SIWE |
| User | Irish educators + students |
| Map | Accurate British Isles (OpenStreetMap base) split into 6 subnations |
| Theming | Brown Ajah of the Wheel of Time (healers, scholars, Earth-workers) |
| Tagline | "Aes Sedai — servants of all" (the Brown Ajah motto) |

#### Scenario: A new spec wants to declare a 6th surface

- **GIVEN** the 5 canonical surfaces table is locked
- **WHEN** a new spec requests a 6th row
- **THEN** the developer MUST first refactor an existing surface out
- **AND** no surface count growth without consolidation

### Requirement: Celtic UI Design System (R6 — NEW)

The system SHALL implement the design tokens + 12 reusable `<Ci*>` components
documented in `docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css`,
drawing on:

**4 product UIs** (per `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md`):
- **MotherDuck** — 3-panel layout, column explorer sparklines, CTE visualizer, instant SQL feedback
- **PostHog** — Lemon UI design system (chunky, physical-depth buttons), Navigation 3000 multi-panel resizable, Notebooks live+replay, Hog mascot
- **Duolingo** — Streak system (flame icon + day counter), Hearts/Lives, Snake Path, 3D tactile buttons (`border-b-4` to `border-b-8`)
- **Khan Academy** — Wonder Blocks design system, Mastery Levels (Attempted → Familiar → Proficient → Mastered), Detail Cells, Semantic Pills, Focus Mode

**4 game UIs**:
- **Hades** — Diegetic UI, Chiaroscuro portraits, Boon Selection (3-choice vertical with god colours), Shadow-first palette
- **Clair Obscur: Expedition 33** — Reactive turn-based AP refund on perfect parry, Material library (Obsidian/Black Marble/Gold Leaf), Belle Époque aesthetics
- **WoW** — Edit Mode HUD customisation, Semantic quest icons (Shield/Circle/Star), Map legend filtering
- **BitCraft Online** — Recipe Tree, Empire Panel hierarchy (Player→Settlement→Empire)

**8 Celtic adaptations** (per the guide):
1. Belle Époque Ironwork → Insular Art Knotwork (Book of Kells)
2. Oil Painting → Ink-Wash & Gold Leaf
3. Obsidian/Marble → Slate & Ogham Stone
4. Cinzel → Uncial/Insular Script
5. (extended) Hades diegetic UI → window chrome integrated into the Cianfhoghlaim OS
6. (extended) WoW semantic quest icons → 24 SVG icons (3 per subject × 8 subjects)
7. (extended) Khan mastery levels → Brown Ajah éraic treasures (4 levels × 13 treasures)
8. (extended) Duolingo streak → Cauldron of the Dagda (never empties)

The 12 components SHALL be: `<CiButton>`, `<CiProgressRing>`, `<CiDetailCell>`,
`<CiSemanticPill>`, `<CiStreakFlame>`, `<CiBoonsChoice>`, `<CiSkillTree>`,
`<CiDiegeticPanel>`, `<CiMapZone>`, `<CiWindow>`, `<CiFocusMode>`,
`<CiTextbookPanel>`.

The 145 comic reference images at `docs/comics/` SHALL be ingested as
the celtic-art reference library for the FIBO asset generator
(`tuatha/asset_generation/fibo/education_fibo.py`).

#### Scenario: CiButton applies the tactile press feedback

- **GIVEN** the user clicks any CiButton component
- **WHEN** the click fires
- **THEN** the button's `border-bottom` compresses from `4px` to `2px`
- **AND** the CiProgressRing fills per the Khan Academy 4-tier mastery levels

#### Scenario: CiStreakFlame is the Cauldron of the Dagda

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the streak indicator shows the user's day count
- **AND** the indicator is themed as the Cauldron of the Dagda (the ever-full cauldron that never empties)
- **AND** on Beltane (1 May) the indicator resets to 100% (the summer refresh)

### Requirement: Brown Ajah theming + accurate British Isles map (R7 — NEW)

The system SHALL implement the **Brown Ajah** Wheel of Time theming per
the 4 WoT excerpts:

- **Aes Sedai** = the 8 NCCA subject specialists (the Brown Ajah members)
- **Amyrlin Seat** = the orchestrator agent (the central authority)
- **Dragon Reborn** = the student who completes the cross-subject mastery
- **Dragon Banner** = the Wales subnation flag (Cadwaladr ap Cadwallon + Owain Glyndwr; red dragon on white)
- **Tuatha'an** = the Irish Travellers (the student-as-traveller; the Cianfhoghlaim mobile client)

The realm map SHALL be an **accurate** map of the British Isles (NOT a
fictional map). The base layer SHALL be OpenStreetMap tiles for Ireland +
Great Britain + Isle of Man, served from Cloudflare CDN.

The 6 subnations SHALL be: Éire (Ireland, v1 active) + Northern Ireland +
Scotland + England + Wales + Isle of Man. Jersey + Guernsey are excluded
(not on the main British Isles landmass; reachable later via the Crown
Dependencies surface).

The 5 NCCA Key Competencies SHALL be the 5 land-marks on the map:
- **Communicating** → Dublin (the Book of Kells, Trinity College Library)
- **Information Processing** → Edinburgh (the Library of the University of Edinburgh)
- **Critical & Creative Thinking** → Cardiff (the Welsh Dragon)
- **Personal Effectiveness** → London (the Royal College of Physicians)
- **Working with Others** → Douglas, Isle of Man (the Tynwald)

The 6th node SHALL be Belfast (the Cross-Border Studies; the 6th wound — the partition of the island).

The 8 NCCA subjects SHALL be the 8 overlay buttons on the map.

The Connacht province (Galway + Mayo + Roscommon + Sligo) SHALL be the
"home base" with the Cian lineage highlights (Delbhna Tír Dhá Locha +
Lough Corrib + Galway Bay + Moycullen).

#### Scenario: Accurate British Isles map renders 6 subnations

- **GIVEN** the user opens `/en/map`
- **WHEN** the page loads
- **THEN** the accurate British Isles map renders
- **AND** all 6 subnations are visible with bilingual EN+GA labels
- **AND** the Éire subnation is highlighted as the v1 active region
- **AND** the other 5 subnations are greyed out with "Coming soon" badges
- **AND** the 5 NCCA Key Competencies are placed at their landmark cities
- **AND** the 8 NCCA subjects are overlay buttons

#### Scenario: Wales subnation flies the Dragon Banner

- **GIVEN** the user hovers over the Wales subnation
- **WHEN** the hover fires
- **THEN** the Dragon Banner (red dragon on white, per Cadwaladr ap Cadwallon + Owain Glyndwr) animates into view
- **AND** the Wales subnation background tints to the Welsh national colour (Y Ddraig Goch red)
- **AND** the bilingual label "Wales / an Bhreatain Bheag" appears

#### Scenario: Personal lineage never appears on the public surface

- **GIVEN** the user opens any page on `oideachais.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]` (Cian Mac an Déisigh)
- **AND** no text matches the family surnames Deacy, Lyons, Morris, Conroy
- **AND** no text references the 3 Gemini Deep Research warrants
- **AND** the lore document `docs/CIANFHLOGHLAIM_LORE.md` is operator-only and never linked from the public surface