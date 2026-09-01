// BAML schema: NCCA Certification Criteria Extractor
//
// Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
// (Phase 7 of the cianfhoghlaim-nua v6 era plan). Lifted + OSS-ified
// from the gemini_hackathon W14 certificate pipeline.
//
// Extracts the official certification criteria from the 5 NCCA
// policy PDFs (data/ireland/ncca_policy/). Stage 1 of the 7-stage
// certificate pipeline at meaisinfhoghlaim/certificate/pipeline.py.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

// ============================================================================
// Canonical enums
// ============================================================================

enum NCCACertificationStage {
  AISTEAR
  BUNSCOIL
  MEANSCOIL
  SCOIL_SINSEARACH
  OLLSCOIL
}

enum NCCAAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum NCCAKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
  STAYING_WELL
}

// ============================================================================
// Output classes
// ============================================================================

class CertificationCitation {
  source_pdf string @description("The NCCA policy PDF filename")
  page int @description("1-indexed page number")
  quote string @description("Verbatim quote from the page")
  relevance string @description("1-sentence explanation of how this page informed the criteria")
}

class NCCAPolicyCriteria {
  stage NCCACertificationStage
  subject_slug string
  award_descriptor NCCAAwardDescriptor
  descriptor_vocabulary NCCAAwardDescriptor[]
  key_competencies NCCAKeyCompetency[]
  policy_citations CertificationCitation[]
}

// ============================================================================
// The function (Stage 1 of the 7-stage certificate pipeline)
// ============================================================================

function ExtractNCCAPolicyCriteria(
  pdf_text: string,
  subject_slug: string,
  stage: NCCACertificationStage
) -> NCCAPolicyCriteria {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting the official NCCA certification
    criteria from the canonical 5 NCCA policy PDFs (data/ireland/ncca_policy/).
    The source is the 5 official NCCA policy documents (SC-L1-L2
    Programme Statement, key competencies in Senior Cycle, SCR
    advisory report, online learning environments, online certification
    + reporting). The subject is {{ subject_slug }} and the stage is
    {{ stage }}.

    PDF text: {{ pdf_text }}

    Extract:
    - award_descriptor: the canonical NCCA award descriptor (one of
      Exceptional, Above expectations, In line with expectations,
      Below expectations, Far below expectations)
    - descriptor_vocabulary: the 4-6 canonical descriptors for the stage
    - key_competencies: the 5 (or 6 with Staying Well) NCCA Key
      Competencies that apply
    - policy_citations: every cited page (one per cited quote)

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test block (per the @assert requirement)
// ============================================================================

test certification_lc_chemistry_sanity {
  functions [ExtractNCCAPolicyCriteria]
  args {
    pdf_text "NCCA LC Chemistry: The 5 award descriptors range from Exceptional to Far below expectations. Key competencies: Communicating, Information Processing, Critical and Creative Thinking, Personal Effectiveness, Working with Others."
    subject_slug "chemistry"
    stage NCCACertificationStage.SCOIL_SINSEARACH
  }
}
