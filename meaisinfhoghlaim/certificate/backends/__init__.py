"""meaisinfhoghlaim.certificate.backends — the certificate backends (OSS-first).

Per the 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 change
(Phase 7). The OSS replacement for the GCP-first
``gemini_hackathon.certificate.backends``.

Currently ships:
  - flux_schnell_compositor (TODO: lift from sister repo)
  - fibo_compositor (TODO: lift from sister repo)
  - diffusiongemma_compositor (TODO: lift from sister repo)
  - compositor_base (the common compositor interface)

Phase 7 ships the stdlib-only PNG gradient fallback as the default
backend; the lifted backends arrive in a follow-on commit.
"""
