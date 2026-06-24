---
name: oideachais-baml-schemas
description: The KCG oideachais BAML extraction schemas in `oideachais/baml_src/`. Covers the 9 BAML files (clients.baml, curriculum_extraction.baml, early_childhood.baml, isles_education.baml, leaving_cert_syllabus_extraction.baml, leaving_cert_past_paper_extraction.baml, leaving_cert_marking_scheme_extraction.baml, official_media.baml, ocr_validation.baml), the 4 gaois BAML files (duchas.baml, folklore_extraction.baml, logainm.baml, tearma.baml), the 6 archived BAML files in `_archive/`, the 3 extraction clients (ExtractEn, ExtractEnStrong, LocalVision), the LitellmClient routing, and the canonical add-a-new-BAML-function workflow. Use when adding a new BAML function, wiring an extraction to a dlt source, designing a new schema for a British Isles curriculum framework, or adding a new Aistear theme.
---

# Oideachais BAML Schemas

## Purpose

The `oideachais/baml_src/` directory houses **9 active + 4 gaois +
6 archived = 19 BAML files** that extract structured data from
the British Isles curriculum sources. This skill captures the
canonical schema patterns, the client registry, the 4 Aistear
themes, the 7-nation enums, and the add-a-new-BAML-function
workflow. The `baml/` skill is generic; this one is oideachais-
specific.

## When to use this skill

Use when you need to:

- "Add a new BAML function"
- "Wire an extraction to a dlt source"
- "Design a new schema for a British Isles curriculum framework"
- "Add a new Aistear theme"
- "Add a 10th extraction client"
- "Re-activate an archived BAML function"

## The 9 active BAML files

| File | Purpose | Functions |
|:--|:--|:--|
| `clients.baml` | The 3 extraction clients + the LitellmClient registry | `ExtractEn`, `ExtractEnStrong`, `LocalVision` |
| `curriculum_extraction.baml` | The 5-framework curriculum extraction (NCCA + CfE + CfW + CCEA + SQA) | `ExtractCurriculum`, `ExtractLearningOutcomes` |
| `early_childhood.baml` | The 4 Aistear themes (Well-being, Identity & Belonging, Communicating, Exploring & Thinking) | `ExtractAistearFramework`, `ExtractAistearTheme` |
| `isles_education.baml` | The 7 British Isles nations + 6 Celtic languages | `ExtractIslesEducation`, `ExtractIslesLanguagePair` |
| `leaving_cert_syllabus_extraction.baml` | The Leaving Cert syllabus extraction | `ExtractLeavingCertSyllabus` |
| `leaving_cert_past_paper_extraction.baml` | The Leaving Cert past-paper extraction (for the 12+ subjects) | `ExtractLeavingCertPastPaper` |
| `leaving_cert_marking_scheme_extraction.baml` | The Leaving Cert marking-scheme extraction | `ExtractLeavingCertMarkingScheme` |
| `official_media.baml` | The official-media extraction (government + educational sources) | `ExtractOfficialMedia` |
| `ocr_validation.baml` | The OCR validation extraction (5 Celtic metrics) | `ValidateOcr` |

The 9 active files are compiled to `oideachais/baml_client/` (the
canonical Python client home).

## The 4 gaois BAML files

| File | Purpose |
|:--|:--|
| `gaois/duchas.baml` | The Dúchas folklore extraction |
| `gaois/folklore_extraction.baml` | The generic folklore extraction |
| `gaois/logainm.baml` | The Logainm (Irish place names) extraction |
| `gaois/tearma.baml` | The Téarma (Irish terminology) extraction |

The 4 gaois files are also active but live in a sub-directory
because they're sourced from the gaois.ie project (the
Údarás na Gaeltachta terminology service).

## The 6 archived BAML files (`_archive/`)

The 6 files in `_archive/` were Q3-2026 archived per the
`archive-celtic-baml-orphans` openspec change. They define 29
functions total and have a re-activation procedure:

1. Move the file back to `oideachais/baml_src/` (the canonical home)
2. Update the `clients.baml` registry to include the new function
3. Add a Dagster asset at `oideachais/dagster_defs/assets/`
4. Update the BAML extraction wire-up in the dlt source

The 6 archived files are:
`_archive/cognates.baml`, `_archive/celtic_linguistics.baml`,
`_archive/morphology.baml`, `_archive/grammar_patterns.baml`,
`_archive/named_entities.baml`, `_archive/portfolio_extraction.baml`.

## The 3 extraction clients (the registry)

```baml
// oideachais/baml_src/clients.baml
client<llm> ExtractEn {
  provider "openai"
  api_key env.OPENAI_API_KEY
  model "gpt-4o"
  options { temperature 0.0 }
}

client<llm> ExtractEnStrong {
  provider "openai"
  api_key env.OPENAI_API_KEY
  model "gpt-4o-2024-08-06"
  options { temperature 0.0, max_tokens 8192 }
}

client<llm> LocalVision {
  provider "openai-generic"
  base_url "http://localhost:10240/v1"
  api_key env.MLX_OMNI_API_KEY
  model "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"
}
```

The 3 clients are referenced from each function via the
`client ExtractEn` annotation. The `LocalVision` client is the
fallback when the OPENAI_API_KEY is missing or the rate limit is
hit.

## The 4 Aistear themes (the early-childhood framework)

```baml
// oideachais/baml_src/early_childhood.baml
enum AistearTheme {
    WELL_BEING
    IDENTITY_AND_BELONGING
    COMMUNICATING
    EXPLORING_AND_THINKING
}

class AistearLearningGoal {
    theme AistearTheme
    age_range string  // "0-3", "3-6", or "0-6"
    goal_id string
    description string
    sample_activities string[]
}
```

The 4 themes are the Aistear framework's core pillars. The
`ExtractAistearTheme` function returns 1 `AistearLearningGoal`
per (theme, age_range) combination.

## The 7 British Isles nations (the canonical enum)

```baml
// oideachais/baml_src/isles_education.baml
enum BritishIslesNation {
    IE  // Ireland
    SCT // Scotland
    WLS // Wales
    NI  // Northern Ireland
    IOM // Isle of Man
    JEY // Jersey
    GGY // Guernsey
}

enum CelticLanguage {
    GA  // Gaeilge (Irish)
    GD  // Gàidhlig (Scottish Gaelic)
    CY  // Cymraeg (Welsh)
    BR  // Brezhoneg (Breton)
    GV  // Gaelg (Manx)
    KW  // Kernowek (Cornish)
}
```

The 7 nations are the canonical home for the cross-domain
asset keys (per `.agents/skills/cross-domain-registry/SKILL.md`).
The 6 Celtic languages are the 6 active in the
`meaisinfhoghlaim/language/` sub-package.

## Worked example: add a new BAML function

1. Choose the right BAML file (e.g. add a new Aistear theme to
   `early_childhood.baml`):

2. Define the new class + the new function:

   ```baml
   class AistearTheme_5_NEW_THEME {
       theme AistearTheme
       description string
   }

   function ExtractAistearTheme_5_NEW_THEME(text: string) -> AistearTheme_5_NEW_THEME[] {
       client ExtractEn
       prompt #"
       Extract the new Aistear theme from the following text.
       Text: {{ text }}
       "#
   }
   ```

3. Add the function to the `clients.baml` registry (if a new
   client is needed):

   ```baml
   client<llm> ExtractEnForNewTheme {
       provider "openai"
       model "gpt-4o-mini"
   }
   ```

4. Compile the BAML files: `uv run baml-cli generate`.

5. Add a Dagster asset at
   `oideachais/dagster_defs/assets/early_childhood_assets.py:ExtractAistearTheme_5_NEW_THEME_asset`.

6. Wire the asset to a dlt source (e.g. `oideachais/dlt_sources/domains/education/ie/aistear.py:ExtractAistearTheme_5_NEW_THEME`).

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `baml-cli generate` fails with a syntax error | A new function is missing the `client` annotation | Add `client ExtractEn` (or one of the 3) to the function |
| The extraction returns an empty list | The text is too short (< 100 chars) | Pass a longer text or chunk the input |
| The extraction returns the wrong language | The prompt is in English but the text is in Irish | Add a language-detection step before the extraction |
| The extraction times out | The model is too slow | Use `ExtractEnStrong` for long documents or `LocalVision` for offline |
| The extraction is rate-limited | The OPENAI_API_KEY is throttled | Fall back to `LocalVision` (the on-prem MLX server) |

## Cross-references

- `.agents/skills/baml/SKILL.md` — the generic BAML patterns
- `.agents/skills/celtic-language-ai/SKILL.md` — the 6 Celtic languages + 8 ISO codes
- `.agents/skills/cross-domain-registry/SKILL.md` — the `{nation}.{domain}.{entity}` contract
- `.agents/skills/oideachais-leabharlann/SKILL.md` — the leabharlann pipeline (the primary consumer of these BAML functions)
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` — the v1 CocoIndex Apps that consume the BAML output
- `oideachais/baml_src/clients.baml` — the canonical 3-client registry
- `oideachais/baml_client/` — the compiled Python client
- `oideachais/STATUS.md` §1 — the BAML × dlt × Dagster × CocoIndex matrix
- `openspec/specs/oideachais-baml-schemas/spec.md` — the canonical spec
