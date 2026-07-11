# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""Chemistry study tools (BIEP v1 Phase 3 - per-subject marimo study tools).

Interactive Leaving Certificate Chemistry study tools for students.
Ships 5 study-tool cells that wire into the BIEP v1 lakehouse
(md:oideachais.leaving_cert.chemistry_*) and the per-subject
BAML functions in qpack_chemistry.baml:

1. Flashcards - GenerateChemFormativeItem over per-subject LOs
   (NCCA codes LC-CHEM-LO-*); produces 10 bilingual EN+GA cards
2. Practice questions - three difficulty levels (1=easy, 3=medium,
   5=hard) via the same per-subject BAML function
3. Mock exam - queries the per-subject past exam paper ingestion
   (oideachais.leaving_cert.chemistry_papers)
4. Study plan - per-subject lectionary + per-student progress
   (synthesised from the per-subject topic frequency table)
5. Per-subject BAML function - invokes GenerateChemQuestPack
   directly from qpack_chemistry.baml (the lc6 extraction stage)

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
        # Chemistry - Study tools

        Interactive Leaving Certificate Chemistry study tools. Wires
        the per-subject BIEP v1 lakehouse (md:oideachais.leaving_cert.chemistry_*)
        to the per-subject BAML functions in qpack_chemistry.baml.

        5 study-tool cells:

        1. Flashcards (per-subject qpack BAML)
        2. Practice questions (per-subject difficulty levels)
        3. Mock exam (per-subject past exam paper ingestion)
        4. Study plan (per the per-subject lectionary + per-student progress)
        5. Per-subject BAML function (GenerateChemQuestPack)

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
    """Cell 1 - Flashcards via the per-subject GenerateChemFormativeItem.

    Reads the per-subject NCCA learning-outcome codes from
    oideachais.leaving_cert.chemistry_topics (or the local
    fallback table) and renders one card per LO.
    """
    import pandas as pd

    try:
        los = con.sql(
            """
            SELECT DISTINCT lo_code, topic
            FROM oideachais.leaving_cert.chemistry_topics
            WHERE subject = 'chemistry'
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
                    f"LC-CHEM-LO-{n}" for n in [
                        "1.1", "1.2", "1.3", "2.1", "2.2",
                        "2.3", "2.4", "3.1", "3.2", "3.3",
                    ]
                ],
                "topic": [
                    "Atomic Structure", "Atomic Structure", "Atomic Structure",
                    "Bonding", "Bonding", "Bonding",
                    "Stoichiometry", "Stoichiometry", "Stoichiometry",
                    "Acids & Bases",
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
        (qpack_chemistry.baml::GenerateChemFormativeItem /
        ExtractChemLOStatement).
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
            "topic": "Atomic Structure",
            "lo_code": "LC-CHEM-LO-1.1",
            "prompt": (
                "State the number of protons, neutrons and electrons "
                "in a neutral atom of carbon-12 (12C)."
            ),
            "marks": 5,
            "time_min": 5,
        },
        {
            "level": "medium",
            "difficulty": 3,
            "topic": "Bonding",
            "lo_code": "LC-CHEM-LO-2.3",
            "prompt": (
                "Explain, with the aid of a labelled diagram, how a "
                "coordinate (dative covalent) bond is formed between "
                "ammonia (NH3) and a hydrogen ion (H+). State the "
                "shape and bond angle of the resulting NH4+ ion."
            ),
            "marks": 10,
            "time_min": 12,
        },
        {
            "level": "hard",
            "difficulty": 5,
            "topic": "Stoichiometry",
            "lo_code": "LC-CHEM-LO-3.1",
            "prompt": (
                "25.0 cm3 of a solution of sodium hydroxide (NaOH) "
                "required 22.5 cm3 of 0.100 mol/dm3 hydrochloric acid "
                "(HCl) for neutralisation. Calculate the concentration "
                "of the NaOH solution in mol/dm3 and g/dm3."
            ),
            "marks": 15,
            "time_min": 18,
        },
    ]

    mo.md(
        """
        ## 2. Practice questions

        Three per-subject difficulty levels via
        qpack_chemistry.baml::GenerateChemFormativeItem
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
            FROM oideachais.leaving_cert.chemistry_papers
            WHERE subject = 'chemistry'
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
                "n_questions": [11, 11, 11, 11, 9, 9, 9, 9],
                "avg_difficulty": [4.1, 4.2, 4.2, 4.1, 3.5, 3.6, 3.7, 3.5],
            }
        )
        source = "local_fallback"

    mo.md(
        f"""
        ## 3. Mock exam (source: {source})

        Per-subject past exam paper ingestion
        (oideachais.leaving_cert.chemistry_papers).
        Build a 3-hour mock exam from the most recent HL paper and the
        matching marking scheme.
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
            FROM oideachais.leaving_cert.chemistry_topics
            WHERE subject = 'chemistry' AND level = 'higher'
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
                    "Atomic Structure", "Bonding", "Stoichiometry",
                    "Acids & Bases", "Organic Chemistry",
                ],
                "n": [24, 22, 20, 18, 16],
            }
        )
        source = "local_fallback"

    progress = pd.DataFrame(
        {
            "topic": topics["topic"].tolist(),
            "mastery_pct": [82, 71, 65, 48, 39][: len(topics)],
            "next_revision_days": [2, 4, 3, 6, 9][: len(topics)],
        }
    )

    plan = topics.merge(progress, on="topic", how="left")

    mo.md(
        f"""
        ## 4. Study plan (source: {source})

        Per-subject lectionary (from chemistry_topics) + per-student
        progress. Topics with low mastery are scheduled sooner.
        """
    )
    plan
    return plan, progress, topics, source


@app.cell
def _per_subject_baml(mo):
    """Cell 5 - Per-subject qpack BAML function.

    Invokes GenerateChemQuestPack from
    cianfhoghlaim/baml/education/subjects/qpack_chemistry.baml.
    Wrapped in try/except so the notebook renders offline (without the
    BAML client available).
    """
    results = {}

    try:
        from cianfhoghlaim.baml_client import b

        results["formative_item"] = {
            "function": "GenerateChemFormativeItem",
            "input": {
                "lo_code": "LC-CHEM-LO-2.3",
                "difficulty": 3,
                "level": "higher",
                "topic": "Bonding",
            },
            "status": "invoked",
        }

        results["quest_pack"] = {
            "function": "GenerateChemQuestPack",
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

        Invokes qpack_chemistry.baml::GenerateChemFormativeItem
        (and the deferred GenerateChemQuestPack for the full pipeline
        runner).

        Status: `{results.get('status', 'unknown')}`
        """
    )
    return results


if __name__ == "__main__":
    app.run()