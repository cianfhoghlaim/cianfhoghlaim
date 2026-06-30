"""
Leaving Certificate Computer Science — Teacher Dashboard (marimo).
"""
import marimo
__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # Leaving Certificate Computer Science — Teacher Dashboard

        ## What is this?

        The per-subject marimo notebook for NCCA Leaving Certificate
        Computer Science (OL + HL) + Junior Cycle Coding short course.

        ## Subject strands

        - **Algorithms** (sorting, searching, complexity)
        - **Data Structures** (arrays, lists, stacks, queues, trees, graphs)
        - **Programming** (Python; variables, control flow, functions, OOP)
        - **Computational Thinking** (decomposition, pattern recognition, abstraction)
        - **Computer Systems** + **Networks** + **Databases**
        - **Web Development** + **Data Representation**
        - **Ethics** (privacy, AI ethics, IP)
        """
    )
    return (mo,)


@app.cell
def _(mo):
    lo_box = mo.ui.text(value="LC-COMP-LO-2.4", label="NCCA LO code")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Difficulty")
    level_box = mo.ui.dropdown(options=["jc_coding_short_course", "lc_ol", "lc_hl"], value="lc_hl", label="Level")
    topic_box = mo.ui.text(value="ALGORITHMS", label="Topic area")
    mo.vstack([lo_box, difficulty_box, level_box, topic_box])
    return difficulty_box, level_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, level_box, lo_box, mo, topic_box):
    try:
        from cianfhoghlaim.baml_client import b
        item = b.GenerateCompFormativeItem(lo_code=lo_box.value, difficulty=difficulty_box.value, level=level_box.value, topic=topic_box.value)
        mo.vstack([
            mo.md(f"### Item (difficulty {item.difficulty})"),
            mo.md(f"**Prompt (EN):** {item.prompt.text_en}"),
            mo.md(f"**Marking scheme:** {item.marking_scheme.text_en}"),
        ])
    except Exception as exc:
        mo.md(f"⚠️ Item generation failed: `{exc}`")
    return (item,)


if __name__ == "__main__":
    app.run()