---
name: retro-gameplay
description: Legacy retro-game design-pattern tier (Number Munchers → Golden Sun → Hades) — kept as the "where we came from" homage reference; canonical surface lives at [`.agents/skills/media-intel/SKILL.md`](../media-intel/SKILL.md). Load only for libretro capture details or the pre-2026-10-10 retro extractor API.
location: .agents/skills/retro-gameplay/SKILL.md
---

# Retro Gameplay (legacy — see media-intel)

The retro-game tier was broadened on **2026-10-10** by the
`2026-10-10-media-intel-and-curriculum-hydration-v1` saga change:

- The cross-media **media-intel** library (Hades / Avatar: The Last
  Airbender / X-Men Hickman / Wheel of Time) became the canonical
  inspiration surface.
- The retro entries (Number Munchers, Golden Sun) remain in
  `MEDIA_LIBRARY` at `agents/adk/tools/media_library.py` with
  `media_class = "retro"` and `artifact = True`.
- The libretro capture paths and the pre-existing
  `agents/adk/tools/retro_capture.py` (if present in the working
  tree) are retained for the legacy `rom_sha256` placeholders
  (`deadbeef000{1..6}`).

**For the canonical cross-media + per-chapter + curriculum
hydration surface, load
[`.agents/skills/media-intel/SKILL.md`](../media-intel/SKILL.md).**

Upstream sources:

- [`openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md`](../../openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md)
  — the saga (Plans 1, 2, 2b, 2.5, 3, 3.5, 4, 5)
- [`openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/`](../../openspec/changes/2026-10-10-media-intel-and-curriculum-hydration-v1/)
  — the umbrella change
