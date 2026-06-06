"""Shared sub-agent: TranslationAgent.

EN↔GA translation via the litellm/irish model alias.
"""
from __future__ import annotations

import os


class TranslationAgent:
    """Celtic + EN↔GA translation via litellm.

    Real implementation: thin wrapper around litellm.completion(model="litellm/irish").
    The Irish alias falls back from UCCIX → Qomhrá → BritLLM per
    `infrastructure/stacks/engineering/litellm/config/config.yaml`.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("LITELLM_IRISH_MODEL", "litellm/irish")
        self.base_url = os.getenv("LITELLM_BASE_URL", "http://litellm:4000/v1")

    def translate(self, text: str, source_language: str = "en", target_language: str = "ga") -> dict:
        """Translate `text` from `source_language` to `target_language`."""
        return {
            "text": text,
            "source_language": source_language,
            "target_language": target_language,
            "translation": text,
            "model": self.model,
            "message": "Stub: real implementation calls litellm",
        }
