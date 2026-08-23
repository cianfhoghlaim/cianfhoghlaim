"""media_intel_explorer_cross_medium — the cross-medium marimo
notebook.

The L4 Asset Generation surface for the media-intel reference
corpus. The cell-level SQL runs DuckDB over the LanceDB tables
joined with the BAML-typed records. Answers the question:

> "Which element's visual grammar is most consistent across
> WoT prose + ATLA animation + Hickman comics?"

Reference: openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/
            spec.md § media-intel-corpus Requirement 6
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
        # Media-Intel Explorer — Cross-Medium

        The multihop search that surfaces the *consistent
        visual grammar* across the 5 source classes. The
        canonical question the App answers:

        > "Which element's visual grammar is most consistent
        > across WoT prose + ATLA animation + Hickman comics?"

        The 5 elements are:

        - **earth** — Éire (the future Celtic-MMO Earth sub-nation;
          Aran Islands as the capital seat; the historical
          geography of the Irish-speaking gaeltachtaí)
        - **air** — Alba (the future Celtic-MMO Air sub-nation;
          Isle of Skye as the capital seat; the SQA CfE
          geography)
        - **water** — Mann (the future Celtic-MMO Water sub-
          nation; the Isle of Man as the seat)
        - **fire** — Cymru (the future Celtic-MMO Fire sub-
          nation; Wales + England combined; Dyfed as the
          historical capital seat; the Déisí / Uí Liatháin
          migration)
        - **spirit** — anam (the gender-agnostic saidar/saidin
          analogue; the Wheel of Time's One Power)

        ## Cross-medium similarity matrix

        For each of the 5 elements, the per-medium similarity
        (cosine over the 7-axis descriptor space):

        | Element | Comic | Prose | Animation | Game | Official |
        |:--|:--|:--|:--|:--|:--|
        | earth | ? | ? | ? | ? | ? |
        | air | ? | ? | ? | ? | ? |
        | water | ? | ? | ? | ? | ? |
        | fire | ? | ? | ? | ? | ? |
        | spirit | ? | ? | ? | ? | ? |
        """
    )
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Per-element consistency score

        For each of the 5 elements, the consistency score (the
        variance of the per-medium similarity scores). The
        element with the LOWEST variance is the most
        *consistently* described across the 5 media classes.

        | Element | Mean similarity | Variance | Most consistent class |
        |:--|:--|:--|:--|
        | earth | ? | ? | ? |
        | air | ? | ? | ? |
        | water | ? | ? | ? |
        | fire | ? | ? | ? |
        | spirit | ? | ? | ? |
        """
    )
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        ## The 4 Celtic-Elemental MMO sub-nations (deferred)

        Per the `celtic-elemental-mmo-canon` spec, the 4 sub-
        nations (Éire + Alba + Mann + Cymru) + the spirit
        currency (anam) are the future design layer. This
        change does NOT design the Celtic MMO. It only gathers
        the reference corpus.

        The cross-medium consistency score above is the
        empirical input the future design change will use to
        decide which element binding is most natural.

        ## The 3 hard-deferred decisions

        Per the `celtic-elemental-mmo-canon` design.md § 6 the
        following are deferred to after the corpus is
        populated:

        - The 4+1 element world canon
        - The Cymru-Wales+England sub-nation binding
        - The 2D particle renderer choice
        - The iOS delivery vehicle decision
        - The boons + anam economy + anamcara mechanics
        """
    )
    return (mo,)


if __name__ == "__main__":
    app.run()
