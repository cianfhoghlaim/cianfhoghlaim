"""oideachais.dlt_sources.official_media.allowlist — Two-stage filter for official-media profiles.

Stage 1 is a deterministic O(1) lookup against 4 curated YAML
allowlists (intelligence / universities / parties / jurisdictions).
Stage 2 is a BAML fallback gated on a cheap regex heuristic — only
invoked for un-matched profiles that "look official" (verified badge,
``.gov``/``.ie``/``.uk``/``.ac`` in external URL, presence of words
like "official", "department", "ministry", "police", "army",
"agency" in the bio).

The filter is a single dataclass, ``AllowlistFilter``, instantiated
once at module load. The module-level singleton
``allowlist_filter`` is the canonical entry point for the rest of
the stack.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Heuristic regex — if any of these match the bio / external URL, the
# BAML fallback is invoked. These are the words that official accounts
# self-describe with; they are NOT a positive classifier on their own.
_HEURISTIC_OFFICIAL_WORDS = re.compile(
    r"\b(?:official|department|ministry|police|army|navy|agency|"
    r"intelligence|security|council|parliament|assembly|government|"
    r"university|college|institute|emergency|rescue|fire brigade|"
    r"border|revenue|customs)\b",
    re.IGNORECASE,
)
_HEURISTIC_GOV_DOMAINS = re.compile(
    r"\b(?:gov\.uk|gov\.ie|gov\.scot|gov\.wales|nidirect\.gov\.uk|"
    r"police\.uk|mod\.uk|met\.police\.uk|"
    r"\.ac\.uk|\.ac\.ie)\b",
    re.IGNORECASE,
)

CATEGORIES = (
    "intelligence",
    "university",
    "party",
    "jurisdiction",
    "agency",
    "emergency_service",
    "military",
    "government",
    "other",
)


# ---------------------------------------------------------------------------
# AllowlistFilter
# ---------------------------------------------------------------------------


@dataclass
class AllowlistMatch:
    """Result of classifying one profile."""

    is_official: bool
    stage: int
    category: str | None
    source: str

    def to_dlt_row(self) -> dict[str, Any]:
        return {
            "is_official": self.is_official,
            "stage": self.stage,
            "category": self.category,
            "source": self.source,
        }


@dataclass
class AllowlistFilter:
    """Two-stage filter: deterministic allowlist + cheap-heuristic-gated BAML fallback.

    Args:
        fixtures_dir: Directory containing the 4 ``allowlist_*.yaml``
            files. Defaults to ``./fixtures`` relative to this module.
        baml_classifier: Optional callable ``(ig_username, bio, external_url)
            -> {is_official_media, confidence, category, reason}`` for
            Stage-2 fallback. Defaults to the BAML-based classifier
            (``dlt_sources.official_media.classifier.classify_with_baml``)
            which is a no-op when the ``baml_client`` package is not
            generated. Pass ``baml_classifier=None`` to force Stage-1
            only.
        confidence_threshold: BAML confidence above which the fallback
            accepts the candidate. Default 0.7.
    """

    fixtures_dir: Path = field(
        default_factory=lambda: Path(__file__).parent / "fixtures"
    )
    baml_classifier: Any | None = None
    confidence_threshold: float = 0.7

    # Private state, populated by ``_load``
    _by_username: dict[str, tuple[str, str]] = field(
        default_factory=dict, init=False, repr=False
    )
    _by_category: dict[str, list[str]] = field(
        default_factory=dict, init=False, repr=False
    )

    def __post_init__(self) -> None:
        if self.baml_classifier is None:
            # Default to the BAML classifier; it returns None when the
            # baml_client is not generated, so Stage-1 is unaffected.
            from dlt_sources.official_media.classifier import classify_with_baml

            self.baml_classifier = classify_with_baml
        self._load()

    def _load(self) -> None:
        """Load all ``allowlist_*.yaml`` fixtures into the lookup dicts.

        The YAML's ``category`` field is the canonical category name
        (singular: ``university``, ``party``, ``jurisdiction``, …).
        The filename is a fallback if the YAML omits the field.
        """
        if not self.fixtures_dir.exists():
            logger.warning(
                "allowlist_fixtures_missing",
                dir=str(self.fixtures_dir),
            )
            return
        for yaml_path in sorted(self.fixtures_dir.glob("allowlist_*.yaml")):
            with yaml_path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            # Prefer the YAML's `category:` field (singular, canonical).
            # Fall back to the filename stem for fixture files that
            # don't declare it.
            category = data.get("category") or yaml_path.stem.replace(
                "allowlist_", ""
            )
            entries = data.get("entries", [])
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                username = entry.get("ig_username")
                if not isinstance(username, str) or not username:
                    continue
                normalised = username.lower().lstrip("@")
                self._by_username[normalised] = (category, yaml_path.name)
                self._by_category.setdefault(category, []).append(normalised)

    # -- Stage 1 --------------------------------------------------------

    def lookup(self, ig_username: str) -> AllowlistMatch | None:
        """Return the Stage-1 allowlist match for ``ig_username`` or
        ``None`` if not in any allowlist."""
        normalised = ig_username.lower().lstrip("@")
        hit = self._by_username.get(normalised)
        if hit is None:
            return None
        category, source = hit
        return AllowlistMatch(
            is_official=True,
            stage=1,
            category=category,
            source=source,
        )

    # -- Stage 2 --------------------------------------------------------

    def _looks_official(
        self,
        ig_username: str,
        bio: str = "",
        external_url: str = "",
    ) -> bool:
        """Cheap heuristic gate for the BAML fallback."""
        haystack = " ".join([ig_username, bio, external_url])
        if _HEURISTIC_OFFICIAL_WORDS.search(haystack):
            return True
        if _HEURISTIC_GOV_DOMAINS.search(haystack):
            return True
        return False

    def _invoke_baml(
        self,
        ig_username: str,
        bio: str,
        external_url: str,
    ) -> dict[str, Any] | None:
        """Invoke the BAML fallback. Returns the parsed decision or
        ``None`` if no classifier is configured or it raises."""
        if self.baml_classifier is None:
            return None
        try:
            return self.baml_classifier(
                ig_username=ig_username,
                ig_bio=bio,
                ig_external_url=external_url,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "baml_classifier_failed",
                ig_username=ig_username,
                error=str(exc),
            )
            return None

    # -- Public API -----------------------------------------------------

    def classify(
        self,
        ig_username: str,
        bio: str = "",
        external_url: str = "",
    ) -> AllowlistMatch:
        """Classify one profile. Returns an ``AllowlistMatch``.

        Order:
          1. If the username is in any allowlist → Stage-1 hit.
          2. Else if the cheap heuristic rejects → ``is_official=False``.
          3. Else if a BAML classifier is configured → invoke; accept if
             ``is_official_media`` and ``confidence >= threshold``.
          4. Else → ``is_official=False``.
        """
        stage1 = self.lookup(ig_username)
        if stage1 is not None:
            return stage1
        if not self._looks_official(ig_username, bio, external_url):
            return AllowlistMatch(
                is_official=False,
                stage=1,
                category=None,
                source="heuristic_reject",
            )
        decision = self._invoke_baml(ig_username, bio, external_url)
        if decision is None:
            return AllowlistMatch(
                is_official=False,
                stage=1,
                category=None,
                source="heuristic_only_no_baml",
            )
        is_official = bool(decision.get("is_official_media"))
        confidence = float(decision.get("confidence", 0.0))
        if is_official and confidence >= self.confidence_threshold:
            return AllowlistMatch(
                is_official=True,
                stage=2,
                category=str(decision.get("category", "other")),
                source="baml_classifier",
            )
        return AllowlistMatch(
            is_official=False,
            stage=2,
            category=None,
            source=f"baml_reject_conf_{confidence:.2f}",
        )

    # -- Diagnostics ----------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._by_username)

    def categories(self) -> dict[str, list[str]]:
        return dict(self._by_category)


# Module-level singleton — the canonical entry point.
allowlist_filter = AllowlistFilter()
