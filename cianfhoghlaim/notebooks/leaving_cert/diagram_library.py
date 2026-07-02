# Marimo notebook for the 4-mode diagram library (teacher view).
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.
# Renders the 4 diagram modes × 8 subjects × EN/GA = 64 SVG catalog
# (pre-rendered by the daily_diagram_pre_render Dagster asset).

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
        # Diagram Library — Teacher View

        The 4 diagram modes × 8 NCCA subjects × EN/GA = 64 SVG catalog.
        Each diagram is pre-rendered daily by the
        `daily_diagram_pre_render` Dagster asset and stored at
        `s3://cianfhoghlaim-diagram-cache/{mode}/{subject}/{lang}.svg`.

        Select a mode below to explore.
        """
    )
    return


@app.cell
def __(mo):
    tabs = mo.ui.tabs(
        {
            "Concept-map": mo.md(
                """
                ## Concept-map diagrams

                The concept-map renders the 5 NCCA Key Competencies as root
                nodes + per-subject LOs as children. Bilingual EN + GA.
                """
            ),
            "Topic-heatmap": mo.md(
                """
                ## Topic-frequency heatmaps

                The topic-heatmap renders question × paper × topic × year
                as a 2.5D matrix (per Theme 9 — the visual RAG).
                """
            ),
            "PCLM Flow": mo.md(
                """
                ## PCLM marking flows

                The PCLM flow renders the Partial Credit, Logical Marking
                flowchart per marking scheme (per Theme 10 — the
                sovereign-mmo-state-stack).
                """
            ),
            "Question Sankey": mo.md(
                """
                ## Question → Topic → Difficulty → Year Sankey

                The Sankey renders the question → topic → difficulty → year
                flows for the per-subject past papers (2017-2025).
                """
            ),
        }
    )
    tabs
    return (tabs,)


@app.cell
def __(tabs):
    # The catalog grid (subject × mode × lang) — placeholder
    import matplotlib.pyplot as plt

    subjects = ["mathematics", "applied_mathematics", "chemistry", "geography", "history", "english", "gaeilge", "computer_science"]
    fig, ax = plt.subplots(figsize=(12, 6))
    for i, subject in enumerate(subjects):
        ax.barh(i, 4, color="#059669")  # 4 diagrams per subject
        ax.text(0.1, i, subject, color="white", va="center")
    ax.set_yticks(range(len(subjects)))
    ax.set_yticklabels([])
    ax.set_xlabel("Diagrams per subject")
    ax.set_title(f"{tabs.value} catalog (8 subjects × EN + GA = 16 SVGs)")
    fig
    return ax, fig, subjects, plt


if __name__ == "__main__":
    app.run()