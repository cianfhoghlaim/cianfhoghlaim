// BAML schema: Geography Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// Geography-specific discriminator (GeoSkillType + GeoRegionalFocus +
// GeoCommonMistake). LC Geography mixes short-answer factual recall,
// OS-map interpretation, and discursive essays on regional / thematic
// topics.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum GeoSkillType {
  FACTUAL_RECALL      @description("Short factual answer (1-3 marks)")
  OS_MAP              @description("Ordnance Survey map interpretation")
  GRAPH_INTERPRET     @description("Read from climate graph / population pyramid")
  DISCURSIVE_SHORT    @description("50-80 word short discursive answer")
  DISCURSIVE_LONG     @description("Extended essay-style discursive answer (15-30 marks)")
  CASE_STUDY          @description("Regional / thematic case study answer")
}

enum GeoRegionalFocus {
  IRELAND_CORE      @description("Core (Irish) regional geography")
  EUROPEAN_UNION    @description("EU regional focus")
  GLOBAL_PATTERNS   @description("Global pattern (climate, tectonics)")
  SUB_SAHARAN       @description("Sub-Saharan regional case study")
  ATLANTIC_FRINGE   @description("European Atlantic fringe")
  SOUTH_ASIA        @description("South Asian regional case study")
  MIXED_REGIONAL    @description("Mix of regions across questions")
}

enum GeoCommonMistake {
  ORDNANCE_SURVEY_MISREAD   @description("Misread grid reference or scale on OS map")
  CASE_STUDY_VAGUE          @description("Vague references lacking place-specific detail")
  PROCESS_VS_FACT           @description("Confused process explanation with rote fact")
  UNITS_OMITTED             @description("Omitted units (°C, mm, %, m, km)")
  DIAGRAM_NOT_ANNOTATED     @description("Diagram missing arrows / labels")
  CONTRADICTORY_POINTS      @description("Contradictory points in discursive answer")
}

class GeoSubjectDiscriminator {
  primary_skill GeoSkillType @description("The dominant skill tested in this paper")
  regional_focus GeoRegionalFocus @description("The dominant regional focus")
  has_os_map bool @description("True iff the paper includes OS map interpretation (Paper 1)")
  has_discursive_essays bool @description("True iff the paper has the 30-mark essays (Paper 2)")
  most_common_mistake GeoCommonMistake
}

class GeographyMarkingScheme {
  subject string @description("Always 'geography'")
  scheme_code string
  language string @description("EN only for Geography")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  subject_specific GeoSubjectDiscriminator

  total_marks int
  total_questions int
  os_map_pages int? @description("Number of OS map pages in the paper")
}

function ExtractGeographyMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> GeographyMarkingScheme {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test geography_marking_extraction_smoke {
//   functions [ExtractGeographyMarkingScheme]
//   args {
//     pdf_text <<<
//       "Marking scheme for LC Geography Paper 1 HL 2024. OS map
//        interpretation: 80 marks. Most common mistake: students
//        confuse grid reference easting and northing."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
