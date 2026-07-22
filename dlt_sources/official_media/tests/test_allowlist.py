"""Tests for ``cianfhoghlaim.dlt.official_media.allowlist``.

Asserts the two-stage filter:

  Stage 1: a username in any of the 4 allowlist YAMLs is classified
           as official at stage 1.
  Stage 2: a username NOT in any allowlist is rejected by the cheap
           heuristic and BAML is NOT invoked (unless the heuristic
           matches).
"""
from __future__ import annotations

import pytest
from dlt_sources.official_media.allowlist import (
    AllowlistFilter,
    allowlist_filter,
)

# ---------------------------------------------------------------------------
# Stage 1: positive cases (in the allowlist)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "username, expected_category",
    [
        ("mi5official", "intelligence"),
        ("MI5OFFICIAL", "intelligence"),  # case-insensitive
        ("@gchq", "intelligence"),  # leading @ stripped
        ("universityofgalway", "university"),
        ("queensuniversitybelfast", "university"),
        ("ucl", "university"),
        ("fiannafailparty", "party"),
        ("dupofficial", "party"),
        ("labourparty", "party"),
        ("libdems", "party"),
        ("govireland", "jurisdiction"),
        ("metpoliceuk", "jurisdiction"),
        ("britisharmy", "jurisdiction"),
        ("hmgcc", "intelligence"),
    ],
)
def test_allowlist_stage1_positive(
    username: str, expected_category: str
) -> None:
    match = allowlist_filter.lookup(username)
    assert match is not None
    assert match.is_official is True
    assert match.stage == 1
    assert match.category == expected_category


# ---------------------------------------------------------------------------
# Stage 1: negative cases (not in the allowlist)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "username",
    [
        "personal_friend_1",
        "nancy19890527",
        "reba_1070",
        "i_am_uk7",
        "emma_watson_fans_page22",
        "carlcashman91",
        "cormlyons",
    ],
)
def test_allowlist_stage1_negative(username: str) -> None:
    match = allowlist_filter.lookup(username)
    assert match is None


# ---------------------------------------------------------------------------
# Stage 2: cheap heuristic gate
# ---------------------------------------------------------------------------


def test_heuristic_rejects_obvious_personal_account() -> None:
    match = allowlist_filter.classify(
        "i_am_uk7",
        bio="Just here for photos of my dog 🐶",
        external_url="",
    )
    assert match.is_official is False
    assert match.source == "heuristic_reject"


def test_heuristic_accepts_gov_url_for_baml_review() -> None:
    match = allowlist_filter.classify(
        "unknown_agency_2024",
        bio="A new government agency",
        external_url="https://www.example.gov.uk",
    )
    assert match.is_official is False  # No BAML configured
    assert match.source == "heuristic_only_no_baml"


def test_classify_returns_stage1_when_in_allowlist() -> None:
    match = allowlist_filter.classify(
        "gchq",
        bio="",
        external_url="",
    )
    assert match.is_official is True
    assert match.stage == 1
    assert match.category == "intelligence"


# ---------------------------------------------------------------------------
# Stage 2: BAML fallback (with a stub classifier)
# ---------------------------------------------------------------------------


def test_baml_fallback_accepts_high_confidence() -> None:
    """A stub BAML classifier returns is_official=True with
    confidence=0.9; the filter accepts at stage 2."""

    def stub_baml(ig_username: str, ig_bio: str, ig_external_url: str) -> dict:
        return {
            "is_official_media": True,
            "confidence": 0.9,
            "category": "agency",
            "reason": f"looks like a government account: {ig_username}",
        }

    filt = AllowlistFilter(baml_classifier=stub_baml, confidence_threshold=0.7)
    match = filt.classify(
        "met_police_new_account",
        bio="The official new Metropolitan Police account",
        external_url="",
    )
    assert match.is_official is True
    assert match.stage == 2
    assert match.category == "agency"
    assert match.source == "baml_classifier"


def test_baml_fallback_rejects_low_confidence() -> None:
    def stub_baml(ig_username: str, ig_bio: str, ig_external_url: str) -> dict:
        return {
            "is_official_media": True,
            "confidence": 0.4,
            "category": "agency",
            "reason": "uncertain",
        }

    filt = AllowlistFilter(baml_classifier=stub_baml, confidence_threshold=0.7)
    match = filt.classify(
        "met_police_new_account",
        bio="The official new Metropolitan Police account",
        external_url="",
    )
    assert match.is_official is False
    assert match.source.startswith("baml_reject_conf_0.40")


def test_baml_fallback_swallows_exceptions() -> None:
    def stub_baml(ig_username: str, ig_bio: str, ig_external_url: str) -> dict:
        raise RuntimeError("LiteLLM gateway is down")

    filt = AllowlistFilter(baml_classifier=stub_baml)
    match = filt.classify(
        "met_police_new_account",
        bio="official",
        external_url="",
    )
    assert match.is_official is False
    assert match.source == "heuristic_only_no_baml"


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def test_filter_size_matches_yaml_entries() -> None:
    """The filter should load at least 50 entries across the 4 YAMLs."""
    assert allowlist_filter.size >= 50


def test_filter_categories_returns_at_least_4_buckets() -> None:
    cats = allowlist_filter.categories()
    assert set(cats.keys()) >= {
        "intelligence",
        "university",
        "party",
        "jurisdiction",
    }
