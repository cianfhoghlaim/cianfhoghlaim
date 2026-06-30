"""
Leaving Certificate Gaeilge — Teacher Dashboard (marimo).

Per-subject marimo notebook for NCCA Leaving Certificate + Junior
Cycle Gaeilge (Irish-medium). All content is canonical in Irish.
"""
import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    mo.md(
        """
        # Leaving Certificate Gaeilge — Teacher Dashboard

        ## Cad é seo? (What is this?)

        An nótaíleabhar marimo don ábhar Gaeilge (NCCA). Gaeilge á
        múineadh trí Ghaeilge — is í an Ghaeilge an teanga chaighdeánach.

        ## Gaeilge is taught in Irish

        Bilingual EN+GA throughout. text_ga is canonical (required);
        text_en is optional helper translation.

        3 NCCA levels (FL / OL / HL) plus Junior Cycle.
        """
    )
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Design a custom Gaeilge formative item

        Cuir isteach cód LO + deacracht + topaic. Samplaí:
        - `LC-GAEL-LO-3.1` (Léamhthuiscint)
        - `LC-GAEL-LO-4.2` (Gramadach: aimsir chaite)
        - `LC-GAEL-LO-5.1` (Filíocht: Aogán Ó Rathaille)
        """
    )

    lo_box = mo.ui.text(value="LC-GAEL-LO-3.1", label="Cód LO")
    difficulty_box = mo.ui.slider(start=1, stop=5, value=3, label="Deacracht")
    level_box = mo.ui.dropdown(options=["jc", "lc_fl", "lc_ol", "lc_hl"], value="lc_hl", label="Leibhéal")
    topic_box = mo.ui.text(value="LEAMHTHUISCINT", label="Topaic")
    mo.vstack([lo_box, difficulty_box, level_box, topic_box])
    return difficulty_box, level_box, lo_box, topic_box


@app.cell
async def _(difficulty_box, level_box, lo_box, mo, topic_box):
    try:
        from cianfhoghlaim.baml_client import b
        item = b.GenerateGaelFormativeItem(
            lo_code=lo_box.value,
            difficulty=difficulty_box.value,
            level=level_box.value,
            topic=topic_box.value,
        )
        mo.vstack(
            [
                mo.md(f"### Mír (deacracht {item.difficulty})"),
                mo.md(f"**Ceist (GA):** {item.prompt.text_ga}"),
                mo.md(f"**Freagra (GA):** {item.expected_answer.text_ga}"),
                mo.md(f"**Scéim mharcála:** {item.marking_scheme.text_ga}"),
                mo.md(f"**Leideanna:**\n" + "\n".join(f"  - {h.text_ga}" for h in item.hints)),
                mo.md(f"**Fianaise:** {item.evidence.source_pdf}, lch. {item.evidence.source_page}"),
            ]
        )
    except Exception as exc:
        mo.md(f"⚠️ Theip ar ghiniúint: `{exc}`")
    return (item,)


if __name__ == "__main__":
    app.run()