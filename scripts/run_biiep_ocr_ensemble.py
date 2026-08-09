"""CLI runner for the BIEP v2 4-path OCR/VLM ensemble (per the 2026-08-10-ocr-vision-activation-v1 openspec change).

Usage:
    uv run python scripts/run_biiep_ocr_ensemble.py --pdf <path> [--baml-function ExtractAistearFramework]
    uv run python scripts/run_biiep_ocr_ensemble.py --batch <dir>
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="BIEP v2 OCR ensemble CLI runner")
    parser.add_argument("--pdf", type=str)
    parser.add_argument("--batch", type=str)
    parser.add_argument("--baml-function", type=str, default="ExtractCurriculumSyllabus")
    parser.add_argument("--subject", type=str, default="chemistry")
    parser.add_argument("--jurisdiction", type=str, default="ireland")
    parser.add_argument("--ragas-threshold", type=float, default=0.70)
    args = parser.parse_args()

    if not args.pdf and not args.batch:
        parser.error("Either --pdf or --batch is required")

    pdfs: list[Path] = []
    if args.pdf:
        p = Path(args.pdf)
        if not p.exists():
            print(f"ERROR: PDF not found: {p}", file=sys.stderr)
            return 1
        pdfs.append(p)
    if args.batch:
        batch_dir = Path(args.batch)
        if not batch_dir.exists():
            print(f"ERROR: Batch dir not found: {batch_dir}", file=sys.stderr)
            return 1
        pdfs.extend(sorted(batch_dir.glob("*.pdf")))

    print(f"Processing {len(pdfs)} PDFs through the BIEP v2 4-path ensemble")

    try:
        from meaisinfoghlaim.ocr.ensemble.ensembled_extractor import EnsembledExtractor
    except ImportError as e:
        print(f"ERROR: EnsembledExtractor not available: {e}", file=sys.stderr)
        return 1

    extractor = EnsembledExtractor(ragas_threshold=args.ragas_threshold)
    total_ragas_score = 0.0
    rows_passed = 0
    for pdf in pdfs:
        start = time.time()
        print(f"\n=== {pdf.name} ===")
        try:
            result = extractor.extract(
                pdf_path=pdf,
                baml_function=args.baml_function,
                jurisdiction=args.jurisdiction,
                scope="education",
                subject=args.subject,
                board=None,
                qualification_level="lc",
            )
            elapsed = time.time() - start
            total_ragas_score += result.ragas_score
            if result.ragas_passed:
                rows_passed += 1
            print(f"  ragas_score: {result.ragas_score:.3f} (passed: {result.ragas_passed})")
            print(f"  voted_path:  {result.ragas_voted_path}")
            print(f"  elapsed:     {elapsed:.1f}s")
            for path in result.paths:
                err_str = f" [error: {path.error}]" if path.error else ""
                preview = (path.raw_response or "")[:80].replace("\n", " ")
                print(
                    f"    {path.path:12s} confidence={path.confidence_score:.2f} "
                    f"preview={preview!r}{err_str}"
                )
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR: {e}", file=sys.stderr)

    print(
        f"\nDone. {rows_passed}/{len(pdfs)} passed (threshold {args.ragas_threshold}). "
        f"Average ragas_score: {total_ragas_score / max(len(pdfs), 1):.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
