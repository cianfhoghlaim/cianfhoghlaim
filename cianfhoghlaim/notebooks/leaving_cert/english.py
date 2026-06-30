"""
Leaving Certificate English — Teacher Dashboard (marimo).
"""
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # Leaving Certificate English — Teacher Dashboard

        ## What is this?

        The per-subject marimo notebook for NCCA Leaving Certificate
        English (OL + HL) + Junior Cycle English.

        Bilingual EN + GA throughout. Includes per-LO NCCA syllabus
        lookup + BGE-M3 semantic search over the quest-pack embeddings.

        ## Subject strands

        - **Comprehending** — fiction + non-fiction
        - **Composition** — 5 modes (personal essay, discursive, argumentative, narrative, descriptive)
        - **Comparative** — 2+ texts (mode: cultural context / vision / literary genre)
        - **Poetry** — prescribed (8 poets) + unseen
        - **Drama** — Shakespeare + Irish playwright
        - **Film** — HL only (since 2022)
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Design a custom English formative item

        Example LOs:
        - `LC-ENGL-LO-2.4` (Comprehending)
        - `LC-ENGL-LO-3.1` (Composition)
        - `LC-ENGL-LO-4.2` (Comparative)
        - `LC-ENGL-LO-5.1` (Poetry)
        """
    )

    lo_box = mo.ui.text(value="LC-ENGL-LO-2.4", label="NCCA LO code")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Difficulty")
    level_box = mo.ui.dropdown(options=["jc", "lc_ol", "lc_hl"], value="lc_hl", label="Level")
    topic_box = mo.ui.text(value="COMPREHENDING", label="Topic area")
    mo.vstack([lo_box, difficulty_box, level_box, topic_box])
    return difficulty_box, level_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, level_box, lo_box, mo, topic_box):
    try:
        from cianfhoghlaim.baml_client import b
        item = b.GenerateEnglFormativeItem(
            lo_code=lo_box.value,
            difficulty=difficulty_box.value,
            level=level_box.value,
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