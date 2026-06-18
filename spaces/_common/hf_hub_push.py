"""HF Hub push helper.

Codifies the HF Hub model-publish pattern from the prior-art project
`spaces/anti-phish/` (which pushed `foghlaimeoir/phishing-DistilBERT`; pattern
B6 from `spaces/README.md` §1.2). Uses `huggingface_hub.HfApi.upload_folder`
rather than the manual `pipeline.push_to_hub` so the helper handles OCR
checkpoints, sklearn pickles, and BAML-compiled artefacts uniformly.

Why this exists:

The prior-art notebook hand-rolled the upload via `huggingface-cli upload`
in a Bash cell. We want a typed, testable Python function that:

1. Resolves the HF token from the `HF_TOKEN` env (the same one that the
   `infrastructure/ci/spaces-sync.yml` workflow uses).
2. Returns the commit SHA so callers can reference it (e.g. for a
   downstream Dagster asset or a BAML `commit_sha` field).
3. Works for any directory, not just HF model checkpoints — so we can
   push `meaisinfhoghlaim/ocr/checkpoints/<model>/` (which is not an HF
   `transformers` checkpoint structure) or sklearn `pickle` files.

Usage:

    from spaces._common.hf_hub_push import push_model_to_hub

    sha = push_model_to_hub(
        local_dir=Path("models/phishing-distilbert"),
        repo_id="cianfhoghlaim/phishing-distilbert",
        commit_message="Initial upload of fine-tuned DistilBERT",
    )
    print(sha)  # 'a1b2c3d4e5f6...'

The 2 `gradio-ensemble-pattern` scenarios in
`openspec/changes/celtic-data-engineering-patterns/specs/gradio-ensemble-pattern/spec.md`
are validated by `meaisinfhoghlaim/tests/test_hf_hub_push.py`.

See also:
- `meaisinfhoghlaim/pipelines/ensemble_gradio.py` (the Gradio ensemble companion)
- `spaces/anti-phish/README.md:25` (the prior-art upload)
"""

from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import HfApi


def push_model_to_hub(
    local_dir: Path,
    repo_id: str,
    commit_message: str,
    *,
    token: str | None = None,
    repo_type: str = "model",
) -> str:
    """Upload a local directory to a HF Hub repo and return the commit SHA.

    Args:
        local_dir: Local directory to upload. Must exist.
        repo_id: HF Hub repo id (e.g. `"cianfhoghlaim/phishing-distilbert"`).
        commit_message: Commit message for the upload.
        token: HF token. Defaults to `HF_TOKEN` env var.
        repo_type: `"model"` (default), `"dataset"`, or `"space"`.

    Returns:
        The commit SHA of the upload.

    Raises:
        FileNotFoundError: If `local_dir` does not exist.
        ValueError: If no token is provided and `HF_TOKEN` is unset.
    """
    local_dir = Path(local_dir)
    if not local_dir.exists():
        raise FileNotFoundError(f"local_dir does not exist: {local_dir}")

    resolved_token = token or os.getenv("HF_TOKEN")
    if not resolved_token:
        raise ValueError(
            "HF_TOKEN is required (set env var or pass `token=` kwarg). "
            "Create a write token at https://huggingface.co/settings/tokens"
        )

    api = HfApi(token=resolved_token)
    result = api.upload_folder(
        folder_path=str(local_dir),
        repo_id=repo_id,
        repo_type=repo_type,
        commit_message=commit_message,
    )
    return result.oid


__all__ = ["push_model_to_hub"]
