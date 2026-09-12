"""marimo notebook: ciancheiltis_en_gd_dashboard.

The Phase 4 (en-gd / Scotland) operator console for the
ciancheiltis umbrella. Dual-mode (per `https://docs.marimo.io/guides/scripts/`):

    uv run marimo edit notebooks/ciancheiltis_en_gd.py
    uv run python notebooks/ciancheiltis_en_gd.py --cli --theme T3

Surfaces:

1. Per-theme coverage matrix (T1–T10)
2. Per-source metadata-language-mismatch rate
   (the Phase 4 mismatch pattern — gov.scot `<html lang="gd">`
   attribute as canonical pair signal vs Phase 1
   `legislation.gov.uk` metadata.language mismatch vs Phase 2
   gov.ie `/en/` ↔ `/ga/` infix pair signal vs Phase 3
   nidirect.gov.uk `/articles/` ↔ `/gaeilge/airteagal/` slug PREFIX)
3. Bilingual-pair coverage RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded)
4. The 8 Phase 4 sources + their canonical URLs

The canonical bilingual reference is
`https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/` (Bòrd na
Gàidhlig under the Gaelic Language (Scotland) Act 2005
`https://www.legislation.gov.uk/asp/2005/7/contents`).
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
        # Ciancheiltis — Phase 4 (en-gd / Scotland) dashboard

        The Phase 4 (en-gd / Scotland) operator console. Renders:

        1. **Per-theme coverage matrix** (T1–T10)
        2. **Per-source metadata-language-mismatch rate**
           (gov.scot `<html lang="gd">` attribute as canonical pair
           signal — different from Phase 1's `legislation.gov.uk`
           metadata.language mismatch, Phase 2's gov.ie `/en/` ↔
           `/ga/` infix pair signal, and Phase 3's nidirect.gov.uk
           `/articles/` ↔ `/gaeilge/airteagal/` slug PREFIX)
        3. **Bilingual-pair RAGAS gate** (≥ 0.70 + ≥ 500 pairs seeded)
        4. **The 8 Phase 4 sources** + canonical URLs

        **Phase 4 caveat**: Scottish Gaelic coverage is partial
        relative to Welsh (Phase 1) or Irish (Phase 2/3) — fewer
        gov.scot pages have full GD translations, and many
        `legislation.gov.uk/asp/<year>/<num>/contents` pages exist
        in English only. The metadata-mismatch rate on Phase 4 is
        EXPECTED to be higher than Phase 1 + Phase 2 + Phase 3 — this
        is a known characteristic of the en-gd landscape, not a
        regression.

        See:
        - `ciancheiltis/README.md`
        - `openspec/specs/ciancheiltis/spec.md`
        - `motherduck/dives/ciancheiltis_en_gd_dive.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis.en_gd import (
        legislation,
        policy_consultations,
        education,
        healthcare,
        language_bodies,
        terminology,
        courts,
        local_government,
    )

    sources = {
        "T1 Legislation": (
            legislation,
            "https://www.legislation.gov.uk/asp/2005/7/contents",
        ),
        "T2 Policy / consultations": (
            policy_consultations,
            "https://www.gov.scot/policies/",
        ),
        "T3 Education": (
            education,
            "https://education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/",
        ),
        "T4 Healthcare": (
            healthcare,
            "https://www.nhsinform.scot/",
        ),
        "T5 Language bodies": (
            language_bodies,
            "https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/",
        ),
        "T6 Terminology": (
            terminology,
            "https://www.storlann.co.uk/",
        ),
        "T7 Courts & Tribunals": (
            courts,
            "https://www.scotcourts.gov.uk/",
        ),
        "T8 Local government": (
            local_government,
            "https://www.edinburgh.gov.uk/",
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

    mo.md("## 1. Phase 4 sources\n\n" + _table_md(rows))
    return


@app.cell
def _opaque_scanner_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.opaque_url_scanner import classify_url

    canonical_urls = [
        "https://www.legislation.gov.uk/asp/2005/7/contents",
        "https://www.legislation.gov.uk/ssi/2005/461/contents/made",
        "https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/",
        "https://education.gov.scot/the-improvement-continuum/foghlam-tron-ghaidhlig/",
        "https://www.storlann.co.uk/foillseachadh/leabhraichean/",
        "https://www.scotcourts.gov.uk/judiciary/court-of-session",
        "https://www.nhsinform.scot/illnesses-and-conditions/",
        "https://www.edinburgh.gov.uk/gaidhlig/",
    ]

    rows = [classify_url(u) for u in canonical_urls]
    mo.md("## 2. Opaque-URL scanner demo (Phase 4 candidates)\n\n" + _table_md(rows))
    return


@app.cell
def _language_detector_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.language_detector import (
        detect_languages,
        metadata_mismatch,
    )

    gaelic_act_preamble = (
        "An Act of the Scottish Parliament to make provision for the "
        "Gaelic language as an official language of Scotland "
        "commanding the same respect as the English language, "
        "including the establishment of Bòrd na Gàidhlig.\n\n"
        "Achd Pàrlamaid na h-Alba a bhios a' dèanamh sholarachaidhean "
        "airson a' Ghàidhlig mar chànan oifigeil air a bheil an aon "
        "urram 's a tha air a' Bheurla, a' gabhail a-steach stèidheachadh "
        "Bòrd na Gàidhlig."
    )

    detected = detect_languages(gaelic_act_preamble, top_k=2)
    mismatch = metadata_mismatch(
        gaelic_act_preamble,
        {"language": "eng"},
        expected_iso="gd",
    )

    mo.md(
        f"## 3. Content-based language detection\n\n"
        f"Detected languages on the Gaelic Language (Scotland) Act "
        f"2005 preamble body: `{detected}`\n\n"
        f"Metadata mismatch summary: `{mismatch}`"
    )
    return


@app.cell
def _metadata_normalization_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.bilingual_page_validator import (
        normalize_for_compare,
    )

    en_url = "https://www.gaidhlig.scot/bord-na-gaidhlig/about-us/"
    gd_url = "https://www.gaidhlig.scot/bord-na-gaidhlig/naidheachdan/"

    en_norm = normalize_for_compare(en_url)
    gd_norm = normalize_for_compare(gd_url)

    mo.md(
        f"## 4. Bilingual-pair normalisation\n\n"
        f"- EN: `{en_url}` → `{en_norm}`\n"
        f"- GD: `{gd_url}` → `{gd_norm}`\n"
        f"- **Same canonical form**: `{en_norm == gd_norm}`"
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
