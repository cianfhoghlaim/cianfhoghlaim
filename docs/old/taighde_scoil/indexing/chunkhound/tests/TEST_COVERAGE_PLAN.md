# Code Research Test Coverage Plan

## Mission

Create comprehensive test coverage for the deep code research feature following ChunkHound's testing philosophy:
- **Real components over mocks** - Exercise actual functionality
- **Zero external APIs** - All tests run deterministically in CI/CD
- **Fast feedback loops** - Tests complete in seconds, not minutes

## Progress Summary

### ✅ Completed (Phase 1 & 2a)

1. **Test Infrastructure**
   - Created `tests/unit/research/` directory
   - Created `tests/integration/research/` directory
   - Created `tests/fixtures/research/` directory
   - Enhanced `FakeLLMProvider` with `complete_structured` method

2. **Unit Tests - Query Expander** (13 tests, all passing)
   - Query building for root and child nodes
   - Context propagation with ancestor chains
   - Position bias optimization
   - LLM-based query expansion
   - Error handling and graceful degradation
   - Edge cases (empty ancestors, whitespace, special chars)

3. **Unit Tests - Question Generator** (20 tests, all passing)
   - Token budget scaling with depth (MIN to MAX)
   - File contents validation
   - Exploration gist tracking
   - Empty question filtering
   - Result limiting to MAX_FOLLOWUP_QUESTIONS
   - Question synthesis with merge parent creation
   - Quality pre-filtering (length, yes/no questions)
   - Relevance filtering by LLM indices
   - Node counter management
   - Error handling and graceful fallbacks

### ⏳ Remaining Work

#### Phase 2: Additional Unit Tests

**test_question_generator.py** (~15 tests)
- Gist tracking (exploration history)
- Token budget scaling with depth
- Follow-up synthesis logic (individual vs merged)
- Quality filtering (yes/no question removal)
- Multi-level question generation
- Synthetic merge parent node creation

**test_synthesis_engine.py** (~20 tests)
- Strategy selection (single-pass vs map-reduce)
- Citation tracking and validation
- Citation remapping in map-reduce
- File reranking by relevance
- Token budget management
- Cluster formation logic
- Source footer generation
- Single-pass synthesis with small result sets
- Map-reduce synthesis with large result sets

#### Phase 3: Integration Tests

**test_unified_search_integration.py** (~12 tests)
- Parallel query expansion execution
- Symbol extraction from semantic results
- Hybrid semantic + regex result merging
- Chunk deduplication by ID
- Real database queries with fake embeddings
- Error handling in search pipeline

**test_multi_hop_discovery.py** (~15 tests)
- All 5 termination conditions
  - Time limit enforcement
  - Result limit enforcement
  - Candidate quality threshold
  - Score degradation detection
  - Minimum relevance threshold
- Score tracking across rounds
- Candidate expansion mechanics
- Semantic drift prevention through reranking
- Real database with deterministic embeddings

**test_bfs_traversal.py** (~10 tests)
- Breadth-first exploration
- Level-by-level processing
- Context propagation through tree
- Result aggregation across levels
- Depth calculation based on repo size
- Maximum depth enforcement

#### Phase 4: End-to-End Tests

**test_code_research_e2e.py** (~8 tests)

Small codebase scenario:
- Index minimal Python files
- Execute simple research query
- Verify single-pass synthesis
- Validate citations match actual chunks

Large codebase scenario:
- Index substantial file set (50+ files)
- Execute complex architectural query
- Verify map-reduce synthesis activation
- Validate citation remapping correctness

Follow-up question generation:
- Query triggering follow-ups
- Verify no duplicate exploration
- Validate gist tracking
- Check question quality filtering

**test_code_research_error_handling.py** (~10 tests)
- LLM expansion failures
- Empty semantic search results
- Synthesis failures with graceful degradation
- Invalid citations handling
- Maximum depth exhaustion
- Database connection errors
- Timeout handling
- Partial result recovery

## Testing Architecture

### Fixture Hierarchy

```
Real Components (No Mocks)
├── DuckDBProvider (in-memory)
├── Real parsers
├── Real file systems (tmp_path)
└── Core services

Fake Providers (Deterministic)
├── FakeLLMProvider
│   ├── Pattern-based response matching
│   ├── complete() for text responses
│   └── complete_structured() for JSON responses
└── FakeEmbeddingProvider
    ├── Hash-based deterministic vectors
    ├── embed() for vector generation
    └── rerank() for deterministic scoring
```

### Test Data Strategy

**Unit Tests**: Minimal synthetic data
- Small context objects
- Simple queries
- Focused test cases

**Integration Tests**: Representative real data
- Small Python files (10-20 files)
- Real directory structures
- Actual ChunkHound source code samples

**End-to-End Tests**: Realistic scenarios
- Indexed codebase subset
- Complex multi-hop queries
- Full pipeline execution

## Key Patterns Established

### 1. LLM Manager Fixture

```python
@pytest.fixture
def llm_manager(fake_llm_provider, monkeypatch):
    """Monkeypatch provider creation for testing."""
    def mock_create_provider(self, config):
        return fake_llm_provider

    monkeypatch.setattr(LLMManager, "_create_provider", mock_create_provider)

    utility_config = {"provider": "fake", "model": "fake-gpt"}
    synthesis_config = {"provider": "fake", "model": "fake-gpt"}
    return LLMManager(utility_config, synthesis_config)
```

### 2. Pattern-Based Response Matching

```python
fake_llm_provider = FakeLLMProvider(
    responses={
        "query": '{"queries": ["var1", "var2"]}',
        "synthesis": '{"answer": "...", "citations": [...]}',
    }
)
```

### 3. Real Database Integration

```python
@pytest.fixture
def real_db(tmp_path):
    """Real in-memory database for integration tests."""
    db = DuckDBProvider(":memory:", base_directory=tmp_path)
    db.connect()
    return db
```

### 4. Deterministic Embeddings

```python
fake_embedding = FakeEmbeddingProvider(dimensions=1536)
# Same text always produces same vector
# Enables reproducible semantic search tests
```

## Test Metrics

### Coverage Goals

- **Unit Tests**: 90%+ coverage of core logic
- **Integration Tests**: 80%+ coverage of workflows
- **End-to-End Tests**: Critical path coverage

### Performance Targets

- Unit tests: <1s per test
- Integration tests: <5s per test
- End-to-end tests: <30s per test
- Full suite: <5 minutes

## Running Tests

```bash
# Run all research tests
uv run pytest tests/ -k "research" -v

# Run unit tests only
uv run pytest tests/unit/research/ -v

# Run integration tests only
uv run pytest tests/integration/research/ -v

# Run end-to-end tests only
uv run pytest tests/test_code_research_e2e.py -v

# Run with coverage
uv run pytest tests/ -k "research" --cov=chunkhound.services.research --cov-report=html
```

## CI/CD Integration

All tests must:
- ✅ Run without external API keys
- ✅ Complete in reasonable time (<10 minutes total)
- ✅ Be deterministic (no flaky tests)
- ✅ Work on all platforms (Windows, macOS, Linux)
- ✅ Use temp directories (no file system pollution)

## Documentation References

- **Testing Philosophy**: `/chunkhound/CONTRIBUTING.md`
- **Fake Providers**: `/tests/fixtures/README.md`
- **Query Expander Tests**: `/tests/unit/research/test_query_expander.py`
- **Research Patterns**: `/tests/unit/research/README.md`

## Estimated Effort

- **Phase 1 (Completed)**: ~2-3 hours ✅
- **Phase 2 (Unit Tests)**: ~4-6 hours
- **Phase 3 (Integration Tests)**: ~6-8 hours
- **Phase 4 (End-to-End Tests)**: ~4-6 hours

**Total**: ~16-23 hours for complete implementation

## Next Actions

1. Review completed query expander tests
2. Implement question generator tests (Phase 2)
3. Implement synthesis engine tests (Phase 2)
4. Move to integration tests (Phase 3)
5. Complete with end-to-end tests (Phase 4)

## Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All end-to-end tests pass
- [ ] No external API dependencies
- [ ] Tests complete in <10 minutes
- [ ] Coverage >85% for research modules
- [ ] All tests run in CI/CD
- [ ] Documentation complete
