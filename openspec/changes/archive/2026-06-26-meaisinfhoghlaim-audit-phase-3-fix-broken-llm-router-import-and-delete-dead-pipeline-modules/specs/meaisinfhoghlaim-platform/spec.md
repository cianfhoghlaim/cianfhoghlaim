## ADDED Requirements

### Requirement: No broken cross-package imports in meaisínfhoghlaim

The meaisínfhoghlaim quadrant MUST NOT contain a `.py` file
with an active (non-lazy `try/except ImportError`) import
that targets a non-existent module path. Every cross-package
import MUST be verifiable via
`PYTHONPATH=./sruth python3 -c "import <module>"` returning
exit code 0 BEFORE the importing file is committed.

The canonical homes for cross-quadrant utilities are:

| Utility | Canonical home |
|:--|:--|
| `CircuitBreaker`, `RateLimiter`, `retry` | `sruth/oideachais/core/utils/` (importable as `from oideachais.core.utils import ...`) |
| `get_logger` | `sruth/oideachais/observability/logging.py` |
| `settings` | `sruth/oideachais/settings.py` |
| DLT sources (Dúchas, Téarma, Gaois, etc.) | `sruth/oideachais/dlt_sources/ie/culture/` |

If a meaisínfhoghlaim module needs a utility that lives in
another quadrant, it MUST import from the canonical home
(e.g. `from sruth.oideachais.core.utils import CircuitBreaker`),
NOT a phantom meaisínfhoghlaim-local path
(e.g. `from ..core.utils import CircuitBreaker` when
`sruth/meaisinfhoghlaim/core/` does not exist).

#### Scenario: A meaisínfhoghlaim module imports from a phantom `meaisinfhoghlaim.core.*` path

- **GIVEN** `sruth/meaisinfhoghlaim/core/` does not exist
  (verified via `ls sruth/meaisinfhoghlaim/core/`)
- **AND** `sruth/meaisinfhoghlaim/pipelines/llm_router.py:23`
  contains an active import `from ..core.utils import CircuitBreaker`
- **WHEN** the module is loaded
- **THEN** Python raises `ModuleNotFoundError: No module named 'meaisinfhoghlaim.core'`
- **AND** the import MUST be rewired to the canonical home
  `from sruth.oideachais.core.utils import CircuitBreaker`

#### Scenario: A future contributor adds a new cross-quadrant import

- **GIVEN** a meaisínfhoghlaim `.py` file needs a utility from
  another quadrant
- **WHEN** the contributor adds the import
- **THEN** the contributor MUST first verify the target module
  exists via `ls <path-to-target>/<file>.py`
- **AND** the contributor MUST first verify the target imports
  cleanly via `PYTHONPATH=./sruth python3 -c "from <canonical.path> import <symbol>"`
- **AND** the import line MUST use the canonical
  `<quadrant>.<package>.<module>` form (e.g. `oideachais.core.utils`),
  NOT a phantom `<quadrant>.core.utils` form (unless
  `sruth/<quadrant>/core/utils/` actually exists)

### Requirement: No orphan resource modules in `pipelines/`

The meaisínfhoghlaim `pipelines/` subtree MUST NOT contain
`.py` files that define a top-level resource class or function
without any importer in `sruth/meaisinfhoghlaim/`. A resource
module is "orphan" if:

- It defines at least one top-level class (e.g.
  `BrowserbaseResource`) or top-level function that is not a
  private helper (prefixed with `_`), AND
- Zero importers exist for any of its top-level symbols
  anywhere in `sruth/meaisinfhoghlaim/`
  (verified via `grep -rn "from .* import .*<Symbol>" sruth/meaisinfhoghlaim/`)

The exception is `pipelines/__init__.py` itself, which is the
canonical re-export surface for the 3 main pipelines
(`dialect_classifier`, `irish_document_scanner`,
`transcript_aligner`).

#### Scenario: A pipeline resource class has zero importers

- **GIVEN** `sruth/meaisinfhoghlaim/pipelines/<name>.py` defines
  a class `BrowserbaseResource` or similar top-level resource
- **AND** `grep -rn "BrowserbaseResource" sruth/meaisinfhoghlaim/`
  returns only the definition (no importers)
- **WHEN** the file is audited
- **THEN** the file MUST be either deleted (if the resource is
  superseded by a LiteLLM or Dagster-native alternative) or
  wired into a real Dagster code-location (the canonical
  destination for `ConfigurableResource` classes)
- **AND** the resource singleton at module load time
  (e.g. `browserbase_resource = BrowserbaseResource()`) MUST
  NOT be eagerly instantiated if there are no importers
  (eager instantiation adds to import-time cost + Dagster
  startup latency)

#### Scenario: A future contributor adds a new pipeline module

- **GIVEN** a new `.py` file is added to
  `sruth/meaisinfhoghlaim/pipelines/`
- **WHEN** the file is committed
- **THEN** at least one of the following MUST be true:
  - The file is added to `pipelines/__init__.py` re-exports
    (becomes a public pipeline module), OR
  - The file is imported by a Dagster asset under
    `sruth/meaisinfhoghlaim/dagster_defs/`, OR
  - The file is imported by a test under
    `sruth/meaisinfhoghlaim/tests/`
- **AND** if none of the above hold for 30 days, the file
  MUST be either deleted or wired into a real consumer
