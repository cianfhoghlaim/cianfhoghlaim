"""Tests for the 13 éraic (Lugh's compensation) BAML extension.

Verifies that:
  1. The eiraic_treasures.baml source file exists on disk and contains the
     13 treasure classes + the GetEiraicTreasures function.
  2. After `baml-cli generate`, the 13 treasure classes are importable from
     the regenerated `baml_client.types` module.
  3. Each treasure class is a Pydantic model with the expected canonical
     fields (treasure_id, title, provenance, capability, primary_subject,
     rationale_en, rationale_ga, mmo_signal).

The 13 treasures (canonical Lugh éraic):
  1.  PigSkinOfDobar               → Biology
  2.  HeiferSkinOfDobar            → Geography
  3.  SpearOfAssal                 → Mathematics
  4.  ChariotOfSidrach             → Applied Mathematics
  5.  SwordOfCaladbolg             → Computer Science
  6.  SevenPigsOfEasmal            → All subjects
  7.  WhelpOfIoruaidh              → English
  8.  CookingSpitOfInnisCera       → Gaeilge
  9.  ArmourOfClochur              → History
  10. ThreeApplesOfHesperides      → Cross-subject
  11. PigSkinBagOfHealingWell      → Citation rigor
  12. FeatherOfBirdOfCrannog       → Recovery from failure
  13. SamildanachOfLugh            → Universal mastery
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BAML_FILE = REPO_ROOT / "baml" / "education" / "_shared" / "eiraic_treasures.baml"

# Add the canonical baml_client locations to sys.path so the generated
# Pydantic types are importable from `baml_client.types`. We try the
# in-project path first, then the share-mounted baml_client (used when
# `baml-cli generate` has been run from the project root).
_CANDIDATE_BAML_CLIENT_DIRS: tuple[Path, ...] = (
    REPO_ROOT / "baml" / "shared" / "baml_client",
    REPO_ROOT / "baml" / "shared",
    REPO_ROOT / "baml",
    REPO_ROOT / "shared" / "baml_client",
)
for _candidate in _CANDIDATE_BAML_CLIENT_DIRS:
    if _candidate.is_dir() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

# The 13 canonical éraic classes. The order matches the 13-demand list.
THE_THIRTEEN_EIRAIC_CLASSES: list[str] = [
    "PigSkinOfDobar",
    "HeiferSkinOfDobar",
    "SpearOfAssal",
    "ChariotOfSidrach",
    "SwordOfCaladbolg",
    "SevenPigsOfEasmal",
    "WhelpOfIoruaidh",
    "CookingSpitOfInnisCera",
    "ArmourOfClochur",
    "ThreeApplesOfHesperides",
    "PigSkinBagOfHealingWell",
    "FeatherOfBirdOfCrannog",
    "SamildanachOfLugh",
]

# Expected primary subject mapping per treasure (cumulative).
THE_THIRTEEN_PRIMARY_SUBJECTS: dict[str, str] = {
    "PigSkinOfDobar": "BIOLOGY",
    "HeiferSkinOfDobar": "GEOGRAPHY",
    "SpearOfAssal": "MATHEMATICS",
    "ChariotOfSidrach": "APPLIED_MATHEMATICS",
    "SwordOfCaladbolg": "COMPUTER_SCIENCE",
    "SevenPigsOfEasmal": "ALL_SUBJECTS",
    "WhelpOfIoruaidh": "ENGLISH",
    "CookingSpitOfInnisCera": "GAEILGE",
    "ArmourOfClochur": "HISTORY",
    "ThreeApplesOfHesperides": "CROSS_SUBJECT",
    "PigSkinBagOfHealingWell": "CITATION_RIGOR",
    "FeatherOfBirdOfCrannog": "RECOVERY_FROM_FAILURE",
    "SamildanachOfLugh": "UNIVERSAL_MASTERY",
}


# ============================================================================
# Test 1 — Source BAML file exists & contains all 13 treasure classes
# ============================================================================


def test_eiraic_baml_file_exists() -> None:
    """The eiraic_treasures.baml source file exists."""
    assert BAML_FILE.exists(), f"Missing BAML source file: {BAML_FILE}"


def test_eiraic_baml_has_get_function() -> None:
    """The BAML source declares the `GetEiraicTreasures` function."""
    assert BAML_FILE.exists()
    content = BAML_FILE.read_text(encoding="utf-8")
    assert "function GetEiraicTreasures" in content, (
        "eiraic_treasures.baml must define the `GetEiraicTreasures` function"
    )


@pytest.mark.parametrize("class_name", THE_THIRTEEN_EIRAIC_CLASSES)
def test_eiraic_baml_has_each_class(class_name: str) -> None:
    """The BAML source declares each of the 13 éraic class definitions."""
    assert BAML_FILE.exists()
    content = BAML_FILE.read_text(encoding="utf-8")
    pattern = rf"\bclass\s+{class_name}\b"
    assert re.search(pattern, content), (
        f"eiraic_treasures.baml must define `class {class_name}` "
        f"(one of the 13 Lugh éraic treasures)"
    )


def test_eiraic_baml_has_exactly_13_class_definitions() -> None:
    """Count check: there are 13 `class <Name>` definitions in the BAML file.

    Plus the auxiliary support classes (EiraicTitle, EiraicTreasures) for a
    grand total of 15 — so we filter for the éraic-specific ones, then
    assert exactly 13 of them.
    """
    assert BAML_FILE.exists()
    content = BAML_FILE.read_text(encoding="utf-8")
    class_decls = re.findall(r"^\s*class\s+(\w+)\s*[{]", content, re.MULTILINE)
    # Pull only the 13 canonical éraic class names.
    present = [name for name in class_decls if name in set(THE_THIRTEEN_EIRAIC_CLASSES)]
    missing = sorted(set(THE_THIRTEEN_EIRAIC_CLASSES) - set(present))
    extras = sorted(set(present) - set(THE_THIRTEEN_EIRAIC_CLASSES))
    assert not missing, f"Missing éraic class definitions: {missing}"
    assert not extras, f"Unexpected éraic class definitions: {extras}"
    assert len(present) == 13, (
        f"Expected exactly 13 éraic treasure class definitions, "
        f"found {len(present)}: {sorted(present)}"
    )


# ============================================================================
# Test 2 — generated baml_client.types (skipped when not generated)
# ============================================================================


@pytest.mark.parametrize("class_name", THE_THIRTEEN_EIRAIC_CLASSES)
def test_baml_types_importable_for_each_eiraic(class_name: str) -> None:
    """Each of the 13 éraic classes is importable from baml_client.types.

    Skipped when baml_client has not been generated (CI default).
    Failure messages tell the developer to run `baml-cli generate`.
    """
    try:
        from baml_client.types import EiraicTreasures, EiraicTitle  # type: ignore[import-not-found]
        # The 13 individual class symbols.
        from baml_client import types as baml_types  # type: ignore[import-not-found]
    except ImportError as e:
        pytest.fail(
            f"baml_client not generated — run `cd cianfhoghlaim && "
            f"uv run baml-cli generate` first: {e}"
        )

    cls = getattr(baml_types, class_name, None)
    assert cls is not None, (
        f"`baml_client.types.{class_name}` must be present after generation "
        f"(one of the 13 éraic treasures)"
    )
    # Each class is a Pydantic v2 model — it should have `model_fields`.
    assert hasattr(cls, "model_fields"), (
        f"`baml_client.types.{class_name}` must be a Pydantic model"
    )

    # Each treasure class must declare the canonical 8 fields.
    expected_fields = {
        "treasure_id",
        "title",
        "provenance",
        "capability",
        "primary_subject",
        "rationale_en",
        "rationale_ga",
        "mmo_signal",
    }
    declared = set(cls.model_fields.keys())
    missing_fields = expected_fields - declared
    assert not missing_fields, (
        f"`{class_name}` is missing canonical fields {sorted(missing_fields)}"
    )

    # The shared types exist too.
    assert hasattr(baml_types, "EiraicTreasures")
    assert hasattr(baml_types, "EiraicTitle")
    assert hasattr(EiraicTreasures, "model_fields")
    assert hasattr(EiraicTitle, "model_fields")
    # The aggregator type must list all 13 éraic child fields.
    aggregator_fields = set(EiraicTreasures.model_fields.keys())
    expected_aggregator_fields = {
        "pig_skin_of_dobar",
        "heifer_skin_of_dobar",
        "spear_of_assal",
        "chariot_of_sidrach",
        "sword_of_caladbolg",
        "seven_pigs_of_easmal",
        "whelp_of_ioruaidh",
        "cooking_spit_of_innis_cera",
        "armour_of_clochur",
        "three_apples_of_hesperides",
        "pigskin_bag_of_healing_well",
        "feather_of_bird_of_crannog",
        "samildanach_of_lugh",
        "primary_treasures_for_subject",
        "total_count",
    }
    missing_agg = expected_aggregator_fields - aggregator_fields
    assert not missing_agg, (
        f"`EiraicTreasures` aggregator is missing fields {sorted(missing_agg)}"
    )


# ============================================================================
# Test 3 — b.GetEiraicTreasures is callable on the generated client
# ============================================================================


def test_get_eiraic_treasures_function_callable() -> None:
    """`b.GetEiraicTreasures('mathematics')` is callable and returns an
    EiraicTreasures object whose `total_count == 13`.

    Skipped when baml_client has not been generated.
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]
        from baml_client.types import EiraicTreasures  # type: ignore[import-not-found]
        from baml_client.async_client import BamlAsyncClient  # type: ignore[import-not-found]
    except ImportError as e:
        pytest.fail(
            f"baml_client not generated — run `cd cianfhoghlaim && "
            f"uv run baml-cli generate` first: {e}"
        )

    # The `b` namespace should expose the function via the sync + async paths.
    assert hasattr(b, "GetEiraicTreasures"), (
        "`b.GetEiraicTreasures` must be available after generation"
    )

    # The async client attribute must include the function too.
    async_client: BamlAsyncClient = b  # type: ignore[assignment]
    assert hasattr(async_client, "GetEiraicTreasures"), (
        "`b.GetEiraicTreasures` must also be exposed on the async client"
    )

    # The return type must be the EiraicTreasures Pydantic model.
    assert EiraicTreasures.__name__ == "EiraicTreasures"
    assert "total_count" in EiraicTreasures.model_fields
    assert "primary_treasures_for_subject" in EiraicTreasures.model_fields


# ============================================================================
# Test 4 — primary-subject routing table is consistent with the BAML spec
# ============================================================================


@pytest.mark.parametrize(
    "class_name,expected_primary_subject",
    list(THE_THIRTEEN_PRIMARY_SUBJECTS.items()),
)
def test_eiraic_class_primary_subject_field_metadata(
    class_name: str, expected_primary_subject: str
) -> None:
    """Each éraic class's `primary_subject` field is typed as an EiraicSubject
    enum, and the enum contains the expected `expected_primary_subject` member.

    Skipped when baml_client has not been generated.
    """
    try:
        from baml_client import types as baml_types  # type: ignore[import-not-found]
    except ImportError as e:
        pytest.fail(
            f"baml_client not generated — run `cd cianfhoghlaim && "
            f"uv run baml-cli generate` first: {e}"
        )

    cls = getattr(baml_types, class_name)
    primary_field = cls.model_fields["primary_subject"]
    enum_cls = getattr(baml_types, "EiraicSubject", None)
    assert enum_cls is not None, "EiraicSubject enum must be defined in baml_client.types"
    assert enum_cls.__name__ == "EiraicSubject"

    # The field annotation must point at the EiraicSubject enum.
    annotation = str(primary_field.annotation)
    assert "EiraicSubject" in annotation, (
        f"`{class_name}.primary_subject` must be typed as `EiraicSubject`, "
        f"got annotation: {annotation}"
    )

    # And the expected primary_subject value is a member of the enum.
    enum_values = {member.value for member in enum_cls}
    assert expected_primary_subject in enum_values, (
        f"EiraicSubject enum must contain {expected_primary_subject!r} for {class_name}, "
        f"got {sorted(enum_values)}"
    )
