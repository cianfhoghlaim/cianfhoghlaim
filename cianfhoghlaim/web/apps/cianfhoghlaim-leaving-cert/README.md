# Cianfhoghlaim Leaving Cert Portal

> The 5th canonical front-end surface — TanStack Start + CopilotKit v2 + AG-UI + Hono oRPC + Convex `conic-leaving-cert` + Brown Ajah Wheel of Time theming + accurate British Isles map (6 subnations).

## Stack

| Layer | Choice |
|:--|:--|
| Front-end | TanStack Start (Vite plugin) + file-based routing + (en)/(ga) bilingual groups |
| Agent UI | CopilotKit v2 Factory Mode + AG-UI SSE streaming + `<CopilotSidebar>` |
| Window manager | Cianfhoghlaim OS (PostHog-style + Framer Motion physics) |
| Realtime backend | Convex (fresh standalone `conic-leaving-cert` deployment, 5 carried-over + 3 new tables) |
| API gateway | Hono + oRPC + BetterAuth + Pocket ID OIDC + optional SIWE |
| Diagram renderer | React Flow + D3 v8 + Babylon.js + `<model-viewer>` |
| Data plane | MotherDuck (read-only lakehouse) + Convex (read-write persona) |
| Auth | BetterAuth (email/password + OAuth) backed by Pocket ID OIDC; optional SIWE |
| User | Irish educators + students |
| Map | Accurate British Isles (OpenStreetMap base) split into 6 subnations |
| Theming | Brown Ajah of the Wheel of Time (healers, scholars, Earth-workers) |
| Tagline | "Aes Sedai — servants of all" (the Brown Ajah motto) |

## Setup

```bash
cd cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert
bun install
bun run dev
```

## Architecture

See [`docs/CIANFHLOGHLAIM_LORE.md`](./docs/CIANFHLOGHLAIM_LORE.md) (operator-only)
and the openspec change
[`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`](../../../openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/).

## Specs

- [`cianfhoghlaim-leaving-cert-portal`](../../../openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md) — the canonical spec
- [`retro-game-asset-pipeline`](../../../openspec/specs/retro-game-asset-pipeline/spec.md) — the 2D + 3D asset generator
- [`ncca-leaving-cert-root-pdfs`](../../../openspec/specs/ncca-leaving-cert-root-pdfs/spec.md) — the 5 NCCA root-level PDFs
- [`cianfhoghlaim-educational-mmo`](../../../openspec/specs/cianfhoghlaim-educational-mmo/spec.md) — the 8 NCCA ADK specialists
- [`agentic-frontend-frameworks`](../../../openspec/specs/agentic-frontend-frameworks/spec.md) — the 5th canonical surface (R5) + Celtic UI Design System (R6) + Brown Ajah theming (R7)

## Theming inputs

- 7 lineage clippings at `../../../../cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` (operator-only — NEVER on public surface)
- 145 comic reference images at `../../../../docs/comics/` (the celtic-art reference library)
- 11 UI inspiration files at `../../../../docs/ui-inspiration/` (the design system)
- 4 Wheel of Time excerpts (Aes Sedai / Amyrlin Seat / Dragon Reborn / Tuatha'an)

## License

BUSL-1.1 — non-commercial, cultural preservation, and academic research use permitted within Ireland, UK, EU, Commonwealth, and aligned jurisdictions.