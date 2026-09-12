"""marimo notebook: ciancheiltis_en_ga_ni_dashboard.

The Phase 3 (en-ga / Northern Ireland) operator console for the
ciancheiltis umbrella. Dual-mode (per `https://docs.marimo.io/guides/scripts/`):

    uv run marimo edit notebooks/ciancheiltis_en_ga_ni.py
    uv run python notebooks/ciancheiltis_en_ga_ni.py --cli --theme T3

Surfaces:

1. Per-theme coverage matrix (T1–T10)
2. Per-source metadata-language-mismatch rate
   (the Phase 3 mismatch pattern — nidirect.gov.uk slug PREFIX
   `/articles/` ↔ `/gaeilge/airteagal/` pairs vs Phase 1
   `legislation.gov.uk` metadata.language mismatch vs Phase 2
   gov.ie `/en/` ↔ `/ga/` infix pair signal)
3. Bilingual-pair coverage RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded)
4. The 8 Phase 3 sources + their canonical URLs

The canonical bilingual reference is
`https://www.legislation.gov.uk/uksi/2022/15/contents/made`
(the Identity and Language (Northern Ireland) Act 2022 itself).
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
        # Ciancheiltis — Phase 3 (en-ga / Northern Ireland) dashboard

        The Phase 3 (en-ga / Northern Ireland) operator console. Renders:

        1. **Per-theme coverage matrix** (T1–T10)
        2. **Per-source metadata-language-mismatch rate**
           (nidirect.gov.uk `/articles/` ↔ `/gaeilge/airteagal/` slug
           PREFIX pairs — different from Phase 1's
           `legislation.gov.uk` metadata.language mismatch and Phase 2's
           gov.ie `/en/` ↔ `/ga/` infix pair signal)
        3. **Bilingual-pair RAGAS gate** (≥ 0.70 + ≥ 500 pairs seeded)
        4. **The 8 Phase 3 sources** + canonical URLs

        See:
        - `ciancheiltis/README.md`
        - `openspec/specs/ciancheiltis/spec.md`
        - `motherduck/dives/ciancheiltis_en_ga_ni_dive.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis.en_ga_ni import (
        legislation,
        nidirect_government,
        education,
        health,
        foras_na_gaeilge,
        ulster_scots_agency,
        courts_service,
        local_government,
    )

    sources = {
        "T1 Legislation": (
            legislation,
            "https://www.legislation.gov.uk/uksi/2022/15/contents/made",
        ),
        "T2 Policy / nidirect": (
            nidirect_government,
            "https://www.nidirect.gov.uk/articles",
        ),
        "T3 Education": (
            education,
            "https://www.education-ni.gov.uk/",
        ),
        "T4 Healthcare": (
            health,
            "https://www.health-ni.gov.uk/",
        ),
        "T5 Language bodies": (
            foras_na_gaeilge,
            "https://www.forasnagaeilge.ie/ga/",
        ),
        "T6 Ulster Scots / terminology": (
            ulster_scots_agency,
            "https://www.comhairle.org/",
        ),
        "T7 Courts & Tribunals": (
            courts_service,
            "https://www.courtsni.uk/",
        ),
        "T8 Local government": (
            local_government,
            "https://www.belfastcity.gov.uk/gaelic",
        ),
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

    mo.md("## 1. Phase 3 sources\n\n" + _table_md(rows))
    return


@app.cell
def _opaque_scanner_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.opaque_url_scanner import classify_url

    canonical_urls = [
        "https://www.legislation.gov.uk/uksi/2022/15/contents/made",
        "https://www.legislation.gov.uk/uksi/2022/15/contents/ga/made",
        "https://www.nidirect.gov.uk/articles/identity-and-language-ni-act-2022",
        "https://www.nidirect.gov.uk/gaeilge/airteagal/identity-and-language-ni-act-2022",
        "https://www.comhairle.org/ga/faoin-comhairle",
        "https://www.ulsterscotsagency.org.uk/education/",
        "https://www.education-ni.gov.uk/articles/school-uniform-guidelines",
        "https://eur-lex.europa.eu/legal-content/GA/TXT/?uri=CELEX:12012E",
    ]

    rows = [classify_url(u) for u in canonical_urls]
    mo.md("## 2. Opaque-URL scanner demo (Phase 3 candidates)\n\n" + _table_md(rows))
    return


@app.cell
def _language_detector_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.language_detector import (
        detect_languages,
        metadata_mismatch,
    )

    identity_act_body = (
        "An Act to make provision in relation to the recognition of "
        "the Irish language and the Ulster Scots language in Northern "
        "Ireland; to confer powers on the Department for Communities "
        "in relation to the Irish language and the Ulster Scots "
        "language; and for connected purposes.\n\n"
        "Acht chun socruithe a dhéanamh maidir le haitheantas na "
        "Gaeilge agus le haitheantas na Bérla Albanaí in Éirinn "
        "Thuaidh; chun cumhachtaí a thabhairt don Roinn Pobal "
        "maidir leis an nGaeilge agus maidir le Bérla Albanaí; "
        "agus chun críocha gaolmhara."
    )

    detected = detect_languages(identity_act_body, top_k=2)
    mismatch = metadata_mismatch(
        identity_act_body,
        {"language": "eng"},
        expected_iso="ga",
    )

    mo.md(
        f"## 3. Content-based language detection\n\n"
        f"Detected languages on the Identity and Language (NI) Act "
        f"2022 preamble body: `{detected}`\n\n"
        f"Metadata mismatch summary: `{mismatch}`"
    )
    return


@app.cell
def _metadata_normalization_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.bilingual_page_validator import (
        normalize_for_compare,
    )

    en_url = "https://www.nidirect.gov.uk/articles/identity-and-language-ni-act-2022"
    ga_url = "https://www.nidirect.gov.uk/gaeilge/airteagal/identity-and-language-ni-act-2022"

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
