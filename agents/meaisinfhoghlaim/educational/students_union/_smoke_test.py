"""cianfhoghlaim — Smoke test for the 5 SU tools + 5 ADK agents.

Run from the cianchosaint/.venv (which has google-adk 2.9.0 installed):

    /Users/cianmacandeisigh/dev/cianchosaint/.venv/bin/python3 \\
        /Users/cianmacandeisigh/dev/cianfhoghlaim/agents.meaisinfhoghlaim.educational.students_union/_smoke_test.py

The script imports each tool directly (bypassing the broken
agents/adk/__init__.py wholesale-copy) and exercises:

  - validate_club_application
  - match_grant_to_pot
  - route_complaint
  - validate_candidate_eligibility
  - aggregate_class_rep_themes
  - classify_su_query
  - the 5 ADK specialist agents + the root_agent (just construction,
    not full LLM invocation, to keep the test deterministic)

Exits 0 on success, 1 on any failure.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md at the cianfhoghlaim repo root).
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent.parent.parent  # cianfhoghlaim/agents/meaisinfhoghlaim/educational/students_union → cianfhoghlaim


def _bootstrap_su_package() -> None:
    """Make the students_union package importable without going through
    the broken agents/adk/__init__.py wholesale-copy."""
    su_pkg = types.ModuleType("students_union")
    su_pkg.__path__ = [str(THIS_DIR)]
    sys.modules["students_union"] = su_pkg

    config_spec = importlib.util.spec_from_file_location(
        "students_union.config", str(THIS_DIR / "config.py"),
    )
    config_mod = importlib.util.module_from_spec(config_spec)
    sys.modules["students_union.config"] = config_mod
    config_mod.__package__ = "students_union"
    config_spec.loader.exec_module(config_mod)

    tools_pkg = types.ModuleType("students_union.tools")
    tools_pkg.__path__ = [str(THIS_DIR / "tools")]
    sys.modules["students_union.tools"] = tools_pkg

    for tool_file in [
        "clubs_socs_validator.py",
        "grants_matcher.py",
        "complaint_router.py",
        "election_validator.py",
        "class_rep_themer.py",
    ]:
        name = tool_file.removesuffix(".py")
        spec = importlib.util.spec_from_file_location(
            f"students_union.tools.{name}",
            str(THIS_DIR / "tools" / tool_file),
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"students_union.tools.{name}"] = mod
        mod.__package__ = "students_union.tools"
        spec.loader.exec_module(mod)


def _bootstrap_su_agents() -> None:
    """Stub google.adk then load the 5 specialist agents + the root_agent."""
    google_stub = types.ModuleType("google")
    adk_stub = types.ModuleType("google.adk")
    agents_stub = types.ModuleType("google.adk.agents")

    # Build a permissive LlmAgent stub that accepts any kwargs and stores them.
    class _StubLlmAgent:
        def __init__(self, **kwargs: object) -> None:
            self.__dict__.update(kwargs)

    agents_stub.LlmAgent = _StubLlmAgent

    apps_stub = types.ModuleType("google.adk.apps")
    app_stub = types.ModuleType("google.adk.apps.app")

    class _StubApp:
        def __init__(self, **kwargs: object) -> None:
            self.__dict__.update(kwargs)

    app_stub.App = _StubApp

    tools_stub = types.ModuleType("google.adk.tools")
    tools_stub.FunctionTool = lambda func: f"FunctionTool({func.__name__})"

    sys.modules.setdefault("google", google_stub)
    sys.modules.setdefault("google.adk", adk_stub)
    sys.modules.setdefault("google.adk.agents", agents_stub)
    sys.modules.setdefault("google.adk.apps", apps_stub)
    sys.modules.setdefault("google.adk.apps.app", app_stub)
    sys.modules.setdefault("google.adk.tools", tools_stub)

    from importlib.machinery import SourceFileLoader

    for agent_file in [
        "clubs_socs_agent.py",
        "grants_funding_agent.py",
        "class_rep_aggregator_agent.py",
        "complaints_welfare_agent.py",
        "elections_agent.py",
    ]:
        module_name = agent_file.removesuffix(".py")
        loader = SourceFileLoader(
            f"students_union.{module_name}",
            str(THIS_DIR / agent_file),
        )
        loader.load_module()

    root_loader = SourceFileLoader(
        "students_union.root_agent",
        str(THIS_DIR / "root_agent.py"),
    )
    root_loader.load_module()


_bootstrap_su_package()
_bootstrap_su_agents()

from students_union.config import config  # noqa: E402
from students_union.tools.clubs_socs_validator import (  # noqa: E402
    ClubApplication, validate_club_application,
)
from students_union.tools.grants_matcher import (  # noqa: E402
    GrantApplication, match_grant_to_pot,
)
from students_union.tools.complaint_router import (  # noqa: E402
    Complaint, route_complaint,
)
from students_union.tools.election_validator import (  # noqa: E402
    Candidate, validate_candidate_eligibility,
)
from students_union.tools.class_rep_themer import (  # noqa: E402
    ClassRepReport, aggregate_class_rep_themes,
)


def main() -> int:
    print(f"SU smoke test — config.academic_year={config.su_academic_year}")
    print(f"  constitution_version={config.su_constitution_version}")
    print()

    # 1. Clubs & Socs
    print("[1/5] clubs_socs_validator")
    result = validate_club_application(ClubApplication(
        club_name="Galway Go Club",
        society_type="cultural",
        member_count=12,
        has_constitution=True,
        has_safeguarding_officer=True,
        has_committee=True,
        has_bank_account=False,
        gdpr_compliant=True,
        purpose_statement="To promote the ancient board game of Go among the University of Galway community.",
        contact_email="go@universityofgalway.ie",
    ))
    assert result.is_valid, f"expected is_valid=True, got {result.errors}"
    assert result.score >= 80, f"expected score >= 80, got {result.score}"
    print(f"  ✓ valid Galway Go Club: score={result.score}, warnings={result.warnings}")

    bad = validate_club_application(ClubApplication(
        club_name="Bad Club",
        society_type="sports",
        member_count=5,  # too few
        has_constitution=False,  # missing
        has_safeguarding_officer=False,  # missing
        has_committee=False,  # missing
        has_bank_account=True,
        gdpr_compliant=False,  # missing
        purpose_statement="short",  # too short
        contact_email="me@gmail.com",  # wrong domain
    ))
    assert not bad.is_valid
    assert len(bad.errors) >= 5  # at least 5 hard fails (member + constitution + safeguarding + committee + gdpr + purpose + email)
    print(f"  ✓ invalid Bad Club: {len(bad.errors)} errors, score={bad.score}")
    print()

    # 2. Grants
    print("[2/5] grants_matcher")
    # 2a. First-time applicant with receipts → capped at €600
    award = match_grant_to_pot(GrantApplication(
        applicant_name="Niamh",
        society_name="Galway Go Club",
        society_type="cultural",
        amount_requested_eur=500,
        purpose="conference",
        description="Travel to the Irish Go Congress 2026",
        has_receipts=True,
        is_first_time_applicant=True,
        previously_awarded_eur_this_year=0,
    ))
    assert award.eligible
    assert award.matched_pot == "TRAVEL"
    # First-time bonus: 500 * 1.2 = 600, but cap is 600
    assert award.awarded_eur == 600, f"expected 600 (capped), got {award.awarded_eur}"
    print(f"  ✓ first-time TRAVEL grant w/ receipts: €{award.awarded_eur} (capped)")

    # 2b. First-time applicant WITHOUT receipts → bonus + receipts penalty → 500 * 1.2 = 600, then /2 = 300
    award_no_receipts = match_grant_to_pot(GrantApplication(
        applicant_name="Niamh",
        society_name="Galway Go Club",
        society_type="cultural",
        amount_requested_eur=500,
        purpose="conference",
        description="Same trip, missing receipts",
        has_receipts=False,
        is_first_time_applicant=True,
    ))
    assert award_no_receipts.awarded_eur == 300, f"expected 300 (bonus then -50%), got {award_no_receipts.awarded_eur}"
    assert "-50%" in (award_no_receipts.cap_reason or "")
    print(f"  ✓ first-time TRAVEL w/o receipts: €{award_no_receipts.awarded_eur} (-50% penalty)")

    # 2c. WELFARE pot fallback (no society-type restriction)
    welfare = match_grant_to_pot(GrantApplication(
        applicant_name="Declan",
        society_name="Skydiving Soc",
        society_type="sports",
        amount_requested_eur=200,
        purpose="exam_breakfast",
        description="Exam breakfasts for skydivers",
        has_receipts=True,
        is_first_time_applicant=False,
    ))
    assert welfare.eligible
    assert welfare.matched_pot == "WELFARE"
    assert welfare.awarded_eur == 200
    print(f"  ✓ WELFARE fallback for skydiving exam breakfast: €{welfare.awarded_eur}")
    print()

    # 3. Complaints
    print("[3/5] complaint_router")
    route = route_complaint(Complaint(
        complainant_id_hash="h:abc123",
        complaint_text="I have been experiencing harassment from a fellow student in my lab group.",
        is_anonymous=False,
        has_already_contacted_su=False,
        submitted_at_iso="2026-09-13T12:00:00+00:00",
    ))
    assert route.category == "HARASSMENT"
    assert route.primary_officer == "Welfare Officer"
    assert route.is_urgent
    print(f"  ✓ harassment → {route.primary_officer} (urgent={route.is_urgent})")

    route2 = route_complaint(Complaint(
        complainant_id_hash="h:def456",
        complaint_text="The timetable clashes between CS203 and CS204.",
        is_anonymous=True,
        has_already_contacted_su=False,
        submitted_at_iso="2026-09-13T12:00:00+00:00",
    ))
    # no urgent keyword, no clear category match → GENERAL → President
    assert route2.primary_officer == "President"
    assert not route2.is_urgent
    print(f"  ✓ generic → {route2.primary_officer} (urgent={route2.is_urgent})")
    print()

    # 4. Elections
    print("[4/5] election_validator")
    elig = validate_candidate_eligibility(Candidate(
        candidate_id="cand-001",
        full_name="Aoife Murphy",
        student_id="22300111",
        role="SABBATICAL_PRESIDENT",
        is_registered_student=True,
        on_academic_suspension=False,
        on_disciplinary_hold=False,
        manifesto_word_count=378,
        nominator_signature_count=42,
        outstanding_su_fines_eur=0.0,
        previously_held_same_role=("2023/24",),
    ))
    assert elig.is_eligible
    assert len(elig.warnings) >= 1  # sabbatical warning
    print(f"  ✓ Sabbatical President (re-standing): eligible={elig.is_eligible}, warnings={len(elig.warnings)}")

    ineligible = validate_candidate_eligibility(Candidate(
        candidate_id="cand-002",
        full_name="Test Candidate",
        student_id="",
        role="CLASS_REP",
        is_registered_student=True,
        on_academic_suspension=False,
        on_disciplinary_hold=False,
        manifesto_word_count=120,  # too short
        nominator_signature_count=4,  # need 10
        outstanding_su_fines_eur=80.0,  # over €50
    ))
    assert not ineligible.is_eligible
    assert len(ineligible.errors) == 3
    assert ineligible.nominators_needed == 6
    print(f"  ✓ ineligible CLASS_REP: {len(ineligible.errors)} errors, needs {ineligible.nominators_needed} more nominators")
    print()

    # 5. Class Rep
    print("[5/5] class_rep_themer")
    agg = aggregate_class_rep_themes([
        ClassRepReport(
            rep_id="cr-1", module_code="CS203", module_title="Data Structures",
            report_text=(
                "Assessments are too heavy and the lecturer is unclear. "
                "Many students have accessibility needs that are not being met. "
                "The content is fine but the lecturer delivery is poor. "
                "Students are stressed about the next deadline."
            ),
            semester="2025/26 S1", submitted_at_iso="2026-09-13T11:00:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-2", module_code="CS204", module_title="Algorithms",
            report_text=(
                "Lecturer is great but assessments clash with other modules. "
                "The timetable clash is causing attendance issues."
            ),
            semester="2025/26 S1", submitted_at_iso="2026-09-13T11:05:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-3", module_code="MA101", module_title="Calculus I",
            report_text=(
                "Welfare concerns — students are stressed and there is no exam breakfast. "
                "International students feel left out."
            ),
            semester="2025/26 S1", submitted_at_iso="2026-09-13T11:10:00+00:00",
        ),
    ])
    assert agg.total_reports == 3
    assert agg.total_modules == 3
    assert not agg.insufficient_data
    # CS203 should have ≥3 themes: ASSESSMENT + LECTURER + ACCESSIBILITY + CONTENT
    assert "CS203" in agg.modules_with_multiple_concerns
    print(f"  ✓ 3 reports aggregated: themes={agg.themes}")
    print(f"  ✓ top_concerns={agg.top_concerns}")
    print(f"  ✓ modules_with_multiple_concerns={agg.modules_with_multiple_concerns}")
    print()

    # 6. classify_su_query (root agent classifier)
    print("[6/7] classify_su_query")
    from students_union.root_agent import classify_su_query
    tests = [
        ("I want to start a new society for board games", "clubs_socs"),
        ("Apply for a €500 travel grant to attend a conference", "grants"),
        ("Summarise this week's class rep reports", "class_rep"),
        ("I want to report harassment from a lecturer", "complaints"),
        ("Am I eligible to run for sabbatical president?", "elections"),
        ("what is the weather in galway?", "ambiguous"),
    ]
    for q, expected in tests:
        got = classify_su_query(q)
        status = "✓" if got == expected else "✗"
        print(f"  {status} {expected:11} <= {got:11}  ::  {q[:60]}")
        assert got == expected, f"expected {expected}, got {got}"
    print()

    # 7. Construct the 5 ADK agents + root_agent
    print("[7/7] construct the 5 ADK agents + root")
    from students_union.clubs_socs_agent import clubs_socs_agent
    from students_union.grants_funding_agent import grants_funding_agent
    from students_union.class_rep_aggregator_agent import class_rep_aggregator_agent
    from students_union.complaints_welfare_agent import complaints_welfare_agent
    from students_union.elections_agent import elections_agent
    from students_union.root_agent import root_agent, students_union_app

    agents = [
        ("clubs_socs_agent", clubs_socs_agent),
        ("grants_funding_agent", grants_funding_agent),
        ("class_rep_aggregator_agent", class_rep_aggregator_agent),
        ("complaints_welfare_agent", complaints_welfare_agent),
        ("elections_agent", elections_agent),
    ]
    for expected_name, agent in agents:
        assert agent.name == expected_name, f"{agent.name} != {expected_name}"
        # Stubbed LlmAgent — check the attribute we set
        assert hasattr(agent, "model")
        print(f"  ✓ {agent.name} constructed: model={agent.model}")

    assert root_agent.name == "students_union_root_agent"
    assert len(root_agent.sub_agents) == 5
    assert students_union_app.name == "students_union_orchestrator"
    print(f"  ✓ root_agent constructed: sub_agents={len(root_agent.sub_agents)}")
    print(f"  ✓ students_union_app constructed: {students_union_app.name}")
    print()

    print("=" * 60)
    print("All 5 SU case-study tools + 5 agents + root_agent + classifier pass.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
