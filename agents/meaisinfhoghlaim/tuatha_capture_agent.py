"""tuatha_capture_agent — ADK agent that owns the Hermes Phase 2 control loop.

Phase 1 (current): disabled behind TUATHER_HERMES_ENABLED=false env var.
Phase 2 (future):  enabled — Hermes Agent computer-use will drive the
                   screen while the Swift daemon captures. The agent
                   exposes a small tool surface for the Cianfhoghlaim agent
                   runtime to call.

Per the agent-fleet-orchestration skill, this agent is registered in
`agents/agent_registry.py:AGENT_REGISTRY` as the 14th main agent under
the key `"tuatha_capture_agent"`.
"""
from __future__ import annotations

import os
import pathlib

import structlog
from google.adk.agents import LlmAgent

from meaisinfhoghlaim.models import model_for, filter_models
from meaisinfhoghlaim.agents.adk.litellm_agent import litellm_model

log = structlog.get_logger("tuatha_capture_agent")

HERMES_ENABLED = os.environ.get("TUATHA_HERMES_ENABLED", "false").lower() == "true"


# -- Tool implementations ------------------------------------------------------


def tuatha_capture_start(window_title: str = "Hades") -> dict:
    """Send a JSON-RPC `start_run` to the local Swift capture daemon.

    Args:
        window_title: substring of the game window title to capture.

    Returns:
        Dict with `run_dir` (the path the daemon writes keyframes + bursts to).
    """
    import json
    import socket
    import time

    sock_path = os.environ.get("TUATHA_CAPTURE_SOCKET", "/tmp/tuatha-capture.sock")
    run_id = time.strftime("%Y-%m-%dT%H%M%S")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect(sock_path)
    req = json.dumps(
        {
            "id": 1,
            "method": "start_run",
            "params": {"window_title": window_title, "run_id": run_id},
        }
    )
    sock.sendall((req + "\n").encode("utf-8"))
    resp = json.loads(sock.recv(8192).decode("utf-8").splitlines()[-1])
    return resp.get("result", {"error": resp.get("error", "unknown")})


def tuatha_capture_stop() -> dict:
    """Send a JSON-RPC `stop_run` to the Swift daemon."""
    import json
    import socket

    sock_path = os.environ.get("TUATHA_CAPTURE_SOCKET", "/tmp/tuatha-capture.sock")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(sock_path)
    sock.sendall(json.dumps({"id": 2, "method": "stop_run", "params": {}}) + "\n")
    resp = json.loads(sock.recv(1024).decode("utf-8").splitlines()[-1])
    return resp.get("result", {"error": resp.get("error", "unknown")})


def tuatha_capture_mark_event(name: str) -> dict:
    """Mark an event marker in the run manifest (e.g. 'boon_picked').

    Useful for BAML extraction alignment: the BAML extractor correlates
    boons to the closest preceding event marker.
    """
    import json
    import socket

    sock_path = os.environ.get("TUATHA_CAPTURE_SOCKET", "/tmp/tuatha-capture.sock")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect(sock_path)
    sock.sendall(
        json.dumps({"id": 3, "method": "mark_event", "params": {"name": name}}) + "\n"
    )
    resp = json.loads(sock.recv(1024).decode("utf-8").splitlines()[-1])
    return resp.get("result", {"error": resp.get("error", "unknown")})


# -- Agent construction --------------------------------------------------------

ADK_MODEL_KEY = model_for("text_llm", "default")  # → "minimax-m3"

INSTRUCTION = """You are the tuatha_capture_agent.

You own the Hermes Phase 2 control loop for the British Isles Formative
Assessment MMO pipeline. When TUATHA_HERMES_ENABLED=true (Phase 2), you
drive the screen via the Swift capture daemon while it records frames.

Phase 1 (current): the user plays manually; you return
{"status": "phase_1"} on any capture request.

Phase 2: you call tuatha_capture_start / stop / mark_event to drive the
capture loop. Always emit a mark_event before interacting with a game
element so the BAML extractor has a temporal anchor.

Status: {}""".format(
    "phase_2 (Hermes enabled)" if HERMES_ENABLED else "phase_1 (manual capture)"
)


def build_agent() -> LlmAgent:
    return LlmAgent(
        name="tuatha_capture_agent",
        model=litellm_model("minimax"),
        description=(
            "Owns the Hermes Phase 2 control loop for the Tuatha capture "
            "pipeline. Drives the Swift capture daemon over JSON-RPC."
        ),
        instruction=INSTRUCTION,
        tools=[
            tuatha_capture_start,
            tuatha_capture_stop,
            tuatha_capture_mark_event,
        ],
    )


# A module-level singleton for the agent registry.
tuatha_capture_agent = build_agent()
