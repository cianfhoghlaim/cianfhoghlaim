"""
Game State Service for Tuath.

Provides synchronization with SpacetimeDB for multiplayer state.
"""



class GameStateService:
    """Service for game state management via SpacetimeDB."""

    def __init__(
        self,
        spacetimedb_url: str | None = None,
        module_name: str = "tuath",
    ):
        """Initialize SpacetimeDB connection."""
        self.spacetimedb_url = spacetimedb_url or "ws://localhost:3000"
        self.module_name = module_name
        self._client = None

    @property
    def client(self):
        """Get or create SpacetimeDB client."""
        if self._client is None:
            try:
                from spacetimedb_sdk import SpacetimeDBClient
                self._client = SpacetimeDBClient(
                    host=self.spacetimedb_url,
                    module_name=self.module_name,
                )
            except ImportError:
                self._client = None
        return self._client

    def close(self):
        """Close connection."""
        if self._client:
            self._client.close()
            self._client = None

    async def get_player(self, player_id: str) -> dict | None:
        """Get player state."""
        try:
            if not self.client:
                return None

            result = await self.client.query(
                "SELECT * FROM player WHERE id = ?",
                [player_id],
            )
            if result:
                return self._format_player(result[0])
            return None
        except Exception:
            return None

    async def update_player_position(
        self,
        player_id: str,
        x: float,
        y: float,
        z: float,
        zone: str,
    ) -> bool:
        """Update player position."""
        try:
            if not self.client:
                return False

            await self.client.call(
                "update_player_position",
                player_id,
                x,
                y,
                z,
                zone,
            )
            return True
        except Exception:
            return False

    async def get_players_in_zone(
        self,
        zone: str,
        limit: int = 50,
    ) -> list[dict]:
        """Get all players in a zone."""
        try:
            if not self.client:
                return []

            results = await self.client.query(
                "SELECT * FROM player WHERE zone = ? LIMIT ?",
                [zone, limit],
            )
            return [self._format_player(r) for r in results]
        except Exception:
            return []

    async def get_npcs_in_zone(
        self,
        zone: str,
    ) -> list[dict]:
        """Get NPCs in a zone."""
        try:
            if not self.client:
                return []

            results = await self.client.query(
                "SELECT * FROM npc WHERE zone = ?",
                [zone],
            )
            return [self._format_npc(r) for r in results]
        except Exception:
            return []

    async def get_active_quests(
        self,
        player_id: str,
    ) -> list[dict]:
        """Get player's active quests."""
        try:
            if not self.client:
                return []

            results = await self.client.query(
                """
                SELECT q.*, pq.progress, pq.started_at
                FROM quest q
                JOIN player_quest pq ON q.id = pq.quest_id
                WHERE pq.player_id = ? AND pq.status = 'active'
                """,
                [player_id],
            )
            return [self._format_quest(r) for r in results]
        except Exception:
            return []

    async def start_quest(
        self,
        player_id: str,
        quest_id: str,
    ) -> dict:
        """Start a quest for a player."""
        try:
            if not self.client:
                return {"success": False, "error": "SpacetimeDB not available"}

            await self.client.call(
                "start_quest",
                player_id,
                quest_id,
            )
            return {"success": True, "quest_id": quest_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def complete_quest_objective(
        self,
        player_id: str,
        quest_id: str,
        objective_id: str,
    ) -> dict:
        """Complete a quest objective."""
        try:
            if not self.client:
                return {"success": False, "error": "SpacetimeDB not available"}

            result = await self.client.call(
                "complete_objective",
                player_id,
                quest_id,
                objective_id,
            )
            return {
                "success": True,
                "quest_id": quest_id,
                "objective_id": objective_id,
                "quest_completed": result.get("quest_completed", False),
                "rewards": result.get("rewards", []),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def send_chat_message(
        self,
        player_id: str,
        message: str,
        channel: str = "zone",
        zone: str | None = None,
    ) -> bool:
        """Send a chat message."""
        try:
            if not self.client:
                return False

            await self.client.call(
                "send_message",
                player_id,
                message,
                channel,
                zone,
            )
            return True
        except Exception:
            return False

    async def get_zone_chat_history(
        self,
        zone: str,
        limit: int = 50,
    ) -> list[dict]:
        """Get zone chat history."""
        try:
            if not self.client:
                return []

            results = await self.client.query(
                """
                SELECT m.*, p.username
                FROM chat_message m
                JOIN player p ON m.player_id = p.id
                WHERE m.zone = ? AND m.channel = 'zone'
                ORDER BY m.sent_at DESC
                LIMIT ?
                """,
                [zone, limit],
            )
            return [
                {
                    "id": r["id"],
                    "player_id": r["player_id"],
                    "username": r["username"],
                    "message": r["message"],
                    "sent_at": r["sent_at"],
                }
                for r in results
            ]
        except Exception:
            return []

    async def interact_with_npc(
        self,
        player_id: str,
        npc_id: str,
        interaction_type: str = "dialogue",
    ) -> dict:
        """Initiate NPC interaction."""
        try:
            if not self.client:
                return {"success": False, "error": "SpacetimeDB not available"}

            result = await self.client.call(
                "npc_interaction",
                player_id,
                npc_id,
                interaction_type,
            )
            return {
                "success": True,
                "npc_id": npc_id,
                "interaction_type": interaction_type,
                "response": result.get("response"),
                "available_actions": result.get("available_actions", []),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _format_player(self, data: dict) -> dict:
        """Format player data."""
        return {
            "id": data.get("id"),
            "username": data.get("username"),
            "position": {
                "x": data.get("x", 0),
                "y": data.get("y", 0),
                "z": data.get("z", 0),
            },
            "zone": data.get("zone"),
            "level": data.get("level", 1),
            "experience": data.get("experience", 0),
            "language_level": {
                "irish": data.get("irish_level", 0),
                "welsh": data.get("welsh_level", 0),
                "scottish_gaelic": data.get("gaelic_level", 0),
            },
            "last_seen": data.get("last_seen"),
        }

    def _format_npc(self, data: dict) -> dict:
        """Format NPC data."""
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "archetype": data.get("archetype"),
            "position": {
                "x": data.get("x", 0),
                "y": data.get("y", 0),
                "z": data.get("z", 0),
            },
            "zone": data.get("zone"),
            "dialogue_state": data.get("dialogue_state"),
            "available_quests": data.get("available_quests", []),
        }

    def _format_quest(self, data: dict) -> dict:
        """Format quest data."""
        return {
            "id": data.get("id"),
            "title": data.get("title"),
            "description": data.get("description"),
            "objectives": data.get("objectives", []),
            "progress": data.get("progress", {}),
            "rewards": data.get("rewards", []),
            "started_at": data.get("started_at"),
            "language_requirement": data.get("language_requirement"),
        }
