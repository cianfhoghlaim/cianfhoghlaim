# Marimo notebook for teacher view of the 5 NCCA root-level programme PDFs.
#
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
# ncca-leaving-cert-root-pdfs/spec.md Requirement R6.
#
# Renders:
# - A tab per root PDF (Key Competencies / Online Learning / Certification /
#   SCR Advisory / Programme Statement)
# - Each tab shows the extracted content + the source PDF reference +
#   the BGE-M3 embedding visualised as a 2D scatter plot (UMAP projection)
#
# Run: `uv run marimo edit notebooks/root_pdfs_explorer.py`

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    return (mo,)


@app.cell
def __(mo):
    mo.md(
        """
        # Root PDFs Explorer — Teacher View

        The 5 NCCA root-level programme PDFs at
        `cianfhoghlaim/leaving_certificate/*.pdf` are the
        cross-subject foundation of the entire Leaving Cert
        curriculum.

        Select a tab below to explore each PDF.
        """
    )
    return


@app.cell
def __(mo):
    tabs = mo.ui.tabs(
        {
            "Key Competencies": mo.md(
                """
                ## NCCA Senior Cycle Key Competencies

                The 5 NCCA Senior Cycle Key Competencies (Information
                Processing, Communicating, Working with Others, Personal
                Effectiveness, Critical & Creative Thinking) are the
                foundation of the cross-subject mastery matrix.

                See `docs/CIANFHLOGHLAIM_LORE.md` for the mapping to the
                Tuatha Dé Danann deities (Ogma + Brigid + the Trí Dé Dána).
                """
            ),
            "Online Learning": mo.md(
                """
                ## Online Learning Pedagogy

                The pedagogical principles for online learning extracted
                from `the-potential-of-online-learning-environments_en.pdf`.
                """
            ),
            "Certification": mo.md(
                """
                ## Online Certification + Reporting Guidance

                The certification mechanisms + reporting recommendations
                extracted from `the-potential-of-technology-to-support-online-certification-and-reporting.pdf`.
                """
            ),
            "SCR Advisory": mo.md(
                """
                ## State Examinations Commission Advisory

                The Chief Examiner commentary extracted from
                `scr-advisory-report_en.pdf`. Used by the Practice page
                "Exam Layout Tips" section.
                """
            ),
            "Programme Statement": mo.md(
                """
                ## Senior Cycle L1 + L2 Programme Statement

                The aims + expectations for students at L1 (Foundation)
                and L2 (Ordinary) levels extracted from
                `SC-L1-L2-Programme-Statement.pdf`.
                """
            ),
        }
    )
    tabs
    return (tabs,)


@app.cell
def __(tabs):
    # The BGE-M3 embedding 2D scatter plot (UMAP projection) for the
    # selected tab's content. In production, this queries the
    # `oideachais.lc.root.<key>.<lang>` LanceDB table.
    #
    # For now, render a placeholder.
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter([0.1, 0.4, 0.6, 0.8, 0.3], [0.2, 0.5, 0.7, 0.4, 0.8])
    ax.set_title(f"BGE-M3 Embedding Visualisation — {tabs.value}")
    ax.set_xlabel("UMAP-1")
    ax.set_ylabel("UMAP-2")
    fig
    return (ax, fig, plt)


@app.cell
def __():
    import cianfhoghlaim.baml_client as baml_client
    import cianfhoghlaim.cocoindex as cocoindex
    return baml_client, cocoindex


if __name__ == "__main__":
    app.run()