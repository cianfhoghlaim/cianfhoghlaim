// BAML schema: Cianfhoghlaim Design Tokens (agent-visible mirror)
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/:
//   - R21 (Machine-readable infrastructure) — BAML classes mirror tokens.css / tokens.ts / tokens.schema.json
//   - R22 (Design-tokens-as-code pipelines) — companion to tokens.css
//
// Agents that emit A2UI surfaces MUST reference DesignToken colors / sizes
// (NOT raw hex / px strings). The MCP design system server enforces this
// at catalog_render() time (R23).
//
// Update procedure:
//   1. Edit baml/portal/study_plan.baml or apps/web/src/styles/tokens.css
//   2. Run `mise run baml:generate`
//   3. Run `bun run tokens:validate` to confirm drift-free

// ============================================================================
// Colour tokens
// ============================================================================

class NationColor {
  group "nations"
  irish    string @description("Emerald-600 — primary #059669")
  scottish string @description("Blue-600 #2563eb")
  welsh    string @description("Red-600 #dc2626")
  breton   string @description("Purple-600 #9333ea")
}

class SubjectColor {
  group "subjects"
  mathematics         string @description("Blue-600 #2563eb")
  applied_mathematics string @description("Violet-600 #7c3aed")
  chemistry           string @description("Green-600 #16a34a")
  geography           string @description("Yellow-600 #ca8a04")
  history             string @description("Red-700 #b91c1c")
  english             string @description("Orange-600 #ea580c")
  gaeilge             string @description("Emerald-600 #059669")
  computer_science    string @description("Slate-600 #475569")
}

class CompetencyColor {
  group "competencies"
  communicating       string @description("Emerald #059669")
  information         string @description("Blue #2563eb")
  creative_thinking   string @description("Gold #ca8a04")
  personal_effective  string @description("Warm brown #92400e")
  working_with_others string @description("Red #b91c1c")
}

class SubnationColor {
  group "subnations"
  eire             string @description("Emerald — Ireland #059669")
  northern_ireland string @description("Blue — NI #2563eb")
  scotland         string @description("Sky — Scotland #0ea5e9")
  england          string @description("Red — St George's Cross #dc2626")
  wales            string @description("Red-700 — Y Ddraig Goch #b91c1c")
  isle_of_man      string @description("Slate — Triskelion #475569")
}

class BrandColor {
  group "brand"
  primary   string @description("Emerald-600 #059669")
  secondary string @description("Blue-600 #2563eb")
}

class StateColor {
  group "states"
  success string @description("Emerald-500 #10b981")
  warning string @description("Amber-500 #f59e0b")
  error   string @description("Rose-500 #f43f5e")
  info    string @description("Sky-500 #0ea5e9")
}

// ============================================================================
// Spacing scale (4px base)
// ============================================================================

class SpacingScale {
  group "spacing"
  s1 string @description("4px")
  s2 string @description("8px")
  s3 string @description("12px")
  s4 string @description("16px")
  s5 string @description("24px")
  s6 string @description("32px")
  s7 string @description("48px")
  s8 string @description("64px")
}

class RadiusScale {
  group "radius"
  sm   string @description("4px")
  md   string @description("8px")
  lg   string @description("12px")
  xl   string @description("16px")
  full string @description("9999px")
}

// ============================================================================
// Typography
// ============================================================================

class TypographyTokens {
  group "typography"
  display string @description("Cinzel, serif — display headings")
  body    string @description("Inter, sans-serif — body text")
  mono    string @description("JetBrains Mono, monospace — code")
}

// ============================================================================
// Aggregate
// ============================================================================

class DesignTokens {
  nations      NationColor
  subjects     SubjectColor
  competencies CompetencyColor
  subnations   SubnationColor
  brand        BrandColor
  states       StateColor
  spacing      SpacingScale
  radius       RadiusScale
  typography   TypographyTokens
}

// ============================================================================
// Function: agent-visible token accessor
// ============================================================================

function GetDesignTokens() -> DesignTokens {
  client "ExtractEn"
  prompt [
    "Return the Cianfhoghlaim design token set (mirror of tokens.css)."
  ]
}
