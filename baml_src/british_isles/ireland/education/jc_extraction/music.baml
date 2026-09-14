// BAML schema: Music Junior Cycle Extractor (BIEP v1 Phase 19)
//
// Per the 2026-09-12-dlt-1.29-feature-adoption-v1 change. Subject-specific
// extension of the canonical JuniorCycleCurriculumSpec in
// baml_src/british_isles/_shared/junior_cycle_template.baml. Adds the
// Music-specific discriminator for the canonical NCCA junior cycle
// subject area (the 3 strands: Performing, Composing, Listening).

enum MusJCDiscriminator {
  STRAND_PERFORMING  @description("Performing strand (JC-MUS-LO-NNN)")
  STRAND_COMPOSING   @description("Composing strand (JC-MUS-LO-NNN)")
  STRAND_LISTENING   @description("Listening strand (JC-MUS-LO-NNN)")
  CROSS_STRAND       @description("Topic spans multiple strands")
}

class MusicSpec {
  subject string @description("Always 'music'")
  lo_code_prefix string @description("Always 'JC-MUS-LO'")
  primary_strand MusJCDiscriminator @description("Dominant NCCA JC Music strand")
  strand_count int @description("Always 3 for JC Music")
  total_learning_outcomes int @description("Number of LOs in the NCCA spec")
  has_cba bool @description("Always true (CBA 1 + CBA 2 composition + performance)")
  cba_count int @description("Usually 2 (composition + performance portfolio)")
  has_listening_exam bool @description("Always true — JC Music has a formal listening exam")
}

function ExtractMusicSpec(
  input: string,
) -> MusicSpec {  client ExtractEn
    prompt #"{{ _.role('user') }} Extract music spec from {{ input }}"#

  catch_all (err) {
    MusicSpec {
      lo_code_prefix "JC-MUS-LO",
      strand_count 3,
      total_learning_outcomes 0,
      has_cba true,
      cba_count 2,
      has_listening_exam true,
    }
  }
}
