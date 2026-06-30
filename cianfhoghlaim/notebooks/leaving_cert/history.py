"""
Leaving Certificate History — Teacher Dashboard (marimo).
"""
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # Leaving Certificate History — Teacher Dashboard

        ## What is this?

        The per-subject marimo notebook for NCCA Leaving Certificate
        History (OL + HL) + Junior Cycle History.

        Bilingual EN + GA throughout. Includes per-LO NCCA syllabus
        lookup + BGE-M3 semantic search over the quest-pack embeddings.

        ## Subject strands

        - **Early Modern Ireland** (1500-1800)
        - **Modern Ireland** (1800-present)
        - **European History**
        - **World History**
        - **Research Study**
        - **Document Study** (HL)
        """
    )
    return (mo,)


@app.cell
def _(mo):
    lo_box = mo.ui.text(value="LC-HIST-LO-2.4", label="NCCA LO code")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Difficulty")
    level_box = mo.ui.dropdown(options=["jc", "lc_ol", "lc_hl"], value="lc_hl", label="Level")
    topic_box = mo.ui.text(value="EARLY_MODERN_IRELAND_1500_1800", label="Topic area")
    mo.vstack([lo_box, difficulty_box, level_box, topic_box])
    return difficulty_box, level_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, level_box, lo_box, mo, topic_box):
    try:
        from cianfhoghlaim.baml_client import b
        item = b.GenerateHistFormativeItem(
            lo_code=lo_box.value,
            difficulty=difficulty_box.value,
            level=level_box.value,
            topic=topic_box.value,
        )
        mo.vstack(
            [
                mo.md(f"### Item (difficulty {item.difficulty})"),
                mo.md(f"**Prompt (EN):** {item.prompt.text_en}"),
                mo.md(f"**Marking scheme:** {item.marking_scheme.text_en}"),
                mo.md(f"**Hints:**\n" + "\n".join(f"  - {h.text_en}" for h in item.hints)),
            ]
        )
    except Exception as exc:
        mo.md(f"⚠️ Item generation failed: `{exc}`")
    return (item,)


if __name__ == "__main__":
    app.run()