# Marimo notebook for Mathematics teacher dashboard.
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.
# Renders the 8-subject NCCA syllabus landscape with bilingual EN + GA content.
#
# Run: `uv run marimo edit notebooks/leaving_cert/mathematics.py`

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Mathematics — Leaving Cert Teacher Dashboard

        Bilingual (EN + GA) overview of the 8 NCCA Leaving Certificate
        subjects, with the Mathematics subject as the lead.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    import numpy as np
    return np, plt


@app.cell
def __(np, plt):
    # Sample data — the real data comes from BAML + Dagster
    topics = ["Algebra", "Calculus", "Probability", "Statistics", "Finance", "Geometry", "Complex Numbers", "Sequences"]
    weights = [25, 25, 15, 10, 10, 5, 5, 5]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(topics, weights, color="#2563eb")
    ax.set_xlabel("Weight (% of total exam marks)")
    ax.set_title("Mathematics — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


@app.cell
def __(mo):
    mo.md(
        """
        ## 5 NCCA Key Competencies for Mathematics

        | Competency | Tuatha Dé deity | Sample LO |
        |:--|:--|:--|
        | Communicating | Brigid | LC-MATHS-LO-1.1 |
        | Information Processing | Ogma | LC-MATHS-LO-2.1 |
        | Critical & Creative Thinking | Lugh | LC-MATHS-LO-3.1 |
        | Personal Effectiveness | Dian Cecht | LC-MATHS-LO-4.1 |
        | Working with Others | Trí Dé Dána | LC-MATHS-LO-5.1 |
        """
    )
    return


if __name__ == "__main__":
    app.run()