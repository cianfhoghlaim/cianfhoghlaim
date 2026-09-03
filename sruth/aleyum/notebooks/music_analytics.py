"""Aleyum Music Analytics Dashboard.

Interactive Marimo notebook for exploring music data from Spotify and SoundCloud.
Visualizes play counts, audio features, and platform comparisons.

Run with: marimo run notebooks/music_analytics.py
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell
def imports():
    """Import dependencies."""
    import marimo as mo
    import ibis
    import altair as alt
    import polars as pl
    from pathlib import Path

    # Configure Altair for better rendering
    alt.data_transformers.enable("vegafusion")

    return mo, ibis, alt, pl, Path


@app.cell
def database_connection(mo, ibis, Path):
    """Connect to the portfolio DuckDB database."""
    db_path = Path("./data/aleyum.duckdb")

    if not db_path.exists():
        mo.md("""
        ## Database Not Found

        The portfolio database hasn't been created yet. Run the data pipelines first:

        ```bash
        # Run Spotify pipeline
        python -m pipelines.spotify.source

        # Run SoundCloud pipeline
        python -m pipelines.soundcloud.scraper
        ```
        """)
        conn = None
    else:
        conn = ibis.duckdb.connect(str(db_path))
        mo.md(f"**Connected to:** `{db_path}`")

    return conn, db_path


@app.cell
def tables_overview(mo, conn):
    """List available tables."""
    if conn is None:
        return mo.md("No database connection")

    tables = conn.list_tables()

    mo.md(f"""
    ## Available Tables

    {', '.join(f'`{t}`' for t in tables)}
    """)

    return tables,


@app.cell
def spotify_tracks_overview(mo, conn, alt, pl):
    """Spotify tracks overview with audio features."""
    if conn is None or "spotify_data_top_tracks" not in conn.list_tables():
        return mo.md("Spotify tracks not loaded yet")

    # Query top tracks
    tracks = conn.table("spotify_data_top_tracks").to_polars()

    # Check if audio features are available
    if "spotify_data_track_audio_features" in conn.list_tables():
        features = conn.table("spotify_data_track_audio_features").to_polars()
        # Join tracks with features
        tracks = tracks.join(features, on="id", how="left")

    mo.md(f"""
    ## Spotify Top Tracks

    **{len(tracks)} tracks loaded**
    """)

    return tracks,


@app.cell
def audio_features_radar(mo, tracks, alt, pl):
    """Radar chart of audio features."""
    if "danceability" not in tracks.columns:
        return mo.md("Audio features not available. Run pipeline with `fetch_audio_features=True`")

    # Select audio feature columns
    feature_cols = ["danceability", "energy", "speechiness", "acousticness",
                    "instrumentalness", "liveness", "valence"]

    available_cols = [c for c in feature_cols if c in tracks.columns]

    if not available_cols:
        return mo.md("No audio features found")

    # Calculate average features
    avg_features = tracks.select(available_cols).mean()

    # Prepare data for radar chart
    radar_data = pl.DataFrame({
        "feature": available_cols,
        "value": [avg_features[c][0] for c in available_cols],
    })

    # Create bar chart (Altair doesn't have native radar, use bar as alternative)
    chart = alt.Chart(radar_data.to_pandas()).mark_bar().encode(
        x=alt.X("feature:N", title="Audio Feature", sort=available_cols),
        y=alt.Y("value:Q", title="Average Value (0-1)", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("feature:N", legend=None),
        tooltip=["feature", alt.Tooltip("value:Q", format=".2f")],
    ).properties(
        title="Average Audio Features Across Top Tracks",
        width=600,
        height=300,
    )

    mo.ui.altair_chart(chart)

    return radar_data, chart


@app.cell
def tempo_distribution(mo, tracks, alt, pl):
    """Distribution of tempo across tracks."""
    if "tempo" not in tracks.columns:
        return mo.md("Tempo data not available")

    tempo_chart = alt.Chart(tracks.to_pandas()).mark_bar().encode(
        x=alt.X("tempo:Q", bin=alt.Bin(maxbins=20), title="Tempo (BPM)"),
        y=alt.Y("count()", title="Number of Tracks"),
        tooltip=["count()"],
    ).properties(
        title="Tempo Distribution",
        width=600,
        height=250,
    )

    mo.ui.altair_chart(tempo_chart)

    return tempo_chart,


@app.cell
def energy_vs_danceability(mo, tracks, alt):
    """Scatter plot of energy vs danceability."""
    if "energy" not in tracks.columns or "danceability" not in tracks.columns:
        return mo.md("Energy/danceability data not available")

    scatter = alt.Chart(tracks.to_pandas()).mark_circle(size=100).encode(
        x=alt.X("energy:Q", title="Energy", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("danceability:Q", title="Danceability", scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("valence:Q", title="Valence (Mood)", scale=alt.Scale(scheme="viridis")),
        tooltip=["name:N", "energy:Q", "danceability:Q", "valence:Q"],
    ).properties(
        title="Energy vs Danceability (colored by mood/valence)",
        width=600,
        height=400,
    )

    mo.ui.altair_chart(scatter)

    return scatter,


@app.cell
def soundcloud_overview(mo, conn, pl):
    """SoundCloud tracks overview."""
    if conn is None:
        return mo.md("No database connection")

    # Check for SoundCloud tables
    tables = conn.list_tables()
    sc_tables = [t for t in tables if "soundcloud" in t.lower()]

    if not sc_tables:
        return mo.md("""
        ## SoundCloud Data Not Loaded

        Run the SoundCloud scraper:
        ```bash
        python -m pipelines.soundcloud.scraper
        ```
        """)

    # Try to load tracks
    if "soundcloud_data_tracks" in tables:
        sc_tracks = conn.table("soundcloud_data_tracks").to_polars()
        mo.md(f"""
        ## SoundCloud Tracks

        **{len(sc_tracks)} tracks scraped**
        """)
        return sc_tracks
    else:
        return mo.md(f"Found tables: {sc_tables}")


@app.cell
def soundcloud_plays_chart(mo, sc_tracks, alt):
    """SoundCloud play counts bar chart."""
    if sc_tracks is None or len(sc_tracks) == 0:
        return mo.md("No SoundCloud tracks available")

    # Sort by play count
    top_tracks = sc_tracks.sort("playback_count", descending=True).head(15)

    plays_chart = alt.Chart(top_tracks.to_pandas()).mark_bar().encode(
        x=alt.X("playback_count:Q", title="Play Count"),
        y=alt.Y("title:N", title="Track", sort="-x"),
        color=alt.Color("likes_count:Q", title="Likes", scale=alt.Scale(scheme="blues")),
        tooltip=["title", "playback_count", "likes_count", "comment_count"],
    ).properties(
        title="Top SoundCloud Tracks by Plays",
        width=700,
        height=400,
    )

    mo.ui.altair_chart(plays_chart)

    return plays_chart,


@app.cell
def platform_comparison(mo, tracks, sc_tracks, alt, pl):
    """Compare metrics across platforms."""
    if tracks is None or sc_tracks is None:
        return mo.md("Need both Spotify and SoundCloud data for comparison")

    # Aggregate stats
    spotify_stats = {
        "platform": "Spotify",
        "total_tracks": len(tracks),
        "avg_popularity": tracks["popularity"].mean() if "popularity" in tracks.columns else 0,
    }

    soundcloud_stats = {
        "platform": "SoundCloud",
        "total_tracks": len(sc_tracks),
        "total_plays": sc_tracks["playback_count"].sum() if "playback_count" in sc_tracks.columns else 0,
        "total_likes": sc_tracks["likes_count"].sum() if "likes_count" in sc_tracks.columns else 0,
    }

    comparison = pl.DataFrame([spotify_stats, soundcloud_stats])

    mo.md(f"""
    ## Platform Comparison

    | Platform | Tracks |
    |----------|--------|
    | Spotify | {spotify_stats['total_tracks']} |
    | SoundCloud | {soundcloud_stats['total_tracks']} |

    **SoundCloud Total Plays:** {soundcloud_stats.get('total_plays', 'N/A'):,}
    **SoundCloud Total Likes:** {soundcloud_stats.get('total_likes', 'N/A'):,}
    """)

    return comparison,


@app.cell
def genre_analysis(mo, sc_tracks, alt):
    """Genre distribution from SoundCloud."""
    if sc_tracks is None or "genre" not in sc_tracks.columns:
        return mo.md("Genre data not available")

    # Filter out empty genres
    genres = sc_tracks.filter(pl.col("genre") != "").group_by("genre").count().sort("count", descending=True)

    if len(genres) == 0:
        return mo.md("No genre data found")

    genre_chart = alt.Chart(genres.to_pandas()).mark_arc().encode(
        theta=alt.Theta("count:Q"),
        color=alt.Color("genre:N", legend=alt.Legend(title="Genre")),
        tooltip=["genre", "count"],
    ).properties(
        title="Genre Distribution",
        width=400,
        height=400,
    )

    mo.ui.altair_chart(genre_chart)

    return genre_chart,


@app.cell
def interactive_track_selector(mo, tracks, sc_tracks, pl):
    """Interactive track selector for detailed view."""
    all_tracks = []

    if tracks is not None and len(tracks) > 0:
        spotify_tracks = tracks.select([
            pl.col("id"),
            pl.col("name").alias("title"),
            pl.lit("Spotify").alias("platform"),
        ]).to_dicts()
        all_tracks.extend(spotify_tracks)

    if sc_tracks is not None and len(sc_tracks) > 0:
        soundcloud_tracks = sc_tracks.select([
            pl.col("id"),
            pl.col("title"),
            pl.lit("SoundCloud").alias("platform"),
        ]).to_dicts()
        all_tracks.extend(soundcloud_tracks)

    if not all_tracks:
        return mo.md("No tracks available")

    track_options = {f"{t['title']} ({t['platform']})": t['id'] for t in all_tracks[:50]}

    selector = mo.ui.dropdown(
        options=track_options,
        label="Select a track to view details",
    )

    return selector,


@app.cell
def track_details(mo, selector, tracks, sc_tracks, pl):
    """Display details for selected track."""
    if selector.value is None:
        return mo.md("Select a track above to view details")

    track_id = selector.value

    # Try to find in Spotify
    if tracks is not None:
        spotify_match = tracks.filter(pl.col("id") == track_id)
        if len(spotify_match) > 0:
            track = spotify_match.to_dicts()[0]
            return mo.md(f"""
            ## {track.get('name', 'Unknown')}

            **Platform:** Spotify
            **Duration:** {track.get('duration_ms', 0) / 1000:.0f}s
            **Popularity:** {track.get('popularity', 'N/A')}

            ### Audio Features
            - **Danceability:** {track.get('danceability', 'N/A')}
            - **Energy:** {track.get('energy', 'N/A')}
            - **Tempo:** {track.get('tempo', 'N/A')} BPM
            - **Valence (Mood):** {track.get('valence', 'N/A')}
            """)

    # Try to find in SoundCloud
    if sc_tracks is not None:
        sc_match = sc_tracks.filter(pl.col("id") == track_id)
        if len(sc_match) > 0:
            track = sc_match.to_dicts()[0]
            return mo.md(f"""
            ## {track.get('title', 'Unknown')}

            **Platform:** SoundCloud
            **Duration:** {track.get('duration_ms', 0) / 1000:.0f}s
            **Genre:** {track.get('genre', 'N/A')}

            ### Engagement
            - **Plays:** {track.get('playback_count', 0):,}
            - **Likes:** {track.get('likes_count', 0):,}
            - **Reposts:** {track.get('reposts_count', 0):,}
            - **Comments:** {track.get('comment_count', 0):,}
            """)

    return mo.md("Track not found")


@app.cell
def export_data(mo, tracks, sc_tracks):
    """Export data options."""
    mo.md("""
    ## Export Data

    Use the data for the portfolio web application:
    """)

    def export_to_json():
        import json
        output = {}
        if tracks is not None:
            output["spotify_tracks"] = tracks.to_dicts()
        if sc_tracks is not None:
            output["soundcloud_tracks"] = sc_tracks.to_dicts()
        return json.dumps(output, indent=2, default=str)

    export_button = mo.ui.button(
        label="Export to JSON",
        on_click=lambda _: mo.download(export_to_json().encode(), filename="music_data.json"),
    )

    return export_button,


if __name__ == "__main__":
    app.run()
