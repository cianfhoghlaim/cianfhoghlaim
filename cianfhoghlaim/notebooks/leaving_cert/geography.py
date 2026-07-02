# Marimo notebook for Geography teacher dashboard.

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
        # Geography — Leaving Cert Teacher Dashboard

        An Tíreolaíocht — the Geography subject uses the WoW map zones
        layout (hex-based claims with decay indicators). The 6 British Isles
        subnations are the 6 zones. The 4 Irish provinces are the home base.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    topics = ["Core 1: Physical Geography", "Core 2: Regional Geography", "Elective 1", "Elective 2", "Elective 3", "Elective 4"]
    weights = [20, 20, 15, 15, 15, 15]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(topics, weights, color="#ca8a04")
    ax.set_xlabel("Weight (% of total exam marks)")
    ax.set_title("Geography — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


if __name__ == "__main__":
    app.run()