// EUR-Lex extraction BAML schema.
//
// Specialised extraction functions for EUR-Lex regulations, directives

class EURLexRegulation {
  celex_id string @description("Canonical CELEX ID, e.g. '32024R0903'")
  language EULanguage
  title string
  publication_date string?
  oj_reference string? @description("Official Journal reference (e.g. 'OJ L 123, 12.5.2024')")
  in_force bool @description("True if the regulation is currently in force")
  amends string[]? @description("CELEX IDs of regulations this one amends")
  repealed_by string? @description("CELEX ID of the regulation that repealed this one")
  source_url string
  content_hash string?
  key_changes string[]? @description("Short list of the substantive changes the regulation introduces")
  affected_sectors string[]? @description("High-level sectors (e.g. 'digital', 'agriculture', 'finance')")
}

class EURLexDirective {
  celex_id string
  language EULanguage
  title string
  publication_date string?
  transposition_deadline string? @description("Member-state transposition deadline (ISO 8601)")
  in_force bool
  source_url string
  content_hash string?
  objectives string[]? @description("The directive's stated objectives")
  affected_sectors string[]?
}

class EURLexDecision {
  celex_id string
  language EULanguage
  title string
  publication_date string?
  addressees string[]? @description("Member states, institutions, or third parties the decision addresses")
  source_url string
  content_hash string?
  summary string?
}

class EURLexTreaty {
  celex_id string
  language EULanguage
  title string
  signature_date string?
  entry_into_force_date string?
  signatories string[]? @description("Member states / institutions that signed the treaty")
  source_url string
  content_hash string?
}

function ExtractEURLexRegulation(
  language: EULanguage,
  text: string
) -> EURLexRegulation {
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

function ExtractEURLexDirective(
  language: EULanguage,
  text: string
) -> EURLexDirective {
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

function ExtractEURLexDecision(
  language: EULanguage,
  text: string
) -> EURLexDecision {
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

function ExtractEURLexTreaty(
  language: EULanguage,
  text: string
) -> EURLexTreaty {
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
