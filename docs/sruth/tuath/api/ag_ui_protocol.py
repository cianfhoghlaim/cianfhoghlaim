"""
AG-UI Protocol Implementation for Tuath Celtic Educational MMO.

Complete implementation of all 17 AG-UI (Agent-User Interface) event types
for CopilotKit integration with proper streaming support.

Event Categories:
- Lifecycle: RUN_STARTED, RUN_FINISHED, RUN_ERROR, STEP_STARTED, STEP_FINISHED
- Messages: TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END
- Tools: TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_RESULT
- State: STATE_SNAPSHOT, STATE_DELTA, MESSAGES_SNAPSHOT
- Special: RAW, CUSTOM

Adapted for Celtic educational gaming domain with game state management.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator


class AGUIEventType(str, Enum):
    """All 17 AG-UI protocol event types."""

    # Lifecycle events
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    STEP_STARTED = "STEP_STARTED"
    STEP_FINISHED = "STEP_FINISHED"

    # Message events
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"

    # Tool events
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_RESULT = "TOOL_RESULT"

    # State events
    STATE_SNAPSHOT = "STATE_SNAPSHOT"
    STATE_DELTA = "STATE_DELTA"
    MESSAGES_SNAPSHOT = "MESSAGES_SNAPSHOT"

    # Special events
    RAW = "RAW"
    CUSTOM = "CUSTOM"


@dataclass
class AGUIEvent:
    """Base AG-UI event structure."""

    type: AGUIEventType
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    run_id: str | None = None
    thread_id: str | None = None

    def to_sse(self) -> str:
        """Convert to Server-Sent Event format."""
        data = self.to_dict()
        return f"data: {json.dumps(data)}\n\n"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        d = asdict(self)
        d["type"] = self.type.value
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class RunStartedEvent(AGUIEvent):
    """Emitted when an agent run begins."""

    type: AGUIEventType = field(default=AGUIEventType.RUN_STARTED)
    agent_name: str | None = None
    input_message: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class RunFinishedEvent(AGUIEvent):
    """Emitted when an agent run completes successfully."""

    type: AGUIEventType = field(default=AGUIEventType.RUN_FINISHED)
    output: str | None = None
    duration_ms: int | None = None
    token_usage: dict[str, int] | None = None


@dataclass
class RunErrorEvent(AGUIEvent):
    """Emitted when an agent run encounters an error."""

    type: AGUIEventType = field(default=AGUIEventType.RUN_ERROR)
    error: str | None = None
    error_code: str | None = None
    recoverable: bool = False


@dataclass
class StepStartedEvent(AGUIEvent):
    """Emitted when a step within a run begins."""

    type: AGUIEventType = field(default=AGUIEventType.STEP_STARTED)
    step_id: str | None = None
    step_name: str | None = None
    step_type: str | None = None  # "agent", "tool", "llm"


@dataclass
class StepFinishedEvent(AGUIEvent):
    """Emitted when a step within a run completes."""

    type: AGUIEventType = field(default=AGUIEventType.STEP_FINISHED)
    step_id: str | None = None
    step_name: str | None = None
    duration_ms: int | None = None
    output: Any | None = None


@dataclass
class TextMessageStartEvent(AGUIEvent):
    """Emitted when a text message stream begins."""

    type: AGUIEventType = field(default=AGUIEventType.TEXT_MESSAGE_START)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "assistant"


@dataclass
class TextMessageContentEvent(AGUIEvent):
    """Emitted for each chunk of streaming text."""

    type: AGUIEventType = field(default=AGUIEventType.TEXT_MESSAGE_CONTENT)
    message_id: str | None = None
    content: str | None = None
    delta: str | None = None  # Incremental content


@dataclass
class TextMessageEndEvent(AGUIEvent):
    """Emitted when a text message stream ends."""

    type: AGUIEventType = field(default=AGUIEventType.TEXT_MESSAGE_END)
    message_id: str | None = None
    full_content: str | None = None


@dataclass
class ToolCallStartEvent(AGUIEvent):
    """Emitted when a tool call begins."""

    type: AGUIEventType = field(default=AGUIEventType.TOOL_CALL_START)
    tool_call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str | None = None


@dataclass
class ToolCallArgsEvent(AGUIEvent):
    """Emitted with tool call arguments (can stream)."""

    type: AGUIEventType = field(default=AGUIEventType.TOOL_CALL_ARGS)
    tool_call_id: str | None = None
    args: dict[str, Any] | None = None
    args_delta: str | None = None  # For streaming JSON args


@dataclass
class ToolCallEndEvent(AGUIEvent):
    """Emitted when a tool call finishes executing."""

    type: AGUIEventType = field(default=AGUIEventType.TOOL_CALL_END)
    tool_call_id: str | None = None
    tool_name: str | None = None


@dataclass
class ToolResultEvent(AGUIEvent):
    """Emitted with tool execution result."""

    type: AGUIEventType = field(default=AGUIEventType.TOOL_RESULT)
    tool_call_id: str | None = None
    tool_name: str | None = None
    result: Any | None = None
    error: str | None = None
    duration_ms: int | None = None


@dataclass
class StateSnapshotEvent(AGUIEvent):
    """Emitted with full state snapshot for CopilotKit shared state."""

    type: AGUIEventType = field(default=AGUIEventType.STATE_SNAPSHOT)
    state: dict[str, Any] | None = None
    state_key: str | None = None  # Optional key for partial state


@dataclass
class StateDeltaEvent(AGUIEvent):
    """Emitted with incremental state update."""

    type: AGUIEventType = field(default=AGUIEventType.STATE_DELTA)
    delta: dict[str, Any] | None = None
    operation: str | None = None  # "set", "delete", "merge"
    path: str | None = None  # JSON path for nested updates


@dataclass
class MessagesSnapshotEvent(AGUIEvent):
    """Emitted with full conversation history."""

    type: AGUIEventType = field(default=AGUIEventType.MESSAGES_SNAPSHOT)
    messages: list[dict[str, Any]] | None = None


@dataclass
class RawEvent(AGUIEvent):
    """Raw event for custom data passthrough."""

    type: AGUIEventType = field(default=AGUIEventType.RAW)
    data: Any | None = None


@dataclass
class CustomEvent(AGUIEvent):
    """Custom event for application-specific purposes."""

    type: AGUIEventType = field(default=AGUIEventType.CUSTOM)
    event_name: str | None = None
    payload: dict[str, Any] | None = None


class AGUIEventEmitter:
    """Helper class for emitting AG-UI events during agent execution."""

    def __init__(self, run_id: str | None = None, thread_id: str | None = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.thread_id = thread_id
        self._message_id: str | None = None
        self._tool_call_id: str | None = None
        self._accumulated_text: str = ""

    def _base_event(self, event_class: type, **kwargs) -> AGUIEvent:
        """Create event with run/thread context."""
        return event_class(run_id=self.run_id, thread_id=self.thread_id, **kwargs)

    # Lifecycle events
    def run_started(
        self, agent_name: str, input_message: str, metadata: dict | None = None
    ) -> RunStartedEvent:
        return self._base_event(
            RunStartedEvent,
            agent_name=agent_name,
            input_message=input_message,
            metadata=metadata,
        )

    def run_finished(
        self,
        output: str | None = None,
        duration_ms: int | None = None,
        token_usage: dict | None = None,
    ) -> RunFinishedEvent:
        return self._base_event(
            RunFinishedEvent,
            output=output,
            duration_ms=duration_ms,
            token_usage=token_usage,
        )

    def run_error(
        self, error: str, error_code: str | None = None, recoverable: bool = False
    ) -> RunErrorEvent:
        return self._base_event(
            RunErrorEvent, error=error, error_code=error_code, recoverable=recoverable
        )

    def step_started(self, step_name: str, step_type: str = "agent") -> StepStartedEvent:
        step_id = str(uuid.uuid4())
        return self._base_event(
            StepStartedEvent, step_id=step_id, step_name=step_name, step_type=step_type
        )

    def step_finished(
        self,
        step_id: str,
        step_name: str,
        duration_ms: int | None = None,
        output: Any = None,
    ) -> StepFinishedEvent:
        return self._base_event(
            StepFinishedEvent,
            step_id=step_id,
            step_name=step_name,
            duration_ms=duration_ms,
            output=output,
        )

    # Message events
    def text_message_start(self, role: str = "assistant") -> TextMessageStartEvent:
        self._message_id = str(uuid.uuid4())
        self._accumulated_text = ""
        return self._base_event(TextMessageStartEvent, message_id=self._message_id, role=role)

    def text_message_content(self, delta: str) -> TextMessageContentEvent:
        self._accumulated_text += delta
        return self._base_event(
            TextMessageContentEvent,
            message_id=self._message_id,
            content=self._accumulated_text,
            delta=delta,
        )

    def text_message_end(self) -> TextMessageEndEvent:
        event = self._base_event(
            TextMessageEndEvent,
            message_id=self._message_id,
            full_content=self._accumulated_text,
        )
        self._message_id = None
        return event

    # Tool events
    def tool_call_start(self, tool_name: str) -> ToolCallStartEvent:
        self._tool_call_id = str(uuid.uuid4())
        return self._base_event(
            ToolCallStartEvent, tool_call_id=self._tool_call_id, tool_name=tool_name
        )

    def tool_call_args(
        self, args: dict | None = None, args_delta: str | None = None
    ) -> ToolCallArgsEvent:
        return self._base_event(
            ToolCallArgsEvent,
            tool_call_id=self._tool_call_id,
            args=args,
            args_delta=args_delta,
        )

    def tool_call_end(self, tool_name: str) -> ToolCallEndEvent:
        event = self._base_event(
            ToolCallEndEvent, tool_call_id=self._tool_call_id, tool_name=tool_name
        )
        self._tool_call_id = None
        return event

    def tool_result(
        self,
        tool_name: str,
        result: Any = None,
        error: str | None = None,
        duration_ms: int | None = None,
    ) -> ToolResultEvent:
        return self._base_event(
            ToolResultEvent,
            tool_call_id=self._tool_call_id,
            tool_name=tool_name,
            result=result,
            error=error,
            duration_ms=duration_ms,
        )

    # State events
    def state_snapshot(self, state: dict, state_key: str | None = None) -> StateSnapshotEvent:
        return self._base_event(StateSnapshotEvent, state=state, state_key=state_key)

    def state_delta(
        self, delta: dict, operation: str = "merge", path: str | None = None
    ) -> StateDeltaEvent:
        return self._base_event(StateDeltaEvent, delta=delta, operation=operation, path=path)

    def messages_snapshot(self, messages: list[dict]) -> MessagesSnapshotEvent:
        return self._base_event(MessagesSnapshotEvent, messages=messages)

    # Special events
    def raw(self, data: Any) -> RawEvent:
        return self._base_event(RawEvent, data=data)

    def custom(self, event_name: str, payload: dict) -> CustomEvent:
        return self._base_event(CustomEvent, event_name=event_name, payload=payload)


async def stream_agui_events(
    generator: AsyncGenerator[AGUIEvent, None],
) -> AsyncGenerator[str, None]:
    """Convert AG-UI events to SSE format for streaming."""
    async for event in generator:
        yield event.to_sse()


class GameProgressState:
    """State container for Celtic MMO game progress (for CopilotKit shared state).

    Tracks player progress through curriculum, mythology exploration, and achievements.
    """

    def __init__(self):
        # Learning progress
        self.current_lesson: str | None = None
        self.current_topic: str | None = None
        self.completed_lessons: list[str] = []
        self.lesson_progress: float = 0.0

        # Game state
        self.current_character: str | None = None
        self.current_location: str | None = None
        self.discovered_locations: list[str] = []
        self.met_characters: list[str] = []

        # Achievements
        self.achievements: list[dict] = []
        self.xp_earned: int = 0
        self.level: int = 1

        # Celtic language progress
        self.vocabulary_learned: list[str] = []
        self.phrases_mastered: list[str] = []
        self.current_dialect: str = "standard"  # connacht, munster, ulster, standard

    def to_dict(self) -> dict:
        return {
            "currentLesson": self.current_lesson,
            "currentTopic": self.current_topic,
            "completedLessons": self.completed_lessons,
            "lessonProgress": self.lesson_progress,
            "currentCharacter": self.current_character,
            "currentLocation": self.current_location,
            "discoveredLocations": self.discovered_locations,
            "metCharacters": self.met_characters,
            "achievements": self.achievements,
            "xpEarned": self.xp_earned,
            "level": self.level,
            "vocabularyLearned": self.vocabulary_learned,
            "phrasesMastered": self.phrases_mastered,
            "currentDialect": self.current_dialect,
        }

    def update_from_event(self, event: dict) -> dict:
        """Update state from a game event and return delta."""
        delta = {}

        if event.get("type") == "lesson_started":
            self.current_lesson = event.get("lesson")
            self.current_topic = event.get("topic")
            self.lesson_progress = 0.0
            delta = {
                "currentLesson": self.current_lesson,
                "currentTopic": self.current_topic,
                "lessonProgress": 0.0,
            }

        elif event.get("type") == "lesson_progress":
            self.lesson_progress = event.get("progress", 0.0)
            delta = {"lessonProgress": self.lesson_progress}

        elif event.get("type") == "lesson_completed":
            lesson = event.get("lesson")
            if lesson and lesson not in self.completed_lessons:
                self.completed_lessons.append(lesson)
            xp = event.get("xp", 10)
            self.xp_earned += xp
            self.current_lesson = None
            self.lesson_progress = 0.0
            delta = {
                "completedLessons": self.completed_lessons,
                "xpEarned": self.xp_earned,
                "currentLesson": None,
                "lessonProgress": 0.0,
            }

        elif event.get("type") == "location_discovered":
            location = event.get("location")
            if location and location not in self.discovered_locations:
                self.discovered_locations.append(location)
            self.current_location = location
            delta = {
                "discoveredLocations": self.discovered_locations,
                "currentLocation": location,
            }

        elif event.get("type") == "character_met":
            character = event.get("character")
            if character and character not in self.met_characters:
                self.met_characters.append(character)
            self.current_character = character
            delta = {
                "metCharacters": self.met_characters,
                "currentCharacter": character,
            }

        elif event.get("type") == "vocabulary_learned":
            word = event.get("word")
            if word and word not in self.vocabulary_learned:
                self.vocabulary_learned.append(word)
                self.xp_earned += event.get("xp", 5)
            delta = {
                "vocabularyLearned": self.vocabulary_learned,
                "xpEarned": self.xp_earned,
            }

        elif event.get("type") == "phrase_mastered":
            phrase = event.get("phrase")
            if phrase and phrase not in self.phrases_mastered:
                self.phrases_mastered.append(phrase)
                self.xp_earned += event.get("xp", 15)
            delta = {
                "phrasesMastered": self.phrases_mastered,
                "xpEarned": self.xp_earned,
            }

        elif event.get("type") == "achievement_unlocked":
            achievement = {
                "id": event.get("id"),
                "name": event.get("name"),
                "description": event.get("description"),
                "unlocked_at": datetime.utcnow().isoformat(),
            }
            self.achievements.append(achievement)
            self.xp_earned += event.get("xp", 50)
            delta = {
                "achievements": self.achievements,
                "xpEarned": self.xp_earned,
            }

        elif event.get("type") == "level_up":
            self.level = event.get("level", self.level + 1)
            delta = {"level": self.level}

        elif event.get("type") == "dialect_changed":
            self.current_dialect = event.get("dialect", "standard")
            delta = {"currentDialect": self.current_dialect}

        return delta


# Event type registry for deserialization
EVENT_TYPE_MAP: dict[str, type[AGUIEvent]] = {
    AGUIEventType.RUN_STARTED.value: RunStartedEvent,
    AGUIEventType.RUN_FINISHED.value: RunFinishedEvent,
    AGUIEventType.RUN_ERROR.value: RunErrorEvent,
    AGUIEventType.STEP_STARTED.value: StepStartedEvent,
    AGUIEventType.STEP_FINISHED.value: StepFinishedEvent,
    AGUIEventType.TEXT_MESSAGE_START.value: TextMessageStartEvent,
    AGUIEventType.TEXT_MESSAGE_CONTENT.value: TextMessageContentEvent,
    AGUIEventType.TEXT_MESSAGE_END.value: TextMessageEndEvent,
    AGUIEventType.TOOL_CALL_START.value: ToolCallStartEvent,
    AGUIEventType.TOOL_CALL_ARGS.value: ToolCallArgsEvent,
    AGUIEventType.TOOL_CALL_END.value: ToolCallEndEvent,
    AGUIEventType.TOOL_RESULT.value: ToolResultEvent,
    AGUIEventType.STATE_SNAPSHOT.value: StateSnapshotEvent,
    AGUIEventType.STATE_DELTA.value: StateDeltaEvent,
    AGUIEventType.MESSAGES_SNAPSHOT.value: MessagesSnapshotEvent,
    AGUIEventType.RAW.value: RawEvent,
    AGUIEventType.CUSTOM.value: CustomEvent,
}


def parse_agui_event(data: dict) -> AGUIEvent:
    """Parse a dictionary into the appropriate AG-UI event type."""
    event_type = data.get("type")
    if event_type not in EVENT_TYPE_MAP:
        raise ValueError(f"Unknown event type: {event_type}")

    event_class = EVENT_TYPE_MAP[event_type]

    # Remove 'type' from data since it's handled by the class
    data_copy = {k: v for k, v in data.items() if k != "type"}

    return event_class(**data_copy)
