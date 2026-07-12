"""CI subpackage — code-only utilities for the cianfhoghlaim CI surface.

Stacks in `bonneagar/stacks/ci/` import modules from this
subpackage. The ops (Dockerfile, compose, blueprint, sidecar,
secrets.env, pangolin.yaml, .env.example) live in
`bonneagar/stacks/ci/<name>/`.

This subpackage is intentionally thin: it contains only
Python code. No Docker, no compose, no Pangolin, no
Infisical — those are the ops side (in bonneagar).

See `docs/stacks/ci/` for the per-stack documentation.
"""
