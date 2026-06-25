"""
Player Progress Service for Tuath.

Tracks learning progress, achievements, and educational analytics.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb


class PlayerProgressService:
    """Service for player learning progress tracking."""

    def __init__(self, db_path: str):
        """Initialize DuckDB connection for progress tracking."""
        self.db_path = db_path
        self._conn = None

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create connection."""
        if self._conn is None:
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def close(self):
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    async def get_player_progress(
        self,
        player_id: str,
    ) -> dict:
        """Get overall player progress."""
        try:
            result = self.conn.execute(
                """
                SELECT player_id,
                       total_xp, level,
                       words_learned, phrases_learned,
                       quests_completed, lessons_completed,
                       current_streak_days, longest_streak_days,
                       last_activity
                FROM progress.player_summary
                WHERE player_id = ?
                """,
                [player_id],
            ).fetchone()

            if result:
                return {
                    "player_id": result[0],
                    "total_xp": result[1],
                    "level": result[2],
                    "words_learned": result[3],
                    "phrases_learned": result[4],
                    "quests_completed": result[5],
                    "lessons_completed": result[6],
                    "current_streak": result[7],
                    "longest_streak": result[8],
                    "last_activity": str(result[9]) if result[9] else None,
                }
            return {
                "player_id": player_id,
                "total_xp": 0,
                "level": 1,
                "words_learned": 0,
                "phrases_learned": 0,
                "quests_completed": 0,
                "lessons_completed": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity": None,
            }
        except Exception:
            return {"player_id": player_id, "error": "Failed to fetch progress"}

    async def get_language_progress(
        self,
        player_id: str,
        language: str,
    ) -> dict:
        """Get progress for a specific language."""
        try:
            result = self.conn.execute(
                """
                SELECT player_id, language,
                       proficiency_level, xp,
                       vocabulary_count, grammar_score,
                       listening_score, speaking_score,
                       reading_score, writing_score,
                       last_practice
                FROM progress.language_progress
                WHERE player_id = ? AND language = ?
                """,
                [player_id, language],
            ).fetchone()

            if result:
                return {
                    "player_id": result[0],
                    "language": result[1],
                    "proficiency_level": result[2],
                    "xp": result[3],
                    "vocabulary_count": result[4],
                    "skills": {
                        "grammar": result[5],
                        "listening": result[6],
                        "speaking": result[7],
                        "reading": result[8],
                        "writing": result[9],
                    },
                    "last_practice": str(result[10]) if result[10] else None,
                }
            return {
                "player_id": player_id,
                "language": language,
                "proficiency_level": "beginner",
                "xp": 0,
                "vocabulary_count": 0,
                "skills": {
                    "grammar": 0,
                    "listening": 0,
                    "speaking": 0,
                    "reading": 0,
                    "writing": 0,
                },
                "last_practice": None,
            }
        except Exception:
            return {"player_id": player_id, "language": language, "error": "Failed to fetch"}

    async def record_lesson_completion(
        self,
        player_id: str,
        lesson_id: str,
        language: str,
        score: float,
        time_spent_seconds: int,
        learning_outcomes: list[str],
    ) -> dict:
        """Record a completed lesson."""
        try:
            self.conn.execute(
                """
                INSERT INTO progress.lesson_completions
                (player_id, lesson_id, language, score, time_spent_seconds,
                 learning_outcomes, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    player_id,
                    lesson_id,
                    language,
                    score,
                    time_spent_seconds,
                    learning_outcomes,
                    datetime.utcnow(),
                ],
            )

            xp_earned = int(score * 10) + len(learning_outcomes) * 5

            self.conn.execute(
                """
                UPDATE progress.player_summary
                SET total_xp = total_xp + ?,
                    lessons_completed = lessons_completed + 1,
                    last_activity = ?
                WHERE player_id = ?
                """,
                [xp_earned, datetime.utcnow(), player_id],
            )

            return {
                "success": True,
                "xp_earned": xp_earned,
                "lesson_id": lesson_id,
                "score": score,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def record_vocabulary_learned(
        self,
        player_id: str,
        language: str,
        words: list[dict],
    ) -> dict:
        """Record vocabulary words learned."""
        try:
            for word in words:
                self.conn.execute(
                    """
                    INSERT INTO progress.vocabulary_learned
                    (player_id, language, word, translation, category,
                     proficiency, learned_at, last_reviewed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (player_id, language, word)
                    DO UPDATE SET proficiency = proficiency + 1, last_reviewed = ?
                    """,
                    [
                        player_id,
                        language,
                        word.get("word"),
                        word.get("translation"),
                        word.get("category"),
                        1,
                        datetime.utcnow(),
                        datetime.utcnow(),
                        datetime.utcnow(),
                    ],
                )

            self.conn.execute(
                """
                UPDATE progress.player_summary
                SET words_learned = words_learned + ?
                WHERE player_id = ?
                """,
                [len(words), player_id],
            )

            return {
                "success": True,
                "words_added": len(words),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_vocabulary_for_review(
        self,
        player_id: str,
        language: str,
        limit: int = 20,
    ) -> list[dict]:
        """Get vocabulary due for spaced repetition review."""
        try:
            results = self.conn.execute(
                """
                SELECT word, translation, category, proficiency,
                       last_reviewed, learned_at
                FROM progress.vocabulary_learned
                WHERE player_id = ? AND language = ?
                  AND (last_reviewed < NOW() - INTERVAL '1 day' * proficiency
                       OR proficiency < 3)
                ORDER BY proficiency ASC, last_reviewed ASC
                LIMIT ?
                """,
                [player_id, language, limit],
            ).fetchall()

            return [
                {
                    "word": r[0],
                    "translation": r[1],
                    "category": r[2],
                    "proficiency": r[3],
                    "last_reviewed": str(r[4]) if r[4] else None,
                    "learned_at": str(r[5]) if r[5] else None,
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_achievements(
        self,
        player_id: str,
    ) -> list[dict]:
        """Get player achievements."""
        try:
            results = self.conn.execute(
                """
                SELECT a.id, a.name, a.description, a.category,
                       a.xp_reward, pa.earned_at
                FROM progress.achievements a
                JOIN progress.player_achievements pa ON a.id = pa.achievement_id
                WHERE pa.player_id = ?
                ORDER BY pa.earned_at DESC
                """,
                [player_id],
            ).fetchall()

            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "description": r[2],
                    "category": r[3],
                    "xp_reward": r[4],
                    "earned_at": str(r[5]) if r[5] else None,
                }
                for r in results
            ]
        except Exception:
            return []

    async def check_and_award_achievements(
        self,
        player_id: str,
    ) -> list[dict]:
        """Check and award any earned achievements."""
        try:
            progress = await self.get_player_progress(player_id)

            new_achievements = []
            achievement_checks = [
                ("first_word", progress.get("words_learned", 0) >= 1),
                ("vocabulary_10", progress.get("words_learned", 0) >= 10),
                ("vocabulary_100", progress.get("words_learned", 0) >= 100),
                ("first_quest", progress.get("quests_completed", 0) >= 1),
                ("quests_10", progress.get("quests_completed", 0) >= 10),
                ("streak_7", progress.get("current_streak", 0) >= 7),
                ("streak_30", progress.get("current_streak", 0) >= 30),
            ]

            for achievement_id, condition in achievement_checks:
                if condition:
                    existing = self.conn.execute(
                        """
                        SELECT 1 FROM progress.player_achievements
                        WHERE player_id = ? AND achievement_id = ?
                        """,
                        [player_id, achievement_id],
                    ).fetchone()

                    if not existing:
                        self.conn.execute(
                            """
                            INSERT INTO progress.player_achievements
                            (player_id, achievement_id, earned_at)
                            VALUES (?, ?, ?)
                            """,
                            [player_id, achievement_id, datetime.utcnow()],
                        )

                        achievement = self.conn.execute(
                            "SELECT name, xp_reward FROM progress.achievements WHERE id = ?",
                            [achievement_id],
                        ).fetchone()

                        if achievement:
                            new_achievements.append({
                                "id": achievement_id,
                                "name": achievement[0],
                                "xp_reward": achievement[1],
                            })

            return new_achievements
        except Exception:
            return []

    async def get_leaderboard(
        self,
        language: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get player leaderboard."""
        try:
            if language:
                results = self.conn.execute(
                    """
                    SELECT p.player_id, p.total_xp, p.level, lp.xp as language_xp
                    FROM progress.player_summary p
                    JOIN progress.language_progress lp ON p.player_id = lp.player_id
                    WHERE lp.language = ?
                    ORDER BY lp.xp DESC
                    LIMIT ?
                    """,
                    [language, limit],
                ).fetchall()
            else:
                results = self.conn.execute(
                    """
                    SELECT player_id, total_xp, level, NULL as language_xp
                    FROM progress.player_summary
                    ORDER BY total_xp DESC
                    LIMIT ?
                    """,
                    [limit],
                ).fetchall()

            return [
                {
                    "rank": i + 1,
                    "player_id": r[0],
                    "total_xp": r[1],
                    "level": r[2],
                    "language_xp": r[3],
                }
                for i, r in enumerate(results)
            ]
        except Exception:
            return []

    async def get_learning_analytics(
        self,
        player_id: str,
        days: int = 30,
    ) -> dict:
        """Get learning analytics for a player."""
        try:
            daily = self.conn.execute(
                """
                SELECT DATE(completed_at) as date,
                       COUNT(*) as lessons,
                       AVG(score) as avg_score,
                       SUM(time_spent_seconds) as total_time
                FROM progress.lesson_completions
                WHERE player_id = ?
                  AND completed_at > NOW() - INTERVAL '? days'
                GROUP BY DATE(completed_at)
                ORDER BY date
                """,
                [player_id, days],
            ).fetchall()

            return {
                "player_id": player_id,
                "period_days": days,
                "daily_activity": [
                    {
                        "date": str(r[0]),
                        "lessons": r[1],
                        "avg_score": round(r[2], 2) if r[2] else 0,
                        "time_minutes": round(r[3] / 60, 1) if r[3] else 0,
                    }
                    for r in daily
                ],
                "total_lessons": sum(r[1] for r in daily),
                "total_time_hours": round(sum(r[3] or 0 for r in daily) / 3600, 1),
            }
        except Exception:
            return {
                "player_id": player_id,
                "period_days": days,
                "daily_activity": [],
                "total_lessons": 0,
                "total_time_hours": 0,
            }
