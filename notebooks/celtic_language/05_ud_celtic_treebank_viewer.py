# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
# ]
# ///
"""05 — UD Celtic treebank viewer (13 treebanks CoNLL-U browser).

Added 2026-07-17. Sentence-level + token-level browse UI for the 13
UD Celtic treebanks. 5-panel layout.

Dual-mode usage:
    marimo edit 05_ud_celtic_treebank_viewer.py
    uv run 16_celtic_language/05_ud_celtic_treebank_viewer.py --treebank UD_Irish-IDT
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import os
    import sys
    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")
    import duckdb
    import pandas as pd
    import altair as alt
    return alt, duckdb, mo, os, pd, sys


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # UD Celtic Treebank Viewer
        ## *CoNLL-U Browser for the 13 Celtic Treebanks*

        **Source data**: `oideachais.celtic.ud_celtic.sentences`
        + `.tokens` + `oideachais.language.ud_celtic_chunks` (LanceDB).

        LlamaSwap routing:
        - Irish treebanks → `uccix-mistral-24b`
        - Other Celtic → `gemma-4-26B-A4B`
        """
    )
    return


@app.cell
def _connect(duckdb, os):
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            duckdb.sql(f"SET motherduck_token='{token}'")
        con = duckdb.connect("md:oideachais", read_only=True)
    else:
        con = duckdb.connect(os.environ.get("DUCKDB_PATH", "/tmp/oideachais.duckdb"), read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_treebank(alt, con, mo, pd):
    mo.md("## 1. Per-treebank sentence + token counts")
    rows = con.execute(
        """
        SELECT treebank, language, variety,
               COUNT(*) AS n_sentences,
               SUM(tokens_count) AS n_tokens
        FROM oideachais.celtic.ud_celtic.sentences
        GROUP BY treebank, language, variety
        ORDER BY n_sentences DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["treebank", "language", "variety", "n_sentences", "n_tokens"])
    chart = alt.Chart(df).mark_bar().encode(x="n_sentences:Q", y=alt.Y("treebank:N", sort="-x"), color="language:N")
    return (chart, df)


@app.cell
def _panel_2_language(alt, con, mo, pd):
    mo.md("## 2. Per-language coverage")
    rows = con.execute(
        """
        SELECT language, COUNT(DISTINCT treebank) AS n_treebanks, COUNT(*) AS n_sentences
        FROM oideachais.celtic.ud_celtic.sentences
        GROUP BY language
        ORDER BY n_sentences DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["language", "n_treebanks", "n_sentences"])
    chart = alt.Chart(df).mark_bar().encode(x="language:N", y="n_sentences:Q", color="language:N")
    return (chart, df)


@app.cell
def _panel_3_top_lemmas(alt, con, mo, pd):
    mo.md("## 3. Top 20 lemmas across all treebanks")
    rows = con.execute(
        """
        SELECT lemma, COUNT(*) AS n_occurrences
        FROM oideachais.celtic.ud_celtic.tokens
        WHERE lemma IS NOT NULL
        GROUP BY lemma
        ORDER BY n_occurrences DESC
        LIMIT 20
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["lemma", "n_occurrences"])
    chart = alt.Chart(df).mark_bar().encode(x="n_occurrences:Q", y=alt.Y("lemma:N", sort="-x"))
    return (chart, df)


@app.cell
def _panel_4_pos(alt, con, mo, pd):
    mo.md("## 4. POS tag distribution")
    rows = con.execute(
        """
        SELECT upos, COUNT(*) AS n_tokens
        FROM oideachais.celtic.ud_celtic.tokens
        WHERE upos IS NOT NULL
        GROUP BY upos
        ORDER BY n_tokens DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["upos", "n_tokens"])
    chart = alt.Chart(df).mark_arc().encode(theta="n_tokens:Q", color="upos:N")
    return (chart, df)


@app.cell
def _panel_5_samples(alt, con, mo, pd):
    mo.md("## 5. Sample sentences (UD_Irish-IDT)")
    rows = con.execute(
        """
        SELECT sent_id, text, tokens_count
        FROM oideachais.celtic.ud_celtic.sentences
        WHERE treebank = 'UD_Irish-IDT'
        LIMIT 20
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["sent_id", "text", "tokens_count"])
    return (df,)


if __name__ == "__main__":
    app.run()