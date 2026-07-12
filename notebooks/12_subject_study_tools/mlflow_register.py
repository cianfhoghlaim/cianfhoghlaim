"""
mlflow_register.py — MLflow experiment registration for the BAML study-plan eval.

Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R16.

The leaving-cert agentic chat registers an MLflow experiment
`portal_study_plan_eval` and tracks prompt versions + RAGAS scores per run.
The experiment registry is shared with the `/official-media` + `/oideachais`
experiments that the operator already runs.

Usage:
    python -m notebooks.mlflow_register
    # or, programmatically:
    from notebooks.mlflow_register import log_run
    log_run(subject="mathematics", prompt_version="v2.1.0",
            ragas_scores={"faithfulness": 0.92, "answer_relevance": 0.85})

Requires:
    pip install mlflow
    MLFLOW_TRACKING_URI         (default: http://mlflow.cianfhoghlaim.ie)
    MLFLOW_EXPERIMENT_NAME      (default: portal_study_plan_eval)
"""

from __future__ import annotations

import os
import logging
from typing import Any

import mlflow

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mlflow_register")

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow.cianfhoghlaim.ie")
EXPERIMENT_NAME = os.environ.get("MLFLOW_EXPERIMENT_NAME", "portal_study_plan_eval")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)


def log_run(
    subject: str,
    prompt_version: str,
    ragas_scores: dict[str, float],
    *,
    params: dict[str, Any] | None = None,
    trace_id: str | None = None,
    langfuse_project: str | None = None,
) -> str:
    """
    Log one BAML extract run to the MLflow experiment.

    Args:
        subject:          one of 6 BIEP v1 LC subjects (mathematics, chemistry, …)
        prompt_version:   the BAML client + prompt hash (e.g. "ExtractEn@2026-07-12")
        ragas_scores:     {"faithfulness": 0.92, "answer_relevance": 0.85, …}
        params:           any extra MLflow params to log
        trace_id:         the Langfuse trace id (correlates the 2 systems)
        langfuse_project: the Langfuse project name

    Returns:
        the MLflow run id (str)
    """
    base_params: dict[str, Any] = {
        "subject": subject,
        "prompt_version": prompt_version,
    }
    if trace_id:
        base_params["langfuse_trace_id"] = trace_id
    if langfuse_project:
        base_params["langfuse_project"] = langfuse_project
    if params:
        base_params.update(params)

    with mlflow.start_run() as run:
        mlflow.log_params(base_params)
        mlflow.log_metrics(ragas_scores)
        # Tag the run with the openspec change it belongs to so the
        # experiment can be filtered.
        mlflow.set_tags({
            "openspec_change": "2026-07-18-british-isles-portal-activation-v3",
            "requirement": "R16",
            "bilingual": "en,ga",
        })
        # Log the trace_id as a tag for cross-system lookup.
        if trace_id:
            mlflow.set_tag("langfuse_trace_id", trace_id)
        run_id = run.info.run_id
        log.info("logged run %s for subject=%s prompt=%s metrics=%s", run_id, subject, prompt_version, ragas_scores)
        return run_id


if __name__ == "__main__":
    # Smoke run — registers the experiment and logs a baseline.
    run_id = log_run(
        subject="mathematics",
        prompt_version="ExtractEn@2026-07-12",
        ragas_scores={"faithfulness": 0.92, "answer_relevance": 0.85},
        trace_id="trace_placeholder_2026-07-12",
        langfuse_project="baml-extract-en",
    )
    print(f"smoke run registered: {run_id}")
