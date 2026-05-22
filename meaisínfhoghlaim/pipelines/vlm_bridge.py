from dagster import asset, ConfigurableResource
import os
import base64
import json
import asyncio
from pydantic import Field

# We use the mcp python package to communicate with MCP servers if available, 
# or standard requests if operating as a simple client.
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    pass

class LlamaSwapResource(ConfigurableResource):
    """Resource for calling llama-swap API."""
    base_url: str = Field(default="http://llama-swap:8080/v1")
    model: str = Field(default="qwen3-vl-7b")

    def transcribe_image(self, image_base64: str) -> str:
        """Call llama-swap VLM for transcription."""
        import requests
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract and transcribe all text from this curriculum document, preserving structure."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ]
        }
        
        # We handle failures gracefully in case llama-swap isn't running in this env
        try:
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Transcription Failed: {str(e)}]"

@asset
async def fetch_ncca_curriculum_images():
    """
    Commands the Browserbase MCP server to navigate to NCCA/SEC sites,
    take screenshots of curriculum PDFs, and return base64 images.
    """
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@browserbasehq/mcp-server-browserbase"],
        env={**os.environ}
    )
    
    images = []
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Use the browserbase tool to navigate and capture screenshot
                result = await session.call_tool(
                    "navigate_and_screenshot", 
                    {"url": "https://curriculumonline.ie", "selector": ".curriculum-content"}
                )
                
                if result and result.content:
                    images.append(result.content[0].text)  # Assuming base64 is returned in text
    except Exception as e:
        # Fallback or logging if MCP server is not available during dev
        print(f"Browserbase MCP execution failed: {e}")
        
    return images

@asset
def transcribe_curriculums(fetch_ncca_curriculum_images, llama_swap: LlamaSwapResource):
    """
    Passes captured base64 images into llama-swap for VLM transcription.
    """
    transcriptions = []
    for img_b64 in fetch_ncca_curriculum_images:
        text = llama_swap.transcribe_image(img_b64)
        transcriptions.append(text)
    
    return transcriptions

@asset
async def ingest_to_knowledge_graph(transcribe_curriculums):
    """
    Extracts semantic triples from transcriptions and inserts them into the Celtic Knowledge Graph via Memgraph MCP.
    """
    server_params = StdioServerParameters(
        command="uvx",
        args=["mcp-memgraph"],
        env={**os.environ}
    )
    
    results = []
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                for text in transcribe_curriculums:
                    # Simplified triple extraction for demonstration
                    cypher_query = f"MERGE (c:Curriculum {{content: '{text[:50]}...'}) RETURN c"
                    
                    result = await session.call_tool(
                        "execute_cypher", 
                        {"query": cypher_query}
                    )
                    results.append(result)
    except Exception as e:
        print(f"Memgraph MCP execution failed: {e}")
        
    return results
