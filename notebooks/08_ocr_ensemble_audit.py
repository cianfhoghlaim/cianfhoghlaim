# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
#   "Pillow>=10",
#   "httpx>=0.27",
# ]
#
# [tool.uv]
# package = "biep-v2-ocr-ensemble-audit"
# ///

"""OCR Ensemble Audit — full provenance trail for any BAML-extracted record.

Per the 2026-07-23-biep-v2-marimo-portal-v1 change.

For any BAML-extracted record in the BIEP v2 pipeline, this notebook shows
side-by-side the 4-path OCR/VLM ensemble output (Change 3):

1. Source PDF page (rendered from `s3://garage/oideachais/...`)
2. Docling DocTags XML (Path 1 — `baml_doctags`)
3. Unstract JSON output (Path 2 — `unstract_json`)
4. qwen3-vl-8b raw response (Path 3 — `qwen3_vl`)
5. gemma-4-26B-A4B raw response (Path 4 — `gemma4`)
6. RAGAS `biiep_extraction_consensus` score bar chart
7. Final BAML Pydantic object (`.voted_canonical`)
8. Langfuse trace link

Reads from the per-jurisdiction DuckLake namespace:
    cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.*
    (baml_canonical | unstract_json | qwen3_vl | gemma4 | voted_canonical)

KCG patterns used:
- ibis (per `.agents/skills/ibis/SKILL.md`)
- marimo (per `.agents/skills/marimo/SKILL.md`)

Reference: openspec/changes/2026-07-23-biep-v2-marimo-portal-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # OCR Ensemble Audit Trail — view the processed BAML output

        For any BAML-extracted record, this notebook shows the **complete
        provenance trail** — the source PDF, the 4-path OCR/VLM ensemble
        output (BAML + Unstract + qwen3-vl-8b + gemma-4-26B-A4B), the
        RAGAS consensus score, and the final canonical BAML Pydantic
        object.

        8 panels:
        1. Source PDF page (rendered from Garage S3)
        2. Docling DocTags XML
        3. Unstract JSON output
        4. qwen3-vl-8b raw response
        5. gemma-4-26B-A4B raw response
        6. RAGAS `biiep_extraction_consensus` score bar chart
        7. Final BAML Pydantic object (the `.voted_canonical` row)
        8. Langfuse trace link
        """
    )
    return (mo,)


@app.cell
def _filter_ui(mo):
    jurisdiction_filter = mo.ui.dropdown(
        options=["ireland", "england"],
        value="ireland",
        label="Jurisdiction",
    )
    record_id_filter = mo.ui.text(
        value=(
            "ireland.junior_cycle.english.en.year_1.2026.Q1.q1"
        ),
        label="Record ID",
    )
    mo.vstack([jurisdiction_filter, record_id_filter])
    return jurisdiction_filter, record_id_filter


@app.cell
def _ibis_conn(mo):
    """The ibis-first contract per the BIEP v2 spec."""
    import ibis

    conn = ibis.duckdb.connect("md:cianfhoghlaim")
    lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
    mo.md("✓ ibis-first contract wired — BIEP v2 DuckLake + Lance ready")
    return conn, lance


@app.cell
def _panel_1_source_pdf(conn, record_id_filter):
    """Panel 1: Source PDF page rendered as a `mo.image` from Garage S3."""
    import marimo as mo
    source_pdf = conn.sql(
        """
        SELECT source_pdf
        FROM cianfhoghlaim.education.british_isles.*._all_records
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    s3_url = source_pdf.iloc[0]["source_pdf"] if len(source_pdf) > 0 else None
    if s3_url:
        # Real impl: render PDF page via a PDF.js or pdf2image endpoint.
        mo.md(f"**Panel 1**: Source PDF → `{s3_url}` (page 1)")
    else:
        mo.md("**Panel 1**: Source PDF not found")
    return s3_url,


@app.cell
def _panel_2_docling(conn, record_id_filter):
    """Panel 2: Docling DocTags XML."""
    import marimo as mo
    docling_xml = conn.sql(
        """
        SELECT doctags
        FROM cianfhoghlaim.education.british_isles.*._all_docling
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    xml = docling_xml.iloc[0]["doctags"] if len(docling_xml) > 0 else "<doctags/>"
    mo.md("**Panel 2**: Docling DocTags XML")
    return mo.ui.code_editor(value=xml, language="xml", disabled=True)


@app.cell
def _panel_3_unstract(conn, record_id_filter):
    """Panel 3: Unstract JSON output."""
    import marimo as mo
    unstract_json = conn.sql(
        """
        SELECT workflow_id, raw_response
        FROM cianfhoghlaim.education.british_isles.*._all_unstract
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    json_str = (
        unstract_json.iloc[0]["raw_response"]
        if len(unstract_json) > 0
        else "{}"
    )
    mo.md("**Panel 3**: Unstract JSON output (collapsible)")
    return mo.ui.code_editor(value=json_str, language="json", disabled=True)


@app.cell
def _panel_4_qwen3_vl(conn, record_id_filter):
    """Panel 4: qwen3-vl-8b raw response."""
    import marimo as mo
    qwen3_vl_md = conn.sql(
        """
        SELECT raw_response
        FROM cianfhoghlaim.education.british_isles.*._all_qwen3_vl
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    md_text = qwen3_vl_md.iloc[0]["raw_response"] if len(qwen3_vl_md) > 0 else ""
    mo.md("**Panel 4**: qwen3-vl-8b raw response (folded markdown)")
    return mo.ui.code_editor(value=md_text[:5000], language="markdown", disabled=True)


@app.cell
def _panel_5_gemma4(conn, record_id_filter):
    """Panel 5: gemma-4-26B-A4B raw response."""
    import marimo as mo
    gemma4_md = conn.sql(
        """
        SELECT raw_response
        FROM cianfhoghlaim.education.british_isles.*._all_gemma4
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    md_text = gemma4_md.iloc[0]["raw_response"] if len(gemma4_md) > 0 else ""
    mo.md("**Panel 5**: gemma-4-26B-A4B raw response (folded markdown)")
    return mo.ui.code_editor(value=md_text[:5000], language="markdown", disabled=True)


@app.cell
def _panel_6_ragas_chart(conn, record_id_filter):
    """Panel 6: RAGAS `biiep_extraction_consensus` score bar chart."""
    import marimo as mo
    import altair as alt
    ragas_scores = conn.sql(
        """
        SELECT path, faithfulness, answer_relevance, context_precision
        FROM cianfhoghlaim.education.british_isles.*._all_ragas_scores
        WHERE record_id = %(record_id)s
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    if len(ragas_scores) == 0:
        chart = mo.md("_no RAGAS scores found_")
    else:
        chart = alt.Chart(ragas_scores).mark_bar().encode(
            x=alt.X("path:N", title="Path"),
            y=alt.Y("faithfulness:Q", title="RAGAS faithfulness"),
            color=alt.Color("path:N"),
            column="metric:N",
        ).properties(width=200, height=150)
        chart = mo.ui.altair_chart(chart)
    mo.md("**Panel 6**: RAGAS `biiep_extraction_consensus` scores")
    return chart,


@app.cell
def _panel_7_voted_canonical(conn, record_id_filter):
    """Panel 7: Final BAML Pydantic object (the `.voted_canonical` row)."""
    import marimo as mo
    voted = conn.sql(
        """
        SELECT *
        FROM cianfhoghlaim.education.british_isles.*._all_voted_canonical
        WHERE record_id = %(record_id)s
        LIMIT 1
        """,
        params={"record_id": record_id_filter.value},
    ).execute()
    table = voted if len(voted) > 0 else conn.sql("SELECT 'no data' AS message").execute()
    mo.md("**Panel 7**: Final BAML Pydantic object (the RAGAS-voted canonical row)")
    return table,


@app.cell
def _panel_8_langfuse_trace(record_id_filter):
    """Panel 8: Langfuse trace link (deep-link)."""
    import marimo as mo
    trace_url = (
        f"https://langfuse.cianfhoghlaim.ie/trace/"
        f"{record_id_filter.value}"
    )
    mo.md(
        f"**Panel 8**: Langfuse trace link → [open in Langfuse]({trace_url})"
    )
    return


if __name__ == "__main__":
    app.run()
