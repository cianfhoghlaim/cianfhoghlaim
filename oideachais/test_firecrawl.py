import os
from firecrawl import FirecrawlApp

api_key = os.getenv("FIRECRAWL_API_KEY")
app = FirecrawlApp(api_key=api_key)

try:
    from firecrawl.v2.types import ScrapeOptions
    scrape_opts = ScrapeOptions(formats=["markdown"])
except ImportError:
    scrape_opts = None

result = app.crawl(url="https://www.curriculumonline.ie/senior-cycle/senior-cycle-subjects/computer-science/", limit=1, max_discovery_depth=1)
if hasattr(result, 'data'):
    data = result.data
else:
    data = result.get('data', [])

for page in data:
    if hasattr(page, 'model_dump'):
        p = page.model_dump()
    elif hasattr(page, 'dict'):
        p = page.dict()
    else:
        p = page
    print(list(p.keys()))
    if 'metadata' in p:
        print("metadata keys:", list(p['metadata'].keys()))
        print("sourceURL:", p['metadata'].get('sourceURL'))
