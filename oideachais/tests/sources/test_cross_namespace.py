"""
Cross-namespace guard.

The AGENTS.md zero-absolute-namespaces rule: code inside the
`oideachais/` package MUST NOT import `oideachais.data_platform.*` or
`oideachais.middleware.*`. Two narrow exceptions exist for the legacy
compatibility shims at `oideachais/oideachais/__init__.py` and
`oideachais/oideachais/data_platform/__init__.py` (which exist
precisely to keep the old namespace importable for external callers
during the transition period).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

# The whole oideachais/ package tree (excluding the legacy compat shim).
PACKAGE_ROOT = Path("oideachais")
# These two files are the *only* legitimate users of the old namespace:
# they exist to keep `import oideachais.data_platform` working for
# downstream code that hasn't migrated yet.
LEGACY_COMPAT_FILES = {
    Path("oideachais/oideachais/__init__.py"),
    Path("oideachais/oideachais/data_platform/__init__.py"),
}
# Every other `.py` file in the package must not import the old namespace.
FORBIDDEN_PREFIXES = ("oideachais.data_platform", "oideachais.middleware")

EXCLUDE_DIR_PARTS = {
    ".venv", "__pycache__", ".git", "stedding", ".cocoindex_code",
    "instagram_output", "dlthub", "node_modules", "docs",
    ".pytest_cache", ".ruff_cache", "site",
}


def _walk_python_files(root: Path):
    for p in root.rglob("*.py"):
        if any(part in EXCLUDE_DIR_PARTS for part in p.parts):
            continue
        if p in LEGACY_COMPAT_FILES:
            continue
        yield p


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
    if not PACKAGE_ROOT.is_dir():
        pytest.skip(f"{PACKAGE_ROOT} not present")
    offenders: list[tuple[Path, int, str]] = []
    for p in _walk_python_files(PACKAGE_ROOT):
        for lineno, name in _imports_of(p):
            for prefix in FORBIDDEN_PREFIXES:
                if name.startswith(prefix):
                    offenders.append((p, lineno, name))
                    break
    assert not offenders, (
        "Found absolute-namespace imports (forbidden by AGENTS.md "
        "zero-absolute-namespaces rule):\n"
        + "\n".join(f"  {p}:{lineno}  {name}" for p, lineno, name in offenders)
    )
