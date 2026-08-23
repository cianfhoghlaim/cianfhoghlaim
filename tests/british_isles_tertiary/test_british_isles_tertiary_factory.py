"""Tests for the British Isles tertiary factory."""

from __future__ import annotations

import pytest


def test_bitertiary_config_validates_paths_starting_with_slash():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        BINation,
        BITertiaryDeepExtractionConfig,
    )

    with pytest.raises(ValueError):
        BITertiaryDeepExtractionConfig(
            university_id="ie-mu",
            institution_name="Maynooth University",
            base_url="https://www.maynoothuniversity.ie",
            nation=BINation.IE,
            catalogue_paths=["study/**"],
        )


def test_bitertiary_factory_emits_5_resources_for_public_only():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        BINation,
        BITertiaryDeepExtractionConfig,
        bitertiary_universities_factory,
    )

    cfg = BITertiaryDeepExtractionConfig(
        university_id="gb-uni-of-york",
        institution_name="University of York",
        base_url="https://www.york.ac.uk",
        nation=BINation.GB_ENG,
        sso_required=False,
    )
    source = bitertiary_universities_factory(cfg)()
    resources = list(source.selected_resources.values())
    names = {r.name for r in resources}
    assert {
        "bitertiary_course_pages",
        "bitertiary_module_pages",
        "bitertiary_programme_pages",
        "bitertiary_handbook_pdfs",
        "bitertiary_official_documents",
    }.issubset(names)
    assert "bitertiary_exam_papers" not in names


def test_bitertiary_qub_source_offers_sso():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        bitertiary_qub_source,
    )

    source = bitertiary_qub_source()()
    resources = list(source.selected_resources.values())
    names = {r.name for r in resources}
    # QUB has sso_required=True → 6 resources including exam_papers
    assert "bitertiary_exam_papers" in names
    assert "bitertiary_official_documents" in names


def test_bitertiary_ulster_source_offers_no_sso():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        bitertiary_ulster_source,
    )

    source = bitertiary_ulster_source()()
    resources = list(source.selected_resources.values())
    names = {r.name for r in resources}
    assert "bitertiary_exam_papers" not in names
    assert "bitertiary_official_documents" in names


def test_bitertiary_level_system_autosets_from_nation():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        BINation,
        BITertiaryDeepExtractionConfig,
    )

    cfg_ie = BITertiaryDeepExtractionConfig(
        university_id="ie-uog",
        institution_name="UoG",
        base_url="https://www.universityofgalway.ie",
        nation=BINation.IE,
    )
    assert cfg_ie.level_system == "NFQ"

    cfg_sct = BITertiaryDeepExtractionConfig(
        university_id="gb-edinburgh",
        institution_name="University of Edinburgh",
        base_url="https://www.ed.ac.uk",
        nation=BINation.GB_SCT,
    )
    assert cfg_sct.level_system == "SCQF"


def test_bitertiary_factory_idempotent():
    from dlt_sources.british_isles.university.british_isles_tertiary_factory import (
        BINation,
        BITertiaryDeepExtractionConfig,
        bitertiary_universities_factory,
    )

    cfg = BITertiaryDeepExtractionConfig(
        university_id="gb-uni-of-york",
        institution_name="University of York",
        base_url="https://www.york.ac.uk",
        nation=BINation.GB_ENG,
    )
    s1 = bitertiary_universities_factory(cfg)()
    s2 = bitertiary_universities_factory(cfg)()
    assert s1 is not s2
