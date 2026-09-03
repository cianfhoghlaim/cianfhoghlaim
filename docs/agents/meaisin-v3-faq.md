# meaisinfhoghlaim v3 — FAQ

> Per the meaisinfhoghlaim v5 umbrella spec. The canonical FAQ for
> meaisinfhoghlaim operators.

## Q: How do I add a new OCR/VLM model to the meaisinfhoghlaim v4 registry?

A: Follow the canonical 4-step pattern:

1. **Add the model entry to `meaisinfhoghlaim/models/registry.py`** as a new
   `OCRModel(...)` instance with the canonical `key`, `name`, `unsloth_id`,
   `mlx_id`, `upstream_id`, `backend`, `capabilities`, `m4_max_48gb_fit`, and
   `available` fields.
2. **Add the inference runner** to the appropriate backend submodule
   (e.g. `meaisinfhoghlaim/backends/llama_swap.py` for an Unsloth GGUF
   model, `meaisinfhoghlaim/backends/mlx.py` for an Apple-Silicon MLX
   model, etc.).
3. **Add the BAML Test block** to the meaisinfhoghlaim-specific BAML
   file (see `meaisin-v3-baml-client.md`).
4. **Run `cd baml_src && uv run baml-cli generate` + `cd baml_src && uv run baml-cli test`**.

## Q: How do I add a new document converter to the meaisinfhoghlaim document factory?

A: Follow the canonical 4-step pattern:

1. **Add the converter file** at
   `meaisinfhoghlaim/document_factory/converters/<name>_converter.py`
   with a `class <Name>Converter` that has a `convert(pdf_path)` method.
2. **Re-export the converter** in
   `meaisinfhoghlaim/document_factory/converters/__init__.py`.
3. **Register the converter** in `meaisinfhoghlaim/document_factory/__init__.py`
   `CONVERTERS = {"<name>": <Name>Converter(), ...}`.
4. **Run the suite of tests** to verify the conversion pipeline.

## Q: How do I add a new scanner domain (filesystem + language)?

A: See `meaisin-v3-systematic-download.md` for the full pattern. The
short version:

1. Add the per-source DLT sources in `dlt_sources/<domain>/<source>.py`.
2. Add the per-domain generic Dagster assets in
   `orchestration/defs/2_materials/<domain>_pipelines/generic_<domain>_assets.py`.
3. Add the per-domain monthly MotherDuck Flight in
   `motherduck/flights/<domain>_monthly_sync_flight.py`.
4. Add the per-domain MotherDuck Dive in
   `motherduck/dives/<domain>_sources_overview_dive.py`.

## Q: How do I add a new agent to the meaisinfhoghlaim 12-agent framework?

A: Follow the canonical 4-step pattern:

1. **Add the agent file** at `agents/meaisinfhoghlaim/<name>.py` with a
   `class <Name>Agent` that inherits from the canonical `Agent` base class.
2. **Register the agent** in `agents/meaisinfhoghlaim/registry.py` in
   `AGENTS = {"<name>": <Name>Agent(), ...}`.
3. **Add the agent's tools** to the canonical Tool registry.
4. **Run the agent's entrypoint** to verify the agent framework.

## Q: How do I run the meaisinfhoghlaim setup on a new machine?

A: Run the canonical operator surface:

```bash
mise run meaisin:v3:setup
```

This single command handles the entire meaisinfhoghlaim setup:
1. Checks Python version
2. Checks CUDA availability
3. Runs the 24-model registry audit
4. Runs the HF watchdog
5. Runs the OCR evaluation harness
6. Validates the 4 meaisinfhoghlaim openspec changes
7. Runs lint:skills

## Q: How do I check the meaisinfhoghlaim status?

A: Run the canonical operator surface:

```bash
mise run meaisin:v3:status
```

This shows the current state of:
- 24 OCR/VLM models × 4 backends
- 7 document converters
- RAGAS BIEP ensemble
- 4-path OCR ensemble
- 12 agents
- 31 mise tasks
- 4 active openspec changes

## Q: How do I check the meaisinfhoghlaim asset checks?

A: Run the canonical mise task:

```bash
mise run meaisin:v3:status
```

The status script verifies the 24-model registry + 7-converter + 12-agent
coverage + 4-openspec change validation.

## Q: How do I run a per-model OCR entrypoint?

A: Run the canonical mise task:

```bash
mise run meaisin:ocr:test:<model_key>
```

The 24 model keys are: `deepseek-ocr-2`, `docling-serve`, `dots-ocr`,
`gemma-3-4b`, `glm-4.6v-flash`, `internvl3-8b`, `llama-3.2-vision-11b`,
`molmo2-4b`, `molmo2-8b`, `olmocr-2-7b-1025`, `paddleocr-vl-1.6`,
`qwen3-vl-30b-a3b`, `qwen3-vl-4b`, `qwen3-vl-8b`, `qwen3.6-27b-mtp`,
`uccix-llama-3.1-8b`, `uccix-llama2-13b`, `uccix-mistral-24b`, `unstract-api`.

## Q: How do I add a new meaisinfhoghlaim BAML Test block?

A: See `meaisin-v3-baml-client.md` for the full pattern. The short
version:

1. Add the `test <function_name> { ... }` block to the
   meaisinfhoghlaim-specific BAML file.
2. Run `cd baml_src && uv run baml-cli generate` to compile.
3. Run `cd baml_src && uv run baml-cli test` to validate.

## Q: How do I add a new meaisinfhoghlaim changset-detection sensor?

A: Add a new file in `orchestration/sensors/<source>_sensor.py`. The
sensor should:

1. Use the canonical `@sensor` decorator + `SensorEvaluationContext`.
2. Use a cursor for incremental updates.
3. Return `RunRequest(run_key=..., tags={...})` per detected change.
4. The sensor is automatically picked up by the BIEP v3 orchestration
   walker.

## Q: How do I add a new infisical secret?

A: Add the secret to `.infisical.env` (the canonical template) and run
`mise run secrets:init` (which delegates to `scripts/init-vault.ts`).
The mise.toml + Infisical hydration handles the rest.

## Q: How do I roll back a meaisinfhoghlaim change?

A: Use git:

```bash
git revert <commit-hash>
git push
```

The meaisinfhoghlaim setup is reproducible from scratch — just delete
the `.venv/` + the `baml_client/` + the `.archive/meaisinfhoghlaim/`
and re-run `mise run meaisin:v3:setup`.

## Q: How do I report a bug?

A: File an issue at
https://github.com/cianfhoghlaim/cianfhoghlaim/issues with the
`meaisin` label. Include the output of `mise run meaisin:v3:status`
and the relevant asset check failure log.

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
