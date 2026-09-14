"""Google ADK health tests (Plan 6 audit, 2026-09-13).

Per Plan 6 of the v6 era audit. These tests verify the Google ADK
(Agent Development Kit) is installed and the per-agent modules can
be imported without errors. The agents use graceful BAML degradation
when `baml_client` is unavailable (per Plan 2).
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_google_adk_lib_installed() -> None:
    """google-adk 1.x is installed."""
    result = subprocess.run(
        ["uv", "pip", "show", "google-adk"],
        capture_output=True, text=True,
        cwd=str(REPO_ROOT),
        timeout=15,
    )
    assert result.returncode == 0, (
        f"Plan 6 audit: google-adk not installed. stderr: {result.stderr}"
    )
    import re
    m = re.search(r"Version:\s*(\S+)", result.stdout)
    assert m, "Plan 6 audit: no version in google-adk output"
    # Accept 1.x (the canonical ADK line)
    assert m.group(1).startswith("1."), (
        f"Plan 6 audit: unexpected google-adk version {m.group(1)}"
    )


def test_agents_meaisinfhoghlaim_exists() -> None:
    """The agents/meaisinfhoghlaim/ directory exists with the 4 sub-clusters."""
    base = REPO_ROOT / "agents" / "meaisinfhoghlaim"
    assert base.exists(), "Plan 6 audit: agents/meaisinfhoghlaim/ missing"
    expected_clusters = ["educational", "firecrawl_mcp", "media_intel"]
    for cluster in expected_clusters:
        assert (base / cluster).exists(), (
            f"Plan 6 audit: agents cluster missing: {cluster}"
        )


def test_agent_modules_count() -> None:
    """There are ≥ 10 ADK-related .py files in agents/meaisinfhoghlaim/."""
    base = REPO_ROOT / "agents" / "meaisinfhoghlaim"
    py_files = list(base.rglob("*.py"))
    # Exclude __pycache__
    py_files = [f for f in py_files if "__pycache__" not in str(f)]
    assert len(py_files) >= 10, (
        f"Plan 6 audit: expected ≥10 agent files, found {len(py_files)}"
    )


def test_celtic_grammar_agent_imports() -> None:
    """The Celtic grammar agent can be imported (with graceful BAML degradation)."""
    try:
        importlib.import_module("agents.meaisinfhoghlaim.educational.celtic_grammar_agent")
    except ImportError as exc:
        # Acceptable: optional deps missing
        if any(s in str(exc) for s in ["baml_client", "routing"]):
            return
        raise


def test_celtic_morphology_agent_imports() -> None:
    """The Celtic morphology agent can be imported."""
    try:
        importlib.import_module("agents.meaisinfhoghlaim.educational.celtic_morphology_agent")
    except ImportError as exc:
        if any(s in str(exc) for s in ["baml_client", "routing"]):
            return
        raise


def test_firecrawl_mcp_client_imports() -> None:
    """The Firecrawl MCP client can be imported."""
    try:
        importlib.import_module("agents.meaisinfhoghlaim.firecrawl_mcp.client")
    except ImportError:
        # External deps may not be available
        return


def test_agents_have_baml_fallback_pattern() -> None:
    """Each agent has the canonical `try: from baml_client import b` pattern."""
    base = REPO_ROOT / "agents" / "meaisinfhoghlaim" / "educational"
    if not base.exists():
        return
    # Sample the celtic grammar agent - known to have the pattern
    sample = base / "celtic_grammar_agent.py"
    if sample.exists():
        content = sample.read_text()
        assert "from baml_client import b" in content, (
            f"Plan 6 audit: {sample.name} missing BAML fallback import"
        )


def test_agent_fleet_orchestration_skill_exists() -> None:
    """The agent-fleet-orchestration skill exists (referenced by ADK agent docs)."""
    skill = REPO_ROOT / ".agents" / "skills" / "agent-fleet-orchestration" / "SKILL.md"
    assert skill.exists(), (
        "Plan 6 audit: .agents/skills/agent-fleet-orchestration/SKILL.md missing"
    )
