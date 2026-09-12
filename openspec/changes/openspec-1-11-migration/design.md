## Context

The repo ran `@fission-ai/openspec@1.4.1` while upstream had shipped
1.5.0 through 1.11.0. `openspec/AGENTS.md` and
`.agents/skills/openspec/SKILL.md` both described a "legacy spec-driven
vs experimental OPSX schema" choice and stated OPSX was "not adopted...
migration would require re-archiving all 78 pending changes." Verified
inventory (`openspec list`, `openspec list --specs`, and a directory
count of `openspec/changes/archive/`) on 2026-09-02 found 36 pending
changes, 102 specs, and 344 archived changes — the docs were stale.
Under openspec 1.11, `openspec doctor` also requires a
project-local `openspec/config.yaml` and the `--strict` validation
surfaces new failure classes (zero-delta changes, TBD-Purpose
placeholders).

## Goals / Non-Goals

**Goals:**
- Bring the installed CLI, the repo's own documentation, and the
  `openspec` skill into agreement with each other and with verified
  reality.
- Establish the `.openspec.yaml` convention for new changes.
- Correct the OPSX framing so it stops discouraging `/opsx:*` adoption
  for a reason that doesn't hold.

**Non-Goals:**
- This change does NOT convert the 36 existing pending changes to the
  new format — that is the scope of the (separately batched) topic-batch
  conversion changes.
- This change does NOT fix the 30 TBD-Purpose specs beyond the ones
  already resolved as a side effect of `spec-registry-dedup`.
- This change does NOT flip `openspec config profile` to `custom` (the
  expanded `/opsx:*` set) — that's a separate, reviewed step.

## Decisions

**Upgrade via `bun add -g` rather than pinning a project-local install.**
The existing install was already global; this change continues that
pattern rather than introducing a project-local `devDependencies` entry,
since the CLI has no other project-local footprint.

**Undated kebab IDs for new changes, no retroactive rename.** Upstream's
own convention (date applied at archive, not at creation) is the
simplest way to stop future-dated changes from recurring, and costs
nothing to adopt going forward. Renaming the existing 36+344 IDs would
touch every cross-reference in `openspec/AGENTS.md` and any script that
greps for a dated ID pattern — not worth the blast radius for a purely
cosmetic gain on history.

**`skip_specs: true` decided per-change, not blanket-applied.** Some
zero-delta changes genuinely need `retire_capabilities: true` instead
of (or in addition to) `skip_specs: true`. Each zero-delta change gets
its own one-line check during implementation, not an automated pass.

## Risks / Trade-offs

- [Risk] `openspec update` (not run by this change) could silently
  rewrite `openspec/AGENTS.md` in a way that conflicts with this
  change's own edits to that file → Mitigation: this change edits
  `openspec/AGENTS.md` directly and by hand; `openspec update` is
  explicitly deferred to a future, separately reviewed change.
- [Risk] Contributors mid-flight on an existing dated-ID change might
  be confused by new changes appearing undated → Mitigation: the skill
  and AGENTS.md both state the convention applies to new changes only,
  with the reasoning inline, not just the rule.
- [Trade-off] Leaving 36 existing dated IDs unrenamed means the repo
  permanently has two ID shapes in `openspec/changes/` (dated legacy,
  undated new) → Accepted: renaming carries higher risk (broken
  cross-references) than the readability cost of two shapes coexisting.

## Open Questions

- Should `openspec config profile custom` (the 9-command `/opsx:*`
  expanded set) be adopted at all? The skill currently recommends
  staying on `core`; flipping to `custom` rewrites per-tool skill
  files and warrants a separate, reviewed change.