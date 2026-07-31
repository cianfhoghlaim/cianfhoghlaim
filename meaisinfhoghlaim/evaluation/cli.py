"""Operator-facing CLI for the meaisinfoghlaim evaluation harness.

Per the 2026-08-15 meaisinfoghlaim-ireland-england-roadmap (Plan 1).

Usage:
    # Run a per-subject RAGAS eval
    python -m meaisinfoghlaim.evaluation.cli eval         --jurisdiction=ireland --stage=lc --subject=mathematics --language=en

    # Seed a golden baseline (interactive)
    python -m meaisinfoghlaim.evaluation.cli seed-golden         --jurisdiction=ireland --stage=lc --subject=chemistry

    # Show the cross-jurisdiction RAGAS report (aggregates from MLflow)
    python -m meaisinfoghlaim.evaluation.cli report

    # Show per-cohort threshold compliance (Ireland vs England)
    python -m meaisinfoghlaim.evaluation.cli compliance

The CLI uses argparse for subcommand routing. The default subcommand
is eval (so calling the CLI without a subcommand runs the per-subject
eval against the synthetic baseline).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

from meaisinfoghlaim.evaluation.golden_baselines import (
    GoldenBaseline,
    GoldenQuestion,
    GoldenBaselineStore,
)
from meaisinfoghlaim.evaluation.per_subject_runner import (
    CohortKey,
    PerSubjectRunner,
)
from meaisinfoghlaim.evaluation.ragas_metrics import RagasFourMetricScore
from meaisinfoghlaim.evaluation.score_aggregator import ScoreAggregator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Subcommand: eval
# ---------------------------------------------------------------------------
async def cmd_eval(args: argparse.Namespace) -> int:
    """Run a per-subject RAGAS eval for a single cohort."""
    cohort = CohortKey(
        jurisdiction=args.jurisdiction,
        stage=args.stage,
        subject=args.subject,
        board=args.board,
        language=args.language,
    )
    store = GoldenBaselineStore()
    baselines = store.get(cohort)
    if not baselines:
        logger.warning(
            "No golden baseline for %s; using the synthetic placeholder. "
            "Seed one via: python -m meaisinfoghlaim.evaluation.cli seed-golden %s %s %s",
            cohort, args.jurisdiction, args.stage, args.subject,
        )
    runner = PerSubjectRunner()
    result = await runner.run(
        jurisdiction=args.jurisdiction,
        stage=args.stage,
        subject=args.subject,
        board=args.board,
        language=args.language,
        golden_baselines=(
            [
                {
                    "id": q.id,
                    "question": q.question,
                    "ground_truth": q.ground_truth,
                    "question_ga": q.question_ga,
                    "ground_truth_ga": q.ground_truth_ga,
                    "domain": q.domain,
                    "subject": q.subject,
                    "level": q.level,
                    "difficulty": q.difficulty,
                    "source": q.source,
                    "metadata": q.metadata,
                }
                for q in baselines
            ]
            if baselines
            else None
        ),
        threshold=args.threshold,
        metadata={"source": "cli_eval", "operator": args.operator or "unknown"},
    )
    summary = result.summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if result.passed_threshold else 1


# ---------------------------------------------------------------------------
# Subcommand: seed-golden
# ---------------------------------------------------------------------------
def cmd_seed_golden(args: argparse.Namespace) -> int:
    """Seed a golden baseline for a cohort.

    Reads JSONL from --input or creates a synthetic placeholder from
    --count placeholder questions.
    """
    cohort = CohortKey(
        jurisdiction=args.jurisdiction,
        stage=args.stage,
        subject=args.subject,
        board=args.board,
        language=args.language,
    )
    store = GoldenBaselineStore()
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            items = [json.loads(line) for line in f if line.strip()]
        questions = [
            GoldenQuestion(
                id=q["id"],
                question=q["question"],
                ground_truth=q["ground_truth"],
                question_ga=q.get("question_ga"),
                ground_truth_ga=q.get("ground_truth_ga"),
                domain=q.get("domain", "curriculum"),
                subject=q.get("subject", args.subject),
                level=q.get("level", args.stage),
                difficulty=q.get("difficulty", "medium"),
                source=q.get("source"),
                metadata=q.get("metadata", {}),
            )
            for q in items
        ]
    else:
        count = args.count
        questions = [
            GoldenQuestion(
                id=f"placeholder-{args.subject}-q{i}",
                question=f"[PLACEHOLDER] Sample question {i+1} for {args.subject}",
                ground_truth=f"[PLACEHOLDER] Sample ground truth {i+1}",
                domain="curriculum",
                subject=args.subject,
                level=args.stage,
                difficulty="medium",
                source="synthetic_placeholder",
                metadata={"placeholder": True},
            )
            for i in range(count)
        ]
    baseline = GoldenBaseline(
        cohort=cohort,
        questions=questions,
        notes=args.notes or "",
    )
    path = store.save(baseline)
    print(f"Saved {baseline.size} questions to {path}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------
def cmd_report(args: argparse.Namespace) -> int:
    """Show the cross-jurisdiction RAGAS report from the latest MLflow run."""
    try:
        import mlflow  # type: ignore[import-not-found]
    except ImportError:
        print("ERROR: mlflow not installed", file=sys.stderr)
        return 2
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(args.experiment or "biiep_v3")
    if experiment is None:
        print(f"ERROR: experiment {args.experiment!r} not found", file=sys.stderr)
        return 2
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=args.limit or 100,
    )
    agg = ScoreAggregator()
    for run in runs:
        cohort_jurisdiction = run.data.params.get("jurisdiction")
        cohort_stage = run.data.params.get("stage")
        cohort_subject = run.data.params.get("subject")
        cohort_board = run.data.params.get("board")
        cohort_language = run.data.params.get("language")
        if cohort_board == "none":
            cohort_board = None
        if not (cohort_jurisdiction and cohort_stage and cohort_subject):
            continue
        try:
            ragas = RagasFourMetricScore(
                faithfulness=float(run.data.metrics.get("ragas.faithfulness", 0.0)),
                answer_relevancy=float(run.data.metrics.get("ragas.answer_relevancy", 0.0)),
                context_precision=float(run.data.metrics.get("ragas.context_precision", 0.0)),
                context_recall=float(run.data.metrics.get("ragas.context_recall", 0.0)),
            )
        except Exception:
            continue
        from meaisinfoghlaim.evaluation.per_subject_runner import PerSubjectEvalResult

        cohort = CohortKey(
            jurisdiction=cohort_jurisdiction,
            stage=cohort_stage,
            subject=cohort_subject,
            board=cohort_board,
            language=cohort_language or "en",
        )
        result = PerSubjectEvalResult(
            cohort=cohort,
            ragas=ragas,
            passed_threshold=run.data.metrics.get("passed_threshold", 0.0) >= 0.5,
            duration_s=0.0,
            question_count=int(run.data.metrics.get("question_count", 0)),
            golden_baseline_id=None,
            mlflow_run_id=run.info.run_id,
            metadata={},
        )
        agg.add(cohort, result)
    print(json.dumps(agg.cross_jurisdiction_report().summary(), indent=2, ensure_ascii=False))
    return 0


# ---------------------------------------------------------------------------
# Subcommand: compliance
# ---------------------------------------------------------------------------
def cmd_compliance(args: argparse.Namespace) -> int:
    """Show the per-(jurisdiction, subject) threshold compliance matrix."""
    try:
        import mlflow  # type: ignore[import-not-found]
    except ImportError:
        print("ERROR: mlflow not installed", file=sys.stderr)
        return 2
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(args.experiment or "biiep_v3")
    if experiment is None:
        print(f"ERROR: experiment {args.experiment!r} not found", file=sys.stderr)
        return 2
    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id],
        max_results=args.limit or 1000,
    )
    agg = ScoreAggregator()
    for run in runs:
        j = run.data.params.get("jurisdiction")
        s = run.data.params.get("stage")
        sub = run.data.params.get("subject")
        if not (j and s and sub):
            continue
        try:
            ragas = RagasFourMetricScore(
                faithfulness=float(run.data.metrics.get("ragas.faithfulness", 0.0)),
                answer_relevancy=float(run.data.metrics.get("ragas.answer_relevancy", 0.0)),
                context_precision=float(run.data.metrics.get("ragas.context_precision", 0.0)),
                context_recall=float(run.data.metrics.get("ragas.context_recall", 0.0)),
            )
        except Exception:
            continue
        from meaisinfoghlaim.evaluation.per_subject_runner import PerSubjectEvalResult

        cohort = CohortKey(jurisdiction=j, stage=s, subject=sub)
        result = PerSubjectEvalResult(
            cohort=cohort,
            ragas=ragas,
            passed_threshold=run.data.metrics.get("passed_threshold", 0.0) >= 0.5,
            duration_s=0.0,
            question_count=0,
            golden_baseline_id=None,
            mlflow_run_id=run.info.run_id,
            metadata={},
        )
        agg.add(cohort, result)
    matrix = agg.threshold_compliance_matrix()
    print(json.dumps({f"{k[0]}/{k[1]}": v for k, v in sorted(matrix.items())}, indent=2))
    return 0


# ---------------------------------------------------------------------------
# Top-level argparse wiring
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meaisinfoghlaim-evaluation",
        description="Per-cohort RAGAS eval + golden baseline management for the Ireland+England pipeline.",
    )
    sub = parser.add_subparsers(dest="cmd")
    sub.required = False

    # eval (the default subcommand)
    p_eval = sub.add_parser("eval", help="Run a per-subject RAGAS eval")
    p_eval.add_argument("--jurisdiction", required=True)
    p_eval.add_argument("--stage", required=True)
    p_eval.add_argument("--subject", required=True)
    p_eval.add_argument("--board", default=None)
    p_eval.add_argument("--language", default="en")
    p_eval.add_argument("--threshold", type=float, default=None)
    p_eval.add_argument("--operator", default=None)
    p_eval.set_defaults(func=lambda a: asyncio.run(cmd_eval(a)))

    # seed-golden
    p_seed = sub.add_parser("seed-golden", help="Seed a golden baseline for a cohort")
    p_seed.add_argument("--jurisdiction", required=True)
    p_seed.add_argument("--stage", required=True)
    p_seed.add_argument("--subject", required=True)
    p_seed.add_argument("--board", default=None)
    p_seed.add_argument("--language", default="en")
    p_seed.add_argument("--input", default=None, help="JSONL input file")
    p_seed.add_argument("--count", type=int, default=5, help="number of placeholder questions")
    p_seed.add_argument("--notes", default="")
    p_seed.set_defaults(func=cmd_seed_golden)

    # report
    p_report = sub.add_parser("report", help="Show the cross-jurisdiction RAGAS report")
    p_report.add_argument("--experiment", default="biiep_v3")
    p_report.add_argument("--limit", type=int, default=100)
    p_report.set_defaults(func=cmd_report)

    # compliance
    p_compl = sub.add_parser("compliance", help="Show the per-(jurisdiction, subject) threshold compliance matrix")
    p_compl.add_argument("--experiment", default="biiep_v3")
    p_compl.add_argument("--limit", type=int, default=1000)
    p_compl.set_defaults(func=cmd_compliance)

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if args.cmd is None:
        # Default subcommand = eval with synthetic baseline
        args.cmd = "eval"
        args.jurisdiction = "ireland"
        args.stage = "lc"
        args.subject = "mathematics"
        args.board = None
        args.language = "en"
        args.threshold = None
        args.operator = None
        return asyncio.run(cmd_eval(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
