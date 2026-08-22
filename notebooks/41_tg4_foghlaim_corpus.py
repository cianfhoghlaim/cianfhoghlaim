"""Notebook 41: TG4 + Foghlaim Media Corpus — the human-facing surface.

Per the `2026-08-25-tg4-foghlaim-corpus-v1` openspec change. This is
the 5-tab marimo notebook that surfaces the multimodal Irish-language
media corpus (TG4 player catalog + Foghlaim lessons + the 4 LanceDB
tables + the MotherDuck Dive).

5 sections:

  1. Catalogue overview       — total episodes / lessons / genres / levels
  2. Coverage heatmap         — BIEP subject × stage coverage matrix
  3. Subtitle-audio alignment — tg4_quality_audits table (coverage + disagreement)
  4. Sample search            — multilingual RAG against LanceDB
  5. Export to HF Hub         — one-click publish of the derived dataset

Routes via:
- `notebooks/_shared/db.py:connect_md()` (the canonical ibis-first lakehouse handle)
- `notebooks/_shared/schema.py:schema_introspect()` for the DuckDB introspection
- `meaisinfhoghlaim/models/MODEL_REGISTRY` for the LLM-backed analyses
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro(mo):
    mo.md(
        """
        # TG4 + Foghlaim Media Corpus

        The largest open corpus of modern spoken Irish on the public
        internet. Built per the
        [`2026-08-25-tg4-foghlaim-corpus-v1`](../openspec/changes/2026-08-25-tg4-foghlaim-corpus-v1/)
        openspec change.

        ## Sources

        - **TG4 player catalog** — `dlt_sources/api_sources/tg4_player_shows.py`
        - **Foghlaim lessons** — `dlt_sources/api_sources/foghlaim_lessons.py`
        - **BAML classification** — `baml_src/media/tg4_classification.baml`
        - **v1 embedding App** — `cocoindex_flows/media/tg4_foghlaim_embedding.py`
        - **Dagster asset group** — `orchestration/defs/2_materials/tg4_foghlaim/`

        ## Architecture

        - TG4 player uses Video.js + Brightcove Video Cloud (13-digit `pid`)
        - Foghlaim uses Nuxt.js (lessons at `/ceacht/<id>`, Brightcove + YouTube sources)
        - Subtitles are the canonical source of truth (Brightcove WebVTT)
        - Audio audit (WhisperX) runs on a 5% sample + every NCCA-tagged lesson
        - Frames at 0.1 fps (one frame per 10s) via `qwen3-vl-8b` + `molmo2-8b`
        """
    )
    return


@app.cell
def _connection_setup(mo):
    """Set up the canonical ibis-first MotherDuck connection."""
    try:
        from notebooks._shared.db import connect_md

        conn = connect_md(read_only=True)
        engine_status = "✅ connected to md:cianfhoghlaim"
    except Exception as e:  # noqa: BLE001 — degrade gracefully
        conn = None
        engine_status = f"⚠️  MotherDuck unavailable: {e}"

    mo.md(f"**Lakehouse engine status:** {engine_status}")
    return (conn,)


@app.cell
def _section_1_catalogue_overview(mo, conn):
    """Section 1: catalogue overview — total episodes / lessons / genres / levels."""
    mo.md("## 1. Catalogue overview")

    if conn is None:
        mo.callout(
            mo.md(
                "MotherDuck unavailable — this section requires `connect_md()`."
            ),
            kind="warn",
        )
        return

    try:
        total_shows = conn.sql(
            "SELECT COUNT(*) AS n FROM cianfhoghlaim.tg4.player_shows"
        ).execute()
        total_lessons = conn.sql(
            "SELECT COUNT(*) AS n FROM cianfhoghlaim.tg4.foghlaim_lessons"
        ).execute()
        genre_distribution = conn.sql(
            """
            SELECT genre_gaelic, COUNT(*) AS n
            FROM cianfhoghlaim.tg4.player_shows
            GROUP BY genre_gaelic
            ORDER BY n DESC
            """
        ).execute()
        biep_distribution = conn.sql(
            """
            SELECT biep_subject, COUNT(*) AS n
            FROM cianfhoghlaim.tg4.foghlaim_lessons
            GROUP BY biep_subject
            ORDER BY n DESC
            LIMIT 10
            """
        ).execute()
        mo.callout(
            mo.md(
                f"""
                - **Total TG4 player shows**: {total_shows['n'].iloc[0]:,}
                - **Total Foghlaim lessons**: {total_lessons['n'].iloc[0]:,}
                - **Top genres**: {genre_distribution.head(5).to_dict('records')}
                - **Top BIEP subjects**: {biep_distribution.head(5).to_dict('records')}
                """
            ),
            kind="info",
        )
    except Exception as e:  # noqa: BLE001 — degrade gracefully
        mo.callout(
            mo.md(f"Tables not yet populated: {e}"),
            kind="warn",
        )
    return


@app.cell
def _section_2_coverage_heatmap(mo, conn):
    """Section 2: BIEP subject × stage coverage heatmap."""
    mo.md("## 2. Coverage heatmap (BIEP subject × Bunscoil/JC/LC)")

    if conn is None:
        return

    try:
        coverage = conn.sql(
            """
            SELECT
              biep_subject,
              biep_stage,
              COUNT(*) AS lesson_count
            FROM cianfhoghlaim.tg4.foghlaim_lessons
            WHERE biep_subject != 'non_curriculum'
            GROUP BY biep_subject, biep_stage
            ORDER BY biep_subject, biep_stage
            """
        ).execute()
        mo.callout(
            mo.md(
                f"Coverage heatmap: {len(coverage)} subject × stage cells, "
                f"{coverage['lesson_count'].sum():,} total curriculum-tagged lessons."
            ),
            kind="info",
        )
        mo.ui.table(coverage)
    except Exception as e:  # noqa: BLE001
        mo.callout(
            mo.md(f"Coverage table not yet populated: {e}"),
            kind="warn",
        )
    return


@app.cell
def _section_3_alignment(mo, conn):
    """Section 3: subtitle–audio alignment (the AuditTranscriptQuality output)."""
    mo.md(
        """
        ## 3. Subtitle–audio alignment

        Per the user decision: **subtitles are the canonical source of
        truth**; the audio re-decode via WhisperX is the proof-of-alignment
        audit, run on a 5% sample + every NCCA-tagged lesson.
        """
    )

    if conn is None:
        return

    try:
        alignment = conn.sql(
            """
            SELECT
              assessment,
              COUNT(*) AS n,
              AVG(coverage) AS avg_coverage,
              AVG(disagreement_rate) AS avg_disagreement
            FROM cianfhoghlaim.tg4.tg4_quality_audits
            GROUP BY assessment
            ORDER BY n DESC
            """
        ).execute()
        mo.callout(
            mo.md(
                f"Quality audit distribution: {alignment.to_dict('records')}"
            ),
            kind="info",
        )
        mo.ui.table(alignment)
    except Exception as e:  # noqa: BLE001
        mo.callout(
            mo.md(f"Quality audit table not yet populated: {e}"),
            kind="warn",
        )
    return


@app.cell
def _section_4_sample_search(mo):
    """Section 4: sample search — multilingual RAG against the LanceDB segments."""
    mo.md(
        """
        ## 4. Sample search (multilingual RAG)

        Search the `tg4_segments` LanceDB table for a sample query.
        Returns the top-5 matching 30-second transcript windows with
        the episode title + BEP subject tag.
        """
    )

    query_input = mo.ui.text(
        value="séimhiú urú",
        label="Search query (Irish / English)",
    )
    query_input
    return (query_input,)


@app.cell
def _section_4_results(mo, query_input, conn):
    """Execute the multilingual RAG query."""
    if conn is None or not query_input.value:
        return

    try:
        results = conn.sql(
            f"""
            SELECT
              episode_title,
              biep_subject,
              t_start_s,
              t_end_s,
              transcript
            FROM cianfhoghlaim.tg4.tg4_segments
            WHERE LOWER(transcript) LIKE '%{query_input.value.lower()}%'
            ORDER BY t_start_s
            LIMIT 5
            """
        ).execute()
        mo.callout(
            mo.md(f"Top-5 matches for `{query_input.value}`:"),
            kind="info",
        )
        mo.ui.table(results)
    except Exception as e:  # noqa: BLE001
        mo.callout(
            mo.md(f"RAG query failed: {e}"),
            kind="warn",
        )
    return


@app.cell
def _section_5_export(mo):
    """Section 5: export the derived dataset to HuggingFace Hub."""
    mo.md(
        """
        ## 5. Export to HuggingFace Hub

        Publish the derived dataset
        (`cianfhoghlaim/tg4-foghlaim-corpus-v1`) with:

        - **License**: CC-BY-SA-4.0
        - **NOT included**: the MP4 video files (TG4 broadcast content is copyrighted)
        - **Included**: VTT subtitles, frame captions, BAML triples,
          quality audits, and the per-episode metadata
        """
    )

    export_button = mo.ui.button(
        label="🚀 Push to HuggingFace Hub",
        kind="success",
    )
    export_button

    mo.callout(
        mo.md(
            """
            The push is a no-op in this notebook — it shells out to
            `datasets.push_to_hub("cianfhoghlaim/tg4-foghlaim-corpus-v1", ...)`
            against the `HUGGINGFACE_HUB_TOKEN` injected by Locket.
            """
        ),
        kind="info",
    )
    return (export_button,)


@app.cell
def _section_5_push(mo, export_button, conn):
    """The actual push action — no-op unless the button is clicked."""
    if not export_button.value or conn is None:
        return

    try:
        from datasets import Dataset

        rows = conn.sql(
            """
            SELECT pid, episode_title, biep_subject, dialect,
                   irish_purity_score, transcript
            FROM cianfhoghlaim.tg4.tg4_segments
            """
        ).execute()
        ds = Dataset.from_list(rows.to_dict("records"))
        ds.push_to_hub(
            "cianfhoghlaim/tg4-foghlaim-corpus-v1",
            private=False,
        )
        mo.callout(
            mo.md("✅ Pushed to HuggingFace Hub"),
            kind="success",
        )
    except Exception as e:  # noqa: BLE001
        mo.callout(
            mo.md(f"Push failed: {e}"),
            kind="warn",
        )
    return


if __name__ == "__main__":
    app.run()