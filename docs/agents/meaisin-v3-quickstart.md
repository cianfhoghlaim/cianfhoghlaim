# meaisinfhoghlaim v3 — Quickstart

> Per the meaisinfhoghlaim v5 umbrella spec. The "first 30 minutes"
> guide for someone who has never seen the meaisinfhoghlaim OCR/HTR
> quadrant.

## Before you start

You'll need:
- **Python 3.12+** (`python3 --version`)
- **CUDA** (optional — for GPU acceleration; the OCR ensemble falls back to CPU)
- **mise** (the dev tool manager)
- **uv** (Python package manager — installed by mise)

## Step 1: Clone + bootstrap (2 minutes)

```bash
git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git
cd cianfhoghlaim
mise install
uv sync
```

## Step 2: Run the meaisinfhoghlaim setup (5 minutes)

```bash
mise run meaisin:v3:setup
```

This single command:
1. Checks Python version (>= 3.12)
2. Checks CUDA availability (optional)
3. Runs `mise run cic:meaisin:registry-audit` to verify the 24-model v4 registry
4. Runs `mise run cic:meaisin:hf-watchdog` to verify the HF watchdog
5. Runs `mise run cic:ocr:test` to verify the OCR evaluation harness
6. Validates the 4 active meaisinfhoghlaim openspec changes
7. Runs `mise run lint:skills` (53/53 pass)

## Step 3: Run the meaisinfhoghlaim status (30 seconds)

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

## Step 4: Run a per-model OCR entrypoint (deepseek-ocr-2)

```bash
mise run meaisin:ocr:test:deepseek-ocr-2
```

This runs the canonical 4-path OCR ensemble for the deepseek-ocr-2 model:
- Path 1 (BAML): Docling-serve → text → BAML deepseek-ocr-2
- Path 2 (Unstract): Docling-serve → Unstract workflow
- Path 3 (qwen3-vl): qwen3-vl-8b page-level image
- Path 4 (gemma4): gemma-4-26B-A4B page-level image

Each path output lands in its own per-jurisdiction DuckLake table.
Then the RAGAS `biiep_extraction_consensus` metric votes the canonical row.

## Step 5: Run a per-converter entrypoint (docling)

```bash
mise run meaisin:converter:test:docling
```

This runs the canonical document converter pipeline for the docling
converter (IBM Docling DocTags XML extraction).

## Step 6: Browse the 12 MotherDuck Dives

```
meaisin_ocr_registry_dive
meaisin_ensemble_audit_dive
meaisin_evaluation_summary_dive
meaisin_converter_coverage_dive
meaisin_converter_performance_dive
meaisin_converter_quality_dive
meaisin_agent_registry_dive
meaisin_agent_memory_dive
meaisin_agent_observability_dive
+ 3 more
```

## Step 7: Verify the meaisinfhoghlaim v5 system

```bash
# Total: 24 OCR models + 7 converters + 12 agents = 43 components
# Plus 4 BAML Test blocks + 24 model entrypoints + 7 converter entrypoints + 12 agent entrypoints

# Check the unified 24-model + 7-converter + 12-agent coverage
python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"
python3 -c "from meaisinfhoghlaim.document_factory import CONVERTERS; print(len(CONVERTERS))"
python3 -c "from agents.meaisinfhoghlaim.registry import AGENTS; print(len(AGENTS))"
```

## What to do next

- **Read the canonical docs**: `meaisin-v3-systematic-download.md` + `meaisin-v3-faq.md`
- **Browse the 12 MotherDuck Dives**
- **Explore the 24 per-model entrypoints** + 7 per-converter entrypoints
- **Run the canonical OCR evaluation harness**: `mise run cic:ocr:test`

## What to do if something goes wrong

| Symptom | Fix |
|:--|:--|
| `mise run meaisin:v3:setup` fails at step 3 (registry audit) | Run `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"` to see the registry |
| `mise run meaisin:v3:setup` fails at step 4 (HF watchdog) | Check the LLAMA-SWAP container is running |
| `mise run meaisin:ocr:test:<model>` fails at model extraction | Check the model is in the `VISION_MODELS` registry + the model's `available` flag is True |
| `mise run meaisin:converter:test:<converter>` fails at conversion | Check the converter is in the `CONVERTERS` registry + the converter's dependencies are installed |
| A BAML Extract* function raises an error | Check the test block in `meaisin-v3-baml-client.md` |

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-cron-schedule.md` — the 4-cadence meaisinfhoghlaim schedule
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
