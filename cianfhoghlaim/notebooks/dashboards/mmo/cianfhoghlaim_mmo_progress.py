#!/usr/bin/env python3
"""The Cianfhoghlaim Educational MMO end-to-end demo.

Per R7.9: the MMO end-to-end demo (mathematics, applied_math, chemistry,
geography, history, english, gaeilge, computer_science — 8 NCCA subjects).
"""
import marimo

__generated_with_marimo = True
app = marimo.App(width="full")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    """Show the 8 NCCA subject agent dashboards (the MMO realm)."""
    subjects = [
        "mathematics", "applied_mathematics", "chemistry",
        "geography", "history", "english", "gaeilge", "computer_science",
    ]
    return subjects,


if __name__ == "__main__":
    app.run()
