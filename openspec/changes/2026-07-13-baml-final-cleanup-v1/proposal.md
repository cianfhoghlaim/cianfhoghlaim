# BAML final cleanup v1

## Why

The `pick-4-biep-v1` branch already shipped the main BAML+CocoIndex cleanup sequence in commits `1623849d9`, `476c866b8`, `49e0259a0`, `5e6734b57`, `93df30ebb`, and `78f2938ac`. This follow-up is intentionally small and handles the final low-risk items that were left behind after those commits.

The user clarified the production model constraint in the prior session: only **MiniMax-M3 via the coding plan API** is available for text extraction; other cloud-provider BAML generators should not remain active until credentials and access exist.

## What changes

1. **Minimax-M3 single text generator**
   - Refactor `baml/clients.baml` to make `generator default` the only active text-extraction generator.
   - Point `default` at `minimax-m3` via `MINIMAX_BASE_URL` + `MINIMAX_API_KEY` using the OpenAI-compatible `openai-generic` provider.
   - Preserve the historical 8-generator layout as line comments for future provider reactivation.
   - Keep the two local vision generators active: `local_vision_gemma4` and `local_vision_qwen3vl`.
   - Update `baml/baml.toml` output directories to `baml_client` and `baml_client_ts`.

2. **MarkingPoint duplicate fix**
   - Rename the cross-stage shared copy to `MarkingPointStrand`.
   - Rename the SEC marking-scheme PDF copy to `MarkingPointSec`.
   - Update local references in those files.

3. **50-error scope decision**
   - Add `SCOPE_DECISION.md` documenting the baseline BAML diagnostics, the in-scope cleanup effects, and the options for the remaining out-of-scope BAML syntax/duplicate failures.
   - Do **not** fix `lc_extraction/*.baml` or the broader pre-existing BAML syntax errors in this change.

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-11-baml-cocoindex-modernization-v1` (this is a cleanup follow-up to the BAML+CocoIndex modernization sequence).

`Blocked by (soft): 2026-07-12-baml-rename-42-duplicates-v1` (the MarkingPoint duplicate was the one missed duplicate from that rename strategy).

`Blocked by (soft): 2026-07-12-baml-type-builder-ncca-v1` (the remaining BAML syntax failures include NCCA/lc-extraction surfaces owned by adjacent BIEP work).

`Affected repos: cianfhoghlaim` (single-repo change; no `cross-repo-sync.md` required).

## Out of scope

- Do not modify the 7 `baml/education/lc_extraction/*.baml` files.
- Do not fix the remaining parser diagnostics in BAML subject packs, processing files, Celtic files, or archived files.
- Do not touch archived OpenSpec changes.
- Do not push to `main`.

## Validation plan

- `mise run baml:generate` — expected to fail on pre-existing BAML diagnostics; after this cleanup the clients/MarkingPoint diagnostics are removed and the remaining file-level diagnostic groups are still out of scope.
- `mise run baml:test` — expected to fail for the same pre-existing parser diagnostics before test execution.
- Exact MarkingPoint duplicate count: `^class MarkingPoint\b` should be `0`.
- `openspec validate 2026-07-13-baml-final-cleanup-v1 --strict` must pass.
