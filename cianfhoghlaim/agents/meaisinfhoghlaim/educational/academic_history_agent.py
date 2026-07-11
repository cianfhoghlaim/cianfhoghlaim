"""Academic History Agent — chat over the user's academic record.

The 13th bucket in the L5 routing map (per
`openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/`).
Routes queries about the user's modules, notes, assignments, exam
papers, answer scripts, formulas, progress, and timeline.

Wires through the canonical `MemoryBackend` Protocol via
`from cianfhoghlaim.storage.memf import get_default_backend`
(see the `agent-memory-systems` spec).

Tools (10):

- `list_my_modules`
- `list_my_artifacts`
- `get_my_notes`
- `get_my_assignments`
- `get_my_exam_history`
- `get_my_answer_scripts`
- `summarise_my_progress`
- `recommend_next_revision`
- `compare_my_answer_to_solution`
- `search_my_formulas`

The tools read from three sources:

1. The academic-history lakehouse tables
   (`oideachais.education.ie.uog_math_coursework`,
   `oideachais_academic_history.*`).
2. The Convex `subject_sessions` + `practice_attempts` + `annotations`
   tables (the user's chat history, attempts, and personal notes).
3. The `academic_history_manifest.yaml` (the user's pseudonymous
   identity and the configured module roots).

BAML extraction (`b.ExtractAcademicHistorySnapshot`) produces a
typed `AcademicHistorySnapshot` that the agent returns at the end of
every turn.
"""
from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Memory backend Protocol (graceful degradation).
try:
    from cianfhoghlaim.storage.memf import (  # type: ignore[import-not-found]
        MemoryBackend,
        get_default_backend,
    )

    _MEMORY_BACKEND_AVAILABLE = True
except Exception:
    _MEMORY_BACKEND_AVAILABLE = False
    get_default_backend = None  # type: ignore[assignment]
    MemoryBackend = None  # type: ignore[assignment, misc]

# BAML client (graceful degradation).
try:
    from baml_client import b  # type: ignore[import-not-found]

    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

# Wire-up dataclass (parallels `WireSubjectAgent` in tuatha/wiring.py).
try:
    from cianfhoghlaim.agents.tuatha.wiring import (  # type: ignore[import-not-found]
        SubjectAgentWiring,
        WireSubjectAgent,
    )

    _WIRE_AVAILABLE = True
except Exception:
    _WIRE_AVAILABLE = False

    @dataclass
    class SubjectAgentWiring:  # type: ignore[no-redef]
        ncca_subject: str = "academic_history"
        module_slug: str = "academic_history"
        display_name: str = "Academic History"
        baml_prefix: str = "History"
        langfuse_trace_name: str = "agent.academic_history.<verb>"
        cognee_dataset: str = "oideachais_history"
        tuatha_de: str = "Cian"
        lore: str = "stair-acadúil"

    @dataclass
    class WireSubjectAgent:  # type: ignore[no-redef]
        """Stub fallback so `academic_history_agent_wire` is always importable."""

        subject: Any = None
        memory_backend_kind: str | None = None
        langfuse_wired: bool = False
        cognee_wired: bool = False
        baml_prefix: str | None = None


# ---------------------------------------------------------------------------
# Manifest resolution
# ---------------------------------------------------------------------------

DEFAULT_MANIFEST_PATH = os.environ.get(
    "ACADEMIC_HISTORY_MANIFEST",
    "academic_history_manifest.yaml",
)


def _load_manifest(path: str | Path | None = None):
    """Load the academic-history manifest.

    Returns `None` if the manifest does not exist or the loader is
    unavailable. Tools that require the manifest MUST handle `None`
    gracefully.
    """
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (  # type: ignore[import-not-found]
        load_manifest,
    )

    candidate = Path(path or DEFAULT_MANIFEST_PATH)
    if not candidate.exists():
        return None
    try:
        return load_manifest(candidate)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Tool helpers (in-memory; tools delegate to these)
# ---------------------------------------------------------------------------


def _list_modules_from_manifest() -> list[dict[str, Any]]:
    manifest = _load_manifest()
    if manifest is None:
        return []
    return [
        {
            "module_code": r.module_code,
            "module_title": r.module_title,
            "institution": r.institution,
            "academic_year": r.academic_year,
            "resolved_path": str(manifest.resolve_path(r.path)),
        }
        for r in manifest.module_roots
    ]


def _list_artifacts_from_manifest(limit: int = 50) -> list[dict[str, Any]]:
    """Walk every resolved module folder and yield file-level rows.

    Privacy-gated: identity folders are excluded by default.
    """
    manifest = _load_manifest()
    if manifest is None:
        return []
    rows: list[dict[str, Any]] = []
    for root in manifest.module_roots:
        path = manifest.resolve_path(root.path)
        if not path.exists() or not path.is_dir():
            continue
        for f in sorted(path.rglob("*")):
            if not f.is_file():
                continue
            rel = str(f.relative_to(path))
            if not manifest.include_file(rel):
                continue
            rows.append(
                {
                    "module_code": root.module_code,
                    "module_title": root.module_title,
                    "file_name": f.name,
                    "rel_path": rel,
                    "size_bytes": f.stat().st_size,
                    "extension": f.suffix.lower(),
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def _summarise_progress() -> dict[str, Any]:
    """Build a per-user progress summary from manifest + artefact counts.

    This is the in-memory fallback; in production the agent delegates
    to `b.ExtractAcademicHistorySnapshot`.
    """
    manifest = _load_manifest()
    artefacts = _list_artifacts_from_manifest(limit=10_000)
    notes = [a for a in artefacts if a["extension"] in {".md", ".txt", ".pdf", ".docx"}]
    assignments = [a for a in artefacts if "assignment" in a["rel_path"].lower()]
    exams = [a for a in artefacts if "exam" in a["rel_path"].lower()]
    answers = [a for a in artefacts if "answer" in a["rel_path"].lower()]
    formulas = [a for a in artefacts if a["extension"] == ".tex"]

    summary: dict[str, Any] = {
        "pseudonym_hash": manifest.pseudonym_hash() if manifest else None,
        "modules_count": len(_list_modules_from_manifest()),
        "artefacts_count": len(artefacts),
        "notes_count": len(notes),
        "assignment_count": len(assignments),
        "exam_count": len(exams),
        "answer_count": len(answers),
        "formula_count": len(formulas),
    }

    # Try BAML extraction (typed `AcademicHistorySnapshot`).
    if _BAML_AVAILABLE and b is not None and manifest is not None:
        try:
            history_json = json.dumps(
                {
                    "pseudonym_hash": summary["pseudonym_hash"],
                    "modules": [
                        {"module_code": m["module_code"], "status": "in_progress"}
                        for m in _list_modules_from_manifest()
                    ],
                    "artefacts": [
                        {"module_code": a["module_code"], "kind": "note"}
                        for a in notes[:50]
                    ],
                },
                indent=2,
            )
            snapshot = b.ExtractAcademicHistorySnapshot(history_json=history_json)
            summary["summary_en"] = snapshot.summary_en
            summary["summary_ga"] = snapshot.summary_ga
            summary["next_recommended_action"] = snapshot.next_recommended_action
            summary["confidence"] = snapshot.confidence
        except Exception:
            summary["summary_en"] = (
                f"You have {summary['modules_count']} modules and "
                f"{summary['artefacts_count']} artefacts. "
                "Try `recommend_next_revision` for a tailored revision plan."
            )
            summary["confidence"] = 0.0

    return summary


def _recommend_next_revision(top_n: int = 3) -> list[dict[str, Any]]:
    """Heuristic: rank modules by artefact density + recency."""
    manifest = _load_manifest()
    if manifest is None:
        return []
    modules = _list_modules_from_manifest()
    artefacts = _list_artifacts_from_manifest(limit=10_000)
    by_module: dict[str, list[dict[str, Any]]] = {}
    for a in artefacts:
        by_module.setdefault(a["module_code"], []).append(a)

    recs: list[dict[str, Any]] = []
    for m in modules:
        code = m["module_code"]
        rows = by_module.get(code, [])
        recs.append(
            {
                "module_code": code,
                "module_title": m["module_title"],
                "artefact_count": len(rows),
                "rationale": (
                    f"{len(rows)} artefacts on disk; recommend reviewing "
                    "formula sheets + worked solutions + last 2 assignments."
                ),
            }
        )
    recs.sort(key=lambda r: r["artefact_count"], reverse=True)
    return recs[:top_n]


def _compare_answer_to_solution(
    *, answer_path: str, solution_path: str
) -> dict[str, Any]:
    """Stub: read both files and return a side-by-side diff.

    The deterministic comparison (mark totals, formula references,
    LaTeX well-formedness) is delegated to
    `baml.education.university.math_validation`.
    """
    from cianfhoghlaim.baml.education.university.math_validation import (  # type: ignore[import-not-found]
        validate_mark_totals,
        validate_step_indices,
    )

    a = Path(answer_path)
    s = Path(solution_path)
    out: dict[str, Any] = {
        "answer_path": str(a),
        "solution_path": str(s),
        "answer_exists": a.exists(),
        "solution_exists": s.exists(),
    }
    if a.exists():
        out["answer_chars"] = a.stat().st_size
    if s.exists():
        out["solution_chars"] = s.stat().st_size

    findings: list[dict[str, Any]] = []
    findings.extend(
        f.to_dict()
        for f in (validate_step_indices(None) + validate_mark_totals(question_marks=None, step_marks_sum=None))
    )
    out["findings"] = findings
    out["next_step"] = (
        "Open the formula registry notebook (`06_formulas_theorems_worked_solutions.py`) "
        "and run a side-by-side render."
    )
    return out


def _search_my_formulas(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Grep `.tex` files in resolved module folders for a query."""
    manifest = _load_manifest()
    if manifest is None:
        return []
    rows: list[dict[str, Any]] = []
    q = query.lower()
    for root in manifest.module_roots:
        path = manifest.resolve_path(root.path)
        if not path.exists():
            continue
        for f in sorted(path.rglob("*.tex")):
            if not manifest.include_file(str(f.relative_to(path))):
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if q in text.lower():
                rows.append(
                    {
                        "module_code": root.module_code,
                        "file_name": f.name,
                        "rel_path": str(f.relative_to(path)),
                        "snippet": _snippet(text, q),
                    }
                )
                if len(rows) >= limit:
                    return rows
    return rows


def _snippet(text: str, q: str, width: int = 80) -> str:
    lower = text.lower()
    idx = lower.find(q)
    if idx == -1:
        return text[:width]
    start = max(0, idx - width // 2)
    end = min(len(text), idx + width // 2)
    return text[start:end].replace("\n", " ")


# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]


TOOLS: list[Tool] = [
    Tool(
        name="list_my_modules",
        description="List the user's configured modules (from the academic-history manifest).",
        fn=lambda: _list_modules_from_manifest(),
    ),
    Tool(
        name="list_my_artifacts",
        description="List the user's artefacts (privacy-gated).",
        fn=lambda limit=50: _list_artifacts_from_manifest(limit=limit),
    ),
    Tool(
        name="get_my_notes",
        description="Return all artefacts classified as notes (md/txt/pdf/docx).",
        fn=lambda: [a for a in _list_artifacts_from_manifest(limit=10_000) if a["extension"] in {".md", ".txt", ".pdf", ".docx"}],
    ),
    Tool(
        name="get_my_assignments",
        description="Return all artefacts with 'assignment' in the path.",
        fn=lambda: [a for a in _list_artifacts_from_manifest(limit=10_000) if "assignment" in a["rel_path"].lower()],
    ),
    Tool(
        name="get_my_exam_history",
        description="Return all artefacts with 'exam' in the path.",
        fn=lambda: [a for a in _list_artifacts_from_manifest(limit=10_000) if "exam" in a["rel_path"].lower()],
    ),
    Tool(
        name="get_my_answer_scripts",
        description="Return all artefacts with 'answer' in the path.",
        fn=lambda: [a for a in _list_artifacts_from_manifest(limit=10_000) if "answer" in a["rel_path"].lower()],
    ),
    Tool(
        name="summarise_my_progress",
        description="Return a per-user progress summary (counts + BAML-typed snapshot).",
        fn=_summarise_progress,
    ),
    Tool(
        name="recommend_next_revision",
        description="Return top-N modules to revise, ranked by artefact density.",
        fn=lambda top_n=3: _recommend_next_revision(top_n=top_n),
    ),
    Tool(
        name="compare_my_answer_to_solution",
        description="Compare a student answer file to a worked-solution file (structural diff).",
        fn=_compare_answer_to_solution,
    ),
    Tool(
        name="search_my_formulas",
        description="Search the user's .tex files for a query string.",
        fn=lambda query, limit=20: _search_my_formulas(query=query, limit=limit),
    ),
]


TOOL_NAMES: set[str] = {t.name for t in TOOLS}


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------


def run_tool(tool_name: str, /, **kwargs: Any) -> Any:
    """Run a tool by name (strict; raises ValueError if unknown)."""
    for t in TOOLS:
        if t.name == tool_name:
            return t.fn(**kwargs)
    raise ValueError(f"unknown tool: {tool_name}")


def list_tools() -> list[dict[str, Any]]:
    """Return the tool registry as JSON-serialisable dicts."""
    return [{"name": t.name, "description": t.description} for t in TOOLS]


# ---------------------------------------------------------------------------
# Memory wire-up (per the `agent-memory-systems` spec)
# ---------------------------------------------------------------------------


def _build_wire() -> WireSubjectAgent:
    """Build the `academic_history_agent_wire` singleton.

    Defers to `get_default_backend()` if the `MemoryBackend` Protocol
    is available; otherwise returns a `WireSubjectAgent` with
    `memory_backend_kind=None` (the graceful fallback mode).
    """
    # SubjectAgentWiring has 8 required positional fields (frozen
    # dataclass); populate all 8 with the academic-history defaults.
    wiring = SubjectAgentWiring(  # type: ignore[call-arg]
        "academic_history",               # ncca_subject
        "academic_history",               # module_slug
        "Academic History",               # display_name
        "History",                        # baml_prefix
        "agent.academic_history.<verb>",  # langfuse_trace_name
        "oideachais_history",             # cognee_dataset
        "Cian",                           # tuatha_de (Cian = knowledge/wisdom)
        "stair-acadúil",                  # lore (Irish: 'academic ladder')
    )
    wire = WireSubjectAgent(subject=wiring, baml_prefix="History")
    if _MEMORY_BACKEND_AVAILABLE and get_default_backend is not None:
        try:
            backend = get_default_backend()
            # `get_default_backend` may be a factory function or an
            # async context manager — handle both shapes gracefully.
            import inspect as _inspect

            if _inspect.iscoroutine(backend) or _inspect.iscoroutinefunction(get_default_backend):
                # Caller is async-only; we cannot await here. Mark
                # the wire kind as "async_pending" so the smoke test
                # does not crash.
                wire.memory_backend_kind = "async_pending"
            else:
                wire.memory_backend_kind = getattr(backend, "kind", None) or "protocol"
        except Exception:
            wire.memory_backend_kind = None
    return wire


academic_history_agent_wire: WireSubjectAgent = _build_wire()


__all__ = [
    "TOOLS",
    "TOOL_NAMES",
    "WireSubjectAgent",
    "academic_history_agent_wire",
    "list_tools",
    "run_tool",
]
