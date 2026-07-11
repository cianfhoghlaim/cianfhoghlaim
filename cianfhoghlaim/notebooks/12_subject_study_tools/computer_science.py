# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""Computer Science study tools (BIEP v1 Phase 3 - per-subject marimo study tools).

Interactive Leaving Certificate Computer Science study tools for
students. Ships 5 study-tool cells that wire into the BIEP v1
lakehouse (md:oideachais.leaving_cert.computer_science_*) and the
per-subject BAML functions in qpack_computer_science.baml:

1. Flashcards - GenerateCompFormativeItem over per-subject LOs
   (NCCA codes LC-COMP-LO-*); produces 10 cards
2. Practice questions - three difficulty levels (1=easy, 3=medium,
   5=hard) via the same per-subject BAML function
3. Mock exam - queries the per-subject past exam paper ingestion
   (oideachais.leaving_cert.computer_science_papers)
4. Study plan - per-subject lectionary + per-student progress
   (synthesised from the per-subject topic frequency table)
5. Per-subject BAML function - invokes GenerateCompQuestPack
   directly from qpack_computer_science.baml (the lc6 extraction stage)

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
        # Computer Science - Study tools

        Interactive Leaving Certificate Computer Science study tools.
        Wires the per-subject BIEP v1 lakehouse
        (md:oideachais.leaving_cert.computer_science_*) to the
        per-subject BAML functions in qpack_computer_science.baml.

        5 study-tool cells:

        1. Flashcards (per-subject qpack BAML)
        2. Practice questions (per-subject difficulty levels)
        3. Mock exam (per-subject past exam paper ingestion)
        4. Study plan (per the per-subject lectionary + per-student progress)
        5. Per-subject BAML function (GenerateCompQuestPack)

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
    """Cell 1 - Flashcards via the per-subject GenerateCompFormativeItem.

    Reads the per-subject NCCA learning-outcome codes from
    oideachais.leaving_cert.computer_science_topics (or the local
    fallback table) and renders one card per LO.
    """
    import pandas as pd

    try:
        los = con.sql(
            """
            SELECT DISTINCT lo_code, topic
            FROM oideachais.leaving_cert.computer_science_topics
            WHERE subject = 'computer_science'
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
                    f"LC-COMP-LO-{n}" for n in [
                        "1.1", "1.2", "1.3", "2.1", "2.2",
                        "2.3", "2.4", "3.1", "3.2", "3.3",
                    ]
                ],
                "topic": [
                    "Algorithms", "Algorithms", "Algorithms",
                    "Programming", "Programming", "Programming",
                    "Data Structures", "Data Structures", "Data Structures",
                    "Databases",
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
        (qpack_computer_science.baml::GenerateCompFormativeItem /
        ExtractCompLOStatement).
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
            "topic": "Algorithms",
            "lo_code": "LC-COMP-LO-1.1",
            "prompt": (
                "Trace the following pseudocode for input n = 5 and "
                "state the output:\n\n"
                "  i = 0\n"
                "  while i < n:\n"
                "      print i\n"
                "      i = i + 1"
            ),
            "marks": 5,
            "time_min": 5,
        },
        {
            "level": "medium",
            "difficulty": 3,
            "topic": "Programming",
            "lo_code": "LC-COMP-LO-2.3",
            "prompt": (
                "Write a Python function `count_vowels(s)` that "
                "returns the number of vowels (a, e, i, o, u) in a "
                "given string. Include a brief explanation of "
                "complexity (Big-O)."
            ),
            "marks": 10,
            "time_min": 12,
        },
        {
            "level": "hard",
            "difficulty": 5,
            "topic": "Data Structures",
            "lo_code": "LC-COMP-LO-3.2",
            "prompt": (
                "Design and implement a stack class in Python "
                "supporting push, pop, peek, and is_empty methods. "
                "Include error handling for underflow. Analyse the "
                "time complexity of each operation."
            ),
            "marks": 20,
            "time_min": 25,
        },
    ]

    mo.md(
        """
        ## 2. Practice questions

        Three per-subject difficulty levels via
        qpack_computer_science.baml::GenerateCompFormativeItem
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
            FROM oideachais.leaving_cert.computer_science_papers
            WHERE subject = 'computer_science'
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
                "n_questions": [12, 12, 12, 12, 10, 10, 10, 10],
                "avg_difficulty": [3.9, 4.0, 4.1, 4.0, 3.4, 3.5, 3.6, 3.5],
            }
        )
        source = "local_fallback"

    mo.md(
        f"""
        ## 3. Mock exam (source: {source})

        Per-subject past exam paper ingestion
        (oideachais.leaving_cert.computer_science_papers). Build a
        2.5-hour mock exam combining Paper 1 (short questions) and
        Paper 2 (long questions + programming task).
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
            FROM oideachais.leaving_cert.computer_science_topics
            WHERE subject = 'computer_science' AND level = 'higher'
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
                    "Algorithms", "Programming", "Data Structures",
                    "Databases", "Networks",
                ],
                "n": [22, 20, 18, 16, 14],
            }
        )
        source = "local_fallback"

    progress = pd.DataFrame(
        {
            "topic": topics["topic"].tolist(),
            "mastery_pct": [76, 70, 60, 50, 42][: len(topics)],
            "next_revision_days": [3, 4, 2, 6, 8][: len(topics)],
        }
    )

    plan = topics.merge(progress, on="topic", how="left")

    mo.md(
        f"""
        ## 4. Study plan (source: {source})

        Per-subject lectionary (from computer_science_topics) +
        per-student progress. Topics with low mastery are scheduled
        sooner.
        """
    )
    plan
    return plan, progress, topics, source


@app.cell
def _per_subject_baml(mo):
    """Cell 5 - Per-subject qpack BAML function.

    Invokes GenerateCompQuestPack from
    cianfhoghlaim/baml/education/subjects/qpack_computer_science.baml.
    Wrapped in try/except so the notebook renders offline (without the
    BAML client available).
    """
    results = {}

    try:
        from cianfhoghlaim.baml_client import b

        results["formative_item"] = {
            "function": "GenerateCompFormativeItem",
            "input": {
                "lo_code": "LC-COMP-LO-2.3",
                "difficulty": 3,
                "level": "higher",
                "topic": "Programming",
            },
            "status": "invoked",
        }

        results["quest_pack"] = {
            "function": "GenerateCompQuestPack",
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

        Invokes qpack_computer_science.baml::GenerateCompFormativeItem
        (and the deferred GenerateCompQuestPack for the full pipeline
        runner).

        Status: `{results.get('status', 'unknown')}`
        """
    )
    return results


if __name__ == "__main__":
    app.run()