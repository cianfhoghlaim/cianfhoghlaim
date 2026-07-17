# UI Inspiration Guide for sruth/ Frontends

## For Use with Google Stitch

Generated: 2025-12-30

This document maps UI/UX inspiration from best-in-class products and games to each sruth/ frontend project.

---

## Table of Contents

1. [sruth/ Frontend Overview](#sruth-frontend-overview)
2. [Product UI Inspiration](#product-ui-inspiration)
3. [Game UI Inspiration](#game-ui-inspiration)
4. [Mapping: Inspiration → Projects](#mapping-inspiration--projects)
5. [Screenshot Reference](#screenshot-reference)

---

## sruth/ Frontend Overview

### 1. tuath/ - Celtic Educational Game

**Stack**: TanStack Start + Babylon.js + SpacetimeDB + CopilotKit
**Current State**: Dark Celtic theme (emerald/slate), 3D game client, AG-UI streaming components
**Needs**: Enhanced HUD design, quest tracking, skill trees, immersive menu systems

### 2. sruth/cianfhoghlaim/ - Irish Education Platform

**Stack**: TanStack Start + Vite + Convex + CopilotKit
**Current State**: Three apps (UI, Web Portal, Dashboard), Generative UI pattern, Irish TTS
**Needs**: Mobile responsiveness, consolidated components, gamification elements

### 3. sruth/crypteolas/ - DeFi Research Platform

**Stack**: React 19 + TanStack + Radix UI + SIWE Auth
**Current State**: DeFi dashboards, TVL charts, AI copilot interface
**Needs**: NFT gallery, improved charts (Recharts), wallet UX (wagmi/RainbowKit)

### 4. aleyum/ - Developer Portal & Portfolio

**Stack**: TanStack Start + React 19 + Recharts + Tailwind 4
**Current State**: Widget dashboard, agent chat, audio cards
**Needs**: Live data integration, responsive grid, waveform visualization

### 5. códeolas/ - Code Intelligence System

**Stack**: Generative UI (AG-UI), Python MCP server
**Current State**: ChunkApproval, CitationCard components
**Needs**: Syntax highlighting (shiki), Monaco editor, architecture diagrams

---

## Product UI Inspiration

### MotherDuck - Analytics Platform

**Screenshots**: `motherduck-homepage.png`
**Key Patterns**:

- **Instant SQL**: Real-time query feedback as you type
- **Three-Panel Layout**: Object Explorer | SQL Notebook | Table Explorer
- **Column Explorer**: Automatic sparklines and summary statistics
- **CTE Visualizer**: Click into intermediate results

**Apply to**:

- `sruth/crypteolas/` - TVL charts, protocol analytics
- `aleyum/` - Portal monitoring dashboards
- `sruth/cianfhoghlaim/` - Curriculum data exploration

**Design Tokens**:

```css
--md-yellow: brand accent --md-neutral-100-900: workspace grays
  --md-semantic-success: green for positive metrics;
```

---

### PostHog - Product Analytics

**Screenshots**: `posthog-homepage.png`
**Key Patterns**:

- **Lemon UI Design System**: Chunky, physical-depth buttons
- **Navigation 3000**: Multi-panel resizable layout
- **Notebooks**: Live insights + session replays + markdown
- **Playful Branding**: Hog mascot, quirky themes

**Apply to**:

- `sruth/cianfhoghlaim/` - Student progress dashboards
- `aleyum/` - Infrastructure monitoring
- All projects - Button depth styling (`border-b-4` active states)

**Design Tokens**:

```css
--posthog-red: #f54e00 --posthog-blue: hsl(228, 100%, 56%)
  --shadow-elevation-3000: layered depth;
```

---

### Duolingo - Language Learning

**Screenshots**: `duolingo-homepage.png`
**Key Patterns**:

- **Streak System**: Loss aversion via flame icon + day counter
- **Hearts/Lives**: Pacing mechanic with mascot feedback
- **Snake Path**: Staggered learning journey with circular progress
- **3D Tactile Buttons**: `border-b-4` to `border-b-8` compression effect
- **Mascot States**: Happy → Sad → Bad based on performance

**Apply to**:

- `tuath/` - XP system, quest progression, Celtic mascot (Púca?)
- `sruth/cianfhoghlaim/` - Irish learning path, streak mechanics
- All educational - Bite-sized lessons, immediate feedback

**Design Tokens**:

```css
--duo-green: #4ade80 (success) --duo-blue: #0ea5e9 (info) --duo-rose: #f43f5e
  (error);
```

---

### Khan Academy - Educational Platform

**Screenshots**: `khanacademy-homepage.png`
**Key Patterns**:

- **Wonder Blocks Design System**: React component library
- **Mastery Levels**: Attempted → Familiar → Proficient → Mastered
- **Detail Cells**: Left accessory icon + metadata layout
- **Semantic Pills**: Status indicators with color coding
- **Focus Mode**: Stripped navigation during video playback

**Apply to**:

- `sruth/cianfhoghlaim/` - Curriculum progression, mastery tracking
- `tuath/` - Skill unlock visualization
- All educational - Content cards, progress visualization

**Design Tokens**:

```css
--khan-blue: #0085a1 --khan-green: #71ce7e (success) --khan-yellow: #ffbc00
  (warning) --radius-080 to radius-240: friendly rounding;
```

---

## Game UI Inspiration

### Hades 1 & 2 - Roguelike

**Screenshots**: `hades-fight-ui.png`, `hades-boons-ui.png`
**Key Patterns**:

- **Diegetic UI**: Interface integrated into game world
- **Chiaroscuro Portraits**: Strong light-dark contrast
- **Boon Selection**: Three-choice vertical layout with god colors
- **Shadow-First Palette**: Dark base with acidic accents

**Apply to**:

- `tuath/` - Celtic god boons, skill selection, dialogue system
- HUD design - Health/Magick bars, status effects

**Color Palette**:

```css
--hades-base: #1d1d2f (deep black) --hades-tuna: #3f3f4b (dark blue)
  --hades-accent: #ff6e61 (orange-red) --hades-gold: boon highlight;
```

**Typography**:

- **Sloop Script**: Elegant titles (Greek calligraphy feel)
- **Caecilia-like serif**: Readable body text

---

### Clair Obscur: Expedition 33 - Turn-Based RPG

**Screenshots**: `clair-obscur-hud.png`, `clair-obscur-skill-tree.png`
**Key Patterns**:

- **Reactive Turn-Based**: AP refund on perfect parry
- **Material Library**: Obsidian, Black Marble, Gold Leaf textures
- **Brushstroke Textures**: Oil-painting in roughness maps
- **Belle Époque Aesthetics**: Art Nouveau + Art Deco

**Apply to**:

- `tuath/` - Combat UI, Celtic transmutation of style
- Menu systems - Rich material-based frames

**Celtic Adaptations**:
| Expedition 33 | Celtic RPG |
|---------------|------------|
| Belle Époque Ironwork | Insular Art Knotwork (Book of Kells) |
| Oil Painting Textures | Ink-Wash & Gold Leaf |
| Obsidian/Marble | Slate & Ogham Stone |
| Cinzel Typography | Uncial/Insular Script |

---

### World of Warcraft - MMO

**Screenshots**: `wow-ui-gallery.png`
**Key Patterns**:

- **Edit Mode**: Full HUD customization
- **Semantic Quest Icons**: Shield (Campaign), Circle (Side), Star (Legendary)
- **Map Legend Filtering**: Progressive disclosure
- **Raid Frames**: Grid-based unit frames

**Apply to**:

- `tuath/` - Quest tracking, map zones, party frames
- Celtic zones - Drust/Night Elf aesthetic adaptation

**Zone Aesthetics**:
| Night Elf (Classic Druidic) | Kul Tiras/Drust (Celtic Gothic) |
|-----------------------------|--------------------------------|
| Purple, Emerald, Silver | Slate, Moss, Gnarled Wood |
| Moon shapes, Leaves, Wisps | Wicker, Branches, Bone Runes |
| Living wood, Starlight | "Death-druidism", Dead wood |

---

### BitCraft Online - Community MMO

**Key Patterns**:

- **Recipe Tree UI**: Hierarchical crafting visualization
- **Empire Panel**: Player → Settlement → Empire hierarchy
- **Hex-Based Claims**: Color-coded territory with decay indicators
- **Supply System**: Upkeep/decay rate widgets

**Apply to**:

- `tuath/` - Crafting interface, community features
- Territory/clan systems if implemented

---

## Mapping: Inspiration → Projects

### tuath/ (Celtic Educational Game)

| Feature         | Primary Inspiration          | Secondary                      |
| --------------- | ---------------------------- | ------------------------------ |
| HUD Design      | Hades (shadow-first)         | WoW (centralized combat wedge) |
| Skill Trees     | Clair Obscur                 | Khan Academy (mastery)         |
| Quest Tracking  | WoW (semantic icons)         | Duolingo (snake path)          |
| Dialogue        | Hades (portrait-to-dialogue) | -                              |
| Combat UI       | Clair Obscur (reactive AP)   | Hades (boon selection)         |
| XP/Progression  | Duolingo (streaks, XP)       | Khan (mastery levels)          |
| Menu Aesthetics | Clair Obscur (material lib)  | Hades (diegetic)               |

### sruth/cianfhoghlaim/ (Education Platform)

| Feature       | Primary Inspiration        | Secondary            |
| ------------- | -------------------------- | -------------------- |
| Learning Path | Duolingo (snake path)      | Khan (skill tree)    |
| Progress      | Khan (mastery levels)      | Duolingo (circular)  |
| Gamification  | Duolingo (streaks, hearts) | -                    |
| Dashboards    | PostHog (navigation 3000)  | MotherDuck (3-panel) |
| Content Cards | Khan (detail cells)        | -                    |

### sruth/crypteolas/ (DeFi Platform)

| Feature          | Primary Inspiration          | Secondary            |
| ---------------- | ---------------------------- | -------------------- |
| Analytics        | MotherDuck (instant SQL)     | PostHog (dashboards) |
| Charts           | MotherDuck (sparklines)      | -                    |
| Data Exploration | MotherDuck (column explorer) | -                    |
| Buttons/Depth    | PostHog (Lemon UI)           | -                    |

### aleyum/ (Developer Portal)

| Feature    | Primary Inspiration      | Secondary                   |
| ---------- | ------------------------ | --------------------------- |
| Widgets    | PostHog (panel layout)   | MotherDuck (table explorer) |
| Monitoring | MotherDuck (diagnostics) | PostHog (insights)          |
| Agent Chat | PostHog (notebooks)      | -                           |

### códeolas/ (Code Intelligence)

| Feature      | Primary Inspiration    | Secondary |
| ------------ | ---------------------- | --------- |
| Code Display | MotherDuck (syntax)    | -         |
| Citations    | PostHog (source cards) | -         |
| Architecture | MotherDuck (CTE viz)   | -         |

---

## Screenshot Reference

All screenshots saved in `/sruth/ui-inspiration/`:

### Product UIs

- `motherduck-homepage.png` - Analytics platform design
- `posthog-homepage.png` - Product analytics with Lemon UI
- `duolingo-homepage.png` - Gamified language learning
- `khanacademy-homepage.png` - Educational mastery system

### Game UIs

- `hades-fight-ui.png` - Combat HUD design
- `hades-boons-ui.png` - Skill/boon selection interface
- `clair-obscur-hud.png` - Turn-based combat UI
- `clair-obscur-skill-tree.png` - Character progression
- `wow-ui-gallery.png` - MMO interface patterns

---

## Design System Recommendations

### Shared Color Tokens (Celtic Theme)

```css
/* Primary Nations */
--celtic-irish:
  emerald-600 --celtic-scottish: blue-600 --celtic-welsh: red-600
    --celtic-breton: purple-600 /* UI States */ --celtic-success: emerald-500
    --celtic-warning: amber-500 --celtic-error: rose-500 --celtic-info: sky-500
    /* Surfaces (Dark Mode First) */ --celtic-bg-primary: slate-900
    --celtic-bg-secondary: slate-800 --celtic-bg-tertiary: slate-700
    --celtic-glass: slate-800/90 /* Typography */ --font-display: "Cinzel",
  serif /* Headers */ --font-body: "Inter",
  sans-serif /* Content */ --font-mono: "JetBrains Mono" /* Code */;
```

### Component Patterns to Implement

1. **Tactile Buttons** (Duolingo-style): `border-b-4 active:border-b-2`
2. **Material Frames** (Clair Obscur): Slate textures with Ogham borders
3. **Progress Rings** (Khan): Circular mastery indicators
4. **Shadow-First HUD** (Hades): Dark base with vibrant accents
5. **Panel Layout** (PostHog): Resizable multi-column navigation

---

## Next Steps for Google Stitch

1. **Upload Screenshots**: Use these PNGs as visual references
2. **Reference This Guide**: Copy relevant sections for each project
3. **Generate Components**: Ask Stitch to create components matching specific inspirations
4. **Iterate**: Refine based on Celtic theme adaptations

---

_Generated by parallel agent research across 13 background tasks analyzing product and game UI patterns._
