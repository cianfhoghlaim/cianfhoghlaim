"""fleet.educational — the 5 educational agents for meaisínfhoghlaim.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
The 5 agents form the canonical educational agent surface:
- OCR-Router — picks the best OCR backend per PDF
- HTR-FineTuner — fine-tunes Gemma 4 / Qwen3-VL on Dúchas transcriptions
- Schema-Extractor — BAML structured field extraction from OCR text
- Eval-Orchestrator — RAGAS eval across the 24 OCR/VLM models
- Alignment-Worker — bilingual EU IR-EN + NCCA alignment pipeline

Each agent is dispatched via Hermes (API + channels) + OpenClaw (consumer gateway).
"""

from .ocr_router import ocr_router_agent, run_ocr_router
from .htr_fine_tuner import htr_fine_tuner_agent, run_htr_finetune
from .schema_extractor import schema_extractor_agent, run_schema_extract
from .eval_orchestrator import eval_orchestrator_agent, run_eval
from .alignment_worker import alignment_worker_agent, run_alignment


AGENT_REGISTRY = {
    "ocr_router": ocr_router_agent,
    "htr_fine_tuner": htr_fine_tuner_agent,
    "schema_extractor": schema_extractor_agent,
    "eval_orchestrator": eval_orchestrator_agent,
    "alignment_worker": alignment_worker_agent,
}


RUNNERS = {
    "ocr_router": run_ocr_router,
    "htr_fine_tuner": run_htr_finetune,
    "schema_extractor": run_schema_extract,
    "eval_orchestrator": run_eval,
    "alignment_worker": run_alignment,
}


__all__ = [
    "AGENT_REGISTRY",
    "RUNNERS",
    "ocr_router_agent", "run_ocr_router",
    "htr_fine_tuner_agent", "run_htr_finetune",
    "schema_extractor_agent", "run_schema_extract",
    "eval_orchestrator_agent", "run_eval",
    "alignment_worker_agent", "run_alignment",
]
