#!/usr/bin/env python3
"""
Run Ragas Evaluation Suite for Celtic Education Platform.

Executes baseline and agentic RAG evaluations, tracking results in MLflow.

Usage:
    # Run full evaluation suite
    uv run python -m sruth.oideachais.evaluation.run_evaluation

    # Run with specific options
    uv run python -m sruth.oideachais.evaluation.run_evaluation \
        --dataset-size 100 \
        --include-irish \
        --compare

    # Run only baseline
    uv run python -m sruth.oideachais.evaluation.run_evaluation --baseline-only

    # Run only agentic
    uv run python -m sruth.oideachais.evaluation.run_evaluation --agentic-only

Expected Results (from taighde/mlflow_ragas.md):
    - Baseline single-query RAG: ~65.2% accuracy
    - Agentic multi-query RAG:   ~87.9% accuracy (+22.7% improvement)
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_evaluation(
    dataset_size: int = 100,
    include_irish: bool = True,
    run_baseline: bool = True,
    run_agentic: bool = True,
    compare: bool = True,
    save_dataset: bool = True,
) -> dict:
    """
    Run the full evaluation suite.

    Args:
        dataset_size: Number of evaluation questions
        include_irish: Include Irish language questions
        run_baseline: Run baseline single-query evaluation
        run_agentic: Run agentic multi-query evaluation
        compare: Compare baseline vs agentic results
        save_dataset: Save dataset to JSON

    Returns:
        Dictionary with evaluation results
    """
    from sruth.oideachais.evaluation.ragas_pipeline import (
        create_curriculum_eval_dataset,
        run_baseline_evaluation,
        run_agentic_evaluation,
        compare_evaluation_runs,
    )

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "dataset_size": dataset_size,
        "include_irish": include_irish,
    }

    # Create evaluation dataset
    logger.info(f"Creating evaluation dataset with {dataset_size} questions...")
    dataset = await create_curriculum_eval_dataset(
        size=dataset_size,
        include_irish=include_irish,
        domains=["curriculum", "exam"],
    )
    logger.info(f"Created dataset with {dataset.size} questions")

    # Save dataset
    if save_dataset:
        dataset_path = PROJECT_ROOT / "storage" / "evaluation" / f"eval_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        dataset.save(dataset_path)
        results["dataset_path"] = str(dataset_path)
        logger.info(f"Saved dataset to {dataset_path}")

    run_ids = []

    # Run baseline evaluation
    if run_baseline:
        logger.info("Running baseline single-query RAG evaluation...")
        try:
            baseline_result = await run_baseline_evaluation(
                dataset=dataset,
                experiment_name="baseline_rag",
            )
            results["baseline"] = baseline_result
            run_ids.append(baseline_result.get("run_id"))

            logger.info(f"Baseline results:")
            logger.info(f"  - Faithfulness: {baseline_result.get('faithfulness', 'N/A')}")
            logger.info(f"  - Answer Relevancy: {baseline_result.get('answer_relevancy', 'N/A')}")
            logger.info(f"  - Context Precision: {baseline_result.get('context_precision', 'N/A')}")
            logger.info(f"  - Answer Correctness: {baseline_result.get('answer_correctness', 'N/A')}")

        except Exception as e:
            logger.error(f"Baseline evaluation failed: {e}")
            results["baseline_error"] = str(e)

    # Run agentic evaluation
    if run_agentic:
        logger.info("Running agentic multi-query RAG evaluation...")
        try:
            agentic_result = await run_agentic_evaluation(
                dataset=dataset,
                experiment_name="agentic_rag",
                num_queries=3,
                enable_self_correction=True,
            )
            results["agentic"] = agentic_result
            run_ids.append(agentic_result.get("run_id"))

            logger.info(f"Agentic results:")
            logger.info(f"  - Faithfulness: {agentic_result.get('faithfulness', 'N/A')}")
            logger.info(f"  - Answer Relevancy: {agentic_result.get('answer_relevancy', 'N/A')}")
            logger.info(f"  - Context Precision: {agentic_result.get('context_precision', 'N/A')}")
            logger.info(f"  - Answer Correctness: {agentic_result.get('answer_correctness', 'N/A')}")
            logger.info(f"  - Avg Queries/Question: {agentic_result.get('avg_queries_per_question', 'N/A')}")
            logger.info(f"  - Avg Contexts/Question: {agentic_result.get('avg_contexts_per_question', 'N/A')}")

        except Exception as e:
            logger.error(f"Agentic evaluation failed: {e}")
            results["agentic_error"] = str(e)

    # Compare runs
    if compare and len(run_ids) >= 2:
        logger.info("Comparing evaluation runs...")
        try:
            comparison = compare_evaluation_runs(
                run_ids=[r for r in run_ids if r is not None],
                metric="answer_correctness",
            )
            results["comparison"] = comparison

            if "improvement_percentage" in comparison:
                logger.info(f"\n{'='*60}")
                logger.info(f"IMPROVEMENT SUMMARY")
                logger.info(f"{'='*60}")
                logger.info(f"Baseline score: {comparison['baseline_score']:.1%}")
                logger.info(f"Agentic score:  {comparison['improved_score']:.1%}")
                logger.info(f"Improvement:    {comparison['improvement_percentage']:.1f}%")
                logger.info(f"{'='*60}")

                # Check if we hit the target
                target_improvement = 22.7
                if comparison['improvement_percentage'] >= target_improvement:
                    logger.info(f"✅ TARGET ACHIEVED: {comparison['improvement_percentage']:.1f}% >= {target_improvement}%")
                else:
                    logger.info(f"🎯 Target: {target_improvement}% improvement (from 65.2% to 87.9%)")

        except Exception as e:
            logger.error(f"Run comparison failed: {e}")
            results["comparison_error"] = str(e)

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run Ragas evaluation suite for Celtic Education Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Run full evaluation (baseline + agentic + comparison)
    python -m sruth.oideachais.evaluation.run_evaluation

    # Quick test with fewer samples
    python -m sruth.oideachais.evaluation.run_evaluation --dataset-size 20

    # Run only agentic evaluation
    python -m sruth.oideachais.evaluation.run_evaluation --agentic-only

Expected Results:
    Baseline accuracy:  ~65.2%
    Agentic accuracy:   ~87.9%
    Improvement:        ~22.7%
        """,
    )

    parser.add_argument(
        "--dataset-size",
        type=int,
        default=100,
        help="Number of evaluation questions (default: 100)",
    )
    parser.add_argument(
        "--include-irish",
        action="store_true",
        default=True,
        help="Include Irish language questions",
    )
    parser.add_argument(
        "--no-irish",
        action="store_true",
        help="Exclude Irish language questions",
    )
    parser.add_argument(
        "--baseline-only",
        action="store_true",
        help="Run only baseline evaluation",
    )
    parser.add_argument(
        "--agentic-only",
        action="store_true",
        help="Run only agentic evaluation",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="Skip comparison",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save dataset to file",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine what to run
    run_baseline = not args.agentic_only
    run_agentic = not args.baseline_only
    compare = not args.no_compare and run_baseline and run_agentic
    include_irish = args.include_irish and not args.no_irish

    logger.info(f"Starting evaluation suite")
    logger.info(f"  Dataset size: {args.dataset_size}")
    logger.info(f"  Include Irish: {include_irish}")
    logger.info(f"  Run baseline: {run_baseline}")
    logger.info(f"  Run agentic: {run_agentic}")
    logger.info(f"  Compare runs: {compare}")

    # Run evaluation
    results = asyncio.run(
        run_evaluation(
            dataset_size=args.dataset_size,
            include_irish=include_irish,
            run_baseline=run_baseline,
            run_agentic=run_agentic,
            compare=compare,
            save_dataset=not args.no_save,
        )
    )

    # Print summary
    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)

    if "baseline" in results:
        print(f"\nBaseline Results:")
        for key in ["faithfulness", "answer_relevancy", "context_precision", "answer_correctness"]:
            value = results["baseline"].get(key)
            if value is not None:
                print(f"  {key}: {value:.2%}" if isinstance(value, float) else f"  {key}: {value}")

    if "agentic" in results:
        print(f"\nAgentic Results:")
        for key in ["faithfulness", "answer_relevancy", "context_precision", "answer_correctness"]:
            value = results["agentic"].get(key)
            if value is not None:
                print(f"  {key}: {value:.2%}" if isinstance(value, float) else f"  {key}: {value}")

    if "comparison" in results and "improvement_percentage" in results["comparison"]:
        print(f"\nImprovement: {results['comparison']['improvement_percentage']:.1f}%")
        print(f"(Target: 22.7% based on taighde/mlflow_ragas.md research)")

    print("=" * 60)

    # Return success/failure
    return 0 if "baseline_error" not in results and "agentic_error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())
