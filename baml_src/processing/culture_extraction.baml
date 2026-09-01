// BAML schema: Culture Heritage Claim Extraction
//
// Extracts structured cultural-heritage claims from the 6 personal-heritage
// Gemini Deep Research PDFs at `leabharlann/gemini_deep_research/culture/`.
// The extracted claims feed the celtic-asset-generation 5-stage pipeline
// (BAML → CocoIndex v1 → Cognee cognify → Graphiti temporal → LanceDB vector)
// via the `culture_heritage_extract` Dagster asset.
//
// The `confidence` field is consumed by the `low_confidence_review` asset
// check; claims below 0.6 are routed out of the production table.
//
// Usage:
//   from oideachais.data_platform.baml_client import b
//   claims = b.ExtractCultureClaims(pdf_path="...pdf", context="...")
//
// Re-gen after changes:  `cd oideachais && uv run baml-cli generate`

enum EvidenceQuality {
  PRIMARY
  SECONDARY
  INFERENCE
}

class CultureHeritageClaim {
  claim_text string @description("A specific factual claim, ideally with inline citation to a primary or secondary source.")
  people_mentioned string[] @description("Named individuals mentioned in the claim: e.g. 'Neil Deacy', 'Éamonn Deacy', 'Martina Morris', 'Polly Conroy', 'Pádraic Ó Conaire', 'Éamonn Deacy'.")
  places_mentioned string[] @description("Place-names mentioned in the claim: 'Galway', 'Connemara', 'Moycullen', 'Kingston', 'Clifden', 'Castlelyons'.")
  dates string[] @description("Date expressions mentioned in the claim: '1845', '1849-1924', '20th century', 'May 2026'.")
  evidence_quality EvidenceQuality @description("PRIMARY (a birth cert, a memorial, a verified public record) | SECONDARY (newspaper, biography, Wikipedia) | INFERENCE (analytical interpretation or synthesis).")
  wikipedia_links string[] @description("Direct https://en.wikipedia.org/wiki/... URLs cited or implied in the claim.")
  confidence float @description("0.0-1.0 self-rated extraction confidence. Claims with confidence < 0.6 are routed to low_confidence_review.")
}

function ExtractCultureClaims(
  pdf_path: string,
  context: string
) -> CultureHeritageClaim[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
