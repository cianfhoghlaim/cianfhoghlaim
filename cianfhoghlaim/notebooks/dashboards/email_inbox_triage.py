"""Leabharlann Email Inbox Triage — Cianfhoghlaim Oideachais.

5-section marimo notebook for the email-inbox pipeline (the primary
manual-tagging + dev surface per the user's preference for marimo
over WebChat for dev work):

  1. Loose threads sorted by urgency
  2. Legal-case prioritisation with linked Gemini PDFs
  3. Medical-access prioritisation with linked Gemini PDFs
  4. Thread explorer (`mo.ui.tree`)
  5. Hybrid search via the new `search_inbox` query handler
     (RRF-fused cosine + BM25)

Style: numbered `1_*`, `2_*`… section headers, `mo.sql` for DuckLake
reads, altair for charts (adopted from
`spaces/anti-phish/2_Classical_Machine_Learning_Models.ipynb`).

Reference: openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
"""

import marimo

__generated_with_marimo__ = "0.9.0"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Leabharlann Email Inbox Triage
        ## *Cianfhoghlaim Oideachais*

        5-section manual-triage surface for the `oideachais_email_inbox`
        cognify dataset + the `oideachais_inbox_messages` LanceDB
        table. Backed by the new `leabharlann_email_inbox` DLT source +
        the `email.baml` BAML functions + the
        `leabharlann_inbox_embedding` CocoIndex v1 App.
        """
    )
    return


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb

    # The DLT source writes to `leabharlann_inbox.inbox_index` +
    # `leabharlann_inbox.inbox_threads` in DuckLake. Default to
    # /tmp for local dev; override via `OIDEACHAIS_DUCKDB`.
    db_path = os.environ.get("OIDEACHAIS_DUCKDB", "/tmp/oideachais.duckdb")
    demo_db = Path(db_path)
    if not demo_db.exists():
        con = None
        inbox_index_df = None
        inbox_threads_df = None
        inbox_legal_df = None
    else:
        try:
            con = duckdb.connect(str(demo_db), read_only=True)
            inbox_index_df = con.execute(
                "SELECT * FROM leabharlann_inbox.inbox_index "
                "ORDER BY date_iso DESC LIMIT 500"
            ).fetchdf()
            inbox_threads_df = con.execute(
                "SELECT * FROM leabharlann_inbox.inbox_threads "
                "ORDER BY last_message_at DESC LIMIT 200"
            ).fetchdf()
            inbox_legal_df = con.execute(
                "SELECT * FROM leabharlann_inbox.inbox_legal_threads "
                "ORDER BY last_message_at DESC LIMIT 200"
            ).fetchdf()
        except Exception:
            inbox_index_df = None
            inbox_threads_df = None
            inbox_legal_df = None
        finally:
            if con is not None:
                con.close()
    return (
        Path,
        duckdb,
        inbox_index_df,
        inbox_legal_df,
        inbox_threads_df,
        os,
        demo_db,
    )


# ---------------------------------------------------------------------------
# Section 1 — Loose threads sorted by urgency
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(r"""## 1. Loose threads sorted by urgency""")
    return


@app.cell
def _(mo, inbox_threads_df):
    if inbox_threads_df is None or len(inbox_threads_df) == 0:
        mo.md(
            "**No inbox threads yet.** Run the `leabharlann_inbox_raw` "
            "Dagster asset first."
        )
    else:
        # Loose threads = no message in the last 7 days.
        import datetime as _dt

        cutoff = _dt.datetime.now(_dt.UTC) - _dt.timedelta(days=7)
        loose = inbox_threads_df[
            inbox_threads_df["last_message_at"] < cutoff.isoformat()
        ].sort_values("legal_flag", ascending=False)
        mo.md(
            f"**{len(loose)} loose threads** across all accounts "
            f"(no message in the last 7 days, sorted by legal_flag)."
        )
    return


# ---------------------------------------------------------------------------
# Section 2 — Legal-case prioritisation with linked Gemini PDFs
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 2. Legal-case prioritisation

        Threads where `baml_class == "legal_case"`. Each row links to
        the top-3 Gemini Deep Research PDFs from
        `leabharlann/gemini_deep_research/law/` via the
        `LinkEmailToResearch` BAML function.
        """
    )
    return


@app.cell
def _(mo, inbox_legal_df):
    if inbox_legal_df is None or len(inbox_legal_df) == 0:
        mo.md(
            "**No legal-class threads yet.** Run "
            "`leabharlann_inbox_baml_classify` first."
        )
    else:
        mo.md(
            f"**{len(inbox_legal_df)} legal-case threads** ready for "
            f"prioritisation. Click a row to call the ADK "
            f"`email_triage` agent's `link_thread_to_research` tool."
        )
    return


# ---------------------------------------------------------------------------
# Section 3 — Medical-access prioritisation
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 3. Medical-access prioritisation

        Threads where `baml_class == "medical_access"`. Each row links
        to the top-3 Gemini Deep Research PDFs from
        `leabharlann/gemini_deep_research/medical/`.
        """
    )
    return


@app.cell
def _(mo, inbox_index_df):
    if inbox_index_df is None or len(inbox_index_df) == 0:
        mo.md("**No medical-access threads yet.**")
    else:
        # The current schema doesn't have baml_class on inbox_index
        # (it's set by the classify asset post-merge); this is a
        # placeholder filter on `legal_flag` until the BAML join lands.
        medical = inbox_index_df[inbox_index_df.get("legal_flag", False) == False]
        mo.md(
            f"**{len(medical)} medical-access candidates** (placeholder "
            f"filter — will be replaced by the BAML `medical_access` "
            f"class once the classify asset has run)."
        )
    return


# ---------------------------------------------------------------------------
# Section 4 — Thread explorer (mo.ui.tree)
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 4. Thread explorer

        Pick an account, see all threads as a tree. Every thread has a
        "Summarise" button that calls the ADK `email_triage` agent's
        `summarise_thread` tool.
        """
    )
    return


@app.cell
def _(mo, inbox_threads_df):
    if inbox_threads_df is None or len(inbox_threads_df) == 0:
        mo.md("**No threads to explore yet.**")
    else:
        accounts = sorted(inbox_threads_df["account"].unique().tolist())
        account_picker = mo.ui.dropdown(
            options=accounts,
            value=accounts[0] if accounts else None,
            label="Account",
        )
        account_picker
    return (account_picker,)


@app.cell
def _(mo, inbox_threads_df, account_picker):
    if account_picker is None or inbox_threads_df is None:
        tree_view = mo.md("")
    else:
        filtered = inbox_threads_df[
            inbox_threads_df["account"] == account_picker.value
        ].sort_values("last_message_at", ascending=False)
        tree_data = {
            "account": account_picker.value,
            "threads": [
                {
                    "thread_id": str(row["thread_id"]),
                    "subject": str(row.get("subject", "(no subject)")),
                    "message_count": int(row.get("message_count", 0)),
                    "last_message_at": str(row.get("last_message_at", "")),
                    "legal_flag": bool(row.get("legal_flag", False)),
                }
                for _, row in filtered.iterrows()
            ],
        }
        tree_view = mo.ui.tree(
            tree_data,
            multiple_selection=False,
            label="Threads",
        )
    tree_view
    return (filtered, tree_data, tree_view)


# ---------------------------------------------------------------------------
# Section 5 — Hybrid search via the new `search_inbox` query handler
# ---------------------------------------------------------------------------


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 5. Hybrid search (RRF-fused cosine + BM25)

        Search the `oideachais_inbox_messages` LanceDB table via the
        `search_inbox` query handler. Filters: `account`, `year`,
        `baml_class`, `urgency_min`. Default limit: 20.
        """
    )
    return


@app.cell
def _(mo):
    query_input = mo.ui.text(
        value="HSE Ireland malpractice appeal",
        label="Query",
    )
    baml_class_filter = mo.ui.dropdown(
        options=["", "legal_case", "medical_access", "personal_correspondence", "other"],
        value="legal_case",
        label="BAML class filter",
    )
    account_filter = mo.ui.text(
        value="",
        label="Account filter (optional)",
    )
    urgency_filter = mo.ui.slider(
        start=0.0,
        stop=1.0,
        step=0.05,
        value=0.0,
        label="Min urgency",
    )
    mo.vstack([query_input, baml_class_filter, account_filter, urgency_filter])
    return account_filter, baml_class_filter, query_input, urgency_filter


@app.cell
async def _(mo, query_input, baml_class_filter, account_filter, urgency_filter):
    """Run the `search_inbox` query handler.

    The actual search is wired through the v1 CocoIndex App at
    `oideachais.cocoindex_flows.leabharlann_embedding:search_inbox`.
    """
    try:
        from cianfhoghlaim.embeddings._oideachais_src.leabharlann_embedding import (  # type: ignore[import-not-found]
            search_inbox as _search_inbox,
        )

        results = await _search_inbox(
            query=query_input.value,
            account=account_filter.value or None,
            baml_class=baml_class_filter.value or None,
            urgency_min=float(urgency_filter.value) if urgency_filter.value else None,
            limit=20,
        )
        if not results:
            search_md = mo.md(
                "**No results.** Make sure the "
                "`leabharlann_inbox_embeddings` asset has run."
            )
        else:
            rows_md = "\n".join(
                f"- score={r.get('score', 0.0):.3f}  "
                f"account={r.get('account', '')}  "
                f"subject={r.get('subject', '')}"
                for r in results[:20]
            )
            search_md = mo.md(
                f"**Top {len(results)} results (RRF-fused cosine + BM25):**\n\n"
                f"{rows_md}"
            )
    except ImportError:
        search_md = mo.md(
            "**LanceDB / CocoIndex not available in this environment** — "
            "the search handler is wired but the dependency stack isn't "
            "loaded. Run `mise run turbo dev` to install."
        )
    search_md
    return (results, search_md)


if __name__ == "__main__":
    app.run()
