# Beads Agent Mail Adapter

Lightweight Python library for integrating [MCP Agent Mail](https://github.com/Dicklesworthstone/mcp_agent_mail) with Beads issue tracking.

## Features

- **Collision Prevention**: Reserve issues to prevent duplicate work across agents
- **Real-Time Coordination**: <100ms latency vs 2-5s with git-only sync
- **Graceful Degradation**: Automatically falls back to git-only mode when server unavailable
- **Zero Configuration**: Works without Agent Mail (optional enhancement)

## Installation

No installation required - just copy `beads_mail_adapter.py` to your project:

```bash
cp lib/beads_mail_adapter.py /path/to/your/agent/
```

## Quick Start

```python
from beads_mail_adapter import AgentMailAdapter

# Initialize adapter (automatically detects server availability)
adapter = AgentMailAdapter()

if adapter.enabled:
    print("✅ Agent Mail coordination enabled")
else:
    print("⚠️  Agent Mail unavailable, using git-only mode")

# Reserve issue before claiming
if adapter.reserve_issue("bd-123"):
    # Claim issue in Beads
    subprocess.run(["bd", "update", "bd-123", "--status", "in_progress"])
    
    # Do work...
    
    # Notify other agents
    adapter.notify("status_changed", {"issue_id": "bd-123", "status": "completed"})
    
    # Release reservation
    adapter.release_issue("bd-123")
else:
    print("❌ Issue bd-123 already reserved by another agent")
```

## Configuration

Configure via environment variables:

```bash
# Agent Mail server URL (default: http://127.0.0.1:8765)
export AGENT_MAIL_URL=http://localhost:8765

# Authentication token (optional)
export AGENT_MAIL_TOKEN=your-bearer-token

# Agent identifier (default: hostname)
export BEADS_AGENT_NAME=assistant-alpha

# Request timeout in seconds (default: 5)
export AGENT_MAIL_TIMEOUT=5
```

Or pass directly to constructor:

```python
adapter = AgentMailAdapter(
    url="http://localhost:8765",
    token="your-token",
    agent_name="assistant-alpha",
    timeout=5
)
```

## API Reference

### `AgentMailAdapter(url=None, token=None, agent_name=None, timeout=5)`

Initialize adapter with optional configuration overrides.

**Attributes:**
- `enabled` (bool): True if server is available, False otherwise

### `reserve_issue(issue_id: str, ttl: int = 3600) -> bool`

Reserve an issue to prevent other agents from claiming it.

**Args:**
- `issue_id`: Issue ID (e.g., "bd-123")
- `ttl`: Reservation time-to-live in seconds (default: 1 hour)

**Returns:** True if reservation successful, False if already reserved

### `release_issue(issue_id: str) -> bool`

Release a previously reserved issue.

**Returns:** True on success

### `notify(event_type: str, data: Dict[str, Any]) -> bool`

Send notification to other agents.

**Args:**
- `event_type`: Event type (e.g., "status_changed", "issue_completed")
- `data`: Event payload

**Returns:** True on success

### `check_inbox() -> List[Dict[str, Any]]`

Check for incoming notifications from other agents.

**Returns:** List of notification messages (empty if none or server unavailable)

### `get_reservations() -> List[Dict[str, Any]]`

Get all active reservations.

**Returns:** List of active reservations

## Testing

Run the test suite:

```bash
cd lib
python3 test_beads_mail_adapter.py -v
```

Coverage includes:
- Server available/unavailable scenarios
- Graceful degradation
- Reservation conflicts
- Environment variable configuration

## Integration Examples

See [examples/python-agent/agent.py](../examples/python-agent/agent.py) for a complete agent implementation.

## Graceful Degradation

The adapter is designed to **never block or fail** your agent:

- If server is unavailable on init → `enabled = False`, all operations no-op
- If server dies mid-operation → methods return success (graceful degradation)
- If network timeout → operations continue (no blocking)
- If 409 conflict on reservation → returns `False` (expected behavior)

This ensures your agent works identically with or without Agent Mail.

## When to Use Agent Mail

**Use Agent Mail when:**
- Running multiple AI agents concurrently
- Need real-time collision prevention
- Want to reduce git commit noise
- Need <100ms coordination latency

**Stick with git-only when:**
- Single agent workflow
- No concurrent work
- Simplicity over speed
- No server infrastructure available

## Resources

- [ADR 002: Agent Mail Integration](../docs/adr/002-agent-mail-integration.md)
- [MCP Agent Mail Repository](https://github.com/Dicklesworthstone/mcp_agent_mail)
- [Latency Benchmark Results](../latency_results.md)
