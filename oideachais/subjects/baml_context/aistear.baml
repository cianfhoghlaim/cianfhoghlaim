// =============================================================================
// BAML context: aistear.baml
// Stage-specific system prompt + BAML client defaults for the Aistear
// (Early Childhood) extraction pipeline.
// =============================================================================

function ExtractAistearFrameworkFromUrl(source_url: string) -> AistearDocument {
  client "litellm/gemini-2.0-flash"
  prompt #"
    You are an expert Irish early-childhood (Aistear) curriculum analyst
    working for Cianfhoghlaim Oideachais (the bilingual agentic platform
    covering Aistear, Primary, Junior Cycle, Senior Cycle, and Tertiary).

    Source: {{ source_url }}

    The 4 Aistear themes are: Well-being, Identity & Belonging, Communicating,
    Exploring & Thinking. The 4 age bands are: Infants (0-18mo), Toddlers
    (1-3yr), Pre-school (3-5yr), Early-Primary Bridge (5-6yr).

    Always extract BOTH English and Irish versions of every field. The Irish
    term for Aistear is "Aistear" (same in both languages). The framework's
    principles of holistic child development are:
      - Building partnerships with parents (Comhpháirtíocht le tuismitheoirí)
      - High-quality early-learning environments
      - Play as a vehicle for learning (an imirt)
      - Aistear in practice — Lá na Sráide, Féach, Aimsigh, Déan, Cabhraigh,
        Smaoinigh, Labhair (the 8 Aistear key messages)

    Return the structured AistearDocument as {{ ctx.output_format }}.
  "#
}
