# Code Research Unit Tests

## Overview

This directory contains unit tests for the deep code research feature components.
These tests follow ChunkHound's testing philosophy: **real components with minimal mocks**.

## Test Structure

### Completed Tests

- ✅ **test_query_expander.py** - Query building and LLM-based expansion (13 tests, all passing)
- ✅ **test_question_generator.py** - Follow-up question generation, synthesis, and filtering (20 tests, all passing)

### Pending Tests

- ⏳ **test_synthesis_engine.py** - Single-pass and map-reduce synthesis strategies

## Testing Patterns

### Fixture Pattern for LLM Tests

```python
@pytest.fixture
def fake_llm_provider():
    """Create fake LLM provider with pattern-based responses."""
    return FakeLLMProvider(
        responses={
            "pattern_in_prompt": '{"expected": "json response"}',
            # Multiple patterns can match different test scenarios
        }
    )

@pytest.fixture
def llm_manager(fake_llm_provider, monkeypatch):
    """Create LLM manager with fake provider."""
    def mock_create_provider(self, config):
        return fake_llm_provider

    monkeypatch.setattr(LLMManager, "_create_provider", mock_create_provider)

    utility_config = {"provider": "fake", "model": "fake-gpt"}
    synthesis_config = {"provider": "fake", "model": "fake-gpt"}
    return LLMManager(utility_config, synthesis_config)
```

### Real vs Mock Strategy

**Use Real Components:**
- ✅ ResearchContext data structures
- ✅ Query building logic
- ✅ Data transformations
- ✅ Business logic

**Use Fake Providers:**
- 🔄 LLM API calls (FakeLLMProvider with pattern matching)
- 🔄 Embedding generation (FakeEmbeddingProvider with deterministic vectors)

**Never Mock:**
- ❌ Core business logic
- ❌ Data structures
- ❌ Pure functions

## Test Categories

### Query Building Tests
- Root node query handling
- Child node context propagation
- Position bias optimization
- Ancestor chain handling

### LLM Expansion Tests
- Successful expansion with multiple queries
- Context-aware expansion
- Graceful failure handling
- Empty result handling
- Original query preservation

### Edge Cases
- Empty ancestors
- Whitespace handling
- Special characters
- Single vs multiple ancestors

## Running Tests

```bash
# Run all research unit tests
uv run pytest tests/unit/research/ -v

# Run specific test file
uv run pytest tests/unit/research/test_query_expander.py -v

# Run specific test
uv run pytest tests/unit/research/test_query_expander.py::TestBuildSearchQuery::test_root_node -v

# Run with coverage
uv run pytest tests/unit/research/ --cov=chunkhound.services.research
```

## Key Learnings

### 1. Monkeypatching LLMManager
The LLMManager uses a factory pattern to create providers. Instead of trying to pass fake providers directly, monkeypatch the `_create_provider` method to return your fake provider.

### 2. Pattern-Based Responses
FakeLLMProvider matches patterns in prompts to return appropriate responses. Use broad patterns like "query", "search", "authentication" that will match the actual prompts.

### 3. Complete Structured Output
FakeLLMProvider needs a `complete_structured` method that returns parsed JSON dictionaries, not just strings.

### 4. Test Independence
Each test should be independent and not rely on shared state. Use fixtures to create fresh instances for each test.

## Next Steps

1. **Implement test_question_generator.py**
   - Gist tracking tests
   - Token budget scaling tests
   - Follow-up synthesis tests
   - Quality filtering tests

2. **Implement test_synthesis_engine.py**
   - Strategy selection tests
   - Citation tracking tests
   - Token budget management tests
   - Map-reduce synthesis tests

3. **Create integration tests**
   - test_unified_search_integration.py
   - test_multi_hop_discovery.py
   - test_bfs_traversal.py

4. **Create end-to-end tests**
   - test_code_research_e2e.py
   - test_code_research_error_handling.py

## Patterns Reference

See `test_query_expander.py` for complete examples of:
- Fixture setup
- Monkeypatching strategies
- Assertion patterns
- Error handling tests
- Edge case coverage
