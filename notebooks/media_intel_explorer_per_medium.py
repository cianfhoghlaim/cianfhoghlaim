"""media_intel_explorer_per_medium — the per-medium marimo
notebook.

The L4 Asset Generation surface for the media-intel reference
corpus. Surfaces:

- Per-medium coverage table (Row count per class)
- Sample descriptors
- Per-axis field histograms
- Top 5 most-cited source URLs

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            spec.md § media-intel-corpus Requirement 5
"""
import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        # Media-Intel Explorer — Per-Medium

        The 5-class reference-corpus coverage. Per the
        `media-intel-corpus` spec, every descriptor ships with
        `shippable: false` enforced.

        The 5 classes are:

        - **A — Comics**: the Jonathan Hickman Marvel run
        - **B — Prose**: The Wheel of Time (the 0-pixel control)
        - **C — Animation**: Avatar: The Last Airbender + The
          Legend of Korra + the Aang-film continuity
        - **D — Games**: Hades 1 + 2 + World of Warcraft + Golden
          Sun (GBA) + Pokémon (GB)
        - **E — Official**: NCCA + SEC / examinations.ie + DfE +
          SQA + WJEC + DESC + Wikipedia + CELT + Dúchas

        ## Per-medium row count

        | Class | Row count | Latest descriptor | Top source URL |
        |:--|--:|:--|:--|
        | A — Comics | ? | ? | ? |
        | B — Prose | ? | ? | ? |
        | C — Animation | ? | ? | ? |
        | D — Games | ? | ? | ? |
        | E — Official | ? | ? | ? |
        """
    )
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Per-axis field histograms

        For each of the 7 descriptor axes (power_event,
        visual_grammar, palette, vfx_vocabulary, narrative_beat,
        transferability, provenance), the histogram of the most-
        common values across all 5 classes.
        """
    )
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Top 5 most-cited source URLs

        The 5 URLs that appear most often across all 5 classes
        in the `source_url` field of the
        `media_descriptors_lance` table.
        """
    )
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ## The 7 axes

        Per `media-intel-corpus` Requirement 2 the 7 axes are:

        1. **power_event** — actor, element, source, trigger,
           scale_tier, cost, consequence, counter
        2. **visual_grammar** — composition, panel/shot type,
           motion_lines, camera, silhouette, focal_hierarchy
        3. **palette** — dominant + accent + emissive hex, per-
           element palette, contrast_strategy
        4. **vfx_vocabulary** — particle_class, density, trail_
           behavior, dissipation, light_interaction
        5. **narrative_beat** — arc_position, beat_significance
        6. **transferability** — in_game_mechanic, anam_cost,
           palette_token, particle_effect
        7. **provenance** — rights_holder, licence, derivation_
           class, shippable (ALWAYS false), shippable_art_path

        ## Why "no graphics-from-graphics"

        Per the `media-intel-corpus` design.md § 1.4 the
        descriptor is description-only. The original comic
        panel / animation frame / game screenshot is NEVER
        stored in the shippable asset output. The descriptor's
        `palette` + `vfx_vocabulary` + `visual_grammar` are the
        only things that flow forward to the (future)
        Celtic-MMO design.
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
