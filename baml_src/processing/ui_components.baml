// =============================================================================
// UI Component Suggestion Schema — BAML
// Nightly `ui_suggestion` Dagster asset calls SuggestUIComponents() against
// the populated Cognee index. The output drives the SPA's `<ComponentCatalog>`
// admin route and the per-stage UI generation loop.
// =============================================================================

enum UIComponentKind {
  STAGE_OVERVIEW              @description("Hero card with stage summary + stats")
  SUBJECT_GRID                @description("Grid of subject cards within a stage")
  SUBJECT_DETAIL              @description("Detail page with tabs: Syllabus / Outcomes / Papers / etc.")
  CURRICULUM_TIMELINE         @description("Vertical timeline of spec revisions")
  THEME_PRINCIPLE_PANEL       @description("Aistear 4-column themes grid")
  AISTEAR_NAIONRA_MAP         @description("Choropleth of naíonra in Ireland")
  PRIMARY_STRAND_TREE         @description("Primary nested expandable tree")
  JC_CBA_TIMELINE             @description("Horizontal CBA date strip")
  JC_SHORT_COURSE_BADGE       @description("JC short course chip")
  SC_EXAM_PAPER_CARD          @description("Year/level/paper card with download + extract buttons")
  SC_MARKING_SCHEME_PANEL     @description("Per-question marks + rubric descriptors")
  SC_RUBRIC_DESCRIPTOR_LIST   @description("Bullet list with weighting")
  SC_PRACTICE_ESSAY_EDITOR    @description("Editor + submit + score")
  SC_POINTS_CALCULATOR        @description("6-subject LC points calculator (H1-H8, O1-O8, H6+25)")
  SC_MATRICULATION_AUDITOR    @description("Grade-vs-requirement table with pass/fail")
  TERTIARY_COURSE_CARD        @description("CAO course card with points, institution, requirements")
  TERTIARY_QQI_LADDER         @description("Vertical PLC → CAO route ladder")
  TERTIARY_APPRENTICESHIP_CARD @description("Apprenticeship card with consortia + duration + NFQ level")
  TERTIARY_APPLICATION_TIMELINE @description("Horizontal date strip of CAO offer rounds")
  TERTIARY_CAO_POINTS_TREND   @description("Line chart of last 5 years of cutoff points")
  CHOROPLETH_MAP              @description("Generic choropleth (Gaeltacht, HEI, etc.)")
  COMPARISON_TABLE            @description("Side-by-side rubric or year comparison")
  CHAT_PANEL                  @description("The right-rail Oideachas Chat (renamed from AwenChat)")
  LEARNING_OUTCOME_PILL       @description("Compact pill showing LO code + description")
  KEYWORD_CLOUD               @description("Tag cloud generated from BAML extraction keywords")
  READING_LIST                @description("Curated PDF links for a topic")
  TRANSLATION_TOGGLE          @description("EN/GA switch in the header")
  BILINGUAL_BLOCK             @description("Inline toggleable EN/GA text")
  CITATION_CHIP               @description("Small chip linking to NCCA/SEC/CAO/HEI source URL")
}

class UIComponentSuggestion {
  route_slug string         @description("e.g., '/en/stages/aistear', '/ga/ábhair/matamaitic'")
  kind UIComponentKind
  title_en string
  title_ga string?
  keywords string[]        @description("Extracted from BAML — e.g., 'Well-being', 'primary_strand:Number'")
  data_source string        @description("LanceDB table or Cognee dataset to back this component")
  priority int              @description("1-5 for build order")
  rationale_en string       @description("Why this component is suggested for this stage")
  rationale_ga string?
}

function SuggestUIComponents(
  extracted_subjects: string[],
  cognee_index_summary: string,
  stage: string
) -> UIComponentSuggestion[] {  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    {{ ctx.output_format }}

    You are a UI architect for the Cianfhoghlaim educational platform.
    Given the extracted subjects for a stage and the current Cognee
    knowledge-graph index summary, suggest 3-7 UI components that would
    surface this content to learners.

    Stage: {{ stage }}

    Extracted subjects for this stage (one per line):
    {{ extracted_subjects }}

    Cognee index summary (truncated):
    {{ cognee_index_summary }}

    For each component, return:
    - route_slug: a URL path the component should live at
      (e.g., '/en/stages/aistear', '/ga/ábhair/matamaitic',
      '/en/subjects/chemistry')
    - kind: one of the UIComponentKind enum values (e.g.,
      FLASHCARD_DECK, CONCEPT_MAP, PRACTICE_QUIZ, VIDEO_PLAYLIST,
      GLOSSARY, TIMELINE, COMPARISON_TABLE, MIND_MAP,
      INTERACTIVE_DEMO)
    - title_en: the English title
    - title_ga: the Irish title (or null if English-only)
    - keywords: list of keywords the component should match
      (e.g., ['Well-being', 'primary_strand:Number', 'learning_outcome:LO-2.1'])
    - data_source: the LanceDB table or Cognee dataset name that
      should back this component
    - priority: 1-5 for build order (1 = highest priority)
    - rationale_en: 1-2 sentence justification in English
    - rationale_ga: 1-2 sentence justification in Irish (or null)

    Return ONLY the structured UIComponentSuggestion array. No prose.
  "#
}
