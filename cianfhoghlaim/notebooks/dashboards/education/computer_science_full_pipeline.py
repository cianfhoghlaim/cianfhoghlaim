#!/usr/bin/env python3
"""Full Computer_Science LC pipeline: DLT → BAML → CocoIndex → Cognee → marimo.

This notebook demonstrates the complete 6-asset dagster pipeline for
computer_science. Run it after `dagster asset materialize --select "computer_science_*"`
to see the end-to-end flow.

Pipeline steps:
1. DLT ingest the computer_science syllabus PDFs (4-12 files per level)
2. BAML ExtractLeavingCertSyllabus to extract structured data
3. BAML GenerateComputer_ScienceQuestPack for formative items
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
    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.computer_science import computer_science_source
    from cianfhoghlaim.baml_client import b
    from pathlib import Path
    return b, dlt, Path, computer_science_source


@app.cell
def __(b, dlt, computer_science_source, Path):
    """Step 1: DLT ingest the computer_science PDFs."""
    pipeline = dlt.pipeline(
        pipeline_name="computer_science_syllabus_demo",
        destination="duckdb",
        dataset_name="computer_science_syllabus",
    )
    pdf_dir = Path("leaving_certificate/computer_science")
    if pdf_dir.exists():
        load_info = pipeline.run(computer_science_source(base_path=pdf_dir))
        return (f"DLT ingested {len(load_info.load_packages)} load packages",)
    return ("No PDFs found in {pdf_dir} — skip",)


@app.cell
def __(b, Path):
    """Step 2: BAML ExtractLeavingCertSyllabus for each PDF."""
    pdf_dir = Path("leaving_certificate/computer_science")
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
    """Step 3: BAML GenerateComputer_ScienceQuestPack."""
    packs = []
    for row in rows:
        if "error" in row:
            continue
        try:
            pack = b.GenerateComputer_ScienceQuestPack(
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
    """Step 4: CocoIndex v1 embedding (lazy, via the computer_science_embedding dagster asset)."""
    return ("Run: dagster asset materialize --select computer_science_embedding",)


@app.cell
def __():
    """Step 5: Cognee cognify pass (lazy, via the computer_science_cognify dagster asset)."""
    return ("Run: dagster asset materialize --select computer_science_cognify",)


@app.cell
def __():
    """Step 6: marimo dashboard render."""
    import marimo as mo
    return mo


if __name__ == "__main__":
    app.run()
