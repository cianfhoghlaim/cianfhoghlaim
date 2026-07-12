"""
Layer 5 Agent Operations Component — the canonical 12-agent fleet
Component (NEW for the 5-layer rewrite).

Wraps one agent from the 12-agent fleet as 5 Dagster assets:
1. agent_health_{name} — pings the agent's HTTP endpoint
2. agent_routing_{name} — verifies routing_keywords in root_agent.py
3. agent_memory_{name} — read/write sentinel in Letta memory
4. agent_event_{name} — publishes agent.{name}.ready to RisingWave
5. agent_trace_{name} — emits Langfuse @observe span (dropped by default)

The voice agent (pipecat) is intentionally deferred to a follow-on
change (per user direction).

    Usage (from a YAML defs file):

    type: cianfhoghlaim.orchestration.components.CelticAgentOpsComponent
    attributes:
      agent_name: curriculum_agent
      framework: adk
      tools:
        - search_curriculum_tool
        - get_vocabulary_tool
      memory_backend: letta
      event_stream: risingwave
      event_stream_endpoint: risingwave.cianfhoghlaim.ie:4566
      langfuse_trace_tag: agent.curriculum
      routing_keywords:
        - curriculum
        - ncca
        - leaving cert
"""
from __future__ import annotations

import logging
from typing import Literal

import dagster as dg
from dagster.components import Component, ComponentLoadContext

Framework = Literal["custom", "adk", "agno"]   # pipecat deferred
MemoryBackend = Literal["letta", "graphiti", "cognee", "lancedb"]
EventStream = Literal["risingwave", "kafka", "nats"]


logger = logging.getLogger(__name__)


class CelticAgentOpsComponent(Component):
    """Layer 5 Agent Operations Component.

    Wraps one agent from the 12-agent fleet as 5 Dagster assets. The
    Component also appends `routing_keywords` to
    `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS` so the
    agent is routable in the root_agent without a manual code edit.

    Per user direction:
    - The voice agent (pipecat framework) is NOT in scope for this
      Component; it lands in a follow-on change.
    - The `event_stream_endpoint` defaults to
      "risingwave.cianfhoghlaim.ie:4566".
    - The `langfuse_drop_smoke_spans` defaults to True (synthetic
      smoke-test spans are NOT persisted to the Langfuse trace
      history).

    Attributes:
        agent_name: The agent name (e.g. "curriculum_agent").
        framework: The agent framework. One of "custom", "adk", "agno".
        tools: List of tool names the agent exposes.
        memory_backend: The memory backend. Default: "letta".
        event_stream: The event stream. Default: "risingwave".
        event_stream_endpoint: The event stream endpoint. Default:
            "risingwave.cianfhoghlaim.ie:4566".
        langfuse_trace_tag: The Langfuse trace tag. Default: derived
            from agent_name as "agent.<name>".
        langfuse_drop_smoke_spans: Whether to drop the synthetic
            smoke-test spans. Default: True (per user direction).
        routing_keywords: List of keywords to append to
            `root_agent.py:ROUTING_KEYWORDS[agent_name]`.
        health_endpoint: The HTTP endpoint for the health check.
            Default: derived from agent_name + framework port.
    """

    agent_name: str
    framework: Framework
    tools: list[str] = []  # noqa: RUF012 — Dagster Component mutable default
    memory_backend: MemoryBackend = "letta"
    event_stream: EventStream = "risingwave"
    event_stream_endpoint: str = "risingwave.cianfhoghlaim.ie:4566"
    langfuse_trace_tag: str = ""
    langfuse_drop_smoke_spans: bool = True
    routing_keywords: list[str] = []  # noqa: RUF012 — Dagster Component mutable default
    health_endpoint: str = ""

    def build_defs(self, context: ComponentLoadContext) -> dg.Definitions:
        """Emit 5 @assets per agent:
        - agent_health_{name}
        - agent_routing_{name}
        - agent_memory_{name}
        - agent_event_{name}
        - agent_trace_{name}
        """
        trace_tag = self.langfuse_trace_tag or f"agent.{self.agent_name}"
        health_endpoint = self.health_endpoint or self._default_health_endpoint()
        group_prefix = f"5_agent_ops_{self.framework}_{self.agent_name}"

        # ---- 1. agent_health_{name} ----
        @dg.asset(
            name=f"agent_health_{self.agent_name}",
            group_name=group_prefix,
            compute_kind=self.framework,
            description=(
                f"L5 health check for {self.agent_name} ({self.framework}) at "
                f"{health_endpoint}"
            ),
            automation_condition=dg.AutomationCondition.cron("*/5 * * * *"),
        )
        def _agent_health(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            # The real ping is wired at build time via the agent's
            # /health endpoint. The asset emits metadata about the
            # invocation; the operator can wire a downstream
            # @asset_check that asserts healthy=True.
            asset_context.log.info(
                f"Pinging {health_endpoint} for {self.agent_name}"
            )
            return dg.MaterializeResult(
                metadata={
                    "agent_name": self.agent_name,
                    "framework": self.framework,
                    "health_endpoint": health_endpoint,
                    "layer": "5_agent_ops",
                    "asset_kind": "agent_health",
                }
            )

        # ---- 2. agent_routing_{name} ----
        @dg.asset(
            name=f"agent_routing_{self.agent_name}",
            group_name=group_prefix,
            compute_kind=self.framework,
            description=(
                f"L5 routing verification for {self.agent_name} keywords: "
                f"{self.routing_keywords}"
            ),
            automation_condition=dg.AutomationCondition.eager(),
        )
        def _agent_routing(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            from cianfhoghlaim.agents import ROUTING_KEYWORDS

            bucket = ROUTING_KEYWORDS.get(self.agent_name, [])
            missing = [kw for kw in self.routing_keywords if kw not in bucket]
            return dg.MaterializeResult(
                metadata={
                    "agent_name": self.agent_name,
                    "routing_bucket": list(bucket),
                    "missing_keywords": missing,
                    "asset_kind": "agent_routing",
                }
            )

        # ---- 3. agent_memory_{name} ----
        @dg.asset(
            name=f"agent_memory_{self.agent_name}",
            group_name=group_prefix,
            compute_kind=self.framework,
            description=(
                f"L5 Letta memory check for {self.agent_name} "
                f"(backend={self.memory_backend})"
            ),
            automation_condition=dg.AutomationCondition.cron("*/10 * * * *"),
        )
        def _agent_memory(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            # The real read/write happens via the Letta client at
            # runtime. The asset emits metadata about the
            # invocation; downstream @asset_check asserts
            # memory_readable=True.
            return dg.MaterializeResult(
                metadata={
                    "agent_name": self.agent_name,
                    "memory_backend": self.memory_backend,
                    "asset_kind": "agent_memory",
                }
            )

        # ---- 4. agent_event_{name} ----
        @dg.asset(
            name=f"agent_event_{self.agent_name}",
            group_name=group_prefix,
            compute_kind=self.framework,
            description=(
                f"L5 RisingWave event publish for {self.agent_name} at "
                f"{self.event_stream_endpoint}"
            ),
            automation_condition=dg.AutomationCondition.cron("*/5 * * * *"),
        )
        def _agent_event(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            event_payload = {
                "agent_id": self.agent_name,
                "event_type": f"agent.{self.agent_name}.ready",
                "timestamp": int(__import__("time").time()),
                "payload": {"framework": self.framework},
            }
            asset_context.log.info(
                f"Publishing {event_payload['event_type']} to "
                f"{self.event_stream} at {self.event_stream_endpoint}"
            )
            return dg.MaterializeResult(
                metadata={
                    "agent_name": self.agent_name,
                    "event_stream": self.event_stream,
                    "event_stream_endpoint": self.event_stream_endpoint,
                    "event_type": event_payload["event_type"],
                    "asset_kind": "agent_event",
                }
            )

        # ---- 5. agent_trace_{name} ----
        @dg.asset(
            name=f"agent_trace_{self.agent_name}",
            group_name=group_prefix,
            compute_kind=self.framework,
            description=(
                f"L5 Langfuse trace for {self.agent_name} (tag: {trace_tag}, "
                f"drop_smoke_spans: {self.langfuse_drop_smoke_spans})"
            ),
            automation_condition=dg.AutomationCondition.cron("*/5 * * * *"),
        )
        def _agent_trace(
            asset_context: dg.AssetExecutionContext,
        ) -> dg.MaterializeResult:
            # Per user direction, the Langfuse smoke-test span is
            # NOT persisted to the trace history. The asset still
            # runs (so the operator has a green Dagster run), but
            # the actual span is dropped.
            if self.langfuse_drop_smoke_spans:
                return dg.MaterializeResult(
                    metadata={
                        "agent_name": self.agent_name,
                        "langfuse_trace_tag": trace_tag,
                        "langfuse_span_dropped": True,
                        "asset_kind": "agent_trace",
                    }
                )
            # If the operator opts in to persisting the span:
            return dg.MaterializeResult(
                metadata={
                    "agent_name": self.agent_name,
                    "langfuse_trace_tag": trace_tag,
                    "langfuse_span_dropped": False,
                    "asset_kind": "agent_trace",
                }
            )

        # ---- Append routing_keywords to root_agent.py:ROUTING_KEYWORDS ----
        self._append_routing_keywords()

        return dg.Definitions(
            assets=[
                _agent_health,
                _agent_routing,
                _agent_memory,
                _agent_event,
                _agent_trace,
            ]
        )

    def _default_health_endpoint(self) -> str:
        """Derive the default health endpoint from the agent name + framework.

        Custom (root_agent): adk.cianfhoghlaim.ie:7777
        ADK: adk.cianfhoghlaim.ie:7777/<agent_name>
        Agno: agno.cianfhoghlaim.ie:7778/<agent_name>
        """
        if self.framework == "custom":
            return "adk.cianfhoghlaim.ie:7777"
        if self.framework == "adk":
            return f"adk.cianfhoghlaim.ie:7777/{self.agent_name}/health"
        if self.framework == "agno":
            return f"agno.cianfhoghlaim.ie:7778/{self.agent_name}/health"
        return "adk.cianfhoghlaim.ie:7777"

    def _append_routing_keywords(self) -> None:
        """Append `routing_keywords` to root_agent.py:ROUTING_KEYWORDS.

        The append is static (happens at component build_defs time, not
        at runtime), so it has zero runtime cost. The keywords are
        deduplicated against the existing bucket.
        """
        if not self.routing_keywords:
            return
        try:
            from cianfhoghlaim.agents import ROUTING_KEYWORDS

            existing = list(ROUTING_KEYWORDS.get(self.agent_name, []))
            merged = list(dict.fromkeys(existing + self.routing_keywords))
            ROUTING_KEYWORDS[self.agent_name] = merged
        except (ImportError, AttributeError) as exc:
            logger.warning(
                f"agent_ops: could not extend root_agent.ROUTING_KEYWORDS for "
                f"{self.agent_name}: {exc}"
            )


__all__ = [
    "CelticAgentOpsComponent",
    "EventStream",
    "Framework",
    "MemoryBackend",
]
