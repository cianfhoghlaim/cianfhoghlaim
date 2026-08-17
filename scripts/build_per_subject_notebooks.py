"""60-subject notebook generator — emits canonical per-subject marimo notebooks.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 9 - per-subject notebooks).

This script consumes:
- The 60-subject factory at `agents/adk/subjects/_factory.py:ALL_SUBJECT_AGENTS`
  (94 instances: 14 LC + 8 JC + 27 GCSE + 15 A-Level)
- The canonical template at `notebooks/_templates/per_subject_pipeline.py`
- The 4-stage BAML files (Phase 4)
- The 4-stage DLT registry (Phase 5)
- The 4-stage CocoIndex factory (Phase 6)

For each (stage, subject) tuple (deduplicated across the 3 GCSE + 3 A-Level boards),
it generates a per-subject notebook at:
- `notebooks/lc/<subject>.py` (14 subjects)
- `notebooks/jc/<subject>.py` (8 subjects)
- `notebooks/gcse/<subject>.py` (9 subjects)
- `notebooks/a_level/<subject>.py` (15 subjects)

Total: 14 + 8 + 9 + 15 = 46 unique subject notebooks (matching the
46 unique subjects in the 4-stage subject matrix).

Each generated notebook:
- Inherits from the canonical per-subject template
- Has the canonical 6-step BIEP pipeline (DLT -> BAML -> CocoIndex ->
  Cognee -> RAGAS -> Marimo)
- Wires through the canonical BAAI/bge-m3 1024-d embedder
- Surfaces the canonical per-subject dashboard

Usage:
    uv run python scripts/build_per_subject_notebooks.py --dry-run
    uv run python scripts/build_per_subject_notebooks.py
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import types
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway")


def load_file_as_module(path, name, base_mod=None):
    """Load a Python file as a module, properly handling relative imports."""
    with open(path) as f:
        code = f.read()
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    if base_mod is not None:
        module.__package__ = name.rsplit(".", 1)[0]
        base_name = name.rsplit(".", 1)[0] + ".base"
        sys.modules[base_name] = base_mod
    exec(compile(code, path, "exec"), module.__dict__)
    return module


def main() -> int:
    """Main entrypoint — generate the 46 per-subject marimo notebooks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only — don't write files",
    )
    args = parser.parse_args()

    template_path = REPO_ROOT / "notebooks" / "_templates" / "per_subject_pipeline.py"
    if not template_path.exists():
        print(f"ERROR: template not found at {template_path}")
        return 1
    template = template_path.read_text()

    # Load the agents factory (the 60-subject agent matrix)
    print("Loading the 60-subject factory...")
    base_mod = load_file_as_module(
        os.path.abspath("agents/adk/subjects/base.py"),
        "agents.adk.subjects.base",
    )
    factory_mod = load_file_as_module(
        os.path.abspath("agents/adk/subjects/_factory.py"),
        "agents.adk.subjects._factory",
        base_mod=base_mod,
    )
    factory_mod.LC_SUBJECT_AGENTS = base_mod.LC_SUBJECT_AGENTS
    factory_mod.JC_SUBJECT_AGENTS = base_mod.JC_SUBJECT_AGENTS
    factory_mod.GCSE_SUBJECT_AGENTS = base_mod.GCSE_SUBJECT_AGENTS
    factory_mod.A_LEVEL_SUBJECT_AGENTS = base_mod.A_LEVEL_SUBJECT_AGENTS

    all_agents = factory_mod.ALL_SUBJECT_AGENTS
    print(f"Loaded {len(all_agents)} agents (94 instances)")

    # Group by (stage, subject) — one notebook per unique subject per stage
    notebooks_to_create: dict[tuple[str, str], list[str]] = {}
    for agent in all_agents:
        key = (agent.stage, agent.subject)
        if key not in notebooks_to_create:
            notebooks_to_create[key] = []
        notebooks_to_create[key].append(agent.board)

    print(f"Unique (stage, subject) combinations: {len(notebooks_to_create)}")

    # Stage display name mapping
    stage_display = {
        "lc": "Leaving Certificate (LC)",
        "jc": "Junior Cycle (JC)",
        "gcse": "GCSE",
        "a_level": "A-Level",
    }

    # Language display mapping
    language_display = {
        "en": "English",
        "ga": "Gaeilge (Irish)",
        "both": "Bilingual (EN + GA)",
    }

    # Exam board display
    exam_board_display = {
        "aqa": "AQA",
        "ocr": "OCR",
        "edexcel": "Edexcel",
    }

    created_count = 0
    for (stage, subject), boards in sorted(notebooks_to_create.items()):
        # Get the canonical agent config
        sample_agent = next(
            a for a in all_agents if a.stage == stage and a.subject == subject
        )

        # Subject display name (from the factory)
        display_name = sample_agent.display_name
        ncca_code = sample_agent.ncca_code
        spec_code = sample_agent.spec_code
        language = ", ".join(
            language_display.get(lang, lang) for lang in sample_agent.languages
        )
        level = (
            "Higher"
            if stage == "lc"
            else "Common"
            if stage == "jc"
            else "Foundation / Higher"
            if stage == "gcse"
            else "AS / A2"
        )
        exam_boards = ", ".join(exam_board_display.get(b, b) for b in boards)

        # Render the template
        notebook = template
        notebook = notebook.replace("{SUBJECT}", subject)
        notebook = notebook.replace("{SUBJECT_DISPLAY_NAME}", display_name)
        notebook = notebook.replace("{STAGE}", stage)
        notebook = notebook.replace("{STAGE_DISPLAY_NAME}", stage_display[stage])
        notebook = notebook.replace("{NCCA_CODE}", ncca_code)
        notebook = notebook.replace("{LANGUAGE}", language)
        notebook = notebook.replace("{LEVEL}", level)
        notebook = notebook.replace("{EXAM_BOARD}", exam_boards)
        notebook = notebook.replace("{COCOINDEX_APP}", sample_agent.cocoindex_app)

        # Write to the canonical per-subject notebook path
        out_path = REPO_ROOT / "notebooks" / stage / f"{subject}.py"
        if not args.dry_run:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(notebook)
        created_count += 1
        print(
            f"  {'would create' if args.dry_run else 'created'}: "
            f"{out_path.relative_to(REPO_ROOT)}"
        )

    print()
    print(f"Total: {created_count} per-subject notebooks")
    if args.dry_run:
        print("(DRY-RUN — no files written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
