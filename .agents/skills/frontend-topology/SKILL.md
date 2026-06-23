---
name: frontend-topology
description: Cross-cutting surface map for the Cianfhoghlaim monorepo. Use when "adding a new front-end surface", "choosing between TanStack, Convex, marimo, Babylon.js", or "debugging auth or data-plane routing". Covers 5 surfaces (oideachais/web, croilar/apps/web, croilar/apps/portal, tuatha/ui, marimo), 5 stacks, 5 auth models, 5 data planes.
---

# Front-end Topology

## When to use this skill

Use when you need to:

- "Add a new front-end surface (new app or microsite)"
- "Choose between TanStack, Convex, marimo, or Babylon.js for
  a new app"
- "Debug auth or data-plane routing across surfaces"
- "Understand 'where does oideachais/web end and croilar/apps/
  portal begin?'"
- "Onboard a new dev to the monorepo's front-end shape"

## The 5 surfaces

| Surface | Stack | Auth | Data plane | User |
|:--|:--|:--|:--|:--|
| `oideachais/web` | TanStack Start + Hono | **No auth** (public lakehouse) | `oideachais.education.ie.*` (DuckDB / MotherDuck) | Irish educators + students |
| `croilar/apps/web` | TanStack Start + Hono | **No auth** (public portfolio) | Convex (read-only) | Public visitors |
| `croilar/apps/portal` | TanStack Start + Hono + BetterAuth | **OAuth + SIWE + 2FA** | Convex (read-write) | The 3 personas (aleyum, cianfhoghlaim, carlcashman) |
| `tuatha/ui` | TanStack Start + Babylon.js | **SIWE** (Ethereum wallet) | Convex (real-time) + SpacetimeDB | Tuatha game players |
| `marimo` | marimo notebook | **No auth** (analyst-only) | DuckLake + MotherDuck (read) | KCG analysts (4 dev machines) |

## Per-surface detail

### oideachais/web — Lakehouse front-end

- **Path**: `oideachais/web/`
- **Stack**: TanStack Start + Hono (just expanded in
  `.agents/skills/tanstack-start/SKILL.md`)
- **Bun workspace**: `oideachais-web`
- **Auth**: **None** (per the root AGENTS.md rule; public
  lakehouse)
- **Data plane**: reads `oideachais.education.ie.*` from
  MotherDuck (`md:oideachais`)
- **Why this stack here but not in oideachais**: TanStack
  Start for the SPA experience; DuckLake as the source-of-
  truth backend. The web is a **read-only** viewer over
  the lakehouse.

### croilar/apps/web + croilar/apps/portal — Persona surfaces

- **Path**: `croilar/apps/web/` + `croilar/apps/portal/`
- **Stack**: TanStack Start + Hono + Convex
- **Auth**: web = none; portal = BetterAuth + Pocket ID + SIWE
  (per `.agents/skills/better-auth/SKILL.md`)
- **Data plane**: Convex (real-time, read-write)
- **Why two apps**: web is the public portfolio (no auth);
  portal is the authenticated persona dashboard (3 personas)

### tuatha/ui — Celtic MMO

- **Path**: `tuatha/ui/`
- **Stack**: TanStack Start + Babylon.js + Convex + SpacetimeDB
- **Auth**: SIWE (Sign-In With Ethereum, per
  `.agents/skills/better-auth/SKILL.md`)
- **Data plane**: Convex (real-time game state) +
  SpacetimeDB (settlement layer)
- **Why Babylon.js + TanStack Start**: the game client is
  Babylon.js (3D); the dashboard is TanStack (UI). Both share
  the TanStack Query client + the SIWE auth context.

### marimo — Analyst notebook surface

- **Path**: `oideachais/notebooks/`
- **Stack**: marimo + DuckDB / MotherDuck
- **Auth**: **None** (analyst-only; bound to the 4 dev machines
  via Pangolin)
- **Data plane**: DuckLake + MotherDuck (read-only)
- **Why marimo not TanStack**: marimo is **reactive Python**
  (cells re-run on dependency change); TanStack is **declarative
  TypeScript** (components re-render on state change). For data
  exploration, marimo's cell-level reactivity is a much better
  fit.

## Why this stack here but not in oideachais

- `oideachais/web` is a read-only viewer over the lakehouse
  (TanStack Start is the right choice)
- `croilar/apps/web` is a public portfolio (no auth, public
  read-only)
- `croilar/apps/portal` is the authenticated persona
  dashboard (BetterAuth, Convex for real-time)
- `tuatha/ui` is a 3D game (Babylon.js for the 3D, TanStack for
  the dashboard)
- `marimo` is the analyst notebook (reactive Python, no auth)

The pattern: **read-only public surfaces use TanStack Start
with no auth; read-write persona surfaces add BetterAuth +
Convex; game surfaces add Babylon.js + SpacetimeDB; analyst
surfaces add marimo**.

## Decision tree

```
New front-end surface?
│
├── Read-only public (no auth)
│   └── TanStack Start + Hono + MotherDuck
│       Example: oideachais/web
│
├── Read-write persona (auth required)
│   └── TanStack Start + Hono + BetterAuth + Convex
│       Example: croilar/apps/portal
│
├── 3D game (WebGL/WebGPU)
│   └── TanStack Start + Babylon.js + Convex + SpacetimeDB
│       Example: tuatha/ui
│
└── Analyst notebook
    └── marimo + DuckDB / MotherDuck
        Example: oideachais/notebooks
```

## Cross-references

- `.agents/skills/tanstack-start/SKILL.md` — the canonical
  TanStack Start reference
- `.agents/skills/marimo/SKILL.md` — the marimo reactive
  notebook surface
- `.agents/skills/babylonjs/SKILL.md` — the 3D game engine
- `.agents/skills/better-auth/SKILL.md` — BetterAuth + SIWE +
  Pocket ID
- `.agents/skills/convex/SKILL.md` — Convex real-time backend
- `.agents/skills/oideachais-storage/SKILL.md` — the
  oideachais storage mental model
- `docs/00-deploy-plans/0[1-5]*.md` — the 5 deploy plans
  that cite this topology
- `docs/00-architecture/STATUS.md` — the current state of
  each surface
