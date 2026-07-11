# MODIFIED Requirements — restore the canonical `cianfhoghlaim/ocr/` package

> **Why this delta:** The BIEP notebooks documented under the
> `oideachais-marimo-dashboards` capability depend on
> `cianfhoghlaim.ocr.models.registry.VISION_MODELS` and
> `CLASSICAL_OCR` (via the dlt / cocoindex / orchestration
> sub-trees). When the canonical package is missing, every PDF
> ingestion pipeline and the
> `test_ocr_vlm_registry.py` conformance test fail with
> `ModuleNotFoundError: No module named 'cianfhoghlaim.ocr'`.

## ADDED Requirements

### Requirement: Canonical `cianfhoghlaim/ocr/` Python package

The system SHALL provide the canonical v4 OCR/VLM model
registry Python package at `cianfhoghlaim/ocr/` with the
following layout, per the v4 platform spec
(`openspec/specs/meaisinfhoghlaim-platform/spec.md` line 685)
and commit `0fceb8654`:

```text
cianfhoghlaim/ocr/
├── __init__.py           # re-exports the canonical symbols
└── models/
    ├── __init__.py       # re-exports + back-compat OCR_MODELS / VLM_MODELS aliases
    └── registry.py       # the 929-line canonical implementation
```

The canonical implementation SHALL export at minimum
`VISION_MODELS` (22 vision models) and `CLASSICAL_OCR`
(6 OCR backends) when
`from cianfhoghlaim.ocr.models.registry import VISION_MODELS, CLASSICAL_OCR`
is executed.

#### Scenario: Canonical import resolves

- **GIVEN** the `cianfhoghlaim/ocr/__init__.py`,
  `cianfhoghlaim/ocr/models/__init__.py`, and
  `cianfhoghlaim/ocr/models/registry.py` files exist on disk
  with content matching `HEAD` (commit `0fceb8654`)
- **WHEN** a Python process executes
  `from cianfhoghlaim.ocr.models.registry import VISION_MODELS, CLASSICAL_OCR`
- **THEN** the import SHALL succeed without
  `ModuleNotFoundError`
- **AND** `len(VISION_MODELS) >= 20` (the v4 spec requires
  ≥ 20 vision models; the current HEAD ships 22)
- **AND** `len(CLASSICAL_OCR) >= 4` (the v4 spec requires
  ≥ 4 classical OCR backends; the current HEAD ships 6)

#### Scenario: All 19 downstream consumers AST-parse

- **GIVEN** the 19 Python files under `cianfhoghlaim/` that
  reference `cianfhoghlaim.ocr.*`
  (cocoindex/, observability/, orchestration/, tests/_meaisinfhoghlaim/,
  and the meaisinfhoghlaim/ sub-package)
- **WHEN** each file is AST-parsed (`python -c "import ast;
  ast.parse(open('<file>').read())"`)
- **THEN** every file SHALL parse without syntax errors
- **AND** the 8 files with hard imports of
  `cianfhoghlaim.ocr.models.registry` SHALL execute their
  `import` statements without `ModuleNotFoundError`

#### Scenario: Back-compat shims re-export the canonical symbols

- **GIVEN** the parallel-agent back-compat shims at
  `cianfhoghlaim/meaisinfhoghlaim/ocr/__init__.py` and
  `cianfhoghlaim/meaisinfhoghlaim/models/{__init__,registry}.py`
  (each emitting a `DeprecationWarning`)
- **WHEN** a Python process executes
  `from cianfhoghlaim.meaisinfhoghlaim.models import VISION_MODELS`
- **THEN** the import SHALL emit the expected
  `DeprecationWarning` about the v4 canonical home
- **AND** the import SHALL return the same `VISION_MODELS` dict
  as `from cianfhoghlaim.ocr.models.registry import VISION_MODELS`
  (identity-equality, not just equality of contents)

#### Scenario: Test conformance — `test_ocr_vlm_registry.py`

- **GIVEN** the test file
  `cianfhoghlaim/tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py`
- **WHEN** `pytest cianfhoghlaim/tests/_meaisinfhoghlaim/test_ocr_vlm_registry.py`
  is run
- **THEN** the `import` statements SHALL resolve
- **AND** the conformance assertions on `VISION_MODELS` (model
  count, required backends, Unsloth-first fallback chain) SHALL
  pass without `ModuleNotFoundError`