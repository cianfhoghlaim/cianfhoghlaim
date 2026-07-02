# Marimo notebook for History teacher dashboard.

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
        # History — Leaving Cert Teacher Dashboard

        The History subject uses the WoW raid-frames grid layout for the
        historical figures. The Morrígan's war-mask is the primary icon.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    topics = ["Early Modern Ireland (1494-1803)", "Modern Ireland (1801-1993)", "European Renaissance", "Industrial Revolution", "20th Century Europe"]
    weights = [25, 25, 15, 15, 20]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(topics, weights, color="#b91c1c")
    ax.set_xlabel("Weight (% of total exam marks)")
    ax.set_title("History — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


if __name__ == "__main__":
    app.run()