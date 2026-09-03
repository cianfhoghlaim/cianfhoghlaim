# Tasks for 2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1

- [x] T1.1: Re-read the previous 1096-line `README.md` (commit `7184745bd^`) and `leabharlann/README.md` to confirm all restored numbers and links are still accurate post-2026-08-19.
- [x] T1.2: Verify each credential PDF in the 12-row table exists at the linked path under `cian_mac_an_déisigh_uí_liatháin/`. **(14 file paths verified; 12-row table with 2 rows referencing 2 files each)**
- [x] T1.3: Verify each leabharlann subdir in the 7-row table exists under `leabharlann/`. **(7/7 match `ls leabharlann/*/` exactly: gaeilge, aigne, mata, ollscoil_na_gaillimhe, zotero, gemini_deep_research, saontacht_oideachais)**
- [x] T1.4: Write the new root `README.md` (~440 lines) per the 19-row section table in the proposal. **(Final: 485 lines)**
- [x] T1.5: ADDED Requirement to `openspec/specs/centralize-cross-cutting-docs/spec.md` (the `Root README depth and discoverability` block + 5 Scenarios).
- [x] T1.6: `openspec validate 2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1 --strict` — **PASSED** (exit 0).
- [ ] T1.7: `mise run lint:drift-docs` — **5 PRE-EXISTING violations** in agents/tuatha/AGENTS.md, bonneagar/AGENTS.md (×3), and notebooks/AGENTS.md — none introduced by this change. The linter only audits the 16 AGENTS.md files (not README.md); this change touches only README.md + the openspec change dir. **No new drift introduced.**
- [x] T1.8: `wc -l README.md` — **485 lines** (within the 400–500 inclusive target).
- [x] T1.9: Manually click every relative link from the new root `README.md` — **every file path resolves** and **every anchor slug resolves** to a real heading (verified via Python slugifier). Fixed 1 stale openspec directory link during verification.
