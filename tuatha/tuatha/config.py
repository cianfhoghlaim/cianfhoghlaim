"""tuatha.config — the canonical configuration surface.

Per the centralized-registry contract:
- LiteLLM model strings route through MODEL_REGISTRY.resolve
- Langfuse trace naming follows the agent.<subject>.<verb>
  pattern
- Cognee dataset naming follows the oideachais_<jurisdiction>_<subject>
  pattern
- Letta agent IDs follow the kcg-<subject>-agent pattern
- BAML client naming follows the MediaDesc + <Subject> patterns

This module exposes the 5 config dataclasses that all the
agents + orchestrator + operator import.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

# Per the centralized-registry contract: model_for() is the
# canonical resolution helper. No hardcoded model strings.
try:
    from meaisinfhoghlaim.models import model_for  # type: ignore
except ImportError:
    model_for = None  # type: ignore


# ── LiteLLM configuration ────────────────────────────────────────


@dataclass(frozen=True)
class LiteLlmConfig:
    """The canonical LiteLLM gateway configuration.

    All agents in the new tuatha/ project route through this
    config. The gateway URL is read from `LITELLM_API_BASE`
    (defaults to the canonical `https://litellm.cianfhoghlaim.ie`)
    + the API key is read from `LITELLM_API_KEY` (Locket-injected).
    """

    api_base: str = field(
        default_factory=lambda: os.environ.get(
            "LITELLM_API_BASE", "https://litellm.cianfhoghlaim.ie"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("LITELLM_API_KEY", "")
    )
    routing_key: str = "minimax"  # the canonical 7-tier fallback alias

    def resolve_model(self, family: str, role: str) -> str:
        """Resolve a model name through the centralized registry.

        Per the centralized-registry contract: never hardcode
        a model string; route through model_for(family, role).
        """
        if model_for is not None:
            # The OCR_VISION family only supports a few canonical
            # roles (default / legacy / lightweight / primary /
            # specialist). For roles that don't exist in the
            # registry (e.g., 'media_descriptor'), fall back to
            # the family default.
            available_roles_for_ocr = {
                "default",
                "legacy",
                "lightweight",
                "primary",
                "specialist",
            }
            actual_role = role
            if family == "ocr_vision" and role not in available_roles_for_ocr:
                actual_role = "default"
            try:
                return model_for(family, actual_role)
            except KeyError:
                # Final fallback: return the kcg-prefixed stub.
                return f"kcg-{family}-{actual_role}"
        # Graceful fallback for unit tests in isolation.
        return f"kcg-{family}-{role}"


# ── Langfuse configuration ────────────────────────────────────────


@dataclass(frozen=True)
class LangfuseConfig:
    """The canonical Langfuse trace naming configuration.

    All agents in the new tuatha/ project use the
    `agent.<subject>.<verb>` trace naming pattern.
    """

    public_key: str = field(
        default_factory=lambda: os.environ.get("LANGFUSE_PUBLIC_KEY", "")
    )
    secret_key: str = field(
        default_factory=lambda: os.environ.get("LANGFUSE_SECRET_KEY", "")
    )
    host: str = field(
        default_factory=lambda: os.environ.get(
            "LANGFUSE_HOST", "https://langfuse.cianfhoghlaim.ie"
        )
    )
    trace_template: str = "agent.{subject}.{verb}"

    def trace_name(self, subject: str, verb: str) -> str:
        """Build the canonical trace name for a (subject, verb) pair."""
        return self.trace_template.format(subject=subject, verb=verb)


# ── Cognee configuration ─────────────────────────────────────────


@dataclass(frozen=True)
class CogneeConfig:
    """The canonical Cognee dataset configuration.

    All agents in the new tuatha/ project emit to the
    `oideachais_<jurisdiction>_<subject>` Cognee dataset pattern.
    """

    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "COGNEE_API_URL", "http://cognee.cianfhoghlaim.ie:8000"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("COGNEE_API_KEY", "")
    )
    dataset_pattern: str = "oideachais_{jurisdiction}_{subject}"

    def dataset_name(self, jurisdiction: str, subject: str) -> str:
        """Build the canonical Cognee dataset name."""
        return self.dataset_pattern.format(
            jurisdiction=jurisdiction, subject=subject
        )


# ── Letta configuration ──────────────────────────────────────────


@dataclass(frozen=True)
class LettaConfig:
    """The canonical Letta agent ID configuration.

    All agents in the new tuatha/ project use the
    `kcg-<subject>-agent` agent ID pattern.
    """

    base_url: str = field(
        default_factory=lambda: os.environ.get(
            "LETTA_API_URL", "http://letta.cianfhoghlaim.ie:8283"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.environ.get("LETTA_API_KEY", "")
    )
    agent_id_pattern: str = "kcg-{subject}-agent"

    def agent_id(self, subject: str) -> str:
        """Build the canonical Letta agent ID for a subject."""
        return self.agent_id_pattern.format(subject=subject)


# ── BAML clients configuration ───────────────────────────────────


@dataclass(frozen=True)
class BamlClientsConfig:
    """The canonical BAML clients configuration.

    Per the centralized-schema-registry contract: BAML is the
    single source of truth; Pydantic + Zod + Convex + DuckLake
    DDL are all codegen.

    The 5 per-medium media_intel extractor clients (comic /
    prose / animation / gameplay / official_document) +
    the 8 per-subject qpack_<subject> clients + the 4 BIEP
    hackathon clients + the 3 educational agent clients.
    """

    baml_cli_path: str = field(
        default_factory=lambda: os.environ.get(
            "BAML_CLI_PATH", "tuatha/baml"
        )
    )
    client_timeout: int = 60  # seconds
    max_concurrent: int = 8  # parallel BAML function calls

    def resolve_client(self, family: str) -> str:
        """Resolve a BAML client by family (e.g., 'media_descriptor',
        'qpack_mathematics', 'marking_grader', etc.).
        """
        return f"{family}_client"


# ── The canonical config aggregate ───────────────────────────────


@dataclass(frozen=True)
class TuathaConfig:
    """The canonical configuration aggregate for the new tuatha/ project.

    Use this in every agent + orchestrator + workflow:
    ```python
    config = TuathaConfig.from_env()
    model = config.litellm.resolve_model("ocr_vision", "media_descriptor")
    trace_name = config.langfuse.trace_name("mathematics", "ask_syllabus")
    dataset = config.cognee.dataset_name("lc", "mathematics")
    agent_id = config.letta.agent_id("mathematics")
    ```
    """

    litellm: LiteLlmConfig = field(default_factory=LiteLlmConfig)
    langfuse: LangfuseConfig = field(default_factory=LangfuseConfig)
    cognee: CogneeConfig = field(default_factory=CogneeConfig)
    letta: LettaConfig = field(default_factory=LettaConfig)
    baml: BamlClientsConfig = field(default_factory=BamlClientsConfig)

    @classmethod
    def from_env(cls) -> TuathaConfig:
        """Build the canonical config from environment variables.

        Per the centralized-secrets-management contract: all
        secrets are Locket-injected via the `LITELLM_API_KEY` +
        `LANGFUSE_SECRET_KEY` + `COGNEE_API_KEY` + `LETTA_API_KEY`
        environment variables.
        """
        return cls(
            litellm=LiteLlmConfig(),
            langfuse=LangfuseConfig(),
            cognee=CogneeConfig(),
            letta=LettaConfig(),
            baml=BamlClientsConfig(),
        )


__all__ = [
    "BamlClientsConfig",
    "CogneeConfig",
    "LangfuseConfig",
    "LettaConfig",
    "LiteLlmConfig",
    "TuathaConfig",
]
