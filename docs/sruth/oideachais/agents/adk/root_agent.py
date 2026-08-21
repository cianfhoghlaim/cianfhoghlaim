"""
Root Agent - Unified Orchestrator for Celtic Education Platform.

Routes queries to specialized domain agents:
- Curriculum Agent: Education content search and Q&A
- Geospatial Agent: Map queries and location search
- Translation Agent: Celtic language translation
- Corpus Agent: Folklore and cultural content
- Statistics Agent: Education statistics and comparisons

Uses LiteLLM for unified LLM access with fallback chains:
- Primary: gemini-2.0-flash
- Fallback: gateway/claude-haiku, fast (local)

Observability:
- Datadog LLMObs for agent tracing
- Langfuse for LLM cost tracking
- Logfire for Pydantic-native tracing
- MLflow for experiment logging
- Kafka for event streaming

Memory:
- Letta Cloud for conversation memory
- Cognee for knowledge graph memory
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Import observability (lazy to handle missing deps)
try:
    from observability import (
        trace_adk_agent,
        GeminiLLMSpan,
        annotate_span,
        langfuse_trace,
        create_generation,
        log_llm_call,
        langfuse_flush,
    )

    HAS_OBSERVABILITY = True
except ImportError:
    HAS_OBSERVABILITY = False
    logger.warning("Observability not available")

# Import Logfire (lazy)
try:
    from observability.logfire_config import (
        logfire_span,
        log_llm_call as logfire_log_llm,
        instrument as logfire_instrument,
        ensure_initialized as ensure_logfire,
    )

    HAS_LOGFIRE = True
except ImportError:
    HAS_LOGFIRE = False
    logger.debug("Logfire not available")

# Import Letta memory (lazy)
try:
    from memory.letta_memory import get_memory_service, LettaMemoryService

    HAS_LETTA = True
except ImportError:
    HAS_LETTA = False
    logger.debug("Letta memory not available")

# Import LiteLLM (lazy)
try:
    from litellm import acompletion

    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False
    logger.debug("LiteLLM not available")

# Import Kafka (lazy)
try:
    from kafka import get_producer, AGENT_QUERIES, AGENT_RESPONSES

    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False


class AgentDomain(str, Enum):
    """Available agent domains."""

    CURRICULUM = "curriculum"
    GEOSPATIAL = "geospatial"
    TRANSLATION = "translation"
    CORPUS = "corpus"
    STATISTICS = "statistics"
    GENERAL = "general"


@dataclass
class AgentContext:
    """Context passed between agents."""

    query: str
    language: str = "en"
    nation: str | None = None
    session_id: str | None = None
    history: list[dict[str, str]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    """Response from an agent."""

    content: str
    domain: AgentDomain
    sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    follow_up_queries: list[str] = field(default_factory=list)


# ============================================================================
# Query Router
# ============================================================================


class QueryRouter:
    """
    Routes queries to appropriate domain agents.

    Uses keyword matching and LLM classification for routing decisions.
    """

    # Domain keywords for fast routing
    DOMAIN_KEYWORDS = {
        AgentDomain.CURRICULUM: [
            "curriculum",
            "syllabus",
            "learning outcome",
            "strand",
            "subject",
            "junior cycle",
            "leaving cert",
            "primary",
            "secondary",
            "specification",
            "assessment",
            "exam",
            "test",
            "siollabas",
            "curaclam",
            "toradh foghlama",  # Irish terms
        ],
        AgentDomain.GEOSPATIAL: [
            "map",
            "location",
            "where",
            "near",
            "nearby",
            "boundary",
            "gaeltacht",
            "county",
            "region",
            "area",
            "district",
            "school location",
            "dialect region",
            "pronunciation area",
            "cá bhfuil",
            "in aice le",
            "ceantar",  # Irish terms
        ],
        AgentDomain.TRANSLATION: [
            "translate",
            "translation",
            "irish",
            "welsh",
            "gaelic",
            "convert",
            "how do you say",
            "what is",
            "in irish",
            "aistrigh",
            "aistriúchán",
            "gaeilge",
            "cymraeg",
        ],
        AgentDomain.CORPUS: [
            "folklore",
            "story",
            "tale",
            "tradition",
            "custom",
            "duchas",
            "seanchas",
            "béaloideas",
            "scéal",
            "song",
            "amhrán",
            "proverb",
            "seanfhocal",
            "schools collection",
            "bailiúchán na scol",
        ],
        AgentDomain.STATISTICS: [
            "statistics",
            "data",
            "numbers",
            "percentage",
            "rate",
            "comparison",
            "compare",
            "trend",
            "change",
            "enrolment",
            "attainment",
            "performance",
            "staitisticí",
            "sonraí",
            "comparáid",
        ],
    }

    # LiteLLM routing model with fallbacks
    ROUTING_MODEL = "gemini-2.0-flash"
    ROUTING_FALLBACKS = ["gateway/claude-haiku", "fast"]

    def __init__(self):
        self._llm = None
        self._use_litellm = HAS_LITELLM

    def _get_llm(self):
        """Lazy-load LLM for complex routing."""
        if self._use_litellm:
            # LiteLLM handles the model loading
            return "litellm"

        # Fallback to direct Gemini if LiteLLM not available
        if self._llm is None:
            try:
                import google.generativeai as genai

                self._llm = genai.GenerativeModel("gemini-2.0-flash-exp")
            except Exception:
                self._llm = None
        return self._llm

    def route_by_keywords(self, query: str) -> AgentDomain | None:
        """Fast routing based on keyword matching."""
        query_lower = query.lower()

        scores = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores, key=scores.get)

        return None

    async def route_by_llm(self, query: str) -> AgentDomain:
        """Route using LLM for complex queries."""
        llm = self._get_llm()

        if llm is None:
            return AgentDomain.GENERAL

        prompt = """You are a query router for a Celtic education platform.
Classify this query into one of these domains:
- curriculum: Questions about curriculum, subjects, learning outcomes, exams
- geospatial: Questions about locations, maps, regions, boundaries
- translation: Requests to translate text between languages
- corpus: Questions about folklore, stories, cultural content
- statistics: Questions about education statistics and data
- general: Other queries

Query: {query}

Respond with just the domain name (lowercase, one word).
"""

        messages = [
            {
                "role": "system",
                "content": "You are a query router. Respond with only the domain name.",
            },
            {"role": "user", "content": prompt.format(query=query)},
        ]

        start_time = time.time()

        try:
            if self._use_litellm and HAS_LITELLM:
                # Use LiteLLM with fallback chain
                response = await acompletion(
                    model=self.ROUTING_MODEL,
                    messages=messages,
                    fallbacks=self.ROUTING_FALLBACKS,
                    max_tokens=20,
                    temperature=0.0,
                )
                domain_str = response.choices[0].message.content.strip().lower()

                # Log to Logfire if available
                if HAS_LOGFIRE:
                    latency_ms = (time.time() - start_time) * 1000
                    logfire_log_llm(
                        model=self.ROUTING_MODEL,
                        messages=messages,
                        response=domain_str,
                        latency_ms=latency_ms,
                        token_usage={
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens,
                        }
                        if hasattr(response, "usage")
                        else None,
                    )
            else:
                # Fallback to direct Gemini
                response = await asyncio.to_thread(
                    llm.generate_content,
                    prompt.format(query=query),
                )
                domain_str = response.text.strip().lower()

            for domain in AgentDomain:
                if domain.value == domain_str:
                    return domain

        except Exception as e:
            logger.warning(f"LLM routing failed: {e}")

        return AgentDomain.GENERAL

    async def route(self, query: str) -> AgentDomain:
        """Route a query to the appropriate domain."""
        # Try keyword routing first (fast)
        domain = self.route_by_keywords(query)
        if domain:
            return domain

        # Fall back to LLM routing
        return await self.route_by_llm(query)


# ============================================================================
# Root Agent
# ============================================================================


class RootAgent:
    """
    Root orchestrator agent.

    Handles:
    1. Query classification and routing
    2. Multi-domain query decomposition
    3. Response aggregation
    4. Context management
    5. Conversation memory (via Letta)
    """

    def __init__(self, enable_memory: bool = True):
        self.router = QueryRouter()
        self._agents: dict[AgentDomain, Any] = {}
        self._memory_enabled = enable_memory and HAS_LETTA
        self._memory_service: LettaMemoryService | None = None

    async def _get_memory_service(self) -> LettaMemoryService | None:
        """Get or create memory service."""
        if not self._memory_enabled:
            return None

        if self._memory_service is None:
            self._memory_service = get_memory_service()
            if not await self._memory_service.initialize():
                self._memory_enabled = False
                return None

        return self._memory_service

    async def _save_to_memory(
        self,
        context: AgentContext,
        response: AgentResponse,
    ) -> None:
        """Save conversation to Letta memory."""
        memory = await self._get_memory_service()
        if memory is None:
            return

        try:
            messages = [
                {"role": "user", "content": context.query},
                {"role": "assistant", "content": response.content},
            ]
            await memory.save_conversation(
                agent_name=f"root_agent_{response.domain.value}",
                messages=messages,
                session_id=context.session_id,
                metadata={
                    "domain": response.domain.value,
                    "sources_count": len(response.sources),
                    "language": context.language,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to save to Letta memory: {e}")

    def _get_agent(self, domain: AgentDomain):
        """Get or create domain agent."""
        if domain not in self._agents:
            if domain == AgentDomain.CURRICULUM:
                from .curriculum_agent import CurriculumAgent

                self._agents[domain] = CurriculumAgent()
            elif domain == AgentDomain.GEOSPATIAL:
                from .geospatial_agent import GeospatialAgent

                self._agents[domain] = GeospatialAgent()
            elif domain == AgentDomain.TRANSLATION:
                from .translation_agent import TranslationAgent

                self._agents[domain] = TranslationAgent()
            elif domain == AgentDomain.CORPUS:
                from .corpus_agent import CorpusAgent

                self._agents[domain] = CorpusAgent()
            elif domain == AgentDomain.STATISTICS:
                from .statistics_agent import StatisticsAgent

                self._agents[domain] = StatisticsAgent()
            else:
                # General agent handles unrouted queries
                self._agents[domain] = GeneralAgent()

        return self._agents[domain]

    async def process(self, context: AgentContext) -> AgentResponse:
        """
        Process a user query with full observability.

        1. Route to appropriate domain
        2. Execute domain agent
        3. Log to observability stack
        4. Publish to Kafka
        5. Return response with sources
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        session_id = context.session_id or str(uuid.uuid4())

        # Publish query to Kafka
        if HAS_KAFKA:
            try:
                producer = get_producer()
                producer.produce(
                    AGENT_QUERIES.name,
                    key=session_id,
                    value={
                        "query_id": query_id,
                        "session_id": session_id,
                        "query": context.query,
                        "language": context.language,
                        "agent_name": "root_agent",
                    },
                )
            except Exception as e:
                logger.warning(f"Kafka query publish failed: {e}")

        # Route the query
        domain = await self.router.route(context.query)

        # Get and execute the appropriate agent
        agent = self._get_agent(domain)

        try:
            # Execute with observability tracing
            if HAS_OBSERVABILITY:
                with langfuse_trace(
                    name="root_agent_process",
                    user_id=context.metadata.get("user_id"),
                    session_id=session_id,
                    metadata={"domain": domain.value, "query_id": query_id},
                ) as trace:
                    with GeminiLLMSpan("gemini-2.0-flash", context.query) as span:
                        response = await agent.process(context)
                        response.domain = domain

                        # Log the LLM call
                        latency_ms = (time.time() - start_time) * 1000
                        create_generation(
                            trace,
                            name=f"{domain.value}_agent",
                            model="gemini-2.0-flash",
                            input_messages=[{"role": "user", "content": context.query}],
                            output=response.content,
                            usage={
                                "prompt_tokens": len(context.query.split()) * 2,
                                "completion_tokens": len(response.content.split()) * 2,
                            },
                        )

                        # Annotate span with metadata
                        annotate_span(
                            input_data=context.query,
                            output_data=response.content,
                            metadata={
                                "domain": domain.value,
                                "sources_count": len(response.sources),
                            },
                            metrics={
                                "latency_ms": latency_ms,
                                "sources_count": float(len(response.sources)),
                            },
                        )

                        span.set_response(
                            response.content,
                            input_tokens=len(context.query.split()) * 2,
                            output_tokens=len(response.content.split()) * 2,
                        )
            else:
                response = await agent.process(context)
                response.domain = domain

            # Publish response to Kafka
            latency_ms = (time.time() - start_time) * 1000
            if HAS_KAFKA:
                try:
                    producer = get_producer()
                    producer.produce(
                        AGENT_RESPONSES.name,
                        key=session_id,
                        value={
                            "response_id": str(uuid.uuid4()),
                            "query_id": query_id,
                            "session_id": session_id,
                            "response": response.content[:2000],  # Truncate for Kafka
                            "agent_name": domain.value,
                            "sources_count": len(response.sources),
                            "latency_ms": latency_ms,
                        },
                    )
                    producer.flush()
                except Exception as e:
                    logger.warning(f"Kafka response publish failed: {e}")

            # Log to Logfire (alongside Datadog/Langfuse)
            if HAS_LOGFIRE:
                logfire_log_llm(
                    model=f"agent/{domain.value}",
                    messages=[{"role": "user", "content": context.query}],
                    response=response.content,
                    latency_ms=latency_ms,
                )

            # Save to Letta memory for conversation persistence
            await self._save_to_memory(context, response)

            return response

        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            return AgentResponse(
                content=f"I encountered an error processing your query: {str(e)}",
                domain=domain,
                metadata={"error": str(e), "query_id": query_id},
            )

    async def stream(self, context: AgentContext):
        """
        Stream response for AG-UI integration.

        Yields response chunks as they're generated.
        """
        # Route the query
        domain = await self.router.route(context.query)

        # Get the appropriate agent
        agent = self._get_agent(domain)

        # Check if agent supports streaming
        if hasattr(agent, "stream"):
            async for chunk in agent.stream(context):
                yield chunk
        else:
            # Fall back to non-streaming
            response = await agent.process(context)
            yield response.content


# ============================================================================
# General Agent (Fallback)
# ============================================================================


class GeneralAgent:
    """
    General-purpose agent for unrouted queries.

    Provides helpful responses and suggests specialized agents.
    """

    async def process(self, context: AgentContext) -> AgentResponse:
        """Process a general query."""
        suggestions = [
            "Ask about curriculum content (e.g., 'What are the learning outcomes for Junior Cycle Irish?')",
            "Search for folklore (e.g., 'Find stories about the Fianna')",
            "Translate text (e.g., 'Translate hello to Irish')",
            "Find locations (e.g., 'Show schools near Galway')",
            "Compare statistics (e.g., 'Compare Irish-medium schools across nations')",
        ]

        content = f"""I can help you with Celtic education content across Ireland, Scotland, Wales, and more.

Here are some things you can ask me:

{chr(10).join(f"- {s}" for s in suggestions)}

What would you like to know?"""

        return AgentResponse(
            content=content,
            domain=AgentDomain.GENERAL,
            follow_up_queries=suggestions[:3],
        )


# ============================================================================
# Factory Function
# ============================================================================


def create_root_agent() -> RootAgent:
    """Create and return the root agent."""
    return RootAgent()


# ============================================================================
# CLI Entry Point
# ============================================================================


async def main():
    """Interactive CLI for testing."""
    agent = create_root_agent()

    print("Celtic Education Platform - Root Agent")
    print("Type 'quit' to exit\n")

    while True:
        try:
            query = input("You: ").strip()
            if query.lower() in ["quit", "exit", "q"]:
                break

            if not query:
                continue

            context = AgentContext(query=query)
            response = await agent.process(context)

            print(f"\nAgent ({response.domain.value}): {response.content}\n")

            if response.sources:
                print(f"Sources: {len(response.sources)} documents")

            if response.follow_up_queries:
                print("Suggestions:", ", ".join(response.follow_up_queries[:2]))

            print()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
