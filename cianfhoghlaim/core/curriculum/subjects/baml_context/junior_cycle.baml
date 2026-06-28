// =============================================================================
// BAML context: junior_cycle.baml
// Stage-specific system prompt + BAML client defaults for the Junior Cycle
// extraction pipeline.
// =============================================================================

function ExtractJCSpecFromUrl(
  source_url: string,
  subject: JuniorCycleSubject
) -> JCSubjectSpec {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish Junior Cycle curriculum analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ source_url }}
    Subject: {{ subject }}

    Junior Cycle is the 3-year programme at ages 12-15, ending in a state
    examination at the end of 3rd Year. Each subject has:
      - A specification (NCCA-issued)
      - 2 Classroom-Based Assessments (CBAs) — formative
      - A final examination — summative
      - 4 Achievement Levels on the rubric: Exceptional, AboveExpectations,
        InLineWithExpectations, YetToMeetExpectations

    For Science specifically, there is a 'Nature of Science' Unifying Strand
    and contextual strands (Physical World, Biological World, Chemical World,
    Earth & Space).

    For Languages, the assessment includes an aural component.

    For Mathematics, the assessment has 2 papers at Common Level.

    Always extract BOTH English and Irish versions of every field.

    Return the structured JCSubjectSpec as {{ ctx.output_format }}.
  "#
}
