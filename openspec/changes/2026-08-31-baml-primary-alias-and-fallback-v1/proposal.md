# Change: BAML Primary Alias + Per-Function Fallback Chains v1

> **Status:** AUTHORED, ready for execution.
>
> **Phase 2 of 6** in the v5 refactor umbrella.
>
> **Anchors:** the `Primary` alias + 3 concrete backends (`MiniMaxPrimary`,
> `UnslothGemma4`, `VertexGemini35Flash`) added by Phase 1 in
> `baml_src/clients.baml`. This change wires the per-function
> `fallback` chains across the canonical BIEP functions + adds a
> `mise run baml:switch-primary` + `mise run baml:list-models`
> helper for runtime model swaps.

## Why

Phase 1 added 7 new concrete BAML clients + a `Primary` alias +
`MODEL_PROFILE` env var. The clients are wired but no function
declares a `fallback` chain yet — every BAML function in
`baml_src/**` still hardcodes `client "ExtractEn"` (or one of the
11 other aliases). The 3 switching knobs (env-driven primary /
per-function override / per-function fallback chain) are documented
in `baml_src/clients.baml` but only knob (b) — the per-function
override — is wired today (via `GaeilgeLCClient`).

This change wires knob (c) — the per-function `fallback` chain — for
the 4 canonical BIEP v3 extraction functions + adds the 2 mise
tasks that make knob (a) (env-driven primary) usable from the CLI.

## What changes

### §1 — `mise run baml:switch-primary` task

- One-liner: `mise run baml:switch-primary --model minimax-m3` (or
  `gemma-4-26b-a4b` / `gemini-3.5-flash`).
- Updates `MODEL_BASE_URL` + `MODEL_API_KEY` + `MODEL_PRIMARY` in
  `.infisical.env` via `mise env set`.
- Prompts the operator to restart any running BAML daemons.

### §2 — `mise run baml:list-models` task

- Lists the 7 concrete clients + their `base_url` + `model` strings
  from the `baml_client` Python module.
- Reads the `baml_client.config` for the resolved client set.

### §3 — `baml_src/_shared/templates/primary_alias_with_fallback.baml`

- A canonical template BAML function that every jurisdiction-specific
  BAML file copies into its header section.
- Shows the canonical fallback chain `Primary -> UnslothGemma4 ->
  VertexGemini35Flash` pattern.
- Comments explain when to use `GaeilgeLCClient` instead of `Primary`.

### §4 — 4 canonical BIEP v3 extraction functions get explicit fallback chains

The 4 lc6 extraction functions + the 3 BIEP v3 helper functions get
explicit `fallback` chains wired:

```baml
function ExtractCurriculumSyllabus(...) -> Syllabus {
  client "Primary"
  prompt #" ... "#
  fallback    "UnslothGemma4"
    "VertexGemini35Flash"
}
```

### §5 — 8 generic alias clients get cleaned up

The 8 generic aliases (`Extractor`, `ExtractorFast`, `FastAnalyzer`,
`FastExtraction`, `Gemini2FlashAlias`, `LiteLLM`, `OideachaisDefault`,
`ArtworkAnalyzer`, `CelticContentFallback`, `ClaudeHaiku`) keep their
M3 chokepoint wiring but add a `# 2026-08-31: use `Primary` for new
code` comment.

### §6 — `scripts/baml_audit_fallbacks.py` (new)

CI gate that fails if any BAML function in `baml_src/**` is missing
a `fallback` block (with a small exception list: `TestMock`, the
GaeilgeLC helper, the 5 tuatha_media_intel helpers,).

## Impact

- 1 new file: `scripts/baml_audit_fallbacks.py`
- 1 new file: `baml_src/_shared/templates/primary_alias_with_fallback.baml`
- 2 new mise tasks: `baml:switch-primary`, `baml:list-models`
- 7 BIEP v3 functions get explicit `fallback` blocks
- 8 generic aliases get `# use Primary for new code` comments
- 0 breaking changes (the fallback chain is a non-breaking additive)

## Dependencies

- Phase 1 (`2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1`) —
  the `Primary` alias + 7 concrete clients are prerequisites.
- `centralized-model-registry` spec — `MODEL_REGISTRY.resolve(family,
  role)` is the runtime API for the `baml:switch-primary` task.

## Out of scope

- Re-wiring all 558 BAML functions (this is the 4 canonical +
  8 alias-only scope; the wider migration is the
  `2026-08-31-baml-quality-bulk-sweep-v1` follow-up change).
- The per-function `client "GaeilgeLCClient"` overrides (already
  done; no change needed).

## Quality gates (must pass before archive)

```bash
mise run openspec:validate 2026-08-31-baml-primary-alias-and-fallback-v1 --strict
mise run baml:generate     # regenerates baml_client/ from the new templates
mise run baml:test         # 558 BAML functions pass
uv run python scripts/baml_audit_fallbacks.py --strict   # 0 drift
```

---

*Last updated by build subagent at 2026-08-31.*