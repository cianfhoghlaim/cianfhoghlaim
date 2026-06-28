"""Tests for ``dlt_sources.official_media.source_resolver``.

Asserts the 4-lookup fan-out + override short-circuit.

  - Override short-circuit works (no network calls).
  - Offline stub mode (USE_LIVE_LOOKUPS unset) returns all-None
    resolved fields but the row is still well-formed.
  - The DLT row schema includes all 11 resolved fields.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from dlt_sources.official_media.source_resolver import (
    ResolvedSource,
    SourceResolver,
    override_title_for,
    source_resolver,
)

# ---------------------------------------------------------------------------
# Override short-circuit
# ---------------------------------------------------------------------------


def test_override_short_circuits_for_gchq() -> None:
    """The 4 network lookups are NOT made; the override fields are
    returned immediately."""
    resolver = SourceResolver()
    resolved = resolver.resolve("gchq", category="intelligence")
    assert resolved.official_website == "https://www.gchq.gov.uk"
    assert resolved.wikipedia_url == "https://en.wikipedia.org/wiki/GCHQ"
    assert resolved.resolver_notes == "override"


def test_override_short_circuits_case_insensitive() -> None:
    resolver = SourceResolver()
    resolved = resolver.resolve("GCHQ", category="intelligence")
    assert resolved.official_website == "https://www.gchq.gov.uk"


def test_override_normalises_leading_at() -> None:
    resolver = SourceResolver()
    resolved = resolver.resolve("@hmgcc", category="intelligence")
    assert resolved.official_website == "https://www.hmgcc.gov.uk"


# ---------------------------------------------------------------------------
# Offline stub mode (the CI default)
# ---------------------------------------------------------------------------


def test_offline_mode_returns_well_formed_row() -> None:
    """With USE_LIVE_LOOKUPS=false, non-override candidates return
    all-None resolved fields and resolver_notes='offline_stub'."""
    resolver = SourceResolver(live_lookups=False)
    resolved = resolver.resolve(
        "metpoliceuk", category="jurisdiction", candidate_id="metpoliceuk@test"
    )
    assert resolved.candidate_id == "metpoliceuk@test"
    assert resolved.ig_username == "metpoliceuk"
    assert resolved.official_website is None
    assert resolved.wikipedia_url is None
    assert resolved.companies_house_id is None
    assert resolved.mastodon_handle is None
    assert resolved.bluesky_handle is None
    assert resolved.resolver_notes == "offline_stub"


def test_resolved_source_to_dlt_row_has_all_fields() -> None:
    """The DLT row schema is stable: 11 fields, datetime serialised."""
    row = ResolvedSource(
        candidate_id="x",
        ig_username="x",
        category=None,
    ).to_dlt_row()
    expected_keys = {
        "candidate_id",
        "ig_username",
        "category",
        "official_website",
        "wikipedia_url",
        "wikipedia_extract",
        "companies_house_id",
        "companies_house_name",
        "cro_number",
        "mastodon_handle",
        "mastodon_url",
        "bluesky_handle",
        "bluesky_did",
        "bluesky_url",
        "resolved_at",
        "resolver_notes",
    }
    assert set(row.keys()) == expected_keys


# ---------------------------------------------------------------------------
# override_title_for helper
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "username, expected_title",
    [
        ("metpoliceuk", "Metpoliceuk"),
        ("met.police.uk", "Met Police Uk"),
        ("met_police_uk", "Met Police Uk"),
        ("gchq", "Gchq"),
        ("ucl", "Ucl"),
        ("hmgcc_official", "Hmgcc"),
        ("mi5_official", "Mi5"),
    ],
)
def test_override_title_for(username: str, expected_title: str) -> None:
    assert override_title_for(username) == expected_title


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------


def test_singleton_resolver_has_overrides() -> None:
    resolved = source_resolver.resolve("mi5official", category="intelligence")
    assert resolved.official_website == "https://www.mi5.gov.uk"
    assert "Crown body" in resolved.resolver_notes or resolved.resolver_notes == "override"


# ---------------------------------------------------------------------------
# Empty override path
# ---------------------------------------------------------------------------


def test_resolver_with_empty_overrides_dir(tmp_path: Path) -> None:
    """A resolver with no fixtures_dir returns all-None fields for
    non-override candidates, and the override is silently empty."""
    resolver = SourceResolver(fixtures_dir=tmp_path)
    resolved = resolver.resolve("gchq", category="intelligence")
    assert resolved.official_website is None
    assert resolved.resolver_notes == "offline_stub"
