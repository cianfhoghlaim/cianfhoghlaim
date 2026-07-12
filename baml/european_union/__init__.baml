// EU institutional BAML cluster — re-exports.

function ExtractEUDocument(
  language: EULanguage,
  text: string
) -> EUDocument {
  client Claude
  prompt #"
    Extract a structured multilingual EU document from the following
    raw text. The document is published in {{ language }} by one of
    the EU institutions.

    Return a single EUDocument with the canonical multilingual
    document shape. Preserve the original text in the row's language;
    do NOT translate.

    Document text:
    {{ text }}

    {{ ctx.output_format }}
  "#
}
