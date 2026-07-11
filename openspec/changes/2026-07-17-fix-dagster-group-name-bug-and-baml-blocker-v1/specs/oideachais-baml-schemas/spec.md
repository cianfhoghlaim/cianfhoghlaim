## MODIFIED Requirements

### Requirement: Multimodal (vision) extraction

The system SHALL support BAML multimodal (vision) extraction across
all 3 BAML functions in
`cianfhoghlaim/baml/processing/_shared/video_kg.baml`. Every vision
function SHALL route through the canonical `client<llm>` aliases
declared in `clients_llama_swap.baml` (not via the v0.212
quoted-string model identifier syntax). The 5-value tagged-union
type (`KnowledgeTripleKind`) SHALL be declared as `enum Name { ... }`
(NOT `class Name { ... }`); the body MUST be one ALL-CAPS identifier
per line with NO commas and NO field-type annotations. All
array-typed fields MUST use the `type[]` suffix syntax (e.g.
`diagram_points string[]`); the Python-like `list<type>` syntax is
FORBIDDEN in field-type positions in class declarations.

(As of the 2026-07-16 pre-pick-4 audit, the untracked file
`cianfhoghlaim/baml/processing/_shared/video_kg.baml` used `class
KnowledgeTripleKind { Concept Definition Example Formula
VisualSequence }` and the 3 v0.212 client references
`client "litellm/qwen3-vl-8b"` / `client "litellm/qwen3.6-27b-mtp"`,
which blocked `baml-cli check + baml-cli generate` from exiting 0 in
5+ recent changes. The user's authorization exception per the 3rd
audit B2 allows this single change to migrate `class → enum`,
`client "<model>" → client <NamedAlias>`, and `list<string> → string[]`.)

The 3 vision functions in `video_kg.baml`:

| Function | Canonical client alias | Backbone |
|:--|:--|:--|
| `ExtractVideoKnowledgeTriple` | `client LlamaSwapClient` | `qwen3-vl-8b` (llama-swap) |
| `ExtractConceptChain` | `client LlamaSwapReasoningClient` | `qwen3.6-27b-mtp` (llama-swap) |
| `ExtractFrameSequence` | `client LlamaSwapClient` | `qwen3-vl-8b` (llama-swap) |

The 4 typed classes (`KnowledgeTriple`, `ConceptChain`, `VisualScene`,
`VisualSequence`) and the 1 enum (`KnowledgeTripleKind`) MUST remain
in the generated `baml_client/types.py` after `baml-cli generate`.

#### Scenario: `baml-cli check` reports zero errors for `video_kg.baml`

- **WHEN** `cd cianfhoghlaim && baml-cli check 2>&1 | grep video_kg` runs
- **THEN** the output is empty (0 references to `video_kg.baml` in any error context)
- **AND** `grep -nE "^(class|enum) KnowledgeTripleKind" cianfhoghlaim/baml/processing/_shared/video_kg.baml` reports `enum KnowledgeTripleKind {`
- **AND** `grep -nE "^  client " cianfhoghlaim/baml/processing/_shared/video_kg.baml` reports the 3 canonical named-client references (no quoted strings, no `list<type>`)

#### Scenario: `baml-cli generate` produces the expected client types

- **WHEN** `cd cianfhoghlaim && baml-cli generate` runs (after the `video_kg.baml` schema is valid)
- **THEN** for the `video_kg.baml` file specifically: the generated `baml_client/types.py` SHALL contain the Python `KnowledgeTripleKind(enum.Enum)` class with the 5 expected values (`Concept`, `Definition`, `Example`, `Formula`, `VisualSequence`)
- **AND** `KnowledgeTriple.triple_kind: KnowledgeTripleKind` is preserved as a strongly-typed enum reference (NOT a free-form `string`)
- **AND** the `baml_client.async_client` exposes the 3 vision functions: `ExtractVideoKnowledgeTriple`, `ExtractConceptChain`, `ExtractFrameSequence`
- **AND** `baml_client/types.py` also contains the 4 classes (`KnowledgeTriple`, `ConceptChain`, `VisualScene`, `VisualSequence`) and the canonical `VisualScene.diagram_points: list[str]` field

#### Scenario: `list<type>` is rejected in field-type positions

- **GIVEN** the canonical syntax for arrays is `type[]` (suffix) and the body MUST be one ALL-CAPS identifier per line with NO commas
- **WHEN** a developer introduces `list<string>` or `ClassField<A, B>` syntax in a `class` field declaration
- **THEN** `baml-cli check` reports `Error validating: This line is not a valid field or attribute definition`
- **AND** the 3 canonical patterns for arrays are: `string[]`, `int[]`, `KnowledgeTriple[]`

#### Scenario: `class` is rejected for tagged-union types

- **GIVEN** the canonical syntax for tagged unions is `enum Name { ... }` with bare-value identifiers
- **WHEN** a developer uses `class TripleKind { Concept Definition Example Formula VisualSequence }` (no field types, just identifiers)
- **THEN** `baml-cli check` reports cascading errors: `No type specified for field Concept / Definition / Example / Formula / VisualSequence` × 5 = at least 5 errors
- **AND** the fix is to rename `class` → `enum`
