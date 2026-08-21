from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key="your-api-key")


class ExtractSchema(BaseModel):
    url_patterns: List[dict]
    site_structure: dict
    file_endpoints: List[dict]
    educational_resources: List[dict]


result = app.agent(
    schema=ExtractSchema,
    prompt="Map the URL patterns, site structure, and direct file endpoints for examinations.ie across all available years. Identify and categorize links to educational resources in both English and Irish, specifically segmenting them by Primary and Post-Primary stages to create a comprehensive crawl schema for file extraction.",
)
