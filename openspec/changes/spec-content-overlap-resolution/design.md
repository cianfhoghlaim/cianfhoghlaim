## Context

The 5 deeper content overlaps (3 oideachais-* / cianfhoghlaim-*
pairs, 1 oideachais-* single-requirement retirement marker, 1
versioned trilogy collapse) were deferred from `spec-registry-dedup`
because each required reading the actual spec.md files to determine
whether the canonical already covered the oideachais-side's
requirement. This change does that read and consolidates.

## Goals / Non-Goals

**Goals:**
- Consolidate the 5 pairs into one canonical owner each.
- Preserve any contract the canonical doesn't already own by
  ADDing it to the canonical before retiring the losing side.

**Non-Goals:**
- This change does NOT resolve the 3 simple retirement markers
  (those are `spec-registry-dedup`'s scope).
- This change does NOT introduce new requirements — every ADDED
  Requirement here is content already owned by the losing spec.

## Decisions

**For each pair, the canonical owner is the cianfhoghlaim-* /
british-isles-education-pipeline side.** This is the longer spec
with the deeper integration surface (Dagster + BAML + CocoIndex +
marimo). The oideachais-* side is a regional marker; the
cianfhoghlaim-* side is the canonical.

**For pair 4 (oideachais-cognify-knowledge-graph), Req 1 stays.**
The "Phase 1 complete — 9 requirements all functional end-to-end"
requirement was already a deliberate retirement marker; the change
archives the other 3 and keeps this one as the retirement signal.

**For pair 5, -v3 is fully retired** (not just reduced). The v1 +
v2 + v3 trilogy was an intentional structure where -v3 was a
milestone tracker rather than a permanent capability; with all 21
reqs now consolidated into the v1 spec, -v3 has no remaining
content.

## Risks / Trade-offs

- [Risk] Adding requirements to a canonical that's already 54-1701
  lines makes review harder → Mitigation: each ADDED Requirement is
  small (1-3 scenarios), and is direct content from the losing spec
  (no new content is invented).
- [Risk] Cross-reference stub requirements on the oideachais side
  (e.g. "Cross-references section must list X") are arguably not
  requirements at all (they're metadata conventions) → Mitigation:
  consolidated into a single new canonical requirement
  ("Cross-references section must enumerate the regional pipelines")
  rather than 1:1 copying each stub.

## Migration Plan

1. The 5 losing specs each lose 1-21 requirements (see the REMOVED
   sections).
2. After archive, the 5 losing specs each exist as single-requirement
   retirement markers (the canonical owner is named in the marker).
3. `openspec list --specs` SHALL drop from 102 to 97.