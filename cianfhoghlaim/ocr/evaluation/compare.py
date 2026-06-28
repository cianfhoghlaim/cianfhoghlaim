"""OCR evaluation harness — compare 11 vision × 4 classical × N corpora.

Runs each vision model and each classical OCR Docker stack against the same
document set, scoring with `cianfhoghlaim/ocr/evaluation/gaelic_metrics.py`
(CER, WER, tironian detection, punctum-delens normalisation, fada
consistency).

For Plan 1, the corpora are:
* Ireland syllabus PDFs (early_childhood, primary, junior_cycle, senior_cycle,
  leaving_cert) in EN + GA
* leabharlann/ subdirs (aigne, gaeilge, gemini_deep_research, mata,
  ollscoil_na_gaillimhe, zotero)

Total: ~220 evals (11 vision × 4 classical × Ireland + 6 leabharlann subdirs).
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from cianfhoghlaim.ocr.models.registry import (
    ClassicalOCRStack,
    OCRModel,
    all_classical_stacks,
    all_models,
)


@dataclass
class EvalSample:
    """A single OCR evaluation: model + corpus + document + scores."""

    model_id: str
    backend: str
    corpus: str  # e.g. "ie/education/leaving_cert/gaeilge"
    document_path: str
    duration_s: float
    cer: float  # character error rate
    wer: float  # word error rate
    fada_consistent: bool
    tironian_detected: bool
    punctum_delens_normalised: bool
    notes: str = ""


@dataclass
class EvalReport:
    """Aggregated OCR evaluation report across all models + corpora."""

    started_at: float = field(default_factory=time.time)
    samples: list[EvalSample] = field(default_factory=list)

    def add(self, sample: EvalSample) -> None:
        self.samples.append(sample)

    def summary(self) -> dict[str, float]:
        if not self.samples:
            return {"count": 0, "mean_cer": 0.0, "mean_wer": 0.0}
        return {
            "count": len(self.samples),
            "mean_cer": sum(s.cer for s in self.samples) / len(self.samples),
            "mean_wer": sum(s.wer for s in self.samples) / len(self.samples),
            "fada_consistency": sum(1 for s in self.samples if s.fada_consistent)
            / len(self.samples),
        }

    def write_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(
                {
                    "started_at": self.started_at,
                    "samples": [asdict(s) for s in self.samples],
                    "summary": self.summary(),
                },
                indent=2,
            )
        )


async def _run_vision_eval(model: OCRModel, corpus: str, document: Path) -> EvalSample:
    """Evaluate one vision model on one document. (skeleton — replace with real call)"""
    start = time.time()
    # TODO: call the model's backend via litellm / mlx / transformers / ollama
    # and score against the gold reference using gaelic_metrics.py.
    return EvalSample(
        model_id=model.model_id,
        backend=model.backend,
        corpus=corpus,
        document_path=str(document),
        duration_s=time.time() - start,
        cer=0.0,
        wer=0.0,
        fada_consistent=True,
        tironian_detected=False,
        punctum_delens_normalised=True,
        notes="skeleton",
    )


async def _run_classical_eval(
    stack: ClassicalOCRStack, corpus: str, document: Path
) -> EvalSample:
    """Evaluate one classical OCR stack on one document. (skeleton — replace with real call)"""
    start = time.time()
    # TODO: hit the Docker stack via HTTP and score against the gold reference.
    return EvalSample(
        model_id=stack.stack_name,
        backend=f"docker:{stack.docker_image}",
        corpus=corpus,
        document_path=str(document),
        duration_s=time.time() - start,
        cer=0.0,
        wer=0.0,
        fada_consistent=True,
        tironian_detected=False,
        punctum_delens_normalised=True,
        notes="skeleton",
    )


async def run_corpus_eval(
    corpus_path: Path,
    corpus_label: str,
    *,
    include_classical: bool = True,
) -> EvalReport:
    """Run the full 11 vision × 4 classical eval on a corpus directory."""
    report = EvalReport()
    documents = sorted(p for p in corpus_path.rglob("*.pdf"))
    if not documents:
        documents = sorted(p for p in corpus_path.rglob("*.txt"))

    # Vision model loop (11 models)
    for model in all_models():
        for doc in documents:
            sample = await _run_vision_eval(model, corpus_label, doc)
            report.add(sample)

    # Classical OCR loop (4 stacks)
    if include_classical:
        for stack in all_classical_stacks():
            for doc in documents:
                sample = await _run_classical_eval(stack, corpus_label, doc)
                report.add(sample)

    return report


def build_plan1_corpora() -> list[tuple[Path, str]]:
    """Return the (path, label) pairs for Plan 1 corpora."""
    return [
        # Ireland education (10 corpus dirs = 5 stages × 2 languages)
        (
            Path("cianfhoghlaim/sources/nations/ie/education/early_childhood/english"),
            "ie/education/early_childhood/english",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/early_childhood/gaeilge"),
            "ie/education/early_childhood/gaeilge",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/primary/english"),
            "ie/education/primary/english",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/primary/gaeilge"),
            "ie/education/primary/gaeilge",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/junior_cycle/english"),
            "ie/education/junior_cycle/english",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/junior_cycle/gaeilge"),
            "ie/education/junior_cycle/gaeilge",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/senior_cycle/english"),
            "ie/education/senior_cycle/english",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/senior_cycle/gaeilge"),
            "ie/education/senior_cycle/gaeilge",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/leaving_cert/english"),
            "ie/education/leaving_cert/english",
        ),
        (
            Path("cianfhoghlaim/sources/nations/ie/education/leaving_cert/gaeilge"),
            "ie/education/leaving_cert/gaeilge",
        ),
        # leabharlann (6 subdirs)
        (Path("cianfhoghlaim/leabharlann/aigne"), "leabharlann/aigne"),
        (Path("cianfhoghlaim/leabharlann/gaeilge"), "leabharlann/gaeilge"),
        (
            Path("cianfhoghlaim/leabharlann/gemini_deep_research"),
            "leabharlann/gemini_deep_research",
        ),
        (Path("cianfhoghlaim/leabharlann/mata"), "leabharlann/mata"),
        (
            Path("cianfhoghlaim/leabharlann/ollscoil_na_gaillimhe"),
            "leabharlann/ollscoil_na_gaillimhe",
        ),
        (Path("cianfhoghlaim/leabharlann/zotero"), "leabharlann/zotero"),
    ]


async def run_plan1_eval(output_path: Path) -> EvalReport:
    """Run the full Plan 1 OCR evaluation (~220 evals) and write JSON."""
    report = EvalReport()
    for corpus_path, label in build_plan1_corpora():
        if not corpus_path.exists():
            continue
        sub_report = await run_corpus_eval(corpus_path, label)
        report.samples.extend(sub_report.samples)
    report.write_json(output_path)
    return report


def main() -> None:
    """CLI entry point: `cianfhoghlaim-ocr eval --plan1 --output eval.json`."""
    import argparse

    parser = argparse.ArgumentParser(description="OCR evaluation harness")
    parser.add_argument("--plan1", action="store_true", help="Run Plan 1 corpora")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cianfhoghlaim/ocr/evaluation/last_run.json"),
    )
    args = parser.parse_args()

    if args.plan1:
        asyncio.run(run_plan1_eval(args.output))
        print(f"Wrote OCR evaluation to {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
