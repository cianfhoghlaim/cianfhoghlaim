"""
Multi-Agent Orchestrator for Tuath Celtic Educational MMO.

Coordinates specialized agents for:
- Celtic Language Tutor: Language learning support
- Mythology Narrator: Celtic lore and NPC dialogue
- Quest Guide: Game objectives and hints
- Research Assistant: Deep Celtic studies research

Implements AG-UI protocol for streaming responses with full event coverage.
"""

import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Types
# ============================================================================


class AgentRole(Enum):
    """Roles for specialized Tuath agents."""

    TUTOR = "tutor"  # Celtic language learning
    MYTHOLOGY = "mythology"  # Celtic lore and NPCs
    QUEST = "quest"  # Game objectives
    RESEARCH = "research"  # Deep Celtic studies
    ORCHESTRATOR = "orchestrator"


class TaskStatus(Enum):
    """Status of an orchestrated task."""

    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """A task assigned to an agent."""

    id: str
    role: AgentRole
    prompt: str
    context: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class OrchestratorState:
    """State of the orchestrator during execution."""

    run_id: str
    thread_id: str | None
    current_task: AgentTask | None
    task_history: list[AgentTask]
    accumulated_context: dict[str, Any]
    game_state: dict[str, Any]


# ============================================================================
# Agent Registry
# ============================================================================


class AgentRegistry:
    """Registry of available Tuath agents."""

    def __init__(self):
        self._agents: dict[AgentRole, Any] = {}
        self._initialized = False

    def register(self, role: AgentRole, agent: Any) -> None:
        """Register an agent for a role."""
        self._agents[role] = agent

    def get(self, role: AgentRole) -> Any | None:
        """Get an agent by role."""
        return self._agents.get(role)

    def initialize_defaults(self) -> None:
        """Initialize default agents from the ADK module."""
        if self._initialized:
            return

        try:
            from .adk.root_agent import (
                celtic_tutor_agent,
                mythology_narrator_agent,
                quest_guide_agent,
                research_assistant_agent,
            )

            self.register(AgentRole.TUTOR, celtic_tutor_agent)
            self.register(AgentRole.MYTHOLOGY, mythology_narrator_agent)
            self.register(AgentRole.QUEST, quest_guide_agent)
            self.register(AgentRole.RESEARCH, research_assistant_agent)
            self._initialized = True
            logger.info("Initialized Tuath ADK agents")
        except Exception as e:
            logger.warning(f"Failed to initialize ADK agents: {e}")

    @property
    def available_roles(self) -> list[AgentRole]:
        """Get list of available agent roles."""
        return list(self._agents.keys())


_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry."""
    return _registry


# ============================================================================
# Intent Classification
# ============================================================================


@dataclass
class ClassifiedIntent:
    """Classified user intent for Tuath."""

    primary_role: AgentRole
    secondary_roles: list[AgentRole]
    target_language: str  # ga, gd, cy, en
    confidence: float
    extracted_entities: dict[str, Any]


class IntentClassifier:
    """Classifies user intent for Celtic educational content."""

    # Intent patterns mapped to agent roles
    INTENT_PATTERNS = {
        AgentRole.TUTOR: [
            "translate",
            "how do you say",
            "what does",
            "mean",
            "grammar",
            "vocabulary",
            "word",
            "phrase",
            "pronunciation",
            "learn",
            "practice",
            "gaeilge",
            "gàidhlig",
            "cymraeg",
            "irish",
            "welsh",
            "scottish gaelic",
            "mutation",
            "conjugate",
            "verb",
        ],
        AgentRole.QUEST: [
            "quest",
            "mission",
            "objective",
            "complete",
            "find",
            "where",
            "how do i",
            "next step",
            "hint",
            "help me",
            "stuck",
            "goal",
            "task",
            "progress",
        ],
        AgentRole.MYTHOLOGY: [
            "story",
            "legend",
            "myth",
            "who is",
            "tell me about",
            "lore",
            "character",
            "hero",
            "god",
            "goddess",
            "tuatha",
            "fianna",
            "mabinogion",
            "cú chulainn",
            "fionn",
            "otherworld",
        ],
        AgentRole.RESEARCH: [
            "research",
            "analyze",
            "compare",
            "history",
            "etymology",
            "origin",
            "celtic",
            "culture",
            "tradition",
        ],
    }

    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "ga": ["irish", "gaeilge", "éire", "ireland"],
        "gd": ["scottish gaelic", "gàidhlig", "alba", "scotland"],
        "cy": ["welsh", "cymraeg", "cymru", "wales"],
    }

    def classify(self, message: str) -> ClassifiedIntent:
        """Classify user intent from message."""
        message_lower = message.lower()

        # Score each role
        role_scores: dict[AgentRole, float] = {}
        for role, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in message_lower)
            role_scores[role] = score / len(patterns) if patterns else 0

        # Determine primary role
        primary_role = max(role_scores, key=role_scores.get)  # type: ignore
        confidence = role_scores[primary_role]

        # If low confidence, default to tutor
        if confidence < 0.1:
            primary_role = AgentRole.TUTOR
            confidence = 0.5

        # Determine secondary roles
        threshold = confidence * 0.5
        secondary_roles = [
            role
            for role, score in role_scores.items()
            if role != primary_role and score >= threshold
        ]

        # Detect target language
        target_language = self._detect_language(message_lower)

        # Extract entities
        entities = self._extract_entities(message_lower)

        return ClassifiedIntent(
            primary_role=primary_role,
            secondary_roles=secondary_roles,
            target_language=target_language,
            confidence=confidence,
            extracted_entities=entities,
        )

    def _detect_language(self, message: str) -> str:
        """Detect target Celtic language."""
        for lang_code, patterns in self.LANGUAGE_PATTERNS.items():
            if any(p in message for p in patterns):
                return lang_code
        return "ga"  # Default to Irish

    def _extract_entities(self, message: str) -> dict[str, Any]:
        """Extract entities from message."""
        entities: dict[str, Any] = {}

        # Extract level
        if any(x in message for x in ["beginner", "basic"]):
            entities["level"] = "beginner"
        elif any(x in message for x in ["intermediate"]):
            entities["level"] = "intermediate"
        elif any(x in message for x in ["advanced", "fluent"]):
            entities["level"] = "advanced"

        # Extract tradition
        if any(x in message for x in ["irish myth", "tuatha", "fianna", "ulster"]):
            entities["tradition"] = "irish"
        elif any(x in message for x in ["welsh myth", "mabinogion", "pwyll"]):
            entities["tradition"] = "welsh"
        elif any(x in message for x in ["scottish", "alba"]):
            entities["tradition"] = "scottish"

        return entities


# ============================================================================
# Orchestrator
# ============================================================================


class TuathAgentOrchestrator:
    """
    Orchestrates multiple specialized agents for Celtic educational tasks.

    Workflow:
    1. Classify user intent
    2. Route to appropriate agent(s)
    3. Execute agent task(s) with LLM calls
    4. Stream AG-UI events throughout
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        classifier: IntentClassifier | None = None,
    ):
        self.registry = registry or get_agent_registry()
        self.classifier = classifier or IntentClassifier()

    async def process_request(
        self,
        message: str,
        thread_id: str | None = None,
        context: dict | None = None,
        game_state: dict | None = None,
    ) -> AsyncGenerator[dict]:
        """
        Process a user request with full AG-UI event streaming.

        Yields AG-UI protocol events throughout execution.
        """
        run_id = str(uuid.uuid4())
        thread_id = thread_id or str(uuid.uuid4())

        state = OrchestratorState(
            run_id=run_id,
            thread_id=thread_id,
            current_task=None,
            task_history=[],
            accumulated_context=context or {},
            game_state=game_state or {},
        )

        # Emit RUN_STARTED
        yield self._emit_event("RUN_STARTED", {
            "runId": run_id,
            "threadId": thread_id,
            "agentName": "tuath_orchestrator",
            "inputMessage": message,
        })

        try:
            # Step 1: Classify intent
            yield self._emit_event("STEP_STARTED", {
                "stepId": f"{run_id}-classify",
                "stepName": "intent_classification",
                "stepType": "orchestrator",
            })

            intent = self.classifier.classify(message)

            yield self._emit_event("STEP_FINISHED", {
                "stepId": f"{run_id}-classify",
                "stepName": "intent_classification",
                "output": {
                    "primaryRole": intent.primary_role.value,
                    "targetLanguage": intent.target_language,
                    "confidence": intent.confidence,
                    "entities": intent.extracted_entities,
                },
            })

            # Step 2: Execute primary agent
            primary_agent = self.registry.get(intent.primary_role)
            if not primary_agent:
                self.registry.initialize_defaults()
                primary_agent = self.registry.get(intent.primary_role)

            if primary_agent:
                task = AgentTask(
                    id=f"{run_id}-primary",
                    role=intent.primary_role,
                    prompt=message,
                    context={
                        **state.accumulated_context,
                        "entities": intent.extracted_entities,
                        "language": intent.target_language,
                        "game_state": state.game_state,
                    },
                )

                async for event in self._execute_agent_task(task, primary_agent, state):
                    yield event

            # Emit final STATE_SNAPSHOT
            yield self._emit_event("STATE_SNAPSHOT", {
                "state": {
                    "threadId": thread_id,
                    "tasksCompleted": len(state.task_history),
                    "primaryRole": intent.primary_role.value,
                    "targetLanguage": intent.target_language,
                    "gameState": state.game_state,
                },
            })

            # Emit RUN_FINISHED
            yield self._emit_event("RUN_FINISHED", {
                "runId": run_id,
                "output": state.current_task.result if state.current_task else None,
            })

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            yield self._emit_event("RUN_ERROR", {
                "runId": run_id,
                "error": str(e),
                "errorCode": "ORCHESTRATOR_ERROR",
                "recoverable": True,
            })

    async def _execute_agent_task(
        self,
        task: AgentTask,
        agent: Any,
        state: OrchestratorState,
    ) -> AsyncGenerator[dict]:
        """Execute a task on an agent with event streaming."""
        task.status = TaskStatus.EXECUTING
        task.started_at = datetime.utcnow()
        state.current_task = task

        # Emit STEP_STARTED
        yield self._emit_event("STEP_STARTED", {
            "stepId": task.id,
            "stepName": f"{task.role.value}_agent",
            "stepType": "agent",
        })

        try:
            # Check if agent is an ADK LlmAgent with run_async
            if hasattr(agent, "run_async"):
                # ADK agent with streaming
                yield self._emit_event("TEXT_MESSAGE_START", {
                    "messageId": f"{task.id}-msg",
                    "role": "assistant",
                })

                accumulated = ""
                async for event in agent.run_async(task.prompt):
                    if hasattr(event, "text"):
                        yield self._emit_event("TEXT_MESSAGE_CONTENT", {
                            "messageId": f"{task.id}-msg",
                            "delta": event.text,
                        })
                        accumulated += event.text

                    elif hasattr(event, "tool_call"):
                        yield self._emit_event("TOOL_CALL_START", {
                            "toolCallId": f"{task.id}-tool",
                            "toolName": event.tool_call.name,
                        })
                        yield self._emit_event("TOOL_CALL_ARGS", {
                            "toolCallId": f"{task.id}-tool",
                            "args": event.tool_call.arguments,
                        })

                yield self._emit_event("TEXT_MESSAGE_END", {
                    "messageId": f"{task.id}-msg",
                })

                task.result = accumulated

            elif hasattr(agent, "run"):
                # Synchronous ADK agent (wrap in executor)
                import asyncio

                yield self._emit_event("TEXT_MESSAGE_START", {
                    "messageId": f"{task.id}-msg",
                    "role": "assistant",
                })

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: agent.run(task.prompt)
                )

                if hasattr(result, "response"):
                    task.result = result.response
                else:
                    task.result = str(result)

                yield self._emit_event("TEXT_MESSAGE_CONTENT", {
                    "messageId": f"{task.id}-msg",
                    "delta": task.result,
                })
                yield self._emit_event("TEXT_MESSAGE_END", {
                    "messageId": f"{task.id}-msg",
                })

            elif callable(agent):
                # Simple callable agent
                result = await agent(task.prompt, task.context)
                task.result = result

                yield self._emit_event("TEXT_MESSAGE_START", {
                    "messageId": f"{task.id}-msg",
                    "role": "assistant",
                })
                yield self._emit_event("TEXT_MESSAGE_CONTENT", {
                    "messageId": f"{task.id}-msg",
                    "delta": str(result),
                })
                yield self._emit_event("TEXT_MESSAGE_END", {
                    "messageId": f"{task.id}-msg",
                })

            else:
                # Fallback: No streaming, generate placeholder
                task.result = await self._generate_fallback_response(task)

                yield self._emit_event("TEXT_MESSAGE_START", {
                    "messageId": f"{task.id}-msg",
                    "role": "assistant",
                })
                yield self._emit_event("TEXT_MESSAGE_CONTENT", {
                    "messageId": f"{task.id}-msg",
                    "delta": task.result,
                })
                yield self._emit_event("TEXT_MESSAGE_END", {
                    "messageId": f"{task.id}-msg",
                })

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()

            # Update accumulated context
            state.accumulated_context[f"{task.role.value}_result"] = task.result
            state.task_history.append(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            logger.error(f"Agent task failed: {e}")

            yield self._emit_event("RUN_ERROR", {
                "runId": state.run_id,
                "error": str(e),
                "errorCode": f"{task.role.value.upper()}_AGENT_ERROR",
                "recoverable": True,
            })

        # Emit STEP_FINISHED
        duration_ms = 0
        if task.started_at and task.completed_at:
            duration_ms = int(
                (task.completed_at - task.started_at).total_seconds() * 1000
            )

        yield self._emit_event("STEP_FINISHED", {
            "stepId": task.id,
            "stepName": f"{task.role.value}_agent",
            "durationMs": duration_ms,
            "output": task.result if task.status == TaskStatus.COMPLETED else None,
        })

    async def _generate_fallback_response(self, task: AgentTask) -> str:
        """Generate a fallback response when ADK is unavailable."""
        role = task.role
        language = task.context.get("language", "ga")

        greetings = {
            "ga": "Dia duit! (Hello in Irish)",
            "gd": "Halò! (Hello in Scottish Gaelic)",
            "cy": "Shwmae! (Hello in Welsh)",
        }

        greeting = greetings.get(language, greetings["ga"])

        if role == AgentRole.TUTOR:
            return f"""## Celtic Language Lesson

{greeting}

I'm your Celtic language tutor. Here are some key concepts:

### Word Order
Celtic languages use Verb-Subject-Object (VSO) order, unlike English.

**Example (Irish):**
- *Tá mé ag foghlaim* (I am learning)
- Literally: "Is me at learning"

### Initial Mutations
Celtic languages feature consonant mutations at the start of words:
- **Lenition (séimhiú)**: c → ch, p → ph, t → th
- Example: *mo chat* (my cat) - 'c' becomes 'ch'

Keep practicing! Go n-éirí leat! (Good luck!)
"""

        elif role == AgentRole.MYTHOLOGY:
            return f"""## Celtic Mythology

{greeting}

*The mists part to reveal ancient wisdom...*

The Celtic world is filled with divine beings and legendary heroes:

### Key Figures
- **Tuatha Dé Danann** - The divine race of Irish mythology
- **Lugh Lámhfhada** - God of skills, many-talented
- **Cú Chulainn** - The Hound of Ulster, greatest warrior

### The Otherworld
- **Tír na nÓg** - Land of Eternal Youth
- **Tech Duinn** - House of Donn, realm of the dead
- **Annwfn** - Welsh Otherworld

*May the old stories guide your path...*
"""

        elif role == AgentRole.QUEST:
            return f"""## Quest Guidance

{greeting}

### Current Objective
Speak to the village elder near the standing stones.

### Hint
Look for the elder wearing traditional garb near the central fire. The standing stones mark the boundary between the mortal world and the Otherworld.

### Learning Connection
This quest teaches basic Celtic greetings and cultural etiquette.

**Key Vocabulary:**
- *Dia duit* - Hello (to one person)
- *Dia daoibh* - Hello (to multiple people)
- *Fáilte* - Welcome

Lean ar aghaidh! (Keep going!)
"""

        else:
            return f"""## Celtic Research

{greeting}

The Celtic languages form a branch of Indo-European, divided into:

**Goidelic (Q-Celtic):**
- Irish (Gaeilge) - ~1.7 million speakers
- Scottish Gaelic (Gàidhlig) - ~57,000 speakers
- Manx (Gaelg) - Revived language

**Brythonic (P-Celtic):**
- Welsh (Cymraeg) - ~560,000 speakers
- Breton (Brezhoneg) - ~200,000 speakers
- Cornish (Kernewek) - Revived language

The linguistic split is visible in cognates: Irish *ceathair* vs Welsh *pedwar* (four).
"""

    def _emit_event(self, event_type: str, data: dict) -> dict:
        """Create an AG-UI event."""
        return {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data,
        }


# ============================================================================
# Factory Functions
# ============================================================================


def create_orchestrator(
    registry: AgentRegistry | None = None,
) -> TuathAgentOrchestrator:
    """Create an orchestrator with optional custom registry."""
    orchestrator = TuathAgentOrchestrator(registry=registry)
    orchestrator.registry.initialize_defaults()
    return orchestrator


_orchestrator: TuathAgentOrchestrator | None = None


def get_orchestrator() -> TuathAgentOrchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = create_orchestrator()
    return _orchestrator
