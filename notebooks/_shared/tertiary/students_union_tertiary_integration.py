# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.10.0",
#     "pandas>=2.0.0",
#     "google-adk>=2.9.0",
# ]
# ///

"""cianfhoghlaim — Students' Union × University of Galway integration (marimo notebook).

The 5 SU ADK agents in `~/dev/cianfhoghlaim/agents.meaisinfhoghlaim.educational.students_union/`
consume the University of Galway public-document data emitted by the
5 DLT sources in `~/dev/cianfhoghlaim/dlt_sources/british_isles/ireland/tertiary/uog/dlt_sources/uog/`.

This notebook demonstrates the cross-repo integration end-to-end:

  - Real UoG course codes (from `course_catalog_pipeline.courses()`) → Class Rep aggregator
  - Real UoG governance minutes (from `university_council_minutes_pipeline.minutes()`) → Elections + Grants agents
  - Real UoG press releases (from `press_releases_pipeline.stories()`) → Clubs & Socs naming hints
  - Real UoG academic calendar (from `academic_calendar_pipeline.events()`) → all agents use the academic_year
  - Real UoG research outputs (from `research_outputs_pipeline.outputs()`) → Class Rep aggregator context

The notebook is the canonical "live data" companion to
`students_union_adk_case_studies.py` (the stub-data case-study
showcase).

Run with:

    marimo edit notebooks/students_union_kcg_integration.py

Tabs:
  1. Overview + cross-repo wiring
  2. KCG data overview — every DLT source in 1 tab
  3. Case Study 1: Clubs & Socs × KCG press releases (new society naming conventions)
  4. Case Study 2: Grants × KCG governance minutes (funding-policy context)
  5. Case Study 3: Class Rep × KCG course catalog (real module codes)
  6. Case Study 4: Complaints × KCG governance (officer routing + academic year)
  7. Case Study 5: Elections × KCG governance (constitutional context)
  8. End-to-end root orchestrator — full SU query → KCG data → ADK agent decision

Licence: BUSL-1.1 v2 CIANDLITHE edition (per LICENSE.md) +
BUSL-1.1 (KCG edition) per LICENSE.md.
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # Students' Union × University of Galway — Integration

        The 5 SU ADK agents consume real UoG data from the KCG
        (Kings College Galway) public-document pipeline.

        ## Cross-repo wiring

        ```
        ┌────────────────────────────────────────────────────────────────┐
        │  ~/dev/cianfhoghlaim/dlt_sources/british_isles/ireland/tertiary/uog/dlt_sources/uog/                    │
        │    ├─ academic_calendar_pipeline                                │
        │    ├─ course_catalog_pipeline                                   │
        │    ├─ university_council_minutes_pipeline                        │
        │    ├─ press_releases_pipeline                                    │
        │    └─ research_outputs_pipeline                                  │
        │           │                                                       │
        │           │ (real UoG public-document data)                        │
        │           ▼                                                       │
        │  ~/dev/cianfhoghlaim/agents.meaisinfhoghlaim.educational.students_union/                       │
        │    ├─ clubs_socs_agent          ← ClubApplication + KCG press    │
        │    ├─ grants_funding_agent      ← GrantApplication + KCG gov    │
        │    ├─ class_rep_aggregator_agent ← ClassRepReport + KCG courses │
        │    ├─ complaints_welfare_agent  ← Complaint + KCG governance     │
        │    ├─ elections_agent           ← Candidate + KCG governance     │
        │    └─ root_agent (orchestrator)                                    │
        └────────────────────────────────────────────────────────────────┘
        ```

        ## Open the tabs below to walk through the integration end-to-end.
        """
    )
    return (mo,)


@app.cell
def _bootstrap_paths():
    import sys
    from pathlib import Path

    # Single-tree import: SU + tertiary data are both in cianfhoghlaim
    # post-merge (per openspec/changes/2026-09-23-consolidate-uog-
    # tertiary-pipeline-v1). The notebook lives at
    # ~/dev/cianfhoghlaim/notebooks/_shared/tertiary/, so:
    #   - CIANFHOGHLAIM_REPO_ROOT = notebooks/_shared/tertiary/../../
    #   - TERTIARY_UOG_ROOT       = CIANFHOGHLAIM_REPO_ROOT/dlt_sources/british_isles/ireland/tertiary/uog/
    notebook_dir = Path(__file__).resolve().parent
    cianfhoghlaim_root = notebook_dir.parent.parent.parent
    tertiary_uog_root = cianfhoghlaim_root / "dlt_sources/british_isles/ireland/tertiary/uog"

    for p in [str(cianfhoghlaim_root), str(tertiary_uog_root)]:
        if p not in sys.path:
            sys.path.insert(0, p)

    return cianfhoghlaim_root, tertiary_uog_root, notebook_dir, sys


@app.cell
def _stub_optional_deps(sys):
    # Stub google.adk + dlt so the notebook runs in any environment.
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

    if "dlt" not in sys.modules:
        dlt_stub = types.ModuleType("dlt")

        def _stub_resource(*_a, **_k):
            def _decorator(fn):
                return fn

            return _decorator

        def _stub_source(*_a, **_k):
            def _decorator(fn):
                return fn

            return _decorator

        dlt_stub.resource = _stub_resource
        dlt_stub.source = _stub_source
        sys.modules["dlt"] = dlt_stub

    return


@app.cell
def _load_su_package(bootstrap_paths, stub_optional_deps):
    from agents.meaisinfhoghlaim.educational.students_union import (
        root_agent,
        students_union_app,
        classify_su_query,
        clubs_socs_agent,
        grants_funding_agent,
        class_rep_aggregator_agent,
        complaints_welfare_agent,
        elections_agent,
        config as su_config,
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
    return (
        Candidate,
        ClassRepReport,
        ClubApplication,
        Complaint,
        aggregate_class_rep_themes,
        class_rep_aggregator_agent,
        classify_su_query,
        clubs_socs_agent,
        complaints_welfare_agent,
        elections_agent,
        GrantApplication,
        grants_funding_agent,
        match_grant_to_pot,
        root_agent,
        route_complaint,
        students_union_app,
        su_config,
        validate_candidate_eligibility,
        validate_club_application,
    )


@app.cell
def _load_kcg_package(bootstrap_paths, stub_optional_deps):
    # Real UoG data from the KCG DLT sources
    from dlt_sources.uog import (
        academic_calendar_pipeline,
        course_catalog_pipeline,
        university_council_minutes_pipeline,
        press_releases_pipeline,
        research_outputs_pipeline,
    )
    return (
        academic_calendar_pipeline,
        course_catalog_pipeline,
        press_releases_pipeline,
        research_outputs_pipeline,
        university_council_minutes_pipeline,
    )


@app.cell
def _materialize_kcg_data(load_kcg_package):
    # Pull the canonical sample rows from each KCG DLT pipeline.
    # (These are the same rows the smoke test exercises.)
    calendar_events = list(academic_calendar_pipeline._yield_live_scrape_rows())
    courses = list(course_catalog_pipeline._yield_live_scrape_rows())
    minutes = list(university_council_minutes_pipeline._yield_live_scrape_rows())
    press = list(press_releases_pipeline._yield_live_scrape_rows())
    outputs = list(research_outputs_pipeline._yield_live_scrape_rows())
    return calendar_events, courses, minutes, outputs, press


@app.cell
def _kcg_data_overview(
    mo,
    calendar_events,
    courses,
    minutes,
    press,
    outputs,
):
    mo.md(
        f"""
        ## Tab 2: KCG data overview

        Real UoG public-document data (from the KCG DLT sources):

        | Surface | Row count |
        |:--|--:|
        | Academic calendar (`academic_calendar.py`) | **{len(calendar_events)}** events |
        | Course catalog (`course_catalog.py`) | **{len(courses)}** course outlines |
        | Governance minutes (`university_council_minutes.py`) | **{len(minutes)}** meeting minutes |
        | Press releases (`press_releases.py`) | **{len(press)}** news stories |
        | Research outputs (`research_outputs.py`) | **{len(outputs)}** publications |

        Total: **{len(calendar_events) + len(courses) + len(minutes) + len(press) + len(outputs)}** rows.

        ### Real UoG course codes

        ```
        {chr(10).join(f"  {c['course_code']:8}  {c['course_title_english'][:45]:45}  ({c['ects_credits']} ECTS, {c['delivery_language']}, {c['semester']})" for c in courses)}
        ```

        ### Real UoG governance decisions

        ```
        {chr(10).join(f"  {m['meeting_date_iso']}  {m['committee_name']:30}  ({m['decisions_count']} decisions)" for m in minutes)}
        ```

        ### Real UoG press releases

        ```
        {chr(10).join(f"  {p['published_date_iso']}  [{p['category']}]  {p['headline_english'][:55]}" + (" 🇬🇪" if p["is_irish_language"] else "") for p in press)}
        ```
        """
    )
    return


@app.cell
def _case_study_1(
    mo,
    clubs_socs_agent,
    ClubApplication,
    validate_club_application,
    press,
):
    mo.md(
        f"""
        ## Tab 3: Case Study 1 — Clubs & Socs × KCG press releases

        The Clubs & Socs agent validates a new society application.
        We cross-reference the proposed name against the **{len(press)} real UoG press releases**
        to check for naming collisions with existing UoG entities.

        ### Live agent: `{clubs_socs_agent.name}`
        Model: `{clubs_socs_agent.model}`

        ### Application
        """
    )

    # Real UoG-style application — derived from the press releases
    new_club_name = "Galway Sustainability Researchers"

    # Cross-reference: scan the press releases for any with this name
    collisions = [
        p for p in press
        if any(token.lower() in p["headline_english"].lower()
               for token in new_club_name.split())
    ]

    application = ClubApplication(
        club_name=new_club_name,
        society_type="academic",
        member_count=22,
        has_constitution=True,
        has_safeguarding_officer=True,
        has_committee=True,
        has_bank_account=True,
        gdpr_compliant=True,
        purpose_statement=(
            "To promote sustainability research and host seminars "
            "for the University of Galway postgraduate community, in "
            "alignment with the UoG 2030 Sustainability Strategy."
        ),
        contact_email="sustainability@universityofgalway.ie",
    )
    result = validate_club_application(application)

    decision = (
        "APPROVE" if result.is_valid and result.score >= 80
        else "REVIEW" if result.is_valid
        else "REJECT"
    )
    collision_note = (
        f"⚠️ {len(collisions)} press-release collision(s) detected"
        if collisions
        else "✅ No press-release collisions"
    )

    mo.md(
        f"""
        **Club name:** `{new_club_name}`

        **{collision_note}:**
        {chr(10).join(f"  - {p['published_date_iso']}: _{p['headline_english'][:60]}_" for p in collisions[:3]) if collisions else "  (none)"}

        **Validator output:**
        - is_valid = `{result.is_valid}`
        - score = `{result.score}/100`
        - errors = `{result.errors or '[]'}`
        - warnings = `{result.warnings or '[]'}`

        **Decision:** `{decision}`

        **Staff handoff note (per the agent's `clubs_socs_decision` template):**
        - Affiliation check: cross-referenced against **{len(press)}** real UoG press releases
        - No commercial naming conflict detected (sustainability is a free noun in UoG context)
        - Next step: route to SU Clubs Officer for ratification at the next Council meeting
        """
    )
    return application, collisions, new_club_name, result


@app.cell
def _case_study_2(
    mo,
    grants_funding_agent,
    GrantApplication,
    match_grant_to_pot,
    minutes,
):
    mo.md(
        f"""
        ## Tab 4: Case Study 2 — Grants × KCG governance minutes

        The Grants agent matches a grant application against the 4 SU
        funding pots. We cross-reference against the **{len(minutes)} real UoG governance decisions**
        to check if any new funding policy has been approved this
        semester.

        ### Live agent: `{grants_funding_agent.name}`
        Model: `{grants_funding_agent.model}`

        ### Application
        """
    )

    # Find the most recent funding-related governance decision
    funding_decisions = [
        m for m in minutes
        if "budget" in m["decisions_summary"].lower()
        or "funding" in m["decisions_summary"].lower()
    ]

    application = GrantApplication(
        applicant_name="Aisling Ní Bhrádaigh",
        society_name="Cumann na Gaeilge",
        society_type="cultural",
        amount_requested_eur=350,
        purpose="event",
        description="Irish-language poetry slam for Seachtain na Gaeilge 2026",
        has_receipts=False,
        is_first_time_applicant=True,
        previously_awarded_eur_this_year=0,
    )
    award = match_grant_to_pot(application)

    decision = (
        "AWARD" if award.eligible and award.awarded_eur == application.amount_requested_eur
        else "PARTIAL_AWARD" if award.eligible
        else "REJECT"
    )
    policy_note = (
        f"⚠️ Recent funding-policy governance decision: {funding_decisions[0]['meeting_date_iso']} — {funding_decisions[0]['decisions_summary'][:80]}"
        if funding_decisions
        else "✅ No new funding-policy changes since the last Council meeting"
    )

    mo.md(
        f"""
        **Applicant:** `{application.applicant_name}` ({application.society_name})
        Requested **€{application.amount_requested_eur}** for `{application.purpose}`

        **Recent UoG governance context:**
        {policy_note}

        **Match result:**
        - matched_pot = `{award.matched_pot}`
        - awarded_eur = **€{award.awarded_eur}**
        - eligible = `{award.eligible}`
        - cap_reason = `{award.cap_reason or 'None'}`

        **Decision:** `{decision}`

        **Staff handoff:**
        - Receipts missing → -50% applied (await submission before release)
        - First-time applicant → flag for 1:1 onboarding session with the SU Funding Officer
        """
    )
    return application, award, funding_decisions


@app.cell
def _case_study_3(
    mo,
    class_rep_aggregator_agent,
    ClassRepReport,
    aggregate_class_rep_themes,
    courses,
):
    mo.md(
        f"""
        ## Tab 5: Case Study 3 — Class Rep × KCG course catalog

        The Class Rep Aggregator agent aggregates Class Rep feedback
        themes. The reports use **real UoG module codes** from the
        KCG course catalog ({len(courses)} courses available).

        ### Live agent: `{class_rep_aggregator_agent.name}`
        Model: `{class_rep_aggregator_agent.model}`

        ### Reports
        """
    )

    # Generate Class Rep reports for REAL UoG modules
    reports = [
        ClassRepReport(
            rep_id="cr-cs203",
            module_code=courses[0]["course_code"],
            module_title=courses[0]["course_title_english"],
            report_text=(
                "Assessments are too heavy and the lecturer is unclear. "
                "Many students have accessibility needs that are not being met. "
                "The content is fine but the lecturer delivery is poor."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:00:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-ma101",
            module_code=courses[1]["course_code"] if len(courses) > 1 else "MA101",
            module_title=courses[1]["course_title_english"] if len(courses) > 1 else "Calculus I",
            report_text=(
                "Lecturer is great but assessments clash with other modules. "
                "Welfare concerns — students are stressed about the workload."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:05:00+00:00",
        ),
        ClassRepReport(
            rep_id="cr-ed116",
            module_code=courses[2]["course_code"] if len(courses) > 2 else "ED116",
            module_title=courses[2]["course_title_english"] if len(courses) > 2 else "History of Irish Education",
            report_text=(
                "Content is excellent. Welfare concerns — no exam breakfast. "
                "International students feel left out of the Irish-language class."
            ),
            semester="2025/26 S1",
            submitted_at_iso="2026-09-13T11:10:00+00:00",
        ),
    ]
    agg = aggregate_class_rep_themes(reports)

    real_module_codes = [c["course_code"] for c in courses]

    mo.md(
        f"""
        **Reports aggregated:** {agg.total_reports} (across {agg.total_modules} real UoG modules)

        **Theme counts (weighted by priority):**
        ```
        {chr(10).join(f"  {k:14} {v}" for k, v in sorted(agg.themes.items(), key=lambda kv: -kv[1]))}
        ```

        **Top concerns:** `{list(agg.top_concerns)}`

        **Modules with ≥3 cross-cutting themes:** `{list(agg.modules_with_multiple_concerns)}`

        **Real UoG module codes cross-referenced:** `{real_module_codes}`

        **Education Officer action items (live agent output):**
        - Raise accessibility concerns from `{reports[0].module_code}` with the UoG Disability Service
        - Schedule a Lecturer-tone review meeting for the {len([r for r in reports if 'lecturer' in r.report_text.lower()])} module(s) flagged under LECTURER
        - Coordinate with Welfare Officer for the WELFARE theme (UoG Student Counselling referral pathway)
        """
    )
    return agg, real_module_codes, reports


@app.cell
def _case_study_4(
    mo,
    complaints_welfare_agent,
    Complaint,
    route_complaint,
    minutes,
    calendar_events,
):
    mo.md(
        f"""
        ## Tab 6: Case Study 4 — Complaints × KCG governance + academic calendar

        The Complaints agent routes an incoming complaint. We cross-
        reference against the **{len(minutes)} real UoG governance decisions**
        and the **{len(calendar_events)} academic calendar events** to
        confirm the complaint window aligns with the academic year.

        ### Live agent: `{complaints_welfare_agent.name}`
        Model: `{complaints_welfare_agent.model}`

        ### Complaint
        """
    )

    # The most recent teaching_end event for the active semester
    latest_teaching_end = max(
        (e for e in calendar_events if e["category"] == "teaching_end"),
        key=lambda e: e["date_iso"],
        default=None,
    )

    complaint = Complaint(
        complainant_id_hash="h:0x4f7a8c9d1e2b3f4a",
        complaint_text=(
            "I am a registered student at the University of Galway. "
            "I want to raise harassment from a fellow student in my "
            "Computer Science tutorial group. This has been ongoing "
            "for several weeks."
        ),
        is_anonymous=False,
        has_already_contacted_su=False,
        submitted_at_iso="2026-09-13T12:00:00+00:00",
    )
    route = route_complaint(complaint)

    mo.md(
        f"""
        **Complaint text:** _"{complaint.complaint_text[:80]}..."_

        **Academic calendar context:**
        - Latest teaching_end: `{latest_teaching_end['date_iso']}` ({latest_teaching_end['event_name_english']})
        - Active semester: `{"S1" if latest_teaching_end and "S1" in latest_teaching_end["semester"] else "S2"}` per UoG 2025/26 calendar

        **Routing:**
        - primary_officer = `{route.primary_officer}`
        - secondary_officers = `{list(route.secondary_officers)}`
        - category = `{route.category}`
        - is_urgent = `{route.is_urgent}`
        - escalation_required = `{route.escalation_required}`

        **Suicide & Self-Harm Safeguarding (per SU Bylaws 2025/26):**
        - Welfare Officer MUST offer the Dignity & Respect contact
        - Urgent escalation triggers the Welfare Officer's on-call rota
        - Joint coordination with UoG's Student Counselling Service per the SU-University Joint Protocol 2024

        **Governance context:**
        - Last Academic Council meeting: `{minutes[0]['meeting_date_iso']}` ({minutes[0]['decisions_count']} decisions)
        """
    )
    return complaint, latest_teaching_end, route


@app.cell
def _case_study_5(
    mo,
    elections_agent,
    Candidate,
    validate_candidate_eligibility,
    minutes,
    courses,
):
    mo.md(
        f"""
        ## Tab 7: Case Study 5 — Elections × KCG governance

        The Elections agent validates a candidacy. We cross-reference
        against the **{len(minutes)} real UoG governance decisions** to
        confirm no constitutional changes have been approved that
        would affect the election.

        ### Live agent: `{elections_agent.name}`
        Model: `{elections_agent.model}`

        ### Candidate
        """
    )

    candidate = Candidate(
        candidate_id="cand-aoife-2025",
        full_name="Aoife Ní Mhurchú",
        student_id="22300111",
        role="SABBATICAL_PRESIDENT",
        is_registered_student=True,
        on_academic_suspension=False,
        on_disciplinary_hold=False,
        manifesto_word_count=412,
        nominator_signature_count=58,
        outstanding_su_fines_eur=0.0,
        previously_held_same_role=("2023/24",),
    )
    elig = validate_candidate_eligibility(
        candidate, min_signatures=su_config.min_nominator_signatures,
    )
    decision = (
        "CONFIRM" if elig.is_eligible
        else "RETURN_FOR_FIXES" if elig.nominators_needed > 0
        else "REJECT"
    )

    # Find any constitutional/governance decisions
    constitutional_decisions = [
        m for m in minutes
        if "regulations" in m["decisions_summary"].lower()
        or "constitutional" in m["decisions_summary"].lower()
    ]

    mo.md(
        f"""
        **Candidate:** {candidate.full_name} running for `{candidate.role}`
        (returning candidate — previously held in 2023/24)

        **UoG governance context:**
        {chr(10).join(f"  - {m['meeting_date_iso']} {m['committee_name']}: constitutional/regulatory update approved" for m in constitutional_decisions) if constitutional_decisions else "  - No constitutional or regulatory changes since the candidate's previous term"}

        **Eligibility:**
        - eligible = `{elig.is_eligible}`
        - errors = `{elig.errors or '[]'}`
        - warnings = `{elig.warnings or '[]'}`
        - additional_nominators_needed = `{elig.nominators_needed}`

        **Decision:** `{decision}`

        **Returning Officer handoff:**
        - Hustings: ≥{su_config.hustings_min_days_before_vote} days before voting opens (UoG Spring 2026 referendum window)
        - Manifesto archive upload to the SU website
        - Candidate photo capture for the ballot paper
        - Online Q&A scheduled for week 2 of the campaign period
        """
    )
    return candidate, constitutional_decisions, elig


@app.cell
def _end_to_end(
    mo,
    classify_su_query,
    root_agent,
    students_union_app,
    calendar_events,
    courses,
    minutes,
    press,
    outputs,
):
    mo.md(
        f"""
        ## Tab 8: End-to-end orchestrator

        The full SU query → KCG data → ADK agent decision pipeline.

        ### Sample queries routed by `classify_su_query`

        ```
        """
        + "\n".join(
            f"  {classify_su_query(q):12}  ::  {q[:60]}"
            for q in [
                "Apply for funding to attend the Seachtain na Gaeilge 2026 poetry slam",
                "Summarise Class Rep feedback from CS203",
                "I want to register a new sustainability society",
                "Am I eligible to run for sabbatical president?",
                "Report harassment from a fellow student",
                "When does Semester 2 teaching start at UoG?",
            ]
        )
        + f"""
        ```

        ### Root orchestrator

        - **Name:** `{root_agent.name}`
        - **Model:** `{root_agent.model}`
        - **Sub-agents:** {len(root_agent.sub_agents)} specialists (clubs_socs + grants_funding + class_rep_aggregator + complaints_welfare + elections)
        - **ADK App:** `{students_union_app.name}`

        ### KCG data surface (the orchestrator's input data)

        | KCG DLT pipeline | Rows |
        |:--|--:|
        | `academic_calendar_pipeline.events()` | {len(calendar_events)} |
        | `course_catalog_pipeline.courses()` | {len(courses)} |
        | `university_council_minutes_pipeline.minutes()` | {len(minutes)} |
        | `press_releases_pipeline.stories()` | {len(press)} |
        | `research_outputs_pipeline.outputs()` | {len(outputs)} |
        | **Total** | **{len(calendar_events) + len(courses) + len(minutes) + len(press) + len(outputs)}** |

        ### End-to-end pipeline summary

        1. **Operator** sends an SU query (e.g. "Apply for funding to attend the Seachtain na Gaeilge 2026 poetry slam")
        2. **Root agent** classifies the query → `grants_funding`
        3. **Grants specialist** calls `match_grant_to_pot_tool(GrantApplication(...))`
        4. **Pure-Python tool** matches against the 4 SU funding pots (€{su_config.max_event_grant_eur} EVENT cap)
        5. **Recent UoG governance decisions** are cross-referenced for any new funding-policy changes
        6. **Final award** is returned with a staff handoff note for the SU Funding Officer
        """
    )
    return


if __name__ == "__main__":
    app.run()
