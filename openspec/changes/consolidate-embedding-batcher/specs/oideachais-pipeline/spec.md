## MODIFIED Requirements

### Requirement: The canonical EmbeddingBatcher is in `oideachais.dlt_utils.batching`
The oideachais quadrant SHALL provide a single canonical `EmbeddingBatcher`
class. The class MUST live at `oideachais.dlt_utils.batching.EmbeddingBatcher`
and MUST be re-exported via `oideachais.dlt_utils.__init__.EmbeddingBatcher`.

The oideachais quadrant SHALL NOT contain a top-level `sruth/oideachais/embeddings/`
package. Any historical `sruth/oideachais/embeddings/batcher.py` /
`sruth/oideachais/embeddings/service.py` / `sruth/oideachais/embeddings/__init__.py`
files are forbidden and MUST NOT be re-introduced.

The `oideachais.dlt_utils.batching` module MUST export:
- `EmbeddingBatcher` (the canonical class)
- `batch_embeddings` (the iterator function)
- `batch_items` (the generic iterator)
- `should_drop_hnsw` (HNSW lifecycle helper)
- `calculate_optimal_batch_size` (HNSW drop threshold helper)
- `MINIMUM_BATCH_SIZE` (the 100-row constant)
- `HNSW_DROP_THRESHOLD` (the 50-row constant)

#### Scenario: New code needs an embedding batcher
- **WHEN** a contributor needs to embed a list of texts in a dlt
  source, Dagster asset, or BAML extraction
- **THEN** they MUST import from `oideachais.dlt_utils`:
  - `from oideachais.dlt_utils import EmbeddingBatcher, batch_embeddings`
- **AND** they MUST NOT import from `oideachais.embeddings` (which
  does not exist and is gitignored)

#### Scenario: A non-canonical EmbeddingBatcher appears
- **WHEN** a new `EmbeddingBatcher` class is added to any other
  location in the oideachais quadrant
- **THEN** the contributor MUST be redirected to import from
  `oideachais.dlt_utils` instead
- **AND** the new class SHOULD be removed in a follow-up commit
