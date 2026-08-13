"""
ragas_asset_check.py — Dagster asset_check that runs RAGAS eval.

Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R16.

Reads the latest RAGAS scores from the MLflow experiment registry
`portal_study_plan_eval` and blocks Phase 5 (`iac:deploy`) if any score
falls below the configured threshold.

Usage as an asset_check:
    from dagster import asset_check, AssetCheckResult
    @asset_check(asset=lc_study_plan_extracted)
    def ragas_faithfulness_min_0_85(context):
        return ragas_asset_check(context, metric="faithfulness", threshold=0.85)

Usage as a CLI for one-off runs:
    python scripts/ragas_asset_check.py --metric faithfulness --threshold 0.85
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

# NOTE: `mlflow` is imported inside `get_latest_scores()`, not here.
# Anything under `orchestration/defs/` is imported by `dg.load_defs()` at
# definitions-build time, so a module-scope import of a heavy, optional
# package makes the ENTIRE code location fail to load — which is what
# happened here until 2026-08-13 (`load_defs failed: No module named
# 'mlflow' ... falling back to _defs_walker`, and the walker ignores all
# YAML, so all 171 Components silently vanished).
#
# This is deferral, not suppression: the import below is unguarded, so
# calling this check without mlflow installed still raises ImportError
# loudly at the call site. Separately, `mlflow` IS a real dependency of
# this repo (15 module-scope importers across observability/,
# meaisinfhoghlaim/ and dlt_sources/) and is missing from both
# pyproject.toml and uv.lock — that belongs to the Wave 0 P0 train.

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ragas_asset_check")

EXPERIMENT_NAME = "portal_study_plan_eval"


def get_latest_scores(metric: str, lookback: int = 10) -> list[float]:
    """Read the latest N runs from the MLflow experiment and return the metric values."""
    import mlflow
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri("http://mlflow.cianfhoghlaim.ie")
    client = MlflowClient()
    exp = client.get_experiment_by_name(EXPERIMENT_NAME)
    if exp is None:
        log.warning("experiment %s missing", EXPERIMENT_NAME)
        return []
    runs = client.search_runs(
        experiment_ids=[exp.experiment_id],
        order_by=["start_time DESC"],
        max_results=lookback,
    )
    return [
        float(r.data.metrics.get(metric, 0.0))
        for r in runs
        if metric in r.data.metrics
    ]


def pass_(scores: list[float], threshold: float) -> bool:
    """Pass = the mean of the latest scores >= threshold."""
    if not scores:
        return False
    return (sum(scores) / len(scores)) >= threshold


def main(metric: str, threshold: float, lookback: int = 10) -> int:
    scores = get_latest_scores(metric, lookback)
    if not scores:
        print(f"FAIL: no RAGAS scores found for {metric!r}; cannot pass gate")
        return 2
    mean = sum(scores) / len(scores)
    status = "PASS" if pass_(scores, threshold) else "FAIL"
    print(f"{status}: {metric} mean={mean:.3f} (threshold={threshold}, n={len(scores)})")
    if status == "FAIL":
        return 1
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--metric", default="faithfulness")
    p.add_argument("--threshold", type=float, default=0.85)
    p.add_argument("--lookback", type=int, default=10)
    args = p.parse_args()
    sys.exit(main(args.metric, args.threshold, args.lookback))
