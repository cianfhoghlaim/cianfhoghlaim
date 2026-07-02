# Marimo notebook for Computer Science teacher dashboard.

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
        # Computer Science — Leaving Cert Teacher Dashboard

        The Computer Science subject uses the BitCraft Recipe Tree +
        Clair Obscur skill tree. The 4 NCCA CS topics (Algorithms + Data
        + Systems + Networks) are arranged as the 4 branches.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    topics = ["Algorithms", "Data Structures", "Computer Systems", "Networks"]
    weights = [30, 30, 20, 20]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(topics, weights, color="#475569")
    ax.set_xlabel("Weight (% of total exam marks)")
    ax.set_title("Computer Science — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


if __name__ == "__main__":
    app.run()