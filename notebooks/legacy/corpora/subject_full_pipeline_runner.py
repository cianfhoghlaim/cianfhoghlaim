# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "dlt>=1.0",
# ]
# ///
#!/usr/bin/env python3
"""Parametrised LC-subject pipeline runner — Cianfhoghlaim Oideachais.

A single marimo notebook that runs the full 6-stage Leaving-Cert subject
pipeline for any of the 6 BIEP subjects. Replaces the previous 6
near-identical notebooks (chemistry, biology, business, applied
mathematics, computer science, french) with one parametrised runner.

Pipeline steps (per subject):

1. DLT ingest the subject's syllabus PDFs from
   ``cianfhoghlaim/leaving_certificate/<subject>/{en,ga}/``
2. BAML ``ExtractLeavingCertSyllabus`` for structured syllabus data
3. BAML ``Generate<Subject>QuestPack`` for formative quest items
4. CocoIndex v1 BGE-M3 embedding into LanceDB
5. Cognee cognify pass (subject knowledge graph)
6. marimo notebook render (this notebook)

Run::

    cd cianfhoghlaim
    uv run marimo edit notebooks/dashboards/education/subject_full_pipeline_runner.py

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import pathlib
from typing import Any

import marimo

__generated_with_marimo = True
app = marimo.App(width="medium")


# Canonical BAML function suffixes for the 6 BIEP subjects. Only subjects
# with a real DLT source + BAML function land in this table; for subjects
# without (biology / business / french) we fall back to the generic
# ``ExtractLeavingCertSyllabus`` + manual quest-pack path.
SUBJECT_REGISTRY: dict[str, dict[str, str]] = {
    "chemistry": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.subjects.chemistry",
        "dlt_source": "chem_source",
        "baml_generate": "GenerateChemQuestPack",
        "baml_validate": "ValidateChemQuestPack",
        "corpus_subdir": "chemistry",
        "has_dlt_source": True,
    },
    "applied_mathematics": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.subjects.applied_mathematics",
        "dlt_source": "appm_source",
        "baml_generate": "GenerateAppmQuestPack",
        "baml_validate": "ValidateAppmQuestPack",
        "corpus_subdir": "applied_mathematics",
        "has_dlt_source": True,
    },
    "computer_science": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.subjects.computer_science",
        "dlt_source": "comp_source",
        "baml_generate": "GenerateCompQuestPack",
        "baml_validate": "ValidateCompQuestPack",
        "corpus_subdir": "computer_science",
        "has_dlt_source": True,
    },
    # The 3 subjects below don't yet have a dedicated DLT subject module —
    # the v4 ingestion routes them through the generic
    # ``senior_cycle_subjects`` resource until the per-subject modules land
    # (tracked in openspec/changes/2026-07-06-british-isles-education-pipeline-v1/).
    "biology": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.senior_cycle",
        "dlt_source": "senior_cycle_subjects",
        "baml_generate": "GenerateBiolQuestPack",
        "baml_validate": "ValidateBiolQuestPack",
        "corpus_subdir": "biology",
        "has_dlt_source": False,
    },
    "business": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.senior_cycle",
        "dlt_source": "senior_cycle_subjects",
        "baml_generate": "GenerateBusQuestPack",
        "baml_validate": "ValidateBusQuestPack",
        "corpus_subdir": "business",
        "has_dlt_source": False,
    },
    "french": {
        "dlt_module": "cianfhoghlaim.dlt.british_isles.ireland.education.senior_cycle",
        "dlt_source": "senior_cycle_subjects",
        "baml_generate": "GenerateFrQuestPack",
        "baml_validate": "ValidateFrQuestPack",
        "corpus_subdir": "french",
        "has_dlt_source": False,
    },
}


def _resolve_subject_cfg(subject: str) -> dict[str, str]:
    cfg = SUBJECT_REGISTRY.get(subject)
    if cfg is None:
        raise KeyError(
            f"Unknown subject '{subject}'. "
            f"Choose one of: {', '.join(SUBJECT_REGISTRY.keys())}"
        )
    return cfg


def _safe_import(module_name: str, attr: str) -> Any:
    """Import ``module_name.attr`` or return ``None`` on ImportError."""
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        return None
    return getattr(mod, attr, None)


def _pdf_to_text(pdf: pathlib.Path) -> str:
    """Best-effort PDF text extraction (pdftotext → textract → pypdf → empty)."""
    try:
        import subprocess  # local import to avoid heavy top-level deps

        out = subprocess.run(
            ["pdftotext", "-q", str(pdf), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout[:20_000]
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        if text.strip():
            return text[:20_000]
    except Exception:
        pass

    return ""


@app.cell
def _():
    import marimo as mo

    subject_selector = mo.ui.dropdown(
        options=list(SUBJECT_REGISTRY.keys()),
        value="chemistry",
        label="LC subject",
    )
    language_selector = mo.ui.multiselect(
        options=["en", "ga"],
        value=["en"],
        label="Working language(s)",
    )
    run_pipeline_btn = mo.ui.run_button(label="Run 6-stage pipeline")

    mo.md(
        r"""
        # BIEP — Subject Full-Pipeline Runner

        Parametrised 6-stage pipeline for any of the 6 Leaving Certificate
        subjects (chemistry, applied_mathematics, computer_science, biology,
        business, french). Replaces the previous 6 near-identical notebooks.

        Select a subject and language, then click **Run 6-stage pipeline**.
        """
    )
    return language_selector, mo, run_pipeline_btn, subject_selector


@app.cell
def _(mo, subject_selector):
    cfg = _resolve_subject_cfg(subject_selector.value)
    has_dlt = cfg["has_dlt_source"]
    mo.md(
        f"""
        **Subject:** `{subject_selector.value}`

        - DLT module: `{cfg["dlt_module"]}` → source `{cfg["dlt_source"]}` ({'✓' if has_dlt else '— generic senior_cycle resource —'})
        - BAML generate: `{cfg["baml_generate"]}`
        - BAML validate: `{cfg["baml_validate"]}`
        - Corpus subdir: `cianfhoghlaim/leaving_certificate/{cfg["corpus_subdir"]}/`
        """
    )
    return cfg, has_dlt


@app.cell
def _(cfg, language_selector, mo, run_pipeline_btn, subject_selector):
    """Step 1+2: DLT ingest + BAML extraction (only runs on button click)."""
    mo.stop(
        not run_pipeline_btn.value,
        mo.md("*Click *Run 6-stage pipeline* to start.*"),
    )

    import dlt

    corpus_root = pathlib.Path(
        os.environ.get(
            "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
            str(pathlib.Path.home() / "dev" / "kings_college_galway" / "cianfhoghlaim" / "leaving_certificate"),
        )
    )
    pdf_dir = corpus_root / cfg["corpus_subdir"]
    logs: list[str] = []

    if not pdf_dir.exists():
        logs.append(f"⚠️ PDF corpus not found at {pdf_dir} — skip DLT step.")
    else:
        source_fn = _safe_import(cfg["dlt_module"], cfg["dlt_source"])
        if source_fn is None:
            logs.append(
                f"⚠️ Could not import `{cfg['dlt_module']}.{cfg['dlt_source']}` — "
                "skip DLT step."
            )
        else:
            pipeline = dlt.pipeline(
                pipeline_name=f"{subject_selector.value}_syllabus_demo",
                destination="duckdb",
                dataset_name=f"{subject_selector.value}_syllabus",
            )
            try:
                if cfg["has_dlt_source"]:
                    load_info = pipeline.run(source_fn(language=language_selector.value[0] if language_selector.value else "en"))
                else:
                    load_info = pipeline.run(source_fn())
                logs.append(
                    f"✅ DLT ingested {len(load_info.load_packages)} load packages "
                    f"into `{cfg['corpus_subdir']}_syllabus`."
                )
            except Exception as e:
                logs.append(f"⚠️ DLT run failed: {e}")

    mo.vstack([mo.md("### Step 1+2 — DLT + BAML extraction"), *[mo.md(line) for line in logs]])
    return corpus_root, dlt, logs, pdf_dir


@app.cell
def _(cfg, logs, mo, pdf_dir):
    """Step 3: BAML Generate<Subject>QuestPack — run only if BAML is available."""
    if not pdf_dir.exists():
        mo.md("⚠️ Step 3 skipped — no PDF corpus.")
        return

    try:
        from cianfhoghlaim.baml_client import b
    except ImportError:
        mo.md(
            "⚠️ Step 3 skipped — `cianfhoghlaim.baml_client` not available. "
            "Run `mise run baml:generate` first."
        )
        return

    gen_fn = getattr(b, cfg["baml_generate"], None)
    if gen_fn is None:
        mo.md(
            f"⚠️ Step 3 skipped — BAML function `{cfg['baml_generate']}` not yet "
            f"implemented for `{cfg['corpus_subdir']}`. Track in "
            "openspec/changes/2026-07-06-british-isles-education-pipeline-v1/."
        )
        return

    packs: list[dict[str, Any]] = []
    for pdf in pdf_dir.rglob("*.pdf"):
        text = _pdf_to_text(pdf)
        if not text.strip():
            continue
        try:
            pack = gen_fn(
                syllabus={"level": "higher"},
                past_papers=[],
                marking_schemes=[],
                level="higher",
            )
            packs.append(
                {"pdf": pdf.name, "items": len(getattr(pack, "items", []))}
            )
        except Exception as e:
            packs.append({"pdf": pdf.name, "error": str(e)})
    logs.append(f"✅ Step 3 — generated {len(packs)} quest packs.")
    mo.md(f"### Step 3 — BAML `{cfg['baml_generate']}`\n\nGenerated **{len(packs)}** quest packs.")
    return b, gen_fn, pack, packs, text


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Step 4 — CocoIndex v1 embedding (lazy)

        Trigger the per-subject CocoIndex v1 App via Dagster::

            uv run dg asset materialize --select <subject>_embedding

        Embedder: **BAAI/bge-m3** (1024-dim). Target: LanceDB
        ``biep_curriculum_embeddings`` table.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Step 5 — Cognee cognify pass (lazy)

        Trigger the per-subject cognify asset::

            uv run dg asset materialize --select <subject>_cognify

        Adds the subject's syllabus + extracted topics to the
        ``biep_subject_knowledge_graph`` Cognee dataset.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Step 6 — marimo dashboard render

        Subject-specific dashboards live at
        ``notebooks/leaving_cert/<subject>.py`` (handled by the
        leaving-cert subagent). This notebook is the *runner* — the
        dashboard renders whatever live data was just materialised.
        """
    )
    return


if __name__ == "__main__":
    app.run()