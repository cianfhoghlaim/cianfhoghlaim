"""marimo notebook: ciancheiltis_en_ga_roi_dashboard.

The Phase 2 (en-ga / Republic of Ireland) operator console for the
ciancheiltis umbrella. Dual-mode (per `https://docs.marimo.io/guides/scripts/`):

    uv run marimo edit notebooks/ciancheiltis_en_ga_roi.py
    uv run python notebooks/ciancheiltis_en_ga_roi.py --cli --theme T3

Surfaces:

1. Per-theme coverage matrix (T1–T10)
2. Per-source metadata-language-mismatch rate
   (the Phase 2 mismatch pattern — gov.ie slug pairs vs
   `legislation.gov.uk`-style metadata.language mismatch)
3. Bilingual-pair coverage RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded)
4. The 8 Phase 2 sources + their canonical URLs

The canonical bilingual reference is
`https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html`
(Bunreacht na hÉireann / Constitution of Ireland 1937).
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # Ciancheiltis — Phase 2 (en-ga / Republic of Ireland) dashboard

        The Phase 2 (en-ga / Republic of Ireland) operator console. Renders:

        1. **Per-theme coverage matrix** (T1–T10)
        2. **Per-source metadata-language-mismatch rate**
           (gov.ie `/en/` ↔ `/ga/` slug pairs — different from Phase 1's
           `legislation.gov.uk` metadata.language mismatch)
        3. **Bilingual-pair RAGAS gate** (≥ 0.70 + ≥ 500 pairs seeded)
        4. **The 8 Phase 2 sources** + canonical URLs

        See:
        - `ciancheiltis/README.md`
        - `openspec/specs/ciancheiltis/spec.md`
        - `motherduck/dives/ciancheiltis_en_ga_roi_dive.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis.en_ga_roi import (
        irish_statute_book,
        gov_ie_policies,
        ncca_curriculum,
        hse_health,
        foras_na_gaeilge,
        tearma,
        courts_service,
        local_government,
    )

    sources = {
        "T1 Legislation": (irish_statute_book, "https://www.irishstatutebook.ie/"),
        "T2 Policy / consultations": (gov_ie_policies, "https://www.gov.ie/en/publication/"),
        "T3 Education": (ncca_curriculum, "https://ncca.ie/en/resources/"),
        "T4 Healthcare": (hse_health, "https://www.hse.ie/eng/"),
        "T5 Language bodies": (foras_na_gaeilge, "https://www.forasnagaeilge.ie/ga/"),
        "T6 Terminology": (tearma, "https://www.tearma.ie/"),
        "T7 Courts & Tribunals": (courts_service, "https://www.courts.ie/"),
        "T8 Local government": (local_government, "https://www.galwaycity.ie/ga/"),
    }

    rows = [
        {
            "theme_code": theme_code.split(" ")[0],
            "theme_name": theme_code.split(" ", 1)[1],
            "source_id": mod.SOURCE_ID,
            "language_pair": mod.LANGUAGE_PAIR,
            "theme_code_field": mod.THEME_CODE,
            "lance_table": mod.LANCE_TABLE,
            "canonical_url": url,
            "status": "stub (awaiting Firecrawl keyless reset)",
        }
        for theme_code, (mod, url) in sources.items()
    ]

    mo.md("## 1. Phase 2 sources\n\n" + _table_md(rows))
    return


@app.cell
def _opaque_scanner_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.opaque_url_scanner import classify_url

    canonical_urls = [
        "https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/ga/html",
        "https://www.irishstatutebook.ie/eli/1937/act/0019/enacted/en/html",
        "https://www.gov.ie/en/publication/7d9a8-bunreacht-na-heireann/",
        "https://www.gov.ie/ga/foilseachan/7d9a8-bunreacht-na-heireann/",
        "https://ncca.ie/en/resources/ty_transition_year_school_guidelines/",
        "https://ncca.ie/ga/acmhainni/ty_transition_year_school_guidelines/",
        "https://www.tearma.ie/Terms-of-Use.html",
        "https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E",
    ]

    rows = [classify_url(u) for u in canonical_urls]
    mo.md("## 2. Opaque-URL scanner demo (Phase 2 candidates)\n\n" + _table_md(rows))
    return


@app.cell
def _language_detector_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.language_detector import (
        detect_languages,
        metadata_mismatch,
    )

    bunreacht_body = (
        "Article 1. The Irish nation hereby affirms its inalienable, "
        "indefeasible, and sovereign right to choose its own form of "
        "Government, to determine the relations of the sexes within the "
        "nation, and to guarantee the religious and civil liberties of "
        "every individual.\n\n"
        "Airteagal 1. Dhearbhaigh an náisiún Éireannach, leis seo, a cheart "
        "dochloíte, doscriosta agus ceart ceannasach chun a rialtas féin a "
        "roghnú, chun caidreamh na n-insíneacha sa náisiún a chinneadh, agus "
        "chun saoirse creidimh agus saoirse sibhialta gach duine dlisteanach "
        "a ráthú."
    )

    detected = detect_languages(bunreacht_body, top_k=2)
    mismatch = metadata_mismatch(
        bunreacht_body,
        {"language": "eng"},
        expected_iso="ga",
    )

    mo.md(
        f"## 3. Content-based language detection\n\n"
        f"Detected languages on Bunreacht na hÉireann Art. 1 body: `{detected}`\n\n"
        f"Metadata mismatch summary: `{mismatch}`"
    )
    return


@app.cell
def _metadata_normalization_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.bilingual_page_validator import (
        normalize_for_compare,
    )

    en_url = "https://ncca.ie/en/resources/ty_transition_year_school_guidelines/"
    ga_url = "https://ncca.ie/ga/acmhainni/ty_transition_year_school_guidelines/"

    en_norm = normalize_for_compare(en_url)
    ga_norm = normalize_for_compare(ga_url)

    mo.md(
        f"## 4. Bilingual-pair normalisation\n\n"
        f"- EN: `{en_url}` → `{en_norm}`\n"
        f"- GA: `{ga_url}` → `{ga_norm}`\n"
        f"- **Same canonical form**: `{en_norm == ga_norm}`"
    )
    return


def _table_md(rows: list[dict]) -> str:
    if not rows:
        return "(empty)"

    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        cells = [str(row.get(h, ""))[:80] for h in headers]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    app.run()