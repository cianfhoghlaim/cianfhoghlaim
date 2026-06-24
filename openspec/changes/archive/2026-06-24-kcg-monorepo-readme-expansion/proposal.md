# kcg-monorepo-readme-expansion

## Why

The 7 READMEs in the Cianfhoghlaim monorepo (root + 6
quadrant READMEs) currently have inconsistent structures:

- `README.md` (root, 655 lines) — has the 8-stream overview
  + the 3-way interaction diagram + a quickstart
- `infrastructure/README.md` (386 lines) — has a "Quick
  start" + the 94-stack inventory
- `oideachais/README.md` (674 lines) — has the lakehouse
  overview + the dlt × Dagster × CocoIndex matrix
- `meaisinfhoghlaim/README.md` (525 lines) — has the
  AI/ML overview + the 4 inference backends
- `tuatha/README.md` (834 lines) — has the MMO overview
  + the crypteolas achievement ledger
- `croilar/README.md` (819 lines) — has the 3-persona
  portfolio + the DevTools Hub
- `spaces/README.md` (157 lines) — has the 4-Space suite
  + the prior-art pattern catalogue

None of the 7 READMEs follow the canonical 6-section
structure (What lives here / Quick start / Key commands /
Common workflows / How to deploy / How to debug). None
have the end-to-end deploy playbook. None document the
canonical rollback procedure.

Round 13 of the multi-quadrant refactor plan unifies the
7 READMEs + creates a standalone `DEPLOY.md` via:

1. **6-section structure** — every README gains the 6
   canonical sections (in addition to the existing
   content; the existing content is preserved)
2. **8-phase end-to-end deploy playbook** — the root
   `README.md` gains the 8-phase playbook
   (pre-flight → infrastructure → oideachais →
   meaisinfhoghlaim → tuatha → croilar → spaces →
   verify → rollback)
3. **Standalone `DEPLOY.md`** — the end-to-end playbook
   is duplicated as a standalone ~800-line file
4. **1 openspec change** — `kcg-monorepo-readme-expansion`
   with 1 MODIFIED + 1 ADDED on `documentation` spec

The change is the 13th and final round of the
multi-quadrant refactor plan (rounds 7-13). Rounds 7-12
have already landed (infrastructure, meaisinfhoghlaim,
oideachais, tuatha, croilar, spaces).

## What changes

- `README.md` — adds the 6 sections + the 8-phase
  end-to-end deploy playbook (preserves the existing
  655 lines of content)
- `infrastructure/README.md` — adds the 6 sections
  (preserves the existing 386 lines of content)
- `oideachais/README.md` — adds the 6 sections
  (preserves the existing 674 lines of content)
- `meaisinfhoghlaim/README.md` — adds the 6 sections
  (preserves the existing 525 lines of content)
- `tuatha/README.md` — adds the 6 sections
  (preserves the existing 834 lines of content)
- `croilar/README.md` — adds the 6 sections
  (preserves the existing 819 lines of content)
- `spaces/README.md` — adds the 6 sections
  (preserves the existing 157 lines of content)
- `DEPLOY.md` — new standalone ~800-line file with
  the full end-to-end deploy playbook
- `openspec/specs/documentation/spec.md` — 1 MODIFIED
  + 1 ADDED requirement

## Impact

- **README consistency** — every README follows the
  same 6-section structure (the canonical Cianfhoghlaim
  README pattern)
- **End-to-end deploy** — the 8-phase deploy playbook
  is documented in the root README + the standalone
  `DEPLOY.md` (no need to grep 7 different files)
- **Rollback procedure** — the canonical rollback is
  documented (the 9th phase of the playbook)
- **Spec consistency** — the `documentation` spec gains
  1 MODIFIED + 1 ADDED requirement documenting the
  6-section README pattern + the standalone DEPLOY.md.
