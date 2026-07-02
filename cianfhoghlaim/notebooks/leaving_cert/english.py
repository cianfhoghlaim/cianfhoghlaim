# Marimo notebook for English teacher dashboard.

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
        # English — Leaving Cert Teacher Dashboard

        The English subject uses the Clair Obscur brushstroke textures
        with the Brigid poetry-healing motif.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    skills = ["Comprehension", "Composition", "Single Text", "Comparative", "Studied Poetry"]
    weights = [25, 25, 20, 15, 15]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(weights, labels=skills, autopct="%1.1f%%", colors=["#ea580c", "#f97316", "#fb923c", "#fdba74", "#fed7aa"])
    ax.set_title("English — Skill Distribution (HL)")
    fig
    return ax, fig, skills, weights


if __name__ == "__main__":
    app.run()