## ADDED Requirements

### Requirement: `notebooks/24_lakehouse_memory_doctor.py` surfaces 5-backend health

The system SHALL provide a marimo notebook at
`notebooks/24_lakehouse_memory_doctor.py` that surfaces per-backend
health (cognee, graphiti, lancedb, falkordb, memgraph) + a federated
search demo. The notebook SHALL be wired into the
`notebooks/00_control_panel.py` Tab 5 (Registry) so the operator can
navigate to it with one click. The notebook SHALL be WASM-portable
(per the `wasm-compatibility` skill — no `@app.setup` blocks with
Docker network side-effects).

#### Scenario: Operator opens the marimo memory doctor

- **WHEN** the operator runs `marimo edit notebooks/24_lakehouse_memory_doctor.py`
- **THEN** the notebook SHALL display a 5-column grid: cognee / graphiti / lancedb / falkordb / memgraph
- **AND** each column SHALL show: container status (Up/Down), endpoint ping latency in ms, last cognify/episode timestamp, vector-index row count
- **AND** a "federated search" expander SHALL demo a single query routed across all 5 backends using the `MemoryBackend` Protocol from `agents/memory_layer.py`

#### Scenario: Tab 5 of 00_control_panel.py surfaces the memory doctor

- **WHEN** the operator opens `notebooks/00_control_panel.py` Tab 5 (Registry)
- **THEN** the tab SHALL display a clickable card labelled "Memory Doctor"
- **AND** clicking the card SHALL navigate the operator to `notebooks/24_lakehouse_memory_doctor.py`
- **AND** the tab SHALL display the latest `stedding/memory-health/<date>.json` summary (timestamp + healthy count)

#### Scenario: Notebook is WASM-portable

- **WHEN** `mise run lint:wasm` runs against the new notebook
- **THEN** the validator SHALL report zero WASM-incompatibility errors
- **AND** the notebook SHALL NOT use Docker network side-effects in `@app.setup` blocks