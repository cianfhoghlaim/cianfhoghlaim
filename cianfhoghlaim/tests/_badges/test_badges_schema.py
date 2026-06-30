"""Tests for cianfhoghlaim.badges (the hybrid x402 educational credential).

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone

import pytest

from cianfhoghlaim.badges import (
    BilingualText,
    CredentialAnchor,
    EvidenceLink,
    MerkleBatch,
    SkillTreeBadge,
)
from cianfhoghlaim.badges.anchor import compute_merkle_root, verify_merkle_path


# ============================================================================
# Schema tests
# ============================================================================

class TestSkillTreeBadge:
    def test_minimal_badge(self):
        """The smallest valid badge."""
        badge = SkillTreeBadge(
            id="test-uuid-1",
            student_id="hash-of-pseudonym+salt",
            framework="ncca-lc",
            level="hl",
            subject="mathematics",
            competency_code="LC-MATHS-LO-2.4",
            competency_text={"text_en": "Differentiate polynomial", "text_ga": None},
            date_earned=datetime.now(tz=timezone.utc),
            agent_issuer="math_agent",
            evidence=EvidenceLink(
                item_id="item-1",
                response="f(x) = 2x",
                score_pct=85.0,
                feedback_en="Correct!",
            ),
            evidence_hash=hashlib.sha256(b"test").hexdigest(),
            signature="0x-signature",
        )
        assert badge.subject == "mathematics"
        assert badge.framework == "ncca-lc"
        assert badge.level == "hl"
        assert badge.competency_text.text_ga is None  # Math is EN-only

    def test_gael_badge_with_both_languages(self):
        """A Gaeilge badge should support both text_ga and text_en."""
        badge = SkillTreeBadge(
            id="test-uuid-2",
            student_id="hash-of-pseudonym+salt",
            framework="ncca-lc",
            level="ol",
            subject="gaeilge",
            competency_code="LC-GAEL-LO-3.1",
            competency_text={
                "text_en": "Reading comprehension of a news article",
                "text_ga": "Léamhthuiscint nuachtlitir",
            },
            date_earned=datetime.now(tz=timezone.utc),
            agent_issuer="gael_agent",
            evidence=EvidenceLink(
                item_id="item-2",
                response="Sample student response in Irish",
                score_pct=92.0,
                feedback_ga="Maith an iarracht!",
                feedback_en="Well done!",
            ),
            evidence_hash=hashlib.sha256(b"test2").hexdigest(),
            signature="0x-sig-2",
        )
        assert badge.subject == "gaeilge"
        assert badge.competency_text.text_en == "Reading comprehension of a news article"
        assert badge.competency_text.text_ga == "Léamhthuiscint nuachtlitir"
        assert badge.evidence.feedback_ga == "Maith an iarracht!"

    def test_badge_with_on_chain_anchor(self):
        """A badge that has been anchored on Base L2."""
        badge = SkillTreeBadge(
            id="test-uuid-3",
            student_id="hash-of-pseudonym+salt",
            framework="ncca-lc",
            level="hl",
            subject="chemistry",
            competency_code="LC-CHEM-LO-2.4",
            competency_text={"text_en": "Atomic structure", "text_ga": None},
            date_earned=datetime.now(tz=timezone.utc),
            agent_issuer="chem_agent",
            evidence=EvidenceLink(
                item_id="item-3",
                response="1s2 2s2 2p6 3s2",
                score_pct=88.0,
                feedback_en="Correct electron configuration",
            ),
            evidence_hash=hashlib.sha256(b"test3").hexdigest(),
            signature="0x-sig-3",
            on_chain_anchor="0xabc123",
            anchor_date="2026-07-01",
        )
        assert badge.on_chain_anchor == "0xabc123"
        assert badge.anchor_date == "2026-07-01"


class TestEvidenceLink:
    def test_minimal_evidence(self):
        ev = EvidenceLink(
            item_id="item-1",
            response="2 + 2 = 4",
            score_pct=100.0,
            feedback_en="Correct",
        )
        assert ev.score_pct == 100.0
        assert ev.source_pdf is None
        assert ev.source_page is None

    def test_full_evidence(self):
        ev = EvidenceLink(
            item_id="item-2",
            response="f'(x) = 2x + 3",
            score_pct=85.0,
            feedback_en="Step 1 correct; minor arithmetic error",
            feedback_ga="Céim 1 ceart; earráid bheag",
            source_pdf="LC-Maths-paper-2024.pdf",
            source_page=12,
        )
        assert ev.source_page == 12
        assert ev.feedback_ga == "Céim 1 ceart; earráid bheag"


# ============================================================================
# Merkle tree tests
# ============================================================================

class TestMerkleTree:
    """Test the Merkle root computation + path verification."""

    def test_compute_merkle_root_empty(self):
        """Empty list → hash of empty string."""
        root = compute_merkle_root([])
        assert root == hashlib.sha256(b"").hexdigest()

    def test_compute_merkle_root_single(self):
        """Single leaf → hash of that leaf."""
        leaf = hashlib.sha256(b"badge-1").hexdigest()
        root = compute_merkle_root([leaf])
        assert root == leaf

    def test_compute_merkle_root_deterministic(self):
        """Same input → same output (sorted lexicographically)."""
        leaves = [hashlib.sha256(f"badge-{i}".encode()).hexdigest() for i in range(5)]
        # Even unsorted input should produce the same root (sorting is internal)
        sorted_leaves = sorted(leaves)
        reversed_leaves = list(reversed(leaves))
        root1 = compute_merkle_root(sorted_leaves)
        root2 = compute_merkle_root(reversed_leaves)
        assert root1 == root2

    def test_compute_merkle_root_two_leaves(self):
        """Two leaves: H(H(a) + H(b))."""
        a = "0" * 64  # placeholder
        b = "1" * 64
        root = compute_merkle_root([a, b])
        # Since sorted_leaves = [a, b] (lex), pair is a+b
        expected = hashlib.sha256((a + b).encode()).hexdigest()
        assert root == expected

    def test_compute_merkle_root_odd_number(self):
        """Odd number of leaves: the last leaf is duplicated (Bitcoin-style)."""
        a = "a" * 64
        b = "b" * 64
        c = "c" * 64
        root = compute_merkle_root([a, b, c])
        # After sorting: [a, b, c]. Pair a+b → H(a+b), then c duplicated: H(c+c)
        pair_ab = hashlib.sha256((a + b).encode()).hexdigest()
        expected = hashlib.sha256((c + c).encode()).hexdigest()
        # Wait — that's not right; the root should be H(H(a+b) + H(c+c))
        # Actually let me trace through the algorithm:
        # leaves sorted: [a, b, c]
        # next_level[0] = H(a+b), next_level[1] = H(c+c)
        # next level: [H(a+b), H(c+c)]
        # root = H(H(a+b) + H(c+c))
        expected_root = hashlib.sha256(
            (pair_ab + expected).encode()
        ).hexdigest()
        assert root == expected_root

    def test_verify_merkle_path_single_leaf(self):
        """A single-leaf tree's root equals the leaf."""
        leaf = hashlib.sha256(b"only-badge").hexdigest()
        root = compute_merkle_root([leaf])
        assert verify_merkle_path(leaf, root, []) is True
        assert verify_merkle_path(leaf, root, []) is True

    def test_verify_merkle_path_correct(self):
        """Correct path → True."""
        a = "0" * 64
        b = "1" * 64
        # In a 2-leaf tree: sorted = [a, b], pair = a+b
        # For leaf 'a' (index 0), sibling is 'b' on the RIGHT
        # path: [(b, "right")]
        root = compute_merkle_root([a, b])
        assert verify_merkle_path(a, root, [(b, "right")]) is True

    def test_verify_merkle_path_incorrect(self):
        """Wrong root → False."""
        leaf = "0" * 64
        wrong_root = "f" * 64
        assert verify_merkle_path(leaf, wrong_root, []) is False


# ============================================================================
# MerkleBatch tests
# ============================================================================

class TestMerkleBatch:
    def test_minimal_batch(self):
        batch = MerkleBatch(
            id="batch-2026-07-01",
            batch_date="2026-07-01",
            merkle_root="0xabc",
            leaf_count=10,
            badge_ids=["badge-1", "badge-2"],
            tx_hash="0xtx",
            published_at=datetime.now(tz=timezone.utc),
        )
        assert batch.leaf_count == 10
        assert batch.batch_date == "2026-07-01"
        assert len(batch.badge_ids) == 2

    def test_pending_batch_no_tx_hash(self):
        """A batch that hasn't been published to Base L2 yet."""
        batch = MerkleBatch(
            id="batch-pending",
            batch_date="2026-07-02",
            merkle_root="0xdef",
            leaf_count=5,
            badge_ids=["badge-3"],
        )
        assert batch.tx_hash is None
        assert batch.published_at is None


# ============================================================================
# CredentialAnchor tests
# ============================================================================

class TestCredentialAnchor:
    def test_anchor_record(self):
        anchor = CredentialAnchor(
            batch_id="2026-07-01",
            merkle_root="0xabc",
            timestamp=1719849600,
            tx_hash="0xdef",
        )
        assert anchor.batch_id == "2026-07-01"
        assert anchor.timestamp == 1719849600


# ============================================================================
# Pytest fixtures
# ============================================================================

@pytest.fixture
def sample_evidence():
    return EvidenceLink(
        item_id="item-test-1",
        response="x = 5",
        score_pct=85.0,
        feedback_en="Correct approach, minor arithmetic error",
        feedback_ga="Cur chuige ceart, earráid bheag",
        source_pdf="LC-Maths-paper-2024.pdf",
        source_page=5,
    )


@pytest.fixture
def sample_badge(sample_evidence):
    return SkillTreeBadge(
        id="badge-test-1",
        student_id="hash-of-pseudonym+salt",
        framework="ncca-lc",
        level="hl",
        subject="mathematics",
        competency_code="LC-MATHS-LO-2.4",
        competency_text={
            "text_en": "Differentiate polynomial functions",
            "text_ga": None,
        },
        date_earned=datetime.now(tz=timezone.utc),
        agent_issuer="math_agent",
        evidence=sample_evidence,
        evidence_hash=hashlib.sha256(b"sample").hexdigest(),
        signature="0x-sig-test",
    )


@pytest.fixture
def gael_badge(sample_evidence):
    return SkillTreeBadge(
        id="badge-gaeilge-1",
        student_id="hash-of-pseudonym+salt",
        framework="ncca-lc",
        level="hl",
        subject="gaeilge",
        competency_code="LC-GAEL-LO-3.1",
        competency_text={
            "text_en": "Reading comprehension",
            "text_ga": "Léamhthuiscint",
        },
        date_earned=datetime.now(tz=timezone.utc),
        agent_issuer="gael_agent",
        evidence=EvidenceLink(
            item_id="item-gaeilge-1",
            response="Sample Irish response",
            score_pct=92.0,
            feedback_ga="Maith an iarracht!",
            feedback_en="Well done!",
        ),
        evidence_hash=hashlib.sha256(b"gaeilge-1").hexdigest(),
        signature="0x-sig-gaeilge",
    )


# ============================================================================
# Cross-subject Merkle batch tests (real-world scenario)
# ============================================================================

class TestEndToEndScenario:
    """End-to-end test: issue badges for 3 subjects, anchor as a batch."""

    def test_three_subject_batch_round_trip(self):
        # Three badges from three different subjects
        leaves = [
            hashlib.sha256(b"mathematics-badge-1").hexdigest(),
            hashlib.sha256(b"gaeilge-badge-2").hexdigest(),
            hashlib.sha256(b"chemistry-badge-3").hexdigest(),
        ]
        root = compute_merkle_root(leaves)

        # Verify each leaf independently
        # (In practice, the third-party verifier would compute the path
        # from the leaf up to the root; here we just verify the root
        # is consistent with the leaves)
        assert len(root) == 64  # SHA-256 hex digest
        # Compute the root the same way twice → deterministic
        assert root == compute_merkle_root(leaves)

    def test_empty_batch(self):
        """A day with no new badges → empty Merkle batch (root of empty string)."""
        empty_root = compute_merkle_root([])
        expected = hashlib.sha256(b"").hexdigest()
        assert empty_root == expected