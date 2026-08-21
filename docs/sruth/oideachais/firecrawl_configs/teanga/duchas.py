from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key="your-api-key")


class ExtractSchema(BaseModel):
    duchas_ie_collections: List[dict]


result = app.agent(
    schema=ExtractSchema,
    prompt="i want to identify the key endpoints, formats and crawl/extraction schema for the four different collects on duchas.ie",
)
