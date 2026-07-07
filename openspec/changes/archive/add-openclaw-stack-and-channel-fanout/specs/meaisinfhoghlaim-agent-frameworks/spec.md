# `meaisinfhoghlaim-agent-frameworks` capability spec — openclaw delta

The meaisinfhoghlaim-agent-frameworks capability spec governs
the 12 specialised agents in the meaisínfhoghlaim fleet and
their routing through LiteLLM, Letta, and the Langfuse
observability stack.

This delta adds the openclaw channel-fanout gateway as the
**outbound entry-point** to the 12-agent fleet — a way for
users to reach the Celtic Tutor, the Mythology Narrator, and
the other agents through WhatsApp, Telegram, Slack, Discord,
Signal, iMessage, Matrix, MS Teams, and the openclaw WebChat.

## ADDED Requirements

### Requirement: openclaw as Channel-Fanout Entry-Point
The system SHALL route inbound messages from the openclaw channel-fanout gateway to the 12-agent meaisínfhoghlaim fleet based on the openclaw `dm_policy: "pairing"` model.

#### Scenario: Paired sender reaches Celtic Tutor
- **WHEN** a paired sender sends a message via any enabled openclaw channel (Telegram, Slack, Discord, WhatsApp, WebChat, Teams)
- **THEN** the openclaw gateway SHALL route the message to the **Celtic Tutor** agent (the fleet's primary education agent)
- **AND** the agent's response SHALL be returned to the sender via the same channel

#### Scenario: Unpaired sender receives a pairing code
- **WHEN** an unpaired sender sends a message via any enabled openclaw channel
- **THEN** the openclaw gateway SHALL return a 6-character pairing code
- **AND** the message body SHALL NOT be forwarded to any agent
- **AND** the pairing request SHALL appear in the operator's `/api/pairing/pending` queue

#### Scenario: Routing respects allow_from
- **WHEN** an operator populates the `allow_from` list in `openclaw.json`
- **THEN** only senders on that list SHALL bypass the pairing step
- **AND** all other senders SHALL be subject to the pairing flow

### Requirement: openclaw Channels Reach the Agent Fleet via LiteLLM
The system SHALL configure openclaw to call the meaisínfhoghlaim 12-agent fleet through the LiteLLM gateway (once healthy) or directly through the OpenCode Go gateway in v1.

#### Scenario: Primary path is opencode-go
- **WHEN** the openclaw container starts in v1
- **THEN** the gateway SHALL use `OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1` as the primary provider
- **AND** the `OPENCODE_GO_API_KEY` env var SHALL be the only key required

#### Scenario: LiteLLM is a documented future path
- **WHEN** the `litellm-minimax-vendor-derisking` change lands and the LiteLLM gateway is verified healthy
- **THEN** an operator MAY switch openclaw's primary provider by editing `openclaw.json` to set `provider: "litellm"` and `LITELLM_BASE_URL`/`LITELLM_MASTER_KEY` env vars
- **AND** this switch SHALL NOT require a code change or a new openspec proposal

### Requirement: openclaw Traces Land in Langfuse
The system SHALL emit openclaw LLM spans to Langfuse via the OTLP/HTTP endpoint configured by `OTEL_EXPORTER_OTLP_ENDPOINT`.

#### Scenario: Langfuse receives openclaw spans
- **WHEN** an openclaw-channeled message triggers an LLM call
- **THEN** the LLM span SHALL be exported to the Langfuse OTLP/HTTP endpoint
- **AND** the span SHALL carry `service.name=openclaw-gateway` and the channel as a span attribute (`channel=telegram|slack|...`)

#### Scenario: Operator can trace a chat session
- **WHEN** an operator searches Langfuse for a sender's phone number or chat ID
- **THEN** all LLM spans from that session SHALL be retrievable as a single trace
- **AND** the trace SHALL include the openclaw pairing state at the time of the message

### Requirement: openclaw Cognee Memory Recall
The system SHALL route memory-recall requests from chat to the cognee knowledge graph through the existing Cognee MCP server (per the `agent-memory-systems` capability).

#### Scenario: Chat user can ask "what did I learn last week"
- **WHEN** a paired sender sends the message "what did I learn last week?" to any enabled channel
- **THEN** the openclaw gateway SHALL invoke the `cognee` skill
- **AND** the response SHALL be returned to the sender within 10 seconds (95th percentile)

#### Scenario: Memory write from chat
- **WHEN** a paired sender sends a message that the agent decides to memorise
- **THEN** the agent SHALL write to cognee via the MCP server
- **AND** the write SHALL be attributed to the openclaw session (not the agent's Letta memory)