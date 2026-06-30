"""
meaisinfhoghlaim_platform — Python asset module for Domain 3.

Wires the 6 meaisinfhoghlaim AI/ML pipelines as Dagster assets:

1. canuint_audio_slicer — slices Canuint audio recordings
2. dialect_classifier — classifies Irish dialects from audio
3. irish_document_scanner — scans Irish PDFs for OCR
4. llm_router — routes LLM calls via LiteLLM
5. transcript_aligner — aligns transcripts to audio
6. ensemble_gradio — launches a Gradio ensemble UI

These 6 pipelines are the AI/ML layer 2 of the 4-layer asset
graph (per .agents/skills/dagster/SKILL.md). They consume the
Layer 1 DLT sources from Domain 1 + 2 and produce typed outputs
for Layer 3 (CocoIndex) and Layer 4 (asset generation).

Reference: openspec/specs/meaisinfhoghlaim-platform/spec.md
(22 requirements, AI/ML services).
"""
from __future__ import annotations

import dagster as dg


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="python",
    description="Slice Canuint audio recordings into utterances",
)
def canuint_audio_slicer_asset() -> dg.MaterializeResult:
    """Run the canuint_audio_slicer pipeline.

    The actual implementation lives at
    `cianfhoghlaim/pipelines/process/_meaisinfhoghlaim_pipelines/canuint_audio_slicer.py`.
    This asset is a thin Dagster wrapper.
    """
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.canuint_audio_slicer import (
        slice_canuint_recordings,
    )

    result = slice_canuint_recordings()
    return dg.MaterializeResult(
        metadata={"pipeline": "canuint_audio_slicer", "result": str(result)[:500]}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="python",
    description="Classify Irish dialects from audio segments",
)
def dialect_classifier_asset() -> dg.MaterializeResult:
    """Run the dialect_classifier pipeline."""
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.dialect_classifier import (
        classify_dialects,
    )

    result = classify_dialects()
    return dg.MaterializeResult(
        metadata={"pipeline": "dialect_classifier", "result": str(result)[:500]}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="python",
    description="Scan Irish PDFs for OCR and BAML extraction",
)
def irish_document_scanner_asset() -> dg.MaterializeResult:
    """Run the irish_document_scanner pipeline."""
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.irish_document_scanner import (
        IrishDocumentScanner,
    )

    scanner = IrishDocumentScanner()
    result = scanner.scan()
    return dg.MaterializeResult(
        metadata={"pipeline": "irish_document_scanner", "result": str(result)[:500]}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="python",
    description="Route LLM calls via LiteLLM with the minimax alias",
)
def llm_router_asset() -> dg.MaterializeResult:
    """Run the llm_router pipeline."""
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.llm_router import (
        route_llm_call,
    )

    result = route_llm_call()
    return dg.MaterializeResult(
        metadata={"pipeline": "llm_router", "result": str(result)[:500]}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="python",
    description="Align transcripts to Canuint audio segments",
)
def transcript_aligner_asset() -> dg.MaterializeResult:
    """Run the transcript_aligner pipeline."""
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.transcript_aligner import (
        align_transcripts,
    )

    result = align_transcripts()
    return dg.MaterializeResult(
        metadata={"pipeline": "transcript_aligner", "result": str(result)[:500]}
    )


@dg.asset(
    group_name="meaisinfhoghlaim_platform",
    compute_kind="gradio",
    description="Launch the Gradio ensemble UI for the 5 above pipelines",
)
def ensemble_gradio_asset() -> dg.MaterializeResult:
    """Run the ensemble_gradio pipeline."""
    from cianfhoghlaim.pipelines.process._meaisinfhoghlaim_pipelines.ensemble_gradio import (
        launch_ensemble,
    )

    result = launch_ensemble()
    return dg.MaterializeResult(
        metadata={"pipeline": "ensemble_gradio", "result": str(result)[:500]}
    )


# The 6 assets are exported for the defs.yaml loader.
meaisinfhoghlaim_platform_assets = [
    canuint_audio_slicer_asset,
    dialect_classifier_asset,
    irish_document_scanner_asset,
    llm_router_asset,
    transcript_aligner_asset,
    ensemble_gradio_asset,
]


__all__ = ["meaisinfhoghlaim_platform_assets"]
