from dagster import asset, Config
from firecrawl import FirecrawlApp
import os
import json

class FirecrawlConfig(Config):
    url: str
    limit: int = 100

@asset
def scraped_curriculum_pages(context, config: FirecrawlConfig):
    # Use Infisical to get the API key if needed, or rely on env var
    # (assuming env var is injected via Locket/Infisical sidecar)
    api_key = os.getenv("FIRECRAWL_API_KEY")
    app = FirecrawlApp(api_key=api_key)
    
    context.log.info(f"Starting Firecrawl scrape for {config.url}...")
    
    # In a real scenario, we might use crawl_url for deep crawling
    crawl_result = app.scrape_url(
        config.url,
        params={'formats': ['markdown']}
    )
    
    # Save the result as a raw artifact
    output_path = f"/app/storage/data/scrapes/{config.url.replace('https://', '').replace('/', '_')}.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(crawl_result, f)
        
    context.log.info(f"Scrape complete. Saved to {output_path}")
    
    return output_path
