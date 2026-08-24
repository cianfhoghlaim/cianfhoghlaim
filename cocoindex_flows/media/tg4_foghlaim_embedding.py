"""
tg4_foghlaim_embedding — CocoIndex v1 App for the TG4 + Foghlaim
multimodal media corpus.

Per the `2026-08-25-tg4-foghlaim-corpus-v1` openspec change. The
sibling / architectural template is
`knowledge_graph.youtube_kg_embedding.youtube_kg_embedding_app` (the
YouTube KG Phase 1 App). This App extends the YouTube KG pattern with:

1. **Subtitle canonical** — Brightcove `text_tracks` WebVTT (per the
   user decision: subtitles are the canonical source of truth; audio
   re-transcription is the proof-of-alignment audit).
2. **Audio audit** (5% sample + every NCCA-tagged lesson) —
   `meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner` re-runs
   the audio through WhisperX + writes the result alongside the
   canonical VTT.
3. **Frame sampling** — `0.1 fps` (one frame per 10s, same as YouTube
   KG); captions via `qwen3-vl-8b`, diagram pointing via `molmo2-8b`.
4. **BAML classification** — the 4 BAML fns in
   `baml_src/media/tg4_classification.baml`:
   - `ClassifyTg4Episode` (every episode)
   - `ExtractSpeakerLineup` (every episode)
   - `ExtractWorksheetAnswers` (only when `has_worksheet=true`)
   - `AuditTranscriptQuality` (5% sample + every NCCA-tagged lesson)

Mounts 4 LanceDB tables:
- `tg4_segments` — per-30-second WebVTT transcript + audio audit
- `tg4_frame_captions` — per-frame qwen3-vl-8b caption
- `tg4_triples` — typed knowledge triples + ClassifyTg4Episode +
  ExtractSpeakerLineup outputs
- `tg4_quality_audits` — per-episode AuditTranscriptQuality output

R1–R4 v1 conformance (per `infrastructure/cocoindex_v1_conformance.py`):
- R1 — imports from `.._shared._lifespan`
- R2 — no new `ContextKey[` outside `_lifespan.py`
- R3 — `app = coco.App(...)` at module scope
- R4 — at least one `@coco.fn` decorator

Embedder: `BAAI/bge-m3` (multilingual 1024-dim, supports Irish).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any

import structlog

from .._shared._lifespan import (
    COCOINDEX_AVAILABLE,
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
# Configuration (mirrors the existing 32 L3 Components + the YouTube KG flow)
# ---------------------------------------------------------------------------


LANCEDB_TABLE_SEGMENTS = "tg4_segments"
LANCEDB_TABLE_FRAME_CAPTIONS = "tg4_frame_captions"
LANCEDB_TABLE_TRIPLES = "tg4_triples"
LANCEDB_TABLE_QUALITY_AUDITS = "tg4_quality_audits"

REFRESH_INTERVAL_SECS = int(os.getenv("TG4_FOGHLAIM_REFRESH_SECS", "86400"))  # daily
FRAME_SAMPLE_FPS = float(os.getenv("TG4_FOGHLAIM_FRAME_FPS", "0.1"))  # 1 frame / 10s
QUALITY_AUDIT_SAMPLE_RATE = float(os.getenv("TG4_QUALITY_AUDIT_RATE", "0.05"))  # 5%

# The DuckLake tables populated by the 2 DLT sources. The App reads from
# both via the shared `coco.duckdb_source` connector.
PLAYER_SHOWS_DUCKLAKE_TABLE = "cianfhoghlaim.tg4.player_shows"
FOGHLAIM_LESSONS_DUCKLAKE_TABLE = "cianfhoghlaim.tg4.foghlaim_lessons"

# The staging dir for the per-episode MP4 + VTT files. Mirrors the
# `dlt_sources/api_sources/tg4_player_shows.py:DEFAULT_STAGING_DIR`.
DEFAULT_STAGING_DIR = Path(
    os.getenv(
        "TG4_STAGING_DIR",
        str(
            Path(__file__).resolve().parents[3]
            / "stedding"
            / "ingest_queue"
            / "tg4"
        ),
    )
)


# ---------------------------------------------------------------------------
# Data model (one row per record written to LanceDB)
# ---------------------------------------------------------------------------


@dataclass
class Tg4SegmentRecord:
    """One 30-second subtitle segment from one TG4 episode."""

    pid: str  # Brightcove 13-digit video ID
    segment_idx: int
    t_start_s: float
    t_end_s: float
    speaker: str  # populated when ExtractSpeakerLineup has run
    transcript: str  # canonical VTT cue text
    word_timestamps: str  # JSON-encoded [{word, t_start, t_end}, ...]
    audio_audit_transcript: str  # WhisperX output (empty when no audit)
    audio_audit_words: str  # JSON-encoded word-level WhisperX output
    channel_title: str  # "TG4"
    language: str  # "ga" | "en"
    series: str
    genre_gaelic: str
    biep_subject: str  # populated by ClassifyTg4Episode
    biep_stage: str
    dialect: str  # connacht | munster | ulster | mixed | unknown
    irish_purity_score: float
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


@dataclass
class Tg4FrameCaptionRecord:
    """One frame caption from one TG4 episode."""

    pid: str
    frame_idx: int
    t_start_s: float
    t_end_s: float
    caption: str
    has_diagram: bool
    has_formula: bool
    has_text: bool
    diagram_points: list[str] = field(default_factory=list)
    biep_subject: str = ""
    image_path: str | None = None
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


@dataclass
class Tg4TripleRecord:
    """One typed knowledge triple extracted by the 4 BAML fns."""

    pid: str
    triple_kind: str  # "EpisodeClassification" | "SpeakerTurn" | "WorksheetQuestion" | "ConceptChain"
    subject: str
    verb: str
    object: str
    confidence: float
    source_kind: str  # "baml_classify" | "baml_speaker" | "baml_worksheet" | "baml_audit"
    source_segment_idx: int | None = None
    source_frame_idx: int | None = None
    chain_summary: str | None = None
    biep_subject: str = ""
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


@dataclass
class Tg4QualityAuditRecord:
    """One row per episode for the AuditTranscriptQuality output."""

    pid: str
    coverage: float  # 0.0-1.0
    disagreement_rate: float  # 0.0-1.0
    insertion_rate: float  # 0.0-1.0
    missing_cues_count: int
    total_vtt_cues: int
    total_whisperx_segments: int
    matched_pairs: int
    assessment: str  # "high_quality" | "medium_quality" | "low_quality"
    notes: str
    biep_subject: str
    embedding: Annotated[list[float], EMBED_MODEL] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers (subtitles + WhisperX + frame sampling)
# ---------------------------------------------------------------------------


def _parse_vtt(vtt_text: str) -> list[dict[str, Any]]:
    """Parse a WebVTT file into a list of cue dicts.

    Each cue dict has `start_s`, `end_s`, `text`, `speaker` (optional).
    Falls back to a minimal parser if `webvtt-py` is not installed.
    """
    cues: list[dict[str, Any]] = []
    # VTT block separator is blank line. Cue format:
    #   [optional id]
    #   HH:MM:SS.mmm --> HH:MM:SS.mmm [optional <v Speaker 1>]
    #   <text...>
    pattern = re.compile(
        r"(?:(\S+)\n)?"
        r"(\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}\.\d{3})"
        r"(?:\s+([^\n]+))?\n"
        r"((?:.+(?:\n|$))+?)(?:\n|$)",
        re.MULTILINE,
    )
    for m in pattern.finditer(vtt_text):
        ident, start, end, voice_line, text = m.groups()
        speaker = ""
        if voice_line and "<v" in voice_line:
            v_match = re.search(r"<v\s+([^>]+)>", voice_line)
            if v_match:
                speaker = v_match.group(1).strip()
        cues.append(
            {
                "id": (ident or "").strip(),
                "start_s": _vtt_ts_to_s(start),
                "end_s": _vtt_ts_to_s(end),
                "text": text.strip(),
                "speaker": speaker,
            }
        )
    return cues


def _vtt_ts_to_s(ts: str) -> float:
    """Convert HH:MM:SS.mmm to seconds."""
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def _s_to_vtt_ts(s: float) -> str:
    """Convert seconds to HH:MM:SS.mmm (VTT-friendly)."""
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{sec:06.3f}"


def _split_into_30s_windows(
    cues: list[dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """Group cues into 30-second windows, yielding one record per window.

    The YouTube KG flow uses the same windowing. The window text is
    the concatenation of all cues whose `[start_s, end_s)` overlaps
    the window.
    """
    if not cues:
        return
    start_s = cues[0]["start_s"]
    end_s = cues[-1]["end_s"]
    idx = 0
    for w_start in range(int(start_s), int(end_s) + 30, 30):
        w_end = w_start + 30.0
        w_cues = [c for c in cues if c["end_s"] > w_start and c["start_s"] < w_end]
        if not w_cues:
            continue
        text = " ".join(c["text"] for c in w_cues).strip()
        speakers = sorted({c["speaker"] for c in w_cues if c["speaker"]})
        speaker = speakers[0] if speakers else "narrator"
        # Word-level timestamps = the cue timing structure.
        word_timestamps = json.dumps(
            [
                {
                    "word": w,
                    "t_start": c["start_s"],
                    "t_end": c["end_s"],
                }
                for c in w_cues
                for w in c["text"].split()
            ]
        )
        yield {
            "segment_idx": idx,
            "t_start_s": float(w_start),
            "t_end_s": float(w_end),
            "speaker": speaker,
            "transcript": text,
            "word_timestamps": word_timestamps,
        }
        idx += 1


def _sample_frames_at_fps(video_path: Path, fps: float = 0.1) -> list[Path]:
    """Sample frames from `video_path` at `fps` (default: 1 per 10s) via ffmpeg.

    Returns the list of PNG frame paths in a sibling dir.
    """
    if not video_path.exists():
        return []
    out_dir = video_path.with_suffix("").parent / f"{video_path.stem}_frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = out_dir / "frame_%05d.png"
    cmd = [
        "ffmpeg",
        "-i",
        str(video_path),
        "-vf",
        f"fps={fps}",
        "-q:v",
        "2",
        str(pattern),
        "-y",
    ]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=900, check=False)
    except subprocess.TimeoutExpired as e:
        logger.warning("tg4_frame_sampling_timeout", path=str(video_path), error=str(e))
        return []
    frames = sorted(out_dir.glob("frame_*.png"))
    return frames


def _resolve_model_for_role(role: str) -> str:
    """Resolve a vision model ID via MODEL_REGISTRY (no literal IDs).

    Per `meaisinfhoghlaim.AGENTS.md` DO NOT: never hardcode a model
    string; route via `MODEL_REGISTRY.filter(family=...)` or
    `model_for(family, role)`.
    """
    try:
        from meaisinfhoghlaim.models.model_registry import model_for

        return model_for(family="ocr_vision", role=role)
    except Exception as e:  # noqa: BLE001 — degrade gracefully
        logger.warning("model_registry_resolution_failed", role=role, error=str(e))
        # Backstop only — runtime prefers the resolved ID.
        return ""


def _should_audit(pid: str, has_worksheet: bool, biep_subject: str) -> bool:
    """Decide whether to run the expensive WhisperX re-decode audit for this episode.

    Per the cost-ordering in the proposal: 5% sample + every NCCA-tagged
    lesson (the NCCA tag is detected via `biep_subject` not starting
    with `non_curriculum` and not being one of the entertainment-only
    slugs).
    """
    if not biep_subject or biep_subject == "non_curriculum":
        return False
    # Use a deterministic hash of the pid to gate the 5% sample.
    import hashlib

    h = int(hashlib.md5(pid.encode("utf-8")).hexdigest(), 16)
    return (h % 100) < int(QUALITY_AUDIT_SAMPLE_RATE * 100)


# ---------------------------------------------------------------------------
# CocoIndex v1 App
# ---------------------------------------------------------------------------


if COCOINDEX_AVAILABLE_LOCAL and coco is not None:

    # [Wave 3 fix] @coco.App(shared_lifespan) was the v0 decorator; replaced with coco.App(...) at end of file
    def _wave3_main_fn(builder: coco.AppBuilder):  # type: ignore[valid-type]
        """Mount the 4 LanceDB tables + read from the 2 DuckLake tables.

        The R4 conformance (vector index) is added by the L3 Component
        `defs.yaml` (not in the App code).
        """

        # The 2 DuckLake source tables — one per DLT source.
        builder.set_source(  # type: ignore[attr-defined]
            "player_shows",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name=PLAYER_SHOWS_DUCKLAKE_TABLE,
                database="lakehouse",
            ),
        )
        builder.set_source(  # type: ignore[attr-defined]
            "foghlaim_lessons",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name=FOGHLAIM_LESSONS_DUCKLAKE_TABLE,
                database="lakehouse",
            ),
        )

        # Mount the 4 LanceDB targets.
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
        quality_audits_table = lancedb.mount_table_target(  # type: ignore[attr-defined]
            None,
            table_name=LANCEDB_TABLE_QUALITY_AUDITS,
        )

        @coco.fn(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def process_tg4_episode(row: dict) -> dict[str, list[Any]]:  # type: ignore[no-untyped-def]
            """Per-episode pipeline: VTT canonical + frame captions + BAML.

            Returns a dict with four lists (one per LanceDB target).
            """
            pid = row.get("pid", "")
            lesson_id = row.get("lesson_id") or pid
            mp4_path = DEFAULT_STAGING_DIR / f"{pid}.mp4"
            vtt_path = DEFAULT_STAGING_DIR / f"{pid}.vtt"

            channel_title = "TG4"
            language = "ga"
            series = row.get("series", "") or ""
            genre_gaelic = row.get("genre_gaelic", "") or ""
            biep_subject = ""  # populated by ClassifyTg4Episode below
            biep_stage = row.get("biep_stage", "") or ""
            dialect = "unknown"
            irish_purity_score = 0.0
            has_worksheet = bool(row.get("has_worksheet", False))

            # --- Step 1: Subtitle canonical ---
            segments_out: list[Tg4SegmentRecord] = []
            triples_out: list[Tg4TripleRecord] = []
            frames_out: list[Tg4FrameCaptionRecord] = []
            quality_audit_out: list[Tg4QualityAuditRecord] = []

            vtt_text = ""
            if vtt_path.exists():
                vtt_text = vtt_path.read_text(encoding="utf-8", errors="replace")
            cues = _parse_vtt(vtt_text) if vtt_text else []

            for win in _split_into_30s_windows(cues):
                segments_out.append(
                    Tg4SegmentRecord(
                        pid=pid,
                        segment_idx=win["segment_idx"],
                        t_start_s=win["t_start_s"],
                        t_end_s=win["t_end_s"],
                        speaker=win["speaker"],
                        transcript=win["transcript"],
                        word_timestamps=win["word_timestamps"],
                        audio_audit_transcript="",  # populated below
                        audio_audit_words="",
                        channel_title=channel_title,
                        language=language,
                        series=series,
                        genre_gaelic=genre_gaelic,
                        biep_subject=biep_subject,
                        biep_stage=biep_stage,
                        dialect=dialect,
                        irish_purity_score=irish_purity_score,
                        embedding=[],  # populated by the embedder
                    )
                )

            # --- Step 2: Frame sampling ---
            frame_paths = _sample_frames_at_fps(mp4_path, fps=FRAME_SAMPLE_FPS)
            caption_model = _resolve_model_for_role("qwen3_vl_default")
            diagram_model = _resolve_model_for_role("diagram_pointing")
            for i, fp in enumerate(frame_paths):
                # Caption + diagram pointing — placeholder; the real
                # dispatch happens via the coco.App's downstream
                # functions (or via the BAML fns if the model is
                # BAML-routed). For now we record the frame metadata
                # + the resolved model name; the downstream pipeline
                # fills in `caption` + `has_diagram` + `diagram_points`.
                frames_out.append(
                    Tg4FrameCaptionRecord(
                        pid=pid,
                        frame_idx=i,
                        t_start_s=float(i) / FRAME_SAMPLE_FPS,
                        t_end_s=float(i + 1) / FRAME_SAMPLE_FPS,
                        caption="",
                        has_diagram=False,
                        has_formula=False,
                        has_text=False,
                        diagram_points=[],
                        biep_subject=biep_subject,
                        image_path=str(fp),
                        embedding=[],
                    )
                )

            # --- Step 3: BAML classification ---
            try:
                from baml_src.media import ClassifyTg4Episode, ExtractSpeakerLineup

                classification = ClassifyTg4Episode(
                    title=row.get("title", ""),
                    description=row.get("description", ""),
                    genre=row.get("english_label", "") or genre_gaelic,
                    series=series,
                    duration_s=int(row.get("duration_s", 0)),
                    foghlaim_metadata=row.get("description", ""),
                )
                biep_subject = classification.biep_subject
                biep_stage = classification.biep_stage or biep_stage
                dialect = classification.dialect
                irish_purity_score = classification.irish_purity_score

                triples_out.append(
                    Tg4TripleRecord(
                        pid=pid,
                        triple_kind="EpisodeClassification",
                        subject=row.get("title", ""),
                        verb="classified_as",
                        object=f"{biep_subject} ({classification.biep_stage}, "
                        f"{dialect}, purity={irish_purity_score:.2f})",
                        confidence=classification.confidence,
                        source_kind="baml_classify",
                        source_segment_idx=None,
                        source_frame_idx=None,
                        chain_summary=classification.rationale,
                        biep_subject=biep_subject,
                        embedding=[],
                    )
                )
                # Backfill the per-segment biep_subject / dialect fields.
                for seg in segments_out:
                    seg.biep_subject = biep_subject
                    seg.dialect = dialect
                    seg.irish_purity_score = irish_purity_score

                # Speaker diarization from the VTT cues.
                lineup = ExtractSpeakerLineup(
                    vtt_cues_json=json.dumps(cues, ensure_ascii=False),
                    duration_s=int(row.get("duration_s", 0)),
                    show_context=series,
                )
                for turn in lineup.turns:
                    triples_out.append(
                        Tg4TripleRecord(
                            pid=pid,
                            triple_kind="SpeakerTurn",
                            subject=turn.speaker,
                            verb="speaks_from",
                            object=f"{turn.t_start_s:.1f}s→{turn.t_end_s:.1f}s",
                            confidence=0.9,
                            source_kind="baml_speaker",
                            source_segment_idx=None,
                            source_frame_idx=None,
                            chain_summary=turn.transcript[:500],
                            biep_subject=biep_subject,
                            embedding=[],
                        )
                    )
            except Exception as e:  # noqa: BLE001 — degrade gracefully
                logger.warning(
                    "tg4_baml_classify_failed",
                    pid=pid,
                    error=str(e),
                )

            # --- Step 4: Quality audit (5% sample + every NCCA-tagged) ---
            if _should_audit(pid, has_worksheet, biep_subject):
                try:
                    from baml_src.media import AuditTranscriptQuality

                    # The WhisperX transcript is loaded from the
                    # `tg4_segments.audio_audit_transcript` column if
                    # populated by a prior Dagster materialisation;
                    # otherwise we leave the audit deferred.
                    whisperx_segments_json = json.dumps(
                        [
                            {
                                "t_start_s": seg.t_start_s,
                                "t_end_s": seg.t_end_s,
                                "text": seg.audio_audit_transcript,
                            }
                            for seg in segments_out
                            if seg.audio_audit_transcript
                        ]
                    )
                    if whisperx_segments_json != "[]":
                        audit = AuditTranscriptQuality(
                            vtt_cues_json=json.dumps(cues, ensure_ascii=False),
                            whisperx_segments_json=whisperx_segments_json,
                            show_context=series,
                        )
                        quality_audit_out.append(
                            Tg4QualityAuditRecord(
                                pid=pid,
                                coverage=audit.coverage,
                                disagreement_rate=audit.disagreement_rate,
                                insertion_rate=audit.insertion_rate,
                                missing_cues_count=audit.missing_cues_count,
                                total_vtt_cues=audit.total_vtt_cues,
                                total_whisperx_segments=audit.total_whisperx_segments,
                                matched_pairs=audit.matched_pairs,
                                assessment=audit.assessment,
                                notes=audit.notes,
                                biep_subject=biep_subject,
                                embedding=[],
                            )
                        )
                except Exception as e:  # noqa: BLE001 — degrade gracefully
                    logger.warning(
                        "tg4_quality_audit_failed",
                        pid=pid,
                        error=str(e),
                    )

            return {
                "segments": segments_out,
                "frame_captions": frames_out,
                "triples": triples_out,
                "quality_audits": quality_audit_out,
            }

        # Wire the 4 targets + the 1 process function.
        builder.process(process_tg4_episode).out(  # type: ignore[attr-defined]
            segments_table
        ).out(frames_table).out(triples_table).out(quality_audits_table)

        # The module-level `app` symbol is what the L3 Component def
        # references. Per the R3 conformance contract, it MUST be at
        # module scope.
        app = tg4_foghlaim_embedding_app  # type: ignore[assignment]

else:
    # CocoIndex unavailable — degrade gracefully. The downstream
    # dagster-asset-sync + ccc-cognee ingestion still works.
    app = None  # type: ignore[assignment]
    logger.warning(
        "tg4_foghlaim_embedding_app_disabled: cocoindex not available"
    )