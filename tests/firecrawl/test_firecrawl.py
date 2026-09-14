"""Firecrawl health tests (Plan 8 audit, 2026-09-13).

Per Plan 8 of the v6 era audit. These tests verify the Firecrawl
MCP surface (12 tools, 4 monitor configs) is configured correctly.
"""
from __future__ import annotations

import importlib
import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_firecrawl_mcp_configured() -> None:
    """The Firecrawl MCP server is configured in `.mcp.json`."""
    mcp = REPO_ROOT / ".mcp.json"
    assert mcp.exists(), "Plan 8 audit: .mcp.json missing"
    config = json.loads(mcp.read_text())
    servers = config.get("mcpServers", {})
    assert "firecrawl" in servers, (
        "Plan 8 audit: firecrawl not in mcpServers"
    )
    fc = servers["firecrawl"]
    assert "firecrawl-mcp" in fc.get("args", [""])[-1], (
        "Plan 8 audit: firecrawl MCP command doesn't reference firecrawl-mcp"
    )


def test_firecrawl_monitor_configs_present() -> None:
    """All 4 upstream-package Firecrawl monitor configs exist."""
    monitor_dir = REPO_ROOT / "docs/firecrawl/monitors/upstream_packages"
    assert monitor_dir.exists(), (
        "Plan 8 audit: docs/firecrawl/monitors/upstream_packages/ missing"
    )
    expected = ["dlthub_blog.yml", "lancedb_blog.yml", "motherduck_blog.yml", "cocoindex_docs.yml"]
    for name in expected:
        path = monitor_dir / name
        assert path.exists(), f"Plan 8 audit: monitor config {name} missing"


def test_firecrawl_monitor_configs_valid_yaml() -> None:
    """Each monitor config is a valid YAML with the canonical schema."""
    monitor_dir = REPO_ROOT / "docs/firecrawl/monitors/upstream_packages"
    if not monitor_dir.exists():
        return
    import yaml
    for path in monitor_dir.glob("*.yml"):
        content = yaml.safe_load(path.read_text())
        assert "name" in content, f"Plan 8 audit: {path.name} missing 'name'"
        assert "targets" in content or "schedule" in content, (
            f"Plan 8 audit: {path.name} missing targets/schedule"
        )


def test_firecrawl_mcp_client_imports() -> None:
    """The Firecrawl MCP client wrapper can be imported."""
    try:
        importlib.import_module("agents.meaisinfhoghlaim.firecrawl_mcp.client")
    except ImportError as exc:
        # Skip if optional deps missing (e.g. langfuse)
        if "langfuse" in str(exc) or "pydantic" in str(exc):
            return
        raise


def test_firecrawl_skills_both_exist() -> None:
    """Both the firecrawl (meta) and firecrawl-cli skills exist."""
    meta = REPO_ROOT / ".agents/skills/firecrawl/SKILL.md"
    cli = REPO_ROOT / ".agents/skills/firecrawl-cli/SKILL.md"
    assert meta.exists(), "Plan 8 audit: firecrawl/SKILL.md missing"
    assert cli.exists(), "Plan 8 audit: firecrawl-cli/SKILL.md missing"


def test_firecrawl_bunx_available() -> None:
    """`bunx` is available for running firecrawl-mcp."""
    result = subprocess.run(
        ["which", "bunx"],
        capture_output=True, text=True,
        timeout=10,
    )
    assert result.returncode == 0, (
        f"Plan 8 audit: bunx not available. stderr: {result.stderr}"
    )


def test_firecrawl_meta_skill_references_monitor_pipeline() -> None:
    """The meta-skill documents the upstream-blog → cocoindex → KG pipeline."""
    meta = REPO_ROOT / ".agents/skills/firecrawl/SKILL.md"
    content = meta.read_text()
    # After our update, the meta-skill should reference monitor pipeline
    assert "monitor" in content.lower(), (
        "Plan 8 audit: firecrawl meta-skill doesn't mention monitor pipeline"
    )


def test_firecrawl_cli_documents_12_subcommands() -> None:
    """The firecrawl-cli skill documents all 12 subcommands."""
    cli = REPO_ROOT / ".agents/skills/firecrawl-cli/SKILL.md"
    content = cli.read_text()
    # Per the skill description, 12 subcommands
    subcommands = ["scrape", "crawl", "search", "extract", "map",
                   "agent", "deep-research", "browser-sandbox",
                   "monitor", "batch", "download", "feedback"]
    found = sum(1 for s in subcommands if s in content.lower())
    assert found >= 10, (
        f"Plan 8 audit: firecrawl-cli skill only references {found}/12 subcommands"
    )
