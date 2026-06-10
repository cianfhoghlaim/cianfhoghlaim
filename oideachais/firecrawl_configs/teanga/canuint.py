
from firecrawl import FirecrawlApp
from pydantic import BaseModel

app = FirecrawlApp(api_key = "your-api-key")

class ExtractSchema(BaseModel):
    canuint_ie_endpoints: list[dict]
    transcription_formats: list[dict]
    crawl_extraction_schema: dict

result = app.agent(
    schema=ExtractSchema,
    prompt="i want to identify the key url endpoints, audio and transcription formats and relevant data and metadata in an extraction schema i will then use to scrape all the audio and transcripts from canuint.ie",
)
