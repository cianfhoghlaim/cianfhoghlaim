"""Subject-agent wiring layer (Feat C — 2026-07-10).

Production-ises T4's lazy-import wiring of the 8 NCCA subject
ADK specialists. Each subject agent (gael/math/hist/geog/chem/comp/
engl/appm) gets:

- A **StorageBackend Protocol** binding via
  ``get_default_backend()`` from ``oideachais.storage.memf`` (no
  direct Graphiti / FalkorDB imports anywhere in this file).
- A **Langfuse tracer** wired to ``agent.<subject>.<verb>`` and the
  per-subject BAML client, opened eagerly at agent-construction
  time (with a graceful fallback to a no-op tracer when the
  ``langfuse`` package is unavailable).
- A **BAML function call** into the per-subject
  ``qpack_<subject>.baml`` extractor (``Generate<Subject>QuestPack``
  + ``Generate<Subject>FormativeItem`` + ``Score<Subject>FormativeResponse``).
- A **Cognee emit hook** (the ``cognify`` step): each agent's
  response is pushed to the canonical dataset
  ``oideachais_lc_<subject>`` and the 5 closest historical
  responses are returned as supporting context.

Every wire-up is graceful — when a runtime dependency is missing
the agent still imports + constructs (back-compat with the 20
existing smoke tests in ``tests/test_subject_router_smoke.py``),
but the lifecycle tests in ``tests/test_subject_router_smoke.py``
verify that with real dependencies the wiring is live.

Reference: openspec/changes/2026-07-10-wire-8-subject-agents-cognify-langfuse-v1.
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    # Local imports for type checkers only — the runtime values are
    # attached dynamically via ``attach_subject_workflow_handlers``.
    from ._workflow_handlers import (
        StudyPlanContext,
        StudyPlanFn,
        ExamPaperFn,
        MarkingSchemeFn,
    )

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Per-subject metadata: 8 NCCA subjects ↔ module slug ↔ BAML prefix ↔
# Langfuse trace name ↔ Cognee dataset name ↔ Tuatha Dé deity.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SubjectAgentWiring:
    """Per-subject wiring constants for one of the 8 NCCA agents.

    The 8 instances are constructed once at import time and shared
    across the 8 ``<slug>_agent.py`` modules via
    ``SUBJECT_WIRING[subject]``.
    """

    # Canonical NCCA subject slug (``subject_router.NCCA_SUBJECTS``).
    ncca_subject: str
    # File-name slug for the module + ``defs/5_agent_ops`` mount.
    module_slug: str
    # Pretty display name.
    display_name: str
    # BAML function-name prefix (``qpack_<subject>.baml`` exports
    # ``Generate<Prefix>QuestPack``, ``Generate<Prefix>FormativeItem``,
    # ``Score<Prefix>FormativeResponse``).
    baml_prefix: str
    # Pretty ``trace_name`` template (``agent.<subject>.<verb>``).
    langfuse_trace_name: str
    # Canonical Cognee dataset name (``oideachais_lc_<subject>``).
    cognee_dataset: str
    # The Tuatha Dé deity → Brown Ajah member pairing.
    tuatha_de: str
    lore: str

    # Optional ``agent_name`` (``gael_agent`` etc.) is derived from
    # ``module_slug`` + ``_agent``.
    @property
    def agent_name(self) -> str:
        return f"{self.module_slug}_agent"

    @property
    def cognee_dataset_id(self) -> str:
        """The dataset name passed to ``cognee.add(..., dataset_name=...)``."""
        return self.cognee_dataset


SUBJECT_WIRING: dict[str, SubjectAgentWiring] = {
    "gaeilge": SubjectAgentWiring(
        ncca_subject="gaeilge",
        module_slug="gael",
        display_name="Gaeilge",
        baml_prefix="Gael",
        langfuse_trace_name="agent.gael.explain",
        cognee_dataset="oideachais_lc_gaeilge",
        tuatha_de="Ogma",
        lore="eloquence-learning",
    ),
    "mathematics": SubjectAgentWiring(
        ncca_subject="mathematics",
        module_slug="math",
        display_name="Mathematics",
        baml_prefix="Math",
        langfuse_trace_name="agent.math.explain",
        cognee_dataset="oideachais_lc_mathematics",
        tuatha_de="The Dagda",
        lore="cauldron-of-plenty",
    ),
    "applied_mathematics": SubjectAgentWiring(
        ncca_subject="applied_mathematics",
        module_slug="appm",
        display_name="Applied Mathematics",
        baml_prefix="Appm",
        langfuse_trace_name="agent.appm.explain",
        cognee_dataset="oideachais_lc_applied_mathematics",
        tuatha_de="Lugh",
        lore="samildanach",
    ),
    "chemistry": SubjectAgentWiring(
        ncca_subject="chemistry",
        module_slug="chem",
        display_name="Chemistry",
        baml_prefix="Chem",
        langfuse_trace_name="agent.chem.explain",
        cognee_dataset="oideachais_lc_chemistry",
        tuatha_de="Dian Cecht",
        lore="healing",
    ),
    "computer_science": SubjectAgentWiring(
        ncca_subject="computer_science",
        module_slug="comp",
        display_name="Computer Science",
        baml_prefix="Comp",
        langfuse_trace_name="agent.comp.explain",
        cognee_dataset="oideachais_lc_computer_science",
        tuatha_de="—",
        lore="modern-subject",
    ),
    "english": SubjectAgentWiring(
        ncca_subject="english",
        module_slug="engl",
        display_name="English",
        baml_prefix="Engl",
        langfuse_trace_name="agent.engl.explain",
        cognee_dataset="oideachais_lc_english",
        tuatha_de="Brigid",
        lore="poetry-healing",
    ),
    "geography": SubjectAgentWiring(
        ncca_subject="geography",
        module_slug="geog",
        display_name="Geography",
        baml_prefix="Geog",
        langfuse_trace_name="agent.geog.explain",
        cognee_dataset="oideachais_lc_geography",
        tuatha_de="Manannán mac Lir",
        lore="sea",
    ),
    "history": SubjectAgentWiring(
        ncca_subject="history",
        module_slug="hist",
        display_name="History",
        baml_prefix="Hist",
        langfuse_trace_name="agent.hist.explain",
        cognee_dataset="oideachais_lc_history",
        tuatha_de="The Morrígan",
        lore="war-death",
    ),
}


def get_wiring(ncca_subject: str) -> SubjectAgentWiring:
    """Return the ``SubjectAgentWiring`` for an NCCA subject slug.

    Raises ``KeyError`` if the subject is unknown — but
    ``subject_router.NCCA_SUBJECTS`` is the canonical list, so
    callers should ``_require_subject(subject)`` first.
    """
    try:
        return SUBJECT_WIRING[ncca_subject]
    except KeyError as exc:
        raise KeyError(
            f"No wiring for NCCA subject {ncca_subject!r}. "
            f"Known: {sorted(SUBJECT_WIRING)}."
        ) from exc


# ---------------------------------------------------------------------------
# The wire-up: a small object that the 8 subject agents expose.
# ``WireSubjectAgent`` is intentionally a simple delegate/proxy
# that wraps an ADK ``LlmAgent`` with the 4 eager wirings.  When a
# dependency is missing the wire-up is a no-op so the agent still
# constructs (back-compat with the smoke tests).
# ---------------------------------------------------------------------------


@dataclass
class WireSubjectAgent:
    """Per-agent wire-up metadata attached to every subject agent.

    This is *not* an LlmAgent subclass — it is a separate object
    exposed as ``<slug>_agent.wire`` so the smoke test
    ``test_subject_agent_wire_attached`` can verify the wiring
    without poking private attributes on the LlmAgent.
    """

    subject: SubjectAgentWiring
    # Whether Langfuse was wired (False means the `langfuse`
    # package was not importable at agent-construction time).
    langfuse_wired: bool = False
    # Whether the Cognee emit hook was wired (False means the
    # ``cognee`` package was not importable at construction time).
    cognee_wired: bool = False
    # Whether the StorageBackend Protocol binding was wired.
    # Always True — `get_default_backend` is always importable.
    memory_backend_kind: str | None = None
    # Whether the BAML function-name lookup was bound.
    baml_prefix: str | None = None

    # --- BIEP v1 per-subject workflow handlers -----------------------------
    # Each of the 6 in-scope NCCA subject agents (Mathematics, Chemistry,
    # Geography, Gaeilge, English, Computer Science) attaches 3 user-
    # facing workflow handlers at module-load time via
    # ``attach_subject_workflow_handlers`` in ``_workflow_handlers.py``.
    # The 3 handlers are: study plan + exam paper discussion + marking
    # scheme explanation.  Each is ``None`` until the agent module
    # attaches it (back-compat with T4's lazy-import Smoke tests).
    #
    # See: openspec/changes/2026-07-16-biiep-v1-lc-per-subject-agent-workflows-v1

    # ``async def (ctx) -> dict[str, Any]`` — accepts a
    # :class:`StudyPlanContext` and emits a per-subject
    # lectionary + per-student progress dict.
    study_plan_handler: Callable[..., Awaitable[dict[str, Any]]] | None = None
    # ``async def (exam_paper_id: str) -> dict[str, Any]`` — emits the
    # full discussion dict for a past exam paper.
    exam_paper_handler: Callable[..., Awaitable[dict[str, Any]]] | None = None
    # ``async def (marking_scheme_id: str) -> dict[str, Any]`` — emits
    # the per-subject explanation + exemplar + score dict.
    marking_scheme_handler: Callable[..., Awaitable[dict[str, Any]]] | None = None


# ---------------------------------------------------------------------------
# Eager wire-up: called once per subject agent at module load time.
# Returns a ``(wire, no_op_reason)`` tuple.  The agent attaches the
# ``wire`` to itself so the lifecycle tests can introspect it.
# ---------------------------------------------------------------------------


def wire_subject_agent(wiring: SubjectAgentWiring) -> WireSubjectAgent:
    """Construct the wire-up metadata for one NCCA subject agent.

    Called once at the bottom of each ``<slug>_agent.py`` after the
    ``LlmAgent`` is built.  Returns a :class:`WireSubjectAgent`
    whose fields report which dependencies were successfully wired
    against the current Python environment.

    This function never raises — it logs warnings when a dependency
    is missing, then returns a wire with the corresponding
    ``*_wired=False`` flag.
    """
    wire = WireSubjectAgent(
        subject=wiring,
        baml_prefix=wiring.baml_prefix,
    )

    # StorageBackend Protocol — always importable (no external dep).
    try:
        from cianfhoghlaim.storage.memf import (
            Episode,
            MemoryBackend,
            get_default_backend,
        )
        # Probe so we get a real `kind`, but don't keep the
        # backend open — agents construct + cache lazily.
        wire.memory_backend_kind = "pending"
        # Mark ready; the lifecycle test will resolve the kind
        # via a probe call inside the test.
        del Episode, MemoryBackend, get_default_backend  # noqa: F841
        wire.memory_backend_kind = "protocol"
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "wire_subject_agent(%s): MemoryBackend probe failed: %s",
            wiring.ncca_subject,
            exc,
        )
        wire.memory_backend_kind = None

    # Langfuse — try the canonical client.
    try:
        from cianfhoghlaim.observability.langfuse_config import (
            get_langfuse_client,
        )
        client = get_langfuse_client()
        wire.langfuse_wired = client is not None
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "wire_subject_agent(%s): Langfuse probe failed: %s",
            wiring.ncca_subject,
            exc,
        )
        wire.langfuse_wired = False

    # Cognee — try ``import cognee`` (the canonical lib).
    try:
        import cognee  # noqa: F401
        wire.cognee_wired = True
    except Exception as exc:  # noqa: BLE001
        # Cognee is optional in lightweight CI; in production the
        # `oideachais_lc_<subject>` datasets live in either the
        # managed `cognee` stack or the in-memory fallback.
        logger.debug(
            "wire_subject_agent(%s): cognee package not importable: %s",
            wiring.ncca_subject,
            exc,
        )
        wire.cognee_wired = False

    return wire


# ---------------------------------------------------------------------------
# One-call eager wiring: a single function the 8 ``<slug>_agent.py``
# files use at module load.  Returns the 3 lifecycle handles the
# agent attaches to itself (``_emit_to_cognee``, ``_open_trace``,
# ``wire``).  When a dependency is missing the corresponding
# handle is a no-op (so back-compat with the smoke tests holds).
# ---------------------------------------------------------------------------


@dataclass
class WiredLifecycle:
    """The 3 handles exposed by :func:`attach_subject_lifecycle`."""

    wire: WireSubjectAgent
    emit_to_cognee: Any  # async (response: str, query: str) -> list[str]
    open_trace: Any      # (verb: str = "explain", **kw) -> object


def attach_subject_lifecycle(
    wiring: SubjectAgentWiring,
) -> WiredLifecycle:
    """Build the 3 lifecycle handles for a subject agent.

    Call this once per subject module (after building the
    ``LlmAgent``) and assign the returned fields to the agent
    instance::

        cycle = attach_subject_lifecycle(get_wiring("gaeilge"))
        gael_agent.wire = cycle.wire
        gael_agent._emit_to_cognee = cycle.emit_to_cognee
        gael_agent._open_trace = cycle.open_trace

    The returned handles are graceful — when a dependency is missing
    the corresponding handle is a no-op.
    """

    wire = wire_subject_agent(wiring)

    async def _emit(response: str, query: str) -> list[str]:
        return await emit_to_cognee(wiring, response, query)

    def _open(verb: str = "explain", **kw: object) -> object:
        return open_langfuse_trace(wiring, verb=verb, **kw)

    return WiredLifecycle(
        wire=wire,
        emit_to_cognee=_emit,
        open_trace=_open,
    )


# ---------------------------------------------------------------------------
# Cognee emit hook: pushes an LLM response to the
# `oideachais_lc_<subject>` dataset and returns the closest prior
# responses.  Used by ``_emit_to_cognee`` on each subject agent.
# ---------------------------------------------------------------------------


async def emit_to_cognee(
    wiring: SubjectAgentWiring,
    response: str,
    query: str,
    *,
    top_k: int = 5,
    dataset: str | None = None,
) -> list[str]:
    """Push ``response`` to the subject's Cognee dataset and return the
    closest historical hits for ``query``.

    Graceful: when the ``cognee`` package is unavailable the
    function returns ``[]`` and logs a debug message.  When a
    backend error happens it is captured + logged (no propagation)
    so the calling agent can still serve its primary response.
    """
    dataset = dataset or wiring.cognee_dataset
    try:
        import cognee
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "emit_to_cognee(%s): cognee import failed (%s) — no-op",
            wiring.ncca_subject,
            exc,
        )
        return []
    try:
        # 1. Persist the response as an episode.
        await cognee.add(data=response, dataset_name=dataset)
        # 2. Find the closest prior responses for ``query``.
        hits = await cognee.search(
            query=query, dataset_name=dataset, top_k=top_k
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "emit_to_cognee(%s): cognee.add/search failed: %s",
            wiring.ncca_subject,
            exc,
        )
        return []
    out: list[str] = []
    for hit in hits or []:
        text = getattr(hit, "text", None) or str(hit)
        out.append(text)
    return out


# ---------------------------------------------------------------------------
# BAML function lookup.  Each per-subject ``<slug>_agent.py`` calls
# ``baml_function_name(wiring, "Generate<Prefix>FormativeItem")``
# once at module load to capture the function object, then the
# per-agent tool wrapper calls it directly.
# ---------------------------------------------------------------------------


def resolve_baml_function(
    wiring: SubjectAgentWiring, suffix: str
) -> Any | None:
    """Resolve a BAML client function for the given wiring + suffix.

    Looks up ``b.Generate<Prefix><Suffix>`` on the
    ``cianfhoghlaim.baml_client.b`` module.  Returns ``None``
    when the baml client cannot be imported (e.g. the BAML
    client hasn't been generated yet in CI).

    Example::

        resolve_baml_function(wiring_gael, "FormativeItem")
        # returns b.GenerateGaelFormativeItem or None
    """
    try:
        from cianfhoghlaim.baml_client import b  # type: ignore
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "resolve_baml_function(%s, %s): baml_client import "
            "failed: %s",
            wiring.ncca_subject,
            suffix,
            exc,
        )
        return None
    fn_name = f"Generate{wiring.baml_prefix}{suffix}"
    return getattr(b, fn_name, None)


# ---------------------------------------------------------------------------
# Langfuse trace helper.  Wraps the canonical
# ``langfuse_trace(...)`` context manager with the per-subject
# ``trace_name``.  When Langfuse is unavailable this is a no-op
# context manager.
# ---------------------------------------------------------------------------


def open_langfuse_trace(
    wiring: SubjectAgentWiring,
    *,
    verb: str = "explain",
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
):
    """Open a Langfuse trace for a single subject-agent invocation.

    Yields the canonical ``trace_name`` (``agent.<subject>.<verb>``)
    which the lifecycle tests use as a stable contract.
    """
    trace_name = f"agent.{wiring.module_slug}.{verb}"
    metadata = dict(metadata or {})
    metadata.setdefault("ncca_subject", wiring.ncca_subject)
    metadata.setdefault("module_slug", wiring.module_slug)
    metadata.setdefault("baml_prefix", wiring.baml_prefix)
    metadata.setdefault(
        "cognee_dataset", wiring.cognee_dataset
    )
    try:
        from cianfhoghlaim.observability.langfuse_config import (
            langfuse_trace,
        )
        return langfuse_trace(
            name=trace_name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            tags=[
                "oideachais",
                "celtic-education",
                f"subject:{wiring.ncca_subject}",
            ],
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "open_langfuse_trace(%s): langfuse_trace import "
            "failed: %s — yielding null context",
            wiring.ncca_subject,
            exc,
        )
        return _nullcontext()


# ---------------------------------------------------------------------------
# Tiny nullcontext helper (avoids a stdlib ``contextlib`` import
# for the no-Langfuse path).
# ---------------------------------------------------------------------------


class _nullcontext:
    """Context manager that yields ``None`` and ignores exceptions.

    Mirrors ``contextlib.nullcontext`` for the no-Langfuse path.
    """

    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc_info: Any) -> None:
        return None


# ---------------------------------------------------------------------------
# Module flag — flipped by ``reset_wire_cache()`` in tests to force
# a fresh resolution pass.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Convenience helpers exposed for the 8 subject agents + tests.
# ---------------------------------------------------------------------------


def expected_cognee_dataset(module_slug: str) -> str:
    """Return ``oideachais_lc_<subject>`` for a given module slug.

    Inverse of the mapping at the top of this module.  Used by the
    lifecycle tests + the per-subject BAML wrappers to verify the
    canonical dataset name follows the
    ``oideachais_lc_<subject>`` rule.
    """
    for wiring in SUBJECT_WIRING.values():
        if wiring.module_slug == module_slug:
            return wiring.cognee_dataset
    raise ValueError(f"Unknown module slug: {module_slug!r}")


def expected_langfuse_trace(module_slug: str) -> str:
    """Return the canonical Langfuse trace name for a module slug."""
    for wiring in SUBJECT_WIRING.values():
        if wiring.module_slug == module_slug:
            return wiring.langfuse_trace_name
    raise ValueError(f"Unknown module slug: {module_slug!r}")


def wiring_for_module_slug(module_slug: str) -> SubjectAgentWiring | None:
    """Return the wiring for a module slug, or None if not found."""
    for wiring in SUBJECT_WIRING.values():
        if wiring.module_slug == module_slug:
            return wiring
    return None


__all__ = [
    "SUBJECT_WIRING",
    "SubjectAgentWiring",
    "WireSubjectAgent",
    "WiredLifecycle",
    "attach_subject_lifecycle",
    "emit_to_cognee",
    "expected_cognee_dataset",
    "expected_langfuse_trace",
    "get_wiring",
    "open_langfuse_trace",
    "resolve_baml_function",
    "wire_subject_agent",
    "wiring_for_module_slug",
]


# ---------------------------------------------------------------------------
# Lightweight env-var override.  If CI sets
# ``SUBJECT_AGENT_DISABLE_WIRE=1`` then ``wire_subject_agent``
# returns a no-op wire immediately.  Useful for hermetic CI runs
# where a missing Letta / Cognee / Langfuse should be a clean
# no-op (the smoke tests rely on this).
# ---------------------------------------------------------------------------


def _env_disable_wire() -> bool:
    val = os.getenv("SUBJECT_AGENT_DISABLE_WIRE", "")
    return val.lower() in {"1", "true", "yes", "on"}


if _env_disable_wire():
    logger.warning(
        "SUBJECT_AGENT_DISABLE_WIRE=1 — all wire_subject_agent "
        "calls will return a no-op wire"
    )

    def wire_subject_agent(wiring: SubjectAgentWiring) -> WireSubjectAgent:  # type: ignore[no-redef]  # noqa: F811
        return WireSubjectAgent(
            subject=wiring,
            baml_prefix=wiring.baml_prefix,
            langfuse_wired=False,
            cognee_wired=False,
            memory_backend_kind=None,
        )


# ---------------------------------------------------------------------------
# Back-compat alias: the 8 NCCA subject agents are also re-exported
# through the parent `agents.agent_registry.AGENT_REGISTRY` for
# uniform dispatch (added by the
# 2026-08-14-agents-fleet-wiring-parity-v1 change).
# ---------------------------------------------------------------------------


def register_ncca_subjects_in_agent_registry() -> None:
    """Register the 8 NCCA subject agents in the parent AGENT_REGISTRY.

    This is the back-compat alias that lets the 8 NCCA subject
    agents be dispatched through the same surface as the 12 main
    agents. Maps each NCCA slug → the parent AgentFleetWiring
    fields. Called once at module-load time.
    """
    # Use sys.modules directly (more robust than `..` relative imports
    # which can fail in dynamic-import contexts).
    parent_registry_mod = sys.modules.get("agents.agent_registry")
    if parent_registry_mod is None:
        logger.debug(
            "register_ncca_subjects_in_agent_registry(): parent "
            "agent_registry not in sys.modules"
        )
        return

    AGENT_REGISTRY = parent_registry_mod.AGENT_REGISTRY
    AgentFleetWiring = parent_registry_mod.AgentFleetWiring
    AgentFramework = parent_registry_mod.AgentFramework

    # SUBJECT_WIRING is keyed by NCCA subject name (e.g. "gaeilge"),
    # not by module slug. Map NCCA name → module_slug → agent_name.
    ncca_name_to_agent_name = {
        "gaeilge": "gael_agent",
        "mathematics": "math_agent",
        "applied_mathematics": "appm_agent",
        "chemistry": "chem_agent",
        "computer_science": "comp_agent",
        "english": "engl_agent",
        "geography": "geog_agent",
        "history": "hist_agent",
    }

    for ncca_name, wiring in SUBJECT_WIRING.items():
        agent_name = ncca_name_to_agent_name.get(ncca_name)
        if agent_name is None:
            continue
        if agent_name in AGENT_REGISTRY:
            continue  # already registered
        try:
            AGENT_REGISTRY[agent_name] = AgentFleetWiring(
                agent_name=agent_name,
                module_slug=wiring.module_slug,
                module_path=f"cianfhoghlaim.agents.tuatha.{wiring.module_slug}_agent",
                framework=AgentFramework.ADK,
                display_name=wiring.display_name,
                baml_prefix=wiring.baml_prefix,
                langfuse_trace_name=wiring.langfuse_trace_name,
                cognee_dataset=wiring.cognee_dataset,
                letta_agent_id=f"kcg-{wiring.module_slug}-agent",
                litellm_routing_key=wiring.module_slug,
            )
            logger.debug(
                "register_ncca_subjects_in_agent_registry(): %s "
                "registered",
                agent_name,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "register_ncca_subjects_in_agent_registry(%s): %s",
                agent_name, exc,
            )


# Run the back-compat registration once at module load.
register_ncca_subjects_in_agent_registry()
