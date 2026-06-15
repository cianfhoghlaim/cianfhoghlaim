"""meaisínfhoghlaim.dagster_defs.assets.healthchecks — 4 heartbeat assets.

Phase 0.2 of lateralise-british-isles-domains. Each heartbeat
materialises to a no-op `MaterializeResult("ok")` so the AI/ML
quadrant is observable in `dg dev` from the repo root, without
requiring GPU compute or live network access.

The 4 heartbeats correspond to the 4 major meaisínfhoghlaim
subsystems that will eventually be wrapped as Dagster+DLT assets:

  1. curriculum_agent_healthcheck   ← agents/curriculum_agent.py
  2. dialect_classifier_healthcheck ← pipelines/dialect_classifier.py
  3. transcript_aligner_healthcheck  ← pipelines/transcript_aligner.py
  4. irish_document_scanner_healthcheck ← pipelines/irish_document_scanner.py

We import via short sub-package names (e.g. `from agents import
curriculum_agent`) because the meaisínfhoghlaim wheel only installs
its sub-packages (agents, ocr, language, pipelines, ...), not the
top-level namespace.
"""
from dagster import MaterializeResult, asset


@asset(
    group_name="meaisin_heartbeat",
    compute_kind="python",
    description=(
        "Heartbeat for the curriculum_agent module. Phase 0.2: no-op. "
        "Future: wraps the 12 meaisín agents as Dagster assets, calling "
        "the FastAPI agent endpoints and materialising the response."
    ),
)
def curriculum_agent_healthcheck(context) -> MaterializeResult:
    """Smoke-test that the curriculum_agent module imports cleanly."""
    try:
        from agents import curriculum_agent  # noqa: F401
        ok = True
        err = None
    except Exception as exc:
        ok = False
        err = f"{type(exc).__name__}: {exc}"
    return MaterializeResult(
        metadata={
            "subsystem": "curriculum_agent",
            "import_ok": ok,
            "error": err or "",
        }
    )


@asset(
    group_name="meaisin_heartbeat",
    compute_kind="python",
    description=(
        "Heartbeat for the dialect_classifier pipeline. Phase 0.2: no-op. "
        "Future: wraps the IrishConnacht/Munster/Ulster dialect classifier "
        "as a DLT resource that materialises per-dialect audio embeddings."
    ),
)
def dialect_classifier_healthcheck(context) -> MaterializeResult:
    try:
        from pipelines import dialect_classifier  # noqa: F401
        ok = True
        err = None
    except Exception as exc:
        ok = False
        err = f"{type(exc).__name__}: {exc}"
    return MaterializeResult(
        metadata={
            "subsystem": "dialect_classifier",
            "import_ok": ok,
            "error": err or "",
        }
    )


@asset(
    group_name="meaisin_heartbeat",
    compute_kind="python",
    description=(
        "Heartbeat for the transcript_aligner pipeline. Phase 0.2: no-op. "
        "Future: wraps MFA / Wav2Vec2 / WhisperX alignment as a DLT "
        "resource that materialises (audio_path, transcript) rows."
    ),
)
def transcript_aligner_healthcheck(context) -> MaterializeResult:
    try:
        from pipelines import transcript_aligner  # noqa: F401
        ok = True
        err = None
    except Exception as exc:
        ok = False
        err = f"{type(exc).__name__}: {exc}"
    return MaterializeResult(
        metadata={
            "subsystem": "transcript_aligner",
            "import_ok": ok,
            "error": err or "",
        }
    )


@asset(
    group_name="meaisin_heartbeat",
    compute_kind="python",
    description=(
        "Heartbeat for the irish_document_scanner pipeline. Phase 0.2: no-op. "
        "Future: wraps the OCR/HTR pipeline (pytesseract, olmOCR, VLM "
        "fine tuning) as a Dagster asset that materialises scanned-document "
        "LanceDB embeddings."
    ),
)
def irish_document_scanner_healthcheck(context) -> MaterializeResult:
    try:
        from pipelines import irish_document_scanner  # noqa: F401
        ok = True
        err = None
    except Exception as exc:
        ok = False
        err = f"{type(exc).__name__}: {exc}"
    return MaterializeResult(
        metadata={
            "subsystem": "irish_document_scanner",
            "import_ok": ok,
            "error": err or "",
        }
    )
