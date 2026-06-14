---
title: 'Front-end Topology'
domain: 'web'
status: 'stable'
description: 'Which front-end surface lives where, what stack it uses, how it authenticates, and which data plane it reads from. The 5 quadrants have 5 different front-end shapes.'
read_when:
  - adding a new front-end surface
  - choosing between TanStack, Convex, marimo, Babylon.js
  - debugging auth or data-plane routing
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - front end topology tanstack convex marimo babylon
---

# Front-end Topology

> **One page for the whole monorepo's front-end story.** The 5 quadrants
> have 5 different front-end shapes; the doc below maps them.

| Surface | Stack | Auth | Data plane | Use case |
|---|---|---|---|---|
| `oideachais/web` | TanStack Start | **none** (lakehouse front-end) | DuckLake / MotherDuck via `oideachais/api/` | Public-facing research UI for the unified lakehouse |
| `croilar/apps/web` | TanStack + Hono | none | Convex (TanStack queries) | Public multi-persona portfolio |
| `croilar/apps/portal` | TanStack + Hono + Convex | **BetterAuth + Pocket ID SSO + SIWE (crypto wallet)** | Convex + DuckLake | Authenticated developer portal for the operator (Cian) |
| `tuatha/ui` | **Babylon.js** (not TanStack) | in-game Crypteolas token | SpacetimeDB (real-time) + DuckLake (premium) | The Celtic MMO game client |
| marimo (any stack) | marimo server | none (analyst UI) | DuckLake / MotherDuck via MCP | Analyst dashboard / exploratory notebook |

## `oideachais/web` (the lakehouse front-end)

- **Stack**: TanStack Start (SSR React). No auth.
- **Data plane**: `oideachais/api/ducklake_reader.py` reads from
  `md:oideachais` (MotherDuck).
- **Why no auth**: the data is non-sensitive (public NCCA, SEC, DfE,
  etc.). Adding auth would break the research ergonomics.
- **Deploy**: `infrastructure/stacks/engineering/oideachais/` (the
  canonical stack per `infrastructure/AGENTS.md`).
- **Phase 5+ migration in flight**: a TanStack+Hono+Convex auth
  pattern may be adopted *if* the LC 2026 portal surface (private
  per-user data) lands here. For now it stays bare.

## `croilar/apps/web` + `croilar/apps/portal`

- **Stack**: TanStack (both surfaces) + Hono (BFF in both) +
  Convex (database for `croilar/apps/web`; query layer for `croilar/apps/portal`).
- **Auth**:
  - `croilar/apps/web`: **none**. The portfolio is public.
  - `croilar/apps/portal`: **BetterAuth + Pocket ID SSO** (the
    monorepo-wide OIDC provider at `infrastructure/stacks/infrastructure/pocket-id/`)
    + **SIWE** (Sign-In-With-Ethereum, for the crypto-wallet-bound
    persona).
- **Data plane**:
  - `croilar/apps/web`: Convex (TanStack queries against the
    Convex backend at `infrastructure/stacks/engineering/convex/`).
  - `croilar/apps/portal`: Convex + DuckLake (the operator can
    pull a private Convex view of their data joined with the
    unified lakehouse).
- **Why this stack here but not in oideachais**:
  - croilar is the *reference implementation* of the full monorepo
    pattern (Convex + auth + Hono + DuckLake). oideachais is the
    *data* quadrant; the auth pattern lives in croilar and can be
    adopted into oideachais if needed.

## `tuatha/ui` (the MMO)

- **Stack**: Babylon.js + SpacetimeDB. **Not TanStack.**
- **Auth**: in-game Crypteolas token (an ERC-20 with EIP-2612 + EIP-3009
  for x402 micropayments). See
  [`docs/06-product/crypteolas.md`](../06-product/crypteolas.md).
- **Data plane**:
  - SpacetimeDB (real-time game state).
  - `oideachais/` (DuckLake) for premium content served via x402
    payment-protected endpoints (the Axum Rust service).
- **Why Babylon.js**: it is the canonical 3D browser game engine in
  the monorepo. The Godot client (`tuatha/Hades II/`) uses
  `gdext` to share Rust code with the Axum backend.

## marimo (any stack)

- **Stack**: marimo server (Python).
- **Auth**: none. The analyst UI is open.
- **Data plane**:
  - Local dev: `duckdb :memory:` with `ATTACH 'oideachais' (DUCKLAKE)`.
  - Public: `md:oideachais` via the motherduck MCP.
  - **Read-only**: marimo does *not* write to the lakehouse. It
    reads from it. Writes go through Dagster + DLT.
- **Where it lives**:
  - `infrastructure/stacks/engineering/marimo/` (the
    standalone marimo stack).
  - `oideachais/notebooks/dashboards/*` (per-nation / per-domain
    dashboards, e.g. `all_nations.py`, `registers.py`).
- **Why marimo over Jupyter**: marimo is reactive; the notebook
  re-evaluates on data change. Jupyter is one-shot.

## Decision tree (which front-end to use?)

```
What are you building?
│
├── A new dashboard over the lakehouse
│     → marimo + oideachais/notebooks/dashboards/<domain>/<nation>.py
│
├── A new public-facing research page on the unified lakehouse
│     → oideachais/web (TanStack Start, no auth)
│
├── A new public-facing persona/portfolio surface
│     → croilar/apps/web (TanStack + Convex, no auth)
│
├── A new authenticated developer / operator surface
│     → croilar/apps/portal (TanStack + Hono + Convex + BetterAuth)
│
├── A new game-side surface
│     → tuatha/ui (Babylon.js + SpacetimeDB + Crypteolas)
│
└── A new agent that needs a UI
      → use the AGNO / ADK agent runtime (no front-end); the
        agent skill returns a text response.
```

## See also

- [`docs/05-web/frontend-stack.md`](frontend-stack.md) — TanStack + Hono + Convex
- [`docs/05-web/convex-hono-auth.md`](convex-hono-auth.md) — auth pattern
- [`docs/06-product/educational-platform.md`](../06-product/educational-platform.md)
- [`docs/06-product/celtic-mmo.md`](../06-product/celtic-mmo.md)
- [`docs/06-product/crypteolas.md`](../06-product/crypteolas.md)
- [`oideachais/web/`](../../oideachais/web/) — the lakehouse front-end
- [`croilar/apps/`](../../croilar/apps/) — the multi-persona surface
- [`tuatha/ui/`](../../tuatha/ui/) — the MMO client
- [`infrastructure/stacks/engineering/marimo/`](../../infrastructure/stacks/engineering/marimo/) — the marimo stack
