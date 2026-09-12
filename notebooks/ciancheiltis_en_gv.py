"""marimo notebook: ciancheiltis_en_gv_dashboard.

The Phase 5 (en-gv / Isle of Man) operator console for the
ciancheiltis umbrella. Dual-mode (per `https://docs.marimo.io/guides/scripts/`):

    uv run marimo edit notebooks/ciancheiltis_en_gv.py
    uv run python notebooks/ciancheiltis_en_gv.py --cli --theme T3

Surfaces:

1. Per-theme coverage matrix (T1–T10)
2. Per-source metadata-language-mismatch rate
   (the Phase 5 mismatch pattern — `en_only_no_pair` is the
   DOMINANT tag because Manx is a REVIVAL language with NO
   statutory bilingual framework; most IoM government pages exist
   in English only — different from Phase 1's
   `legislation.gov.uk` metadata.language mismatch, Phase 2's
   gov.ie `/en/` ↔ `/ga/` infix pair signal, Phase 3's
   nidirect.gov.uk `/articles/` ↔ `/gaeilge/airteagal/` slug
   PREFIX, and Phase 4's gov.scot `<html lang="gd">` attribute)
3. Bilingual-pair coverage RAGAS gate (≥ 0.70 + ≥ 500 pairs seeded)
   — ASPIRATIONAL on Phase 5 because Manx is a REVIVAL language
4. The 8 Phase 5 sources + their canonical URLs

The canonical bilingual reference is
`https://www.culturevannin.im/learn-gaelg/` (Culture Vannin under
Tynwald — the bicameral Isle of Man Parliament with the House of
Keys + the Legislative Council; Tynwald Day 5 July is the oldest
continuous parliament in the world, dating to AD 979).
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
        # Ciancheiltis — Phase 5 (en-gv / Isle of Man) dashboard

        The Phase 5 (en-gv / Isle of Man) operator console. Renders:

        1. **Per-theme coverage matrix** (T1–T10)
        2. **Per-source metadata-language-mismatch rate**
           (`en_only_no_pair` is the DOMINANT Phase 5 tag because
           Manx is a REVIVAL language with NO statutory bilingual
           framework — different from Phase 1's `legislation.gov.uk`
           metadata.language mismatch, Phase 2's gov.ie `/en/` ↔
           `/ga/` infix pair signal, Phase 3's nidirect.gov.uk
           `/articles/` ↔ `/gaeilge/airteagal/` slug PREFIX, and
           Phase 4's gov.scot `<html lang="gd">` attribute)
        3. **Bilingual-pair RAGAS gate** (≥ 0.70 + ≥ 500 pairs seeded)
           — ASPIRATIONAL on Phase 5 because Manx is a REVIVAL language
        4. **The 8 Phase 5 sources** + canonical URLs

        **Phase 5 caveat**: Manx (Gaelg) is a REVIVAL language
        (last native speaker — Ned Maddrell — died 1974) under
        Culture Vannin + Learn Manx + Bunscoill Ghaelgagh + Radio
        Manx. There is NO statutory bilingual framework comparable
        to Welsh (Phase 1), Irish (Phase 2/3), or Scottish Gaelic
        (Phase 4). The bilingual-pairs-seeded gate is ASPIRATIONAL,
        and the metadata-mismatch rate on Phase 5 is EXPECTED to be
        DRAMATICALLY higher than Phase 1 + Phase 2 + Phase 3 + Phase
        4 — this is a known characteristic of the en-gv revival-language
        landscape, not a regression.

        See:
        - `ciancheiltis/README.md`
        - `openspec/specs/ciancheiltis/spec.md`
        - `motherduck/dives/ciancheiltis_en_gv_dive.py`
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis.en_gv import (
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
            "https://legislation.gov.im/",
        ),
        "T2 Policy / consultations": (
            policy_consultations,
            "https://www.gov.im/about-the-government/manx-public-records/",
        ),
        "T3 Education": (
            education,
            "https://bunscoill.sch.im/",
        ),
        "T4 Healthcare": (
            healthcare,
            "https://www.gov.im/categories/health-and-social-care/",
        ),
        "T5 Language bodies": (
            language_bodies,
            "https://www.culturevannin.im/learn-gaelg/",
        ),
        "T6 Terminology": (
            terminology,
            "https://www.learnmanx.com/",
        ),
        "T7 Courts & Tribunals": (
            courts,
            "https://www.courts.im/",
        ),
        "T8 Local government": (
            local_government,
            "https://www.gov.im/local-government/",
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

    mo.md("## 1. Phase 5 sources\n\n" + _table_md(rows))
    return


@app.cell
def _opaque_scanner_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.opaque_url_scanner import classify_url

    canonical_urls = [
        "https://legislation.gov.im/",
        "https://legislation.gov.im/cms/gazette/2024/gazette_20240715.pdf",
        "https://www.culturevannin.im/learn-gaelg/",
        "https://www.culturevannin.im/for-school/",
        "https://www.learnmanx.com/lessons/",
        "https://www.learnmanx.com/grammar/",
        "https://bunscoill.sch.im/about-our-school/",
        "https://www.courts.im/judiciary/",
        "https://www.gov.im/about-the-government/manx-public-records/",
    ]

    rows = [classify_url(u) for u in canonical_urls]
    mo.md("## 2. Opaque-URL scanner demo (Phase 5 candidates)\n\n" + _table_md(rows))
    return


@app.cell
def _language_detector_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.language_detector import (
        detect_languages,
        metadata_mismatch,
    )

    culture_vannin_preamble = (
        "Welcome to Culture Vannin, the Manx language and culture "
        "body, working to support and grow the use of Manx Gaelic "
        "across the Isle of Man.\n\n"
        "Failt ort er Culture Vannin, yn obbyr Ghaelg as culture "
        "Vannin, gobbraghey son cur lesh as mooadaghey yn ymmyd jeh "
        "Gaelg Vannin er Ellan Vannin."
    )

    detected = detect_languages(culture_vannin_preamble, top_k=2)
    mismatch = metadata_mismatch(
        culture_vannin_preamble,
        {"language": "en"},
        expected_iso="gv",
    )

    mo.md(
        f"## 3. Content-based language detection\n\n"
        f"Detected languages on the Culture Vannin preamble body: "
        f"`{detected}`\n\n"
        f"Metadata mismatch summary: `{mismatch}`"
    )
    return


@app.cell
def _metadata_normalization_demo() -> None:
    import marimo as mo

    from dlt_sources.ciancheiltis._shared.bilingual_page_validator import (
        normalize_for_compare,
    )

    en_url = "https://www.culturevannin.im/about-us/"
    gv_url = "https://www.culturevannin.im/learn-gaelg/"

    en_norm = normalize_for_compare(en_url)
    gv_norm = normalize_for_compare(gv_url)

    mo.md(
        f"## 4. Bilingual-pair normalisation\n\n"
        f"- EN: `{en_url}` → `{en_norm}`\n"
        f"- GV: `{gv_url}` → `{gv_norm}`\n"
        f"- **Same canonical form**: `{en_norm == gv_norm}`"
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
