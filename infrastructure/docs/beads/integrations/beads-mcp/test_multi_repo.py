#!/usr/bin/env python3
"""Integration test for multi-repo daemon support.

Tests that the daemon can handle operations across multiple repositories
simultaneously using per-request cwd context.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from beads_mcp.bd_daemon_client import BdDaemonClient
from beads_mcp.models import CreateIssueParams, ListIssuesParams


async def main():
    """Run multi-repo integration test."""
    print("=== Multi-Repo Daemon Integration Test ===\n")
    
    # Create two temporary repositories
    with tempfile.TemporaryDirectory() as tmpdir:
        repo1 = Path(tmpdir) / "repo1"
        repo2 = Path(tmpdir) / "repo2"
        repo1.mkdir()
        repo2.mkdir()
        
        print(f"Created test repositories:")
        print(f"  repo1: {repo1}")
        print(f"  repo2: {repo2}\n")
        
        # Initialize bd in both repos
        print("Initializing beads in both repos...")
        subprocess.run(["bd", "init", "--prefix", "r1"], cwd=repo1, check=True, capture_output=True)
        subprocess.run(["bd", "init", "--prefix", "r2"], cwd=repo2, check=True, capture_output=True)
        print("✅ Initialized\n")
        
        # Find or start daemon in beads project
        beads_project = Path(__file__).parent.parent.parent
        beads_socket = beads_project / ".beads" / "bd.sock"
        
        print("Checking daemon status...")
        if not beads_socket.exists():
            print("Starting daemon in beads project...")
            subprocess.run(["bd", "daemon", "start"], cwd=beads_project, check=True, capture_output=True)
            await asyncio.sleep(1)  # Give daemon time to start
            print("✅ Daemon started\n")
        else:
            print(f"✅ Daemon socket found at {beads_socket}\n")
        
        # Create daemon clients for each repo, pointing to beads project socket
        print("Creating daemon clients...")
        client1 = BdDaemonClient(socket_path=str(beads_socket), working_dir=str(repo1))
        client2 = BdDaemonClient(socket_path=str(beads_socket), working_dir=str(repo2))
        print("✅ Clients created\n")
        
        # Test 1: Create issues in both repos concurrently
        print("Test 1: Creating issues concurrently in both repos...")
        params1 = CreateIssueParams(
            title="Issue in repo1",
            description="This should go to repo1 database",
            priority=1,
            issue_type="task"
        )
        params2 = CreateIssueParams(
            title="Issue in repo2",
            description="This should go to repo2 database",
            priority=1,
            issue_type="task"
        )
        
        issue1, issue2 = await asyncio.gather(
            client1.create(params1),
            client2.create(params2)
        )
        
        print(f"  ✅ Created {issue1.id} in repo1")
        print(f"  ✅ Created {issue2.id} in repo2")
        assert issue1.id.startswith("r1-"), f"Expected r1- prefix, got {issue1.id}"
        assert issue2.id.startswith("r2-"), f"Expected r2- prefix, got {issue2.id}"
        print()
        
        # Test 2: List issues from each repo - should be isolated
        print("Test 2: Verifying issue isolation between repos...")
        list_params = ListIssuesParams()
        
        issues1 = await client1.list_issues(list_params)
        issues2 = await client2.list_issues(list_params)
        
        print(f"  repo1 issues: {[i.id for i in issues1]}")
        print(f"  repo2 issues: {[i.id for i in issues2]}")
        
        assert len(issues1) == 1, f"Expected 1 issue in repo1, got {len(issues1)}"
        assert len(issues2) == 1, f"Expected 1 issue in repo2, got {len(issues2)}"
        assert issues1[0].id == issue1.id, "repo1 issue mismatch"
        assert issues2[0].id == issue2.id, "repo2 issue mismatch"
        print("  ✅ Issues are properly isolated\n")
        
        # Test 3: Rapid concurrent operations
        print("Test 3: Rapid concurrent operations across repos...")
        tasks = []
        for i in range(5):
            p1 = CreateIssueParams(
                title=f"Concurrent issue {i} in repo1",
                priority=2,
                issue_type="task"
            )
            p2 = CreateIssueParams(
                title=f"Concurrent issue {i} in repo2",
                priority=2,
                issue_type="task"
            )
            tasks.append(client1.create(p1))
            tasks.append(client2.create(p2))
        
        created = await asyncio.gather(*tasks)
        print(f"  ✅ Created {len(created)} issues concurrently")
        
        # Verify counts
        issues1 = await client1.list_issues(list_params)
        issues2 = await client2.list_issues(list_params)
        
        print(f"  repo1 total: {len(issues1)} issues")
        print(f"  repo2 total: {len(issues2)} issues")
        assert len(issues1) == 6, f"Expected 6 issues in repo1, got {len(issues1)}"
        assert len(issues2) == 6, f"Expected 6 issues in repo2, got {len(issues2)}"
        print("  ✅ All concurrent operations succeeded\n")
        
        # Test 4: Verify prefixes are correct
        print("Test 4: Verifying all prefixes are correct...")
        for issue in issues1:
            assert issue.id.startswith("r1-"), f"repo1 issue has wrong prefix: {issue.id}"
        for issue in issues2:
            assert issue.id.startswith("r2-"), f"repo2 issue has wrong prefix: {issue.id}"
        print("  ✅ All prefixes correct\n")
        
        print("=== All Tests Passed! ===")
        print("\nSummary:")
        print("  ✅ Per-request context routing works")
        print("  ✅ Multiple repos are properly isolated")
        print("  ✅ Concurrent operations succeed")
        print("  ✅ Daemon handles rapid context switching")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
