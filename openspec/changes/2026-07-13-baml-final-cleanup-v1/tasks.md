# BAML final cleanup v1 — Tasks

## Step 1 — Refactor `clients.baml` to minimax-m3 default

- [x] Preserve the historical 8-generator setup as a comment block in `cianfhoghlaim/baml/clients.baml`.
- [x] Make `generator default` the only active text-extraction generator.
- [x] Point `default` at `minimax-m3` via `MINIMAX_BASE_URL` + `MINIMAX_API_KEY`.
- [x] Keep `local_vision_gemma4` active.
- [x] Keep `local_vision_qwen3vl` active.
- [x] Remove active Gemini and legacy local-vision text/vision generators that are not usable in the current environment.

## Step 2 — Update `baml.toml`

- [x] Set `[generators.lang_py].output_dir = "baml_client"`.
- [x] Set `[generators.lang_ts].output_dir = "baml_client_ts"`.

## Step 3 — Add Minimax-M3 env placeholders

- [x] Add root `.env.example` with `MINIMAX_BASE_URL` and `MINIMAX_API_KEY` placeholders.

## Step 4 — Fix `MarkingPoint` duplicate

- [x] Rename `education/_shared/strand_outcome.baml` class `MarkingPoint` to `MarkingPointStrand`.
- [x] Update `MarkingCriteria.marking_points` to use `MarkingPointStrand[]`.
- [x] Rename `education/pdfs/leaving_cert_marking_scheme.baml` class `MarkingPoint` to `MarkingPointSec`.
- [x] Update `MarkingSchemeSec.markingPoints` to use `MarkingPointSec[]`.

## Step 5 — Run BAML validation commands

- [x] `mise run baml:generate` run and captured.
  - Result: fails on pre-existing parser diagnostics outside this task's fix scope.
  - Baseline before cleanup: 50 file-level diagnostic groups.
  - After this cleanup: 47 file-level diagnostic groups remain (the clients.baml parser error and the two MarkingPoint duplicate groups were removed by the in-scope work; no new clients/MarkingPoint diagnostics were introduced).
- [x] `mise run baml:test` run and captured.
  - Result: fails before test execution on the same pre-existing parser diagnostics.

## Step 6 — Write scope decision

- [x] Add `SCOPE_DECISION.md` documenting the baseline 50 diagnostics, 3 scope options, recommendation, risks, and cost.
- [x] Recommend Option 1 (leave remaining errors to the BIEP v1 / dedicated BAML syntax cleanup owner) with Option 3 as a future small alternative.

## Step 7 — Write OpenSpec deltas

- [x] Add `specs/oideachais-baml-schemas/spec.md` with one ADDED requirement for the active single `minimax-m3` text generator.
- [x] Add `specs/british-isles-education-pipeline/spec.md` with one ADDED requirement for unique `MarkingPoint*` names.

## Validation

- [ ] `openspec validate 2026-07-13-baml-final-cleanup-v1 --strict` passes.
- [x] Exact `^class MarkingPoint\b` count is `0`.
- [x] Active `generator` definitions in `clients.baml`: `default`, `local_vision_gemma4`, `local_vision_qwen3vl`.

## Commit + push

- [ ] Commit on `pick-4-biep-v1` (NOT `main`).
- [ ] Push to `origin/pick-4-biep-v1`.
