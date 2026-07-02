# Marimo notebook for Chemistry teacher dashboard.

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
        # Chemistry — Leaving Cert Teacher Dashboard

        The Chemistry subject uses the Hades shadow-first palette
        (deep black + acid green for reactions + bronze for transition
        metals) with the Dian Cecht physician motif.
        """
    )
    return


@app.cell
def __():
    import matplotlib.pyplot as plt
    return (plt,)


@app.cell
def __(plt):
    topics = ["Atomic Structure", "Bonding", "Stoichiometry", "Organic", "Rates", "Equilibrium"]
    weights = [15, 15, 20, 25, 15, 10]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(topics, weights, color="#16a34a")
    ax.set_ylabel("Weight (% of total exam marks)")
    ax.set_title("Chemistry — Topic Distribution (HL)")
    fig
    return ax, fig, topics, weights


if __name__ == "__main__":
    app.run()