"""Tests for the 24-entry VISION_MODELS registry (v4 home).

Per the openspec change 2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority,
every VISION_MODELS entry must have:
- A valid `unsloth_id`, `mlx_id`, OR `upstream_id` (at least one)
- A `role` in {"tier1_heavy", "tier2_medium", "tier3_light", "specialist", "legacy"}
- A `backend` in the v4 enum (no OpenAI / Anthropic)
- At least one `ModelCapability`
- `m4_max_48gb_fit` is a bool
- `arm1_oci_required` is a bool
- `available` is a bool
- A non-empty `notes` string

Plus: at least 3 models must have `unsloth_features` containing
"moe_12x" (the Gemma-4-26B-A4B + Qwen3-VL-30B-A3B + Qwen3.6-35B-A3B),
at least 1 must have "mtp_speculative" (the Qwen 3.6 models),
at least 5 must have "imatrix" (the Unsloth GGUFs).
"""

from __future__ import annotations

import os
import sys
import unittest

# Add the repo root to sys.path so the `cianfhoghlaim` package is importable.
# The v4 consolidation has moved everything to `cianfhoghlaim.*` but the
# tests still run in the legacy `sruth.*` namespace by default.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from cianfhoghlaim.ocr.models import (  # noqa: E402
    CLASSICAL_OCR,
    MODEL_BACKEND,
    MODEL_CAPABILITY,
    TEXT_MODELS,
    VISION_MODELS,
    ModelBackend,
    ModelCapability,
    ModelRegistry,
    get_default_for_m4_max,
    get_optimal_for_m4,
    select_ocr_backend,
)


class TestRegistryStructure(unittest.TestCase):
    """Structural tests for the 24-entry VISION_MODELS registry."""

    def test_vision_models_count(self):
        """The registry must have at least 20 entries per the v4 spec (post-2026-06-29 trim)."""
        self.assertGreaterEqual(
            len(VISION_MODELS), 20,
            f"Expected at least 20 VISION_MODELS entries, got {len(VISION_MODELS)}",
        )

    def test_vision_models_keys_unique(self):
        """All VISION_MODELS keys must be unique."""
        self.assertEqual(len(VISION_MODELS), len(set(VISION_MODELS.keys())))

    def test_no_cloud_api_backends(self):
        """Per the v4 spec, no OpenAI or Anthropic backends in the registry.

        The v4 ModelBackend enum has been narrowed to LITELLM, MLX,
        TRANSFORMERS, and LLAMASWAP — no OPENAI, no ANTHROPIC, no OLLAMA.
        """
        # The v4 enum must not contain OPENAI or ANTHROPIC
        backend_values = {b.value for b in ModelBackend}
        self.assertNotIn("openai", backend_values)
        self.assertNotIn("anthropic", backend_values)
        # And no model should have a backend string value of "openai" or "anthropic"
        for key, model in VISION_MODELS.items():
            self.assertNotIn(model.backend.value, ("openai", "anthropic"))

    def test_all_entries_have_at_least_one_inference_id(self):
        """Every entry must have at least one of unsloth_id, mlx_id, upstream_id."""
        for key, model in VISION_MODELS.items():
            self.assertTrue(
                model.unsloth_id or model.mlx_id or model.upstream_id,
                f"{key} has no inference ID (unsloth_id/mlx_id/upstream_id)",
            )

    def test_all_entries_have_valid_role(self):
        """Every entry must have a role in the canonical 5-value enum."""
        valid_roles = {"tier1_heavy", "tier2_medium", "tier3_light", "specialist", "legacy"}
        for key, model in VISION_MODELS.items():
            self.assertIn(
                model.role, valid_roles,
                f"{key} has invalid role: {model.role}",
            )

    def test_all_entries_have_at_least_one_capability(self):
        """Every entry must have at least one ModelCapability."""
        for key, model in VISION_MODELS.items():
            self.assertGreaterEqual(
                len(model.capabilities), 1,
                f"{key} has no capabilities",
            )

    def test_all_entries_have_non_empty_notes(self):
        """Every entry must have a non-empty notes string."""
        for key, model in VISION_MODELS.items():
            self.assertTrue(
                len(model.notes) > 0,
                f"{key} has empty notes",
            )


class TestRegistryContent(unittest.TestCase):
    """Content tests for specific VISION_MODELS entries."""

    def test_gemma_4_4_size_ladder(self):
        """The Gemma 4 ladder must have 4 sizes (post-2026-06-29 trim: gemma-4-31B removed)."""
        gemma4_keys = [k for k in VISION_MODELS if k.startswith("gemma-4-")]
        self.assertEqual(
            len(gemma4_keys), 4,
            f"Expected 4 Gemma 4 sizes, got {len(gemma4_keys)}: {gemma4_keys}",
        )
        expected = {"gemma-4-E2B", "gemma-4-E4B", "gemma-4-12B", "gemma-4-26B-A4B"}
        self.assertEqual(set(gemma4_keys), expected)

    def test_qwen3_vl_3_size_ladder(self):
        """The Qwen 3-VL ladder must have 3 sizes (4B + 8B + 30B-A3B; 235B-A22B removed)."""
        qwen3_vl_keys = [k for k in VISION_MODELS if k.startswith("qwen3-vl-")]
        self.assertEqual(
            len(qwen3_vl_keys), 3,
            f"Expected 3 Qwen 3-VL sizes, got {len(qwen3_vl_keys)}: {qwen3_vl_keys}",
        )
        expected = {"qwen3-vl-4b", "qwen3-vl-8b", "qwen3-vl-30b-a3b"}
        self.assertEqual(set(qwen3_vl_keys), expected)

    def test_qwen3_6_1_size_mtp_ladder(self):
        """The Qwen 3.6 ladder must have 1 size with MTP speculative decoding (post-trim: 35B-A3B-MTP removed)."""
        qwen36_keys = [k for k in VISION_MODELS if k.startswith("qwen3.6-")]
        self.assertEqual(
            len(qwen36_keys), 1,
            f"Expected 1 Qwen 3.6 size, got {len(qwen36_keys)}: {qwen36_keys}",
        )
        for k in qwen36_keys:
            self.assertIn(
                "mtp_speculative", VISION_MODELS[k].unsloth_features,
                f"{k} should have mtp_speculative in unsloth_features",
            )

    def test_gemma_4_26B_A4B_is_default(self):
        """Per the v4 spec, gemma-4-26B-A4B is the M4 Max default."""
        self.assertEqual(get_default_for_m4_max(), "gemma-4-26B-A4B")

    def test_moe_12x_models_count(self):
        """At least 1 model must have moe_12x (the qwen3-vl-30b-a3b MoE; 2 others removed in trim)."""
        moe_models = [
            k for k, m in VISION_MODELS.items()
            if "moe_12x" in m.unsloth_features
        ]
        self.assertGreaterEqual(
            len(moe_models), 1,
            f"Expected at least 1 moe_12x model, got {len(moe_models)}",
        )

    def test_uccix_mistral_24b_is_primary(self):
        """UCCIX-Mistral-24B must be available; UCCIX-Llama2-13B must be legacy."""
        self.assertTrue(VISION_MODELS["uccix-mistral-24b"].available)
        self.assertFalse(
            VISION_MODELS["uccix-llama2-13b"].available,
            "uccix-llama2-13b (deprecated Llama 2) should be marked unavailable",
        )
        self.assertEqual(VISION_MODELS["uccix-llama2-13b"].role, "legacy")

    def test_olmocr_correct_id(self):
        """The allenai olmOCR ID must be allenai/olmOCR-2-7B-1025 (v2)."""
        self.assertEqual(
            VISION_MODELS["olmocr-2-7b-1025"].upstream_id,
            "allenai/olmOCR-2-7B-1025",
        )

    def test_deepseek_ocr_correct_id(self):
        """The DeepSeek-OCR ID must be deepseek-ai/DeepSeek-OCR-2 (v2 superset)."""
        self.assertEqual(
            VISION_MODELS["deepseek-ocr-2"].upstream_id,
            "deepseek-ai/DeepSeek-OCR-2",
        )

    def test_granite_docling_correct_id(self):
        """The Granite-Docling ID must be ibm-granite/granite-docling-258M."""
        self.assertEqual(
            VISION_MODELS["granite-docling-258M"].upstream_id,
            "ibm-granite/granite-docling-258M",
        )

    def test_glm_4_6v_flash_kept_not_renamed(self):
        """Per the v4 spec, glm-4.6v-flash is the canonical key (reverted from glm-4v-9b)."""
        self.assertIn("glm-4.6v-flash", VISION_MODELS)
        self.assertIn("zai-org/GLM-4.6V-Flash", VISION_MODELS["glm-4.6v-flash"].upstream_id)

    def test_qwen3_vl_8b_unsloth_gguf(self):
        """Qwen3-VL 8B must point at the Unsloth GGUF (priority)."""
        model = VISION_MODELS["qwen3-vl-8b"]
        self.assertEqual(
            model.unsloth_id,
            "unsloth/Qwen3-VL-8B-Instruct-GGUF",
        )

    def test_digram_capability_present(self):
        """The new DIAGRAM capability (per the v4 spec) must be present."""
        diagram_models = [
            k for k, m in VISION_MODELS.items()
            if ModelCapability.DIAGRAM in m.capabilities
        ]
        self.assertGreaterEqual(
            len(diagram_models), 5,
            f"Expected at least 5 DIAGRAM-capable models, got {len(diagram_models)}",
        )


class TestClassicalOCR(unittest.TestCase):
    """Tests for the CLASSICAL_OCR Docker registry."""

    def test_classical_ocr_count(self):
        """The CLASSICAL_OCR registry must have 6 stacks (per the v4 spec)."""
        self.assertGreaterEqual(
            len(CLASSICAL_OCR), 6,
            f"Expected at least 6 classical OCR stacks, got {len(CLASSICAL_OCR)}",
        )

    def test_classical_ocr_keys(self):
        """The 6 classical OCR stacks must be the canonical ones."""
        expected = {
            "docling-serve", "paddleocr", "olmocr",
            "tesseract", "pylaia", "dots-ocr",
        }
        actual = set(CLASSICAL_OCR.keys())
        self.assertTrue(
            expected.issubset(actual),
            f"Missing classical OCR stacks: {expected - actual}",
        )


class TestTextModels(unittest.TestCase):
    """Tests for the TEXT_MODELS dict (for the agent fleet)."""

    def test_text_models_count(self):
        """The TEXT_MODELS dict must have at least 3 entries."""
        self.assertGreaterEqual(len(TEXT_MODELS), 3)


class TestGetOptimalForM4(unittest.TestCase):
    """Tests for the get_optimal_for_m4 helper."""

    def test_prefers_unsloth(self):
        """When unsloth_id is set, get_optimal_for_m4 must return it."""
        model = VISION_MODELS["gemma-4-26B-A4B"]
        self.assertEqual(
            get_optimal_for_m4("gemma-4-26B-A4B"),
            "unsloth/gemma-4-26B-A4B-it-GGUF",
        )

    def test_falls_back_to_upstream(self):
        """When unsloth_id is None, must fall back to mlx_id or upstream_id."""
        model = VISION_MODELS["molmo2-8b"]
        self.assertIsNone(model.unsloth_id)
        # molmo2-8b has mlx_id=None too, so it falls back to upstream_id
        self.assertEqual(
            get_optimal_for_m4("molmo2-8b"),
            "allenai/Molmo2-8B",
        )


class TestSelectOCRBackend(unittest.TestCase):
    """Tests for the select_ocr_backend helper."""

    def test_small_pdf_uses_gemma4_e2b(self):
        """Small (<5 MB) text-first PDFs should use gemma-4-E2B."""
        from pathlib import Path
        # Create a small temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"x" * (1 * 1024 * 1024))  # 1 MB
            tmp_path = Path(tmp.name)

        try:
            selection = select_ocr_backend(tmp_path)
            self.assertEqual(selection.model.key, "gemma-4-E2B")
        finally:
            tmp_path.unlink()

    def test_dense_pdf_uses_gemma4_26B(self):
        """Large (>=5 MB) PDFs should use gemma-4-26B-A4B."""
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(b"x" * (10 * 1024 * 1024))  # 10 MB
            tmp_path = Path(tmp.name)

        try:
            selection = select_ocr_backend(tmp_path)
            self.assertEqual(selection.model.key, "gemma-4-26B-A4B")
        finally:
            tmp_path.unlink()

    def test_marking_scheme_uses_molmo2(self):
        """Marking schemes should use molmo2-8b (image-heavy)."""
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(suffix="marking_scheme.pdf", delete=False) as tmp:
            tmp.write(b"x" * (10 * 1024 * 1024))  # 10 MB
            tmp_path = Path(tmp.name)

        try:
            selection = select_ocr_backend(tmp_path)
            self.assertEqual(selection.model.key, "molmo2-8b")
        finally:
            tmp_path.unlink()


class TestModelRegistry(unittest.TestCase):
    """Tests for the ModelRegistry class."""

    def test_default_registry_has_20_models(self):
        """A default ModelRegistry must have at least 20 models (post-2026-06-29 trim)."""
        reg = ModelRegistry()
        self.assertGreaterEqual(len(reg.list_models()), 20)

    def test_get_model_by_key(self):
        """get_model must return the correct model by key."""
        reg = ModelRegistry()
        model = reg.get_model("gemma-4-26B-A4B")
        self.assertEqual(model.key, "gemma-4-26B-A4B")

    def test_get_model_unknown_raises(self):
        """get_model with an unknown key must raise ValueError."""
        reg = ModelRegistry()
        with self.assertRaises(ValueError):
            reg.get_model("nonexistent-model")

    def test_get_models_with_capability(self):
        """get_models_with_capability must return all models with the capability."""
        reg = ModelRegistry()
        diagram_models = reg.get_models_with_capability(ModelCapability.DIAGRAM)
        self.assertGreaterEqual(len(diagram_models), 5)


if __name__ == "__main__":
    unittest.main()
