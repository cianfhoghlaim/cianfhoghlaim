# Marimo notebook for Applied Mathematics teacher dashboard.

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
        # Applied Mathematics — Leaving Cert Teacher Dashboard

        The Applied Mathematics subject uses the Clair Obscur Belle Époque
        material library + the BitCraft Recipe Tree (the algorithm-design-pattern
        visualisation). The 4 modules (Mechanics + Statistics) are arranged
        hierarchically.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    topics = ["Mechanics", "Statistics", "Probability", "Numerical Methods"]
    weights = [40, 25, 20, 15]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(weights, labels=topics, autopct="%1.1f%%", colors=["#7c3aed", "#a855f7", "#c084fc", "#d8b4fe"])
    ax.set_title("Applied Mathematics — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


if __name__ == "__main__":
    app.run()