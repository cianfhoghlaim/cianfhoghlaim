from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import List, Optional

app = FirecrawlApp(api_key="your-api-key")


class ExtractSchema(BaseModel):
    collection_information: dict
    english_stories: List[dict]
    irish_scottish_gaelic_stories: List[dict]


result = app.agent(
    schema=ExtractSchema,
    prompt="Extract the schema and key endpoints for stories from hiddenheritages.ai, including image file URLs, transcription text, story-level metadata, and collection-wide information. Specifically target the English and Irish/Scottish Gaelic story collections and individual story pages.",
)
