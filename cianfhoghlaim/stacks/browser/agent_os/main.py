"""Browser AgentOS - Production Runtime for Web Automation Agents.

This is the main entrypoint for the Browser agent service.
It provides an orchestrator agent that routes to different browser backends:
- Stagehand: Vision-driven automation with Claude/Gemini
- Crawl4AI: High-performance web scraping
- Skyvern: RPA-style automation
- Browserbase: Cloud browser infrastructure

Usage:
    # Development
    python -m sruth.browser.agent_os.main

    # Production (via uvicorn)
    uvicorn sruth.browser.agent_os.main:app --host 0.0.0.0 --port 7773
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb
from agno.team import Team
from pydantic import BaseModel, Field

# Import shared middleware
from sruth.shared.agent_os.middleware import TinyAuthMiddleware, A2AAuthMiddleware
from sruth.shared.agent_os.config import init_config

# Initialize config for this service
config = init_config(service_name="browser", service_port=7773)

# Storage for session persistence
STORAGE_DIR = Path(os.getenv("AGNO_STORAGE_DIR", "./storage/sessions"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

team_storage = SqliteDb(
    session_table="browser_team_sessions",
    db_file=str(STORAGE_DIR / "browser_team.db"),
)


# =============================================================================
# Structured Output Models
# =============================================================================

class BrowserTask(BaseModel):
    """A browser automation task."""

    url: str
    action: str  # navigate, extract, interact, screenshot
    selectors: List[str] = Field(default_factory=list)
    instructions: Optional[str] = None


class ExtractionResult(BaseModel):
    """Result from web extraction."""

    url: str
    content: str
    structured_data: dict = Field(default_factory=dict)
    screenshots: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class BrowserResponse(BaseModel):
    """Response from browser orchestrator."""

    query: str
    status: str
    backend_used: str  # stagehand, crawl4ai, skyvern
    result: Optional[ExtractionResult] = None
    error: Optional[str] = None
    suggestions: List[str] = Field(default_factory=list)


# =============================================================================
# Backend Tool Stubs (would integrate with actual backends)
# =============================================================================

class StagehandTools:
    """Tools for Stagehand vision-driven automation."""

    def navigate(self, url: str) -> dict:
        """Navigate to URL using Stagehand."""
        return {"status": "navigated", "url": url}

    def act(self, instruction: str) -> dict:
        """Perform an action using natural language."""
        return {"status": "acted", "instruction": instruction}

    def extract(self, instruction: str, schema: Optional[dict] = None) -> dict:
        """Extract structured data from page."""
        return {"status": "extracted", "instruction": instruction}


class Crawl4AITools:
    """Tools for Crawl4AI web scraping."""

    def scrape(self, url: str, js_enabled: bool = True) -> dict:
        """Scrape a URL with Crawl4AI."""
        return {"status": "scraped", "url": url}

    def extract_structured(self, url: str, schema: dict) -> dict:
        """Extract structured data using LLM."""
        return {"status": "extracted", "url": url}


class SkyvernTools:
    """Tools for Skyvern RPA automation."""

    def run_workflow(self, workflow_id: str, inputs: dict) -> dict:
        """Run a Skyvern workflow."""
        return {"status": "running", "workflow_id": workflow_id}

    def create_task(self, url: str, goal: str) -> dict:
        """Create a Skyvern task."""
        return {"status": "created", "url": url, "goal": goal}


# =============================================================================
# Agent Definitions
# =============================================================================

DEFAULT_MODEL = os.getenv("AGNO_DEFAULT_MODEL", "gpt-4o")
CLAUDE_MODEL = os.getenv("AGNO_CLAUDE_MODEL", "claude-sonnet-4-20250514")


# Stagehand Agent - Vision-driven automation
stagehand_agent = Agent(
    name="Stagehand Agent",
    model=Claude(id=CLAUDE_MODEL),  # Claude for vision understanding
    role="Performs vision-driven web automation using natural language. "
    "Can navigate, click, fill forms, and extract data without CSS selectors.",
    tools=[StagehandTools()],
    instructions=[
        "Use natural language to describe web interactions.",
        "Prefer observe() before act() for reliability.",
        "Extract structured data using Zod schemas.",
        "Handle dynamic content with appropriate waits.",
        "Take screenshots for verification.",
        "Report page state changes clearly.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Crawl4AI Agent - High-performance scraping
crawl4ai_agent = Agent(
    name="Crawl4AI Agent",
    model=OpenAIChat(id=DEFAULT_MODEL),
    role="Performs high-performance web scraping with JavaScript rendering. "
    "Specializes in bulk extraction, crawling, and structured data output.",
    tools=[Crawl4AITools()],
    instructions=[
        "Use for bulk scraping and crawling tasks.",
        "Enable JavaScript rendering for dynamic sites.",
        "Extract clean markdown or structured JSON.",
        "Handle pagination efficiently.",
        "Respect rate limits and robots.txt.",
        "Report extraction statistics.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Skyvern Agent - RPA workflows
skyvern_agent = Agent(
    name="Skyvern Agent",
    model=OpenAIChat(id=DEFAULT_MODEL),
    role="Runs RPA-style browser workflows for complex multi-step tasks. "
    "Handles authentication, form filling, and data entry automation.",
    tools=[SkyvernTools()],
    instructions=[
        "Use for complex multi-step workflows.",
        "Handle authentication flows securely.",
        "Manage state across workflow steps.",
        "Report workflow progress and errors.",
        "Retry failed steps with backoff.",
        "Store workflow results persistently.",
    ],
    add_datetime_to_context=True,
    markdown=True,
)


# Browser Orchestrator - Routes to appropriate backend
browser_orchestrator = Team(
    name="Browser Orchestrator",
    model=OpenAIChat(id=DEFAULT_MODEL),
    members=[
        stagehand_agent,
        crawl4ai_agent,
        skyvern_agent,
    ],
    db=team_storage,
    description=(
        "Orchestrates web automation tasks by routing to the best backend. "
        "Chooses between Stagehand (vision), Crawl4AI (scraping), and "
        "Skyvern (RPA) based on the task requirements."
    ),
    instructions=[
        # Backend selection
        "Select the best backend for each task:",
        "  - Single page interaction → Stagehand",
        "  - Bulk scraping/crawling → Crawl4AI",
        "  - Complex workflows/auth → Skyvern",
        "",
        # Task routing
        "For extraction tasks without interaction → Crawl4AI",
        "For tasks requiring visual understanding → Stagehand",
        "For multi-step workflows → Skyvern",
        "",
        # Error handling
        "If one backend fails, try an alternative.",
        "Report which backend was used and why.",
        "Provide clear error messages with recovery suggestions.",
    ],
    output_schema=BrowserResponse,
    share_member_interactions=True,
    markdown=True,
    debug_mode=os.getenv("AGNO_DEBUG", "false").lower() == "true",
)


# Create AgentOS instance
agent_os = AgentOS(
    id="browser-agent-os",
    name="Browser Automation AgentOS",
    description=(
        "Production runtime for web automation agents. "
        "Orchestrates Stagehand, Crawl4AI, and Skyvern backends "
        "for vision-driven automation, scraping, and RPA workflows."
    ),
    agents=[
        stagehand_agent,
        crawl4ai_agent,
        skyvern_agent,
    ],
    teams=[browser_orchestrator],
    a2a_interface=True,
    config=os.environ.get("BROWSER_CONFIG", str(Path(__file__).parent / "config.yaml")),
)

# Get the FastAPI app
app = agent_os.get_app()

# Add middleware
app.add_middleware(A2AAuthMiddleware)
app.add_middleware(
    TinyAuthMiddleware,
    require_auth=False,
    skip_paths=["/health", "/healthz", "/ready", "/metrics", "/.well-known", "/docs", "/openapi.json"],
)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "browser-agent-os", "version": "1.0.0"}


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "agents": ["stagehand-agent", "crawl4ai-agent", "skyvern-agent"],
        "teams": ["browser-orchestrator"],
    }


if __name__ == "__main__":
    agent_os.serve(
        app="sruth.browser.agent_os.main:app",
        host="0.0.0.0",
        port=7773,
        reload=True,
    )
