# UI Inspiration — KCG Summary

## What It Is
A curated collection of UI/UX inspiration screenshots from best-in-class products and games, mapped to the sruth/ frontend projects. Includes: MotherDuck (analytics platform), PostHog (product analytics with Lemon UI), Duolingo (gamified language learning), Khan Academy (educational mastery system), Hades 1 & 2 (diegetic game UI), Clair Obscur: Expedition 33 (turn-based RPG UI), and World of Warcraft (MMO interface patterns). The `UI_INSPIRATION_GUIDE.md` provides detailed design token extraction, pattern analysis, and project-specific mapping.

## Why This Matters for Kings' College Galway
Each sruth/ frontend has a deliberate UI inspiration mapping: `tuath/` draws from Hades (shadow-first HUD), Clair Obscur (material library), and WoW (quest tracking); `oideachais/` draws from Duolingo (streaks/hearts) and Khan Academy (mastery levels); `crypteolas/` and `aleyum/` draw from MotherDuck and PostHog (analytics dashboards, 3-panel layouts). The design tokens and component pattern recommendations (tactile buttons, progress rings, material frames) directly inform the shadcn/ui theme configuration and Tailwind CSS customizations.

## Key Patterns Preserved
- **docs/web/ui-inspiration/UI_INSPIRATION_GUIDE.md** — Comprehensive UI inspiration guide with design tokens, pattern analysis, and project-specific mappings

## Source Files
Inspiration screenshots were large PNG files (30MB total) sourced from product websites and game footage (2025-12-30). Removed (2026-06-06) to reduce repository size. The design analysis and tokens are fully preserved in the guide document.

## What Was Removed
- 9 large PNG screenshots (30MB): motherduck-homepage.png, posthog-homepage.png, duolingo-homepage.png, khanacademy-homepage.png, hades-fight-ui.png, hades-boons-ui.png, clair-obscur-hud.png, clair-obscur-skill-tree.png, wow-ui-gallery.png
