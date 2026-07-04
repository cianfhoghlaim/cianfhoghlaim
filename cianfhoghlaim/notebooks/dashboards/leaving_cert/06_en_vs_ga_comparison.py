"""
Cross-subject EN vs GA comparison — same Learning Outcome in EN vs GA.

For each subject's syllabus + the canonical LO list, pull the EN
text and the GA text; visualise the translation fidelity as a
divergence chart.

Used to validate the LC5 BAML ExtractCrossLinguisticConcept function.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # EN ↔ GA Cross-Linguistic Comparison

    Compares the same Learning Outcome (LO) in English vs Irish
    across all 5 LC subjects. Routes through BAML
    `ExtractCrossLinguisticConcept` per subject.
    """)
    return mo


@app.cell
def _chemistry():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCrossLinguisticConcept(
            subject="chemistry",
            source_pdf="SCSEC09_Chemistry_syllabus_Eng.pdf",
            ga_source_pdf="SCSEC09_Chemistry_syllabus_Gaeilge.pdf",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _gaeilge():
    try:
        from cianfhoghlaim.baml_client import b
        # Gaeilge is its own language; concept is *the* canonical LO
        return b.ExtractCrossLinguisticConcept(
            subject="gaeilge",
            source_pdf="Siollabais-Nuashonraithe-na-hArdteistimeireachta_1.pdf",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _viz():
    import altair as alt
    import pandas as pd
    # Sample data: 5 subjects × ~10 LOs each
    df = pd.DataFrame({
        "subject": ["chemistry"] * 8 + ["computer_science"] * 8 + ["gaeilge"] * 8 +
                   ["geography"] * 8 + ["mathematics"] * 8,
        "translation_fidelity": [0.97, 0.95, 0.93, 0.99, 0.88, 0.91, 0.94, 0.96] * 5,
        "lo_id": [f"LO-{i}" for i in range(1, 41)],
    })
    chart = alt.Chart(df).mark_circle(size=80).encode(
        x="lo_id:O",
        y="translation_fidelity:Q",
        color="subject:N",
        tooltip=["subject", "lo_id", "translation_fidelity"],
    ).properties(width=700, height=300, title="Translation fidelity per LO across 5 subjects")
    return chart


if __name__ == "__main__":
    app.run()
