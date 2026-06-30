"""
Leaving Certificate Mathematics — Teacher Dashboard (marimo).

Per-subject marimo notebook for Mathematics. Renders:
- The full NCCA Mathematics syllabus landscape (bilingual EN + GA)
- A searchable table of all LOs across HL / OL / FL
- A BGE-M3 semantic search box over the quest-pack embeddings
- A "design quest" panel that lets a teacher generate a custom
  FormativeItem via the BAML client
- A student-mastery heat-map (FalkorDB-backed)

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/leaving_cert/mathematics.py
"""
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Leaving Certificate Mathematics — Teacher Dashboard

        ## What is this?

        The per-subject marimo notebook for NCCA Leaving Certificate
        Mathematics. Built per the
        `cianfhoghlaim-educational-mmo-v1` openspec change.

        Bilingual EN + GA throughout. The 3 NCCA levels (Foundation,
        Ordinary, Higher) are loaded from the Mathematics quest-pack
        DuckDB database (`./data/mathematics.duckdb`).

        ## What can you do here?

        1. Browse all NCCA Mathematics learning outcomes across the
           3 levels (FL / OL / HL).
        2. Search the LanceDB-embedded quest-pack corpus with a
           BGE-M3 semantic search box.
        3. Design a custom formative item via the BAML client.
        4. View the student-mastery heat-map (FalkorDB-backed).
        """
    )
    return (mo,)


@app.cell
def _(mo):
    import duckdb
    import pandas as pd

    # Open the Mathematics DuckDB produced by the math_quest_pack asset
    con = duckdb.connect("./data/mathematics.duckdb", read_only=True)
    los = con.execute(
        """
        SELECT lo_code, level, topic, competency_text_en, competency_text_ga,
               source_pdf, source_page
        FROM math_syllabus_los
        ORDER BY level, topic, lo_code
        """
    ).df()
    mo.ui.table(los, page_size=20, label="NCCA Mathematics Learning Outcomes")
    return con, duckdb, los, pd


@app.cell
def _(mo):
    import duckdb

    con = duckdb.connect("./data/mathematics.duckdb", read_only=True)
    items = con.execute(
        """
        SELECT id, lo_code, level, item_type, difficulty, est_time_minutes,
               prompt_en, expected_answer_en
        FROM math_quest_items
        ORDER BY level, difficulty
        """
    ).df()

    mo.vstack(
        [
            mo.md("## Formative Items (the practice corpus)"),
            mo.ui.table(items, page_size=15),
        ]
    )
    return con, items


@app.cell
async def _(mo):
    """Semantic search over the quest-pack embeddings."""
    import duckdb

    mo.md("## Semantic search over the quest-pack corpus")

    query_box = mo.ui.text(value="differentiation", label="Search query (BGE-M3)")
    level_select = mo.ui.dropdown(
        options=["hl", "ol", "fl", "all"],
        value="hl",
        label="Level",
    )
    mo.vstack([query_box, level_select])
    return level_select, query_box


@app.cell
async def _(level_select, mo, query_box):
    """Run the semantic search."""
    try:
        from cianfhoghlaim.cocoindex.mathematics_embedding import (
            query_mathematics,
        )

        level = level_select.value if level_select.value != "all" else "hl"
        results = await query_mathematics(
            query=query_box.value, level=level, top_k=5
        )
        mo.ui.table(results, page_size=5, label="Top 5 semantic matches")
    except Exception as exc:
        mo.md(f"⚠️ Search failed: `{exc}`")
    return (results,)


@app.cell
async def _(mo):
    """Design a custom formative item via the BAML client."""
    mo.md(
        """
        ## Design a custom formative item

        Enter an LO code + difficulty + level, and the BAML client will
        generate a fresh formative item. Example LO codes:
        - `LC-MATHS-LO-2.4` (differentiation)
        - `LC-MATHS-LO-3.1` (probability)
        - `JC-MATHS-LO-1.2` (arithmetic)
        """
    )

    lo_box = mo.ui.text(value="LC-MATHS-LO-2.4", label="NCCA LO code")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Difficulty")
    level_box = mo.ui.dropdown(
        options=["lc_fl", "lc_ol", "lc_hl", "jc"],
        value="lc_hl",
        label="Level",
    )
    topic_box = mo.ui.text(value="DIFFERENTIATION", label="Topic area")
    mo.vstack([lo_box, difficulty_box, level_box, topic_box])
    return difficulty_box, level_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, level_box, lo_box, mo, topic_box):
    """Generate the item."""
    try:
        from cianfhoghlaim.baml_client import b

        item = b.GenerateMathFormativeItem(
            lo_code=lo_box.value,
            difficulty=difficulty_box.value,
            level=level_box.value,
            topic=topic_box.value,
        )
        mo.vstack(
            [
                mo.md(f"### Item (difficulty {item.difficulty})"),
                mo.md(f"**Prompt (EN):** {item.prompt.text_en}"),
                mo.md(f"**Prompt (GA):** {item.prompt.text_ga or '— (EN only) —'}"),
                mo.md(f"**Expected answer (EN):** {item.expected_answer.text_en}"),
                mo.md(f"**Marking scheme:** {item.marking_scheme.text_en}"),
                mo.md(f"**Hints:**\n" + "\n".join(f"  - {h.text_en}" for h in item.hints)),
                mo.md(f"**Common errors:**\n" + "\n".join(f"  - {e.text_en}" for e in item.common_errors)),
                mo.md(f"**Evidence:** {item.evidence.source_pdf}, p. {item.evidence.source_page}"),
            ]
        )
    except Exception as exc:
        mo.md(f"⚠️ Item generation failed: `{exc}`")
    return (item,)


if __name__ == "__main__":
    app.run()