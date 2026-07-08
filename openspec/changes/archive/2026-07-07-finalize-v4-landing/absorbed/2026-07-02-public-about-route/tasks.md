# Public /about route — tasks

## 1. Route files

- [ ] 1.1 Create `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/about.tsx` — the public About page in English.
- [ ] 1.2 Create `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/ga/about.tsx` — the Irish mirror of the About page.
- [ ] 1.3 Both routes must import `CiTextbookPanel`, `CiBoonsChoice`, `CiStreakFlame`, `CiDetailCell` from `@cianfhoghlaim/ui`.

## 2. Content

- [ ] 2.1 Render the Brown Ajah Wheel of Time theming summary (the 4 lore references — Aes Sedai, Amyrlin Seat, Dragon Reborn, Dragon Banner, Tuatha'an).
- [ ] 2.2 Render the 6 subnations (Éire, Northern Ireland, Scotland, England, Wales, Isle of Man) with v1-active + coming-soon badges.
- [ ] 2.3 Render the 13 éraic treasures (Pig of Dobar + Heifer of Dobar + Spear of Assal + Chariot of Sidrach + Sword of Caladbolg + 7 Pigs of Easmal + Whelp of Ioruaidh + Spit of Innis Cera + Helmet of Clochur + 3 Apples of the Hesperides + Pigskin Bag + Feather of the Bird of Crannog + Lugh's own samildanach).
- [ ] 2.4 Render the 5 NCCA Key Competencies (Communicating / Information Processing / Critical & Creative Thinking / Personal Effectiveness / Working with Others) with their Tuatha Dé Danann deity mapping.

## 3. Header nav

- [ ] 3.1 Add an `About` link to the `Header` component right-hand nav (next to the TranslationToggle).
- [ ] 3.2 Link to `/en/about` and `/ga/about` — language-aware (EN lang → `/en/about`, GA lang → `/ga/about`).

## 4. Validation

- [ ] 4.1 `openspec validate 2026-07-02-public-about-route --strict` passes.
- [ ] 4.2 `bun run typecheck` (or `tsc --noEmit`) passes for the new route files.
- [ ] 4.3 `curl http://localhost:3082/en/about` returns the HTML shell (the TanStack Router SPA fallback serves the index for any non-asset path).
- [ ] 4.4 Take a screenshot via the Chrome browser MCP at `http://localhost:3082/en/about` and confirm the 13 éraic + 6 subnations + 5 KC render.