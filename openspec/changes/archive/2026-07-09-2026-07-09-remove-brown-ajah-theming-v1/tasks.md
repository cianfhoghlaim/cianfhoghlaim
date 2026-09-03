# Tasks: 2026-07-09-remove-brown-ajah-theming-v1

## Phase 1 — OpenSpec artifacts (5 min)

- [x] 1.1 Create change directory: `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/`
- [x] 1.2 Write `proposal.md`
- [x] 1.3 Write `tasks.md` (this file)
- [x] 1.4 Write 3 spec delta files under `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/specs/`

## Phase 2 — Edit the 3 active specs + project.md (10 min)

- [x] 2.1 `openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` — REMOVE R7 + strip WoT body text (lines 43-46, 138-141)
- [x] 2.2 `openspec/specs/agentic-frontend-frameworks/spec.md` — REMOVE R6 + strip Theming/Tagline rows (lines 194-195, 217, 242-244)
- [x] 2.3 `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — KEEP R10 but REPHASE (remove WoT excerpts, Brown Ajah-only public theming line, Aes Sedai tagline scenario; lines 299-317, 329, 333)
- [x] 2.4 `openspec/project.md` — Update Plan 1.5 line (drop the "Brown Ajah of the Wheel of Time" phrasing)

## Phase 3 — Validate (1 min)

- [x] 3.1 `openspec validate 2026-07-09-remove-brown-ajah-theming-v1 --strict` passes
- [x] 3.2 `ccc search "Brown Ajah"` in the 3 cleaned specs returns 0 matches
- [x] 3.3 `ccc search "Wheel of Time"` in the 3 cleaned specs returns 0 matches
- [x] 3.4 `ccc search "Aes Sedai" "Amyrlin Seat" "Dragon Reborn" "Dragon Banner" "Tuatha'an"` in the 3 cleaned specs returns 0 matches
- [x] 3.5 `mise run lint:skills` still passes

## Phase 4 — Commit + push (5 min)

- [x] 4.1 Stage the 9 files (5 new + 4 edited)
- [x] 4.2 `git commit -m "chore(openspec): remove Brown Ajah / WoT theming from 3 active specs"`
- [x] 4.3 `git push` to `origin/pick-4-biep-v1`