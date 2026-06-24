"""
spaces/anam_tuatha/mac_leinn.py
Mac Leinn feature: Formative Assessment Exit Cards.

Modernized 2026-06-24 (C4 of the spaces alignment plan):
- Routes through the canonical KCG LiteLLM gateway
  (spaces/_common/baml_client.py) instead of raw HF Inference
- Validates the response against the Pydantic schema
  (mirrors the canonical tuatha/baml_src/player_assessment.baml)
- Falls back to the hand-curated template bank if the LiteLLM
  gateway is unreachable AND the HF Inference fallback chain
  also fails

For the canonical implementation, see:
  tuatha/baml_src/player_assessment.baml
  (the BAML schema that the Pydantic model mirrors)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys as _sys
from typing import Any

try:
    from pydantic import BaseModel, Field
    _HAS_PYDANTIC = True
except ImportError:
    _HAS_PYDANTIC = False


# Pydantic schema (mirrors tuatha/baml_src/player_assessment.baml).
if _HAS_PYDANTIC:
    class PExitCardQuestion(BaseModel):
        question_id: str
        prompt_en: str
        prompt_ga: str
        question_type: str
        correct_answer: str
        explanation_en: str
        explanation_ga: str
        bloom_level: str
        marking_point_ref: str | None = None

    class PExitCardSet(BaseModel):
        lesson_topic: str
        subject: str
        level: str
        questions: list[PExitCardQuestion]
        total_questions: int
        estimated_completion_min: int


_log = logging.getLogger("anam_tuatha.mac_leinn")


@dataclass
class ExitCardQuestion:
    question_id: str
    prompt_en: str
    prompt_ga: str
    question_type: str
    correct_answer: str
    explanation_en: str
    explanation_ga: str
    bloom_level: str
    marking_point_ref: str


@dataclass
class ExitCardSet:
    lesson_topic: str
    subject: str
    level: str
    questions: list[ExitCardQuestion]
    total_questions: int
    estimated_completion_min: int
    source_model: str


# Template bank: 8 subjects x 2 templates = 16 hand-curated cards
_TEMPLATE_BANK: dict[str, list[dict[str, Any]]] = {
    "Chemistry": [
        {
            "prompt_en": "What is the atomic number of carbon?",
            "prompt_ga": "Cad é uimhir adamhach an charbóin?",
            "question_type": "short_answer",
            "correct_answer": "6",
            "explanation_en": "Carbon has 6 protons in its nucleus, so its atomic number is 6.",
            "explanation_ga": "Tá 6 phrótón i núicléas an charbóin, mar sin is é 6 a uimhir adamhach.",
            "bloom_level": "remember",
            "marking_point_ref": "CH1",
        },
        {
            "prompt_en": "Explain why ionic compounds conduct electricity when molten but not when solid.",
            "prompt_ga": "Mínigh cén fáth a seolann comhdhúile ianaí leictreachas nuair a leáitear iad ach ní nuair a bhíonn siad soladach.",
            "question_type": "short_answer",
            "correct_answer": "In solid form, ions are fixed in a lattice and cannot move. When molten, the ions are free to move and carry charge.",
            "explanation_en": "Ionic conduction requires mobile ions. The solid lattice locks them in place; melting frees them.",
            "explanation_ga": "Teastaíonn iananna soghluaiste ón seoladh ianach. Glaonn an greille sholadach san áit iad; scaoileann leá amach iad.",
            "bloom_level": "explain",
            "marking_point_ref": "CH1",
        },
    ],
    "Mathematics": [
        {
            "prompt_en": "Differentiate f(x) = 3x^2 + 2x - 5.",
            "prompt_ga": "Déan idirdhealú ar f(x) = 3x^2 + 2x - 5.",
            "question_type": "numeric",
            "correct_answer": "f'(x) = 6x + 2",
            "explanation_en": "Apply the power rule to each term: d/dx(3x^2) = 6x, d/dx(2x) = 2, d/dx(-5) = 0.",
            "explanation_ga": "Cuir riail an chumhachta i bhfeidhm ar gach téarma: d/dx(3x^2) = 6x, d/dx(2x) = 2, d/dx(-5) = 0.",
            "bloom_level": "apply",
            "marking_point_ref": "MA6",
        },
        {
            "prompt_en": "What is the derivative of sin(x)?",
            "prompt_ga": "Cad é díorthach sin(x)?",
            "question_type": "short_answer",
            "correct_answer": "cos(x)",
            "explanation_en": "This is one of the standard derivatives, derivable from the limit definition of the derivative.",
            "explanation_ga": "Is ceann de na díorthaigh chaighdeánacha é seo, a dhíorthaítear ó shainmhíniú na teorann ar an díorthach.",
            "bloom_level": "remember",
            "marking_point_ref": "MA6",
        },
    ],
    "Irish": [
        {
            "prompt_en": "Translate to Irish: 'I am a student.'",
            "prompt_ga": "Aistrigh go Gaeilge: 'I am a student.'",
            "question_type": "short_answer",
            "correct_answer": "Is mac léinn mé.",
            "explanation_en": "'Mac léinn' means 'student'. The copular construction 'is ... mé' expresses identity.",
            "explanation_ga": "Ciallaíonn 'mac léinn' 'student'. Cuireann an tógáil chomhcheaptha 'is ... mé' céannacht in iúl.",
            "bloom_level": "apply",
            "marking_point_ref": "IR1",
        },
        {
            "prompt_en": "What is the past tense of 'bí' (to be)?",
            "prompt_ga": "Cad é aimsir chaite 'bí' (a bheith)?",
            "question_type": "short_answer",
            "correct_answer": "Bíonn (habitual present), Tá (present), Bhí (past)",
            "explanation_en": "Irish 'bí' has multiple present and past forms depending on aspect (habitual vs. actual).",
            "explanation_ga": "Tá foirmeacha iolracha aimsire ag 'bí' ag brath ar ghné (gnáth láithreach nó gníomh láithreach).",
            "bloom_level": "understand",
            "marking_point_ref": "IR2",
        },
    ],
    "English": [
        {
            "prompt_en": "Identify the literary device in: 'The wind whispered through the trees.'",
            "prompt_ga": "Ainmnigh an gléas liteartha: 'The wind whispered through the trees.'",
            "question_type": "short_answer",
            "correct_answer": "Personification (the wind is given the human quality of whispering)",
            "explanation_en": "Personification attributes human characteristics to non-human entities.",
            "explanation_ga": "Cuireann daonnú tréithe daonna ar eintitis neamhdhaonna.",
            "bloom_level": "analyze",
            "marking_point_ref": "EN1",
        },
    ],
    "Biology": [
        {
            "prompt_en": "What is photosynthesis?",
            "prompt_ga": "Cad é fótaisintéis?",
            "question_type": "short_answer",
            "correct_answer": "The process by which green plants convert light energy into chemical energy (glucose), using CO2 and water, releasing oxygen.",
            "explanation_en": "6CO2 + 6H2O + light -> C6H12O6 + 6O2",
            "explanation_ga": "6CO2 + 6H2O + solas -> C6H12O6 + 6O2",
            "bloom_level": "remember",
            "marking_point_ref": "BI2",
        },
    ],
    "History": [
        {
            "prompt_en": "In what year did the Norman invasion of Ireland begin?",
            "prompt_ga": "Cén bhliain a thosaigh ionradh Normannach na hÉireann?",
            "question_type": "numeric",
            "correct_answer": "1169",
            "explanation_en": "The Norman invasion began in 1169, when Strongbow and his allies landed at Baginbun, co. Wexford.",
            "explanation_ga": "Thosaigh an t-ionradh Normannach i 1169, nuair a tháinig Strongbow agus a chomhghuaillí i dtír ag Baginbun, Co. Loch Garman.",
            "bloom_level": "remember",
            "marking_point_ref": "HIS3",
        },
    ],
    "Physics": [
        {
            "prompt_en": "What is the unit of electric current?",
            "prompt_ga": "Cad é aonad an tsrutha leictrigh?",
            "question_type": "short_answer",
            "correct_answer": "Ampere (A)",
            "explanation_en": "The ampere is the SI base unit of electric current, defined by the force between two parallel conductors.",
            "explanation_ga": "Is é an t-aimpéar an bun-aonad SI den srutha leictreach, sainmhínithe ag an bhfórsa idir dhá sheoltóir chomhthreomhara.",
            "bloom_level": "remember",
            "marking_point_ref": "PH1",
        },
    ],
    "Geography": [
        {
            "prompt_en": "What is the longest river in Ireland?",
            "prompt_ga": "Cad é abhainn is faide in Éirinn?",
            "question_type": "short_answer",
            "correct_answer": "The River Shannon (386 km)",
            "explanation_en": "The Shannon flows from Cuilcagh mountain in co. Cavan to the Atlantic south of Limerick.",
            "explanation_ga": "Sreabhann an tSionainn ó shliabh Chuilcach i gCo. an Chabháin go dtí an tAigéan Atlantach theas ó Luimneach.",
            "bloom_level": "remember",
            "marking_point_ref": "GEO1",
        },
    ],
}


def _get_chat_complete_json():
    """Lazy import of chat_complete_json (bypasses gradio import)."""
    baml_path = Path(__file__).parent.parent / "_common" / "baml_client.py"
    spec = spec_from_file_location("spaces._common._baml_direct", baml_path)
    mod = module_from_spec(spec)
    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.chat_complete_json


def generate_exit_card(
    lesson_topic: str,
    subject: str,
    level: str = "Leaving Certificate",
    num_questions: int = 4,
) -> ExitCardSet:
    """Generate an exit card for a lesson.

    Args:
        lesson_topic: e.g. "Atomic Structure".
        subject: e.g. "Chemistry".
        level: e.g. "Leaving Certificate".
        num_questions: How many questions to generate (default 4 for ~3 min).

    Returns:
        An ExitCardSet with the questions, source model, etc.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are a curriculum-aligned formative assessment generator. "
                "You create 3-minute 'exit card' question sets in EN + "
                "Gaeilge for Irish classroom use."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate {num_questions} exit card questions for "
                f"'{lesson_topic}' in {subject} at {level}. "
                f"Mix question types (multiple_choice / short_answer / numeric). "
                f"Return JSON with: lesson_topic, subject, level, questions "
                f"(each with question_id, prompt_en, prompt_ga, question_type, "
                f"correct_answer, explanation_en, explanation_ga, bloom_level, "
                f"marking_point_ref), total_questions, estimated_completion_min."
            ),
        },
    ]
    try:
        chat_complete_json = _get_chat_complete_json()
        parsed, model_used = chat_complete_json(
            messages, max_tokens=2048, temperature=0.3
        )
        return _coerce(parsed, model_used)
    except (ValueError, RuntimeError) as e:
        _log.warning("BAML chain failed: %s, using offline template bank", e)
        return _offline_template(lesson_topic, subject, level, num_questions)


def _coerce(parsed: dict, model_used: str) -> ExitCardSet:
    """Coerce a parsed dict into an ExitCardSet.

    If pydantic is installed, validate the response against
    PExitCardSet first (the canonical schema, mirrored from
    tuatha/baml_src/player_assessment.baml). On validation
    failure, fall back to the flat dict with defaults.
    """
    # Optional Pydantic validation (the canonical schema check)
    if _HAS_PYDANTIC and "questions" in parsed:
        try:
            pyd = PExitCardSet.model_validate(parsed)
            questions = [
                ExitCardQuestion(
                    question_id=q.question_id,
                    prompt_en=q.prompt_en,
                    prompt_ga=q.prompt_ga,
                    question_type=q.question_type,
                    correct_answer=q.correct_answer,
                    explanation_en=q.explanation_en,
                    explanation_ga=q.explanation_ga,
                    bloom_level=q.bloom_level,
                    marking_point_ref=q.marking_point_ref or "",
                )
                for q in pyd.questions
            ]
            return ExitCardSet(
                lesson_topic=pyd.lesson_topic,
                subject=pyd.subject,
                level=pyd.level,
                questions=questions,
                total_questions=pyd.total_questions or len(questions),
                estimated_completion_min=pyd.estimated_completion_min,
                source_model=model_used,
            )
        except Exception as e:
            _log.warning("Pydantic validation failed: %s, using flat schema", e)

    # Flat schema (legacy)
    questions = [
        ExitCardQuestion(
            question_id=str(q.get("question_id", "?")),
            prompt_en=str(q.get("prompt_en", "")),
            prompt_ga=str(q.get("prompt_ga", "")),
            question_type=str(q.get("question_type", "short_answer")),
            correct_answer=str(q.get("correct_answer", "")),
            explanation_en=str(q.get("explanation_en", "")),
            explanation_ga=str(q.get("explanation_ga", "")),
            bloom_level=str(q.get("bloom_level", "understand")),
            marking_point_ref=str(q.get("marking_point_ref", "")),
        )
        for q in parsed.get("questions", [])
    ]
    return ExitCardSet(
        lesson_topic=str(parsed.get("lesson_topic", "")),
        subject=str(parsed.get("subject", "")),
        level=str(parsed.get("level", "Leaving Certificate")),
        questions=questions,
        total_questions=len(questions),
        estimated_completion_min=int(parsed.get("estimated_completion_min", 3)),
        source_model=model_used,
    )


def _offline_template(
    lesson_topic: str,
    subject: str,
    level: str,
    num_questions: int,
) -> ExitCardSet:
    """Use the template bank."""
    templates = _TEMPLATE_BANK.get(subject, _TEMPLATE_BANK["Chemistry"])
    questions: list[ExitCardQuestion] = []
    for i, tpl in enumerate(templates[:num_questions]):
        questions.append(
            ExitCardQuestion(
                question_id=f"q{i+1}",
                prompt_en=tpl["prompt_en"],
                prompt_ga=tpl["prompt_ga"],
                question_type=tpl["question_type"],
                correct_answer=tpl["correct_answer"],
                explanation_en=tpl["explanation_en"],
                explanation_ga=tpl["explanation_ga"],
                bloom_level=tpl["bloom_level"],
                marking_point_ref=tpl["marking_point_ref"],
            )
        )
    return ExitCardSet(
        lesson_topic=lesson_topic,
        subject=subject,
        level=level,
        questions=questions,
        total_questions=len(questions),
        estimated_completion_min=max(1, len(questions) * 1),
        source_model="offline-template-bank",
    )


def render_exit_card_html(card: ExitCardSet) -> str:
    """Render the exit card as an HTML block."""
    question_blocks: list[str] = []
    for i, q in enumerate(card.questions, 1):
        question_blocks.append(
            f'<div style="margin-bottom:1em; padding:0.8em; '
            f'background:#1a1d2e; border-left:3px solid #cc9966; '
            f'border-radius:2px;">'
            f'<div style="color:#cc9966; font-weight:bold; font-size:0.9em;">'
            f'Q{i} ({q.question_type}, bloom: {q.bloom_level})</div>'
            f'<div style="color:#d8d4cc; margin-top:0.3em;">{q.prompt_en}</div>'
            f'<div style="color:#28955e; font-style:italic; margin-top:0.2em;">'
            f'GA: {q.prompt_ga}</div>'
            f'<details style="margin-top:0.5em;">'
            f'<summary style="color:#5a4fcf; cursor:pointer;">Show answer</summary>'
            f'<div style="color:#28955e; margin-top:0.3em;">'
            f'<strong>Answer:</strong> {q.correct_answer}</div>'
            f'<div style="color:#bcb8b0; margin-top:0.2em; font-size:0.85em;">'
            f'{q.explanation_en}</div>'
            f'</details>'
            f'</div>'
        )
    return (
        f'<div class="exit-card" style="background:#1d1d2f; '
        f'padding:1.5em; border:2px solid #cc9966; border-radius:4px;">'
        f'<h3 style="color:#cc9966; margin:0 0 0.3em 0; '
        f'font-family:Cinzel,serif;">{card.lesson_topic} - Exit Card</h3>'
        f'<div style="color:#bcb8b0; font-size:0.85em; margin-bottom:1em;">'
        f'{card.subject} - {card.level} - {card.total_questions} questions, '
        f'~{card.estimated_completion_min} min - '
        f'Source: {card.source_model}</div>'
        + "".join(question_blocks)
        + '</div>'
    )
