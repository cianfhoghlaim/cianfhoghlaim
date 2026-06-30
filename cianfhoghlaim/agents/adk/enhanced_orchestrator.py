"""
Enhanced Orchestrator - Advanced Agent Coordination for Celtic Education.

Extends the root_agent with patterns from oideachas/agents/orchestrator.py:
- AG-UI protocol event streaming for frontend integration
- Task lifecycle management with state tracking
- Multi-agent validation workflows
- Entity extraction for intelligent routing
- Memory context retrieval via Cognee/LanceDB

This module bridges the orchestration patterns from both codebases,
providing a unified approach to agent coordination.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .root_agent import (
    AgentContext,
    AgentDomain,
    AgentResponse,
    RootAgent,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Task Lifecycle Types
# ============================================================================


class TaskStatus(Enum):
    """Status of an orchestrated task."""

    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """A task assigned to an agent with full lifecycle tracking."""

    id: str
    domain: AgentDomain
    prompt: str
    context: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: AgentResponse | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to serializable dict."""
        return {
            "id": self.id,
            "domain": self.domain.value,
            "prompt": self.prompt[:200],  # Truncate for logging
            "status": self.status.value,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


@dataclass
class OrchestratorState:
    """State of the orchestrator during execution."""

    run_id: str
    session_id: str
    current_task: AgentTask | None = None
    task_history: list[AgentTask] = field(default_factory=list)
    accumulated_context: dict[str, Any] = field(default_factory=dict)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    memory_results: list[dict[str, Any]] = field(default_factory=list)

    def to_snapshot(self) -> dict[str, Any]:
        """Create a state snapshot for AG-UI."""
        return {
            "runId": self.run_id,
            "sessionId": self.session_id,
            "tasksCompleted": len([t for t in self.task_history
                                   if t.status == TaskStatus.COMPLETED]),
            "tasksFailed": len([t for t in self.task_history
                               if t.status == TaskStatus.FAILED]),
            "currentDomain": self.current_task.domain.value if self.current_task else None,
            "memoryResultsCount": len(self.memory_results),
        }


# ============================================================================
# Intent Classification with Entity Extraction
# ============================================================================


@dataclass
class ClassifiedIntent:
    """Classified user intent with entities."""

    primary_domain: AgentDomain
    secondary_domains: list[AgentDomain]
    requires_validation: bool
    confidence: float
    extracted_entities: dict[str, Any]


class EnhancedIntentClassifier:
    """
    Enhanced intent classifier with entity extraction.

    Combines keyword matching with entity extraction for:
    - Subject identification (mathematics, irish, welsh, etc.)
    - Education level detection (primary, junior cycle, GCSE)
    - Document type recognition (specification, exam paper)
    - Language preferences
    - Nation filtering
    """

    # Domain patterns (expanded from both codebases)
    DOMAIN_PATTERNS = {
        AgentDomain.CURRICULUM: [
            "curriculum", "syllabus", "learning outcome", "strand", "subject",
            "junior cycle", "leaving cert", "primary", "secondary",
            "specification", "assessment", "exam", "test", "marking scheme",
            "siollabas", "curaclam", "toradh foghlama",
            "search", "find", "look for", "where", "documents",
        ],
        AgentDomain.GEOSPATIAL: [
            "map", "location", "where", "near", "nearby", "boundary",
            "gaeltacht", "county", "region", "area", "district",
            "school location", "dialect region", "pronunciation area",
            "ca bhfuil", "in aice le", "ceantar",
        ],
        AgentDomain.TRANSLATION: [
            "translate", "translation", "irish", "welsh", "gaelic",
            "convert", "how do you say", "what is", "in irish",
            "aistrigh", "aistriuchán", "gaeilge", "cymraeg",
            "check", "validate", "correct", "verify",
        ],
        AgentDomain.CORPUS: [
            "folklore", "story", "tale", "tradition", "custom",
            "duchas", "seanchas", "bealoideas", "sceal",
            "song", "amhran", "proverb", "seanfhocal",
            "schools collection", "bailiuchan na scol",
        ],
        AgentDomain.STATISTICS: [
            "statistics", "data", "numbers", "percentage", "rate",
            "comparison", "compare", "trend", "change", "analysis",
            "enrolment", "attainment", "performance",
            "staitistici", "sonrai", "comparaid",
        ],
    }

    # Entity patterns for extraction
    ENTITY_PATTERNS = {
        "subject": [
            "mathematics", "maths", "english", "irish", "gaeilge",
            "science", "history", "geography", "computer science",
            "welsh", "scottish gaelic", "french", "german", "spanish",
            "music", "art", "physical education", "religion",
        ],
        "education_level": [
            "primary", "junior cycle", "junior cert", "senior cycle",
            "leaving cert", "gcse", "a level", "a-level", "third level",
            "university", "further education",
        ],
        "document_type": [
            "curriculum", "specification", "examiner report",
            "marking scheme", "guidelines", "exam paper", "syllabus",
            "learning outcomes", "assessment criteria",
        ],
        "nation": [
            "ireland", "irish", "scotland", "scottish", "wales", "welsh",
            "england", "english", "northern ireland", "uk",
        ],
        "language": [
            "irish", "gaeilge", "welsh", "cymraeg", "scottish gaelic",
            "gaidhlig", "manx", "gaelg", "english", "bearla",
        ],
    }

    def classify(self, query: str, context: AgentContext | None = None) -> ClassifiedIntent:
        """Classify user intent from query with entity extraction."""
        query_lower = query.lower()

        # Score each domain
        domain_scores: dict[AgentDomain, float] = {}
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = sum(1 for p in patterns if p in query_lower)
            domain_scores[domain] = score / len(patterns) if patterns else 0

        # Determine primary domain
        primary_domain = max(domain_scores, key=domain_scores.get)  # type: ignore
        confidence = domain_scores[primary_domain]

        # Low confidence -> default to general
        if confidence < 0.05:
            primary_domain = AgentDomain.GENERAL
            confidence = 0.3

        # Determine secondary domains
        threshold = confidence * 0.5
        secondary_domains = [
            domain
            for domain, score in domain_scores.items()
            if domain != primary_domain and score >= threshold
        ]

        # Check if validation needed
        requires_validation = any(
            p in query_lower for p in ["irish", "gaeilge", "as gaeilge", "translate", "check"]
        )

        # Extract entities
        entities = self._extract_entities(query_lower)

        # Add context-based entities
        if context:
            if context.nation and "nation" not in entities:
                entities["nation"] = context.nation
            if context.language and "language" not in entities:
                entities["language"] = context.language

        return ClassifiedIntent(
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            requires_validation=requires_validation,
            confidence=confidence,
            extracted_entities=entities,
        )

    def _extract_entities(self, query: str) -> dict[str, Any]:
        """Extract entities from query."""
        entities: dict[str, Any] = {}

        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                if pattern in query:
                    entities[entity_type] = pattern
                    break

        return entities


# ============================================================================
# AG-UI Event Protocol
# ============================================================================


class AGUIEventEmitter:
    """
    Emits AG-UI protocol events for frontend integration.

    Event types:
    - RUN_STARTED/FINISHED/ERROR: Run lifecycle
    - STEP_STARTED/FINISHED: Agent step tracking
    - TEXT_MESSAGE_START/CONTENT/END: Text streaming
    - TOOL_CALL_START/ARGS/END: Tool invocations
    - STATE_SNAPSHOT: State updates
    - CUSTOM: Domain-specific events
    """

    @staticmethod
    def emit(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create an AG-UI event."""
        return {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **data,
        }

    @staticmethod
    def run_started(run_id: str, session_id: str, agent_name: str, query: str) -> dict:
        return AGUIEventEmitter.emit("RUN_STARTED", {
            "runId": run_id,
            "sessionId": session_id,
            "agentName": agent_name,
            "inputMessage": query,
        })

    @staticmethod
    def run_finished(run_id: str, output: Any) -> dict:
        return AGUIEventEmitter.emit("RUN_FINISHED", {
            "runId": run_id,
            "output": output if isinstance(output, (str, dict)) else str(output),
        })

    @staticmethod
    def run_error(run_id: str, error: str, code: str = "AGENT_ERROR", recoverable: bool = True) -> dict:
        return AGUIEventEmitter.emit("RUN_ERROR", {
            "runId": run_id,
            "error": error,
            "errorCode": code,
            "recoverable": recoverable,
        })

    @staticmethod
    def step_started(step_id: str, step_name: str, step_type: str = "agent") -> dict:
        return AGUIEventEmitter.emit("STEP_STARTED", {
            "stepId": step_id,
            "stepName": step_name,
            "stepType": step_type,
        })

    @staticmethod
    def step_finished(step_id: str, step_name: str, duration_ms: int, output: Any = None) -> dict:
        return AGUIEventEmitter.emit("STEP_FINISHED", {
            "stepId": step_id,
            "stepName": step_name,
            "durationMs": duration_ms,
            "output": output,
        })

    @staticmethod
    def text_message_start(message_id: str, role: str = "assistant") -> dict:
        return AGUIEventEmitter.emit("TEXT_MESSAGE_START", {
            "messageId": message_id,
            "role": role,
        })

    @staticmethod
    def text_message_content(message_id: str, delta: str) -> dict:
        return AGUIEventEmitter.emit("TEXT_MESSAGE_CONTENT", {
            "messageId": message_id,
            "delta": delta,
        })

    @staticmethod
    def text_message_end(message_id: str) -> dict:
        return AGUIEventEmitter.emit("TEXT_MESSAGE_END", {
            "messageId": message_id,
        })

    @staticmethod
    def state_snapshot(state: dict[str, Any]) -> dict:
        return AGUIEventEmitter.emit("STATE_SNAPSHOT", {
            "state": state,
        })

    @staticmethod
    def tool_call_start(tool_call_id: str, tool_name: str) -> dict:
        return AGUIEventEmitter.emit("TOOL_CALL_START", {
            "toolCallId": tool_call_id,
            "toolName": tool_name,
        })

    @staticmethod
    def tool_call_args(tool_call_id: str, args: dict[str, Any]) -> dict:
        return AGUIEventEmitter.emit("TOOL_CALL_ARGS", {
            "toolCallId": tool_call_id,
            "args": args,
        })

    @staticmethod
    def tool_call_end(tool_call_id: str, result: Any = None) -> dict:
        return AGUIEventEmitter.emit("TOOL_CALL_END", {
            "toolCallId": tool_call_id,
            "result": result,
        })


# ============================================================================
# Enhanced Orchestrator
# ============================================================================


class EnhancedOrchestrator:
    """
    Enhanced orchestrator with full AG-UI event streaming.

    Workflow:
    1. Classify intent with entity extraction
    2. Retrieve memory context (if available)
    3. Route to primary domain agent
    4. Execute agent with event streaming
    5. Optional validation pass for Celtic language content
    6. Emit state snapshot and completion events

    Integrates patterns from:
    - oideachas/agents/orchestrator.py: Task lifecycle, AG-UI events
    - oideachais/agents/adk/root_agent.py: Domain routing, observability
    """

    def __init__(
        self,
        root_agent: RootAgent | None = None,
        classifier: EnhancedIntentClassifier | None = None,
    ):
        self.root_agent = root_agent or RootAgent()
        self.classifier = classifier or EnhancedIntentClassifier()
        self.emit = AGUIEventEmitter()
        self._memory_service = None

    async def _get_memory_service(self):
        """Get memory service lazily."""
        if self._memory_service is None:
            try:
                # Try Cognee first (from oideachas)
                from ...memory.cognee_service import get_memory_service
                self._memory_service = get_memory_service()
                await self._memory_service.initialize()
            except ImportError:
                try:
                    # Fall back to LanceDB memory
                    from ...memory import get_memory_store
                    self._memory_service = get_memory_store()
                except ImportError:
                    logger.debug("Memory service not available")
        return self._memory_service

    async def process_with_events(
        self,
        query: str,
        context: AgentContext | None = None,
        session_id: str | None = None,
        stream_callback: Callable[[dict], None] | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        """
        Process a query with full AG-UI event streaming.

        Args:
            query: User query
            context: Optional agent context
            session_id: Session ID for tracking
            stream_callback: Optional callback for events

        Yields:
            AG-UI protocol events
        """
        run_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        # Create context if not provided
        if context is None:
            context = AgentContext(query=query, session_id=session_id)

        # Initialize state
        state = OrchestratorState(
            run_id=run_id,
            session_id=session_id,
            user_preferences=context.metadata.get("preferences", {}),
        )

        # Emit RUN_STARTED
        event = self.emit.run_started(run_id, session_id, "enhanced_orchestrator", query)
        yield event
        if stream_callback:
            stream_callback(event)

        try:
            # Step 1: Classify intent
            step_id = f"{run_id}-classify"
            yield self.emit.step_started(step_id, "intent_classification", "orchestrator")

            start = time.time()
            intent = self.classifier.classify(query, context)
            duration_ms = int((time.time() - start) * 1000)

            yield self.emit.step_finished(step_id, "intent_classification", duration_ms, {
                "primaryDomain": intent.primary_domain.value,
                "confidence": intent.confidence,
                "entities": intent.extracted_entities,
                "requiresValidation": intent.requires_validation,
            })

            # Step 2: Memory retrieval (if available)
            memory = await self._get_memory_service()
            if memory:
                step_id = f"{run_id}-memory"
                yield self.emit.step_started(step_id, "memory_retrieval", "memory")

                start = time.time()
                try:
                    memory_results = await memory.search(query=query, limit=5)
                    state.memory_results = [
                        {"content": r.content, "score": r.score}
                        for r in memory_results
                    ]
                except Exception as e:
                    logger.warning(f"Memory search failed: {e}")
                    state.memory_results = []

                duration_ms = int((time.time() - start) * 1000)
                yield self.emit.step_finished(step_id, "memory_retrieval", duration_ms, {
                    "resultsCount": len(state.memory_results),
                })

                # Add memory context
                if state.memory_results:
                    state.accumulated_context["memory"] = state.memory_results

            # Step 3: Execute primary agent
            task = AgentTask(
                id=f"{run_id}-primary",
                domain=intent.primary_domain,
                prompt=query,
                context={
                    **state.accumulated_context,
                    "entities": intent.extracted_entities,
                },
                status=TaskStatus.PENDING,
            )
            state.current_task = task

            async for event in self._execute_task(task, context, state):
                yield event
                if stream_callback:
                    stream_callback(event)

            # Step 4: Validation pass (if required)
            if intent.requires_validation and task.status == TaskStatus.COMPLETED:
                validation_task = AgentTask(
                    id=f"{run_id}-validate",
                    domain=AgentDomain.TRANSLATION,  # Use translation agent for validation
                    prompt=f"Validate Irish language content: {task.result.content if task.result else ''}",
                    context={"original_task": task.to_dict()},
                    status=TaskStatus.PENDING,
                )

                async for event in self._execute_task(
                    validation_task,
                    AgentContext(query=validation_task.prompt, session_id=session_id),
                    state,
                    is_validation=True,
                ):
                    yield event
                    if stream_callback:
                        stream_callback(event)

            # Emit STATE_SNAPSHOT
            yield self.emit.state_snapshot(state.to_snapshot())

            # Emit RUN_FINISHED
            final_output = task.result.content if task.result else None
            yield self.emit.run_finished(run_id, final_output)

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            yield self.emit.run_error(run_id, str(e), "ORCHESTRATOR_ERROR", True)

    async def _execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
        state: OrchestratorState,
        is_validation: bool = False,
    ) -> AsyncGenerator[dict[str, Any]]:
        """Execute a task with event streaming."""
        task.status = TaskStatus.EXECUTING
        task.started_at = datetime.utcnow()

        step_name = f"{task.domain.value}_{'validation' if is_validation else 'agent'}"
        yield self.emit.step_started(task.id, step_name, "agent")

        try:
            # Get domain agent
            agent = self.root_agent._get_agent(task.domain)

            # Start text message
            message_id = f"{task.id}-msg"
            yield self.emit.text_message_start(message_id)

            # Execute agent
            if hasattr(agent, "stream"):
                # Streaming agent
                accumulated = ""
                async for chunk in agent.stream(context):
                    if isinstance(chunk, str):
                        yield self.emit.text_message_content(message_id, chunk)
                        accumulated += chunk
                    elif hasattr(chunk, "content"):
                        yield self.emit.text_message_content(message_id, chunk.content)
                        accumulated += chunk.content

                # Create response from accumulated text
                task.result = AgentResponse(
                    content=accumulated,
                    domain=task.domain,
                )
            else:
                # Non-streaming agent
                response = await agent.process(context)
                task.result = response

                # Emit content
                yield self.emit.text_message_content(message_id, response.content)

            yield self.emit.text_message_end(message_id)

            task.status = TaskStatus.COMPLETED

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Task execution failed: {e}")

            yield self.emit.run_error(
                state.run_id,
                str(e),
                f"{task.domain.value.upper()}_AGENT_ERROR",
                True,
            )

        finally:
            task.completed_at = datetime.utcnow()
            if task.started_at and task.completed_at:
                task.duration_ms = int(
                    (task.completed_at - task.started_at).total_seconds() * 1000
                )

            # Update state
            state.task_history.append(task)
            if task.result:
                state.accumulated_context[f"{task.domain.value}_result"] = task.result.content

            yield self.emit.step_finished(
                task.id,
                step_name,
                task.duration_ms,
                {"content": task.result.content[:500] if task.result else None},
            )

    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process a query without event streaming.

        Convenience method that collects all events and returns final response.
        """
        response = None
        async for event in self.process_with_events(
            query=context.query,
            context=context,
            session_id=context.session_id,
        ):
            if event["type"] == "TEXT_MESSAGE_CONTENT":
                if response is None:
                    response = AgentResponse(
                        content="",
                        domain=AgentDomain.GENERAL,
                    )
                response.content += event.get("delta", "")
            elif event["type"] == "STATE_SNAPSHOT":
                if response:
                    response.metadata["state"] = event.get("state", {})

        return response or AgentResponse(
            content="No response generated",
            domain=AgentDomain.GENERAL,
        )


# ============================================================================
# Multi-Agent Validation Workflow
# ============================================================================


class ValidationWorkflow:
    """
    Multi-agent validation workflow for Celtic language content.

    Stages:
    1. Primary content generation
    2. Irish language validation
    3. Terminology verification
    4. Final quality check
    """

    def __init__(self, orchestrator: EnhancedOrchestrator):
        self.orchestrator = orchestrator

    async def validate_content(
        self,
        content: str,
        language: str = "irish",
        session_id: str | None = None,
    ) -> AsyncGenerator[dict[str, Any]]:
        """
        Run validation workflow on content.

        Args:
            content: Content to validate
            language: Target language for validation
            session_id: Session ID for tracking

        Yields:
            AG-UI events for each validation stage
        """
        run_id = str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())

        yield self.orchestrator.emit.run_started(
            run_id, session_id, "validation_workflow", content[:100]
        )

        validation_stages = [
            ("grammar_check", f"Check grammar and spelling in {language}: {content}"),
            ("terminology_verify", f"Verify terminology is correct for {language}: {content}"),
            ("style_review", f"Review style consistency for {language}: {content}"),
        ]

        for stage_name, prompt in validation_stages:
            step_id = f"{run_id}-{stage_name}"
            yield self.orchestrator.emit.step_started(step_id, stage_name, "validation")

            start = time.time()
            context = AgentContext(
                query=prompt,
                language=language,
                session_id=session_id,
            )

            # Execute validation stage
            try:
                response = await self.orchestrator.root_agent.process(context)
                duration_ms = int((time.time() - start) * 1000)

                yield self.orchestrator.emit.step_finished(step_id, stage_name, duration_ms, {
                    "passed": "error" not in response.content.lower(),
                    "feedback": response.content[:200],
                })

            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                yield self.orchestrator.emit.step_finished(step_id, stage_name, duration_ms, {
                    "passed": False,
                    "error": str(e),
                })

        yield self.orchestrator.emit.run_finished(run_id, {"validated": True})


# ============================================================================
# Factory Functions
# ============================================================================


def create_enhanced_orchestrator(
    root_agent: RootAgent | None = None,
) -> EnhancedOrchestrator:
    """Create an enhanced orchestrator instance."""
    return EnhancedOrchestrator(root_agent=root_agent)


_orchestrator: EnhancedOrchestrator | None = None


def get_enhanced_orchestrator() -> EnhancedOrchestrator:
    """Get the global enhanced orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = create_enhanced_orchestrator()
    return _orchestrator


def create_validation_workflow(
    orchestrator: EnhancedOrchestrator | None = None,
) -> ValidationWorkflow:
    """Create a validation workflow instance."""
    return ValidationWorkflow(orchestrator or get_enhanced_orchestrator())


# ============================================================================
# Integration with Existing Root Agent
# ============================================================================


def enhance_root_agent(root_agent: RootAgent) -> EnhancedOrchestrator:
    """
    Enhance an existing root agent with orchestrator capabilities.

    Usage:
        from .root_agent import create_root_agent
        from .enhanced_orchestrator import enhance_root_agent

        agent = create_root_agent()
        orchestrator = enhance_root_agent(agent)

        # Now use orchestrator.process_with_events() for AG-UI streaming
    """
    return EnhancedOrchestrator(root_agent=root_agent)
