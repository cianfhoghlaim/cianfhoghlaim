# Qwen3 Batch Size Tuning Guide

This guide explains how to optimize ChunkHound performance for Qwen3 embedding and reranking models via Ollama or other OpenAI-compatible endpoints.

## Quick Start

### Automatic Configuration (Recommended)

ChunkHound automatically detects Qwen3 models and applies optimal batch sizes:

```json
{
  "embedding": {
    "provider": "openai",
    "base_url": "http://localhost:11434/v1",
    "model": "dengcao/Qwen3-Embedding-8B:Q5_K_M",
    "api_key": "not-required"
  }
}
```

**No manual tuning needed** - ChunkHound will automatically apply:
- Embedding batch size: 128 documents
- Reranking batch size: 64 documents (if using Qwen3 reranker)

### Calibration Tool (For Custom Tuning)

Find optimal batch sizes for your specific hardware:

```bash
# Basic calibration
chunkhound calibrate --embedding-provider openai --embedding-model dengcao/Qwen3-Embedding-8B:Q5_K_M

# Custom batch size ranges
chunkhound calibrate \
  --embedding-provider openai \
  --embedding-model dengcao/Qwen3-Embedding-8B:Q5_K_M \
  --embedding-batch-sizes 64 128 256 512 \
  --reranking-batch-sizes 32 64 96 128

# Save results to JSON
chunkhound calibrate \
  --embedding-provider openai \
  --embedding-model dengcao/Qwen3-Embedding-4B:Q5_K_M \
  --output-format json \
  --output-file calibration-results.json
```

## Supported Models

ChunkHound includes optimized configurations for:

### Embedding Models

| Model | Default Batch Size | Max Throughput | Use Case |
|-------|-------------------|----------------|----------|
| `dengcao/Qwen3-Embedding-0.6B:Q5_K_M` | 512 | High | Fast indexing, large corpora |
| `dengcao/Qwen3-Embedding-4B:Q5_K_M` | 256 | Medium | Balanced performance |
| `dengcao/Qwen3-Embedding-8B:Q5_K_M` | 128 | Lower | Maximum accuracy |

### Reranking Models

| Model | Default Batch Size | Max Documents | Use Case |
|-------|-------------------|---------------|----------|
| `qwen3-reranker-0.6b` | 128 | High | Fast reranking |
| `qwen3-reranker-4b` | 96 | Medium | Balanced reranking |
| `qwen3-reranker-8b` | 64 | Lower | Highest accuracy |

## Configuration Examples

### Example 1: Ollama with Qwen3-Embedding-8B

```json
{
  "embedding": {
    "provider": "openai",
    "base_url": "http://localhost:11434/v1",
    "model": "dengcao/Qwen3-Embedding-8B:Q5_K_M",
    "api_key": "not-required"
  }
}
```

**Auto-configured batch sizes:**
- Embedding: 128 documents per batch
- Token limit: 100,000 tokens per batch

### Example 2: Qwen3 Embedding + Reranking

```json
{
  "embedding": {
    "provider": "openai",
    "base_url": "http://localhost:11434/v1",
    "model": "dengcao/Qwen3-Embedding-4B:Q5_K_M",
    "rerank_model": "qwen3-reranker-4b",
    "rerank_url": "/rerank",
    "api_key": "not-required"
  }
}
```

**Auto-configured batch sizes:**
- Embedding: 256 documents per batch
- Reranking: 96 documents per batch (prevents OOM)

### Example 3: High-Throughput Indexing

For maximum indexing speed with Qwen3-0.6B:

```json
{
  "embedding": {
    "provider": "openai",
    "base_url": "http://localhost:11434/v1",
    "model": "dengcao/Qwen3-Embedding-0.6B:Q5_K_M",
    "batch_size": 512,
    "api_key": "not-required"
  },
  "indexing": {
    "max_concurrent_batches": 16
  }
}
```

**Performance expectations:**
- Throughput: 2-5x faster than default (100 batch size)
- Batching speedup: Up to 100x vs sequential (1 doc/request)
- Memory: ~2GB VRAM for model + batches

### Example 4: Remote API (Fireworks, etc.)

```json
{
  "embedding": {
    "provider": "openai",
    "base_url": "https://api.fireworks.ai/inference/v1",
    "model": "fireworks/qwen3-embedding-8b",
    "rerank_model": "fireworks/qwen3-reranker-8b",
    "api_key": "YOUR_API_KEY"
  }
}
```

**Auto-configured batch sizes:**
- Reranking: 64 documents per batch (optimized for 8B model)

## Performance Tuning

### Understanding Batch Sizes

**Embedding Batch Size**: Number of documents embedded in a single API call
- **Larger batches** = Higher throughput, better GPU utilization
- **Smaller batches** = Lower latency, less memory usage
- **Sweet spot**: Model-dependent (auto-configured by ChunkHound)

**Reranking Batch Size**: Maximum documents reranked in one request
- **Too large** = OOM errors, timeouts
- **Too small** = Suboptimal throughput
- **ChunkHound handles**: Automatic batch splitting for large result sets

### Calibration Results Interpretation

Example calibration output:

```
Embedding Batch Size Results:
----------------------------------------------------------
  Batch size   64:   850.2 docs/sec | Latency:  37.5ms (p50),  45.0ms (p95)
  Batch size  128:  1203.8 docs/sec | Latency:  53.2ms (p50),  63.9ms (p95) ⭐ RECOMMENDED
  Batch size  256:  1245.1 docs/sec | Latency: 102.8ms (p50), 123.4ms (p95)
  Batch size  512:  1251.3 docs/sec | Latency: 204.6ms (p50), 245.5ms (p95)

✓ Recommended embedding batch size: 128
```

**Interpretation:**
- Batch 128: "Knee" of the curve (15% throughput improvement over 64)
- Batch 256+: Diminishing returns (<4% improvement, 2x latency)
- **Use 128**: Best throughput-to-latency ratio

### Hardware-Specific Tuning

#### Consumer GPUs (8-16GB VRAM)

- **Qwen3-0.6B**: Use batch size 256-512
- **Qwen3-4B**: Use batch size 128-256
- **Qwen3-8B**: Use batch size 64-128

#### Data Center GPUs (40GB+ VRAM)

- **Qwen3-0.6B**: Use batch size 512+
- **Qwen3-4B**: Use batch size 256-512
- **Qwen3-8B**: Use batch size 128-256

#### CPU-Only (Ollama CPU mode)

- Reduce batch sizes by 50%
- Increase `max_concurrent_batches` for parallel processing
- Use Qwen3-0.6B for best CPU performance

## Troubleshooting

### OOM Errors During Indexing

**Symptom**: Out of memory errors when processing large batches

**Solution 1**: Reduce batch size
```json
{
  "embedding": {
    "batch_size": 64  // Lower than auto-configured value
  }
}
```

**Solution 2**: Reduce concurrent batches
```json
{
  "indexing": {
    "max_concurrent_batches": 4  // Default: 8 for OpenAI
  }
}
```

### Reranking Timeouts

**Symptom**: Timeouts when reranking large result sets (>200 documents)

**Solution**: ChunkHound now **automatically handles** this via batch splitting.
If timeouts persist:

```json
{
  "embedding": {
    "timeout": 60  // Increase timeout (default: 30s)
  }
}
```

### Low Throughput

**Symptom**: Indexing slower than expected

**Diagnosis**: Run calibration to find optimal batch size
```bash
chunkhound calibrate --test-document-count 1000
```

**Common fixes**:
1. Increase batch size (if GPU has headroom)
2. Increase `max_concurrent_batches` (if CPU-bound)
3. Switch to smaller model (0.6B for speed, 8B for accuracy)

## Best Practices

### 1. Use Calibration for Initial Setup

Run calibration once per hardware configuration:

```bash
# Save calibration results
chunkhound calibrate \
  --embedding-provider openai \
  --embedding-model dengcao/Qwen3-Embedding-8B:Q5_K_M \
  --output-format json \
  --output-file qwen3-8b-calibration.json

# Use results to update .chunkhound.json
```

### 2. Model Selection Guidelines

- **Large corpora (>100K documents)**: Use Qwen3-0.6B for 2-5x faster indexing
- **Mixed workload**: Use Qwen3-4B for balanced speed/accuracy
- **Maximum accuracy**: Use Qwen3-8B with reranking

### 3. Reranking Configuration

Always configure reranking for production search:

```json
{
  "embedding": {
    "model": "dengcao/Qwen3-Embedding-8B:Q5_K_M",
    "rerank_model": "qwen3-reranker-8b",
    "rerank_url": "/rerank"
  }
}
```

ChunkHound will automatically:
- Split large document sets into batches of 64
- Aggregate and re-sort results by relevance
- Prevent OOM errors

### 4. Monitor Performance

Enable verbose logging to see batch processing:

```bash
chunkhound index /path/to/code --verbose
```

Look for log messages like:
```
Detected Qwen embedding model: dengcao/Qwen3-Embedding-8B:Q5_K_M
Limiting batch size to 128 (model max: 128)
Splitting 300 documents into batches of 64 for reranking
```

## Advanced Configuration

### Override Auto-Configuration

Force specific batch sizes (not recommended unless calibrated):

```json
{
  "embedding": {
    "provider": "openai",
    "model": "dengcao/Qwen3-Embedding-8B:Q5_K_M",
    "batch_size": 256,  // Override auto-configured 128
    "base_url": "http://localhost:11434/v1"
  }
}
```

**Warning**: Values higher than model defaults may cause errors.

### Environment Variables

Override configuration via environment:

```bash
# Batch size
export CHUNKHOUND_EMBEDDING__BATCH_SIZE=256

# Model selection
export CHUNKHOUND_EMBEDDING__MODEL="dengcao/Qwen3-Embedding-4B:Q5_K_M"

# Concurrent batches
export CHUNKHOUND_INDEXING__MAX_CONCURRENT_BATCHES=16
```

## Performance Benchmarks

### Qwen3-0.6B vs 4B vs 8B (Consumer GPU)

Test: Index 10,000 Python files (~50MB total)

| Model | Batch Size | Throughput | Total Time | Accuracy* |
|-------|-----------|------------|------------|-----------|
| Qwen3-0.6B | 512 | 2,100 docs/sec | 4.8 sec | 0.82 |
| Qwen3-4B | 256 | 1,200 docs/sec | 8.3 sec | 0.89 |
| Qwen3-8B | 128 | 650 docs/sec | 15.4 sec | 0.94 |

*Accuracy: MTEB average score (normalized)

**Recommendation**: Use Qwen3-4B for best speed/accuracy tradeoff.

## Further Reading

- [Qwen3 Technical Report](https://arxiv.org/pdf/2506.05176) - Official model documentation
- [Baseten Benchmarks](https://www.baseten.co/blog/day-zero-benchmarks-for-qwen-3-with-sglang-on-baseten) - Performance analysis
- [ChunkHound GitHub](https://github.com/chunkhound/chunkhound) - Source code and issues

## Support

For issues or questions:
1. Check [GitHub Issues](https://github.com/chunkhound/chunkhound/issues)
2. Run `chunkhound calibrate` to diagnose performance issues
3. Enable `--verbose` logging for detailed diagnostics
