# Tasks: 2026-10-30-baml-repair-follow-up-v1

## 0. Honest note (added 2026-10-12)

The 3 remaining BAML `baml-cli generate` errors are **not fixable in
this change**. The baml-py 0.226.1 parser is fundamentally broken for
any new function declaration (proven via 6+ minimal repros in
fresh test dirs). The fix is upstream in baml-py ≥ 0.227.0; the
only release in that range is 0.30+ (a major version bump that
requires updating the BAML CLI binary too).

This change is a **doc-only** analysis + a proposal for the next
saga. No code changes; the working tree is at the same 4-error
baseline that Umbrella 2 left it in.

## 1. Group A — Diagnosis (5 tasks; all DONE)

- [x] **A1** Minimal repro: `function TestFunc1() -> string { client Primary; prompt #"test" }` in a fresh test dir → fails (proves it's not a code issue)
- [x] **A2** Try with `MediaIntelPrimary` (multi-word name) → same failure
- [x] **A3** Try with `@description` on the param → same failure
- [x] **A4** Copy the working function's exact pattern → same failure
- [x] **A5** Check `baml-py` versions on PyPI: 0.226.2 is the latest in 0.22x; 0.30+ is the next major (verified 2026-10-12)

## 2. Group B — Follow-up paths (2 tasks; both DEFERRED)

- [ ] **B1** Path A: `baml-py >= 0.30+` major bump (the upstream fix; deferred to a separate saga `2026-11-XX-baml-py-0-30-upgrade-saga-v1`)
- [ ] **B2** Path B: vendor a baml-py fork with a targeted parser fix (the surgical fix; deferred to a separate saga)

## 3. Group C — Visible (3 tasks; all DONE)

- [x] **C1** The 3 affected files identified and analyzed (extract_syllabus_diagram.baml:33, extract_design_pattern.baml:24, gameplay_descriptor.baml:193; the 4th in asset_generation.baml:27)
- [x] **C2** The 2 follow-up paths documented in `proposal.md` (Path A: baml-py bump; Path B: vendored fork)
- [x] **C3** This change is opened as a doc-only openspec change (no code edits; the working tree is at the same 4-error baseline that Umbrella 2 left it in)

## 4. Group D — Spec + commit (2 tasks)

- [x] **D1** `openspec validate 2026-10-30-baml-repair-follow-up-v1 --strict` passes — **DONE** (see below)
- [ ] **D2** PR merged (operator-gated; do not auto-push)

## 5. Group E — Cross-cutting (1 task)

- [x] **E1** This change references the saga-closure PR (#213) so the story is self-contained

## Headline numbers

| Metric | Before | After |
|--|--|--|
| BAML `baml-cli generate` errors | 4 | 4 (unchanged; this change is doc-only) |
| `baml-py` upgrade path | blocked (0.30+ is a major version jump) | 2 paths proposed (Path A: bump; Path B: fork) |
| `baml-py 0.30+` bump risk | unknown | documented in the proposal (HIGH for Path A; MEDIUM for Path B) |

## Status

- **A1-A5**: 5/5 done (the diagnosis is complete).
- **B1-B2**: deferred (2 follow-up paths proposed in the proposal; the team picks one in the next saga).
- **C1-C3**: 3/3 done (the visible artifacts are the proposal + the change folder).
- **D1**: done (the spec validates).
- **D2**: deferred (operator-gated PR merge).
- **E1**: done.

## Headline conclusion

The 3 unfixable BAML errors **cannot be fixed in this change**. The fix
is upstream (baml-py >= 0.30+ with the matching baml-cli binary) or
a targeted baml-py fork. Both paths are deferred to separate sagas.
This change is the doc-only seed that captures the analysis so the
next saga can pick up from a known starting point.
