# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="arg-type"

import os

import pytest

from app.agent_engine_app import AgentEngineApp
from tests.helpers import (
    build_get_request,
    build_post_request,
    poll_task_completion,
)


@pytest.fixture
def agent_app() -> AgentEngineApp:
    """Fixture to create and set up AgentEngineApp instance"""
    from app.agent_engine_app import agent_engine

    agent_engine.set_up()
    return agent_engine


@pytest.mark.asyncio
async def test_agent_on_message_send(agent_app: AgentEngineApp) -> None:
    """Test complete A2A message workflow from send to task completion with artifacts."""
    # Send message
    message_data = {
        "message": {
            "messageId": f"msg-{os.urandom(8).hex()}",
            "content": [{"text": "What is the capital of France?"}],
            "role": "ROLE_USER",
        },
    }
    response = await agent_app.on_message_send(
        request=build_post_request(message_data),
        context=None,
    )

    # Verify task creation
    assert "task" in response and "id" in response["task"], (
        "Expected task with ID in response"
    )

    # Poll for completion
    final_response = await poll_task_completion(agent_app, response["task"]["id"])

    # Verify artifacts
    assert final_response.get("artifacts"), "Expected artifacts in completed task"
    artifact = final_response["artifacts"][0]
    assert artifact.get("parts") and artifact["parts"][0].get("text"), (
        "Expected artifact with text content"
    )


@pytest.mark.asyncio
async def test_agent_card(agent_app: AgentEngineApp) -> None:
    """Test agent card retrieval and validation of required A2A fields."""
    response = await agent_app.handle_authenticated_agent_card(
        request=build_get_request(None),
        context=None,
    )

    # Verify core agent card fields
    assert response.get("name") == "root_agent", "Expected agent name 'root_agent'"
    assert response.get("protocolVersion") == "0.3.0", "Expected protocol version 0.3.0"
    assert response.get("preferredTransport") == "HTTP+JSON", (
        "Expected HTTP+JSON transport"
    )

    # Verify capabilities
    capabilities = response.get("capabilities", {})
    assert capabilities.get("streaming") is False, "Expected streaming disabled"

    # Verify skills
    skills = response.get("skills", [])
    assert len(skills) > 0, "Expected at least one skill"
    for skill in skills:
        assert all(key in skill for key in ["id", "name", "description"]), (
            "Expected id, name, and description in each skill"
        )

    # Verify extended card support
    assert response.get("supportsAuthenticatedExtendedCard") is True, (
        "Expected supportsAuthenticatedExtendedCard to be True"
    )
