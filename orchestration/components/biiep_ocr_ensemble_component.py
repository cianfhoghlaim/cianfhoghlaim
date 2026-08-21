"""BIEP OCR ensemble Component (Layer 2).

Referenced by `type:` from
`orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/
biiep_ocr_ensemble/defs.yaml` but never written — `dg.load_defs()` failed with
`orchestration.components has no attribute 'BIEPOCREnsembleComponent'`, which
aborted the entire code location.

WHAT THIS REPLACES
------------------
The hand-written asset at `.../ensemble_comparison/biiep_ocr_ensemble.py`
instantiates `EnsembledExtractor()` and then **never calls `.extract()`**,
returning `{"rows_landed": 0, "ragas_passed": False, "ragas_score": 0.0}` with
a comment reading "Placeholder: real impl materializes 4 * 154 = 616 DuckLake
rows". Its paired asset check then asserted against those same zeros.

This Component calls the extractor for real, and its asset check reads the
actual materialisation metadata rather than the asset's return value — the
rule that breaks the repo's false-success loop.
"""
# Deliberately NOT `from __future__ import annotations` — Dagster's Resolvable
# derives the YAML schema from real (not postponed-string) type annotations.
import importlib
import logging
from dataclasses import dataclass, field
from typing import Any

import dagster as dg
from dagster.components import Component, ComponentLoadContext, Resolvable

logger = logging.getLogger(__name__)


def _import_dotted(path: str) -> Any:
    """Resolve a dotted `module.path.Symbol`, tolerating the stale
    `cianfhoghlaim.` prefix the defs.yaml files still carry.

    The v7 flatten moved `cianfhoghlaim/<pkg>` to `<pkg>` at the repo root,
    but the YAML was never updated, so every path here reads
    `cianfhoghlaim.meaisinfhoghlaim...` while the real module is
    `meaisinfhoghlaim...`. Try the literal path first so a future correct
    path keeps working.
    """
    candidates = [path]
    if path.startswith("cianfhoghlaim."):
        candidates.append(path[len("cianfhoghlaim.") :])

    errors: list[str] = []
    for candidate in candidates:
        module_path, _, symbol = candidate.rpartition(".")
        try:
            return getattr(importlib.import_module(module_path), symbol)
        except (ImportError, AttributeError) as exc:
            errors.append(f"{candidate}: {type(exc).__name__}: {exc}")
    raise dg.Failure(
        description=f"biiep_ensemble_symbol_unresolvable tried={errors}"
    )


@dataclass
class BIEPOCREnsembleComponent(Component, Resolvable):
    """One asset that runs the 4-path OCR/VLM ensemble + one real check.

    Attributes:
        asset_key: Name of the emitted asset.
        ensemble_extractor_class: Dotted path to `EnsembledExtractor`.
        ragas_metric_class: Dotted path to the RAGAS evaluation callable.
        unstract_workflows: Per-jurisdiction Unstract workflow descriptors.
            Each entry drives one ensemble invocation scope.
        ragas_threshold: Minimum mean RAGAS score for the check to pass.
        assertion / asset_check_kind: Documentation for the emitted check.
        mlflow_experiment / grouping: Documentation labels.
        automation_cron: Cron for the AutomationCondition; `"manual"`
            disables auto-materialisation.
    """

    asset_key: str
    ensemble_extractor_class: str
    ragas_metric_class: str = ""
    unstract_workflows: list[dict[str, Any]] = field(default_factory=list)
    ragas_threshold: float = 0.70
    asset_check_kind: str = "ragas_score"
    assertion: str = "ragas_score >= 0.70"
    mlflow_experiment: str = ""
    grouping: str = ""
    automation_cron: str = "manual"

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        if self.automation_cron == "manual":
            # Dagster 1.13 has no `AutomationCondition.manual()` — `None` is how
            # "never auto-materialise, launch by hand" is expressed.
            automation = None
        else:
            automation = dg.AutomationCondition.on_cron(self.automation_cron)

        workflows = self.unstract_workflows
        threshold = self.ragas_threshold
        extractor_path = self.ensemble_extractor_class

        @dg.asset(
            name=self.asset_key,
            group_name="2_materials_ocr_comparison_ensemble",
            compute_kind="ocr_ensemble",
            description=(
                f"L2 4-path OCR/VLM ensemble over {len(workflows)} Unstract "
                f"workflow scopes; RAGAS threshold {threshold}"
            ),
            automation_condition=automation,
        )
        def _ensemble_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
            # Resolved at EXECUTE time — the extractor pulls in httpx, BAML
            # and pymupdf, and anything imported at defs-build time under
            # orchestration/defs takes down the whole code location.
            extractor_cls = _import_dotted(extractor_path)
            extractor = extractor_cls()

            queue = self._pending_documents(context)
            if not queue:
                # No work is not the same as success. Fail rather than emit a
                # zero-row "materialised" event that a downstream check could
                # read as passing.
                raise dg.Failure(
                    description=(
                        "biiep_ensemble_no_input_documents: no PDFs resolved "
                        f"from {len(workflows)} workflow scopes. Populate the "
                        "ingest queue (STEDDING_INGEST_QUEUE) or the Garage "
                        "`oideachais` bucket first."
                    )
                )

            rows_landed = 0
            scores: list[float] = []
            failures: list[str] = []
            for doc in queue:
                try:
                    result = extractor.extract(
                        pdf_path=doc["pdf_path"],
                        baml_function=doc["baml_function"],
                        jurisdiction=doc.get("jurisdiction", "ireland"),
                        scope=doc.get("scope", "education"),
                        subject=doc.get("subject"),
                        board=doc.get("board"),
                        qualification_level=doc.get("qualification_level"),
                    )
                except Exception as exc:  # noqa: BLE001
                    failures.append(f"{doc['pdf_path']}: {type(exc).__name__}: {exc}")
                    continue
                rows_landed += getattr(result, "rows_landed", 0)
                scores.append(result.ragas_score)

            if not scores:
                raise dg.Failure(
                    description=(
                        f"biiep_ensemble_all_documents_failed count={len(queue)} "
                        f"errors={failures[:5]}"
                    )
                )

            mean_score = sum(scores) / len(scores)
            return dg.MaterializeResult(
                metadata={
                    # Every number here is measured, not declared.
                    "rows_landed": rows_landed,
                    "documents_processed": len(scores),
                    "documents_failed": len(failures),
                    "ragas_score_mean": mean_score,
                    "ragas_threshold": threshold,
                    "extractor": extractor_path,
                    "mlflow_experiment": self.mlflow_experiment,
                    "layer": "2_materials",
                }
            )

        @dg.asset_check(
            asset=_ensemble_asset,
            name=f"{self.asset_key}_{self.asset_check_kind}",
            description=self.assertion,
        )
        def _ensemble_check(
            context: dg.AssetCheckExecutionContext,
        ) -> dg.AssetCheckResult:
            # Reads the STORE, not the asset's return value. The previous
            # implementation asserted against literals the asset had just
            # made up, so it could not fail.
            record = context.instance.get_latest_materialization_event(
                _ensemble_asset.key
            )
            entries = (
                record.asset_materialization.metadata
                if record and record.asset_materialization
                else {}
            )
            if "ragas_score_mean" not in entries or "rows_landed" not in entries:
                return dg.AssetCheckResult(
                    passed=False,
                    metadata={
                        "reason": (
                            "no materialisation metadata; the ensemble has not "
                            "run, so its RAGAS score cannot be verified"
                        )
                    },
                )
            mean = float(entries["ragas_score_mean"].value)
            rows = int(entries["rows_landed"].value)
            return dg.AssetCheckResult(
                # Rows must actually exist AND the score must clear the bar.
                passed=rows > 0 and mean >= threshold,
                metadata={
                    "ragas_score_mean": mean,
                    "ragas_threshold": threshold,
                    "rows_landed": rows,
                    "assertion": self.assertion,
                },
            )

        return dg.Definitions(assets=[_ensemble_asset], asset_checks=[_ensemble_check])

    def _pending_documents(
        self, context: dg.AssetExecutionContext
    ) -> list[dict[str, Any]]:
        """Resolve the PDFs to run the ensemble over, from the workflow specs.

        Each `unstract_workflows` entry names a scope (jurisdiction, boards,
        qualification levels). PDFs are read from the local ingest queue —
        `STEDDING_INGEST_QUEUE`, the same source `CelticIngestionComponent`
        uses via `USE_LOCAL_SCRAPES`.
        """
        import os
        import pathlib

        queue_root = pathlib.Path(
            os.environ.get("STEDDING_INGEST_QUEUE", "stedding/ingest_queue")
        )
        if not queue_root.exists():
            context.log.warning(
                f"ingest_queue_missing path={queue_root}; no documents to process"
            )
            return []

        docs: list[dict[str, Any]] = []
        for wf in self.unstract_workflows:
            jurisdictions = wf.get("jurisdictions") or ["ireland"]
            for jurisdiction in jurisdictions:
                scope_dir = queue_root / jurisdiction
                if not scope_dir.exists():
                    continue
                for pdf in sorted(scope_dir.rglob("*.pdf")):
                    docs.append(
                        {
                            "pdf_path": str(pdf),
                            "baml_function": wf.get("name", "ExtractCurriculumSyllabus"),
                            "jurisdiction": jurisdiction,
                            "scope": "education",
                            "qualification_level": (
                                (wf.get("qualification_levels") or [None])[0]
                            ),
                            "board": (wf.get("boards") or [None])[0],
                        }
                    )
        context.log.info(
            f"biiep_ensemble_queue documents={len(docs)} "
            f"workflows={len(self.unstract_workflows)} root={queue_root}"
        )
        return docs


__all__ = ["BIEPOCREnsembleComponent"]
