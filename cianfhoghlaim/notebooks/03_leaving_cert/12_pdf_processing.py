# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "altair>=5.0",
#     "pandas>=2.0",
# ]
# ///
"""Marimo dashboard for the 6-stage PDF processing pipeline — BIEP.

Per `openspec/specs/oideachais-pdf-processing/spec.md` — Requirement:
"Marimo dashboard for processed PDFs".

Visualises the 6-stage pipeline state for any (subject, year, paper)
tuple from the BIEP MotherDuck + DuckLake lakehouse
(``md:oideachais.leabharlann_pdf_processing``).

Pipeline stages:
1. OCR (VLM dispatch) — select_ocr_backend() from the VISION_MODELS registry
2. Diagram detection — Granite-Docling + Molmo2-8B
3. BAML extraction — ExtractLeavingCertSyllabus / ExtractPastPaper / ExtractMarkingScheme
4. Topic validation — fuzzy-match against the NCCA taxonomy
5. Semantic chunking — CocoIndex v1 + BAAI/bge-m3
6. Lakehouse + Cognee + Graphiti — DuckLake + KG + temporal

Run with: `marimo edit 03_pdf_processing.py`
"""
from __future__ import annotations

import marimo

__generated_with = "0.9.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __(mo):
    mo.md(
        """
        # BIEP PDF Processing Dashboard

        Live view of the 6-stage PDF processing pipeline for any
        (subject, year, paper) tuple. Reads from the BIEP MotherDuck +
        DuckLake lakehouse (``md:oideachais.leabharlann_pdf_processing``).

        The 6 stages are: **OCR → Diagram detection → BAML extraction →
        Topic validation → Semantic chunking → Lakehouse + Cognee + Graphiti.**
        """
    )
    return


@app.cell
def __(mo):
    subject_selector = mo.ui.dropdown(
        options=[
            "mathematics",
            "applied_mathematics",
            "english",
            "gaeilge",
            "biology",
            "chemistry",
            "computer_science",
            "french",
            "business",
            "geography",
            "history",
            "physics",
        ],
        value="mathematics",
        label="Subject",
    )
    year_selector = mo.ui.slider(
        start=2010, stop=2026, step=1, value=2024, label="Year"
    )
    paper_selector = mo.ui.dropdown(
        options=["paper-1", "paper-2", "all"], value="paper-1", label="Paper"
    )
    mo.hstack([subject_selector, year_selector, paper_selector])
    return subject_selector, year_selector, paper_selector


@app.cell
def __(mo, subject_selector, year_selector, paper_selector):
    mo.md(
        f"## Selected: {subject_selector.value} / {year_selector.value} / {paper_selector.value}"
    )
    return


@app.cell
def __(mo):
    """Engine selector + DuckDB attach against the BIEP lakehouse."""
    import os
    import duckdb
    import pandas as pd

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    token = os.environ.get("MOTHERDUCK_TOKEN", "")

    df = pd.DataFrame()
    err: str | None = None
    con = None
    engine = "synthetic"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = duckdb.connect("md:oideachais")
            engine = "md:oideachais"
        except Exception as e:
            err = f"md:oideachais attach failed: {e}"

    return con, df, duckdb, engine, err, os, pd, token, use_md


@app.cell
def _(
    con, df, engine, err, mo,
    paper_selector, subject_selector, use_md, year_selector,
):
    """Stage 1 — OCR (VLM dispatch) + per-page confidence.

    Real query against the BIEP lakehouse table
    ``md:oideachais.leabharlann_pdf_processing.ocr_pages``.
    Falls back to a deterministic synthetic sample if the table is
    empty or unreachable.
    """
    import pandas as pd

    if con is None or not use_md:
        # Synthetic fallback (deterministic seed)
        import random as _r

        rng = _r.Random(hash((subject_selector.value, year_selector.value)) & 0xFFFFFFFF)
        rows = [
            {
                "page": i + 1,
                "ocr_model": rng.choice(
                    ["gemma-4-E2B", "qwen3-vl-8b", "glm-4.6v-flash", "molmo2-8b"]
                ),
                "confidence": round(rng.uniform(0.78, 0.99), 3),
                "char_count": rng.randint(800, 6000),
            }
            for i in range(20)
        ]
        df = pd.DataFrame(rows)
        src = "synthetic (deterministic)"
    else:
        try:
            df = con.execute(
                f"""
                SELECT page, ocr_model, confidence, char_count
                FROM md:oideachais.leabharlann_pdf_processing.ocr_pages
                WHERE subject = '{subject_selector.value}'
                  AND year = {int(year_selector.value)}
                  AND ('{paper_selector.value}' = 'all' OR paper = '{paper_selector.value}')
                ORDER BY page
                """
            ).fetchdf()
            src = "md:oideachais.leabharlann_pdf_processing.ocr_pages"
            if df.empty:
                # Fall back to the consolidated ``pdf_extracted_text`` view
                df = con.execute(
                    f"""
                    SELECT page_number AS page,
                           'unknown' AS ocr_model,
                           confidence,
                           length(text) AS char_count
                    FROM md:oideachais.curriculum.pdf_extracted_text
                    WHERE subject = '{subject_selector.value}'
                      AND year = {int(year_selector.value)}
                    ORDER BY page
                    """
                ).fetchdf()
                src = "md:oideachais.curriculum.pdf_extracted_text"
        except Exception as e:
            err = str(e)
            df = pd.DataFrame()
            src = f"error: {e}"

    mo.vstack([
        mo.md(f"### Stage 1 — OCR (VLM dispatch) — source: `{src}`"),
        mo.md(
            "**Dispatch logic** (``cianfhoghlaim/meaisinfhoghlaim/models/registry.py``):\n"
            "- `gemma-4-E2B` for small text-first PDFs (<5 MB)\n"
            "- `qwen3-vl-8b` for SEC exam papers (image-heavy)\n"
            "- `glm-4.6v-flash` for pre-1922 scanned Gaelic texts\n"
            "- `molmo2-8b` for marking-scheme image-heavy"
        ),
        mo.ui.table(df, page_size=10),
        mo.md(f"⚠️ {err}" if err else ""),
    ])
    return rng, rows, src


@app.cell
def _(mo):
    """Stage 2 — Diagram detection (placeholder — table TBD)."""
    import altair as alt

    mo.md(
        """
        ### Stage 2 — Diagram detection

        Per-page diagram detection with bounding-box overlay. Uses
        Granite-Docling 258M (DocTags) for layout classification and
        Molmo2-8B (transformers) for figure-region pointing.

        *(Live table not yet materialised — diagrams land in
        `md:oideachais.leabharlann_pdf_processing.diagrams` once the
        `pdf_processing` Dagster asset's stage-2 step runs. Until then,
        the chart below renders synthetic counts.)*
        """
    )

    import pandas as pd
    import random as _r

    rng = _r.Random(42)
    df = pd.DataFrame(
        {
            "page": list(range(1, 11)),
            "diagrams": [rng.randint(0, 4) for _ in range(10)],
            "tables": [rng.randint(0, 3) for _ in range(10)],
        }
    )
    chart = (
        alt.Chart(df)
        .mark_bar(opacity=0.75)
        .encode(
            x=alt.X("page:O", title="Page"),
            y=alt.Y("diagrams:Q", title="Diagrams / tables"),
            color=alt.Color("diagrams:N", legend=None),
            tooltip=["page", "diagrams", "tables"],
        )
        .properties(width=600, height=240, title="Diagrams detected per page")
    )
    mo.vstack([mo.ui.altair_chart(chart), mo.ui.table(df, page_size=10)])
    return alt, chart, df, pd, rng


@app.cell
def _(con, err, mo, subject_selector, use_md, year_selector):
    """Stage 3 — BAML extraction (typed records).

    Real query against the BIEP lakehouse view
    ``md:oideachais.curriculum.baml_extracted_records`` (one row per
    BAML-typed record — `LeavingCertSyllabusTopic`,
    `LeavingCertPastPaperQuestion`, `LeavingCertMarkingPoint`).
    """
    import pandas as pd

    if con is None or not use_md:
        mo.md(
            "### Stage 3 — BAML extraction (synthetic preview)\n\n"
            "*Connect MotherDuck + run the `pdf_processing` Dagster asset "
            "to populate `oideachais.curriculum.baml_extracted_records`.*"
        )
        return

    try:
        df = con.execute(
            f"""
            SELECT record_type, subject, year, level, topic, marks
            FROM md:oideachais.curriculum.baml_extracted_records
            WHERE subject = '{subject_selector.value}'
              AND year = {int(year_selector.value)}
            ORDER BY record_type, topic
            LIMIT 200
            """
        ).fetchdf()
        mo.vstack([
            mo.md("### Stage 3 — BAML typed records"),
            mo.md(
                f"BAML functions: `ExtractLeavingCertSyllabus`, "
                f"`ExtractLeavingCertPastPaper`, `ExtractLeavingCertMarkingScheme` "
                f"(defined in `cianfhoghlaim/baml_src/education/`). All clients "
                f"route through `litellm.cianfhoghlaim.ie:4000` → "
                f"`deepseek/deepseek-chat` fallback."
            ),
            mo.ui.table(df, page_size=15),
        ])
    except Exception as e:
        err = str(e)
        mo.md(f"### Stage 3 — BAML typed records\n\n⚠️ Query failed: {e}")


@app.cell
def _(con, err, mo, subject_selector, use_md, year_selector):
    """Stage 4 — Topic validation (NCCA taxonomy pass/fail).

    Real query against the BIEP lakehouse view
    ``md:oideachais.curriculum.topic_validation``. Pass/fail is the
    95% fuzzy-match threshold against the canonical NCCA syllabus topic
    list. Failed records are flagged for human review in the Gradio UI.
    """
    import pandas as pd

    if con is None or not use_md:
        mo.md(
            "### Stage 4 — Topic validation (synthetic preview)\n\n"
            "*Run the `pdf_processing` Dagster asset to populate "
            "`oideachais.curriculum.topic_validation`.*"
        )
        return

    try:
        df = con.execute(
            f"""
            SELECT validation_status, count(*) AS n
            FROM md:oideachais.curriculum.topic_validation
            WHERE subject = '{subject_selector.value}'
              AND year = {int(year_selector.value)}
            GROUP BY validation_status
            """
        ).fetchdf()
        pass_n = int(df.loc[df["validation_status"] == "pass", "n"].sum()) if not df.empty else 0
        fail_n = int(df.loc[df["validation_status"] == "fail", "n"].sum()) if not df.empty else 0
        total = pass_n + fail_n
        rate = pass_n / max(total, 1)

        mo.vstack([
            mo.md(
                f"### Stage 4 — Topic validation\n\n"
                f"**Pass rate**: {pass_n} / {total} ({rate:.1%}) — "
                f"threshold = 95% fuzzy match against the NCCA canonical topic list.\n\n"
                f"Failed records are surfaced for human review in the Gradio UI "
                f"at `spaces/oideachais-pdf-review/`."
            ),
            mo.ui.table(df, page_size=10),
        ])
    except Exception as e:
        err = str(e)
        mo.md(f"### Stage 4 — Topic validation\n\n⚠️ Query failed: {e}")


@app.cell
def _(con, mo, subject_selector, use_md, year_selector):
    """Stage 5 — Semantic chunking (CocoIndex v1 + BAAI/bge-m3).

    Real query against the BIEP lakehouse view
    ``md:oideachais.curriculum.semantic_chunks`` (one row per BGE-M3
    chunk with `chunk_type`, `level`, `topic`, and `token_count`).
    """
    if con is None or not use_md:
        mo.md(
            "### Stage 5 — Semantic chunking (synthetic preview)\n\n"
            "Chunking strategy:\n"
            "- **Syllabus:** one chunk per `SyllabusTopic`\n"
            "- **Past paper:** one chunk per `PastExamQuestion`\n"
            "- **Marking scheme:** one chunk per `MarkingPoint`\n"
            "- **Diagrams:** one chunk per figure region (caption as text)\n\n"
            "Chunk size: 256–1024 tokens. Embedder: `BAAI/bge-m3` (1024-dim, batched 100+)."
        )
        return

    try:
        df = con.execute(
            f"""
            SELECT chunk_type, level, count(*) AS chunks, sum(token_count) AS total_tokens
            FROM md:oideachais.curriculum.semantic_chunks
            WHERE subject = '{subject_selector.value}'
              AND year = {int(year_selector.value)}
            GROUP BY chunk_type, level
            ORDER BY chunk_type, level
            """
        ).fetchdf()
        mo.vstack([
            mo.md("### Stage 5 — Semantic chunking (CocoIndex v1 + BAAI/bge-m3)"),
            mo.ui.table(df, page_size=10),
            mo.md(
                "*LanceDB table: `biep_curriculum_embeddings`. The 1024-dim BGE-M3 "
                "vectors are indexed with HNSW for sub-millisecond semantic search.*"
            ),
        ])
    except Exception as e:
        mo.md(f"### Stage 5 — Semantic chunking\n\n⚠️ Query failed: {e}")


@app.cell
def _(con, mo, subject_selector, use_md, year_selector):
    """Stage 6 — Lakehouse + Cognee + Graphiti fan-out counts.

    Real queries against:
    - ``md:oideachais.curriculum.<subject>_<year>_<paper>_documents`` (lakehouse row count)
    - ``md:oideachais.graphiti.episodes`` (Graphiti episode count)
    - Cognee KG node count (computed at cognify time, surfaced via
      ``md:oideachais.graphiti.node_count``).
    """
    if con is None or not use_md:
        mo.md(
            "### Stage 6 — Lakehouse + Cognee + Graphiti (synthetic preview)\n\n"
            "The final stage fans out to:\n"
            "- DuckLake: `oideachais.curriculum.<subject>_<year>_<paper>_documents`\n"
            "- Cognee dataset: `biep_<subject>_kg`\n"
            "- Graphiti episode: `{type, subject, year, paper, n_chunks, n_validated}`"
        )
        return

    try:
        row = con.execute(
            f"""
            SELECT
                (SELECT count(*) FROM md:oideachais.curriculum.documents
                 WHERE subject = '{subject_selector.value}'
                   AND year = {int(year_selector.value)}) AS lakehouse_rows,
                (SELECT count(*) FROM md:oideachais.graphiti.episodes
                 WHERE subject = '{subject_selector.value}'
                   AND year = {int(year_selector.value)}) AS graphiti_episodes,
                (SELECT node_count FROM md:oideachais.graphiti.node_count
                 WHERE subject = '{subject_selector.value}') AS cognee_nodes
            """
        ).fetchone()
        mo.vstack([
            mo.md(
                f"### Stage 6 — Lakehouse + Cognee + Graphiti\n\n"
                f"- **Lakehouse rows:** `{row[0]}`\n"
                f"- **Graphiti episodes:** `{row[1]}`\n"
                f"- **Cognee nodes:** `{row[2]}`"
            ),
        ])
    except Exception as e:
        mo.md(f"### Stage 6 — Lakehouse + Cognee + Graphiti\n\n⚠️ Query failed: {e}")


if __name__ == "__main__":
    app.run()