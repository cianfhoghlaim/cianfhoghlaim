"""
AG-UI Protocol Implementation.

Complete implementation of all 17 AG-UI (Agent-User Interface) event types
for CopilotKit integration with proper streaming support.

Event Categories:
- Lifecycle: RUN_STARTED, RUN_FINISHED, RUN_ERROR, STEP_STARTED, STEP_FINISHED
- Messages: TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END
- Tools: TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_RESULT
- State: STATE_SNAPSHOT, STATE_DELTA, MESSAGES_SNAPSHOT
- Special: RAW, CUSTOM
"""

import json
import uuid
from collections.abc import AsyncGenerator
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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

    # Generative UI events
    GENERATIVE_UI = "GENERATIVE_UI"


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


@dataclass
class GenerativeUIEvent(AGUIEvent):
    """
    Generative UI event for rendering dynamic components.

    Used to emit UI components from the agent that should be rendered
    in specific slots in the frontend.

    Slots:
    - main: Primary content area
    - sidebar: Side panel
    - overlay: Modal/popup overlay
    """

    type: AGUIEventType = field(default=AGUIEventType.GENERATIVE_UI)
    component: str | None = None  # Component name (e.g., "CurriculumCard")
    props: dict[str, Any] | None = None  # Props to pass to the component
    slot: str = "main"  # Where to render: "main", "sidebar", "overlay"
    component_id: str = field(default_factory=lambda: str(uuid.uuid4()))


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

    def step_started(
        self, step_name: str, step_type: str = "agent"
    ) -> StepStartedEvent:
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
        return self._base_event(
            TextMessageStartEvent, message_id=self._message_id, role=role
        )

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
    def state_snapshot(
        self, state: dict, state_key: str | None = None
    ) -> StateSnapshotEvent:
        return self._base_event(
            StateSnapshotEvent, state=state, state_key=state_key
        )

    def state_delta(
        self, delta: dict, operation: str = "merge", path: str | None = None
    ) -> StateDeltaEvent:
        return self._base_event(
            StateDeltaEvent, delta=delta, operation=operation, path=path
        )

    def messages_snapshot(self, messages: list[dict]) -> MessagesSnapshotEvent:
        return self._base_event(MessagesSnapshotEvent, messages=messages)

    # Special events
    def raw(self, data: Any) -> RawEvent:
        return self._base_event(RawEvent, data=data)

    def custom(self, event_name: str, payload: dict) -> CustomEvent:
        return self._base_event(CustomEvent, event_name=event_name, payload=payload)

    # Generative UI events
    def generative_ui(
        self,
        component: str,
        props: dict | None = None,
        slot: str = "main",
    ) -> GenerativeUIEvent:
        """
        Emit a generative UI component.

        Args:
            component: Component name (e.g., "CurriculumCard", "PronunciationButton")
            props: Props to pass to the React component
            slot: Where to render ("main", "sidebar", "overlay")

        Returns:
            GenerativeUIEvent to be sent via SSE
        """
        return self._base_event(
            GenerativeUIEvent,
            component=component,
            props=props or {},
            slot=slot,
        )


async def stream_agui_events(
    generator: AsyncGenerator[AGUIEvent, None],
) -> AsyncGenerator[str, None]:
    """Convert AG-UI events to SSE format for streaming."""
    async for event in generator:
        yield event.to_sse()


class DagsterProgressState:
    """State container for Dagster pipeline progress (for CopilotKit shared state)."""

    def __init__(self):
        self.active_jobs: list[dict] = []
        self.completed_assets: list[str] = []
        self.errors: list[dict] = []
        self.overall_progress: float = 0.0
        self.current_asset: str | None = None
        self.current_stage: str | None = None

    def to_dict(self) -> dict:
        return {
            "activeJobs": self.active_jobs,
            "completedAssets": self.completed_assets,
            "errors": self.errors,
            "overallProgress": self.overall_progress,
            "currentAsset": self.current_asset,
            "currentStage": self.current_stage,
        }

    def update_from_event(self, event: dict) -> dict:
        """Update state from a Dagster event and return delta."""
        delta = {}

        if event.get("type") == "asset_started":
            self.current_asset = event.get("asset")
            self.current_stage = "processing"
            delta = {"currentAsset": self.current_asset, "currentStage": "processing"}

        elif event.get("type") == "asset_completed":
            asset = event.get("asset")
            if asset and asset not in self.completed_assets:
                self.completed_assets.append(asset)
            self.current_asset = None
            self.current_stage = None
            delta = {
                "completedAssets": self.completed_assets,
                "currentAsset": None,
                "currentStage": None,
            }

        elif event.get("type") == "progress":
            self.overall_progress = event.get("progress", 0.0)
            self.current_stage = event.get("stage")
            delta = {
                "overallProgress": self.overall_progress,
                "currentStage": self.current_stage,
            }

        elif event.get("type") == "error":
            self.errors.append(
                {"asset": event.get("asset"), "error": event.get("error")}
            )
            delta = {"errors": self.errors}

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
    AGUIEventType.GENERATIVE_UI.value: GenerativeUIEvent,
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
