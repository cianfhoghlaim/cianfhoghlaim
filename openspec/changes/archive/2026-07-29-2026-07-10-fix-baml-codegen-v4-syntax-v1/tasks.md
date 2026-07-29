# Tasks — Fix BAML codegen v4-syntax-v1

## 1. Migration script

- [x] **1.1** Write `scripts/migrate-baml-syntax.py` (Python, ~280 lines) with
      `--dry-run`, `--apply`, `--verify` modes
- [x] **1.2** Implement the regex matching Pydantic-style `field: type` lines
      (handles primitives + custom classes + `[]` + `?` + `@description` attrs)
- [x] **1.3** Add defensive heuristics: skip lines inside `#"...content...#`
      raw-string blocks, `"""..."""` docstrings, and lines with `{{`/`}}`
      Jinja tokens
- [x] **1.4** Add `--verify` mode that exits 1 if any Pydantic-style lines
      remain in the 17 target files

## 2. Migrate the 17 processing files

- [x] **2.1** Run `uv run python scripts/migrate-baml-syntax.py --dry-run`
      to preview all 353 changes
- [x] **2.2** Run `uv run python scripts/migrate-baml-syntax.py --apply`
      to rewrite the 17 files in place
- [x] **2.3** Run `uv run python scripts/migrate-baml-syntax.py --verify`
      to confirm 0 Pydantic-style lines remain in the 17 target files

## 3. Hand-fix escape cases

- [x] **3.1** Fix `topic_profile.baml:25` — `@description("parties, politicians, organisations"]`
      → `@description("parties, politicians, organisations")`
- [x] **3.2** Fix `topic_profile.baml:65` — `@description("frameworks, libraries, protocols"]`
      → `@description("frameworks, libraries, protocols")`
- [x] **3.3** Fix `legal_case_profile.baml:59` — `@description("e.g. 'Irish Constitution Art. 40', 'Employment Equality Act 1998']`
      → `@description("e.g. 'Irish Constitution Art. 40', 'Employment Equality Act 1998'")`
- [x] **3.4** Spot-check 10-20 lines per migrated file to confirm no
      regressions (canonical syntax preserved + Jinja prompts intact)

## 4. Delete stale .bak files

- [x] **4.1** `find cianfhoghlaim/ -name "*.baml.bak" -exec rm {} +`
- [x] **4.2** Confirm both `clients.baml.bak` and
      `clients_llama_swap.baml.bak` are gone

## 5. Verify

- [x] **5.1** `mise run baml:generate` (or `cd cianfhoghlaim && uv run baml-cli generate`)
      to confirm partial improvement (~4,479 → ~1,742 errors) — full 0
      blocked on out-of-scope clusters (documented in proposal.md)
- [x] **5.2** The 7 BIEP v1 `lc_extraction/*.baml` files unchanged (verified
      Pydantic line counts: 28, 12, 18, 27, 15, 23, 15 — all preserved)
- [x] **5.3** `clients.baml` and `clients_llama_swap.baml` unchanged (T4's
      canonical `generator {}` blocks preserved)

## 6. OpenSpec change artefacts

- [x] **6.1** Create `openspec/changes/2026-07-10-fix-baml-codegen-v4-syntax-v1/`
- [x] **6.2** Write `proposal.md` (the 17 files + regex + scope)
- [x] **6.3** Write `tasks.md` (this file)
- [x] **6.4** Write `specs/cianfhoghlaim-baml-schemas/spec.md` delta
      (ADDED 2 Requirements, 16 → 18 total)
- [x] **6.5** Run `openspec validate 2026-07-10-fix-baml-codegen-v4-syntax-v1 --strict`
      — must pass before commit

## 7. Commit + push

- [x] **7.1** `git add -A` (script + 17 migrated .baml + openspec change + 2 deleted .bak)
- [x] **7.2** Commit with the conventional `fix(baml):` prefix
- [x] **7.3** Push to `origin/pick-4-biep-v1` (NOT `main`)

## Out of scope (deferred to follow-up openspec changes)

- The 7 `lc_extraction/*.baml` files (owned by BIEP v1 follow-up)
- The 8 `qpack_*.baml` files (owned by BIEP v1 follow-up)
- The 5 `education/_shared/*.baml` files (owned by BIEP v1 follow-up)
- The 3 `education/pdfs/*.baml` files (owned by pdfs cluster migration)
- The 2 `celtic/curriculum/*.baml` files (owned by celtic-cluster migration)
- The 10 OTHER `processing/*.baml` files (owned by future "fix-remaining-processing-cluster" change)