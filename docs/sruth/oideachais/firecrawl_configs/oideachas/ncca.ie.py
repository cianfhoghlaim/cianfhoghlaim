from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key="your-api-key")


class ExtractSchema(BaseModel):
    ncca_ie_url_patterns: List[dict]
    ncca_ie_site_structure: List[dict]


result = app.agent(
    schema=ExtractSchema,
    prompt="Identify and map the URL patterns, endpoints, and site structure for all educational stages and subjects on ncca.ie. The goal is to define a crawl schema for future file extraction, ensuring coverage of both English and Irish language resources across Primary and Post-Primary sectors.",
)
