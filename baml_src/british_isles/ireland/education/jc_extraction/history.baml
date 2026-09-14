// BAML schema: History Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// History-specific discriminator for the canonical NCCA junior cycle
// subject area (the 4 strands: The Nature of History, Eras of Conflict
// and Change, Life Society Work and Culture in the Past, Ireland and
// the Wider World).

enum HistJCDiscriminator {
  STRAND_NATURE          @description("The Nature of History strand (JC-HIST-LO-NNN)")
  STRAND_ERAS            @description("Eras of Conflict and Change strand (JC-HIST-LO-NNN)")
  STRAND_LIFE_SOCIETY    @description("Life, Society, Work and Culture in the Past strand (JC-HIST-LO-NNN)")
  STRAND_IRELAND_WIDER   @description("Ireland and the Wider World strand (JC-HIST-LO-NNN)")
  CROSS_STRAND           @description("Topic spans multiple strands")
}

class HistorySpec {
  subject string @description("Always 'history'")
  lo_code_prefix string @description("Always 'JC-HIST-LO'")
  primary_strand HistJCDiscriminator @description("Dominant NCCA JC History strand for this syllabus")
  strand_count int @description("Always 4 for JC History")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (CB1 + CB2)")
  cba_count int @description("Usually 2 (The Past in My Place + A Life in History)")
}

function ExtractHistorySpec(
  input: string,
) -> HistorySpec {
  client ExtractEn
    prompt #"{{ _.role('user') }} Extract history spec from {{ input }}"#


}
