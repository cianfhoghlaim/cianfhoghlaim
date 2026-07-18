# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "lancedb>=0.20",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""02 — Dúchas folklore with 5-level bounding boxes (the BIG one).

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Visualises the 5-level bounding box alignment
(page → region → sentence → word → letter) on a sample Dúchas
manuscript page, with hover-tooltips showing the Irish transcript +
English translation per bbox.

Reads from:
- `cianfhoghlaim.celtic.duchas.manuscripts` (page-level summaries)
- `cianfhoghlaim.celtic.duchas.bboxes` (5-level bbox child table)
- `cianfhoghlaim.language.duchas_chunks` (LanceDB vector store)
- `cianfhoghlaim.language.duchas_bboxes` (LanceDB bbox child store)

Dual-mode usage:
    # Interactive
    marimo edit 02_duchas_folklore_with_bboxes.py
    # CLI
    uv run 16_celtic_language/02_duchas_folklore_with_bboxes.py --collection cbes --page-id 4606492
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="wide")


@app.cell
def _imports():
    import marimo as mo
    import os
    import sys

    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")

    import duckdb
    import pandas as pd
    import altair as alt
    import ibis
    import json

    return alt, duckdb, ibis, json, mo, os, pd, sys


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Dúchas Folklore — 5-Level Bounding Box Visualisation
        ## *Bailiúchán na Béaloideais Náisiúnta*

        **Source data**: Dúchas DuckLake tables
        (`cianfhoghlaim.celtic.duchas.manuscripts` + `.bboxes` +
        `.transcriptions`) + the 2 LanceDB companion tables.

        **5-level bbox hierarchy**: page → region → sentence → word → letter.
        Letter-level bboxes are NULL-fallback when unavailable
        (pre-1922, low-quality scans).

        LlamaSwap routing:
        - `molmo2-8b` for diagram pointing (Dúchas specialist)
        - `dots-ocr` for layout (Dúchas specialist)

        See `openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`.
        """
    )
    return


@app.cell
def _connect(duckdb, os):
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            duckdb.sql(f"SET motherduck_token='{token}'")
        con = duckdb.connect("md:cianfhoghlaim", read_only=True)
    else:
        db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
        con = duckdb.connect(db_path, read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_collection(alt, con, mo, pd):
    mo.md("## 1. Per-collection breakdown (CBE / CBES / CBEG / CBEF)")
    rows = con.execute(
        """
        SELECT collection,
               COUNT(*) AS n_pages,
               COUNT(DISTINCT volume_id) AS n_volumes,
               COUNT(DISTINCT county) AS n_counties,
               AVG(transcription_confidence) AS avg_confidence
        FROM cianfhoghlaim.celtic.duchas.manuscripts
        GROUP BY collection
        ORDER BY n_pages DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["collection", "n_pages", "n_volumes", "n_counties", "avg_confidence"])
    chart = alt.Chart(df).mark_bar().encode(x="collection:N", y="n_pages:Q", color="collection:N")
    return (chart, df)


@app.cell
def _panel_2_county(alt, con, mo, pd):
    mo.md("## 2. Per-county distribution")
    rows = con.execute(
        """
        SELECT county,
               COUNT(*) AS n_pages,
               COUNT(DISTINCT collection) AS n_collections
        FROM cianfhoghlaim.celtic.duchas.manuscripts
        WHERE county IS NOT NULL
        GROUP BY county
        ORDER BY n_pages DESC
        LIMIT 32
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["county", "n_pages", "n_collections"])
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(y=alt.Y("county:N", sort="-x"), x="n_pages:Q")
    )
    return (chart, df)


@app.cell
def _panel_3_decade(alt, con, mo, pd):
    mo.md("## 3. Per-decade coverage")
    rows = con.execute(
        """
        SELECT SUBSTR(CAST(created_at AS VARCHAR), 1, 4) AS year,
               COUNT(*) AS n_pages
        FROM cianfhoghlaim.celtic.duchas.manuscripts
        WHERE created_at IS NOT NULL
        GROUP BY year
        ORDER BY year
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["year", "n_pages"])
    chart = alt.Chart(df).mark_line(point=True).encode(x="year:O", y="n_pages:Q")
    return (chart, df)


@app.cell
def _panel_4_bbox_overlay(alt, con, mo, pd):
    mo.md("## 4. 5-level bbox overlay on a sample manuscript page")
    page_row = con.execute(
        """
        SELECT page_id, collection, county, primary_language, ga_text, en_translation, image_url
        FROM cianfhoghlaim.celtic.duchas.manuscripts
        WHERE ga_text IS NOT NULL
        LIMIT 1
        """
    ).fetchone()
    if page_row is None:
        mo.md("_(No manuscript pages available — try ingesting first)_")
        return (None,)

    page_id, collection, county, primary_language, ga_text, en_translation, image_url = page_row
    mo.md(
        f"**Page**: `{page_id}` ({collection}, {county}, lang={primary_language})\n\n"
        f"**ga**: _{ga_text[:200]}_\n\n"
        f"**en**: {en_translation[:200] if en_translation else '_not available_'}"
    )

    bboxes = con.execute(
        """
        SELECT bbox_id, level, x1, y1, x2, y2, text, ga_text, en_translation, confidence
        FROM cianfhoghlaim.celtic.duchas.bboxes
        WHERE page_id = ?
        ORDER BY level, bbox_id
        """,
        [page_id],
    ).fetchall()
    if not bboxes:
        mo.md("_(No bounding boxes for this page — bbox extraction not run)_")
        return (page_id,)

    df = pd.DataFrame(
        bboxes,
        columns=["bbox_id", "level", "x1", "y1", "x2", "y2", "text", "ga_text", "en_translation", "confidence"],
    )

    # Altair bbox overlay — mark_rect with x1/x2/y1/y2
    chart = (
        alt.Chart(df)
        .mark_rect(opacity=0.3, stroke="red")
        .encode(
            x="x1:Q",
            x2="x2:Q",
            y="y1:Q",
            y2="y2:Q",
            color="level:N",
            tooltip=["bbox_id", "level", "ga_text", "en_translation", "confidence"],
        )
        .properties(height=400, width=600, title=f"5-level bbox overlay — {page_id}")
    )
    return (chart, page_id)


@app.cell
def _panel_5_topic(alt, con, mo, pd):
    mo.md("## 5. Per-topic classification (HandbookTopicCode A-N)")
    rows = con.execute(
        """
        SELECT topic_code, COUNT(*) AS n_pages
        FROM (
            SELECT UNNEST(STRING_SPLIT(topic_codes, ',')) AS topic_code
            FROM cianfhoghlaim.celtic.duchas.manuscripts
            WHERE topic_codes IS NOT NULL
        )
        WHERE topic_code != ''
        GROUP BY topic_code
        ORDER BY n_pages DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["topic_code", "n_pages"])
    chart = alt.Chart(df).mark_bar().encode(x="n_pages:Q", y=alt.Y("topic_code:N", sort="-x"))
    return (chart, df)


if __name__ == "__main__":
    app.run()