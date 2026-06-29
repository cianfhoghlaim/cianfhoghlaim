"""
Tests for the University of Galway deep extraction pipeline
(Phase 7 of `university-of-galway-deep-extraction`).

Covers:
  - `cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory`
    (Pydantic config + factory + validation)
  - `cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.ie.education.university_of_galway_deep`
    (case-study wrapper)
  - `cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory`
    (SourceEntry + the new dispatch + the new university_deep_extraction kind)
  - `cianfhoghlaim.assets._oideachais_dagster_defs.assets.university_deep_extraction.uog_assets`
    (5 Dagster assets, group_name, compute_kind)
  - `cianfhoghlaim.embeddings._oideachais_src.university_embedding`
    (2 v1 CocoIndex Apps)
  - `cianfhoghlaim.cognify.rules.university_cross_archive`
    (4th cross-archive rule + title similarity + exact match)
  - `cianfhoghlaim.notebooks._oideachais.university_courses`
    (marimo notebook parses + has 4 tabs)

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest


# ============================================================================
# Factory: Pydantic config + validation
# ============================================================================


class TestUniversityDeepExtractionConfig:
    """The Pydantic v2 model that backs the factory."""

    def test_valid_config_accepted(self) -> None:
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory import (
            UniversityDeepExtractionConfig,
        )

        cfg = UniversityDeepExtractionConfig(
            university_id="ie-university-galway",
            institution_name="University of Galway",
            base_url="https://www.universityofgalway.ie",
            catalogue_paths=["/courses/**"],
            school_subdomain_paths=["/schools/computer-science/**"],
            handbook_root_path="/handbooks/2025-26/",
            academic_year=2025,
        )
        assert cfg.university_id == "ie-university-galway"
        assert cfg.academic_year == 2025
        assert cfg.prefer_free_browser is True  # default

    def test_missing_required_field_rejected(self) -> None:
        from pydantic import ValidationError

        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory import (
            UniversityDeepExtractionConfig,
        )

        # Omit `university_id` (the only field without a default) to
        # force a ValidationError on the required base fields.
        with pytest.raises(ValidationError) as exc_info:
            UniversityDeepExtractionConfig(  # type: ignore[call-arg]
                institution_name="Test",
                base_url="https://test.ie",
                handbook_root_path="/h/",
                academic_year=2025,
            )
        errors = " ".join(str(e["loc"]) for e in exc_info.value.errors())
        assert "university_id" in errors

    def test_bad_regex_rejected(self) -> None:
        from pydantic import ValidationError

        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory import (
            UniversityDeepExtractionConfig,
        )

        with pytest.raises(ValidationError):
            UniversityDeepExtractionConfig(
                university_id="test",
                institution_name="Test",
                base_url="https://test.ie",
                handbook_root_path="/h/",
                academic_year=2025,
                programme_code_regex="[unclosed",
            )

    def test_path_must_start_with_slash(self) -> None:
        from pydantic import ValidationError

        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory import (
            UniversityDeepExtractionConfig,
        )

        with pytest.raises(ValidationError):
            UniversityDeepExtractionConfig(
                university_id="test",
                institution_name="Test",
                base_url="https://test.ie",
                catalogue_paths=["courses/**"],  # missing leading /
                handbook_root_path="/h/",
                academic_year=2025,
            )

    def test_to_legacy_dict_round_trip(self) -> None:
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources._university_deep_factory import (
            UniversityDeepExtractionConfig,
        )

        cfg = UniversityDeepExtractionConfig(
            university_id="x",
            institution_name="X",
            base_url="https://x.ie",
            handbook_root_path="/h/",
            academic_year=2025,
        )
        d = cfg.to_legacy_dict()
        assert d["university_id"] == "x"
        assert d["academic_year"] == 2025
        # HttpUrl normalises URLs by adding a trailing slash; the
        # factory uses the normalised form.
        assert str(d["base_url"]).rstrip("/") == "https://x.ie"


# ============================================================================
# Case-study wrapper
# ============================================================================


class TestUoGCaseStudyWrapper:
    """The `ie.education.university_of_galway_deep` thin wrapper."""

    def test_uog_config_exposes_canonical_fields(self) -> None:
        # The case-study wrapper lives at the top level of
        # `_oideachais_dlt_sources` (not under `ie/education/` which
        # has a pre-existing broken `dlt_sources` import chain).
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.university_of_galway_deep import (  # type: ignore[no-redef]
            UOG_CONFIG,
        )

        assert UOG_CONFIG.university_id == "ie-university-galway"
        assert UOG_CONFIG.institution_name == "University of Galway"
        assert str(UOG_CONFIG.base_url).rstrip("/") == "https://www.universityofgalway.ie"
        assert UOG_CONFIG.academic_year == 2025
        assert UOG_CONFIG.programme_code_regex == r"[A-Z]{2,4}\d{3,4}"
        assert "/courses/**" in UOG_CONFIG.catalogue_paths
        assert "/schools/computer-science/**" in UOG_CONFIG.school_subdomain_paths

    def test_uog_source_name_format(self) -> None:
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.university_of_galway_deep import (  # type: ignore[no-redef]
            UOG_SOURCE_NAME,
            get_uog_source_name,
        )

        assert UOG_SOURCE_NAME == "university_ie-university-galway_deep"
        assert get_uog_source_name() == UOG_SOURCE_NAME

    def test_uog_deep_source_callable(self) -> None:
        from cianfhoghlaim.pipelines.ingest._oideachais_dlt_sources.university_of_galway_deep import (  # type: ignore[no-redef]
            university_of_galway_deep_source,
        )

        src = university_of_galway_deep_source()
        assert src is not None
        # The dlt source is a 0-arg callable (per the SourceFactory
        # convention).
        assert callable(src)


# ============================================================================
# SourceFactory dispatch
# ============================================================================


class TestSourceFactoryDispatch:
    """The `kind=university_deep_extraction` dispatch in source_factory.py."""

    def test_kind_literal_includes_new_kind(self) -> None:
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            SourceEntry,
            _KIND_DISPATCH,
        )

        assert "university_deep_extraction" in _KIND_DISPATCH
        # SourceEntry accepts the new kind.
        entry = SourceEntry(
            id="ie.university.galway",
            name="UoG",
            domain="education",
            nation="ie",
            kind="university_deep_extraction",
            urls=["https://www.universityofgalway.ie"],
            base_url="https://www.universityofgalway.ie",
            catalogue_paths=["/courses/**"],
            school_subdomain_paths=["/schools/computer-science/**"],
            handbook_root_path="/handbooks/2025-26/",
            academic_year=2025,
            asset_key=["ie", "education", "university", "galway", "deep"],
        )
        assert entry.kind == "university_deep_extraction"

    def test_builder_returns_callable(self) -> None:
        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            SourceEntry,
            _build_university_deep_source,
        )

        entry = SourceEntry(
            id="ie.university.galway",
            name="UoG",
            domain="education",
            nation="ie",
            kind="university_deep_extraction",
            urls=["https://www.universityofgalway.ie"],
            base_url="https://www.universityofgalway.ie",
            catalogue_paths=["/courses/**"],
            school_subdomain_paths=["/schools/computer-science/**"],
            handbook_root_path="/handbooks/2025-26/",
            academic_year=2025,
            asset_key=["ie", "education", "university", "galway", "deep"],
        )
        builder = _build_university_deep_source(entry, None)
        assert callable(builder)
        src = builder()
        assert src is not None
        assert src.name == "university_ie-university-galway_deep"

    def test_missing_required_field_rejected(self) -> None:
        from pydantic import ValidationError

        from cianfhoghlaim.core.dlt._oideachais_dlt_utils.source_factory import (
            SourceEntry,
        )

        with pytest.raises(ValidationError) as exc_info:
            SourceEntry(
                id="ie.university.test",
                name="Test",
                domain="education",
                nation="ie",
                kind="university_deep_extraction",
                urls=["https://test.ie"],
                # Missing base_url + handbook_root_path + academic_year.
                asset_key=["ie", "education", "test"],
            )
        msg = " ".join(str(e["loc"]) for e in exc_info.value.errors())
        assert "university_deep_extraction" in str(exc_info.value)


# ============================================================================
# 5 Dagster assets
# ============================================================================


class TestUoGAssets:
    """The 5 Dagster assets in the `university_deep_extraction` group."""

    def _load_assets(self) -> list:
        # Direct load bypassing the broken parent __init__.py.
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "uog_assets_test",
            "cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/uog_assets.py",
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["uog_assets_test"] = mod
        spec.loader.exec_module(mod)
        return mod.uog_assets

    def test_5_assets_present(self) -> None:
        assets = self._load_assets()
        assert len(assets) == 5
        names = {a.op.name for a in assets}
        assert names == {
            "uog__pre_research",
            "uog__bulk_scrape",
            "uog__extract_courses",
            "uog__extract_modules",
            "uog__extract_programmes",
        }

    def test_compute_kinds_match_spec(self) -> None:
        assets = self._load_assets()
        by_name = {a.op.name: a for a in assets}
        # 2 scrape assets
        assert by_name["uog__pre_research"].op.tags["dagster/compute_kind"] == "scrape"
        assert by_name["uog__bulk_scrape"].op.tags["dagster/compute_kind"] == "scrape"
        # 3 baml assets
        for n in (
            "uog__extract_courses",
            "uog__extract_modules",
            "uog__extract_programmes",
        ):
            assert by_name[n].op.tags["dagster/compute_kind"] == "baml"

    def test_asset_keys_match_spec(self) -> None:
        assets = self._load_assets()
        for a in assets:
            # `a.keys` is a list of AssetKey objects; the path is
            # the 2-tuple `["uog", "<subkey>"]`.
            key_paths = [list(k.path) for k in a.keys]
            expected = ["uog", a.op.name.replace("uog__", "")]
            assert key_paths == [expected], (
                f"Asset {a.op.name} has keys {key_paths}, expected [{expected}]"
            )


# ============================================================================
# 2 CocoIndex v1 Apps
# ============================================================================


class TestUniversityEmbeddingApps:
    """The 2 CocoIndex v1 Apps in `university_embedding.py`."""

    def test_module_imports(self) -> None:
        import importlib

        mod = importlib.import_module(
            "cianfhoghlaim.embeddings._oideachais_src.university_embedding"
        )
        assert mod.COCOINDEX_AVAILABLE is True
        assert mod.UniversityCoursesApp is not None
        assert mod.UniversityModulesApp is not None

    def test_app_names(self) -> None:
        import importlib

        mod = importlib.import_module(
            "cianfhoghlaim.embeddings._oideachais_src.university_embedding"
        )
        # The 2 v1 Apps are real `coco.App` instances. The name is
        # stored on the internal `_name` attribute (set from
        # `coco.AppConfig(name=...)`). The conformance linter reads
        # the same attribute.
        if mod.COCOINDEX_AVAILABLE:
            assert mod.UniversityCoursesApp._name == "UniversityCoursesApp"
            assert mod.UniversityModulesApp._name == "UniversityModulesApp"

    def test_ducklake_table_addresses(self) -> None:
        import importlib

        mod = importlib.import_module(
            "cianfhoghlaim.embeddings._oideachais_src.university_embedding"
        )
        assert "courses" in mod.UNIVERSITY_DUCKLAKE_TABLES
        assert "modules" in mod.UNIVERSITY_DUCKLAKE_TABLES
        assert "programmes" in mod.UNIVERSITY_DUCKLAKE_TABLES
        assert (
            mod.UNIVERSITY_DUCKLAKE_TABLES["courses"]
            == "oideachais.education.ie.university_courses"
        )
        assert (
            mod.UNIVERSITY_DUCKLAKE_TABLES["modules"]
            == "oideachais.education.ie.university_modules"
        )

    def test_search_helpers_present(self) -> None:
        import importlib

        mod = importlib.import_module(
            "cianfhoghlaim.embeddings._oideachais_src.university_embedding"
        )
        assert callable(mod.search_university_courses)
        assert callable(mod.search_university_modules)


# ============================================================================
# 4th cross-archive edge rule
# ============================================================================


class TestUniversityCrossArchiveRule:
    """The new `UoGArtifact-MATCHES-CourseDescriptor` rule."""

    def test_title_similarity(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            _title_similarity,
        )

        assert _title_similarity("Cryptography", "Cryptography") == 1.0
        assert _title_similarity("Cryptography", "CRYPTOGRAPHY") == 1.0
        assert _title_similarity("Software Engineering", "Software Engineer") < 1.0
        assert _title_similarity("Cryptography", "Statistics") == 0.0
        assert _title_similarity("", "Statistics") == 0.0

    def test_exact_course_code_match(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            _course_code_exact_match,
        )

        assert _course_code_exact_match("CT511", "CT511") == 1.0
        assert _course_code_exact_match("ct511", "CT511") == 1.0
        assert _course_code_exact_match("CT511", "HDSD") == 0.0

    def test_exact_code_match_emits_edge(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            build_uog_matches_course_descriptor_query,
        )

        uog = [
            {
                "file_hash": "h1",
                "course_code": "CT511",
                "module_title": "Software Engineering",
            }
        ]
        desc = [
            {
                "source_url": "https://www.universityofgalway.ie/ct511",
                "programme_code": "CT511",
                "course_title": "Software Engineering",
            }
        ]
        cypher, params = build_uog_matches_course_descriptor_query(uog, desc)
        assert cypher
        assert len(params["edges"]) == 1
        edge = params["edges"][0]
        assert edge["source"] == "h1"
        assert edge["target"] == "https://www.universityofgalway.ie/ct511"
        assert edge["match_confidence"] == 1.0
        assert edge["match_kind"] == "course_code_exact"

    def test_fuzzy_title_match_emits_edge(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            build_uog_matches_course_descriptor_query,
        )

        uog = [{"file_hash": "h2", "course_code": "", "module_title": "Software Engineering"}]
        desc = [
            {
                "source_url": "https://www.universityofgalway.ie/sweng",
                "programme_code": "SWENG",
                "course_title": "Software Engineering",
            }
        ]
        cypher, params = build_uog_matches_course_descriptor_query(uog, desc)
        assert cypher
        assert len(params["edges"]) == 1
        assert params["edges"][0]["match_kind"] == "fuzzy_title"

    def test_below_threshold_emits_no_edge(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            build_uog_matches_course_descriptor_query,
        )

        uog = [
            {"file_hash": "h3", "course_code": "MA335", "module_title": "Mathematical Statistics"}
        ]
        desc = [
            {
                "source_url": "https://www.universityofgalway.ie/bscmaths",
                "programme_code": "BScMS",
                "course_title": "Bachelor of Science (Mathematical Science)",
            }
        ]
        cypher, params = build_uog_matches_course_descriptor_query(uog, desc, fuzzy_threshold=0.85)
        # The fuzzy similarity between "Mathematical Statistics" and
        # "Bachelor of Science (Mathematical Science)" is 0.2 (well
        # below 0.85), so no edge is emitted.
        assert not cypher
        assert params == {}

    def test_empty_inputs(self) -> None:
        from cianfhoghlaim.cognify.rules.university_cross_archive import (
            build_uog_matches_course_descriptor_query,
        )

        cypher, params = build_uog_matches_course_descriptor_query([], [])
        assert not cypher
        assert params == {}


# ============================================================================
# Marimo notebook
# ============================================================================


class TestUniversityCoursesNotebook:
    """The marimo notebook with 4 tabs."""

    def test_notebook_parses(self) -> None:
        path = Path("cianfhoghlaim/notebooks/_oideachais/university_courses.py")
        assert path.is_file()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        # Find all @app.cell functions.
        cells = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.decorator_list
        ]
        assert len(cells) >= 4  # at least 4 cells (one per tab)

    def test_has_4_tabs(self) -> None:
        path = Path("cianfhoghlaim/notebooks/_oideachais/university_courses.py")
        src = path.read_text(encoding="utf-8")
        # Look for the 4 tab labels in the `tabs` dict.
        for label in (
            "1. M.Sc. AI 25/26 modules",
            "2. All UoG courses",
            "3. Reading lists",
            "4. Cross-archive",
        ):
            assert label in src, f"Missing tab label {label!r}"


# ============================================================================
# BAML file shape (smoke test)
# ============================================================================


class TestUniversityExtractionBAML:
    """The new BAML file has the expected 5 classes + 4 functions + 4 tests."""

    def test_baml_file_exists(self) -> None:
        path = Path("cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml")
        assert path.is_file()
        src = path.read_text(encoding="utf-8")

    def test_baml_5_classes(self) -> None:
        src = Path(
            "cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml"
        ).read_text(encoding="utf-8")
        for cls in (
            "class CourseDescriptor",
            "class ModuleDescriptor",
            "class ProgrammeDescriptor",
            "class LecturerInfo",
            "class ReadingListItem",
        ):
            assert cls in src, f"Missing BAML class {cls!r}"

    def test_baml_4_functions(self) -> None:
        src = Path(
            "cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml"
        ).read_text(encoding="utf-8")
        for fn in (
            "function ExtractCourseDescriptor(",
            "function ExtractModuleDescriptor(",
            "function ExtractProgrammeDescriptor(",
            "function ExtractReadingList(",
        ):
            assert fn in src, f"Missing BAML function {fn!r}"

    def test_baml_4_tests(self) -> None:
        src = Path(
            "cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml"
        ).read_text(encoding="utf-8")
        for test_name in (
            "test ExtractCourseDescriptorTest",
            "test ExtractModuleDescriptorTest",
            "test ExtractProgrammeDescriptorTest",
            "test ExtractReadingListTest",
        ):
            assert test_name in src, f"Missing BAML test {test_name!r}"

    def test_baml_uses_canonical_client(self) -> None:
        src = Path(
            "cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml"
        ).read_text(encoding="utf-8")
        # All 4 functions route through `ExtractEn` (the canonical
        # LiteLLM client; the gateway alias `extract-en` resolves to
        # gemini-2.5-flash → glm-4.6 → gemini-1.5-flash).
        assert src.count("client ExtractEn") == 4
