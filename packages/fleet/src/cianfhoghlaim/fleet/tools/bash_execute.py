"""bash_execute — Local sandbox bash execution tool.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Allows Hermes + OpenClaw agents to run shell commands in a sandboxed
/tmp/agent-sandbox/ working directory. Used for testing local software,
running pre-commit hooks, verifying JSON schemas, etc.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Any


SANDBOX_DIR = "/tmp/agent-sandbox"


async def bash_execute(
    command: str,
    cwd: str | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Execute a shell command in a sandboxed working directory.

    Args:
        command: The shell command to execute.
        cwd: Optional working directory (defaults to /tmp/agent-sandbox).
        timeout: Command timeout in seconds.

    Returns:
        {"stdout": str, "stderr": str, "exit_code": int}
    """
    if cwd is None:
        cwd = SANDBOX_DIR
    Path(cwd).mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout[-2000:],  # truncate
            "stderr": result.stderr[-500:],
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "stdout": e.stdout.decode()[-2000:] if e.stdout else "",
            "stderr": f"Timeout after {timeout}s",
            "exit_code": 124,
        }


__all__ = ["bash_execute"]
