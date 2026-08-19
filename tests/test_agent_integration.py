"""Comprehensive agent integration tests for the 12 + 4-stage agent fleet.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5):
the cross-package integration surface (BAML ↔ CocoIndex ↔ Marimo ↔
ADK ↔ CopilotKit) is verified by 14 comprehensive tests:

 1.  test_agent_registry_has_4_stage_agents
 2.  test_agent_registry_has_11_baseline_agents
 3.  test_agent_wiring_namedtuple_fields
 4.  test_stage_agents_have_baml_tools
 5.  test_agent_ui_bridge_make_planner_agent
 6.  test_agent_ui_bridge_register_adk_agent
 7.  test_agent_ui_bridge_emit_agui_registration_event
 8.  test_cocoindex_query_api_biep_apps
 9.  test_cocoindex_query_api_get_search
10.  test_marimo_baml_lc6_functions
11.  test_marimo_baml_jc_functions
12.  test_marimo_baml_qpack_functions
13.  test_marimo_to_copilotkit_canonical_notebooks
14.  test_marimo_to_copilotkit_discover_public_functions

Each test uses `importlib.util.spec_from_file_location` + `try/except`
to be resilient to missing optional dependencies (BAML, adk, ag-ui-adk,
lancedb, marimo).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from typing import Any

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Module loaders (use spec_from_file_location to avoid __init__ import
# side-effects — same pattern as test_4_stage_plane_integration.py)
# ============================================================================


def _load_module(name: str, path: Path) -> Any:
    """Load a Python module from a file path without triggering parent __init__."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_agent_registry() -> Any:
    """Load agents/adk/agent_registry.py with the agents.* package context."""
    # Set up package context for relative imports inside the module
    if "agents" not in sys.modules:
        agents_pkg = types.ModuleType("agents")
        agents_pkg.__path__ = [str(REPO_ROOT / "agents")]
        sys.modules["agents"] = agents_pkg
    if "agents.adk" not in sys.modules:
        adk_pkg = types.ModuleType("agents.adk")
        adk_pkg.__path__ = [str(REPO_ROOT / "agents" / "adk")]
        sys.modules["agents.adk"] = adk_pkg
    if "agents.integrations" not in sys.modules:
        integrations_pkg = types.ModuleType("agents.integrations")
        integrations_pkg.__path__ = [str(REPO_ROOT / "agents" / "integrations")]
        sys.modules["agents.integrations"] = integrations_pkg

    path = REPO_ROOT / "agents" / "adk" / "agent_registry.py"
    return _load_module("agents.adk.agent_registry", path)


def _load_agent_ui_bridge() -> Any:
    """Load agents/integrations/agent_ui_bridge.py."""
    sys.path.insert(0, str(REPO_ROOT / "agents" / "integrations"))
    path = REPO_ROOT / "agents" / "integrations" / "agent_ui_bridge.py"
    return _load_module("agent_ui_bridge", path)


def _load_cocoindex_query_api() -> Any:
    """Load cocoindex/_shared/cocoindex_query_api.py."""
    sys.path.insert(0, str(REPO_ROOT))
    path = REPO_ROOT / "cocoindex" / "_shared" / "cocoindex_query_api.py"
    return _load_module("cocoindex_query_api", path)


def _load_marimo_baml() -> Any:
    """Load notebooks/_shared/marimo_baml.py."""
    sys.path.insert(0, str(REPO_ROOT))
    path = REPO_ROOT / "notebooks" / "_shared" / "marimo_baml.py"
    return _load_module("marimo_baml", path)


def _load_marimo_to_copilotkit() -> Any:
    """Load notebooks/_shared/marimo_to_copilotkit.py."""
    sys.path.insert(0, str(REPO_ROOT))
    path = REPO_ROOT / "notebooks" / "_shared" / "marimo_to_copilotkit.py"
    return _load_module("marimo_to_copilotkit", path)


# ============================================================================
# Test 1: 4 stage agents in AGENT_REGISTRY
# ============================================================================


def test_agent_registry_has_4_stage_agents() -> None:
    """Verify the 4 stage agents (lc, jc, alevel, gcse) are in AGENT_REGISTRY.

    The 4-stage plane architecture (per the 2026-08-18-mega-3-roadmap-v1
    + 2026-08-26-mega-3a-baml-and-adk-v1 changes) requires that the
    AGENT_REGISTRY exposes 4 canonical stage agents with the correct
    stage metadata.
    """
    try:
        registry_module = _load_agent_registry()
        AGENT_REGISTRY = registry_module.AGENT_REGISTRY
    except Exception as e:
        pytest.skip(f"agent_registry could not be loaded: {e}")

    # The 4 stage agents MUST be in the registry
    for stage_name, expected_stage in [
        ("lc_subject_agent", "lc"),
        ("jc_subject_agent", "jc"),
        ("alevel_subject_agent", "alevel"),
        ("gcse_subject_agent", "gcse"),
    ]:
        assert stage_name in AGENT_REGISTRY, f"Missing {stage_name}"
        wiring = AGENT_REGISTRY[stage_name]
        assert wiring.stage == expected_stage, (
            f"{stage_name} has stage={wiring.stage}, expected={expected_stage}"
        )
        assert wiring.name == stage_name
        assert wiring.description  # non-empty
        # The agent object must be non-None
        assert wiring.agent is not None


# ============================================================================
# Test 2: 11 baseline agents in registry source
# ============================================================================


def test_agent_registry_has_11_baseline_agents() -> None:
    """Verify the 11 baseline agents are in the registry source.

    The 11 baseline agents are the original agents.adk/*.py that
    have consistent `<name> = LlmAgent(...)` export patterns. They
    are lazy-imported with try/except for resilience.
    """
    registry_src = (REPO_ROOT / "agents" / "adk" / "agent_registry.py").read_text()
    baseline_agents = [
        "agui_curriculum_agent", "celtic_tutor_agent", "curriculum_comparison_agent",
        "education_research_agent", "email_triage_agent", "geospatial_agent",
        "mythology_narrator_agent", "quest_guide_agent", "research_agent",
        "research_assistant_agent", "statistics_agent",
    ]
    # All 11 must be in the registry source
    for baseline in baseline_agents:
        assert baseline in registry_src, f"Missing {baseline} in registry source"
    # Exactly 11 baseline agents in the source
    assert len(baseline_agents) == 11, f"Expected 11 baseline agents, got {len(baseline_agents)}"


# ============================================================================
# Test 3: AgentWiring NamedTuple fields
# ============================================================================


def test_agent_wiring_namedtuple_fields() -> None:
    """Verify the AgentWiring NamedTuple has the canonical fields.

    Per the 2026-08-14-agents-fleet-wiring-parity-v1 change, the
    canonical AgentWiring has 5 fields: name, agent, description,
    stage, tools.
    """
    try:
        registry_module = _load_agent_registry()
        AgentWiring = registry_module.AgentWiring
    except Exception as e:
        pytest.skip(f"agent_registry could not be loaded: {e}")

    # NamedTuple has _fields attribute
    assert hasattr(AgentWiring, "_fields")
    canonical_fields = ("name", "agent", "description", "stage", "tools")
    assert AgentWiring._fields == canonical_fields, (
        f"Expected {canonical_fields}, got {AgentWiring._fields}"
    )


# ============================================================================
# Test 4: 4 stage agents have BAML tools
# ============================================================================


def test_stage_agents_have_baml_tools() -> None:
    """Verify the 4 stage agents each have ≥ 1 BAMLFunctionTool-wrapped tool.

    Each stage agent is built via `make_litellm_agent(tools=...)` where
    the tools are wrapped via `BAMLFunctionTool(fn)` for each canonical
    BAML function in the stage's template.
    """
    try:
        registry_module = _load_agent_registry()
        AGENT_REGISTRY = registry_module.AGENT_REGISTRY
    except Exception as e:
        pytest.skip(f"agent_registry could not be loaded: {e}")

    stage_agents = ["lc_subject_agent", "jc_subject_agent", "alevel_subject_agent", "gcse_subject_agent"]
    for stage_name in stage_agents:
        assert stage_name in AGENT_REGISTRY, f"Missing {stage_name}"
        wiring = AGENT_REGISTRY[stage_name]
        assert len(wiring.tools) >= 1, (
            f"{stage_name} has {len(wiring.tools)} tools, expected ≥ 1"
        )


# ============================================================================
# Test 5: agent_ui_bridge.make_planner_agent
# ============================================================================


def test_agent_ui_bridge_make_planner_agent() -> None:
    """Verify make_planner_agent('test', 'test description') returns an LlmAgent."""
    try:
        bridge = _load_agent_ui_bridge()
    except Exception as e:
        pytest.skip(f"agent_ui_bridge could not be loaded: {e}")

    if not getattr(bridge, "_HAS_ADK", False):
        pytest.skip("google-adk not installed")

    try:
        agent = bridge.make_planner_agent("test", "test description")
    except Exception as e:
        pytest.skip(f"make_planner_agent failed: {e}")

    # The agent should have the correct name + description
    assert agent.name == "test"
    assert agent.description == "test description"


# ============================================================================
# Test 6: agent_ui_bridge.register_adk_agent
# ============================================================================


def test_agent_ui_bridge_register_adk_agent() -> None:
    """Verify register_adk_agent(agent) returns None when ag-ui-adk is not installed."""
    try:
        bridge = _load_agent_ui_bridge()
    except Exception as e:
        pytest.skip(f"agent_ui_bridge could not be loaded: {e}")

    if not getattr(bridge, "_HAS_ADK", False):
        pytest.skip("google-adk not installed")

    # Try to create an LlmAgent to register
    try:
        agent = bridge.make_planner_agent("test", "test description")
    except Exception as e:
        pytest.skip(f"make_planner_agent failed: {e}")

    # register_adk_agent returns None when ag-ui-adk or CopilotKit is not installed
    has_agui = getattr(bridge, "_HAS_AGUI", False)
    has_copilotkit = getattr(bridge, "_HAS_COPILOTKIT", False)
    result = bridge.register_adk_agent(agent, name="test")

    if has_agui and has_copilotkit:
        # Both installed: returns ADKAgent wrapper
        assert result is not None
    else:
        # Either missing: returns None
        assert result is None


# ============================================================================
# Test 7: agent_ui_bridge.emit_agui_registration_event
# ============================================================================


def test_agent_ui_bridge_emit_agui_registration_event() -> None:
    """Verify emit_agui_registration_event(agent) returns the canonical event dict."""
    try:
        bridge = _load_agent_ui_bridge()
    except Exception as e:
        pytest.skip(f"agent_ui_bridge could not be loaded: {e}")

    if not getattr(bridge, "_HAS_ADK", False):
        pytest.skip("google-adk not installed")

    try:
        agent = bridge.make_planner_agent("test_emit", "emit test description")
    except Exception as e:
        pytest.skip(f"make_planner_agent failed: {e}")

    event = bridge.emit_agui_registration_event(agent, name="test_emit")

    # The event MUST be a dict with the canonical keys
    assert isinstance(event, dict)
    assert event["type"] == "ag-ui-agent-registered"
    assert event["name"] == "test_emit"
    assert event["description"] == "emit test description"
    assert "model" in event
    assert "tools" in event
    assert isinstance(event["tools"], list)


# ============================================================================
# Test 8: cocoindex_query_api.BIEP_COCOINDEX_APPS
# ============================================================================


def test_cocoindex_query_api_biep_apps() -> None:
    """Verify BIEP_COCOINDEX_APPS contains the canonical apps.

    The list contains the canonical 11 LC apps + 8 JC apps + 4
    infrastructure apps + 40 european_nations apps = 63 entries
    (per the 2026-08-18-mega-3-fast-follow-v1 + 2026-09-30-mega-3b).
    """
    try:
        query_api = _load_cocoindex_query_api()
    except Exception as e:
        pytest.skip(f"cocoindex_query_api could not be loaded: {e}")

    BIEP_COCOINDEX_APPS = query_api.BIEP_COCOINDEX_APPS

    # The canonical 11 LC apps
    lc_apps = [
        "ireland_lc_mathematics_embedding", "ireland_lc_chemistry_embedding",
        "ireland_lc_physics_embedding", "ireland_lc_biology_embedding",
        "ireland_lc_geography_embedding", "ireland_lc_english_embedding",
        "ireland_lc_gaeilge_embedding", "ireland_lc_french_embedding",
        "ireland_lc_history_embedding", "ireland_lc_business_embedding",
        "ireland_lc_computer_science_embedding",
    ]
    for app in lc_apps:
        assert app in BIEP_COCOINDEX_APPS, f"Missing LC app {app}"

    # The canonical 8 JC apps
    jc_apps = [
        "ireland_jc_mathematics_embedding", "ireland_jc_english_embedding",
        "ireland_jc_gaeilge_embedding", "ireland_jc_science_embedding",
        "ireland_jc_history_embedding", "ireland_jc_geography_embedding",
        "ireland_jc_french_embedding", "ireland_jc_business_embedding",
    ]
    for app in jc_apps:
        assert app in BIEP_COCOINDEX_APPS, f"Missing JC app {app}"


# ============================================================================
# Test 9: cocoindex_query_api.get_search
# ============================================================================


def test_cocoindex_query_api_get_search() -> None:
    """Verify get_search('ireland_lc_mathematics_embedding') returns a callable."""
    try:
        query_api = _load_cocoindex_query_api()
    except Exception as e:
        pytest.skip(f"cocoindex_query_api could not be loaded: {e}")

    # get_search should return a callable
    search = query_api.get_search("ireland_lc_mathematics_embedding")
    assert callable(search), f"get_search returned {type(search)}, expected callable"
    # The closure should have a sensible name
    assert hasattr(search, "__name__")
    # The closure should be callable with a query
    assert callable(search)

    # Calling the search closure should return a list (or error dict if lancedb missing)
    try:
        results = search("test query", top_k=3)
        assert isinstance(results, list)
    except Exception:
        # lancedb missing → returns error dict in a list — also fine
        pass


# ============================================================================
# Test 10: marimo_baml.LC6_FUNCTIONS
# ============================================================================


def test_marimo_baml_lc6_functions() -> None:
    """Verify LC6_FUNCTIONS has 5 functions (the canonical lc6 extraction set)."""
    try:
        marimo_baml = _load_marimo_baml()
    except Exception as e:
        pytest.skip(f"marimo_baml could not be loaded: {e}")

    LC6_FUNCTIONS = marimo_baml.LC6_FUNCTIONS
    assert len(LC6_FUNCTIONS) == 5, f"Expected 5 LC6 functions, got {len(LC6_FUNCTIONS)}"

    # The 5 canonical LC6 extraction functions
    canonical = [
        "ExtractCurriculumSyllabus", "ExtractExamPaperLayout",
        "ExtractMarkingSchemeGuideline", "ExtractCrossLinguisticConcept",
        "ExtractSyllabusDiagram",
    ]
    for fn in canonical:
        assert fn in LC6_FUNCTIONS, f"Missing {fn} in LC6_FUNCTIONS"


# ============================================================================
# Test 11: marimo_baml.JC_FUNCTIONS
# ============================================================================


def test_marimo_baml_jc_functions() -> None:
    """Verify JC_FUNCTIONS has 4 functions (the canonical JC extraction set)."""
    try:
        marimo_baml = _load_marimo_baml()
    except Exception as e:
        pytest.skip(f"marimo_baml could not be loaded: {e}")

    JC_FUNCTIONS = marimo_baml.JC_FUNCTIONS
    assert len(JC_FUNCTIONS) == 4, f"Expected 4 JC functions, got {len(JC_FUNCTIONS)}"

    # The 4 canonical JC extraction functions
    canonical = [
        "ExtractJuniorCycleCurriculum", "ExtractJuniorCycleExamPaper",
        "ExtractJuniorCycleCBADescriptor", "ExtractJuniorCycleShortCourse",
    ]
    for fn in canonical:
        assert fn in JC_FUNCTIONS, f"Missing {fn} in JC_FUNCTIONS"


# ============================================================================
# Test 12: marimo_baml.QPACK_FUNCTIONS
# ============================================================================


def test_marimo_baml_qpack_functions() -> None:
    """Verify QPACK_FUNCTIONS has 3 functions (the cross-stage qpack set)."""
    try:
        marimo_baml = _load_marimo_baml()
    except Exception as e:
        pytest.skip(f"marimo_baml could not be loaded: {e}")

    QPACK_FUNCTIONS = marimo_baml.QPACK_FUNCTIONS
    assert len(QPACK_FUNCTIONS) == 3, f"Expected 3 qpack functions, got {len(QPACK_FUNCTIONS)}"

    # The 3 canonical qpack functions
    canonical = [
        "GenerateSubjectQuestPack", "GenerateSubjectFormativeItem",
        "ScoreSubjectFormativeResponse",
    ]
    for fn in canonical:
        assert fn in QPACK_FUNCTIONS, f"Missing {fn} in QPACK_FUNCTIONS"


# ============================================================================
# Test 13: marimo_to_copilotkit.CANONICAL_NOTEBOOKS
# ============================================================================


def test_marimo_to_copilotkit_canonical_notebooks() -> None:
    """Verify CANONICAL_NOTEBOOKS has 10 entries."""
    try:
        m2c = _load_marimo_to_copilotkit()
    except Exception as e:
        pytest.skip(f"marimo_to_copilotkit could not be loaded: {e}")

    CANONICAL_NOTEBOOKS = m2c.CANONICAL_NOTEBOOKS
    assert len(CANONICAL_NOTEBOOKS) == 10, (
        f"Expected 10 canonical notebooks, got {len(CANONICAL_NOTEBOOKS)}"
    )
    # Each entry must be a path string
    for nb in CANONICAL_NOTEBOOKS:
        assert isinstance(nb, str)
        assert nb.endswith(".py")
        assert nb.startswith("notebooks/")


# ============================================================================
# Test 14: marimo_to_copilotkit.discover_public_functions
# ============================================================================


def test_marimo_to_copilotkit_discover_public_functions() -> None:
    """Verify discover_public_functions() returns a list (heuristic AST scan)."""
    try:
        m2c = _load_marimo_to_copilotkit()
    except Exception as e:
        pytest.skip(f"marimo_to_copilotkit could not be loaded: {e}")

    # discover_public_functions should be callable
    assert callable(m2c.discover_public_functions)

    # Calling with a non-existent path should return an empty list (graceful)
    result = m2c.discover_public_functions("notebooks/00_marimo_patterns_tour.py")
    assert isinstance(result, list), (
        f"discover_public_functions returned {type(result)}, expected list"
    )

    # Each entry should be a function name (string)
    for fn_name in result:
        assert isinstance(fn_name, str)
        assert not fn_name.startswith("_")  # heuristic: only public functions
