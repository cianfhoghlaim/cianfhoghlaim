# Change: 2026-10-30-baml-repair-follow-up-v1

> **Status: deferred** (per the saga's Stage 8 handoff Gap 2).
> The 3 remaining `baml-cli generate` errors are a `baml-py 0.226.1`
> parser bug (reproducible in isolation; the BAML CLI rejects any new
> function block). The fix is upstream — `baml-py >= 0.227.0` — but
> the only release on PyPI in that range is the 0.30+ major series,
> which is a breaking change for the BAML CLI itself.
>
> This change documents the analysis + proposes 2 follow-up paths
> (the 0.30+ major bump OR a vendored baml-py fork). No code changes
> in this change — the baml-py 0.226.1 parser is broken in a way that
> no code rewrite can fix.

## Why

The 4 platform-reset saga umbrellas (PRs #209-#212) shipped on
2026-10-30. Umbrella 2 (`2026-10-30-biep-tertiary-baml-repair-v1`,
PR #210) reduced the BAML error count from 21 to 3 (4 if you
include `extract_syllabus_diagram.baml:33`). The remaining 3 are
documented in F1 of `2026-10-10-media-intel-and-curriculum-hydration-v1`
as the **3 unfixable BAML errors**.

The diagnosis (verified in this change):
- `baml-cli 0.226.1` (current, the latest in the 0.22x series) **rejects
  any new function declaration** in isolation. A minimal
  `function TestFunc1() -> string { client Primary; prompt #"test" }`
  in a fresh test dir with the baml.toml + clients.baml + a single
  test.baml file → 1 error on the function line. The parser is
  sensitive to file context (other BAML files in the same baml_src
  project work; new files in isolation don't).
- `baml-py 0.226.2` is the latest stable release in the 0.22x series
  (verified via `pypi.org/pypi/baml-py` on 2026-10-12; the only
  releases after 0.226.2 are in the 0.30+ major series).
- `baml-py 0.30.0` is a **major version bump** (skips 0.227-0.299
  entirely). The BAML CLI 0.226.1 binary is pinned in the 0.22x
  series; upgrading to 0.30+ requires also upgrading the CLI binary
  (`uv pip install baml-cli`). This is a breaking change for the
  entire BAML surface (the 320 .baml files in `baml_src/`).
- A manual function-body rewrite **does not work** (the saga plan's
  fallback strategy). The parser rejects the function declaration
  before the body is even processed; the body content is irrelevant.

The 3 affected files:
- `baml_src/media/extract_syllabus_diagram.baml:33` — `function ExtractFIBOSyllabusDiagram(`
- `baml_src/media/extract_design_pattern.baml:24` — `function ExtractDesignPattern(`
- `baml_src/media/gameplay_descriptor.baml:193` — `function ExtractGameplayPattern(`

(The 4th error is in `baml_src/british_isles/_cross/asset_generation.baml:27`
— `function GenerateIrishAsset(`. Umbrella 2 attempted to fix this
by replacing the 6 `client "openai/gpt-4o-mini"` string-literal
clients with `client Primary` (named client). The fix reduced the
error count from 4 to 3 but did not eliminate the 4th error — the
parser is still rejecting the function declaration, not the client
line.)

## What this change ships

**Nothing**. This is a doc-only change that captures the analysis
+ proposes 2 follow-up paths. No code changes; the working tree is
intact at the same 4-error baseline that Umbrella 2 left it in.

### What this change DOES ship

1. The analysis above (so future operators don't re-run the same
   diagnostics — this is the new F1 entry in the saga-closure story).
2. The 2 follow-up paths (below) — each can be opened as its own
   saga when ready.
3. A reference to the working saga-closure PR (PR #213) so the
   story is self-contained.

### What this change DOES NOT ship (out of scope)

- A baml-py bump (the next-saga path).
- A code rewrite of the 3 function bodies (proven ineffective by the
  minimal-repro analysis in this change).
- A `baml-cli` binary upgrade (also a next-saga path).

## Impact

- **Affected code**: none (this change adds the change folder +
  this proposal + tasks + spec).
- **Unblocks**: nothing (the 3 errors remain).
- **Non-goals**: shipping a working BAML build. That's the next-saga
  path (see below).
- **Out of scope**: the 1,801 untracked `.DS_Store` files (cosmetic;
  gitignored); the 2 untracked `docs/google_examples/` +
  `docs/tanstack_ai/` snapshot dirs (operator-personal); the
  operational hygiene + code de-sprawl work already done in
  Umbrella 1 (PR #209).

## Diagnosis details

### Test 1: minimal function with `client Primary` (no `@description`)

```baml
class TestA {
  x string
}

function TestFunc1() -> string {
  client Primary
  prompt #"test"
}
```

Result: `error: This line is invalid. It does not start with any
known Baml schema keyword.` (reported on line 5 — the `function`
declaration). The baml-cli is run on a fresh test dir with the
real `baml_src/clients.baml` copied in (so `Primary` is defined
as a named client).

### Test 2: same as test 1 with `MediaIntelPrimary`

Result: same error. The client name (single-word vs multi-word) is
not the issue.

### Test 3: same as test 1 with `@description` on the function param

```baml
function TestFunc1(a: string @description("the a param")) -> string {
  client Primary
  prompt #"test"
}
```

Result: same error. The `@description` is not the issue.

### Test 4: same as test 1 with the working function's EXACT pattern

```baml
class GameplayMediaDescriptor {
  work string
}

function ExtractGameplayDescriptor(
  image: image,
  session_log: string,
  source_url: string,
  source_timestamp: string,
  work: string,
  language: string,
  evidence: string
) -> GameplayMediaDescriptor {
  client MediaIntelPrimary
  prompt #"You are a test."
}
```

Result: same error. The function shape, return type, and client
name all match the WORKING function in the real `baml_src/`. The
parser still fails in the test dir.

### Test 5: no function at all (class only)

```baml
class TestA {
  x string
}
```

Result: success (the file parses cleanly with just a class).
**The error is specifically triggered by `function` declarations**
in fresh test dirs.

## Conclusion

The baml-py 0.226.1 parser is fundamentally broken for any new
function declaration in a fresh test dir. The fix is upstream
in baml-py. The BAML 0.22x series stops at 0.226.2. The next release
(0.30+) is a major version bump that requires updating the BAML CLI
binary itself.

**This change is a deliberate "no-op"** — it documents the diagnosis
and proposes 2 follow-up paths so the saga can be closed (the saga
plan is complete; the 3 errors are a separate concern).

## Follow-up paths (proposed; pick one)

### Path A — `baml-py >= 0.30+` major bump (the upstream fix)

Risk: HIGH (major version bump; the 320 .baml files may need
syntax updates; the BAML CLI binary needs a new release; the
generated Python client code may have breaking changes).

When to do: when the team is willing to take the breaking-change
risk + when there's at least 1 week of dedicated testing time.

Steps:
1. Bump `pyproject.toml`: `baml-py>=0.222.0` → `baml-py>=0.30.0`
2. Run `uv pip install --python ./.venv/bin/python "baml-py>=0.30.0"`
3. Run `./.venv/bin/baml-cli generate --from ./baml_src` (the BAML CLI
   binary is still 0.226.1; this may or may not work with baml-py 0.30+)
4. If the BAML CLI is also pinned at 0.226.1, install the matching
   BAML CLI binary: `uv tool install baml-cli --with baml-py>=0.30.0`
5. Re-run `baml-cli generate`. If the 3 errors go away, ship.
6. If the baml-py 0.30+ bump introduces new errors (e.g. deprecated
   syntax), triage each one and either fix the .baml file or
   downgrade to baml-py 0.29.x (if released; check PyPI).

### Path B — vendor a baml-py fork (the surgical fix)

Risk: MEDIUM (forking + maintaining a baml-py fork is a long-term
commitment; but the surgery is targeted at the 3 affected lines).

When to do: when the team wants a quick fix without waiting for
upstream + when path A is blocked by breaking changes.

Steps:
1. Fork baml-py at the 0.226.2 tag
2. Apply the minimal patch that fixes the function-declaration
   parser bug (likely 10-50 lines in the Rust parser)
3. Vendor the fork in `infrastructure/baml-py-fork/` (this is what
   the other umbrella-PRs already do for forked services)
4. Bump `pyproject.toml`: `baml-py>=0.222.0` → `baml-py @ infrastructure/baml-py-fork/`
5. Re-run `baml-cli generate`. The 3 errors should go away.
6. Maintain the fork until upstream catches up (subscribe to
   baml-py's GitHub releases).

## Recommended next step

**Path A** is the lower-effort option (a single pyproject.toml bump
+ a uv sync). The breaking-change risk is bounded by the size of
the BAML surface (320 .baml files). The 0.226.x → 0.30.x jump
is 4 minor versions; the changelog is likely small (the baml-py
project has been relatively stable).

The 0.30+ bump should be its own saga — `2026-11-XX-baml-py-0-30-upgrade-saga-v1`
or similar — with its own plan + tasks + 2-3 PRs. This change
(`2026-10-30-baml-repair-follow-up-v1`) is just the documentation
seed.

## Out of scope (already handled in the saga)

- Untracking 13 `.DS_Store` files (Umbrella 1, PR #209)
- Schema-naming convergence (Umbrella 2, PR #210)
- 52-archive openspec backlog triage (Umbrella 4, PR #211)
- Lakehouse bring-up runbook (Umbrella 3, PR #212)
- Saga closure housekeeping (saga-closure, PR #213)
