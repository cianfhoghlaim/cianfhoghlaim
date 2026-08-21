"""
Challenge 8: Anonymous Voting - tuath Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/zk-voting

Learning Objectives:
- Zero-knowledge proofs for gaming
- Anonymous guild governance
- Private peer review systems
- Verifiable credentials for achievements

Project Integration:
- Celtic MMO anonymous guild voting
- Private Irish language peer corrections
- ZK proof of quest completion
- Verifiable achievement credentials
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md("""
    # Challenge 8: Anonymous Voting

    ## tuath Guild Governance

    Use ZK proofs to enable private voting and verifiable credentials
    in the Celtic MMO without revealing player identities.

    ### Use Cases

    | Feature | Description | Privacy Benefit |
    |---------|-------------|-----------------|
    | **Guild Elections** | Anonymous officer voting | No retaliation |
    | **Peer Reviews** | Private language corrections | Honest feedback |
    | **Achievement Proofs** | Verify quest completion | No spoilers |
    | **Skill Verification** | Prove level without revealing | Matchmaking |

    ### ZK in Gaming

    - Prove you completed a quest without revealing how
    - Vote on guild decisions anonymously
    - Review peer work without bias
    - Verify credentials without exposing player data
    """)
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    ## Guild Election System

    Anonymous voting for guild leadership positions.
    """)
    return


@app.cell
def _():
    import hashlib
    import secrets
    from dataclasses import dataclass, field
    from datetime import datetime, timedelta
    from typing import Optional
    from enum import Enum

    def sha256_hash(*args) -> bytes:
        """Hash inputs together."""
        h = hashlib.sha256()
        for arg in args:
            if isinstance(arg, str):
                h.update(arg.encode())
            elif isinstance(arg, bytes):
                h.update(arg)
            elif isinstance(arg, int):
                h.update(arg.to_bytes(32, "big"))
            else:
                h.update(str(arg).encode())
        return h.digest()

    class GuildRole(Enum):
        CHIEFTAIN = "chieftain"  # Guild leader
        DRUID = "druid"  # Spiritual advisor
        CHAMPION = "champion"  # War leader
        BARD = "bard"  # Lore keeper
        SENTINEL = "sentinel"  # Moderator

    @dataclass
    class Candidate:
        """Election candidate."""

        player_id: str
        role: GuildRole
        platform: str
        endorsements: int = 0

    @dataclass
    class Election:
        """Guild election."""

        election_id: str
        guild_id: str
        role: GuildRole
        candidates: list
        start_time: datetime
        end_time: datetime
        votes: dict = field(default_factory=dict)  # nullifier -> candidate_id
        nullifiers: set = field(default_factory=set)
        revealed: bool = False
        results: Optional[dict] = None

    class GuildElectionSystem:
        """Anonymous guild election system."""

        def __init__(self):
            self.elections: dict[str, Election] = {}
            self.guild_members: dict[str, list] = {}  # guild_id -> member secrets

        def register_guild(self, guild_id: str, member_ids: list[str]):
            """Register guild members for voting."""
            # Each member gets a secret for nullifier generation
            self.guild_members[guild_id] = {
                member_id: secrets.token_bytes(32) for member_id in member_ids
            }

        def create_election(
            self, guild_id: str, role: GuildRole, candidates: list[str], duration_days: int = 3
        ) -> Election:
            """Create a new election."""
            election_id = f"election_{guild_id}_{role.value}_{len(self.elections)}"

            candidate_list = [
                Candidate(player_id=cid, role=role, platform=f"{cid}'s platform for {role.value}")
                for cid in candidates
            ]

            election = Election(
                election_id=election_id,
                guild_id=guild_id,
                role=role,
                candidates=candidate_list,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=duration_days),
            )

            self.elections[election_id] = election
            return election

        def cast_vote(self, election_id: str, voter_id: str, candidate_id: str) -> bool:
            """
            Cast an anonymous vote.

            Voter identity is hidden through nullifier.
            """
            election = self.elections[election_id]
            guild_members = self.guild_members.get(election.guild_id, {})

            if voter_id not in guild_members:
                raise ValueError("Not a guild member")

            # Generate nullifier from voter secret
            voter_secret = guild_members[voter_id]
            nullifier = sha256_hash(voter_secret, election_id)

            # Check for double voting
            if nullifier in election.nullifiers:
                raise ValueError("Already voted")

            # Verify candidate exists
            valid_candidates = [c.player_id for c in election.candidates]
            if candidate_id not in valid_candidates:
                raise ValueError("Invalid candidate")

            # Record vote
            election.nullifiers.add(nullifier)
            election.votes[nullifier] = candidate_id

            return True

        def tally_results(self, election_id: str) -> dict:
            """Tally election results."""
            election = self.elections[election_id]

            # Count votes per candidate
            vote_counts = {}
            for candidate in election.candidates:
                vote_counts[candidate.player_id] = 0

            for nullifier, candidate_id in election.votes.items():
                vote_counts[candidate_id] += 1

            # Determine winner
            sorted_candidates = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)

            election.revealed = True
            election.results = {
                "winner": sorted_candidates[0][0] if sorted_candidates else None,
                "vote_counts": vote_counts,
                "total_votes": len(election.votes),
                "participation": len(election.votes)
                / len(self.guild_members.get(election.guild_id, [1])),
            }

            return election.results

    # Demo
    election_system = GuildElectionSystem()

    # Register guild
    election_system.register_guild(
        "na_fianna", ["seamus", "aoife", "ciaran", "niamh", "padraig", "siobhan"]
    )

    # Create chieftain election
    election = election_system.create_election(
        guild_id="na_fianna",
        role=GuildRole.CHIEFTAIN,
        candidates=["seamus", "aoife"],
        duration_days=3,
    )

    print(f"Election: {election.election_id}")
    print(f"Role: {election.role.value}")
    print(f"Candidates: {[c.player_id for c in election.candidates]}")

    # Members vote anonymously
    votes = [
        ("ciaran", "seamus"),
        ("niamh", "aoife"),
        ("padraig", "seamus"),
        ("siobhan", "aoife"),
        ("seamus", "seamus"),
        ("aoife", "aoife"),
    ]

    for voter, candidate in votes:
        election_system.cast_vote(election.election_id, voter, candidate)

    # Tally
    results = election_system.tally_results(election.election_id)

    print(f"\nResults:")
    for candidate, count in results["vote_counts"].items():
        print(f"  {candidate}: {count} votes")
    print(f"Winner: {results['winner']}")
    print(f"Participation: {results['participation']:.0%}")
    return (
        Candidate,
        Election,
        Enum,
        GuildElectionSystem,
        GuildRole,
        election,
        election_system,
        results,
        secrets,
        sha256_hash,
        votes,
        datetime,
        dataclass,
        field,
        hashlib,
        timedelta,
        Optional,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Anonymous Peer Review System

    Private Irish language corrections without revealing reviewer identity.
    """)
    return


@app.cell
def _(sha256_hash, secrets, dataclass, field, datetime):
    from enum import Enum as Enum2

    class ReviewCategory(Enum2):
        GRAMMAR = "grammar"
        VOCABULARY = "vocabulary"
        PRONUNCIATION = "pronunciation"
        DIALECTT = "dialect"
        COMPREHENSION = "comprehension"

    @dataclass
    class LanguageSubmission:
        """Player's Irish language submission."""

        submission_id: str
        player_id: str
        content: str
        content_type: str  # "essay", "recording", "translation"
        timestamp: datetime
        reviews: list = field(default_factory=list)
        average_score: float = 0

    @dataclass
    class AnonymousReview:
        """Anonymous peer review."""

        review_hash: bytes  # Hash of reviewer identity
        submission_id: str
        score: float  # 1-5 stars
        categories: dict  # category -> score
        feedback: str
        timestamp: datetime

    class PeerReviewSystem:
        """
        Anonymous peer review for language learning.

        Reviewers are anonymous to:
        - Prevent bias (knowing who reviewed)
        - Encourage honest feedback
        - Protect reviewers from retaliation
        """

        def __init__(self):
            self.submissions: dict[str, LanguageSubmission] = {}
            self.reviewer_secrets: dict[str, bytes] = {}
            self.review_nullifiers: dict[str, set] = {}  # submission_id -> nullifiers

        def register_reviewer(self, player_id: str) -> bytes:
            """Register a player as reviewer, return their secret."""
            if player_id not in self.reviewer_secrets:
                self.reviewer_secrets[player_id] = secrets.token_bytes(32)
            return self.reviewer_secrets[player_id]

        def submit_content(
            self, player_id: str, content: str, content_type: str
        ) -> LanguageSubmission:
            """Submit content for peer review."""
            submission_id = f"sub_{player_id}_{len(self.submissions)}"

            submission = LanguageSubmission(
                submission_id=submission_id,
                player_id=player_id,
                content=content,
                content_type=content_type,
                timestamp=datetime.now(),
            )

            self.submissions[submission_id] = submission
            self.review_nullifiers[submission_id] = set()

            return submission

        def submit_review(
            self,
            reviewer_id: str,
            submission_id: str,
            score: float,
            categories: dict[str, float],
            feedback: str,
        ) -> bool:
            """
            Submit an anonymous review.

            Reviewer identity hidden but can't review twice.
            """
            if submission_id not in self.submissions:
                raise ValueError("Submission not found")

            submission = self.submissions[submission_id]

            # Can't review own submission
            if submission.player_id == reviewer_id:
                raise ValueError("Cannot review own submission")

            # Generate nullifier
            reviewer_secret = self.reviewer_secrets.get(reviewer_id)
            if not reviewer_secret:
                raise ValueError("Reviewer not registered")

            nullifier = sha256_hash(reviewer_secret, submission_id)

            # Check for double review
            if nullifier in self.review_nullifiers[submission_id]:
                raise ValueError("Already reviewed this submission")

            # Create anonymous review
            review = AnonymousReview(
                review_hash=sha256_hash(reviewer_id),  # Only hash stored
                submission_id=submission_id,
                score=score,
                categories=categories,
                feedback=feedback,
                timestamp=datetime.now(),
            )

            # Record
            self.review_nullifiers[submission_id].add(nullifier)
            submission.reviews.append(review)

            # Update average score
            scores = [r.score for r in submission.reviews]
            submission.average_score = sum(scores) / len(scores)

            return True

        def get_submission_reviews(self, submission_id: str) -> list[dict]:
            """Get reviews for a submission (anonymized)."""
            submission = self.submissions.get(submission_id)
            if not submission:
                return []

            return [
                {
                    "reviewer": f"Reviewer #{i + 1}",  # Anonymous ID
                    "score": r.score,
                    "categories": r.categories,
                    "feedback": r.feedback,
                    "timestamp": r.timestamp.isoformat(),
                }
                for i, r in enumerate(submission.reviews)
            ]

        def get_reviewer_stats(self, reviewer_id: str) -> dict:
            """Get reviewer's contribution stats (self only)."""
            reviewer_secret = self.reviewer_secrets.get(reviewer_id)
            if not reviewer_secret:
                return {"reviews": 0}

            review_count = 0
            for sub_id, nullifiers in self.review_nullifiers.items():
                nullifier = sha256_hash(reviewer_secret, sub_id)
                if nullifier in nullifiers:
                    review_count += 1

            return {
                "total_reviews": review_count,
                "reviewer_since": "Unknown",  # Privacy preserved
            }

    # Demo
    review_system = PeerReviewSystem()

    # Register reviewers
    review_system.register_reviewer("seamus")
    review_system.register_reviewer("aoife")
    review_system.register_reviewer("ciaran")

    # Submit Irish essay
    submission = review_system.submit_content(
        player_id="niamh",
        content="Dia duit! Is mise Niamh. Taim i mo chonai i nGaillimh...",
        content_type="essay",
    )

    print(f"Submission: {submission.submission_id}")
    print(f"Content: {submission.content[:50]}...")

    # Anonymous reviews
    review_system.submit_review(
        reviewer_id="seamus",
        submission_id=submission.submission_id,
        score=4.5,
        categories={"grammar": 4.0, "vocabulary": 5.0, "dialect": 4.0},
        feedback="Go hiontach! Gramadach maith, focal beag: 'i mo chonai' -> 'i mo chonai'.",
    )

    review_system.submit_review(
        reviewer_id="aoife",
        submission_id=submission.submission_id,
        score=4.0,
        categories={"grammar": 3.5, "vocabulary": 4.5, "dialect": 4.5},
        feedback="Maith thu! Bain usaid as nios mo focail Gaeilge.",
    )

    print(f"\nAnonymous Reviews:")
    for review in review_system.get_submission_reviews(submission.submission_id):
        print(f"  {review['reviewer']}: {review['score']}/5 - {review['feedback'][:40]}...")

    print(f"\nAverage Score: {submission.average_score:.1f}/5")
    return (
        AnonymousReview,
        Enum2,
        LanguageSubmission,
        PeerReviewSystem,
        ReviewCategory,
        review_system,
        submission,
    )


@app.cell
def _(mo):
    mo.md("""
    ## ZK Achievement Credentials

    Prove quest completion without revealing strategy.
    """)
    return


@app.cell
def _(sha256_hash, secrets, dataclass, datetime):
    from typing import Any

    @dataclass
    class Achievement:
        """Game achievement."""

        achievement_id: str
        name: str
        description: str
        requirements: dict  # What needs to be proven
        points: int

    @dataclass
    class Credential:
        """ZK credential for achievement."""

        credential_id: bytes
        achievement_id: str
        player_id: str
        proof_hash: bytes  # Hash of proof data (ZK would be actual proof)
        issued_at: datetime
        metadata: dict  # Non-revealing metadata

    class ZKCredentialSystem:
        """
        Zero-knowledge credential system for achievements.

        Players can prove:
        - They completed a quest (without revealing how)
        - They have a skill level (without revealing exact level)
        - They own an item (without revealing inventory)
        """

        def __init__(self):
            self.achievements: dict[str, Achievement] = {}
            self.credentials: dict[bytes, Credential] = {}
            self.player_credentials: dict[str, list] = {}

        def register_achievement(
            self, achievement_id: str, name: str, description: str, requirements: dict, points: int
        ) -> Achievement:
            """Register an achievement type."""
            achievement = Achievement(
                achievement_id=achievement_id,
                name=name,
                description=description,
                requirements=requirements,
                points=points,
            )
            self.achievements[achievement_id] = achievement
            return achievement

        def issue_credential(
            self,
            player_id: str,
            achievement_id: str,
            proof_data: dict,  # Private proof data (would be ZK proof inputs)
        ) -> Credential:
            """
            Issue a ZK credential for achievement.

            In production, this would verify a ZK proof.
            """
            achievement = self.achievements.get(achievement_id)
            if not achievement:
                raise ValueError("Achievement not found")

            # Generate credential ID (would be ZK commitment)
            credential_id = sha256_hash(player_id, achievement_id, secrets.token_bytes(16))

            # Create proof hash (in production, this is the ZK proof)
            proof_hash = sha256_hash(str(proof_data), secrets.token_bytes(16))

            # Extract non-revealing metadata
            metadata = {
                "completion_tier": proof_data.get("tier", "standard"),
                "timestamp_range": "2025-Q1",  # Coarse timestamp
            }

            credential = Credential(
                credential_id=credential_id,
                achievement_id=achievement_id,
                player_id=player_id,
                proof_hash=proof_hash,
                issued_at=datetime.now(),
                metadata=metadata,
            )

            self.credentials[credential_id] = credential

            if player_id not in self.player_credentials:
                self.player_credentials[player_id] = []
            self.player_credentials[player_id].append(credential_id)

            return credential

        def verify_credential(self, credential_id: bytes, achievement_id: str) -> bool:
            """
            Verify a player has a credential.

            Returns True if valid, without revealing player identity
            to the verifier (in production with ZK).
            """
            credential = self.credentials.get(credential_id)
            if not credential:
                return False

            return credential.achievement_id == achievement_id

        def prove_skill_level(
            self, player_id: str, skill: str, minimum_level: int, actual_level: int
        ) -> dict:
            """
            Generate proof that skill >= minimum without revealing exact level.

            Returns proof that can be verified.
            """
            # In production, this would generate a ZK range proof
            if actual_level < minimum_level:
                raise ValueError("Level requirement not met")

            proof = {
                "skill": skill,
                "minimum_level": minimum_level,
                "proof_type": "range",
                "proof_hash": sha256_hash(
                    player_id, skill, actual_level, secrets.token_bytes(16)
                ).hex(),
                "valid": True,
            }

            return proof

        def get_player_credentials_anonymous(self, player_id: str) -> list[dict]:
            """Get player's credentials (anonymized for sharing)."""
            credential_ids = self.player_credentials.get(player_id, [])

            return [
                {
                    "achievement": self.credentials[cid].achievement_id,
                    "metadata": self.credentials[cid].metadata,
                    "proof_valid": True,  # Would verify ZK proof
                }
                for cid in credential_ids
                if cid in self.credentials
            ]

    # Demo
    cred_system = ZKCredentialSystem()

    # Register achievements
    cred_system.register_achievement(
        "tir_na_nog_complete",
        "Tir na nOg Explorer",
        "Complete the Tir na nOg quest line",
        {"quests_completed": ["tnq1", "tnq2", "tnq3", "tnq_boss"]},
        1000,
    )

    cred_system.register_achievement(
        "irish_fluent",
        "Gaeilgeoir",
        "Achieve B2 level Irish proficiency",
        {"vocabulary": 5000, "grammar_tests": 50, "conversation_hours": 100},
        2500,
    )

    # Issue credentials
    cred1 = cred_system.issue_credential(
        player_id="seamus",
        achievement_id="tir_na_nog_complete",
        proof_data={
            "quests_completed": ["tnq1", "tnq2", "tnq3", "tnq_boss"],
            "completion_time": 3600,  # Private: how long it took
            "tier": "gold",  # Public tier
            "strategy": "stealth",  # Private: how they did it
        },
    )

    print(f"Credential Issued: {cred1.achievement_id}")
    print(f"Credential ID: {cred1.credential_id.hex()[:32]}...")
    print(f"Metadata (public): {cred1.metadata}")

    # Verify credential (without revealing player)
    is_valid = cred_system.verify_credential(cred1.credential_id, "tir_na_nog_complete")
    print(f"\nCredential Valid: {is_valid}")

    # Prove skill level (range proof)
    skill_proof = cred_system.prove_skill_level(
        player_id="seamus",
        skill="irish_vocabulary",
        minimum_level=5000,
        actual_level=7500,  # Actual level hidden
    )
    print(f"\nSkill Proof: {skill_proof['skill']} >= {skill_proof['minimum_level']}")
    print(f"Proof Valid: {skill_proof['valid']}")
    return (
        Achievement,
        Any,
        Credential,
        ZKCredentialSystem,
        cred1,
        cred_system,
        is_valid,
        skill_proof,
    )


@app.cell
def _(mo):
    mo.md("""
    ## SpacetimeDB Integration

    Schema for ZK voting and credentials in SpacetimeDB.
    """)
    return


@app.cell
def _():
    spacetimedb_schema = """
    // SpacetimeDB Schema for tuath ZK Voting and Credentials

    // Guild election
    table guild_election {
        #[primarykey]
        election_id: String,
        guild_id: String,
        role: String,
        start_time: Timestamp,
        end_time: Timestamp,
        merkle_root: Vec<u8>,  // Root of eligible voters
        status: String,        // pending, active, completed
    }

    // Election candidate
    table election_candidate {
        #[primarykey]
        id: U64,
        #[index]
        election_id: String,
        player_id: Identity,
        platform: String,
        endorsements: U32,
    }

    // Anonymous vote (only nullifier stored, not voter)
    table anonymous_vote {
        #[primarykey]
        id: U64,
        #[index]
        election_id: String,
        nullifier: Vec<u8>,    // Prevents double voting
        candidate_id: String,  // Who they voted for
        timestamp: Timestamp,
    }

    // Language submission for peer review
    table language_submission {
        #[primarykey]
        submission_id: String,
        player_id: Identity,
        content: String,
        content_type: String,
        submitted_at: Timestamp,
        average_score: Float64,
        review_count: U32,
    }

    // Anonymous peer review
    table anonymous_review {
        #[primarykey]
        id: U64,
        #[index]
        submission_id: String,
        reviewer_hash: Vec<u8>,  // Hash of reviewer (not identity)
        nullifier: Vec<u8>,      // Prevents double review
        score: Float64,
        grammar_score: Float64,
        vocabulary_score: Float64,
        dialect_score: Float64,
        feedback: String,
        timestamp: Timestamp,
    }

    // Achievement definition
    table achievement {
        #[primarykey]
        achievement_id: String,
        name: String,
        description: String,
        points: U32,
        requirements_json: String,
    }

    // ZK credential (proves achievement without revealing method)
    table zk_credential {
        #[primarykey]
        credential_id: Vec<u8>,
        #[index]
        player_id: Identity,
        #[index]
        achievement_id: String,
        proof_hash: Vec<u8>,
        issued_at: Timestamp,
        metadata_json: String,
    }

    // Skill level proof (range proof)
    table skill_proof {
        #[primarykey]
        proof_id: String,
        player_id: Identity,
        skill: String,
        minimum_level: U32,
        proof_hash: Vec<u8>,
        valid_until: Timestamp,
    }

    // Reducers

    #[reducer]
    fn cast_anonymous_vote(
        election_id: String,
        candidate_id: String,
        nullifier: Vec<u8>,
        merkle_proof: Vec<Vec<u8>>,
        voter_leaf: Vec<u8>,
    ) {
        let election = GuildElection::filter_by_election_id(&election_id)
            .expect("Election not found");

        // Verify voting is active
        let now = Timestamp::now();
        assert!(now >= election.start_time && now <= election.end_time,
                "Voting not active");

        // Check nullifier not used
        assert!(
            AnonymousVote::filter_by_election_id(&election_id)
                .filter(|v| v.nullifier == nullifier)
                .count() == 0,
            "Already voted"
        );

        // Verify Merkle proof
        assert!(
            verify_merkle_proof(&election.merkle_root, &merkle_proof, &voter_leaf),
            "Invalid voter proof"
        );

        // Record vote
        AnonymousVote::insert(AnonymousVote {
            id: 0,
            election_id,
            nullifier,
            candidate_id,
            timestamp: now,
        });
    }

    #[reducer]
    fn submit_anonymous_review(
        submission_id: String,
        reviewer_nullifier: Vec<u8>,
        score: Float64,
        grammar_score: Float64,
        vocabulary_score: Float64,
        dialect_score: Float64,
        feedback: String,
    ) {
        // Verify not already reviewed
        assert!(
            AnonymousReview::filter_by_submission_id(&submission_id)
                .filter(|r| r.nullifier == reviewer_nullifier)
                .count() == 0,
            "Already reviewed"
        );

        let reviewer_hash = sha256(&reviewer_nullifier);

        AnonymousReview::insert(AnonymousReview {
            id: 0,
            submission_id: submission_id.clone(),
            reviewer_hash,
            nullifier: reviewer_nullifier,
            score,
            grammar_score,
            vocabulary_score,
            dialect_score,
            feedback,
            timestamp: Timestamp::now(),
        });

        // Update submission average
        update_submission_score(&submission_id);
    }

    #[reducer]
    fn issue_zk_credential(
        player_id: Identity,
        achievement_id: String,
        proof_hash: Vec<u8>,
        metadata_json: String,
    ) {
        // Verify achievement exists
        let _achievement = Achievement::filter_by_achievement_id(&achievement_id)
            .expect("Achievement not found");

        // Generate credential ID
        let credential_id = sha256(&[
            player_id.to_bytes(),
            achievement_id.as_bytes(),
            &random_bytes(16),
        ].concat());

        ZkCredential::insert(ZkCredential {
            credential_id,
            player_id,
            achievement_id,
            proof_hash,
            issued_at: Timestamp::now(),
            metadata_json,
        });
    }
    """

    print("SpacetimeDB Schema for ZK Voting and Credentials")
    print("=" * 50)
    print(spacetimedb_schema[:3000] + "...")
    return (spacetimedb_schema,)


@app.cell
def _(mo):
    mo.md("""
    ## Anchor Program Structure

    Solana program for ZK voting and credentials.
    """)
    return


@app.cell
def _():
    anchor_program = """
    // Anchor Program: tuath_zk_voting
    // Solana implementation of anonymous voting and credentials

    use anchor_lang::prelude::*;

    declare_id!("ZKVot111111111111111111111111111111111111");

    #[program]
    pub mod tuath_zk_voting {
        use super::*;

        /// Create a guild election
        pub fn create_election(
            ctx: Context<CreateElection>,
            role: String,
            merkle_root: [u8; 32],
            duration_seconds: i64,
        ) -> Result<()> {
            let election = &mut ctx.accounts.election;
            election.guild = ctx.accounts.guild.key();
            election.role = role;
            election.merkle_root = merkle_root;
            election.start_time = Clock::get()?.unix_timestamp;
            election.end_time = election.start_time + duration_seconds;
            election.yes_votes = 0;
            election.no_votes = 0;
            election.status = ElectionStatus::Active;
            election.bump = ctx.bumps.election;
            Ok(())
        }

        /// Cast anonymous vote using Merkle proof
        pub fn cast_anonymous_vote(
            ctx: Context<CastVote>,
            vote: VoteChoice,
            nullifier: [u8; 32],
            merkle_proof: Vec<[u8; 32]>,
            voter_leaf: [u8; 32],
        ) -> Result<()> {
            let election = &mut ctx.accounts.election;
            let nullifier_account = &mut ctx.accounts.nullifier_account;

            // Verify voting is active
            let now = Clock::get()?.unix_timestamp;
            require!(
                now >= election.start_time && now <= election.end_time,
                ErrorCode::VotingNotActive
            );

            // Verify Merkle proof
            require!(
                verify_merkle_proof(&election.merkle_root, &merkle_proof, &voter_leaf),
                ErrorCode::InvalidMerkleProof
            );

            // Mark nullifier as used
            nullifier_account.used = true;

            // Record vote
            match vote {
                VoteChoice::For => election.yes_votes += 1,
                VoteChoice::Against => election.no_votes += 1,
                VoteChoice::Abstain => {},
            }

            Ok(())
        }

        /// Issue a ZK credential for achievement
        pub fn issue_credential(
            ctx: Context<IssueCredential>,
            achievement_id: String,
            proof_hash: [u8; 32],
            metadata_uri: String,
        ) -> Result<()> {
            let credential = &mut ctx.accounts.credential;

            credential.player = ctx.accounts.player.key();
            credential.achievement_id = achievement_id;
            credential.proof_hash = proof_hash;
            credential.metadata_uri = metadata_uri;
            credential.issued_at = Clock::get()?.unix_timestamp;
            credential.bump = ctx.bumps.credential;

            Ok(())
        }

        /// Verify a credential (on-chain verification)
        pub fn verify_credential(
            ctx: Context<VerifyCredential>,
            achievement_id: String,
        ) -> Result<bool> {
            let credential = &ctx.accounts.credential;
            Ok(credential.achievement_id == achievement_id)
        }

        /// Submit anonymous peer review
        pub fn submit_anonymous_review(
            ctx: Context<SubmitReview>,
            submission_id: String,
            nullifier: [u8; 32],
            score: u8,
            feedback_uri: String,
        ) -> Result<()> {
            let review = &mut ctx.accounts.review;
            let nullifier_account = &mut ctx.accounts.nullifier_account;

            require!(score >= 1 && score <= 5, ErrorCode::InvalidScore);

            // Mark nullifier as used
            nullifier_account.used = true;

            review.submission_id = submission_id;
            review.score = score;
            review.feedback_uri = feedback_uri;
            review.timestamp = Clock::get()?.unix_timestamp;
            review.bump = ctx.bumps.review;

            Ok(())
        }
    }

    #[derive(Accounts)]
    #[instruction(role: String)]
    pub struct CreateElection<'info> {
        #[account(mut)]
        pub creator: Signer<'info>,

        pub guild: Account<'info, Guild>,

        #[account(
            init,
            payer = creator,
            space = 8 + Election::INIT_SPACE,
            seeds = [b"election", guild.key().as_ref(), role.as_bytes()],
            bump,
        )]
        pub election: Account<'info, Election>,

        pub system_program: Program<'info, System>,
    }

    #[derive(Accounts)]
    #[instruction(vote: VoteChoice, nullifier: [u8; 32])]
    pub struct CastVote<'info> {
        #[account(mut)]
        pub voter: Signer<'info>,

        #[account(mut)]
        pub election: Account<'info, Election>,

        #[account(
            init,
            payer = voter,
            space = 8 + NullifierAccount::INIT_SPACE,
            seeds = [b"nullifier", election.key().as_ref(), &nullifier],
            bump,
        )]
        pub nullifier_account: Account<'info, NullifierAccount>,

        pub system_program: Program<'info, System>,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct Election {
        pub guild: Pubkey,
        #[max_len(32)]
        pub role: String,
        pub merkle_root: [u8; 32],
        pub start_time: i64,
        pub end_time: i64,
        pub yes_votes: u32,
        pub no_votes: u32,
        pub status: ElectionStatus,
        pub bump: u8,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct NullifierAccount {
        pub used: bool,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct ZkCredential {
        pub player: Pubkey,
        #[max_len(64)]
        pub achievement_id: String,
        pub proof_hash: [u8; 32],
        #[max_len(256)]
        pub metadata_uri: String,
        pub issued_at: i64,
        pub bump: u8,
    }

    #[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, InitSpace)]
    pub enum ElectionStatus {
        Pending,
        Active,
        Completed,
        Cancelled,
    }

    #[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
    pub enum VoteChoice {
        For,
        Against,
        Abstain,
    }

    #[error_code]
    pub enum ErrorCode {
        #[msg("Voting is not currently active")]
        VotingNotActive,
        #[msg("Invalid Merkle proof")]
        InvalidMerkleProof,
        #[msg("Score must be between 1 and 5")]
        InvalidScore,
    }

    // Helper function for Merkle verification
    fn verify_merkle_proof(
        root: &[u8; 32],
        proof: &[[u8; 32]],
        leaf: &[u8; 32],
    ) -> bool {
        let mut current = *leaf;
        for sibling in proof {
            if current < *sibling {
                current = hash_pair(&current, sibling);
            } else {
                current = hash_pair(sibling, &current);
            }
        }
        current == *root
    }
    """

    print("Anchor Program: tuath_zk_voting")
    print("=" * 50)
    print(anchor_program[:3000] + "...")
    return (anchor_program,)


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Challenge 8 Complete

    ### Key Learnings

    1. **Anonymous Guild Voting**: Merkle proofs + nullifiers for privacy
    2. **Private Peer Review**: Honest feedback without revealing reviewer
    3. **ZK Credentials**: Prove achievements without revealing methods
    4. **Skill Range Proofs**: Prove level >= X without exact disclosure

    ### tuath Integration

    - Guild chieftain elections with anonymous voting
    - Irish language peer review system
    - Quest completion credentials (no spoilers)
    - Skill verification for matchmaking

    ### SpeedRunEthereum Complete!

    All 9 challenges implemented with both crypteolas and tuath:

    | Challenge | crypteolas | tuath |
    |-----------|------------|-------|
    | 0: Tokenization | NFT Analytics | Celtic Creature NFTs |
    | 1: Staking | Staking Analytics | Learn-to-Earn |
    | 2: Token Vendor | Token Economics | In-Game Shop |
    | 3: Dice Game | Randomness Analysis | Quest RNG |
    | 4: DEX | AMM Analytics | Item Exchange |
    | 5: Lending | Lending Analytics | Skill Lending |
    | 6: Stablecoins | Stablecoin Tracking | Learning Tokens |
    | 7: Predictions | Market Analytics | Exam Predictions |
    | 8: ZK Voting | Governance Analytics | Anonymous Voting |
    """)
    return


if __name__ == "__main__":
    app.run()
