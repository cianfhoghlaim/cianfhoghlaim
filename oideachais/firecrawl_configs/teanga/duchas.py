
from firecrawl import FirecrawlApp
from pydantic import BaseModel

app = FirecrawlApp(api_key = "your-api-key")

class ExtractSchema(BaseModel):
    duchas_ie_collections: list[dict]

result = app.agent(
    schema=ExtractSchema,
    prompt="i want to identify the key endpoints, formats and crawl/extraction schema for the four different collects on duchas.ie",
)
