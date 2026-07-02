// @cianfhoghlaim/ui — 12 reusable components per the Brown Ajah theming
// (docs/BROWN_AJAH_THEMING.md and docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css).
//
// The 12 components:
//   <CiButton>        — Duolingo tactile 3D press feedback (border-b-4 → border-b-2)
//   <CiProgressRing>  — Khan Academy 4-tier mastery (Attempted / Familiar / Proficient / Mastered)
//   <CiDetailCell>    — Khan Academy detail cells (left icon + metadata)
//   <CiSemanticPill>  — Khan Academy semantic pills (status indicators)
//   <CiStreakFlame>   — Duolingo streak flame (the Cauldron of the Dagda)
//   <CiBoonsChoice>   — Hades 3-way vertical choice with god colours
//   <CiSkillTree>     — Clair Obscur material library + BitCraft Empire Panel hierarchy
//   <CiDiegeticPanel> — Hades diegetic UI (integrated into world)
//   <CiMapZone>       — WoW hex-based claim with decay indicator
//   <CiWindow>        — PostHog Navigation 3000 multi-panel resizable
//   <CiFocusMode>     — Khan Academy Focus Mode (stripped nav)
//   <CiTextbookPanel> — Clair Obscur material library (parchment + slate + ink-wash + gold-leaf + knotwork)
//
// Plus the 5 lore components (per docs/CIANFHLOGHLAIM_LORE.md):
//   <CiCianHeader>    — the Cian → Lugh header tagline (operator-only)
//   <CiBrownAjahBadge> — the russet brown knotwork badge
//   <CiAmyrlinSeat>   — the orchestrator agent visual
//   <CiTuathanWagon>  — the student-as-traveller mobile client icon
//   <CiDragonBanner>  — the Wales subnation flag (red dragon on white)
//
// Plus the 4 map components (per the accurate British Isles map, R7):
//   <CiRealmMap>      — the accurate British Isles map base
//   <CiSubnationRegion> — the 6 subnations SVG regions
//   <CiLandmark>      — the 5 NCCA Key Competencies land-marks
//   <CiSubnationFlag> — the 6 subnation flags
//
// All components are pure presentational; the data layer is supplied via
// props from the consuming app.

export { CiButton } from "./button";
export { CiProgressRing } from "./progress-ring";
export { CiDetailCell } from "./detail-cell";
export { CiSemanticPill } from "./semantic-pill";
export { CiStreakFlame } from "./streak-flame";
export { CiBoonsChoice } from "./boons-choice";
export { CiSkillTree } from "./skill-tree";
export { CiDiegeticPanel } from "./diegetic-panel";
export { CiMapZone } from "./map-zone";
export { CiWindow } from "./window";
export { CiFocusMode } from "./focus-mode";
export { CiTextbookPanel } from "./textbook-panel";

export { CiCianHeader } from "./lore/cian-header";
export { CiBrownAjahBadge } from "./lore/brown-ajah-badge";
export { CiAmyrlinSeat } from "./lore/amyrlin-seat";
export { CiTuathanWagon } from "./lore/tuathan-wagon";
export { CiDragonBanner } from "./lore/dragon-banner";

export { CiRealmMap } from "./map/realm-map";
export { CiSubnationRegion } from "./map/subnation-region";
export { CiLandmark } from "./map/landmark";
export { CiSubnationFlag } from "./map/subnation-flag";

// Re-export the utility helpers
export { cn } from "./utils";