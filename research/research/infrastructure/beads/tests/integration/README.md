# Integration Tests

This directory contains integration tests for bd (beads) that test end-to-end functionality.

## Tests

### test_agent_race.py

Multi-agent race condition test that validates collision prevention with Agent Mail.

**What it tests:**
- Multiple agents simultaneously attempting to claim the same issue
- WITH Agent Mail: Only one agent succeeds (via reservation)
- WITHOUT Agent Mail: Multiple agents may succeed (collision)
- Verification via JSONL that no duplicate claims occur

### test_mail_failures.py

Agent Mail server failure scenarios test that validates graceful degradation.

**What it tests:**
- Server never started (connection refused)
- Server crashes during operation  
- Network partition (timeout)
- Server returns 500 errors
- Invalid bearer token (401)
- Malformed JSON responses
- JSONL consistency under multiple failures

**Performance:**
- Uses `--no-daemon` flag for fast tests (~33s total)
- 1s HTTP timeouts for quick failure detection
- Mock HTTP server avoids real network calls

### test_reservation_ttl.py

Reservation TTL and expiration test that validates time-based reservation behavior.

**What it tests:**
- Short TTL reservations (30s)
- Reservation blocking verification (agent2 cannot claim while agent1 holds reservation)
- Auto-release after expiration (expired reservations become available)
- Renewal/heartbeat mechanism (re-reserving extends expiration)

**Performance:**
- Uses `--no-daemon` flag for fast tests
- 30s TTL for expiration tests (includes wait time)
- Total test time: ~57s (includes 30s+ waiting for expiration)
- Mock HTTP server with full TTL management

## Prerequisites

- bd installed: `go install github.com/steveyegge/beads/cmd/bd@latest`
- Agent Mail server running (optional, for full test suite):
  ```bash
  cd ~/src/mcp_agent_mail
  source .venv/bin/activate
  uv run python -m mcp_agent_mail.cli serve-http
  ```

## Running Tests

**Run test_agent_race.py:**
```bash
python3 tests/integration/test_agent_race.py
```

**Run test_mail_failures.py:**
```bash
python3 tests/integration/test_mail_failures.py
```

**Run test_reservation_ttl.py:**
```bash
python3 tests/integration/test_reservation_ttl.py
```

**Run all integration tests:**
```bash
python3 tests/integration/test_agent_race.py
python3 tests/integration/test_mail_failures.py
python3 tests/integration/test_reservation_ttl.py
```

## Expected Results

### test_agent_race.py
- **WITH Agent Mail running:** Test 1 passes (only 1 claim), Test 2 shows collision, Test 3 passes
- **WITHOUT Agent Mail running:** All tests demonstrate collision (expected behavior without reservation system)

### test_mail_failures.py
- All 7 tests should pass in ~30-35 seconds
- Each test validates graceful degradation to Beads-only mode
- JSONL remains consistent across all failure scenarios

### test_reservation_ttl.py
- All 4 tests should pass in ~57 seconds
- Tests verify TTL-based reservation expiration and renewal
- Includes 30s+ wait time to validate actual expiration behavior

## Adding New Tests

Integration tests should:
1. Use temporary workspaces (cleaned up automatically)
2. Test real bd CLI commands, not just internal APIs
3. Use `--no-daemon` flag for fast execution
4. Verify behavior in `.beads/issues.jsonl` when relevant
5. Clean up resources in `finally` blocks
6. Provide clear output showing what's being tested
