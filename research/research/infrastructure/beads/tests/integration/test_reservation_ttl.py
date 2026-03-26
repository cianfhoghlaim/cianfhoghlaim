#!/usr/bin/env python3
"""
Reservation TTL and Expiration Test Suite

Tests verify time-based reservation behavior:
- Short TTL reservations (30s)
- Reservation blocking verification
- Auto-release after expiration
- Renewal/heartbeat mechanisms

Performance notes:
- Uses 30s TTL for expiration tests (fast enough for CI)
- Uses mock HTTP server with minimal overhead
- Each test ~30-60s (waiting for expiration)
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
from threading import Thread, Lock
from typing import Optional, Dict, Any, List
import socket
from datetime import datetime, timedelta

# Add lib directory for beads_mail_adapter
lib_path = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(lib_path))

from beads_mail_adapter import AgentMailAdapter

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_TIMEOUT = 2  # HTTP timeout
SHORT_TTL = 30    # Short TTL for expiration tests (30 seconds)


class Reservation:
    """Represents a file reservation with TTL."""
    
    def __init__(self, file_path: str, agent_name: str, ttl: int):
        self.file_path = file_path
        self.agent_name = agent_name
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
        self.created_at = datetime.now()
    
    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        return datetime.now() >= self.expires_at
    
    def renew(self, ttl: int) -> None:
        """Renew reservation with new TTL."""
        self.expires_at = datetime.now() + timedelta(seconds=ttl)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "agent_name": self.agent_name,
            "expires_at": self.expires_at.isoformat(),
            "created_at": self.created_at.isoformat()
        }


class MockAgentMailServer:
    """Mock Agent Mail server with TTL-based reservation management."""
    
    def __init__(self, port: int = 0):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[Thread] = None
        self.reservations: Dict[str, Reservation] = {}  # file_path -> Reservation
        self.lock = Lock()  # Thread-safe access to reservations
        self.request_count = 0
        
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
        
        logger.info(f"Mock Agent Mail server started on port {self.port}")
        return self.port
    
    def stop(self):
        """Stop the mock server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info(f"Mock Agent Mail server stopped")
    
    def _cleanup_expired(self) -> None:
        """Remove expired reservations."""
        with self.lock:
            expired = [path for path, res in self.reservations.items() if res.is_expired()]
            for path in expired:
                del self.reservations[path]
                logger.debug(f"Auto-released expired reservation: {path}")
    
    def _create_handler(self):
        """Create request handler class with access to server state."""
        parent = self
        
        class MockHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Suppress default logging."""
                pass
            
            def do_GET(self):
                parent.request_count += 1
                parent._cleanup_expired()  # Clean up expired reservations
                
                # Health check
                if self.path == "/api/health":
                    response = {"status": "ok"}
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                
                # Get all reservations
                elif self.path == "/api/reservations":
                    with parent.lock:
                        reservations = [res.to_dict() for res in parent.reservations.values()]
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"reservations": reservations}).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                parent.request_count += 1
                parent._cleanup_expired()  # Clean up expired reservations
                
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length) if content_length > 0 else b'{}'
                
                try:
                    data = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                    return
                
                # Create/renew reservation
                if self.path == "/api/reservations":
                    file_path = data.get("file_path")
                    agent_name = data.get("agent_name")
                    ttl = data.get("ttl", 3600)
                    
                    if not file_path or not agent_name:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "Missing file_path or agent_name"}).encode())
                        return
                    
                    with parent.lock:
                        # Check if already reserved by another agent
                        if file_path in parent.reservations:
                            existing = parent.reservations[file_path]
                            if existing.agent_name != agent_name:
                                # Conflict: already reserved by another agent
                                self.send_response(409)
                                self.send_header('Content-Type', 'application/json')
                                self.end_headers()
                                error_msg = f"File already reserved by {existing.agent_name}"
                                self.wfile.write(json.dumps({"error": error_msg}).encode())
                                return
                            else:
                                # Renewal: same agent re-reserving (heartbeat)
                                existing.renew(ttl)
                                logger.debug(f"Renewed reservation: {file_path} by {agent_name}")
                        else:
                            # New reservation
                            parent.reservations[file_path] = Reservation(file_path, agent_name, ttl)
                            logger.debug(f"Created reservation: {file_path} by {agent_name} (TTL={ttl}s)")
                    
                    self.send_response(201)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "reserved"}).encode())
                
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_DELETE(self):
                parent.request_count += 1
                parent._cleanup_expired()  # Clean up expired reservations
                
                # Release reservation: /api/reservations/{agent}/{issue_id}
                # Extract file_path from URL (last component is issue_id)
                parts = self.path.split('/')
                if len(parts) >= 5 and parts[1] == "api" and parts[2] == "reservations":
                    agent_name = parts[3]
                    issue_id = parts[4]
                    file_path = f".beads/issues/{issue_id}"
                    
                    with parent.lock:
                        if file_path in parent.reservations:
                            res = parent.reservations[file_path]
                            if res.agent_name == agent_name:
                                del parent.reservations[file_path]
                                logger.debug(f"Released reservation: {file_path}")
                    
                    self.send_response(204)
                    self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
        
        return MockHandler


class TestAgent:
    """Test agent that performs bd operations with reservation support."""
    
    def __init__(self, workspace: str, agent_name: str = "test-agent", 
                 mail_url: Optional[str] = None):
        self.workspace = workspace
        self.agent_name = agent_name
        self.mail_url = mail_url
        
        # Initialize adapter if URL provided
        if mail_url:
            self.mail = AgentMailAdapter(
                url=mail_url,
                agent_name=agent_name,
                timeout=TEST_TIMEOUT
            )
        else:
            self.mail = None
    
    def run_bd(self, *args) -> dict:
        """Run bd command and return JSON output."""
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
    
    def claim_issue(self, issue_id: str, ttl: int = 3600) -> bool:
        """Attempt to claim an issue with optional reservation."""
        # Try to reserve if Agent Mail is enabled
        if self.mail and self.mail.enabled:
            reserved = self.mail.reserve_issue(issue_id, ttl=ttl)
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
    
    def renew_reservation(self, issue_id: str, ttl: int = 3600) -> bool:
        """Renew reservation (heartbeat)."""
        if self.mail and self.mail.enabled:
            # Re-reserving with same agent acts as renewal
            return self.mail.reserve_issue(issue_id, ttl=ttl)
        return True


def test_short_ttl_reservation():
    """Test reservation with short TTL (30s)."""
    print("\n" + "="*70)
    print("TEST 1: Short TTL Reservation (30s)")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-ttl-")
    server = MockAgentMailServer()
    
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
        
        # Create and claim issue with short TTL
        issue_id = agent.create_issue("Test short TTL reservation")
        assert issue_id is not None, "Should create issue"
        
        start_time = time.time()
        claimed = agent.claim_issue(issue_id, ttl=SHORT_TTL)
        assert claimed, f"Should claim issue with {SHORT_TTL}s TTL"
        
        # Verify reservation exists
        reservations = agent.mail.get_reservations()
        assert len(reservations) == 1, f"Should have 1 reservation, got {len(reservations)}"
        assert reservations[0]["agent_name"] == "test-agent", "Reservation should be owned by test-agent"
        
        # Check TTL info
        res = reservations[0]
        expires_at = datetime.fromisoformat(res["expires_at"])
        created_at = datetime.fromisoformat(res["created_at"])
        actual_ttl = (expires_at - created_at).total_seconds()
        
        print(f"✅ PASS: Created reservation with {SHORT_TTL}s TTL")
        print(f"   • Issue: {issue_id}")
        print(f"   • Actual TTL: {actual_ttl:.1f}s")
        print(f"   • Expires at: {expires_at.strftime('%H:%M:%S')}")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_reservation_blocking():
    """Test that reservation blocks other agents from claiming."""
    print("\n" + "="*70)
    print("TEST 2: Reservation Blocking Verification")
    print("="*70)
    
    workspace = tempfile.mkdtemp(prefix="bd-test-block-")
    server = MockAgentMailServer()
    
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
        
        # Create two agents
        agent1 = TestAgent(workspace, "agent1", mail_url=mail_url)
        agent2 = TestAgent(workspace, "agent2", mail_url=mail_url)
        
        # Agent 1 creates and claims issue
        issue_id = agent1.create_issue("Test reservation blocking")
        assert issue_id is not None, "Agent 1 should create issue"
        
        claimed1 = agent1.claim_issue(issue_id, ttl=SHORT_TTL)
        assert claimed1, "Agent 1 should claim issue"
        
        # Agent 2 attempts to claim same issue (should fail)
        claimed2 = agent2.claim_issue(issue_id, ttl=SHORT_TTL)
        assert not claimed2, "Agent 2 should NOT be able to claim (blocked by reservation)"
        
        # Verify only one reservation exists
        reservations = agent1.mail.get_reservations()
        assert len(reservations) == 1, f"Should have 1 reservation, got {len(reservations)}"
        assert reservations[0]["agent_name"] == "agent1", "Reservation should be owned by agent1"
        
        print("✅ PASS: Reservation successfully blocked other agent")
        print(f"   • Agent 1 claimed: {issue_id}")
        print(f"   • Agent 2 blocked by reservation")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_auto_release_after_expiration():
    """Test that reservation auto-releases after TTL expires."""
    print("\n" + "="*70)
    print("TEST 3: Auto-Release After Expiration")
    print("="*70)
    print(f"   (This test waits {SHORT_TTL}s for expiration)")
    
    workspace = tempfile.mkdtemp(prefix="bd-test-expire-")
    server = MockAgentMailServer()
    
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
        
        # Create two agents
        agent1 = TestAgent(workspace, "agent1", mail_url=mail_url)
        agent2 = TestAgent(workspace, "agent2", mail_url=mail_url)
        
        # Agent 1 creates and claims issue with short TTL
        issue_id = agent1.create_issue("Test auto-release")
        assert issue_id is not None, "Agent 1 should create issue"
        
        start_time = time.time()
        claimed1 = agent1.claim_issue(issue_id, ttl=SHORT_TTL)
        assert claimed1, "Agent 1 should claim issue"
        
        # Verify reservation exists
        reservations = agent1.mail.get_reservations()
        assert len(reservations) == 1, "Should have 1 active reservation"
        
        # Agent 2 attempts to claim (should fail - still reserved)
        claimed2_before = agent2.claim_issue(issue_id, ttl=SHORT_TTL)
        assert not claimed2_before, "Agent 2 should be blocked before expiration"
        
        print(f"   • Waiting {SHORT_TTL}s for reservation to expire...")
        
        # Wait for TTL to expire (add 2s buffer for clock skew)
        time.sleep(SHORT_TTL + 2)
        
        elapsed = time.time() - start_time
        
        # Verify reservation auto-released (next request cleans up expired)
        reservations_after = agent2.mail.get_reservations()  # Triggers cleanup
        assert len(reservations_after) == 0, f"Reservation should have expired, got {len(reservations_after)}"
        
        # Agent 2 should now be able to claim
        claimed2_after = agent2.claim_issue(issue_id, ttl=SHORT_TTL)
        assert claimed2_after, "Agent 2 should claim issue after expiration"
        
        # Verify new reservation by agent2
        final_reservations = agent2.mail.get_reservations()
        assert len(final_reservations) == 1, "Should have 1 reservation after agent2 claims"
        assert final_reservations[0]["agent_name"] == "agent2", "Reservation should be owned by agent2"
        
        print(f"✅ PASS: Reservation auto-released after {elapsed:.1f}s")
        print(f"   • Agent 1 reservation expired")
        print(f"   • Agent 2 successfully claimed after expiration")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def test_renewal_heartbeat():
    """Test reservation renewal (heartbeat mechanism)."""
    print("\n" + "="*70)
    print("TEST 4: Renewal/Heartbeat Mechanism")
    print("="*70)
    print(f"   (This test waits {SHORT_TTL // 2}s to test renewal)")
    
    workspace = tempfile.mkdtemp(prefix="bd-test-renew-")
    server = MockAgentMailServer()
    
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
        
        # Create and claim issue with short TTL
        issue_id = agent.create_issue("Test renewal/heartbeat")
        assert issue_id is not None, "Should create issue"
        
        claimed = agent.claim_issue(issue_id, ttl=SHORT_TTL)
        assert claimed, f"Should claim issue with {SHORT_TTL}s TTL"
        
        # Get initial expiration time
        reservations = agent.mail.get_reservations()
        assert len(reservations) == 1, "Should have 1 reservation"
        initial_expires = datetime.fromisoformat(reservations[0]["expires_at"])
        
        print(f"   • Initial expiration: {initial_expires.strftime('%H:%M:%S')}")
        print(f"   • Waiting {SHORT_TTL // 2}s before renewal...")
        
        # Wait halfway through TTL
        time.sleep(SHORT_TTL // 2)
        
        # Renew reservation (heartbeat)
        renewed = agent.renew_reservation(issue_id, ttl=SHORT_TTL)
        assert renewed, "Should renew reservation"
        
        # Get new expiration time
        reservations_after = agent.mail.get_reservations()
        assert len(reservations_after) == 1, "Should still have 1 reservation"
        renewed_expires = datetime.fromisoformat(reservations_after[0]["expires_at"])
        
        # Verify expiration was extended
        extension = (renewed_expires - initial_expires).total_seconds()
        
        print(f"   • Renewed expiration: {renewed_expires.strftime('%H:%M:%S')}")
        print(f"   • Extension: {extension:.1f}s")
        
        # Extension should be approximately TTL/2 (since we renewed halfway)
        # Allow 5s tolerance for clock skew and processing time
        expected_extension = SHORT_TTL // 2
        assert abs(extension - expected_extension) < 5, \
            f"Extension should be ~{expected_extension}s, got {extension:.1f}s"
        
        print(f"✅ PASS: Reservation renewed successfully")
        print(f"   • Heartbeat extended expiration by {extension:.1f}s")
        return True
        
    finally:
        server.stop()
        shutil.rmtree(workspace, ignore_errors=True)


def main():
    """Run all TTL/expiration tests."""
    print("🧪 Reservation TTL and Expiration Test Suite")
    print(f"Testing time-based reservation behavior (SHORT_TTL={SHORT_TTL}s)")
    
    # Check if bd is available
    try:
        subprocess.run(["bd", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ERROR: bd command not found")
        print("   Install: go install github.com/steveyegge/beads/cmd/bd@latest")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Short TTL reservation", test_short_ttl_reservation),
        ("Reservation blocking", test_reservation_blocking),
        ("Auto-release after expiration", test_auto_release_after_expiration),
        ("Renewal/heartbeat mechanism", test_renewal_heartbeat),
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
    print(f"⏱️  Total time: {elapsed:.1f}s")
    
    if failed == 0:
        print("\n🎉 All TTL/expiration tests passed!")
        print("   Reservation expiration and renewal work correctly")
        sys.exit(0)
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
