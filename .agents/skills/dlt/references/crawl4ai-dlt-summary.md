# crawl4ai → dlt Summary

**crawl4ai** is a sister scraper to Firecrawl with stronger
JavaScript-rendering support. It's useful for sites that don't
work well with the standard `FirecrawlSource` (e.g. SPAs that
require JS execution to render content).

## Pattern

```python
import dlt
import crawl4ai

@dlt.resource(name="scraped_pages")
def scraped_pages(urls: list[str]):
    for url in urls:
        # crawl4ai handles JS rendering, proxy rotation, etc.
        result = crawl4ai.run(url)
        yield {
            "url": url,
            "title": result.metadata.get("title"),
            "content": result.markdown,
            "scraped_at": result.scraped_at,
        }

pipeline = dlt.pipeline(destination="duckdb", dataset_name="scraped")
load_info = pipeline.run(scraped_pages(["https://example.com/page1", ...]))
```

## When to use crawl4ai vs Firecrawl

| | crawl4ai | Firecrawl |
|:--|:--|:--|
| **JS rendering** | Excellent (Playwright-based) | Good (headless browser) |
| **Speed** | Slower (full browser) | Faster (HTTP-first, JS on demand) |
| **Cost** | Free (self-hosted) | API credits |
| **Proxy rotation** | Built-in | Optional |
| **Best for** | SPAs, JS-heavy sites | Static + light JS sites |
| **KCG usage** | Rare (Firecrawl is primary) | Primary (NCCA, SEC, DES) |

## KCG usage

- The KCG stack uses **Firecrawl** as the primary scraper
  (`FirecrawlSource` in `dlt/`)
- `crawl4ai` is the fallback for JS-heavy sites that Firecrawl
  cannot handle
- The `cianfhoghlaim-leabharlann` spec uses crawl4ai for some Google
  Takeout HTML pages

## Reference

- The `crawl4ai-dlt.md` reference (80K, the full crawl4ai → dlt
  integration) was in `docs/dlt/` (deleted with the
  `sync-skills-from-docs` change)
- The `crawl4ai` skill for the upstream crawl4ai patterns
- The `firecrawl` skill for the Firecrawl alternative
