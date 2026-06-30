#!/usr/bin/env python3
"""Full Applied_Mathematics LC pipeline: DLT → BAML → CocoIndex → Cognee → marimo.

This notebook demonstrates the complete 6-asset dagster pipeline for
applied_mathematics. Run it after `dagster asset materialize --select "applied_mathematics_*"`
to see the end-to-end flow.

Pipeline steps:
1. DLT ingest the applied_mathematics syllabus PDFs (4-12 files per level)
2. BAML ExtractLeavingCertSyllabus to extract structured data
3. BAML GenerateApplied_MathematicsQuestPack for formative items
4. CocoIndex v1 embedding into LanceDB
5. Cognee cognify pass (subject knowledge graph)
6. marimo notebook execution (this notebook)
"""
import marimo

__generated_with_marimo = True
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return mo,


@app.cell
def __():
    import dlt
    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.applied_mathematics import applied_mathematics_source
    from cianfhoghlaim.baml_client import b
    from pathlib import Path
    return b, dlt, Path, applied_mathematics_source


@app.cell
def __(b, dlt, applied_mathematics_source, Path):
    """Step 1: DLT ingest the applied_mathematics PDFs."""
    pipeline = dlt.pipeline(
        pipeline_name="applied_mathematics_syllabus_demo",
        destination="duckdb",
        dataset_name="applied_mathematics_syllabus",
    )
    pdf_dir = Path("leaving_certificate/applied_mathematics")
    if pdf_dir.exists():
        load_info = pipeline.run(applied_mathematics_source(base_path=pdf_dir))
        return (f"DLT ingested {len(load_info.load_packages)} load packages",)
    return ("No PDFs found in {pdf_dir} — skip",)


@app.cell
def __(b, Path):
    """Step 2: BAML ExtractLeavingCertSyllabus for each PDF."""
    pdf_dir = Path("leaving_certificate/applied_mathematics")
    rows = []
    if pdf_dir.exists():
        for pdf in pdf_dir.rglob("*.pdf"):
            text = pdf.read_text(errors="ignore")[:10000]  # truncate
            try:
                syllabus = b.ExtractLeavingCertSyllabus(pdf_text=text)
                rows.append({"pdf": pdf.name, "level": getattr(syllabus, "level", "?")})
            except Exception as e:
                rows.append({"pdf": pdf.name, "error": str(e)})
    return rows


@app.cell
def __(b, rows):
    """Step 3: BAML GenerateApplied_MathematicsQuestPack."""
    packs = []
    for row in rows:
        if "error" in row:
            continue
        try:
            pack = b.GenerateApplied_MathematicsQuestPack(
                syllabus={"level": row["level"]},
                past_papers=[],
                marking_schemes=[],
                level=row["level"],
            )
            packs.append({"level": row["level"], "items": getattr(pack, "items", [])})
        except Exception as e:
            packs.append({"level": row["level"], "error": str(e)})
    return packs


@app.cell
def __():
    """Step 4: CocoIndex v1 embedding (lazy, via the applied_mathematics_embedding dagster asset)."""
    return ("Run: dagster asset materialize --select applied_mathematics_embedding",)


@app.cell
def __():
    """Step 5: Cognee cognify pass (lazy, via the applied_mathematics_cognify dagster asset)."""
    return ("Run: dagster asset materialize --select applied_mathematics_cognify",)


@app.cell
def __():
    """Step 6: marimo dashboard render."""
    import marimo as mo
    return mo


if __name__ == "__main__":
    app.run()
