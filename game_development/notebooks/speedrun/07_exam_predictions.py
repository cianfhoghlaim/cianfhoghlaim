"""
Challenge 7: Exam Predictions - tuath Implementation

SpeedRunEthereum Challenge: https://speedrunethereum.com/challenge/prediction-markets

Learning Objectives:
- Binary outcome markets for education
- Self-prediction for study motivation
- Subject difficulty betting (Leaving Cert)
- Reputation-based resolution

Project Integration:
- Celtic MMO exam prediction markets
- Irish Leaving Certificate subject predictions
- Player study motivation through stakes
- Guild academic competitions
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.md("""
    # Challenge 7: Exam Predictions

    ## tuath Education Prediction Markets

    Use prediction markets to motivate study and track academic progress
    in the Celtic MMO. Players can predict their own exam results and
    subject difficulty levels.

    ### Market Types

    | Market Type | Description | Resolution |
    |-------------|-------------|------------|
    | **Self-Prediction** | Predict your own exam grade | Verified exam result |
    | **Subject Difficulty** | Predict hardest LC subject | Official stats |
    | **Class Performance** | Guild average predictions | Teacher verification |
    | **Topic Mastery** | In-game quiz predictions | Game system |

    ### Motivation Mechanics

    - Players stake tokens on their predictions
    - Correct self-predictions earn bonus XP
    - Creates accountability for study commitments
    - Guild competitions for best predictors
    """)
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    ## Self-Prediction Markets

    Predict your own exam results to create study accountability.
    """)
    return


@app.cell
def _():
    from dataclasses import dataclass, field
    from datetime import datetime, timedelta
    from typing import Optional
    from enum import Enum
    import math

    class ExamGrade(Enum):
        """Leaving Certificate grade bands."""
        H1 = "H1"  # 90-100%
        H2 = "H2"  # 80-89%
        H3 = "H3"  # 70-79%
        H4 = "H4"  # 60-69%
        H5 = "H5"  # 50-59%
        H6 = "H6"  # 40-49%
        H7 = "H7"  # 30-39%
        H8 = "H8"  # 0-29%

    class LCSubject(Enum):
        """Leaving Certificate subjects."""
        IRISH = "irish"
        ENGLISH = "english"
        MATHS = "maths"
        FRENCH = "french"
        GERMAN = "german"
        SPANISH = "spanish"
        HISTORY = "history"
        GEOGRAPHY = "geography"
        BIOLOGY = "biology"
        CHEMISTRY = "chemistry"
        PHYSICS = "physics"
        ACCOUNTING = "accounting"
        BUSINESS = "business"
        ECONOMICS = "economics"
        ART = "art"
        MUSIC = "music"

    @dataclass
    class SelfPrediction:
        """Player's prediction about their own exam result."""
        prediction_id: str
        player_id: str
        subject: LCSubject
        predicted_grade: ExamGrade
        confidence: float  # 0-1, how confident they are
        stake_amount: float
        exam_date: datetime
        created_at: datetime = field(default_factory=datetime.now)
        actual_grade: Optional[ExamGrade] = None
        resolved: bool = False
        payout: float = 0

        @property
        def potential_return(self) -> float:
            """Calculate potential return based on confidence."""
            # Higher confidence = lower return (less risky)
            # Lower confidence = higher return (more risky)
            base_multiplier = 2.0  # 2x for 50% confidence

            # Adjust based on confidence
            if self.confidence >= 0.9:
                return self.stake_amount * 1.2  # Low return for high confidence
            elif self.confidence >= 0.7:
                return self.stake_amount * 1.5
            elif self.confidence >= 0.5:
                return self.stake_amount * base_multiplier
            else:
                return self.stake_amount * 3.0  # High return for low confidence

        @property
        def grade_distance(self) -> int:
            """Calculate grade distance (for partial credit)."""
            if not self.actual_grade:
                return -1

            grades = list(ExamGrade)
            predicted_idx = grades.index(self.predicted_grade)
            actual_idx = grades.index(self.actual_grade)

            return abs(predicted_idx - actual_idx)

    class SelfPredictionMarket:
        """Manage player self-prediction markets."""

        def __init__(self):
            self.predictions: dict[str, SelfPrediction] = {}
            self.player_stats: dict[str, dict] = {}

        def create_prediction(
            self,
            player_id: str,
            subject: LCSubject,
            predicted_grade: ExamGrade,
            confidence: float,
            stake_amount: float,
            exam_date: datetime
        ) -> SelfPrediction:
            """Create a new self-prediction."""
            prediction_id = f"pred_{player_id}_{subject.value}_{len(self.predictions)}"

            prediction = SelfPrediction(
                prediction_id=prediction_id,
                player_id=player_id,
                subject=subject,
                predicted_grade=predicted_grade,
                confidence=min(max(confidence, 0.1), 0.99),  # Clamp confidence
                stake_amount=stake_amount,
                exam_date=exam_date
            )

            self.predictions[prediction_id] = prediction
            return prediction

        def resolve_prediction(
            self,
            prediction_id: str,
            actual_grade: ExamGrade
        ) -> float:
            """Resolve prediction with actual exam result."""
            prediction = self.predictions[prediction_id]
            prediction.actual_grade = actual_grade
            prediction.resolved = True

            # Calculate payout
            distance = prediction.grade_distance

            if distance == 0:
                # Exact match - full payout
                prediction.payout = prediction.potential_return
            elif distance == 1:
                # One grade off - 50% payout
                prediction.payout = prediction.stake_amount * 0.5
            else:
                # More than one grade off - lose stake
                prediction.payout = 0

            # Update player stats
            self._update_player_stats(prediction)

            return prediction.payout

        def _update_player_stats(self, prediction: SelfPrediction):
            """Update player prediction statistics."""
            player_id = prediction.player_id

            if player_id not in self.player_stats:
                self.player_stats[player_id] = {
                    "total_predictions": 0,
                    "exact_matches": 0,
                    "close_matches": 0,
                    "total_staked": 0,
                    "total_winnings": 0,
                    "subjects": {}
                }

            stats = self.player_stats[player_id]
            stats["total_predictions"] += 1
            stats["total_staked"] += prediction.stake_amount
            stats["total_winnings"] += prediction.payout

            if prediction.grade_distance == 0:
                stats["exact_matches"] += 1
            elif prediction.grade_distance == 1:
                stats["close_matches"] += 1

            # Track by subject
            subject = prediction.subject.value
            if subject not in stats["subjects"]:
                stats["subjects"][subject] = {"predictions": 0, "accuracy": 0}

            stats["subjects"][subject]["predictions"] += 1
            subject_preds = [
                p for p in self.predictions.values()
                if p.player_id == player_id and p.subject == prediction.subject and p.resolved
            ]
            if subject_preds:
                exact = sum(1 for p in subject_preds if p.grade_distance == 0)
                stats["subjects"][subject]["accuracy"] = exact / len(subject_preds)

        def get_calibration_score(self, player_id: str) -> float:
            """
            Calculate player calibration (Brier-like score).

            Lower is better - measures how well confidence matches outcomes.
            """
            player_predictions = [
                p for p in self.predictions.values()
                if p.player_id == player_id and p.resolved
            ]

            if not player_predictions:
                return 0.5  # Default for no predictions

            total_error = 0
            for pred in player_predictions:
                # 1 if exact match, 0 otherwise
                outcome = 1 if pred.grade_distance == 0 else 0
                error = (pred.confidence - outcome) ** 2
                total_error += error

            return total_error / len(player_predictions)

        def get_leaderboard(self, limit: int = 10) -> list[dict]:
            """Get player leaderboard by prediction accuracy."""
            leaderboard = []

            for player_id, stats in self.player_stats.items():
                if stats["total_predictions"] >= 3:  # Minimum predictions
                    accuracy = stats["exact_matches"] / stats["total_predictions"]
                    profit = stats["total_winnings"] - stats["total_staked"]

                    leaderboard.append({
                        "player_id": player_id,
                        "predictions": stats["total_predictions"],
                        "accuracy": accuracy,
                        "profit": profit,
                        "calibration": self.get_calibration_score(player_id)
                    })

            return sorted(leaderboard, key=lambda x: x["accuracy"], reverse=True)[:limit]

    # Demo
    market = SelfPredictionMarket()

    # Create predictions
    pred1 = market.create_prediction(
        player_id="seamus_og",
        subject=LCSubject.IRISH,
        predicted_grade=ExamGrade.H2,
        confidence=0.75,
        stake_amount=100,
        exam_date=datetime(2025, 6, 10)
    )

    pred2 = market.create_prediction(
        player_id="seamus_og",
        subject=LCSubject.MATHS,
        predicted_grade=ExamGrade.H3,
        confidence=0.60,
        stake_amount=150,
        exam_date=datetime(2025, 6, 12)
    )

    print("Self-Predictions Created:")
    print(f"  {pred1.subject.value}: Predicted {pred1.predicted_grade.value}")
    print(f"    Confidence: {pred1.confidence:.0%}, Potential: ${pred1.potential_return:.2f}")
    print(f"  {pred2.subject.value}: Predicted {pred2.predicted_grade.value}")
    print(f"    Confidence: {pred2.confidence:.0%}, Potential: ${pred2.potential_return:.2f}")

    # Resolve
    payout1 = market.resolve_prediction(pred1.prediction_id, ExamGrade.H2)
    payout2 = market.resolve_prediction(pred2.prediction_id, ExamGrade.H4)

    print(f"\nResolutions:")
    print(f"  Irish: Got {ExamGrade.H2.value} (predicted H2) -> Payout: ${payout1:.2f}")
    print(f"  Maths: Got {ExamGrade.H4.value} (predicted H3) -> Payout: ${payout2:.2f}")
    return (
        ExamGrade,
        LCSubject,
        SelfPrediction,
        SelfPredictionMarket,
        field,
        market,
        math,
        datetime,
        dataclass,
        payout1,
        payout2,
        pred1,
        pred2,
        timedelta,
        Optional,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Subject Difficulty Markets

    Predict which subjects will be hardest in the upcoming Leaving Cert.
    """)
    return


@app.cell
def _(LCSubject, dataclass, datetime, field, Optional):
    from typing import Any

    @dataclass
    class SubjectDifficultyMarket:
        """Market for predicting subject difficulty."""
        market_id: str
        exam_year: int
        subject: LCSubject
        difficulty_predictions: dict = field(default_factory=dict)  # player_id -> difficulty (1-10)
        liquidity: float = 0
        resolved: bool = False
        actual_difficulty: Optional[float] = None  # Based on grade distribution

    class DifficultyPredictor:
        """
        Predict and aggregate subject difficulty levels.

        Resolution based on:
        - Mean grade for subject
        - Grade distribution (more H6/H7 = harder)
        - Comparison to previous years
        """

        def __init__(self):
            self.markets: dict[str, SubjectDifficultyMarket] = {}
            self.historical_data: dict[str, list] = {}

        def create_market(
            self,
            exam_year: int,
            subject: LCSubject,
            initial_liquidity: float = 1000
        ) -> SubjectDifficultyMarket:
            """Create difficulty prediction market."""
            market_id = f"diff_{exam_year}_{subject.value}"

            market = SubjectDifficultyMarket(
                market_id=market_id,
                exam_year=exam_year,
                subject=subject,
                liquidity=initial_liquidity
            )

            self.markets[market_id] = market
            return market

        def submit_prediction(
            self,
            market_id: str,
            player_id: str,
            difficulty: float,
            stake: float
        ):
            """Submit difficulty prediction (1-10 scale)."""
            market = self.markets[market_id]
            market.difficulty_predictions[player_id] = {
                "difficulty": min(max(difficulty, 1), 10),
                "stake": stake,
                "timestamp": datetime.now()
            }
            market.liquidity += stake

        def get_consensus_difficulty(self, market_id: str) -> float:
            """Get stake-weighted average difficulty prediction."""
            market = self.markets[market_id]

            if not market.difficulty_predictions:
                return 5.0  # Default

            total_stake = sum(p["stake"] for p in market.difficulty_predictions.values())
            weighted_sum = sum(
                p["difficulty"] * p["stake"]
                for p in market.difficulty_predictions.values()
            )

            return weighted_sum / total_stake if total_stake > 0 else 5.0

        def resolve_market(
            self,
            market_id: str,
            grade_distribution: dict[str, float]
        ) -> dict[str, float]:
            """
            Resolve market based on actual grade distribution.

            Returns payouts per player.
            """
            market = self.markets[market_id]

            # Calculate actual difficulty from grade distribution
            # Weight: H1/H2 = easy, H6/H7/H8 = hard
            weights = {
                "H1": 1, "H2": 2, "H3": 3, "H4": 4,
                "H5": 5, "H6": 7, "H7": 8, "H8": 10
            }

            total_weight = sum(
                grade_distribution.get(grade, 0) * weight
                for grade, weight in weights.items()
            )
            total_students = sum(grade_distribution.values())

            actual_difficulty = (total_weight / total_students) if total_students > 0 else 5.0
            market.actual_difficulty = actual_difficulty
            market.resolved = True

            # Calculate payouts
            payouts = {}
            for player_id, pred in market.difficulty_predictions.items():
                error = abs(pred["difficulty"] - actual_difficulty)

                if error <= 0.5:
                    # Very close - 2x return
                    payouts[player_id] = pred["stake"] * 2.0
                elif error <= 1.5:
                    # Close - 1.5x return
                    payouts[player_id] = pred["stake"] * 1.5
                elif error <= 2.5:
                    # Okay - return stake
                    payouts[player_id] = pred["stake"]
                else:
                    # Far off - lose stake
                    payouts[player_id] = 0

            return payouts

        def get_subject_rankings(self, exam_year: int) -> list[dict]:
            """Get subjects ranked by predicted difficulty."""
            year_markets = [
                m for m in self.markets.values()
                if m.exam_year == exam_year
            ]

            rankings = []
            for market in year_markets:
                rankings.append({
                    "subject": market.subject.value,
                    "predicted_difficulty": self.get_consensus_difficulty(market.market_id),
                    "num_predictions": len(market.difficulty_predictions),
                    "liquidity": market.liquidity
                })

            return sorted(rankings, key=lambda x: x["predicted_difficulty"], reverse=True)

    # Demo
    predictor = DifficultyPredictor()

    # Create markets for 2025 LC
    subjects = [LCSubject.IRISH, LCSubject.MATHS, LCSubject.PHYSICS, LCSubject.HISTORY]
    for subj in subjects:
        predictor.create_market(2025, subj)

    # Submit predictions
    predictions = [
        ("diff_2025_maths", "player1", 7.5, 50),
        ("diff_2025_maths", "player2", 8.0, 75),
        ("diff_2025_irish", "player1", 6.0, 40),
        ("diff_2025_physics", "player3", 9.0, 100),
        ("diff_2025_history", "player2", 5.5, 30),
    ]

    for market_id, player, diff, stake in predictions:
        predictor.submit_prediction(market_id, player, diff, stake)

    print("Subject Difficulty Rankings (2025 LC):")
    print("-" * 50)
    for rank in predictor.get_subject_rankings(2025):
        print(f"  {rank['subject']:>10}: {rank['predicted_difficulty']:.1f}/10 "
              f"({rank['num_predictions']} predictions, ${rank['liquidity']:.0f} liquidity)")
    return (
        Any,
        DifficultyPredictor,
        SubjectDifficultyMarket,
        predictor,
        predictions,
        subj,
        subjects,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Guild Academic Competitions

    Guilds compete on aggregate prediction accuracy and academic performance.
    """)
    return


@app.cell
def _(ExamGrade, LCSubject, dataclass, datetime, field):
    @dataclass
    class GuildMember:
        """Guild member with academic stats."""
        player_id: str
        guild_id: str
        subjects: list
        predictions: list = field(default_factory=list)
        exam_results: dict = field(default_factory=dict)

    @dataclass
    class GuildCompetition:
        """Inter-guild academic competition."""
        competition_id: str
        name: str
        start_date: datetime
        end_date: datetime
        subjects: list  # Subjects included in competition
        participating_guilds: list
        guild_scores: dict = field(default_factory=dict)

    class GuildAcademicLeague:
        """Manage guild academic competitions."""

        def __init__(self):
            self.guilds: dict[str, dict] = {}
            self.competitions: dict[str, GuildCompetition] = {}
            self.members: dict[str, GuildMember] = {}

        def register_guild(self, guild_id: str, name: str):
            """Register a guild."""
            self.guilds[guild_id] = {
                "name": name,
                "members": [],
                "total_points": 0,
                "prediction_accuracy": 0,
                "rank": 0
            }

        def add_member(self, player_id: str, guild_id: str, subjects: list):
            """Add member to guild."""
            member = GuildMember(
                player_id=player_id,
                guild_id=guild_id,
                subjects=subjects
            )
            self.members[player_id] = member
            self.guilds[guild_id]["members"].append(player_id)

        def create_competition(
            self,
            name: str,
            subjects: list,
            guild_ids: list,
            duration_days: int = 30
        ) -> GuildCompetition:
            """Create inter-guild competition."""
            comp_id = f"comp_{len(self.competitions)}"

            competition = GuildCompetition(
                competition_id=comp_id,
                name=name,
                start_date=datetime.now(),
                end_date=datetime.now() + datetime.timedelta(days=duration_days)
                         if hasattr(datetime, 'timedelta') else datetime.now(),
                subjects=subjects,
                participating_guilds=guild_ids,
                guild_scores={gid: 0 for gid in guild_ids}
            )

            self.competitions[comp_id] = competition
            return competition

        def record_prediction_result(
            self,
            player_id: str,
            subject: LCSubject,
            predicted: ExamGrade,
            actual: ExamGrade
        ):
            """Record a player's prediction result."""
            member = self.members.get(player_id)
            if not member:
                return

            # Calculate points
            grades = list(ExamGrade)
            pred_idx = grades.index(predicted)
            actual_idx = grades.index(actual)
            distance = abs(pred_idx - actual_idx)

            if distance == 0:
                points = 100  # Exact match
            elif distance == 1:
                points = 50  # One grade off
            else:
                points = max(0, 25 - (distance - 2) * 10)  # Decreasing points

            member.predictions.append({
                "subject": subject,
                "predicted": predicted,
                "actual": actual,
                "points": points
            })

            # Update guild score
            guild = self.guilds[member.guild_id]
            guild["total_points"] += points

        def get_guild_leaderboard(self) -> list[dict]:
            """Get guild leaderboard."""
            leaderboard = []

            for guild_id, guild in self.guilds.items():
                member_count = len(guild["members"])
                total_predictions = sum(
                    len(self.members[mid].predictions)
                    for mid in guild["members"]
                )

                if total_predictions > 0:
                    avg_points = guild["total_points"] / total_predictions
                else:
                    avg_points = 0

                leaderboard.append({
                    "guild_id": guild_id,
                    "name": guild["name"],
                    "members": member_count,
                    "total_points": guild["total_points"],
                    "avg_points": avg_points,
                    "predictions": total_predictions
                })

            return sorted(leaderboard, key=lambda x: x["avg_points"], reverse=True)

        def get_subject_champions(self, subject: LCSubject) -> list[dict]:
            """Get top predictors for a subject."""
            champions = []

            for player_id, member in self.members.items():
                subject_preds = [
                    p for p in member.predictions
                    if p["subject"] == subject
                ]

                if subject_preds:
                    exact = sum(1 for p in subject_preds if p["points"] == 100)
                    avg_points = sum(p["points"] for p in subject_preds) / len(subject_preds)

                    champions.append({
                        "player_id": player_id,
                        "guild_id": member.guild_id,
                        "predictions": len(subject_preds),
                        "exact_matches": exact,
                        "avg_points": avg_points
                    })

            return sorted(champions, key=lambda x: x["avg_points"], reverse=True)[:10]

    # Demo
    league = GuildAcademicLeague()

    # Register guilds
    league.register_guild("na_fianna", "Na Fianna")
    league.register_guild("clann_lir", "Clann Lir")
    league.register_guild("tuatha_de", "Tuatha De Danann")

    # Add members
    league.add_member("seamus", "na_fianna", [LCSubject.IRISH, LCSubject.MATHS])
    league.add_member("aoife", "na_fianna", [LCSubject.IRISH, LCSubject.ENGLISH])
    league.add_member("ciaran", "clann_lir", [LCSubject.PHYSICS, LCSubject.MATHS])
    league.add_member("niamh", "tuatha_de", [LCSubject.IRISH, LCSubject.HISTORY])

    # Record some predictions
    league.record_prediction_result("seamus", LCSubject.IRISH, ExamGrade.H2, ExamGrade.H2)
    league.record_prediction_result("seamus", LCSubject.MATHS, ExamGrade.H3, ExamGrade.H4)
    league.record_prediction_result("aoife", LCSubject.IRISH, ExamGrade.H1, ExamGrade.H2)
    league.record_prediction_result("ciaran", LCSubject.PHYSICS, ExamGrade.H4, ExamGrade.H4)
    league.record_prediction_result("niamh", LCSubject.IRISH, ExamGrade.H3, ExamGrade.H3)

    print("Guild Academic League Leaderboard:")
    print("-" * 60)
    for i, guild in enumerate(league.get_guild_leaderboard(), 1):
        print(f"  #{i} {guild['name']:>20} | "
              f"Avg: {guild['avg_points']:.1f} pts | "
              f"{guild['predictions']} predictions")

    print("\nIrish Subject Champions:")
    for champ in league.get_subject_champions(LCSubject.IRISH):
        print(f"  {champ['player_id']} ({champ['guild_id']}): "
              f"{champ['avg_points']:.1f} avg pts, {champ['exact_matches']} exact")
    return (
        GuildAcademicLeague,
        GuildCompetition,
        GuildMember,
        league,
    )


@app.cell
def _(mo):
    mo.md("""
    ## SpacetimeDB Integration

    Schema for storing prediction market data in SpacetimeDB.
    """)
    return


@app.cell
def _():
    spacetimedb_schema = """
    // SpacetimeDB Schema for tuath Exam Predictions

    // Player prediction for their own exam
    table self_prediction {
        #[primarykey]
        prediction_id: String,
        player_id: Identity,
        subject: String,
        predicted_grade: String,
        confidence: Float64,
        stake_amount: Float64,
        exam_date: Timestamp,
        created_at: Timestamp,
        actual_grade: Option<String>,
        resolved: Bool,
        payout: Float64,
    }

    // Subject difficulty market
    table difficulty_market {
        #[primarykey]
        market_id: String,
        exam_year: U32,
        subject: String,
        consensus_difficulty: Float64,
        liquidity: Float64,
        resolved: Bool,
        actual_difficulty: Option<Float64>,
    }

    // Player difficulty predictions
    table difficulty_prediction {
        #[primarykey]
        id: U64,
        #[index]
        market_id: String,
        #[index]
        player_id: Identity,
        difficulty: Float64,
        stake: Float64,
        timestamp: Timestamp,
    }

    // Guild competition
    table guild_competition {
        #[primarykey]
        competition_id: String,
        name: String,
        start_date: Timestamp,
        end_date: Timestamp,
        subjects: Vec<String>,
    }

    // Guild competition scores
    table guild_score {
        #[primarykey]
        id: U64,
        #[index]
        competition_id: String,
        #[index]
        guild_id: String,
        total_points: Float64,
        prediction_count: U32,
    }

    // Player prediction stats
    table player_prediction_stats {
        #[primarykey]
        player_id: Identity,
        total_predictions: U32,
        exact_matches: U32,
        close_matches: U32,
        total_staked: Float64,
        total_winnings: Float64,
        calibration_score: Float64,
    }

    // Reducers

    #[reducer]
    fn create_self_prediction(
        player_id: Identity,
        subject: String,
        predicted_grade: String,
        confidence: Float64,
        stake_amount: Float64,
        exam_date: Timestamp,
    ) {
        // Validate inputs
        assert!(confidence >= 0.1 && confidence <= 0.99);
        assert!(stake_amount > 0.0);

        let prediction_id = format!("pred_{}_{}", player_id, subject);

        // Deduct stake from player balance (would call token contract)

        SelfPrediction::insert(SelfPrediction {
            prediction_id,
            player_id,
            subject,
            predicted_grade,
            confidence,
            stake_amount,
            exam_date,
            created_at: Timestamp::now(),
            actual_grade: None,
            resolved: false,
            payout: 0.0,
        });
    }

    #[reducer]
    fn resolve_self_prediction(
        prediction_id: String,
        actual_grade: String,
        verifier: Identity,  // Teacher or oracle
    ) {
        let mut pred = SelfPrediction::filter_by_prediction_id(&prediction_id)
            .expect("Prediction not found");

        assert!(!pred.resolved, "Already resolved");

        // Calculate grade distance
        let grades = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8"];
        let pred_idx = grades.iter().position(|&g| g == pred.predicted_grade).unwrap();
        let actual_idx = grades.iter().position(|&g| g == actual_grade).unwrap();
        let distance = (pred_idx as i32 - actual_idx as i32).abs();

        // Calculate payout
        let payout = if distance == 0 {
            pred.stake_amount * calculate_return_multiplier(pred.confidence)
        } else if distance == 1 {
            pred.stake_amount * 0.5
        } else {
            0.0
        };

        pred.actual_grade = Some(actual_grade);
        pred.resolved = true;
        pred.payout = payout;

        SelfPrediction::update_by_prediction_id(&prediction_id, pred);

        // Update player stats
        update_player_stats(pred.player_id, distance == 0, distance == 1, payout);
    }

    #[reducer]
    fn submit_difficulty_prediction(
        market_id: String,
        player_id: Identity,
        difficulty: Float64,
        stake: Float64,
    ) {
        assert!(difficulty >= 1.0 && difficulty <= 10.0);

        DifficultyPrediction::insert(DifficultyPrediction {
            id: 0,  // Auto-increment
            market_id: market_id.clone(),
            player_id,
            difficulty,
            stake,
            timestamp: Timestamp::now(),
        });

        // Update market consensus
        recalculate_consensus(&market_id);
    }
    """

    print("SpacetimeDB Schema for Exam Predictions")
    print("=" * 50)
    print(spacetimedb_schema[:2000] + "...")
    return (spacetimedb_schema,)


@app.cell
def _(mo):
    mo.md("""
    ## Anchor Program Structure

    Solana program for exam prediction markets.
    """)
    return


@app.cell
def _():
    anchor_program = """
    // Anchor Program: tuath_exam_predictions
    // Solana implementation of exam prediction markets

    use anchor_lang::prelude::*;
    use anchor_spl::token::{Token, TokenAccount, Transfer};

    declare_id!("ExmPrd111111111111111111111111111111111111");

    #[program]
    pub mod tuath_exam_predictions {
        use super::*;

        /// Create a self-prediction market
        pub fn create_self_prediction(
            ctx: Context<CreateSelfPrediction>,
            subject: String,
            predicted_grade: u8,  // 0 = H1, 7 = H8
            confidence: u64,      // Basis points (5000 = 50%)
            exam_date: i64,
        ) -> Result<()> {
            require!(confidence >= 1000 && confidence <= 9900, ErrorCode::InvalidConfidence);
            require!(predicted_grade <= 7, ErrorCode::InvalidGrade);

            let prediction = &mut ctx.accounts.prediction;
            prediction.player = ctx.accounts.player.key();
            prediction.subject = subject;
            prediction.predicted_grade = predicted_grade;
            prediction.confidence = confidence;
            prediction.stake_amount = ctx.accounts.stake_source.amount;
            prediction.exam_date = exam_date;
            prediction.created_at = Clock::get()?.unix_timestamp;
            prediction.resolved = false;
            prediction.bump = ctx.bumps.prediction;

            // Transfer stake to vault
            let transfer_ctx = CpiContext::new(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.stake_source.to_account_info(),
                    to: ctx.accounts.vault.to_account_info(),
                    authority: ctx.accounts.player.to_account_info(),
                },
            );
            anchor_spl::token::transfer(transfer_ctx, ctx.accounts.stake_source.amount)?;

            Ok(())
        }

        /// Resolve a self-prediction with actual grade
        pub fn resolve_prediction(
            ctx: Context<ResolvePrediction>,
            actual_grade: u8,
        ) -> Result<()> {
            let prediction = &mut ctx.accounts.prediction;
            require!(!prediction.resolved, ErrorCode::AlreadyResolved);
            require!(actual_grade <= 7, ErrorCode::InvalidGrade);

            let grade_distance = (prediction.predicted_grade as i16 - actual_grade as i16).abs();

            // Calculate payout
            let payout = if grade_distance == 0 {
                // Exact match - full return based on confidence
                calculate_return(prediction.stake_amount, prediction.confidence)
            } else if grade_distance == 1 {
                // One grade off - 50% return
                prediction.stake_amount / 2
            } else {
                // More than one grade off - no payout
                0
            };

            prediction.actual_grade = Some(actual_grade);
            prediction.resolved = true;
            prediction.payout = payout;

            // Transfer payout if any
            if payout > 0 {
                let seeds = &[
                    b"vault",
                    prediction.subject.as_bytes(),
                    &[ctx.accounts.vault.bump],
                ];
                let signer = &[&seeds[..]];

                let transfer_ctx = CpiContext::new_with_signer(
                    ctx.accounts.token_program.to_account_info(),
                    Transfer {
                        from: ctx.accounts.vault.to_account_info(),
                        to: ctx.accounts.player_token.to_account_info(),
                        authority: ctx.accounts.vault.to_account_info(),
                    },
                    signer,
                );
                anchor_spl::token::transfer(transfer_ctx, payout)?;
            }

            // Update player stats
            let stats = &mut ctx.accounts.player_stats;
            stats.total_predictions += 1;
            stats.total_staked += prediction.stake_amount;
            stats.total_winnings += payout;
            if grade_distance == 0 {
                stats.exact_matches += 1;
            } else if grade_distance == 1 {
                stats.close_matches += 1;
            }

            Ok(())
        }

        /// Submit difficulty prediction for a subject
        pub fn submit_difficulty_prediction(
            ctx: Context<SubmitDifficultyPrediction>,
            difficulty: u8,  // 1-10 scale
            stake: u64,
        ) -> Result<()> {
            require!(difficulty >= 1 && difficulty <= 10, ErrorCode::InvalidDifficulty);

            let market = &mut ctx.accounts.market;
            let prediction = &mut ctx.accounts.difficulty_prediction;

            prediction.player = ctx.accounts.player.key();
            prediction.market = market.key();
            prediction.difficulty = difficulty;
            prediction.stake = stake;
            prediction.timestamp = Clock::get()?.unix_timestamp;

            // Update market consensus
            market.total_predictions += 1;
            market.total_stake += stake;
            market.weighted_difficulty += (difficulty as u64) * stake;
            market.liquidity += stake;

            Ok(())
        }
    }

    #[derive(Accounts)]
    #[instruction(subject: String)]
    pub struct CreateSelfPrediction<'info> {
        #[account(mut)]
        pub player: Signer<'info>,

        #[account(
            init,
            payer = player,
            space = 8 + SelfPrediction::INIT_SPACE,
            seeds = [b"prediction", player.key().as_ref(), subject.as_bytes()],
            bump,
        )]
        pub prediction: Account<'info, SelfPrediction>,

        #[account(mut)]
        pub stake_source: Account<'info, TokenAccount>,

        #[account(
            mut,
            seeds = [b"vault", subject.as_bytes()],
            bump,
        )]
        pub vault: Account<'info, TokenAccount>,

        pub token_program: Program<'info, Token>,
        pub system_program: Program<'info, System>,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct SelfPrediction {
        pub player: Pubkey,
        #[max_len(32)]
        pub subject: String,
        pub predicted_grade: u8,
        pub confidence: u64,
        pub stake_amount: u64,
        pub exam_date: i64,
        pub created_at: i64,
        pub actual_grade: Option<u8>,
        pub resolved: bool,
        pub payout: u64,
        pub bump: u8,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct PlayerStats {
        pub player: Pubkey,
        pub total_predictions: u32,
        pub exact_matches: u32,
        pub close_matches: u32,
        pub total_staked: u64,
        pub total_winnings: u64,
    }

    #[account]
    #[derive(InitSpace)]
    pub struct DifficultyMarket {
        pub exam_year: u16,
        #[max_len(32)]
        pub subject: String,
        pub total_predictions: u32,
        pub total_stake: u64,
        pub weighted_difficulty: u64,
        pub liquidity: u64,
        pub resolved: bool,
        pub actual_difficulty: Option<u8>,
    }

    #[error_code]
    pub enum ErrorCode {
        #[msg("Confidence must be between 10% and 99%")]
        InvalidConfidence,
        #[msg("Grade must be H1-H8 (0-7)")]
        InvalidGrade,
        #[msg("Prediction already resolved")]
        AlreadyResolved,
        #[msg("Difficulty must be 1-10")]
        InvalidDifficulty,
    }
    """

    print("Anchor Program: tuath_exam_predictions")
    print("=" * 50)
    print(anchor_program[:2500] + "...")
    return (anchor_program,)


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Challenge 7 Complete

    ### Key Learnings

    1. **Self-Prediction Markets**: Players predict own exam grades for motivation
    2. **Subject Difficulty**: Aggregate predictions on exam difficulty
    3. **Guild Competitions**: Inter-guild academic competitions
    4. **Reputation System**: Track prediction accuracy over time

    ### tuath Integration

    - Prediction markets for Leaving Certificate subjects
    - XP bonuses for accurate self-predictions
    - Guild leaderboards for academic achievement
    - SpacetimeDB storage + Anchor program

    ### Motivation Mechanics

    | Prediction Type | Stake | Correct | Partial |
    |-----------------|-------|---------|---------|
    | Self-prediction | Required | 2x return | 50% |
    | Difficulty | Optional | Based on error | Graduated |
    | Guild | Pool | Shared | Rank-based |

    ### Next Steps

    - Challenge 8: ZK Voting for anonymous guild governance
    - Integration with NCCA curriculum milestones
    - Teacher verification oracles
    """)
    return


if __name__ == "__main__":
    app.run()
