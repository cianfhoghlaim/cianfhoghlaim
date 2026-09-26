// asset_generation.baml
// The bilingual Celtic asset generation contract (Plan 7 of the saga).
//
// Per the 2026-10-07-bilingual-celtic-asset-pipeline-v1 saga change
// (Plan 7 of openspec/plans/2026-10-01-convergence-saga-v1.md).
//
// Reuses the existing VernacularLanguage enum from
// baml_src/british_isles/_cross/vernacular_languages.baml.

class CelticAssetRecord {
  asset_id string              @description("Deterministic: sha256(language + prompt + subject + role)[:16]")
  subject string               @description("The NCCA subject (e.g. 'chemistry')")
  language string              @description("The Celtic language code (ga | cy | gd | gv | kw | br)")
  language_label string        @description("Human-readable label in the vernacular (e.g. 'Gaeilge', 'Cymraeg', 'Gàidhlig')")
  language_native_script string @description("The language name written in its native script")
  title string                 @description("Human-readable title in the vernacular language")
  title_en string              @description("English translation of the title")
  prompt string                @description("The asset-generation prompt (translated + culturally adapted for the target language)")
  prompt_en string             @description("The English source prompt")
  palette_hex string[]
  role string                  @description("The image_gen role (default | fast | bilingual | legacy | diagrams)")
  source_briefing_id string?   @description("The LearningEpisode.episode_id this asset was generated from (per Plan 6)")
  provenance_pdf string?       @description("The source PDF the prompt was extracted from (when available)")
  generated_at string           @description("ISO 8601 timestamp")
}

function GenerateIrishAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject (e.g. 'chemistry')"),
  role string @description("The image_gen role (default | fast | bilingual | legacy | diagrams)"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Irish
    (Gaeilge) and culturally adapt it (e.g. use Irish place names
    where appropriate, use Irish design motifs, preserve the Celtic
    art style). Generate the asset with bilingual EN + GA metadata.
  "
}

function GenerateWelshAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject (e.g. 'chemistry')"),
  role string @description("The image_gen role"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Welsh
    (Cymraeg) and culturally adapt it (use Welsh place names where
    appropriate, use Welsh design motifs). Generate the asset with
    bilingual EN + CY metadata.
  "
}

function GenerateScottishGaelicAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject"),
  role string @description("The image_gen role"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Scottish
    Gaelic (Gàidhlig) and culturally adapt it. Generate the asset with
    bilingual EN + GD metadata.
  "
}

function GenerateManxAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject"),
  role string @description("The image_gen role"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Manx
    (Gaelg) and culturally adapt it. Generate the asset with bilingual
    EN + GV metadata.
  "
}

function GenerateCornishAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject"),
  role string @description("The image_gen role"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Cornish
    (Kernewek) and culturally adapt it. Generate the asset with
    bilingual EN + KW metadata.
  "
}

function GenerateBretonAsset(
  prompt string @description("The English source prompt"),
  subject string @description("The NCCA subject"),
  role string @description("The image_gen role"),
) -> CelticAssetRecord {
  client "openai/gpt-4o-mini"
  prompt #"
    You are generating a FIBO 2D educational diagram asset for the
    Cianfhoghlaim British Isles MMO. Translate the prompt to Breton
    (Brezhoneg) and culturally adapt it. Generate the asset with
    bilingual EN + BR metadata.
  "
}
