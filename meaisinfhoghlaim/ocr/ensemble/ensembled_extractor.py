"""EnsembledExtractor — the BIEP v2 4-path OCR/VLM extractor (Change 3).

Runs 4 paths in parallel for any incoming PDF:
  Path 1 (BAML):    Docling-serve -> text -> BAML function
  Path 2 (Unstract): Docling-serve -> Unstract workflow -> JSON
  Path 3 (qwen3-vl): gemma-4-26B-A4B-vision page-level image -> JSON
  Path 4 (gemma4):  gemma-4-26B-A4B page-level image -> JSON

Each path output lands in its own per-jurisdiction DuckLake table.
Then the RAGAS `biiep_extraction_consensus` metric votes the canonical row.

Reference: openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/

OCR_WEBHOOK_URL emission (post-trilogy, 2026-08-XX):
    On every successful extraction, the canonical envelope is POSTed to
    ``os.getenv("OCR_WEBHOOK_URL", "")`` via ``httpx.AsyncClient`` using
    a fire-and-forget async task. The webhook emission mirrors the
    langfuse callback pattern (one-way, never blocks the extraction).

    The payload schema (per the british-isles-education-pipeline-v3
    spec delta on the OCR webhook delta):
        {
          "document_id": "<uuid>",
          "capability": "<forms|layout|tables+latex|doctags|gaelic|english>",
          "backend_used": "<paddleocr|mlx-omni|olmocr|docling-serve|llama-swap|dots-ocr>",
          "model": "<model name>",
          "result_url": "<s3://lakehouse/ocr/...>",
          "duration_ms": <int>,
          "trace_id": "<opentelemetry trace id>",
          "completed_at": "<iso-8601 utc>"
        }

    Bearer auth: ``Authorization: Bearer ${OCR_WEBHOOK_TOKEN}`` if set.

    If ``OCR_WEBHOOK_URL`` is empty (dev mode), the emission is silently
    skipped (no error). The POST is wrapped in try/except so a webhook
    failure never blocks the extraction result.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

PathName = Literal["baml", "unstract", "gemma4_vision", "gemma4"]


@dataclass
class EnsemblePathOutput:
    """One path's output (before RAGAS voting)."""

    path: PathName
    raw_response: str
    confidence_score: float = 0.0
    schema_valid: bool = False
    ragas_faithfulness: float | None = None
    ragas_answer_relevance: float | None = None
    ragas_context_precision: float | None = None
    error: str | None = None

    # BAML Collector observability fields (added by
    # 2026-08-17-hygiene-drift-cleanup-v1 P1.8). Populated when the
    # path's runtime supports BAML Collector (only the BAML path
    # today; Unstract / qwen3-vl / gemma4 leave these None until
    # their runtimes gain Collector parity).
    usage_input_tokens: int | None = None
    usage_output_tokens: int | None = None
    usage_total_tokens: int | None = None
    raw_llm_response: str | None = None
    http_responses: list[str] = field(default_factory=list)


@dataclass
class EnsembleResult:
    """The 4-path ensemble result + the RAGAS-voted canonical row."""

    # The 4 path outputs (input to RAGAS vote)
    paths: list[EnsemblePathOutput] = field(default_factory=list)

    # RAGAS vote metadata
    ragas_voted_path: PathName | None = None
    ragas_score: float = 0.0

    # Final consensus output (the winner's raw response, JSON-serialised)
    voted_output: str | None = None
    voted_canonical_id: str | None = None

    # Provenance trail (so the Change 4 audit notebook can show side-by-side)
    baml_canonical_id: str | None = None
    unstract_canonical_id: str | None = None
    qwen3_vl_canonical_id: str | None = None
    gemma4_canonical_id: str | None = None

    # Common metadata
    source_pdf: str | None = None
    content_hash: str | None = None
    ingested_at: str | None = None
    board: str | None = None
    qualification_level: str | None = None
    subject: str | None = None

    # Rows actually written to DuckLake by `_land_paths_in_ducklake`. Stays
    # 0 if the landing did not run, so a caller can never report a row count
    # the store does not have.
    rows_landed: int = 0

    @property
    def ragas_passed(self) -> bool:
        """Whether the ensemble's RAGAS score meets the production threshold (0.70)."""
        return self.ragas_score >= 0.70


class EnsembledExtractor:
    """The canonical BIEP v2 4-path OCR/VLM extractor.

    Parameters
    ----------
    docling_url : str
        The IBM Docling HTTP REST API base URL (default: `http://localhost:5001/v1`).
    unstract_url : str
        The Unstract Prompt Studio HTTP REST API base URL
        (default: `http://localhost:8000/api/v1/deployment`).
    unstract_workflow_id : str | None
        The per-doc-type Unstract workflow ID (e.g. `aqa_gcse_spec`,
        `ncca_jc_cba`, `sec_lc_marking`). If None, falls back to BAML-only.
    qwen3_vl_endpoint : str
        The LiteLLM gateway endpoint for `gemma-4-26B-A4B-vision` (the workhorse VLM).
    gemma4_endpoint : str
        The llama-swap endpoint for `gemma-4-26B-A4B` (the M4 default MoE).
    ragas_threshold : float
        The production RAGAS score threshold (default: 0.70).
    """

    def __init__(
        self,
        docling_url: str = "http://localhost:5001/v1",
        unstract_url: str = "http://localhost:8000/api/v1/deployment",
        unstract_workflow_id: str | None = None,
        qwen3_vl_endpoint: str = "http://litellm:4000/v1",
        gemma4_endpoint: str = "http://llama-swap:8080/v1",
        ragas_threshold: float = 0.70,
    ) -> None:
        self.docling_url = docling_url
        self.unstract_url = unstract_url
        self.unstract_workflow_id = unstract_workflow_id
        self.qwen3_vl_endpoint = qwen3_vl_endpoint
        self.gemma4_endpoint = gemma4_endpoint
        self.ragas_threshold = ragas_threshold
        # Stashed observations from the most recent BAML Collector
        # invocation (Path 1). Read by _to_path_output after the
        # asyncio.gather() completes. Added by
        # 2026-08-17-hygiene-drift-cleanup-v1 P1.8.
        self._last_baml_collector_observations: dict[str, Any] | None = None

    # ─── Public API ────────────────────────────────────────────────────────

    def extract(
        self,
        pdf_path: str | Path,
        baml_function: str,
        jurisdiction: str = "ireland",
        scope: str = "education",
        subject: str | None = None,
        board: str | None = None,
        qualification_level: str | None = None,
    ) -> EnsembleResult:
        """Run the 4-path ensemble on one PDF and return the RAGAS-voted result.

        Parameters
        ----------
        pdf_path : str | Path
            The local path to the PDF to extract.
        baml_function : str
            The BAML function name to invoke for Path 1 (e.g.
            `b.ExtractJCCurriculum`).
        jurisdiction : str
            The jurisdiction (`"ireland"` | `"england"` | ...) for the
            DuckLake namespace routing.
        scope : str
            The scope (`"education"` | `"law"` | `"medicine"` | ...).
        subject : str | None
            The subject slug (e.g. `"english"`, `"mathematics"`).
        board : str | None
            The awarding body (`"aqa"`, `"ocr"`, `"edexcel"` — England only).
        qualification_level : str | None
            The qualification level (`"gcse"`, `"a_level"` — England only).

        Returns
        -------
        EnsembleResult
            The 4-path output + the RAGAS-voted canonical row + provenance IDs.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        start_time = time.time()
        content_hash = _file_hash(pdf_path)
        ingested_at = _now_iso()

        # Run the 4 paths in parallel (asyncio.gather).
        path_results = asyncio.run(
            asyncio.gather(
                self._run_path_baml(pdf_path, baml_function),
                self._run_path_unstract(pdf_path),
                self._run_path_qwen3_vl(pdf_path),
                self._run_path_gemma4(pdf_path),
                return_exceptions=True,
            )
        )

        # Materialise as EnsemblePathOutputs (gracefully degrade on per-path
        # failures — the RAGAS vote still runs on whatever succeeded).
        # Added by 2026-08-17-hygiene-drift-cleanup-v1 P1.8: the BAML
        # path's collector observations are read from the closure-bound
        # attribute set during _run_path_baml(); the other 3 paths leave
        # the observation kwargs as None until their runtimes gain
        # Collector parity.
        paths = [
            _to_path_output(
                path_results[0], "baml",
                collector_observations=self._last_baml_collector_observations,
            ),
            _to_path_output(path_results[1], "unstract"),
            _to_path_output(path_results[2], "qwen3_vl"),
            _to_path_output(path_results[3], "gemma4"),
        ]

        # RAGAS vote.
        voted_path, ragas_score, voted_output = _ragas_vote(paths)

        result = EnsembleResult(
            paths=paths,
            ragas_voted_path=voted_path,
            ragas_score=ragas_score,
            voted_output=voted_output,
            source_pdf=str(pdf_path),
            content_hash=content_hash,
            ingested_at=ingested_at,
            board=board,
            qualification_level=qualification_level,
            subject=subject,
        )

        # Per-path canonical IDs (so the Change 4 audit notebook can deep-link
        # back to the DuckLake rows).
        for path in paths:
            cid = _path_canonical_id(jurisdiction, scope, subject, board, content_hash, path.path)
            if path.path == "baml":
                result.baml_canonical_id = cid
            elif path.path == "unstract":
                result.unstract_canonical_id = cid
            elif path.path == "qwen3_vl":
                result.qwen3_vl_canonical_id = cid
            elif path.path == "gemma4":
                result.gemma4_canonical_id = cid

        # Voted canonical ID for the warehouse.
        result.voted_canonical_id = _voted_canonical_id(
            jurisdiction, scope, subject, board, content_hash, voted_path,
        )

        # Land each path's row + the voted canonical in the per-jurisdiction
        # DuckLake namespace, via the canonical dlt destination factory.
        result.rows_landed = self._land_paths_in_ducklake(
            result, jurisdiction, scope, subject, board
        )

        # OCR_WEBHOOK_URL emission (post-trilogy delta). Fire-and-forget
        # async POST — never blocks the extraction result. The payload
        # conforms to the british-isles-education-pipeline-v3 spec delta.
        self._emit_ocr_webhook(
            result=result,
            jurisdiction=jurisdiction,
            scope=scope,
            subject=subject,
            board=board,
            qualification_level=qualification_level,
            elapsed_seconds=time.time() - start_time,
        )

        return result

    # ─── 4-path runners ─────────────────────────────────────────────────────

    async def _run_path_baml(
        self, pdf_path: Path, baml_function: str
    ) -> str:
        """Path 1: Docling-serve -> text -> BAML function.

        Per the 2026-08-13-ocr-vision-activation-completion-v1 change:
        this path now does a real BAML call against the docling-extracted
        text. The `baml_function` parameter is the canonical BAML function
        name (e.g. `ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
        `ExtractMarkingSchemeGuideline`, `ExtractSyllabusDiagram`); the
        function is invoked via `baml_client.baml_client.sync_client` if
        available, else gracefully degrades to returning the docling text
        as the path output so the orchestrator can still vote.
        """
        try:
            _docling_text = await _call_docling(pdf_path, self.docling_url)
        except Exception as e:
            logger.warning("docling_text_extraction_failed", error=str(e))
            _docling_text = pdf_path.read_bytes().decode("utf-8", errors="ignore")[:200_000]

        # Real BAML call (per 2026-08-13-ocr-vision-activation-completion-v1)
        try:
            from baml_client.baml_client import sync_client as _baml_sync  # type: ignore[import-not-found]
        except ImportError:
            logger.warning(
                "baml_client_not_available",
                baml_function=baml_function,
                hint="Run `mise run baml:generate` to produce the baml_client package",
            )
            return f"[BAML_PATH] baml_client not available for {baml_function}"

        try:
            # Invoke the BAML function dynamically via the sync client.
            # The BAML-generated `b.Extract<Function>` accessor pattern
            # wraps each function as a callable. We call it with the
            # docling text as the source input.
            baml_fn = getattr(_baml_sync.b, baml_function, None)
            if baml_fn is None:
                return f"[BAML_PATH] unknown_function: {baml_function}"
            # Wire BAML Collector API for observability (added by
            # 2026-08-17-hygiene-drift-cleanup-v1 P1.8) — populates
            # usage_input_tokens + raw_llm_response + http_responses on
            # the EnsemblePathOutput so MLflow can record the per-call
            # telemetry via evaluate_ensemble().
            #
            # The Collector is module-level-scoped; we lazily import
            # baml_py so the ensemble can still load when the
            # baml-py extra is not installed.
            collector = None
            try:
                from baml_py import Collector as _BamlCollector
                collector = _BamlCollector(name=f"biep_ocr_{baml_function}")
            except ImportError:
                logger.debug("baml_py_collector_unavailable", baml_function=baml_function)
            # The BAML sync client is a context manager; the call
            # returns a typed Pydantic model (or list of models) which
            # we JSON-serialise as the path output.
            with _baml_sync() as client:
                baml_kwargs = {"text": _docling_text, "source_pdf": str(pdf_path)}
                if collector is not None:
                    baml_kwargs["baml_options"] = {"collector": collector}
                result = client.call(baml_fn, **baml_kwargs)
            json_response = json.dumps(
                result.model_dump() if hasattr(result, "model_dump") else result,
                default=str,
            )
            # Stash the collector observations on the closure-bound
            # attribute so _to_path_output can read them after the
            # asyncio.gather() completes (collector is per-call, not
            # per-path-output).
            if collector is not None and hasattr(collector, "last") and collector.last is not None:
                self._last_baml_collector_observations = {
                    "usage_input_tokens": getattr(collector.last.usage, "input_tokens", None) if collector.last.usage else None,
                    "usage_output_tokens": getattr(collector.last.usage, "output_tokens", None) if collector.last.usage else None,
                    "raw_llm_response": collector.last.raw_llm_response,
                    "http_responses": [
                        str(getattr(c, "http_response", ""))
                        for c in (collector.last.calls or [])
                    ],
                }
            else:
                self._last_baml_collector_observations = None
            return json_response
        except Exception as e:
            logger.warning("baml_call_failed", baml_function=baml_function, error=str(e))
            return f"[BAML_PATH] error={e}"

    async def _run_path_unstract(self, pdf_path: Path) -> str:
        """Path 2: Docling-serve -> Unstract workflow -> JSON."""
        if self.unstract_workflow_id is None:
            return "[UNSTRACT_PATH] no_workflow_id_configured"
        try:
            return await _call_unstract(
                pdf_path, self.unstract_url, self.unstract_workflow_id,
            )
        except Exception as e:
            logger.warning("unstract_call_failed", error=str(e))
            return f'[UNSTRACT_PATH] error={e}'

    async def _run_path_qwen3_vl(self, pdf_path: Path) -> str:
        """Path 3: gemma-4-26B-A4B-vision page-level image -> JSON."""
        try:
            return await _call_qwen3_vl(pdf_path, self.qwen3_vl_endpoint)
        except Exception as e:
            logger.warning("qwen3_vl_call_failed", error=str(e))
            return f'[QWEN3_VL_PATH] error={e}'

    async def _run_path_gemma4(self, pdf_path: Path) -> str:
        """Path 4: gemma-4-26B-A4B page-level image -> JSON."""
        try:
            return await _call_gemma4(pdf_path, self.gemma4_endpoint)
        except Exception as e:
            logger.warning("gemma4_call_failed", error=str(e))
            return f'[GEMMA4_PATH] error={e}'

    # ─── DuckLake landing (stub for now) ─────────────────────────────────

    def _land_paths_in_ducklake(
        self,
        result: EnsembleResult,
        jurisdiction: str,
        scope: str,
        subject: str | None,
        board: str | None,
    ) -> int:
        """Land each path's output + the voted canonical row in DuckLake.

        Returns the number of rows actually written (4 path rows + 1 voted
        row per PDF, when all four paths ran).

        IMPLEMENTED 2026-08-14. This was previously two `logger.info` calls
        with a docstring promising a "real implementation" — so the flagship
        4-path ensemble produced no persisted output at all, while its
        Dagster asset check reported success. Routed through the canonical
        `get_dlt_destination()` so it honours the same DuckLake/DuckDB tier
        selection as every other writer.
        """
        import dlt

        from dlt_sources.common.destinations_cianfhoghlaim import (
            get_ducklake_destination,
        )

        rows: list[dict[str, Any]] = []
        for path in result.paths:
            rows.append(
                {
                    "namespace": _path_destination_namespace(
                        jurisdiction, scope, subject, board, path.path,
                    ),
                    "row_kind": "path",
                    "path": path.path,
                    "raw_response": path.raw_response,
                    "confidence_score": path.confidence_score,
                    "schema_valid": path.schema_valid,
                    "ragas_faithfulness": path.ragas_faithfulness,
                    "ragas_answer_relevance": path.ragas_answer_relevance,
                    "ragas_context_precision": path.ragas_context_precision,
                    "error": path.error,
                    "source_pdf": result.source_pdf,
                    "content_hash": result.content_hash,
                    "ingested_at": result.ingested_at,
                    "jurisdiction": jurisdiction,
                    "scope": scope,
                    "subject": subject or result.subject,
                    "board": board or result.board,
                    "qualification_level": result.qualification_level,
                }
            )

        rows.append(
            {
                "namespace": _path_destination_namespace(
                    jurisdiction, scope, subject, board, "voted_canonical",
                ),
                "row_kind": "voted_canonical",
                "path": result.ragas_voted_path,
                "raw_response": result.voted_output,
                "confidence_score": result.ragas_score,
                "schema_valid": True,
                "voted_canonical_id": result.voted_canonical_id,
                "source_pdf": result.source_pdf,
                "content_hash": result.content_hash,
                "ingested_at": result.ingested_at,
                "jurisdiction": jurisdiction,
                "scope": scope,
                "subject": subject or result.subject,
                "board": board or result.board,
                "qualification_level": result.qualification_level,
            }
        )

        pipeline = dlt.pipeline(
            pipeline_name="biiep_ocr_ensemble",
            destination=get_ducklake_destination(),
            dataset_name="ocr_ensemble",
            dev_mode=False,
        )
        # `content_hash` + `path` identify a row uniquely, so re-running the
        # ensemble on the same PDF updates rather than duplicates.
        load_info = pipeline.run(
            rows,
            table_name="ensemble_paths",
            write_disposition="merge",
            primary_key=["content_hash", "row_kind", "path"],
        )
        logger.info(
            "ensemble_landed",
            rows=len(rows),
            source_pdf=result.source_pdf,
            ragas_score=result.ragas_score,
            voted_path=result.ragas_voted_path,
            loads_ids=str(load_info.loads_ids[0]) if load_info.loads_ids else "",
        )
        return len(rows)

    # ─── OCR_WEBHOOK_URL emission (post-trilogy delta) ────────────────────

    def _emit_ocr_webhook(
        self,
        result: EnsembleResult,
        jurisdiction: str,
        scope: str,
        subject: str | None,
        board: str | None,
        qualification_level: str | None,
        elapsed_seconds: float,
    ) -> None:
        """Fire-and-forget POST to ``OCR_WEBHOOK_URL`` on a successful extraction.

        Mirrors the langfuse callback pattern (one-way, never blocks the
        extraction result). The payload conforms to the
        ``british-isles-education-pipeline-v3`` spec delta.

        If ``OCR_WEBHOOK_URL`` is empty (dev mode), the emission is silently
        skipped. A webhook failure is caught by the background task's
        try/except — it never propagates back to the caller.
        """
        webhook_url = os.getenv("OCR_WEBHOOK_URL", "")
        if not webhook_url:
            return  # dev mode — skip silently

        document_id = str(uuid.uuid4())
        completed_at = datetime.now(UTC).isoformat()
        duration_ms = int(elapsed_seconds * 1000)

        # The capability + backend_used map to the 4-path ensemble + the
        # 6 canonical BIEP v3 capabilities (forms | layout | tables+latex |
        # doctags | gaelic | english). The python manifest supplies a
        # stable mapping for the source quartet.
        capability = _capability_for(
            scope=scope, subject=subject, board=board,
            qualification_level=qualification_level,
        )
        backend_used = _backend_used_for(result.ragas_voted_path or "baml")
        model = _model_for_path(result.ragas_voted_path or "baml")
        result_url = _result_s3_url(
            jurisdiction=jurisdiction,
            scope=scope,
            subject=subject,
            board=board,
            content_hash=result.content_hash or "",
        )

        # Pull the OpenTelemetry trace id if available (best-effort;
        # missing trace_id is fine — the webhook accepts null).
        trace_id = _current_trace_id() or ""

        envelope = {
            "document_id": document_id,
            "capability": capability,
            "backend_used": backend_used,
            "model": model,
            "result_url": result_url,
            "duration_ms": duration_ms,
            "trace_id": trace_id,
            "completed_at": completed_at,
        }

        # Fire-and-forget — schedule the POST in the background.
        # If there's no running event loop (e.g. sync caller), fall back
        # to a thread-pool dispatch so the main call still returns.
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                _post_ocr_webhook(webhook_url, envelope),
                name=f"ocr-webhook-{document_id}",
            )
        except RuntimeError:
            # No running loop — fall back to background thread.
            import threading

            threading.Thread(
                target=_post_ocr_webhook_sync,
                args=(webhook_url, envelope),
                daemon=True,
                name=f"ocr-webhook-{document_id}",
            ).start()


# ─── Helpers ────────────────────────────────────────────────────────────


# ─── Helpers ────────────────────────────────────────────────────────────


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _now_iso() -> str:
    from datetime import UTC, datetime
    return datetime.now(UTC).isoformat()


def _to_path_output(
    result: Any,
    path: PathName,
    collector_observations: dict[str, Any] | None = None,
) -> EnsemblePathOutput:
    """Normalise an asyncio path result into an EnsemblePathOutput.

    The optional `collector_observations` dict (only populated for the
    BAML path today, via the `baml_py.Collector` API) populates the
    observability fields on the EnsemblePathOutput. Added by
    2026-08-17-hygiene-drift-cleanup-v1 P1.8.
    """
    if isinstance(result, Exception):
        return EnsemblePathOutput(
            path=path,
            raw_response="",
            confidence_score=0.0,
            schema_valid=False,
            error=str(result),
        )
    obs = collector_observations or {}
    return EnsemblePathOutput(
        path=path,
        raw_response=str(result) if result is not None else "",
        confidence_score=0.9 if result else 0.0,
        schema_valid=True,
        usage_input_tokens=obs.get("usage_input_tokens"),
        usage_output_tokens=obs.get("usage_output_tokens"),
        raw_llm_response=obs.get("raw_llm_response"),
        http_responses=list(obs.get("http_responses") or []),
    )


def _ragas_vote(paths: list[EnsemblePathOutput]) -> tuple[PathName, float, str | None]:
    """The RAGAS-voted canonical path + score + output.

    Per the 2026-08-13-ocr-vision-activation-completion-v1 change:
    delegates to `evaluate_ensemble()` from
    `meaisinfhoghlaim.evaluation.ragas_biiep_ensemble`. The previous
    inline scoring implementation is replaced by the canonical RAGAS
    vote (which also fires the MLflow observability hook).

    The helper takes a list of `EnsemblePathOutput` records, builds a
    temporary `EnsembleResult` wrapping them, calls `evaluate_ensemble`,
    and returns `(voted_path, ragas_score, voted_output)` by selecting
    the path with the highest `composite` RAGAS score.
    """
    from meaisinfhoghlaim.evaluation.ragas_biiep_ensemble import (  # noqa: E402
        evaluate_ensemble,
        RAGASScore,
    )

    if not paths:
        return "baml", 0.0, None

    # Build a minimal EnsembleResult so evaluate_ensemble can consume it.
    # Source PDF + provenance fields are not known at this layer; the
    # caller (`EnsembledExtractor.extract`) is the source of truth for
    # those. The RAGAS vote only depends on `paths`.
    result = EnsembleResult(paths=list(paths))

    try:
        scores: dict[str, RAGASScore] = evaluate_ensemble(result, mlflow_run=True)
    except Exception as e:
        logger.warning("evaluate_ensemble_failed", error=str(e))
        return paths[0].path, 0.0, paths[0].raw_response

    if not scores:
        return paths[0].path, 0.0, paths[0].raw_response

    # Pick the path with the highest composite score
    winner_path_name, winner_score = max(
        scores.items(), key=lambda kv: kv[1].composite
    )
    winner_output = next(
        (p.raw_response for p in paths if p.path == winner_path_name),
        None,
    )
    return winner_path_name, winner_score.composite, winner_output


def _path_destination_namespace(
    jurisdiction: str,
    scope: str,
    subject: str | None,
    board: str | None,
    path: str,
) -> str:
    """Return the canonical DuckLake namespace for one path's output row."""
    base = f"oideachais.{scope}.british_isles.{jurisdiction}"
    if subject:
        base = f"{base}.{subject}"
    if board:
        base = f"{base}.{board}"
    return f"{base}.{path}"


def _path_canonical_id(
    jurisdiction: str,
    scope: str,
    subject: str | None,
    board: str | None,
    content_hash: str,
    path: PathName,
) -> str:
    """The canonical ID of the per-path DuckLake row."""
    return f"{jurisdiction}.{scope}.{subject or '*'}.{board or '*'}.{content_hash[:16]}.{path}"


def _voted_canonical_id(
    jurisdiction: str,
    scope: str,
    subject: str | None,
    board: str | None,
    content_hash: str,
    voted_path: PathName | None,
) -> str:
    """The canonical ID of the RAGAS-voted DuckLake row."""
    return f"{jurisdiction}.{scope}.{subject or '*'}.{board or '*'}.{content_hash[:16]}.voted_canonical.{voted_path or 'unknown'}"


# ─── Async HTTP placeholders ────────────────────────────────────────────


async def _call_docling(pdf_path: Path, docling_url: str) -> str:
    """Call the IBM Docling HTTP REST API and return the DocTags XML."""
    # Per the 2026-08-08-biep-v3-production-readiness-v1 change: real httpx
    # implementation replaces the previous stub.
    try:
        import httpx  # type: ignore[import-not-found]
        timeout = httpx.Timeout(60.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            with open(pdf_path, "rb") as f:
                files = {"file": (pdf_path.name, f, "application/pdf")}
                params = {"to_formats": "doctags"}
                resp = await client.post(
                    f"{docling_url.rstrip('/')}/v1/convert/file",
                    files=files,
                    params=params,
                )
                resp.raise_for_status()
                # DocTags XML is in the response
                return resp.text
    except ImportError:
        # httpx not installed — fall back to PDF text extraction
        try:
            return pdf_path.read_bytes().decode("utf-8", errors="ignore")[:200_000]
        except Exception:
            return f"[DOCTAGS_STUB] file={pdf_path.name} size={pdf_path.stat().st_size}"
    except Exception as e:
        # Network error or HTTP error — fall back gracefully
        return f'[{{"workflow":"docling","error":"{type(e).__name__}: {e}","fallback":"stub"}}]'


async def _call_unstract(pdf_path: Path, unstract_url: str, workflow_id: str) -> str:
    """Call the Unstract HTTP REST API and return the workflow JSON output."""
    # Per the 2026-08-08 change: real httpx implementation.
    try:
        import httpx  # type: ignore[import-not-found]
        timeout = httpx.Timeout(120.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            with open(pdf_path, "rb") as f:
                files = {"file": (pdf_path.name, f, "application/pdf")}
                resp = await client.post(
                    f"{unstract_url.rstrip('/')}/api/v1/deployment/{workflow_id}/process",
                    files=files,
                )
                resp.raise_for_status()
                return resp.text
    except ImportError:
        try:
            text = pdf_path.read_bytes().decode("utf-8", errors="ignore")[:80_000]
            return f'[{{"workflow_id":"{workflow_id}","text":"{text[:200]}..."}}]'
        except Exception:
            return f'[{{"workflow_id":"{workflow_id}","stub":true}}]'
    except Exception as e:
        return f'[{{"workflow":"unstract","error":"{type(e).__name__}: {e}","fallback":"stub"}}]'


async def _call_qwen3_vl(pdf_path: Path, endpoint: str) -> str:
    """Call the gemma-4-26B-A4B-vision VLM via LiteLLM and return the JSON response.

    Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this used
    to send `"content": f"Extract ... at {pdf_path}"` -- a plain text
    string containing a local filesystem path, which a remote litellm/
    llama-swap container obviously can't read. No image data ever left
    the process despite the docstring claiming "page-level image -> JSON"
    and a prior comment claiming "real httpx implementation". Now renders
    page 1 (representative sample -- true all-page processing is future
    work, not attempted here) via
    `meaisinfhoghlaim.document_factory.pdf_to_image_bridge` and sends a
    proper OpenAI-compatible `image_url` content block, matching the
    already-correct pattern in
    `sruth/shared/extraction/docling_resource.py::ocr_page_vlm()`.
    """
    try:
        import httpx  # type: ignore[import-not-found]

        from meaisinfhoghlaim.document_factory.pdf_to_image_bridge import (
            render_pdf_page_to_data_uri,
        )

        image_url = render_pdf_page_to_data_uri(pdf_path, page_number=1)
        content: Any = (
            [
                {"type": "text", "text": "Extract the structured content from this document page."},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
            if image_url is not None
            # Rendering failed (pymupdf missing, corrupt PDF, ...) --
            # degrade to a text-only prompt rather than crashing, but
            # never silently send a bare filesystem path as "content"
            # again.
            else "Extract the structured content from this document. "
                 "(No page image was available to attach for this call.)"
        )

        timeout = httpx.Timeout(180.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{endpoint.rstrip('/')}/v1/chat/completions",
                json={
                    "model": "local/vision/gemma-4-26B-A4B-vision",
                    "messages": [{"role": "user", "content": content}],
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data)
    except ImportError:
        try:
            size = pdf_path.stat().st_size
            return f'[{{"vlm":"gemma-4-26B-A4B-vision","file_size":{size}}}]'
        except Exception:
            return '[{"vlm":"gemma-4-26B-A4B-vision","stub":true}]'
    except Exception as e:
        return f'[{{"vlm":"gemma-4-26B-A4B-vision","error":"{type(e).__name__}: {e}","fallback":"stub"}}]'


async def _call_gemma4(pdf_path: Path, endpoint: str) -> str:
    """Call the gemma-4-26B-A4B MoE VLM via llama-swap and return the JSON response.

    Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: same fake
    text-only-path bug as `_call_qwen3_vl` above, fixed the same way --
    render page 1 and attach it. This endpoint is llama.cpp's own raw
    `/completion` API (not litellm's OpenAI-compatible `/v1/chat/
    completions`), so the multimodal contract is different: llama.cpp
    server expects an `image_data: [{"data": <base64>, "id": <int>}]`
    array alongside a prompt that references the image via a `[img-<id>]`
    marker, per llama.cpp server's own documented multimodal API. This
    has NOT been verified against a live llama-swap instance in this
    environment (no live services running here) -- flagged explicitly
    rather than silently assumed correct; verify against Phase D's live
    stack before relying on it.
    """
    try:
        import base64 as _base64

        import httpx  # type: ignore[import-not-found]

        from meaisinfhoghlaim.document_factory.pdf_to_image_bridge import (
            render_pdf_page_to_bytes,
        )

        image_bytes = render_pdf_page_to_bytes(pdf_path, page_number=1)
        if image_bytes is not None:
            prompt = "Extract the structured content from this document page: [img-1]"
            image_data = [{"data": _base64.b64encode(image_bytes).decode("ascii"), "id": 1}]
        else:
            prompt = (
                "Extract structured content from this document. "
                "(No page image was available to attach for this call.)"
            )
            image_data = []

        timeout = httpx.Timeout(180.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{endpoint.rstrip('/')}/completion",
                json={
                    "model": "gemma-4-26B-A4B",
                    "prompt": prompt,
                    "image_data": image_data,
                    "max_tokens": 4096,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(data)
    except ImportError:
        try:
            size = pdf_path.stat().st_size
            return f'[{{"vlm":"gemma-4-26B-A4B","file_size":{size}}}]'
        except Exception:
            return '[{"vlm":"gemma-4-26B-A4B","stub":true}]'
    except Exception as e:
        return f'[{{"vlm":"gemma-4-26B-A4B","error":"{type(e).__name__}: {e}","fallback":"stub"}}]'


# ─── OCR_WEBHOOK_URL helpers (post-trilogy) ──────────────────────────────


# Stable mapping from the 4-path ensemble winner to the canonical BIEP
# backend_used + model strings. The 6 canonical BIEP v3 capabilities are:
#   forms | layout | tables+latex | doctags | gaelic | english
_PATH_TO_BACKEND: dict[str, tuple[str, str]] = {
    # path -> (backend_used, model)
    # 2026-08-31: qwen3_vl path replaced with gemma4_vision (per the
    # 2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1 change).
    "baml": ("docling-serve", "docling-serve"),
    "unstract": ("llama-swap", "unstract-v1"),
    "gemma4_vision": ("llama-swap", "gemma-4-26B-A4B-vision"),
    "gemma4": ("llama-swap", "gemma-4-26B-A4B"),
}


def _backend_used_for(path: str) -> str:
    """Return the canonical `backend_used` for a 4-path ensemble winner."""
    return _PATH_TO_BACKEND.get(path, ("paddleocr", "paddleocr-v4"))[0]


def _model_for_path(path: str) -> str:
    """Return the canonical `model` string for a 4-path ensemble winner."""
    return _PATH_TO_BACKEND.get(path, ("paddleocr", "paddleocr-v4"))[1]


def _capability_for(
    scope: str | None,
    subject: str | None,
    board: str | None,
    qualification_level: str | None,
) -> str:
    """Return the canonical BIEP v3 `capability` for the current extract call.

    Picks from the 6 canonical capabilities: forms | layout |
    tables+latex | doctags | gaelic | english. The default is ``doctags``
    (the (subject, board, qualification_level) tuple drives the more
    specific capability).
    """
    if subject == "gaeilge" or subject == "irish":
        return "gaelic"
    if subject == "english":
        return "english"
    if board and qualification_level == "a_level":
        return "forms"
    if qualification_level == "gcse":
        return "tables+latex"
    return "doctags"


def _result_s3_url(
    jurisdiction: str,
    scope: str,
    subject: str | None,
    board: str | None,
    content_hash: str,
) -> str:
    """Return the canonical S3 URL for the per-extraction result blob.

    The path mirrors the BIEP v3 snake_case S3 contract:
        ``s3://lakehouse/ocr/<jurisdiction>/<scope>/<subject>/<board>/<content_hash>.json``

    Subject + board are optional; the URL elides them when missing.
    """
    parts = ["s3://lakehouse/ocr", jurisdiction, scope]
    if subject:
        parts.append(subject)
    if board:
        parts.append(board)
    parts.append(f"{content_hash[:16] if content_hash else 'unknown'}.json")
    return "/".join(parts)


def _current_trace_id() -> str | None:
    """Return the current OpenTelemetry trace id (best-effort, or None).

    Falls back gracefully when OTel isn't installed or no trace is active.
    """
    try:
        from opentelemetry import trace  # type: ignore[import-not-found]

        span = trace.get_current_span()
        if span is None:
            return None
        ctx = span.get_span_context()
        if ctx is None or not ctx.is_valid:
            return None
        return format(ctx.trace_id, "032x")
    except Exception:
        return None


async def _post_ocr_webhook(webhook_url: str, envelope: dict[str, Any]) -> None:
    """Async POST the OCR_WEBHOOK envelope. Never raises."""
    try:
        import httpx
    except ImportError:
        logger.warning("ocr_webhook_skipped: httpx not installed")
        return

    headers = {"Content-Type": "application/json"}
    token = os.getenv("OCR_WEBHOOK_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json=envelope, headers=headers)
            if resp.status_code >= 400:
                logger.warning(
                    "ocr_webhook_non_2xx",
                    url=webhook_url,
                    status=resp.status_code,
                    body=resp.text[:200],
                )
    except Exception as e:
        logger.warning(
            "ocr_webhook_failed",
            url=webhook_url,
            error=type(e).__name__,
            detail=str(e)[:200],
        )


def _post_ocr_webhook_sync(webhook_url: str, envelope: dict[str, Any]) -> None:
    """Synchronous fallback for callers without a running event loop."""
    try:
        import httpx
    except ImportError:
        logger.warning("ocr_webhook_skipped: httpx not installed")
        return

    headers = {"Content-Type": "application/json"}
    token = os.getenv("OCR_WEBHOOK_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(webhook_url, json=envelope, headers=headers)
            if resp.status_code >= 400:
                logger.warning(
                    "ocr_webhook_non_2xx",
                    url=webhook_url,
                    status=resp.status_code,
                    body=resp.text[:200],
                )
    except Exception as e:
        logger.warning(
            "ocr_webhook_failed",
            url=webhook_url,
            error=type(e).__name__,
            detail=str(e)[:200],
        )
