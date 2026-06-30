"""
Test the canonical `oideachais/sources.yaml` registry.

- Loads the YAML via SourceFactory.
- Asserts every block has the required fields.
- Asserts every `nation` is in the allowlist.
- Asserts every `kind` is in the enum.
- Asserts every `asset_key` starts with `nation + domain`.
- Asserts every URL parses.
- Asserts the seven factory methods return coherent addresses.
"""
from __future__ import annotations

import re

import pytest

pytestmark = pytest.mark.integration


def test_factory_loads(sources_factory) -> None:
    f = sources_factory
    assert f is not None
    assert f.spec.version == 2
    # We have all 8 nations in the allowlist.
    assert {n.code for n in f.spec.nations} == {"ie", "ni", "en", "sct", "wls", "iom", "jey", "ggy"}
    # Kinds match the enum.
    expected_kinds = {
        "firecrawl_pages",
        "stagehand_papers",
        "browserbase_extract",
        "api_table",
        "api_xml",
        "filesystem_csv",
        "filesystem_parquet",
    }
    assert set(f.spec.kinds) == expected_kinds


def test_every_id_matches_nation_domain(sources_factory) -> None:
    """Every `sources[].id` is `{{nation}}.{{domain}}.{{entity}}` and the
    id's nation/domain match the entry's `nation`/`domain` fields."""
    f = sources_factory
    for entry in f.spec.sources:
        parts = entry.id.split(".")
        assert len(parts) == 3, f"{entry.id!r} must have 3 dot-separated parts"
        assert parts[0] == entry.nation, f"{entry.id}: id nation {parts[0]} != {entry.nation}"
        assert parts[1] == entry.domain, f"{entry.id}: id domain {parts[1]} != {entry.domain}"


def test_every_asset_key_starts_with_nation_domain(sources_factory) -> None:
    f = sources_factory
    for entry in f.spec.sources:
        assert entry.asset_key[:2] == [entry.nation, entry.domain], (
            f"{entry.id}: asset_key {entry.asset_key!r} must start with "
            f"[{entry.nation}, {entry.domain}]"
        )


def test_every_url_is_http_or_template(sources_factory) -> None:
    f = sources_factory
    pattern = re.compile(r"^https?://[^\s/$.?#].[^\s]*$|^https?://[^/]*\{[^/]+\}.*$")
    for entry in f.spec.sources:
        for url in entry.urls:
            assert pattern.match(url) or "{year}" in url or "{number}" in url, (
                f"{entry.id}: url {url!r} does not look like a real URL"
            )


def test_law_domain_is_statutory_only(sources_factory) -> None:
    """User decision: `law/` is statutory only. Reject any non-statutory entry."""
    f = sources_factory
    law = f.filter(domain="law")
    assert law, "expected at least one law source"
    for entry in law:
        # Statutory = `legislation` (api_xml) or `doj` / `lawreform` (firecrawl_pages).
        assert entry.kind in {"api_xml", "firecrawl_pages"}, (
            f"{entry.id}: law domain is statutory only; got kind {entry.kind!r}"
        )
        assert "courts" not in entry.id, (
            f"{entry.id}: case law is reserved for the future 'case-law-and-precedent' change"
        )


def test_seven_methods_are_coherent(sources_factory) -> None:
    """For each id, the seven method outputs are mutually consistent."""
    f = sources_factory
    for entry in f.spec.sources:
        # lance_table embeds `nation` and `domain` (order may be `.nation.domain.entity`
        # for `oideachais.education.ie.ncca_pages` or `.entity.nation.domain` for
        # `oideachais.{nation}.{domain}.{entity}`). Both forms contain both.
        lt = f.lance_table(entry.id)
        assert "oideachais" in lt
        assert entry.nation in lt
        assert entry.domain in lt
        # cognee_dataset is oideachais_{domain}_{nation} (or explicit override)
        ds = f.cognee_dataset(entry.id)
        assert ds.startswith("oideachais_"), ds
        if entry.kg and entry.kg.dataset:
            # explicit override; just sanity-check it starts with the prefix
            continue
        assert entry.nation in ds and entry.domain in ds, (
            f"cognee_dataset({entry.id!r}) = {ds!r} must contain both nation and domain"
        )
        # marimo_path & tests_path live under the canonical subtrees
        mp = f.marimo_path(entry.id)
        assert str(mp).startswith("oideachais/notebooks/dashboards/"), mp
        assert entry.nation in str(mp) and entry.domain in str(mp)
        tp = f.tests_path(entry.id)
        assert str(tp).startswith("oideachais/tests/dlt_sources/"), tp
        assert entry.nation in str(tp) and entry.domain in str(tp)
        # asset_key accessor returns the same tuple
        assert f.asset_key(entry.id) == entry.asset_key


def test_unknown_id_raises(sources_factory) -> None:
    f = sources_factory
    with pytest.raises(KeyError):
        f.get("xy.education.foo")


def test_source_factory_rejects_malformed_yaml(tmp_path) -> None:
    """A YAML file with an unknown nation must raise pydantic.ValidationError."""
    from cianfhoghlaim.dlt.source_factory import SourceFactory
    from pydantic import ValidationError

    bad = tmp_path / "bad.yaml"
    bad.write_text(
        """
version: 2
nations:
  - { code: xx, name: "Nowhere", jurisdiction: "nowhere" }
kinds: [firecrawl_pages]
sources:
  - id: xx.education.foo
    name: Bad
    domain: education
    nation: xx
    kind: firecrawl_pages
    urls: ["https://example.com"]
    asset_key: [xx, education, foo]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        SourceFactory.from_yaml(bad)
