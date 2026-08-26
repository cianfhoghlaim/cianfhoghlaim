// tuatha_media_intel.baml
//
// The British Isles Formative Assessment MMO — capture → VLM → ANAM pipeline.
// Description-only extraction (per the tuatha skill: shippable=false invariant).
//
// Three BAML classes:
//   • HadesBoon          — 10 Olympians × ~6-15 boons × 28 Duo Boons
//   • ComicParticleFrame — Absolute Superman red-dust-of-Krypton → ANAM turquoise/blue
//   • GbaMagicSystem     — Golden Sun Djinn/Psynergy → ANAM element binding

class HadesBoon {
  boon_id            string         @description("Deterministic id, e.g. 'hades:athena:divine_strike'")
  god                GodName
  tier               BoonTier
  slot               BoonSlot
  effect_text        string         @description("Canonical English effect description, copied from the UI text exactly")
  color_hex          string         @description("Dominant particle/icon color as #RRGGBB")
  particle_motion    string         @description("e.g. 'arc burst', 'chain lightning', 'radial frost', 'vine bloom', 'music waves'")
  ui_position        BoundingBox    @description("4-corner normalized coords of the boon icon within the source frame")
  run_id             string
  frame_index        int
  captured_at        string         @description("ISO-8601 UTC timestamp")
}

class ComicParticleFrame {
  issue_id              string      @description("e.g. 'absolute-superman-2024-001'")
  page_number           int
  panel_id              string      @description("Panel coordinate, e.g. 'p4-tr' for top-right of page 4")
  particle_form         ComicParticleForm
  color_hex             string
  motion_description    string      @description("e.g. 'slow drifting cloud, no discrete particles'")
  character_attribution string      @description("e.g. 'superman-cape', 'background-krypton', 'laser-beam'")
  source_page_url       string?     @description("Optional traceability only — never the panel pixels")
  run_id                string
  frame_index           int
  captured_at           string
}

class GbaMagicSystem {
  game                GbaGame
  room_id             string      @description("Internal GBA map/room id from the save state")
  djinn_name          string?
  psynergy_name       string
  element             GbaElement
  effect_text         string
  color_hex           string
  sprite_description  string      @description("e.g. '8-direction projectile, orange trail, 16 frames'")
  run_id              string
  frame_index         int
  captured_at         string
}

// ANAM particle — the cross-source join result.
// Maps any source artifact to the ANAM turquoise/blue particle primitive
// + the Tuatha Dé deity it belongs to.

class AnamParticle {
  anam_id           string         @description("Deterministic: '<source>:<source_id>:<deity>'")
  source            AnamSource     // enum: hades | comic | gba | manual
  source_id         string         // the source row's primary key
  celtic_deity      CelticDeity    // the Tuatha Dé counterpart
  anam_color_hex    string         // derived turquoise/blue palette
  anam_motion       string         // one of the canonical ANAM motion primitives
  description_en    string         // multilingual synthesis (English + Gaeilge OK)
  description_ga    string?
  bias_mode         BiasMode       // enum: description_heavy | color_heavy | balanced
  run_id            string
  generated_at      string
}

enum GodName {
  Zeus
  Poseidon
  Athena
  Ares
  Artemis
  Aphrodite
  Dionysus
  Demeter
  Hermes
  Chaos
}

enum BoonTier {
  Common
  Rare
  Epic
  Heroic
  Legendary
  Duo
}

enum BoonSlot {
  Attack
  Special
  Cast
  Dash
  Call
  Aid
  Keepsake
  Other
}

enum ComicParticleForm {
  Dust
  Spark
  Vapor
  Ray
  Aura
  Plume
  Other
}

enum GbaGame {
  GoldenSun
  GoldenSunTheLostAge
}

enum GbaElement {
  Venus
  Mars
  Jupiter
  Mercury
  Neutral
}

enum AnamSource {
  Hades
  Comic
  Gba
  Manual
}

enum CelticDeity {
  Lugh           // skill / craft / sun — counter to Ares / Athena
  Brigid         // poetry / healing / smithcraft — counter to Aphrodite / Demeter
  Manannan       // sea / travel — counter to Poseidon
  TheMorrigan    // battle / prophecy — counter to Ares / Athena
  Aengus         // youth / love — counter to Artemis / Dionysus
  Danu           // earth / mother — counter to Demeter
  Taranis        // sky / thunder — counter to Zeus
  Ogma           // writing / eloquence — counter to Hermes
  TheDagda       // abundance / contracts — counter to Dionysus
  Cernunnos      // wild / nature — counter to Artemis / Dionysus
  Other
}

enum BiasMode {
  DescriptionHeavy
  ColorHeavy
  Balanced
}

class BoundingBox {
  x_min           float  @description("Normalized 0-1, top-left origin")
  y_min           float
  x_max           float
  y_max           float
}

// The 4 client<llm> declarations — routed via MODEL_REGISTRY, never hardcoded.

client<llm> HadesBoonClient {
  provider      "openai-generic"
  base_url      env.LLAMASWAP_URL
  api_key       env.LLAMASWAP_API_KEY
  model_name    env.VISION_MODEL_HADES    // resolves to MODEL_REGISTRY ocr_vision:tier2_medium
  max_tokens    1024
  temperature   0.0
}

client<llm> ComicParticleClient {
  provider      "openai-generic"
  base_url      env.LLAMASWAP_URL
  api_key       env.LLAMASWAP_API_KEY
  model_name    env.VISION_MODEL_COMIC    // resolves to MODEL_REGISTRY ocr_vision:tier2_medium
  max_tokens    1024
  temperature   0.0
}

client<llm> GbaMagicClient {
  provider      "openai-generic"
  base_url      env.LLAMASWAP_URL
  api_key       env.LLAMASWAP_API_KEY
  model_name    env.VISION_MODEL_GBA      // resolves to MODEL_REGISTRY ocr_vision:tier3_light
  max_tokens    512
  temperature   0.0
}

client<llm> AnamMapClient {
  provider      "openai-generic"
  base_url      env.LITELLM_URL
  api_key       env.LITELLM_API_KEY
  model_name    env.TEXT_MODEL_DEFAULT    // resolves to MODEL_REGISTRY text_llm:default
  max_tokens    2048
  temperature   0.2
}

// The 7 BAML functions the pipeline calls.

function ExtractHadesBoon(image: image) -> HadesBoon {
  client HadesBoonClient
  prompt #"
    You are a precise visual game analyst. Extract the Hades boon visible
    in the source frame.

    Look at the boon icon (around the center of the frame) and its particle
    effects. Return:
      - god (from the GodName enum)
      - tier (Common / Rare / Epic / Heroic / Legendary / Duo)
      - slot (Attack / Special / Cast / Dash / Call / Aid / Keepsake)
      - effect_text (canonical English effect, exactly as shown in the UI)
      - color_hex (dominant particle color in #RRGGBB)
      - particle_motion (e.g. 'arc burst', 'chain lightning', 'radial frost')
      - ui_position (4-corner bounding box of the boon icon, normalized 0-1)
      - boon_id (deterministic: 'hades:<lowercase-god>:<kebab-effect-name>')

    Cite visual evidence only; never invent effects not visible in the frame.
  "#
}

function ExtractComicParticle(image: image, issue_context: string) -> ComicParticleFrame {
  client ComicParticleClient
  client_resource_fallback
  prompt #"
    You are a comic-book panel visual analyst working on DC's Absolute
    Superman (Jason Aaron, 2024). {{ issue_context }}

    Describe the visible particle phenomenon in the source page image.
    Return:
      - issue_id (from context)
      - page_number, panel_id (use compass labels: tl/tr/bl/br/c)
      - particle_form (Dust / Spark / Vapor / Ray / Aura / Plume / Other)
      - color_hex (dominant particle color)
      - motion_description (drift, burst, flow, ambient)
      - character_attribution (who/what emits it)

    Description-only output. NEVER describe the artwork; describe the
    particle phenomenon only.
  "#
}

function ExtractGbaMagic(frame: image) -> GbaMagicSystem {
  client GbaMagicClient
  prompt #"
    You are a Golden Sun / Golden Sun: The Lost Age visual analyst.
    Identify the Djinn and Psynergy visible in the source frame.

    Return:
      - game (GoldenSun / GoldenSunTheLostAge)
      - room_id (best-effort guess based on visual context)
      - djinn_name (visible Djinn, or null)
      - psynergy_name (the spell name, if visible)
      - element (Venus / Mars / Jupiter / Mercury / Neutral)
      - color_hex (particle/element color in #RRGGBB)
      - sprite_description (e.g. '8-direction projectile, orange trail')

    Cite visual evidence only; never invent Djinn names not visible.
  "#
}

function MapToAnamParticle(
  source: AnamSource,
  source_payload: string, // JSON-encoded source row
  bias_mode: BiasMode
) -> AnamParticle {
  client AnamMapClient
  prompt #"
    You are the Tuatha Dé ANAM particle mapper. Take the source artifact
    and map it to the canonical ANAM turquoise/blue particle palette.

    {{ source_payload }}  (source: {{ source }}, bias: {{ bias_mode }})

    Return:
      - anam_id (deterministic: '<source>:<source_id>:<lowercase-celtic-deity>')
      - source, source_id
      - celtic_deity (best Tuatha Dé counterpart from CelticDeity enum)
      - anam_color_hex (within the ANAM turquoise/blue family, #RRGGBB)
      - anam_motion (canonical ANAM motion primitive)
      - description_en (English description)
      - description_ga (Irish translation, or null if not feasible)
      - bias_mode (passthrough)
  "#
}

function ExtractCrossLinguisticAnamDescription(
  anam_en: string,
  target_lang: string
) -> string {
  client AnamMapClient
  prompt #"
    Translate this ANAM particle description into {{ target_lang }}.
    Preserve the mythological / physical specificity.

    {{ anam_en }}

    Return ONLY the translated text, no commentary.
  "#
}

// Test cases (run via `baml-cli test` per the BAML skill).

test hades_athena_divine_strike {
  functions [ExtractHadesBoon]
  input {
    image "hades_athena_divine_strike.png"
  }
  output {
    boon_id "hades:athena:divine_strike"
    god GodName::Athena
    tier BoonTier::Common
    slot BoonSlot::Attack
    color_hex "#A8D8E8"
    particle_motion "arc burst"
  }
}

test comic_absolute_superman_dust {
  functions [ExtractComicParticle]
  input {
    image "absolute_superman_001_p1.png"
    issue_context "Absolute Superman #1, cover dust reveal"
  }
  output {
    issue_id "absolute-superman-2024-001"
    page_number 1
    particle_form ComicParticleForm::Dust
    color_hex "#C84747"
    character_attribution "superman-cape"
  }
}

test gba_golden_sun_jupiter {
  functions [ExtractGbaMagic]
  input {
    image "golden_sun_jupiter_jolt.png"
  }
  output {
    game GbaGame::GoldenSun
    element GbaElement::Jupiter
    color_hex "#FFD700"
    sprite_description "vertical lightning bolt, 16 frames"
  }
}
