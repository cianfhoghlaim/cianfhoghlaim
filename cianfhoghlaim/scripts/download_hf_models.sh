#!/usr/bin/env bash
# =============================================================================
# Resume and bootstrap HuggingFace model downloads
# =============================================================================
# Downloads all 28 cached models + 12 pending + 2 stubs (gemma-2-9b, UCCIX).
# Uses parallel transfers + resume-on-failure.
#
# Cache layout:  stedding/huggingface/hub/
# Env wiring:    HF_HOME, HF_HUB_CACHE, HF_HUB_DOWNLOAD_TIMEOUT (in .env)
# =============================================================================
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
CACHE_DIR="$REPO_ROOT/stedding/huggingface/hub"
export HF_HOME="$REPO_ROOT/stedding/huggingface"
export HF_HUB_CACHE="$CACHE_DIR"
export HF_HUB_DOWNLOAD_TIMEOUT="${HF_HUB_DOWNLOAD_TIMEOUT:-600}"
export HF_HUB_ENABLE_HF_TRANSFER=1   # parallel downloads via Rust hf_transfer

if [[ -z "${HF_TOKEN:-}" && -f "$REPO_ROOT/.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source "$REPO_ROOT/.env"; set +a
fi

if [[ -z "${HF_TOKEN:-}" ]]; then
  echo "ERROR: HF_TOKEN not set. Add to .env or set HF_TOKEN=hf_..." >&2
  exit 1
fi

# hf-transfer speeds up large downloads by 5-10x
python3 -c "import hf_transfer" 2>/dev/null || pip install --quiet hf_transfer

mkdir -p "$CACHE_DIR"

# =============================================================================
# In-use (cached) models — refresh metadata + verify
# =============================================================================
IN_USE_MODELS=(
  "BAAI/bge-large-en-v1.5"
  "BAAI/bge-m3"
  "BAAI/bge-small-en-v1.5"
  "cpierse/wav2vec2-large-xlsr-53-irish"
  "DCU-NLP/bert-base-irish-cased-v1"
  "deepseek-ai/deepseek-ocr"
  "facebook/m2m100_418M"
  "facebook/nllb-200-distilled-600M"
  "facebook/wav2vec2-base"
  "facebook/wav2vec2-large-xlsr-53"
  "google/gemma-2-9b"             # STUB — re-download full
  "Helsinki-NLP/opus-mt-cy-en"
  "Helsinki-NLP/opus-mt-en-cy"
  "Helsinki-NLP/opus-mt-en-ga"
  "Helsinki-NLP/opus-mt-ga-en"
  "openai/whisper-large-v3"
  "Qwen/Qwen2-VL-7B-Instruct"
  "Qwen/Qwen2.5-Math-7B-Instruct"
  "Qwen/Qwen2.5-VL-7B-Instruct"
  "ReliableAI/UCCIX-Llama2-13B-Instruct"  # STUB — re-download full
  "ResembleAI/chatterbox"
  "sentence-transformers/all-MiniLM-L6-v2"
  "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  "Snowflake/snowflake-arctic-embed-xs"
  "THUDM/glm-4v-9b"
  "vidore/colpali-v1.2"
  "vidore/colpali-v1.3"
)

# =============================================================================
# Pending downloads (from stedding/huggingface/README.md)
# =============================================================================
PENDING_MODELS=(
  "briaai/FIBO"                 # image gen, JSON config
  "briaai/FIBO-VAE"             # VAE for FIBO
  "briaai/FIBO-Adapter"
  "briaai/FIBO-Adapter-v2"
  "google/siglip-so400m-patch14-384"  # vision encoder
  "google/siglip2-so400m-patch16-256"  # newer siglip
  "unsloth/gemma-3-9b-it-GGUF"  # pre-quantized GGUF
  "unsloth/DeepSeek-OCR"        # GGUF variant
  "vantagewithai/Z-Image-Turbo-GGUF"  # fast image gen
  "unsloth/Qwen-Image-GGUF"     # image gen
  "unsloth/Qwen-Image-Edit-2511-GGUF"  # image editing
  "unsloth/FLUX.2-dev-GGUF"     # high quality image gen
)

# =============================================================================
# OpenCode Go (for LiteLLM passthrough — not actually downloaded, API access)
# =============================================================================

echo "==> Downloading ${#IN_USE_MODELS[@]} in-use models + ${#PENDING_MODELS[@]} pending"
echo "==> Cache: $CACHE_DIR"
echo "==> HF_HUB_DOWNLOAD_TIMEOUT: $HF_HUB_DOWNLOAD_TIMEOUT s"
echo ""

download_model() {
  local repo_id="$1"
  echo "----------------------------------------------------------------"
  echo "  Fetching: $repo_id"
  huggingface-cli download "$repo_id" \
    --token "$HF_TOKEN" \
    --cache-dir "$CACHE_DIR" \
    --resume-download \
    --include '*.json' '*.txt' '*.model' '*.safetensors' '*.bin' '*.gguf' '*.tiktoken' '*.py' 'tokenizer*' \
    2>&1 | tail -5 \
    || echo "  WARNING: partial download for $repo_id — will resume on next run"
}

for model in "${IN_USE_MODELS[@]}" "${PENDING_MODELS[@]}"; do
  download_model "$model"
done

echo ""
echo "==> Disk footprint after downloads:"
du -sh "$CACHE_DIR"/* 2>/dev/null | sort -hr | head -20
echo ""
echo "==> Total cache size:"
du -sh "$CACHE_DIR"
