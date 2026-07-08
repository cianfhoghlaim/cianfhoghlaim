# Public /about route — proposal

## Why

The Cianfhoghlaim OS needs a public landing surface that explains the
theming to a first-time visitor without exposing operator-only
lineage. Today the only public surfaces are:

- `/` (the landing tiles for the 6 subnations)
- `/en/map` (the British Isles map)
- `/en/key-competencies` (the 5 NCCA Key Competencies)
- `/en/leaving-cert/$subject` (the 8 NCCA LC subject shells)

None of them carries the **Brown Ajah Wheel of Time theming summary**
or the **13 éraic treasures** that anchor the
`docs/CIANFHLOGHLAIM_LORE.md` document. The lore document is
operator-only (per R10 of `cianfhoghlaim-leaving-cert-portal`); the
about route is the public mirror — it shows the Brown Ajah theming +
the 6 subnations + the 13 éraic treasures + the 5 NCCA Key
Competencies without exposing any personal lineage.

## What changes

1. New public route `/en/about` rendered by
   `apps/web/src/routes/en/about.tsx`.
2. New mirror route `/ga/about` rendered by
   `apps/web/src/routes/ga/about.tsx`.
3. The Header gets an `About` link in its right-hand nav (next to the
   TranslationToggle) — only the EN and GA about routes are linked
   (no operator-only docs).
4. The pages use the existing `@cianfhoghlaim/ui` components:
   `<CiTextbookPanel>`, `<CiBoonsChoice>`, `<CiStreakFlame>`,
   `<CiDetailCell>` — no new UI primitives.

## Privacy constraint

The about route renders **only** the Brown Ajah Wheel of Time
theming + the 13 éraic treasures + the 6 subnations + the 5 NCCA Key
Competencies. No personal lineage (Cian / Deacy / Lyons / Morris /
Conroy) appears. The route is publicly accessible (no auth required).
The `docs/CIANFHLOGHLAIM_LORE.md` is not linked from the page or the
Header.

## Non-goals

- No new UI components.
- No i18n infrastructure beyond the existing `en` / `ga` route mirrors.
- No new data sources — all lore facts are hard-coded in the route
  module.
- No operator-only facts (lineage, 3 Gemini Deep Research warrants).