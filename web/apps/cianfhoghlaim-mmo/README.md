# Cianfhoghlaim Educational MMO

TanStack Start 2D client for the Cianfhoghlaim Educational MMO.
Bilingual EN + GA, focused on the 8 NCCA Leaving Certificate subjects.

## Subjects (8 NCCA realms)

| Slug | Subject (EN) | Subject (GA) | Route |
|:--|:--|:--|:--|
| `mathematics` | Mathematics | Matamaitic | `/realm/mathematics` |
| `applied_mathematics` | Applied Mathematics | Matamaitic Fheidhmeach | `/realm/applied_mathematics` |
| `chemistry` | Chemistry | Ceimic | `/realm/chemistry` |
| `geography` | Geography | Tíreolaíocht | `/realm/geography` |
| `history` | History | Stair | `/realm/history` |
| `english` | English | Béarla | `/realm/english` |
| `gaeilge` | Irish (Gaeilge) | Gaeilge | `/realm/gaeilge` |
| `computer_science` | Computer Science | Ríomheolaíocht | `/realm/computer_science` |

## Routes

| Path | Purpose |
|:--|:--|
| `/` | Landing page (NCCA-corpus hero, subject chooser) |
| `/realm/<subject>` | Subject realm (2D quest list + CopilotKit chat + quest pack UI) |
| `/student/<id>/badges` | Badge wallet (off-chain badges + on-chain anchor lookup) |
| `/student/<id>/mastery` | Cross-subject mastery dashboard (FalkorDB-backed) |
| `/teacher/<class>/quests` | Teacher view (marimo-embedded quest designer) |
| `/anchor/<date>` | Public Merkle-root proof page (verifies against Base L2) |

## Stack

- **TanStack Start** (file-based routing + SSR)
- **CopilotKit + AG-UI** (streaming agent chat)
- **Convex** (real-time state: `player_progress`, `quest_attempts`, `badges`)
- **TanStack Query** (read caches)
- **Hono** (write APIs; reuses `cianfhoghlaim/web/hono-api/`)
- **BetterAuth** (email/password + SIWE wallet)
- **BAML** (server-side, via Hono; never reaches the browser)

## Dev

```bash
bun install
bun run dev   # port 3080
```

## Reference

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D3)