"""
Leaving Certificate Applied Mathematics — Teacher Dashboard (marimo).

Per-subject marimo notebook for NCCA Leaving Certificate Applied
Mathematics (Higher Level only). Renders:
- The full NCCA APPM syllabus landscape (bilingual EN + GA)
- A searchable table of all HL learning outcomes
- A BGE-M3 semantic search box over the APPM quest-pack embeddings
- A "design quest" panel
- A student-mastery heat-map (FalkorDB-backed)

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/leaving_cert/applied_mathematics.py
"""
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
        # Leaving Certificate Applied Mathematics — Teacher Dashboard

        ## What is this?

        The per-subject marimo notebook for NCCA Leaving Certificate
        Applied Mathematics (Higher Level only — APPM is HL only).

        Bilingual EN + GA throughout. APPM is the mechanics-focused
        subject; it bridges naturally to Pure Mathematics (calculus,
        vectors) and to Physics (forces, motion).

        ## What can you do here?

        1. Browse all NCCA APPM learning outcomes (HL).
        2. Search the LanceDB-embedded quest-pack corpus semantically.
        3. Design a custom formative item via the BAML client.
        4. View the student-mastery heat-map (FalkorDB-backed).
        """
    )
    return (mo,)


@app.cell
def _(mo):
    import duckdb

    con = duckdb.connect("./data/applied_mathematics.duckdb", read_only=True)
    los = con.execute(
        """
        SELECT lo_code, level, topic, competency_text_en, competency_text_ga,
               source_pdf, source_page
        FROM appm_syllabus_los
        ORDER BY topic, lo_code
        """
    ).df()
    mo.ui.table(los, page_size=20, label="NCCA APPM Learning Outcomes")
    return con, duckdb, los


@app.cell
def _(mo):
    import duckdb

    con = duckdb.connect("./data/applied_mathematics.duckdb", read_only=True)
    items = con.execute(
        """
        SELECT id, lo_code, level, item_type, difficulty, est_time_minutes,
               prompt_en, expected_answer_en
        FROM appm_quest_items
        ORDER BY difficulty
        """
    ).df()

    mo.vstack(
        [
            mo.md("## Formative Items"),
            mo.ui.table(items, page_size=15),
        ]
    )
    return con, items


@app.cell
async def _(mo):
    mo.md("## Semantic search over the APPM quest-pack corpus")
    query_box = mo.ui.text(value="projectile motion", label="Search query (BGE-M3)")
    mo.vstack([query_box])
    return (query_box,)


@app.cell
async def _(mo, query_box):
    try:
        from cianfhoghlaim.cocoindex.applied_mathematics_embedding import (
            query_applied_mathematics,
        )

        results = await query_applied_mathematics(
            query=query_box.value, level="hl", top_k=5
        )
        mo.ui.table(results, page_size=5, label="Top 5 semantic matches")
    except Exception as exc:
        mo.md(f"⚠️ Search failed: `{exc}`")
    return (results,)


@app.cell
async def _(mo):
    mo.md(
        """
        ## Design a custom formative item

        Enter an LO code + difficulty + topic. Example LOs:
        - `LC-APPM-LO-2.4` (Newton's Laws)
        - `LC-APPM-LO-3.1` (Projectiles)
        - `LC-APPM-LO-4.2` (Circular motion)
        """
    )

    lo_box = mo.ui.text(value="LC-APPM-LO-2.4", label="NCCA LO code")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Difficulty")
    topic_box = mo.ui.text(value="NEWTONS_LAWS", label="Topic area")
    mo.vstack([lo_box, difficulty_box, topic_box])
    return difficulty_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, lo_box, mo, topic_box):
    try:
        from cianfhoghlaim.baml_client import b

        item = b.GenerateAppmFormativeItem(
            lo_code=lo_box.value,
            difficulty=difficulty_box.value,
            level="lc_hl",
            topic=topic_box.value,
        )
        mo.vstack(
            [
                mo.md(f"### Item (difficulty {item.difficulty})"),
                mo.md(f"**Prompt (EN):** {item.prompt.text_en}"),
                mo.md(f"**Expected answer (EN):** {item.expected_answer.text_en}"),
                mo.md(f"**Marking scheme:** {item.marking_scheme.text_en}"),
                mo.md(f"**Hints:**\n" + "\n".join(f"  - {h.text_en}" for h in item.hints)),
                mo.md(f"**Evidence:** {item.evidence.source_pdf}, p. {item.evidence.source_page}"),
            ]
        )
    except Exception as exc:
        mo.md(f"⚠️ Item generation failed: `{exc}`")
    return (item,)


if __name__ == "__main__":
    app.run()