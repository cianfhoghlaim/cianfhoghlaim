// BAML schema: Mathematics Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// Mathematics-specific discriminator (MathMarkingBand + MathQuestionType +
// MathCommonMistake) and the `ExtractMathematicsMarkingScheme` function.
//
// Replaces the generic ExtractMarkingSchemeGuideline path for
// `subject="mathematics"` so the MarkAllocation items reflect
// Mathematics-specific mistake patterns (sign errors, arithmetic slips,
// algebraic manipulation errors, unit errors) and question types
// (WORKED_SOLUTION / PROOF / VISUAL_INTERPRETATION).
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   scheme = b.ExtractMathematicsMarkingScheme(pdf_text, year=2024, level="hl")
//   print(scheme.subject_specific.most_common_mistake)
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Subject-specific enums (the discriminator)
// ============================================================================

enum MathMarkingBand {
  H1 @description("Higher Level H1: 80-100% (Distinction)")
  H2 @description("Higher Level H2: 70-79%")
  H3 @description("Higher Level H3: 60-69%")
  H4 @description("Higher Level H4: 50-59%")
  H5 @description("Higher Level H5: 40-49%")
  H6 @description("Higher Level H6: 30-39%")
  H7 @description("Higher Level H7: 0-29% (Ungraded)")
  O1 @description("Ordinary Level O1: 80-100% (Distinction)")
  O2 @description("Ordinary Level O2: 70-79%")
  O3 @description("Ordinary Level O3: 60-69%")
  O4 @description("Ordinary Level O4: 50-59%")
  O5 @description("Ordinary Level O5: 40-49%")
  O6 @description("Ordinary Level O6: 30-39%")
  O7 @description("Ordinary Level O7: 0-29% (Ungraded)")
}

enum MathQuestionType {
  WORKED_SOLUTION @description("Step-by-step calculation with marking-scheme points")
  PROOF           @description("Construct a mathematical proof")
  VISUAL          @description("Read from a graph, table, or diagram")
  SHORT_ANSWER    @description("Single-step answer")
  WORD_PROBLEM    @description("Real-world contextual application")
}

enum MathCommonMistake {
  SIGN_ERROR            @description("Sign error in algebra or arithmetic")
  ARITHMETIC_SLIP       @description("Computational arithmetic slip")
  UNIT_ERROR            @description("Unit conversion or omission error")
  FORMULA_MISAPPLIED    @description("Wrong formula or formula misapplied")
  ALGEBRAIC_REARRANGE   @description("Algebraic manipulation error in rearrangement")
  GRAPH_MISREAD         @description("Misread value from a graph or table")
  NOT_SIMPLIFIED        @description("Final answer not simplified")
  MISSING_CONSTRAINT    @description("Solution ignores a stated domain/range constraint")
  INVERSE_OP_WRONG      @description("Applied wrong inverse operation")
  BRACKET_MISUSE        @description("Bracket/distributive error")
}

class MathSubjectDiscriminator {
  primary_topic string @description("e.g. 'Calculus', 'Algebra', 'Statistics' (NCCA topic)")
  band_scheme MathMarkingBand @description("The grade-band scheme for this subject (HL or OL)")
  question_types MathQuestionType[] @description("Dominant question types in this paper")
  most_common_mistake MathCommonMistake @description("The single most frequent student mistake pattern")
  has_formula_sheet bool @description("LC Maths Paper 1 + 2 always have a formula sheet")
  is_higher_level bool @description("True iff this is the HL paper; HL has calculus & proofs")
}

class MathematicsMarkingScheme {
  // Inherited generic MarkingScheme fields (re-declared for per-subject richness)
  subject string @description("Always 'mathematics'")
  scheme_code string @description("e.g. 'SCSEC25_Maths_marking_2024'")
  language string @description("EN or GA")
  level string @description("HL / OL / FDN")
  year int
  source_pdf string

  // Inherited BAML types referenced for compatibility with the generic extractor
  grade_descriptors GradeDescriptor[] @description("5 generic grade bands from the canonical extractor")
  mark_allocations MarkAllocation[]

  // Mathematics-specific discriminator
  subject_specific MathSubjectDiscriminator

  total_marks int
  total_questions int
  estimated_full_marks_time_minutes int @description("Time to attempt all questions at full marks rate")
}

// ============================================================================
// BAML function — the per-subject Mathematics marking-scheme extractor
// ============================================================================

function ExtractMathematicsMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> MathematicsMarkingScheme {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    MathematicsMarkingScheme {
      year 0,
      source_pdf "",
      mark_allocations null,
      subject_specific mathsubjectdiscriminator {},
      total_marks 0,
      total_questions 0,
    }
  }
}

// test mathematics_marking_extraction_smoke {
//   functions [ExtractMathematicsMarkingScheme]
//   args {
//     pdf_text <<<
//       "Marking scheme for LC Mathematics Paper 2 HL 2024. Most common
//        mistake: sign error when applying chain rule in differentiation."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
