"""cianfhoghlaim.cocoindex — CocoIndex v1 App canonical home (post-v4 + post-Phase-1 2026-06-30).

This package hosts the CocoIndex v1 Apps (per `cianfhoghlaim-cocoindex-v1` skill).
The dynamic `V1_APPS` tuple is built via AST discovery of all
`coco.App(...)` and `*_app = coco.App(...)` instances across the
package — see `_discover_v1_apps()` below.

Per `cianfhoghlaim-cocoindex-v1` skill REFACTORING.md item 12:
- `cocoindex/_shared/_lifespan.py` is the canonical home for the
  shared `@coco.lifespan` + 3 ContextKeys (LANCE_DB, EMBEDDER,
  RESOLVED_FILE_REGISTRY).
- Every v1 App imports from `.._shared._lifespan` instead of re-declaring.

CLI entry-point: `uv run cianfhoghlaim-cocoindex --help`
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

__all__ = [
    # Shared lifespan
    "LANCE_DB",
    "EMBEDDER",
    "RESOLVED_FILE_REGISTRY",
    "lifespan",
    "RESOLVED_REGISTRY",
    "V1_APPS",
]


def _discover_v1_apps() -> tuple[str, ...]:
    """Walk every `.py` under `cocoindex/` and collect names assigned
    to `coco.App(...)` calls (module-scope only).

    Recognised shapes (the BIEP v3 fan-out produces both):
      - `app = coco.App(coco.AppConfig(...))`
      - `<name>_app = coco.App(coco.AppConfig(...))`
      - `<name>_embedding = coco.App(coco.AppConfig(...))`
      - `<jurisdiction>_<stage>_<topic>_apps = {"key": coco.App(...), ...}`
        (factory dicts are walked for the key names)

    Returns:
        Sorted unique tuple of all discovered App names.
    """
    cocoindex_root = Path(__file__).parent
    discovered: set[str] = set()

    SKIP_FILES = {
        "__init__.py",
        # The R1-R4 linter + CLI + shared infra are not Apps
        "_lifespan.py",
        "caighdean_standardize.py",
        "languages.py",
        "reranker.py",
        "repo_embedding.py",
        "repo_type_detector.py",
        "cocoindex_v1_conformance.py",
    }

    for path in cocoindex_root.rglob("*.py"):
        if path.name in SKIP_FILES:
            continue
        if "__pycache__" in str(path):
            continue
        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Detect `x = coco.App(...)` and `x = {"k": coco.App(...)}`
                if isinstance(node.value, ast.Call):
                    func_name = _called_func_name(node.value)
                    if func_name in ("coco.App", "coco.cocoindex.App"):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                discovered.add(target.id)
                # Detect dict literals containing coco.App(...) values
                if isinstance(node.value, ast.Dict):
                    for v in node.value.values:
                        if isinstance(v, ast.Call):
                            if _called_func_name(v) in ("coco.App", "coco.cocoindex.App"):
                                for target in node.targets:
                                    if isinstance(target, ast.Name):
                                        discovered.add(target.id)

    return tuple(sorted(discovered))


def _called_func_name(call: ast.Call) -> str | None:
    """Resolve a Call node's function name (e.g. `coco.App` → 'coco.App')."""
    func = call.func
    parts: list[str] = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
        return ".".join(reversed(parts))
    return None


def __getattr__(name: str) -> object:
    """Lazy attribute access — defer cocoindex imports until needed."""
    if name in {"LANCE_DB", "EMBEDDER", "RESOLVED_FILE_REGISTRY", "lifespan", "RESOLVED_REGISTRY"}:
        from ._shared import _lifespan

        return getattr(_lifespan, name)
    if name == "V1_APPS":
        # Dynamic discovery via AST — the canonical single source of truth
        # for "how many v1 Apps are there?" was previously a 14-name
        # hard-coded tuple (now stale). The AST walker catches all
        # `coco.App(...)` instances + factory dicts.
        return _discover_v1_apps()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")