# 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1

## Why

The Cianfhoghlaim OCR/VLM stack today is a mature but unfederated set of 6
classical OCR Docker stacks (docling-serve + paddleocr + tesseract +
tesseract-shadow + unstract + dots-ocr) plus 24 VLM models across 4 backends
(litellm / mlx / transformers / llama-swap) at
`meaisinfhoghlaim/models/registry.py:VISION_MODELS`. There is no canonical
way for a BAML function to invoke any of them. Each tool is reached via its
own bespoke integration. The 2 BIEP v2 pipelines from Changes 1 + 2
(Junior Cycle + England AQA/OCR/Edexcel) both need:

- **Docling** for layout-aware PDF parsing (the "safety net" first stage)
- **Unstract** as a parallel-path extraction backend (the non-engineer UI
  for authoring per-doc-type prompts in Unstract Prompt Studio)
- **2 vision LLMs in ensemble** (qwen3-vl-8b workhorse + gemma-4-26B-A4B
  MoE M4-default) for scanned PDFs where Docling falls below 0.85 confidence
- **RAGAS-voted consensus** to merge all 4 paths into a canonical
  BAML-validated output

This change **unifies all of this** into a single canonical OCR ensemble
pipeline that both Changes 1 + 2 (and any future BIEP v2 jurisdiction) plug
into. Specifically, it:

- Extends the v4 OCR/VLM registry from 24 → **26 models** and 4 → **6 backends**
  (adding `DOCLING` for the Docling HTTP API + `UNSTRACT` for the Unstract
  REST API; both first-class `ModelBackend` enum values per the spec
  "synchronous with the registry")
- Declares 2 new `ModelCapability` enum values:
  - `UNISTRUCT_WORKFLOW` — for the Unstract Prompt Studio workflow
  - `DOCLING_LAYOUT` — for the Docling DocTags output
- Adds 2 BAML clients (`Docling` + `Unstract`) in `baml_src/clients.baml` so
  any BAML function can select them as a fallback
- Adds the `EnsembledExtractor` class in
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` that runs the 4
  paths in parallel and votes via RAGAS
- Adds 3 Unstract workflows in `bonneagar/stacks/unstract/workflow_data/`:
  - `aqa_gcse_spec.json` (for Change 2's England pipeline)
  - `ncca_jc_cba.json` (for Change 1's JC pipeline)
  - `sec_lc_marking.json` (for the existing BIEP v1 LC pipeline)
- Adds 1 Dagster asset `biiep_ocr_ensemble` and 1 RAGAS evaluation harness
  in `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py`
- Registers 2 new entries in the registry
  (`unstract-api` and `docling-serve`)

This is the convergence layer that makes the 2 parallel BAML + Unstract
outputs land in DuckLake (per the user's chosen strategy "Both outputs land
in DuckLake, RAGAS scores them"), and lets a downstream Dagster asset
materialise the canonical row by picking the higher-scoring run.

## What changes

### 1. Extended OCR/VLM registry

`meaisinfhoghlaim/models/registry.py` — extended from 24 → **26 models**
and 4 → **6 backends**:

- Add `ModelBackend.DOCLING = "docling"` enum value
- Add `ModelBackend.UNSTRACT = "unstract"` enum value
- Add 2 new `VISION_MODELS` entries:
  - `unstract-api` → backend `UNSTRACT`, port 8000, capabilities
    `[DENSE_OCR, TABLES, MULTILINGUAL, UNISTRUCT_WORKFLOW]`
  - `docling-serve` → backend `DOCLING`, port 5001, capabilities
    `[DENSE_OCR, TABLES, LATEX, DIAGRAM, DOCLING_LAYOUT]`
- Add 2 new `ModelCapability` enum values:
  - `UNISTRUCT_WORKFLOW = "unstract_workflow"` — invoked when the document
    has a hand-authored Unstract workflow
  - `DOCLING_LAYOUT = "docling_layout"` — invoked when the document has
    DocTags XML output (preserves layout + tables + equations)

### 2. Extended BAML clients

`baml_src/clients.baml` — add 2 new clients:

```baml
client<llm> Docling {
  provider docling
  options {
    endpoint: env.DOCLING_URL  // default: http://localhost:5001
    output_format: doc_tags_xml
  }
}

client<llm> Unstract {
  provider unstract
  options {
    endpoint: env.UNSTRACT_API_URL  // default: http://localhost:8000/api/v1
    workflow_id: env.UNSTRACT_WORKFLOW_ID  // set per-doc-type
  }
}
```

The `england_education.baml` `ExtractEnglandEnsembleConsensus` from
Change 2 already declares these as the inputs to its ensemble function;
this change extends `clients.baml` to make them real.

### 3. Ensemble extractor

`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` — new `EnsembledExtractor`
class with the following API:

```python
class EnsembledExtractor:
    def __init__(self, docling_url, unstract_url, qwen3_vl_endpoint, gemma4_endpoint):
        ...

    def extract(
        self,
        pdf_path: str | Path,
        baml_function: str,         # e.g. "b.ExtractJCCurriculum"
        unstract_workflow_id: str | None = None,
        ragas_threshold: float = 0.85,
    ) -> EnsembleResult:
        """Run all 4 paths in parallel, return EnsembleResult.

        Each path's output lands in the per-jurisdiction DuckLake
        `cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.<path>`
        table (per the per-path DuckLake landing convention from the
        user's chosen strategy).

        EnsembleResult carries:
        - baml_canonical: the BAML function output (default canonical)
        - docling_text: the DocTags XML (first path)
        - unstract_json: the Unstract JSON (second path)
        - qwen3_vl_response: the qwen3-vl-8b raw response (third path)
        - gemma4_response: the gemma-4-26B-A4B raw response (fourth path)
        - ragas_score: dict per path
        - voted_output: the RAGAS-voted canonical BAML object
        """
```

The voting strategy: RAGAS `biiep_extraction_consensus` metric ranks the 4
outputs by 3 sub-metrics (faithfulness, completeness, schema-conformance)
and returns the highest-scoring output as `voted_output`.

### 4. New Dagster asset + RAGAS harness

- **1 Dagster asset** `biiep_ocr_ensemble` at
  `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py`
  — the orchestrator that runs `EnsembledExtractor.extract()` for any
  incoming PDF and writes the 4 outputs + the voted canonical row
- **1 RAGAS evaluation harness** at
  `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py` — registers the
  `biiep_extraction_consensus` metric in MLflow; the canonical RAGAS
  metric contract is `faithfulness`, `answer_relevance`, `context_precision`

### 5. Three Unstract workflows

`bonneagar/stacks/unstract/workflow_data/` (the canonical Unstract
filesystem):

- `aqa_gcse_spec.json` — AQA GCSE specification extraction (used by Change 2)
- `ncca_jc_cba.json` — NCCA Junior Cycle CBA descriptor extraction (used by Change 1)
- `sec_lc_marking.json` — SEC Leaving Certificate marking scheme extraction (used by BIEP v1 LC)

Each workflow has a `prompt_studio.json` companion that documents the prompt
template + the JSON output schema. The Unstract deployment manager uploads
these on `docker compose up unstract`.

### 6. Spec deltas

1 spec delta:

- `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` — extend the registry
  schema from 24 → **26 models, 6 backends**; add 2 new `ModelCapability`
  enum values (`UNISTRUCT_WORKFLOW`, `DOCLING_LAYOUT`); add a new requirement
  `Ensemble consensus (BIEP v2)` that mandates the parallel-path + RAGAS-vote
  for the BIEP v2 jurisdiction pipelines

## Dependencies

```yaml
Blocked by: none
Blocked by (soft): 2026-07-20-biep-v2-junior-cycle-extraction-v1
                   (the JC pipeline is the first consumer of Docling layout
                    for scanned pre-2015 NCCA PDFs)
Blocked by (soft): 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1
                   (the England pipeline is the first consumer of Unstract
                    Prompt Studio for AQA/OCR/Edexcel spec extraction)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1 --strict` passes
- `dg check yaml` passes on the new asset defs
- `mise run registry:lint` (the v4 OCR/VLM registry test) passes — 26 models, 6 backends
- `mise run ragas:biiep:ensemble --dry-run` passes — RAGAS metric registered in MLflow
- `mise run unstract:upload-workflows` passes — 3 workflows uploaded
- The 6-subject BIEP v1 + JC + England pipelines (from Changes 1 + 2) still pass regression
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`meaisinfhoghlaim-ocr-htr`](../../specs/meaisinfhoghlaim-ocr-htr/spec.md) —
  the OCR/HTR capability that this change extends
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that the 4-path ensemble runs in the service of
- `docs/research/biiep_v2_ocr_ensemble_audit.md` *(authoritative per-stack
  doc-comparison audit)*
- `.agents/skills/dagster/SKILL.md` — the 5-layer component architecture
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
- `.agents/skills/ragas/SKILL.md` — RAGAS trace-based metrics
- `.agents/skills/mlflow/SKILL.md` — MLflow experiment tracking
- `.agents/skills/litellm/SKILL.md` — the LiteLLM gateway (the 2 VLM endpoints are reachable via LiteLLM)
