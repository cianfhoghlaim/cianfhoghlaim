"""Z.AI MCP client for remote MCP servers (Vision, Search, Reader, Zread)."""

import base64
import json
import time
from pathlib import Path
from typing import Any

import httpx
import structlog

from ...config import BrowserConfig, get_config
from ...exceptions import BackendError

logger = structlog.get_logger()


class ZAIMCPClient:
    """Client for Z.AI's remote MCP servers.

    Z.AI provides 4 MCP servers accessible via SSE:
    1. Vision MCP: UI analysis, OCR, diagram understanding
    2. Search MCP: Web search with webSearchPrime
    3. Reader MCP: Webpage content extraction with webReader
    4. Zread MCP: GitHub documentation search
    """

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._http_client: httpx.AsyncClient | None = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the MCP client."""
        if not self.config.zai_api_key:
            raise BackendError(
                "Z.AI API key not configured",
                retryable=False,
            )

        self._http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.config.zai_api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(120.0),
        )
        self._initialized = True
        logger.info("zai_mcp_client_initialized")

    async def close(self) -> None:
        """Close the client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        self._initialized = False

    async def _call_mcp_tool(
        self,
        server_url: str,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """Call an MCP tool via SSE transport."""
        if not self._http_client:
            raise BackendError("Z.AI MCP client not initialized")

        start_time = time.perf_counter()

        request_id = f"req_{int(time.time() * 1000)}"
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        try:
            async with self._http_client.stream(
                "POST",
                server_url,
                json=payload,
                timeout=timeout,
            ) as response:
                response.raise_for_status()

                result_data = None
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str:
                            try:
                                data = json.loads(data_str)
                                if data.get("id") == request_id:
                                    if "result" in data:
                                        result_data = data["result"]
                                    elif "error" in data:
                                        raise BackendError(
                                            f"MCP error: {data['error'].get('message', 'Unknown error')}"
                                        )
                            except json.JSONDecodeError:
                                continue

                latency_ms = (time.perf_counter() - start_time) * 1000

                if result_data:
                    return {
                        "success": True,
                        "data": result_data,
                        "latency_ms": latency_ms,
                    }
                else:
                    return {
                        "success": False,
                        "error": "No response received",
                        "latency_ms": latency_ms,
                    }

        except httpx.TimeoutException:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "error": f"Request timed out after {timeout}s",
                "latency_ms": latency_ms,
            }
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error("zai_mcp_call_failed", tool=tool_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "latency_ms": latency_ms,
            }

    def _encode_image_source(self, image_source: str) -> str:
        """Encode image to proper format for MCP."""
        if image_source.startswith(("http://", "https://", "data:")):
            return image_source

        path = Path(image_source)
        if path.exists():
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
                suffix = path.suffix.lower()
                mime_type = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                }.get(suffix, "image/png")
                return f"data:{mime_type};base64,{image_data}"

        return image_source

    async def ui_to_artifact(
        self,
        image_source: str,
        prompt: str,
        output_type: str = "code",
    ) -> dict[str, Any]:
        """Convert UI screenshot to code, prompt, spec, or description.

        Args:
            image_source: Path or URL to UI screenshot
            prompt: Instructions for artifact generation
            output_type: Type of output (code, prompt, spec, description)
        """
        encoded_image = self._encode_image_source(image_source)
        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "ui_to_artifact",
            {
                "image_source": encoded_image,
                "output_type": output_type,
                "prompt": prompt,
            },
        )

    async def extract_text_from_screenshot(
        self,
        image_source: str,
        prompt: str = "Extract all text from this image",
        programming_language: str | None = None,
    ) -> dict[str, Any]:
        """Extract text from screenshot using OCR.

        Args:
            image_source: Path or URL to image
            prompt: Instructions for text extraction
            programming_language: Hint for code extraction (e.g., 'python')
        """
        encoded_image = self._encode_image_source(image_source)
        args = {
            "image_source": encoded_image,
            "prompt": prompt,
        }
        if programming_language:
            args["programming_language"] = programming_language

        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "extract_text_from_screenshot",
            args,
        )

    async def diagnose_error_screenshot(
        self,
        image_source: str,
        prompt: str = "Diagnose this error and suggest solutions",
        context: str | None = None,
    ) -> dict[str, Any]:
        """Diagnose error from screenshot.

        Args:
            image_source: Path or URL to error screenshot
            prompt: Instructions for diagnosis
            context: Additional context (e.g., 'during npm install')
        """
        encoded_image = self._encode_image_source(image_source)
        args = {
            "image_source": encoded_image,
            "prompt": prompt,
        }
        if context:
            args["context"] = context

        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "diagnose_error_screenshot",
            args,
        )

    async def understand_technical_diagram(
        self,
        image_source: str,
        prompt: str,
        diagram_type: str | None = None,
    ) -> dict[str, Any]:
        """Analyze technical diagram.

        Args:
            image_source: Path or URL to diagram
            prompt: What to understand from the diagram
            diagram_type: Type hint (architecture, flowchart, uml, er-diagram, sequence)
        """
        encoded_image = self._encode_image_source(image_source)
        args = {
            "image_source": encoded_image,
            "prompt": prompt,
        }
        if diagram_type:
            args["diagram_type"] = diagram_type

        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "understand_technical_diagram",
            args,
        )

    async def analyze_data_visualization(
        self,
        image_source: str,
        prompt: str,
        analysis_focus: str | None = None,
    ) -> dict[str, Any]:
        """Analyze data visualization (charts, graphs, dashboards).

        Args:
            image_source: Path or URL to visualization
            prompt: What insights to extract
            analysis_focus: Focus area (trends, anomalies, comparisons, metrics)
        """
        encoded_image = self._encode_image_source(image_source)
        args = {
            "image_source": encoded_image,
            "prompt": prompt,
        }
        if analysis_focus:
            args["analysis_focus"] = analysis_focus

        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "analyze_data_visualization",
            args,
        )

    async def ui_diff_check(
        self,
        expected_image: str,
        actual_image: str,
        prompt: str = "Compare these UI screenshots and identify differences",
    ) -> dict[str, Any]:
        """Compare expected vs actual UI screenshots.

        Args:
            expected_image: Path or URL to expected/reference UI
            actual_image: Path or URL to actual implementation
            prompt: Instructions for comparison
        """
        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "ui_diff_check",
            {
                "expected_image_source": self._encode_image_source(expected_image),
                "actual_image_source": self._encode_image_source(actual_image),
                "prompt": prompt,
            },
        )

    async def analyze_image(
        self,
        image_source: str,
        prompt: str,
    ) -> dict[str, Any]:
        """General-purpose image analysis.

        Args:
            image_source: Path or URL to image
            prompt: What to analyze
        """
        encoded_image = self._encode_image_source(image_source)
        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "analyze_image",
            {
                "image_source": encoded_image,
                "prompt": prompt,
            },
        )

    async def analyze_video(
        self,
        video_source: str,
        prompt: str,
    ) -> dict[str, Any]:
        """Analyze video content.

        Args:
            video_source: Path or URL to video (MP4, MOV, M4V, max 8MB)
            prompt: What to analyze in the video
        """
        return await self._call_mcp_tool(
            self.config.zai_vision_mcp_url,
            "analyze_video",
            {
                "video_source": video_source,
                "prompt": prompt,
            },
            timeout=120.0,
        )

    async def web_search(
        self,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search the web using webSearchPrime.

        Args:
            query: Search query
            limit: Maximum number of results
        """
        return await self._call_mcp_tool(
            self.config.zai_search_mcp_url,
            "webSearchPrime",
            {
                "query": query,
                "limit": limit,
            },
        )

    async def web_read(
        self,
        url: str,
        extract_format: str = "markdown",
    ) -> dict[str, Any]:
        """Read webpage content using webReader.

        Args:
            url: URL to read
            extract_format: Output format (markdown, html, text)
        """
        return await self._call_mcp_tool(
            self.config.zai_reader_mcp_url,
            "webReader",
            {
                "url": url,
                "format": extract_format,
            },
        )

    async def search_repo_docs(
        self,
        repo_url: str,
        query: str,
        limit: int = 10,
    ) -> dict[str, Any]:
        """Search documentation in a GitHub repository.

        Args:
            repo_url: GitHub repository URL (e.g., 'https://github.com/owner/repo')
            query: Search query
            limit: Maximum number of results
        """
        return await self._call_mcp_tool(
            self.config.zai_zread_mcp_url,
            "search_doc",
            {
                "repo_url": repo_url,
                "query": query,
                "limit": limit,
            },
        )

    async def get_repo_structure(
        self,
        repo_url: str,
    ) -> dict[str, Any]:
        """Get structure of a GitHub repository.

        Args:
            repo_url: GitHub repository URL
        """
        return await self._call_mcp_tool(
            self.config.zai_zread_mcp_url,
            "get_repo_structure",
            {
                "repo_url": repo_url,
            },
        )

    async def read_repo_file(
        self,
        repo_url: str,
        file_path: str,
    ) -> dict[str, Any]:
        """Read a file from a GitHub repository.

        Args:
            repo_url: GitHub repository URL
            file_path: Path to file within the repository
        """
        return await self._call_mcp_tool(
            self.config.zai_zread_mcp_url,
            "read_file",
            {
                "repo_url": repo_url,
                "file_path": file_path,
            },
        )


_mcp_client: ZAIMCPClient | None = None


async def get_zai_mcp_client() -> ZAIMCPClient:
    """Get or create the Z.AI MCP client singleton."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = ZAIMCPClient()
        await _mcp_client.initialize()
    return _mcp_client
