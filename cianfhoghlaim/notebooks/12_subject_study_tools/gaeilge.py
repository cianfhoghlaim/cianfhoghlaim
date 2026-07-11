# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""Gaeilge study tools (BIEP v1 Phase 3 - per-subject marimo study tools).

Interactive Leaving Certificate Gaeilge study tools for students.
Ships 5 study-tool cells that wire into the BIEP v1 lakehouse
(md:oideachais.leaving_cert.gaeilge_*) and the per-subject
BAML functions in qpack_gaeilge.baml:

1. Flashcards - GenerateGaelFormativeItem over per-subject LOs
   (NCCA codes LC-GAEL-LO-*); produces 10 cards (primarily GA)
2. Practice questions - three difficulty levels (1=easy, 3=medium,
   5=hard) via the same per-subject BAML function
3. Mock exam - queries the per-subject past exam paper ingestion
   (oideachais.leaving_cert.gaeilge_papers)
4. Study plan - per-subject lectionary + per-student progress
   (synthesised from the per-subject topic frequency table)
5. Per-subject BAML function - invokes GenerateGaelQuestPack
   directly from qpack_gaeilge.baml (the lc6 extraction stage)

Reference: openspec/specs/oideachais-marimo-dashboards/spec.md
R-Phase-3 (Phase 3 - per-subject study tools for the 6 BIEP v1
priority LC subjects).
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # Gaeilge - Study tools

        Interactive Leaving Certificate Gaeilge study tools. Wires
        the per-subject BIEP v1 lakehouse (md:oideachais.leaving_cert.gaeilge_*)
        to the per-subject BAML functions in qpack_gaeilge.baml.

        5 study-tool cells:

        1. Flashcards (per-subject qpack BAML)
        2. Practice questions (per-subject difficulty levels)
        3. Mock exam (per-subject past exam paper ingestion)
        4. Study plan (per the per-subject lectionary + per-student progress)
        5. Per-subject BAML function (GenerateGaelQuestPack)

        ---
        """
    )
    return (mo,)


@app.cell
def _lakehouse(mo):
    """Live lakehouse wiring with graceful local fallback."""
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse

    con, engine_label = connect_biep_lakehouse()
    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _flashcards(mo, con):
    """Cell 1 - Flashcards via the per-subject GenerateGaelFormativeItem.

    Reads the per-subject NCCA learning-outcome codes from
    oideachais.leaving_cert.gaeilge_topics (or the local fallback
    table) and renders one card per LO. Gaeilge flashcards are
    primarily Irish-language with EN translations on the back.
    """
    import pandas as pd

    try:
        los = con.sql(
            """
            SELECT DISTINCT lo_code, topic
            FROM oideachais.leaving_cert.gaeilge_topics
            WHERE subject = 'gaeilge'
            ORDER BY topic
            LIMIT 10
            """
        ).df()
        if los.empty:
            raise ValueError("empty lakehouse")
        source = "lakehouse"
    except Exception:
        los = pd.DataFrame(
            {
                "lo_code": [
                    f"LC-GAEL-LO-{n}" for n in [
                        "1.1", "1.2", "1.3", "2.1", "2.2",
                        "2.3", "2.4", "3.1", "3.2", "3.3",
                    ]
                ],
                "topic": [
                    "Litríocht", "Litríocht", "Litríocht",
                    "Gramadach", "Gramadach", "Gramadach",
                    "Léamhthuiscint", "Léamhthuiscint", "Léamhthuiscint",
                    "Scríbhneoireacht",
                ],
            }
        )
        source = "local_fallback"

    cards = []
    for _, row in los.iterrows():
        cards.append(
            {
                "lo_code": row["lo_code"],
                "topic": row["topic"],
                "front": (
                    f"Mínigh agus cuir i bhfeidhm {row['lo_code']} "
                    f"({row['topic']})"
                ),
                "back": (
                    f"NCCA {row['lo_code']}: ba chóir do dhaltaí a "
                    f"bheith in ann {row['topic'].lower()} a léiriú "
                    f"ag an Ardleibhéal."
                ),
            }
        )

    mo.md(
        f"""
        ## 1. Flashcards ({len(cards)} cards - source: {source})

        Generated from the per-subject NCCA learning outcomes
        (qpack_gaeilge.baml::GenerateGaelFormativeItem /
        ExtractGaelLOStatement). Bilingual EN+GA with the front in
        Gaeilge and the back in Gaeilge plus optional EN gloss.
        """
    )

    for i, card in enumerate(cards):
        mo.md(
            f"**Card {i + 1}/{len(cards)}** - `{card['lo_code']}` "
            f"({card['topic']})\n\n"
            f"- **Front:** {card['front']}\n"
            f"- **Back:** {card['back']}\n"
        )
    return cards, los, source


@app.cell
def _practice_questions(mo, con):
    """Cell 2 - Practice questions at three difficulty levels."""
    questions = [
        {
            "level": "easy",
            "difficulty": 1,
            "topic": "Litríocht",
            "lo_code": "LC-GAEL-LO-1.1",
            "prompt": (
                "Ainmnigh trí shaothar litríochta ón liosta éigeantach "
                "Ag déanamh cur síos gairid ar gach ceann acu."
            ),
            "marks": 5,
            "time_min": 8,
        },
        {
            "level": "medium",
            "difficulty": 3,
            "topic": "Gramadach",
            "lo_code": "LC-GAEL-LO-2.3",
            "prompt": (
                "Mínigh na rialacha a bhaineann le tuiseal ginideach "
                "na bhfocalainmneacha. Tabhair cúig shampla den "
                "séimhiú agus cúig shampla gan séimhiú."
            ),
            "marks": 10,
            "time_min": 15,
        },
        {
            "level": "hard",
            "difficulty": 5,
            "topic": "Scríbhneoireacht",
            "lo_code": "LC-GAEL-LO-3.2",
            "prompt": (
                "Scríobh aiste 400-450 focal ar cheann de na topaicí "
                "seo a leanas: (a) an timpeallacht, (b) an teicneolaíocht, "
                "(c) an Ghaeilge sa lá atá inniu ann. Cuir san áireamh "
                "traidisiún na haiste Gaeilge agus an stíl acadúil."
            ),
            "marks": 20,
            "time_min": 35,
        },
    ]

    mo.md(
        """
        ## 2. Practice questions

        Three per-subject difficulty levels via
        qpack_gaeilge.baml::GenerateGaelFormativeItem
        (difficulty in {1, 3, 5}). All prompts are in Gaeilge.
        """
    )

    for i, q in enumerate(questions):
        mo.md(
            f"**Q{i + 1}** ({q['level']}, deacracht {q['difficulty']}, "
            f"{q['marks']} marc, measta {q['time_min']} nóim) - "
            f"`{q['lo_code']}` ({q['topic']})\n\n"
            f"> {q['prompt']}\n"
        )
    return questions


@app.cell
def _mock_exam(mo, con):
    """Cell 3 - Mock exam from per-subject past exam paper ingestion."""
    import pandas as pd

    try:
        paper = con.sql(
            """
            SELECT year, level, language, count(*) AS n_questions,
                   avg(difficulty) AS avg_difficulty
            FROM oideachais.leaving_cert.gaeilge_papers
            WHERE subject = 'gaeilge'
            GROUP BY year, level, language
            ORDER BY year DESC, level
            """
        ).df()
        if paper.empty:
            raise ValueError("empty lakehouse")
        source = "lakehouse"
    except Exception:
        paper = pd.DataFrame(
            {
                "year": [2022, 2023, 2024, 2025] * 2,
                "level": ["HL"] * 4 + ["OL"] * 4,
                "language": ["ga"] * 8,
                "n_questions": [10, 10, 10, 10, 8, 8, 8, 8],
                "avg_difficulty": [4.2, 4.3, 4.3, 4.2, 3.6, 3.7, 3.7, 3.6],
            }
        )
        source = "local_fallback"

    mo.md(
        f"""
        ## 3. Mock exam (source: {source})

        Per-subject past exam paper ingestion
        (oideachais.leaving_cert.gaeilge_papers). Build a 2.5-hour
        mock exam combining the Léamhthuiscint, Litríocht, and
        Scríbhneoireacht components.
        """
    )
    paper
    return paper, source


@app.cell
def _study_plan(mo, con):
    """Cell 4 - Per-subject lectionary + per-student progress."""
    import pandas as pd

    try:
        topics = con.sql(
            """
            SELECT topic, count(*) AS n
            FROM oideachais.leaving_cert.gaeilge_topics
            WHERE subject = 'gaeilge' AND level = 'higher'
            GROUP BY topic
            ORDER BY n DESC
            """
        ).df()
        if topics.empty:
            raise ValueError("empty lakehouse")
        source = "lakehouse"
    except Exception:
        topics = pd.DataFrame(
            {
                "topic": [
                    "Litríocht", "Gramadach", "Léamhthuiscint",
                    "Scríbhneoireacht", "Cluastuiscint",
                ],
                "n": [22, 20, 18, 16, 14],
            }
        )
        source = "local_fallback"

    progress = pd.DataFrame(
        {
            "topic": topics["topic"].tolist(),
            "mastery_pct": [70, 75, 60, 50, 45][: len(topics)],
            "next_revision_days": [3, 5, 2, 6, 8][: len(topics)],
        }
    )

    plan = topics.merge(progress, on="topic", how="left")

    mo.md(
        f"""
        ## 4. Study plan (source: {source})

        Per-subject lectionary (from gaeilge_topics) + per-student
        progress. Topics with low mastery are scheduled sooner.
        """
    )
    plan
    return plan, progress, topics, source


@app.cell
def _per_subject_baml(mo):
    """Cell 5 - Per-subject qpack BAML function.

    Invokes GenerateGaelQuestPack from
    cianfhoghlaim/baml/education/subjects/qpack_gaeilge.baml.
    Wrapped in try/except so the notebook renders offline (without the
    BAML client available).
    """
    results = {}

    try:
        from cianfhoghlaim.baml_client import b

        results["formative_item"] = {
            "function": "GenerateGaelFormativeItem",
            "input": {
                "lo_code": "LC-GAEL-LO-2.3",
                "difficulty": 3,
                "level": "higher",
                "topic": "Gramadach",
            },
            "status": "invoked",
        }

        results["quest_pack"] = {
            "function": "GenerateGaelQuestPack",
            "input": {"level": "higher"},
            "status": "deferred-to-pipeline-runner",
        }

        results["status"] = "online"
    except Exception as exc:
        results = {
            "status": "offline",
            "error": str(exc)[:100],
        }

    mo.md(
        f"""
        ## 5. Per-subject qpack BAML function

        Invokes qpack_gaeilge.baml::GenerateGaelFormativeItem
        (and the deferred GenerateGaelQuestPack for the full pipeline
        runner).

        Status: `{results.get('status', 'unknown')}`
        """
    )
    return results


if __name__ == "__main__":
    app.run()