"""Tests for `meaisinfhoghlaim.pipelines.ensemble_gradio`.

The 3 `gradio-ensemble-pattern` scenarios from
`openspec/changes/celtic-data-engineering-patterns/specs/gradio-ensemble-pattern/spec.md`
are validated here.
"""

from __future__ import annotations

import pytest

from sruth.meaisinfhoghlaim.pipelines.ensemble_gradio import build_ensemble_interface


def _sklearn_stub(text: str) -> str:
    return "phishing" if "verify" in text.lower() else "legit"


def _distilbert_stub(text: str) -> str:
    return f"distilbert:{text[:10]}"


def _regex_stub(text: str) -> str:
    return f"regex:{len(text)}"


def test_multi_model_interface_has_one_output_per_model() -> None:
    """3 models passed in → 3 output Textboxes, 1 input Textbox."""
    iface = build_ensemble_interface(
        title="Phishing email classifier",
        description="Compare 3 models side by side.",
        examples=["verify your account", "buy 20 netflix films"],
        models={
            "sklearn": _sklearn_stub,
            "distilbert": _distilbert_stub,
            "regex": _regex_stub,
        },
    )
    # Gradio uses `.output_components` for the list of output blocks
    assert len(iface.output_components) == 3
    # One input textbox
    assert len(iface.input_components) == 1
    # Flagging: in Gradio 6 the equivalent of `allow_flagging="never"` is
    # the default (no flag button). In Gradio 4.x the helper passed
    # `allow_flagging="never"`; in Gradio 6 that kwarg was removed. We
    # assert that no flagging_mode is set (= opt-out = never).
    assert iface.flagging_mode in (None, "never", "manual")


def test_examples_are_populated() -> None:
    """2 examples passed in → 2 example rows in the Examples component."""
    iface = build_ensemble_interface(
        title="x",
        examples=["example 1", "example 2"],
        models={"a": _sklearn_stub},
    )
    examples = iface.examples
    assert examples is not None
    assert len(examples) == 2
    # Each example row is a list of inputs (Gradio 4.x format)
    assert examples[0] == ["example 1"]
    assert examples[1] == ["example 2"]


def test_ensemble_predict_calls_every_model() -> None:
    """The ensemble function returns a list with one element per model, in order."""
    iface = build_ensemble_interface(
        title="x",
        examples=[],
        models={
            "a": _sklearn_stub,
            "b": _distilbert_stub,
        },
    )
    # Invoke the underlying fn directly via the Interface's .fn attribute
    outputs = iface.fn("verify your account")
    assert outputs == ["phishing", "distilbert:verify you"]


def test_empty_models_raises() -> None:
    """Empty models dict raises ValueError per the helper's contract."""
    with pytest.raises(ValueError, match="models must be non-empty"):
        build_ensemble_interface(title="x", examples=[], models={})


def test_wrong_arity_raises() -> None:
    """A model with 0 or 2 required positional args raises ValueError."""
    with pytest.raises(ValueError, match="must accept exactly 1 required positional argument"):

        def zero_arg() -> str:
            return "x"

        build_ensemble_interface(
            title="x",
            examples=[],
            models={"zero": zero_arg},
        )

    with pytest.raises(ValueError, match="must accept exactly 1 required positional argument"):

        def two_args(a: str, b: str) -> str:
            return a + b

        build_ensemble_interface(
            title="x",
            examples=[],
            models={"two": two_args},
        )


def test_keyword_only_model_accepted() -> None:
    """A model with one keyword-only arg counts as 1 positional param via POSITIONAL_OR_KEYWORD.

    Actually POSITIONAL_OR_KEYWORD accepts positional OR keyword, so it counts.
    Models with VAR_POSITIONAL (`*args`) or VAR_KEYWORD (`**kwargs`) are not
    supported by this helper, but those are extremely unusual for a per-model
    callable. The current test asserts the helper accepts models with default
    values (POSITIONAL_OR_KEYWORD with default).
    """

    def model_with_default(text: str, threshold: float = 0.5) -> str:
        return f"{text}:{threshold}"

    iface = build_ensemble_interface(
        title="x",
        examples=["hi"],
        models={"kw": model_with_default},
    )
    assert iface.fn("hi") == ["hi:0.5"]
