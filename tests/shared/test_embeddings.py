"""
Tests for sruth.shared.embeddings module.

Tests:
- EmbeddingBatcher batching behavior
- EmbeddingService multi-provider support
- Performance constants
"""

from unittest.mock import MagicMock

import pytest


class TestEmbeddingBatcher:
    """Tests for EmbeddingBatcher."""

    def test_batch_size_constants(self):
        """Test batch size constants are correct."""
        from sruth.shared.embeddings import DEFAULT_BATCH_SIZE, MIN_BATCH_SIZE

        assert MIN_BATCH_SIZE == 100
        assert DEFAULT_BATCH_SIZE == 256

    def test_embed_returns_correct_count(self):
        """Test embed returns correct number of embeddings."""
        from sruth.shared.embeddings import EmbeddingBatcher

        mock_embed = MagicMock(return_value=[[0.1, 0.2], [0.3, 0.4]])
        batcher = EmbeddingBatcher(embed_fn=mock_embed, batch_size=2)

        texts = ["hello", "world"]
        result = batcher.embed(texts)

        assert len(result) == 2
        mock_embed.assert_called_once_with(texts)

    def test_embed_batches_large_inputs(self):
        """Test embed batches large inputs."""
        from sruth.shared.embeddings import EmbeddingBatcher

        call_count = 0
        def mock_embed(texts):
            nonlocal call_count
            call_count += 1
            return [[0.1] * 10 for _ in texts]

        batcher = EmbeddingBatcher(embed_fn=mock_embed, batch_size=3)

        texts = ["a", "b", "c", "d", "e", "f", "g"]
        result = batcher.embed(texts)

        assert len(result) == 7
        assert call_count == 3  # ceil(7/3) = 3 batches

    def test_embed_empty_list(self):
        """Test embed handles empty list."""
        from sruth.shared.embeddings import EmbeddingBatcher

        mock_embed = MagicMock()
        batcher = EmbeddingBatcher(embed_fn=mock_embed)

        result = batcher.embed([])

        assert result == []
        mock_embed.assert_not_called()

    def test_total_embedded_tracks_count(self):
        """Test total_embedded property tracks count."""
        from sruth.shared.embeddings import EmbeddingBatcher

        mock_embed = MagicMock(side_effect=lambda x: [[0.1] for _ in x])
        batcher = EmbeddingBatcher(embed_fn=mock_embed, batch_size=10, min_batch_size=1)

        batcher.embed(["a", "b", "c"])
        assert batcher.total_embedded == 3

        batcher.embed(["d", "e"])
        assert batcher.total_embedded == 5

    def test_batch_embed_convenience_function(self):
        """Test batch_embed convenience function."""
        from sruth.shared.embeddings import batch_embed

        mock_embed = MagicMock(return_value=[[0.1], [0.2]])
        result = batch_embed(["a", "b"], embed_fn=mock_embed)

        assert len(result) == 2


class TestEmbeddingService:
    """Tests for EmbeddingService."""

    def test_embedding_models_registry(self):
        """Test EMBEDDING_MODELS registry has expected models."""
        from sruth.shared.embeddings import EMBEDDING_MODELS

        # Check some expected models exist
        assert "BAAI/bge-m3" in EMBEDDING_MODELS
        assert "text-embedding-3-small" in EMBEDDING_MODELS

        # Check model has required fields
        bge = EMBEDDING_MODELS["BAAI/bge-m3"]
        assert bge.dimensions == 1024
        assert bge.name == "BAAI/bge-m3"

    def test_embedding_provider_enum(self):
        """Test EmbeddingProvider enum values."""
        from sruth.shared.embeddings import EmbeddingProvider

        assert EmbeddingProvider.OPENAI == "openai"
        assert EmbeddingProvider.COHERE == "cohere"
        assert EmbeddingProvider.SENTENCE_TRANSFORMERS == "sentence_transformers"
        assert EmbeddingProvider.OLLAMA == "ollama"

    def test_embedding_service_dimensions(self):
        """Test EmbeddingService reports correct dimensions."""
        from sruth.shared.embeddings import EmbeddingService

        # Mock backend
        class MockBackend:
            @property
            def dimensions(self):
                return 768
            def embed(self, texts):
                return [[0.1] * 768 for _ in texts]

        service = EmbeddingService(
            model="test",
            custom_backend=MockBackend(),
        )

        assert service.dimensions == 768

    def test_embed_one_method(self):
        """Test embed_one returns single vector."""
        from sruth.shared.embeddings import EmbeddingService

        class MockBackend:
            @property
            def dimensions(self):
                return 3
            def embed(self, texts):
                return [[0.1, 0.2, 0.3] for _ in texts]

        service = EmbeddingService(model="test", custom_backend=MockBackend())
        vector = service.embed_one("hello")

        assert len(vector) == 3
        assert vector == [0.1, 0.2, 0.3]

    def test_get_embedding_service_factory(self):
        """Test get_embedding_service factory function."""
        from sruth.shared.embeddings import EmbeddingService, get_embedding_service

        service = get_embedding_service(model="BAAI/bge-m3")
        assert isinstance(service, EmbeddingService)


class TestEmbeddingModel:
    """Tests for EmbeddingModel dataclass."""

    def test_embedding_model_defaults(self):
        """Test EmbeddingModel default values."""
        from sruth.shared.embeddings import EmbeddingModel, EmbeddingProvider

        model = EmbeddingModel(
            name="test",
            provider=EmbeddingProvider.CUSTOM,
            dimensions=512,
        )

        assert model.max_tokens == 8192
        assert model.batch_size == 256
        assert model.api_key_env is None

    def test_embedding_model_custom_values(self):
        """Test EmbeddingModel with custom values."""
        from sruth.shared.embeddings import EmbeddingModel, EmbeddingProvider

        model = EmbeddingModel(
            name="custom-model",
            provider=EmbeddingProvider.OPENAI,
            dimensions=1536,
            max_tokens=4096,
            batch_size=100,
            api_key_env="MY_API_KEY",
        )

        assert model.name == "custom-model"
        assert model.dimensions == 1536
        assert model.max_tokens == 4096
        assert model.batch_size == 100
        assert model.api_key_env == "MY_API_KEY"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
