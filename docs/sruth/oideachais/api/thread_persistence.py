"""
Thread Persistence for AG-UI Protocol.

Provides persistent storage for conversation threads with:
- PostgreSQL (PlanetScale) for metadata and messages
- Cognee integration for memory enrichment
- Redis for fast access caching
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from storage.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """A message in a thread."""

    id: str
    role: str  # user, assistant, system, tool
    content: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict] | None = None
    tool_results: list[dict] | None = None


@dataclass
class Thread:
    """A conversation thread."""

    id: str
    user_id: str | None
    agent_name: str
    title: str | None
    messages: list[Message]
    state: dict[str, Any]
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def message_count(self) -> int:
        return len(self.messages)

    @property
    def last_message(self) -> Message | None:
        return self.messages[-1] if self.messages else None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_name": self.agent_name,
            "title": self.title,
            "messages": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata,
                    "tool_calls": m.tool_calls,
                    "tool_results": m.tool_results,
                }
                for m in self.messages
            ],
            "state": self.state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


class ThreadPersistence:
    """
    Persistent thread storage with PostgreSQL and Redis caching.
    """

    def __init__(self):
        self.config = get_config()
        self._pool = None
        self._redis = None

    def _get_pool(self):
        """Get PostgreSQL connection pool."""
        if self._pool is None:
            import psycopg2
            from psycopg2 import pool

            self._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **self.config.planetscale.dsn,
            )
        return self._pool

    def _get_redis(self):
        """Get Redis client for caching."""
        if self._redis is None:
            import redis

            self._redis = redis.from_url(self.config.redis.url)
        return self._redis

    def close(self) -> None:
        """Close connections."""
        if self._pool:
            self._pool.closeall()
            self._pool = None
        if self._redis:
            self._redis.close()
            self._redis = None

    # =========================================================================
    # Schema Initialization
    # =========================================================================

    def init_schema(self) -> None:
        """Initialize the thread tables."""
        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS threads (
                        id UUID PRIMARY KEY,
                        user_id VARCHAR(255),
                        agent_name VARCHAR(100) NOT NULL,
                        title TEXT,
                        state JSONB DEFAULT '{}',
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );

                    CREATE TABLE IF NOT EXISTS thread_messages (
                        id UUID PRIMARY KEY,
                        thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        tool_calls JSONB,
                        tool_results JSONB,
                        created_at TIMESTAMP DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_threads_user ON threads(user_id);
                    CREATE INDEX IF NOT EXISTS idx_threads_agent ON threads(agent_name);
                    CREATE INDEX IF NOT EXISTS idx_threads_updated ON threads(updated_at DESC);
                    CREATE INDEX IF NOT EXISTS idx_messages_thread ON thread_messages(thread_id);
                    CREATE INDEX IF NOT EXISTS idx_messages_created ON thread_messages(created_at);
                """)
                conn.commit()
                logger.info("Thread persistence schema initialized")
        finally:
            pool.putconn(conn)

    # =========================================================================
    # Thread Operations
    # =========================================================================

    def create_thread(
        self,
        agent_name: str,
        user_id: str | None = None,
        title: str | None = None,
        initial_state: dict | None = None,
        metadata: dict | None = None,
    ) -> Thread:
        """Create a new thread."""
        thread_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO threads (id, user_id, agent_name, title, state, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at, updated_at
                    """,
                    (
                        thread_id,
                        user_id,
                        agent_name,
                        title,
                        json.dumps(initial_state or {}),
                        json.dumps(metadata or {}),
                    ),
                )
                result = cur.fetchone()
                conn.commit()

                thread = Thread(
                    id=str(result[0]),
                    user_id=user_id,
                    agent_name=agent_name,
                    title=title,
                    messages=[],
                    state=initial_state or {},
                    created_at=result[1].isoformat(),
                    updated_at=result[2].isoformat(),
                    metadata=metadata or {},
                )

                # Cache in Redis
                self._cache_thread(thread)

                return thread
        finally:
            pool.putconn(conn)

    def get_thread(self, thread_id: str) -> Thread | None:
        """Get a thread by ID."""
        # Try cache first
        cached = self._get_cached_thread(thread_id)
        if cached:
            return cached

        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                # Get thread
                cur.execute(
                    """
                    SELECT id, user_id, agent_name, title, state, metadata, created_at, updated_at
                    FROM threads WHERE id = %s
                    """,
                    (thread_id,),
                )
                row = cur.fetchone()

                if not row:
                    return None

                # Get messages
                cur.execute(
                    """
                    SELECT id, role, content, metadata, tool_calls, tool_results, created_at
                    FROM thread_messages
                    WHERE thread_id = %s
                    ORDER BY created_at
                    """,
                    (thread_id,),
                )
                message_rows = cur.fetchall()

                messages = [
                    Message(
                        id=str(m[0]),
                        role=m[1],
                        content=m[2],
                        metadata=m[3] or {},
                        tool_calls=m[4],
                        tool_results=m[5],
                        timestamp=m[6].isoformat(),
                    )
                    for m in message_rows
                ]

                thread = Thread(
                    id=str(row[0]),
                    user_id=row[1],
                    agent_name=row[2],
                    title=row[3],
                    state=row[4] or {},
                    metadata=row[5] or {},
                    created_at=row[6].isoformat(),
                    updated_at=row[7].isoformat(),
                    messages=messages,
                )

                # Cache for future access
                self._cache_thread(thread)

                return thread
        finally:
            pool.putconn(conn)

    def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
        tool_calls: list[dict] | None = None,
        tool_results: list[dict] | None = None,
    ) -> Message:
        """Add a message to a thread."""
        message_id = str(uuid.uuid4())
        now = datetime.utcnow()

        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                # Insert message
                cur.execute(
                    """
                    INSERT INTO thread_messages (id, thread_id, role, content, metadata, tool_calls, tool_results)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, created_at
                    """,
                    (
                        message_id,
                        thread_id,
                        role,
                        content,
                        json.dumps(metadata or {}),
                        json.dumps(tool_calls) if tool_calls else None,
                        json.dumps(tool_results) if tool_results else None,
                    ),
                )
                result = cur.fetchone()

                # Update thread timestamp
                cur.execute(
                    "UPDATE threads SET updated_at = NOW() WHERE id = %s",
                    (thread_id,),
                )
                conn.commit()

                message = Message(
                    id=str(result[0]),
                    role=role,
                    content=content,
                    timestamp=result[1].isoformat(),
                    metadata=metadata or {},
                    tool_calls=tool_calls,
                    tool_results=tool_results,
                )

                # Invalidate cache
                self._invalidate_thread_cache(thread_id)

                return message
        finally:
            pool.putconn(conn)

    def update_state(self, thread_id: str, state: dict, merge: bool = True) -> dict:
        """Update thread state."""
        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                if merge:
                    # Merge with existing state
                    cur.execute(
                        """
                        UPDATE threads
                        SET state = state || %s, updated_at = NOW()
                        WHERE id = %s
                        RETURNING state
                        """,
                        (json.dumps(state), thread_id),
                    )
                else:
                    # Replace state
                    cur.execute(
                        """
                        UPDATE threads
                        SET state = %s, updated_at = NOW()
                        WHERE id = %s
                        RETURNING state
                        """,
                        (json.dumps(state), thread_id),
                    )

                result = cur.fetchone()
                conn.commit()

                # Invalidate cache
                self._invalidate_thread_cache(thread_id)

                return result[0] if result else {}
        finally:
            pool.putconn(conn)

    def list_threads(
        self,
        user_id: str | None = None,
        agent_name: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """List threads with optional filters."""
        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                query = """
                    SELECT id, user_id, agent_name, title, metadata, created_at, updated_at,
                           (SELECT COUNT(*) FROM thread_messages WHERE thread_id = threads.id) as message_count
                    FROM threads
                    WHERE 1=1
                """
                params = []

                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)

                if agent_name:
                    query += " AND agent_name = %s"
                    params.append(agent_name)

                query += " ORDER BY updated_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cur.execute(query, tuple(params))
                rows = cur.fetchall()

                return [
                    {
                        "id": str(row[0]),
                        "user_id": row[1],
                        "agent_name": row[2],
                        "title": row[3],
                        "metadata": row[4] or {},
                        "created_at": row[5].isoformat(),
                        "updated_at": row[6].isoformat(),
                        "message_count": row[7],
                    }
                    for row in rows
                ]
        finally:
            pool.putconn(conn)

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its messages."""
        pool = self._get_pool()
        conn = pool.getconn()

        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM threads WHERE id = %s", (thread_id,))
                deleted = cur.rowcount > 0
                conn.commit()

                # Invalidate cache
                self._invalidate_thread_cache(thread_id)

                return deleted
        finally:
            pool.putconn(conn)

    # =========================================================================
    # Redis Caching
    # =========================================================================

    def _cache_thread(self, thread: Thread, ttl: int = 3600) -> None:
        """Cache a thread in Redis."""
        try:
            redis = self._get_redis()
            redis.setex(
                f"thread:{thread.id}",
                ttl,
                json.dumps(thread.to_dict()),
            )
        except Exception as e:
            logger.warning(f"Failed to cache thread: {e}")

    def _get_cached_thread(self, thread_id: str) -> Thread | None:
        """Get a cached thread from Redis."""
        try:
            redis = self._get_redis()
            data = redis.get(f"thread:{thread_id}")
            if data:
                d = json.loads(data)
                return Thread(
                    id=d["id"],
                    user_id=d["user_id"],
                    agent_name=d["agent_name"],
                    title=d["title"],
                    messages=[
                        Message(
                            id=m["id"],
                            role=m["role"],
                            content=m["content"],
                            timestamp=m["timestamp"],
                            metadata=m.get("metadata", {}),
                            tool_calls=m.get("tool_calls"),
                            tool_results=m.get("tool_results"),
                        )
                        for m in d["messages"]
                    ],
                    state=d["state"],
                    created_at=d["created_at"],
                    updated_at=d["updated_at"],
                    metadata=d.get("metadata", {}),
                )
        except Exception as e:
            logger.warning(f"Failed to get cached thread: {e}")
        return None

    def _invalidate_thread_cache(self, thread_id: str) -> None:
        """Invalidate a cached thread."""
        try:
            redis = self._get_redis()
            redis.delete(f"thread:{thread_id}")
        except Exception as e:
            logger.warning(f"Failed to invalidate thread cache: {e}")

    # =========================================================================
    # Cognee Integration
    # =========================================================================

    async def add_to_memory(self, thread: Thread) -> None:
        """
        Add thread to Cognee memory for context enrichment.

        This enables:
        - Semantic search across conversation history
        - Context retrieval for agents
        - Knowledge graph integration
        """
        try:
            from memory.cognee_service import CelticMemoryService

            memory = CelticMemoryService()

            # Prepare conversation text
            conversation_text = "\n".join(
                f"{m.role.upper()}: {m.content}" for m in thread.messages
            )

            # Add to Cognee as manuscript (using existing method)
            await memory.add_manuscript(
                text=conversation_text,
                source="conversation",
                metadata={
                    "thread_id": thread.id,
                    "agent_name": thread.agent_name,
                    "user_id": thread.user_id,
                    "message_count": len(thread.messages),
                    "created_at": thread.created_at,
                },
            )

            logger.info(f"Added thread {thread.id} to Cognee memory")
        except ImportError:
            logger.debug("Cognee not available, skipping memory integration")
        except Exception as e:
            logger.warning(f"Failed to add thread to Cognee memory: {e}")


# Singleton instance
_thread_persistence: ThreadPersistence | None = None


def get_thread_persistence() -> ThreadPersistence:
    """Get the thread persistence singleton."""
    global _thread_persistence
    if _thread_persistence is None:
        _thread_persistence = ThreadPersistence()
    return _thread_persistence
