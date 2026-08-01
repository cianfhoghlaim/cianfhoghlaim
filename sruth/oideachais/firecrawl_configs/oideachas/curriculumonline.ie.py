from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key = "your-api-key")

class ExtractSchema(BaseModel):
    curriculumonline_ie: dict
    oide_ie: dict

result = app.agent(
    schema=ExtractSchema,
    prompt="Map the URL patterns, site structure, and direct file endpoints for curriculumonline.ie and oide.ie. Identify links to educational resources in both English and Irish, categorized by Primary and Post-Primary stages, to create a crawl schema for file extraction.",
)