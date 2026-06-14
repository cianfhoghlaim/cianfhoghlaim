#!/usr/bin/env bash
# =============================================================================
# Convert HuggingFace safetensors → GGUF (Q4_K_M + mmproj f16)
# =============================================================================
# Conversion follows the patterns in docs/meaisínfhoghlaim/llamacpp.md
# and docs/meaisínfhoghlaim/Setting Up Local LLM Services on Mac.md
#
# Two-stage pipeline:
#   1. python convert_hf_to_gguf.py  → F16 GGUF (preserves quality)
#   2. llama-quantize  → Q4_K_M GGUF (4-bit, balanced)
#
# For VLMs, the mmproj file is converted separately and kept at F16.
#
# Output layout:  stedding/huggingface/gguf/{text,vision,image}/
# =============================================================================
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
CACHE_DIR="$REPO_ROOT/stedding/huggingface/hub"
GGUF_DIR="$REPO_ROOT/stedding/huggingface/gguf"
LLAMA_CPP_DIR="$REPO_ROOT/stedding/llama.cpp"

mkdir -p "$GGUF_DIR/text" "$GGUF_DIR/vision" "$GGUF_DIR/image"

# Find llama-quantize + convert_hf_to_gguf.py
if [[ ! -f "$LLAMA_CPP_DIR/build/bin/llama-quantize" ]]; then
  echo "ERROR: llama.cpp not built. Clone + build first:"
  echo "  git clone https://github.com/ggml-org/llama.cpp $LLAMA_CPP_DIR"
  echo "  cd $LLAMA_CPP_DIR && cmake -B build && cmake --build build --config Release -j8"
  exit 1
fi

QUANTIZE="$LLAMA_CPP_DIR/build/bin/llama-quantize"
CONVERT="$LLAMA_CPP_DIR/convert_hf_to_gguf.py"

# =============================================================================
# TEXT MODELS
# =============================================================================
convert_text() {
  local hf_repo="$1"
  local out_basename="$2"
  local snapshot
  snapshot=$(ls -d "$CACHE_DIR/models--${hf_repo//\//--}"/snapshots/*/ | head -1)
  if [[ ! -d "$snapshot" ]]; then
    echo "SKIP: $hf_repo — not in cache. Run download_hf_models.sh first."
    return 1
  fi

  echo "==> Converting $hf_repo → $GGUF_DIR/text/$out_basename"
  python3 "$CONVERT" "$snapshot" \
    --outfile "$GGUF_DIR/text/$out_basename-f16.gguf" \
    --outtype f16

  echo "    Quantizing → Q4_K_M"
  "$QUANTIZE" \
    "$GGUF_DIR/text/$out_basename-f16.gguf" \
    "$GGUF_DIR/text/$out_basename-Q4_K_M.gguf" \
    Q4_K_M

  echo "    Removing F16 intermediate (saves ~50% disk)"
  rm -f "$GGUF_DIR/text/$out_basename-f16.gguf"
}

# =============================================================================
# VISION MODELS (LLM weights Q4_K_M, mmproj kept F16)
# =============================================================================
convert_vision() {
  local hf_repo="$1"
  local out_basename="$2"
  local snapshot
  snapshot=$(ls -d "$CACHE_DIR/models--${hf_repo//\//--}"/snapshots/*/ | head -1)
  if [[ ! -d "$snapshot" ]]; then
    echo "SKIP: $hf_repo — not in cache. Run download_hf_models.sh first."
    return 1
  fi

  echo "==> Converting VLM $hf_repo → $GGUF_DIR/vision/$out_basename"

  # 1. Convert the LLM portion
  python3 "$CONVERT" "$snapshot" \
    --outfile "$GGUF_DIR/vision/$out_basename-f16.gguf" \
    --outtype f16

  # 2. Extract the mmproj file (F16 — DO NOT quantize)
  if ls "$snapshot"/mmproj*.gguf "$snapshot"/*mmproj*.gguf 2>/dev/null; then
    cp "$snapshot"/mmproj*.gguf "$GGUF_DIR/vision/$out_basename-mmproj-f16.gguf" 2>/dev/null || \
    cp "$snapshot"/*mmproj*.gguf "$GGUF_DIR/vision/$out_basename-mmproj-f16.gguf" 2>/dev/null || \
    echo "    NOTE: no pre-built mmproj — must run llama-gen-docs mmproj separately"
  fi

  # 3. Quantize LLM portion to Q4_K_M
  "$QUANTIZE" \
    "$GGUF_DIR/vision/$out_basename-f16.gguf" \
    "$GGUF_DIR/vision/$out_basename-Q4_K_M.gguf" \
    Q4_K_M

  # 4. Remove the F16 LLM (we kept mmproj F16; LLM is Q4_K_M)
  rm -f "$GGUF_DIR/vision/$out_basename-f16.gguf"
}

# =============================================================================
# Run conversions
# =============================================================================
echo "================================================================"
echo "  TEXT MODELS"
echo "================================================================"
convert_text "Qwen/Qwen2.5-Math-7B-Instruct"        "Qwen2.5-Math-7B-Instruct"
convert_text "ReliableAI/UCCIX-Llama2-13B-Instruct" "UCCIX-Llama2-13B-Instruct"
convert_text "google/gemma-2-9b"                    "gemma-2-9b"
convert_text "Qwen/Qwen2.5-VL-7B-Instruct"          "Qwen2.5-VL-7B-Instruct-text"

echo ""
echo "================================================================"
echo "  VISION MODELS (Q4_K_M LLM + F16 mmproj)"
echo "================================================================"
convert_vision "Qwen/Qwen2.5-VL-7B-Instruct"        "Qwen2.5-VL-7B-Instruct"
convert_vision "Qwen/Qwen2-VL-7B-Instruct"          "Qwen2-VL-7B-Instruct"
convert_vision "deepseek-ai/deepseek-ocr"           "deepseek-ocr"
convert_vision "THUDM/glm-4v-9b"                    "glm-4v-9b"

echo ""
echo "================================================================"
echo "  Pre-quantized GGUFs (download from unsloth, no conversion needed)"
echo "================================================================"
copy_gguf() {
  local hf_repo="$1"
  local out_basename="$2"
  local snapshot
  snapshot=$(ls -d "$CACHE_DIR/models--${hf_repo//\//--}"/snapshots/*/ | head -1)
  if [[ ! -d "$snapshot" ]]; then
    echo "SKIP: $hf_repo — not in cache"
    return 1
  fi
  echo "  Copying $hf_repo → $GGUF_DIR/image/$out_basename.gguf"
  find "$snapshot" -name "*.gguf" -not -name "*mmproj*" -exec cp {} "$GGUF_DIR/image/$out_basename.gguf" \;
}

copy_gguf "vantagewithai/Z-Image-Turbo-GGUF"        "Z-Image-Turbo-Q4_K_M"
copy_gguf "unsloth/Qwen-Image-GGUF"                 "Qwen-Image-Q4_K_M"
copy_gguf "unsloth/Qwen-Image-Edit-2511-GGUF"       "Qwen-Image-Edit-2511-Q4_K_M"
copy_gguf "unsloth/FLUX.2-dev-GGUF"                 "FLUX.2-dev-Q4_K_M"

echo ""
echo "================================================================"
echo "  RESULT"
echo "================================================================"
du -sh "$GGUF_DIR"/*/*.gguf 2>/dev/null | sort -hr
echo ""
echo "Total GGUF size:"
du -sh "$GGUF_DIR"
