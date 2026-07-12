"""Regression test: the legacy `oideachais.data_platform.*` namespace
must not appear anywhere in the oideachais source tree.

Commit 8484a6353 (the "v2 monorepo layout" cleanup) removed the
`oideachais/data_platform/` directory in favour of the flat post-
cleanup layout. Any lingering `from cianfhoghlaim.X
import Y` is a broken import.

This test walks the entire `oideachais/{dagster_defs,dlt_sources,
dlt_utils,api,observability,...}/` tree and asserts no Python file
contains the banned namespace in a real import.

Docstrings (which mention the legacy path for historical context)
are stripped before scanning so they don't false-positive.
"""
from __future__ import annotations

import ast
from pathlib import Path

BANNED = "oideachais.data_platform"

# Tree roots we own. Excludes `__pycache__`, `tests/`, `.venv/`.
SCAN_ROOTS = [
    "dagster_defs",
    "dlt_sources",
    "dlt_utils",
    "api",
    "observability",
    "cognee_integration",
    "site_analysis",
    "agents",
    "baml_src",
    "cocoindex_flows",
    "core",
    "dagster_assets",
    "config",
]


def _real_imports(py: Path) -> list[tuple[int, str]]:
    """Return (lineno, full_dotted_name) for every real import in `py`.

    Strips:
      - module-level and function-level __future__ imports
      - TYPE_CHECKING blocks
      - try/except ImportError guards
      - docstring contents
    """
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []

    out: list[tuple[int, str]] = []

    class V(ast.NodeVisitor):
        def __init__(self) -> None:
            self.skip = 0
            self.in_type_checking = False

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                if self.skip == 0:
                    out.append((node.lineno, alias.name))

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if self.skip > 0 or self.in_type_checking:
                return
            mod = node.module or ""
            if mod.startswith(BANNED):
                out.append((node.lineno, mod))

        def visit_Try(self, node: ast.Try) -> None:
            # Don't penalise guards: imports inside try/except
            # are usually best-effort.
            for handler in node.handlers:
                self.skip += 1
                self.visit(handler)
                self.skip -= 1
            self.generic_visit(node)

    V().visit(tree)
    return out


def test_no_legacy_data_platform_imports() -> None:
    """No real import may reference `oideachais.data_platform.*`."""
    pkg_root = Path(__file__).resolve().parents[2]
    bad: list[tuple[Path, int, str]] = []
    for sub in SCAN_ROOTS:
        root = pkg_root / sub
        if not root.is_dir():
            continue
        for py in root.rglob("*.py"):
            if "__pycache__" in py.parts:
                continue
            for lineno, mod in _real_imports(py):
                if mod == BANNED or mod.startswith(BANNED + "."):
                    bad.append((py, lineno, mod))
    assert not bad, (
        f"Found {len(bad)} legacy `oideachais.data_platform` imports:\n"
        + "\n".join(f"  {p.relative_to(pkg_root)}:{l}  {m!r}" for p, l, m in bad[:10])
    )
