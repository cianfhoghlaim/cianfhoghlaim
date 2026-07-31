"""UC 4: QualificationNormalizer (LC <-> GCSE <-> A-Level).

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 3).

The canonical LC <-> GCSE <-> A-Level normalizer. Bridges:
  - Ireland Leaving Certificate (LC) <-> England GCSE / A-Level
  - Ireland Junior Cycle (JC) <-> England GCSE (via the cross-qualification map)
  - Generalisable to Scotland (Nat 5 / Higher / Adv Higher) later

Uses the canonical cross_qualification_subject_map (Plan 3 module 6)
to declare subject equivalences (e.g. Chemistry LC <-> A-Level Chemistry
with equivalence_strength=0.95).
"""

from __future__ import annotations

import logging
from typing import Any

from meaisinfoghlaim.alignment.cross_qualification_subject_map import (
    CrossQualificationSubjectMap,
)
from meaisinfoghlaim.alignment.schema import (
    Board,
    QualificationEquivalence,
    QualificationLevel,
)

logger = logging.getLogger(__name__)


class QualificationNormalizer:
    """The canonical cross-qualification normalizer.

    Wraps the canonical CrossQualificationSubjectMap + provides the
    canonical subject/cohort lookup by (qualification, jurisdiction, subject).
    Stateless beyond the cross_qualification_subject_map collaborator.
    """

    def __init__(self, subject_map=None) -> None:
        self.subject_map = subject_map or CrossQualificationSubjectMap()

    def normalize(
        self,
        qualification: QualificationLevel,
        jurisdiction: str,
        subject: str,
        board: Board = Board.NONE,
    ) -> list:
        """Return all equivalences for the given (qualification, jurisdiction, subject).

        Returns:
            list of QualificationEquivalence rows where this cohort is either
            the a-side OR the b-side. The equivalence_strength is the confidence.
        """
        all_equivalences = self.subject_map.all()
        out = []
        for equiv in all_equivalences:
            a_match = (
                equiv.qualification_a == qualification
                and equiv.jurisdiction_a == jurisdiction
                and equiv.subject_a == subject
                and (equiv.board_a == board or equiv.board_a == Board.NONE)
            )
            b_match = (
                equiv.qualification_b == qualification
                and equiv.jurisdiction_b == jurisdiction
                and equiv.subject_b == subject
                and (equiv.board_b == board or equiv.board_b == Board.NONE)
            )
            if a_match or b_match:
                out.append(equiv)
        return out

    def equivalent_subjects(
        self,
        qualification: QualificationLevel,
        jurisdiction: str,
        subject: str,
        board: Board = Board.NONE,
        min_strength: float = 0.5,
    ) -> list:
        """Return the list of equivalent (qualification, jurisdiction, subject) tuples.

        Useful for building cross-jurisdiction comparison pipelines.
        """
        equivalences = self.normalize(qualification, jurisdiction, subject, board)
        out = []
        for equiv in equivalences:
            if equiv.equivalence_strength < min_strength:
                continue
            # Determine which side is "self" and which is "the other"
            if (
                equiv.qualification_a == qualification
                and equiv.jurisdiction_a == jurisdiction
                and equiv.subject_a == subject
                and (equiv.board_a == board or equiv.board_a == Board.NONE)
            ):
                out.append((equiv.qualification_b, equiv.jurisdiction_b, equiv.subject_b, equiv.equivalence_strength))
            else:
                out.append((equiv.qualification_a, equiv.jurisdiction_a, equiv.subject_a, equiv.equivalence_strength))
        return out


__all__ = ["QualificationNormalizer", "QualificationEquivalence", "QualificationLevel", "Board"]
