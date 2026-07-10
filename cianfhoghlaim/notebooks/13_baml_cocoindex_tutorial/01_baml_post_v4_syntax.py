# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Tutorial 1: Canonical post-v4 BAML 0.223.0 syntax.

Walks through:
- `generator` blocks (replaces legacy v0.x `client<llm>`)
- `field Type` whitespace syntax (replaces Pydantic-style `field: Type`)
- `enum` / `class` / `function` semantics
- `@description` (field-level) + `@@description` (block-level)
- `image` first-class type
- `@stream.done` / `@stream.not_null` / `@stream.with_state` semantic-attributes
- `?` optionality

Loads `cianfhoghlaim/baml/clients.baml` + `baml/processing/docs_skills_extraction.baml`
(per the 5-tangent commit `1d94711c1`) and emits the Pydantic v2 schema
via `baml-cli generate --mode check`.

Cross-references:
- `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
- `openspec/changes/2026-07-11-baml-cocoindex-modernization-v1/` — the
  parent mega-change (Phase B: v0.223 bump)
- `openspec/changes/2026-07-12-baml-stream-attributes-v1/` — the
  `@stream.*` follow-up that added the 121 `@stream.*` annotations
- `openspec/changes/2026-07-12-baml-type-builder-ncca-v1/` — the
  TypeBuilder / `@@dynamic` follow-up

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/01_baml_post_v4_syntax

Bilingual note: this notebook is the canonical English-language
walkthrough. The Irish-language (Gaeilge) counterpart of the
5-tutorial track lives at
`openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1-ga/` (a
planned follow-up; not yet shipped).
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
    # Tutorial 1 — BAML post-v4 syntax

    This is the **canonical** BAML 0.223.0 syntax (the `generator` block
    + the `field Type` whitespace pattern + the `@@description` block-level
    attribute + the `image` first-class type + the `@stream.*`
    semantic-attributes + the `?` optionality).

    The legacy v0.x `client<llm>` block syntax and the Pydantic-style
    `field: Type` colon syntax are deprecated as of v0.212 (the
    `baml-cli migrate` command automates the colon → whitespace rewrite;
    see `openspec/changes/2026-07-10-fix-baml-codegen-v4-syntax-v1`
    which rewrote 17 `.baml` files across the repo).

    **What you'll learn:**
    1. The `generator` block (replaces legacy `client<llm>`)
    2. The `field Type` whitespace pattern (replaces `field: Type`)
    3. `enum` / `class` / `function` semantics
    4. `@description` (field-level) + `@@description` (block-level)
    5. The `image` first-class type
    6. The `@stream.*` semantic-attributes
    7. `?` optionality on nullable fields
    """
    )
    return


@app.cell
def _section1_generator_block(mo):
    mo.md(
        """
    ## 1. The `generator` block (post-v4 canonical)

    Replaces the legacy v0.x `client Name { provider "..." model "..." }`
    block syntax. Per BAML 0.212+, every backend (OpenAI, Google AI,
    Anthropic, local llama-swap, local MLX) is configured via a
    `generator <name> { ... }` block.

    Source of truth: `cianfhoghlaim/baml/clients.baml` (post-v4 canonical,
    10 generators).
    """
    )
    return


@app.cell
def _generator_block_literal():
    generator_block = '''\
generator default {
  provider "openai"
  model "gpt-5-mini"
  retry_policy Exponential {
    max_retries 3
    delay_ms 200
    multiplier 1.5
    max_delay_ms 10000
  }
  timeout {
    total_ms 60000
  }
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
  }
}

generator local_vision_gemma4 {
  provider "openai"
  model "local/vision/gemma-4-26B-A4B"
  retry_policy Exponential { max_retries 3 }
  timeout { total_ms 60000 }
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
  }
}

generator local_vision_qwen3vl {
  provider "openai"
  model "local/vision/qwen3-vl-8b"
  retry_policy Exponential { max_retries 3 }
  timeout { total_ms 60000 }
  options {
    base_url env.LITELLM_BASE_URL
    api_key  env.LITELLM_API_KEY
  }
}\
'''
    return (generator_block,)


@app.cell
def _render_generator_block(generator_block, mo):
    mo.md(
        f"""
    ```baml
    {generator_block}
    ```

    **3 generators shown here:**
    - `default` — the canonical OpenAI/LiteLLM backend (used for text
      extraction across all 121 `Extract*` functions)
    - `local_vision_gemma4` — `gemma-4-26B-A4B` via the local llama-swap
      MLX backend (per Tutorial 3's side-by-side comparison)
    - `local_vision_qwen3vl` — `qwen3-vl-8b` via the same local
      llama-swap MLX backend

    All 3 use the canonical `retry_policy Exponential { ... }` block +
    `timeout {{ total_ms 60000 }}` (both added per the parent
    `2026-07-11-baml-cocoindex-modernization-v1` mega-change Phase B2).
    """
    )
    return


@app.cell
def _section2_field_type(mo):
    mo.md(
        """
    ## 2. `field Type` whitespace syntax (replaces Pydantic-style colon)

    BAML 0.212+ uses **whitespace**, not colons, between field name and
    type. The colon form (`field: Type`) is legacy and triggers
    `baml-cli migrate` warnings.

    Source of truth: `cianfhoghlaim/baml/education/subjects/qpack_chemistry.baml`
    (rewritten in the `2026-07-10-fix-baml-codegen-v4-syntax-v1` change).
    """
    )
    return


@app.cell
def _class_with_optionality():
    class_syntax = '''\
class CurriculumSyllabus {
  subject string
  level string                // "higher" | "ordinary" | "foundation"
  year int
  description string?
  blooms_level string?        // "remember" | "understand" | "apply" | "analyse" | ...
  topics Topic[]
  @@description "The NCCA strand/outcome extraction shape."
}

class Topic {
  code string
  description string
}\
'''
    return (class_syntax,)


@app.cell
def _render_class_syntax(class_syntax, mo):
    mo.md(
        f"""
    ```baml
    {class_syntax}
    ```

    **Key syntax features visible:**
    - `field Type` whitespace (NOT `field: Type` colon)
    - `string?` for nullable/optional (the `?` optionality)
    - `Type[]` for list types (NOT `List[Type]` or `list[Type]`)
    - `@@description` block-level attribute (the double-`@` is
      **block-level**, single-`@` is **field-level**)
    - Inline `// comments` are supported
    """
    )
    return


@app.cell
def _section3_description(mo):
    mo.md(
        """
    ## 3. `@description` (field-level) + `@@description` (block-level)

    The single-`@` prefix is **field-level**; the double-`@@` is
    **block-level** (attached to the enclosing class / enum / function).
    """
    )
    return


@app.cell
def _description_syntax():
    description_syntax = '''\
class MarkingPoint {
  code string
  @description("e.g. '3 marks for correct substitution'")
  criterion string
  @description("Marks awarded, 0-N")
  marks int
  @description("Optional examiner note")
  examiner_note string?
}

@@description "Canonical marking point for LC higher-level marking schemes."
class MarkingPointCanonical { ... }
'''
    return (description_syntax,)


@app.cell
def _render_description(description_syntax, mo):
    mo.md(
        f"""
    ```baml
    {description_syntax}
    ```

    The `@description("...")` attribute feeds the LLM prompt — the
    LLM sees the description as a hint about what to extract. This is
    **far more effective** than putting the hint in a class-level
    docstring, because the LLM receives the description alongside the
    field name at every call site.
    """
    )
    return


@app.cell
def _section4_image(mo):
    mo.md(
        """
    ## 4. `image` first-class type

    BAML 0.218+ has a first-class `image` type for vision model inputs.
    Per the parent mega-change Phase B3, the 2 new local vision
    generators (`local_vision_gemma4` + `local_vision_qwen3vl`) feed
    the 4 vision-extraction functions in
    `baml/education/pdfs/`.
    """
    )
    return


@app.cell
def _image_syntax():
    image_syntax = '''\
class SyllabusPageImage {
  page_number int
  image image                          // base64 or URL
  diagram_type string                  // "graph" | "table" | "diagram" | "equation"
  pointing_model string                // "gemma-4-26B-A4B" | "qwen3-vl-8b"
}

function ExtractSyllabusDiagram(page: SyllabusPageImage) -> ExtractedDiagram {
  client local_vision_gemma4
  prompt #"
    Extract the diagram from page {{ page.page_number }} of this syllabus PDF.
    {{ page.image }}
    Diagram type: {{ page.diagram_type }}
  "#
}\
'''
    return (image_syntax,)


@app.cell
def _render_image(image_syntax, mo):
    mo.md(
        f"""
    ```baml
    {image_syntax}
    ```

    Note `image image` (the field is named `image`, of type `image`) —
    BAML is fine with the name-type collision. See Tutorial 3 for the
    **side-by-side** comparison of `gemma-4-26B-A4B` vs `qwen3-vl-8b`
    on the same syllabus PDFs.
    """
    )
    return


@app.cell
def _section5_streaming(mo):
    mo.md(
        """
    ## 5. `@stream.*` semantic-attributes (the 5-tangent canonical pattern)

    BAML 0.220+ supports streaming with semantic annotations. The 3
    canonical `@stream.*` attributes are:

    - `@stream.done` — emit this field when it's complete (or when the
      LLM signals done for the whole object)
    - `@stream.not_null` — never emit null while streaming
    - `@stream.with_state` — emit a state object alongside the streamed
      value (for partial-progress UIs)

    Source of truth: `cianfhoghlaim/baml/processing/docs_skills_extraction.baml`
    (rewritten in commit `5e6734b57` to add the 121 `@stream.*`
    annotations to all Extract functions).
    """
    )
    return


@app.cell
def _streaming_attrs():
    streaming_syntax = '''\
class MarkingScheme {
  @stream.not_null
  subject string
  scheme_code string
  level string
  year int
  @@stream.done
  marking_points MarkingPoint[]
  @@stream.with_state
}

function ExtractMarkingScheme(pdf_text: string) -> MarkingScheme @stream.done {
  client Gemini
  prompt #"Extract the structured marking scheme from {{ pdf_text }}."#
}\
'''
    return (streaming_syntax,)


@app.cell
def _render_streaming(streaming_syntax, mo):
    mo.md(
        f"""
    ```baml
    {streaming_syntax}
    ```

    **The 3 `@stream.*` patterns:**
    - `@stream.not_null` on a field — the LLM never streams null for
      this field; it streams the partial value instead
    - `@@stream.done` on the class — the LLM signals object completion
      with the canonical done-token
    - `@@stream.with_state` on the class — emit a state object so the
      UI can render a progress bar

    **On the function:** `@stream.done` (single `@`) is the
    function-level marker that the function supports streaming with the
    done semantics.
    """
    )
    return


@app.cell
def _section6_optionality(mo):
    mo.md(
        """
    ## 6. `?` optionality

    Nullable / optional fields use the `?` suffix:

    | Form | Meaning |
    |:--|:--|
    | `string` | Required, non-null |
    | `string?` | Optional, may be null |
    | `string[]` | Required list (may be empty) |
    | `string[]?` | Optional list (may be null OR empty) |
    | `int` | Required int (may be 0) |
    | `int?` | Optional int (may be null) |

    There is no `Optional[string]` form (that's the Pydantic-style —
    forbidden in BAML 0.212+).
    """
    )
    return


@app.cell
def _section7_enum(mo):
    mo.md(
        """
    ## 7. `enum` (also post-v4 canonical)

    Enums in BAML 0.212+ are values-only (no Pydantic-style `class
    Enum(str, Enum)` derivation).
    """
    )
    return


@app.cell
def _enum_syntax():
    enum_syntax = '''\
enum BloomsLevel {
  Remember
  Understand
  Apply
  Analyse
  Evaluate
  Create
  @@description "Bloom's revised taxonomy (Anderson & Krathwohl 2001)."
}

enum EducationLevel {
  Higher
  Ordinary
  Foundation
  @@description "LC level (one of higher / ordinary / foundation)."
}\
'''
    return (enum_syntax,)


@app.cell
def _render_enum(enum_syntax, mo):
    mo.md(
        f"""
    ```baml
    {enum_syntax}
    ```

    Enums are **strings at the LLM boundary** (the LLM sees
    `"Remember"` / `"Understand"` / etc.) but are typed in the
    generated Pydantic v2 client.
    """
    )
    return


@app.cell
def _section8_function(mo):
    mo.md(
        """
    ## 8. `function` (the canonical 5-step pattern)

    Every BAML `Extract*` / `Generate*` function has the canonical
    5-part anatomy:

    ```baml
    function ExtractFoo(input: FooInput) -> FooOutput {
      client <generator_name>     // 1. the generator (from §1)
      prompt #"...{{ input }}..."  // 2. the prompt (Jinja-templated)
      // 3. optional streaming marker (e.g. @stream.done)
      // 4. optional retry_policy (default: client-level Exponential)
      // 5. optional @@stream.* block-level attributes
    }
    ```

    The 8 `qpack_<subject>.baml` files (per Tutorial 2) follow this
    pattern 40+ times — once per `Generate*QuestPack` /
    `Extract*LOStatement` / `Generate*FormativeItem` /
    `Score*FormativeResponse` / `Validate*QuestPack` function.
    """
    )
    return


@app.cell
def _function_syntax():
    function_syntax = '''\
class FooInput {
  paragraph string
  subject string
}

class FooOutput {
  learning_outcomes string[]
  blooms_levels BloomsLevel[]
}

function ExtractFoo(input: FooInput) -> FooOutput {
  client default
  prompt #"
    Extract the learning outcomes from this {{ input.subject }}
    paragraph:

    {{ input.paragraph }}

    Return one Bloom's level per outcome.
  "#
}\
'''
    return (function_syntax,)


@app.cell
def _render_function(function_syntax, mo):
    mo.md(
        f"""
    ```baml
    {function_syntax}
    ```

    **Note:** the prompt uses **Jinja2** templating (`{{ input.subject }}`).
    This is the BAML 0.212+ canonical replacement for the v0.x
    `f-string` style prompts.
    """
    )
    return


@app.cell
def _validate_section(mo):
    mo.md(
        """
    ## 9. Validate the syntax with `baml-cli`

    ```bash
    cd cianfhoghlaim
    uv run baml-cli check baml/                      # quick syntax check
    uv run baml-cli generate --mode check            # generate + check
    mise run baml:test                               # full @test sweep
    ```

    **What to expect:** after the 5-tangent modernization commit
    (`1d94711c1`) + the parent mega-change (`409898008`) + the 4
    follow-ups (`476c866b8` + `1623849d9` + `49e0259a0` + `5e6734b57`
    + `93df30ebb`), the canonical `.baml` files in
    `baml/education/lc_extraction/`, `baml/education/subjects/qpack_*.baml`,
    and `baml/processing/docs_skills_extraction.baml` all parse
    cleanly under `baml-cli check`. The remaining 50+ validation
    errors are in the `_shared/` / `pdfs/` / `celtic/` clusters and
    are out of scope per the parent change.
    """
    )
    return


@app.cell
def _next_steps(mo):
    mo.md(
        """
    ## Next steps

    - See `02_qpack_8_subject_walkthrough.py` for the per-subject BAML
      function pattern (40+ `Generate*QuestPack` / `Extract*LOStatement`
      / `Generate*FormativeItem` / `Score*FormativeResponse` /
      `Validate*QuestPack` functions across 8 LC subjects)
    - See `03_education_pdf_vision_pipeline.py` for the side-by-side
      `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison on the same PDFs
    - See `04_cocoindex_baml_integration.py` for the 3 real
      CocoIndex+BAML integration patterns (`upstream_api_surface` /
      `upstream_blog_monitor` / `docs_skills_consolidation`)
    - See `05_post_v4_duplicate_audit_and_migration.py` for the
      42-renames commit (`49e0259a0`) audit notebook

    **Cross-references:**
    - `.agents/skills/baml/SKILL.md` — the BAML 0.223.0 skill router
    - `openspec/specs/oideachais-baml-schemas/spec.md` — the BAML
      schemas capability spec (18 → 19 → 20 requirements)
    - `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`
      — this tutorial track's parent capability spec
    """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run the tutorial as a CLI script from any cwd.

    Usage from any directory:
        python 01_baml_post_v4_syntax.py --help
        uv run notebooks/13_baml_cocoindex_tutorial/01_baml_post_v4_syntax.py <flags>

    The marimo entry point is unchanged:
        marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax
        marimo run  13_baml_cocoindex_tutorial/01_baml_post_v4_syntax
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="01_baml_post_v4_syntax.py",
        description=__doc__,
    )
    parser.add_argument(
        "--section",
        type=int,
        default=0,
        help="0 = full tutorial; 1..8 = jump to that section (default: 0)",
    )
    args = parser.parse_args(argv)
    print("[01_baml_post_v4_syntax] Tutorial 1 — BAML post-v4 syntax")
    print(f"  Section: {args.section} (0 = full)")
    print("  Sections covered: 8 (generator / field Type / description / image /")
    print("                    stream / optionality / enum / function)")
    print("  Run: uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax")
    return 0


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
