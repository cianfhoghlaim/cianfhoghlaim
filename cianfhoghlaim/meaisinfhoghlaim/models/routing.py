"""Shared LlamaSwap routing table for the Gaois + Celtic language pipeline.

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Provides a single source of truth for routing BAML extraction
functions and CocoIndex v1 Apps through the canonical
`meaisinfhoghlaim/models/registry.py` OCR/VLM registry.

Per-language + per-source routing:

| Source group            | Language | Client            | Model              | Reason                       |
|:--|:--|:--|:--|:--|
| `gaois`                 | `ga`     | `LlamaSwap`       | `uccix-mistral-24b` | Modern Irish-language path   |
| `gaois`                 | `en`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Multilingual MoE            |
| `gaois`                 | `*`      | `LlamaSwap`       | `gemma-4-26B-A4B`   | Default (multilingual)      |
| `duchas`                | `*`      | `LlamaSwap`       | `molmo2-8b`         | Diagram pointing specialist  |
| `duchas`                | `*`      | `LlamaSwap`       | `dots-ocr`          | Layout specialist            |
| `heritage`              | `*`      | `LlamaSwap`       | `gemma-4-26B-A4B`   | Multilingual MoE            |
| `canuint`               | `*`      | `LlamaSwap`       | `qwen3-vl-8b`       | Audio + text multimodal      |
| `ud_celtic`             | `ga`     | `LlamaSwap`       | `uccix-mistral-24b` | Irish treebank               |
| `ud_celtic`             | `*`      | `LlamaSwap`       | `gemma-4-26B-A4B`   | Other Celtic treebanks       |
| `local_documents`       | `*`      | `LlamaSwap`       | `qwen3-vl-8b`       | OCR workhorse                |
| `celtic_curriculum`     | `ga`     | `LlamaSwap`       | `uccix-mistral-24b` | Irish curriculum             |
| `celtic_curriculum`     | `cy`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Welsh curriculum             |
| `celtic_curriculum`     | `gd`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Scottish Gaelic curriculum   |
| `celtic_curriculum`     | `br`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Breton curriculum            |
| `celtic_curriculum`     | `gv`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Manx curriculum              |
| `celtic_curriculum`     | `kw`     | `LlamaSwap`       | `gemma-4-26B-A4B`   | Cornish curriculum           |
| `celtic_curriculum`     | `*`      | `LlamaSwap`       | `gemma-4-26B-A4B`   | Default (multilingual)      |
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RoutingConfig:
    """The LiteLLM routing decision for a (source_group, language) pair."""

    client: str
    model: str
    tier: str

    def to_baml_client_name(self) -> str:
        """Return the BAML client name (e.g., 'LlamaSwap' → 'LlamaSwapClient')."""
        return f"{self.client}Client"


# Canonical routing table.
# Key: (source_group, language) where language can be "*" for default.
# Value: RoutingConfig with the LiteLLM client + model to dispatch to.
ROUTING_TABLE: dict[tuple[str, str], "RoutingConfig"] = {
    # Gaois APIs (Téarma + Logainm + Ainm)
    ("gaois", "ga"): RoutingConfig(client="LlamaSwap", model="uccix-mistral-24b", tier="tier2_medium"),
    ("gaois", "en"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("gaois", "*"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    # Dúchas National Folklore Collection
    ("duchas", "*"): RoutingConfig(client="LlamaSwap", model="molmo2-8b", tier="specialist"),
    # Heritage + Hidden Heritages
    ("heritage", "*"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    # Canuint (audio + text)
    ("canuint", "*"): RoutingConfig(client="LlamaSwap", model="qwen3-vl-8b", tier="tier2_medium"),
    # Universal Dependencies Celtic Treebanks
    ("ud_celtic", "ga"): RoutingConfig(client="LlamaSwap", model="uccix-mistral-24b", tier="tier2_medium"),
    ("ud_celtic", "*"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    # Local documents by subject (OCR)
    ("local_documents", "*"): RoutingConfig(client="LlamaSwap", model="qwen3-vl-8b", tier="tier2_medium"),
    # Celtic curriculum (6 Celtic languages)
    ("celtic_curriculum", "ga"): RoutingConfig(client="LlamaSwap", model="uccix-mistral-24b", tier="tier2_medium"),
    ("celtic_curriculum", "cy"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("celtic_curriculum", "gd"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("celtic_curriculum", "br"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("celtic_curriculum", "gv"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("celtic_curriculum", "kw"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
    ("celtic_curriculum", "*"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium"),
}


def route_language(source_group: str, language: str) -> RoutingConfig:
    """Look up the routing decision for a (source_group, language) pair.

    Falls back to the "*" wildcard if the exact language match is
    missing, then to the default fallback `gemma-4-26B-A4B`.
    """
    key = (source_group, language)
    if key in ROUTING_TABLE:
        return ROUTING_TABLE[key]
    # Try the wildcard for the source group
    wildcard_key = (source_group, "*")
    if wildcard_key in ROUTING_TABLE:
        return ROUTING_TABLE[wildcard_key]
    # Final fallback: multilingual MoE
    return RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B", tier="tier2_medium")


def get_baml_client(source_group: str, language: str) -> str:
    """Return the BAML client name to use for a (source_group, language) pair.

    Example:
        get_baml_client("duchas", "ga")  # → "LlamaSwapClient"
    """
    return route_language(source_group, language).to_baml_client_name()


def get_model_name(source_group: str, language: str) -> str:
    """Return the model name to use for a (source_group, language) pair."""
    return route_language(source_group, language).model


def list_supported_routes() -> list[dict[str, Any]]:
    """Return all supported (source_group, language) routes as a list of dicts.

    Useful for documentation + the marimo notebooks that visualise
    the routing table.
    """
    return [
        {
            "source_group": sg,
            "language": lang,
            "client": cfg.client,
            "model": cfg.model,
            "tier": cfg.tier,
        }
        for (sg, lang), cfg in sorted(ROUTING_TABLE.items())
    ]


__all__ = [
    "ROUTING_TABLE",
    "RoutingConfig",
    "route_language",
    "get_baml_client",
    "get_model_name",
    "list_supported_routes",
]