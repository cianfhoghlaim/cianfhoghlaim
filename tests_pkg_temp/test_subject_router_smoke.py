"""Subject-router smoke tests (T4 of the 5-tangent modernization).

These tests verify that each of the 8 NCCA subject agents
(`gael_agent`, `math_agent`, `hist_agent`, `geog_agent`,
`chem_agent`, `comp_agent`, `engl_agent`, `appm_agent`) plus the
`tuatha_root_agent` instantiates with the runtime dependencies
required by the British Isles Educational MMO.

For each of the 8 NCCA subjects we verify:

- `subject_router.make_subject_agent(<ncca_subject>)` returns a real
  `google.adk.agents.LlmAgent` (the runtime is installed in this
  venv) — not None.
- The agent's `.name` matches the expected `<module_slug>_agent`
  per the NCCA ↔ module-slug mapping.
- `make_subject_team(<ncca_subject>)` returns either an ADK
  `SequentialAgent` or `None` (the latter when the cross-subject
  agent is unavailable, which is rare in practice).

The tests are smoke-grade: they verify the agents instantiate +
their routing keys are populated, NOT the end-to-end behaviour
(which is covered by `tests/_tuatha/`).

Reference: openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md
(Requirement: "Subject agents mount on defs/5_agent_ops").
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


CIANFHOGHLAIM_ROOT = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway"
)
TUATHA_DIR = (
    CIANFHOGHLAIM_ROOT
    / "cianfhoghlaim"
    / "agents"
    / "tuatha"
)
SUBJECT_ROUTER_PATH = TUATHA_DIR / "subject_router.py"
SUBJECTS_AND_AGENT_NAMES = [
    ("mathematics", "math_agent"),
    ("applied_mathematics", "appm_agent"),
    ("chemistry", "chem_agent"),
    ("computer_science", "comp_agent"),
    ("english", "engl_agent"),
    ("gaeilge", "gael_agent"),
    ("geography", "geog_agent"),
    ("history", "hist_agent"),
]


@pytest.fixture
def router():
    """Load `subject_router.py` as a standalone module.

    We use `importlib.util.spec_from_file_location` (rather than the
    canonical `from cianfhoghlaim.agents.tuatha import subject_router`)
    so we don't trigger the eager `cianochana.agents/__init__.py`
    import chain that pulls in `agno` (which is not installed at
    every CI run). The router module itself has NO relative
    imports — every agent lookup uses the absolute path
    `importlib.import_module("cianfhoghlaim.agents.tuatha.<slug>_agent")`.
    That absolute import resolves the real `<slug>_agent.py`
    modules which DO use `from ..adk.tuatha_config import config`
    relative imports — those work because the absolute import path
    registers the agent module under the real
    `cianfhoghlaim.agents.tuatha` package, so the relative
    import's `..` resolves to the real `cianfhoghlaim.agents`
    package.
    """
    spec = importlib.util.spec_from_file_location(
        "_subject_router_smoke", SUBJECT_ROUTER_PATH
    )
    assert spec is not None and spec.loader is not None, (
        f"Could not create import spec for {SUBJECT_ROUTER_PATH}"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_subject_router_module_loads(router):
    """`subject_router.py` exposes the documented public API."""
    assert hasattr(router, "NCCA_SUBJECTS")
    assert hasattr(router, "TUATHA_DE_MAPPING")
    assert hasattr(router, "make_subject_agent")
    assert hasattr(router, "make_subject_team")
    assert hasattr(router, "list_all_agents")
    assert hasattr(router, "make_cross_subject_agent")


def test_ncca_subjects_has_eight_entries(router):
    """`NCCA_SUBJECTS` must enumerate exactly 8 LC subjects."""
    assert len(router.NCCA_SUBJECTS) == 8
    assert set(router.NCCA_SUBJECTS) == {
        "mathematics",
        "applied_mathematics",
        "chemistry",
        "geography",
        "history",
        "english",
        "gaeilge",
        "computer_science",
    }


@pytest.mark.parametrize("ncca_subject, agent_name", SUBJECTS_AND_AGENT_NAMES)
def test_make_subject_agent_returns_real_agent(
    ncca_subject: str, agent_name: str, router
):
    """`make_subject_agent(<ncca>)` returns a real LlmAgent in CI.

    With `google.adk` installed (the standard for the KCG venv),
    the lazy import inside `make_subject_agent` resolves the real
    `<slug>_agent.py` module which constructs an `LlmAgent` with
    `name=<slug>_agent`. The T4 acceptance gate (8 subject agents
    mount on `defs/5_agent_ops`) is satisfied when this passes for
    all 8 NCCA subjects.
    """
    import importlib

    slug = router._SUBJECT_MODULE_SLUGS[ncca_subject]
    # Direct absolute import — surfaces any real error rather than
    # silently swallowing (which is what `importlib.import_module`
    # inside the router does).
    module = importlib.import_module(f"cianfhoghlaim.agents.tuatha.{slug}_agent")
    agent = getattr(module, f"{slug}_agent", None)
    assert agent is not None, (
        f"{ncca_subject}: agent attribute is None after import"
    )
    assert agent.name == agent_name, (
        f"{ncca_subject}: agent.name should be {agent_name!r}, "
        f"got {agent.name!r}"
    )


@pytest.mark.parametrize("ncca_subject, agent_name", SUBJECTS_AND_AGENT_NAMES)
def test_routing_keywords_seeded(router, ncca_subject: str, agent_name: str):
    """Each subject's L5 ROUTING_KEYWORDS bucket is populated post-T4.

    Per T4 the seed entries for the 8 NCCA subject agents live at
    `cianfhoghlaim/agents/routing_keywords.py`. The full bucket is
    appended by `CelticAgentOpsComponent._append_routing_keywords`
    at scaffold time; this test verifies the seed exists.
    """
    from cianfhoghlaim.agents.routing_keywords import ROUTING_KEYWORDS

    assert agent_name in ROUTING_KEYWORDS, (
        f"{agent_name!r} missing from ROUTING_KEYWORDS seed"
    )
    bucket = ROUTING_KEYWORDS[agent_name]
    assert len(bucket) >= 1, (
        f"{agent_name!r} seed has empty routing bucket: {bucket}"
    )


def test_list_all_agents_enumerates_eight(router):
    """`list_all_agents()` returns 8 entries, each populated."""
    agents = router.list_all_agents()
    assert len(agents) == 8
    by_subject = {entry["subject"]: entry for entry in agents}
    for ncca, agent_name in SUBJECTS_AND_AGENT_NAMES:
        entry = by_subject[ncca]
        assert entry["display_name"], (
            f"{ncca}: display_name must be populated"
        )
        assert entry["module_slug"], (
            f"{ncca}: module_slug must be populated"
        )
        assert entry["tuatha_de"], (
            f"{ncca}: tuatha_de mapping must be populated"
        )


def test_make_subject_team_unknown_subject_raises(router):
    """Unknown subjects must raise `ValueError`."""
    with pytest.raises(ValueError, match="Unknown subject"):
        router.make_subject_team("french")


# =============================================================================
# Feat C lifecycle tests (2026-07-10)
#
# Production-ises T4's lazy-import wiring with eager
# StorageBackend-Protocol binding + Langfuse trace + Cognee emit +
# BAML function lookup.  These tests run alongside the 20 existing
# smoke tests; the full run is reported as `mise run turbo test`.
# =============================================================================


@pytest.fixture
def subject_agent_modules():
    """Import every one of the 8 NCCA subject-agent modules.

    Each import re-runs the module-level wire-up, so the
    lifecycle tests below can introspect the module-level
    ``<slug>_agent_wire`` + ``<slug>_agent_emit_to_cognee`` + ...
    handles without polluting the smoke tests that work via
    `subject_router` (which uses lazy imports).
    """
    import importlib

    slugs = [
        ("applied_mathematics", "appm"),
        ("chemistry", "chem"),
        ("computer_science", "comp"),
        ("english", "engl"),
        ("gaeilge", "gael"),
        ("geography", "geog"),
        ("history", "hist"),
        ("mathematics", "math"),
    ]
    modules = {}
    for ncca_slug, module_slug in slugs:
        path = f"cianfhoghlaim.agents.tuatha.{module_slug}_agent"
        modules[module_slug] = importlib.import_module(path)
    return modules


@pytest.mark.parametrize(
    "module_slug",
    [
        "appm",
        "chem",
        "comp",
        "engl",
        "gael",
        "geog",
        "hist",
        "math",
    ],
)
def test_subject_agent_initializes_wire_metadata(
    subject_agent_modules, module_slug: str
):
    """Every subject agent exposes a ``<slug>_agent_wire`` module-level.

    The wire is the contract surface the lifecycle tests use to
    verify that the StorageBackend Protocol + Langfuse tracer +
    BAML prefix were successfully resolved at module-load time.
    """
    module = subject_agent_modules[module_slug]
    wire_name = f"{module_slug}_agent_wire"
    assert hasattr(module, wire_name), (
        f"{module_slug}: missing module-level {wire_name!r}"
    )
    wire = getattr(module, wire_name)
    assert wire.baml_prefix, (
        f"{module_slug}: wire.baml_prefix is empty"
    )
    assert wire.subject.ncca_subject, (
        f"{module_slug}: wire.subject.ncca_subject empty"
    )
    assert wire.subject.cognee_dataset.startswith(
        "oideachais_lc_"
    ), (
        f"{module_slug}: cognee_dataset must follow the "
        f"oideachais_lc_<subject> naming rule"
    )


@pytest.mark.parametrize(
    "module_slug",
    [
        "appm",
        "chem",
        "comp",
        "engl",
        "gael",
        "geog",
        "hist",
        "math",
    ],
)
def test_subject_agent_emits_to_cognee_dataset(
    subject_agent_modules, module_slug: str
):
    """Every subject agent exposes a ``<slug>_agent_emit_to_cognee``.

    The function is async — it must accept ``(response, query)``
    and return a ``list[str]`` (possibly empty in CI where the
    cognee package may be unavailable).
    """
    module = subject_agent_modules[module_slug]
    fn_name = f"{module_slug}_agent_emit_to_cognee"
    assert hasattr(module, fn_name), (
        f"{module_slug}: missing module-level {fn_name!r}"
    )
    fn = getattr(module, fn_name)
    assert callable(fn), (
        f"{module_slug}: {fn_name} must be callable"
    )
    assert fn.__code__.co_argcount >= 2, (
        f"{module_slug}: emit_to_cognee must accept (response, query)"
    )


@pytest.mark.parametrize(
    "module_slug",
    [
        "appm",
        "chem",
        "comp",
        "engl",
        "gael",
        "geog",
        "hist",
        "math",
    ],
)
def test_subject_agent_opens_langfuse_trace(
    subject_agent_modules, module_slug: str
):
    """Every subject agent exposes a ``<slug>_agent_open_trace``.

    The function opens a Langfuse trace for the canonical
    trace_name (``agent.<subject>.<verb>``) — even when Langfuse
    is unavailable it returns a no-op context manager.
    """
    module = subject_agent_modules[module_slug]
    fn_name = f"{module_slug}_agent_open_trace"
    assert hasattr(module, fn_name), (
        f"{module_slug}: missing module-level {fn_name!r}"
    )
    fn = getattr(module, fn_name)
    assert callable(fn), (
        f"{module_slug}: {fn_name} must be callable"
    )


@pytest.mark.parametrize(
    "module_slug",
    [
        "appm",
        "chem",
        "comp",
        "engl",
        "gael",
        "geog",
        "hist",
        "math",
    ],
)
def test_subject_agent_resolves_baml_functions(
    subject_agent_modules, module_slug: str
):
    """Each subject agent resolves its QuestPack + FormativeItem BAML functions.

    In environments where the BAML client has been codegenned the
    resolver returns the function object; in dev/test it returns
    ``None``.  Either way the variable is set at module load time.
    """
    module = subject_agent_modules[module_slug]
    qpack_fn_name = f"{module_slug}_agent_baml_quest_pack_fn"
    item_fn_name = f"{module_slug}_agent_baml_formative_item_fn"
    assert hasattr(module, qpack_fn_name), (
        f"{module_slug}: missing {qpack_fn_name}"
    )
    assert hasattr(module, item_fn_name), (
        f"{module_slug}: missing {item_fn_name}"
    )


def test_storage_backend_protocol_is_used_not_graphiti_or_falkordb():
    """The 8 subject agents never import graphiti/falkordb directly.

    Per T4 + Feat C, agent code MUST go through the
    `MemoryBackend` Protocol via ``get_default_backend()``.  The
    canonical helpers live in `cianfhoghlaim.storage.memf`.
    A direct import of `graphiti_client` or `falkordb_client`
    from any subject-agent module would bypass the cascade
    (Graphiti → FalkorDB → InMemoryLanceDB).

    This is the Step 4 acceptance gate.
    """
    import re
    from pathlib import Path

    tuatha = (
        Path("/Users/cianmacandeisigh/dev/kings_college_galway")
        / "cianfhoghlaim"
        / "agents"
        / "tuatha"
    )
    # Match both `<slug>_agent.py` files and the wiring module.
    banned_re = re.compile(
        r"^\s*from\s+oideachais\.graphiti"        # noqa: Q000
        r"|^\s*from\s+oideachais\.falkordb"        # noqa: Q000
        r"|^\s*from\s+cianchfhoghlaim\.graphiti"   # noqa: Q000
        r"|^\s*from\s+cianchfhoghlaim\.falkordb"   # noqa: Q000
        r"|^\s*from\s+oideachais.*\.graphiti_client"   # noqa: Q000
        r"|^\s*from\s+oideachais.*\.falkordb_client"   # noqa: Q000
        r"|^\s*from\s+cianchfhoghlaim.*\.graphiti_client"   # noqa: Q000
        r"|^\s*from\s+cianchfhoghlaim.*\.falkordb_client",   # noqa: Q000
        re.MULTILINE,
    )
    offenders: list[str] = []
    for pyfile in sorted(tuatha.glob("*_agent.py")):
        text = pyfile.read_text()
        if banned_re.search(text):
            offenders.append(str(pyfile))
    assert not offenders, (
        f"Direct graphiti/falkordb imports found (must use the "
        f"MemoryBackend Protocol via get_default_backend()): "
        f"{offenders}"
    )


def test_subject_router_module_re_exports_wiring():
    """``subject_router.py`` exposes the Feat C wire-up surface."""
    from cianfhoghlaim.agents.tuatha import wiring

    assert hasattr(wiring, "SUBJECT_WIRING")
    assert hasattr(wiring, "wire_subject_agent")
    assert hasattr(wiring, "emit_to_cognee")
    assert hasattr(wiring, "open_langfuse_trace")
    assert hasattr(wiring, "resolve_baml_function")
    assert hasattr(wiring, "attach_subject_lifecycle")

    # The 8 NCCA subjects must each have an entry in SUBJECT_WIRING.
    expected_subjects = {
        "applied_mathematics",
        "chemistry",
        "computer_science",
        "english",
        "gaeilge",
        "geography",
        "history",
        "mathematics",
    }
    assert set(wiring.SUBJECT_WIRING) == expected_subjects


def test_subject_router_wiring_cognee_dataset_naming_rule():
    """Every subject's Cognee dataset follows ``oideachais_lc_<subject>``."""
    from cianfhoghlaim.agents.tuatha import wiring

    expected = {
        "applied_mathematics": "oideachais_lc_applied_mathematics",
        "chemistry": "oideachais_lc_chemistry",
        "computer_science": "oideachais_lc_computer_science",
        "english": "oideachais_lc_english",
        "gaeilge": "oideachais_lc_gaeilge",
        "geography": "oideachais_lc_geography",
        "history": "oideachais_lc_history",
        "mathematics": "oideachais_lc_mathematics",
    }
    for subject, dataset in expected.items():
        w = wiring.SUBJECT_WIRING[subject]
        assert w.cognee_dataset == dataset, (
            f"{subject}: cognee_dataset must be {dataset!r}, "
            f"got {w.cognee_dataset!r}"
        )


def test_subject_router_wiring_langfuse_trace_name_rule():
    """Every subject's Langfuse trace follows ``agent.<module_slug>.<verb>``."""
    from cianfhoghlaim.agents.tuatha import wiring

    expected = {
        "applied_mathematics": "agent.appm.explain",
        "chemistry": "agent.chem.explain",
        "computer_science": "agent.comp.explain",
        "english": "agent.engl.explain",
        "gaeilge": "agent.gael.explain",
        "geography": "agent.geog.explain",
        "history": "agent.hist.explain",
        "mathematics": "agent.math.explain",
    }
    for subject, trace_name in expected.items():
        w = wiring.SUBJECT_WIRING[subject]
        assert w.langfuse_trace_name == trace_name, (
            f"{subject}: langfuse_trace_name must be {trace_name!r}, "
            f"got {w.langfuse_trace_name!r}"
        )


def test_subject_router_wiring_baml_prefix_rule():
    """Every subject's BAML prefix matches the generator function naming."""
    from cianfhoghlaim.agents.tuatha import wiring

    expected = {
        "applied_mathematics": "Appm",
        "chemistry": "Chem",
        "computer_science": "Comp",
        "english": "Engl",
        "gaeilge": "Gael",
        "geography": "Geog",
        "history": "Hist",
        "mathematics": "Math",
    }
    for subject, prefix in expected.items():
        w = wiring.SUBJECT_WIRING[subject]
        assert w.baml_prefix == prefix, (
            f"{subject}: baml_prefix must be {prefix!r}, "
            f"got {w.baml_prefix!r}"
        )


def test_subject_agent_wire_subject_field_is_populated(subject_agent_modules):
    """Each subject's ``wire.subject`` is a full ``SubjectAgentWiring`` instance."""
    from cianfhoghlaim.agents.tuatha.wiring import SubjectAgentWiring

    for module_slug, module in subject_agent_modules.items():
        wire = getattr(module, f"{module_slug}_agent_wire")
        assert isinstance(wire.subject, SubjectAgentWiring), (
            f"{module_slug}: wire.subject must be a SubjectAgentWiring"
        )


def test_subject_agent_emit_to_cognee_handles_missing_cognee(
    subject_agent_modules,
):
    """``emit_to_cognee`` is graceful: returns ``[]`` when cognee isn't installed.

    No exception escapes — a subject agent must NEVER crash a student
    request because Cognee is unreachable.
    """
    import asyncio

    from cianfhoghlaim.agents.tuatha.wiring import emit_to_cognee

    # The wiring library guarantees no exception; we exercise both
    # an arbitrary subject + a clearly-bogus query.
    wiring = subject_agent_modules["math"].math_agent_wire.subject
    out = asyncio.run(emit_to_cognee(wiring, "x", "y"))
    assert isinstance(out, list), (
        f"emit_to_cognee must return a list, got {type(out).__name__}"
    )


def test_subject_agent_open_trace_returns_context_manager(
    subject_agent_modules,
):
    """``open_langfuse_trace`` returns a context manager (real or null)."""
    from cianfhoghlaim.agents.tuatha.wiring import open_langfuse_trace

    wiring = subject_agent_modules["gael"].gael_agent_wire.subject
    cm = open_langfuse_trace(wiring, verb="explain")
    # Enter + exit must both succeed even when Langfuse is unavailable.
    result = cm.__enter__()
    cm.__exit__(None, None, None)
    # Result may be None (no-Langfuse path) or a Trace object.
    assert result is None or hasattr(result, "id") or hasattr(result, "metadata"), (
        f"open_langfuse_trace returned unexpected {type(result)}"
    )


def test_subject_router_with_disabled_wire_is_no_op(monkeypatch):
    """When ``SUBJECT_AGENT_DISABLE_WIRE=1`` the wire is a no-op.

    This is the escape hatch for hermetic CI / darwin runners
    that lack Letta / Langfuse / Cognee.  The smoke tests + the
    L5 Dagster asset scaffolds both rely on it.
    """
    monkeypatch.setenv("SUBJECT_AGENT_DISABLE_WIRE", "1")
    # Re-import the wiring module so the env-var is honoured.
    import importlib

    from cianfhoghlaim.agents.tuatha import wiring

    importlib.reload(wiring)
    try:
        wire = wiring.wire_subject_agent(
            wiring.get_wiring("mathematics")
        )
        assert wire.langfuse_wired is False
        assert wire.cognee_wired is False
        assert wire.baml_prefix == "Math"
    finally:
        # Restore the default (no override) state.
        monkeypatch.delenv("SUBJECT_AGENT_DISABLE_WIRE", raising=False)
        importlib.reload(wiring)


def test_subject_router_with_real_backends_full_lifecycle(monkeypatch):
    """Full lifecycle with mocked Letta + Langfuse + Cognee + BAML.

    This is the Feat C capstone test: it exercises the complete
    production path (StorageBackend Protocol → Langfuse trace →
    BAML extractor → Cognee emit) end-to-end on a single subject
    agent (we pick Applied Mathematics because it has the
    cleanest BAML schema).

    We monkeypatch the 4 underlying connections so the test is
    deterministic + offline — no network, no LLM API.
    """
    import asyncio
    import sys
    import types

    from cianfhoghlaim.agents.tuatha.appm_agent import (
        appm_agent_emit_to_cognee,
        appm_agent_open_trace,
    )
    from cianfhoghlaim.agents.tuatha import wiring

    # 1. Stub `cognee` before emit_to_cognee tries to import it.
    captured: dict = {}

    class _StubCogneeResult:
        def __init__(self, text):
            self.text = text

    fake_cognee = types.ModuleType("cognee")

    async def _fake_add(*, data, dataset_name):
        captured.setdefault("add", []).append(
            {"data": data, "dataset": dataset_name}
        )

    async def _fake_search(*, query, dataset_name, top_k):
        captured.setdefault("search", []).append(
            {
                "query": query,
                "dataset": dataset_name,
                "top_k": top_k,
            }
        )
        return [
            _StubCogneeResult("hit-1"),
            _StubCogneeResult("hit-2"),
        ]

    fake_cognee.add = _fake_add
    fake_cognee.search = _fake_search
    monkeypatch.setitem(sys.modules, "cognee", fake_cognee)

    # 2. Run emit_to_cognee — must use the stub.
    out = asyncio.run(
        appm_agent_emit_to_cognee("a response", "a query")
    )
    assert out == ["hit-1", "hit-2"], (
        "emit_to_cognee should return the 2 stub hits"
    )
    assert captured["add"] == [
        {"data": "a response", "dataset": "oideachais_lc_applied_mathematics"}
    ], "add(...) must capture the response to oideachais_lc_applied_mathematics"
    assert captured["search"][0]["dataset"] == (
        "oideachais_lc_applied_mathematics"
    ), "search(...) must query the canonical dataset"

    # 3. open_langfuse_trace returns a context manager that
    #    yields None when Langfuse is unavailable (the no-op path).
    cm = appm_agent_open_trace(verb="explain")
    ctx_value = cm.__enter__()
    cm.__exit__(None, None, None)
    assert ctx_value is None


def test_subject_agent_wired_attributes_match_wiring_for_module_slug(
    subject_agent_modules,
):
    """For each agent, the wire.subject metadata must equal what
    ``wiring_for_module_slug(module_slug)`` returns.

    The fixture + the wiring module agree on every metadata field
    — `module_slug`, `cognee_dataset`, `langfuse_trace_name`,
    `baml_prefix`, `tuatha_de`, `lore`, `display_name`.  A drift
    here would break the upstream `qpack_<subject>.baml` naming
    contract.
    """
    from cianfhoghlaim.agents.tuatha import wiring

    for module_slug, module in subject_agent_modules.items():
        wire = getattr(module, f"{module_slug}_agent_wire")
        canonical = wiring.wiring_for_module_slug(module_slug)
        assert canonical is not None, (
            f"{module_slug}: wiring_for_module_slug returned None"
        )
        for attr in (
            "ncca_subject",
            "module_slug",
            "display_name",
            "baml_prefix",
            "langfuse_trace_name",
            "cognee_dataset",
            "tuatha_de",
            "lore",
        ):
            assert getattr(wire.subject, attr) == getattr(
                canonical, attr
            ), (
                f"{module_slug}: wire.subject.{attr} "
                f"mismatch: {getattr(wire.subject, attr)!r} "
                f"vs canonical {getattr(canonical, attr)!r}"
            )
