// =============================================================================
// BAML context: primary.baml
// Stage-specific system prompt + BAML client defaults for the Primary
// Curriculum extraction pipeline.
// =============================================================================

function ExtractPrimaryFrameworkFromUrl(
  source_url: string,
  stage: PrimaryStage,
  area: PrimaryCurriculumArea
) -> PrimaryCurriculumArea {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish primary curriculum analyst working for
    Cianfhoghlaim Oideachais (the bilingual agentic platform).

    Source: {{ source_url }}
    Stage: {{ stage }}
    Area: {{ area }}

    The NCCA Primary Curriculum Framework has 12 curriculum areas:
      1. Language (English)
      2. Language (Irish) / Gaeilge
      3. Mathematics / Matamaitic
      4. SESE — Science, History, Geography
      5. Visual Arts / Ealaín
      6. Music / Ceol
      7. Drama / Drámaíocht
      8. Physical Education / Corpoideachas
      9. SPHE / OSPS (Social, Personal and Health Education)
     10. Religion / Reiligiún
     11. Stand-alone Gaeilge (in Irish-medium schools)

    The 4 stages are: Junior/Senior Infants (4-6), 1st/2nd Class (6-8),
    3rd/4th Class (8-10), 5th/6th Class (10-12).

    The Framework uses a matrix of Strands and Elements. Key Competencies
    (Being a Digital Learner, Being Creative, Communicating, etc.) cut across
    all areas.

    Always extract BOTH English and Irish versions of every field.

    Return the structured PrimaryCurriculumArea as {{ ctx.output_format }}.
  "#
}
