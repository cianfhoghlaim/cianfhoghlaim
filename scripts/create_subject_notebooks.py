#!/usr/bin/env python3
"""Create per-subject full_pipeline notebooks in notebooks/dashboards/education/.

Per R7.1: 11 per-subject notebooks showing the full DLT→BAML→CocoIndex→Cognee
→ marimo workflow.
"""
from __future__ import annotations
from pathlib import Path

# 11 subjects to cover
SUBJECTS = [
    "mathematics", "english", "gaeilge", "applied_mathematics",
    "chemistry", "computer_science", "biology", "business",
    "french", "geography", "history",
]

# Skip the already-existing notebooks (R7.1 only creates the missing ones)
ALREADY_EXISTS = {
    "mathematics",  # has 3+ versions
    "english",       # existing
    "gaeilge",       # gael already covered
    "geography",     # has geography.py
    "history",       # has history.py
}


def generate_notebook(subject: str) -> str:
    """Generate a full-pipeline notebook for the given subject."""
    return f'''#!/usr/bin/env python3
"""Full {subject.title()} LC pipeline: DLT → BAML → CocoIndex → Cognee → marimo.

This notebook demonstrates the complete 6-asset dagster pipeline for
{subject}. Run it after `dagster asset materialize --select "{subject}_*"`
to see the end-to-end flow.

Pipeline steps:
1. DLT ingest the {subject} syllabus PDFs (4-12 files per level)
2. BAML ExtractLeavingCertSyllabus to extract structured data
3. BAML Generate{subject.title().replace(" ", "")}QuestPack for formative items
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
    from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.{subject} import {subject}_source
    from cianfhoghlaim.baml_client import b
    from pathlib import Path
    return b, dlt, Path, {subject}_source


@app.cell
def __(b, dlt, {subject}_source, Path):
    """Step 1: DLT ingest the {subject} PDFs."""
    pipeline = dlt.pipeline(
        pipeline_name="{subject}_syllabus_demo",
        destination="duckdb",
        dataset_name="{subject}_syllabus",
    )
    pdf_dir = Path("leaving_certificate/{subject}")
    if pdf_dir.exists():
        load_info = pipeline.run({subject}_source(base_path=pdf_dir))
        return (f"DLT ingested {{len(load_info.load_packages)}} load packages",)
    return ("No PDFs found in {{pdf_dir}} — skip",)


@app.cell
def __(b, Path):
    """Step 2: BAML ExtractLeavingCertSyllabus for each PDF."""
    pdf_dir = Path("leaving_certificate/{subject}")
    rows = []
    if pdf_dir.exists():
        for pdf in pdf_dir.rglob("*.pdf"):
            text = pdf.read_text(errors="ignore")[:10000]  # truncate
            try:
                syllabus = b.ExtractLeavingCertSyllabus(pdf_text=text)
                rows.append({{"pdf": pdf.name, "level": getattr(syllabus, "level", "?")}})
            except Exception as e:
                rows.append({{"pdf": pdf.name, "error": str(e)}})
    return rows


@app.cell
def __(b, rows):
    """Step 3: BAML Generate{subject.title()}QuestPack."""
    packs = []
    for row in rows:
        if "error" in row:
            continue
        try:
            pack = b.Generate{subject.title().replace(" ", "")}QuestPack(
                syllabus={{"level": row["level"]}},
                past_papers=[],
                marking_schemes=[],
                level=row["level"],
            )
            packs.append({{"level": row["level"], "items": getattr(pack, "items", [])}})
        except Exception as e:
            packs.append({{"level": row["level"], "error": str(e)}})
    return packs


@app.cell
def __():
    """Step 4: CocoIndex v1 embedding (lazy, via the {subject}_embedding dagster asset)."""
    return ("Run: dagster asset materialize --select {subject}_embedding",)


@app.cell
def __():
    """Step 5: Cognee cognify pass (lazy, via the {subject}_cognify dagster asset)."""
    return ("Run: dagster asset materialize --select {subject}_cognify",)


@app.cell
def __():
    """Step 6: marimo dashboard render."""
    import marimo as mo
    return mo


if __name__ == "__main__":
    app.run()
'''


def main() -> None:
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/notebooks/dashboards/education")
    for subject in SUBJECTS:
        if subject in ALREADY_EXISTS:
            print(f"[SKIP] {subject}_full_pipeline.py (exists)")
            continue
        path = root / f"{subject}_full_pipeline.py"
        if path.exists():
            print(f"[SKIP] {path.name} (exists)")
            continue
        content = generate_notebook(subject)
        path.write_text(content)
        print(f"[OK] {path.name} ({len(content)} chars)")


if __name__ == "__main__":
    main()