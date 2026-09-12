# Restore the depth of the root `README.md` and cross-link to the `leabharlann/` corpus + the personal credential corpus

## Why

The 2026-08-19 commit `9484e397f` rewrote the root `README.md` against verified reality and shrank it from **1020 → 210 lines**. The rewrite fixed real drift (5 wrong paths in the topology tables — `baml/`, `dlt/`, `libraries/codeolas/`, `spaces/`, plus a web app that never existed — the openspec count that said `~45` in prose and `8` in code, the CocoIndex → `cocoindex_flows/` rename, and the agent-fleet table that named 2 stale + 2 missing agents), but the side effect was to demote the **personal credential corpus** + the **family-history narrative** + the **leabharlann subdir breakdown** out of the root.

The credential table now lives at [`cian_mac_an_déisigh_uí_liatháin/README.md`](../../cian_mac_an_déisigh_uí_liatháin/README.md) (25 lines) and the family-history narrative at [`cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`](../../cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md) (619 lines). Neither is discoverable from the root without scrolling-and-clicking, and the user (the author) explicitly wants the root to walk a new visitor through the project as an integrated system — not just hand them a topology table and link out.

The user confirmed the four preferences that anchor this change:

1. **Hybrid restoration** — ~440-line root README (vs the 210-line lean rewrite and the 1096-line pre-rewrite). Restore the depth, but keep verified-reality correctness.
2. **Linked pointer** for credentials + family history — the root carries a curated table + a 1-paragraph Triple-Crown summary; the long-form files remain the single source of truth.
3. **Per-subdir leabharlann summary** in the root — a 7-row table mirroring the 7 top-level subdirs (`gaeilge/`, `aigne/`, `mata/`, `ollscoil_na_gaillimhe/`, `zotero/`, `gemini_deep_research/`, `saontacht_oideachais/`).
4. **Agent fleet stays as a 2-sentence pointer** (not a full 12+8 table).

## What changes

Restore the root [`README.md`](../../README.md) to ~440 lines with the 19-row section table laid out in the plan:

| § | Section | Source | Action |
|---|---|---|---|
| 1 | Title, blurb, badges | `prev_readme.md:1-8` | Restore the `v7 flat` badge |
| 2 | External companion resources | `prev_readme.md:10-19` | Restore the `iximiuz Labs` + `DBQuacks` references |
| 3 | Mise Tasks priority quick reference | `prev_readme.md:21-33` | **Restore** — was deleted by `7184745bd` + `9484e397f` |
| 4 | Addendum — A note for anyone looking at this project right now | `prev_readme.md:35-93` | **Restore** the full discursive addendum |
| 5 | ⚠️ Important Disclaimer | `prev_readme.md:96-114` | Keep, lightly trim |
| 6 | TL;DR — what this is, today | `prev_readme.md:368-399` | **Restore** the 5-step flow + credentials paragraph |
| 7 | Centralized Registries | `prev_readme.md:400-444` | **Restore** the 4 + 4 canonical artifacts + code patterns |
| 8 | Monorepo Topology (v7) | `prev_readme.md:448-490` | **Restore** in fuller form with verified sub-tables |
| 9 | The 5-stage architecture | `prev_readme.md:509-521` | **Restore** with the new `4_budget/` + `4_memory/` siblings |
| 10 | British Isles Education Pipeline (BIEP) — the flagship | `prev_readme.md:523-535` | **Restore** |
| 11 | The agent fleet | current rewrite lines 139-143 | Keep as **pointer** (per user choice) |
| 12 | Personal credential corpus (verified references) | `prev_readme.md:562-585` | **Restore as a linked pointer** — 12-row table inline + pointer to `cian_mac_an_déisigh_uí_liatháin/README.md` |
| 13 | Verified academic archive (leabharlann) | new content + `leabharlann/README.md:43-220` | **Restore + expand** — 7-row per-subdir summary + the 7 culture-PDF warrants |
| 14 | Family history | current rewrite lines 196-202 | **Strengthen** — 1-paragraph Triple-Crown summary + link to deep narrative |
| 15 | Repository constellation | `prev_readme.md:602-612` | **Restore** the 3-row table |
| 16 | Cross-cutting concerns | `prev_readme.md:614-642` | **Restore** in compacted form |
| 17 | Licensing | `prev_readme.md:644-655` | **Restore** the full 17-item jurisdiction list |
| 18 | Quick Start for new operators | `prev_readme.md:117-366` | **Defer** to `AGENTS.md` + per-stack READMEs |
| 19 | Agent telemetry block | current rewrite lines 204-209 | Keep (machine-readable) |

**Total target: ~440 lines** (within the user's chosen hybrid range).

## What does NOT change

- The web/ + python/ + IaC topology tables use the **verified** subdirectory names from the 2026-08-19 rewrite (`cocoindex_flows/`, 13-agent registry, 96 specs).
- The **agent fleet section stays as a 2-sentence pointer** (per user preference; the full 12-agent table is already in `agents/README.md` + `agents/AGENTS.md`).
- The Pocket ID + Tuatha onboarding Quick Starts (8 sections each, ~250 lines) stay in `bonneagar/README.md` and `tuatha/README.md` respectively, not in the root.
- The 619-line family history narrative stays as a separate file (`cian_mac_an_déisigh_uí_liatháin/FAMILY_HISTORY.md`); only the 1-paragraph summary moves into the root.
- The four post-rewrite hub READMEs (`agents/README.md`, `orchestration/README.md`, `meaisinfhoghlaim/README.md`, `bonneagar/README.md`) are not touched.

## Dependencies

`Blocked by: none`
`Blocked by (soft): none`
`Affected repos: cianfhoghlaim` (single-repo docs change)

## Verification

- `openspec validate 2026-08-19-readme-restore-depth-and-cross-link-to-leabharlaim-v1 --strict` MUST pass.
- `mise run lint:drift-docs` MUST stay clean (the new sections don't introduce any number claims that contradict ground truth).
- `wc -l README.md` MUST land in the 400-500 range.
- Every link from the root `README.md` to a sub-README MUST resolve to an existing file in the working tree at the same commit.
- The 12-row credential table in the root + the 12-row credential index in `cian_mac_an_déisigh_uí_liatháin/README.md` MUST list the same set of credentials.
- The 7-row leabharlann subdir table in the root MUST match `ls leabharlann/` exactly.
