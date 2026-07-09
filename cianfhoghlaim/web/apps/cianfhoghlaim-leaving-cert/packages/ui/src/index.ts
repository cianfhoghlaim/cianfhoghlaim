// @cianfhoghlaim/ui — 12 reusable components for the professional + minimal
// Cianfhoghlaim theming (per docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css and the
// 2026-07-09 WoT-theming cleanup). The mythology / historical-sources
// layer is deferred to BIEP-v2; the 5 WoT-flavored lore components are
// no longer re-exported here.
//
// The 12 components:
//   <CiButton>        — Duolingo tactile 3D press feedback (border-b-4 → border-b-2)
//   <CiProgressRing>  — Khan Academy 4-tier mastery (Attempted / Familiar / Proficient / Mastered)
//   <CiDetailCell>    — Khan Academy detail cells (left icon + metadata)
//   <CiSemanticPill>  — Khan Academy semantic pills (status indicators)
//   <CiStreakFlame>   — Duolingo streak flame (the daily-practice indicator)
//   <CiBoonsChoice>   — Hades 3-way vertical choice with god colours
//   <CiSkillTree>     — Clair Obscur material library + BitCraft Empire Panel hierarchy
//   <CiDiegeticPanel> — Hades diegetic UI (integrated into world)
//   <CiMapZone>       — WoW hex-based claim with decay indicator
//   <CiWindow>        — PostHog Navigation 3000 multi-panel resizable
//   <CiFocusMode>     — Khan Academy Focus Mode (stripped nav)
//   <CiTextbookPanel> — Clair Obscur material library (parchment + slate + ink-wash + gold-leaf + knotwork)
//
// Plus the 4 map components (per the accurate British Isles map, kept):
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

export { CiRealmMap } from "./map/realm-map";
export { CiSubnationRegion } from "./map/subnation-region";
export { CiLandmark } from "./map/landmark";
export { CiSubnationFlag } from "./map/subnation-flag";

// Re-export the utility helpers
export { cn } from "./utils";