# BAML Domain Templates

> **The 18 domain-specific BAML prompt templates for the 4-stage plane.**

Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3: BAML
bulk-quality). These templates replace the 114 stub prompts found
by the `lint:baml-stub-prompts` lint.

## How it works

Each template is a high-quality BAML prompt body that:

1. Declares the role context (e.g. "You are an expert Irish Leaving
   Certificate syllabus extractor")
2. Lists the return-type fields to extract (read from the class
   definition's `@description` decorators)
3. Has subject/board/language branching where applicable
4. Uses BAML best features (`_.role("user")`, `ctx.output_format`,
   `{% if subject %}`)
5. References canonical sources (Leaving Cert directory, leabharlann,
   Firecrawl output where relevant)

The templates are **referenced** by stub functions in the
co-located BAML files via a `baml_bulk_replace_stubs.py` script
(see `scripts/baml_bulk_replace_stubs.py`).

## The 18 templates

| Template | Domain | Stub count |
|:--|:--|:--|
| `processing_gemini_report.baml` | `processing/gemini_deep_research/` | ~10 |
| `processing_author_archive.baml` | `processing/author_archive.baml` | ~10 |
| `processing_style_transfer.baml` | `processing/style_transfer.baml` | 7 |
| `processing_game_content.baml` | `processing/game_content.baml` | ~6 |
| `processing_circular_extraction.baml` | `processing/circular_extraction.baml` | ~6 |
| `processing_cv_extraction.baml` | `processing/cv_extraction.baml` | ~5 |
| `celtic_tearma.baml` | `celtic/gaois/tearma.baml` | 26 |
| `celtic_grammar_patterns.baml` | `celtic/grammar_patterns.baml` | 7 |
| `celtic_curriculum.baml` | `celtic/curriculum/celtic_curriculum.baml` | 7 |
| `ireland_lc_stage.baml` | `british_isles/.../stages/upper_secondary.baml` | ~8 |
| `ireland_jc_stage.baml` | `british_isles/.../stages/junior_cycle.baml` | ~8 |
| `ireland_university_module.baml` | `british_isles/.../university/` | 21 |
| `ireland_web_content.baml` | `british_isles/.../web/` | 18 |
| `isles_marking_scheme.baml` | `british_isles/.../marking/` | 6 |
| `isles_statistics.baml` | `british_isles/.../statistics/` | 5 |
| `isles_grading.baml` | `british_isles/.../grading/` | 12 |
| `european_nations_curriculum.baml` | `european_nations/.../curriculum/` | 13 |
| `american_nations_law.baml` | `american_nations/.../law/` | 7 |

**Total: ~180 stub functions covered** (covers all 114 unique
stub functions, with 60+ extra coverage for the catch-block sweep).

## Template structure

Each template follows this pattern:

```baml
// Domain header (comment block)
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change.

template DomainExtractor(input: <input>) -> <return_type> {
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting [domain] from [source type].

    {% if subject %}
    - For subject `{{ subject }}`, follow the [subject-specific guidance]
    {% endif %}

    From the [input type] below, extract:
    - field_1: [description from @description decorator]
    - field_2: [description from @description decorator]
    - ...

    {{ ctx.output_format }}

    [INPUT TYPE]:
    {{ input }}
  "#
}
```

## Usage

The templates are **not directly invoked** — they are referenced by
the `baml_bulk_replace_stubs.py` script which replaces the
`Auto-generated extraction prompt.` stub with the template body
appropriate for the function.

## DO NOT

- **Never** edit a co-located function's prompt by hand — use the
  template + the script.
- **Never** add a new template without also updating
  `scripts/baml_bulk_replace_stubs.py:TEMPLATE_MAP`.
- **Never** change the template structure without updating all
  18 templates in lockstep.
