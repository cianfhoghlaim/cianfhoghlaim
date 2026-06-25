## Why

The current feedback loop between projects → openspec → skills is
informal: the quadrant `AGENTS.md` files have a "Related skills"
section that lists skills by name, but there is no formal
mechanism for the project / openspec change to update the
canonical skill (or vice versa).

The result:

- A new openspec capability is added; the corresponding
  quadrant `AGENTS.md` is not updated.
- A skill is updated for a 2026-06 package refresh (e.g. the
  cocoindex v1.0.1–1.0.7 update); the corresponding quadrant
  `AGENTS.md` and the openspec `Capability Specs` table are not
  updated.
- A project status changes (e.g. a DLT source is now wired with
  a Dagster asset per C4.1); the corresponding
  `sruth/oideachais/STATUS.md` is not updated.

The 3 new rules in this change close the loop:

1. **When an openspec change is archived**, the canonical
   skill (if any) gets a "Post-archive update" note in its
   "## Pair this skill with" cross-reference table (or a new
   "## Recent changes" section at the top).
2. **When a project changes a BAML extraction / DLT source /
   Dagster asset**, the corresponding skill
   (e.g. `baml/SKILL.md`, `dlt/SKILL.md`, `dagster/SKILL.md`)
   gets a 1-line addition to its "When to use this skill"
   section (or a "KCG examples" appendix).
3. **When a project's `STATUS.md` / `REFACTORING.md` /
   README.md changes**, the corresponding
   `data-engineering-pipeline-documentation/SKILL.md` gets a
   link to the new content.

The 2 cross-cutting rules from the consolidation work that
complete the loop:

4. **Each quadrant `AGENTS.md` "Related skills" section MUST
   reference only the skills used by that quadrant.** The
   pre-consolidation list was the same 12 skills in all 4
   quadrants; post-consolidation, each quadrant's list is
   tailored to its actual skills.
5. **Each openspec spec, when archived, points at the
   canonical skill** (the "Implementation reference" line in
   the archived change's `proposal.md`).

## What changes

- 2 new Requirements to the `infrastructure-stacks` spec
  (the formal feedback-loop rules)
- 1 MODIFIED Requirement to the `agent-memory-systems` spec
  (the post-archive note rule, captured earlier in D1)
- 2 new sections appended to each quadrant's `AGENTS.md`
  ("Feedback loop" + "Related skills (quadrant-specific)")
