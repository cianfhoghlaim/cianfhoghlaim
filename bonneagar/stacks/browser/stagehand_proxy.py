"""Stagehand Proxy — bridges OpenAI Responses API to Chat Completions for OpenCode Go.

Stagehand V3's SEA binary uses @ai-sdk/openai's OpenAIResponsesLanguageModel,
which sends requests to /v1/responses. OpenCode Go only supports /v1/chat/completions.
This proxy sits between them, converting request/response formats.

Architecture:
  Stagehand SEA binary → /v1/responses → [proxy] → /v1/chat/completions → OpenCode Go
"""

import logging
import os
import time
import uuid
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("stagehand-proxy")

app = FastAPI(title="Stagehand Responses Proxy")

OPENCODE_API_KEY = os.environ.get("OPENCODE_GO_API", "")
OPENCODE_BASE_URL = os.environ.get("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1")
OPENCODE_CHAT_URL = f"{OPENCODE_BASE_URL.rstrip('/')}/chat/completions"
DEFAULT_MODEL = os.environ.get("PROXY_DEFAULT_MODEL", "deepseek-v4-pro")
REQUEST_TIMEOUT = int(os.environ.get("PROXY_REQUEST_TIMEOUT", "180"))


def _convert_input_to_messages(inputs: list[Any]) -> list[dict[str, Any]]:
    """Convert Responses API 'input' array to Chat Completions 'messages' array.

    Handles:
    - Simple role/content messages: {"role": "user", "content": "text"}
    - Complex content: {"role": "user", "content": [{"type": "input_text", "text": "..."}]}
    - Function call outputs: {"type": "function_call_output", "call_id": "...", "output": "..."}
    - Function calls from assistant: {"type": "function_call", "name": "...", "arguments": "..."}
    """
    messages: list[dict[str, Any]] = []
    for item in inputs:
        if isinstance(item, str):
            messages.append({"role": "user", "content": item})
            continue

        item_type = item.get("type", "")

        if item_type == "function_call":
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": item.get("call_id", f"call_{uuid.uuid4().hex[:24]}"),
                    "type": "function",
                    "function": {
                        "name": item.get("name", ""),
                        "arguments": item.get("arguments", "{}"),
                    },
                }],
            })
            continue

        if item_type == "function_call_output":
            tool_call_id = item.get("call_id", "")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": item.get("output", ""),
            })
            continue

        role = item.get("role", "user")
        content = item.get("content", "")

        if isinstance(content, list):
            text_parts: list[str] = []
            image_parts: list[dict[str, Any]] = []
            for part in content:
                if isinstance(part, dict):
                    ptype = part.get("type", "")
                    if ptype == "input_text":
                        text_parts.append(part.get("text", ""))
                    elif ptype == "input_image":
                        image_url = part.get("image_url", "")
                        if image_url:
                            image_parts.append({
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            })
                        else:
                            b64 = part.get("image_url_data", part.get("data", ""))
                            mime = part.get("media_type", "image/png")
                            if b64:
                                image_parts.append({
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime};base64,{b64}"},
                                })
                    elif ptype == "text":
                        text_parts.append(part.get("text", ""))
            if image_parts:
                combined: list[dict[str, Any]] = []
                if text_parts:
                    combined.append({"type": "text", "text": "\n".join(text_parts)})
                combined.extend(image_parts)
                messages.append({"role": role, "content": combined})
            elif text_parts:
                messages.append({"role": role, "content": "\n".join(text_parts)})
        elif isinstance(content, str):
            messages.append({"role": role, "content": content})
        else:
            messages.append({"role": role, "content": str(content)})

    return messages


def _convert_tools_responses_to_chat(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Responses API tool format to Chat Completions tool format.

    Responses: {"type": "function", "name": "...", "description": "...", "parameters": {...}}
    Chat:      {"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}
    """
    chat_tools: list[dict[str, Any]] = []
    for tool in tools:
        tool_type = tool.get("type", "")

        if tool_type == "function":
            if "function" in tool:
                chat_tools.append(tool)
            else:
                chat_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "parameters": tool.get("parameters", {}),
                    },
                })
        elif tool_type == "web_search" or tool_type == "web_search_preview":
            pass
        elif tool_type:
            chat_tools.append(tool)

    return chat_tools


def _convert_chat_to_responses(
    chat_response: dict[str, Any],
    original_model: str,
) -> dict[str, Any]:
    """Convert OpenAI Chat Completion response to Responses API response format.

    Chat Completion has:
      choices[0].message.content, choices[0].message.tool_calls, usage.prompt_tokens, etc.

    Responses API expects:
      output[].content[].text, output[].function_call, usage.input_tokens, usage.output_tokens
    """
    now = int(time.time())
    resp_id = f"resp_{uuid.uuid4().hex[:24]}"
    msg_id = f"msg_{uuid.uuid4().hex[:24]}"

    choices = chat_response.get("choices", [])
    usage = chat_response.get("usage", {})
    model = chat_response.get("model", original_model)

    output: list[dict[str, Any]] = []

    if choices:
        choice = choices[0]
        message = choice.get("message", {})
        content = message.get("content")
        tool_calls = message.get("tool_calls")

        content_items: list[dict[str, Any]] = []
        if content:
            content_items.append({
                "type": "output_text",
                "text": content,
                "annotations": [],
            })

        if content_items:
            output.append({
                "type": "message",
                "id": msg_id,
                "status": "completed",
                "role": "assistant",
                "content": content_items,
            })

        if tool_calls:
            for tc in tool_calls:
                func = tc.get("function", {})
                output.append({
                    "type": "function_call",
                    "call_id": tc.get("id", f"call_{uuid.uuid4().hex[:24]}"),
                    "name": func.get("name", ""),
                    "arguments": func.get("arguments", "{}"),
                })

    if not output:
        output.append({
            "type": "message",
            "id": msg_id,
            "status": "completed",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "", "annotations": []}],
        })

    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)

    response = {
        "id": resp_id,
        "object": "response",
        "created_at": now,
        "model": model,
        "status": "completed",
        "output": output,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
        "metadata": {},
    }

    for key in ("id", "object", "created", "model"):
        if key in chat_response and key not in response:
            response[f"_chat_{key}"] = chat_response[key]

    return response


@app.post("/v1/responses")
@app.post("/responses")
async def handle_responses(request: Request) -> Response:
    data = await request.json()
    model = data.pop("model", DEFAULT_MODEL)

    input_data = data.get("input", [])
    if isinstance(input_data, str):
        input_data = [{"role": "user", "content": input_data}]
    messages = _convert_input_to_messages(input_data)

    responses_tools = data.get("tools", [])
    chat_tools = _convert_tools_responses_to_chat(responses_tools) if responses_tools else []

    temperature = data.get("temperature")
    max_output_tokens = data.get("max_output_tokens")
    top_p = data.get("top_p")

    chat_payload: dict[str, Any] = {"model": model, "messages": messages}

    if chat_tools:
        chat_payload["tools"] = chat_tools

    tool_choice = data.get("tool_choice")
    if tool_choice is not None:
        if isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
            chat_payload["tool_choice"] = {
                "type": "function",
                "function": {"name": tool_choice["function"]["name"]},
            }
        elif isinstance(tool_choice, str):
            chat_payload["tool_choice"] = tool_choice
        else:
            chat_payload["tool_choice"] = "auto"

    if temperature is not None:
        chat_payload["temperature"] = temperature
    if max_output_tokens is not None:
        chat_payload["max_tokens"] = max_output_tokens
    if top_p is not None:
        chat_payload["top_p"] = top_p

    if data.get("stream"):
        chat_payload["stream"] = True

    auth_key = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    api_key = auth_key or OPENCODE_API_KEY

    logger.info(f"[responses→chat] model={model} msgs={len(messages)} tools={len(chat_tools)}")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            resp = await client.post(
                OPENCODE_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=chat_payload,
            )
        except httpx.TimeoutException as exc:
            logger.error(f"Upstream timeout: {exc}")
            return JSONResponse(
                content={"error": {"message": f"Upstream timeout: {exc}", "type": "proxy_timeout"}},
                status_code=504,
            )
        except httpx.HTTPError as exc:
            logger.error(f"Upstream error: {exc}")
            return JSONResponse(
                content={"error": {"message": f"Upstream error: {exc}", "type": "proxy_error"}},
                status_code=502,
            )

    if resp.status_code != 200:
        logger.error(f"Upstream returned {resp.status_code}: {resp.text[:500]}")
        return JSONResponse(
            content={"error": {"message": resp.text[:2000], "type": "upstream_error", "code": resp.status_code}},
            status_code=resp.status_code,
        )

    is_stream = chat_payload.get("stream", False)

    if is_stream:
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={"Content-Type": "text/event-stream"},
        )

    upstream = resp.json()
    responses_fmt = _convert_chat_to_responses(upstream, model)

    logger.info(
        f"[responses←chat] id={responses_fmt['id']} "
        f"tokens={responses_fmt['usage']['input_tokens']}+{responses_fmt['usage']['output_tokens']} "
        f"output_types={[o['type'] for o in responses_fmt['output']]}"
    )

    return JSONResponse(content=responses_fmt)


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def handle_chat(request: Request) -> Response:
    data = await request.json()

    if "model" not in data:
        data["model"] = DEFAULT_MODEL

    auth_key = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    api_key = auth_key or OPENCODE_API_KEY

    logger.info(f"[chat passthrough] model={data['model']}")

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            resp = await client.post(
                OPENCODE_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=data,
            )
        except httpx.HTTPError as exc:
            return JSONResponse(
                content={"error": str(exc)},
                status_code=502,
            )

    if resp.status_code != 200:
        return JSONResponse(content=resp.json(), status_code=resp.status_code)

    return JSONResponse(content=resp.json())


@app.get("/v1/models")
@app.get("/models")
async def handle_models() -> Response:
    return JSONResponse(content={
        "object": "list",
        "data": [
            {"id": DEFAULT_MODEL, "object": "model", "owned_by": "opencode-go"},
        ],
    })


@app.get("/health")
async def health() -> Response:
    return JSONResponse(content={"status": "ok", "proxy": "stagehand-responses"})


if __name__ == "__main__":
    port = int(os.environ.get("PROXY_PORT", "4005"))
    host = os.environ.get("PROXY_HOST", "0.0.0.0")
    logger.info(f"Stagehand proxy starting on {host}:{port} → {OPENCODE_CHAT_URL}")
    uvicorn.run(app, host=host, port=port)