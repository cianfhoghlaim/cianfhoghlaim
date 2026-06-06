"""Calibrate command argument parser for ChunkHound CLI."""

import argparse
from typing import Any, cast

from .common_arguments import add_common_arguments, add_config_arguments


def add_calibrate_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Add calibrate command subparser to the main parser.

    Args:
        subparsers: Subparsers object from the main argument parser

    Returns:
        The configured calibrate subparser
    """
    calibrate_parser = subparsers.add_parser(
        "calibrate",
        help="Calibrate batch sizes for optimal performance",
        description=(
            "Benchmark embedding and reranking operations to find optimal batch sizes "
            "for your hardware configuration. Tests different batch sizes and measures "
            "throughput and latency to provide performance-tuned recommendations."
        ),
    )

    # Note: --model and --provider are added via add_config_arguments(["embedding"])

    # Batch size ranges to test
    calibrate_parser.add_argument(
        "--embedding-batch-sizes",
        nargs="+",
        type=int,
        default=[32, 64, 128, 256, 512],
        help="Batch sizes to test for embeddings (default: 32 64 128 256 512)",
    )

    calibrate_parser.add_argument(
        "--reranking-batch-sizes",
        nargs="+",
        type=int,
        default=[32, 64, 96, 128],
        help="Batch sizes to test for reranking (default: 32 64 96 128)",
    )

    # Test parameters
    calibrate_parser.add_argument(
        "--test-document-count",
        type=int,
        default=500,
        help="Number of test documents to process (default: 500)",
    )

    calibrate_parser.add_argument(
        "--num-test-runs",
        type=int,
        default=5,
        help="Number of measurement runs per batch size (default: 5)",
    )

    # Output format
    calibrate_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for results (default: text)",
    )

    calibrate_parser.add_argument(
        "--output-file",
        help="Write results to file (JSON format recommended for config generation)",
    )

    # Add common arguments
    add_common_arguments(calibrate_parser)

    # Add config-specific arguments - only embedding needed
    add_config_arguments(calibrate_parser, ["embedding"])

    return cast(argparse.ArgumentParser, calibrate_parser)


__all__: list[str] = ["add_calibrate_subparser"]
