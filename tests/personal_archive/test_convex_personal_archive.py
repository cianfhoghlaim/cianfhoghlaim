"""Tests for the Convex actions / queries
`web/apps/cianfhoghlaim/convex/personalArchive.ts`.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).

The file must export the 5 expected symbols:
  1. `chatOverMyArchive`         (action)
  2. `getModuleDossier`          (query)
  3. `getQuestionsForTopic`      (query)
  4. `getMyAnswerForQuestion`    (query)
  5. `searchSimilarQuestions`    (action)
"""
from __future__ import annotations

import re
from pathlib import Path


_CONVEX_TS = Path(
    "/Users/cianmacandeisigh/dev/kings_college_galway/web/apps/cianfhoghlaim/convex/personalArchive.ts"
)


def _expected_symbols() -> set[str]:
    return {
        "chatOverMyArchive",
        "getModuleDossier",
        "getQuestionsForTopic",
        "getMyAnswerForQuestion",
        "searchSimilarQuestions",
    }


def test_convex_personal_archive_exports_5_symbols() -> None:
    """The TypeScript file must export the 5 expected symbols."""
    assert _CONVEX_TS.exists(), f"Convex file not found at {_CONVEX_TS}"
    text = _CONVEX_TS.read_text(encoding="utf-8")
    expected = _expected_symbols()
    found: set[str] = set()
    for match in re.finditer(
        r"export\s+const\s+(\w+)\s*=\s*(?:action|query)\b", text
    ):
        found.add(match.group(1))
    missing = expected - found
    assert not missing, f"Missing expected exports: {sorted(missing)}"
    # We do not assert `found == expected` because the file may have
    # additional helper exports; we only care that the 5 expected
    # symbols are present.
