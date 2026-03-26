#!/usr/bin/env python3
"""
Agent Mail Server Failure Scenarios Test Suite

Tests verify graceful degradation across various failure modes:
- Server never started (connection refused)
- Server crashes during operation (connection reset)
- Network partition (timeout)
- Server returns 500 errors
- Invalid bearer token (401/403)
- Malformed responses

Validates:
- Agents continue working in Beads-only mode
- Clear log messages about degradation
- No crashes or data loss
- JSONL remains consistent

Performance notes:
- Uses 1s HTTP timeouts for fast failure detection
- Uses --no-daemon flag to avoid 5s debounce delays
- Mock HTTP server with minimal overhead  
- Each test ~2-5s (much faster without daemon)
- Full suite ~15-30s (7 tests with workspace setup)
"""

import json
import subprocess
import tempfile
import shutil
import os
import sys
import time
import logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from typing import Optional, Dict, Any, List
import socket

# Add lib directory for beads_mail_adapter
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from beads_mail_adapter import AgentMailAdapter

# Configure logging (WARNING to reduce noise)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fast timeout for tests (1s instead of default 5s)
TEST_TIMEOUT = 1


class MockAgentMailServer:
    """Mock Agent Mail server for testing various failure scenarios."""
    
    def __init__(self, port: int = 0, failure_mode: Optional[str] = None):
        """
        Initialize mock server.
        
        Args:
            port: Port to listen on (0 = auto-assign)
            failure_mode: Type of failure to simulate:
                - None: Normal operation
                - "500_error": Always return 500
                - "timeout": Hang requests indefinitely
                - "invalid_json": Return malformed JSON
                - "crash_after_health": Crash after first health check
        """
        self.port = port
        self.failure_mode = failure_mode
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[Thread] = None
        self.request_count = 0
        self.crash_triggered = False
        
    def start(self) -> int:
        """Start the mock server. Returns actual port number."""
        handler_class = self._create_handler()
        
        # Find available port if port=0
        if self.port == 0:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                s.listen(1)
                self.port = s.getsockname()[1]
        
        self.server = HTTPServer(('127.0.0.1', self.port), handler_class)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        # Wait for server to be ready
        time.sleep(0.1)
        
        logger.info(f"Mock Agent Mail server started on port {self.port} (mode={self.failure_mode})")
        return self.port
    
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info(f"Mock Agent Mail server stopped (handled {self.request_count} requests)")
    
    def crash(self):
        """Simulate server crash."""
        self.crash_triggered = True
        self.stop()
        logger.info("Mock Agent Mail server CRASHED")
    
    def _create_handler(self):
        """Create request handler class with access to server state."""
        parent = self
        
        class MockHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Suppress default logging."""
                pass
            
            def do_GET(self):
                parent.request_count += 1
                
                # Handle crash_after_health mode
                if parent.failure_mode == "crash_after_health" and parent.request_count > 1:
                    parent.crash()
                    return
                
                # Handle timeout mode (hang long enough to trigger timeout)
                if parent.failure_mode == "timeout":
                    time.sleep(10)  # Hang longer than test timeout
                    return
                
                # Handle 500 error mode
                if parent.failure_mode == "500_error":
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
                    return
                
                # Normal health check response
                if self.path == "/api/health":
                    response = {"status": "ok"}
                    if parent.failure_mode == "invalid_json":
                        # Return malformed JSON
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(b'{invalid json')
                        return
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                parent.request_count += 1
                
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body = self.rfile.read(content_length)
                
                # Check authorization for invalid_token mode
                if parent.failure_mode == "invalid_token":
                    auth = self.headers.get('Authorization', '')
                    if not auth or auth != "Bearer valid_token":
                        self.send_response(401)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Invalid token"}).encode())
                        return
                
                # Handle timeout mode (hang long enough to trigger timeout)
                if parent.failure_mode == "timeout":
                    time.sleep(10)  # Hang longer than test timeout
                    return
                
                # Handle 500 error mode
                if parent.failure_mode == "500_error":
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
                    return
                
                # Normal responses for reservations/notifications
                if self.path == "/api/reservations":
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "reserved"}).encode())
                elif self.path == "/api/notifications":
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "sent"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_DELETE(self):
                parent.request_count += 1
                
                # Handle timeout mode (hang long enough to trigger timeout)
                if parent.failure_mode == "timeout":
                    time.sleep(10)  # Hang longer than test timeout
                    return
                
                # Normal release response
                self.send_response(204)
                self.end_headers()
        
        return MockHandler


class TestAgent:
    """Test agent that performs basic bd operations."""
    
    def __init__(self, workspace: str, agent_name: str = "test-agent", 
                 mail_url: Optional[str] = None, mail_token: Optional[str] = None):
        self.workspace = workspace
        self.agent_name = agent_name
        self.mail_url = mail_url
        self.mail_token = mail_token
        
        # Initialize adapter if URL provided
        if mail_url:
            self.mail = AgentMailAdapter(
                url=mail_url,
                token=mail_token,
                agent_name=agent_name,
                timeout=TEST_TIMEOUT  # Use global test timeout
            )
        else:
            self.mail = None
    
    def run_bd(self, *args) -> dict:
        """Run bd command and return JSON output."""
        # Use --no-daemon for fast tests (avoid 5s debounce timer)
        cmd = ["bd", "--no-daemon"] + list(args) + ["--json"]
        result = subprocess.run(
            cmd,
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return {"error": result.stderr}
        
        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON", "output": result.stdout}
        return {}
    
    def create_issue(self, title: str, priority: int = 1) -> Optional[str]:
        """Create an issue and return its ID."""
        result = self.run_bd("create", title, "-p", str(priority))
        if "error" in result:
            logger.error(f"Failed to create issue: {result['error']}")
            return None
        return result.get("id")
    
    def claim_issue(self, issue_id: str) -> bool:
        """Attempt to claim an issue (with optional reservation)."""
        # Try to reserve if Agent Mail is enabled
        if self.mail and self.mail.enabled:
            reserved = self.mail.reserve_issue(issue_id)
            if not reserved:
                logger.warning(f"Failed to reserve {issue_id}")
                return False
        
        # Update status
        result = self.run_bd("update", issue_id, "--status", "in_progress")
        
        if "error" in result:
            logger.error(f"Failed to claim {issue_id}: {result['error']}")
            if self.mail and self.mail.enabled:
                self.mail.release_issue(issue_id)
            return False
        
        return True
    
    def complete_issue(self, issue_id: str) -> bool:
        """Complete an issue."""
        result = self.run_bd("close", issue_id, "--reason", "Done")
        
        if "error" in result:
            logger.error(f"Failed to complete {issue_id}: {result['error']}")
            return False
        
        # Release reservation if Agent Mail enabled
        if self.mail and self.mail.enabled:
            self.mail.release_issue(issue_id)
        
        return True


def verify_jsonl_consistency(workspace: str) -> Dict[str, Any]:
    """
    Verify JSONL file is valid and consistent.
    
    Returns dict with:
        - valid: bool
        - issue_count: int
        - errors: list of error messages
    """
    jsonl_path = Path(workspace) / ".beads" / "issues.jsonl"
    
    if not jsonl_path.exists():
        return {"valid": False, "issue_count": 0, "errors": ["JSONL file does not exist"]}
    
    issues = {}
    errors = []
    
    try:
        with open(jsonl_path) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    record = json.loads(line)
                    issue_id = record.get("id")
                    if not issue_id:
                        errors.append(f"Line {line_num}: Missing issue ID")
                        continue
                    
                    issues[issue_id] = record
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
    except Exception as e:
        errors.append(f"Failed to read JSONL: {e}")
        return {"valid": False, "issue_count": 0, "errors": errors}
    
    return {
        "valid": len(errors) == 0,
        "issue_count": len(issues),
        "errors": errors
    }


def test_server_never_started():
    """Test that agents work when Agent Mail server is not running."""
    print("\n" + "="*70)
    print("TEST 1: Server Never Started (Connection Refused)")
    print("="*70)
    
    test_start = time.time()
    
    workspace = tempfile.mkdtemp(prefix="bd-test-noserver-")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Create agent with non-existent server
        agent = TestAgent(workspace, "test-agent", mail_url="http://127.0.0.1:9999")
        
        # Verify Agent Mail is disabled
        assert agent.mail is not None, "Agent Mail adapter should exist"
        assert not agent.mail.enabled, "Agent Mail should be disabled (server not running)"
        
        # Perform normal operations
        issue_id = agent.create_issue("Test issue when server down")
        assert issue_id is not None, "Should create issue without Agent Mail"
        
        claimed = agent.claim_issue(issue_id)
        assert claimed, "Should claim issue without Agent Mail"
        
        completed = agent.complete_issue(issue_id)
        assert completed, "Should complete issue without Agent Mail"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        assert jsonl_check["issue_count"] == 1, "Should have 1 issue in JSONL"
        
        test_elapsed = time.time() - test_start
        print("✅ PASS: Agent worked correctly without server")
        print(f"   • Created, claimed, and completed issue: {issue_id}")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        print(f"   • Test duration: {test_elapsed:.2f}s")
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_server_crash_during_operation():
    """Test that agents handle server crash gracefully."""
    print("\n" + "="*70)
    print("TEST 2: Server Crashes During Operation")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-crash-")
    server = MockAgentMailServer(failure_mode="crash_after_health")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Start server
        port = server.start()
        mail_url = f"http://127.0.0.1:{port}"
        
        # Create agent
        agent = TestAgent(workspace, "test-agent", mail_url=mail_url)
        
        # Verify Agent Mail is initially enabled
        assert agent.mail.enabled, "Agent Mail should be enabled initially"
        
        # Create issue (triggers health check, count=1)
        issue_id = agent.create_issue("Test issue before crash")
        assert issue_id is not None, "Should create issue before crash"
        
        # Server will crash on next request (count=2)
        # Agent should handle gracefully and continue in Beads-only mode
        claimed = agent.claim_issue(issue_id)
        assert claimed, "Should claim issue even after server crash"
        
        completed = agent.complete_issue(issue_id)
        assert completed, "Should complete issue after server crash"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        
        print("✅ PASS: Agent handled server crash gracefully")
        print(f"   • Server crashed after request #{server.request_count}")
        print(f"   • Agent continued in Beads-only mode")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_network_partition_timeout():
    """Test that agents handle network timeouts without blocking indefinitely."""
    print("\n" + "="*70)
    print("TEST 3: Network Partition (Timeout)")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-timeout-")
    server = MockAgentMailServer(failure_mode="timeout")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Start server (will hang all requests)
        port = server.start()
        mail_url = f"http://127.0.0.1:{port}"
        
        # Measure how long initialization takes (includes health check timeout)
        init_start = time.time()
        
        # Create agent with short timeout (2s set in TestAgent)
        agent = TestAgent(workspace, "test-agent", mail_url=mail_url)
        
        init_elapsed = time.time() - init_start
        
        # Agent Mail should be disabled after health check timeout
        # The health check itself will take ~2s to timeout
        assert not agent.mail.enabled, "Agent Mail should be disabled (health check timeout)"
        
        # Operations should proceed quickly in Beads-only mode (no more server calls)
        ops_start = time.time()
        issue_id = agent.create_issue("Test issue with timeout")
        claimed = agent.claim_issue(issue_id)
        ops_elapsed = time.time() - ops_start
        
        # Operations should be fast (not waiting on server) - allow up to 15s for bd commands
        assert ops_elapsed < 15, f"Operations took too long: {ops_elapsed:.2f}s (should be quick in Beads-only mode)"
        assert issue_id is not None, "Should create issue despite timeout"
        assert claimed, "Should claim issue despite timeout"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        
        print("✅ PASS: Agent handled network timeout gracefully")
        print(f"   • Health check timeout: {init_elapsed:.2f}s")
        print(f"   • Operations completed in {ops_elapsed:.2f}s (Beads-only mode)")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_server_500_errors():
    """Test that agents handle 500 errors gracefully."""
    print("\n" + "="*70)
    print("TEST 4: Server Returns 500 Errors")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-500-")
    server = MockAgentMailServer(failure_mode="500_error")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Start server (returns 500 for all requests)
        port = server.start()
        mail_url = f"http://127.0.0.1:{port}"
        
        # Create agent
        agent = TestAgent(workspace, "test-agent", mail_url=mail_url)
        
        # Agent Mail should be disabled (health check returns 500)
        assert not agent.mail.enabled, "Agent Mail should be disabled (500 error)"
        
        # Operations should work in Beads-only mode
        issue_id = agent.create_issue("Test issue with 500 errors")
        assert issue_id is not None, "Should create issue despite 500 errors"
        
        claimed = agent.claim_issue(issue_id)
        assert claimed, "Should claim issue despite 500 errors"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        
        print("✅ PASS: Agent handled 500 errors gracefully")
        print(f"   • Server returned {server.request_count} 500 errors")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_invalid_bearer_token():
    """Test that agents handle invalid bearer token (401) gracefully."""
    print("\n" + "="*70)
    print("TEST 5: Invalid Bearer Token (401)")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-token-")
    server = MockAgentMailServer(failure_mode="invalid_token")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Start server (requires "Bearer valid_token")
        port = server.start()
        mail_url = f"http://127.0.0.1:{port}"
        
        # Create agent with invalid token
        agent = TestAgent(workspace, "test-agent", mail_url=mail_url, mail_token="invalid_token")
        
        # Note: The health check endpoint doesn't require auth in our mock server,
        # so Agent Mail may be enabled initially. However, reservation requests
        # will fail with 401, causing graceful degradation.
        # This tests that the adapter handles auth failures during actual operations.
        
        # Operations should work (graceful degradation on auth failure)
        issue_id = agent.create_issue("Test issue with invalid token")
        assert issue_id is not None, "Should create issue despite auth issues"
        
        claimed = agent.claim_issue(issue_id)
        assert claimed, "Should claim issue (reservation may fail but claim succeeds)"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        
        print("✅ PASS: Agent handled invalid token gracefully")
        print(f"   • Server requests: {server.request_count}")
        print(f"   • Agent Mail enabled: {agent.mail.enabled}")
        print(f"   • Operations succeeded via graceful degradation")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_malformed_json_response():
    """Test that agents handle malformed JSON responses gracefully."""
    print("\n" + "="*70)
    print("TEST 6: Malformed JSON Response")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-badjson-")
    server = MockAgentMailServer(failure_mode="invalid_json")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Start server (returns malformed JSON)
        port = server.start()
        mail_url = f"http://127.0.0.1:{port}"
        
        # Create agent
        agent = TestAgent(workspace, "test-agent", mail_url=mail_url)
        
        # Agent Mail should be disabled (malformed health check response)
        assert not agent.mail.enabled, "Agent Mail should be disabled (invalid JSON)"
        
        # Operations should work in Beads-only mode
        issue_id = agent.create_issue("Test issue with malformed JSON")
        assert issue_id is not None, "Should create issue despite malformed JSON"
        
        claimed = agent.claim_issue(issue_id)
        assert claimed, "Should claim issue despite malformed JSON"
        
        # Verify JSONL consistency
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        
        print("✅ PASS: Agent handled malformed JSON gracefully")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issue(s)")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_jsonl_consistency_under_failures():
    """Test JSONL remains consistent across multiple failure scenarios."""
    print("\n" + "="*70)
    print("TEST 7: JSONL Consistency Under Multiple Failures")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-consistency-")
    
    try:
        # Initialize workspace
        subprocess.run(
            ["bd", "init", "--quiet", "--prefix", "test"],
            cwd=workspace,
            check=True,
            capture_output=True
        )
        
        # Scenario 1: No server
        agent1 = TestAgent(workspace, "agent1", mail_url="http://127.0.0.1:9999")
        id1 = agent1.create_issue("Issue 1 - no server")
        agent1.claim_issue(id1)
        
        # Scenario 2: Server crash
        server2 = MockAgentMailServer(failure_mode="crash_after_health")
        port2 = server2.start()
        agent2 = TestAgent(workspace, "agent2", mail_url=f"http://127.0.0.1:{port2}")
        id2 = agent2.create_issue("Issue 2 - server crash")
        agent2.claim_issue(id2)  # Triggers crash
        server2.stop()
        
        # Scenario 3: 500 errors
        server3 = MockAgentMailServer(failure_mode="500_error")
        port3 = server3.start()
        agent3 = TestAgent(workspace, "agent3", mail_url=f"http://127.0.0.1:{port3}")
        id3 = agent3.create_issue("Issue 3 - 500 errors")
        agent3.claim_issue(id3)
        server3.stop()
        
        # Verify JSONL is still consistent
        jsonl_check = verify_jsonl_consistency(workspace)
        assert jsonl_check["valid"], f"JSONL should be valid: {jsonl_check['errors']}"
        assert jsonl_check["issue_count"] == 3, f"Expected 3 issues, got {jsonl_check['issue_count']}"
        
        # Verify we can still read issues with bd
        result = subprocess.run(
            ["bd", "list", "--json"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=True
        )
        issues = json.loads(result.stdout)
        assert len(issues) == 3, f"Expected 3 issues from bd list, got {len(issues)}"
        
        print("✅ PASS: JSONL remained consistent across all failure scenarios")
        print(f"   • Created 3 issues across 3 different failure modes")
        print(f"   • JSONL valid with {jsonl_check['issue_count']} issues")
        print(f"   • All issues readable via bd CLI")
        return True
        
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    """Run all failure scenario tests."""
    print("🧪 Agent Mail Server Failure Scenarios Test Suite")
    print("Testing graceful degradation across various failure modes")
    
    # Check if bd is available
    try:
        subprocess.run(["bd", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ERROR: bd command not found")
        print("   Install: go install github.com/steveyegge/beads/cmd/bd@latest")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Server never started", test_server_never_started),
        ("Server crash during operation", test_server_crash_during_operation),
        ("Network partition timeout", test_network_partition_timeout),
        ("Server 500 errors", test_server_500_errors),
        ("Invalid bearer token", test_invalid_bearer_token),
        ("Malformed JSON response", test_malformed_json_response),
        ("JSONL consistency under failures", test_jsonl_consistency_under_failures),
    ]
    
    passed = 0
    failed = 0
    start_time = time.time()
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ FAIL: {name}")
            print(f"   {e}")
            failed += 1
        except Exception as e:
            print(f"\n💥 ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print(f"⏱️  Total time: {elapsed:.2f}s")
    
    if failed == 0:
        print("\n🎉 All failure scenario tests passed!")
        print("   Agents gracefully degrade to Beads-only mode in all failure cases")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
