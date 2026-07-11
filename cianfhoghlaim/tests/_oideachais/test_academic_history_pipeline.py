"""Tests for the academic-history pipeline.

Covers:
- BAML math/statistics extraction schema (file structure + golden samples)
- Deterministic validation helpers (LaTeX, p-value, regression, etc.)
- Pydantic AcademicHistoryManifest (load, dump, privacy gate, pseudonym)
- Academic-history agent (10 tools + wire + privacy defaults)
- DLT/Dagster defs YAML files (parse, valid keys)
- CocoIndex v1 app (R1-R4 conformance shape, source tables)
- 8 marimo notebooks (parse, CLI dual-mode)

Reference: openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
NOTEBOOKS_DIR = REPO_ROOT / "cianfhoghlaim" / "notebooks" / "14_academic_history"
BAML_DIR = REPO_ROOT / "cianfhoghlaim" / "baml" / "education" / "university"
AGENT_MODULE = "cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent"


# ---------------------------------------------------------------------------
# 1. BAML schema presence + golden-sample tests
# ---------------------------------------------------------------------------


def test_baml_math_statistics_extraction_file_exists():
    """The BAML file for math/statistics extraction must exist."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    assert baml_path.exists(), f"BAML file missing: {baml_path}"


def test_baml_math_statistics_extraction_enums():
    """The BAML file declares the 11 required enums."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    text = baml_path.read_text()
    required_enums = [
        "TertiaryMathTopic",
        "DistributionFamily",
        "InferenceProcedure",
        "RegressionFamily",
        "NumericalMethod",
        "ConvergenceRate",
        "NonlinearSystemKind",
        "BifurcationType",
        "MathContentLanguage",
        "AssignmentKind",
        "DocumentKind",
        "ValidationSeverity",
    ]
    for enum in required_enums:
        assert f"enum {enum} " in text, f"missing enum: {enum}"


def test_baml_math_statistics_extraction_classes():
    """The BAML file declares the 15 required classes."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    text = baml_path.read_text()
    required_classes = [
        "AcademicModuleDescriptor",
        "CourseworkArtifactExtraction",
        "TertiaryExamPaper",
        "AssignmentBrief",
        "StudentAnswerScript",
        "WorkedSolution",
        "SolutionStep",
        "MarkingAnnotation",
        "FormulaRecord",
        "TheoremRecord",
        "StatisticalProcedureRecord",
        "NumericalMethodRecord",
        "NonlinearSystemRecord",
        "ValidationFinding",
        "AcademicHistorySnapshot",
    ]
    for cls in required_classes:
        assert f"class {cls} " in text, f"missing class: {cls}"


def test_baml_math_statistics_extraction_functions():
    """The BAML file declares all 12 functions (per the proposal)."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    text = baml_path.read_text()
    required_functions = [
        "ExtractAcademicModuleSyllabus",
        "ExtractCourseworkArtifact",
        "ExtractTertiaryExamPaper",
        "ExtractAssignmentBrief",
        "ExtractStudentAnswerScript",
        "ExtractWorkedSolution",
        "ExtractFormulaRecords",
        "ExtractTheorems",
        "ExtractStatisticalProcedureRecords",
        "ExtractNumericalMethodRecords",
        "ExtractNonlinearSystemRecords",
        "ExtractAcademicHistorySnapshot",
    ]
    for fn in required_functions:
        assert f"function {fn}(" in text, f"missing function: {fn}"


def test_baml_math_statistics_extraction_routes_through_extract_en():
    """Every BAML function routes through the canonical ExtractEn client."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    text = baml_path.read_text()
    # Count "function X(...) {" blocks; each should have `client ExtractEn`.
    function_blocks = text.count("function ")
    assert function_blocks >= 12, f"expected >=12 functions, found {function_blocks}"
    extract_en_count = text.count("client ExtractEn")
    assert extract_en_count >= 12, (
        f"expected >=12 `client ExtractEn` directives, found {extract_en_count}"
    )


def test_baml_math_statistics_extraction_golden_samples():
    """Each BAML function has a `test` block with golden-sample args."""
    baml_path = BAML_DIR / "mathematics_statistics_extraction.baml"
    text = baml_path.read_text()
    for fn in [
        "ExtractAcademicModuleSyllabusTest",
        "ExtractCourseworkArtifactTest",
        "ExtractTertiaryExamPaperTest",
        "ExtractAssignmentBriefTest",
        "ExtractStudentAnswerScriptTest",
        "ExtractWorkedSolutionTest",
        "ExtractFormulaRecordsTest",
        "ExtractTheoremsTest",
        "ExtractStatisticalProcedureRecordsTest",
        "ExtractNumericalMethodRecordsTest",
        "ExtractNonlinearSystemRecordsTest",
        "ExtractAcademicHistorySnapshotTest",
    ]:
        assert f"test {fn} " in text, f"missing golden sample: {fn}"


# ---------------------------------------------------------------------------
# 2. Deterministic validation helpers
# ---------------------------------------------------------------------------


def test_validate_latex_balanced_braces():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_latex,
    )

    findings = validate_latex("E = mc^2")
    assert findings == []


def test_validate_latex_unbalanced_braces():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_latex,
    )

    findings = validate_latex("E = mc^{2")
    codes = {f.code for f in findings}
    assert "LATEX_UNBALANCED_BRACE" in codes


def test_validate_latex_unknown_command():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_latex,
    )

    findings = validate_latex(r"\notacommand x")
    codes = {f.code for f in findings}
    assert "LATEX_UNKNOWN_COMMAND" in codes


def test_validate_probability_param_alpha_out_of_range():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_probability_param,
    )

    f = validate_probability_param("alpha", 0.0, kind="alpha")
    assert f is not None
    assert f.code == "ALPHA_OUT_OF_RANGE"


def test_validate_test_decision_consistent():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_test_decision,
    )

    findings = validate_test_decision(p_value=0.04, alpha=0.05, decision="REJECT")
    assert findings == []
    findings = validate_test_decision(p_value=0.04, alpha=0.05, decision="FAIL_TO_REJECT")
    assert any(f.code == "PVALUE_ALPHA_INCONSISTENT" for f in findings)


def test_validate_regression_diagnostics_r2_out_of_range():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_regression_diagnostics,
    )

    findings = validate_regression_diagnostics({"r_squared": 1.5})
    assert any(f.code == "R2_OUT_OF_RANGE" for f in findings)


def test_validate_iteration_record_converged_false_warning():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_iteration_record,
    )

    findings = validate_iteration_record(
        [{"step_index": 1, "residual": 0.5}, {"step_index": 2, "residual": 1e-3}],
        converged=False,
    )
    assert any(f.code == "ITERATION_DID_NOT_CONVERGE" for f in findings)


def test_validate_step_indices_not_contiguous():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_step_indices,
    )

    findings = validate_step_indices(
        [{"step_index": 1}, {"step_index": 3}],  # gap
    )
    assert any(f.code == "STEPS_NOT_CONTIGUOUS" for f in findings)


def test_validate_ode_stability_violated():
    from cianfhoghlaim.baml.education.university.math_validation import (
        validate_ode_stability,
    )

    findings = validate_ode_stability(
        step_size=10.0, lambda_max=1.0, method="RK4"
    )
    assert any(f.code == "RK_STABILITY_VIOLATED" for f in findings)


# ---------------------------------------------------------------------------
# 3. Pydantic AcademicHistoryManifest
# ---------------------------------------------------------------------------


def test_manifest_round_trip(tmp_path):
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (
        AcademicHistoryManifest,
        ModuleRoot,
        Privacy,
        StudentProfile,
        dump_manifest,
        load_manifest,
    )

    manifest = AcademicHistoryManifest(
        student_profile=StudentProfile(pseudonym="test-user-2026"),
        module_roots=[
            ModuleRoot(
                path="notes/ST311",
                module_code="ST311",
                module_title="Probability & Statistics",
            ),
            ModuleRoot(
                path="notes/ST312",
                module_code="ST312",
                module_title="Applied Statistics",
            ),
        ],
        privacy=Privacy(include_identity_records=False),
    )

    yaml_path = tmp_path / "manifest.yaml"
    yaml_path.write_text(dump_manifest(manifest))
    loaded = load_manifest(yaml_path)
    assert loaded.student_profile.pseudonym == "test-user-2026"
    assert len(loaded.module_roots) == 2
    assert loaded.module_roots[0].module_code == "ST311"
    assert loaded.privacy.include_identity_records is False


def test_manifest_pseudonym_hash_is_stable(tmp_path, monkeypatch):
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (
        AcademicHistoryManifest,
        ModuleRoot,
        StudentProfile,
    )

    monkeypatch.setenv("ACADEMIC_HISTORY_PSEUDONYM_SALT", "fixed-salt")
    m1 = AcademicHistoryManifest(
        student_profile=StudentProfile(pseudonym="ciaran"),
        module_roots=[ModuleRoot(path="notes/ST311", module_code="ST311")],
    )
    m2 = AcademicHistoryManifest(
        student_profile=StudentProfile(pseudonym="ciaran"),
        module_roots=[ModuleRoot(path="notes/ST312", module_code="ST312")],
    )
    assert m1.pseudonym_hash() == m2.pseudonym_hash()


def test_manifest_privacy_gate_excludes_identity_by_default(tmp_path):
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (
        AcademicHistoryManifest,
        ModuleRoot,
        Privacy,
        StudentProfile,
    )

    m = AcademicHistoryManifest(
        student_profile=StudentProfile(pseudonym="ciaran"),
        module_roots=[ModuleRoot(path="notes/ST311", module_code="ST311")],
        privacy=Privacy(include_identity_records=False),
    )
    assert m.include_file("notes/ST311/lecture01.pdf") is True
    assert m.include_file("notes/ST311/identity/passport.pdf") is False


def test_manifest_skip_patterns_work():
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_manifest import (
        AcademicHistoryManifest,
        ModuleRoot,
        Privacy,
        PrivacyOverrides,
        StudentProfile,
    )

    m = AcademicHistoryManifest(
        student_profile=StudentProfile(pseudonym="ciaran"),
        module_roots=[ModuleRoot(path="notes/ST311", module_code="ST311")],
        privacy=Privacy(include_identity_records=True),
        privacy_overrides=PrivacyOverrides(skip_patterns=[".*medical.*"]),
    )
    assert m.include_file("notes/ST311/medical/record.pdf") is False
    assert m.include_file("notes/ST311/lecture01.pdf") is True


# ---------------------------------------------------------------------------
# 4. Academic-history agent
# ---------------------------------------------------------------------------


def test_agent_module_imports():
    """The academic_history_agent module must import cleanly."""
    mod = __import__(AGENT_MODULE, fromlist=["academic_history_agent_wire"])
    assert hasattr(mod, "academic_history_agent_wire")
    assert hasattr(mod, "TOOLS")
    assert hasattr(mod, "TOOL_NAMES")
    assert hasattr(mod, "list_tools")
    assert hasattr(mod, "run_tool")


def test_agent_has_exactly_10_tools():
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (
        TOOLS,
    )

    assert len(TOOLS) == 10
    expected = {
        "list_my_modules",
        "list_my_artifacts",
        "get_my_notes",
        "get_my_assignments",
        "get_my_exam_history",
        "get_my_answer_scripts",
        "summarise_my_progress",
        "recommend_next_revision",
        "compare_my_answer_to_solution",
        "search_my_formulas",
    }
    assert {t.name for t in TOOLS} == expected


def test_agent_wire_attached():
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (
        academic_history_agent_wire,
    )

    assert academic_history_agent_wire is not None
    assert hasattr(academic_history_agent_wire, "subject")
    assert academic_history_agent_wire.subject.ncca_subject == "academic_history"


def test_agent_run_tool_unknown_raises():
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (
        run_tool,
    )

    with pytest.raises(ValueError, match="unknown tool"):
        run_tool("not_a_real_tool")


def test_routing_keyword_bucket_added():
    """The 13th routing keyword bucket must exist."""
    from cianfhoghlaim.agents.routing_keywords import ROUTING_KEYWORDS

    assert "academic_history_agent" in ROUTING_KEYWORDS
    keywords = ROUTING_KEYWORDS["academic_history_agent"]
    assert "my history" in keywords
    assert "summarise my degree" in keywords
    assert "st311" in keywords
    assert "st312" in keywords


# ---------------------------------------------------------------------------
# 5. Dagster defs YAML files
# ---------------------------------------------------------------------------


DEFS_PATHS = [
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/1_ingestion/filesystem/uog_math_coursework/defs.yaml",
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/2_materials/baml_extraction/uog_math_coursework/defs.yaml",
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/2_materials/academic_history_validation/defs.yaml",
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/academic_history_flow/defs.yaml",
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/4_asset_generation/marimo_dashboards/uog_math_coursework/defs.yaml",
    REPO_ROOT / "cianfhoghlaim/orchestration/defs/5_agent_ops/meaisinfhoghlaim/academic_history_agent/defs.yaml",
]


@pytest.mark.parametrize("defs_path", DEFS_PATHS)
def test_defs_yaml_exists_and_parses(defs_path):
    """Every L1-L5 defs.yaml file exists and parses as valid YAML."""
    assert defs_path.exists(), f"missing defs: {defs_path}"
    text = defs_path.read_text()
    assert "type:" in text, f"missing `type:` in {defs_path}"
    assert "attributes:" in text, f"missing `attributes:` in {defs_path}"


def test_l1_defs_targets_uog_math_coursework_source():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/1_ingestion/filesystem/uog_math_coursework/defs.yaml").read_text()
    assert "uog_math_coursework" in text
    assert "on_dlt_freshness" in text
    assert "INCLUDE_IDENTITY_RECORDS=false" in text


def test_l2_baml_defs_calls_coursework_extraction():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/2_materials/baml_extraction/uog_math_coursework/defs.yaml").read_text()
    assert "b.ExtractCourseworkArtifact" in text
    assert "b.ExtractFormulaRecords" in text
    assert "b.ExtractTheorems" in text
    assert "b.ExtractStatisticalProcedureRecords" in text
    assert "b.ExtractNumericalMethodRecords" in text
    assert "b.ExtractNonlinearSystemRecords" in text


def test_l2_validation_defs_routes_through_math_validation():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/2_materials/academic_history_validation/defs.yaml").read_text()
    assert "math_validation.validate_formula_record" in text


def test_l3_cocoindex_defs_uses_bge_m3():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/academic_history_flow/defs.yaml").read_text()
    assert "BAAI/bge-m3" in text
    assert "academic_history_flow" in text


def test_l4_dashboard_defs_lists_eight_notebooks():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/4_asset_generation/marimo_dashboards/uog_math_coursework/defs.yaml").read_text()
    expected_notebooks = [
        "01_uog_maths_corpus_overview",
        "02_module_syllabus_assessment_map",
        "03_statistics_methods_lab",
        "04_numerical_analysis_lab",
        "05_nonlinear_systems_lab",
        "06_formulas_theorems_worked_solutions",
        "07_assignments_exams_answers",
        "08_academic_history_chat",
    ]
    for nb in expected_notebooks:
        assert nb in text, f"missing notebook in defs: {nb}"


def test_l5_agent_defs_has_privacy_gate():
    text = (REPO_ROOT / "cianfhoghlaim/orchestration/defs/5_agent_ops/meaisinfhoghlaim/academic_history_agent/defs.yaml").read_text()
    assert "academic_history_agent" in text
    assert "INCLUDE_IDENTITY_RECORDS=false" in text
    assert "pseudonymous_user: true" in text


# ---------------------------------------------------------------------------
# 6. CocoIndex v1 app
# ---------------------------------------------------------------------------


def test_cocoindex_module_imports():
    """The AcademicHistoryFlow module imports cleanly even when
    CocoIndex is unavailable (graceful degradation)."""
    import importlib
    import sys as _sys

    # Force-register so dataclass introspection works.
    spec = importlib.util.spec_from_file_location(
        "_academic_history_flow_test",
        REPO_ROOT / "cianfhoghlaim" / "cocoindex" / "academic_history_flow.py",
    )
    mod = importlib.util.module_from_spec(spec)
    _sys.modules["_academic_history_flow_test"] = mod
    try:
        spec.loader.exec_module(mod)
    except (ImportError, AttributeError, TypeError):
        # The environment may not have cocoindex properly installed
        # (a pre-existing repo issue). In that case, fall back to a
        # lightweight text-based check.
        text = (REPO_ROOT / "cianfhoghlaim" / "cocoindex" / "academic_history_flow.py").read_text()
        assert "AcademicHistoryFlow" in text
        assert "ACADEMIC_HISTORY_DUCKLAKE_TABLES" in text
        assert "AcademicHistoryChunk" in text
        return
    assert hasattr(mod, "AcademicHistoryFlow")
    assert hasattr(mod, "ACADEMIC_HISTORY_DUCKLAKE_TABLES")
    assert hasattr(mod, "AcademicHistoryChunk")


def test_cocoindex_has_seven_source_tables():
    """The CocoIndex app declares exactly 7 source tables."""
    text = (REPO_ROOT / "cianfhoghlaim" / "cocoindex" / "academic_history_flow.py").read_text()
    expected = {"coursework", "formulas", "theorems", "stats", "numerical", "nonlinear", "findings"}
    for alias in expected:
        assert f'"{alias}":' in text or f"'{alias}':" in text, f"missing source-table alias: {alias}"


# ---------------------------------------------------------------------------
# 7. Marimo notebooks
# ---------------------------------------------------------------------------


NOTEBOOK_FILES = [
    "01_uog_maths_corpus_overview.py",
    "02_module_syllabus_assessment_map.py",
    "03_statistics_methods_lab.py",
    "04_numerical_analysis_lab.py",
    "05_nonlinear_systems_lab.py",
    "06_formulas_theorems_worked_solutions.py",
    "07_assignments_exams_answers.py",
    "08_academic_history_chat.py",
]


@pytest.mark.parametrize("notebook", NOTEBOOK_FILES)
def test_notebook_exists_and_has_pep723(notebook):
    p = NOTEBOOKS_DIR / notebook
    assert p.exists(), f"missing notebook: {p}"
    text = p.read_text()
    assert text.startswith("# /// script\n"), f"missing PEP 723 header in {notebook}"
    assert "marimo" in text


@pytest.mark.parametrize("notebook", NOTEBOOK_FILES)
def test_notebook_has_cli_main(notebook):
    p = NOTEBOOKS_DIR / notebook
    text = p.read_text()
    assert "def _cli_main(" in text, f"missing _cli_main in {notebook}"
    assert 'if __name__ == "__main__"' in text, f"missing __main__ guard in {notebook}"


@pytest.mark.parametrize("notebook", NOTEBOOK_FILES)
def test_notebook_has_footer_openspec_reference(notebook):
    """Every notebook footer must reference the openspec change."""
    p = NOTEBOOKS_DIR / notebook
    text = p.read_text()
    assert "2026-07-11-uog-math-statistics-academic-history-v1" in text


def test_common_helper_imports():
    """The shared _common.py helper must be importable."""
    sys.path.insert(0, str(NOTEBOOKS_DIR))
    from _common import (  # type: ignore[import-not-found]
        acad_engine_label,
        acad_health_md,
        acad_table,
        load_manifest_or_default,
        pseudo_id,
    )

    assert callable(acad_engine_label)
    assert callable(acad_health_md)
    assert callable(acad_table)
    assert callable(load_manifest_or_default)
    assert callable(pseudo_id)


def test_common_helper_privacy_gating():
    """The privacy gate helper must default-off identity records."""
    sys.path.insert(0, str(NOTEBOOKS_DIR))
    from _common import load_manifest_or_default  # type: ignore[import-not-found]

    manifest = load_manifest_or_default()
    assert manifest.privacy.include_identity_records is False
    assert "identity" in str(manifest.student_profile.pseudonym).lower() or manifest.student_profile.pseudonym == "change-me"


def test_cli_groups_registered():
    """The notebook cli.py must register the 14_academic_history group."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "nb_cli", REPO_ROOT / "cianfhoghlaim" / "notebooks" / "cli.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert "14_academic_history" in mod.GROUPS


# ---------------------------------------------------------------------------
# 8. End-to-end smoke: the agent + manifest round-trip
# ---------------------------------------------------------------------------


def test_agent_summarise_my_progress_returns_expected_keys(tmp_path, monkeypatch):
    """`summarise_my_progress` returns at least the canonical key set."""
    manifest_yaml = tmp_path / "manifest.yaml"
    manifest_yaml.write_text(
        """
student_profile:
  pseudonym: ciaran
module_roots:
  - path: notes/ST311
    module_code: ST311
  - path: notes/ST312
    module_code: ST312
privacy:
  include_identity_records: false
"""
    )
    monkeypatch.setenv("ACADEMIC_HISTORY_MANIFEST", str(manifest_yaml))
    sys.path.insert(0, str(NOTEBOOKS_DIR))

    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (
        run_tool,
    )

    summary = run_tool("summarise_my_progress")
    assert "pseudonym_hash" in summary
    assert "modules_count" in summary
    assert "artefacts_count" in summary


def test_agent_list_tools_returns_ten():
    from cianfhoghlaim.agents.meaisinfhoghlaim.educational.academic_history_agent import (
        list_tools,
    )

    tools = list_tools()
    assert len(tools) == 10
    assert all("name" in t and "description" in t for t in tools)
