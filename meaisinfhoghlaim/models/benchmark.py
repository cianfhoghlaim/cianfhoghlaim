"""Real cross-model OCR/VLM comparison harness.

Per the lakehouse-multi-subject-multi-model-rollout change: the actual
point of `model_registry.py`'s `ocr_vision` redesign (role -> unique
key, no more resolve()-forced single-winner arbitration) was to make
running the SAME real PDF page through MULTIPLE vision models, and
comparing their real cost + output, an actual first-class capability --
not just a config-schema cleanup. This module is that capability.

For each real, available `ocr_vision` model
(`MODEL_REGISTRY.filter(family="ocr_vision", available=True)`), this:

1. Calls the model via litellm with a real rendered page image
   (reusing the exact request shape live-verified this session's
   qwen3-vl-8b smoke tests).
2. Captures REAL resource cost: wall-clock latency, llama-server's own
   `timings` (prompt_ms / predicted_ms / predicted_per_second) when the
   backend is llama-swap, and the model's on-disk GGUF size where known.
3. Scores the extraction's faithfulness against the PDF's own text
   layer (a real, if imperfect, proxy ground truth -- see
   `_faithfulness_vs_text_layer`) via the now-fixed
   `observability.ragas_evaluator.RagasEvaluator`.
4. Logs to Langfuse via `observability.ocr.OCRObservability` and to
   MLflow under the `oideachais-ocr` experiment.
5. Lands every result as a row in the real local DuckLake catalog
   (`leaving_cert.model_comparison_runs`), reusing the exact
   ATTACH/pandas/CREATE-OR-REPLACE-TABLE pattern already proven live in
   `scripts/hydrate_lc_full_corpus.py::connect_ducklake()`.

Scope for this pass: models with real downloaded GGUF weights only
(qwen3-vl-8b confirmed; more added as they're downloaded and verified
-- see `scripts/download_unsloth_models.py`). Calling a model with no
real weights would just 500 at the litellm/llama-swap layer -- this
harness surfaces that as a real, visible failure (`success=False`,
`error=...`) in its own results rather than silently skipping it, since
"this model isn't actually available yet" is itself useful comparison
information.
"""

from __future__ import annotations

import base64
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


LITELLM_BASE_URL = (
    os.environ.get("CIANFHOGHLAIM_LITELLM_URL")
    or os.environ.get("LITELLM_BASE_URL")
    or "http://localhost:4000/v1"
).rstrip("/")
LITELLM_API_KEY_ENV = "LITELLM_MASTER_KEY"

DEFAULT_PROMPT = (
    "Describe what this document page contains: the subject, any "
    "headings or titles you can read, and a brief summary of the "
    "visible content. Be concise."
)


@dataclass
class ModelComparisonResult:
    """One model's result for one page, in one comparison run."""

    model_key: str
    litellm_alias: str
    backend: str
    tier: str | None
    success: bool
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    prompt_ms: float | None = None
    predicted_ms: float | None = None
    predicted_per_second: float | None = None
    extracted_text: str = ""
    error: str | None = None
    faithfulness_score: float | None = None
    model_size_gb: float | None = None
    source_pdf: str = ""
    page_number: int = 0
    subject: str = ""
    run_id: str = ""
    run_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "run_at": self.run_at,
            "subject": self.subject,
            "source_pdf": self.source_pdf,
            "page_number": self.page_number,
            "model_key": self.model_key,
            "litellm_alias": self.litellm_alias,
            "backend": self.backend,
            "tier": self.tier,
            "success": self.success,
            "latency_ms": self.latency_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "prompt_ms": self.prompt_ms,
            "predicted_ms": self.predicted_ms,
            "predicted_per_second": self.predicted_per_second,
            "extracted_text": self.extracted_text,
            "error": self.error,
            "faithfulness_score": self.faithfulness_score,
            "model_size_gb": self.model_size_gb,
        }


def _call_litellm_vision(
    litellm_alias: str,
    image_b64: str,
    prompt: str,
    *,
    timeout: float = 300.0,
) -> dict[str, Any]:
    """Real litellm chat-completion call with an image.

    Reuses the exact request shape live-verified this session's
    qwen3-vl-8b PONG / chemistry-syllabus-page smoke tests. Raises on
    any transport/HTTP error -- the caller (`compare_models`) is
    responsible for catching this and recording a failed
    ModelComparisonResult, not this function.
    """
    headers = {"Content-Type": "application/json"}
    key = os.environ.get(LITELLM_API_KEY_ENV)
    if key:
        headers["Authorization"] = f"Bearer {key}"

    payload = {
        "model": litellm_alias,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ],
        "max_tokens": 512,
    }
    resp = httpx.post(
        f"{LITELLM_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=timeout
    )
    resp.raise_for_status()
    return resp.json()


def _faithfulness_vs_text_layer(
    extracted_text: str, page_text_layer: str, *, judge_model: str = "minimax-m3"
) -> float | None:
    """Score how well `extracted_text` (a VLM's description of a rendered
    page image) is grounded in `page_text_layer` (the PDF's own real
    embedded text, extracted via pymupdf -- a real, if imperfect, proxy
    ground truth for "what's actually on the page", reusing the same
    text-layer-extraction path the rest of this codebase's text-only
    pipeline already depends on).

    Returns None (not 0.0) when there's nothing to score, ragas isn't
    available, or the judge call fails -- callers should treat that as
    "not scored", not "scored zero". Never raises.
    """
    if not page_text_layer.strip() or not extracted_text.strip():
        return None
    try:
        import asyncio

        from observability.ragas_evaluator import EvaluationSample, RagasEvaluator

        evaluator = RagasEvaluator(model=judge_model)
        sample = EvaluationSample(
            question="What does this document page contain?",
            answer=extracted_text,
            contexts=[page_text_layer[:4000]],
        )
        result = asyncio.run(evaluator.evaluate([sample], metrics=["faithfulness"]))
        return result.faithfulness
    except Exception as exc:  # noqa: BLE001 — best-effort, never block the comparison run
        logger.warning("faithfulness scoring failed: %s", exc)
        return None


def _model_size_gb(entry) -> float | None:
    """Real on-disk GGUF size for a llama-swap-backed model, in GB.

    Looks for the GGUF file at the path
    `meaisinfhoghlaim/models/llama_swap_config.yaml` expects
    (`stedding/huggingface/gguf/<key>/`) relative to the repo root.
    Returns None (not 0.0) when the backend isn't llama-swap or the
    weights aren't downloaded yet -- "unknown" is not "zero".
    """
    if entry.backend != "llama-swap":
        return None
    repo_root = Path(__file__).resolve().parents[2]
    gguf_dir = repo_root / "stedding" / "huggingface" / "gguf" / entry.key
    if not gguf_dir.is_dir():
        return None
    total_bytes = sum(f.stat().st_size for f in gguf_dir.glob("*.gguf"))
    return round(total_bytes / (1024**3), 2) if total_bytes else None


def compare_models(
    pdf_path: Path,
    page_number: int,
    *,
    subject: str = "",
    prompt: str = DEFAULT_PROMPT,
    model_keys: list[str] | None = None,
    score_faithfulness: bool = True,
) -> list[ModelComparisonResult]:
    """Run the same real PDF page through every (or a chosen subset of)
    real, available `ocr_vision` models and return one
    `ModelComparisonResult` per model.

    This is the actual entry point for "compare cost/quality across
    models" -- the point of the `model_registry.py` `ocr_vision`
    redesign. Reuses `pdf_page_to_baml_image` for rendering (same proven
    path as `lc5_chemistry_diagrams_extracted`) and pymupdf's own text
    layer as the faithfulness proxy ground truth.
    """
    import uuid
    from datetime import datetime, timezone

    from meaisinfhoghlaim.models.model_registry import MODEL_REGISTRY

    run_id = str(uuid.uuid4())
    run_at = datetime.now(timezone.utc).isoformat()

    # Render the page once, real image bytes -- reused across every model.
    import fitz  # pymupdf

    doc = fitz.open(str(pdf_path))
    page = doc[page_number - 1]
    page_text_layer = page.get_text()
    pix = page.get_pixmap(dpi=150)
    image_b64 = base64.b64encode(pix.tobytes("png")).decode()

    entries = MODEL_REGISTRY.filter(family="ocr_vision", available=True)
    if model_keys is not None:
        entries = [e for e in entries if e.key in model_keys]

    results: list[ModelComparisonResult] = []
    for entry in entries:
        if not entry.litellm_alias:
            continue  # not routed through litellm -- nothing to compare here yet

        start = time.time()
        try:
            resp = _call_litellm_vision(entry.litellm_alias, image_b64, prompt)
            latency_ms = (time.time() - start) * 1000
            choice = resp.get("choices", [{}])[0]
            extracted_text = choice.get("message", {}).get("content", "") or ""
            usage = resp.get("usage", {})
            timings = resp.get("timings", {})

            faithfulness = (
                _faithfulness_vs_text_layer(extracted_text, page_text_layer)
                if score_faithfulness
                else None
            )

            result = ModelComparisonResult(
                model_key=entry.key,
                litellm_alias=entry.litellm_alias,
                backend=entry.backend,
                tier=entry.tier,
                success=True,
                latency_ms=latency_ms,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                prompt_ms=timings.get("prompt_ms"),
                predicted_ms=timings.get("predicted_ms"),
                predicted_per_second=timings.get("predicted_per_second"),
                extracted_text=extracted_text,
                faithfulness_score=faithfulness,
                model_size_gb=_model_size_gb(entry),
                source_pdf=pdf_path.name,
                page_number=page_number,
                subject=subject,
                run_id=run_id,
                run_at=run_at,
            )
        except Exception as exc:  # noqa: BLE001 — a real per-model failure is a real result, not a crash
            latency_ms = (time.time() - start) * 1000
            result = ModelComparisonResult(
                model_key=entry.key,
                litellm_alias=entry.litellm_alias,
                backend=entry.backend,
                tier=entry.tier,
                success=False,
                latency_ms=latency_ms,
                error=str(exc),
                model_size_gb=_model_size_gb(entry),
                source_pdf=pdf_path.name,
                page_number=page_number,
                subject=subject,
                run_id=run_id,
                run_at=run_at,
            )
            logger.warning("compare_models: %s failed: %s", entry.key, exc)

        results.append(result)

    return results


def land_comparison_results(results: list[ModelComparisonResult]) -> int:
    """Land comparison results into the real local DuckLake catalog as
    `leaving_cert.model_comparison_runs`.

    Reuses the exact connect/ATTACH + pandas.DataFrame + CREATE-OR-
    REPLACE-TABLE pattern already proven live in
    `scripts/hydrate_lc_full_corpus.py::connect_ducklake()` /
    `orchestration/resources.py::DuckLakeResource.get_client()` --
    APPENDS to the existing table (if any) rather than replacing it,
    since comparison runs accumulate over time rather than being a
    full-corpus snapshot rebuild like the documents table is.

    Returns the number of rows landed.
    """
    if not results:
        return 0

    import pandas as pd

    from scripts.hydrate_lc_full_corpus import SCHEMA_NAME, connect_ducklake

    table = f"{SCHEMA_NAME}.model_comparison_runs"
    con = connect_ducklake()
    df = pd.DataFrame([r.to_dict() for r in results])

    existing = con.execute(
        "SELECT count(*) FROM information_schema.tables "
        f"WHERE table_schema = '{SCHEMA_NAME}' AND table_name = 'model_comparison_runs'"
    ).fetchone()[0]

    con.register("_comparison_df", df)
    if existing:
        con.execute(f"INSERT INTO {table} SELECT * FROM _comparison_df")
    else:
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM _comparison_df")
    con.unregister("_comparison_df")

    logger.info("model_comparison_runs_landed", extra={"table": table, "rows": len(df)})
    return len(df)


def log_comparison_to_observability(
    results: list[ModelComparisonResult], source_name: str
) -> None:
    """Log a comparison run to Langfuse (via OCRObservability) and MLflow
    (under the `oideachais-ocr` experiment). Best-effort -- never raises.
    """
    try:
        from observability.ocr import OCRObservability

        obs = OCRObservability(project_name="oideachais-ocr", service_name="model-comparison")
        obs.log_comparison({r.model_key: r for r in results}, source_name)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Langfuse comparison logging failed: %s", exc)

    try:
        import mlflow

        from observability.mlflow_config import EXPERIMENTS, init_mlflow, mlflow_run

        init_mlflow(experiment_name=EXPERIMENTS["ocr"]["name"])
        with mlflow_run(run_name=f"comparison_{source_name}", tags={"kind": "model_comparison"}) as run:
            if run is None:
                return  # MLflow unavailable -- degrade gracefully, already logged above
            for r in results:
                prefix = r.model_key.replace("-", "_").replace(".", "_")
                mlflow.log_metric(f"{prefix}_latency_ms", r.latency_ms)
                if r.faithfulness_score is not None:
                    mlflow.log_metric(f"{prefix}_faithfulness", r.faithfulness_score)
                if r.model_size_gb is not None:
                    mlflow.log_metric(f"{prefix}_model_size_gb", r.model_size_gb)
    except Exception as exc:  # noqa: BLE001
        logger.warning("MLflow comparison logging failed: %s", exc)
