# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "google-adk>=2.9.0",
#     "pandas>=2.0.0",
# ]
# ///

"""cianfhoghlaim — Students' Union Google ADK case studies (marimo notebook).

5 case studies + 1 root orchestrator, all from
`agents.meaisinfhoghlaim.educational.students_union/`. Run with:

    marimo edit notebooks/students_union_adk_case_studies.py

The notebook imports the local `agents.meaisinfhoghlaim.educational.students_union` package
(it must be runnable as a Python module — see `pyproject.toml`).

Tabs:
  1. Overview + how the 5 agents wire together
  2. Tools only (no LLM) — deterministic smoke test of every tool
  3. Case Study 1: Clubs & Societies Registration
  4. Case Study 2: Grants & Funding Triage
  5. Case Study 3: Class Rep Feedback Aggregation
  6. Case Study 4: Complaints & Welfare Triage
  7. Case Study 5: Election & Referendum Workflow
  8. Root Orchestrator: classify_su_query across many queries

Licence: BUSL-1.1 v2 CIANDLITHE edition (per LICENSE.md).
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # University of Galway Students' Union — Google ADK case studies

        **5 specialist agents + 1 root orchestrator**, all wrapped around pure-Python
        tools that implement the SU's published bylaws deterministically.

        The 5 case studies:

        | # | Workflow | Tool | ADK specialist |
        |--:|:--|:--|:--|
        | 1 | Clubs & Societies Registration | `validate_club_application` | `clubs_socs_agent` |
        | 2 | Grants & Funding Triage | `match_grant_to_pot` | `grants_funding_agent` |
        | 3 | Class Rep Feedback Aggregation | `aggregate_class_rep_themes` | `class_rep_aggregator_agent` |
        | 4 | Complaints & Welfare Triage | `route_complaint` | `complaints_welfare_agent` |
        | 5 | Election & Referendum Workflow | `validate_candidate_eligibility` | `elections_agent` |

        Open the tabs below to walk through each case study end-to-end.
        """
    )
    return (mo,)


@app.cell
def _imports():
    import sys
    from pathlib import Path

    # The SU agents live at <repo>/agents.meaisinfhoghlaim.educational.students_union. Add the
    # nearest sys.path entry that lets `import agents.meaisinfhoghlaim.educational.students_union`
    # work without going through the broken agents/adk/__init__.py
    # wholesale-copy. The marimo notebook lives at <repo>/notebooks/, so
    # the repo root is the parent of the current file's parent.
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return Path, repo_root, sys


@app.cell
def _import_su_package(Path, repo_root, sys):
    # Stub google.adk so the SU agents construct cleanly even in
    # environments without google-adk installed. The notebook still
    # demonstrates the routing logic; for real LLM calls, install
    # google-adk>=2.9.0 in your venv and remove this stub.
    import importlib
    import types

    if "google" not in sys.modules:
        google_stub = types.ModuleType("google")
        adk_stub = types.ModuleType("google.adk")
        agents_stub = types.ModuleType("google.adk.agents")

        class _StubLlmAgent:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        agents_stub.LlmAgent = _StubLlmAgent
        apps_stub = types.ModuleType("google.adk.apps")
        app_stub = types.ModuleType("google.adk.apps.app")

        class _StubApp:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        app_stub.App = _StubApp
        tools_stub = types.ModuleType("google.adk.tools")
        tools_stub.FunctionTool = lambda func: f"FunctionTool({func.__name__})"
        sys.modules["google"] = google_stub
        sys.modules["google.adk"] = adk_stub
        sys.modules["google.adk.agents"] = agents_stub
        sys.modules["google.adk.apps"] = apps_stub
        sys.modules["google.adk.apps.app"] = app_stub
        sys.modules["google.adk.tools"] = tools_stub

    # Now import the SU package
    try:
        from agents.meaisinfhoghlaim.educational.students_union import (
            root_agent,
            students_union_app,
            classify_su_query,
            clubs_socs_agent,
            grants_funding_agent,
            class_rep_aggregator_agent,
            complaints_welfare_agent,
            elections_agent,
            config,
        )
        from agents.meaisinfhoghlaim.educational.students_union.tools import (
            ClubApplication,
            GrantApplication,
            Complaint,
            Candidate,
            ClassRepReport,
            validate_club_application,
            match_grant_to_pot,
            route_complaint,
            validate_candidate_eligibility,
            aggregate_class_rep_themes,
        )
        su_import_ok = True
        import_error = None
    except Exception as e:
        # If the wholesale-copy __init__.py chain fails, fall back to
        # importing via the smoke-test bootstrap pattern
        su_import_ok = False
        import_error = e
        root_agent = students_union_app = classify_su_query = None
        clubs_socs_agent = grants_funding_agent = class_rep_aggregator_agent = None
        complaints_welfare_agent = elections_agent = config = None
        ClubApplication = GrantApplication = Complaint = None
        Candidate = ClassRepReport = None
        validate_club_application = match_grant_to_pot = None
        route_complaint = validate_candidate_eligibility = None
        aggregate_class_rep_themes = None

    return (
        Candidate,
        ClassRepReport,
        ClubApplication,
        Complaint,
        aggregate_class_rep_themes,
        classify_su_query,
        class_rep_aggregator_agent,
        clubs_socs_agent,
        complaints_welfare_agent,
        config,
        elections_agent,
        GrantApplication,
        grants_funding_agent,
        import_error,
        match_grant_to_pot,
        root_agent,
        route_complaint,
        students_union_app,
        su_import_ok,
        validate_candidate_eligibility,
        validate_club_application,
    )


@app.cell
def _tools_only_check(
    mo,
    su_import_ok,
    import_error,
    validate_club_application,
    ClubApplication,
    match_grant_to_pot,
    GrantApplication,
    route_complaint,
    Complaint,
    validate_candidate_eligibility,
    Candidate,
    aggregate_class_rep_themes,
    ClassRepReport,
):
    mo.md(
        f"""
        ## Tab 1: Tools only (no LLM required)

        The 5 pure-Python tools work without `google-adk` or any API key.
        This tab exercises every tool with one positive + one negative case.

        `su_import_ok` = `{su_import_ok}` -- if False, run
        `python3 agents.meaisinfhoghlaim.educational.students_union/_smoke_test.py` first to
        validate the package layout.

        `import_error` = `{import_error}` (None if everything is fine)
        """
    )
    return


@app.cell
def _case_study_1(
    mo,
    validate_club_application,
    ClubApplication,
    su_import_ok,
):
    mo.md("## Tab 2: Case Study 1 — Clubs & Societies Registration")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    app = ClubApplication(
        club_name="Galway Go Club",
        society_type="cultural",
        member_count=14,
        has_constitution=True,
        has_safeguarding_officer=True,
        has_committee=True,
        has_bank_account=True,
        gdpr_compliant=True,
        purpose_statement=(
            "To promote the ancient board game of Go among the "
            "University of Galway community, run weekly informal sessions, "
            "and field a team at the annual Irish Go Congress."
        ),
        contact_email="go@universityofgalway.ie",
    )
    result = validate_club_application(app)
    mo.md(
        f"""
        **Application:** {app.club_name} ({app.society_type}, {app.member_count} members)

        **Validation result:**
        - ✅ is_valid = **{result.is_valid}**
        - 📊 score = **{result.score}/100**
        - ❌ errors = `{result.errors or '[]'}`
        - ⚠️ warnings = `{result.warnings or '[]'}`

        **Decision:** `{'APPROVE' if result.is_valid and result.score >= 80 else 'REVIEW'}`
        """
    )
    return app, result


@app.cell
def _case_study_2(
    mo,
    match_grant_to_pot,
    GrantApplication,
    su_import_ok,
    config,
):
    mo.md("## Tab 3: Case Study 2 — Grants & Funding Triage")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    application = GrantApplication(
        applicant_name="Niamh Ní Cheallaigh",
        society_name="Cumann Gaeilge na Gaillimhe",
        society_type="cultural",
        amount_requested_eur=500,
        purpose="conference",
        description="Travel to the Irish Go Congress 2026 in Cork",
        has_receipts=False,
        is_first_time_applicant=True,
        previously_awarded_eur_this_year=0,
    )
    award = match_grant_to_pot(application)
    mo.md(
        f"""
        **Application:** {application.applicant_name} ({application.society_name})
        requested **€{application.amount_requested_eur}** for `{application.purpose}`

        **Funding pot caps (per {config.su_academic_year} Funding Policy):**
        - TRAVEL:    up to €{config.max_travel_grant_eur}
        - EQUIPMENT: up to €{config.max_equipment_grant_eur}
        - EVENT:     up to €{config.max_event_grant_eur}
        - WELFARE:   up to €{config.max_welfare_grant_eur}

        **Match result:**
        - 🎯 pot = **{award.matched_pot}**
        - 💰 awarded = **€{award.awarded_eur}**
        - ✅ eligible = **{award.eligible}**
        - 📝 cap_reason = `{award.cap_reason or 'None'}`

        **Decision:** `{'AWARD' if award.eligible and award.awarded_eur == application.amount_requested_eur else 'PARTIAL_AWARD' if award.eligible else 'REJECT'}`
        """
    )
    return application, award


@app.cell
def _case_study_3(
    mo,
    aggregate_class_rep_themes,
    ClassRepReport,
    su_import_ok,
):
    mo.md("## Tab 4: Case Study 3 — Class Rep Feedback Aggregation")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    reports = [
        ClassRepReport(
            rep_id="cr-cs203",
            module_code="CS203",
            module_title="Data Structures",
            report_text=(
                "Assessments are too heavy and the lecturer is unclear. "
                "Many students have accessibility needs that are not being met. "
                "The content is fine but the lecturer delivery is poor. "
                "Students are stressed about the next deadline."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:00:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-cs204",
            module_code="CS204",
            module_title="Algorithms",
            report_text=(
                "Lecturer is great but assessments clash with other modules. "
                "The timetable clash is causing attendance issues."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:05:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-ma101",
            module_code="MA101",
            module_title="Calculus I",
            report_text=(
                "Welfare concerns — students are stressed and there is no exam breakfast. "
                "International students feel left out."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:10:00+00:00",
        ),
    ]
    agg = aggregate_class_rep_themes(reports)
    mo.md(
        f"""
        **Reports aggregated:** {agg.total_reports} (across {agg.total_modules} modules)

        **Theme counts** (weighted by priority):
        ```
        {chr(10).join(f"  {k:14} {v}" for k, v in sorted(agg.themes.items(), key=lambda kv: -kv[1]))}
        ```

        **Top concerns:** `{agg.top_concerns}`

        **Modules with ≥3 cross-cutting themes:** `{agg.modules_with_multiple_concerns}`

        **Insufficient data:** `{agg.insufficient_data}`
        """
    )
    return agg, reports


@app.cell
def _case_study_4(
    mo,
    route_complaint,
    Complaint,
    su_import_ok,
):
    mo.md("## Tab 5: Case Study 4 — Complaints & Welfare Triage")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    complaint = Complaint(
        complainant_id_hash="h:abc123",
        complaint_text=(
            "I have been experiencing harassment from a fellow student "
            "in my lab group. It's been going on for weeks."
        ),
        is_anonymous=False,
        has_already_contacted_su=False,
        submitted_at_iso="2026-09-13T12:00:00+00:00",
    )
    route = route_complaint(complaint)
    mo.md(
        f"""
        **Complaint text:** _"{complaint.complaint_text[:80]}..."_

        **Routing:**
        - 👤 primary officer = **{route.primary_officer}**
        - 👥 secondary officers = `{route.secondary_officers}`
        - 📂 category = **{route.category}**
        - 🚨 urgent = **{route.is_urgent}**
        - ⬆️ escalation_required = **{route.escalation_required}**
        - 📝 rationale = `{route.rationale}`
        """
    )
    return complaint, route


@app.cell
def _case_study_5(
    mo,
    validate_candidate_eligibility,
    Candidate,
    su_import_ok,
    config,
):
    mo.md("## Tab 6: Case Study 5 — Election & Referendum Workflow")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    candidate = Candidate(
        candidate_id="cand-aoife-2025",
        full_name="Aoife Ní Mhurchú",
        student_id="22300111",
        role="SABBATICAL_PRESIDENT",
        is_registered_student=True,
        on_academic_suspension=False,
        on_disciplinary_hold=False,
        manifesto_word_count=378,
        nominator_signature_count=42,
        outstanding_su_fines_eur=0.0,
        previously_held_same_role=("2023/24",),
    )
    elig = validate_candidate_eligibility(
        candidate, min_signatures=config.min_nominator_signatures,
    )
    mo.md(
        f"""
        **Candidate:** {candidate.full_name} running for `{candidate.role}`

        **Eligibility:**
        - ✅ eligible = **{elig.is_eligible}**
        - ❌ errors = `{elig.errors or '[]'}`
        - ⚠️ warnings = `{elig.warnings or '[]'}`
        - 📝 additional nominators needed = **{elig.nominators_needed}**

        **Decision:** `{'CONFIRM' if elig.is_eligible else 'RETURN_FOR_FIXES' if elig.nominators_needed > 0 else 'REJECT'}`
        """
    )
    return candidate, elig


@app.cell
def _orchestrator(
    mo,
    classify_su_query,
    su_import_ok,
):
    mo.md("## Tab 7: Root Orchestrator — classify_su_query across many queries")
    if not su_import_ok:
        mo.md("_Skipped: SU package failed to import._")
        return

    sample_queries = [
        "I want to start a new society for board games",
        "Apply for a €500 travel grant to attend a conference",
        "Summarise this week's class rep reports",
        "I want to report harassment from a lecturer",
        "Am I eligible to run for sabbatical president?",
        "What is the SU's policy on hardship funds?",
        "How many nominators do I need for class rep?",
        "I want to lodge a complaint about accommodation",
        "When does the sabbatical election open?",
        "Help me register a new academic society",
        "What funding pots are available?",
        "Can I appeal an SU decision?",
    ]

    routes = [(q, classify_su_query(q)) for q in sample_queries]

    mo.md(
        "**Routing table:**\n\n"
        + "\n".join(
            f"| `{q[:55]:55}` | `{r}` |"
            for q, r in routes
        )
    )
    return routes, sample_queries


@app.cell
def _agent_topology(mo, su_import_ok, root_agent, students_union_app):
    mo.md("## Tab 8: Agent topology")
    if not su_import_ok or root_agent is None:
        mo.md("_Skipped: SU package failed to import._")
        return

    sub_agents_list = "\n".join(f"  - `{sa.name}`" for sa in root_agent.sub_agents)
    mo.md(
        f"""
        **Root orchestrator:** `{root_agent.name}` (model: `{root_agent.model}`)

        **Sub-agents (5):**
        {sub_agents_list}

        **ADK App:** `{students_union_app.name}`

        The root agent routes incoming SU queries to the correct specialist
        based on the `classify_su_query` intent classifier (see Tab 7).
        The 5 specialists each wrap a pure-Python tool that implements
        the SU's published bylaws deterministically.
        """
    )
    return (sub_agents_list,)


if __name__ == "__main__":
    app.run()
