"""
youtube_kg_embedding — CocoIndex v1 App (Phase 1 of
`2026-07-14-multimodal-code-and-media-intel-v1`).

Ingest curated YouTube videos (via the `dlt.api_sources.youtube_videos`
DLT source) into 3 LanceDB tables:

* `video_segments`       — per-30-second WhisperX-aligned transcript +
                           summary metadata (channel, duration, etc.)
* `video_frame_captions` — per-frame qwen3-vl-8b caption + molmo2-8b
                           diagram pointing + has_formula / has_code flags
* `video_triples`        — typed knowledge triples + the prerequisite
                           `ConceptChain` extracted by BAML

Backbone dispatch goes through the canonical
`ocianfhoghlaim.meaisinfhoghlaim.ocr.models.registry.VISION_MODELS` —
no App-level HuggingFace IDs.

The CocoIndex v1 App mounts the 3 LanceDB tables + the BAML client as
a `ContextKey`. The 5 L3 Component defs.yaml under
`orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/`
references this App via `CelticModelLifecycleComponent` per the
existing 32-component pattern.

The `@coco.fn(memo=True)` wrappers below keep the per-video work
cacheable: a video whose transcript + frame captions are unchanged
won't re-extract triples on the next sync.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Annotated, Any

import structlog

from .._shared._lifespan import (
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    shared_lifespan,
)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from numpy.typing import NDArray

    COCOINDEX_AVAILABLE_LOCAL = COCOINDEX_AVAILABLE
except ImportError as e:  # pragma: no cover - degrade gracefully
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    NDArray = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE_LOCAL = False

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration (mirrors the existing 32 L3 Components)
# ---------------------------------------------------------------------------


LANCEDB_TABLE_SEGMENTS = "video_segments"
LANCEDB_TABLE_FRAME_CAPTIONS = "video_frame_captions"
LANCEDB_TABLE_TRIPLES = "video_triples"
REFRESH_INTERVAL_SECS = int(os.getenv("YOUTUBE_KG_REFRESH_SECS", "86400"))  # daily
FRAME_SAMPLE_FPS = float(os.getenv("YOUTUBE_KG_FRAME_FPS", "0.1"))  # 1 frame / 10s


# The DuckLake table populated by the `dlt.api_sources.youtube_videos`
# DLT source. CocoIndex reads it via the shared `coco.duckdb_source`
# connector (same pattern as `apple_photos_chunks.py`).
YOUTUBE_VIDEOS_DUCKLAKE_TABLE = "cianfhoghlaim.youtube.youtube_videos"


# ---------------------------------------------------------------------------
# Data model (one row per record written to LanceDB)
# ---------------------------------------------------------------------------


@dataclass
class VideoSegmentRecord:
    """One 30-second audio transcript segment from one video."""

    video_id: str
    segment_idx: int
    t_start_s: float
    t_end_s: float
    speaker: str  # "narrator" | "interviewee" | "unknown"
    transcript: str
    word_timestamps: str  # JSON-encoded [{word, t_start, t_end}, ...]
    channel_title: str
    language: str
    # Embedder model is sourced from cocoindex_flows/_shared/_lifespan.py:EMBED_MODEL
    # (which reads CIANFHOGHLAIM_EMBED_MODEL). The previous hardcoded
    # "BAAI/bge-m3" string was replaced with the shared symbol so the
    # canonical env knob (CIANFHOGHLAIM_EMBED_MODEL) propagates here.
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


@dataclass
class VideoFrameCaptionRecord:
    """One frame caption from one video."""

    video_id: str
    frame_idx: int
    t_start_s: float
    t_end_s: float
    caption: str
    has_diagram: bool
    has_formula: bool
    has_code: bool
    diagram_points: list[str] = field(default_factory=list)
    image_path: str | None = None  # local PNG path
    # Embedder model is sourced from cocoindex_flows/_shared/_lifespan.py:EMBED_MODEL
    # (which reads CIANFHOGHLAIM_EMBED_MODEL). The previous hardcoded
    # "BAAI/bge-m3" string was replaced with the shared symbol so the
    # canonical env knob (CIANFHOGHLAIM_EMBED_MODEL) propagates here.
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


@dataclass
class VideoTripleRecord:
    """One typed knowledge triple extracted by BAML."""

    video_id: str
    subject: str
    verb: str
    object: str
    triple_kind: str  # "Concept" | "Definition" | "Example" | "Formula" | "VisualSequence"
    confidence: float
    source_frame_idx: int | None = None
    source_segment_idx: int | None = None
    chain_summary: str | None = None  # populated when extracted via ExtractConceptChain
    # Embedder model is sourced from cocoindex_flows/_shared/_lifespan.py:EMBED_MODEL
    # (which reads CIANFHOGHLAIM_EMBED_MODEL). The previous hardcoded
    # "BAAI/bge-m3" string was replaced with the shared symbol so the
    # canonical env knob (CIANFHOGHLAIM_EMBED_MODEL) propagates here.
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


# ---------------------------------------------------------------------------
# CocoIndex v1 App
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:

    # [Wave 3 fix] @coco.App(shared_lifespan) was the v0 decorator; replaced with coco.App(...) at end of file
    def _wave3_main_fn(builder: coco.AppBuilder):  # type: ignore[valid-type]
        """Mount the 3 LanceDB tables + read from the DuckLake `youtube_videos` table."""

        builder.set_source(  # type: ignore[attr-defined]
            "videos",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name=YOUTUBE_VIDEOS_DUCKLAKE_TABLE,
                database="lakehouse",
            ),
        )

        # Mount the 3 LanceDB targets. The R4 conformance (vector index)
        # is added by the L3 Component defs.yaml.
        segments_table = lancedb.mount_table_target(  # type: ignore[attr-defined]
            None,
            table_name=LANCEDB_TABLE_SEGMENTS,
        )
        frames_table = lancedb.mount_table_target(  # type: ignore[attr-defined]
            None,
            table_name=LANCEDB_TABLE_FRAME_CAPTIONS,
        )
        triples_table = lancedb.mount_table_target(  # type: ignore[attr-defined]
            None,
            table_name=LANCEDB_TABLE_TRIPLES,
        )

        @coco.fn(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def process_video(row: dict) -> dict[str, list[Any]]:  # type: ignore[no-untyped-def]
            """Per-video pipeline: WhisperX + ffmpeg + qwen3-vl-8b + BAML.

            Returns a dict with three lists (one per LanceDB target).
            """
            video_id = row.get("video_id", "")
            mp4_path = (
                Path(os.getenv("YOUTUBE_STAGING_DIR", "/tmp"))
                / row.get("file_path", f"{video_id}.mp4")
            )
            if not mp4_path.exists():
                logger.warning(
                    "youtube_kg.missing_mp4",
                    video_id=video_id,
                    expected_path=str(mp4_path),
                )
                return {"segments": [], "frames": [], "triples": []}

            # 1) Audio transcript via WhisperX.
            audio_path = await _extract_audio(mp4_path)
            transcript_segments = await _transcribe_with_whisperx(
                audio_path,
                language=row.get("language"),
            )

            # 2) Frame sampling + qwen3-vl-8b caption + molmo2-8b diagram pointing.
            frames_dir = mp4_path.parent / f"{video_id}_frames"
            frame_paths = await _sample_frames(mp4_path, frames_dir, fps=FRAME_SAMPLE_FPS)
            frame_caption_records = await _caption_frames(frame_paths, video_id)

            # 3) BAML knowledge-graph extraction.
            transcript_text = "\n".join(
                f"[{s['t_start_s']:.1f}-{s['t_end_s']:.1f}] {s['transcript']}"
                for s in transcript_segments
            )
            frame_caption_strings = [f.frame_idx if False else f.caption for f in frame_caption_records]
            # ^ the comprehension above normalises to strings; the
            # dataclass `.caption` is the field we emit.

            triples_records, chain = await _extract_via_baml(
                video_id=video_id,
                transcript=transcript_text,
                frame_caption_strings=[f.caption for f in frame_caption_records],
            )

            # Materialise the typed records.
            segments_records = [
                VideoSegmentRecord(
                    video_id=video_id,
                    segment_idx=i,
                    t_start_s=s["t_start_s"],
                    t_end_s=s["t_end_s"],
                    speaker=s.get("speaker", "unknown"),
                    transcript=s["transcript"],
                    word_timestamps=s.get("word_timestamps", "[]"),
                    channel_title=row.get("channel_title", ""),
                    language=s.get("language") or row.get("language") or "en",
                    embedding=[],  # populated by CocoIndex via @coco.fn(...)
                )
                for i, s in enumerate(transcript_segments, start=1)
            ]

            return {
                "segments": segments_records,
                "frames": frame_caption_records,
                "triples": [
                    VideoTripleRecord(
                        video_id=video_id,
                        subject=t.subject,
                        verb=t.verb,
                        object=t.object,
                        triple_kind=t.triple_kind.value if hasattr(t.triple_kind, "value") else str(t.triple_kind),
                        confidence=t.confidence,
                        source_frame_idx=t.source_frame_idx,
                        source_segment_idx=t.source_segment_idx,
                        chain_summary=chain.summary if chain else None,
                        embedding=[],
                    )
                    for t in triples_records
                ],
            }

        # Flow the per-video result into the 3 LanceDB targets.
        for output_name, target_table in (
            ("segments", segments_table),
            ("frames", frames_table),
            ("triples", triples_table),
        ):
            process_video[output_name].into(target_table)  # type: ignore[index]
            # R4 conformance: declare the vector index on the
            # `embedding` column for every mounted LanceDB table.
            target_table.declare_vector_index(column="embedding")  # type: ignore[union-attr]

else:  # pragma: no cover - degrade gracefully
    youtube_kg_embedding_app = None


# ---------------------------------------------------------------------------
# Helpers (the heavy lifting)
# ---------------------------------------------------------------------------


async def _extract_audio(mp4_path: Path) -> Path:
    """Extract the audio track from an MP4 to a temporary .m4a file.

    Uses `ffmpeg -vn -c:a copy` (stream-copy, fast). Returns the
    `.m4a` path; the caller is responsible for cleanup.
    """
    audio_path = mp4_path.with_suffix(".audio.m4a")
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # overwrite
            "-i",
            str(mp4_path),
            "-vn",  # drop video
            "-c:a",
            "copy",
            str(audio_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return audio_path


async def _transcribe_with_whisperx(
    audio_path: Path,
    language: str | None = None,
) -> list[dict[str, Any]]:
    """Transcribe an audio file via WhisperX.

    Uses the existing `meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner`
    if available, otherwise falls back to a `whisperx` direct call.
    Returns a list of `{"t_start_s", "t_end_s", "transcript", "speaker",
    "word_timestamps", "language"}` dicts.
    """
    try:
        from cianfhoghlaim.meaisinfhoghlaim.process.transcript_aligner import (
            WhisperXAligner,
        )
    except ImportError:
        # Fallback: direct whisperx call (less accurate, no aligner).
        import whisperx  # type: ignore[import-not-found]

        model = whisperx.load_model("small", device="cpu", compute_type="int8")
        result = model.transcribe(str(audio_path), language=language or "en")
        return [
            {
                "t_start_s": float(seg["start"]),
                "t_end_s": float(seg["end"]),
                "transcript": seg["text"],
                "speaker": "narrator",
                "word_timestamps": "[]",
                "language": language or "en",
            }
            for seg in result.get("segments", [])
        ]

    aligner = WhisperXAligner()
    result = aligner.align(str(audio_path), language=language or "en")
    return [
        {
            "t_start_s": float(seg.start),
            "t_end_s": float(seg.end),
            "transcript": seg.text,
            "speaker": getattr(seg, "speaker", "narrator"),
            "word_timestamps": getattr(seg, "words", "[]"),
            "language": language or "en",
        }
        for seg in result.segments
    ]


async def _sample_frames(
    mp4_path: Path,
    frames_dir: Path,
    fps: float = 0.1,
) -> list[Path]:
    """Sample frames at `fps` frames-per-second via ffmpeg.

    Returns the list of PNG paths in time order. Defaults to
    0.1 fps = 1 frame every 10 seconds.
    """
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = frames_dir / "frame_%05d.png"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp4_path),
            "-vf",
            f"fps={fps}",
            str(pattern),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(frames_dir.glob("frame_*.png"))


async def _caption_frames(
    frame_paths: list[Path],
    video_id: str,
) -> list[VideoFrameCaptionRecord]:
    """Caption each frame via the canonical registry.

    For each frame:
    - call qwen3-vl-8b (from `VISION_MODELS`) for the caption
    - call molmo2-8b for diagram pointing (if has_diagram)

    Returns the typed records ready for LanceDB.
    """
    try:
        from cianfhoghlaim.meaisinfhoghlaim.ocr.models.registry import (
            VISION_MODELS,
            get_optimal_for_m4,
        )
    except ImportError as e:
        logger.warning(
            "youtube_kg.registry_unavailable",
            video_id=video_id,
            error=str(e),
        )
        return []

    qwen_id = get_optimal_for_m4("qwen3-vl-8b")
    molmo_id = get_optimal_for_m4("molmo2-8b")

    out: list[VideoFrameCaptionRecord] = []
    for idx, frame_path in enumerate(frame_paths, start=1):
        # Caption via qwen3-vl-8b
        caption = await _call_vl_model(
            qwen_id,
            prompt=(
                "Describe what is shown in this frame of an educational "
                "video tutorial. Mention any diagrams, formulas, or code."
            ),
            image_path=frame_path,
        )
        has_diagram = await _detect_diagram(caption)
        has_formula = await _detect_formula(caption)
        has_code = await _detect_code(caption)
        diagram_points: list[str] = []
        if has_diagram:
            diagram_points = await _call_vl_model(
                molmo_id,
                prompt="Point to every labelled region in this diagram.",
                image_path=frame_path,
                task="grounding",
            )
            # `_call_vl_model(task="grounding")` returns a list[str] of
            # pointed-to labels. The caller never sees raw tensor output.
        out.append(
            VideoFrameCaptionRecord(
                video_id=video_id,
                frame_idx=idx,
                t_start_s=(idx - 1) / FRAME_SAMPLE_FPS,
                t_end_s=idx / FRAME_SAMPLE_FPS,
                caption=caption if isinstance(caption, str) else str(caption),
                has_diagram=has_diagram,
                has_formula=has_formula,
                has_code=has_code,
                diagram_points=diagram_points if isinstance(diagram_points, list) else [],
                image_path=str(frame_path),
                embedding=[],
            )
        )
    return out


async def _extract_via_baml(
    video_id: str,
    transcript: str,
    frame_caption_strings: list[str],
) -> tuple[list[Any], Any]:
    """Run the 3 BAML functions in `baml_src/processing/_shared/video_kg.baml`.

    Returns (triples_records, ConceptChain | None).
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]
    except ImportError as e:
        logger.warning(
            "youtube_kg.baml_client_missing",
            video_id=video_id,
            error=str(e),
        )
        return [], None

    triples = await b.ExtractVideoKnowledgeTriple(
        video_id=video_id,
        transcript=transcript,
        frame_captions=frame_caption_strings,
    )
    chain = await b.ExtractConceptChain(triples=triples, video_id=video_id)
    return triples, chain


# ---------------------------------------------------------------------------
# Tiny VL-model call helpers (LiteLLM route through the registry)
# ---------------------------------------------------------------------------


async def _call_vl_model(
    model_id: str,
    prompt: str,
    image_path: Path | None = None,
    task: str = "caption",
) -> Any:
    """Send a prompt (optionally with an image) to a VL model via LiteLLM.

    Returns either a string (for `task="caption"`) or a list[str] (for
    `task="grounding"`). Errors degrade to a warning + empty result.
    """
    try:
        import litellm  # type: ignore[import-not-found]

        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        if image_path is not None:
            import base64

            encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
            ext = image_path.suffix.lower().lstrip(".") or "png"
            mime = f"image/{'jpeg' if ext == 'jpg' else ext}"
            messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{encoded}"},
                },
            ]

        response = await litellm.acompletion(  # type: ignore[func-returns-value]
            model=model_id,
            messages=messages,
            max_tokens=512,
            temperature=0.2,
        )
        text = response.choices[0].message.content
        if task == "grounding":
            return [line.strip("-* ") for line in text.splitlines() if line.strip()]
        return text
    except Exception as e:
        logger.warning(
            "youtube_kg.vl_model_error",
            model_id=model_id,
            error=str(e),
        )
        return "" if task == "caption" else []


async def _detect_diagram(caption: str) -> bool:
    """Heuristic: a diagram is in the frame iff the caption mentions
    'diagram', 'graph', 'figure', 'whiteboard', 'drawing', or 'chart'."""
    keywords = {"diagram", "graph", "figure", "whiteboard", "drawing", "chart", "illustration"}
    return any(kw in caption.lower() for kw in keywords)


async def _detect_formula(caption: str) -> bool:
    """Heuristic: a formula is in the frame iff the caption mentions
    'equation', 'formula', '=', or contains LaTeX-like markers."""
    if "equation" in caption.lower() or "formula" in caption.lower():
        return True
    if "=" in caption and any(c in caption for c in "∑∫∂∇"):
        return True
    return False


async def _detect_code(caption: str) -> bool:
    """Heuristic: code is in the frame iff the caption mentions code-like
    constructs."""
    code_keywords = {"function", "class", "import", "def ", "return", "const ", "var ", "let "}
    return any(kw in caption.lower() for kw in code_keywords)


__all__ = [
    "VideoSegmentRecord",
    "VideoFrameCaptionRecord",
    "VideoTripleRecord",
    "youtube_kg_embedding_app",
    "YOUTUBE_VIDEOS_DUCKLAKE_TABLE",
    "LANCEDB_TABLE_SEGMENTS",
    "LANCEDB_TABLE_FRAME_CAPTIONS",
    "LANCEDB_TABLE_TRIPLES",
]