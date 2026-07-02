# Marimo notebook for Gaeilge teacher dashboard.
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.

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
        # Gaeilge — Leaving Cert Teacher Dashboard

        An teanga is na Mná Gaoithe — the language is the women of the wind.

        The Gaeilge subject uses Insular Art (Book of Kells knotwork) +
        Uncial/Insular script + Ogham as the primary script. Ogma
        (the inventor of Ogham) is the Tuatha Dé deity.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    # Sample data — the real data comes from BAML + Dagster
    skills = ["Léamh", "Scríbhneoireacht", "Cluastuiscint", "Litríocht", "Gramadach"]
    weights = [30, 25, 20, 15, 10]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(weights, labels=skills, autopct="%1.1f%%", colors=["#059669", "#0d9488", "#0891b2", "#0284c7", "#2563eb"])
    ax.set_title("Gaeilge — Skill Distribution (HL)")
    fig
    return ax, fig, skills, weights


if __name__ == "__main__":
    app.run()