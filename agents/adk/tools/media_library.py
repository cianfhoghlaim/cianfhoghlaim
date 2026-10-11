"""agents/adk/tools/media_library.py — the cross-media design-pattern library.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change
(Plan 2 of openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md).

This module is the canonical inspiration surface for the Tuatha British
Isles MMO. It generalises the retro-only ``RETRO_LIBRARY`` (see
``agents/adk/tools/retro_capture.py``) into a **four-class** media library:

  - Class A — **X-Men** (the Hickman Marvel run) — comic — the X-gene
  - Class B — **The Wheel of Time** — prose (+ per-chapter) — channeling
  - Class C — **Avatar: The Last Airbender** — animation — the 4+1 elements
  - Class D — **Hades / Hades 2** — game — Olympian boons / rogue-lite

Every entry is **description-only**: the module records the *design
pattern* (power economy, visual grammar, palette) and never the literal
asset. ``MediaEntry.provenance.shippable`` is enforced ``False`` at
construction; ``assert_description_only()`` re-checks the whole library.

Model choices are resolved through the platform ``MODEL_REGISTRY`` (no
hardcoded model strings); see ``meaisinfhoghlaim/models/model_registry``.

Reference:
    baml_src/media/media_power_system.baml    — the cross-media schema
    baml_src/media/wheel_of_time.baml         — the per-chapter schema
    openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class MediaClass(StrEnum):
    """The four media-intel classes + the legacy retro tier."""

    COMIC = "comic"
    PROSE = "prose"
    ANIMATION = "animation"
    GAME = "game"
    RETRO = "retro"


class MediaMedium(StrEnum):
    """The medium of the source work (mirrors the BAML MediaMedium enum)."""

    COMIC = "Comic"
    PROSE = "Prose"
    ANIMATION = "Animation"
    GAME = "Game"
    FILM = "Film"


class PowerSystemKind(StrEnum):
    """Mirrors ``baml_src/media/media_power_system.baml::PowerSystemKind``."""

    DIVINE_BOON = "DivineBoon"
    ELEMENTAL_BENDING = "ElementalBending"
    MUTANT_GENE = "MutantGene"
    CHANNELING = "Channeling"
    COSMIC = "Cosmic"
    OTHER = "Other"


@dataclass(frozen=True)
class Provenance:
    """Description-only provenance. ``shippable`` is always ``False``."""

    rights_holder: str
    licence: str = "all-rights-reserved"
    derivation_class: str = "description_only"
    shippable: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.shippable is not False:
            raise ValueError(
                "MediaEntry provenance must be description-only "
                f"(shippable must be False, got {self.shippable!r})"
            )


@dataclass(frozen=True)
class MediaEntry:
    """One reference work in the media-intel library.

    Attributes:
        key: The stable slug (e.g. ``"hades"``).
    """

    key: str
    title: str
    media_class: MediaClass
    medium: MediaMedium
    power_system_kind: PowerSystemKind
    baml_function: str
    model_family: str
    model_role: str
    source_url: str
    provenance: Provenance
    first_appearance: str | None = None
    artifact: bool = False
    notes: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.provenance.shippable:
            raise ValueError(
                f"MediaEntry {self.key!r} declares shippable provenance; "
                "the media library is description-only"
            )

    @property
    def identity(self) -> tuple[MediaClass, str]:
        return (self.media_class, self.key)


def _prov(rights_holder: str, licence: str = "all-rights-reserved") -> Provenance:
    return Provenance(rights_holder=rights_holder, licence=licence)


MEDIA_LIBRARY: list[MediaEntry] = [
    # ── Class D — Games ────────────────────────────────────────────
    MediaEntry(
        key="hades",
        title="Hades",
        media_class=MediaClass.GAME,
        medium=MediaMedium.GAME,
        power_system_kind=PowerSystemKind.DIVINE_BOON,
        baml_function="ExtractHadesBoon",
        model_family="ocr_vision",
        model_role="hades_boon",
        source_url="https://www.supergiantgames.com/games/hades/",
        provenance=_prov("Supergiant Games"),
        first_appearance="2020",
        notes=(
            "Olympian boon economy: 9 Olympians, rarity tiers, duo boons. "
            "The rogue-lite power economy the MMO's boon system is modelled on."
        ),
        tags=("roguelite", "boon-system", "greek-mythology"),
    ),
    MediaEntry(
        key="hades_2",
        title="Hades II",
        media_class=MediaClass.GAME,
        medium=MediaMedium.GAME,
        power_system_kind=PowerSystemKind.DIVINE_BOON,
        baml_function="ExtractHadesBoon",
        model_family="ocr_vision",
        model_role="hades_boon",
        source_url="https://www.supergiantgames.com/games/hades-ii/",
        provenance=_prov("Supergiant Games"),
        first_appearance="2024",
        notes="Adds the Arcana cards + the Selene / Moon boon axis.",
        tags=("roguelite", "boon-system", "greek-mythology"),
    ),
    # ── Class C — Animation ────────────────────────────────────────
    MediaEntry(
        key="avatar_the_last_airbender",
        title="Avatar: The Last Airbender",
        media_class=MediaClass.ANIMATION,
        medium=MediaMedium.ANIMATION,
        power_system_kind=PowerSystemKind.ELEMENTAL_BENDING,
        baml_function="ExtractAnimationDescriptor",
        model_family="ocr_vision",
        model_role="media_descriptor",
        source_url="https://en.wikipedia.org/wiki/Avatar:_The_Last_Airbender",
        provenance=_prov("Nickelodeon / Paramount"),
        first_appearance="2005",
        notes=(
            "The 4+1 element vocabulary (air/water/fire/earth/spirit) + the "
            "sub-discipline axes (metal/blood/lightning/healing)."
        ),
        tags=("elemental", "martial-arts", "coming-of-age"),
    ),
    MediaEntry(
        key="the_legend_of_korra",
        title="The Legend of Korra",
        media_class=MediaClass.ANIMATION,
        medium=MediaMedium.ANIMATION,
        power_system_kind=PowerSystemKind.ELEMENTAL_BENDING,
        baml_function="ExtractAnimationDescriptor",
        model_family="ocr_vision",
        model_role="media_descriptor",
        source_url="https://en.wikipedia.org/wiki/The_Legend_of_Korra",
        provenance=_prov("Nickelodeon / Paramount"),
        first_appearance="2012",
        notes="Adds pro-bending team mechanics + the spirit-energy axis.",
        tags=("elemental", "steampunk", "sequel"),
    ),
    # ── Class A — Comics ───────────────────────────────────────────
    MediaEntry(
        key="xmen_hickman",
        title="X-Men (Jonathan Hickman run)",
        media_class=MediaClass.COMIC,
        medium=MediaMedium.COMIC,
        power_system_kind=PowerSystemKind.MUTANT_GENE,
        baml_function="ExtractComicDescriptor",
        model_family="ocr_vision",
        model_role="xmen_scene",
        source_url="https://www.marvel.com/comics/guides/1174/x-men",
        provenance=_prov("Marvel Comics"),
        first_appearance="2019",
        notes=(
            "The X-gene / mutant power taxonomy across House of X / Powers "
            "of X / the 6 Hickman publications. Data-page visual grammar."
        ),
        tags=("mutant", "team-book", "data-page"),
    ),
    # ── Class B — Prose (per-chapter) ──────────────────────────────
    MediaEntry(
        key="wheel_of_time",
        title="The Wheel of Time",
        media_class=MediaClass.PROSE,
        medium=MediaMedium.PROSE,
        power_system_kind=PowerSystemKind.CHANNELING,
        baml_function="ExtractWotChapterSchema",
        model_family="text_llm",
        model_role="Primary",
        source_url="https://en.wikipedia.org/wiki/The_Wheel_of_Time",
        provenance=_prov("Tor Books / Bandersnatch Group"),
        first_appearance="1990",
        notes=(
            "Per-chapter schema: saidar / saidin / True Power / Tel'aran'rhiod "
            "/ wolfbrothers, indexed chapter by chapter across all 14 books "
            "so the pipeline can identify WHEN a power is used."
        ),
        tags=("channeling", "epic-fantasy", "per-chapter"),
    ),
    # ── The legacy retro tier (kept; marked artifact) ──────────────
    MediaEntry(
        key="number_munchers",
        title="Number Munchers",
        media_class=MediaClass.RETRO,
        medium=MediaMedium.GAME,
        power_system_kind=PowerSystemKind.OTHER,
        baml_function="ExtractGameplayPattern",
        model_family="ocr_vision",
        model_role="media_descriptor",
        source_url="https://en.wikipedia.org/wiki/Number_Munchers",
        provenance=_prov("MECC"),
        first_appearance="1990",
        artifact=True,
        notes="Legacy placeholder tier — retained as the 'where we came from' reference.",
        tags=("retro", "maths", "education"),
    ),
    MediaEntry(
        key="golden_sun",
        title="Golden Sun",
        media_class=MediaClass.RETRO,
        medium=MediaMedium.GAME,
        power_system_kind=PowerSystemKind.OTHER,
        baml_function="ExtractGameplayPattern",
        model_family="ocr_vision",
        model_role="media_descriptor",
        source_url="https://en.wikipedia.org/wiki/Golden_Sun",
        provenance=_prov("Camelot / Nintendo"),
        first_appearance="2001",
        artifact=True,
        notes="Djinn summon progression; the retro tier's clearest power economy.",
        tags=("retro", "jrpg", "djinn"),
    ),
]


def list_media() -> list[MediaEntry]:
    """Return every media-library entry."""
    return list(MEDIA_LIBRARY)


def get_media(key: str) -> MediaEntry | None:
    """Return the entry for ``key`` or ``None``."""
    for entry in MEDIA_LIBRARY:
        if entry.key == key:
            return entry
    return None


def by_class(media_class: MediaClass) -> list[MediaEntry]:
    """Filter entries by their media class."""
    return [e for e in MEDIA_LIBRARY if e.media_class == media_class]


def by_power_system(kind: PowerSystemKind) -> list[MediaEntry]:
    """Filter entries by their power-system kind."""
    return [e for e in MEDIA_LIBRARY if e.power_system_kind == kind]


def first_class_media() -> list[MediaEntry]:
    """Return the non-artifact entries (the four current classes)."""
    return [e for e in MEDIA_LIBRARY if not e.artifact]


def resolve_model(entry: MediaEntry, *, language: str | None = None) -> str | None:
    """Resolve the entry's model key via ``MODEL_REGISTRY``.

    Returns ``None`` (and logs) when the family/role is not registered,
    so callers can degrade gracefully. Never returns a hardcoded string.
    """
    if entry.model_family == "text_llm" and entry.model_role == "Primary":
        return None
    try:
        from typing import cast

        from meaisinfhoghlaim.models import ModelFamily, model_for
    except ImportError:
        logger.debug("media_library: MODEL_REGISTRY not importable")
        return None
    try:
        return model_for(
            cast(ModelFamily, entry.model_family),
            entry.model_role,
            language=language,
        )
    except (KeyError, ValueError):
        logger.debug(
            "media_library: no MODEL_REGISTRY entry for family=%s role=%s",
            entry.model_family,
            entry.model_role,
        )
        return None


def power_descriptor_targets() -> list[dict[str, Any]]:
    """Yield the (media_class → BAML function → model) routing table.

    Consumed by ``cocoindex_flows/media/media_power_embedding.py`` and the
    marimo comparative-study dashboard.
    """
    targets: list[dict[str, Any]] = []
    for entry in first_class_media():
        targets.append(
            {
                "key": entry.key,
                "title": entry.title,
                "media_class": entry.media_class.value,
                "medium": entry.medium.value,
                "power_system_kind": entry.power_system_kind.value,
                "baml_function": entry.baml_function,
                "model_family": entry.model_family,
                "model_role": entry.model_role,
                "resolved_model": resolve_model(entry),
                "shippable": entry.provenance.shippable,
            }
        )
    return targets


def assert_description_only() -> None:
    """Raise if any entry declares shippable provenance (invariant guard)."""
    violations = [e.key for e in MEDIA_LIBRARY if e.provenance.shippable]
    if violations:
        raise AssertionError(
            f"media_library shippable violation(s): {', '.join(violations)}"
        )


def summary() -> dict[str, Any]:
    """Return a summary dict for dashboards + the control panel."""
    by_class_counts: dict[str, int] = {}
    for entry in MEDIA_LIBRARY:
        by_class_counts[entry.media_class.value] = (
            by_class_counts.get(entry.media_class.value, 0) + 1
        )
    return {
        "total": len(MEDIA_LIBRARY),
        "first_class": len(first_class_media()),
        "artifacts": sum(1 for e in MEDIA_LIBRARY if e.artifact),
        "by_class": by_class_counts,
        "all_description_only": all(not e.provenance.shippable for e in MEDIA_LIBRARY),
    }


__all__ = [
    "MEDIA_LIBRARY",
    "MediaClass",
    "MediaEntry",
    "MediaMedium",
    "PowerSystemKind",
    "Provenance",
    "assert_description_only",
    "by_class",
    "by_power_system",
    "first_class_media",
    "get_media",
    "list_media",
    "power_descriptor_targets",
    "resolve_model",
    "summary",
]
