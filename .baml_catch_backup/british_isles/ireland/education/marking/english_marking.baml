// BAML schema: English Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// English-specific discriminator (EngGenreType + EngSkillType +
// EngCommonMistake). LC English mixes comprehension (Paper 1) +
// composition + comparative study + prescribed text analysis (Paper 2).
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum EngGenreType {
  COMPREHENSION       @description("Reading comprehension of a non-fiction / literary text")
  COMPOSITION         @description("Single-text composition (narrative / discursive / etc.)")
  COMPARATIVE         @description("Comparative study across 3 prescribed texts (2017+ spec)")
  PRESCRIBED_TEXT     @description("Prescribed text analysis (King Lear / Hamnet / etc.)")
  POETRY_ANTHOLOGY    @description("Unseen poetry interpretation")
  DRAMA_SCRIPT        @description("Playscript composition (post-2017)")
}

enum EngSkillType {
  FACTUAL_COMPREHENSION  @description("Find factual answer in a passage")
  INFERENCE              @description("Infer an answer from subtext / tone")
  LANGUAGE_ANALYSIS      @description("Analyse use of language (rhyme, metaphor, register)")
  ARGUMENT_EVALUATION    @description("Evaluate the argument in a speech / article")
  DISCOURSE_WRITING      @description("Write a speech / article / review")
  REFLECTIVE_WRITING     @description("Reflective / diary / first-person composition")
  COMPARATIVE_ESSAY      @description("Comparative essay across 3 prescribed texts")
  SHORT_ANSWER           @description("Short sentence / word answer")
}

enum EngCommonMistake {
  PARAPHRASE_NOT_ANALYSIS  @description("Paraphrases the text instead of analysing technique")
  MISSED_CITATION          @description("Did not cite the prescribed text with line ref")
  DRAMA_FORMAT_WRONG       @description("Composition formatted as narrative instead of playscript")
  COMPARATIVE_BALANCE       @description("Comparative essay uneven — heavy on 2 texts, light on 1st")
  GENERIC_INTRO            @description("Generic introduction that does not anchor to the text")
  VOCAB_GENERIC            @description("Generic vocabulary — does not name the technique")
}

class EngSubjectDiscriminator {
  primary_genre EngGenreType @description("Dominant genre in this paper")
  skill_mix EngSkillType[] @description("The skill mix in the paper")
  has_comparative bool @description("Paper 2 always has comparative since 2017 spec")
  has_composition bool @description("Paper 2 always has composition since 2017 spec")
  most_common_mistake EngCommonMistake
  is_post_2017_spec bool @description("True iff this paper follows the 2017+ revised spec")
}

class EnglishMarkingScheme {
  subject string @description("Always 'english'")
  scheme_code string
  language string @description("EN")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  subject_specific EngSubjectDiscriminator

  total_marks int
  total_questions int
  prescribed_text_count int? @description("Usually 3 since 2017 (King Lear, Hamnet, etc.)")
}

function ExtractEnglishMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> EnglishMarkingScheme {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test english_marking_extraction_smoke {
//   functions [ExtractEnglishMarkingScheme]
//   args {
//     pdf_text <<<
//       "Marking scheme for LC English Paper 2 HL 2024 (post-2017 spec).
//        Comparative on King Lear + Hamnet + 1 other. Most common
//        mistake: students paraphrase the text rather than analysing technique."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
