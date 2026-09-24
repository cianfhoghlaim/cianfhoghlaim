"""
Routing Keywords for the 12-agent fleet.

This module is the canonical home for the L5 `ROUTING_KEYWORDS` dict
used by `CelticAgentOpsComponent` to verify each agent is routable
in the root_agent.

Moved out of `adk/root_agent.py` so it can be imported independently
of the ADK dependency (which may not be installed in every env).
The seed values mirror the agent-fleet-orchestration skill's
"12-bucket" map. The L5 Components append at scaffold time
(CelticAgentOpsComponent._append_routing_keywords) so a new agent
becomes routable without touching this file.

The canonical 12-agent fleet (per the agent-fleet-orchestration skill):
- root_agent (custom)
- 8 ADK agents: curriculum, translation, corpus, research, geospatial,
  statistics, curriculum_comparison, mcp_curriculum
- 3 Agno agents: education_research, bunchloch_research, agui_curriculum
(Voice agent / pipecat is deferred to a follow-on change.)

T4 (2026-07-09) added seed entries for the 8 NCCA subject agents
(gael_agent / math_agent / appm_agent / chem_agent / comp_agent /
engl_agent / geog_agent / hist_agent) — these are mounted under
`defs/5_agent_ops/adk/<slug>_agent/defs.yaml` and the full bucket
is appended by `CelticAgentOpsComponent._append_routing_keywords`
at scaffold time.
"""
from __future__ import annotations

# The seed values. L5 Components extend this dict at build time.
ROUTING_KEYWORDS: dict[str, list[str]] = {
    "root_agent": [],
    "curriculum_agent": [
        "curriculum", "spec", "learning outcome", "ncca", "cfe", "cfw",
        "ccea", "sqa", "leaving cert", "gcse", "a-level",
    ],
    "translation_agent": [
        "translate", "gaeilge", "irish", "scottish gaelic", "welsh",
        "cymraeg", "brezhoneg", "cornish", "manx",
    ],
    "corpus_agent": [
        "corpus", "duchas", "gaois", "tearma", "logainm", "canuint",
        "foclóir",
    ],
    "research_agent": ["research", "paper", "cite", "doi", "arxiv"],
    "education_research_agent": [
        "policy", "report", "oecd", "european commission", "unesco",
    ],
    "bunchloch_research_agent": [
        "m4", "macbook", "local model", "federated", "on-device",
    ],
    "geospatial_agent": [
        "geospatial", "lsoa", "data zone", "map", "school location",
    ],
    "statistics_agent": [
        "statistics", "metric", "benchmark", "performance", "kpi",
    ],
    "curriculum_comparison_agent": [
        "compare", "cross-nation", "side-by-side", "uk vs ireland",
    ],
    "agui_curriculum_agent": ["ag-ui", "streaming", "copilot", "react"],
    "mcp_curriculum_agent": ["mcp", "model context protocol", "tool"],
    # T4 (2026-07-09) — the 8 NCCA subject agents from
    # `cianfhoghlaim/agents/tuatha/<slug>_agent.py`. The full keyword
    # bucket is appended by `CelticAgentOpsComponent._append_routing_keywords`
    # at scaffold time; this seed contains only the cross-subject
    # canonical name(s) so the root_agent can route to the right
    # specialist before scaffold runs.
    "gael_agent": ["gaeilge", "irish", "gaelic"],
    "math_agent": ["mathematics", "maths", "lc maths"],
    "appm_agent": ["applied mathematics", "applied maths"],
    "chem_agent": ["chemistry"],
    "comp_agent": ["computer science", "lc cs", "lc computing"],
    "engl_agent": ["english"],
    "geog_agent": ["geography"],
    "hist_agent": ["history", "irish history"],
    # T5 (2026-07-11) — the 13th bucket for the academic-history agent
    # introduced by openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/.
    # Routes queries like "summarise my degree", "what should I revise",
    # "show me my stats modules", "mo chuid cuntas", etc. before the
    # generic statistics_agent bucket.
    "academic_history_agent": [
        "my history", "my notes", "my modules", "my assignments",
        "my exam history", "my answers", "my progress", "my timeline",
        "what have i done", "what did i cover", "how am i doing",
        "summarise my degree", "summarise my year",
        "what should i revise", "next step",
        "academic record", "transcript", "study history",
        "stair acadúil", "mo chuid cuntas", "mo nótaí",
        "mo shonraí", "mo mhodúil", "mo scrúduithe",
        "mo chuid oibre", "my work", "my essays",
        "what have i submitted", "my last attempt",
        "my strengths", "my weaknesses",
        "st311", "st312", "ma335", "ma347", "ma410",
        "ms421", "st412", "st419", "cs402",
        "numerical analysis", "nonlinear systems",
    ],
    # T6 (2026-09-23) — the 14th bucket for the Students' Union root
    # orchestrator introduced by openspec/changes/2026-09-23-consolidate-
    # uog-tertiary-pipeline-v1/. Routes SU-specific queries (clubs/socs,
    # grants, class rep, complaints, elections) before any generic bucket.
    "students_union_root_agent": [
        "students union", "su ", "clubs", "societies", "socs",
        "affiliate", "registration form", "start a society",
        "grant", "funding", "budget", "subsid", "travel grant",
        "equipment grant", "welfare grant", "event grant",
        "class rep", "rep report", "module review", "lecturer concerns",
        "assessment feedback", "complaint", "harassment", "discrimination",
        "hardship", "welfare concern", "safeguard", "election",
        "candidate", "nominat", "sabbatical", "sabbat", "referendum",
        "vote", "ballot", "president", "vp ",
        "comhaltas", "mac léinn", "ollscoil na gaillimhe",
    ],
    # T7 (2026-09-23) — the 15th-19th buckets for the K-12 TEACHER agents
    # introduced by openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
    # Routes teacher-centric queries (lesson plan, assessment, SEN, parent,
    # PD) before any generic bucket.
    "lesson_planner_agent": [
        "lesson plan", "planning", "scheme of work", "weekly plan",
        "tasc an lae", "plean ceachta",
    ],
    "assessment_scorer_agent": [
        "cba", "classroom-based assessment", "assessment task",
        "scoring", "marking", "rubric", "feedback", "grade",
        "exam paper", "scrap exam",
    ],
    "sen_pastoral_care_agent": [
        "sen", "special educational needs", "pastoral", "welfare",
        "safeguarding", "children first", "asd", "spld",
        "senco", "inclusive education", "reasonable accommodation",
        "resource teaching", "learning support",
    ],
    "parent_meeting_agent": [
        "parent meeting", "parent-teacher", "ptm", "tuismitheoir",
        "school report", "progress meeting",
    ],
    "professional_learning_agent": [
        "oide", "pdst", "cpd", "professional development",
        "summer course", "cluster meeting", "induction",
        "career stage", "newly qualified teacher",
    ],
    # T8 (2026-09-23) — the 20th-24th buckets for the K-12 STUDENT agents
    # introduced by openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
    # Routes post-primary student queries (homework + CBA + study + wellbeing
    # + exam) before any generic bucket.
    "homework_tracker_agent": [
        "homework", "obair bhaile", "assignment", "due date",
        "tracking homework", "homework tracker",
    ],
    "cba_planner_agent": [
        "cba", "classroom-based assessment", "cba planning",
        "cba tracker", "brief", "draft", "final",
    ],
    "study_plan_agent": [
        "study plan", "revision", "leaving cert", "lc",
        "transition year", "ty", "exam prep", "past papers",
    ],
    "wellbeing_agent": [
        "wellbeing", "mental health", "stress", "anxiety",
        "meabhairshláinte", "wellbeing check-in",
    ],
    "exam_timetable_agent": [
        "exam timetable", "state examinations commission",
        "sec timetable", "lc timetable", "jc timetable",
        "exam centre", "exam clashes", "exam logistics",
    ],
}


__all__ = ["ROUTING_KEYWORDS"]
