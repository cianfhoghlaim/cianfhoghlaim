# Spec Delta: meaisinfhoghlaim-agent-frameworks

This change modifies the `meaisinfhoghlaim-agent-frameworks` capability
(`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`) by
adding 4 new requirements and modifying 0 existing requirements.
The full modified spec lives at
`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`.

## ADDED Requirements

### Requirement: 8 NCCA subject agent definitions wired to Layer 5

The system SHALL mount each of the 8 NCCA subject agents
(`gael_agent`, `math_agent`, `appm_agent`, `chem_agent`,
`comp_agent`, `engl_agent`, `geog_agent`, `hist_agent`) at
`cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
under the 5-layer KCG Components pattern. Each mount consumes
the `CelticAgentOpsComponent` and emits 5 Dagster assets per agent:
`agent_health_<slug>_agent`, `agent_routing_<slug>_agent`,
`agent_memory_<slug>_agent`, `agent_event_<slug>_agent`,
`agent_trace_<slug>_agent`.

The `ROUTING_KEYWORDS` map at
`cianfhoghlaim/agents/routing_keywords.py` SHALL expose a seed
bucket for each of the 8 subjects with at least the NCCA canonical
name (`gaeilge`, `mathematics`, `applied_mathematics`,
`chemistry`, `computer_science`, `english`, `geography`,
`history`); the full bucket is appended by
`CelticAgentOpsComponent._append_routing_keywords()` at scaffold
time.

#### Scenario: math_agent mounts on L5 + routes by keyword

- **GIVEN** `defs/5_agent_ops/adk/math_agent/defs.yaml`
- **WHEN** `dg list defs | grep math_agent` runs
- **THEN** the 5 math_agent assets are visible in the
  output
- **AND** `ROUTING_KEYWORDS["math_agent"]` contains
  `"mathematics"`

### Requirement: OCR adapter wiring to the standard eval harness

The system SHALL wire the 4 `OCRAdapter` concrete implementations
at `cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py`
(`PaddleOCRAdapter`, `DoclingAdapter`, `DotsOCRAdapter`,
`UnstractAdapter`) to `meaisinfhoghlaim/evaluation/compare.py`
via the `_run_classical_eval()` helper. The
`_CLASSICAL_ADAPTER_FOR_STACK` mapping MUST resolve every
`ClassicalOCRStack.stack_name` to one of the 4 adapters.

`compare_ocr_models()` SHALL remain the canonical entry point
for end-to-end multi-model OCR comparisons.

#### Scenario: docling stack is wired through DoclingAdapter

- **GIVEN** a `ClassicalOCRStack(stack_name="docling", ...)`
- **WHEN** `_run_classical_eval(stack, corpus, document)` runs
- **THEN** `OCRAdapterRegistry.get("docling")` returns a
  `DoclingAdapter`
- **AND** `adapter.process_pdf(document)` is invoked
- **AND** the resulting `EvalSample` reports the adapter name
  in `model_id`

#### Scenario: adapter error produces well-formed EvalSample

- **WHEN** the adapter raises (Docker stack unreachable)
- **THEN** `EvalSample` is still emitted with
  `notes="adapter-error: <message>"`
- **AND** `cer=1.0`, `wer=1.0`, `fada_consistent=False`

### Requirement: Federated OCR Dagster asset materialises

The federated OCR subsystem SHALL be moved from
`meaisinfhoghlaim/process/irish_ocr_federated.py` (an orphaned
618-LOC file post-v4) to `meaisinfhoghlaim/federated/`, and
materialised as a Dagster asset `irish_ocr_federated_smoke` on a
30-minute cron cycle via the `CelticFederatedOcrComponent`. The
asset SHALL be a graceful smoke run (not a long-running server
thread) and SHALL surface any exception in the
`metadata.error` field rather than crashing the Dagster run.

#### Scenario: Asset materialises every 30 minutes

- **WHEN** the cron `*/30 * * * *` triggers
- **THEN** Dagster materialises `irish_ocr_federated_smoke`
- **AND** `metadata.status` is either `"ok"` or `"error"`
- **AND** `metadata.result` is JSON-encoded with the
  `run_federated_training(...)` return value or the exception
  message

### Requirement: MemoryBackend Protocol contract

Every memory backend (Graphiti, FalkorDB, InMemoryLanceDB) SHALL
implement the `MemoryBackend` protocol at
`cianfhoghlaim/storage/memf.py`. The protocol surface SHALL be
exactly:

- `async def add_episode(episode: Episode) -> str`
- `async def search(query: str, *, k: int = 10, **filters) -> list[SearchResult]`
- `async def get_node(node_id: str) -> Node | None`
- `async def close() -> None`
- `kind: ClassVar[str]`

Agent code SHALL depend on the protocol, not on any concrete
class. `get_default_backend()` SHALL be the canonical factory.

#### Scenario: get_default_backend() returns InMemoryLanceDBBackend when both backends are down

- **GIVEN** Graphiti is unreachable (TCP probe fails)
- **AND** FalkorDB is unreachable (TCP probe fails)
- **WHEN** `await get_default_backend()` is called
- **THEN** the result is an `InMemoryLanceDBBackend`
- **AND** `backend.kind == "in_memory_lancedb"`
- **AND** `isinstance(backend, MemoryBackend)` is True

#### Scenario: get_default_backend() probes fall through to FalkorDB on Graphiti 5xx

- **GIVEN** Graphiti is marked `DOWN_5XX`
- **AND** FalkorDB is reachable
- **WHEN** `await get_default_backend()` is called
- **THEN** the result is a `FalkorDBBackend`
- **AND** subsequent calls within the 30s cache TTL return the
  same instance

## Cross-references

- [`cianfhoghlaim/orchestration/defs/5_agent_ops/`](../../../cianfhoghlaim/orchestration/defs/5_agent_ops/) (the L5 mounts)
- [`cianfhoghlaim/agents/routing_keywords.py`](../../../cianfhoghlaim/agents/routing_keywords.py) (the seed bucket)
- [`cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py`](../../../cianfhoghlaim/meaisinfhoghlaim/backends/adapters.py) (the 4 OCRAdapter concretes)
- [`cianfhoghlaim/meaisinfhoghlaim/evaluation/compare.py`](../../../cianfhoghlaim/meaisinfhoghlaim/evaluation/compare.py) (the eval harness)
- [`cianfhoghlaim/orchestration/components/layer3_model_lifecycle.py`](../../../cianfhoghlaim/orchestration/components/layer3_model_lifecycle.py) (the `CelticFederatedOcrComponent`)
- [`cianfhoghlaim/storage/memf.py`](../../../cianfhoghlaim/storage/memf.py) (the `MemoryBackend` Protocol + factory)
- [`openspec/specs/storage-memory-facade/spec.md`](../storage-memory-facade/spec.md) (the new capability)
