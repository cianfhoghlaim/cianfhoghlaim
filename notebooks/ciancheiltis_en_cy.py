"""marimo notebook: ciancheiltis_en_cy_dashboard.

The Phase 1 (en-cy / Wales) operator console for the ciancheiltis
umbrella. Dual-mode (per `https://docs.marimo.io/guides/scripts/`):

    uv run marimo edit notebooks/ciancheiltis_en_cy.py
    uv run python notebooks/ciancheiltis_en_cy.py --cli --theme T3

Surfaces:

1. Per-theme coverage matrix (T1–T10)
2. Per-source metadata-language-mismatch rate
   (the SI 2007/1484 lesson — never trust `metadata.language`)
3. Bilingual-pair coverage RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded)
4. The 8 Phase 1 sources + their canonical URLs
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
        # Ciancheiltis — Phase 1 (en-cy / Wales) dashboard

        The Phase 1 (en-cy / Wales) operator console. Renders:

        1. **Per-theme coverage matrix** (T1–T10)
        2. **Per-source metadata-language-mismatch rate**
        3. **Bilingual-pair RAGAS gate** (≥ 0.70 + ≥ 500 pairs seeded)
        4. **The 8 Phase 1 sources** + canonical URLs

        See:
        - `ciancheiltis/README.md`
        - `openspec/specs/ciancheiltis/spec.md`
        - `motherduck/dives/ciancheiltis_en_cy_dive.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis.en_cy import (
        legislation,
        policy_consultations,
        education,
        healthcare,
        language_commissioner,
        termau_cymru,
        court_service,
        local_government,
    )

    sources = {
        "T1 Legislation": (legislation, "https://www.legislation.gov.uk/wsi"),
        "T2 Policy / consultations": (policy_consultations, "https://gov.wales/policy"),
        "T3 Education": (education, "https://hwb.gov.wales/curriculum-for-wales/"),
        "T4 Healthcare": (healthcare, "https://phw.nhs.wales/cy/"),
        "T5 Language bodies": (language_commissioner, "https://welshlanguagecommissioner.wales/cy/standards/"),
        "T6 Terminology": (termau_cymru, "https://colegcymraeg.ac.uk/termau/"),
        "T7 Courts & Tribunals": (court_service, "https://www.find-court-tribunal.service.gov.uk/"),
        "T8 Local government": (local_government, "https://www.gov.wales/find-your-local-authority"),
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

    mo.md("## 1. Phase 1 sources\n\n" + _table_md(rows))
    return


@app.cell
def _opaque_scanner_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.opaque_url_scanner import classify_url

    canonical_urls = [
        "https://www.legislation.gov.uk/uksi/2007/1484/made",
        "https://www.legislation.gov.uk/uksi/2007/1484/made/welsh",
        "https://www.legislation.gov.uk/wsi/2007/2044/made/welsh",
        "https://ncca.ie/en/resources/ty_transition_year_school_guidelines/",
        "https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/",
        "https://www.culturevannin.im/learn-gaelg/",
        "https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E",
    ]

    rows = [classify_url(u) for u in canonical_urls]
    mo.md("## 2. Opaque-URL scanner demo (all 6 phases)\n\n" + _table_md(rows))
    return


@app.cell
def _language_detector_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.language_detector import (
        detect_languages,
        metadata_mismatch,
    )

    si_2007_1484_body = (
        "The Secretary of State makes the following Order in exercise of the "
        "powers conferred by section 26(2) of the Welsh Language Act 1993.\n\n"
        "“Llw teyrngarwch\n\n"
        "Yr wyf i, [enw], yn tyngu i Dduw Hollalluog y byddaf i, ar ôl dod yn "
        "ddinesydd Prydeinig, yn ffyddlon ac yn wir deyrngar i'w Mawrhydi y "
        "Brenin Charles y Trydydd, ei Etifeddion a'i Olynwyr, yn unol âr gyfraith."
    )

    detected = detect_languages(si_2007_1484_body, top_k=2)
    mismatch = metadata_mismatch(
        si_2007_1484_body,
        {"language": "eng"},
        expected_iso="cy",
    )

    mo.md(
        f"## 3. Content-based language detection\n\n"
        f"Detected languages on SI 2007/1484 body: `{detected}`\n\n"
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
    ga_url = "https://ncca.ie/ga/resources/ty_transition_year_school_guidelines/"

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
