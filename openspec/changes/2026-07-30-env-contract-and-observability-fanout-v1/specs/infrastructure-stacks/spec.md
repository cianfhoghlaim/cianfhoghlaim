# Spec delta: `infrastructure-stacks`

This delta is part of the openspec change
`2026-07-30-env-contract-and-observability-fanout-v1`. It adds 1
requirement that pins the canonical Infisical URI grammar and the
grammar-mixed-stack CI gate.

## ADDED Requirements

### Requirement: Canonical Infisical URI grammar

Every `bonneagar/stacks/<name>/secrets.env` file MUST use one of two
Infisical URI forms, and MUST NOT mix both forms in the same file:

1. **Bare form (canonical, post-v4)**: `KEY=infisical://dev-baile/<svc>/<key>`
2. **Jinja-wrapped form (legacy, accepted by the bons-locket-shim v0.2.0)**:
   `KEY={{ infisical:///KEY?path=/<svc> }}`

The two forms parse through different code paths:

- The bare form is parsed by `scripts/init-vault.ts` (which pushes local
  `.env` values into the Infisical vault).
- The Jinja form is parsed by `bonneagar/scripts/cianfhoghlaim-locket-shim.py`
  (which the Locket sidecar uses at container runtime).

A stack whose `secrets.env` mixes both forms is a silent integration break:
the shim sees one half, the seeder sees the other half, the operator sees
neither.

#### Scenario: stack-doctor --strict --check-grammar reports clean

```
$ mise run stack-doctor:strict
[lakehouse/secrets.env]    ✓ 7 bare + 0 Jinja (canonical)
[litellm/secrets.env]      ✓ 11 bare + 0 Jinja (canonical)
[openclaw/secrets.env]     ✓ 3 bare + 0 Jinja (canonical)
[openchamber/secrets.env]  ⚠ 5 Jinja + 0 bare (legacy, accepted but warning)
...
```

#### Scenario: a mixed-grammar secrets.env fails CI

```
$ mise run stack-doctor:strict
[tuatha/secrets.env]       ✗ MIXED: 4 bare + 2 Jinja (CI GATE FAILURE)
  bare line 12:  TUATH_OPENAI_API_KEY=infisical://dev-baile/tuatha/openai_api_key
  jinja line 18: TUATH_LANGFUSE_HOST={{ infisical:///langfuse/host }}
  → fix: pick one grammar; the canonical form is bare.
exit 1
```

#### Scenario: migration helper sweeps Jinja → bare

```
$ bun run scripts/normalize-infisical-uri.ts --apply
[lakehouse/secrets.env]    7 Jinja → 7 bare  (committed)
[litellm/secrets.env]      11 Jinja → 11 bare (committed)
[tuatha/secrets.env]       6 Jinja → 6 bare (committed)
...
synced 24 files in 4.2s
```

### Requirement: stack-doctor:strict CI gate

The `mise run stack-doctor:strict` task MUST be wired into CI and MUST
fail any merge that introduces a mixed-grammar `secrets.env` or a
`secrets.env` without any `infisical://` URI at all.

The task wraps `bun run scripts/stack-doctor.sh --strict --check-grammar`
which:

1. Lists every `bonneagar/stacks/<name>/secrets.env`
2. For each file, counts bare-form lines + Jinja-form lines + mixed
   detection
3. Exits non-zero if any stack has mixed grammar
4. Exits non-zero if any stack has zero URI lines (regression)
5. Prints a single-line summary per stack

#### Scenario: pre-commit hook blocks a mixed-grammar file

```
$ git commit -m "feat(tuatha): add TUATH_LANGFUSE_HOST env"
> mise run stack-doctor:strict
[tuatha/secrets.env]       ✗ MIXED: 4 bare + 2 Jinja (CI GATE FAILURE)
hook: pre-commit exited with code 1
```

## Why this matters

Two parallel URI grammars across 86 `secrets.env` files is the
single biggest silent-integration-break risk in the IaC surface.
Pinning one canonical form + a CI gate that prevents mixed files
eliminates the risk class entirely.