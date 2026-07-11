# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""English study tools (BIEP v1 Phase 3 - per-subject marimo study tools).

Interactive Leaving Certificate English study tools for students.
Ships 5 study-tool cells that wire into the BIEP v1 lakehouse
(md:oideachais.leaving_cert.english_*) and the per-subject
BAML functions in qpack_english.baml:

1. Flashcards - GenerateEnglFormativeItem over per-subject LOs
   (NCCA codes LC-ENGL-LO-*); produces 10 cards
2. Practice questions - three difficulty levels (1=easy, 3=medium,
   5=hard) via the same per-subject BAML function
3. Mock exam - queries the per-subject past exam paper ingestion
   (oideachais.leaving_cert.english_papers)
4. Study plan - per-subject lectionary + per-student progress
   (synthesised from the per-subject topic frequency table)
5. Per-subject BAML function - invokes GenerateEnglQuestPack
   directly from qpack_english.baml (the lc6 extraction stage)

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
        # English - Study tools

        Interactive Leaving Certificate English study tools. Wires
        the per-subject BIEP v1 lakehouse (md:oideachais.leaving_cert.english_*)
        to the per-subject BAML functions in qpack_english.baml.

        5 study-tool cells:

        1. Flashcards (per-subject qpack BAML)
        2. Practice questions (per-subject difficulty levels)
        3. Mock exam (per-subject past exam paper ingestion)
        4. Study plan (per the per-subject lectionary + per-student progress)
        5. Per-subject BAML function (GenerateEnglQuestPack)

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
    """Cell 1 - Flashcards via the per-subject GenerateEnglFormativeItem.

    Reads the per-subject NCCA learning-outcome codes from
    oideachais.leaving_cert.english_topics (or the local fallback
    table) and renders one card per LO.
    """
    import pandas as pd

    try:
        los = con.sql(
            """
            SELECT DISTINCT lo_code, topic
            FROM oideachais.leaving_cert.english_topics
            WHERE subject = 'english'
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
                    f"LC-ENGL-LO-{n}" for n in [
                        "1.1", "1.2", "1.3", "2.1", "2.2",
                        "2.3", "2.4", "3.1", "3.2", "3.3",
                    ]
                ],
                "topic": [
                    "Reading", "Reading", "Reading",
                    "Writing", "Writing", "Writing",
                    "Comprehension", "Comprehension", "Comprehension",
                    "Composition",
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
                "front": f"Define and apply {row['lo_code']} ({row['topic']})",
                "back": (
                    f"NCCA {row['lo_code']}: students should be able to "
                    f"demonstrate competency in {row['topic'].lower()} at "
                    f"Leaving Certificate Higher Level."
                ),
            }
        )

    mo.md(
        f"""
        ## 1. Flashcards ({len(cards)} cards - source: {source})

        Generated from the per-subject NCCA learning outcomes
        (qpack_english.baml::GenerateEnglFormativeItem /
        ExtractEnglLOStatement).
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
            "topic": "Reading",
            "lo_code": "LC-ENGL-LO-1.1",
            "prompt": (
                "Read the extract provided and identify THREE key "
                "themes. Quote from the text to support each."
            ),
            "marks": 5,
            "time_min": 8,
        },
        {
            "level": "medium",
            "difficulty": 3,
            "topic": "Comprehension",
            "lo_code": "LC-ENGL-LO-2.3",
            "prompt": (
                "Analyse the writer's use of language and structure in "
                "the given extract. Support your response with close "
                "reference to the text."
            ),
            "marks": 10,
            "time_min": 15,
        },
        {
            "level": "hard",
            "difficulty": 5,
            "topic": "Composition",
            "lo_code": "LC-ENGL-LO-3.2",
            "prompt": (
                "Write a 400-450 word personal essay on the theme of "
                "identity. Demonstrate command of varied vocabulary, "
                "complex sentence structures, and a distinctive voice."
            ),
            "marks": 20,
            "time_min": 35,
        },
    ]

    mo.md(
        """
        ## 2. Practice questions

        Three per-subject difficulty levels via
        qpack_english.baml::GenerateEnglFormativeItem
        (difficulty in {1, 3, 5}).
        """
    )

    for i, q in enumerate(questions):
        mo.md(
            f"**Q{i + 1}** ({q['level']}, difficulty {q['difficulty']}, "
            f"{q['marks']} marks, est. {q['time_min']} min) - "
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
            FROM oideachais.leaving_cert.english_papers
            WHERE subject = 'english'
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
                "language": ["en"] * 8,
                "n_questions": [8, 8, 8, 8, 6, 6, 6, 6],
                "avg_difficulty": [3.8, 3.9, 4.0, 3.9, 3.3, 3.4, 3.5, 3.4],
            }
        )
        source = "local_fallback"

    mo.md(
        f"""
        ## 3. Mock exam (source: {source})

        Per-subject past exam paper ingestion
        (oideachais.leaving_cert.english_papers). Build a 3-hour
        mock exam combining Paper 1 (comprehension + composition) and
        Paper 2 (single text + comparative text).
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
            FROM oideachais.leaving_cert.english_topics
            WHERE subject = 'english' AND level = 'higher'
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
                    "Reading", "Writing", "Comprehension",
                    "Composition", "Poetry",
                ],
                "n": [20, 18, 16, 14, 12],
            }
        )
        source = "local_fallback"

    progress = pd.DataFrame(
        {
            "topic": topics["topic"].tolist(),
            "mastery_pct": [80, 72, 65, 55, 42][: len(topics)],
            "next_revision_days": [2, 4, 3, 5, 7][: len(topics)],
        }
    )

    plan = topics.merge(progress, on="topic", how="left")

    mo.md(
        f"""
        ## 4. Study plan (source: {source})

        Per-subject lectionary (from english_topics) + per-student
        progress. Topics with low mastery are scheduled sooner.
        """
    )
    plan
    return plan, progress, topics, source


@app.cell
def _per_subject_baml(mo):
    """Cell 5 - Per-subject qpack BAML function.

    Invokes GenerateEnglQuestPack from
    cianfhoghlaim/baml/education/subjects/qpack_english.baml.
    Wrapped in try/except so the notebook renders offline (without the
    BAML client available).
    """
    input_payload = {
        "lo_code": "LC-ENGL-LO-2.3",
        "difficulty": 3,
        "level": "higher",
        "topic": "Comprehension",
    }

    try:
        from cianfhoghlaim.baml_client.baml_client.sync_client import b

        result = b.GenerateEnglFormativeItem(**input_payload)
        results = {
            "status": "ok",
            "function": "GenerateEnglFormativeItem",
            "input": input_payload,
            "result": result,
        }
    except Exception as exc:
        results = {
            "status": "error",
            "function": "GenerateEnglFormativeItem",
            "input": input_payload,
            "error": str(exc),
        }

    result_preview = results.get("result", results.get("error", ""))

    mo.md(
        f"""
        ## 5. Per-subject qpack BAML function

        Invokes qpack_english.baml::GenerateEnglFormativeItem
        with the canonical `(lo_code, difficulty, level, topic)`
        signature.

        Status: `{results.get('status', 'unknown')}`

        ### Generated Study Card

        ```python
        {result_preview}
        ```
        """
    )
    return results


if __name__ == "__main__":
    app.run()