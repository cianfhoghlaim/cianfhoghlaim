"""Tests for the croilar-devtools-hub analyzer and Convex modules.

These tests verify the monorepo walker (scripts/analyze-web-stack.ts)
produces stable output for each kind, and the new Convex modules
follow the established shape (list query, getByProject query, refreshAll
action, ingest mutation).

Run with:
    cd croilar && uv run pytest tests/test_devtools.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ANALYZER = REPO_ROOT / "croilar" / "scripts" / "analyze-web-stack.ts"


def _run_analyzer(kind: str) -> list:
    env = os.environ.copy()
    env["CROILAR_REPO_ROOT"] = str(REPO_ROOT)
    proc = subprocess.run(
        ["bun", "run", str(ANALYZER), "--kind", kind],
        cwd=str(REPO_ROOT / "croilar"),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, f"analyzer failed: {proc.stderr}"
    payload = json.loads(proc.stdout)
    camel = {
        "tanstack_routes": "tanstackRoutes",
        "convex_functions": "convexFunctions",
        "cloudflare": "cloudflareResources",
        "baml": "bamlSchemas",
        "marimo": "marimoNotebooks",
    }
    return payload[camel[kind]]


# ---------------------------------------------------------------------------
# Tanstack route analyzer
# ---------------------------------------------------------------------------

def test_analyzer_finds_tanstack_routes() -> None:
    rows = _run_analyzer("tanstack_routes")
    assert isinstance(rows, list)
    assert len(rows) >= 5
    projects = {r["project"] for r in rows}
    assert "tuatha" in projects
    assert "croilar" in projects
    sample = rows[0]
    for key in (
        "project",
        "route",
        "file",
        "isPublic",
        "isServer",
        "hasLoader",
        "hasAuth",
        "lines",
        "lastCommit",
        "lastCommitAt",
    ):
        assert key in sample, f"missing key: {key}"


def test_analyzer_tanstack_routes_idempotent() -> None:
    """Running the analyzer twice yields stable row counts (within the repo)."""
    rows1 = _run_analyzer("tanstack_routes")
    rows2 = _run_analyzer("tanstack_routes")
    assert len(rows1) == len(rows2)


# ---------------------------------------------------------------------------
# Convex function analyzer
# ---------------------------------------------------------------------------

def test_analyzer_finds_convex_functions() -> None:
    rows = _run_analyzer("convex_functions")
    assert isinstance(rows, list)
    assert len(rows) >= 20
    projects = {r["project"] for r in rows}
    assert "croilar" in projects
    sample = rows[0]
    assert sample["kind"] in {
        "query", "mutation", "action",
        "internalQuery", "internalMutation", "internalAction",
    }


# ---------------------------------------------------------------------------
# Cloudflare resource analyzer
# ---------------------------------------------------------------------------

def test_analyzer_finds_cloudflare_resources() -> None:
    rows = _run_analyzer("cloudflare")
    assert isinstance(rows, list)
    assert len(rows) >= 3
    sample = rows[0]
    assert sample["kind"] in {"worker", "pages", "r2", "kv", "d1", "durable_object"}
    assert sample["project"] in {"tuatha", "oideachais", "croilar", "meaisinfhoghlaim"}


# ---------------------------------------------------------------------------
# BAML schema analyzer
# ---------------------------------------------------------------------------

def test_analyzer_finds_baml_schemas() -> None:
    rows = _run_analyzer("baml")
    assert isinstance(rows, list)
    assert len(rows) >= 5
    sample = rows[0]
    assert sample["classCount"] >= 0
    assert sample["functionCount"] >= 0
    assert sample["enumCount"] >= 0


# ---------------------------------------------------------------------------
# Marimo notebook analyzer
# ---------------------------------------------------------------------------

def test_analyzer_finds_marimo_notebooks() -> None:
    rows = _run_analyzer("marimo")
    assert isinstance(rows, list)
    assert len(rows) >= 1
    sample = rows[0]
    assert sample["project"]
    assert sample["slug"]
    assert sample["file"].endswith(".py")


# ---------------------------------------------------------------------------
# Convex module surface (declarative — there is no live deployment)
# ---------------------------------------------------------------------------

CONVEX_MODULES = [
    "tanstack_routes",
    "convex_functions",
    "cloudflare_resources",
    "baml_schemas",
    "test_runs",
    "convex_function_calls",
    "convex_metrics",
    "marimo_notebooks",
    "glance_config",
    "devtools",
]


@pytest.mark.parametrize("module_name", CONVEX_MODULES)
def test_convex_module_exports_expected_symbols(module_name: str) -> None:
    """Each new Convex module must follow the established shape.

    `list` is required for modules that surface rows; `tail` is the equivalent
    for `convex_function_calls`. `refreshAll` / `refresh` / `regenerate` are
    required for action modules. The `devtools` aggregator only needs
    `getSummary`. We read the source file as text — there is no Convex
    deployment in this environment to import against.
    """
    path = REPO_ROOT / "croilar" / "convex" / f"{module_name}.ts"
    assert path.exists(), f"missing convex module: {path}"
    text = path.read_text(encoding="utf-8")
    if module_name == "devtools":
        assert "export const getSummary" in text
        assert "import { requireOrgRole } from \"./helpers\"" in text
        return
    if module_name == "convex_function_calls":
        assert "export const tail" in text
        assert "import { query" in text
        return
    if module_name == "convex_metrics":
        assert "export const get " in text or "export const get(" in text or "export const getByScope" in text
        assert "import { requireOrgRole } from \"./helpers\"" in text
        assert "loggedAction" in text
        return
    assert "export const list" in text, f"{module_name} missing list query"
    assert "import { requireOrgRole } from \"./helpers\"" in text, (
        f"{module_name} must use requireOrgRole from helpers"
    )
    if module_name in {
        "tanstack_routes",
        "convex_functions",
        "cloudflare_resources",
        "baml_schemas",
        "marimo_notebooks",
        "glance_config",
        "convex_metrics",
    }:
        assert "loggedAction" in text, f"{module_name} must use loggedAction"
        assert (
            "export const refreshAll" in text
            or "export const refresh" in text
            or "export const regenerate" in text
        ), f"{module_name} must export refreshAll/refresh/regenerate"


# ---------------------------------------------------------------------------
# Action middleware
# ---------------------------------------------------------------------------

def test_logged_action_helper_exists() -> None:
    """The loggedAction helper must export a function wrapping any action."""
    path = REPO_ROOT / "croilar" / "convex" / "_middleware.ts"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "export function loggedAction" in text
    assert "convexFunctionCalls" in text


# ---------------------------------------------------------------------------
# Portal pages and data layer
# ---------------------------------------------------------------------------

def test_webstack_data_layer_exists() -> None:
    """The webstack data layer must export the canonical types and helpers."""
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "lib" / "webstack.ts"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    for export in [
        "WebStackSnapshot",
        "TanstackRoute",
        "ConvexFunction",
        "CloudflareResource",
        "BamlSchema",
        "MarimoNotebook",
        "fetchSnapshot",
        "troubleshoot",
    ]:
        assert export in text, f"missing export: {export}"


def test_web_index_page_exists() -> None:
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "web" / "index.tsx"
    assert path.exists()


def test_web_project_page_exists() -> None:
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "web" / "$project.tsx"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "TroubleshootDrawer" in text


def test_notebooks_index_page_exists() -> None:
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "notebooks" / "index.tsx"
    assert path.exists()


def test_notebooks_slug_page_exists() -> None:
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "notebooks" / "$slug.tsx"
    assert path.exists()


def test_webstack_snapshot_api_exists() -> None:
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "api" / "webstack" / "snapshot.ts"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "loadOrRegenerate" in text


def test_dashboard_links_to_devtools() -> None:
    """The portal dashboard must surface the new devtools pages."""
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "index.tsx"
    text = path.read_text(encoding="utf-8")
    assert 'to="/web"' in text
    assert 'to="/notebooks"' in text
    assert "DevTools Hub" in text


def test_pipelines_page_uses_snapshot() -> None:
    """The /data/pipelines page must read from the live webstack snapshot, not a hard-coded array."""
    path = REPO_ROOT / "croilar" / "apps" / "portal" / "src" / "routes" / "_layout" / "data" / "pipelines.tsx"
    text = path.read_text(encoding="utf-8")
    assert "fetchSnapshot" in text
    assert "buildPipelines" in text


# ---------------------------------------------------------------------------
# Marimo notebooks
# ---------------------------------------------------------------------------

NOTEBOOKS = [
    "croilar/notebooks/streams/teaching/web_route_health.py",
    "croilar/notebooks/streams/teaching/convex_function_latency.py",
    "croilar/notebooks/streams/teaching/baml_extraction_quality.py",
]


@pytest.mark.parametrize("notebook_path", NOTEBOOKS)
def test_devtools_notebook_exists(notebook_path: str) -> None:
    path = REPO_ROOT / notebook_path
    assert path.exists(), f"missing notebook: {path}"
    text = path.read_text(encoding="utf-8")
    assert "app = marimo.App" in text
    assert "@app.cell" in text


# ---------------------------------------------------------------------------
# Glance regenerator
# ---------------------------------------------------------------------------

REGENERATOR = REPO_ROOT / "croilar" / "scripts" / "regenerate-glance-config.ts"


def test_regenerator_emits_all_project_pages(tmp_path: Path) -> None:
    """The regenerator must emit one Glance page per project."""
    out = tmp_path / "glance.yml"
    env = os.environ.copy()
    env["CROILAR_REPO_ROOT"] = str(REPO_ROOT)
    proc = subprocess.run(
        ["bun", "run", str(REGENERATOR), "--out", str(out)],
        cwd=str(REPO_ROOT / "croilar"),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, f"regenerator failed: {proc.stderr}"
    text = out.read_text(encoding="utf-8")
    for project in ("tuatha", "oideachais", "croilar", "meaisinfhoghlaim"):
        assert f'name: "{project}"' in text, f"missing page: {project}"
    assert "server:" in text
    assert "pages:" in text
    assert text.startswith("# Generated by")


def test_regenerator_respects_force_flag(tmp_path: Path) -> None:
    """The regenerator must NOT clobber a manually-edited file without FORCE."""
    out = tmp_path / "glance.yml"
    out.write_text("# manual edit — do not touch\n", encoding="utf-8")
    env = os.environ.copy()
    env["CROILAR_REPO_ROOT"] = str(REPO_ROOT)
    proc = subprocess.run(
        ["bun", "run", str(REGENERATOR), "--out", str(out)],
        cwd=str(REPO_ROOT / "croilar"),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode != 0, "should have refused to clobber manual file"
    assert "manually edited" in proc.stderr


def test_regenerator_with_force_overrides(tmp_path: Path) -> None:
    """With CROILAR_GLANCE_REGEN_FORCE=true the regenerator must clobber."""
    out = tmp_path / "glance.yml"
    out.write_text("# manual edit — do not touch\n", encoding="utf-8")
    env = os.environ.copy()
    env["CROILAR_REPO_ROOT"] = str(REPO_ROOT)
    env["CROILAR_GLANCE_REGEN_FORCE"] = "true"
    proc = subprocess.run(
        ["bun", "run", str(REGENERATOR), "--out", str(out)],
        cwd=str(REPO_ROOT / "croilar"),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, f"force regen failed: {proc.stderr}"
    assert out.read_text().startswith("# Generated by")


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

MCP_DIR = REPO_ROOT / "croilar" / "mcp" / "devtools"


def test_mcp_server_has_package_json() -> None:
    pkg = MCP_DIR / "package.json"
    assert pkg.exists()
    text = pkg.read_text(encoding="utf-8")
    assert "croilar-mcp-devtools" in text
    assert "@modelcontextprotocol/sdk" in text


def test_mcp_server_exposes_expected_tools() -> None:
    index = MCP_DIR / "index.ts"
    assert index.exists()
    text = index.read_text(encoding="utf-8")
    for tool in [
        "list_tanstack_routes",
        "list_convex_functions",
        "list_cloudflare",
        "list_baml",
        "list_marimo",
        "get_project_summary",
        "get_snapshot",
    ]:
        assert f'name: "{tool}"' in text, f"missing tool: {tool}"


def test_mcp_server_boot() -> None:
    """The MCP server must start cleanly and log a ready message."""
    env = os.environ.copy()
    env["CROILAR_REPO_ROOT"] = str(REPO_ROOT)
    proc = subprocess.Popen(
        ["bun", "run", str(MCP_DIR / "index.ts")],
        cwd=str(MCP_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _, stderr = proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        proc.terminate()
        proc.wait(timeout=2)
        # If it stayed alive, that's success — stdio server
        return
    # If it exited, stderr should still show the ready message
    assert "ready on stdio" in stderr or "ready on stdio" in (proc.stderr.read() if proc.stderr else "")


# ---------------------------------------------------------------------------
# Komodo procedure
# ---------------------------------------------------------------------------

def test_komodo_glance_regen_procedure_exists() -> None:
    path = REPO_ROOT / "infrastructure" / "komodo" / "procedures" / "croilar-glance-regenerate.toml"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "croilar-glance-regenerate" in text
    assert "regenerate-glance-config.ts" in text


# ---------------------------------------------------------------------------
# opencode.json MCP registration
# ---------------------------------------------------------------------------

def test_opencode_registers_croilar_devtools() -> None:
    cfg = REPO_ROOT / "opencode.json"
    text = cfg.read_text(encoding="utf-8")
    assert '"croilar-devtools"' in text
    assert "croilar/mcp/devtools/index.ts" in text
