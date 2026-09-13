# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "pandas",
# ]
# ///

"""Agent Training Research — cross-source view across the HuggingFace + Google Cloud playlists.

NEW (2026-09-12 — youtube-source-playlist-support-and-agent-training-v1).
A 4-tab marimo notebook that joins the 2 playlists ingested by the
extended `dlt_sources/api_sources/youtube_videos.py` source (6 HF + 11 GC
= 17 videos) + the cross-source concept extraction from
`baml_src/processing/youtube_cross_source.baml`.

Tabs:
    1. HuggingFace playlist timeline     — the 6 HF videos sorted by date
    2. Google Cloud playlist timeline     — the 11 GC videos sorted by date
    3. Cross-source concepts              — concepts shared across both
    4. Concept deep-dive                  — picked concept + comparison

The notebook reads from the local DuckDB at
`~/Documents/cianfhoghlaim/youtube_local.duckdb` (per the personal-scope
decision in the openspec change). Override via the
`YOUTUBE_LOCAL_DUCKDB` env var.
"""

import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium", app_title="Agent Training Research")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb

    db_path = Path(
        os.environ.get(
            "YOUTUBE_LOCAL_DUCKDB",
            str(Path.home() / "Documents" / "cianfhoghlaim" / "youtube_local.duckdb"),
        )
    )
    if not db_path.exists():
        # Fall back to the smoke-test path from the openspec change
        fallback = Path("/tmp/youtube_smoke/main.duckdb")
        if fallback.exists():
            db_path = fallback
        else:
            return {
                "_db": None,
                "_db_path": db_path,
                "_error": f"No local DuckDB found at {db_path} (or {fallback}). Run the YouTube source first.",
            }

    try:
        conn = duckdb.connect(str(db_path), read_only=True)
    except Exception as exc:
        return {"_db": None, "_db_path": db_path, "_error": str(exc)}

    # Verify the 3 views exist (they're created by apply_migrations())
    expected_views = [
        "youtube_videos",
        "youtube_huggingface_post_training_agents",
        "youtube_google_cloud_ai_agent_crash_course",
        "youtube_playlist_registry",
    ]
    try:
        existing = [
            r[0]
            for r in conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'cianfhoghlaim.youtube'"
            ).fetchall()
        ]
    except Exception as exc:
        return {"_db": None, "_db_path": db_path, "_error": str(exc)}

    return {
        "_db": conn,
        "_db_path": db_path,
        "_error": None,
        "_existing": existing,
        "_missing": [v for v in expected_views if v not in existing],
    }


@app.cell
def _():
    mo_md = mo.md("# Agent Training Research")
    mo_md
    return (mo_md,)


@app.cell
def _(mo):
    """Status banner showing the DB connection state."""
    mo.md(
        f"""
        **DB status:** {'OK' if _db is not None else 'FAILED'} —
        path: `{_db_path}`{' — missing views: ' + str(_missing) if _missing else ''}
        {' — error: ' + _error if _error else ''}
        """
    )
    return


@app.cell
def _():
    """HuggingFace playlist timeline (Tab 1).

    Renders the 6 HF videos sorted by upload date with their
    descriptions + the playlist_index (1-6).
    """
    import pandas as pd

    if _db is None:
        return mo.md("> Connect to the local DuckDB first (run the YouTube source).")

    df = _db.execute(
        """
        SELECT video_id, title, playlist_index, duration_s, upload_date,
               channel_title, description
        FROM cianfhoghlaim.youtube.youtube_huggingface_post_training_agents
        ORDER BY playlist_index
        """
    ).df()
    return df, pd


@app.cell
def _(df, mo, pd):
    """Tab 1: HF playlist timeline visualisation."""
    if df is None or len(df) == 0:
        return mo.md("> No HuggingFace videos found in the local DuckDB yet.")

    # Format the duration as mm:ss
    df_display = df.copy()
    df_display["duration"] = df_display["duration_s"].apply(
        lambda s: f"{int(s // 60)}:{int(s % 60):02d}" if s else "?"
    )
    display_cols = ["playlist_index", "video_id", "title", "duration", "upload_date"]
    return mo.ui.table(df_display[display_cols], selection=None)


@app.cell
def _():
    """Google Cloud playlist timeline (Tab 2)."""
    import pandas as pd

    if _db is None:
        return mo.md("> Connect to the local DuckDB first (run the YouTube source).")

    df = _db.execute(
        """
        SELECT video_id, title, playlist_index, duration_s, upload_date,
               channel_title, description
        FROM cianfhoghlaim.youtube.youtube_google_cloud_ai_agent_crash_course
        ORDER BY playlist_index
        """
    ).df()
    return df, pd


@app.cell
def _(df, mo, pd):
    """Tab 2: GC playlist timeline visualisation."""
    if df is None or len(df) == 0:
        return mo.md("> No Google Cloud videos found in the local DuckDB yet.")

    df_display = df.copy()
    df_display["duration"] = df_display["duration_s"].apply(
        lambda s: f"{int(s // 60)}:{int(s % 60):02d}" if s else "?"
    )
    display_cols = ["playlist_index", "video_id", "title", "duration", "upload_date"]
    return mo.ui.table(df_display[display_cols], selection=None)


@app.cell
def _():
    """Cross-source concepts (Tab 3).

    Reads the `cross_source_concepts` LanceDB table produced by the
    CocoIndex App + decodes the source_evidence_json column.
    For the smoke test, falls back to a stub if the CocoIndex App
    hasn't been run yet — the user can manually trigger it with
    `python -m cocoindex_flows.knowledge_graph.youtube_kg_embedding`.
    """
    if _db is None:
        return []

    # The cross_source_concepts table is in LanceDB, not DuckDB. For the
    # smoke test (no CocoIndex App run yet) we surface a stub message
    # explaining how to populate it.
    return mo.md(
        "> The cross-source concepts table is in LanceDB (not DuckDB). "
        "Run the CocoIndex App to populate it: "
        "`python -m cocoindex_flows.knowledge_graph.youtube_kg_embedding`. "
        "The App reads the DuckLake parent table + emits 1 row per shared "
        "concept to the `cross_source_concepts` LanceDB table."
    )


@app.cell
def _():
    """Playlist registry (bonus surface — used by both playlist timelines)."""
    if _db is None:
        return mo.md("> Connect to the local DuckDB first.")

    df = _db.execute(
        """
        SELECT playlist_id, video_count, first_upload, last_upload,
               total_duration_s, avg_duration_s
        FROM cianfhoghlaim.youtube.youtube_playlist_registry
        ORDER BY playlist_id
        """
    ).df()

    if df is None or len(df) == 0:
        return mo.md("> Playlist registry is empty.")

    # Format durations
    df_display = df.copy()
    df_display["total_duration"] = df_display["total_duration_s"].apply(
        lambda s: f"{int(s // 3600)}h{int((s % 3600) // 60)}m{int(s % 60)}s" if s else "?"
    )
    df_display["avg_duration"] = df_display["avg_duration_s"].apply(
        lambda s: f"{int(s // 60)}:{int(s % 60):02d}" if s else "?"
    )
    return mo.ui.table(
        df_display[
            [
                "playlist_id",
                "video_count",
                "first_upload",
                "last_upload",
                "total_duration",
                "avg_duration",
            ]
        ],
        selection=None,
    )


if __name__ == "__main__":
    app.run()
