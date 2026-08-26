"""tuatha_media_intel.ingestors — the 4 CocoIndex v1 ingestor Apps.

Apps:
  - hades_boons_app    →  cianfhoghlaim.tuatha.hades.boons
  - comic_particles_app →  cianfhoghlaim.tuatha.comic.particles
  - gba_magic_app      →  cianfhoghlaim.tuatha.gba.magic
  - anam_particles_app →  cianfhoghlaim.tuatha.anam_particles (the cross-source join)

All four share `_shared/shared_lifespan` + `LANCE_DB` + `EMBEDDER`
per the BIEP v3 conformance (R1-R4).
"""
