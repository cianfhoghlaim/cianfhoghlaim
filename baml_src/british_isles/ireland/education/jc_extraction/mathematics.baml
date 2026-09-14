// BAML schema: Mathematics Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Mathematics-specific discriminator for the canonical NCCA junior cycle
// subject area (the 5 strands: Number, Algebra, Shape & Space, Measure, Data).

enum MathJCDiscriminator {
  STRAND_NUMBER   @description("Number strand (JC-MATH-LO-NNN)")
  STRAND_ALGEBRA  @description("Algebra strand (JC-MATH-LO-NNN)")
  STRAND_SHAPE    @description("Shape and Space strand (JC-MATH-LO-NNN)")
  STRAND_MEASURE  @description("Measure strand (JC-MATH-LO-NNN)")
  STRAND_DATA     @description("Data strand (JC-MATH-LO-NNN)")
  CROSS_STRAND    @description("Topic spans multiple strands")
}

class MathematicsSpec {
  subject string @description("Always 'mathematics'")
  lo_code_prefix string @description("Always 'JC-MATH-LO'")
  primary_strand MathJCDiscriminator @description("Dominant NCCA JC Mathematics strand for this syllabus")
  strand_count int @description("Always 5 for JC Mathematics")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (CBA 1 + CBA 2)")
  cba_count int @description("Usually 2 (Mathematical Investigation + Statistical Investigation)")
}

function ExtractMathematicsSpec(
  input: string,
) -> MathematicsSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract mathematics spec from {{ input }}"#

  catch_all (err) {
    MathematicsSpec {
      lo_code_prefix "JC-MATH-LO",
      strand_count 5,
      total_learning_outcomes 0,
      has_cba true,
      cba_count 2,
    }
  }
}
