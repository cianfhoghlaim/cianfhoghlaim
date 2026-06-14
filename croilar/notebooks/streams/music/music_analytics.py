"""Aleyum Music Analytics — Spotify + SoundCloud + Labels.

Run with: marimo run notebooks/aleyum/music_analytics.py
WASM export: marimo export wasm notebooks/aleyum/music_analytics.py -o public/wasm/aleyum-music/
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def header():
    import marimo as mo

    return mo.md("# Aleyum — Music Analytics Dashboard")


@app.cell
def imports():
    import duckdb
    import altair as alt
    import marimo as mo
    import polars as pl

    alt.data_transformers.enable("vegafusion")

    data_path = "data/croilar.duckdb"
    conn = duckdb.connect(data_path, read_only=True)

    return mo, duckdb, alt, pl, data_path, conn


@app.cell
def track_overview(mo, conn):
    try:
        tracks = conn.execute(
            "SELECT name, popularity, duration_ms, external_url FROM spotify_data.tracks ORDER BY popularity DESC LIMIT 20"
        ).fetchdf()
        if tracks.empty:
            return mo.md("⚠️ No data yet — run the DLT Spotify pipeline first.")
        return mo.ui.table(tracks, page_size=10)
    except Exception:
        return mo.md("⚠️ Database not available — run DLT pipelines to populate data.")


@app.cell
def audio_features_chart(mo, alt, conn):
    try:
        df = conn.execute(
            "SELECT name, tempo, energy, danceability FROM spotify_data.tracks WHERE tempo > 0 ORDER BY popularity DESC LIMIT 15"
        ).fetchdf()
        if df.empty:
            return mo.md("No audio features available.")

        chart = alt.Chart(df).transform_fold(
            ["energy", "danceability"], as_=["feature", "value"]
        ).mark_bar().encode(
            x=alt.X("name:N", sort="-y", title="Track"),
            y=alt.Y("value:Q", title="Score"),
            color="feature:N",
            tooltip=["name", "feature", "value"],
        ).properties(width=700, height=300)

        return mo.ui.altair_chart(chart)
    except Exception:
        return mo.md("⚠️ Chart data not available.")


@app.cell
def platform_breakdown(mo, conn):
    try:
        spotify_count = conn.execute("SELECT COUNT(*) FROM spotify_data.tracks").fetchone()[0]
        tracks_sc = 0
        try:
            tracks_sc = conn.execute("SELECT COUNT(*) FROM soundcloud_data.tracks").fetchone()[0]
        except Exception:
            pass

        return mo.md(f"""
        ## Platform Breakdown

        | Platform | Tracks |
        |:--|:--|
        | Spotify | {spotify_count} |
        | SoundCloud | {tracks_sc} |
        """)
    except Exception:
        return mo.md("No platform data available.")
