# Decision: Secret resolution chain

**Date:** 2026-08-23

**Context.** The UoG exam-paper pipeline needs the student's Campus
Identity credentials to drive the Playwright persistent context. We
have three viable backends in the wider platform:

1. Self-hosted Infisical (`~/.infisical` is installed on the workstation).
2. Local `.env` (already in use for the SEC exam browser scraper).
3. 1Password CLI (`.op.env` is shipped in the repository; LOCKET is
   available system-wide).

**Decided.**

- **Primary**: Self-hosted Infisical.
- **Fallback**: local `.env` (default `.env` ships with a placeholder
  `OOG_STUDENT_PASSWORD=fixture-only` so CI runners see fixture-only data).
- **Documented only**: 1Password CLI — `op read` is NOT invoked from the
  runner, but a cloner's swap-in snippet is documented in
  `design/auth-credential-priority-chain.md`.

**Rationale.** Matches the platform's existing VLM-server chain
(self-hosted → local LLM → commercial remote API). Both chains prefer
self-hosted first, local fallback second. 1Password is mentioned in
docs because LOCKET interop makes it a natural choice for end users,
but it is no more secure than Infisical for a single-user thesis
pipeline and adds an external runtime dependency to the runner image.

**Consequences.**

- The `Sec*` extraction code does not need to know which backend won.
- CI skips with a single `MaterializeResult` row, no Playwright launch.
- Local `.env` is **not** checked in to version control (already
  `.gitignore`'d by the platform `.gitignore`).
