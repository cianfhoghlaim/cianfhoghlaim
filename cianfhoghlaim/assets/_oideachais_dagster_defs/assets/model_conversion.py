"""
Dagster Assets for HuggingFace → GGUF model conversion.

Wires the bash scripts in meaisínfhoghlaim/scripts/ as Dagster assets so the
conversion can be re-run on schedule, after upgrading HF models, or after
adding new pre-quantized GGUFs.

Reference: docs/meaisínfhoghlaim/llamacpp.md (Task 2: Convert HF → GGUF)
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from dagster import AssetExecutionContext, AssetMaterialization, MaterializeResult, asset

# ============================================================================
# Paths
# ============================================================================
REPO_ROOT = Path(__file__).resolve().parents[4]  # oideachais/data_platform/dagster_assets -> repo root
CACHE_DIR = REPO_ROOT / "stedding" / "huggingface" / "hub"
GGUF_DIR = REPO_ROOT / "stedding" / "huggingface" / "gguf"
LLAMA_CPP_DIR = REPO_ROOT / "stedding" / "llama.cpp"
SCRIPTS_DIR = REPO_ROOT / "meaisínfhoghlaim" / "scripts"

# Quantization preferences — per docs/meaisínfhoghlaim/llamacpp.md
TEXT_QUANT = "Q4_K_M"
VISION_QUANT = "Q4_K_M"   # LLM portion
MMPROJ_QUANT = "F16"      # vision encoder MUST stay f16


# ============================================================================
# Resource: Conversion result metadata
# ============================================================================
@dataclass
class ConversionResult:
    model_id: str
    src_path: Path
    gguf_path: Path
    quant: str
    size_bytes: int
    duration_s: float


# ============================================================================
# Assets
# ============================================================================

@asset(
    group_name="model_conversion",
    description="Resumes all pending HuggingFace model downloads (28 in-use + 12 pending + 2 stubs)",
)
def hf_models_downloaded(context: AssetExecutionContext) -> MaterializeResult:
    """Run the download_hf_models.sh script to refresh / complete the HF cache."""
    script = SCRIPTS_DIR / "download_hf_models.sh"
    if not script.exists():
        raise FileNotFoundError(f"download_hf_models.sh not found at {script}")

    context.log.info(f"Running {script} (this can take hours for the full set)")

    env = os.environ.copy()
    env["REPO_ROOT"] = str(REPO_ROOT)
    env.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")

    result = subprocess.run(
        [str(script)],
        env=env,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=86400,  # 24h upper bound
    )

    if result.returncode != 0:
        context.log.error(f"stderr: {result.stderr[-2000:]}")
        raise RuntimeError(f"download_hf_models.sh failed: rc={result.returncode}")

    # Count downloaded models
    model_count = sum(1 for p in CACHE_DIR.iterdir() if p.is_dir() and p.name.startswith("models--"))

    return MaterializeResult(
        metadata={
            "model_count": model_count,
            "cache_size": _du(CACHE_DIR),
            "stdout_tail": result.stdout[-1000:],
        }
    )


@asset(
    group_name="model_conversion",
    description="Converts Qwen2.5-Math-7B-Instruct to GGUF Q4_K_M for llama-swap text profile",
)
def gguf_qwen2_5_math_7b(context: AssetExecutionContext) -> MaterializeResult:
    return _convert_text_model(
        context,
        hf_repo="Qwen/Qwen2.5-Math-7B-Instruct",
        out_basename="Qwen2.5-Math-7B-Instruct",
    )


@asset(
    group_name="model_conversion",
    description="Converts UCCIX-Llama2-13B-Instruct to GGUF Q4_K_M (Irish text generation)",
)
def gguf_uccix_13b(context: AssetExecutionContext) -> MaterializeResult:
    return _convert_text_model(
        context,
        hf_repo="ReliableAI/UCCIX-Llama2-13B-Instruct",
        out_basename="UCCIX-Llama2-13B-Instruct",
    )


@asset(
    group_name="model_conversion",
    description="Converts gemma-2-9b to GGUF Q4_K_M (English fallback — replaces 28KB stub)",
)
def gguf_gemma_2_9b(context: AssetExecutionContext) -> MaterializeResult:
    return _convert_text_model(
        context,
        hf_repo="google/gemma-2-9b",
        out_basename="gemma-2-9b",
    )


@asset(
    group_name="model_conversion",
    description="Converts Qwen2.5-VL-7B-Instruct to GGUF Q4_K_M + mmproj f16 (primary VLM)",
)
def gguf_qwen2_5_vl_7b(context: AssetExecutionContext) -> MaterializeResult:
    return _convert_vision_model(
        context,
        hf_repo="Qwen/Qwen2.5-VL-7B-Instruct",
        out_basename="Qwen2.5-VL-7B-Instruct",
    )


@asset(
    group_name="model_conversion",
    description="Converts deepseek-ocr to GGUF Q4_K_M + mmproj f16 (OCR specialist)",
)
def gguf_deepseek_ocr(context: AssetExecutionContext) -> MaterializeResult:
    return _convert_vision_model(
        context,
        hf_repo="deepseek-ai/deepseek-ocr",
        out_basename="deepseek-ocr",
    )


@asset(
    group_name="model_conversion",
    description="Copies pre-quantized Z-Image-Turbo GGUF (no conversion needed)",
)
def gguf_z_image_turbo(context: AssetExecutionContext) -> MaterializeResult:
    return _copy_pre_quantized(
        context,
        hf_repo="vantagewithai/Z-Image-Turbo-GGUF",
        out_basename="Z-Image-Turbo-Q4_K_M",
    )


@asset(
    group_name="model_conversion",
    description="Copies pre-quantized Qwen-Image GGUF",
)
def gguf_qwen_image(context: AssetExecutionContext) -> MaterializeResult:
    return _copy_pre_quantized(
        context,
        hf_repo="unsloth/Qwen-Image-GGUF",
        out_basename="Qwen-Image-Q4_K_M",
    )


@asset(
    group_name="model_conversion",
    description="Copies pre-quantized Qwen-Image-Edit-2511 GGUF",
)
def gguf_qwen_image_edit(context: AssetExecutionContext) -> MaterializeResult:
    return _copy_pre_quantized(
        context,
        hf_repo="unsloth/Qwen-Image-Edit-2511-GGUF",
        out_basename="Qwen-Image-Edit-2511-Q4_K_M",
    )


@asset(
    group_name="model_conversion",
    description="Copies pre-quantized FLUX.2-dev GGUF (highest quality image gen)",
)
def gguf_flux2_dev(context: AssetExecutionContext) -> MaterializeResult:
    return _copy_pre_quantized(
        context,
        hf_repo="unsloth/FLUX.2-dev-GGUF",
        out_basename="FLUX.2-dev-Q4_K_M",
    )


# ============================================================================
# Helpers
# ============================================================================

def _du(path: Path) -> str:
    """Return human-readable disk usage of a path."""
    try:
        out = subprocess.check_output(["du", "-sh", str(path)], text=True)
        return out.split()[0]
    except Exception:
        return "?"


def _convert_text_model(context: AssetExecutionContext, hf_repo: str, out_basename: str) -> MaterializeResult:
    """Convert a text-only HuggingFace model to GGUF Q4_K_M."""
    snapshot = _find_snapshot(hf_repo)
    if not snapshot:
        raise FileNotFoundError(
            f"{hf_repo} not in cache. Run hf_models_downloaded asset first."
        )

    quantize = LLAMA_CPP_DIR / "build" / "bin" / "llama-quantize"
    convert_py = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"
    if not quantize.exists():
        raise FileNotFoundError(
            f"llama.cpp not built. Clone + build at {LLAMA_CPP_DIR}"
        )

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    text_dir = GGUF_DIR / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    f16_path = text_dir / f"{out_basename}-f16.gguf"
    final_path = text_dir / f"{out_basename}-Q4_K_M.gguf"

    # Stage 1: HF → F16 GGUF
    context.log.info(f"Converting {hf_repo} → F16 GGUF")
    subprocess.run(
        ["python3", str(convert_py), str(snapshot),
         "--outfile", str(f16_path), "--outtype", "f16"],
        check=True,
    )

    # Stage 2: F16 → Q4_K_M
    context.log.info(f"Quantizing {f16_path.name} → Q4_K_M")
    subprocess.run(
        [str(quantize), str(f16_path), str(final_path), "Q4_K_M"],
        check=True,
    )

    # Remove F16 intermediate
    f16_path.unlink(missing_ok=True)

    return MaterializeResult(
        metadata={
            "hf_repo": hf_repo,
            "gguf_path": str(final_path),
            "quantization": "Q4_K_M",
            "size": _du(final_path),
        }
    )


def _convert_vision_model(context: AssetExecutionContext, hf_repo: str, out_basename: str) -> MaterializeResult:
    """Convert a VLM to GGUF Q4_K_M (LLM portion) + F16 (mmproj)."""
    snapshot = _find_snapshot(hf_repo)
    if not snapshot:
        raise FileNotFoundError(
            f"{hf_repo} not in cache. Run hf_models_downloaded asset first."
        )

    quantize = LLAMA_CPP_DIR / "build" / "bin" / "llama-quantize"
    convert_py = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    vision_dir = GGUF_DIR / "vision"
    vision_dir.mkdir(parents=True, exist_ok=True)

    # Stage 1: LLM portion → F16
    f16_path = vision_dir / f"{out_basename}-f16.gguf"
    context.log.info(f"Converting {hf_repo} LLM portion → F16 GGUF")
    subprocess.run(
        ["python3", str(convert_py), str(snapshot),
         "--outfile", str(f16_path), "--outtype", "f16"],
        check=True,
    )

    # Stage 2: LLM → Q4_K_M
    final_path = vision_dir / f"{out_basename}-Q4_K_M.gguf"
    context.log.info(f"Quantizing LLM → Q4_K_M")
    subprocess.run(
        [str(quantize), str(f16_path), str(final_path), "Q4_K_M"],
        check=True,
    )
    f16_path.unlink(missing_ok=True)

    # Stage 3: mmproj — try to find a prebuilt one, or skip
    mmproj_src = list(snapshot.glob("**/mmproj*.gguf")) + list(snapshot.glob("**/*mmproj*.gguf"))
    mmproj_dst = vision_dir / f"{out_basename}-mmproj-f16.gguf"
    if mmproj_src:
        mmproj_dst.write_bytes(mmproj_src[0].read_bytes())
        context.log.info(f"mmproj copied to {mmproj_dst.name}")
    else:
        context.log.warning(
            f"No pre-built mmproj found in {snapshot}. "
            "VLM cannot run without mmproj. Check the model's repo for an mmproj file."
        )

    return MaterializeResult(
        metadata={
            "hf_repo": hf_repo,
            "gguf_llm_path": str(final_path),
            "gguf_mmproj_path": str(mmproj_dst) if mmproj_src else None,
            "llm_quantization": "Q4_K_M",
            "mmproj_quantization": "F16",
            "llm_size": _du(final_path),
        }
    )


def _copy_pre_quantized(context: AssetExecutionContext, hf_repo: str, out_basename: str) -> MaterializeResult:
    """Copy a pre-quantized GGUF (e.g. unsloth/*) without conversion."""
    snapshot = _find_snapshot(hf_repo)
    if not snapshot:
        raise FileNotFoundError(
            f"{hf_repo} not in cache. Run hf_models_downloaded asset first."
        )

    GGUF_DIR.mkdir(parents=True, exist_ok=True)
    image_dir = GGUF_DIR / "image"
    image_dir.mkdir(parents=True, exist_ok=True)

    final_path = image_dir / f"{out_basename}.gguf"

    ggufs = [f for f in snapshot.rglob("*.gguf") if "mmproj" not in f.name]
    if not ggufs:
        raise FileNotFoundError(f"No GGUF found in {snapshot}")

    # Pick the largest (most likely Q8 or similar) unless only one
    src = max(ggufs, key=lambda p: p.stat().st_size) if len(ggufs) > 1 else ggufs[0]
    final_path.write_bytes(src.read_bytes())

    return MaterializeResult(
        metadata={
            "hf_repo": hf_repo,
            "gguf_path": str(final_path),
            "source_file": src.name,
            "size": _du(final_path),
        }
    )


def _find_snapshot(hf_repo: str) -> Path | None:
    """Find the snapshot directory for a HuggingFace repo_id in the local cache."""
    repo_dir = CACHE_DIR / f"models--{hf_repo.replace('/', '--')}"
    if not repo_dir.exists():
        return None
    snapshots = list((repo_dir / "snapshots").iterdir())
    if not snapshots:
        return None
    return snapshots[0]


# Asset collections for definitions.py
model_conversion_assets = [
    hf_models_downloaded,
    gguf_qwen2_5_math_7b,
    gguf_uccix_13b,
    gguf_gemma_2_9b,
    gguf_qwen2_5_vl_7b,
    gguf_deepseek_ocr,
    gguf_z_image_turbo,
    gguf_qwen_image,
    gguf_qwen_image_edit,
    gguf_flux2_dev,
]
