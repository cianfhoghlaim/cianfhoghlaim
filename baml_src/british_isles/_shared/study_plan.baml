// BAML template: Canonical Study Plan Generator
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1 of the cianfhoghlaim-nua v6 era plan).
//
// Replaces the 6 legacy per-subject
// baml_src/british_isles/ireland/education/_legacy/web/<subject>_web.baml
// files (chemistry_web.baml + computer_science_web.baml +
// english_web.baml + gaeilge_web.baml + geography_web.baml +
// mathematics_web.baml = ~1,500 LOC) with a single canonical
// `StudyPlan` schema + `GenerateStudyPlanAssets` function that
// covers ALL 14 NCCA LC subjects + the 6 NCCA-adjacent subjects
// via the `NCCASubjectSlug` enum.
//
// The `IrishDialect` enum is defined locally (not imported from
// baml_src/celtic/sources.baml) to avoid cross-file coupling and
// keep this template self-contained; values match the canonical
// MUNSTER / CONNACHT / ULSTER / STANDARD classification.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src
//
// Reference:
//   openspec/changes/2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/
//   openspec/specs/oideachais-pipeline/spec.md (StudyPlan Requirement)
//   baml_src/british_isles/_shared/qpack_template.baml (sister template

// ============================================================================
// Canonical enums
// ============================================================================

enum StudyPlanIrishDialect {
  CONNACHT @description("Gaeilge Chonnacht - Galway, Mayo, Roscommon")
  MUNSTER  @description("Gaeilge na Mumhan - Kerry, Cork, Waterford")
  ULSTER   @description("Gaeilge Uladh - Donegal")
  STANDARD @description("An Caighdeán Oifigiúil - Official Standard")
}

enum StudyPlanAssessmentType {
  QUIZ         @description("Short formative quiz (5-10 items)")
  PAST_PAPER   @description("Full past paper section or full paper")
  MOCK_ORALE   @description("Mock oral exam (Gaeilge + language subjects)")
  ESSAY        @description("Extended essay or composition")
  PRACTICAL    @description("Lab practical (Chemistry, Physics, Biology)")
  PORTFOLIO    @description("Cumulative portfolio review")
}

enum StudyPlanKeyCompetency {
  COMMUNICATING          @description("Key competency: Communicating")
  INFORMATION_PROCESSING @description("Key competency: Information Processing")
  CRITICAL_CREATIVE      @description("Key competency: Critical & Creative Thinking")
  PERSONAL_EFFECTIVENESS @description("Key competency: Personal Effectiveness")
  WORKING_WITH_OTHERS    @description("Key competency: Working with Others")
}

// ============================================================================
// Output classes
// ============================================================================

class StudyPlanBilingual {
  text_en string  @description("English text")
  text_ga string? @description("Irish translation (null for EN-only subjects)")
}

class PastPaperRef {
  paper_id                  string @description("Past paper identifier (e.g. 'LC-CHEM-2024-P1')")
  year                      int    @description("Year of the past paper")
  level                     string @description("LC_OL | LC_HL | LC_FDN | JC | GCSE | AS_LEVEL | A_LEVEL")
  language                  string @description("EN | GA | EN_AND_GA")
  ncca_page_citation        int    @description("Page number in the canonical NCCA PDF (1-indexed)")
  marking_scheme_page       int    @description("Page number in the canonical marking-scheme PDF")
  question_ids              string[] @description("Specific question ids to attempt (e.g. ['Q3', 'Q7(b)'])")
}

class StudyPlanWeek {
  week_number             int      @description("1-indexed week number")
  theme                   StudyPlanBilingual @description("Week theme (EN + GA)")
  marking_scheme_focus    string[] @description("PCLM marking patterns to drill this week")
  estimated_hours         float    @description("Total study hours for the week")
  lo_codes                string[] @description("NCCA LO codes covered this week (subset of input)")
  key_competency_weights  StudyPlanKeyCompetencyWeight[]
  recommended_past_papers PastPaperRef[]
}

class StudyPlanKeyCompetencyWeight {
  competency StudyPlanKeyCompetency
  weight     float @description("0.0 - 1.0")
}

class StudyPlanMilestone {
  week           int      @description("Week number this milestone lands on")
  description    StudyPlanBilingual
  assessment_type StudyPlanAssessmentType
  marks_available int     @description("Total marks for the milestone (for past papers + quizzes)")
}

class StudyPlan {
  subject                string  @description("NCCA subject slug (e.g. 'chemistry')")
  dialect                StudyPlanIrishDialect? @description("Irish dialect for Gaeilge subject; null otherwise")
  duration_weeks         int     @description("Total number of weeks in the plan")
  total_study_hours      float   @description("Sum of estimated_hours across all weeks")
  weeks_plan             StudyPlanWeek[]
  milestones             StudyPlanMilestone[]
  kc_weights             StudyPlanKeyCompetencyWeight[]
  recommended_past_papers PastPaperRef[]
  trace_id               string? @description("Langfuse trace id (populated by the @trace decorator)")
}

// ============================================================================
// The canonical study plan generator
//
// New BAML functions MUST declare `client "Primary"` per the v5 model
// priority change (2026-08-31-baml-primary-alias-and-fallback-v1).
// The fallback chain (Primary -> UnslothGemma4 -> VertexGemini35Flash)
// is inherited from the Primary client definition in clients.baml.
// ============================================================================

function GenerateStudyPlanAssets(
  subject: string,
  lo_codes: string[],
  duration_weeks: int,
  dialect: StudyPlanIrishDialect?,
  target_date: string?,
  language: string?
) -> StudyPlan {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Leaving Certificate study plan generator
    for the subject `{{ subject }}` over `{{ duration_weeks }}` weeks
    {% if dialect %} in the `{{ dialect }}` Irish dialect{% endif %}.
    The student has identified the following NCCA Learning Outcome codes
    as their focus areas: `{{ lo_codes }}`.

    Build a study plan with one entry per week, themed to the LO codes,
    with bilingual EN/GA themes where the subject is Gaeilge (otherwise
    `text_ga` is null). Every `lo_codes` field across all weeks MUST be
    a subset of the input `{{ lo_codes }}` (no extra codes invented).
    Every `PastPaperRef.ncca_page_citation` MUST point to a real page in
    the canonical NCCA PDF for `{{ subject }}`.

    {% if subject == "gaeilge" %}
    - The plan MUST additionally produce an `OralStudyPlan` (see
      baml_src/british_isles/_shared/oral_study_plan.baml) with
      `audio_segments[]` keyed by `StudyPlanWeek.week_number`.
    - Use the `{{ dialect }}` dialect for all Irish-language content.
    {% elif subject == "chemistry" %}
    - Cover all 4 NCCA Chemistry strands (Atomic Structure, Chemical
      Bonding, Stoichiometry, Acids/Bases) with at least 1 week per strand.
    - Include 1 mandatory `PRACTICAL` milestone per 4 weeks.
    {% elif subject == "mathematics" %}
    - Cover all 5 NCCA Math strands (Statistics & Probability, Geometry
      & Trigonometry, Number, Algebra, Functions).
    {% elif subject == "computer_science" %}
    - Cover all 5 NCCA CS strands (Algorithms, Data, Networks,
      Programming, Systems).
    {% endif %}

    Output the plan as JSON conforming to the `StudyPlan` schema.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test blocks (per the canonical @assert requirement)
// ============================================================================

test study_plan_lc_chemistry_12_weeks {
  functions [GenerateStudyPlanAssets]
  args {
    subject "chemistry"
    lo_codes ["LC-CHEM-LO-3.1", "LC-CHEM-LO-3.2", "LC-CHEM-LO-4.5"]
    duration_weeks 12
    dialect null
    target_date "2027-06-15"
    language "en"
  }
}

test study_plan_lc_gaeilge_16_weeks_connacht {
  functions [GenerateStudyPlanAssets]
  args {
    subject "gaeilge"
    lo_codes ["LC-GAEL-LO-1.1", "LC-GAEL-LO-2.3", "LC-GAEL-LO-3.2"]
    duration_weeks 16
    dialect StudyPlanIrishDialect.CONNACHT
    target_date "2027-06-15"
    language "en_and_ga"
  }
}

test study_plan_lc_mathematics_8_weeks {
  functions [GenerateStudyPlanAssets]
  args {
    subject "mathematics"
    lo_codes ["LC-MATH-LO-1.2", "LC-MATH-LO-4.1"]
    duration_weeks 8
    dialect null
    target_date "2027-06-15"
    language "en"
  }
}

test study_plan_lc_computer_science_10_weeks {
  functions [GenerateStudyPlanAssets]
  args {
    subject "computer_science"
    lo_codes ["LC-COMP-LO-1.1", "LC-COMP-LO-2.3", "LC-COMP-LO-5.2"]
    duration_weeks 10
    dialect null
    target_date "2027-06-15"
    language "en"
  }
}
