"""
Cross-namespace guard.

The AGENTS.md zero-absolute-namespaces rule: DLT sources inside
`oideachais/dlt_sources/` MUST NOT import `oideachais.data_platform.*`.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

DLT_SOURCES_ROOT = Path("oideachais/dlt_sources")
FORBIDDEN_PREFIX = "oideachais.data_platform"


def _walk_python_files(root: Path):
    yield from root.rglob("*.py")


def _imports_of(path: Path) -> list[tuple[int, str]]:
    src = path.read_text(encoding="utf-8", errors="ignore")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                out.append((node.lineno, n.name))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            out.append((node.lineno, mod))
    return out


def test_no_absolute_oideachais_data_platform_imports() -> None:
    if not DLT_SOURCES_ROOT.is_dir():
        pytest.skip(f"{DLT_SOURCES_ROOT} not present")
    offenders: list[tuple[Path, int, str]] = []
    for p in _walk_python_files(DLT_SOURCES_ROOT):
        for lineno, name in _imports_of(p):
            if name.startswith(FORBIDDEN_PREFIX):
                offenders.append((p, lineno, name))
    assert not offenders, (
        "Found absolute-namespace imports (forbidden by AGENTS.md):\n"
        + "\n".join(f"  {p}:{lineno}  {name}" for p, lineno, name in offenders)
    )
