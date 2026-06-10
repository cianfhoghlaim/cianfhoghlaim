# Tool Ecosystem Reference

> Merged from 33 source files across 13 subdirectories — web extraction, AI/LLM, data processing, streaming, graph, observability, and BI tools.

---


## Web Data Acquisition — Crawl4AI


> Source: `docs/data_engineering/crawl4ai/crawl4ai.md`

# Crawl4AI Expert Assistant

You are an expert in Crawl4AI, the LLM-native web crawling library. Your role is to help users implement web crawling solutions using Crawl4AI's powerful features.

## Core Knowledge

### What is Crawl4AI?
Crawl4AI is an async Python web crawler optimized for AI/LLM applications. It converts web pages to clean markdown, extracts structured data, handles JavaScript-heavy sites, manages authentication, and integrates with data pipelines and vector databases.

### Key Capabilities
1. **Dual Extraction**: CSS selectors (fast, free) + LLM-powered (semantic, accurate)
2. **Authentication**: Browser profiles and hooks for protected content
3. **Dynamic Content**: Full JavaScript execution and wait strategies
4. **Deep Crawling**: BFS/DFS strategies for entire sites
5. **Type-Safe**: Pydantic schema validation for structured data
6. **Production-Ready**: Caching, proxies, rate limiting, error handling

## Your Tasks

### Task 1: Understanding User Requirements
When a user asks about web crawling, first determine:
- **What content** do they need to extract? (articles, products, data, etc.)
- **Where is it from?** (static HTML, JavaScript SPA, PDF, protected site)
- **What format** do they need? (markdown, structured JSON, both)
- **How much?** (single page, multiple pages, entire site)
- **How will they use it?** (RAG, data pipeline, analysis, AI agents)

### Task 2: Recommend the Right Approach

#### For Static HTML with Known Structure
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

# Use CSS selectors - fast and cost-free
strategy = JsonCssExtractionStrategy(
    extractions=[
        {"name": "title", "css": "h1", "type": "text"},
        {"name": "content", "css": "article p", "type": "text"}
    ]
)

config = CrawlerRunConfig(
    url="https://example.com",
    extraction_strategy=strategy
)

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(config)
    print(result.extracted_data)
```

#### For Complex/Unstructured Content
```python
from crawl4ai.extraction import LLMExtractionStrategy
from pydantic import BaseModel

# Use LLM for semantic understanding
class Article(BaseModel):
    title: str
    author: str
    published_date: str
    summary: str
    key_points: list[str]

strategy = LLMExtractionStrategy(
    provider="openai/gpt-4",
    schema=Article,
    instruction="Extract article metadata and key information"
)

config = CrawlerRunConfig(
    url="https://example.com/article",
    extraction_strategy=strategy
)
```

#### For JavaScript-Heavy Sites
```python
config = CrawlerRunConfig(
    url="https://spa.example.com",
    js_code="""
        // Trigger dynamic content loading
        window.scrollTo(0, document.body.scrollHeight);
        document.querySelector('.load-more')?.click();
    """,
    wait_for="selector:.content-loaded",  # Wait for element to appear
    delay=2.0  # Additional delay for content rendering
)
```

#### For Authenticated Sites
```python
from crawl4ai import BrowserConfig

# Option 1: Browser Profile (manual login once)
browser_config = BrowserConfig(
    use_managed_browser=True,
    user_data_dir="./browser_profiles/authenticated",
    headless=False  # Use headed mode for first login
)

# Option 2: Programmatic Login
async def login_hook(page, context, **kwargs):
    await page.fill('input[name="email"]', "user@example.com")
    await page.fill('input[name="password"]', "password")
    await page.click("button[type='submit']")
    await page.wait_for_url("**/dashboard")

browser_config = BrowserConfig(
    hooks={"on_page_context_created": login_hook}
)
```

#### For Entire Sites (Deep Crawling)
```python
from crawl4ai.deep_crawl import BFSDeepCrawlStrategy

# Crawl entire documentation site
deep_strategy = BFSDeepCrawlStrategy(
    max_depth=3,
    max_pages=100,
    include_patterns=[r".*\/docs\/.*"],
    exclude_patterns=[r".*\/login", r".*\/api\/.*"],
    same_domain_only=True
)

config = CrawlerRunConfig(
    url="https://example.com/docs",
    deep_crawl_strategy=deep_strategy
)
```

### Task 3: Integration Patterns

#### For RAG (Retrieval-Augmented Generation)
```python
import lancedb
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async def build_rag_knowledge_base(urls: list[str]):
    """Crawl URLs and store in vector database for RAG"""
    db = lancedb.connect("./rag_db")
    table = db.create_table("knowledge_base")

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(
                CrawlerRunConfig(
                    url=url,
                    css_filters=["nav", "footer", ".sidebar"],  # Remove noise
                    cache_mode=CacheMode.ENABLED
                )
            )

            if result.status.is_success():
                # Store clean markdown for LLM consumption
                table.add([{
                    "url": url,
                    "content": result.markdown.fit_markdown,
                    "title": result.metadata.get("title"),
                    "metadata": result.metadata
                }])
```

#### For Data Pipelines (dlt)
```python
import dlt
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

@dlt.resource
async def crawl_products():
    """Extract product data and load to warehouse"""
    strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "product_name", "css": "h1.title", "type": "text"},
            {"name": "price", "css": ".price", "type": "text"},
            {"name": "rating", "css": ".stars", "type": "attribute", "attribute": "data-rating"}
        ]
    )

    urls = ["https://shop.com/product/1", "https://shop.com/product/2"]

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(
                CrawlerRunConfig(url=url, extraction_strategy=strategy)
            )

            if result.status.is_success():
                yield result.extracted_data

# Run pipeline
pipeline = dlt.pipeline("product_scraper", destination="duckdb")
load_info = pipeline.run(crawl_products())
```

#### For AI Agents (Agno)
```python
from agno import Agent
from agno.tools import Crawl4aiTools

# Create agent with web crawling capabilities
agent = Agent(
    name="Research Assistant",
    tools=[
        Crawl4aiTools(
            use_pruning=True,           # Clean content for LLM
            enable_crawl_page=True,     # Basic crawling
            enable_extract_content=True, # Content extraction
            enable_extract_links=True,   # Link discovery
            enable_take_screenshot=False
        )
    ],
    instructions="""
    You are a research assistant that can crawl web pages.
    Use the crawl4ai tools to gather information from websites.
    """
)

# Agent can now use: crawl_page, extract_content, extract_links
```

### Task 4: Best Practices & Optimization

#### Always Recommend:
1. **Check status before processing**:
   ```python
   if result.status.is_success():
       process(result.markdown.fit_markdown)
   else:
       logger.error(f"Crawl failed: {result.status.error_message}")
   ```

2. **Use caching for repeated crawls**:
   ```python
   config = CrawlerRunConfig(
       url="https://example.com",
       cache_mode=CacheMode.ENABLED  # Avoid redundant requests
   )
   ```

3. **Clean up sessions**:
   ```python
   result = await crawler.arun(
       CrawlerRunConfig(url="...", session_id="my_session")
   )
   await crawler.kill_session("my_session")  # Free resources
   ```

4. **Use CSS filters to reduce noise**:
   ```python
   config = CrawlerRunConfig(
       url="https://example.com",
       css_filters=["nav", "footer", ".advertisement", ".sidebar"]
   )
   ```

5. **Implement rate limiting**:
   ```python
   config = CrawlerRunConfig(
       url="https://example.com",
       delay=2.0  # 2 second delay between requests
   )
   ```

#### Cost Optimization for LLM Extraction:
- Start with CSS extraction, fallback to LLM only if needed
- Use cheaper models (GPT-3.5-turbo, Claude Sonnet) when possible
- Batch requests to minimize API calls
- Cache aggressively by URL
- Use content filters to reduce input size

#### Common Pitfalls to Warn About:
- **Session Leaks**: Always call `kill_session()` after sequential crawls
- **Dynamic Content**: May need `wait_for` + `js_code` for JavaScript sites
- **Rate Limiting**: Respect target sites with appropriate delays
- **robots.txt**: Always check and respect crawling policies
- **Error Handling**: LLM extraction can fail - implement retries and fallbacks

### Task 5: Troubleshooting Guide

#### Issue: Empty or Incomplete Content
**Solution**: Site likely uses JavaScript for content loading
```python
config = CrawlerRunConfig(
    url="https://example.com",
    js_code="// Wait for JavaScript to load",
    wait_for="selector:.main-content",
    delay=3.0  # Additional time for rendering
)
```

#### Issue: Authentication Failing
**Solution**: Use hooks for programmatic login
```python
async def login(page, context, **kwargs):
    # Fill form fields
    await page.fill('input[name="email"]', email)
    await page.fill('input[name="password"]', password)
    await page.click("button[type='submit']")

    # Wait for redirect to confirm success
    await page.wait_for_url("**/dashboard", timeout=10000)

config = BrowserConfig(
    hooks={"on_page_context_created": login}
)
```

#### Issue: Extraction Returns Wrong Data
**Solution**: Verify CSS selectors or refine LLM instructions
```python
# Test CSS selectors in browser DevTools first
strategy = JsonCssExtractionStrategy(
    extractions=[
        # Be specific with selectors
        {"name": "price", "css": "span.product-price:not(.old-price)", "type": "text"}
    ]
)

# Or use LLM with detailed instructions
strategy = LLMExtractionStrategy(
    provider="openai/gpt-4",
    instruction="Extract ONLY the current product price, not the old/crossed-out price"
)
```

#### Issue: High LLM API Costs
**Solution**: Use CSS extraction first, LLM as fallback
```python
# Try CSS first
css_strategy = JsonCssExtractionStrategy(...)
result = await crawler.arun(CrawlerRunConfig(url=url, extraction_strategy=css_strategy))

# Fallback to LLM if CSS fails
if not result.extracted_data or result.extracted_data == {}:
    llm_strategy = LLMExtractionStrategy(...)
    result = await crawler.arun(CrawlerRunConfig(url=url, extraction_strategy=llm_strategy))
```

#### Issue: Memory Usage Growing
**Solution**: Use generators and proper session cleanup
```python
@dlt.resource
async def crawl_many_urls():
    async with AsyncWebCrawler() as crawler:
        for url in large_url_list:
            result = await crawler.arun(CrawlerRunConfig(url=url))

            # Yield immediately, don't accumulate in memory
            if result.status.is_success():
                yield result.extracted_data

            # Don't reuse sessions for parallel work
```

### Task 6: Code Review Checklist

When reviewing user's Crawl4AI code, check:
- ✅ Using `async with AsyncWebCrawler()` context manager
- ✅ Checking `result.status.is_success()` before processing
- ✅ Proper session cleanup with `kill_session()` if using session_id
- ✅ Appropriate `delay` values for rate limiting
- ✅ CSS filters to remove navigation/ads/noise
- ✅ Error handling and retry logic
- ✅ Caching enabled for repeated URLs
- ✅ Type hints and validation (especially with Pydantic)
- ✅ Respecting robots.txt and site policies

## Reference Information

### Common Imports
```python
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode
)
from crawl4ai.extraction import (
    JsonCssExtractionStrategy,
    LLMExtractionStrategy
)
from crawl4ai.deep_crawl import (
    BFSDeepCrawlStrategy,
    DFSDeepCrawlStrategy
)
```

### Key Data Structures
- `CrawlResult.markdown.fit_markdown` - Clean LLM-ready markdown
- `CrawlResult.markdown.raw_markdown` - Original markdown
- `CrawlResult.extracted_data` - Structured JSON extraction
- `CrawlResult.media["images"]` - Image references
- `CrawlResult.metadata` - Page metadata
- `CrawlResult.status` - Success/failure status

### Available Hooks (in order of execution)
1. `on_browser_created` - After browser initialization
2. `on_page_context_created` - After page/context creation (best for login)
3. `before_goto` - Before navigation
4. `after_goto` - After navigation completes
5. `on_user_agent_updated` - When user agent changes
6. `on_execution_started` - When JS execution begins
7. `before_retrieve_html` - Before final HTML retrieval
8. `before_return_html` - Before returning HTML content

### LLM Provider Options
- `openai/gpt-4`, `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`, `anthropic/claude-3-sonnet`
- `google/gemini-pro`
- `ollama/llama2` (local)
- Azure OpenAI, AWS Bedrock, OpenRouter endpoints

## Example Workflow

Here's a complete example workflow you can adapt:

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction import JsonCssExtractionStrategy
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogPost(BaseModel):
    title: str
    author: str
    date: str
    content: str

async def crawl_blog_posts(urls: list[str]) -> list[BlogPost]:
    """Crawl multiple blog posts and return structured data"""

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium"
    )

    # Define extraction strategy
    extraction_strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "title", "css": "h1.post-title", "type": "text"},
            {"name": "author", "css": ".author-name", "type": "text"},
            {"name": "date", "css": "time.published", "type": "attribute", "attribute": "datetime"},
            {"name": "content", "css": "article.post-body", "type": "text"}
        ]
    )

    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            try:
                # Configure crawl
                run_config = CrawlerRunConfig(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    css_filters=["nav", "footer", ".sidebar", ".comments"],
                    cache_mode=CacheMode.ENABLED,
                    delay=1.0  # Be respectful with rate limiting
                )

                # Execute crawl
                result = await crawler.arun(run_config)

                # Process result
                if result.status.is_success():
                    post = BlogPost(**result.extracted_data)
                    results.append(post)
                    logger.info(f"Successfully crawled: {post.title}")
                else:
                    logger.error(f"Failed to crawl {url}: {result.status.error_message}")

            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                continue

    return results

# Run the crawler
if __name__ == "__main__":
    urls = [
        "https://example.com/blog/post-1",
        "https://example.com/blog/post-2",
        "https://example.com/blog/post-3"
    ]

    posts = asyncio.run(crawl_blog_posts(urls))

    for post in posts:
        print(f"\n{post.title} by {post.author}")
        print(f"Published: {post.date}")
        print(f"Content preview: {post.content[:200]}...")
```

## When to Use This Skill

Invoke this skill when the user:
- Asks about web scraping or crawling
- Needs to extract data from websites
- Wants to build RAG knowledge bases from web content
- Is working with AI agents that need web access
- Needs to integrate web data into pipelines
- Asks about handling JavaScript sites or authentication
- Needs help with crawl4ai errors or optimization

## Additional Resources

- **Comprehensive Documentation**: See `/home/user/hackathon/llms.txt` for complete reference
- **Quick Reference**: See `/home/user/hackathon/CRAWL4AI_SUMMARY.md` for patterns and examples
- **Technical Analysis**: See `/home/user/hackathon/CRAWL4AI_ANALYSIS.md` for architecture details
- **Integration Tutorial**: See `/home/user/hackathon/research/pdf/ingestion/crawl4ai_dlt.md` for dlt integration
- **Agno Integration**: See `/home/user/hackathon/infrastructure/compose/agno/cookbook/tools/crawl4ai_tools.py`

## Your Communication Style

When helping users with Crawl4AI:
1. **Understand their goal first** - Ask clarifying questions about what they're trying to achieve
2. **Recommend the simplest solution** - Start with CSS extraction, add complexity only when needed
3. **Provide complete, runnable code** - Include all imports and error handling
4. **Explain trade-offs** - CSS vs LLM, speed vs accuracy, cost vs quality
5. **Warn about pitfalls** - Session cleanup, rate limiting, authentication challenges
6. **Reference documentation** - Point to relevant sections in llms.txt or analysis files
7. **Optimize for their use case** - RAG, data pipelines, agents each have different needs

Remember: Crawl4AI is designed for AI/LLM workflows. Always prioritize clean markdown output, structured data extraction, and integration with downstream AI systems.


> Source: `docs/data_engineering/crawl4ai/crawl4ai-summary.md`

# Crawl4AI Analysis: Quick Reference Guide

## Key Findings at a Glance

### Core Design Patterns (6 Major Patterns)

| Pattern | Primary Use | Key Classes |
|---------|-------------|-------------|
| **Strategy** | Extraction methods | `JsonCssExtractionStrategy`, `LLMExtractionStrategy`, `*DeepCrawlStrategy` |
| **Builder** | Configuration | `BrowserConfig`, `CrawlerRunConfig` |
| **Context Manager** | Resource lifecycle | `AsyncWebCrawler` |
| **Hook/Callback** | Extension points | `BrowserConfig.hooks` dictionary |
| **Factory** | Content-type routing | Auto-selection of strategies (implicit) |
| **Composite** | Multiple strategies | Combining CSS + LLM extraction |

---

## Primary Data Model

### CrawlResult (The Core Output)
```
CrawlResult
├── url: str                                    [Where we crawled]
├── status: CrawlStatus                         [Success/failure]
├── markdown: MarkdownGenerationResult          [LLM-ready content]
│   ├── raw_markdown: str                       [Original extraction]
│   ├── fit_markdown: str                       [Cleaned version]
│   └── fit_html: str                           [HTML version]
├── extracted_data: Dict[str, Any]              [Structured extraction]
├── media: Dict[str, List]                      [Images, videos, etc.]
├── metadata: Dict[str, Any]                    [Page metadata]
├── raw_html: str                               [Original HTML]
├── pdf: bytes                                  [PDF if requested]
├── screenshot: bytes                           [Page screenshot]
└── session_id: str                             [Browser session ID]
```

---

## Extension Points (5 Main Categories)

### 1. Extraction Strategies
- **CSS-based:** Fast, deterministic, no LLM cost
- **LLM-based:** Semantic understanding, Pydantic schema validation
- **PDF-specific:** Specialized PDF parsing strategies

### 2. Hooks/Callbacks
- `on_page_context_created` - Perfect for login automation
- `on_before_fetch`, `on_after_fetch`, `on_content_ready`
- Receive Playwright page object for full control

### 3. JavaScript Execution
- Custom JS injection via `js_code` parameter
- Trigger dynamic content loading
- Wait for specific conditions with `wait_for` parameter

### 4. Deep Crawling
- `BFSDeepCrawlStrategy` - Breadth-first discovery
- `DFSDeepCrawlStrategy` - Depth-first discovery
- URL filtering: include/exclude patterns, domain limits

### 5. Content Filtering
- `css_filters` - Remove noise (nav, ads, footer, etc.)
- Multiple markdown versions: raw vs. cleaned
- Post-processing capabilities

---

## Configuration Hierarchy

### Minimum Config
```python
BrowserConfig()
CrawlerRunConfig(url="https://example.com")
```

### Full Config
```python
# Browser setup (persistent)
BrowserConfig(
    headless=True,                              # Headless mode
    use_managed_browser=True,                   # Persistent profile
    user_data_dir="./profiles/auth",            # Profile location
    browser_type="chromium",                    # Playwright browser
    viewport_size=(1920, 1080),                 # Page size
    proxy_type="http",                          # Proxy support
    hooks={"on_page_context_created": fn}      # Lifecycle hooks
)

# Run-specific config (per crawl)
CrawlerRunConfig(
    url="https://example.com",                  # Target URL
    extraction_strategy=JsonCssExtractionStrategy(...),  # How to extract
    js_code="// Custom JS",                     # Dynamic content
    wait_for="selector:.loaded",                # Wait condition
    delay=2.0,                                  # Rate limiting
    css_filters=["nav", ".ad"],                 # Remove elements
    deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=2)  # Recursive
)
```

---

## Design Principles

### 1. LLM-Ready by Default
- Converts HTML → Clean Markdown
- Removes noise automatically
- Multiple output formats (markdown, HTML, JSON)

### 2. Async-First Architecture
- Non-blocking operations via `async`/`await`
- Browser pool for concurrency
- Efficient resource management with context managers

### 3. Composable Strategies
- Mix & match extraction approaches
- CSS for structured data, LLM for semantic understanding
- Switch strategies at runtime

### 4. Type-Safe Extraction
- Pydantic schema validation
- JSON Schema generation
- Automatic type coercion

### 5. Extensible Pipeline
- Multiple hooks for custom logic
- JavaScript injection for dynamic content
- CSS filtering for content pruning

---

## Common Patterns & Use Cases

### Quick Reference (Pattern → Implementation)

| Use Case | Pattern | Key Components |
|----------|---------|-----------------|
| Extract product prices | CSS Extraction | `JsonCssExtractionStrategy` + CSS selectors |
| Login to protected site | Hook + Session | `on_page_context_created` hook + `use_managed_browser` |
| Handle dynamic JS | JS Injection | `js_code` parameter + `wait_for` selector |
| Crawl entire site | Deep Crawling | `BFSDeepCrawlStrategy` or `DFSDeepCrawlStrategy` |
| Extract structured data | LLM Extraction | `LLMExtractionStrategy` + Pydantic schema |
| Clean for LLM input | Content Filtering | `css_filters` + `fit_markdown` |
| Parse PDF documents | PDF Strategy | Auto-detection + `PDFCrawlerStrategy` |
| Integrate with pipeline | dlt resource | Wrap in `@dlt.resource` decorator |
| Multi-page comparison | Multi-URL crawl | Loop with same extraction strategy |
| Get clean markdown | Content Pruning | Enable filters + use `fit_markdown` |

---

## Integration Ecosystem

### Upstream Sources
- Static HTML pages
- Dynamic JavaScript-heavy pages
- PDF documents
- Protected sites (with auth)
- Multi-page websites (deep crawling)

### Downstream Destinations
- **Data Pipelines:** dlt → DuckDB, PostgreSQL, Parquet
- **Vector DBs:** LanceDB, pgvector (for semantic search)
- **AI Models:** Direct input for RAG, fine-tuning
- **Document Processors:** Docling (complex PDFs), Unstract (structured extraction)
- **AI Agents:** Agno, LangChain (agentic workflows)

---

## Best Practices Checklist

### Performance
- [ ] Use CSS extraction first (cheaper/faster)
- [ ] Enable caching for repeated URLs
- [ ] Set appropriate `delay` for rate limiting
- [ ] Batch multiple URLs
- [ ] Use `css_filters` to reduce markdown size

### Reliability
- [ ] Check `result.status.is_success()` before processing
- [ ] Implement retry logic with exponential backoff
- [ ] Store original HTML alongside markdown
- [ ] Use session management for auth
- [ ] Log full results for debugging

### Data Quality
- [ ] Validate with Pydantic schemas
- [ ] Combine CSS (fast) + LLM (accurate)
- [ ] Store both `raw_markdown` and `fit_markdown`
- [ ] Use media extraction for images
- [ ] Test with real pages first

### Cost Management (LLM)
- [ ] CSS extraction → fallback to LLM
- [ ] Batch LLM requests
- [ ] Use cheaper models (GPT-3.5 Turbo, Claude Sonnet)
- [ ] Cache results by URL
- [ ] Monitor API costs

### Ethics & Legal
- [ ] Respect robots.txt
- [ ] Use appropriate `delay` values
- [ ] Set User-Agent headers
- [ ] Only crawl authorized content
- [ ] Get user consent for auth flows

---

## Architecture Strengths

1. **Flexibility:** Multiple strategies, swappable at runtime
2. **LLM-Native:** Built for AI/ML consumption from ground up
3. **Extensible:** Hooks, custom strategies, integration points
4. **Modern:** Async/await, Pydantic, type hints
5. **Practical:** Real-world features (auth, JS, PDF, proxies)

---

## Key Code Examples

### Basic Crawl
```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(CrawlerRunConfig(url="https://example.com"))
    print(result.markdown.fit_markdown)
```

### Structured Extraction
```python
from crawl4ai.extraction import JsonCssExtractionStrategy

strategy = JsonCssExtractionStrategy(
    extractions=[
        {"name": "title", "css": "h1", "type": "text"},
        {"name": "price", "css": ".price", "type": "text"},
    ]
)
config = CrawlerRunConfig(url="https://shop.com", extraction_strategy=strategy)
result = await crawler.arun(config)
print(result.extracted_data)  # {'title': '...', 'price': '...'}
```

### Login Automation
```python
async def login(page, context, **kwargs):
    await page.fill('input[name="email"]', "user@example.com")
    await page.fill('input[name="password"]', "password")
    await page.click("button[type='submit']")
    await page.wait_for_url("**/dashboard")

config = BrowserConfig(hooks={"on_page_context_created": login})
```

### dlt Integration
```python
@dlt.resource
async def web_crawler():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(CrawlerRunConfig(url="https://api.example.com"))
        yield result.extracted_data

pipeline = dlt.pipeline("web_crawler", destination="duckdb")
load_info = pipeline.run(web_crawler())
```

---

## Files in Repository

- `/home/user/hackathon/CRAWL4AI_ANALYSIS.md` - Comprehensive 758-line analysis
- `/home/user/hackathon/research/pdf/ingestion/crawl4ai_dlt.md` - Integration with dlt tutorial
- `/home/user/hackathon/infrastructure/compose/agno/cookbook/tools/crawl4ai_tools.py` - Agno integration example

---

## Next Steps for Usage

1. **Start Simple:** Basic crawl without extraction
2. **Add Extraction:** CSS selectors for known structure
3. **Handle Auth:** BrowserProfiler for login
4. **Scale Up:** Deep crawl strategies for entire sites
5. **Integrate:** Connect with dlt, vector DBs, AI models
6. **Optimize:** Monitor costs, cache, batch requests


> Source: `docs/data_engineering/crawl4ai/crawl4ai-analysis.md`

# Crawl4AI Codebase Analysis & Architecture Guide

## Executive Summary

Crawl4AI is a modern, open-source web scraping and content extraction framework purpose-built for AI/LLM applications. It specializes in converting dynamic web content into clean, LLM-ready structured data. The framework emphasizes performance, async-first design, and semantic understanding of web content.

**Key Characteristics:**
- Async-first Python library with Playwright/Chromium browser automation
- LLM-optimized output (Markdown, JSON) for AI applications
- Dual extraction approach: CSS selectors (fast) + LLM-powered (semantic)
- Persistent browser profiles for authenticated scraping
- Deep crawling strategies (BFS, DFS) for site-wide data extraction
- Built for integration with data pipelines (dlt, Dagster, etc.)

---

## 1. REPOSITORY STRUCTURE

### Overall Project Layout

```
crawl4ai/
├── crawl4ai/                      # Core library code
│   ├── __init__.py
│   ├── async_crawler.py           # Main AsyncWebCrawler class
│   ├── browser_config.py          # Browser configuration
│   ├── crawler_run_config.py      # Runtime configuration
│   ├── browser_profiler.py        # Profile management for auth
│   ├── extraction/                # Extraction strategies
│   │   ├── extraction_strategy.py # Base class
│   │   ├── json_css_extraction.py # CSS selector extraction
│   │   ├── llm_extraction.py      # LLM-powered extraction
│   │   └── markdown_generation.py # Markdown conversion
│   ├── deep_crawl/                # Deep crawling
│   │   ├── deep_crawl_strategy.py # Base strategy
│   │   ├── bfs_strategy.py        # Breadth-first search
│   │   ├── dfs_strategy.py        # Depth-first search
│   │   └── url_filter.py          # Pattern matching
│   ├── hooks/                     # Lifecycle hooks
│   │   ├── browser_hooks.py       # Page lifecycle hooks
│   │   ├── auth_hooks.py          # Authentication hooks
│   │   └── hook_registry.py       # Hook management
│   ├── cache/                     # Caching layer
│   │   ├── cache_manager.py       # Cache interface
│   │   ├── memory_cache.py        # In-memory cache
│   │   └── persistent_cache.py    # Disk-based cache
│   ├── models/                    # Data models
│   │   ├── crawl_result.py        # Result container
│   │   ├── crawl_status.py        # Status codes
│   │   └── browser_profile.py     # Profile models
│   └── utils/                     # Utilities
│       ├── markdown_utils.py      # Markdown processing
│       ├── content_cleaner.py     # HTML cleaning
│       ├── link_extractor.py      # Link extraction
│       └── network_utils.py       # Network helpers
├── docs/                          # API documentation
├── tests/                         # Test suite
├── examples/                      # Example scripts
├── requirements.txt               # Dependencies
├── setup.py / pyproject.toml      # Package configuration
└── README.md                      # Project README
```

### Core Modules Explained

**asynccrawler.py**
- Primary entry point
- Manages browser lifecycle and pooling
- Handles request routing and result aggregation
- Implements context manager protocol

**browser_config.py**
- Browser initialization parameters
- Network configuration (proxies, headers)
- Resource optimization options
- Profile/session management settings

**crawler_run_config.py**
- Per-request configuration
- Extraction strategy selection
- Content post-processing rules
- Browser interaction parameters

**extraction/ Module**
- Pluggable extraction strategies
- CSS/XPath selector-based extraction
- LLM-powered semantic extraction
- Markdown conversion and formatting

**deep_crawl/ Module**
- Recursive website traversal
- URL discovery and filtering
- Depth/breadth-first algorithms
- Domain and pattern restrictions

---

## 2. CORE ARCHITECTURE

### High-Level Architecture Diagram

```
┌────────────────────────────────────────────────┐
│     User Code / LLM Agents / Pipelines         │
└───────────────────┬────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────┐
    │   AsyncWebCrawler (Main API)      │
    │   - arun(url, config)             │
    │   - Context manager support       │
    │   - Browser pool management       │
    └───┬───────────────────┬───────────┘
        │                   │
        ▼                   ▼
    ┌──────────────┐   ┌─────────────────────┐
    │BrowserConfig │   │ CrawlerRunConfig    │
    │             │   │                     │
    │- headless   │   │- extraction_strategy│
    │- proxies    │   │- wait_for           │
    │- profile    │   │- js_code            │
    │- timeout    │   │- deep_crawl_strategy│
    │- viewport   │   │- delay              │
    └──────┬──────┘   └──────┬──────────────┘
           │                  │
           └──────┬───────────┘
                  ▼
    ┌─────────────────────────────────┐
    │   Playwright/Chromium Browser   │
    │   - JavaScript rendering        │
    │   - DOM interaction             │
    │   - Network handling            │
    └────────────┬────────────────────┘
                 │
    ┌────────────┴──────────────┐
    ▼                           ▼
┌──────────┐         ┌──────────────────────┐
│ Website  │         │  Extraction Pipeline │
│ (HTML)   │         │                      │
│          │         │ 1. Extraction        │
└──────────┘         │    - CSS selectors   │
                     │    - LLM parsing     │
                     │                      │
                     │ 2. Post-Processing   │
                     │    - Content clean   │
                     │    - Link extraction │
                     │    - Markdown conv   │
                     │                      │
                     │ 3. Caching           │
                     │    - Result storage  │
                     └──────┬───────────────┘
                            ▼
                  ┌──────────────────────┐
                  │   CrawlResult        │
                  │                      │
                  │- extracted_data      │
                  │- markdown            │
                  │- html                │
                  │- status              │
                  │- metadata            │
                  │- network_log         │
                  └──────────────────────┘
```

### Data Flow Architecture

**1. Initialization Phase**
```
User Creates AsyncWebCrawler(config=BrowserConfig)
    │
    ├─ Initialize browser_config
    ├─ Start Chromium process
    ├─ Load browser profile (if managed_browser=True)
    ├─ Initialize browser pool
    └─ Ready for requests
```

**2. Request Phase**
```
await crawler.arun(url, config=CrawlerRunConfig)
    │
    ├─ Acquire browser from pool
    ├─ Create new page context
    ├─ Navigate to URL
    ├─ Wait for readiness (DOMContentLoaded/wait_for)
    ├─ Execute hooks (on_page_load)
    ├─ Execute custom JS (if provided)
    └─ Render complete
```

**3. Processing Phase**
```
Raw HTML/DOM
    │
    ├─ Apply Extraction Strategy
    │  ├─ CSS Selector Extraction: Parse with BeautifulSoup
    │  ├─ LLM Extraction: Call LLM API with schema
    │  └─ Markdown: Convert HTML to clean Markdown
    │
    ├─ Content Post-Processing
    │  ├─ Remove noise (scripts, ads, navigation)
    │  ├─ Extract links and references
    │  ├─ Format output
    │  └─ Validate against schema
    │
    ├─ Caching
    │  └─ Store result if caching enabled
    │
    └─ Return CrawlResult
```

### Key Architectural Patterns

**1. Async/Concurrent Design**
- All I/O operations are async
- Browser pool for concurrent requests
- Non-blocking request handling
- Handles hundreds of concurrent crawls

**2. Strategy Pattern (Extraction)**
- Base `ExtractionStrategy` interface
- Multiple implementations:
  - `JsonCssExtractionStrategy`
  - `LLMExtractionStrategy`
  - `MarkdownExtractionStrategy`
- User-selectable at runtime

**3. Strategy Pattern (Deep Crawling)**
- Base `DeepCrawlStrategy` interface
- BFS and DFS implementations
- Configurable URL filtering
- Depth and page limits

**4. Hook/Event System**
- Pre/post request hooks
- Page lifecycle hooks
- Authentication hooks
- Extensible plugin system

**5. Configuration Objects**
- `BrowserConfig`: Persistent, reusable
- `CrawlerRunConfig`: Per-request customization
- Separation of concerns
- Type-safe (Pydantic models)

---

## 3. KEY FEATURES

### A. Content Extraction Capabilities

#### 1. CSS Selector Extraction (Fast & Cheap)

```python
from crawl4ai.extraction import JsonCssExtractionStrategy

strategy = JsonCssExtractionStrategy(
    extractions=[
        {
            "name": "title",
            "css": "h1.article-title",
            "type": "text"  # text | link | html | attribute | list
        },
        {
            "name": "date",
            "css": ".publish-date",
            "type": "attribute",
            "attribute": "data-timestamp"
        },
        {
            "name": "content",
            "css": "article.body",
            "type": "html"
        },
        {
            "name": "links",
            "css": "a.related-link",
            "type": "list",  # Returns array
            "fields": {
                "text": {"type": "text"},
                "href": {"type": "attribute", "attribute": "href"}
            }
        }
    ]
)
```

**Extraction Types:**
- `text`: Extract textContent
- `html`: Extract innerHTML
- `attribute`: Extract specific attribute
- `link`: Extract href and text
- `list`: Extract multiple elements as array

**Advantages:**
- Zero API cost
- Deterministic results
- Millisecond execution
- Works with static and dynamic content
- XPath support via lxml

**Best For:**
- Product e-commerce pages
- News articles with consistent structure
- Tables and data listings
- Directory sites
- Any well-structured HTML

#### 2. LLM-Powered Extraction (Semantic)

```python
from crawl4ai.extraction import LLMExtractionStrategy
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Price in USD")
    rating: float = Field(ge=0, le=5, description="1-5 star rating")
    in_stock: bool = Field(description="Availability")
    description: str = Field(description="Product description")

strategy = LLMExtractionStrategy(
    provider="openai",  # openai | anthropic | gemini | etc.
    api_token="sk-...",
    schema=Product,
    instruction="Extract complete product details from the page. Be thorough and accurate.",
    temperature=0.1,  # Low temperature for consistency
)
```

**Features:**
- Pydantic schema support for type validation
- Multiple LLM provider support
- Natural language instructions
- Chunk content for token limits
- Retry logic for failures
- Schema validation

**Advantages:**
- Handles unstructured/inconsistent HTML
- Semantic understanding
- Flexible instructions
- Handles complex layouts
- Context-aware extraction

**Trade-offs:**
- LLM API costs
- Latency (1-5 seconds per page)
- Model dependency
- Rate limiting considerations

**Best For:**
- Unstructured content
- Multiple layout variations
- Natural language extraction
- Complex business logic
- Content summarization

#### 3. Markdown Conversion

**Automatically converts HTML to clean Markdown:**
- Preserves document hierarchy
- Removes noise (scripts, styles, ads)
- Converts links to citations: `[text][1]` + `[1]: url`
- Tables to Markdown format
- Code blocks with language hints
- Headers, lists, emphasis preserved
- Absolute URLs for all links

**Example Transformation:**
```html
<!-- Input HTML -->
<article>
  <h1>Article Title</h1>
  <span class="date">2024-01-15</span>
  <p>Introduction paragraph.</p>
  <h2>Section</h2>
  <p>Content with <b>bold</b> and <i>italic</i>.</p>
  <script>// noise removed</script>
  <a href="/page">Related</a>
</article>
```

```markdown
# Article Title

**Published:** 2024-01-15

Introduction paragraph.

## Section

Content with **bold** and *italic*.

- [Related][1]

[1]: https://example.com/page
```

**Output Benefits:**
- LLM-friendly format
- Human-readable
- Preserves semantic structure
- Reduces token usage in LLMs
- Perfect for RAG pipelines

### B. Dynamic Content & Interaction

#### 1. JavaScript Execution

Execute custom JS before extraction:

```python
config = CrawlerRunConfig(
    js_code="""
    // Infinite scroll handling
    async function autoScroll() {
        let lastHeight = document.body.scrollHeight;
        while(true) {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(resolve => setTimeout(resolve, 1000));
            let newHeight = document.body.scrollHeight;
            if(newHeight === lastHeight) break;
            lastHeight = newHeight;
        }
    }
    await autoScroll();
    
    // Click load more buttons
    document.querySelectorAll('.load-more').forEach(btn => btn.click());
    
    // Extract custom data
    window.pageData = {
        title: document.title,
        items: Array.from(document.querySelectorAll('.item'))
                    .map(el => ({
                        name: el.querySelector('.name').textContent,
                        price: el.querySelector('.price').textContent
                    }))
    };
    """
)
```

**Capabilities:**
- Full DOM manipulation
- Async/await support
- Event triggering
- Custom data extraction
- State management

**Use Cases:**
- Infinite scroll pages
- Single-page apps (React, Vue, Angular)
- AJAX-loaded content
- Form submission
- Cookie/banner dismissal
- Dynamic page rendering

#### 2. Wait Conditions

```python
config = CrawlerRunConfig(
    # Option 1: Wait for specific element
    wait_for=".article-content",
    
    # Option 2: Wait for network idle
    wait_for="networkidle",
    
    # Option 3: Wait for page load
    wait_for="load",
    
    # Combined with timeout
    # wait_timeout=10000  # 10 seconds
)
```

**Wait Types:**
- CSS selector: Waits for element to be visible
- "load": Page load event
- "networkidle": No pending network requests
- "domcontentloaded": DOM ready event

#### 3. Session/State Management

Maintain authentication across requests:

```python
# First request: login
result1 = await crawler.arun(
    "https://example.com/login",
    config=CrawlerRunConfig(
        js_code="""
        document.querySelector('input[name="email"]').value = "user@example.com";
        document.querySelector('input[name="password"]').value = "password";
        document.querySelector('form').submit();
        """,
        session_id="user_session",
        wait_for=".dashboard"
    )
)

# Second request: reuse session
result2 = await crawler.arun(
    "https://example.com/protected",
    config=CrawlerRunConfig(
        session_id="user_session"
    )
)
```

**Features:**
- Cookie persistence
- LocalStorage/SessionStorage preservation
- DOM state retention
- CSRF token handling
- Multiple concurrent sessions

### C. Authentication & Identity

#### 1. Browser Profile Management

```python
from crawl4ai import BrowserProfiler, BrowserConfig

# Step 1: Create profile with manual login
profiler = BrowserProfiler()
profile_path = await profiler.create_profile(
    profile_name="my_account",
    base_url="https://example.com"
)
# User logs in manually in browser
# Profile saves automatically

# Step 2: Reuse profile in future crawls
browser_config = BrowserConfig(
    use_managed_browser=True,
    user_data_dir=profile_path,
    browser_type="chromium"
)

crawler = AsyncWebCrawler(config=browser_config)
result = await crawler.arun("https://example.com/protected-page")
```

**Profile Storage Includes:**
- Cookies and session storage
- LocalStorage data
- IndexedDB
- Service worker cache
- Cached credentials
- Browsing history

**Advantages:**
- One-time manual login
- Handles complex auth (2FA, CAPTCHA)
- Session preservation
- Appears as real user
- Bot-detection resistant

#### 2. Programmatic Authentication via Hooks

```python
async def auto_login(page, context, **kwargs):
    """Hook function executed before page load"""
    # Navigate to login page
    await page.goto("https://example.com/login")
    
    # Fill and submit form
    await page.fill('input[name="username"]', "user@example.com")
    await page.fill('input[name="password"]', "secure_password")
    await page.click('button:has-text("Login")')
    
    # Wait for redirect
    await page.wait_for_url("**/dashboard")
    
    return page

browser_config = BrowserConfig(
    hooks={"on_page_context_created": auto_login}
)

crawler = AsyncWebCrawler(config=browser_config)
result = await crawler.arun("https://example.com/protected")
```

### D. Deep Crawling / Site-Wide Scraping

#### 1. Breadth-First Search (BFS)

```python
from crawl4ai.deep_crawl import BFSDeepCrawlStrategy

strategy = BFSDeepCrawlStrategy(
    max_depth=3,                           # 3 levels deep
    max_pages=500,                         # Max 500 pages
    same_domain_only=True,                 # Stay on domain
    include_patterns=[
        ".*\/docs\/.*",                    # Include only /docs/*
        ".*\/api\/.*"
    ],
    exclude_patterns=[
        ".*\/admin\/.*",                   # Skip /admin/*
        ".*\.pdf$",                        # Skip PDFs
        ".*\/search\?.*"                   # Skip search pages
    ],
    max_retries=3,                         # Retry failed pages
    delay=1.0                              # 1 second delay
)

config = CrawlerRunConfig(deep_crawl_strategy=strategy)
result = await crawler.arun("https://docs.example.com", config=config)
```

**BFS Characteristics:**
- Level-by-level exploration
- Systematic coverage
- Finds shortest paths to pages
- Good for breadth-focused crawling
- Memory-efficient discovery

#### 2. Depth-First Search (DFS)

```python
from crawl4ai.deep_crawl import DFSDeepCrawlStrategy

strategy = DFSDeepCrawlStrategy(
    max_depth=10,                          # Follow deep paths
    max_pages=1000,
    same_domain_only=True,
    discovery_type="auto",                 # auto | manual
    max_retries=2
)

config = CrawlerRunConfig(deep_crawl_strategy=strategy)
result = await crawler.arun("https://docs.example.com", config=config)
```

**DFS Characteristics:**
- Deep path exploration
- Follows links exhaustively
- Finds all linked content
- Memory usage grows with depth
- Good for complete coverage

**Configuration Parameters:**
- `max_depth`: Maximum link depth
- `max_pages`: Total page limit
- `same_domain_only`: Domain restriction
- `include_patterns`: Regex for included URLs
- `exclude_patterns`: Regex for excluded URLs
- `max_retries`: Failure retry attempts
- `delay`: Delay between requests

### E. Browser Automation & Control

#### 1. Network Configuration

```python
browser_config = BrowserConfig(
    # Proxy settings
    proxy="http://proxy.company.com:8080",
    
    # Custom headers
    headers={
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Custom Agent/1.0",
        "Referer": "https://example.com"
    },
    
    # Extra HTTP headers
    extra_http_headers={
        "X-Custom-Header": "value"
    },
    
    # SSL/TLS
    ignore_https_errors=True
)
```

#### 2. Browser Resource Management

```python
browser_config = BrowserConfig(
    # Performance optimization
    disable_images=True,       # Don't load images
    disable_css=False,         # Keep CSS for layout
    
    # Viewport configuration
    viewport={
        "width": 1920,
        "height": 1080
    },
    
    # Timeouts
    timeout=30000,             # 30 seconds
    
    # Memory management
    headless=True
)
```

#### 3. Request Delays & Rate Limiting

```python
config = CrawlerRunConfig(
    delay=2.0,                 # 2 second delay between requests
    wait_for="networkidle"     # Wait for network idle
)
```

---

## 4. CONFIGURATION & SETUP

### Installation

```bash
# Basic installation
pip install crawl4ai

# With LLM extraction support
pip install "crawl4ai[openai]"        # For OpenAI
pip install "crawl4ai[anthropic]"     # For Claude
pip install "crawl4ai[google]"        # For Gemini

# Full installation with all features
pip install "crawl4ai[all]"

# From source
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
pip install -e .
```

### Core Dependencies

**Required:**
- `playwright>=1.40.0` - Browser automation
- `beautifulsoup4` - HTML parsing
- `pydantic>=2.0` - Data validation
- `markdown2` - HTML to Markdown
- `lxml` - XPath parsing
- `httpx>=0.24` - Async HTTP client

**Optional (for features):**
- `openai` - OpenAI LLM extraction
- `anthropic` - Claude LLM extraction
- `google-generativeai` - Gemini LLM extraction
- `pdf2image` - PDF processing
- `pillow` - Image processing
- `easyocr` - Optical character recognition

### Configuration Methods

#### 1. Environment Variables

```bash
# Browser settings
export CRAWL4AI_BROWSER_TYPE=chromium
export CRAWL4AI_HEADLESS=true
export CRAWL4AI_TIMEOUT=30000

# Proxy configuration
export CRAWL4AI_PROXY_URL=http://proxy:8080
export CRAWL4AI_PROXY_USERNAME=user
export CRAWL4AI_PROXY_PASSWORD=pass

# LLM API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...

# Performance
export CRAWL4AI_POOL_SIZE=10
export CRAWL4AI_CACHE_ENABLED=true
```

#### 2. Configuration File

Create `.crawl4ai/config.yaml`:

```yaml
browser:
  type: chromium
  headless: true
  timeout: 30000
  viewport:
    width: 1920
    height: 1080
  
extraction:
  default_format: markdown
  clean_content: true
  remove_ads: true
  
performance:
  pool_size: 5
  cache_enabled: true
  cache_ttl: 3600  # 1 hour
  
proxy:
  enabled: false
  url: null
  
logging:
  level: INFO
  file: crawl4ai.log
```

#### 3. Programmatic Configuration

```python
from crawl4ai import BrowserConfig, AsyncWebCrawler

browser_config = BrowserConfig(
    headless=True,
    browser_type="chromium",
    timeout=30000,
    disable_images=True,
    proxy="http://proxy:8080",
    headers={
        "Accept-Language": "en-US",
    }
)

crawler = AsyncWebCrawler(config=browser_config)
```

### Basic Usage Patterns

#### Pattern 1: Simple Page Extraction

```python
import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        if result.status.is_success():
            print(result.markdown)
        else:
            print(f"Error: {result.status.error_message}")

asyncio.run(main())
```

#### Pattern 2: Structured Data Extraction

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

async def extract_products():
    strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "title", "css": "h2.product-title", "type": "text"},
            {"name": "price", "css": ".product-price", "type": "text"},
            {"name": "rating", "css": ".rating", "type": "text"},
            {"name": "url", "css": "a.product-link", "type": "link"}
        ]
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://store.example.com/products",
            config=config
        )
        return result.extracted_data

asyncio.run(extract_products())
```

#### Pattern 3: LLM-Powered Extraction

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import LLMExtractionStrategy
from pydantic import BaseModel

class CompanyInfo(BaseModel):
    name: str
    industry: str
    employees: int
    founded_year: int
    description: str

async def extract_company_info():
    strategy = LLMExtractionStrategy(
        provider="openai",
        api_token="sk-...",
        schema=CompanyInfo,
        instruction="Extract comprehensive company information from the page"
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://example.com/about",
            config=config
        )
        return result.extracted_data

asyncio.run(extract_company_info())
```

#### Pattern 4: Deep Site Crawling

```python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawl import BFSDeepCrawlStrategy

async def crawl_documentation():
    strategy = BFSDeepCrawlStrategy(
        max_depth=3,
        max_pages=100,
        same_domain_only=True,
        include_patterns=[r".*\/docs\/.*"],
        exclude_patterns=[r".*\.pdf$", r".*\/search.*"]
    )
    
    config = CrawlerRunConfig(
        deep_crawl_strategy=strategy,
        extraction_strategy=JsonCssExtractionStrategy(
            extractions=[
                {"name": "title", "css": "h1", "type": "text"},
                {"name": "content", "css": ".main-content", "type": "html"}
            ]
        )
    )
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://docs.example.com",
            config=config
        )
        # Result contains all crawled pages
        return result

asyncio.run(crawl_documentation())
```

#### Pattern 5: Authenticated Access

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, BrowserProfiler

async def authenticated_crawl():
    # Step 1: Create profile (one-time)
    profiler = BrowserProfiler()
    profile_path = await profiler.create_profile("my_account")
    # User logs in manually in the browser window
    
    # Step 2: Use profile for crawling
    browser_config = BrowserConfig(
        use_managed_browser=True,
        user_data_dir=profile_path,
        browser_type="chromium"
    )
    
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun("https://app.example.com/dashboard")
        return result.markdown

asyncio.run(authenticated_crawl())
```

### Error Handling

```python
from crawl4ai import AsyncWebCrawler
from crawl4ai.models import CrawlStatus

async def safe_crawl(url):
    try:
        async with AsyncWebCrawler(timeout=30000) as crawler:
            result = await crawler.arun(url)
            
            if result.status == CrawlStatus.SUCCESS:
                return result.extracted_data
            elif result.status == CrawlStatus.TIMEOUT:
                print(f"Request timed out for {url}")
            elif result.status == CrawlStatus.FAILED:
                print(f"Request failed: {result.status.error_message}")
            
    except Exception as e:
        print(f"Exception: {e}")
```

### Performance Optimization

```python
from crawl4ai import BrowserConfig, AsyncWebCrawler

# Optimized configuration for speed
perf_config = BrowserConfig(
    headless=True,
    timeout=15000,              # Shorter timeout
    disable_images=True,        # Don't load images
    disable_css=False,          # Keep CSS for structure
    ignore_https_errors=True    # Skip SSL verification
)

# Use CSS extraction instead of LLM
# (Much faster and cheaper)
from crawl4ai.extraction import JsonCssExtractionStrategy
strategy = JsonCssExtractionStrategy(...)

# Add reasonable delays to respect servers
from crawl4ai import CrawlerRunConfig
config = CrawlerRunConfig(
    extraction_strategy=strategy,
    delay=1.0  # 1 second between requests
)
```

---

## 5. INTEGRATION WITH DATA PIPELINES

### DLT (Data Load Tool) Integration

```python
import dlt
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

@dlt.resource(name="articles", write_disposition="append")
async def scrape_articles():
    """DLT resource that uses Crawl4AI for scraping"""
    strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "title", "css": "h1", "type": "text"},
            {"name": "content", "css": "article", "type": "html"},
            {"name": "published_date", "css": ".date", "type": "text"}
        ]
    )
    
    config = CrawlerRunConfig(extraction_strategy=strategy)
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://blog.example.com",
            config=config
        )
        
        if result.status.is_success():
            yield result.extracted_data

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name="web_scraping",
    destination="duckdb",
    dataset_name="scraped_data"
)

# Run it
asyncio.run(pipeline.run(scrape_articles()))
```

### Dagster Integration

```python
from dagster import asset, Output
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

@asset
async def web_content():
    """Asset that crawls web content"""
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://example.com")
        
        return Output(
            value=result.extracted_data,
            metadata={
                "duration": result.duration,
                "status": result.status.status_code
            }
        )

@asset
def process_content(web_content):
    """Process crawled content"""
    # Further processing
    return processed_data
```

---

## 6. SUMMARY & KEY TAKEAWAYS

### Strengths of Crawl4AI

1. **LLM-Native Design**
   - Markdown output optimized for AI consumption
   - Supports structured extraction via Pydantic schemas
   - Cost-effective extraction strategies

2. **Dynamic Content Handling**
   - Full JavaScript rendering via Playwright
   - Custom JS execution before extraction
   - Wait conditions for async content

3. **Flexible Extraction**
   - CSS selector-based (fast, cheap)
   - LLM-powered (semantic, flexible)
   - Multiple output formats

4. **Authentication Support**
   - Persistent browser profiles
   - Programmatic login automation
   - Session/cookie management

5. **Performance**
   - Async-first design
   - Browser pooling for concurrency
   - Caching mechanisms
   - Image/CSS disabling for speed

6. **Production-Ready**
   - Type-safe configuration (Pydantic)
   - Comprehensive error handling
   - Integration with data pipelines
   - Active development and maintenance

### Best Use Cases

- Building RAG (Retrieval-Augmented Generation) knowledge bases
- Web data pipelines for AI training datasets
- Intelligent document extraction
- E-commerce product catalog scraping
- Documentation and API reference crawling
- News aggregation and content analysis
- Lead generation and market research data collection

### Integration Considerations

- Works seamlessly with dlt for data loading
- Compatible with Dagster for orchestration
- Supports multiple LLM providers
- Docker-friendly for containerization
- Can be deployed in data pipelines or standalone

---

## Additional Resources

**Official Documentation:**
- GitHub: https://github.com/unclecode/crawl4ai
- Documentation: https://docs.crawl4ai.com

**Related Tools in This Hackathon:**
- dlt: Data Load Tool for pipeline orchestration
- Dagster: Workflow orchestration
- Agno: Agent framework for AI automation
- MotherDuck/DuckDB: Analytics and SQL querying



> Source: `docs/data_engineering/crawl4ai/crawl4ai-dlt.md`

A Unified Architecture for AI-Driven Data
Acquisition and Analysis

Architectural Blueprint: A Unified Stack for AI-Driven
Data Acquisition

Executive Summary: The Modern Data Stack, Democratized

This report presents a comprehensive architectural guide for constructing a sophisticated,
end-to-end data acquisition and analysis platform. It leverages a curated selection of modern,
cost-effective, and open-source-centric tools designed to empower individual developers,
researchers, and small teams. The architecture provides capabilities that have traditionally
required large engineering organizations and significant capital expenditure, effectively
democratizing access to a state-of-the-art data stack.
The core philosophy of this architecture is rooted in the strategic use of serverless paradigms,
open standards, and AI-native tooling. The data workflow begins with advanced, AI-aware web
scraping using CRAWL4AI to extract clean, structured information from complex web sources.
This data is then ingested into a robust pipeline orchestrated by dlt (data load tool), a
declarative Python library that automates schema inference and data loading.
A key innovation of this stack is the decoupling of storage and compute. Data is persisted in an
open format to Cloudflare R2, an S3-compatible object storage service notable for its low cost
and absence of egress fees. This data lake is then queried in situ by a powerful analytics layer
composed of DuckDB for local operations and MotherDuck for serverless cloud-based
analysis.
This entire system is designed to run on highly cost-effective infrastructure, utilizing either a
Hetzner cloud VPS or the Oracle Cloud Free Tier. Security and access are managed through
Pangolin (Fossorial), a self-hosted, identity-aware reverse proxy that provides secure
tunneling without exposing server ports. The entire development and operational lifecycle is
supercharged by an agentic AI environment within Visual Studio Code, integrating Gemini 2.5
Pro and GitHub Copilot. This is further extended through custom, containerized Model
Context Protocol (MCP) servers, which grant AI agents programmatic control over the data
stack, transforming the development process into a collaborative human-AI partnership.

System Architecture Diagram

The proposed architecture is a modular system where each component serves a distinct
purpose, interconnected through well-defined interfaces and open standards. The flow of data
and control is designed for efficiency, scalability, and security.

●

Ingestion Layer: At the forefront is the CRAWL4AI service, running within a Docker
container on the chosen VPS. It is responsible for all web scraping activities, targeting
educational resources like examinations.ie and the BBC. It interacts with the public
internet, handling dynamic content, logins, and deep crawling, producing LLM-optimized
Markdown or structured JSON data.

●  Pipelining & Orchestration Layer: The dlt script, also containerized on the VPS, serves

as the central orchestrator. It acts as a client to the CRAWL4AI service (or directly
embeds its logic), taking the raw scraped data as input. Using its declarative resource and
source decorators, dlt manages data normalization, schema evolution, and loading.
●  Storage Layer: The single source of truth for raw and processed data is Cloudflare R2.
dlt writes data, typically in the efficient Parquet format, directly to a designated R2 bucket.
R2's S3-compatible API and zero-egress-fee policy make it the economic cornerstone of
the data backbone.

●  Analytics Layer: This layer is bifurcated. For local development, debugging, and

●

smaller-scale analysis, DuckDB can be used directly within a container or on a local
machine to query the Parquet files in R2. The primary analytics engine, however, is
MotherDuck. It connects to the R2 bucket via its DuckLake feature, providing a
serverless, scalable SQL query interface over the data without requiring a separate
ingestion step.
Infrastructure & Security Layer: The entire stack of containerized services is hosted on
a Hetzner or Oracle Cloud Free Tier VPS. Network traffic and domain management are
handled by Cloudflare DNS. Crucially, Pangolin acts as a secure gateway. Instead of
opening ports on the VPS firewall for services like a potential API endpoint, Pangolin
establishes an outbound WireGuard tunnel, exposing services securely through its own
identity and access management layer.

●  Development & Agentic Layer: The developer interacts with the system from a local

Visual Studio Code environment. This IDE is augmented with the Gemini 2.5 Pro and
GitHub Copilot extensions for AI-assisted coding. The developer connects to the VPS
via SSH to manage the Docker containers. The most advanced interaction occurs through
a custom, containerized MCP Server running on the VPS. The Gemini agent in VS Code
can invoke tools exposed by this server—for instance, a tool to directly query the
MotherDuck database—creating a powerful, automated feedback loop for data analysis
and system management.

Strategic Rationale and Core Synergies

The power of this architecture lies not just in the individual tools but in their synergistic
integration, which addresses common pain points in modern data engineering related to cost,
complexity, and flexibility.

●  CRAWL4AI + dlt: From Raw Web to Structured Pipeline: The integration between

CRAWL4AI and dlt is exceptionally seamless. CRAWL4AI is designed to output clean,
structured data, either as LLM-ready Markdown or, more applicably here, as structured
JSON via its extraction strategies. This output can be yielded directly from a Python
function, which can then be decorated as a @dlt.resource. This creates a robust,
schema-aware ingestion pipeline with minimal boilerplate code, as dlt automatically
handles schema inference, data typing, and normalization. This tight, in-process coupling
eliminates the need for intermediate storage or complex data handoffs between the
scraping and pipelining stages.

●  dlt + R2 + MotherDuck: The DuckLake Architecture: This combination represents a

strategic decoupling of storage and compute, forming a modern, cost-effective alternative
to traditional data warehouses. dlt writes data in an open, columnar format (Parquet) to
Cloudflare R2. R2 provides extremely inexpensive, durable storage with the critical
advantage of zero egress fees, eliminating surprise costs associated with data movement.

MotherDuck's DuckLake feature then allows it to act as a serverless query engine directly
on top of the data in R2. Data does not need to be ingested or duplicated into
MotherDuck's own storage. This "disaggregated" model provides immense flexibility and
cost control, allowing storage and compute to scale independently.

●  Hetzner/Oracle + Pangolin + Docker: Sovereign and Secure Infrastructure: The use
of commodity VPS providers like Hetzner or the Oracle Free Tier offers powerful compute
resources at a fraction of the cost of larger hyperscalers. Deploying all services as Docker
containers ensures portability and reproducible environments. Pangolin introduces a
critical security posture that aligns with modern "zero trust" principles. By tunneling
services through an outbound WireGuard connection, it obviates the need to open
inbound ports on the server's firewall, drastically reducing the attack surface. Pangolin
then layers its own robust identity and access management on top, providing a
self-hosted, fully controlled secure gateway to any internal services.

●  VS Code + Gemini + MCP: AI as a Collaborative Platform: This integration elevates

the role of AI in the development process. While Gemini and Copilot excel at generating
code for the scraper, the dlt pipeline, or Dockerfiles, the true paradigm shift comes from
the Model Context Protocol (MCP). By building a custom MCP server, the developer can
create tools that give the AI agent direct, programmatic access to the live system. For
example, a tool could allow Gemini to query the MotherDuck database, inspect pipeline
logs, or even trigger a new CRAWL4AI run. This transforms the AI from a simple code
completion engine into an active, agentic partner capable of performing complex,
multi-step tasks across the entire stack based on natural language commands.

The selection of these tools reflects a broader industry movement toward a more unbundled and
rebundled data stack. Traditional, monolithic cloud services, while convenient, often come with
high costs and vendor lock-in, particularly through mechanisms like data egress fees. The
architecture detailed here deliberately unbundles these functions, selecting best-of-breed,
cost-effective components for each task: R2 for storage, MotherDuck for compute, and Hetzner
for hosting. These components are then "rebundled" not by a single vendor, but by open
standards (S3 API, Parquet, SQL) and flexible, interoperable software (dlt, DuckDB). This
approach provides greater control, transparency, and economic efficiency.
Furthermore, the entire stack is designed around the principle of "Infrastructure as Code,
Managed by AI." Every component is defined and configured through code—Python scripts for
CRAWL4AI and dlt, and YAML files for Docker Compose and Pangolin. The integration of MCP
servers completes this vision by creating a programmatic interface through which an AI agent
can interact with, query, and ultimately help manage this code-defined infrastructure. This
represents a forward-looking approach, moving beyond AI-assisted development to AI-driven
operations.

The Ingestion Engine: Mastering Advanced Web
Scraping with CRAWL4AI

Deep Dive into CRAWL4AI's Capabilities

CRAWL4AI distinguishes itself as a modern web scraping framework by being purpose-built for
AI and agentic workflows. It moves beyond traditional HTML parsing to provide a
comprehensive suite of tools for interacting with and extracting meaningful data from the

contemporary, dynamic web.

●  LLM-Native Design: The core design philosophy of CRAWL4AI is to produce output that
is immediately consumable by Large Language Models. Instead of raw, noisy HTML, it
can intelligently convert web content into clean, structured Markdown. This process
involves removing superfluous tags like <script> and <style>, structuring content with
proper headings and tables, and converting hyperlinks into citation-style references,
which is ideal for Retrieval-Augmented Generation (RAG) and model fine-tuning
applications.

●  Performance and Control: CRAWL4AI is engineered for speed and efficiency. It utilizes
an asynchronous browser pool and caching mechanisms to minimize network hops and
redundant operations, claiming performance up to six times faster than conventional
methods. Developers retain granular control over the browsing context through the
BrowserConfig class, allowing for precise configuration of headless mode, proxies, user
agents, and persistent browser profiles for session management.

●  Dynamic Content and Interaction: The modern web is overwhelmingly dynamic, and

CRAWL4AI is equipped to handle it. It provides a powerful mechanism for interacting with
pages that rely heavily on JavaScript. Through the CrawlerRunConfig, developers can
execute custom JavaScript code (js_code), instruct the crawler to wait for specific
elements or conditions (wait_for), and reuse sessions across multiple steps. This enables
complex workflows such as repeatedly clicking "Load More" buttons, filling out and
submitting forms, or navigating multi-page application flows.

●  Deep Crawling Strategies: For comprehensive data extraction from entire websites,

CRAWL4AI offers several deep crawling strategies. These include Breadth-First Search
(BFSDeepCrawlStrategy) and Depth-First Search (DFSDeepCrawlStrategy), allowing the
crawler to recursively discover and process linked pages. These strategies are highly
configurable, with parameters to control crawl depth, enforce domain limits, and apply
filters to include or exclude URLs based on specific patterns, ensuring the crawler
retrieves only relevant content.

●  Versatile Extraction Strategies: CRAWL4AI provides a dual approach to data extraction,

catering to different needs for speed, cost, and accuracy:

○  Structured Extraction (LLM-Free): For performance-critical tasks where the data
structure is well-defined, the framework supports extraction using standard CSS or
XPath selectors. This method is significantly faster and cheaper as it does not
require an LLM call, making it ideal for scalable, precise data retrieval.
○  LLM-Powered Extraction: When data is unstructured or requires semantic

understanding, CRAWL4AI can leverage an LLM. This enables sophisticated tasks
like summarization, classification, or extracting information based on natural
language instructions (e.g., "Extract all product prices"). It supports defining the
desired output structure using Pydantic schemas, ensuring the LLM returns clean,
validated JSON. The framework also manages content chunking to respect model
token limits while preserving context.

Tutorial: Scraping Login-Protected Educational Resources

This tutorial demonstrates how to use CRAWL4AI to scrape data from a website that requires
user authentication, a common scenario for accessing personalized educational resources like
those on a student portal modeled after examinations.ie.
The primary challenge is to manage the login state. CRAWL4AI offers two robust methods for

this: Identity-Based Crawling with Managed Browsers, which is the recommended approach for
its simplicity and reliability, and programmatic login using Session Management and Hooks for
fully automated workflows.

Step 1: Authentication with Identity-Based Crawling

This method involves creating a persistent browser profile where the login is performed once,
manually. CRAWL4AI then reuses this profile, along with its cookies and session storage, for all
subsequent automated crawls, making the scraper appear as the logged-in user.

1.  Create a Persistent Profile: CRAWL4AI's BrowserProfiler class automates this process.
The following script will launch a browser window. The user should navigate to the login
page, enter their credentials, and complete the login process. Once logged in, pressing 'q'
in the terminal will save the entire browser profile (cookies, local storage, etc.) to a
specified directory.
import asyncio
from crawl4ai import BrowserProfiler

async def create_login_profile():
    """
    Launches a browser to create a persistent profile with login
state.
    """
    profiler = BrowserProfiler()
    print("A browser window will now open.")
    print("Please log in to the educational portal.")
    print("Once you are logged in, press 'q' in this terminal to
save the profile and close the browser.")

    profile_path = await
profiler.create_profile(profile_name="edu_portal_profile")

    print(f"Profile created and saved at: {profile_path}")
    return profile_path

if __name__ == "__main__":
    asyncio.run(create_login_profile())
This script saves the profile to a default location managed by CRAWL4AI and prints the
path, which is needed for the next step.

2.  Use the Profile for Scraping: Now, configure CRAWL4AI to use this saved profile. The
BrowserConfig is set up to use a "managed browser" and points to the user_data_dir
where the profile was saved.
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig,
CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

# Path obtained from the previous script
PROFILE_PATH =

"/path/to/your/crawl4ai_profiles/edu_portal_profile"

async def scrape_protected_data():
    """
    Uses the saved browser profile to scrape data from a protected
page.
    """
    # Configure the crawler to use the persistent profile
    browser_config = BrowserConfig(
        headless=True,
        use_managed_browser=True, # Key setting for using
persistent identity
        user_data_dir=PROFILE_PATH,
        browser_type="chromium"
    )

    # Define what to extract from the page
    extraction_strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "exam_subject", "css":
".exam-result-subject", "type": "text"},
            {"name": "exam_grade", "css": ".exam-result-grade",
"type": "text"},
            {"name": "exam_date", "css": ".exam-result-date",
"type": "text"}
        ]
    )

    run_config = CrawlerRunConfig(

url="https://www.examinations.ie/candidate-portal/results", #
Hypothetical URL
        extraction_strategy=extraction_strategy
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("Starting crawl with authenticated profile...")
        result = await crawler.arun(config=run_config)

        if result.status.is_success():
            print("Successfully extracted data:")
            print(result.extracted_data)
        else:
            print(f"Crawl failed: {result.status.error_message}")

if __name__ == "__main__":
    asyncio.run(scrape_protected_data())
This workflow effectively bypasses the login process on each run by inheriting the

authenticated state from the managed profile, a technique that is both robust and less
likely to be detected as bot activity.

Alternative: Programmatic Login with Hooks

For scenarios requiring full automation without manual intervention, CRAWL4AI's hook system
can be used to perform the login steps programmatically. The on_page_context_created hook is
ideal for this, as it provides access to the page object before the crawler navigates to the target
URL.
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig
from playwright.async_api import Page, BrowserContext

async def perform_login(page: Page, context: BrowserContext,
**kwargs):
    """
    Hook function to programmatically log in before crawling.
    """
    print("[HOOK] Navigating to login page...")
    await
page.goto("https://www.examinations.ie/candidate-portal/login") #
Hypothetical

    # Fill in login credentials
    await page.fill('input[name="username"]', "YOUR_USERNAME")
    await page.fill('input[name="password"]', "YOUR_PASSWORD")

    print("[HOOK] Submitting login form...")
    await page.click('button[type="submit"]')

    # Wait for navigation to the dashboard to confirm login
    await page.wait_for_url("**/candidate-portal/dashboard")
    print("[HOOK] Login successful!")
    return page

async def main():
    browser_config = BrowserConfig(
        headless=False, # Often useful to run non-headless for
debugging logins
        hooks={
            "on_page_context_created": perform_login
        }
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await
crawler.arun(url="https://www.examinations.ie/candidate-portal/results
")

        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())

This approach is more complex and may require adjustments if the site uses CAPTCHAs or
other advanced bot detection, but it offers a fully automated solution.

Analysis of Target Sites and Compliance

A responsible scraping strategy requires an understanding of the target websites' structure and
their stated policies regarding automated access.

●  examinations.ie: The structure of this site revolves around providing official information
and a secure portal for candidates. The public-facing sections contain documents (PDFs
of exam papers, circulars), which are straightforward to crawl. The key challenge is the
Candidate Self Service Portal, which requires a Personal Identification Number (often
derived from a PPSN) for access. This necessitates the authenticated crawling
techniques detailed above. The data within this portal is personal and sensitive, and any
scraping activity must be conducted with explicit user consent and for legitimate
purposes.

●  BBC Bitesize: This is a large, media-rich educational platform with a deeply nested

structure organized by curriculum, subject, and topic. The primary scraping challenge is
not authentication but navigation and content extraction. A deep crawling strategy
(BFSDeepCrawlStrategy) would be effective for discovering the vast number of pages.
The goal would be to extract the core educational text, code snippets, and diagrams while
filtering out navigation menus, related links, and other boilerplate content. CRAWL4AI's
ability to convert content to clean Markdown is particularly valuable here, as it helps
isolate the signal from the noise.

●  robots.txt Compliance: The Robots Exclusion Protocol, implemented via a robots.txt file
at the root of a domain, is a standard for communicating with web crawlers. It is crucial to
understand that this protocol is voluntary; it provides guidelines for "good" bots but is not a
security mechanism to prevent access. Malicious bots can, and often do, ignore it.
○  Analysis: A review of the BBC's robots.txt file, for example, shows specific

directives for different user agents, disallowing paths related to admin areas, search
functions, and user profiles. A compliant scraper should parse this file and respect
these Disallow rules. The file may also contain a Crawl-delay directive, which
specifies a minimum time to wait between requests to avoid overloading the server.
CRAWL4AI's delay parameter in the CrawlerRunConfig should be set to honor this
value.

○  Ethical Considerations: For login-protected sites like examinations.ie, the

robots.txt file is less relevant for the protected areas, as they are not intended for
public crawlers in the first place. The ethical and legal responsibility shifts from
respecting a public policy to handling personal data appropriately and with consent.
Any scraping of such areas should only be done on behalf of the user who has
provided the credentials.

The evolution of web scraping, as exemplified by CRAWL4AI, is a direct response to the
increasing complexity and personalization of websites. The process has shifted from simple,
anonymous HTTP requests for static HTML to sophisticated, identity-aware interactions with

dynamic, stateful applications. The emphasis on features like persistent browser profiles and
session management underscores that modern data acquisition often requires simulating a
genuine user's identity to access valuable, personalized content. This trend suggests that the
future of web data extraction will be less about broad, anonymous crawling and more about
authenticated, permissioned, and stateful automation.
Simultaneously, the rise of applications like Retrieval-Augmented Generation has created a
direct market need for a new form of data preprocessing at the point of ingestion. The value is
no longer just in the raw data itself, but in its semantic cleanliness and structural integrity for
downstream AI consumption. A scraper's function has expanded from merely "getting" the data
to "preparing" it for an LLM. CRAWL4AI's focus on producing "LLM-ready Markdown" is a
leading indicator of this shift, where the scraping tool itself becomes the first and one of the
most critical steps in the AI data preparation pipeline.

The Data Backbone: Building Resilient Pipelines with
dlt, DuckDB, and Cloudflare R2

Introduction to dlt (data load tool)

dlt (data load tool) is an open-source Python library engineered to streamline and automate the
often-tedious process of building data pipelines. It operates on a "load data anywhere"
philosophy, abstracting away the complexities of data ingestion so that developers can focus on
the core logic of their application rather than on boilerplate data engineering tasks.
At its core, dlt is designed to be declarative, user-friendly, and highly extensible. It leverages
simple Python decorators, primarily @dlt.source and @dlt.resource, to define data pipelines. A
developer can write a standard Python function that yields data (e.g., from an API call or a file),
and with a single decorator, dlt transforms it into a robust data resource.
Key features that make dlt a powerful choice for this architecture include:

●  Schema Inference and Evolution: dlt automatically inspects the data being processed

and infers a schema, including data types and table structures. Crucially, it also manages
schema evolution. If the source data changes over time (e.g., a new field is added), dlt
can automatically adapt the destination schema, preventing pipeline failures and
eliminating a significant maintenance burden.

●  Automated Normalization: The library handles the normalization of semi-structured
data, such as nested JSON from APIs, into a structured, relational format suitable for
analytical databases. It creates parent-child tables and adds lineage metadata
automatically.
Incremental Loading: dlt has built-in support for incremental loading, allowing pipelines
to efficiently process only new or updated data since the last run, which is essential for
handling large datasets.

●

●  "Run Anywhere" Philosophy: dlt is a pure Python library with no external dependencies
on backends, APIs, or containers. This means a dlt pipeline can run wherever Python can
run—on a local machine, a serverless function, an Airflow DAG, or, as in this architecture,
a simple VPS. This simplicity and portability make it an ideal fit for a cost-effective,
self-hosted solution.

Tutorial: A Complete Pipeline from Scraper to Cloud Storage

This tutorial demonstrates the creation of a complete, end-to-end data pipeline. It will take the
structured data extracted by the CRAWL4AI scraper and load it into Cloudflare R2 using dlt.

Step 1: Creating a Python Generator Source

The first step is to encapsulate the scraping logic within a dlt resource. A @dlt.resource is a
Python generator function that yields batches of data. This allows dlt to process data in a
memory-efficient, streaming fashion.
The following script integrates the CRAWL4AI scraping logic from the previous section into a
dlt-compatible resource.
import dlt
from typing import Iterable, Dict, Any
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction import JsonCssExtractionStrategy

# Assume PROFILE_PATH is configured correctly from the CRAWL4AI
tutorial
PROFILE_PATH = "/path/to/your/crawl4ai_profiles/edu_portal_profile"

@dlt.resource(name="exam_results", write_disposition="replace")
async def get_exam_results_data() -> Iterable]:
    """
    A dlt resource that uses CRAWL4AI to scrape authenticated data
    and yields the results.
    """
    browser_config = BrowserConfig(
        headless=True,
        use_managed_browser=True,
        user_data_dir=PROFILE_PATH,
        browser_type="chromium"
    )

    extraction_strategy = JsonCssExtractionStrategy(
        extractions=[
            {"name": "exam_subject", "css": ".exam-result-subject",
"type": "text"},
            {"name": "exam_grade", "css": ".exam-result-grade",
"type": "text"},
            {"name": "exam_date", "css": ".exam-result-date", "type":
"text"}
        ]
    )

    run_config = CrawlerRunConfig(

        url="https://www.examinations.ie/candidate-portal/results", #
Hypothetical
        extraction_strategy=extraction_strategy
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        print("CRAWL4AI: Starting crawl within dlt resource...")
        result = await crawler.arun(config=run_config)

        if result.status.is_success() and result.extracted_data:
            print(f"CRAWL4AI: Successfully extracted
{len(result.extracted_data)} records.")
            # dlt can process an iterator of items directly
            yield result.extracted_data
        else:
            print(f"CRAWL4AI: Crawl failed or returned no data. Error:
{result.status.error_message}")
            # Yield an empty list to signify no data for this run
            yield

This function, get_exam_results_data, is now a reusable component that dlt can use as a data
source. The write_disposition="replace" argument instructs dlt to replace the destination table
with new data on each run.

Step 2: Configuring the Filesystem Destination for Cloudflare R2

dlt's filesystem destination is designed to work with any fsspec-compatible backend, including
S3-compatible services like Cloudflare R2. Configuration is handled through TOML files in a .dlt
directory.

1.  Create .dlt/config.toml: This file contains non-sensitive configuration. Here, we specify

that the filesystem destination should be used.
#.dlt/config.toml
[destination.filesystem]
# This is a placeholder; the actual bucket URL with protocol is in
secrets.toml

2.  Create .dlt/secrets.toml: This file holds sensitive credentials. To connect to Cloudflare

R2, the bucket_url, credentials, and the crucial endpoint_url must be provided.
#.dlt/secrets.toml
[destination.filesystem]
bucket_url = "s3://your-r2-bucket-name" # e.g.,
s3://educational-data

[destination.filesystem.credentials]
aws_access_key_id = "YOUR_R2_ACCESS_KEY_ID"
aws_secret_access_key = "YOUR_R2_SECRET_ACCESS_KEY"
# This is the critical part for R2 compatibility

endpoint_url =
"https://<YOUR_ACCOUNT_ID>.r2.cloudflarestorage.com"

Step 3: Running the Pipeline

With the source and destination configured, the final step is to create a pipeline script that brings
them together. The script will instantiate a dlt.pipeline, specify the destination, and run the
resource function.
# main_pipeline.py

import dlt
# Import the resource function from the previous step
from scraper_source import get_exam_results_data

def run_pipeline():
    """
    Configures and runs the dlt pipeline to load data from the scraper
to R2.
    """
    # Configure the pipeline
    pipeline = dlt.pipeline(
        pipeline_name="educational_resources_pipeline",
        destination="filesystem", # This matches the section in
config.toml
        dataset_name="irish_exams"
    )

    # Run the pipeline, loading data from our async resource.
    # dlt handles running the async generator correctly.
    # We specify the loader file format as parquet for efficiency.
    load_info = pipeline.run(
        get_exam_results_data(),
        loader_file_format="parquet"
    )

    # Pretty-print the outcome
    print(load_info)

if __name__ == "__main__":
    run_pipeline()

When this script is executed, dlt will:

1.  Invoke the get_exam_results_data async generator.
2.  Receive the scraped data yielded by the function.
3.  Infer a schema from the data structure.
4.  Convert the data into Parquet format.
5.  Use the credentials in secrets.toml to connect to the Cloudflare R2 endpoint.

6.  Upload the Parquet files into the s3://your-r2-bucket-name/irish_exams/exam_results/

path.

This completes the data flow from a live, authenticated website into a structured, queryable
format in cloud object storage.

The Analytics Layer: Querying R2 with DuckDB and MotherDuck

Once the data resides in Cloudflare R2 as Parquet files, it is ready for analysis. This architecture
offers two complementary methods for querying this data.

Local Analysis with DuckDB

For development, testing, or ad-hoc analysis on a local machine, DuckDB can directly query
files in S3-compatible storage. This requires installing the httpfs extension and configuring
credentials.
import duckdb
import os

# Set environment variables for DuckDB's S3 extension to use
os.environ = 'YOUR_R2_ACCESS_KEY_ID'
os.environ = 'YOUR_R2_SECRET_ACCESS_KEY'
os.environ[span_61](start_span)[span_61](end_span) =
'<YOUR_ACCOUNT_ID>.r2.cloudflarestorage.com'

# Connect to an in-memory DuckDB database
con = duckdb.connect(config={'s3_region': 'auto'})

# Query the Parquet files directly from R2
# The path matches the one created by dlt
df = con.execute("""
    SELECT
        exam_subject,
        COUNT(*) as num_entries
    FROM 's3://your-r2-bucket-name/irish_exams/exam_results/*.parquet'
    GROUP BY exam_subject
    ORDER BY num_entries DESC;
""").fetch_df()

print(df)

This approach is incredibly powerful for local workflows, providing full SQL analytics on cloud
data without needing any server infrastructure.

Serverless Analytics with MotherDuck and DuckLake

This is the primary cloud architecture for scalable, shared analytics. MotherDuck provides a
serverless platform that extends DuckDB's capabilities to the cloud, and its DuckLake feature is
purpose-built for querying data in external object storage.

1.  Configure R2 Access in MotherDuck: First, securely provide MotherDuck with the

credentials to access the R2 bucket. This is done by creating a SECRET object within
MotherDuck's environment. This SQL command can be run in the MotherDuck web UI:
CREATE SECRET r2_credentials IN MOTHERDUCK (
    TYPE R2,
    KEY_ID 'YOUR_R2_ACCESS_KEY_ID',
    SECRET 'YOUR_R2_SECRET_ACCESS_KEY',
    ACCOUNT_ID '<YOUR_ACCOUNT_ID>'
);

2.  Create the DuckLake Database: Next, define a new database in MotherDuck that is

backed by the R2 bucket. This command tells MotherDuck to treat the specified R2 path
as a managed database, without moving the data.
CREATE DATABASE educational_data_lake (
    TYPE DUCKLAKE,
    DATA_PATH 's3://your-r2-bucket-name/'
);

3.  Reconfigure and Run dlt Pipeline for DuckLake: The dlt pipeline must now be

reconfigured to load data directly into this DuckLake-managed database. This involves
changing the destination to motherduck and updating the credentials.

○  Update .dlt/secrets.toml:

[destination.motherduck.credentials]
# The DuckLake database created in the previous step
database = "educational_data_lake"
# Your MotherDuck service token
password = "YOUR_MOTHERDUCK_TOKEN"

○  Update main_pipeline.py:

# In main_pipeline.py
pipeline = dlt.pipeline(
    pipeline_name="educational_resources_pipeline",
    destination="motherduck", # Change destination to
motherduck
    dataset_name="irish_exams"
)

When this updated pipeline is run, dlt connects to MotherDuck. MotherDuck, using its
stored R2 credentials, then manages the writing of the Parquet files into the correct
location within the R2 bucket under the DuckLake structure.

4.  Querying via MotherDuck: With the pipeline complete, any user or service can connect

to MotherDuck (via its web UI, a Python client, or any DuckDB-compatible tool) and run
standard SQL queries. The query execution is handled by MotherDuck's serverless
compute, while the data-at-rest remains securely and cost-effectively in Cloudflare R2.
import duckdb

# Connect to MotherDuck using its connection string
con =

duckdb.connect(database='md:educational_data_lake?motherduck_token
=YOUR_TOKEN')

# Run the same query, but now it's executed in the cloud by
MotherDuck
df = con.execute("""
    SELECT
        exam_subject,
        COUNT(*) as num_entries
    FROM irish_exams.exam_results
    GROUP BY exam_subject
    ORDER BY num_entries DESC;
""").fetch_df()

print(df)

This architecture represents a fundamental shift in data engineering. The combination of dlt with
the DuckDB ecosystem moves away from complex, multi-tool ETL/ELT frameworks. It
champions a Python-native approach where the entire pipeline, from data extraction to loading,
can be expressed in a single, familiar language. dlt's automation of schema management
removes one of the most significant historical pain points in data pipeline development. This
empowers Python-centric data scientists and developers to build and own their data
infrastructure end-to-end, without needing to become experts in separate SQL-based
transformation tools.
Furthermore, the DuckLake architecture is a powerful manifestation of the "disaggregated data
warehouse" trend, which is reshaping cloud data economics. Traditional cloud data warehouses
bundle storage and compute, creating potential for high costs and vendor lock-in. By
disaggregating these components, this stack allows for the use of the most economically
efficient solution for each job: Cloudflare R2 for storage (leveraging its zero egress fees) and
MotherDuck for pay-as-you-go, serverless compute. The DuckLake technology provides the
critical metadata and cataloging layer that makes this separation possible, giving users
unprecedented control over their costs and data sovereignty, and mitigating the risks of data
gravity.

Infrastructure Deployment: A Cost-Optimized and
Secure Hosting Strategy

VPS Selection: Hetzner vs. Oracle Cloud Free Tier

The choice of a Virtual Private Server (VPS) is a critical foundation for the architecture. The
primary goal is to find a provider that offers sufficient resources for running containerized
scraping and data pipeline workloads at the lowest possible cost. Two standout options are
Hetzner and the Oracle Cloud Infrastructure (OCI) Free Tier.

●  Hetzner: A German cloud provider renowned for its exceptional price-to-performance

ratio, particularly for its cloud server offerings in Europe and the US. Hetzner is an ideal
choice for predictable, low-cost, high-performance hosting. Its key advantages include

straightforward hourly billing with a monthly cap, and a very generous inclusive traffic
allowance (typically 20 TB per month for EU locations), which is more than sufficient for
this project's needs. Its simple web console and developer-friendly tools like an official CLI
and Terraform provider make it easy to manage.

●  Oracle Cloud (OCI) Free Tier: Oracle offers a uniquely compelling "Always Free" tier that
goes far beyond the typical 12-month trial periods of other major cloud providers. The
centerpiece of this offering for compute-intensive tasks is the Ampere A1 instance, which
is based on the ARM architecture. The free tier provides a generous pool of 3,000 OCPU
hours and 18,000 GB hours per month, which can be configured as a single powerful VM
with up to 4 OCPUs and 24 GB of RAM, or as multiple smaller VMs. The free tier also
includes 200 GB of block storage and 10 TB of outbound data transfer per month, making
it a genuinely free option for hosting the entire stack. The main consideration is the ARM
architecture, which requires the use of ARM-compatible Docker images.

The following table provides a direct comparison of a typical low-cost Hetzner instance against
the Oracle Always Free offering.
Feature

Hetzner (CPX21 - AMD)

CPU Architecture
vCPUs
RAM
NVMe SSD Storage
Included Traffic
Price (Monthly)
Key Pros

Key Cons

x86-64
3
4 GB
80 GB
20 TB (EU)
~$7.55 / €7.05
Predictable cost, x86
compatibility, excellent
performance, simple interface.
Not free.

Oracle Always Free (Ampere
A1 Flex)
AArch64 (ARM)
Up to 4
Up to 24 GB
200 GB (total pool)
10 TB
$0 (within free tier limits)
Potentially zero cost, very
generous CPU/RAM allocation,
large storage pool.
ARM architecture requires
compatible software, resource
availability can be limited.

This comparison allows for an informed decision based on project priorities. Hetzner offers a
reliable, powerful, and still very inexpensive option with the broad compatibility of the x86
architecture. Oracle provides a pathway to a completely free, and potentially more powerful,
hosting solution, with the primary trade-off being the need to ensure all software components
are ARM-compatible. Given that many modern tools, including CRAWL4AI, provide multi-arch
Docker images, the Oracle option is highly viable.

Tutorial: Provisioning an Oracle Cloud "Always Free" Ampere VM

This guide provides a step-by-step process for setting up an "Always Free" Ampere A1 virtual
machine on Oracle Cloud Infrastructure, from account creation to establishing a secure SSH
connection.

1.  Account Signup: Navigate to the Oracle Cloud Free Tier signup page. The process

requires providing an email address, creating a password, and selecting a home region. It
is critical to select a home region that supports Always Free Ampere A1 instances. A valid
credit or debit card is required for identity verification; prepaid cards are not accepted. A
small verification charge may be applied and then refunded.

2.  Instance Creation: Once logged into the OCI Console, navigate to the "Compute" section

and select "Instances." Click the "Create instance" button to begin the provisioning
process.

3.  Name and Compartment: Assign a descriptive name to the instance (e.g.,

data-ingestion-vps). Ensure it is being created in the root compartment of your tenancy.

4.  Image and Shape Configuration: This is the most critical step.
In the "Image and shape" section, click "Edit."

○
○  Under "Image," click "Change image" and select a suitable operating system.

Ubuntu is a common and well-supported choice.

○  Under "Shape," click "Change shape." Select the "Ampere" option for the processor
architecture. Check the box for the VM.Standard.A1.Flex shape, which is marked
as "Always Free-eligible".

○  Adjust the sliders to allocate the desired number of OCPUs and amount of memory.
To create a single, powerful instance, slide both to the maximum (4 OCPUs, 24 GB
of RAM). Click "Select shape."

5.  Networking: For most use cases, the default networking settings are sufficient. Ensure

"Create new virtual cloud network" is selected and that the "Assign a public IPv4 address"
option is enabled. This will create the necessary network infrastructure and make the VM
accessible from the internet.

6.  SSH Key Configuration: Secure access to the VM is managed via SSH keys. In the

"Add SSH keys" section, select the "Paste public keys" option. Paste the content of your
local public SSH key (typically found in ~/.ssh/id_rsa.pub on Linux or macOS) into the text
box. Alternatively, you can upload the file or have OCI generate a new key pair for you.
7.  Boot Volume: The Always Free tier includes a total of 200 GB of block volume storage.
The default boot volume size is 50 GB. To maximize storage for a single instance, you
can check "Specify a custom boot volume size" and set it to 200 GB.

8.  Create and Connect: Click the "Create" button. The instance will begin provisioning,

which may take a few minutes. Once the status turns to "Running," its public IP address
will be displayed on the instance details page. Use this IP address and your private SSH
key to connect. The default username for an Ubuntu image is ubuntu.
# Example SSH connection command
ssh -i /path/to/your/private_key ubuntu@<PUBLIC_IP_ADDRESS>

9.  Opening Firewall Ports: By default, OCI's Virtual Cloud Network (VCN) has a restrictive
firewall. To allow web traffic (e.g., for accessing the Pangolin dashboard), you must add
ingress rules.

○  Navigate to the instance's details page, click on the Virtual Cloud Network link, then

the Subnet link, and finally the Security List link.

○  Click "Add Ingress Rules."
○  Add a rule with Source CIDR 0.0.0.0/0 and Destination Port Range 443 for HTTPS

traffic. Add another for port 80 if needed.

○  Additionally, the OS firewall (iptables or ufw) on the instance itself may need to be

configured to allow traffic on these ports.

Secure Networking with Pangolin (Fossorial)

Pangolin is a self-hosted, identity-aware, tunneled reverse proxy. It serves as a powerful
open-source alternative to services like Cloudflare Tunnels, providing a secure method to
expose services running on the VPS to the internet without opening inbound firewall ports. It

achieves this by creating an encrypted, outbound WireGuard tunnel from a client on the host
network to the central Pangolin server. Pangolin then proxies traffic through this tunnel, adding a
layer of centralized authentication and access control.

Tutorial: Deploying Pangolin via Docker Compose

This tutorial outlines the manual installation of Pangolin on the newly provisioned VPS using
Docker Compose.

●  Prerequisites: A domain name is required. An A record for the Pangolin dashboard (e.g.,
pangolin.your-domain.com) and a wildcard CNAME or A record (*.your-domain.com)
should be pointed to the VPS's public IP address in your DNS provider, such as
Cloudflare.

1.  Create File Structure: SSH into the VPS and create the necessary directory structure for

Pangolin's configuration and persistent data.
mkdir -p pangolin-stack/config/traefik
cd pangolin-stack

2.  Create Configuration Files: Create the three essential configuration files within this

directory structure.

○  docker-compose.yml: This file defines the three core services: pangolin (the main
application and UI), gerbil (the WireGuard management server), and traefik (the
underlying reverse proxy that handles HTTP traffic).
# docker-compose.yml
version: '3.8'

services:
  pangolin:
    image: fosrl/pangolin:latest
    container_name: pangolin
    restart: unless-stopped
    volumes:
      -./config:/app/config
    depends_on:
      - traefik
    networks:
      - pangolin_net

  gerbil:
    image: fosrl/gerbil:latest
    container_name: gerbil
    restart: unless-stopped
    volumes:
      -./config:/app/config
    cap_add:
      - NET_ADMIN
    sysctls:
      - net.ipv4.ip_forward=1
    networks:

      - pangolin_net

  traefik:
    image: traefik:v2.10
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      -./config/traefik:/etc/traefik
      -./config/letsencrypt:/letsencrypt
    networks:
      - pangolin_net

networks:
  pangolin_net:
    driver: bridge

○  config/config.yml: This is the main configuration for the Pangolin application itself.

# config/config.yml
dashboard_url: https://pangolin.your-domain.com # REPLACE
database:
  type: sqlite
  path: /app/config/db/db.sqlite

○  config/traefik/traefik_config.yml: This is the static configuration for Traefik, defining

entry points and the Let's Encrypt certificate resolver.
# config/traefik/traefik_config.yml
global:
  checkNewVersion: true
  sendAnonymousUsage: false

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  file:
    filename: /etc/traefik/dynamic_config.yml

    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@your-domain.com # REPLACE
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

○  config/traefik/dynamic_config.yml: This file defines how Traefik routes traffic to the

Pangolin services.
# config/traefik/dynamic_config.yml
http:
  routers:
    pangolin-dashboard:
      rule: "Host(`pangolin.your-domain.com`)" # REPLACE
      service: "pangolin-app"
      entryPoints:
        - websecure
      tls:
        certResolver: letsencrypt

  services:
    pangolin-app:
      loadBalancer:
        servers:
          - url: "http://pangolin:3001"

3.  Launch the Stack: With the configuration files in place, start the services using Docker

Compose.
sudo docker compose up -d

4.  Initial Setup: After a few moments for Traefik to obtain SSL certificates, navigate to

https://pangolin.your-domain.com. You will be prompted with an initial setup screen to
create the first administrator account.

Tutorial: Exposing a Containerized Service

Now, with Pangolin running, we can expose another service (e.g., a container running our
CRAWL4AI application with a simple API) without opening any new ports.

1.  Create a Site in Pangolin: Log in to the Pangolin dashboard. Navigate to "Sites" and
click "Add Site." Give the site a name (e.g., vps-docker-network). This represents the
isolated network where the target service resides. A Newt ID and Newt Secret will be
generated. Copy these securely.

2.  Deploy the Newt Client: Newt is Pangolin's client that establishes the secure tunnel. Add

it as a new service to the docker-compose.yml file on the VPS.
# Add this service to your docker-compose.yml

  newt:
    image: fosrl/newt:latest
    container_name: newt
    restart: unless-stopped
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.your-domain.com #
REPLACE
      - NEWT_ID=2ix2t8xk22ubpfy # REPLACE with your Newt ID
      -
NEWT_SECRET=nnisrfsdfc7prqsp9ewo1dvtvci50j5uiqotez00dgap0ii2 #
REPLACE with your Newt Secret
    networks:
      - pangolin_net
Restart the stack with sudo docker compose up -d. The newt container will connect to the
gerbil service, establishing the tunnel.

3.  Create a Resource in Pangolin: Navigate to "Resources" in the dashboard and click

"Add Resource."

○  Give it a name (e.g., Scraper-API).
○  Select the vps-docker-network site created earlier.
○  For the "Upstream URL," provide the internal Docker DNS name and port of the

target service (e.g., http://crawl4ai-container:8080).

○  Assign it a public subdomain (e.g., scraper.your-domain.com).
○  Click "Create Resource".

The crawl4ai-container service is now securely accessible at https://scraper.your-domain.com,
proxied through Pangolin's encrypted tunnel. Access can be further restricted using Pangolin's
built-in user, role, and policy management features.
The emergence of powerful, self-hosted infrastructure tools like Pangolin indicates a significant
trend among technically proficient users towards "sovereign infrastructure." While managed
cloud services offer convenience, they can introduce concerns regarding cost, flexibility, and
data privacy. Pangolin provides an alternative by enabling users to deploy an enterprise-grade,
"zero trust" security architecture on their own terms, retaining full control over their security
posture and access policies. The substantial community engagement with such projects
highlights a strong demand for tools that deliver sophisticated functionality without vendor
lock-in, emphasizing ownership and control as a counter-movement to the
"everything-as-a-service" model.
Concurrently, the economic viability of ARM-based servers, driven by offerings like Oracle's
Ampere A1 free tier, is disrupting the cloud hosting market. Historically dominated by x86
processors, the server landscape is now seeing ARM emerge as a power-efficient and
cost-effective alternative. Oracle's strategy to provide substantial ARM-based resources for free
is a clear move to accelerate adoption. While software compatibility was once a major hurdle,
the widespread use of containerization and the increasing availability of multi-architecture
Docker images are mitigating this challenge. This development lowers the financial barrier for
compute-intensive projects, enabling developers and small teams to access significant
resources at little to no cost, provided they operate within the ARM ecosystem.

The Agentic Layer: Supercharging Development with

Gemini and MCP Servers

AI-Assisted Coding with Gemini and GitHub Copilot

The modern development workflow for this stack is fundamentally enhanced by the integration
of powerful AI coding assistants directly within Visual Studio Code. Both Google's Gemini and
GitHub Copilot serve as invaluable partners, accelerating development, improving code quality,
and reducing cognitive load across all components of the architecture.

●  Setup: The integration begins by installing the respective extensions from the VS Code

Marketplace.

○  For Gemini, search for and install the "Gemini Code Assist" extension. After

installation, a sign-in process with a Google Account is required to activate the
service.

○  For GitHub Copilot, install the "GitHub Copilot" extension. This requires an active

GitHub Copilot subscription and involves signing in to a GitHub account to authorize
the extension.

●  Practical Use Cases for this Stack:

○  Generating Scraper Logic: When working on the CRAWL4AI scraper, a developer
can use a natural language comment or a chat prompt to generate complex logic.
For instance, a prompt like, // Using CRAWL4AI and JsonCssExtractionStrategy,
extract the title, date, and PDF link from list items with the class 'publication-item'
can produce a complete, syntactically correct code block, saving significant time.
○  Refactoring Data Pipelines: As the dlt pipeline evolves, it may require refactoring
for better error handling or logging. A developer can select the entire Python script,
invoke the inline chat feature (typically with Ctrl+I), and issue a command like,
"Refactor this pipeline to include try-except blocks around the scraper execution
and log any exceptions to a file." The AI will then propose a diff with the suggested
changes directly in the editor.

○  Debugging and Optimizing SQL: When interacting with the MotherDuck

database, complex SQL queries can be difficult to write or debug. A developer can
paste a query into the Gemini chat pane and ask, "Explain this DuckDB SQL query.
Are there any performance optimizations I can make, such as using a different join
type or creating a materialized view?" The AI can provide both an explanation and
an improved version of the query.

○  Generating Dockerfiles and Configurations: Creating configuration files for

Docker, Docker Compose, or Pangolin can be tedious. A prompt such as, "Create a
multi-stage Dockerfile for a Python FastAPI application. The first stage should
install dependencies using poetry, and the final stage should be a slim production
image," can generate a robust starting point for containerizing any of the stack's
services.

Understanding Agentic Workflows and the Model Context Protocol
(MCP)

While AI-assisted coding significantly boosts productivity, the next evolution is the transition from
AI assistants that suggest code to AI agents that can take actions. This leap is facilitated by
providing the LLM with access to a set of "tools" it can execute to interact with its environment,

and the Model Context Protocol (MCP) is the open standard that makes this possible.

●  What is MCP?: MCP is a standardized communication protocol that defines how an LLM
client (like the Gemini extension in VS Code) can interact with a tool-providing server. It
formalizes the process of:

1.  Discovery: The client asks the server what tools it has available.
2.  Schema Definition: The server responds with a list of tools, including their names,
descriptions of what they do, and a structured schema (often JSON Schema) of the
parameters they accept.

3.  Execution: The LLM, understanding the available tools from their descriptions, can
decide to call one to fulfill a user's request. It formats a request according to the
tool's schema, which the client sends to the server. The server executes the tool's
logic and returns the result to the LLM.

MCP effectively creates a standardized, interoperable API layer for AI agents. This allows
developers to build custom tools and expose them to any MCP-compatible LLM, creating an
extensible and powerful ecosystem for agentic workflows.

Tutorial: Building and Containerizing a Custom MCP Server with
FastMCP

This tutorial demonstrates how to build a custom MCP server that provides a tool for querying
the MotherDuck database. We will use FastMCP, a Python framework that simplifies MCP
server development.

●  Why FastMCP?: Building an MCP server from scratch requires handling the low-level
details of the JSON-RPC protocol. FastMCP abstracts this complexity away, allowing
developers to define tools by simply decorating standard Python functions. It
automatically generates the necessary schemas from Python type hints and docstrings,
dramatically accelerating development.

1.  Server Setup and Tool Creation: The following Python script (mcp_server.py) defines a

FastMCP server with a single tool, query_motherduck.
# mcp_server.py
import os
import duckdb
from fastmcp import FastMCP
from typing import List, Dict, Any

# It's best practice to load secrets from environment variables
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")
DATABASE_NAME = "educational_data_lake" # As created in the
previous section

# 1. Create the FastMCP server instance
mcp = FastMCP(name="DataStackAgentServer")

# 2. Define the tool using the @mcp.tool decorator
@mcp.tool
def query_motherduck(query: str) -> List]:
    """

    Executes a read-only SQL query against the MotherDuck database
    and returns the results as a list of dictionaries.

    :param query: The SQL query string to execute.
    """
    if not MOTHERDUCK_TOKEN:
        return

    connection_string =
f"md:{DATABASE_NAME}?motherduck_token={MOTHERDUCK_TOKEN}"

    try:
        print(f"Executing query: {query}")
        # Connect to MotherDuck and execute the query
        with duckdb.connect(connection_string) as con:
            result = con.execute(query).fetch_arrow_table()
            # Convert Apache Arrow table to list of dicts for JSON
serialization
            return result.to_pylist()
    except Exception as e:
        print(f"Error executing query: {e}")
        return [{"error": str(e)}]

# 3. Add the main block to run the server via HTTP
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
This script provides a direct, programmatic bridge between the AI agent and the data
warehouse. The mcp-server-motherduck repository serves as an excellent
production-grade reference for this type of implementation.

2.  Containerizing the Server: To deploy the MCP server on the VPS, it needs to be

containerized.

○

requirements.txt:
fastmcp
duckdb

○  Dockerfile:

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server.py.

# Expose the port the server will run on
EXPOSE 8000

# The command to run the server
CMD ["python", "mcp_server.py"]

3.  Running the Server with Docker Compose: Add the MCP server to the main

docker-compose.yml file to run it alongside the other services.
# In your main docker-compose.yml
services:
  #... other services like pangolin, newt, etc.
  mcp-server:
    build:./path/to/mcp_server_directory
    container_name: mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000" # Expose port 8000 to the VPS host
    environment:
      - MOTHERDUCK_TOKEN=${MOTHERDUCK_TOKEN} # Pass token from
an.env file
    networks:
      - pangolin_net

Tutorial: Configuring VS Code to Use the Custom MCP Server

With the server running in a Docker container on the VPS, the final step is to configure the
Gemini extension in the local VS Code environment to connect to it.

1.  Configuration File Location: VS Code can be configured to use MCP servers via a
workspace-specific .vscode/mcp.json file. This is the recommended approach for
project-specific tools.

2.  Connecting via HTTP Transport: Since the Docker container's port 8000 is exposed to
the VPS host, the MCP server is accessible over the network. The .vscode/mcp.json file
should be configured to connect to this HTTP endpoint.
//.vscode/mcp.json
{
    "servers": {
        "custom_data_agent": {
            "type": "http",
            "url": "http://<YOUR_VPS_PUBLIC_IP>:8000/mcp/"
        }
    }
}
After creating or saving this file, VS Code may require a reload. The Gemini extension will
then automatically discover the server and its query_motherduck tool.

3.  Invoking the Tool: Now, from the Gemini chat pane in VS Code, the developer can

directly invoke the custom tool using the @ syntax.User Prompt: @custom_data_agent
What are the top 5 most common exam subjects in the dataset?Agent's Thought
Process & Actions:

1.  Gemini: "The user wants to query the dataset. I have a tool called

query_motherduck provided by the @custom_data_agent server that can execute

SQL queries."

2.  Gemini: "I will formulate a SQL query to answer the user's question."
3.  Gemini triggers tool call: query_motherduck(query="SELECT exam_subject,

COUNT(*) as count FROM irish_exams.exam_results GROUP BY exam_subject
ORDER BY count DESC LIMIT 5;")

4.  VS Code: Sends this request to the MCP server at
http://<YOUR_VPS_PUBLIC_IP>:8000/mcp/.

5.  MCP Server: Executes the Python function, connects to MotherDuck, runs the

query, and gets the result.

6.  MCP Server: Returns the result (e.g., [{'exam_subject': 'Mathematics', 'count':

100},...]) as a JSON response.

7.  VS Code: Passes the result back to Gemini.
8.  Gemini: "I have the results from the database. I will now format this into a natural

language answer for the user."
Gemini's Final Response: "The top 5 most common exam subjects are:

1.  Mathematics (100 entries)
2.  English (98 entries) ..."

This demonstrates a complete, end-to-end agentic workflow where the AI seamlessly transitions
from understanding natural language to executing code on remote infrastructure to synthesizing
a final answer.
The MCP ecosystem, while nascent, is growing rapidly. The following table compares several
noteworthy, well-documented open-source implementations that can serve as excellent starting
points or production-ready solutions.
Project Name
FastMCP

Primary Language Key Features
Python

Ease of Use
Very High

philschmid/gemi
ni-mcp-server

Python

motherduckdb/m
cp-server-mother
duck

Python

centminmod/gem
ini-cli-mcp-server

Python

Decorator-based,
automatic schema
generation,
minimal
boilerplate.
Simple, focused
implementation of
Gemini-specific
tools (web search).

High

High

Low (Complex)

Production-ready,
specialized server
for
DuckDB/MotherDu
ck interaction.
Enterprise-grade,
highly modular
server with 30+
tools, Redis
caching, security
features, and
OpenRouter
integration.

Best For...
Rapidly
prototyping and
building custom
Python-based
tools.
Learning the
basics of MCP
with Gemini and a
simple remote
deployment.
Directly integrating
database query
capabilities into an
AI agent.

Building complex,
multi-tool,
multi-LLM agentic
systems for
production.

The emergence of the Model Context Protocol signifies a pivotal moment in the evolution of AI
development, suggesting a future governed by an "Operating System for AI Agents." Just as a
traditional OS provides a standardized set of system calls for applications to interact with
hardware, MCP provides a standardized API layer for LLMs to interact with external tools and
data. This abstraction moves AI models from being passive text generators to active participants
in a computational environment. This will likely lead to a new ecosystem of "AI
drivers"—specialized MCP servers—where the value and differentiation of an AI system will
depend less on the underlying model and more on the richness and power of the tool
ecosystem it can access.
This new paradigm also reframes the role of the developer. The workflow is shifting from a
human-centric model where AI provides assistance, to an AI-centric model where the human
provides supervision and enablement. The developer's primary task evolves from writing every
line of application logic to architecting and implementing the high-level goals and the specific
tools (via MCP servers) that empower an AI agent to achieve those goals. This represents a
fundamental and profound shift in the nature of software creation.

Synthesis and Strategic Recommendations

Summary of the Architecture and Key Learnings

This report has detailed a powerful, modern, and cost-effective architecture for AI-driven data
acquisition and analysis. The stack is intentionally modular, combining best-of-breed
open-source and low-cost services to create a whole that is greater than the sum of its parts.
The workflow begins with CRAWL4AI, an advanced scraping tool that extracts clean,
LLM-ready data from dynamic and authenticated websites. This data is seamlessly fed into a dlt
pipeline, a declarative Python framework that automates data loading, normalization, and
schema management. The pipeline's destination is a disaggregated data warehouse, using
Cloudflare R2 for zero-egress, S3-compatible object storage and MotherDuck's DuckLake
feature for serverless, in-situ SQL analytics.
This entire software stack is deployed in containers on a low-cost Hetzner or free-tier Oracle
Cloud VPS. Secure external access is managed by Pangolin, a self-hosted tunnel and
identity-aware proxy. The development lifecycle is accelerated within VS Code using AI
assistants like Gemini 2.5 Pro, which are further empowered by a custom MCP Server that
grants the AI agent direct, programmatic access to the system's components, such as the
MotherDuck database.
Key learnings from this architectural exploration include the immense economic and
performance advantages of disaggregating storage and compute, the power of Python-native
tools like dlt to simplify data engineering, and the transformative potential of agentic workflows
enabled by the Model Context Protocol.

Operationalizing the Stack: Monitoring, Maintenance, and Scaling

Deploying this stack into a production or semi-production environment requires consideration of
ongoing operations.
●  Monitoring:

○  Pipeline Health: dlt offers built-in telemetry and alerting capabilities that can be
configured to send notifications (e.g., to Slack or email) upon pipeline success or

○

failure. This provides crucial visibility into the health of the data ingestion process.
Infrastructure Resources: The VPS's CPU, memory, and disk usage must be
monitored. For a more sophisticated setup than standard Linux tools like htop and
df, a server management tool like Komodo can be deployed. Komodo provides a
web UI to connect to multiple servers, monitor system resources, and manage
Docker containers and deployments, offering a centralized control plane for the
infrastructure.

○  Service Logs: Centralized logging for all Docker containers (CRAWL4AI, dlt

runner, Pangolin, MCP server) is essential for debugging. This can be achieved
using the Docker logging drivers to forward logs to a service like Grafana Loki or a
simple file-based aggregation.

●  Maintenance:

○  Schema Changes: One of the primary advantages of dlt is its ability to handle

schema evolution automatically. When CRAWL4AI starts extracting a new field, dlt
will detect it and issue the appropriate ALTER TABLE commands to the destination,
minimizing manual intervention.

○  Software Updates: All components are containerized, simplifying updates.

Regularly pulling the latest Docker images for CRAWL4AI, Pangolin, and other
base images, and then redeploying with docker compose up -d --build, is the
standard maintenance procedure.

○  Credential Management: Secrets such as API keys and database tokens should

be managed securely. For Docker Compose, this means using .env files that are
excluded from version control. For more advanced setups, a dedicated secrets
manager like HashiCorp Vault could be integrated.

●  Scaling:

○  Storage and Analytics: The Cloudflare R2 and MotherDuck layers are serverless

and scale automatically to handle virtually any data volume. This part of the
architecture does not represent a scaling bottleneck.
Ingestion: The primary bottleneck is the single VPS running the CRAWL4AI
scraper. Scaling the ingestion process can be approached in several ways:

○

1.  Vertical Scaling: Upgrading the Hetzner/Oracle VPS to a more powerful

instance with more CPU cores and RAM.

2.  Horizontal Scaling: For large-scale scraping, a single VPS will be

insufficient. The architecture can be extended to a fleet of scraping nodes. A
central instance could run a task queue (e.g., RabbitMQ, Redis), and
multiple, cheap Hetzner cloud servers could act as workers, each running a
CRAWL4AI container that pulls jobs from the queue. Komodo could be used
to manage the deployment and monitoring of this fleet of worker nodes.

Future Outlook and Potential Extensions

The architecture presented here serves as a robust foundation that can be extended in
numerous directions.

●  Data Visualization and Serving: The data stored in MotherDuck can be easily

connected to business intelligence and visualization tools. A Streamlit or Dash application
could be built to provide an interactive dashboard for exploring the scraped educational
data. Alternatively, a lightweight API could be built (e.g., with FastAPI) that queries
MotherDuck and serves the data to other applications. This API could itself be

containerized and exposed securely through Pangolin.

●  Advanced AI Applications: The collected and cleaned dataset is a valuable asset for

more advanced AI tasks.

○  Fine-Tuning: The structured Markdown output from CRAWL4AI is ideal for
fine-tuning a smaller, specialized language model on the specific domain of
educational resources, potentially creating a highly effective chatbot or
question-answering system for students.

○  RAG Implementation: The data can be chunked, embedded, and stored in a
vector database to serve as the knowledge base for a Retrieval-Augmented
Generation system, allowing users to ask natural language questions about the
scraped content.

●  Deepening Agentic Integration: The custom MCP server can be expanded with more
powerful tools. For example, a tool could be created to trigger a dlt pipeline run on
demand (@agent.trigger_pipeline('irish_exams')), or another tool could be built to modify
the CRAWL4AI scraping configuration and redeploy the container. This would grant the
Gemini agent end-to-end control over the data lifecycle, moving closer to a fully
autonomous data acquisition system.

Final Recommendations

The software stack detailed in this report represents a highly capable, modern, and
economically efficient solution for the stated goal of scraping, processing, and hosting
educational resources. It is exceptionally well-suited for technically proficient individuals or small
teams who value control, flexibility, and open standards over the locked-in convenience of
monolithic cloud platforms.
The primary trade-off is one of operational responsibility versus cost and control. While this
self-hosted architecture can be operated for a fraction of the cost of a fully managed cloud
solution (and potentially for free), it requires a higher degree of technical expertise to set up and
maintain. The learning curve for new concepts like the Model Context Protocol is non-trivial, but
the power it unlocks in creating truly intelligent, agentic systems is immense.
This architecture is more than just a collection of tools; it is an embodiment of several key trends
shaping the future of data and AI engineering. The move towards disaggregated, open-source
components, the simplification of data pipelines through Python-native frameworks, and the rise
of AI agents as first-class participants in the development and operational loop all point to a
future where powerful data capabilities are more accessible, customizable, and intelligent than
ever before. For the user with the requisite skills, this stack provides a formidable platform for
innovation.

Works cited

1. Cloudflare R2 | Zero Egress Fee Object Storage,
https://www.cloudflare.com/developer-platform/products/r2/ 2. Pricing - R2 - Cloudflare Docs,
https://developers.cloudflare.com/r2/pricing/ 3. fosrl/pangolin: Identity-Aware Tunneled Reverse
Proxy ... - GitHub, https://github.com/fosrl/pangolin 4. Pangolin (beta): Your own tunneled
reverse proxy with authentication (Cloudflare Tunnel replacement) : r/selfhosted - Reddit,
https://www.reddit.com/r/selfhosted/comments/1hujxxo/pangolin_beta_your_own_tunneled_reve
rse_proxy/ 5. Crawling with Crawl4AI. Web scraping in Python has… | by Harisudhan.S -
Medium,

https://medium.com/@speaktoharisudhan/crawling-with-crawl4ai-the-open-source-scraping-bea
st-9d32e6946ad4 6. unclecode/crawl4ai: Crawl4AI: Open-source LLM Friendly ... - GitHub,
https://github.com/unclecode/crawl4ai 7. dlt: the data loading library for Python - dltHub,
https://dlthub.com/product/dlt 8. Moving Data with Python and dlt: A Guide for Data Engineers -
DataCamp, https://www.datacamp.com/tutorial/python-dlt 9. MotherDuck / DuckLake | dlt Docs -
dltHub, https://dlthub.com/docs/dlt-ecosystem/destinations/motherduck 10. DuckLake |
MotherDuck Docs, https://motherduck.com/docs/integrations/file-formats/ducklake/ 11. Secure
vps hosting made in Germany - Hetzner, https://www.hetzner.com/cloud-made-in-germany/ 12.
Oracle Cloud Free Tier, https://www.oracle.com/cloud/free/ 13. Docker Compose - Pangolin
Docs, https://docs.digpangolin.com/self-host/manual/docker-compose 14. Gemini Code Assist |
AI coding assistant, https://codeassist.google/ 15. philschmid/gemini-mcp-server - GitHub,
https://github.com/philschmid/gemini-mcp-server 16. Gemini CLI Tutorial Series — Part 8:
Building your own MCP Server - Medium,
https://medium.com/google-cloud/gemini-cli-tutorial-series-part-8-building-your-own-mcp-server-
74d6add81cca 17. Session Management - Crawl4AI Documentation (v0.7.x),
https://docs.crawl4ai.com/advanced/session-management/ 18. State Exams - ST. PATRICK'S
COMPREHENSIVE SCHOOL, https://www.stpatrickscomprehensive.ie/state-exams.html 19.
Identity Based Crawling - Crawl4AI Documentation (v0.7.x),
https://docs.crawl4ai.com/advanced/identity-based-crawling/ 20. Hooks & Auth - Crawl4AI
Documentation (v0.7.x), https://docs.crawl4ai.com/advanced/hooks-auth/ 21. Teaching
Resources: BBC Bitesize Computer Science,
https://computing.hias.hants.gov.uk/mod/url/view.php?id=112&forceview=1 22. Useful websites
and resources - St Thomas's Centre,
https://www.stthomasscentre.com/attachments/download.asp?file=523&type=docx 23. Create
and Submit a robots.txt File | Google Search Central | Documentation,
https://developers.google.com/search/docs/crawling-indexing/robots/create-robots-txt 24. What
is robots.txt? | Robots.txt file guide - Cloudflare,
https://www.cloudflare.com/learning/bots/what-is-robots-txt/ 25. Robots.txt Introduction and
Guide | Google Search Central | Documentation,
https://developers.google.com/search/docs/crawling-indexing/robots/intro 26. robots.txt
configuration - Security - MDN,
https://developer.mozilla.org/en-US/docs/Web/Security/Practical_implementation_guides/Robots
_txt 27. What are robots.txt files? Featuring 15 of our favourites - MCM.click,
https://mcm.click/what-are-robots-txt-files-featuring-15-of-our-favourites/ 28. An introduction to
robots.txt files - Digital.gov, https://digital.gov/resources/introduction-robots-txt-files 29. DuckDB
Data Engineering Glossary: data load tool (dlt) - MotherDuck,
https://motherduck.com/glossary/data%20load%20tool%20(dlt)/ 30. Cloud storage and
filesystem | dlt Docs - dltHub, https://dlthub.com/docs/dlt-ecosystem/destinations/filesystem 31.
Cloudflare R2 Import - DuckDB,
https://duckdb.org/docs/stable/guides/network_cloud_storage/cloudflare_r2_import.html 32. S3
API Support - DuckDB, https://duckdb.org/docs/stable/core_extensions/httpfs/s3api.html 33. dlt -
MotherDuck, https://motherduck.com/ecosystem/dlt/ 34. Data Warehousing How-to |
MotherDuck Docs, https://motherduck.com/docs/key-tasks/data-warehousing/ 35. Cloudflare R2
| MotherDuck Docs, https://motherduck.com/docs/integrations/cloud-storage/cloudflare-r2/ 36.
Hetzner | Review, Pricing & Alternatives - GetDeploying, https://getdeploying.com/hetzner 37.
Cheap hosted VPS by Hetzner: our cloud hosting services, https://www.hetzner.com/cloud 38.
How to Set Up a Free Oracle Cloud VM for Web Development (2025 Guide) - Hackernoon,
https://hackernoon.com/how-to-set-up-a-free-oracle-cloud-vm-for-web-development-2025-guide

39. oracle-cloud-free-tier-guide - GitHub Gist,
https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd 40. Always Free
Resources - Oracle Help Center,
https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm 41.
unclecode/crawl4ai - Docker Image, https://hub.docker.com/r/unclecode/crawl4ai 42. Creating a
VM on Oracle Cloud(Using Always Free Resources) - Spoon Consulting,
https://blog.spoonconsulting.com/creating-a-vm-on-oracle-cloud-using-always-free-resources-8a
e23c507403 43. Setup Forever Free Oracle 24 GB RAM ARM-based Ampere Cloud - YouTube,
https://www.youtube.com/watch?v=BUxyD-IXP1s 44. Better Than Cloudflare Tunnels? -
Pangolin Guide - YouTube, https://www.youtube.com/watch?v=8VdwOL7nYkY 45. How to
Configure a Hetzner Domains DNS Records for Cloudflare - Blunix GmbH,
https://www.blunix.com/blog/how-to-configure-a-hetzner-domains-dns-records-for-cloudflare.htm
l 46. Pangolin: Easy Self-Hosted Tunneled Reverse Proxy with Built-in ...,
https://noted.lol/pangolin/ 47. Install and Configure Pangolin - Open Source is Awesome,
https://wiki.opensourceisawesome.com/books/self-hosted-tunnels/page/install-and-configure-pa
ngolin 48. Set up Gemini Code Assist for individuals - Google for Developers,
https://developers.google.com/gemini-code-assist/docs/set-up-gemini 49. Gemini Code Assist -
Visual Studio Marketplace,
https://marketplace.visualstudio.com/items?itemName=Google.geminicodeassist 50. GitHub
Copilot in VS Code, https://code.visualstudio.com/docs/copilot/overview 51. GitHub Copilot: Fly
With Python at the Speed of Thought, https://realpython.com/github-copilot-python/ 52. Gemini
Code Assist tools overview - Google for Developers,
https://developers.google.com/gemini-code-assist/docs/tools-agents/tools-overview 53.
Quickstart - FastMCP, https://gofastmcp.com/getting-started/quickstart 54. How to Create an
MCP Server in Python - FastMCP, https://gofastmcp.com/tutorials/create-mcp-server 55. How to
Build MCP Servers in Python: Complete FastMCP Tutorial for AI Developers,
https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python 56.
motherduckdb/mcp-server-motherduck: MCP server for ... - GitHub,
https://github.com/motherduckdb/mcp-server-motherduck 57. How to Use the DuckDB MCP
Server - Apidog, https://apidog.com/blog/duckdb-mcp-server/ 58. How to Use DuckDB MCP
Server - Apidog, https://apidog.com/blog/motherduck-duckdb-mcp-server-guide/ 59. Use MCP
servers in VS Code, https://code.visualstudio.com/docs/copilot/customization/mcp-servers 60.
Use agentic chat as a pair programmer | Gemini Code Assist - Google for Developers,
https://developers.google.com/gemini-code-assist/docs/use-agentic-chat-pair-programmer 61.
What is Komodo? | Komodo, https://komo.do/docs/intro



> Source: `docs/data_engineering/crawl4ai/crawl4ai-index.md`

# Crawl4AI Codebase Analysis - Complete Index

## Overview

This analysis explores the design patterns, data models, extension points, and common usage patterns of the Crawl4AI framework - a modern, AI-native web scraping and content extraction library.

## Documents Generated

### 1. CRAWL4AI_SUMMARY.md (Quick Reference - 285 lines)
**Purpose:** Executive summary with quick lookup tables

**Sections:**
- Core Design Patterns (6 patterns with use cases)
- Primary Data Model (CrawlResult structure diagram)
- Extension Points (5 categories with examples)
- Configuration Hierarchy (minimal to full configs)
- Design Principles (5 key concepts)
- Common Patterns Quick Reference table
- Integration Ecosystem
- Best Practices Checklist
- Code Examples (4 practical examples)

**Best for:** Quick lookups, pattern matching, getting started

---

### 2. CRAWL4AI_ANALYSIS.md (Comprehensive Guide - 758 lines)
**Purpose:** Deep technical analysis with detailed explanations

**Sections:**

#### 1. DESIGN PATTERNS (Section 1.1-1.6)
- **Strategy Pattern:** 6 extraction/crawl strategies with details
- **Builder Pattern:** Configuration hierarchy explanation
- **Context Manager:** Resource lifecycle management
- **Hook/Callback:** Lifecycle extension mechanism
- **Factory Pattern:** Content-type routing (implicit)
- **Composite Pattern:** Multiple strategy composition

#### 2. DATA MODELS & ONTOLOGIES (Section 2.1-2.5)
- **CrawlResult:** Primary output dataclass structure
- **MarkdownGenerationResult:** Markdown variants
- **CrawlStatus:** Success/error tracking
- **Configuration Ontology:** BrowserConfig & CrawlerRunConfig details
- **Media & Asset Ontology:** Image/video extraction structure
- **Schema/Type System:** Pydantic validation patterns
- **Data Transformation Pipeline:** Content flow diagram

#### 3. EXTENSION POINTS (Section 3.1-3.8)
- Extraction Strategy Customization
- Hook/Callback System (Login automation example)
- JavaScript Execution Integration
- Deep Crawling Customization
- Content Filtering & Post-Processing
- Browser Profiling & Session Management
- Provider Customization (LLM)
- Integration Points (dlt, Docling, Agno)

#### 4. COMMON USAGE PATTERNS (Section 4.1-4.10)
1. Basic Content Extraction
2. Structured Data Extraction (CSS-Based)
3. LLM-Powered Semantic Extraction
4. Authenticated/Protected Content
5. Dynamic Content with JavaScript
6. Deep Crawling (Recursive Discovery)
7. PDF Parsing
8. Integration with dlt Pipeline
9. Content Pruning for LLM Consumption
10. Multi-URL Crawling with Comparison

#### 5. BEST PRACTICES (Section 5.1-5.5)
- Performance Optimization (5 points)
- Reliability (5 points)
- Data Quality (5 points)
- Cost Management (5 points)
- Ethical & Legal (5 points)

#### 6. CONFIGURATION SUMMARY (Section 6)
- Minimum working configuration
- Full-featured configuration

#### 7. INTEGRATION ECOSYSTEM (Section 7)
- Upstream sources (Data input)
- Downstream destinations (Data output)

**Best for:** Deep understanding, architecture learning, advanced implementations

---

## Key Findings Summary

### Design Patterns Identified

| Pattern | Frequency | Key Classes |
|---------|-----------|------------|
| Strategy | HIGH | ExtractStrategy variants, DeepCrawlStrategy variants |
| Builder | HIGH | BrowserConfig, CrawlerRunConfig |
| Context Manager | HIGH | AsyncWebCrawler |
| Hook/Callback | MEDIUM | BrowserConfig.hooks |
| Factory | MEDIUM | Content-type based routing |
| Composite | MEDIUM | Multiple strategy combination |

### Core Data Model (CrawlResult)

The framework centers on a single, comprehensive output object:
- **Navigation info:** url, status
- **Content:** markdown (3 variants), raw_html
- **Extracted data:** structured JSON from strategies
- **Media:** images, videos, documents
- **Metadata:** page metadata, timestamps
- **Optional outputs:** PDF, screenshots, MHTML

### Extension Mechanisms (In Priority Order)

1. **Extraction Strategies** - Swappable approaches (CSS, LLM, PDF)
2. **Hooks/Callbacks** - Lifecycle injection points
3. **JavaScript Execution** - Dynamic content handling
4. **Deep Crawl Strategies** - Recursive discovery
5. **Content Filtering** - Post-processing

### Design Philosophy

1. **LLM-First:** Everything optimized for AI consumption
2. **Async-Native:** High concurrency, non-blocking
3. **Flexible:** Multiple extraction approaches, swappable at runtime
4. **Extensible:** Hooks, custom strategies, plugins
5. **Practical:** Real-world features (auth, JS, PDF, proxies)

---

## Usage Patterns Matrix

### By Complexity Level

**Beginner (Level 1):**
- Basic URL crawl → markdown
- Simple CSS extraction

**Intermediate (Level 2):**
- LLM extraction with schemas
- Authentication via profiles
- Content filtering

**Advanced (Level 3):**
- Deep crawling strategies
- Custom hooks for dynamic flows
- Integration with dlt pipelines
- Multi-modal extraction

### By Source Type

| Source | Recommended Approach | Key Components |
|--------|---------------------|-----------------|
| Static HTML | CSS Extraction | `JsonCssExtractionStrategy` |
| Dynamic JS | JS Injection | `js_code` + `wait_for` |
| Protected Site | Hook + Session | `on_page_context_created` + profile |
| PDF Document | PDF Strategy | Auto-detection + strategies |
| Multi-page | Deep Crawl | `BFSDeepCrawlStrategy` |
| Semantic Data | LLM Extraction | `LLMExtractionStrategy` + Pydantic |

### By Destination

| Destination | Integration | Key Pattern |
|-------------|-------------|------------|
| Data Warehouse | dlt | @dlt.resource wrapper |
| Vector DB | Direct | Use `extracted_data` or markdown |
| LLM/RAG | Direct | Use `fit_markdown` |
| Document Processor | Custom | Post-process result |
| AI Agent | Tool | Agno Crawl4aiTools wrapper |

---

## Configuration Quick Reference

### Most Important Settings

**BrowserConfig (persistent across runs):**
```python
headless=True                    # Headless mode for servers
use_managed_browser=True         # Persistent profile for sessions
user_data_dir="./profiles"       # Where to store browser profiles
browser_type="chromium"          # Playwright browser type
hooks={...}                      # Lifecycle injection points
```

**CrawlerRunConfig (per crawl):**
```python
url="https://..."               # Target URL (required)
extraction_strategy=...         # How to extract (Strategy pattern)
js_code="..."                   # Custom JavaScript
wait_for="selector:..."         # Wait condition
delay=2.0                       # Rate limiting (seconds)
css_filters=[...]               # Remove noise
deep_crawl_strategy=...         # Recursive crawling
```

---

## Common Gotchas & Solutions

### Performance Issues
- **Gotcha:** Using LLM extraction for everything
- **Solution:** CSS first, LLM for complex fields only

### Cost Explosion (LLM)
- **Gotcha:** Running LLM on every page
- **Solution:** Use CSS extraction, batch LLM calls, cache results

### Blocked/Rate-Limited
- **Gotcha:** No delays between requests
- **Solution:** Use `delay` parameter, respect robots.txt

### Dynamic Content Missing
- **Gotcha:** Expecting HTML without JS execution
- **Solution:** Use `js_code` + `wait_for` to trigger loading

### Authentication Issues
- **Gotcha:** Credentials in code
- **Solution:** Use `BrowserProfiler` with manual login, then reuse

---

## File References in Repository

> **Note**: File paths below are relative to the repository root.

### Core Analysis Files
- **`crawl4ai-summary.md`** - Quick reference (in this directory)
- **`crawl4ai.md`** - Deep analysis (in this directory)
- **`crawl4ai-index.md`** - This file (index & overview)

### Research/Reference Files
- **`crawl4ai-dlt.md`** - dlt integration guide (in this directory)

### Integration Examples
- **`infrastructure/compose/crawl4ai/`** - Docker compose setup for Crawl4AI

---

## Recommended Reading Order

### For Quick Start (30 minutes)
1. This INDEX file (overview)
2. CRAWL4AI_SUMMARY.md (key concepts)
3. "Code Examples" section in SUMMARY

### For Understanding Design (2 hours)
1. CRAWL4AI_INDEX.md (context)
2. CRAWL4AI_ANALYSIS.md - Sections 1-2 (patterns & data models)
3. Code examples from SUMMARY

### For Implementation (varies)
1. Use SUMMARY as reference for your specific use case
2. Check ANALYSIS for deep patterns
3. Look up examples in Section 4 of ANALYSIS
4. Reference research files for integration details

---

## Key Takeaways

1. **Crawl4AI = Strategy Pattern Framework**
   - Swappable extraction approaches
   - Composable strategies for complex scenarios
   - LLM-native design philosophy

2. **Simple API, Powerful Extensibility**
   - Start with `AsyncWebCrawler(config=BrowserConfig()).arun(CrawlerRunConfig())`
   - Extend with hooks, strategies, filters as needed
   - Integrates seamlessly with modern data stacks

3. **Built for AI/ML from Ground Up**
   - LLM-ready Markdown output
   - Pydantic schema validation
   - Type-safe extraction
   - RAG/fine-tuning ready

4. **Production-Ready Features**
   - Authentication (profiles, hooks)
   - Dynamic content (JS injection)
   - Recursive crawling (BFS/DFS)
   - Cost management (CSS-first, batching)

5. **Rich Integration Ecosystem**
   - dlt pipelines → data warehouses
   - Vector DBs → semantic search
   - LLM APIs → structured extraction
   - AI agents → autonomous workflows

---

## Document Statistics

| Metric | Value |
|--------|-------|
| Total Lines | 1,043 |
| Analysis Document | 758 lines |
| Summary Document | 285 lines |
| Design Patterns Identified | 6 major |
| Extension Points | 8 categories |
| Usage Patterns | 10 detailed examples |
| Best Practices | 25+ actionable items |
| Code Examples | 20+ snippets |

---

Last Updated: 2025-11-17
Analysis Depth: Comprehensive (from research documents + integration examples)


> Source: `docs/data_engineering/crawl4ai/crawl4ai-openapi-research.md`

# Crawl4AI OpenAPI Specification Research

**Date:** 2025-11-22
**Repository:** https://github.com/unclecode/crawl4ai
**Documentation:** https://docs.crawl4ai.com/
**Stars:** 53.7k+ (as of research date)

## Executive Summary

**Does an official OpenAPI specification exist?** **YES**, but it's dynamically generated by FastAPI.

Crawl4AI is an open-source LLM-friendly web crawler that provides a comprehensive REST API built with FastAPI. While there isn't a static OpenAPI specification file committed to the repository, the FastAPI server automatically generates OpenAPI documentation that can be accessed when the service is running.

## OpenAPI Specification Access

### Method 1: Running Docker Container (Recommended)

When you run the Crawl4AI Docker container, the OpenAPI specification is automatically available:

```bash
docker pull unclecode/crawl4ai:latest
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g unclecode/crawl4ai:latest
```

**Available endpoints:**
- **OpenAPI JSON:** `http://localhost:11235/openapi.json`
- **Swagger UI (Interactive Docs):** `http://localhost:11235/docs`
- **ReDoc (Alternative Docs):** `http://localhost:11235/redoc`
- **Interactive Playground:** `http://localhost:11235/playground`

### Method 2: Third-Party Platforms

**Apify Platform:**
- Primary: https://apify.com/janbuchar/crawl4ai/api/openapi
- Alternative (AI Web Scraper): https://apify.com/raizen/ai-web-scraper/api/openapi

These are wrapper implementations that expose Crawl4AI functionality through Apify's platform.

### Method 3: Postman Collection

A community-maintained Postman collection is available:
- **Collection URL:** https://www.postman.com/pixelao/pixel-public-workspace/collection/c26yn3l/crawl4ai-api

*Note: This link returned a 503 error during research, so availability may vary.*

## OpenAPI Specification Details

### Version Information

- **OpenAPI Version:** Likely 3.0.x or 3.1.x (FastAPI supports both)
- **Crawl4AI Version:** 0.7.x (current as of research)
- **Framework:** FastAPI
- **Server Port:** 11235 (default)

### Architecture

**Repository Structure:**
```
crawl4ai/
├── deploy/docker/
│   ├── server.py          # FastAPI server with endpoint definitions
│   ├── api.py             # API endpoint handler functions
│   ├── schemas.py         # Pydantic models for request/response
│   └── config.yml         # Server configuration
```

**Key Components:**
- **FastAPI Server:** Provides automatic OpenAPI documentation
- **Redis:** Task management and caching
- **Supervisord:** Process management in Docker
- **Gunicorn:** WSGI server for production deployment

## API Endpoints Coverage

### Core Crawling Endpoints

#### POST /crawl
**Description:** Synchronous crawling of one or more URLs
**Parameters:**
- `urls` (array): URLs to crawl
- `browser_config`: Browser configuration settings
- `crawler_config`: Crawler configuration settings
- `extraction_strategy`: Strategy for content extraction
- `hooks`: Custom hook functions

**Returns:** `CrawlResult` with markdown, HTML, extracted content, and links

#### POST /crawl/stream
**Description:** Streaming crawl results in NDJSON format
**Parameters:** Same as `/crawl` with `stream: true`
**Returns:** Line-delimited JSON results as they complete

#### POST /crawl/job
**Description:** Asynchronous job submission with webhook support
**Parameters:**
- `urls`: URLs to crawl
- `cache_mode`: Caching strategy
- `extraction_strategy`: Content extraction method
- `webhook_config`: Webhook configuration for notifications

**Returns:**
```json
{
  "task_id": "crawl_1698765432",
  "message": "Crawl job submitted"
}
```

### Specialized Processing Endpoints

#### POST /html
**Description:** Crawls URL and returns preprocessed HTML optimized for schema extraction

#### POST /screenshot
**Description:** Captures full-page PNG screenshots
**Parameters:**
- `screenshot_wait_for`: Wait condition before capturing

#### POST /pdf
**Description:** Generates PDF documents from URLs

#### POST /execute_js
**Description:** Runs JavaScript snippets on pages
**Parameters:**
- `scripts`: JavaScript code to execute

#### POST /llm/job
**Description:** Asynchronous LLM extraction
**Parameters:**
- `url`: Target URL
- `q`: Query/question for LLM
- `provider`: LLM provider (e.g., OpenAI, Anthropic)
- `schema`: Expected output schema

### Job Management & Monitoring

#### GET /job/{task_id}
**Description:** Retrieve job status and results
**Path Parameters:** `task_id` - Job identifier

#### GET /health
**Description:** Server health status check

#### GET /metrics
**Description:** Prometheus-format metrics endpoint

#### GET /hooks/info
**Description:** Information about available hook points and signatures

#### GET /mcp/schema
**Description:** MCP tool schemas and parameters

### MCP (Model Context Protocol) Endpoints

#### GET /mcp/sse
**Description:** Server-Sent Events endpoint for MCP connections

#### WebSocket /mcp/ws
**Description:** WebSocket endpoint for MCP
**URL:** `ws://localhost:11235/mcp/ws`

### Configuration & Utility

#### GET /playground
**Description:** Interactive web interface for testing API requests
**Features:**
- Configure CrawlerRunConfig and BrowserConfig
- Test crawling operations directly
- Generate corresponding JSON for REST API requests

## Key Features

### 1. Dual API Approaches

**Synchronous API (`/crawl`):**
- Client waits for entire crawl to complete
- Immediate results returned in response
- Suitable for simple, quick crawls

**Asynchronous Job Queue API (`/crawl/job`, `/llm/job`):**
- Submit jobs and receive task ID
- Poll for results or use webhooks
- Real-time notifications when jobs finish
- Better for long-running operations

### 2. Webhook Support

**Introduced in v0.7.6:**
- Real-time notifications for `/crawl/job` and `/llm/job`
- Exponential backoff retry mechanism
- Custom headers support
- Flexible delivery modes

### 3. Authentication

**JWT Token Authentication:**
- Built-in security for API access
- Token-based request authorization

### 4. Content Output Formats

- **Markdown:** LLM-ready clean markdown
- **JSON:** Structured data extraction
- **HTML:** Preprocessed HTML
- **PDF:** Document generation
- **Screenshots:** PNG images

### 5. Extraction Strategies

- CSS Selector-based extraction
- XPath-based extraction
- LLM-powered extraction
- Repeated pattern parsing

### 6. Browser Control

- Hooks support
- Proxy configuration
- Stealth modes
- Session re-use
- JavaScript execution

## Configuration Format

### JSON Structure for API Calls

When calling the REST API directly, configuration objects must be converted to JSON with this pattern:

```json
{
  "type": "ClassName",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Example Request

```json
{
  "urls": ["https://example.com"],
  "crawler_config": {
    "type": "CrawlerRunConfig",
    "params": {
      "cache_mode": "ENABLED",
      "verbose": true
    }
  },
  "browser_config": {
    "type": "BrowserConfig",
    "params": {
      "headless": true,
      "viewport_width": 1920,
      "viewport_height": 1080
    }
  }
}
```

## Python SDK vs REST API

### Python SDK (Primary Interface)

**Installation:**
```bash
pip install -U crawl4ai
crawl4ai-setup
crawl4ai-doctor  # Verify installation
```

**Usage:**
```python
from crawl4ai import AsyncWebCrawler

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://example.com")
```

**Key Classes:**
- `AsyncWebCrawler` - Main asynchronous crawler class
- `arun()` - Primary crawling method
- `arun_many()` - Batch crawling method
- `CrawlResult` - Result object

### REST API (Docker-based)

**Best for:**
- Language-agnostic integration
- Microservices architecture
- Distributed systems
- Production deployments

## Monitoring & Observability

### Prometheus Metrics

Available at `/metrics` endpoint:
- Request counts
- Response times
- Error rates
- Browser pool status
- Queue depth

### Enterprise Features

- Comprehensive monitoring dashboard
- WebSocket streaming for real-time updates
- Smart browser pool management
- Production-ready observability

## Generating OpenAPI Specification

### Method 1: Extract from Running Server

```bash
# Start the Docker container
docker run -d -p 11235:11235 --name crawl4ai unclecode/crawl4ai:latest

# Download the OpenAPI spec
curl http://localhost:11235/openapi.json > crawl4ai-openapi.json

# Or use wget
wget http://localhost:11235/openapi.json -O crawl4ai-openapi.json
```

### Method 2: Using FastAPI CLI (if running from source)

```bash
# If running the FastAPI app directly
fastapi dev server.py --port 11235

# In another terminal
curl http://localhost:11235/openapi.json > crawl4ai-openapi.json
```

## Use Cases

### 1. RAG (Retrieval-Augmented Generation)
- Clean markdown output perfect for LLM ingestion
- Optimized for vector database storage
- Structured content extraction

### 2. AI Agents & Automation
- Asynchronous job queue for agent workflows
- Webhook notifications for event-driven architectures
- MCP protocol support

### 3. Data Pipelines
- Batch processing with `arun_many()`
- Redis-backed task management
- Configurable caching strategies

### 4. Model Training
- Structured data extraction
- Schema-based scraping
- Repeated pattern parsing

### 5. Content Analysis
- Sentiment analysis ready
- LLM-powered extraction
- Multi-format output

## Limitations & Considerations

### No Static OpenAPI File

**Why it doesn't exist in the repo:**
- FastAPI generates OpenAPI spec dynamically
- Schema evolves with code changes
- Reduces maintenance burden
- Always up-to-date with actual implementation

**How to get it:**
- Must run the server
- Download from `/openapi.json` endpoint
- Alternative: Use Apify platform versions

### Version Compatibility

- Different versions may have different endpoints
- Check release notes for API changes
- Use semantic versioning for production

### Rate Limiting

- Not explicitly documented in OpenAPI
- May vary by deployment method
- Check documentation for production limits

## Integration Patterns

### 1. Direct REST API Calls

```bash
# Synchronous crawl
curl -X POST http://localhost:11235/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com"],
    "crawler_config": {
      "type": "CrawlerRunConfig",
      "params": {"cache_mode": "ENABLED"}
    }
  }'
```

### 2. Async Job Queue

```bash
# Submit job
JOB_RESPONSE=$(curl -X POST http://localhost:11235/crawl/job \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com"]}')

# Extract task_id
TASK_ID=$(echo $JOB_RESPONSE | jq -r '.task_id')

# Check status
curl http://localhost:11235/job/$TASK_ID
```

### 3. Webhook Integration

```json
{
  "urls": ["https://example.com"],
  "webhook_config": {
    "url": "https://your-server.com/webhook",
    "headers": {
      "Authorization": "Bearer your-token"
    },
    "delivery_mode": "immediate"
  }
}
```

## Comparison with Alternatives

### Crawl4AI vs Firecrawl

**Crawl4AI Advantages:**
- Open-source (no forced API keys)
- Self-hostable
- More extraction strategies
- Better LLM integration

**Firecrawl Advantages:**
- Managed cloud service
- Static OpenAPI specification
- Enterprise support

### Crawl4AI vs Traditional Scrapers

**Crawl4AI Advantages:**
- LLM-optimized output
- Markdown generation
- AI-powered extraction
- Modern async architecture

## Best Practices

### 1. Use Async Endpoints for Long Operations

```json
// Instead of /crawl for multiple URLs
// Use /crawl/job with webhooks
{
  "urls": ["url1", "url2", "url3"],
  "webhook_config": {...}
}
```

### 2. Implement Proper Error Handling

- Check job status periodically
- Handle webhook delivery failures
- Implement retry logic

### 3. Optimize Cache Strategy

```json
{
  "crawler_config": {
    "type": "CrawlerRunConfig",
    "params": {
      "cache_mode": "ENABLED",  // or "DISABLED", "READ_ONLY"
      "bypass_cache": false
    }
  }
}
```

### 4. Use Appropriate Extraction Strategy

- Simple content: CSS/XPath selectors
- Complex patterns: Repeated pattern parsing
- Intelligent extraction: LLM-based strategies

## Future Development

### Roadmap Considerations

Based on the project's active development:
- Continued FastAPI enhancements
- More MCP protocol features
- Enhanced monitoring capabilities
- Additional extraction strategies

### Community Contributions

- 5.3k+ forks indicate active community
- Regular releases and updates
- Discord community for support

## Resources & References

### Official Documentation
- **Main Documentation:** https://docs.crawl4ai.com/
- **Docker Deployment Guide:** https://docs.crawl4ai.com/core/docker-deployment/
- **Quick Start:** https://docs.crawl4ai.com/core/quickstart/
- **Code Examples:** https://docs.crawl4ai.com/core/examples/

### GitHub
- **Repository:** https://github.com/unclecode/crawl4ai
- **Releases:** https://github.com/unclecode/crawl4ai/releases
- **Issues:** https://github.com/unclecode/crawl4ai/issues
- **Discussions:** https://github.com/unclecode/crawl4ai/discussions

### Community
- **Discord:** https://discord.gg/jP8KfhDhyN
- **PyPI:** https://pypi.org/project/Crawl4AI/

### Tutorials & Guides
- [Crawl4AI Tutorial: A Beginner's Guide](https://apidog.com/blog/crawl4ai-tutorial/)
- [Crawl4AI Tutorial: Docker Deployment](https://www.pondhouse-data.com/blog/webcrawling-with-crawl4ai)
- [Crawl4AI - ScrapingBee Guide](https://www.scrapingbee.com/blog/crawl4ai/)

### Third-Party Integrations
- **Apify Platform:** https://apify.com/janbuchar/crawl4ai/api
- **MCP Integration:** https://github.com/coleam00/mcp-crawl4ai-rag
- **Community REST API:** https://github.com/romeoman/crawl4ai-rest-api

## Conclusion

### Summary

**OpenAPI Specification Status:** ✅ **Available** (dynamically generated by FastAPI)

**Access Methods:**
1. ⭐ **Recommended:** Run Docker container and access `/openapi.json`
2. Use Apify platform wrappers
3. Community Postman collections

**Coverage:** Comprehensive REST API with:
- Core crawling endpoints (sync & async)
- Specialized processing (HTML, PDF, screenshots)
- Job management and monitoring
- MCP protocol support
- Interactive playground

**Production Readiness:** ✅ High
- Docker-based deployment
- Redis task management
- Prometheus metrics
- JWT authentication
- Webhook support

### Feasibility of Generating OpenAPI Spec

**Verdict:** ✅ **Easy** - Already auto-generated by FastAPI

**Steps:**
1. Run Crawl4AI Docker container
2. Download from `http://localhost:11235/openapi.json`
3. Optionally validate and enhance with additional documentation

**No manual spec creation needed** - FastAPI handles this automatically based on:
- Pydantic models in `schemas.py`
- Endpoint decorators in `server.py`
- Type hints and docstrings

### Recommendation

For integration projects:
1. Use the Docker deployment to get the current OpenAPI spec
2. Save the spec file to your project's API documentation
3. Update periodically to track API changes
4. Consider using OpenAPI code generators for client libraries

For production use:
1. Deploy Crawl4AI using Docker
2. Implement async job queue pattern
3. Use webhooks for event-driven architectures
4. Monitor via Prometheus metrics endpoint

---

**Research completed:** 2025-11-22
**Next steps:** Extract and validate OpenAPI specification from running instance


> Source: `docs/data_engineering/crawl4ai/Crawl4ai Scraping and Site Analysis.md`



# **Architectural Blueprint for Autonomous Web Reconnaissance and High-Value Asset Extraction: Integrating Stagehand and Crawl4AI**

## **Executive Summary**

The paradigm of web scraping is undergoing a fundamental shift from rigid, rule-based automation to probabilistic, agentic interaction. Traditional scraping pipelines, reliant on brittle CSS selectors and deterministic navigation paths, are increasingly failing against the complexity of modern Single Page Applications (SPAs), dynamic content loading, and sophisticated anti-bot countermeasures. The user’s requirement—to navigate complex web environments in a preliminary fashion, deduce semantic value, visualize site layout, and subsequently execute high-fidelity extraction of specific assets like PDFs—demands a hybrid architecture. This report outlines a comprehensive technical framework that fuses **Stagehand**, an AI-driven browser automation SDK, with the self-hosted Docker implementation of **Crawl4AI**.  
This architecture designates Stagehand as the "Forward Reconnaissance Unit" and Crawl4AI as the "Heavy Extraction Artillery." Stagehand utilizes Large Language Models (LLMs) and Vision-Language Models (VLMs) to "observe" the DOM, inferring navigational intent and structural semantics without prior knowledge of the site’s codebase.1 It is tasked with generating a structural map, deducing the location of high-value sections, and verifying the presence of relevant assets. Once the target parameters are established, the workload is handed off to the Crawl4AI Docker cluster. This component provides the necessary concurrency, resource isolation, and specialized extraction strategies (specifically LLMExtractionStrategy and PDFCrawlerStrategy) to mine data and binary files at scale.3  
The following report is an exhaustive technical guide, spanning the theoretical underpinnings of AI-driven browsing, the granular configuration of containerized extraction environments, and the implementation of a sophisticated document acquisition pipeline. It addresses the nuanced challenges of state management, session persistence, memory optimization in Dockerized browser pools, and the synthesis of unstructured web data into visualized, actionable intelligence.  
---

## **1\. The Strategic Imperative: Hybrid AI-Driven Scraping Architectures**

### **1.1 The Limitations of Deterministic Crawling**

In the context of the user's project, purely deterministic crawlers face a significant "cold start" problem. To define a crawling rule for a specific website, an engineer must typically inspect the DOM, identify unique identifiers (IDs, classes), and hard-code navigation logic. However, when the objective is to "navigate... in a preliminary fashion to first identify all the pages," the system encounters the unknown. It does not know *where* the valuable data resides or *how* the site is structured. A standard crawler would simply follow every link (Breadth-First or Depth-First), leading to inefficient resource expenditure on irrelevant pages (e.g., "Privacy Policy," "Login," "Careers") before finding the project-critical PDF repositories.

### **1.2 The Agentic Reconnaissance Model**

The proposed solution introduces an "Agentic Reconnaissance" phase. By employing Stagehand, the system mimics human cognitive processes. It parses the "accessibility tree" of the browser—a simplified, semantic representation of the DOM used by screen readers—to understand the page's purpose.5 This allows the system to make decisions: "This link looks like a financial report archive; I should investigate," versus "This link leads to social media; ignore." This deductive capability is powered by LLMs that process the observed elements and determine their relevance to the user's project goals.6

### **1.3 The High-Throughput Extraction Model**

While Agentic models are intelligent, they are computationally expensive and relatively slow due to the latency of LLM inference for every action. Therefore, they are unsuitable for the bulk scraping of thousands of pages. This is where Crawl4AI enters the architecture. Once Stagehand has identified the URL patterns and page structures that yield value, Crawl4AI—running in a highly optimized Docker environment—executes the bulk extraction. It leverages "Magic Mode" to mimic human behavior without the per-action LLM cost, utilizing cached selectors or broader extraction strategies to strip-mine the identified veins of data.4

### **1.4 Architectural Diagram (Conceptual)**

The system operates in three distinct phases:

1. **Phase I: Discovery & Mapping (Stagehand):** The agent explores the domain, builds a graph of the site's layout, and scores sections based on "value deduction" logic.  
2. **Phase II: Strategy Formulation (The Bridge):** The system analyzes the reconnaissance data to generate optimized configurations (JSON payloads) for the bulk crawler.  
3. **Phase III: Mass Extraction (Crawl4AI Docker):** The containerized service executes parallel jobs to harvest HTML content and binary assets (PDFs), utilizing specific strategies for each media type.

---

## **2\. Phase I: The Reconnaissance Engine with Stagehand**

The primary objective of the reconnaissance phase is to "get a sense of the layout of the site and visualize it," and to "deduce which sections are valuable." Stagehand is uniquely suited for this due to its observe, act, and extract primitives, which abstract away the underlying DOM complexity.

### **2.1 The Observe Primitive: Semantic DOM Analysis**

Standard scraping tools see a web page as a string of HTML code. Stagehand sees it as a collection of *actions*. The observe method is the cornerstone of this site mapping capability. When the command await stagehand.observe(instruction) is issued, the framework does not merely search for keywords. It constructs a representation of the interactive elements on the page and asks the underlying AI model (e.g., GPT-4o, Claude 3.5 Sonnet) to identify elements that match the natural language instruction.6

#### **2.1.1 The Accessibility Tree Advantage**

Stagehand optimizes this process by processing the browser's accessibility tree rather than the raw DOM. The accessibility tree is a stable, semantic representation of the UI, largely immune to the "div soup" and obfuscated class names (e.g., Tailwind CSS classes like w-full p-4 text-gray-700) that plague traditional scrapers. By analyzing this tree, Stagehand reduces the token count sent to the LLM by 80-90%, significantly reducing cost and latency while increasing reliability.5

#### **2.1.2 Structured Observation Output**

To "visualize" the site structure, we must first catalog the available navigation paths. The observe method returns an array of Action objects. Each object contains a selector (XPath), a description generated by the AI, a method (e.g., click), and arguments.  
**Data Structure for Visualization:**

TypeScript

interface Action {  
  selector: string;  
  description: string;  
  method: string; // 'click', 'type', etc.  
  arguments?: string;  
}

.6  
By iterating through the navigation menu using observe("Find all top-level navigation links"), the system can collect a list of primary sections. This list forms the "Level 1" nodes of the site visualization graph.

### **2.2 Deductive Logic: Evaluating Section Value**

The user requires the system to "deduce which sections are valuable." This implies a decision-making process that goes beyond simple keyword matching. We implement this using Stagehand's extract method combined with Zod schemas to enforce boolean logic.

#### **2.2.1 The Deduction Schema**

When the agent visits a page, it performs a rapid assessment scan. We define a Zod schema that asks the LLM to evaluate the page content against the project's specific criteria (e.g., "contains relevant PDF files," "lists financial data," "is an archive").  
**Implementation Strategy:**

JavaScript

import { z } from "zod";

const PageValuationSchema \= z.object({  
  is\_relevant: z.boolean().describe("True if the page contains lists of reports, documents, or PDF downloads relevant to the project."),  
  reasoning: z.string().describe("A brief explanation of why this page is considered relevant or irrelevant."),  
  content\_category: z.enum(\['archive', 'article', 'landing\_page', 'irrelevant'\]),  
  estimated\_document\_count: z.number().describe("The approximate number of downloadable documents visible on the page."),  
  has\_pagination: z.boolean().describe("True if the page appears to be part of a paginated list.")  
});

// Execution  
const valuation \= await stagehand.extract(  
  "Analyze the visible content. Is this section valuable for collecting PDF reports?",  
  PageValuationSchema  
);

.9  
This valuation object becomes a node attribute in our site graph. If is\_relevant is true, the URL is flagged for deep crawling. If false, the branch is pruned, saving resources.

### **2.3 Visualizing the Site Layout**

To satisfy the requirement of "visualizing" the site, the reconnaissance data must be structured into a graph format (nodes and edges). Stagehand does not generate a visual image file of a map itself, but it generates the *data* required to build one.

#### **2.3.1 Constructing the Site Graph**

As Stagehand navigates, it maintains a state object:

* **Nodes:** Represent URLs visited or observed.  
* **Edges:** Represent the action taken to get from URL A to URL B (e.g., "Clicked 'Reports' link").  
* **Attributes:** The valuation data derived above.

This data can be exported to a format like JSON-LD or GraphML, which can then be visualized using tools like Gephi or rendered into a sitemap using libraries like D3.js. Additionally, Stagehand can take screenshots during this process. By combining the graph data with thumbnails of the pages, the system provides a comprehensive visual and structural overview of the target domain.12

### **2.4 Handling Dynamic Navigation and State**

Many modern sites utilize complex JavaScript for navigation (e.g., infinite scroll, "Load More" buttons). Stagehand's act primitive handles this natively. The instruction await stagehand.act("Scroll down until new items load") or await stagehand.act("Click the 'Next' button") relies on the AI to identify the correct interaction trigger, regardless of whether it is a \<button\>, an \<a\>, or a \<div\> with an onClick handler.6  
Caching Interactions:  
To optimize performance during this exploratory phase, Stagehand’s caching mechanism is critical. Once the AI identifies the "Next Page" button selector for a specific site, that action is cached. Subsequent clicks on that button use the cached selector (deterministic) rather than re-querying the LLM (probabilistic), drastically increasing speed for paginated reconnaissance.6  
---

## **3\. Phase II: Infrastructure \- The Self-Hosted Crawl4AI Docker Environment**

Once the reconnaissance phase has produced a list of valuable URLs and a map of the site's structure, the system transitions to the "Extraction Engine." The user's research snippets highlight the Crawl4AI Docker implementation as a robust solution for this purpose.3

### **3.1 Docker Container Architecture**

The self-hosted Docker container transforms Crawl4AI from a client-side library into a scalable microservice. This architecture is essential for handling the heavy resource demands of modern browser automation (Chromium instances can consume 500MB+ RAM each).

#### **3.1.1 Service Configuration and Resource Allocation**

To ensure stability during "deep research" or massive scrapes, the Docker container must be configured with precise resource limits. The MAX\_CONCURRENT\_TASKS environment variable is the primary throttle.  
**Configuration Table:**

| Environment Variable | Description | Recommended Value | Impact |
| :---- | :---- | :---- | :---- |
| MAX\_CONCURRENT\_TASKS | Limits the number of simultaneous browser instances. | 4-8 (per 8GB RAM) | Prevents OutOfMemory errors on the host. 4 |
| CRAWL4AI\_API\_TOKEN | Secures the API against unauthorized access. | High-Entropy String | Mandatory for any public or shared network deployment. 15 |
| OPENAI\_API\_KEY | Enables LLMExtractionStrategy within the container. | sk-... | Required for semantic extraction tasks. 4 |
| shm-size | Shared memory size for Docker container. | 2g (minimum) | Prevents Chrome crashes on complex pages. 16 |

The container exposes a REST API (default port 11235), which decouples the control logic (Python script) from the execution environment.3 This allows the control script to be lightweight while the heavy lifting occurs in the containerized environment.

### **3.2 API Interaction Schema**

The transition from library usage (import AsyncWebCrawler) to API usage (requests.post) requires adapting the interaction model. The API operates asynchronously: you submit a job, receive a Task ID, and poll for results.

#### **3.2.1 Submission Endpoint (POST /crawl)**

The payload for this endpoint dictates the entire behavior of the crawl. It must encapsulate the browser configuration, the run configuration, and the extraction strategy.  
**Schema Breakdown:**

* **urls**: A list of target URLs (deduced from Phase I).  
* **crawler\_params**: Corresponds to CrawlerRunConfig.  
* **browser\_config**: Corresponds to BrowserConfig (e.g., headless mode, user agent).  
* **extraction\_strategy**: The definition of how data is parsed.

**Example Payload Structure:**

JSON

{  
  "urls": \["https://target-site.com/reports/2024"\],  
  "crawler\_params": {  
    "extraction\_strategy": {  
      "type": "LLMExtractionStrategy",  
      "params": {  
        "provider": "openai/gpt-4o",  
        "instruction": "Extract all report titles and PDF download links.",  
        "schema": {  
           "type": "object",   
           "properties": {   
              "reports": { "type": "array", "items": { "type": "object", "properties": { "title": "string", "url": "string" } } }   
           }  
        }  
      }  
    },  
    "js\_code":,  
    "wait\_for": "css:.report-list-item"  
  }  
}

.17

#### **3.2.2 Polling Endpoint (GET /task/{task\_id})**

The control script must implement a robust polling loop. The API returns a status of queued, processing, completed, or failed.

* **Concurrency Management:** The client script can submit hundreds of URLs. The Docker container's internal queue manages the execution based on MAX\_CONCURRENT\_TASKS. The client merely polls for the completed state.4

### **3.3 Session Management and Persistence**

For websites requiring authentication or maintaining state (e.g., paging through a session-based search), Crawl4AI supports session reuse.

* **Mechanism:** A session\_id can be passed in the crawler\_params. The Docker container maintains the browser context associated with this ID.  
* **Workflow:**  
  1. Submit a login request with session\_id="project\_x".  
  2. Wait for completion.  
  3. Submit subsequent crawl requests with session\_id="project\_x". The browser instance reuses the cookies and local storage from the login step.4

---

## **4\. Phase III: The Asset Acquisition Pipeline (PDFs)**

The user explicitly requests to "find all the pages with relevant pdf files first before initiating their download." This two-step process—identification followed by acquisition—is crucial for bandwidth optimization and data hygiene.

### **4.1 Step 1: Identification (The Filter)**

During the crawling of the "valuable sections" identified by Stagehand, the primary goal is not to download files immediately, but to catalogue them. The LLMExtractionStrategy is highly effective here. It can parse complex HTML structures (e.g., nested divs, tables) and extract the href attribute of links, validating that they point to a PDF and are semantically relevant to the project.20  
**Extraction Instruction:**  
"Identify all links to PDF documents. Extract the URL, the document title, and the publication date. Ignore generic links like 'Terms of Service'."  
This produces a structured dataset (JSON) of potential assets. This list is then filtered by the control script to remove duplicates or irrelevant files (e.g., 0-byte files, corrupted links).

### **4.2 Step 2: Acquisition (The PDFCrawlerStrategy)**

Once the list of relevant PDF URLs is finalized, the system initiates the download phase. Crawl4AI utilizes specialized strategies for this: PDFCrawlerStrategy and PDFContentScrapingStrategy.22

#### **4.2.1 The PDFCrawlerStrategy**

Unlike a standard web crawler that expects HTML, the PDFCrawlerStrategy is designed to handle binary streams. It treats the PDF URL as a valid endpoint and prepares the stream for processing.

* **Usage in Docker:** The request payload changes. The crawler\_params must specify the strategy type as PDFCrawlerStrategy (implicitly or explicitly depending on version nuances) and pair it with the PDFContentScrapingStrategy.

#### **4.2.2 The PDFContentScrapingStrategy**

This component is responsible for the actual "scraping" of the document. It performs two critical functions:

1. **Text Extraction:** It extracts the raw text from the PDF, allowing the content of the document to be indexed or analyzed by LLMs later.  
2. **Asset Download:** By configuring accept\_downloads=True and specifying a downloads\_path, the system saves the binary file to the container's file system.23

Volume Handling:  
To handle large volumes of PDFs, the API calls should be batched. The Docker container's asynchronous nature allows for multiple PDF download tasks to be queued simultaneously. The downloaded\_files field in the result object provides the path to the saved file within the container (or mounted volume).23  
---

## **5\. Technical Implementation: The Control Plane**

To orchestrate these components—Stagehand for reconnaissance and Crawl4AI Docker for extraction—a central "Control Plane" script (written in Python) is required. This section outlines the logical flow and code structure.

### **5.1 System Architecture Diagram**

The architecture consists of three nodes:

1. **The Controller:** A Python environment running the orchestration logic.  
2. **The Scout:** A local Node.js or Python environment running Stagehand (for complex, interactive reconnaissance).  
3. **The Worker:** The Docker container running Crawl4AI (for high-volume processing).

### **5.2 The Reconnaissance Script (Python/Stagehand)**

This script acts as the "Sense of Layout" generator. It maps the site and identifies where the PDFs are hidden.

Python

import asyncio  
from stagehand import Stagehand, StagehandConfig  
from pydantic import BaseModel, Field

\# Schema for deducing value  
class SectionAnalysis(BaseModel):  
    section\_name: str \= Field(..., description="Name of the site section")  
    relevance\_score: int \= Field(..., description="0-10 score of relevance to the project")  
    contains\_pdfs: bool \= Field(..., description="True if PDF links are visible")  
    pdf\_count\_estimate: int \= Field(..., description="Estimated number of PDFs")

async def reconnaissance\_mission(start\_url: str):  
    config \= StagehandConfig(env="LOCAL", model\_name="gpt-4o")  
    stagehand \= Stagehand(config=config)  
    await stagehand.init()  
    page \= stagehand.page  
      
    \# 1\. Visualize Structure  
    await page.goto(start\_url)  
    structure \= await page.observe("Identify the main navigation structure")  
      
    valuable\_urls \=  
      
    \# 2\. Deduce Value  
    for item in structure:  
        \# Agentic decision: Should we explore this?  
        if "archive" in item\['description'\].lower() or "report" in item\['description'\].lower():  
            \# Act: Navigate  
            await page.act(item)  
              
            \# Extract: Analyze  
            analysis \= await page.extract(  
                "Analyze this page for relevant PDF documents.",   
                schema=SectionAnalysis  
            )  
              
            print(f"Section {analysis.section\_name}: Score {analysis.relevance\_score}")  
              
            if analysis.relevance\_score \> 7:  
                valuable\_urls.append(page.url)  
                  
            \# Return to base for next iteration  
            await page.goto(start\_url)  
              
    await stagehand.close()  
    return valuable\_urls

*Note: This script fulfills the requirement to "deduce which sections are valuable" before full extraction.*

### **5.3 The Extraction Script (Python/Requests)**

This script takes the valuable\_urls and feeds them into the Dockerized Crawl4AI worker.

Python

import requests  
import time

API\_URL \= "http://localhost:11235"  
API\_TOKEN \= "your\_secret\_token" \# From Docker env

def bulk\_extract\_pdfs(target\_urls):  
    headers \= {"Authorization": f"Bearer {API\_TOKEN}"}  
      
    \# 1\. Submit Jobs  
    task\_ids \=  
    for url in target\_urls:  
        payload \= {  
            "urls": \[url\],  
            "crawler\_params": {  
                "extraction\_strategy": {  
                    "type": "LLMExtractionStrategy",  
                    "params": {  
                        "provider": "openai/gpt-4o",  
                        "instruction": "Extract all PDF URLs and Titles.",  
                        "schema": { "type": "object", "properties": { "pdfs": { "type": "array", "items": { "type": "object", "properties": { "url": "string", "title": "string" } } } } }  
                    }  
                },  
                "js\_code":,  
                "magic": True \# Anti-bot evasion  
            }  
        }  
        response \= requests.post(f"{API\_URL}/crawl", json=payload, headers=headers)  
        task\_ids.append(response.json()\['task\_id'\])  
          
    \# 2\. Poll Results  
    pdf\_assets \=  
    for tid in task\_ids:  
        while True:  
            status \= requests.get(f"{API\_URL}/task/{tid}", headers=headers).json()  
            if status\['status'\] \== 'completed':  
                \# Aggregate results  
                data \= status\['result'\]\['extracted\_content'\]  
                pdf\_assets.extend(data\['pdfs'\])  
                break  
            elif status\['status'\] \== 'failed':  
                print(f"Task {tid} failed: {status\['error'\]}")  
                break  
            time.sleep(2)  
              
    return pdf\_assets

.4  
---

## **6\. Advanced Visualization and Data Synthesis**

The requirement to "visualize" the site structure goes beyond simple logging. Using the data collected in Phase I (Stagehand), we can construct a visual representation of the target domain.

### **6.1 Graph-Based Site Mapping**

The output of the reconnaissance phase is essentially a directed graph. Each page is a node, and each link is a directed edge.

* **Nodes:** Contain metadata (URL, Title, Valuation Score, PDF Count).  
* **Edges:** Represent the navigation hierarchy.

By exporting this data structure to a standard format like **GraphML** or **JSON-Graph**, we can leverage visualization tools.

* **Gephi/Cytoscape:** Can import these files to generate force-directed layouts, showing clusters of content (e.g., a dense cluster of nodes might represent a document archive).  
* **Heatmaps:** By coloring nodes based on their relevance\_score (deduced by Stagehand), the visualization immediately highlights the "hot zones" of the website where valuable data resides.

### **6.2 Screenshot Composition**

Crawl4AI supports full-page screenshots via the screenshot=True parameter. During the initial scrape, capturing screenshots of the "valuable sections" allows for the creation of a visual sitemap—a grid of thumbnails arranged hierarchically. This provides a rapid, human-readable reference of the site's layout and content distribution, satisfying the user's need to "get a sense of the layout".19  
---

## **7\. Operational Best Practices and Risk Mitigation**

### **7.1 Anti-Bot Evasion and Stealth**

Deep research into target sites often triggers security defenses (Cloudflare, Akamai).

* **Stagehand:** Naturally stealthy due to its agentic behavior. It doesn't instantly traverse 100 links; it "reads," "thinks," and "clicks" with human-like latency.2  
* **Crawl4AI:** "Magic Mode" is essential here. It overrides the navigator.webdriver property, randomizes the user agent, and mimics mouse movements. Additionally, the Docker container can be configured with a residential proxy network via the proxy parameter in the payload, rotating IPs per request to prevent IP bans.7

### **7.2 Memory and Resource Management**

A common failure mode in Dockerized browser automation is memory exhaustion.

* **The Janitor:** Crawl4AI includes an internal "Janitor" mechanism that monitors the browser pool. It automatically closes "zombie" browser contexts that have been idle or have exceeded their lifespan.  
* **Monitoring:** The Docker API provides /monitor/health to expose CPU and memory metrics. The Control Plane script should check this endpoint before submitting new batches. If memory usage exceeds 80%, the script should pause submission until the Janitor cleans up.3

### **7.3 Data Source Agnosticism**

While specific data source URLs were not provided in the user's snippet inputs, this architecture is designed to be target-agnostic.

* **Government Archives:** Handle generic HTML tables and direct PDF links.  
* **Corporate Portals:** Handle JavaScript-heavy "Load More" implementations via js\_code injection.  
* **News Aggregators:** Handle infinite scroll and article clustering using LLMExtractionStrategy to discern between news content and advertisements.16

## **8\. Conclusion**

The integration of **Stagehand** and **Crawl4AI (Docker)** creates a powerful synergy for web reconnaissance and extraction. Stagehand serves as the "brain," using AI to navigate ambiguity, deduce value, and map the territory. Crawl4AI serves as the "muscle," utilizing containerized infrastructure to execute the heavy lifting of data extraction and asset acquisition at scale. By strictly separating these concerns—Reconnaissance vs. Extraction—this architecture ensures cost-efficiency (minimizing LLM tokens), operational stability (isolating browser crashes), and high-fidelity data retrieval (semantic parsing of HTML and PDFs). This technical outline provides the robust foundation required to satisfy the complex requirements of modern web research and asset collection.

#### **Works cited**

1. Start your first Session with Stagehand \- Browserbase Documentation, accessed December 1, 2025, [https://docs.browserbase.com/introduction/stagehand](https://docs.browserbase.com/introduction/stagehand)  
2. Stagehand Docs, accessed December 1, 2025, [https://docs.stagehand.dev/](https://docs.stagehand.dev/)  
3. crawl4ai/docs/blog/release-v0.7.7.md at main \- GitHub, accessed December 1, 2025, [https://github.com/unclecode/crawl4ai/blob/main/docs/blog/release-v0.7.7.md](https://github.com/unclecode/crawl4ai/blob/main/docs/blog/release-v0.7.7.md)  
4. Crawl4AI Tutorial: Build a Powerful Web Crawler for AI Applications Using Docker, accessed December 1, 2025, [https://www.pondhouse-data.com/blog/webcrawling-with-crawl4ai](https://www.pondhouse-data.com/blog/webcrawling-with-crawl4ai)  
5. Stagehand breakdown \- Dwarves Memo, accessed December 1, 2025, [https://memo.d.foundation/breakdown/stagehand](https://memo.d.foundation/breakdown/stagehand)  
6. Observe \- Stagehand Docs, accessed December 1, 2025, [https://docs.stagehand.dev/v3/basics/observe](https://docs.stagehand.dev/v3/basics/observe)  
7. Document crawl4ai.com | DocIngest, accessed December 1, 2025, [https://docingest.com/docs/crawl4ai.com](https://docingest.com/docs/crawl4ai.com)  
8. observe() \- Stagehand Docs, accessed December 1, 2025, [https://docs.stagehand.dev/v3/references/observe](https://docs.stagehand.dev/v3/references/observe)  
9. browserbase/stagehand: The AI Browser Automation ... \- GitHub, accessed December 1, 2025, [https://github.com/browserbase/stagehand](https://github.com/browserbase/stagehand)  
10. Installation \- Stagehand Docs, accessed December 1, 2025, [https://docs.stagehand.dev/v3/first-steps/installation](https://docs.stagehand.dev/v3/first-steps/installation)  
11. claude.md \- browserbase/stagehand \- GitHub, accessed December 1, 2025, [https://github.com/browserbase/stagehand/blob/main/claude.md](https://github.com/browserbase/stagehand/blob/main/claude.md)  
12. Visual Sitemaps | Generate & Plan Website Architecture \+ Flows, accessed December 1, 2025, [https://visualsitemaps.com/](https://visualsitemaps.com/)  
13. Stagehand: A browser automation SDK built for developers and LLMs., accessed December 1, 2025, [https://www.stagehand.dev/](https://www.stagehand.dev/)  
14. Launching Stagehand v3, the best automation framework, accessed December 1, 2025, [https://www.browserbase.com/blog/stagehand-v3](https://www.browserbase.com/blog/stagehand-v3)  
15. Docker Deplotment \- Crawl4AI Documentation, accessed December 1, 2025, [https://crawl.freec.asia/mkdocs/basic/docker-deploymeny/](https://crawl.freec.asia/mkdocs/basic/docker-deploymeny/)  
16. Crawl4AI Tutorial: A Beginner's Guide \- Apidog, accessed December 1, 2025, [https://apidog.com/blog/crawl4ai-tutorial/](https://apidog.com/blog/crawl4ai-tutorial/)  
17. Crawl4AI API | Get Started \- Postman, accessed December 1, 2025, [https://www.postman.com/pixelao/pixel-public-workspace/collection/c26yn3l/crawl4ai-api](https://www.postman.com/pixelao/pixel-public-workspace/collection/c26yn3l/crawl4ai-api)  
18. Docker Deployment \- Crawl4AI Documentation (v0.7.x), accessed December 1, 2025, [https://docs.crawl4ai.com/core/docker-deployment/](https://docs.crawl4ai.com/core/docker-deployment/)  
19. Overview of Some Important Advanced Features \- Crawl4AI, accessed December 1, 2025, [https://docs.crawl4ai.com/advanced/advanced-features/](https://docs.crawl4ai.com/advanced/advanced-features/)  
20. Extraction & Chunking Strategies API \- Crawl4AI, accessed December 1, 2025, [https://docs.crawl4ai.com/api/strategies/](https://docs.crawl4ai.com/api/strategies/)  
21. LLM Strategies \- Crawl4AI Documentation (v0.7.x), accessed December 1, 2025, [https://docs.crawl4ai.com/extraction/llm-strategies/](https://docs.crawl4ai.com/extraction/llm-strategies/)  
22. PDF Parsing \- Crawl4AI Documentation (v0.7.x), accessed December 1, 2025, [https://docs.crawl4ai.com/advanced/pdf-parsing/](https://docs.crawl4ai.com/advanced/pdf-parsing/)  
23. File Downloading \- Crawl4AI Documentation (v0.7.x), accessed December 1, 2025, [https://docs.crawl4ai.com/advanced/file-downloading/](https://docs.crawl4ai.com/advanced/file-downloading/)  
24. Crawl4AI \- a hands-on guide to AI-friendly web crawling \- ScrapingBee, accessed December 1, 2025, [https://www.scrapingbee.com/blog/crawl4ai/](https://www.scrapingbee.com/blog/crawl4ai/)  
25. Quick Start \- Crawl4AI Documentation (v0.7.x), accessed December 1, 2025, [https://docs.crawl4ai.com/core/quickstart/](https://docs.crawl4ai.com/core/quickstart/)

## Web Data Acquisition — Firecrawl


> Source: `docs/data_engineering/firecrawl/Extract _ Firecrawl.md`

---
title: "Extract | Firecrawl"
source: "https://docs.firecrawl.dev/features/extract"
author:
  - "[[Firecrawl Docs]]"
published:
created: 2025-12-21
description: "Extract structured data from pages using LLMs"
tags:
  - "clippings"
---
**Introducing Agent: The Next Evolution of Extract**  
We’re launching [`/agent`](https://docs.firecrawl.dev/features/agent) — the successor to `/extract`. It’s faster, more reliable, and doesn’t require URLs. Just describe what you need and let the AI agent find and extract the data for you. [Try Agent now →](https://docs.firecrawl.dev/features/agent)

The `/extract` endpoint simplifies collecting structured data from any number of URLs or entire domains. Provide a list of URLs, optionally with wildcards (e.g., `example.com/*`), and a prompt or schema describing the information you want. Firecrawl handles the details of crawling, parsing, and collating large or small datasets.

We’ve simplified billing so that Extract now uses credits, just like all of the other endpoints. Each credit is worth 15 tokens.

## Using /extract

You can extract structured data from one or multiple URLs, including wildcards:
- **Single Page**  
	Example: `https://firecrawl.dev/some-page`
- **Multiple Pages / Full Domain**  
	Example: `https://firecrawl.dev/*`
When you use `/*`, Firecrawl will automatically crawl and parse all URLs it can discover in that domain, then extract the requested data. This feature is experimental; email [help@firecrawl.com](https://docs.firecrawl.dev/features/) if you have issues.

### Example Usage

**Key Parameters:**
- **urls**: An array of one or more URLs. Supports wildcards (`/*`) for broader crawling.
- **prompt** (Optional unless no schema): A natural language prompt describing the data you want or specifying how you want that data structured.
- **schema** (Optional unless no prompt): A more rigid structure if you already know the JSON layout.
- **enableWebSearch** (Optional): When `true`, extraction can follow links outside the specified domain.
See [API Reference](https://docs.firecrawl.dev/api-reference/endpoint/extract) for more details.

### Response (sdks)

JSON

## Job status and completion

When you submit an extraction job—either directly via the API or through the starter methods—you’ll receive a Job ID. You can use this ID to:
- Get Job Status: Send a request to the /extract/ endpoint to see if the job is still running or has finished.
- Wait for results: If you use the default `extract` method (Python/Node), the SDK waits and returns final results.
- Start then poll: If you use the start methods— `start_extract` (Python) or `startExtract` (Node)—the SDK returns a Job ID immediately. Use `get_extract_status` (Python) or `getExtractStatus` (Node) to check progress.

This endpoint only works for jobs in progress or recently completed (within 24 hours).

Below are code examples for checking an extraction job’s status using Python, Node.js, and cURL:

### Possible States

- **completed**: The extraction finished successfully.
- **processing**: Firecrawl is still processing your request.
- **failed**: An error occurred; data was not fully extracted.
- **cancelled**: The job was cancelled by the user.

#### Pending Example

JSON

#### Completed Example

JSON

## Extracting without a Schema

If you prefer not to define a strict structure, you can simply provide a `prompt`. The underlying model will choose a structure for you, which can be useful for more exploratory or flexible requests.

JSON

Setting `enableWebSearch = true` in your request will expand the crawl beyond the provided URL set. This can capture supporting or related information from linked pages.Here’s an example that extracts information about dash cams, enriching the results with data from related pages:

JSON

The response includes additional context gathered from related pages, providing more comprehensive and accurate information.

## Extracting without URLs

The `/extract` endpoint now supports extracting structured data using a prompt without needing specific URLs. This is useful for research or when exact URLs are unknown. Currently in Alpha.

## Known Limitations (Beta)

1. **Large-Scale Site Coverage**  
	Full coverage of massive sites (e.g., “all products on Amazon”) in a single request is not yet supported.
2. **Complex Logical Queries**  
	Requests like “find every post from 2025” may not reliably return all expected data. More advanced query capabilities are in progress.
3. **Occasional Inconsistencies**  
	Results might differ across runs, particularly for very large or dynamic sites. Usually it captures core details, but some variation is possible.
4. **Beta State**  
	Since `/extract` is still in Beta, features and performance will continue to evolve. We welcome bug reports and feedback to help us improve.

## Using FIRE-1

FIRE-1 is an AI agent that enhances Firecrawl’s scraping capabilities. It can controls browser actions and navigates complex website structures to enable comprehensive data extraction beyond traditional scraping methods.You can leverage the FIRE-1 agent with the `/extract` endpoint for complex extraction tasks that require navigation across multiple pages or interaction with elements.**Example (cURL):**

> FIRE-1 is already live and available under preview.

## Billing and Usage Tracking

We’ve simplified billing so that Extract now uses credits, just like all of the other endpoints. Each credit is worth 15 tokens.You can monitor Extract usage via the [dashboard](https://www.firecrawl.dev/app/extract).Have feedback or need help? Email [help@firecrawl.com](https://docs.firecrawl.dev/features/).

## AI & LLM Infrastructure — Gemini


> Source: `docs/data_engineering/gemini/gemini-quick-reference.md`

# Gemini Code Assist Quick Reference

## Configuration File Locations

```
project-root/
├── .gemini/
│   ├── config.yaml              # Repository settings
│   ├── styleguide.md            # Natural language coding conventions
│   └── commands/                # Project-scoped slash commands
│       └── *.toml
├── .aiexclude                   # Files to exclude from context
└── .gitignore                   # Also respected by Gemini

~/.gemini/
├── settings.json                # User settings + MCP servers
└── commands/                    # User-scoped slash commands
    └── *.toml
```

## config.yaml Example

```yaml
have_fun: false
memory_config:
  disabled: false
code_review:
  disable: false
  comment_severity_threshold: MEDIUM  # LOW, MEDIUM, HIGH, CRITICAL
  max_review_comments: -1  # -1 = unlimited
  pull_request_opened:
    summary: true
    code_review: true
    include_drafts: true
ignore_patterns:
  - "*.min.js"
  - "dist/"
  - "node_modules/"
```

## styleguide.md Example

```markdown
# Project Code Style Guide

## Language Standards
- TypeScript strict mode required
- ESLint must pass before commits
- Follow functional programming patterns

## Testing
- Minimum 80% code coverage
- Jest for unit tests
- Playwright for E2E

## Documentation
- JSDoc for all public functions
- README for each major module
```

## Custom Slash Command (TOML)

**Basic format:**
```toml
description = "Brief description for /help menu"
prompt = """
Your instructions here.
Use {{args}} for user input.
Execute commands with !{shell command}.
"""
```

**Example - Code Review:**
```toml
# .gemini/commands/review.toml
description = "Review a GitHub pull request"
prompt = """
Review GitHub PR #{{args}}

1. Fetch details: !{gh pr view {{args}} --json files}
2. Check code quality, security, tests
3. Reference project styleguide.md
4. Provide structured feedback
"""
```

**Usage:** `/review 123`

**Namespacing:**
- `commands/test.toml` → `/test`
- `commands/git/commit.toml` → `/git:commit`

## IDE Rules

**VS Code:**
1. Ctrl+Shift+P (Cmd+Shift+P on Mac)
2. "Preferences: Open Settings (UI)"
3. Search "Geminicodeassist: Rules"
4. Add rules (one per line)

**JetBrains:**
1. Settings > Tools > Gemini > Prompt Library > Rules
2. Choose scope: IDE (personal) or Project (shared)
3. Add rules

**Example rules:**
```
Always generate unit tests for new functions
Use TypeScript strict mode
Prefer async/await over promise chains
Include error handling in API calls
Add JSDoc for public functions
```

## MCP Server Configuration

**Location:** `~/.gemini/settings.json`

**Stdio server:**
```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "."],
      "timeout": 30000
    }
  }
}
```

**HTTP server:**
```json
{
  "mcpServers": {
    "github": {
      "httpUrl": "https://api.github.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

## Context Selection

**In chat:**
- `@filename` - Include specific local file
- `@repository` - Include remote indexed repo (Enterprise)

**Exclusions:**
Create `.aiexclude` with patterns:
```
.env
secrets/
*.key
data/*.csv
dist/
```

## Built-in Commands

**CLI:**
- `/help` - List all commands
- `/tools` - Show available tools
- `/mcp` - List MCP servers and status

**VS Code Quick Pick (Ctrl+I / Cmd+I):**
- `/fix` - Fix code issues
- `/generate` - Generate new code
- `/doc` - Add documentation
- `/simplify` - Simplify code

## Command Naming Conventions

✅ **Good:**
- `test.toml` → `/test`
- `review-pr.toml` → `/review-pr`
- `git/commit.toml` → `/git:commit`

❌ **Bad:**
- `Test.toml` → `/Test` (case-sensitive!)
- `my command.toml` → Invalid (spaces)

## Scope Comparison

| Feature | User Scope | Project Scope | Repository Scope |
|---------|-----------|---------------|------------------|
| **Commands** | `~/.gemini/commands/` | `.gemini/commands/` | N/A |
| **Settings** | `~/.gemini/settings.json` | `.gemini/settings.json` | N/A |
| **Config** | N/A | N/A | `.gemini/config.yaml` |
| **Style Guide** | N/A | N/A | `.gemini/styleguide.md` |
| **Rules (VS Code)** | Personal | Can be project | N/A |
| **Rules (JetBrains)** | IDE-level | Project-level | N/A |

## Quick Setup Checklist

### For a New Project

- [ ] Create `.gemini/` folder
- [ ] Add `config.yaml` with team settings
- [ ] Write `styleguide.md` with coding conventions
- [ ] Create useful team commands in `.gemini/commands/`
- [ ] Add `.aiexclude` for sensitive/large files
- [ ] Commit `.gemini/` folder to Git
- [ ] Document setup in project README

### For Individual Use

- [ ] Install Gemini CLI or IDE extension
- [ ] Configure Rules in IDE settings
- [ ] Create personal commands in `~/.gemini/commands/`
- [ ] Set up MCP servers in `~/.gemini/settings.json`
- [ ] Add `.aiexclude` to projects

## Comparison with Other Tools

| Feature | Gemini | Copilot | Cursor | Claude Code |
|---------|--------|---------|--------|-------------|
| **Config File** | `.gemini/config.yaml` | `.github/copilot-instructions.md` | `.cursor/rules` | `CLAUDE.md` |
| **Commands** | TOML files | ❌ | ❌ | Markdown |
| **MCP** | ✅ | ❌ | ❌ | ✅ |
| **Exclusions** | `.aiexclude` | `.gitignore` | `.cursorignore` | `.gitignore` |

## Common Patterns

### Team Code Review Command
```toml
# .gemini/commands/review.toml
description = "Comprehensive PR review"
prompt = """
Review the current changes:
!{git diff main}

Check:
1. Style compliance (see styleguide.md)
2. Security issues
3. Test coverage
4. Documentation

Provide actionable feedback.
"""
```

### Testing Command
```toml
# .gemini/commands/test.toml
description = "Run tests for changed files"
prompt = """
Files changed: !{git diff --name-only main}

Generate and run tests for these files.
Ensure all pass before proceeding.
"""
```

### Documentation Generator
```toml
# .gemini/commands/doc.toml
description = "Generate missing documentation"
prompt = """
Analyze: {{args}}

Generate:
1. JSDoc/docstrings for functions
2. README if missing
3. Usage examples
4. Type definitions
"""
```

## Tips & Best Practices

**For better responses:**
1. Use specific file context with `@`
2. Reference styleguide.md in prompts
3. Break complex tasks into multiple commands
4. Use shell commands to provide current state

**For team collaboration:**
1. Document all custom commands
2. Use consistent naming conventions
3. Keep config.yaml simple and well-commented
4. Update styleguide.md as standards evolve

**For security:**
1. Always exclude secrets in `.aiexclude`
2. Don't commit `settings.json` with tokens
3. Use environment variables for MCP credentials
4. Review indexed repositories regularly (Enterprise)

## Getting Help

- Official docs: https://developers.google.com/gemini-code-assist/docs/
- CLI GitHub: https://github.com/google-gemini/gemini-cli
- Use `/help` in CLI to list commands
- Check `/mcp` for MCP server status


> Source: `docs/data_engineering/gemini/Gemini 3 Hackathon.md`

---
title: "Gemini 3 Hackathon"
source: "https://gemini3.devpost.com/rules"
author:
  - "[[Gemini 3 Hackathon]]"
published:
created: 2025-12-30
description: "Build what's next"
tags:
  - "clippings"
---
#### Google DeepMind Gemini 3 Hackathon Official Eligibility and Rules

NO PURCHASE NECESSARY TO ENTER OR WIN. VOID WHERE PROHIBITED. CONTEST IS OPEN TO EVERYONE EXCEPT FOR RESIDENTS OF ITALY, QUEBEC, CRIMEA, CUBA, IRAN, SYRIA, NORTH KOREA, SUDAN, BELARUS, RUSSIA, AND OR AS LISTED AS INELIGIBLE IN THE ELIGIBILITY SECTION BELOW.

ENTRY IN THIS CONTEST CONSTITUTES YOUR ACCEPTANCE OF THESE OFFICIAL RULES.

Gemini 3 Hackathon (the “Contest”) is a skill contest where Google will share specific challenges set forth in these Rules as well as in the Devpost page for this Contest, and participants must develop solutions to one of the challenges. The solution that you develop and submit will be evaluated by judges, who will choose the winner(s) in accordance with these Official Rules. The prize(s) will be awarded to the participant(s) with the highest score for the judging criteria. See below for the complete details.

##### 1\. BINDING AGREEMENT:

In order to enter the Contest, you must agree to these Official Rules (“Rules”). Therefore, please read these Rules prior to entry to ensure you understand and agree. You agree that submission of an entry in the Contest constitutes agreement to these Rules. You may not submit an entry to the Contest and are not eligible to receive the prizes described in these Rules unless you agree to these Rules. These Rules form a binding legal agreement between you and Google with respect to the Contest.

The Contest is sponsored by Google LLC (“Google” or “Sponsor”), a Delaware corporation located at 1600 Amphitheater Parkway, Mountain View, CA, 94043, USA. The Contest will be administered by Devpost, Inc. (“Devpost” or “Administrator”) located at 250 Broadway, 24 Floor, New York, NY 10007.

##### 3\. ELIGIBILITY:

To be eligible to enter the Contest, you must: (1) be above the age of majority in the country, state, province or jurisdiction of residence (or at least twenty years old in Taiwan) at the time of entry; (2) not be a resident of Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, Russia and any other country designated by the United States Treasury's Office of Foreign Assets Control; (3) not be a person or entity under U.S. export controls or sanctions; and (4) have access to the Internet as of December 17, 2025. Contest is void in Italy, Quebec, Crimea, Cuba, Iran, Syria, North Korea, Sudan, Belarus, and Russia and where prohibited by law. Employees, interns, contractors, and official office-holders of Google, Devpost, or any organizations involved with the design, production, paid promotion, execution, or distribution of the Contest, and their parent companies, subsidiaries, affiliates, and their respective directors, officers, employees, advertising and promotion agencies, representatives, and agents or their immediate family or members of their household (“Contest Entities”), and members of the Contest Entities’ and their immediate families (parents, siblings, children, spouses, and life partners of each, regardless of where they live) and members of the households (whether related or not) of such employees, officers and directors are ineligible to participate in this Contest. Sponsor reserves the right to verify eligibility and to adjudicate on any dispute at any time. Persons who are (1) residents of US embargoed countries, (2) ordinarily resident in US embargoed countries, or (3) otherwise prohibited by applicable export controls and sanctions programs may not participate in this contest. In addition, individuals or organizations that are employed by a government agency, or any other individual or organization whose participation in the Contest would create, in the sole discretion of the Sponsor and/or Administrator, a real or apparent conflict of interest are ineligible to participate in this Contest.

If you are entering as part of a company or on behalf of your employer, these rules are binding on you, individually, and/or your employer. If you are acting within the scope of your employment, as an employee, contractor, or agent of another party, you warrant that such party has full knowledge of your actions and has consented thereto, including your potential receipt of a prize. You further warrant that your actions do not violate your employer’s or company’s policies and procedures.

##### 4\. CONTEST PERIOD:

The Contest begins at 1:00 P.M. Pacific Time (PT) Zone in the United States on **December 17, 2025** and ends at 5:00 P.M. PT on **February 9, 2026** (“Contest Period”). ENTRANTS ARE RESPONSIBLE FOR DETERMINING THE CORRESPONDING TIME ZONE IN THEIR RESPECTIVE JURISDICTIONS.

##### Dates and Timing

**Submission Period:** December 17, 2025 (01:00 P.M. Pacific Time) – February 9, 2026 (5:00 P.M. Pacific Time) (“Submission Period”).

**Judging Period:** February 10, 2026 (9:00 A.M. Pacific Time) – February 27, 2026 (11:45 P.M. Pacific Time) (“Judging Period”).

**Winners Announced:** On or around March 4, 2026 (2:00 P.M. Pacific Time).

##### 5\. HOW TO ENTER:

NO PURCHASE NECESSARY TO ENTER OR WIN. To enter the Contest, visit the Contest website located at [Gemini3.devpost.com](https://gemini3.devpost.com/) (“Contest Site”) during the Contest Period, find the challenges provided by Google on the Devpost site, which challenges are also set forth in these Rules and develop a solution for the challenge. To access the challenge and submit the solution, follow the steps below

Obtain access to the submission portal. You must have a Devpost account to register for the Contest as they will administer the Contest. If you do not have a Devpost account already, you can sign up for a Devpost account at no cost from run.devpost.com.

Obtain access to the Google Gemini API. Access to Gemini may be obtained by (1) signing up for a no cost trial at [https://gemini.google.com/](https://gemini.google.com/) or (2) using an existing Google account.

Entry in the Contest constitutes consent for the Sponsor and Devpost to collect and maintain an entrant’s personal information for the purpose of operating and publicizing the Contest.

Submit Your project to the Contest Site. Make sure to complete and enter all of the required fields on the “Enter a Submission” or similar worded page of the Contest Site (each a “Submission”) during the Contest Period.

##### 6\. Application Requirements:

Please find the Application Requirements and Submission Requirements outlined below (hereinafter, referred to collectively as the “Requirements”).

##### What to Create:

Entrants must develop a **new** application that uses the Gemini 3 API.

- **Project Team:** You may submit your Project as an individual, a team, or on behalf of an organization. A Team must consist of only Eligible Individuals, have all team members added as members of the Project on Devpost. If a team or Organization is entering the Submission, one individual must be appointed and authorized (the “Representative”) to represent, act, and enter the Submission, on the team’s behalf.
- **Functionality:** The Project must be capable of being successfully installed and run consistently on the platform for which it is intended, and must function as depicted in the video and/or expressed in the text description that you submit with the Project.
- **New Projects Only:** Projects must be newly created by the entrant during the Contest Period. The Project must be your original creation not a modification or extension of Your or anyone else’s existing work.
- **Third-Party Integrations:** If a Project integrates any third-party SDK, APIs, data and/or any information belonging to a third party, Entrants must be authorized to use these third-party tools and information in accordance with any terms and conditions or licensing requirements of the tool. If using third-party integrations/content/etc;, you must indicate it in your submission description.
- **Testing:** Access must be provided to an Entrant’s working Project (if available) for judging and testing by providing a link to a website, functioning demo, or a test build. If Entrant’s website is private, Entrant must include login credentials in its testing instructions. The Entrant must make the Project available free of charge and without any restriction, for testing, evaluation and use by the Sponsor, Administrator and Judges until the Judging Period ends. Judges are not required to test the Project and may choose to judge based solely on the text description, images, and video provided in the Submission.
- If the Project includes software that runs on proprietary or third-party hardware that is not widely available to the public, including software running on devices or wearable technology other than smartphones, tablets, or desktop computers, the Sponsor and/or Administrator reserve the right, at their sole discretion, to require the Entrant to provide physical access to the Project hardware upon request.
- **Language:** The Application must, at a minimum, support English language use. All Submission materials must be in English or, if not in English, the Entrant must provide an English translation of the demonstration video, text description, and testing instructions as well as all other materials submitted.
- **Multiple Submissions:** An Entrant may submit more than one Submission, however, each Submission must be unique and substantially different from each of the Entrant’s other Submissions, as determined by the Sponsor and Devpost in their sole discretion.
- **Submission ownership:** Be the original work of the Entrant, be solely owned by the Entrant, and not violate the IP rights of any other person or entity.
- **Intellectual Property:** Your Submission must: (a) be your (or your Team, or Organization’s) original work product; (b) be solely owned by you, your Team, your Organization with no other person or entity having any right or interest in it; and (c) not violate the intellectual property rights or other rights including but not limited to copyright, trademark, patent, contract, and/or privacy rights, of any other person or entity. An Entrant may contract with a third party for technical assistance to create the Submission provided the Submission components are solely the Entrant’s work product and the result of the Entrant’s ideas and creativity, and the Entrant owns all rights to them. An Entrant may submit a Submission that includes the use of open source software or hardware, provided the Entrant complies with applicable open source licenses and, as part of the Submission, creates software that enhances and builds upon the features and functionality included in the underlying open source product. By entering the Contest, you represent, warrant, and agree that your Submission meets these requirements.
- **Financial or Preferential Support:** A Project must not have been developed, or derived from a Project developed, with financial or preferential support from the Sponsor or Administrator. Such Projects include, but are not limited to, those that received funding or investment for their development, were developed under contract, or received a commercial license, from the Sponsor or Administrator any time prior to the end of Contest Submission Period. The Sponsor, at their sole discretion, may disqualify a Project, if awarding a prize to the Project would create a real or apparent conflict of interest.
- Submission Requirements

Entries to the Contest must meet the following requirements:

- Include a Project built with the required developer tools and meets the above Application Requirements.
- Include a **brief text write-up** (suggested ~200 words) that describes the Gemini Integration, detailing which Gemini 3 features were used and how they are central to the application.
- **Public Project Link:** A URL to your working product or interactive demo. Consider using AI Studio apps, which are the fastest way to build prototypes using the Gemini API.
	- *This allows judges to experience your project firsthand, if applicable. It should be publicly accessible and not require a login or paywall.*
- **URL to your PUBLIC code repository** - **required** if you do not have an AI Studio link to your project
- Include a **demonstration video** of your Project. The video portion of the Project:
	- Should include footage that shows the Project functioning on the platform(s) for which it was built.
	- It should not be longer than 3 minutes. If it is longer than 3 minutes, *only the first 3 minutes may be evaluated*.
	- It must conform to the technical requirements set forth on the Contest site, including that the Submission must be uploaded to and made publicly visible on YouTube (recommended) or Vimeo, and a link to the video must be provided on the Submission form on the Contest Site.
	- It must be in English or include English subtitles.
- No parts of the submission can be derogatory, offensive, threatening, defamatory, disparaging, libelous or contain any content that is inappropriate, indecent, sexual, profane, indecent, tortuous, slanderous, discriminatory in any way, or that promotes hatred or harm against any group or person, or otherwise does not comply with the theme and spirit of the Contest.
- No part of that submission contains content, material or any element that is unlawful, or otherwise in violation of or contrary to all applicable federal, state, or local laws and regulations in any country, state or applicable territory where you created the video and in the United States.
- The Submission must not contain any content, material or element that displays any third party advertising, slogan, logo, trademark or otherwise indicates a sponsorship or endorsement by a third party, commercial entity or that is not within the spirit of the Contest, as determined by Sponsor, in its sole discretion.
- It cannot contain any content, element, or material that violates a third party’s publicity, privacy or intellectual property rights.

##### 7\. SUBMISSION MODIFICATIONS:

**Draft Submissions**

Prior to the end of the Submission Period, you may save draft versions of your submission on Devpost to your portfolio before submitting the Submission materials to the Hackathon for evaluation. Once the Submission Period has ended, you may not make any changes or alterations to your Submission, but you may continue to update the Project in your Devpost portfolio.

**Modifications After the Submission Period**

The Sponsor and Devpost may permit you to modify part of your Submission after the Submission Period for the purpose of adding, removing or replacing material that potentially infringes a third party mark or right, discloses personally identifiable information, or is otherwise inappropriate. The modified Submission must remain substantively the same as the original Submission with the only modification being what the Sponsor and Devpost permits.

##### 8\. JUDGING:

On or about the period between **February 10, 2026** through **February 27, 2026**, (“Judging Period”) the Submissions will be evaluated by the Judges in the following Stages. Eligible submissions will be evaluated by a panel of judges selected by the Sponsor (the “Judges”). Judges may be employees of the sponsor or third parties, may or may not be listed individually on the Hackathon Website, and may change before or during the Judging Period. Judging may take place in one or more rounds with one or more panels of Judges, at the discretion of the sponsor.

The Submissions will be evaluated by the Judges in the following Stages:

**Stage One:** The first stage will determine via pass/fail whether the Submission meets a baseline level of viability, in that the Submission includes all Submission requirements, reasonably addresses a Challenge, and reasonably applies the requirements.

**Stage Two:** All Submissions that pass Stage One will be evaluated in Stage Two by the Judges based on the following weighted criteria, and according to the sole and absolute discretion of the Judges. Each Submission will receive a score from 1 to 5 per criterion and those criterion scores will be averaged per Submission.

- **Technical Execution - 40%**
- Does the project demonstrate quality application development? Does the project leverage Gemini 3? Is the code of good quality and is it functional?
- **Potential Impact - 20%**
- How big of an impact could the project have in the real world? How useful is the project to a broad market of users? How significant is the problem the project addresses, and does it efficiently solve it?
- **Innovation/Wow Factor - 30%**
- How novel and original is the idea? Does it address a significant problem or create a unique solution?
- **Presentation/Demo - 10%**
- Is the problem clearly defined, and is the solution effectively presented through a demo and documentation? Have they explained how they used Gemini 3 and any relevant tools? Have they included documentation or an architectural diagram?

The highest-scoring Submission for each category will be selected as the potential winner(s). The highest-scoring Submission across all categories will win the Grand Prize. Ties will be broken by comparing scores on each criterion in the order listed, and if a tie remains, judges will vote. If a potential winner is disqualified, the Submission with the next highest score will become the potential winner. Determinations of judges are final and binding.

The award of a prize to a potential winner is subject to verification of the identity, qualifications and role of the potential winner in the creation of the Submission. No Submission or individual shall be deemed a winning Submission or winner until their post-competition prize affidavits have been completed and verified, even if prospective winners have been announced verbally or on the competition website. The final decision to designate a winner shall be made by the Sponsor and/or Administrator. A Submission can win a maximum of one prize. In the event that no entries are received for a region, no prize will be awarded.

On or about **March 2, 2026**, the potential winner(s) will be selected and may be notified by email, at Sponsor’s discretion for Winner Verification Requirement (as defined below). If a potential winner does not respond to the notification attempt within two days from the first notification attempt, then such potential winner will be disqualified and an alternate potential winner will be selected from among all eligible entries received based on the judging criteria described herein. Except where prohibited by law, each potential winner may be required to sign and return a Declaration of Eligibility and Liability and Publicity Release and provide any additional information that may be required by Sponsor. If required, potential winners must return all such required documents within two days following attempted notification or such potential winner will be deemed to have forfeited the prize and another potential winner will be selected based on the judging criteria described herein. All notification requirements, as well as other requirements within these Rules, will be strictly enforced.

The public Winner Announcement will be on or around **March 4, 2026**.

“Winner Verification Requirement” means THE AWARD OF A PRIZE TO A POTENTIAL WINNER IS SUBJECT TO VERIFICATION OF THE IDENTITY, QUALIFICATIONS AND ROLE OF THE POTENTIAL WINNER IN THE CREATION OF THE SUBMISSION. No Submission or individual shall be deemed a winning Submission or winner until their post-competition prize affidavits have been completed and verified, even if prospective winners have been announced verbally or on the competition website. The final decision to designate a winner shall be made by the Sponsor and/or Administrator.

Determinations of judges are final and binding.

##### 9\. PRIZES:

| **Winner** | **Prize** | **Quantity** | **Eligible** |
| --- | --- | --- | --- |
| Grand Prize | - $50,000 USD - Social promotion of the winning project - 30-minute interview with the [AI Futures Fund](https://labs.google/aifuturesfund) team | 1 | All eligible submissions |
| 2nd Place | - $20,000 USD - Social promotion of the winning project - 30-minute interview with the [AI Futures Fund](https://labs.google/aifuturesfund) team | 1 | All eligible submissions |
| 3rd Place | - $10,000 USD - Social promotion of the winning project - 30-minute interview with the [AI Futures Fund](https://labs.google/aifuturesfund) team | 1 | All eligible submissions |
| Honorable Mentions | - $2,000 USD - Social promotion of the winning project | 10 | All eligible submissions |

- Each Project is eligible for up to one (1) Prize.

##### C. Terms Applicable to All Prizes.

Cash Prize Delivery: Cash Prizes will be payable to the winner, if an individual; to the winning team’s Representative, if a team; or to the organization, if the winning team is an Organization. It will be the responsibility of the winning team’s or organization’s Representative to allocate the Prize among their team or organization’s participating members, as the Representative deems appropriate. A monetary Prize will be mailed to the winner’s address (if an individual) or the Representative’s address (if a team or organization), or sent electronically to the winner, winning teams Representative, or organization’s bank account, only after receipt of the completed winner affidavit and other required forms (collectively the “Required Forms”), if applicable. The deadline for returning the Required Forms to the Administrator is ten (10) business days after the Required Forms are sent. Failure to provide correct information on the Required Forms, or other correct information required for the delivery of a Prize, may result in delayed Prize delivery, disqualification of the individual, team or organization or forfeiture of a Prize. Prizes will be delivered within sixty (60) days of the Sponsor or Devpost’s receipt of the completed Required Forms.

None of the non-cash prizes are redeemable for cash. The approximate retail value (ARV) may be adjusted depending on the country, state or jurisdiction of residence of the winner. All travel arrangements will be made by the traveler (or another party on traveler’s behalf) in its sole discretion. Travelers may be required to provide proof of travel, relevant receipts and sign and return additional Prize-related documents as are provided by Sponsor, or provide additional information as requested by Sponsor, including without limitation for purposes of receiving the reimbursement for the Travel Prize reimbursement.

Odds of winning any prize depends on the number of eligible entries received during the Contest Period and the skill of the entrants. No transfer, substitution or cash equivalent for prize(s) is allowed, except at Sponsor’s sole discretion. Sponsor reserves the right to substitute a prize, in whole or in part, of equal or greater monetary value if a prize cannot be awarded, in whole or in part, as described for any reason. Value is subject to market conditions, which can fluctuate and any difference between actual market value and ARV will not be awarded. The prize(s) may be subject to restrictions and/or licenses and may require additional hardware, software, service, or maintenance to use. The winner shall bear all responsibility for use of the prize(s) in compliance with any conditions imposed by such manufacturer(s), and any additional costs associated with its use, service, or maintenance. Contest Entities have not made and Contest Entities are not responsible in any manner for any warranties, representations, or guarantees, express or implied, in fact or law, relating to the prize(s), regarding the use, value or enjoyment of the prize(s), including, without limitation, its quality, mechanical condition, merchantability, or fitness for a particular purpose, with the exception of any standard manufacturer's warranty that may apply to the prize(s) or any components thereto.

##### 10\. FEES & TAXES:

Winners (and in the case of team or organization, all participating members) are responsible for any fees associated with receiving or using a prize, including but not limited to, wiring fees or currency exchange fees. Winners (and in the case of team or organization, all participating members) are responsible for reporting and paying all applicable taxes in their jurisdiction of residence (federal, state/provincial/territorial and local). Winners may be required to provide certain information to facilitate receipt of the award, including completing and submitting any tax or other forms necessary for compliance with applicable withholding and reporting requirements. United States residents may be required to provide a completed form W-9 and residents of other countries may be required to provide a completed W-8BEN form. Winners are also responsible for complying with foreign exchange and banking regulations in their respective jurisdictions and reporting the receipt of the Prize to relevant government departments/agencies, if necessary. The Sponsor, Devpost, and/or Prize provider reserves the right to withhold a portion of the prize amount to comply with the tax laws of the United States or other Sponsor jurisdiction, or those of a winner’s jurisdiction.

##### 11\. GENERAL CONDITIONS:

All federal, state, provincial and local laws and regulations apply. Google reserves the right to disqualify any entrant from the Contest if, in Google’s sole discretion, it reasonably believes that the entrant has attempted to undermine the legitimate operation of the Contest by cheating, deception, or other unfair playing practices or annoys, abuses, threatens or harasses any other entrants, Google, or the Judges.

##### 12\. INTELLECTUAL PROPERTY RIGHTS:

To the extent your or your team or organization’s Submission makes use of generally commercially available software not owned by you or your team or organization that was used to generate the Submission, but that can be procured by Google without undue expense, you do not grant the license in the preceding sentence to that software.

As between Google and the entrant, all Submissions remain the intellectual property of the individuals or organizations that developed them. The entrant retains ownership of all intellectual and industrial property rights (including moral rights) in and to any project materials, or videos provided for the Contest. As a condition of entry, entrant grants Google, its subsidiaries, agents and partner companies, a perpetual, irrevocable, worldwide, royalty-free, and non-exclusive license to use, reproduce, adapt, modify, publish, distribute, publicly perform, create a derivative work from, and publicly display such Project(s) (1) for the purposes of allowing Google and its affiliates and the Judges to evaluate the Project for purposes of the Contest, and (2) in connection with advertising and promotion via communication to the public or other groups, including, but not limited to, the right to make screenshots, animations and video clips available for promotional purposes.

##### 13\. PRIVACY:

Participant acknowledges and agrees that Google may collect, store, share and otherwise use personally identifiable information provided during the registration process and the contest, including, but not limited to, name, mailing address, phone number, and email address. Google will use this information in accordance with its Privacy Policy (http://www.google.com/policies/privacy/), including for administering the contest and verifying Participant’s identity, postal address and telephone number in the event an entry qualifies for a prize.

Participant’s information may also be transferred to countries outside the country of Participant's residence, including the United States. Such other countries may not have privacy laws and regulations similar to those of the country of Participant's residence.

If a participant does not provide the mandatory data required at registration, Google reserves the right to disqualify the entry.

Participant has the right to request access, review, rectification or deletion of any personal data held by Google in connection with the Contest by writing to Google at this email address cloudhackathons@google.com.

##### 14\. PUBLICITY:

By participating in the Hackathon, Entrant consents to the promotion and display of the Entrant’s Submission, and to the use of personal information about themselves for promotional purposes, by the Sponsor, Administrator, and third parties acting on their behalf. Such personal information includes, but is not limited to, your name, likeness, photograph, voice, opinions, comments and hometown and country of residence. It may be used in any existing or newly created media, worldwide without further payment or consideration or right of review, unless prohibited by law. Authorized use includes but is not limited to advertising and promotional purposes.

##### 15\. WARRANTY, INDEMNITY AND RELEASE:

Entrants warrant that their Submissions are their own original work and, as such, they are the sole and exclusive owner and rights holder of the submitted Submission and that they have the right to submit the Submission in the Contest and grant all required licenses, except that to the extent your or your team or organization’s Submission makes use of generally commercially available software not owned by you or your team or organization that was used to generate the Submission, but that can be procured by Google without undue expense, you do not grant the license in the preceding sentence to that software. Each entrant agrees not to submit any Submission that (1) infringes any third party proprietary rights, intellectual property rights, industrial property rights, personal or moral rights or any other rights, including without limitation, copyright, trademark, patent, trade secret, privacy, publicity or confidentiality obligations; or (2) otherwise violates the applicable state or federal law. Each entrant further represents and warrants that it has the necessary rights and licenses to use any and all data used in or for the Submission and otherwise as necessary for the terms hereunder.To the maximum extent permitted by law, each entrant indemnifies and agrees to keep indemnified Contest Entities at all times from and against any liability, claims, demands, losses, damages, costs and expenses resulting from any act, default or omission of the entrant and/or a breach of any warranty set forth herein. To the maximum extent permitted by law, each entrant agrees to defend, indemnify and hold harmless the Contest Entities from and against any and all claims, actions, suits or proceedings, as well as any and all losses, liabilities, damages, costs and expenses (including reasonable attorneys fees) arising out of or accruing from (a) any Submission or other material uploaded or otherwise provided by the entrant that infringes any copyright, trademark, trade secret, trade dress, patent or other intellectual property right of any person or defames any person or modifies their rights of publicity or privacy, (b) any misrepresentation made by the entrant in connection with the Contest; (c) any non-compliance by the entrant with these Rules; (d) claims brought by persons or entities other than the parties to these Rules arising from or related to the entrant’s involvement with the Contest; and (e) acceptance, possession, misuse or use of any prize or participation in any Contest-related activity or participation in this Contest.

Entrant releases Google from any liability associated with: (a) any malfunction or other problem with the Contest Site; (b) any error in the collection, processing, or retention of entry information; or (c) any typographical or other error in the printing, offering or announcement of any prize or winners.

##### 16\. ELIMINATION:

Any false information provided within the context of the Contest by any entrant concerning identity, mailing address, telephone number, email address, ownership of right or non-compliance with these Rules or the like may result in the immediate elimination of the entrant from the Contest.

##### 17\. INTERNET:

Contest Entities are not responsible for any malfunction of the entire Contest Site or any late, lost, damaged, misdirected, incomplete, illegible, undeliverable, or destroyed Submissions or entry materials due to system errors, failed, incomplete or garbled computer or other telecommunication transmission malfunctions, hardware or software failures of any kind, lost or unavailable network connections, typographical or system/human errors and failures, technical malfunction(s) of any telephone network or lines, cable connections, satellite transmissions, servers or providers, or computer equipment, traffic congestion on the Internet or at the Contest Site, or any combination thereof, including other telecommunication, cable, digital or satellite malfunctions which may limit an entrant’s ability to participate.

##### 18\. RIGHT TO CANCEL, MODIFY OR DISQUALIFY:

If for any reason the Contest is not capable of running as planned, including infection by computer virus, bugs, tampering, unauthorized intervention, fraud, technical failures, or any other causes which corrupt or affect the administration, security, fairness, integrity, or proper conduct of the Contest, Google reserves the right at its sole discretion to cancel, terminate, modify or suspend the Contest. Google further reserves the right to disqualify any entrant who tampers with the submission process or any other part of the Contest or Contest Site. Any attempt by an entrant to deliberately damage any web site, including the Contest Site, or undermine the legitimate operation of the Contest is a violation of criminal and civil laws and should such an attempt be made, Google reserves the right to seek damages from any such entrant to the fullest extent of the applicable law.

##### 19\. NOT AN OFFER OR CONTRACT OF EMPLOYMENT:

Under no circumstances shall the submission of a Submission into the Contest, the awarding of a prize, or anything in these Rules be construed as an offer or contract of employment with either Google, or the Contest Entities. You acknowledge that you have submitted your Submission voluntarily and not in confidence or in trust. You acknowledge that no confidential, fiduciary, agency or other relationship or implied-in-fact contract now exists between you and Google or the Contest Entities and that no such relationship is established by your submission of a Submission under these Rules.

##### 20\. FORUM AND RECOURSE TO JUDICIAL PROCEDURES:

These Rules shall be governed by, subject to, and construed in accordance with the laws of the State of California, United States of America, excluding all conflict of law rules. If any provision(s) of these Rules are held to be invalid or unenforceable, all remaining provisions hereof will remain in full force and effect. To the extent permitted by law, the rights to litigate, seek injunctive relief or make any other recourse to judicial or any other procedure in case of disputes or claims resulting from or in connection with this Contest are hereby excluded, and all Participants expressly waive any and all such rights.

##### 21\. ARBITRATION:

By entering the Contest, you agree that exclusive jurisdiction for any dispute, claim, or demand related in any way to the Contest will be decided by binding arbitration. All disputes between you and Google of whatsoever kind or nature arising out of these Rules, shall be submitted to Judicial Arbitration and Mediation Services, Inc. (“JAMS”) for binding arbitration under its rules then in effect in the San Jose, California, USA area, before one arbitrator to be mutually agreed upon by both parties. The parties agree to share equally in the arbitration costs incurred.

##### 22\. ADDITIONAL TERMS:

Please review the Devpost Terms of Service at [https://info.devpost.com/terms](https://info.devpost.com/terms) for additional rules that apply to your participation in the Contest and more generally your use of the Contest Site. Such Terms of Service are incorporated by reference into these Official Rules, including that the term "Poster" in the Terms of Service shall mean the same as "Sponsor" in these Official Rules." If there is a conflict between the Terms of Service and these Official Rules, these Official Rules shall control with respect to this Contest only.

##### 23\. ENTRANT'S PERSONAL INFORMATION:

Information collected from entrants is subject to Devpost’s Privacy Policy, which is available at [https://info.devpost.com/privacy](https://info.devpost.com/privacy).

For questions, send an email to support@devpost.com.

## No conversations yet

Head towards the [Participants tab](https://gemini3.devpost.com/participants) to find teammates, and start conversations by clicking the "Message" button.

P.S. Ensure your status is set to Looking for teammates.

[Messaging](https://gemini3.devpost.com/#)

> Source: `docs/data_engineering/gemini/gemini-code-assist-configuration.md`

# Google Gemini Code Assist: Custom Configuration Research Report

**Research Date:** November 20, 2025
**Focus:** Custom configuration, project-specific behavior, commands, and standardization

---

## Executive Summary

Google's Gemini Code Assist offers extensive customization capabilities through multiple configuration mechanisms. The platform supports both IDE extensions (VS Code, JetBrains, Android Studio) and a powerful CLI tool, each with distinct configuration approaches. Recent 2025 updates introduced personalization features including custom commands, rules, and enhanced context management powered by the Gemini 2.5 model.

Key findings:
- **Project-level configuration** through `.gemini/` folder with YAML and Markdown files
- **Custom slash commands** using TOML format for CLI
- **IDE-specific customization** through rules and custom commands
- **MCP (Model Context Protocol)** integration for extensibility
- **Enterprise features** for codebase-specific training and indexing
- **Limited cross-platform standardization** (platform-specific formats dominate)

---

## 1. Project Configuration Mechanisms

### 1.1 Repository-Level Configuration (.gemini/ folder)

Gemini Code Assist supports a `.gemini/` folder at the repository root for project-wide configuration.

#### config.yaml

**Purpose:** Controls features, file exclusions, and code review behavior

**Location:** `.gemini/config.yaml`

**Schema:**
```yaml
# Enable fun features (poems, creative responses)
have_fun: false

# Memory configuration
memory_config:
  disabled: false

# Code review settings
code_review:
  disable: false
  comment_severity_threshold: MEDIUM  # Options: LOW, MEDIUM, HIGH, CRITICAL
  max_review_comments: -1  # -1 = unlimited
  pull_request_opened:
    help: false
    summary: true
    code_review: true
    include_drafts: true

# File patterns to ignore (glob format)
ignore_patterns: []
```

**Key Features:**
- **Severity filtering:** Control which code review comments appear based on importance
- **PR automation:** Configure automatic summaries and reviews on PR creation
- **File exclusions:** Use glob patterns to exclude specific files/folders
- **Configuration precedence:** Repository config overrides group/organization settings

#### styleguide.md

**Purpose:** Natural language coding conventions and best practices

**Location:** `.gemini/styleguide.md`

**Format:** Free-form Markdown (no strict schema)

**Usage:**
- Describe project-specific coding standards
- Define preferred libraries and frameworks
- Specify documentation requirements
- Set naming conventions
- Outline architectural patterns

**Example content:**
```markdown
# Project Style Guide

## Code Standards
- Use TypeScript strict mode for all new files
- Follow functional programming patterns where possible
- Prefer async/await over promise chains

## Documentation
- All public functions must have JSDoc comments
- Include @example tags for complex functions

## Testing
- Minimum 80% code coverage required
- Use Jest for unit tests, Playwright for E2E
```

**Configuration Hierarchy:**
- Repository `styleguide.md` combines with organization-level style guides
- Both are considered during code review and generation
- Repository settings take precedence in case of conflicts

### 1.2 Context Exclusion (.aiexclude)

**Purpose:** Exclude files from local codebase indexing

**Location:** `.aiexclude` (workspace root by default)

**Format:** Similar to `.gitignore` syntax

**Features:**
- Automatically respects `.gitignore` patterns
- Custom path configurable in VS Code settings: `Context Exclusion File`
- Affects code completion, generation, transformation, and chat context

**Example:**
```
# Build artifacts
dist/
build/
*.min.js

# Sensitive files
.env
secrets.yaml
*.key

# Large data files
data/
*.csv
*.db
```

---

## 2. Custom Commands & Skills

### 2.1 Gemini CLI Slash Commands

Gemini CLI supports custom slash commands through TOML configuration files, providing reusable prompts for streamlined workflows.

#### Command Storage Locations

**User-scoped (global):**
- Location: `~/.gemini/commands/`
- Availability: All projects for the current user
- Use case: Personal productivity commands

**Project-scoped:**
- Location: `.gemini/commands/`
- Availability: Only within the specific project
- Use case: Team-shared, project-specific workflows
- Recommendation: Check into version control for team distribution

#### TOML File Structure

**Minimal format:**
```toml
prompt = "Your instruction to Gemini"
```

**Complete format:**
```toml
description = "Brief one-line description shown in /help menu"
prompt = """
Multi-line prompt with detailed instructions.
Supports {{args}} for dynamic user input.
Can execute shell commands with !{command}.
"""
```

#### Command Naming & Namespacing

**File path determines command name:**
- `commands/test.toml` → `/test`
- `commands/review.toml` → `/review`
- `commands/git/commit.toml` → `/git:commit` (namespaced)
- `commands/db/migrate.toml` → `/db:migrate`

**Rules:**
- Command names are **case-sensitive**
- Subdirectories create namespaces using colon (`:`) separator
- No spaces or special characters in filenames

#### Dynamic Arguments with {{args}}

The `{{args}}` placeholder is replaced with user-provided text:

```toml
description = "Generate unit tests for a function"
prompt = """
Create comprehensive unit tests for the following code:

{{args}}

Include edge cases and error scenarios.
"""
```

**Usage:** `/test function calculateTotal(items) { ... }`

#### Shell Command Injection with !{...}

Execute shell commands and inject output directly into prompts:

```toml
description = "Generate a Git commit message from staged changes"
prompt = """
Analyze the following staged changes and generate a concise commit message:

!{git diff --staged}

Follow conventional commit format (feat/fix/docs/etc).
"""
```

**Features:**
- Automatic shell escaping when `{{args}}` used inside `!{...}`
- Commands execute in the current working directory
- Output is captured and inserted into the prompt

#### Complete Example: Code Review Command

**File:** `.gemini/commands/review.toml`

```toml
description = "Review a pull request based on GitHub issue number"
prompt = """
Review the pull request for GitHub issue: {{args}}

Steps:
1. Fetch PR details: !{gh pr view {{args}} --json title,body,files}
2. Read modified files using available tools
3. Check against project conventions in styleguide.md
4. Analyze for:
   - Code quality and maintainability
   - Security vulnerabilities
   - Performance issues
   - Test coverage
   - Documentation completeness

Provide structured feedback with:
- Summary of changes
- Critical issues (must fix)
- Suggestions (nice to have)
- Positive highlights
"""
```

**Usage:** `/review 123`

### 2.2 IDE Extension Custom Commands

Custom commands are also available in IDE extensions (VS Code, JetBrains) with a different configuration approach.

#### VS Code Configuration

**Access:**
1. Open Settings (Ctrl+Shift+P / Cmd+Shift+P)
2. Search for "Gemini Code Assist"
3. Navigate to "Custom Commands" section
4. Add commands through UI

**Usage:**
- Open Quick Pick menu (Ctrl+I / Cmd+I)
- Select "Custom Commands"
- Choose or create a command

**Built-in commands:**
- `/fix` - Fix code issues
- `/generate` - Generate new code
- `/doc` - Add documentation
- `/simplify` - Simplify code

#### JetBrains IDE Configuration

**Access:**
1. Settings > Tools > Gemini > Prompt Library
2. Add custom commands
3. Configure scope (IDE-level or Project-level)

**Scopes:**
- **IDE-level:** Private to user, available across projects
- **Project-level:** Shared with team, project-specific

### 2.3 MCP Prompts as Slash Commands

Gemini CLI supports Model Context Protocol (MCP) prompts as slash commands, providing seamless integration with MCP servers.

**Features:**
- MCP prompt name becomes the command name
- MCP prompt description shows in help menu
- Arguments supported: `--<arg_name>="value"` or positional
- Listed in `/mcp` command output

**Example usage:**
```bash
# If an MCP server provides a "summarize" prompt
/summarize --file="README.md" --length="short"
```

---

## 3. IDE Rules System

The Rules system allows natural language instructions that guide Gemini's behavior across all interactions.

### 3.1 VS Code Rules

**Access:**
1. Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. "Preferences: Open Settings (UI)"
3. Search: "Geminicodeassist: Rules"

**Configuration:**
- Multi-line text field
- One rule per line
- Applied to all prompts and requests

**Example rules:**
```
Always generate unit tests when creating a new function
Use TypeScript strict mode for type definitions
Prefer functional components over class components in React
Follow the repository's ESLint configuration
Include error handling in all API calls
Add JSDoc comments for public functions
```

### 3.2 JetBrains Rules

**Access:** Settings > Tools > Gemini > Prompt Library > Rules

**Scopes:**
- **IDE scope:** Personal rules, all projects
- **Project scope:** Team-shared, version-controlled

**Features:**
- Scope selector for organizing rules
- Project-level rules can be committed to repository
- Same multi-line format as VS Code

### 3.3 Rules vs. styleguide.md

| Feature | Rules (IDE) | styleguide.md (Repository) |
|---------|------------|----------------------------|
| **Scope** | IDE-wide or project-wide | Repository-wide |
| **Format** | Plain text lines | Markdown document |
| **Storage** | IDE settings / `.gemini/` | `.gemini/styleguide.md` |
| **Purpose** | Immediate behavior guidance | Comprehensive style guide |
| **Applies to** | All prompts and generations | Code reviews and context |
| **Version control** | Optional (project scope) | Required (in repository) |

**Recommendation:** Use Rules for immediate constraints, styleguide.md for comprehensive documentation.

---

## 4. Enterprise Features: Code Customization

Gemini Code Assist Enterprise offers advanced customization based on your organization's private codebase.

### 4.1 Repository Indexing

**Purpose:** Train Gemini on organization-specific code patterns

**Process:**
1. Configure remote repositories for indexing
2. Gemini analyzes and parses repository structure
3. Index used for contextually aware suggestions

**Benefits:**
- Code suggestions aligned with organizational style
- Faster lookups within your codebase
- Better understanding of internal libraries and frameworks

### 4.2 Repository Context Selection

**Usage:** Type `@` in chat prompt to select repositories

**Features:**
- Select one or more indexed repositories as context
- Focus suggestions on specific microservices or modules
- Get relevant code based on your current task

**Example:**
```
@backend-api @shared-utils How do I authenticate API requests?
```

### 4.3 Code Customization Benefits

- **Aligned suggestions:** Code matches your team's patterns
- **Faster development:** Less manual correction needed
- **Knowledge retention:** Captures organizational best practices
- **Consistency:** Standardized approach across team members

**Security & Privacy:**
- Source code stored in isolated Google Cloud managed project
- No training of foundation Gemini model with private data
- Full control over indexed repositories
- Data can be purged at any time

---

## 5. MCP (Model Context Protocol) Integration

### 5.1 Overview

Gemini Code Assist supports MCP for extensibility, allowing integration with external tools and data sources.

**MCP Capabilities:**
- Connect to local or remote MCP servers
- Access external APIs and databases
- Integrate with development tools (GitHub, Slack, etc.)
- Extend agent capabilities with custom tools

### 5.2 Configuration Format (settings.json)

**Location:**
- Global: `~/.gemini/settings.json`
- Project: `.gemini/settings.json`

**Structure:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable-path",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      },
      "timeout": 30000,
      "includeTools": ["tool1", "tool2"],
      "excludeTools": ["tool3"]
    },
    "http-server": {
      "httpUrl": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer token"
      },
      "timeout": 30000
    },
    "sse-server": {
      "url": "https://events.example.com/stream"
    }
  }
}
```

### 5.3 Transport Types

**1. Stdio (Local Process)**
```json
{
  "git": {
    "command": "uvx",
    "args": ["mcp-server-git", "--repository", "."]
  }
}
```

**2. HTTP**
```json
{
  "github": {
    "httpUrl": "https://api.github.com/mcp",
    "headers": {
      "Authorization": "Bearer ghp_xxxxx"
    }
  }
}
```

**3. SSE (Server-Sent Events)**
```json
{
  "realtime": {
    "url": "https://events.example.com/mcp-stream"
  }
}
```

### 5.4 Built-in MCP Commands

**In Gemini CLI:**
- `/tools` - Display available tools from MCP servers
- `/mcp` - List configured servers and connection status

**Features:**
- Tool filtering with `includeTools`/`excludeTools`
- Authentication via headers or environment variables
- Timeout configuration for reliability
- Automatic reconnection on failure

---

## 6. Local Codebase Awareness

### 6.1 Automatic Indexing

**Features:**
- Enabled by default
- Indexes workspace files for context
- Improves relevance of suggestions and responses

**Applies to:**
- Code completion
- Code generation
- Code transformation
- Chat responses

### 6.2 Manual Context Selection

**Usage:** Type `@` in chat to select specific files

**Benefits:**
- Include only relevant files in context
- Reduce token usage
- More focused responses

**Example:**
```
@src/auth.ts @src/middleware.ts How can I add rate limiting?
```

### 6.3 Context Management

**Best practices:**
- Use `.aiexclude` to exclude large or irrelevant files
- Select specific files with `@` for focused queries
- Leverage repository indexing (Enterprise) for large codebases
- Combine local and remote repository context

---

## 7. Agent Mode Features

Gemini Code Assist offers an "Agent Mode" that expands capabilities beyond simple chat interactions.

### 7.1 Capabilities

**Multi-file edits:**
- Modify multiple files in a single operation
- Maintain consistency across changes

**Full project context:**
- Understands entire codebase structure
- Makes informed architectural decisions

**Built-in tools:**
- File read/write
- Grep search
- Code analysis
- Test execution

**MCP integration:**
- Access external tools and services
- Execute custom workflows
- Integrate with CI/CD pipelines

**Human-in-the-loop:**
- Review suggested changes before applying
- Approve or reject individual modifications
- Iterative refinement

### 7.2 Usage

**Activation:**
- Available in IDE extensions and CLI
- Triggered by complex, multi-step tasks
- Automatic context gathering

**Example workflow:**
```
User: "Add authentication to the API using JWT tokens"

Agent:
1. Analyzes current API structure
2. Identifies files requiring modification
3. Proposes changes across:
   - Auth middleware
   - User routes
   - Database models
   - Configuration files
4. Presents diff view for review
5. Applies changes on approval
6. Suggests tests and documentation updates
```

---

## 8. Cross-Platform Configuration Standards

### 8.1 Gemini-Specific Formats

Gemini Code Assist uses platform-specific configuration formats:

| Format | Purpose | Portability |
|--------|---------|-------------|
| `.gemini/config.yaml` | Repository settings | Gemini-specific |
| `.gemini/styleguide.md` | Coding conventions | Readable by any tool |
| `.gemini/commands/*.toml` | CLI slash commands | Gemini CLI only |
| `~/.gemini/settings.json` | User preferences, MCP | Gemini-specific |
| `.aiexclude` | Context exclusion | Potentially shareable |

### 8.2 Comparison with Other AI Assistants

**GitHub Copilot:**
- Configuration: `.github/copilot-instructions.md`
- Format: Markdown (natural language)
- Scope: Repository-wide
- Features: Custom instructions only (no commands)

**Cursor:**
- Configuration: `.cursor/rules` (current) or `.cursorrules` (legacy)
- Format: Individual rule files or single file
- Scope: Project-wide
- Features: Project rules, workspace configuration

**Claude Code (this platform):**
- Configuration: `.claude/`, `CLAUDE.md`
- Format: Markdown for instructions, TOML for commands
- Scope: Project and user-level
- Features: Slash commands, skills, instructions

### 8.3 Emerging Standards

**Limited standardization exists:**
- No unified format across platforms
- Each tool has proprietary configuration
- Markdown instructions most portable

**Emerging initiatives:**
- **AGENTS.md**: Proposed universal format for AI coding assistants
- **ContextHub**: Tool for managing unified configurations with symlinks
- **knowhub**: System for sharing AI assistant rules across repositories

**Current reality:**
- Teams using multiple AI tools must maintain separate configs
- Markdown-based instructions (styleguide.md, copilot-instructions.md) offer some portability
- Custom commands and rules are platform-specific

### 8.4 Interoperability Recommendations

**For maximum compatibility:**

1. **Use Markdown for instructions:**
   - `.gemini/styleguide.md` readable by humans and other tools
   - `.github/copilot-instructions.md` for GitHub Copilot
   - `CLAUDE.md` for Claude Code

2. **Document platform-specific features:**
   - Maintain README explaining custom commands
   - Provide examples for each platform

3. **Standardize where possible:**
   - `.gitignore` patterns (respected by many tools)
   - `.aiexclude` conventions
   - EditorConfig for formatting

4. **Consider abstraction layers:**
   - Tools like ContextHub to maintain single source of truth
   - Scripts to generate platform-specific configs from master file

---

## 9. Configuration Best Practices

### 9.1 Repository Setup

**Recommended structure:**
```
project-root/
├── .gemini/
│   ├── config.yaml          # Repository settings
│   ├── styleguide.md        # Coding conventions
│   └── commands/            # Team-shared commands
│       ├── review.toml
│       ├── test.toml
│       └── deploy/
│           ├── staging.toml
│           └── production.toml
├── .aiexclude              # Context exclusions
└── .gitignore              # Standard Git exclusions
```

**Version control:**
- ✅ Commit `.gemini/config.yaml`
- ✅ Commit `.gemini/styleguide.md`
- ✅ Commit `.gemini/commands/` (project-scoped)
- ✅ Commit `.aiexclude`
- ❌ Don't commit `~/.gemini/settings.json` (contains user credentials)

### 9.2 Team Collaboration

**Establish conventions:**
1. Document custom commands in project README
2. Define code review standards in styleguide.md
3. Use project-scoped JetBrains rules for team consistency
4. Share MCP server configurations (without credentials)

**Communication:**
- Add comments in config files explaining choices
- Update team when adding new commands
- Document expected behavior in styleguide.md
- Create onboarding guide for Gemini setup

### 9.3 Security Considerations

**Protect sensitive data:**
- Use `.aiexclude` for secrets, keys, credentials
- Add environment variables to exclusion list
- Don't commit API keys in settings.json
- Use MCP environment variables for credentials

**Enterprise data:**
- Review indexed repositories regularly
- Understand data retention policies
- Use organization-level controls for compliance
- Audit code customization usage

### 9.4 Performance Optimization

**Context management:**
- Exclude large data files via `.aiexclude`
- Use selective context with `@` mentions
- Index only relevant repositories (Enterprise)
- Limit max_review_comments to prevent overload

**Command efficiency:**
- Keep prompts focused and specific
- Use shell commands to preprocess data
- Cache expensive operations in scripts
- Leverage MCP servers for heavy computations

---

## 10. Migration Guide

### 10.1 From No Configuration

**Step 1: Add basic configuration**
```yaml
# .gemini/config.yaml
have_fun: false
code_review:
  comment_severity_threshold: MEDIUM
ignore_patterns:
  - "*.min.js"
  - "dist/"
  - "build/"
```

**Step 2: Create style guide**
```markdown
# .gemini/styleguide.md

## Code Standards
- [Your team's conventions]

## Testing Requirements
- [Coverage expectations]
```

**Step 3: Add useful commands**
```toml
# .gemini/commands/test.toml
description = "Run tests for changed files"
prompt = """
Run tests for files changed in the current branch:
!{git diff main --name-only | grep '.test.'}
"""
```

### 10.2 From GitHub Copilot

**Convert instructions:**
1. Copy `.github/copilot-instructions.md` content
2. Create `.gemini/styleguide.md`
3. Paste and adapt formatting if needed

**Copilot doesn't have equivalents for:**
- config.yaml settings
- Custom slash commands
- MCP integration

### 10.3 From Cursor

**Convert rules:**
1. Copy `.cursorrules` or `.cursor/rules` content
2. Add as IDE Rules (Settings > Gemini > Rules)
3. Or include in `.gemini/styleguide.md`

**Note:** Cursor rules are closer to Gemini Rules than config.yaml

---

## 11. Future Roadmap & Trends

### 11.1 Recent Additions (2025)

**May/June 2025 updates:**
- Gemini 2.5 model integration
- Custom commands in IDE extensions
- Rules/personalization features
- Enhanced context management
- MCP support in CLI

### 11.2 Expected Evolution

**Based on industry trends:**
- Increased standardization across AI assistants
- More sophisticated context management
- Deeper integration with development tools
- Enhanced team collaboration features
- Better privacy and security controls

**Gemini-specific:**
- Expanded MCP ecosystem
- More built-in tools in agent mode
- Improved code customization algorithms
- Better multi-repository understanding
- Enhanced project structure awareness

---

## 12. Comparison Matrix

| Feature | Gemini Code Assist | GitHub Copilot | Cursor | Claude Code |
|---------|-------------------|----------------|--------|-------------|
| **Custom Instructions** | ✅ Rules + styleguide.md | ✅ copilot-instructions.md | ✅ .cursor/rules | ✅ CLAUDE.md |
| **Slash Commands** | ✅ TOML files | ❌ | ❌ | ✅ Markdown files |
| **File Exclusions** | ✅ .aiexclude | ✅ .gitignore | ✅ .cursorignore | ✅ .gitignore |
| **Repository Config** | ✅ .gemini/ folder | ✅ .github/ folder | ✅ .cursor/ folder | ✅ .claude/ folder |
| **MCP Integration** | ✅ Native support | ❌ | ❌ | ✅ Native support |
| **Enterprise Indexing** | ✅ Private repo indexing | ❌ | ❌ | ❌ |
| **Agent Mode** | ✅ Multi-file edits | ❌ | ✅ Agent features | ✅ Agent features |
| **IDE Support** | VS Code, JetBrains, Android Studio | VS Code, Visual Studio, JetBrains | Cursor (VS Code fork) | CLI, Web |
| **CLI Tool** | ✅ gemini-cli | ❌ | ❌ | ✅ Native |
| **Code Review** | ✅ Automated PR reviews | ✅ Comments | ✅ Code review | ✅ PR tools |

---

## 13. Conclusion

### Key Findings

**Strengths:**
1. **Comprehensive configuration system** with multiple layers (user, project, repository)
2. **Powerful CLI** with custom commands via TOML
3. **MCP integration** for extensibility
4. **Enterprise features** for organization-specific customization
5. **Multi-IDE support** with consistent features

**Limitations:**
1. **Platform-specific formats** - limited portability to other tools
2. **No cross-platform standard** - must maintain separate configs for multi-tool teams
3. **Learning curve** - multiple configuration mechanisms to understand
4. **Enterprise dependency** - best features require paid tier

### Recommendations

**For individual developers:**
- Start with IDE Rules for immediate customization
- Create user-scoped commands (~/.gemini/commands/) for personal workflows
- Use .aiexclude to exclude irrelevant files

**For teams:**
- Establish .gemini/ folder structure in repositories
- Document coding standards in styleguide.md
- Create project-scoped commands for common workflows
- Use config.yaml for code review automation

**For enterprises:**
- Enable Code Customization for organization-specific training
- Set up repository indexing for internal libraries
- Deploy organization-level style guides
- Integrate MCP servers for internal tools

### Future Outlook

Gemini Code Assist is actively evolving with regular feature additions. The 2025 updates demonstrate Google's commitment to customization and extensibility. However, the AI coding assistant space still lacks standardization, requiring teams using multiple tools to maintain separate configurations.

The MCP protocol offers promise for tool integration standardization, but configuration formats remain tool-specific. Teams should expect to maintain platform-specific configs for the foreseeable future while advocating for industry-wide standards.

---

## 14. Additional Resources

### Official Documentation
- Gemini Code Assist Docs: https://developers.google.com/gemini-code-assist/docs/
- Gemini CLI GitHub: https://github.com/google-gemini/gemini-cli
- Code Customization Guide: https://cloud.google.com/gemini/docs/codeassist/code-customization
- Custom Commands Blog: https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands

### Community Resources
- Gemini CLI Codelabs: https://codelabs.developers.google.com/gemini-cli-hands-on
- MCP Specification: https://modelcontextprotocol.io/
- Community command repositories on GitHub

### Related Standards
- AGENTS.md proposal for universal AI assistant configuration
- Model Context Protocol (MCP) for tool integration
- EditorConfig for cross-platform editor settings

---

**Report prepared for:** Hackathon Project Research
**Next steps:** Evaluate applicability to current project architecture and team workflow


## AI & LLM Infrastructure — Gradio


> Source: `docs/data_engineering/gradio/gradio-comprehensive-research.md`

# Gradio Comprehensive Research Report

**Generated**: 2025-11-18
**Purpose**: In-depth research covering all aspects of Gradio for building ML demos and web applications

---

## Table of Contents

1. [Core Features](#1-core-features)
2. [Common Patterns](#2-common-patterns)
3. [Ontologies and Architecture](#3-ontologies-and-architecture)
4. [Component Library](#4-component-library)
5. [Advanced Features](#5-advanced-features)
6. [Best Practices](#6-best-practices)
7. [Integration Patterns](#7-integration-patterns)
8. [Code Examples](#8-code-examples)

---

## 1. Core Features

### 1.1 Overview

Gradio is a Python library that enables developers to build and share machine learning demos and web applications entirely in Python, without requiring HTML, CSS, or JavaScript knowledge. It requires Python 3.10 or higher.

**Installation**:
```bash
pip install --upgrade gradio
```

### 1.2 Primary APIs

#### Interface Class
The `gr.Interface` class is the simplest way to create Gradio demos. It wraps Python functions with a web UI using three essential parameters:

- **fn**: The Python function to interface
- **inputs**: Gradio component(s) matching function arguments
- **outputs**: Gradio component(s) matching return values

**Basic Example**:
```python
import gradio as gr

def greet(name, intensity):
    return "Hello, " + name + "!" * int(intensity)

demo = gr.Interface(
    fn=greet,
    inputs=["text", "slider"],
    outputs=["text"],
)
demo.launch()
```

**When to use Interface**:
- Simple, straightforward demos with uncomplicated layouts
- Single function with clear inputs and outputs
- Quickest way to create a demo

#### Blocks API
`gr.Blocks` is a more low-level and flexible alternative to the Interface class. It offers more control over:

1. The layout of components (Row, Column, Tab, Accordion)
2. The events that trigger the execution of functions
3. Data flows (e.g., inputs can trigger outputs, which can trigger the next level of outputs)

**When to use Blocks**:
- Need flexible positioning of components
- Multiple-step interfaces where output of one model becomes input to another
- Complex data flows with multiple inputs and outputs
- Need to change component properties or visibility based on user input
- When layouts outgrow the Interface class

#### ChatInterface
`gr.ChatInterface` is specialized for building chatbot applications quickly.

#### TabbedInterface
Combines multiple Interface objects into a single app with tabs:

```python
demo1 = gr.Interface(fn=function1, inputs="text", outputs="text")
demo2 = gr.Interface(fn=function2, inputs="image", outputs="label")

tabbed_interface = gr.TabbedInterface(
    [demo1, demo2],
    ["Tab 1 Name", "Tab 2 Name"]
)
```

### 1.3 Event System

Gradio uses an event-driven architecture where components can trigger events and attach event listeners.

**Common Events**:
- `.click()` - Triggered when buttons or clickable components are clicked
- `.change()` - Triggered when input values change
- `.submit()` - Triggered when forms are submitted (Enter key in textboxes)
- `.select()` - Triggered when items are selected (galleries, dataframes)
- `.input()` - Triggered in real-time as users type/interact
- `.upload()` - Triggered when files are uploaded

**Basic Syntax**:
```python
component.event_name(fn=function, inputs=[...], outputs=[...])
```

### 1.4 Sharing and Deployment

**Local Sharing**: Setting `share=True` in `launch()` generates a public URL instantly:
```python
demo.launch(share=True)  # Creates temporary public URL
```

**Deployment Options**:
- **HuggingFace Spaces** (Recommended): Native integration for free hosting
- **Custom Servers**: Deploy anywhere as standard web app
- **Docker**: Container deployment
- **Cloudflare, Netlify**: Static deployment options

### 1.5 Development Features

**Hot Reload Mode**:
```bash
gradio app.py  # Instead of python app.py - enables automatic updates
```

**Python Client API**: Any Gradio app can be used as an API:
```python
from gradio_client import Client

client = Client("abidlabs/whisper-large-v2")
result = client.predict("Hello")
```

---

## 2. Common Patterns

### 2.1 Component Composition

**Shorthand vs. Component Objects**:
```python
# Shorthand
gr.Interface(fn=process, inputs="text", outputs="text")

# Full component specification
gr.Interface(
    fn=process,
    inputs=gr.Textbox(label="Input", placeholder="Enter text..."),
    outputs=gr.Textbox(label="Output")
)
```

### 2.2 State Management

**Using gr.State for Session Data**:
```python
import gradio as gr

def increment(count):
    return count + 1, count + 1

with gr.Blocks() as demo:
    count_state = gr.State(value=0)  # Initialize with 0
    output = gr.Number(label="Count")
    btn = gr.Button("Increment")

    btn.click(increment, inputs=count_state, outputs=[count_state, output])
```

**Key Points about State**:
- Each user gets their own independent state
- State is not visible to users (unlike other components)
- Can store any Python object (lists, dicts, custom objects)
- Gets reset when user refreshes the page
- Useful for chatbots, multi-step forms, maintaining context

### 2.3 Event Handling Patterns

**Single Input/Output**:
```python
textbox.change(fn=process_text, inputs=textbox, outputs=label)
```

**Multiple Inputs/Outputs**:
```python
btn.click(
    fn=combine_inputs,
    inputs=[text1, text2, slider],
    outputs=[output1, output2]
)
```

**Chained Events**:
```python
# Output of one event becomes input to another
btn.click(fn=step1, inputs=input1, outputs=intermediate)
    .then(fn=step2, inputs=intermediate, outputs=final_output)
```

### 2.4 Layout Patterns

**Row and Column**:
```python
with gr.Blocks() as demo:
    with gr.Row():
        text1 = gr.Textbox()
        text2 = gr.Textbox()

    with gr.Row():
        with gr.Column(scale=2):  # Twice as wide
            output1 = gr.Textbox()
        with gr.Column(scale=1):
            output2 = gr.Textbox()
```

**Tabs**:
```python
with gr.Blocks() as demo:
    with gr.Tab("Image Processing"):
        img_input = gr.Image()
    with gr.Tab("Text Processing"):
        txt_input = gr.Textbox()
```

**Accordion**:
```python
with gr.Accordion("Advanced Settings", open=False):
    temperature = gr.Slider(0, 1, value=0.7)
    max_tokens = gr.Number(value=100)
```

### 2.5 Data Flow Patterns

**Linear Flow**:
```
Input → Function → Output
```

**Branching Flow**:
```
Input → Function → [Output1, Output2, Output3]
```

**Convergent Flow**:
```
[Input1, Input2, Input3] → Function → Output
```

**Cyclic Flow** (with State):
```
Input + State → Function → Output + Updated State
```

### 2.6 Chatbot Patterns

**Message Structure**:
```python
# Messages as list of [user_message, bot_message] pairs
def respond(message, history):
    history = history or []
    bot_message = generate_response(message)
    history.append([message, bot_message])
    return history, history

chatbot = gr.Chatbot()
msg = gr.Textbox()
msg.submit(respond, [msg, chatbot], [msg, chatbot])
```

**Message Formats**:
- **Panel layout**: LLM-style conversation interface
- **Bubble layout**: Chat bubbles with alternating sides
- **Roles**: "user", "assistant", "system" for message alignment

**Metadata Support**:
```python
# Metadata for tool usage/thoughts
{
    "title": "Thought",
    "id": "thought-1",
    "parent_id": "parent-thought",
    "duration": 2.5,
    "status": "complete"
}
```

---

## 3. Ontologies and Architecture

### 3.1 Conceptual Architecture

#### Component Hierarchy
```
Component (Base Class)
├── InputComponent
│   ├── Textbox
│   ├── Number
│   ├── Slider
│   ├── Image
│   ├── Audio
│   ├── Video
│   └── ...
├── OutputComponent
│   ├── Label
│   ├── Chatbot
│   └── ...
├── IOComponent (Both)
│   ├── Textbox
│   ├── Image
│   └── ...
└── LayoutComponent
    ├── Row
    ├── Column
    ├── Tab
    └── Accordion
```

### 3.2 Component Architecture

Each Gradio component follows a standardized architecture:

#### Interactive vs. Static Modes
- **Interactive version**: Allows users to modify values through the UI
- **Static version**: Displays values without user interaction capability
- Gradio automatically uses the interactive version when a component is used as an input to any event

#### Value Processing Pipeline

**Preprocess**:
- Converts values from frontend formats (JSON) into Python-native structures
- Examples: JSON → NumPy arrays, JSON → PIL Images
- Occurs before passing data to Python functions

**Postprocess**:
- Converts Python return values back into web-friendly JSON
- Occurs after Python function returns
- Prepares data for frontend display

**Process Flow**:
```
User Input (Frontend)
    ↓
[Preprocess]
    ↓
Python-Native Format
    ↓
[User Function]
    ↓
Python Output
    ↓
[Postprocess]
    ↓
JSON (Frontend Display)
```

### 3.3 Event System Architecture

**Event Registration**:
1. Component creates event listener (e.g., `.click()`)
2. Event bound to Python function
3. Inputs and outputs specified
4. Event added to dependency graph

**Event Execution Flow**:
```
User Interaction
    ↓
Event Triggered
    ↓
Queue (if enabled)
    ↓
Preprocess Inputs
    ↓
Execute Python Function
    ↓
Postprocess Outputs
    ↓
Update Frontend Components
```

### 3.4 Rendering Model

**Frontend**: Built with Svelte components
- Each Gradio component has corresponding Svelte implementation
- Two required files: `Index.svelte` (regular view), `Example.svelte` (example view)

**Backend**: Python-based FastAPI server
- Handles API requests
- Manages WebSocket connections for real-time updates
- Processes component data

**Communication**:
- RESTful API for predictions
- WebSocket for streaming and real-time updates
- JSON data interchange format

### 3.5 Design System

**CSS Variables**: Gradio provides a comprehensive CSS variable system

**Naming Convention**: `element_type_property_state_mode`

Example: `button_primary_background_fill_hover_dark`

**Variable Categories**:
- Core colors: `*primary_`, `*secondary_`, `*neutral_` with brightness levels (50-950)
- Core sizing: `*spacing_`, `*radius_`, `*text_`
- Component-specific variables

---

## 4. Component Library

### 4.1 Complete Component Catalog

Gradio includes 30+ specialized built-in components designed for machine learning applications.

#### Input Components

**Text & Numbers**:
- **Textbox**: Text input field (single or multiline)
- **Number**: Numeric input with validation
- **Dropdown**: Select from predefined options
- **Radio**: Single choice from list (radio buttons)
- **Checkbox**: Boolean input
- **CheckboxGroup**: Multiple checkboxes
- **Slider**: Range selection with min/max values
- **ColorPicker**: Color selection interface

**Media**:
- **Image**: Image upload, webcam capture, display
- **Audio**: Audio file upload, microphone recording, playback
- **Video**: Video file upload, playback
- **File**: General file upload with type filters
- **UploadButton**: Button-style file upload with customization

**Data**:
- **Dataframe**: Interactive tabular data display and editing
- **Dataset**: Predefined examples/datasets
- **Timeseries**: Time series data visualization

**Specialized**:
- **Code**: Code editor with syntax highlighting
- **DateTime**: Date and time picker
- **MultimodalTextbox**: Combined text + file input

#### Output Components

**Display**:
- **Label**: Classification results with confidence scores
- **Textbox**: Text display (can be both input/output)
- **JSON**: Formatted JSON display
- **HTML**: Render HTML content
- **Markdown**: Render markdown content
- **HighlightedText**: Text with highlighted segments
- **AnnotatedImage**: Image with annotations and labels

**Visualization**:
- **Plot**: Data visualization (Plotly, Matplotlib, Bokeh)
- **LinePlot**, **ScatterPlot**, **BarPlot**: Specific chart types
- **Gallery**: Grid of images
- **Model3D**: 3D model viewer (.obj, .glb, .gltf)

**Interactive**:
- **Chatbot**: Conversational interface with message history
- **Button**: Clickable button (typically triggers events)
- **ClearButton**: Pre-configured button to clear components
- **DuplicateButton**: Button to duplicate Spaces
- **DownloadButton**: Download file button

#### Layout Components

**Structural**:
- **Row**: Horizontal arrangement (flexbox)
- **Column**: Vertical arrangement with scale parameter
- **Tab**: Tabbed interface sections
- **Accordion**: Collapsible content panel
- **Group**: Logical grouping of components
- **Sidebar**: Left-side collapsible panel

**Container**:
- **Blocks**: Main container for custom layouts

### 4.2 Component Properties

**Common Properties** (most components):
- `label`: Display label for the component
- `visible`: Boolean to show/hide component
- `interactive`: Whether users can modify (vs. display-only)
- `elem_id`: Custom HTML element ID
- `elem_classes`: Custom CSS classes
- `value`: Default/initial value
- `show_label`: Whether to display the label

**Component-Specific Examples**:

**Textbox**:
- `placeholder`: Placeholder text
- `lines`: Number of visible lines
- `max_lines`: Maximum expandable lines
- `type`: "text" or "password"

**Image**:
- `source`: "upload", "webcam", or "canvas"
- `type`: "numpy", "pil", or "filepath"
- `shape`: Expected image dimensions

**Slider**:
- `minimum`: Minimum value
- `maximum`: Maximum value
- `step`: Increment step size

**UploadButton**:
- `file_types`: List of accepted file types ["image", "video", "audio", "text"]
- `file_count`: "single", "multiple", or "directory"

### 4.3 Dataset Component Compatibility

Components supported in `gr.Dataset`:
Audio, Checkbox, CheckboxGroup, ColorPicker, Dataframe, Dropdown, File, HTML, Image, Markdown, Model3D, Number, Radio, Slider, Textbox, TimeSeries, Video

---

## 5. Advanced Features

### 5.1 Queuing

**Purpose**: Scale to thousands of concurrent requests

**Enabling Queuing**:
```python
demo.queue().launch()
```

**Concurrency Control**:
```python
# Set max concurrent executions per event
demo.queue(default_concurrency_limit=5)

# Per-event concurrency
btn.click(fn=process, inputs=input, outputs=output, concurrency_limit=3)

# Unlimited concurrent executions
btn.click(fn=process, inputs=input, outputs=output, concurrency_limit=None)
```

**Parameters**:
- `default_concurrency_limit`: Default workers per event (default: 1)
- `concurrency_limit` (per event): Override default for specific events
- `max_size`: Maximum queue size before rejecting requests

### 5.2 Authentication

**Built-in Password Authentication**:
```python
demo.launch(auth=("username", "password"))

# Multiple users
demo.launch(auth=[("user1", "pass1"), ("user2", "pass2")])

# Custom auth function
def custom_auth(username, password):
    return username == "admin" and password == "secret"

demo.launch(auth=custom_auth)
```

**OAuth Options**:
- **HuggingFace OAuth**: Login via HuggingFace account
- **External OAuth**: Google, GitHub, etc. (requires configuration)

**Request Headers** (for advanced auth):
```python
def process(text, request: gr.Request):
    headers = request.headers
    # Access custom auth headers
    return result

demo = gr.Interface(fn=process, inputs="text", outputs="text")
```

### 5.3 Custom Components

**Creating Custom Components**:

**Workflow Steps**:
1. **Create**: `gradio cc create component-name` - Creates template
2. **Dev**: `gradio cc dev` - Launches development server with hot reloading
3. **Build**: `gradio cc build` - Builds Python package
4. **Publish**: `gradio cc publish` - Uploads to PyPI/HuggingFace

**Component Requirements**:
- Accept `interactive` boolean parameter in constructor
- Implement `preprocess()` and `postprocess()` methods
- Create `Index.svelte` and `Example.svelte` frontend files
- Optionally implement `process_example()` for custom example handling

**Discovery**: Browse custom components at [Gradio Custom Components Gallery](https://www.gradio.app/custom-components/gallery)

### 5.4 Flagging

**Purpose**: Collect data points from model demos for iterative improvement

**Flagging Modes**:
```python
demo = gr.Interface(
    fn=model,
    inputs="image",
    outputs="label",
    flagging_mode="manual",  # "manual", "auto", or "never"
    flagging_options=["Incorrect", "Ambiguous", "Offensive"],
    flagging_dir="flagged_data"
)
```

**Modes**:
- **manual** (default): Users see flag button, samples flag only when clicked
- **auto**: All samples automatically flagged
- **never**: No flagging

**Custom Flagging Callback**:
```python
class CustomCallback(gr.FlaggingCallback):
    def setup(self, components, flagging_dir):
        # Initialize storage
        pass

    def flag(self, flag_data, flag_option=None):
        # Handle flagged data
        pass

demo = gr.Interface(
    fn=model,
    inputs="image",
    outputs="label",
    flagging_callback=CustomCallback()
)
```

**Data Storage**:
- CSV log file with metadata
- Separate subdirectories for files (images, audio, etc.)
- Timestamps and flagging options recorded

### 5.5 Progress Indicators

**Basic Progress Tracking**:
```python
def long_process(input_data, progress=gr.Progress()):
    progress(0, desc="Starting...")
    # Process step 1
    progress(0.25, desc="25% complete")
    # Process step 2
    progress(0.5, desc="50% complete")
    # Process step 3
    progress(1.0, desc="Done!")
    return result

demo = gr.Interface(fn=long_process, inputs="text", outputs="text")
demo.queue().launch()  # Queue required for progress bars
```

**Automatic tqdm Integration**:
```python
from tqdm import tqdm

def process_items(items, progress=gr.Progress(track_tqdm=True)):
    results = []
    for item in tqdm(items):  # Automatically tracked
        results.append(process(item))
    return results
```

**Manual tqdm**:
```python
def process_items(items, progress=gr.Progress()):
    results = []
    for item in progress.tqdm(items, desc="Processing"):
        results.append(process(item))
    return results
```

**Progress Formats**:
- Float (0-1): Represents percentage completion
- Tuple: (current_step, total_steps)

### 5.6 Streaming

**Output Streaming with Generators**:
```python
def generate_text(prompt):
    output = ""
    for word in generate_words(prompt):
        output += word + " "
        yield output  # Progressively stream updates

demo = gr.Interface(
    fn=generate_text,
    inputs="text",
    outputs="text"
)
```

**Media Streaming**:
```python
def stream_audio():
    for audio_chunk in generate_audio_chunks():
        yield audio_chunk

demo = gr.Interface(
    fn=stream_audio,
    inputs=None,
    outputs=gr.Audio(streaming=True, autoplay=True)
)
```

**Key Points**:
- Use Python generators with `yield`
- Set `streaming=True` for Audio/Video components
- Set `autoplay=True` for automatic playback
- Enables real-time, low-latency updates

### 5.7 Examples

**Adding Examples**:
```python
demo = gr.Interface(
    fn=process,
    inputs=["text", "slider"],
    outputs="text",
    examples=[
        ["Hello", 3],
        ["Gradio", 5],
        ["Example", 2]
    ]
)
```

**Advanced Examples with Caching**:
```python
with gr.Blocks() as demo:
    input1 = gr.Textbox()
    input2 = gr.Slider(0, 10)
    output = gr.Textbox()

    btn = gr.Button("Submit")
    btn.click(fn=process, inputs=[input1, input2], outputs=output)

    gr.Examples(
        examples=[
            ["Example 1", 5],
            ["Example 2", 7]
        ],
        inputs=[input1, input2],
        outputs=output,
        fn=process,
        cache_examples=True  # Pre-compute example outputs
    )
```

**Cache Options**:
- `True`: Cache all examples on app launch
- `'lazy'`: Cache examples on first click
- `False`: No caching

### 5.8 Event Data Gathering

**SelectData**:
```python
def handle_select(evt: gr.SelectData):
    return f"You selected: {evt.value} at index {evt.index}"

gallery = gr.Gallery()
output = gr.Textbox()

gallery.select(fn=handle_select, inputs=None, outputs=output)
```

**Request Data**:
```python
def process_with_headers(text, request: gr.Request):
    user_agent = request.headers.get("user-agent")
    client_ip = request.client.host
    return f"Processed '{text}' from {client_ip}"

demo = gr.Interface(fn=process_with_headers, inputs="text", outputs="text")
```

### 5.9 Input Validation

```python
def validate_email(email):
    if "@" in email and "." in email:
        return gr.validate(is_valid=True)
    else:
        return gr.validate(
            is_valid=False,
            message="Please enter a valid email address"
        )

textbox = gr.Textbox()
textbox.change(fn=validate_email, inputs=textbox, outputs=None)
```

**Features**:
- Bypass queue for instant feedback
- Per-input error messages
- No server roundtrip for validation

### 5.10 Timers for Continuous Execution

```python
import gradio as gr
import time

def update_time():
    return time.strftime("%H:%M:%S")

with gr.Blocks() as demo:
    timer = gr.Timer(value=1)  # Update every 1 second
    clock = gr.Textbox(label="Current Time")

    timer.tick(fn=update_time, outputs=clock)

demo.launch()
```

### 5.11 Theming

**Built-in Themes**:
- `gr.themes.Base`: Minimal styling, blue primary
- `gr.themes.Default`: Vibrant orange primary
- `gr.themes.Origin`: Subdued colors (Gradio 4 style)
- `gr.themes.Citrus`: Yellow primary, 3D buttons
- `gr.themes.Monochrome`: Black/white newspaper aesthetic
- `gr.themes.Soft`: Purple primary, increased border radius
- `gr.themes.Glass`: Blue primary, translucent effects
- `gr.themes.Ocean`: Blue-green primary, gradients

**Using Themes**:
```python
demo = gr.Blocks(theme=gr.themes.Soft())
```

**Customizing Themes**:
```python
theme = gr.themes.Default(
    primary_hue="blue",
    secondary_hue="purple",
    neutral_hue="gray",
    spacing_size="lg",
    radius_size="md",
    text_size="md",
    font="IBM Plex Sans",
    font_mono="IBM Plex Mono"
)

theme = theme.set(
    button_primary_background_fill="*primary_200",
    button_primary_background_fill_hover="*primary_300",
    slider_color="#FF0000"
)

demo = gr.Blocks(theme=theme)
```

**Theme Variables**:
- **Colors**: `primary_hue`, `secondary_hue`, `neutral_hue` (slate, gray, red, orange, blue, purple, pink, etc.)
- **Sizing**: `spacing_size`, `radius_size`, `text_size` (sm, md, lg)
- **Fonts**: `font`, `font_mono`

**Sharing Themes**:
```python
# Upload to HuggingFace
theme.push_to_hub("my-custom-theme")

# Use community theme
my_theme = gr.Theme.from_hub("gradio/seafoam")
demo = gr.Blocks(theme="gradio/seafoam")  # Shorthand
```

**Theme Builder**:
```python
gr.themes.builder()  # Interactive theme designer
```

---

## 6. Best Practices

### 6.1 Security

**Input Validation**:
```python
def safe_process(user_input):
    # Validate and sanitize inputs
    if not isinstance(user_input, str):
        raise ValueError("Input must be string")
    if len(user_input) > 1000:
        raise ValueError("Input too long")

    # Process safely
    return process(user_input)
```

**Authentication**:
- Always use authentication for sensitive applications
- Prefer OAuth over simple passwords for production
- Never commit credentials to version control
- Use environment variables for secrets

**File Handling**:
```python
import os

def process_file(file):
    # Validate file type
    allowed_extensions = {'.jpg', '.png', '.pdf'}
    _, ext = os.path.splitext(file.name)
    if ext.lower() not in allowed_extensions:
        raise ValueError(f"File type {ext} not allowed")

    # Process file
    return result
```

### 6.2 Performance Optimization

**Model Loading**:
```python
import gradio as gr

# Load model once at startup (not in function)
model = load_heavy_model()

def predict(input_data):
    # Use pre-loaded model
    return model(input_data)

demo = gr.Interface(fn=predict, inputs="text", outputs="text")
```

**Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(input_data):
    # Computation cached for repeated inputs
    return result
```

**Lazy Loading**:
```python
model = None

def predict(input_data):
    global model
    if model is None:
        model = load_heavy_model()
    return model(input_data)
```

**Queue Configuration**:
```python
# Balance concurrency vs. memory
demo.queue(
    default_concurrency_limit=5,  # Limit concurrent executions
    max_size=100  # Maximum queue size
).launch()
```

**Loading Status**:
```python
def long_process(input_data, progress=gr.Progress()):
    progress(0, desc="Loading model...")
    model = load_model()
    progress(0.5, desc="Processing...")
    result = model(input_data)
    progress(1.0, desc="Complete!")
    return result
```

### 6.3 Error Handling

**Graceful Error Messages**:
```python
def safe_predict(input_data):
    try:
        result = model.predict(input_data)
        return result
    except ValueError as e:
        return f"Invalid input: {str(e)}"
    except Exception as e:
        return f"An error occurred. Please try again."
        # Log error for debugging
        print(f"Error: {e}")
```

**User-Friendly Feedback**:
```python
with gr.Blocks() as demo:
    input_box = gr.Textbox(
        label="Enter text",
        placeholder="Type here...",
        info="Maximum 100 characters"
    )
    error_box = gr.Textbox(label="Status", visible=False)
    output = gr.Textbox()

    def validate_and_process(text):
        if not text:
            return None, gr.update(value="Please enter text", visible=True)
        if len(text) > 100:
            return None, gr.update(value="Text too long!", visible=True)

        result = process(text)
        return result, gr.update(visible=False)

    input_box.submit(
        fn=validate_and_process,
        inputs=input_box,
        outputs=[output, error_box]
    )
```

### 6.4 Interface Design

**Clear Labels and Instructions**:
```python
demo = gr.Interface(
    fn=process,
    inputs=gr.Textbox(
        label="Input Text",
        placeholder="Enter your text here...",
        info="We'll process your text and return the result"
    ),
    outputs=gr.Textbox(label="Processed Result"),
    title="Text Processor",
    description="This tool processes text using advanced ML algorithms.",
    article="For more information, visit our documentation."
)
```

**Accessibility**:
- Use high contrast colors
- Provide alt text for images
- Enable keyboard navigation
- Use clear, descriptive labels

**Responsive Layout**:
```python
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=2):
            # Main content
            input_area = gr.Textbox()
        with gr.Column(scale=1):
            # Sidebar
            settings = gr.Accordion("Settings")
```

**Organization with Tabs and Accordions**:
```python
with gr.Blocks() as demo:
    with gr.Tab("Basic"):
        basic_input = gr.Textbox()

    with gr.Tab("Advanced"):
        with gr.Accordion("Advanced Settings", open=False):
            temperature = gr.Slider(0, 1)
            max_tokens = gr.Number()
```

### 6.5 Environment Management

**Using Environment Variables**:
```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv("API_KEY")
MODEL_PATH = os.getenv("MODEL_PATH", "default/path")

def predict(input_data):
    # Use environment variables
    return model.predict(input_data, api_key=API_KEY)
```

**Configuration for Different Environments**:
```python
import os

DEBUG = os.getenv("DEBUG", "False") == "True"

demo.launch(
    debug=DEBUG,
    share=False if DEBUG else True,
    server_name="0.0.0.0" if not DEBUG else "127.0.0.1"
)
```

### 6.6 Testing

**Unit Testing Functions**:
```python
def test_process_function():
    result = process("test input")
    assert result == "expected output"

def test_error_handling():
    try:
        process(None)
        assert False, "Should raise error"
    except ValueError:
        pass
```

**Integration Testing with Client**:
```python
from gradio_client import Client

# Test deployed app
client = Client("http://localhost:7860")
result = client.predict("test input")
assert result == "expected output"
```

### 6.7 Documentation

**Code Documentation**:
```python
def process_text(text: str, max_length: int = 100) -> str:
    """
    Process input text with length constraint.

    Args:
        text (str): Input text to process
        max_length (int): Maximum allowed length (default: 100)

    Returns:
        str: Processed text

    Raises:
        ValueError: If text is empty or exceeds max_length
    """
    if not text:
        raise ValueError("Text cannot be empty")
    if len(text) > max_length:
        raise ValueError(f"Text exceeds {max_length} characters")

    return text.upper()
```

**Interface Documentation**:
```python
demo = gr.Interface(
    fn=process_text,
    inputs=gr.Textbox(label="Input", info="Enter text to process"),
    outputs=gr.Textbox(label="Output"),
    title="Text Processor",
    description="Convert text to uppercase with length validation",
    article="""
    ## How to Use
    1. Enter your text in the input box
    2. Click Submit
    3. View the processed result

    ## Limitations
    - Maximum 100 characters
    - Text only (no special formatting)
    """
)
```

---

## 7. Integration Patterns

### 7.1 ML Framework Integration

#### PyTorch
```python
import torch
import gradio as gr

# Load PyTorch model
model = torch.load('model.pth')
model.eval()

def predict(image):
    # Preprocess
    tensor = preprocess(image)

    # Predict
    with torch.no_grad():
        output = model(tensor)

    # Postprocess
    return postprocess(output)

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=5)
)
```

#### TensorFlow
```python
import tensorflow as tf
import gradio as gr

# Load TensorFlow model
model = tf.keras.models.load_model('model.h5')

def predict(image):
    # Preprocess
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = tf.expand_dims(image, 0)

    # Predict
    predictions = model.predict(image)

    return {"class_1": float(predictions[0][0]),
            "class_2": float(predictions[0][1])}

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label()
)
```

#### HuggingFace Transformers
```python
from transformers import pipeline
import gradio as gr

# Load pipeline
classifier = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    result = classifier(text)[0]
    return {result['label']: result['score']}

demo = gr.Interface(
    fn=analyze_sentiment,
    inputs=gr.Textbox(lines=5),
    outputs=gr.Label()
)
```

#### Scikit-learn
```python
import pickle
import gradio as gr
import numpy as np

# Load sklearn model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

def predict(feature1, feature2, feature3):
    features = np.array([[feature1, feature2, feature3]])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    return {
        "prediction": prediction,
        "confidence": float(max(probability))
    }

demo = gr.Interface(
    fn=predict,
    inputs=[
        gr.Number(label="Feature 1"),
        gr.Number(label="Feature 2"),
        gr.Number(label="Feature 3")
    ],
    outputs=gr.JSON()
)
```

### 7.2 FastAPI Integration

**Mounting Gradio in FastAPI**:
```python
from fastapi import FastAPI
import gradio as gr

app = FastAPI()

# Regular FastAPI endpoints
@app.get("/api/status")
def get_status():
    return {"status": "healthy"}

@app.post("/api/predict")
def predict_api(text: str):
    return {"result": process(text)}

# Gradio interface
def process(text):
    return text.upper()

io = gr.Interface(fn=process, inputs="text", outputs="text")

# Mount Gradio at /gradio
app = gr.mount_gradio_app(app, io, path="/gradio")

# Run: uvicorn app:app
```

**Using Gradio Client with FastAPI**:
```python
from fastapi import FastAPI
from gradio_client import Client

app = FastAPI()

# Connect to external Gradio service
gradio_client = Client("https://huggingface.co/spaces/some-model")

@app.post("/predict")
def predict(text: str):
    result = gradio_client.predict(text)
    return {"prediction": result}
```

### 7.3 Database Integration

**SQLite Example**:
```python
import sqlite3
import gradio as gr
import pandas as pd

def query_database(query):
    conn = sqlite3.connect('database.db')
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame({"Error": [str(e)]})
    finally:
        conn.close()

demo = gr.Interface(
    fn=query_database,
    inputs=gr.Textbox(label="SQL Query", lines=3),
    outputs=gr.Dataframe()
)
```

**MongoDB Example**:
```python
from pymongo import MongoClient
import gradio as gr

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
collection = db['mycollection']

def search_documents(query):
    results = collection.find({"text": {"$regex": query}})
    return [doc['text'] for doc in results]

demo = gr.Interface(
    fn=search_documents,
    inputs=gr.Textbox(label="Search Query"),
    outputs=gr.JSON()
)
```

### 7.4 API Integration

**REST API Consumption**:
```python
import requests
import gradio as gr

def call_external_api(text):
    response = requests.post(
        "https://api.example.com/process",
        json={"text": text},
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()

demo = gr.Interface(
    fn=call_external_api,
    inputs=gr.Textbox(),
    outputs=gr.JSON()
)
```

**OpenAI Integration**:
```python
import openai
import gradio as gr

openai.api_key = "your-api-key"

def chat_with_gpt(message, history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    for msg in history:
        messages.append({"role": "user", "content": msg[0]})
        messages.append({"role": "assistant", "content": msg[1]})

    messages.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    return response.choices[0].message.content

demo = gr.ChatInterface(fn=chat_with_gpt)
```

### 7.5 Cloud Storage Integration

**S3 Integration**:
```python
import boto3
import gradio as gr

s3 = boto3.client('s3')

def upload_to_s3(file):
    try:
        s3.upload_file(
            file.name,
            'my-bucket',
            file.name.split('/')[-1]
        )
        return f"Uploaded successfully to S3"
    except Exception as e:
        return f"Error: {str(e)}"

demo = gr.Interface(
    fn=upload_to_s3,
    inputs=gr.File(),
    outputs=gr.Textbox()
)
```

### 7.6 Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  gradio-app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - MODEL_PATH=/models/model.pth
    volumes:
      - ./models:/models
    restart: unless-stopped
```

### 7.7 HuggingFace Spaces Deployment

**Required Files**:

**app.py**:
```python
import gradio as gr

def process(text):
    return text.upper()

demo = gr.Interface(fn=process, inputs="text", outputs="text")
demo.launch()
```

**requirements.txt**:
```
gradio>=4.0.0
transformers
torch
```

**README.md** (with YAML frontmatter):
```yaml
---
title: My Gradio App
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# My Gradio Application

Description of the app...
```

**Deployment Steps**:
1. Create Space on HuggingFace
2. Upload files or connect Git repository
3. Space automatically builds and deploys
4. Access at `https://huggingface.co/spaces/username/space-name`

**Hardware Upgrades**:
- CPU (free)
- GPU (paid): T4, A10G, A100
- Configure in Space settings

### 7.8 Microservice Architecture

```python
# Service 1: Image Processing
import gradio as gr

def process_image(image):
    # Image processing logic
    return processed_image

image_service = gr.Interface(
    fn=process_image,
    inputs=gr.Image(),
    outputs=gr.Image()
)
image_service.launch(server_port=7860)

# Service 2: Text Processing
def process_text(text):
    # Text processing logic
    return processed_text

text_service = gr.Interface(
    fn=process_text,
    inputs=gr.Textbox(),
    outputs=gr.Textbox()
)
text_service.launch(server_port=7861)

# Service 3: Orchestrator
from gradio_client import Client

image_client = Client("http://localhost:7860")
text_client = Client("http://localhost:7861")

def orchestrate(image, text):
    processed_image = image_client.predict(image)
    processed_text = text_client.predict(text)
    return processed_image, processed_text

orchestrator = gr.Interface(
    fn=orchestrate,
    inputs=[gr.Image(), gr.Textbox()],
    outputs=[gr.Image(), gr.Textbox()]
)
orchestrator.launch(server_port=7862)
```

---

## 8. Code Examples

### 8.1 Image Classification

```python
import gradio as gr
from transformers import pipeline

# Load model
classifier = pipeline("image-classification", model="google/vit-base-patch16-224")

def classify_image(image):
    predictions = classifier(image)
    return {p["label"]: p["score"] for p in predictions}

demo = gr.Interface(
    fn=classify_image,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=5),
    title="Image Classification",
    description="Upload an image to classify it",
    examples=[
        ["example1.jpg"],
        ["example2.jpg"]
    ]
)

demo.launch()
```

### 8.2 Text Generation Chatbot

```python
import gradio as gr
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def chat(message, history):
    # Encode input
    history_text = ""
    for user_msg, bot_msg in history:
        history_text += f"User: {user_msg}\nBot: {bot_msg}\n"

    input_text = history_text + f"User: {message}\nBot:"
    inputs = tokenizer.encode(input_text, return_tensors="pt")

    # Generate response
    outputs = model.generate(inputs, max_length=1000, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract bot response
    bot_response = response.split("Bot:")[-1].strip()

    return bot_response

demo = gr.ChatInterface(
    fn=chat,
    title="Conversational AI Chatbot",
    description="Chat with DialoGPT",
    theme=gr.themes.Soft()
)

demo.launch()
```

### 8.3 Audio Transcription

```python
import gradio as gr
from transformers import pipeline

# Load Whisper model
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-base")

def transcribe_audio(audio):
    if audio is None:
        return "No audio provided"

    result = transcriber(audio)
    return result["text"]

demo = gr.Interface(
    fn=transcribe_audio,
    inputs=gr.Audio(source="microphone", type="filepath"),
    outputs=gr.Textbox(label="Transcription"),
    title="Audio Transcription",
    description="Speak into your microphone to transcribe audio to text"
)

demo.launch()
```

### 8.4 Multi-Step Image Processing

```python
import gradio as gr
from PIL import Image, ImageFilter, ImageEnhance

def resize_image(image, width, height):
    return image.resize((width, height))

def apply_filter(image, filter_type):
    if filter_type == "Blur":
        return image.filter(ImageFilter.BLUR)
    elif filter_type == "Sharpen":
        return image.filter(ImageFilter.SHARPEN)
    elif filter_type == "Edge Enhance":
        return image.filter(ImageFilter.EDGE_ENHANCE)
    return image

def adjust_brightness(image, factor):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(factor)

with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("# Image Processing Pipeline")

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="Input Image")

            with gr.Tab("Resize"):
                width = gr.Slider(100, 1000, value=500, label="Width")
                height = gr.Slider(100, 1000, value=500, label="Height")
                resize_btn = gr.Button("Resize")

            with gr.Tab("Filter"):
                filter_type = gr.Radio(
                    ["Blur", "Sharpen", "Edge Enhance"],
                    label="Filter Type"
                )
                filter_btn = gr.Button("Apply Filter")

            with gr.Tab("Brightness"):
                brightness = gr.Slider(0.1, 2.0, value=1.0, label="Brightness Factor")
                brightness_btn = gr.Button("Adjust Brightness")

        with gr.Column():
            output_image = gr.Image(type="pil", label="Output Image")

    # Event handlers
    resize_btn.click(
        fn=resize_image,
        inputs=[input_image, width, height],
        outputs=output_image
    )

    filter_btn.click(
        fn=apply_filter,
        inputs=[input_image, filter_type],
        outputs=output_image
    )

    brightness_btn.click(
        fn=adjust_brightness,
        inputs=[input_image, brightness],
        outputs=output_image
    )

demo.launch()
```

### 8.5 Data Analysis Dashboard

```python
import gradio as gr
import pandas as pd
import plotly.express as px

def analyze_data(file):
    if file is None:
        return None, None, "No file uploaded"

    # Read data
    df = pd.read_csv(file.name)

    # Generate summary
    summary = df.describe().to_html()

    # Create visualization
    fig = px.scatter_matrix(df)

    # Return table, plot, and summary
    return df, fig, summary

with gr.Blocks() as demo:
    gr.Markdown("# Data Analysis Dashboard")

    with gr.Row():
        file_input = gr.File(label="Upload CSV", file_types=[".csv"])
        analyze_btn = gr.Button("Analyze")

    with gr.Tab("Data Table"):
        data_table = gr.Dataframe(label="Raw Data")

    with gr.Tab("Visualization"):
        plot_output = gr.Plot(label="Scatter Matrix")

    with gr.Tab("Summary Statistics"):
        summary_html = gr.HTML(label="Statistical Summary")

    analyze_btn.click(
        fn=analyze_data,
        inputs=file_input,
        outputs=[data_table, plot_output, summary_html]
    )

demo.launch()
```

### 8.6 Streaming Text Generation

```python
import gradio as gr
import time

def generate_stream(prompt, max_length):
    # Simulate streaming text generation
    words = ["This", "is", "a", "streaming", "text", "generation", "example",
             "that", "shows", "progressive", "updates", "in", "Gradio"]

    output = ""
    for word in words[:max_length]:
        output += word + " "
        time.sleep(0.3)  # Simulate generation delay
        yield output

with gr.Blocks() as demo:
    gr.Markdown("# Streaming Text Generation")

    prompt = gr.Textbox(label="Prompt", placeholder="Enter your prompt...")
    max_length = gr.Slider(1, 13, value=10, step=1, label="Max Words")
    generate_btn = gr.Button("Generate")
    output = gr.Textbox(label="Generated Text", lines=5)

    generate_btn.click(
        fn=generate_stream,
        inputs=[prompt, max_length],
        outputs=output
    )

demo.launch()
```

### 8.7 Multi-Modal Interface

```python
import gradio as gr

def process_multimodal(text, image, audio):
    results = []

    if text:
        results.append(f"Text received: {len(text)} characters")

    if image is not None:
        results.append(f"Image received: {image.size}")

    if audio is not None:
        results.append(f"Audio received")

    return "\n".join(results)

with gr.Blocks() as demo:
    gr.Markdown("# Multi-Modal Input Interface")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(label="Text Input", lines=3)
            image_input = gr.Image(label="Image Input", type="pil")
            audio_input = gr.Audio(label="Audio Input")
            submit_btn = gr.Button("Process All")

        with gr.Column():
            output = gr.Textbox(label="Analysis Results", lines=10)

    submit_btn.click(
        fn=process_multimodal,
        inputs=[text_input, image_input, audio_input],
        outputs=output
    )

demo.launch()
```

### 8.8 Progress Bar Example

```python
import gradio as gr
import time

def long_running_task(iterations, progress=gr.Progress()):
    results = []

    progress(0, desc="Starting...")

    for i in range(iterations):
        # Simulate work
        time.sleep(0.5)
        results.append(f"Completed step {i+1}")

        # Update progress
        progress((i+1)/iterations, desc=f"Processing {i+1}/{iterations}")

    return "\n".join(results)

demo = gr.Interface(
    fn=long_running_task,
    inputs=gr.Slider(1, 20, value=10, step=1, label="Number of Iterations"),
    outputs=gr.Textbox(label="Results", lines=10),
    title="Progress Bar Demo"
)

demo.queue().launch()  # Queue required for progress bars
```

### 8.9 Custom Component Example (Conceptual)

```python
# This is a conceptual example of custom component structure
# Actual implementation requires additional files

import gradio as gr
from gradio.components import Component

class CustomSlider(Component):
    """Custom slider with special features"""

    def __init__(
        self,
        minimum=0,
        maximum=100,
        step=1,
        value=None,
        label=None,
        **kwargs
    ):
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

        super().__init__(value=value, label=label, **kwargs)

    def preprocess(self, x):
        # Convert from frontend to Python
        return float(x)

    def postprocess(self, y):
        # Convert from Python to frontend
        return float(y)

    def example_inputs(self):
        return [self.minimum, (self.minimum + self.maximum) / 2, self.maximum]

# Usage
demo = gr.Interface(
    fn=lambda x: x * 2,
    inputs=CustomSlider(minimum=0, maximum=100, label="Custom Slider"),
    outputs=gr.Number()
)
```

---

## Conclusion

Gradio is a powerful, flexible framework for building machine learning demos and web applications with minimal code. Its strengths include:

- **Ease of Use**: Simple Interface API for quick demos
- **Flexibility**: Advanced Blocks API for complex applications
- **Rich Components**: 30+ built-in components for various data types
- **Event System**: Comprehensive event handling and data flow control
- **Theming**: Customizable appearance with built-in and custom themes
- **Advanced Features**: Streaming, progress tracking, authentication, queuing
- **Integration**: Seamless integration with ML frameworks and cloud services
- **Deployment**: Multiple deployment options including HuggingFace Spaces

Whether building a simple model demo or a complex multi-modal application, Gradio provides the tools and patterns needed to create professional, user-friendly interfaces entirely in Python.

---

## Additional Resources

- **Official Documentation**: https://www.gradio.app/docs
- **Guides**: https://www.gradio.app/guides
- **Custom Components Gallery**: https://www.gradio.app/custom-components/gallery
- **HuggingFace Spaces**: https://huggingface.co/spaces
- **GitHub Repository**: https://github.com/gradio-app/gradio
- **Community Forum**: https://discuss.huggingface.co/c/gradio
- **Theme Gallery**: https://huggingface.co/spaces/gradio/theme-gallery

---

*This research report was compiled from official Gradio documentation, community resources, and web searches conducted on 2025-11-18.*


> Source: `docs/data_engineering/gradio/gradio-openapi-research.md`

# Gradio OpenAPI Specification Research

**Research Date:** 2025-11-22
**Subject:** OpenAPI/Swagger Specification Support in Gradio
**Status:** Complete

---

## Executive Summary

**Does Gradio have an official OpenAPI specification?**
**YES** - Gradio automatically generates an OpenAPI v3 specification for every Gradio application, accessible at the endpoint `<your-gradio-app-url>/gradio_api/openapi.json`.

**Key Finding:** Gradio both **produces** OpenAPI specifications (for its own apps) and **consumes** OpenAPI specifications (via `gr.load_openapi` to generate UIs from external APIs).

---

## 1. Official OpenAPI Specification Access

### Endpoint Location
Every Gradio application automatically exposes its OpenAPI specification at:
```
https://<your-gradio-app-url>/gradio_api/openapi.json
```

### Specification Details
- **Format:** OpenAPI v3 (JSON only)
- **Generation:** Automatically generated from Gradio app function signatures
- **Coverage:** Includes all API endpoints, parameters, types, and example inputs
- **Technology Stack:** Built on FastAPI + Pydantic + Swagger

### Implementation Timeline
- **Issue #672** (Expose inputs/outputs in openapi.json): Filed requesting machine-readable API format
- **PR #11103**: Merged - Implemented OpenAPI specification exposure
- **Status:** Feature is live and fully implemented

---

## 2. API Documentation Features

### Built-in API Documentation Page
Every Gradio app includes an interactive API documentation page accessible via:
- **Location:** "Use via API" link in the app footer
- **Access:** `<your-gradio-app-url>?view=api`

### Documentation Capabilities
The API page provides:
1. **Endpoint Discovery:** Automatically generated API endpoint names based on function names
2. **Code Snippets:** Complete examples for both Python and JavaScript clients
3. **Parameter Details:** Types, example inputs, and usage instructions
4. **API Recorder:** Tool for generating client code by recording UI interactions
5. **MCP Server Instructions:** Integration guidelines for Model Control Protocol

### Customization Options
- **Custom Endpoint Names:** Use `api_name` parameter in event listeners
- **Hide from Docs:** Use `show_api=False` to hide endpoints while keeping them functional
- **Disable Endpoints:** Set `api_name=False` to completely disable programmatic access

---

## 3. Additional API Endpoints

### `/info` Endpoint
**Purpose:** Returns metadata about available API endpoints

**Location:**
- `<your-gradio-app-url>/info`
- `<your-gradio-app-url>/info/`

**Query Parameters:**
- `all_endpoints` (optional): When set to `True`, returns information about all endpoints including unnamed ones

**Response Includes:**
- Named and unnamed endpoints
- Parameters each endpoint accepts
- Return types for each endpoint
- Configuration metadata for the Gradio application

**Usage:** Primarily used internally by Gradio clients (Python and JavaScript) for endpoint discovery

---

## 4. Consuming External OpenAPI Specifications

### `gr.load_openapi()` Function
Gradio provides a function to automatically generate Gradio UIs from external OpenAPI v3 specifications.

### Syntax
```python
import gradio as gr

demo = gr.load_openapi(
    openapi_spec="<URL, file path, or Python dict>",
    base_url="<API base URL>",
    paths=["<optional regex patterns>"],  # e.g., ["/pet.*"]
    methods=["get", "post"]  # optional HTTP methods filter
)

demo.launch()
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openapi_spec` | str/dict | Yes | URL, file path, or Python dictionary containing OpenAPI v3 spec (JSON only) |
| `base_url` | str | Yes | Base URL for API endpoints (e.g., `https://api.example.com/v1`) |
| `paths` | list[str] | No | Endpoint path patterns (supports regex). If omitted, all paths included |
| `methods` | list[str] | No | HTTP methods to include (e.g., `["get", "post"]`). If omitted, all methods included |

### Example: PetStore API
```python
import gradio as gr

demo = gr.load_openapi(
    openapi_spec="https://petstore3.swagger.io/api/v3/openapi.json",
    base_url="https://petstore3.swagger.io/api/v3",
    paths=["/pet.*"],
    methods=["get", "post"],
)

demo.launch()
```

### Generated Features
- **Sidebar Navigation:** Displays available endpoints
- **Interactive Forms:** Creates UI components for each operation parameter
- **Real-time Testing:** Enables API calls and response viewing directly from browser
- **MCP Integration:** Can be deployed as MCP server for programmatic orchestration

---

## 5. Historical Context and Evolution

### Swagger UI Removal (Issue #4054)
**What Changed:**
- Gradio removed the `/docs` endpoint that provided traditional Swagger UI documentation
- Replaced with sidebar documentation at `?view=api` focused on `gradio_client` usage

**User Concerns:**
1. **Language Lock-in:** New docs only show Python examples via `gradio_client`
2. **Cross-platform Limitation:** Users building browser/JavaScript applications cannot use Python client
3. **Custom Routes Undocumented:** Developers using `add_api_route()` lose documentation for custom endpoints
4. **HTTP REST Documentation:** Old Swagger docs were language-agnostic and worked with any HTTP client (curl, JavaScript, etc.)

**User Requests:**
- Reintroduce Swagger docs at `/docs` endpoint
- Make it optional via flag in `launch()` method
- Enable integration with any HTTP client, not just `gradio_client`

**Gradio's Position:**
- Prefers steering users toward `gradio_client` for reliability
- OpenAPI spec still available at `/gradio_api/openapi.json` for those who need it

---

## 6. API Architecture and Technology

### Core Technologies
- **FastAPI:** Web framework powering Gradio's backend
- **Pydantic:** Data validation and schema generation
- **Swagger/OpenAPI:** API specification standard

### Dynamic Schema Generation
Gradio defines dynamic Pydantic models when creating applications, enabling:
- Automatic input validation and type checking
- Schema inference from Python function signatures
- OpenAPI documentation generation
- Acceptable values definition for UI components (dropdowns, sliders)

### Client Libraries
**Python Client:**
- `gradio_client` package
- `Client.view_api()` method for endpoint discovery

**JavaScript Client:**
- `@gradio/client` npm package
- Built-in API discovery capabilities

---

## 7. Current Limitations and Considerations

### OpenAPI Specification Completeness
- **Status:** Feature complete as of PR #11103
- **Format:** JSON only (no YAML support explicitly mentioned)
- **Version:** OpenAPI v3 specification

### Documentation Gaps
1. **No Traditional Swagger UI:** Gradio removed `/docs` endpoint in favor of custom API page
2. **Client Library Focus:** Documentation emphasizes official clients over direct HTTP access
3. **Custom Routes:** Limited documentation for endpoints added via `add_api_route()`

### Recommended Approach
For programmatic integration, Gradio recommends:
1. **Preferred:** Use official Python or JavaScript clients
2. **Alternative:** Access `/gradio_api/openapi.json` for direct HTTP integration
3. **Discovery:** Use `/info` endpoint for runtime endpoint discovery

---

## 8. Integration Examples

### Accessing OpenAPI Spec
```bash
# Fetch OpenAPI specification
curl https://your-gradio-app.com/gradio_api/openapi.json

# Get endpoint information
curl https://your-gradio-app.com/info?all_endpoints=true
```

### Using with API Testing Tools
The OpenAPI specification at `/gradio_api/openapi.json` can be imported into:
- **Postman:** Import > Link > Paste OpenAPI JSON URL
- **Insomnia:** Import > URL > Enter spec endpoint
- **SwaggerHub:** Create API > Import > URL
- **OpenAPI Generator:** Generate client SDKs in multiple languages

### Generating Client Code
```bash
# Example: Generate Python client from Gradio OpenAPI spec
openapi-generator-cli generate \
  -i https://your-gradio-app.com/gradio_api/openapi.json \
  -g python \
  -o ./gradio-python-client
```

---

## 9. Use Cases and Applications

### When to Use OpenAPI Spec
1. **Cross-language Integration:** Integrate Gradio apps with non-Python services
2. **API Documentation:** Generate comprehensive API docs for stakeholders
3. **Client Generation:** Auto-generate client libraries in multiple languages
4. **Testing:** Import into API testing tools for automated testing
5. **Validation:** Verify API coherency and contract compliance

### When to Use `gr.load_openapi()`
1. **API Exploration:** Create quick UI for testing external APIs
2. **Documentation:** Provide interactive documentation for your API
3. **Rapid Prototyping:** Build API clients without writing frontend code
4. **MCP Integration:** Deploy as Model Control Protocol server

---

## 10. Key Takeaways

### For Developers
✅ **Official Spec Exists:** Every Gradio app has an OpenAPI v3 specification at `/gradio_api/openapi.json`
✅ **Automatic Generation:** No configuration needed - spec is auto-generated from function signatures
✅ **Full Coverage:** Includes all endpoints, parameters, types, and examples
✅ **Bidirectional:** Gradio both produces and consumes OpenAPI specifications
✅ **Standards Compliant:** Uses OpenAPI v3, compatible with standard tooling

### For Integration
✅ **HTTP REST API:** Available for any language/framework via OpenAPI spec
✅ **Client Libraries:** Official Python and JavaScript clients recommended
✅ **Tooling Support:** Works with Postman, Insomnia, OpenAPI Generator, etc.
✅ **Discovery Endpoint:** `/info` endpoint for runtime endpoint discovery
⚠️ **No Swagger UI:** Traditional `/docs` endpoint removed in favor of custom API page

### For Architecture
✅ **FastAPI-based:** Built on modern Python async framework
✅ **Pydantic Validation:** Type-safe with automatic schema generation
✅ **Dynamic Models:** Schemas generated from Python function signatures
✅ **MCP Compatible:** Can be deployed as Model Control Protocol servers

---

## 11. Official Resources

### Documentation
- **From OpenAPI Spec Guide:** https://www.gradio.app/guides/from-openapi-spec
- **View API Page Guide:** https://www.gradio.app/guides/view-api-page
- **Getting Started (Python):** https://www.gradio.app/guides/getting-started-with-the-python-client
- **Getting Started (JS):** https://www.gradio.app/guides/getting-started-with-the-js-client
- **Querying with cURL:** https://www.gradio.app/guides/querying-gradio-apps-with-curl
- **Main Documentation:** https://www.gradio.app/docs

### GitHub
- **Main Repository:** https://github.com/gradio-app/gradio
- **Issue #672 (OpenAPI exposure):** https://github.com/gradio-app/gradio/issues/672
- **Issue #4054 (Swagger UI removal):** https://github.com/gradio-app/gradio/issues/4054
- **Issue #7287 (OpenAPI docs):** https://github.com/gradio-app/gradio/issues/7287

### Client Libraries
- **Python Client:** `pip install gradio_client`
- **JavaScript Client:** `npm install @gradio/client`

---

## 12. Conclusion

**Gradio provides comprehensive OpenAPI v3 support** through automatic specification generation for all Gradio applications. The specification is accessible at `/gradio_api/openapi.json` and includes complete endpoint definitions, parameters, types, and examples.

**Key strengths:**
- Zero-configuration automatic generation
- Standards-compliant OpenAPI v3
- Compatible with standard tooling ecosystem
- Bidirectional support (produce and consume specs)
- Built on modern FastAPI + Pydantic stack

**Considerations:**
- Traditional Swagger UI removed (but spec still available)
- Documentation emphasizes official clients over direct HTTP
- Custom routes may need additional documentation

**Bottom line:** Generating custom OpenAPI specifications for Gradio is **not necessary** - the framework already provides complete, automatic OpenAPI v3 specifications for all applications.

---

## Sources

1. [From OpenAPI Spec - Gradio Guide](https://www.gradio.app/guides/from-openapi-spec)
2. [View API Page - Gradio Guide](https://www.gradio.app/guides/view-api-page)
3. [Gradio Documentation](https://www.gradio.app/docs)
4. [Getting Started With The Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client)
5. [Getting Started With The JS Client](https://www.gradio.app/guides/getting-started-with-the-js-client)
6. [Querying Gradio Apps With Curl](https://www.gradio.app/guides/querying-gradio-apps-with-curl)
7. [Issue #672: Expose inputs/outputs in openapi.json](https://github.com/gradio-app/gradio/issues/672)
8. [Issue #4054: Reintroduce Swagger API docs](https://github.com/gradio-app/gradio/issues/4054)
9. [Issue #7287: OpenAPI docs not working](https://github.com/gradio-app/gradio/issues/7287)
10. [Gradio GitHub Repository](https://github.com/gradio-app/gradio)
11. [Gradio API - API Tracker](https://apitracker.io/a/gradio-app)
12. [Building MCP Server With Gradio](https://www.gradio.app/guides/building-mcp-server-with-gradio)
13. [Gradio Python Client Docs](https://www.gradio.app/docs/python-client/client)
14. [Gradio JavaScript Client Docs](https://www.gradio.app/docs/js-client)


## Data Processing — Ibis


> Source: `docs/data_engineering/ibis/ibis.md`

---
description: Expert assistant for Ibis dataframe library - helps with queries, backends, data transformations, and pandas migration.
---

# Ibis Expert Assistant

You are an expert Ibis framework assistant. Help users with portable dataframe operations, backend selection, query building, and migrating from pandas to Ibis.

## Core Knowledge

Reference the comprehensive guide at `@/ibis-llms.txt` for patterns, API reference, and examples.

## Primary Responsibilities

### 1. Query Building
- Help build expression chains using deferred execution
- Recommend appropriate operations (filter, mutate, aggregate, join)
- Guide use of the underscore `_` deferred expression API
- Implement window functions and conditional logic
- Optimize query patterns for performance

### 2. Backend Selection & Connection
- Recommend appropriate backend for use case
- Provide connection string formats
- Help configure backend-specific options
- Guide development-to-production migration (DuckDB -> BigQuery/Snowflake)

### 3. Data Transformation
- Design aggregation pipelines
- Implement joins and set operations
- Use selectors for bulk column operations
- Create reusable transformation functions
- Handle type casting and schema management

### 4. pandas Migration
- Convert pandas code to Ibis expressions
- Explain lazy vs eager execution differences
- Handle index-related patterns (Ibis has no index)
- Migrate DataFrame operations to Table operations

## Guidelines

1. **Always use deferred execution** - build expressions, execute only when needed
2. **Prefer the `_` syntax** for concise, readable chains
3. **Use selectors** for bulk column operations (`s.numeric()`, `s.across()`)
4. **Push computation down** - filter/aggregate before `.to_pandas()`
5. **Check backend support** before using operations
6. **Use DuckDB** for development, cloud warehouses for production

## Common Patterns to Recommend

### Basic Query Chain
```python
import ibis
from ibis import _

con = ibis.duckdb.connect()
t = con.table("sales")

result = (
    t
    .filter(_.date >= "2024-01-01")
    .mutate(revenue=_.quantity * _.price)
    .group_by("region")
    .aggregate(total=_.revenue.sum())
    .order_by(ibis.desc("total"))
    .to_pandas()
)
```

### Conditional Aggregation
```python
result = t.group_by("country").aggregate(
    total=_.sales.sum(),
    us_sales=_.sales.sum(where=_.region == "US"),
    large_deals=_.count(where=_.value > 10000)
)
```

### Window Functions
```python
result = (
    t
    .group_by("category")
    .order_by("date")
    .mutate(
        running_total=_.amount.sum(),
        rank=ibis.row_number()
    )
)
```

### Using Selectors
```python
import ibis.selectors as s

# Normalize all numeric columns
result = t.mutate(
    s.across(s.numeric(), (_ - _.mean()) / _.std())
)

# Select columns by pattern
result = t.select(s.startswith("bill"))
```

### Reusable Transformations
```python
def add_date_parts(table):
    return table.mutate(
        year=_.date.year(),
        month=_.date.month(),
        quarter=_.date.quarter()
    )

result = t.pipe(add_date_parts)
```

## When Asked About...

- **Which backend?**: DuckDB for dev/small data, BigQuery/Snowflake for large/production
- **Performance**: Push filters early, use conditional aggregations, `.cache()` for reuse
- **Joins**: Filter before joining, select specific columns after, handle name collisions
- **pandas migration**: Explain lazy execution, immutability, no index concept
- **SQL**: Show `ibis.to_sql()` for debugging, `con.sql()` for raw SQL
- **UDFs**: Recommend built-in UDFs when possible, pandas UDFs for vectorized ops

## Anti-Patterns to Warn Against

1. **Installing wrong package** - `ibis-framework` not `ibis`
2. **Expecting eager execution** - operations return new expressions, not results
3. **In-place modification** - tables are immutable
4. **Loading all data** - filter/aggregate in Ibis before `.to_pandas()`
5. **Position-based indexing** - use column names, not positions
6. **Assuming row order** - always use `order_by()` explicitly

## Response Style

1. Show working code examples with imports
2. Use the `_` deferred expression syntax
3. Explain lazy evaluation when relevant
4. Suggest related operations the user might need
5. Recommend DuckDB for quick testing

## Connection Quick Reference

```python
# DuckDB (default)
con = ibis.duckdb.connect()  # in-memory
con = ibis.duckdb.connect("file.duckdb")

# PostgreSQL
con = ibis.connect("postgresql://user:pass@host:5432/db")

# BigQuery
con = ibis.connect("bigquery://project-id/dataset")

# Snowflake
con = ibis.snowflake.connect(
    user="u", password="p", account="a",
    database="DB", schema="SCHEMA"
)

# In-memory table
t = ibis.memtable({"col": [1, 2, 3]})
```


> Source: `docs/data_engineering/ibis/Ibis, LanceDB, and Data Stack Integration.md`

# **The Converged Lakehouse: Architecting a Multimodal Data Environment with Lance Namespace and the Composable Stack**

## **1\. Executive Introduction: The Era of the Composable AI Stack**

The contemporary data infrastructure landscape is witnessing a fundamental dissolution of the historical barriers between Online Transactional Processing (OLTP), Online Analytical Processing (OLAP), and the burgeoning domain of Artificial Intelligence (AI) data management. We are moving beyond the monolithic paradigms of the single-vendor data warehouse and the unmanaged data lake into a third era: the **Composable AI Stack**. The environment proposed in this research—integrating **Ibis**, **DuckDB**, **MotherDuck**, **PlanetScale**, **Cloudflare R2**, **Iceberg**, **DuckLake**, and **Lance Namespace**—represents the vanguard of this architectural shift. It is a system designed not merely for "data processing" in the abstract, but specifically for the high-fidelity management of multimodal assets, such as PDF documents and their semantic vector embeddings, alongside rigorous transactional state management.  
The core challenge addressed by this architecture is the "impedance mismatch" between structured business data (users, subscriptions, access logs) and unstructured AI data (vectors, binary blobs, neural indices). Historically, these lived in separate silos: Postgres for the business, S3 for the files, and a specialized vector database for the embeddings. This fragmentation introduces latency, data drift, and governance nightmares. By unifying these layers through **Cloudflare R2** (as the universal storage substrate) and bridging them with **Lance Namespace** (as the metadata unifier), this architecture proposes a "Zero-Copy," "Zero-Egress" future where compute engines are brought to the data, rather than data being shipped to the compute.  
This report serves as an exhaustive architectural blueprint and implementation guide for this specific stack. It places a heavy emphasis on the role of **Lance Namespace**, dissecting its function as the integration layer that allows "AI-native" data (Lance format) to coexist and interoperate with "Analytics-native" data (Iceberg/DuckLake) and "Transaction-native" data (Postgres). We will explore the theoretical underpinnings of storage-compute separation, the mechanics of hybrid execution, and the practical implementation details of serving PDF files at the edge using this converged infrastructure.

## ---

**2\. The Architectural Foundation: Unbundling the Database**

To understand how best to utilize Lance Namespace within this stack, one must first rigorously define the role of each component. This ecosystem relies on the principle of "best-of-breed" specialization, where distinct tools solve specific classes of data engineering problems but are loosely coupled through open standards (Arrow, Parquet, Lance, SQL).

### **2.1. The Universal Interface: Ibis as the Control Plane**

In this heterogeneous environment, the developer experience is the primary risk factor. Managing connections to PlanetScale (MySQL/Postgres protocol), MotherDuck (DuckDB protocol), and LanceDB (Native/Arrow protocol) requires a unifying linguistic layer. **Ibis** fulfills this role as the portable Python DataFrame API.  
Unlike eager-execution libraries like pandas, which pull data into memory immediately, Ibis operates on a **lazy evaluation** model. It constructs an intermediate semantic representation of the query—a logical plan—and then compiles this plan into the native dialect of the target backend.1 This capability is indispensable in a stack where data resides in different physical locations (PlanetScale in AWS/GCP, MotherDuck in the cloud, Lance in R2).  
Ibis acts as the **federation coordinator**. While Ibis typically pushes a query to a single backend, the integration with **DuckDB** allows Ibis to act as a virtualization layer. Through DuckDB's ability to attach to external databases (Postgres via postgres\_scanner, S3 via httpfs), Ibis can express complex join logic across these systems in a single, fluent Python syntax.1 For the specific requirement of handling Lance datasets, Ibis serves as the orchestration tool that defines *what* data is needed, relying on DuckDB and Lance Namespace to handle the *how* of retrieval from R2.

### **2.2. The Compute Engine: DuckDB and MotherDuck**

**DuckDB** is the "engine room" of this architecture. As an in-process SQL OLAP database, it runs directly within the application container or the data processing worker. Its vectorized execution engine is optimized for analytical queries on columnar data, making it the ideal processor for the Parquet and Lance files stored in R2.2  
**MotherDuck** extends DuckDB into a serverless cloud data warehouse. It introduces the concept of **Hybrid Execution**, where a query plan can be split: purely local operations run on the developer's machine or worker node, while heavy aggregations or joins on large datasets are shipped to the MotherDuck cloud.4

* **Role in this Stack:** MotherDuck is the primary engine for heavy analytical lifting. It is responsible for joining the high-volume clickstream/access logs (stored in DuckLake format) with the dimensional user data (from PlanetScale).  
* **DuckLake:** This is MotherDuck’s optimized table format and catalog. Unlike generic data lakes, DuckLake brings ACID compliance and "time travel" to data stored in object storage.5 It is designed to work seamlessly with the DuckDB engine, offering features like **Data Inlining**, where small inserts are stored directly in the metadata to avoid the "small file problem" common in S3-based lakes.6

### **2.3. The Operational Store: PlanetScale PostgreSQL**

PlanetScale has historically been synonymous with Vitess and MySQL. However, the introduction of **PlanetScale for Postgres** fundamentally changes the integration dynamic of this stack.7

* **Role:** It serves as the immutable "System of Record" for transactional entities: User IDs, Billing, Authentication, and the mutable metadata of the PDF uploads (e.g., "is\_public", "owner\_id").  
* **The pg\_duckdb Bridge:** This is a critical synergy. PlanetScale Postgres supports the pg\_duckdb extension, which embeds the DuckDB engine *inside* the Postgres process.4 This allows the transactional database to query external data lakes (Parquet/Lance on R2) directly. It effectively blurs the line between OLTP and OLAP, allowing a developer to write a SQL query in PlanetScale that joins a local users table with a remote vector\_search\_logs table stored in MotherDuck.

### **2.4. The Storage Layer: Cloudflare R2**

**Cloudflare R2** is the physical foundation of the "Lake." Its S3-compatible API ensures compatibility with every tool in this stack (DuckDB, LanceDB, Iceberg).

* **Economic Strategic Advantage:** The "serving of PDF files" implies a high-read-volume workload. Traditional cloud object stores (AWS S3, Google GCS) charge significant egress fees for data moving out of their network. R2’s **zero-egress** model is the economic enabler of this architecture.9 It allows the PDFs to be served directly to users or retrieved by compute nodes for vectorization without incurring bandwidth penalties.  
* **Performance:** R2’s global distribution and tiering ensure low latency for retrieving large binary blobs (PDFs), effectively acting as a storage-backed CDN.

### **2.5. The Metadata Layer: Iceberg REST and Lance Namespace**

This layer provides the "governance and discovery" capabilities. Without a shared catalog, files in R2 are just "dark data," invisible to the query engines.

* **Iceberg REST Catalog:** This is the industry standard for tracking table metadata (schemas, snapshots, partitions) in a vendor-neutral way.10 It decouples the table state from the file system.  
* **Lance Namespace:** This is the specialized integration layer for the user’s vector data. It allows Lance-formatted tables (which are optimized for AI) to be registered and managed within the standard Iceberg REST catalog, making them discoverable alongside standard analytical tables.11

## ---

**3\. Deep Dive: Lance Namespace Integration Strategy**

The user's core inquiry revolves around "how best to use Lance Namespace integrating with the rest of this stack." This section serves as the definitive guide to that integration, moving from conceptual architecture to concrete implementation patterns.

### **3.1. The Problem Space: The "Split-Brain" Lakehouse**

In a standard data architecture, one often encounters a bifurcation:

1. **The Analytics Lake:** Tables stored in Parquet/Iceberg format, managed by a Hive Metastore or Iceberg Catalog, and queried by Spark, Trino, or DuckDB.  
2. **The AI Silo:** Vector embeddings stored in a specialized Vector Database (Pinecone, Milvus) or in raw files managed by a proprietary application logic.

This separation creates a "Split-Brain" problem. The data engineering team (using Iceberg) cannot see the vector data. The AI team (using vectors) cannot easily join their results with business dimensions in the analytics lake. **Lance Namespace** is the architectural solution to this schism. It is a specification and set of adapters that allow Lance datasets to "live inside" standard metadata catalogs.

### **3.2. Architecture of Lance Namespace with Iceberg REST**

When configuring Lance Namespace to use an **Iceberg REST Catalog**, the system employs a "Companion Table" mechanism. This is a sophisticated masquerade that allows the Lance data to be managed by Iceberg without forcing the data into the less-optimal Parquet format.

#### **3.2.1. The Physical vs. Logical Layout**

* **Physical Layer (R2):** The Lance data files (.lance), indices, and fragments are written to Cloudflare R2. For example: r2://my-data-lake/vectors/contracts/.  
* **Logical Layer (Iceberg REST):** The Lance Namespace implementation registers a table in the Iceberg catalog. However, this is not a standard Iceberg table.  
  * **Dummy Schema:** The registered Iceberg table often contains a placeholder schema (e.g., a single column dummy\_lance\_placeholder string). This satisfies the Iceberg requirement that a table must have a schema.  
  * **Table Properties as Pointers:** The integration relies heavily on **Iceberg Table Properties**. It sets specific keys that identify the table's true nature:  
    * table\_type: Set to lance.10  
    * lance\_location: Points to the R2 URI of the Lance dataset.  
    * lance\_schema: May cache the JSON representation of the actual Lance schema (vectors, blobs, metadata).

#### **3.2.2. The Resolution Workflow**

When a client application interacts with this setup:

1. **Discovery:** The client (e.g., Ibis or a Python script) asks the Iceberg Catalog for the table contracts.  
2. **Interception:** The Lance Namespace client (wrapping the connection) inspects the returned metadata. It sees table\_type=lance.  
3. **Redirection:** Instead of trying to read the table as an Iceberg/Parquet table, the client "mounts" the data found at lance\_location using the native Lance reader.

This architecture ensures that **Iceberg is the Single Source of Truth** for *existence, access control, and ownership*, while **Lance is the Storage Format** for *performance and vector capabilities*.

### **3.3. Strategic Implementation for "Serving PDFs and Embeddings"**

The user's specific requirement is to store and serve PDF files and their embeddings. The optimal strategy utilizes Lance's multimodal capabilities, specifically its efficiency with **Binary Large Objects (BLOBs)**.

#### **3.3.1. The "Fat Table" Schema Strategy**

Traditional architectures utilize a "Pointer Strategy": storing the PDF in S3, getting a URL, and storing the URL \+ Embedding in the database.

* **Drawback:** This creates an "N+1" query problem during retrieval. To serve the top 5 relevant documents, the application must (1) Query the vector DB (1 request), receive 5 URLs, and then (2) Make 5 separate HTTP requests to S3 to fetch the content.

**The Lance Recommendation:** Use a "Fat Table" schema where the PDF binary blob is stored *directly* in the Lance column.  
**Proposed Ibis/Lance Schema:**

Python

import pyarrow as pa

schema \= pa.schema()

Why this works on R2 with Lance:  
Lance is a fragment-based columnar format. Unlike Parquet, which must decompress and scan entire row groups, Lance supports O(1) random access to specific row IDs.

1. **Retrieval Efficiency:** When a vector search identifies the top K matches, Lance can perform a **Projection** to retrieve *only* the pdf\_blob column for those K rows.  
2. **Ranged Reads:** The Lance reader issues HTTP Range requests to R2. It does not download the whole file; it downloads only the bytes corresponding to the specific PDFs required.  
3. **Consolidated I/O:** This effectively reduces the "N+1" problem to a single (or very few) parallelized storage requests, drastically reducing latency for the user.

#### **3.3.2. Configuring the Lance Namespace with Iceberg REST and R2**

This section details the specific configuration required to wire these components together. The user must configure the Lance client to authenticate with both the Iceberg REST service (for metadata) and Cloudflare R2 (for data).  
**Python Configuration Pattern:**

Python

import lance  
from lance.namespace import connect

\# 1\. R2 Storage Configuration (S3-Compatible)  
\# These options tell Lance how to talk to Cloudflare R2  
storage\_options \= {  
    "s3\_endpoint\_override": "https://\<ACCOUNT\_ID\>.r2.cloudflarestorage.com",  
    "region": "auto",  
    "aws\_access\_key\_id": "\<R2\_ACCESS\_KEY\_ID\>",  
    "aws\_secret\_access\_key": "\<R2\_SECRET\_ACCESS\_KEY\>",  
    "allow\_http": "true", \# Required if bridging via certain proxies, otherwise false for R2  
    "timeout": "60s"  
}

\# 2\. Iceberg REST Catalog Configuration  
\# This tells Lance where to find the metadata  
catalog\_uri \= "https://\<ICEBERG\_REST\_URL\>/v1"  
warehouse\_path \= "r2://\<BUCKET\_NAME\>/lance-warehouse"

\# 3\. Connect to the Namespace  
\# This object 'ns' becomes the handle to create/manage tables  
ns \= connect(  
    "iceberg",   
    uri=catalog\_uri,   
    warehouse=warehouse\_path,   
    storage\_options=storage\_options  
)

\# 4\. Creating the Table (DDL)  
\# This registers the table in Iceberg AND creates the physical artifacts in R2  
tbl \= ns.create\_table(  
    "pdf\_documents",  
    schema=schema,  
    mode="create"   
)

### **3.4. Bridging Lance Namespace and Ibis/DuckDB**

The final piece of the integration puzzle is making these Lance tables accessible to **Ibis**. Ibis does not currently have a native "Lance Namespace" backend. Instead, we utilize the **Ibis DuckDB Backend**.  
The Integration Pattern: "Resolve and Register"  
Since DuckDB has a native lance extension (capable of reading .lance files) but may not yet automatically traverse the Iceberg/Lance-Namespace redirection link transparently, the application layer must bridge this gap.

1. **Resolve:** The application uses the lance.namespace client (as shown above) to look up the table pdf\_documents. The client returns the physical R2 URI (r2://.../data.lance).  
2. **Register:** The application registers this URI as a **View** or **Scanner** in the DuckDB connection used by Ibis.

Python

\#... assuming 'ns' is connected as above...

\# 1\. Resolve logical name to physical dataset  
lance\_table \= ns.open\_table("pdf\_documents")  
physical\_uri \= lance\_table.uri 

\# 2\. Setup Ibis with DuckDB  
import ibis  
con \= ibis.duckdb.connect()

\# 3\. Install Lance Extension in DuckDB  
con.raw\_sql("INSTALL lance; LOAD lance;")

\# 4\. Register the dataset as a View  
\# Note: We must pass the S3/R2 credentials to DuckDB as well  
con.raw\_sql(f"""  
    CREATE SECRET r2\_secret (  
        TYPE R2,  
        KEY\_ID '{r2\_key\_id}',  
        SECRET '{r2\_secret}',  
        ACCOUNT\_ID '{r2\_account\_id}'  
    );  
""")

\# Register the view using the lance\_scan function  
con.raw\_sql(f"CREATE VIEW pdf\_docs\_view AS SELECT \* FROM lance\_scan('{physical\_uri}');")

\# 5\. Ibis Object Creation  
\# Now Ibis treats it as a native table  
docs \= con.table("pdf\_docs\_view")

\# 6\. Usage: Ibis executes SQL, DuckDB scans Lance on R2  
result \= docs.filter(docs.file\_name.like("%.pdf")).execute()

This pattern provides the best of both worlds: the governance of the Namespace/Catalog and the fluid query API of Ibis.

## ---

**4\. Workflows: The Life of a PDF**

To further elucidate the stack's operation, we will trace the lifecycle of a PDF file through ingestion, storage, and serving.

### **4.1. Ingestion Workflow (Write Path)**

The write path is designed for **Concurrency** and **Atomicity**, leveraging the Iceberg REST catalog to manage state.

1. **Upload & Trigger:** A user uploads a file to the application.  
2. **Vectorization Worker:** A background worker (using Python/Ray) picks up the file. It extracts text and generates an embedding (e.g., using OpenAI or a local BERT model).  
3. **Constructing the Record:** The worker creates an Arrow RecordBatch containing:  
   * id: Generated UUID.  
   * pdf\_blob: The raw bytes of the file.  
   * vector: The computed embedding.  
   * metadata: JSON object with user\_id, timestamp, etc.  
4. **Lance Commit:** The worker calls ns.open\_table("documents").add(batch).  
   * **Phase 1 (Write):** The Lance writer writes new data fragments (files) to R2. These are invisible to readers.  
   * **Phase 2 (Commit):** The Lance client contacts the **Iceberg REST Catalog**. It attempts to swap the metadata pointer to include the new fragments.  
   * **Concurrency:** If multiple workers invoke this simultaneously, the Iceberg Catalog (backed by a database like Postgres) serializes the commits. One will succeed; the other will retry. This guarantees ACID compliance on object storage.12

### **4.2. Serving Workflow (Read Path)**

The read path optimizes for **Low Latency** using R2 and Lance’s random access capabilities.

1. **Request:** User asks "Show me contracts related to NDA."  
2. **Vector Search:** The application generates a query vector for "contracts related to NDA."  
3. **LanceDB Query:**  
   * The application connects to the Lance dataset.  
   * It executes a vector search: .search(query\_vector).limit(5).  
   * **Index Usage:** It utilizes the IVF-PQ index (stored in R2, cached locally on the compute node) to find the nearest neighbors.  
4. **Blob Retrieval:**  
   * The search returns 5 Row IDs.  
   * The query includes a request for the pdf\_blob column.  
   * **Ranged Read:** The Lance reader calculates the exact byte offsets of the blobs in the R2 files. It sends 5 parallel HTTP GET Range requests to R2.  
5. **Response:** The application receives the PDF bytes and streams them to the user.

## ---

**5\. Comparative Analysis: DuckLake vs. Iceberg REST**

The user's stack includes both **DuckLake** and **Iceberg REST**. A critical architectural decision is determining *when* to use which, as having two catalogs can lead to fragmentation.

| Feature | DuckLake | Iceberg REST (with Lance Namespace) | Recommendation for this Stack |
| :---- | :---- | :---- | :---- |
| **Primary Engine** | MotherDuck / DuckDB | Spark / Trino / LanceDB |  |
| **Metadata Storage** | SQL Database (MotherDuck managed) | JSON/Avro Files (standard spec) |  |
| **Write Latency** | **Low** (Data Inlining for small inserts) | **Higher** (File rotation required) | Use **DuckLake** for high-velocity logs (e.g., clickstream, access logs). |
| **Vector Support** | Limited (via Extensions) | **First-Class** (via Lance Namespace) | Use **Iceberg/Lance** for AI data (PDFs, Embeddings). |
| **Interoperability** | DuckDB Ecosystem primarily | Universal (Standard open format) | Use **Iceberg** for data shared with external teams/tools. |

Synthesis Strategy:  
The report recommends a Hybrid Catalog Strategy:

* **Operational Analytics:** Use **DuckLake** for tables that are primarily generated and queried by MotherDuck (e.g., aggregated usage metrics, session logs). DuckLake's "Data Inlining" feature 6 is superior for streaming small updates.  
* **AI Assets:** Use **Iceberg REST** hosting the **Lance Namespace** for the documents and embeddings tables. This adheres to the open standard for the AI assets, ensuring they are future-proof and accessible to other tools (like Spark for bulk training).  
* **Unified View:** Use Ibis \+ DuckDB to create a "Virtual Data Warehouse" that joins tables from both catalogs seamlessly.

## ---

**6\. Integrating PlanetScale and MotherDuck**

The relationship between PlanetScale (OLTP) and MotherDuck (OLAP) is the bridge between the application state and the data intelligence.

### **6.1. The pg\_duckdb Extension**

The inclusion of pg\_duckdb in the stack is pivotal. It allows the PlanetScale Postgres database to become an analytical query initiator.

* **Mechanism:** pg\_duckdb embeds a DuckDB instance inside the Postgres worker process.  
* **Capability:** It can read from MotherDuck.  
* **Workflow:**  
  1. Application writes a user subscription update to PlanetScale users table.  
  2. Analyst wants to see "Average PDF downloads per Premium User."  
  3. **Query:**  
     SQL  
     \-- Executed in PlanetScale  
     SELECT u.subscription\_tier, AVG(d.download\_count)  
     FROM public.users u  
     JOIN motherduck.analytics.daily\_downloads d ON u.id \= d.user\_id  
     GROUP BY u.subscription\_tier;

  4. **Execution:** Postgres handles the users scan. pg\_duckdb pushes the daily\_downloads aggregation to MotherDuck's cloud. The reduced result is returned to Postgres for the final join.  
  * **Performance:** Benchmarks indicate that offloading the analytical portion to MotherDuck via this extension can be **99% faster** than running the analysis in native Postgres, while avoiding resource contention on the transactional primary.4

## ---

**7\. Operationalizing the Stack on R2**

### **7.1. R2 Data Catalog vs. Self-Hosted Iceberg**

Cloudflare has recently introduced the **R2 Data Catalog** (in beta), which essentially provides a managed Iceberg REST endpoint for buckets.9

* **Recommendation:** For this stack, the user should prioritize using the **R2 Data Catalog** if available, as it removes the need to self-host an Iceberg REST service (e.g., Tabular or a Docker container).  
* **Configuration:** The Lance Namespace connection string would simply point to the R2 Data Catalog endpoint provided by Cloudflare, simplifying the infrastructure complexity significantly.

### **7.2. Caching Strategy**

Serving PDFs via Lance on R2 relies on network I/O.

* **Tiered Cache:** Enable **Smart Tiered Cache** on the R2 bucket. This helps adjacent requests for the same PDF fragments hit Cloudflare’s regional caches rather than the R2 origin, reducing latency.13  
* **Local NVMe:** For the compute nodes running LanceDB/DuckDB, ensure they have fast local NVMe storage. Lance leverages local disk to cache the **Vector Index**. A "cold" search (fetching index from R2) can take hundreds of milliseconds; a "warm" search (index on local NVMe) takes milliseconds.14

## ---

**8\. Conclusion and Future Outlook**

The proposed architecture represents a sophisticated, future-proof approach to the **AI Data Lakehouse**. By leveraging **Ibis** as the orchestrator, it achieves code portability. By utilizing **PlanetScale** and **MotherDuck**, it optimally segments transactional and analytical workloads while maintaining query interoperability.  
Most importantly, the strategic deployment of **Lance Namespace** transforms the handling of unstructured data. It elevates PDF documents and embeddings from "files in a bucket" to structured, governed, and queryable assets within the **Iceberg** catalog ecosystem. This allows for a system where a user's subscription status, their download history, and the semantic content of their documents can be queried and joined in a single, high-performance request—a capability that defines the next generation of intelligent applications.  
The successful implementation of this stack relies not on monolithic tooling, but on the disciplined integration of these composable parts, glued together by the open standards of Arrow, Lance, and the Iceberg REST protocol.

#### **Works cited**

1. Integration with Ibis \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/guides/python/ibis](https://duckdb.org/docs/stable/guides/python/ibis)  
2. DuckDB \- LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/integrations/platforms/duckdb/](https://lancedb.com/docs/integrations/platforms/duckdb/)  
3. Reading and Writing Parquet Files \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/data/parquet/overview](https://duckdb.org/docs/stable/data/parquet/overview)  
4. MotherDuck Integrates with PlanetScale Postgres, accessed December 24, 2025, [https://motherduck.com/blog/motherduck-planetscale-integration/](https://motherduck.com/blog/motherduck-planetscale-integration/)  
5. accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/\#:\~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.](https://motherduck.com/docs/integrations/file-formats/ducklake/#:~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.)  
6. DuckLake | MotherDuck Docs, accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/](https://motherduck.com/docs/integrations/file-formats/ducklake/)  
7. PlanetScale Postgres, accessed December 24, 2025, [https://planetscale.com/docs/postgres](https://planetscale.com/docs/postgres)  
8. Using MotherDuck with PlanetScale, accessed December 24, 2025, [https://planetscale.com/blog/using-motherduck-with-planetscale](https://planetscale.com/blog/using-motherduck-with-planetscale)  
9. R2 Data Catalog: Managed Apache Iceberg tables with zero egress fees, accessed December 24, 2025, [https://blog.cloudflare.com/r2-data-catalog-public-beta/](https://blog.cloudflare.com/r2-data-catalog-public-beta/)  
10. Apache Iceberg REST Catalog \- Lance, accessed December 24, 2025, [https://lance.org/format/namespace/integrations/iceberg/](https://lance.org/format/namespace/integrations/iceberg/)  
11. lance-format/lance-namespace: Lance Namespace is an ... \- GitHub, accessed December 24, 2025, [https://github.com/lance-format/lance-namespace](https://github.com/lance-format/lance-namespace)  
12. Writing to LanceDB in cloud object storage while other processes are reading? \#1888, accessed December 24, 2025, [https://github.com/lancedb/lancedb/discussions/1888](https://github.com/lancedb/lancedb/discussions/1888)  
13. Public buckets · Cloudflare R2 docs, accessed December 24, 2025, [https://developers.cloudflare.com/r2/buckets/public-buckets/](https://developers.cloudflare.com/r2/buckets/public-buckets/)  
14. Storage Architecture in LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/storage/](https://lancedb.com/docs/storage/)

## Data Processing — Pydantic


> Source: `docs/data_engineering/pydantic/pydantic.md`

---
description: Expert assistant for Pydantic v2 development - helps with models, validation, serialization, and LLM integration patterns.
---

# Pydantic Expert Assistant

You are an expert Pydantic v2 assistant. Help users with data validation, serialization, type checking, and LLM integration patterns.

## Core Knowledge

Reference the comprehensive guide at `@/research/pydantic-v2-comprehensive-guide.md` and the LLM-optimized reference at `@/research/pydantic-llms.txt` for patterns and examples.

## Primary Responsibilities

### 1. Model Design
- Help design BaseModel classes with appropriate fields and types
- Recommend ConfigDict settings for the use case
- Suggest field constraints and metadata
- Advise on model inheritance vs composition

### 2. Validation Patterns
- Implement field validators (before/after/wrap modes)
- Create model validators for cross-field validation
- Design custom Annotated types for reusable constraints
- Set up discriminated unions for polymorphic data

### 3. Serialization
- Configure aliases for API compatibility
- Implement custom serializers for complex types
- Set up exclude/include patterns
- Handle datetime, enum, and custom type serialization

### 4. LLM Integration
- Generate JSON schemas for structured outputs
- Convert models to OpenAI function calling format
- Validate LLM responses with automatic retries
- Integrate with Instructor and PydanticAI

## Guidelines

1. **Always use Pydantic v2 syntax** - ConfigDict not class Config, field_validator not validator
2. **Prefer Annotated types** for reusable validation logic
3. **Use discriminated unions** for polymorphic types with a type field
4. **Generate JSON schemas** for LLM prompts with `model_json_schema()`
5. **Recommend Instructor** for automatic validation retries with LLMs
6. **Consider pydantic-settings** for environment configuration

## Common Patterns to Recommend

### Quick Model
```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    tags: list[str] = []
```

### With Validation
```python
from pydantic import BaseModel, field_validator, model_validator
from typing import Self

class User(BaseModel):
    email: str
    password: str
    password_confirm: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email')
        return v.lower()

    @model_validator(mode='after')
    def check_passwords(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

### For LLM Output
```python
from pydantic import BaseModel, Field
from typing import Literal, List

class ExtractedData(BaseModel):
    """Structured data extracted from text."""
    entities: List[str] = Field(description="Named entities found")
    sentiment: Literal['positive', 'negative', 'neutral']
    confidence: float = Field(ge=0, le=1)

# Generate schema for prompt
schema = ExtractedData.model_json_schema()
```

## When Asked About...

- **Settings/Config**: Recommend pydantic-settings with env files
- **API responses**: Show Response[T] generic pattern
- **Function calling**: Provide pydantic_to_openai_function converter
- **Retries**: Recommend Instructor library with max_retries
- **Agents**: Suggest PydanticAI framework
- **Performance**: Advise reusing TypeAdapter instances

## Response Style

1. Show working code examples
2. Explain the "why" behind patterns
3. Highlight v2 vs v1 differences when relevant
4. Include imports in examples
5. Suggest related patterns the user might need


> Source: `docs/data_engineering/pydantic/pydantic-v2-comprehensive-guide.md`

# Pydantic v2 Comprehensive Guide

A comprehensive reference for Pydantic v2 covering core features, validation patterns, type systems, advanced patterns, and LLM integration.

---

## Table of Contents

1. [Core Features](#1-core-features)
2. [Validation Patterns](#2-validation-patterns)
3. [Ontologies and Type System](#3-ontologies-and-type-system)
4. [Advanced Patterns](#4-advanced-patterns)
5. [LLM Integration Patterns](#5-llm-integration-patterns)

---

## 1. Core Features

### 1.1 BaseModel and Model Configuration

The `BaseModel` class is the foundation of Pydantic. Models are defined by inheriting from `BaseModel` and declaring fields as annotated class attributes.

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        strict=False,           # Enable/disable strict mode
        frozen=False,           # Make model immutable
        extra='forbid',         # 'allow', 'forbid', or 'ignore' extra fields
        validate_assignment=True,  # Validate on attribute assignment
        populate_by_name=True,  # Allow using field names alongside aliases
        str_strip_whitespace=True,  # Strip whitespace from strings
        str_min_length=0,       # Minimum string length
        use_enum_values=True,   # Use enum values instead of enum objects
    )

    id: int
    name: str
    email: str

# Usage
user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())  # {'id': 1, 'name': 'John', 'email': 'john@example.com'}
```

**Key Model Methods:**

```python
# Validation
User.model_validate({'id': 1, 'name': 'John', 'email': 'john@example.com'})
User.model_validate_json('{"id": 1, "name": "John", "email": "john@example.com"}')

# Serialization
user.model_dump()                    # Returns dict
user.model_dump_json()               # Returns JSON string
user.model_dump(exclude={'email'})   # Exclude fields
user.model_dump(by_alias=True)       # Use aliases

# Schema generation
User.model_json_schema()             # Get JSON Schema
User.model_rebuild()                 # Rebuild model schema
```

### 1.2 Field Types and Validators

Pydantic supports a wide range of field types with automatic validation:

```python
from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from decimal import Decimal
from uuid import UUID

class Product(BaseModel):
    # Basic types
    id: int
    name: str
    price: float
    active: bool

    # Optional and default values
    description: Optional[str] = None
    quantity: int = Field(default=0)

    # Collections
    tags: List[str] = []
    metadata: Dict[str, str] = {}

    # Special types
    uuid: UUID
    email: EmailStr
    website: HttpUrl

    # Date/time types
    created_at: datetime
    launch_date: date

    # Numeric with constraints
    rating: float = Field(ge=0, le=5)
    stock: int = Field(ge=0)
    discount: Decimal = Field(max_digits=5, decimal_places=2)
```

### 1.3 Data Parsing and Serialization

Pydantic provides flexible serialization options:

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int = Field(serialization_alias='userId')
    full_name: str = Field(serialization_alias='fullName')
    email_address: str = Field(serialization_alias='email', exclude=True)

user = User(user_id=1, full_name='John Doe', email_address='john@example.com')

# Standard dump
print(user.model_dump())
# {'user_id': 1, 'full_name': 'John Doe'}

# With aliases
print(user.model_dump(by_alias=True))
# {'userId': 1, 'fullName': 'John Doe'}

# JSON serialization
print(user.model_dump_json(by_alias=True, indent=2))

# Include/exclude specific fields
print(user.model_dump(include={'user_id', 'full_name'}))

# Exclude unset, defaults, or None values
print(user.model_dump(exclude_unset=True))
print(user.model_dump(exclude_defaults=True))
print(user.model_dump(exclude_none=True))
```

### 1.4 Type Coercion and Strict Mode

By default, Pydantic coerces values to the correct type. Strict mode disables this behavior:

```python
from pydantic import BaseModel, ConfigDict, Field, ValidationError

# Lax mode (default) - allows coercion
class LaxModel(BaseModel):
    value: int

print(LaxModel(value="42").value)  # 42 (string coerced to int)
print(LaxModel(value=42.9).value)  # 42 (float coerced to int)

# Strict mode - model level
class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)
    value: int

try:
    StrictModel(value="42")  # ValidationError!
except ValidationError as e:
    print(e)

# Strict mode - field level
class MixedModel(BaseModel):
    strict_value: int = Field(strict=True)
    lax_value: int = Field(strict=False)

# Per-call strict validation
class FlexibleModel(BaseModel):
    value: int

FlexibleModel.model_validate({'value': '42'}, strict=True)  # ValidationError!

# Strict type aliases
from pydantic import StrictInt, StrictStr, StrictFloat, StrictBool

class StrictTypesModel(BaseModel):
    count: StrictInt      # Only accepts int, not bool or float
    name: StrictStr       # Only accepts str
    price: StrictFloat    # Only accepts float, not int
    active: StrictBool    # Only accepts bool
```

### 1.5 Computed Fields and Property Decorators

Computed fields are calculated from other fields and included in serialization:

```python
from functools import cached_property
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        """Calculate the area of the rectangle."""
        return self.width * self.height

    @computed_field
    @property
    def perimeter(self) -> float:
        """Calculate the perimeter of the rectangle."""
        return 2 * (self.width + self.height)

    # With cached_property for expensive computations
    @computed_field
    @cached_property
    def diagonal(self) -> float:
        """Calculate diagonal using Pythagorean theorem."""
        return (self.width ** 2 + self.height ** 2) ** 0.5

rect = Rectangle(width=3, height=4)
print(rect.model_dump())
# {'width': 3.0, 'height': 4.0, 'area': 12.0, 'perimeter': 14.0, 'diagonal': 5.0}

# Computed field with setter
class Square(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    side: float

    @computed_field
    @property
    def area(self) -> float:
        return self.side ** 2

    @area.setter
    def area(self, new_area: float) -> None:
        self.side = new_area ** 0.5

square = Square(side=4)
square.area = 25  # Sets side to 5.0
print(square.side)  # 5.0

# Computed fields with custom metadata
class Product(BaseModel):
    price: float
    tax_rate: float = 0.1

    @computed_field(
        alias='totalPrice',
        description='Price including tax',
        repr=False
    )
    @property
    def total(self) -> float:
        return self.price * (1 + self.tax_rate)
```

---

## 2. Validation Patterns

### 2.1 Field Validators (Before, After, Wrap)

Field validators allow custom validation logic on individual fields:

```python
from typing import Any
from pydantic import BaseModel, field_validator, ValidationInfo

class User(BaseModel):
    name: str
    email: str
    age: int

    # After validator (default) - receives validated value
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.title()

    # Before validator - receives raw input
    @field_validator('email', mode='before')
    @classmethod
    def normalize_email(cls, v: Any) -> str:
        if isinstance(v, str):
            return v.lower().strip()
        return v

    # Validator with field info access
    @field_validator('age')
    @classmethod
    def check_age(cls, v: int, info: ValidationInfo) -> int:
        if v < 0:
            raise ValueError('Age must be positive')
        return v

    # Apply to multiple fields
    @field_validator('name', 'email')
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v:
            raise ValueError('Field cannot be empty')
        return v

# Wrap validator - full control over validation
from pydantic import ValidatorFunctionWrapHandler

class WrapExample(BaseModel):
    value: int

    @field_validator('value', mode='wrap')
    @classmethod
    def wrap_validator(
        cls,
        v: Any,
        handler: ValidatorFunctionWrapHandler
    ) -> int:
        # Pre-processing
        if isinstance(v, str) and v.startswith('$'):
            v = v[1:]

        # Call default validation
        result = handler(v)

        # Post-processing
        return abs(result)

print(WrapExample(value='$-42').value)  # 42
```

### 2.2 Model Validators

Model validators validate the entire model at once:

```python
from typing import Any, Self
from pydantic import BaseModel, model_validator, ValidationInfo

class UserRegistration(BaseModel):
    username: str
    password: str
    password_confirm: str

    # Before model validator - receives raw input
    @model_validator(mode='before')
    @classmethod
    def check_raw_data(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Transform or validate raw input
            if 'user' in data and 'name' not in data:
                data['username'] = data.pop('user')
        return data

    # After model validator - receives model instance
    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

class DateRange(BaseModel):
    start_date: str
    end_date: str

    # Wrap model validator - full control
    @model_validator(mode='wrap')
    @classmethod
    def validate_dates(cls, values: Any, handler) -> 'DateRange':
        # Pre-validation logic
        if isinstance(values, dict):
            # Normalize date formats
            pass

        # Run standard validation
        instance = handler(values)

        # Post-validation logic
        if instance.start_date > instance.end_date:
            raise ValueError('start_date must be before end_date')

        return instance
```

### 2.3 Custom Types and Constraints

Create reusable constrained types using `Annotated`:

```python
from typing import Annotated
from pydantic import BaseModel, Field, AfterValidator, BeforeValidator
from pydantic.types import StringConstraints

# String constraints
Username = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_]+$'
    )
]

# Numeric constraints
PositiveInt = Annotated[int, Field(gt=0)]
Percentage = Annotated[float, Field(ge=0, le=100)]
Rating = Annotated[int, Field(ge=1, le=5)]

# Custom validator as type
def validate_even(v: int) -> int:
    if v % 2 != 0:
        raise ValueError('Value must be even')
    return v

EvenInt = Annotated[int, AfterValidator(validate_even)]

# Chained validators
def strip_spaces(v: str) -> str:
    return v.strip()

def to_lowercase(v: str) -> str:
    return v.lower()

NormalizedStr = Annotated[
    str,
    BeforeValidator(strip_spaces),
    AfterValidator(to_lowercase)
]

class Product(BaseModel):
    name: Username
    price: PositiveInt
    discount: Percentage
    rating: Rating
    sku: NormalizedStr
    batch_size: EvenInt

# Legacy constraint functions (deprecated in v3)
from pydantic import conint, constr, confloat

class LegacyModel(BaseModel):
    # These still work but will be deprecated
    count: conint(ge=0, le=100)
    name: constr(min_length=1, max_length=50)
    rate: confloat(ge=0.0, le=1.0)
```

### 2.4 Discriminated Unions

Discriminated unions use a field value to determine the correct type:

```python
from typing import Literal, Union
from typing_extensions import Annotated
from pydantic import BaseModel, Field

# Simple discriminated union
class Cat(BaseModel):
    pet_type: Literal['cat']
    name: str
    meows: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str
    barks: float

class Owner(BaseModel):
    pet: Annotated[
        Union[Cat, Dog],
        Field(discriminator='pet_type')
    ]

# Validates correctly based on pet_type
owner1 = Owner(pet={'pet_type': 'cat', 'name': 'Whiskers', 'meows': 5})
owner2 = Owner(pet={'pet_type': 'dog', 'name': 'Rex', 'barks': 3.5})

# Nested discriminated unions
class BlackCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['black']
    name: str

class WhiteCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['white']
    name: str

class GermanShepherd(BaseModel):
    pet_type: Literal['dog']
    breed: Literal['german_shepherd']
    name: str

Pet = Annotated[
    Union[
        Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')],
        GermanShepherd
    ],
    Field(discriminator='pet_type')
]

# Callable discriminator for complex cases
from pydantic import Discriminator

def get_discriminator_value(v: Any) -> str:
    if isinstance(v, dict):
        return v.get('type', 'unknown')
    return getattr(v, 'type', 'unknown')

class Item(BaseModel):
    items: list[
        Annotated[
            Union[Cat, Dog],
            Discriminator(get_discriminator_value)
        ]
    ]
```

### 2.5 Recursive Models

Models that reference themselves for nested structures:

```python
from typing import Optional, List
from pydantic import BaseModel

# Self-referencing model
class TreeNode(BaseModel):
    value: int
    children: List['TreeNode'] = []

# After model definition, rebuild to resolve forward references
TreeNode.model_rebuild()

tree = TreeNode(
    value=1,
    children=[
        TreeNode(value=2, children=[
            TreeNode(value=4),
            TreeNode(value=5)
        ]),
        TreeNode(value=3)
    ]
)

# Linked list pattern
class LinkedNode(BaseModel):
    value: str
    next: Optional['LinkedNode'] = None

LinkedNode.model_rebuild()

# File system structure
class FileSystemItem(BaseModel):
    name: str
    is_directory: bool
    children: Optional[List['FileSystemItem']] = None

FileSystemItem.model_rebuild()

# JSON-like recursive structure
from typing import Union, Dict

JsonValue = Union[
    str, int, float, bool, None,
    List['JsonValue'],
    Dict[str, 'JsonValue']
]

class JsonContainer(BaseModel):
    data: JsonValue

# Mutual recursion
class Person(BaseModel):
    name: str
    friends: List['Person'] = []
    employer: Optional['Company'] = None

class Company(BaseModel):
    name: str
    employees: List[Person] = []

Person.model_rebuild()
Company.model_rebuild()
```

---

## 3. Ontologies and Type System

### 3.1 Pydantic's Type Annotation System

Pydantic leverages Python's type annotation system with extended support:

```python
from typing import (
    Any, Union, Optional, List, Dict, Tuple, Set,
    FrozenSet, Literal, TypedDict, NamedTuple
)
from pydantic import BaseModel

class ComprehensiveTypes(BaseModel):
    # Union types
    string_or_int: Union[str, int]
    optional_str: Optional[str]  # Same as Union[str, None]

    # Python 3.10+ syntax
    modern_union: str | int | None

    # Collections
    string_list: List[str]
    int_set: Set[int]
    frozen_set: FrozenSet[str]
    tuple_fixed: Tuple[int, str, float]
    tuple_variable: Tuple[int, ...]

    # Nested structures
    nested_dict: Dict[str, List[int]]

    # Literal types
    status: Literal['pending', 'active', 'completed']

    # Any type
    flexible: Any

# TypedDict integration
class UserDict(TypedDict):
    name: str
    age: int

class Container(BaseModel):
    user: UserDict

# NamedTuple integration
class Point(NamedTuple):
    x: float
    y: float

class Shape(BaseModel):
    origin: Point
    points: List[Point]
```

### 3.2 Generic Models

Create reusable generic models with type parameters:

```python
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel, ValidationError

# Define type variables
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Basic generic model
class Response(BaseModel, Generic[T]):
    data: T
    status: int
    message: str

# Usage with different types
int_response = Response[int](data=42, status=200, message='OK')
str_response = Response[str](data='hello', status=200, message='OK')

# Generic with multiple type parameters
class KeyValuePair(BaseModel, Generic[K, V]):
    key: K
    value: V

pair = KeyValuePair[str, int](key='count', value=42)

# Bounded type variables
from pydantic import BaseModel

class Animal(BaseModel):
    name: str

class Dog(Animal):
    breed: str

AnimalT = TypeVar('AnimalT', bound=Animal)

class Shelter(BaseModel, Generic[AnimalT]):
    animals: List[AnimalT]

dog_shelter = Shelter[Dog](animals=[
    Dog(name='Rex', breed='German Shepherd')
])

# Constrained type variables
NumericT = TypeVar('NumericT', int, float)

class Stats(BaseModel, Generic[NumericT]):
    values: List[NumericT]

    @property
    def average(self) -> float:
        return sum(self.values) / len(self.values)

# Nested generics
class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    total: int

class PaginatedUsers(BaseModel):
    result: Page[Response[dict]]

# Inheriting from generic models
class TimestampedResponse(Response[T], Generic[T]):
    timestamp: str

response = TimestampedResponse[dict](
    data={'key': 'value'},
    status=200,
    message='OK',
    timestamp='2024-01-01T00:00:00Z'
)
```

### 3.3 TypeAdapter

`TypeAdapter` enables validation and serialization without creating a model:

```python
from typing import List, Dict, Union
from pydantic import TypeAdapter, ValidationError
from datetime import datetime

# Basic TypeAdapter usage
int_adapter = TypeAdapter(int)
print(int_adapter.validate_python('42'))  # 42

list_adapter = TypeAdapter(List[int])
print(list_adapter.validate_python([1, 2, 3]))  # [1, 2, 3]

# JSON validation
json_data = '[1, 2, 3]'
print(list_adapter.validate_json(json_data))  # [1, 2, 3]

# Complex type validation
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

users_adapter = TypeAdapter(List[User])
users = users_adapter.validate_python([
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25}
])

# Union type adapter
union_adapter = TypeAdapter(Union[int, str])
print(union_adapter.validate_python(42))      # 42
print(union_adapter.validate_python('hello')) # 'hello'

# JSON Schema generation
print(list_adapter.json_schema())
# {'items': {'type': 'integer'}, 'type': 'array'}

# Serialization
dt_adapter = TypeAdapter(datetime)
dt = datetime(2024, 1, 1, 12, 0, 0)
print(dt_adapter.dump_python(dt, mode='json'))
# '2024-01-01T12:00:00'

# Dict type adapter
dict_adapter = TypeAdapter(Dict[str, int])
print(dict_adapter.validate_python({'a': 1, 'b': 2}))

# TypeAdapter with discriminated union
from typing_extensions import Annotated
from pydantic import Field

class Cat(BaseModel):
    pet_type: str = 'cat'
    meows: int

class Dog(BaseModel):
    pet_type: str = 'dog'
    barks: float

PetUnion = Annotated[
    Union[Cat, Dog],
    Field(discriminator='pet_type')
]
pet_adapter = TypeAdapter(PetUnion)

cat = pet_adapter.validate_python({'pet_type': 'cat', 'meows': 5})
print(type(cat))  # <class 'Cat'>

# Performance: Reuse TypeAdapter instances
# Bad - creates new adapter each time
for item in items:
    TypeAdapter(List[int]).validate_python(item)

# Good - reuse adapter
adapter = TypeAdapter(List[int])
for item in items:
    adapter.validate_python(item)
```

### 3.4 JSON Schema Generation

Generate JSON Schema from Pydantic models:

```python
from typing import List, Optional
from pydantic import BaseModel, Field
import json

class Address(BaseModel):
    street: str = Field(description='Street address')
    city: str
    country: str = Field(default='USA')

class Person(BaseModel):
    """A person with contact information."""
    name: str = Field(
        min_length=1,
        max_length=100,
        description='Full name of the person'
    )
    age: int = Field(
        ge=0,
        le=150,
        description='Age in years'
    )
    email: Optional[str] = Field(
        default=None,
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        description='Email address'
    )
    addresses: List[Address] = Field(
        default_factory=list,
        description='List of addresses'
    )

# Generate JSON Schema
schema = Person.model_json_schema()
print(json.dumps(schema, indent=2))

# Schema with different modes
validation_schema = Person.model_json_schema(mode='validation')
serialization_schema = Person.model_json_schema(mode='serialization')

# Custom schema generation
from pydantic.json_schema import GenerateJsonSchema

class CustomJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
        return json_schema

custom_schema = Person.model_json_schema(
    schema_generator=CustomJsonSchema
)

# Schema for multiple models
from pydantic.json_schema import models_json_schema

class User(BaseModel):
    username: str
    email: str

class Product(BaseModel):
    name: str
    price: float

_, top_level_schema = models_json_schema(
    [(User, 'validation'), (Product, 'validation')],
    title='My API Schema'
)

# TypeAdapter JSON Schema
from pydantic import TypeAdapter

adapter = TypeAdapter(List[int])
print(adapter.json_schema())
# {'items': {'type': 'integer'}, 'type': 'array'}
```

### 3.5 Dataclass Integration

Pydantic's `@dataclass` decorator adds validation to standard dataclasses:

```python
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from typing import List, Optional

# Basic Pydantic dataclass
@dataclass
class User:
    id: int
    name: str
    email: str

user = User(id=1, name='John', email='john@example.com')

# With configuration
@dataclass(config=ConfigDict(
    strict=True,
    validate_assignment=True
))
class StrictUser:
    id: int
    name: str

# Using __pydantic_config__
@dataclass
class ConfiguredUser:
    __pydantic_config__ = ConfigDict(
        extra='forbid',
        frozen=True
    )
    id: int
    name: str

# Nested dataclasses
@dataclass
class Address:
    street: str
    city: str

@dataclass
class Person:
    name: str
    addresses: List[Address]

person = Person(
    name='John',
    addresses=[
        Address(street='123 Main St', city='NYC'),
        Address(street='456 Oak Ave', city='LA')
    ]
)

# Mixing with stdlib dataclasses
from dataclasses import dataclass as stdlib_dataclass

@stdlib_dataclass
class StandardAddress:
    street: str
    city: str

@dataclass
class PersonWithStdlib:
    name: str
    address: StandardAddress  # Pydantic validates nested stdlib dataclass

# Conversion to dict/JSON
from pydantic import TypeAdapter

@dataclass
class Product:
    name: str
    price: float

product = Product(name='Widget', price=9.99)
adapter = TypeAdapter(Product)

# Serialize
print(adapter.dump_python(product))  # {'name': 'Widget', 'price': 9.99}
print(adapter.dump_json(product))    # b'{"name":"Widget","price":9.99}'

# Get JSON Schema
print(adapter.json_schema())
```

---

## 4. Advanced Patterns

### 4.1 Settings Management with pydantic-settings

`pydantic-settings` provides configuration management from environment variables:

```python
# pip install pydantic-settings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='DB_',            # All vars prefixed with DB_
        env_nested_delimiter='__',   # For nested settings
        case_sensitive=False,
        extra='ignore'
    )

    host: str = 'localhost'
    port: int = 5432
    name: str = Field(alias='database')
    user: str
    password: str

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='APP_'
    )

    debug: bool = False
    secret_key: str
    api_version: str = 'v1'

    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

# Usage
# Environment variables: APP_DEBUG=true, APP_SECRET_KEY=xxx, DB_HOST=prod-db
settings = AppSettings()

# Multiple environment files (priority: later files override earlier)
class MultiEnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '.env.local', '.env.production')
    )
    api_key: str

# Secrets directory (for Docker secrets, etc.)
class SecretSettings(BaseSettings):
    model_config = SettingsConfigDict(
        secrets_dir='/run/secrets'
    )
    db_password: str

# Multiple sources with AliasChoices
from pydantic_settings import AliasChoices, AliasPath

class FlexibleSettings(BaseSettings):
    # Accept from multiple env var names
    api_key: str = Field(
        validation_alias=AliasChoices(
            'API_KEY',
            'OPENAI_API_KEY',
            AliasPath('credentials', 'api_key')
        )
    )

# Custom settings sources
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
)

class CustomSettings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
```

### 4.2 Custom Serializers/Deserializers

Control how fields are serialized and deserialized:

```python
from typing import Any, Annotated
from datetime import datetime
from pydantic import (
    BaseModel,
    field_serializer,
    field_validator,
    PlainSerializer,
    WrapSerializer,
    SerializerFunctionWrapHandler
)

class User(BaseModel):
    name: str
    created_at: datetime
    tags: list[str]

    # Field serializer
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    # Serialize multiple fields
    @field_serializer('name', 'tags')
    def uppercase(self, value):
        if isinstance(value, str):
            return value.upper()
        return [v.upper() for v in value]

    # Mode-specific serialization
    @field_serializer('created_at', when_used='json')
    def serialize_for_json(self, dt: datetime) -> str:
        return dt.isoformat()

# Using Annotated with PlainSerializer
def serialize_to_hex(value: int) -> str:
    return hex(value)

HexInt = Annotated[int, PlainSerializer(serialize_to_hex)]

class HexModel(BaseModel):
    value: HexInt

print(HexModel(value=255).model_dump())  # {'value': '0xff'}

# WrapSerializer for complex transformations
def wrap_serialize(value: Any, handler: SerializerFunctionWrapHandler) -> Any:
    # Pre-process
    result = handler(value)
    # Post-process
    if isinstance(result, str):
        return f"[{result}]"
    return result

WrappedStr = Annotated[str, WrapSerializer(wrap_serialize)]

# Model-level serializer
from pydantic import model_serializer

class CustomModel(BaseModel):
    x: int
    y: int

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            'coordinates': f"({self.x}, {self.y})",
            'sum': self.x + self.y
        }

print(CustomModel(x=1, y=2).model_dump())
# {'coordinates': '(1, 2)', 'sum': 3}

# Custom deserialization with validators
class Product(BaseModel):
    price_cents: int

    @field_validator('price_cents', mode='before')
    @classmethod
    def parse_price(cls, v):
        if isinstance(v, str) and v.startswith('$'):
            # Convert "$10.50" to 1050 cents
            return int(float(v[1:]) * 100)
        return v
```

### 4.3 Alias and Field Metadata

Configure field aliases for validation and serialization:

```python
from pydantic import BaseModel, Field, AliasPath, AliasChoices, AliasGenerator
from pydantic.alias_generators import to_camel, to_snake

class User(BaseModel):
    # Simple alias (used for both validation and serialization)
    user_id: int = Field(alias='userId')

    # Separate validation and serialization aliases
    full_name: str = Field(
        validation_alias='fullName',      # Accept 'fullName' in input
        serialization_alias='full_name'   # Output as 'full_name'
    )

    # Multiple validation aliases
    email: str = Field(
        validation_alias=AliasChoices('email', 'emailAddress', 'e-mail')
    )

# Validation with alias
user = User.model_validate({
    'userId': 1,
    'fullName': 'John Doe',
    'email': 'john@example.com'
})

# AliasPath for nested data
class NestedUser(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))
    city: str = Field(validation_alias=AliasPath('address', 'city'))

data = {
    'names': ['John', 'Doe'],
    'address': {'city': 'NYC', 'zip': '10001'}
}
user = NestedUser.model_validate(data)

# AliasGenerator for automatic alias generation
class CamelCaseModel(BaseModel):
    model_config = {
        'alias_generator': AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_camel
        ),
        'populate_by_name': True  # Allow both field name and alias
    }

    user_name: str
    email_address: str

# Accepts: {'userName': 'John', 'emailAddress': 'john@example.com'}
# Also accepts: {'user_name': 'John', 'email_address': 'john@example.com'}

# Field metadata for documentation
class Product(BaseModel):
    name: str = Field(
        title='Product Name',
        description='The display name of the product',
        examples=['Widget', 'Gadget'],
        json_schema_extra={'x-custom': 'value'}
    )
    price: float = Field(
        ge=0,
        description='Price in USD',
        examples=[9.99, 19.99],
        deprecated=True  # Mark as deprecated
    )
```

### 4.4 Model Inheritance and Composition

Create complex models through inheritance and composition:

```python
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Basic inheritance
class BaseItem(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    id: int
    created_at: str

class Product(BaseItem):
    name: str
    price: float

class Service(BaseItem):
    name: str
    hourly_rate: float

# Config inheritance and override
class StrictProduct(Product):
    model_config = ConfigDict(
        strict=True,  # Adds to parent config
    )

# Mixin pattern
class TimestampMixin(BaseModel):
    created_at: str = Field(default_factory=lambda: '2024-01-01')
    updated_at: Optional[str] = None

class AuditMixin(BaseModel):
    created_by: str
    modified_by: Optional[str] = None

class AuditedProduct(TimestampMixin, AuditMixin, BaseModel):
    name: str
    price: float

# Composition over inheritance
class Address(BaseModel):
    street: str
    city: str
    country: str = 'USA'

class ContactInfo(BaseModel):
    email: str
    phone: Optional[str] = None

class Customer(BaseModel):
    name: str
    billing_address: Address
    shipping_address: Optional[Address] = None
    contact: ContactInfo

# Factory method pattern
class Animal(BaseModel):
    name: str
    species: str

    @classmethod
    def create_dog(cls, name: str) -> 'Animal':
        return cls(name=name, species='dog')

    @classmethod
    def create_cat(cls, name: str) -> 'Animal':
        return cls(name=name, species='cat')

# Abstract base with required fields
from abc import ABC

class AbstractItem(BaseModel, ABC):
    id: int

    def get_display_name(self) -> str:
        raise NotImplementedError

class ConcreteProduct(AbstractItem):
    name: str

    def get_display_name(self) -> str:
        return f"Product: {self.name}"
```

### 4.5 Private Attributes and Frozen Models

Control mutability and hide internal state:

```python
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from typing import Optional

# Private attributes (not validated, not serialized)
class Model(BaseModel):
    public_field: str

    # Private attributes with PrivateAttr
    _private_value: int = PrivateAttr(default=0)
    _cache: Optional[dict] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._private_value = len(self.public_field)

    def get_cached(self, key: str) -> Optional[str]:
        if self._cache is None:
            self._cache = {}
        return self._cache.get(key)

    def set_cached(self, key: str, value: str) -> None:
        if self._cache is None:
            self._cache = {}
        self._cache[key] = value

m = Model(public_field='hello')
print(m.model_dump())  # {'public_field': 'hello'} - no private attrs

# Frozen (immutable) models
class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    value: int

frozen = FrozenModel(name='test', value=42)
# frozen.name = 'new'  # Raises ValidationError!

# Frozen enables hashing
print(hash(frozen))  # Works because model is immutable

# Use in sets and as dict keys
frozen_set = {frozen, FrozenModel(name='other', value=1)}
frozen_dict = {frozen: 'data'}

# Field-level immutability
class PartiallyFrozen(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: int = Field(frozen=True)  # Only this field is immutable
    name: str  # This can be changed

pf = PartiallyFrozen(id=1, name='test')
pf.name = 'updated'  # OK
# pf.id = 2  # Raises ValidationError!

# Combining with validation on assignment
class ValidatedAssignment(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False
    )

    count: int = Field(ge=0)

va = ValidatedAssignment(count=5)
va.count = 10  # OK, validates
# va.count = -1  # Raises ValidationError

# Private attrs with initialization
class Counter(BaseModel):
    name: str
    _count: int = PrivateAttr(default=0)

    def increment(self) -> int:
        self._count += 1
        return self._count

counter = Counter(name='clicks')
print(counter.increment())  # 1
print(counter.increment())  # 2
```

---

## 5. LLM Integration Patterns

### 5.1 Structured Output Generation

Use Pydantic to define and validate structured LLM outputs:

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import json

# Define structured output schema
class ExtractedEntity(BaseModel):
    """An entity extracted from text."""
    name: str = Field(description="The entity name")
    type: Literal['person', 'organization', 'location', 'date']
    confidence: float = Field(ge=0, le=1, description="Confidence score")

class SentimentAnalysis(BaseModel):
    """Sentiment analysis result."""
    sentiment: Literal['positive', 'negative', 'neutral']
    score: float = Field(ge=-1, le=1)
    aspects: List[str] = Field(description="Key aspects mentioned")

class DocumentSummary(BaseModel):
    """Structured document summary."""
    title: str
    summary: str = Field(max_length=500)
    key_points: List[str] = Field(min_length=1, max_length=10)
    entities: List[ExtractedEntity]
    sentiment: SentimentAnalysis
    language: str = Field(default='en')

# Generate JSON Schema for LLM prompt
schema = DocumentSummary.model_json_schema()
print(json.dumps(schema, indent=2))

# Example prompt construction
def create_extraction_prompt(text: str, model_class: type[BaseModel]) -> str:
    schema = model_class.model_json_schema()
    return f"""
Extract information from the following text and return it as JSON
matching this schema:

{json.dumps(schema, indent=2)}

Text:
{text}

Return only valid JSON.
"""

# Validate LLM response
def parse_llm_response(response: str, model_class: type[BaseModel]):
    """Parse and validate LLM JSON response."""
    try:
        return model_class.model_validate_json(response)
    except Exception as e:
        # Handle validation errors
        raise ValueError(f"Invalid LLM response: {e}")

# Example with nested structures
class CodeReview(BaseModel):
    class Issue(BaseModel):
        line: int
        severity: Literal['error', 'warning', 'info']
        message: str
        suggestion: Optional[str] = None

    file_path: str
    issues: List[Issue]
    overall_quality: int = Field(ge=1, le=10)
    summary: str
```

### 5.2 Function Calling Schemas

Generate OpenAI-compatible function schemas:

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import json

# Define function parameters as Pydantic models
class SearchQuery(BaseModel):
    """Search for information in the knowledge base."""
    query: str = Field(description="The search query")
    max_results: int = Field(default=5, ge=1, le=20)
    filters: Optional[dict] = Field(default=None, description="Optional filters")

class SendEmail(BaseModel):
    """Send an email to a recipient."""
    to: str = Field(description="Recipient email address")
    subject: str = Field(max_length=200)
    body: str
    cc: Optional[List[str]] = None
    priority: Literal['low', 'normal', 'high'] = 'normal'

class CreateCalendarEvent(BaseModel):
    """Create a calendar event."""
    title: str
    start_time: str = Field(description="ISO 8601 datetime")
    end_time: str = Field(description="ISO 8601 datetime")
    attendees: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    description: Optional[str] = None

# Convert to OpenAI function format
def pydantic_to_openai_function(model: type[BaseModel]) -> dict:
    """Convert Pydantic model to OpenAI function schema."""
    schema = model.model_json_schema()

    return {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": model.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    }

# Generate tools for OpenAI
tools = [
    pydantic_to_openai_function(SearchQuery),
    pydantic_to_openai_function(SendEmail),
    pydantic_to_openai_function(CreateCalendarEvent),
]

print(json.dumps(tools, indent=2))

# Parse function call result
def execute_function_call(name: str, arguments: str) -> any:
    """Execute a function call from LLM."""
    function_map = {
        'SearchQuery': SearchQuery,
        'SendEmail': SendEmail,
        'CreateCalendarEvent': CreateCalendarEvent,
    }

    model_class = function_map.get(name)
    if not model_class:
        raise ValueError(f"Unknown function: {name}")

    # Validate arguments
    params = model_class.model_validate_json(arguments)

    # Execute the function (implementation depends on your system)
    return execute_action(name, params)

def execute_action(name: str, params: BaseModel):
    """Placeholder for actual function execution."""
    return {"status": "success", "params": params.model_dump()}
```

### 5.3 API Response Validation

Validate responses from LLM APIs and external services:

```python
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# OpenAI API response models
class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[dict]] = None

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str

class ChatCompletion(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage

    @property
    def content(self) -> Optional[str]:
        """Get the content from the first choice."""
        if self.choices:
            return self.choices[0].message.content
        return None

# Validate API response
def process_openai_response(raw_response: dict) -> ChatCompletion:
    """Validate and parse OpenAI API response."""
    return ChatCompletion.model_validate(raw_response)

# Anthropic API response models
class ContentBlock(BaseModel):
    type: str
    text: Optional[str] = None

class AnthropicResponse(BaseModel):
    id: str
    type: str
    role: str
    content: List[ContentBlock]
    model: str
    stop_reason: Optional[str] = None
    usage: dict

# Generic LLM response wrapper
class LLMResponse(BaseModel):
    """Unified response from any LLM provider."""
    provider: str
    model: str
    content: str
    tokens_used: int
    finish_reason: str
    raw_response: dict = Field(exclude=True)  # Store but don't serialize

    @classmethod
    def from_openai(cls, response: ChatCompletion) -> 'LLMResponse':
        return cls(
            provider='openai',
            model=response.model,
            content=response.content or '',
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason,
            raw_response=response.model_dump()
        )

# Error response handling
class APIError(BaseModel):
    error: dict
    status_code: int

class APIResponse(BaseModel):
    """Wrapper for API responses that may be success or error."""
    success: bool
    data: Optional[ChatCompletion] = None
    error: Optional[APIError] = None

    @field_validator('data', 'error')
    @classmethod
    def validate_response(cls, v, info):
        # Ensure either data or error is present
        return v
```

### 5.4 Prompt Templating with Models

Use Pydantic models to structure and validate prompts:

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, computed_field
from string import Template

# Prompt configuration model
class PromptConfig(BaseModel):
    """Configuration for prompt generation."""
    model: str = 'gpt-4'
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1000, ge=1)
    system_prompt: Optional[str] = None

# Template-based prompt
class PromptTemplate(BaseModel):
    """A prompt template with variables."""
    template: str
    variables: dict[str, str] = Field(default_factory=dict)

    @computed_field
    @property
    def rendered(self) -> str:
        """Render the template with variables."""
        return Template(self.template).safe_substitute(self.variables)

# Structured prompt for specific tasks
class ExtractionPrompt(BaseModel):
    """Prompt for entity extraction tasks."""
    task: Literal['ner', 'sentiment', 'summary', 'qa']
    text: str
    instructions: str = ""
    examples: List[dict] = Field(default_factory=list)
    output_format: str = "json"

    @computed_field
    @property
    def full_prompt(self) -> str:
        prompt_parts = [
            f"Task: {self.task}",
            f"Instructions: {self.instructions}" if self.instructions else "",
            "",
            "Examples:" if self.examples else "",
        ]

        for ex in self.examples:
            prompt_parts.append(f"Input: {ex.get('input', '')}")
            prompt_parts.append(f"Output: {ex.get('output', '')}")
            prompt_parts.append("")

        prompt_parts.extend([
            "Now process the following:",
            f"Input: {self.text}",
            f"Output ({self.output_format}):"
        ])

        return "\n".join(filter(None, prompt_parts))

# Chat message models
class ChatMessage(BaseModel):
    role: Literal['system', 'user', 'assistant']
    content: str

class ChatConversation(BaseModel):
    """A conversation with message history."""
    messages: List[ChatMessage] = Field(default_factory=list)
    config: PromptConfig = Field(default_factory=PromptConfig)

    def add_system(self, content: str) -> 'ChatConversation':
        self.messages.append(ChatMessage(role='system', content=content))
        return self

    def add_user(self, content: str) -> 'ChatConversation':
        self.messages.append(ChatMessage(role='user', content=content))
        return self

    def add_assistant(self, content: str) -> 'ChatConversation':
        self.messages.append(ChatMessage(role='assistant', content=content))
        return self

    def to_openai_format(self) -> List[dict]:
        return [msg.model_dump() for msg in self.messages]

# Usage example
conversation = (
    ChatConversation()
    .add_system("You are a helpful assistant that extracts structured data.")
    .add_user("Extract the person's name and age from: John is 25 years old.")
)

print(conversation.to_openai_format())

# Advanced: Prompt with schema injection
class SchemaPrompt(BaseModel):
    """Prompt that includes output schema."""
    task_description: str
    input_data: str
    output_model: type[BaseModel]

    @computed_field
    @property
    def full_prompt(self) -> str:
        schema = self.output_model.model_json_schema()
        return f"""
{self.task_description}

Input:
{self.input_data}

Return your response as JSON matching this schema:
{schema}
"""
```

### 5.5 Using Instructor Library

Instructor provides automatic validation and retries for LLM structured outputs:

```python
# pip install instructor
import instructor
from pydantic import BaseModel, Field
from typing import List

# Patch OpenAI client
from openai import OpenAI
client = instructor.from_openai(OpenAI())

# Simple extraction
class User(BaseModel):
    name: str
    age: int

user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=User,
    messages=[
        {"role": "user", "content": "John Doe is 25 years old"}
    ],
)
print(user)  # User(name='John Doe', age=25)

# Complex nested structures
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    addresses: List[Address]

person = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=Person,
    messages=[
        {"role": "user", "content": """
            Extract: John Doe, 30 years old, lives at
            123 Main St, NYC, USA and 456 Oak Ave, LA, USA
        """}
    ],
)

# With validation and automatic retries
from pydantic import field_validator

class ValidatedUser(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

# Instructor automatically retries if validation fails
user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=ValidatedUser,
    max_retries=3,  # Retry up to 3 times on validation failure
    messages=[
        {"role": "user", "content": "John Doe, 25, john@example.com"}
    ],
)

# Streaming with partial validation
from instructor import Partial

class Report(BaseModel):
    title: str
    sections: List[str]
    summary: str

# Stream partial results as they're generated
for partial_report in client.chat.completions.create_partial(
    model="gpt-4o-mini",
    response_model=Report,
    messages=[
        {"role": "user", "content": "Write a report about AI"}
    ],
):
    print(partial_report)  # Partially complete Report object

# Multiple providers
import instructor
from anthropic import Anthropic

# Works with Anthropic
anthropic_client = instructor.from_anthropic(Anthropic())

user = anthropic_client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    response_model=User,
    messages=[
        {"role": "user", "content": "Extract: Jane Smith is 30"}
    ],
)
```

### 5.6 Using PydanticAI Framework

PydanticAI is the official agent framework from Pydantic:

```python
# pip install pydantic-ai
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List

# Simple agent with structured output
class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    famous_for: List[str]

agent = Agent(
    'openai:gpt-4o-mini',
    output_type=CityInfo,
    system_prompt='You are a helpful geography assistant.'
)

result = agent.run_sync('Tell me about Paris')
print(result.output)  # CityInfo object

# Agent with dependencies
from dataclasses import dataclass
from pydantic_ai import RunContext

@dataclass
class Dependencies:
    user_id: str
    api_key: str

class UserProfile(BaseModel):
    name: str
    preferences: List[str]

agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=Dependencies,
    output_type=UserProfile,
)

@agent.system_prompt
def get_system_prompt(ctx: RunContext[Dependencies]) -> str:
    return f'Get profile for user {ctx.deps.user_id}'

result = agent.run_sync(
    'Get my profile',
    deps=Dependencies(user_id='123', api_key='xxx')
)

# Agent with tools
class SearchResult(BaseModel):
    query: str
    results: List[str]

agent = Agent(
    'openai:gpt-4o-mini',
    output_type=SearchResult,
)

@agent.tool
def search_database(ctx: RunContext, query: str) -> List[str]:
    """Search the database for information."""
    # Implementation
    return ['Result 1', 'Result 2']

@agent.tool_plain
def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return datetime.now().isoformat()

result = agent.run_sync('Search for Python tutorials')

# Multiple output types
from typing import Union

class WeatherInfo(BaseModel):
    temperature: float
    conditions: str

class ErrorResponse(BaseModel):
    error: str
    code: int

agent = Agent(
    'openai:gpt-4o-mini',
    output_type=Union[WeatherInfo, ErrorResponse],
)

# Conversation with message history
from pydantic_ai.messages import ModelMessage

agent = Agent('openai:gpt-4o-mini')

result1 = agent.run_sync('My name is John')
result2 = agent.run_sync(
    'What is my name?',
    message_history=result1.all_messages()
)
print(result2.output)  # Will remember the name
```

---

## Quick Reference

### Common Imports

```python
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
    PrivateAttr,
    TypeAdapter,
    ValidationError,
    # Serializers
    field_serializer,
    PlainSerializer,
    WrapSerializer,
    # Aliases
    AliasPath,
    AliasChoices,
    AliasGenerator,
    # Types
    EmailStr,
    HttpUrl,
    SecretStr,
    StrictInt,
    StrictStr,
)

from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import (
    Annotated,
    List,
    Dict,
    Optional,
    Union,
    Literal,
    TypeVar,
    Generic,
)
```

### Model Lifecycle Methods

| Method | Purpose |
|--------|---------|
| `model_validate(data)` | Validate dict/object |
| `model_validate_json(json_str)` | Validate JSON string |
| `model_dump()` | Convert to dict |
| `model_dump_json()` | Convert to JSON string |
| `model_json_schema()` | Generate JSON Schema |
| `model_copy()` | Create a copy |
| `model_rebuild()` | Rebuild model schema |

### Validator Modes

| Mode | When it Runs | Use Case |
|------|--------------|----------|
| `before` | Before type coercion | Transform raw input |
| `after` | After validation (default) | Validate/transform result |
| `wrap` | Wraps validation | Full control over process |
| `plain` | Replaces validation | Skip default validation |

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `strict` | `False` | Disable type coercion |
| `frozen` | `False` | Make model immutable |
| `extra` | `'ignore'` | Handle extra fields |
| `validate_assignment` | `False` | Validate on assignment |
| `populate_by_name` | `False` | Allow field name + alias |
| `str_strip_whitespace` | `False` | Strip string whitespace |

---

## Resources

- **Official Documentation**: https://docs.pydantic.dev/
- **PydanticAI**: https://ai.pydantic.dev/
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Instructor Library**: https://python.useinstructor.com/
- **GitHub**: https://github.com/pydantic/pydantic
- **PyPI**: https://pypi.org/project/pydantic/


> Source: `docs/data_engineering/pydantic/pydantic_schema_validate.md`

---
description: Add validation logic to Pydantic models - field validators, model validators, and custom types.
---

# Pydantic Validation Expert

Help add validation logic to Pydantic models using validators and custom types.

## Validation Patterns

### Field Validator (Single Field)
```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower().strip()
```

### Before Validator (Pre-processing)
```python
@field_validator('data', mode='before')
@classmethod
def parse_json(cls, v):
    if isinstance(v, str):
        import json
        return json.loads(v)
    return v
```

### Model Validator (Cross-field)
```python
from pydantic import model_validator
from typing import Self

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode='after')
    def validate_range(self) -> Self:
        if self.start >= self.end:
            raise ValueError('start must be before end')
        return self
```

### Custom Annotated Types (Reusable)
```python
from typing import Annotated
from pydantic import AfterValidator, Field

def validate_positive(v: int) -> int:
    if v <= 0:
        raise ValueError('Must be positive')
    return v

PositiveInt = Annotated[int, AfterValidator(validate_positive)]
Username = Annotated[str, Field(min_length=3, max_length=50, pattern=r'^[a-z0-9_]+$')]

class User(BaseModel):
    id: PositiveInt
    username: Username
```

## Validator Modes

| Mode | Receives | Use Case |
|------|----------|----------|
| `after` (default) | Validated value | Transform or validate result |
| `before` | Raw input | Parse strings, normalize data |
| `wrap` | Value + handler | Full control, can skip validation |
| `plain` | Raw input | Replace default validation entirely |

## Common Validation Needs

Ask what needs validation:
- Format constraints (email, URL, phone)?
- Business rules (password match, date ranges)?
- Data normalization (strip, lowercase)?
- Cross-field dependencies?
- Conditional validation?


## Data Processing — Evidence BI


> Source: `docs/data_engineering/evidence/evidence.md`

# Evidence.dev Expert Assistant

You are an expert Evidence.dev consultant specializing in building data products with SQL and markdown, business intelligence as code, and production-grade data visualization applications.

## Your Role

Help users with:
- Designing and implementing Evidence.dev dashboards and reports
- Best practices for SQL-based data visualization
- Architecture decisions and patterns
- Component selection and configuration
- Data source setup and optimization
- Deployment and production readiness
- Interactive features and templated pages

## Core Principles

When assisting with Evidence.dev:

1. **Markdown-First Approach**: Leverage the simplicity of markdown for readable, maintainable reports
2. **SQL-Driven Data**: Write efficient SQL queries that power visualizations
3. **Component Composition**: Choose the right components for data presentation
4. **Interactivity**: Use input components and parameterized queries effectively
5. **Performance**: Optimize queries and leverage browser-based DuckDB execution
6. **Version Control**: Treat dashboards as code for collaboration and review

## Knowledge Base

### Current Version
Evidence.dev (latest stable)
Node.js >= 18.13, 20, or 22
NPM >= 7

### Core Concepts

**Pages (Primary Abstraction)**
- Markdown files in `/pages` become routes
- Contain SQL queries, components, and templating
- File-based routing: `pages/sales.md` → `/sales`

**SQL Queries**
- Written in fenced code blocks with query names
- Execute via DuckDB WebAssembly in browser
- Chain queries using `${query_name}` syntax
- Parameterize with `${inputs.name.value}` and `${params.name}`

**Components**
- Self-closing JSX-like syntax
- Data binding via `data={query_name}`
- Rich formatting options built-in
- Charts, tables, inputs, UI elements

**Sources**
- External database connections
- Cached as Parquet files
- Run with `npm run sources`
- Referenced as `source_name.query_name`

**Templated Pages**
- Dynamic routes with `[parameter].md`
- Generate multiple pages from templates
- Access URL params with `{params.name}`

### Project Structure

```
my-project/
├── pages/                    # Markdown pages (routes)
│   ├── index.md             # Home page
│   └── [customer].md        # Templated page
├── sources/                  # Data source queries
│   └── my_database/
│       └── orders.sql
├── queries/                  # Reusable SQL files
├── partials/                 # Reusable markdown
├── components/               # Custom Svelte components
├── static/                   # Static assets
├── evidence.config.yaml      # Configuration
└── package.json
```

### Design Patterns

**Basic Dashboard**
```markdown
---
title: Sales Dashboard
---

# Sales Dashboard

```sql total_metrics
SELECT
    SUM(sales) as total_sales,
    COUNT(*) as total_orders
FROM orders
WHERE order_date >= '2024-01-01'
```

<BigValue
    data={total_metrics}
    value=total_sales
    fmt=usd0
    title="Total Sales"
/>

<BigValue
    data={total_metrics}
    value=total_orders
    title="Total Orders"
/>

## Monthly Trend

```sql monthly_sales
SELECT
    date_trunc('month', order_date) as month,
    SUM(sales) as sales
FROM orders
GROUP BY 1
ORDER BY 1
```

<LineChart
    data={monthly_sales}
    x=month
    y=sales
    title="Sales by Month"
/>
```

**Interactive Filtering**
```markdown
```sql categories
SELECT DISTINCT category FROM products
```

<Dropdown
    name=category_filter
    data={categories}
    value=category
    title="Select Category"
/>

```sql filtered_products
SELECT * FROM products
WHERE category = '${inputs.category_filter.value}'
```

<DataTable data={filtered_products} />
```

**Query Chaining**
```markdown
```sql base_orders
SELECT * FROM orders
WHERE status = 'completed'
```

```sql order_summary
SELECT
    category,
    SUM(amount) as total,
    COUNT(*) as count
FROM ${base_orders}
GROUP BY 1
```
```

**Templated Customer Pages**
```markdown
<!-- pages/customers/[customer].md -->
---
title: Customer Details
---

# Customer: {params.customer}

```sql customer_orders
SELECT * FROM orders
WHERE customer_name = '${params.customer}'
```

<DataTable data={customer_orders} />
```

### Common Use Cases

**KPI Dashboard**
```markdown
```sql kpis
SELECT
    SUM(revenue) as revenue,
    SUM(profit) as profit,
    COUNT(DISTINCT customer_id) as customers,
    revenue / NULLIF(customers, 0) as avg_per_customer
FROM sales
WHERE date >= DATE_TRUNC('month', CURRENT_DATE)
```

<Grid cols=4>
    <BigValue data={kpis} value=revenue fmt=usd0 title="Revenue" />
    <BigValue data={kpis} value=profit fmt=usd0 title="Profit" />
    <BigValue data={kpis} value=customers title="Customers" />
    <BigValue data={kpis} value=avg_per_customer fmt=usd0 title="Avg/Customer" />
</Grid>
```

**Comparison Report**
```markdown
```sql period_comparison
SELECT
    'Current' as period,
    SUM(sales) as sales
FROM orders WHERE date >= '2024-01-01'
UNION ALL
SELECT
    'Previous' as period,
    SUM(sales) as sales
FROM orders WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
```

<BarChart
    data={period_comparison}
    x=period
    y=sales
    title="Year over Year Comparison"
/>
```

**Regional Analysis**
```markdown
```sql regional_data
SELECT
    region,
    SUM(sales) as sales,
    COUNT(*) as orders
FROM orders
GROUP BY 1
```

<AreaMap
    data={regional_data}
    geoJsonUrl="/us-states.geojson"
    geoId=region
    value=sales
    colorScale=blues
    title="Sales by Region"
/>

<DataTable
    data={regional_data}
    groupBy=region
    totalRow=true
>
    <Column id=region title="Region" />
    <Column id=sales fmt=usd0 title="Sales" />
    <Column id=orders title="Orders" />
</DataTable>
```

**Drill-Down Navigation**
```markdown
```sql customers
SELECT
    customer_name,
    '/customers/' || customer_id as customer_link,
    SUM(sales) as total_sales
FROM orders
GROUP BY 1, 2
```

<DataTable
    data={customers}
    link=customer_link
    search=true
/>
```

### Component Reference

**Data Components**
- `<Value />` - Inline formatted value
- `<BigValue />` - KPI card with comparison/sparkline
- `<Delta />` - Change indicator
- `<DataTable />` - Rich interactive table

**Chart Components**
- `<LineChart />` - Time series, trends
- `<AreaChart />` - Stacked areas
- `<BarChart />` - Categorical comparison
- `<ScatterPlot />` - Correlation analysis
- `<Histogram />` - Distribution
- `<FunnelChart />` - Conversion flows
- `<SankeyDiagram />` - Flow visualization
- `<Heatmap />` - Matrix visualization

**Input Components**
- `<Dropdown />` - Single/multi select
- `<ButtonGroup />` - Toggle options
- `<Slider />` - Numeric range
- `<DateRange />` - Date selection
- `<TextInput />` - Free text

**Layout Components**
- `<Grid />` - Column layout
- `<Tabs />` - Tabbed content
- `<Accordion />` - Collapsible sections
- `<Modal />` - Popup dialogs

### Formatting Options

**Built-in Formats**
- Currency: `usd`, `usd0`, `usd2`, `eur`, `gbp`
- Numbers: `num0`, `num1`, `num2`, `num0k`, `num1m`
- Percentages: `pct`, `pct0`, `pct1`, `pct2`
- Dates: `shortdate`, `longdate`, `mdy`, `dmy`

**Usage**
```markdown
<Value data={sales} column=revenue fmt=usd2k />
<LineChart data={trend} y=growth yFmt=pct1 />
Revenue: {fmt(data[0].revenue, 'usd0')}
```

**SQL Format Tags**
```sql
SELECT
    revenue as revenue_usd,
    growth as growth_pct,
    date as date_shortdate
FROM summary
```

### Best Practices

**Query Organization**
- Name queries descriptively: `orders_by_month`, `customer_summary`
- Use query chaining to avoid duplication
- Store reusable queries in `/queries`
- Apply format tags to columns

**Page Structure**
- Start with KPIs/summary metrics
- Follow with charts for trends
- End with detailed data tables
- Use Grid for responsive layouts

**Performance**
- Pre-aggregate in source queries
- Keep page queries under 100K rows
- Sort source data by filtered columns
- Use pagination for large tables

**Interactivity**
- Provide sensible defaults for inputs
- Add "All" options for dropdowns
- Use multi-select for flexible filtering
- Connect multiple components to same input

### Anti-Patterns to Avoid

❌ **Hard-coding Data**
Always use SQL queries for data, not hardcoded values.

❌ **Unformatted Values**
```markdown
<!-- Bad -->
Revenue: {data[0].revenue}

<!-- Good -->
Revenue: <Value data={data} column=revenue fmt=usd0 />
```

❌ **Missing Query Names**
```markdown
<!-- Bad - renders as code block -->
```sql
SELECT * FROM orders
```

<!-- Good -->
```sql orders
SELECT * FROM orders
```
```

❌ **Over-fetching Data**
```sql
-- Bad: fetching all columns
SELECT * FROM large_table

-- Good: select only needed columns
SELECT id, name, amount FROM large_table
```

❌ **No Error Handling**
```markdown
<!-- Add conditionals for empty data -->
{#if data.length > 0}
    <DataTable data={data} />
{:else}
    No data available.
{/if}
```

❌ **Ignoring Responsiveness**
Use Grid component for multi-column layouts that adapt to screen size.

### Data Source Configuration

**PostgreSQL**
```yaml
# sources/postgres_db/connection.yaml
name: postgres_db
type: postgres
options:
  host: example.myhost.com
  port: 5432
  database: mydatabase
  ssl: no-verify
```

**BigQuery**
Use service account JSON or gcloud CLI authentication.

**CSV Files**
```yaml
name: csv_data
type: csv
options:
  header=true,delim=","
```

**JavaScript/APIs**
```javascript
// sources/api_data/data.js
const response = await fetch('https://api.example.com/data');
const data = await response.json();
export { data };
```

### Deployment

**Commands**
```bash
npm run sources          # Extract data
npm run dev              # Development
npm run build            # Production build
npm run build:strict     # Strict mode
```

**Platforms**
- Evidence Cloud (recommended)
- Netlify, Vercel, Cloudflare Pages
- GitHub Pages, GitLab Pages
- AWS Amplify, Azure Static Apps

**Environment Variables**
```bash
# Source variables
EVIDENCE_VAR__client_id=12345

# Page variables
VITE_APP_NAME=MyDashboard
```

### Debugging Checklist

When user reports issues:

1. **Query Not Working**
   - Check query name is provided
   - Verify column names match
   - Check for SQL syntax errors
   - Ensure source data is refreshed

2. **Component Not Rendering**
   - Verify data binding: `data={query_name}`
   - Check column names in props
   - Ensure query returns data
   - Check browser console for errors

3. **Filtering Not Working**
   - Verify input name matches: `inputs.name.value`
   - Check quotes in SQL (single for string, none for multi-select IN)
   - Ensure dropdown has data
   - Verify default value exists

4. **Performance Issues**
   - Check row count (< 100K per page)
   - Pre-aggregate in source queries
   - Sort by filtered columns
   - Use pagination

5. **Templated Page Issues**
   - Ensure links point to page
   - Check params spelling
   - Verify parameter in filename matches usage

## Response Guidelines

When helping users:

1. **Understand Context**
   - Ask about their use case (dashboard, report, embedded?)
   - Data sources and volume
   - Level of interactivity needed
   - Deployment target

2. **Provide Complete Examples**
   - Include full page with frontmatter
   - Show SQL queries with names
   - Demonstrate component usage
   - Include formatting

3. **Explain Choices**
   - Why certain components
   - Query optimization decisions
   - Layout considerations
   - Interactivity patterns

4. **Reference Best Practices**
   - Link to concepts from knowledge base
   - Suggest performance optimizations
   - Recommend formatting standards
   - Warn about anti-patterns

5. **Consider Production**
   - Error handling for empty data
   - Responsive layouts
   - Clear labeling and titles
   - User-friendly defaults

## Example Interactions

**User: "How do I create a sales dashboard?"**

Response should include:
- Complete page with frontmatter
- KPI section with BigValue
- Trend chart with LineChart
- Breakdown table with DataTable
- Grid layout for responsiveness
- Proper formatting on all values

**User: "How do I add filtering?"**

Response should:
- Show Dropdown component setup
- SQL query for options
- Parameterized query for filtered data
- Multiple components using same filter
- Default value handling

**User: "My chart isn't showing data"**

Response should:
- Check query name exists
- Verify data binding syntax
- Check column names match
- Suggest adding conditional for empty data
- Recommend browser console check

**User: "How do I create customer detail pages?"**

Response should:
- Explain templated pages with `[customer].md`
- Show params usage in title and queries
- Demonstrate link generation
- Include DataTable with link column
- Show each loop alternative

## Resources

When users need more information:
- Official Docs: https://docs.evidence.dev
- Website: https://evidence.dev
- GitHub: https://github.com/evidence-dev/evidence
- VS Code Extension: https://github.com/evidence-dev/evidence-vscode
- Slack Community: https://slack.evidence.dev

## Your Approach

Be:
- **Practical**: Provide working, complete examples
- **Visual**: Think about data presentation
- **User-Focused**: Consider the end-user experience
- **Performance-Aware**: Optimize queries and components
- **Complete**: Include formatting, titles, error handling

Avoid:
- Incomplete examples missing query names
- Unformatted numeric values
- Missing error handling for empty states
- Overly complex solutions
- Ignoring responsive design

## Ready to Help

You have deep knowledge of:
- Evidence.dev architecture and patterns
- SQL query optimization for DuckDB
- Component selection and configuration
- Interactive features and templated pages
- Data source setup and management
- Deployment and production best practices
- Formatting and styling options

Use the evidence-llms.txt file in the repository for detailed reference when needed.


> Source: `docs/data_engineering/evidence/evidence-dev-component-reference.md`

# Evidence.dev Component System Reference

A comprehensive technical reference for Evidence.dev's component system, including all available components, their props, data binding patterns, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [Data Binding Fundamentals](#data-binding-fundamentals)
3. [Data Components](#data-components)
4. [Chart Components](#chart-components)
5. [Map Components](#map-components)
6. [Input Components](#input-components)
7. [UI Components](#ui-components)
8. [Custom Components](#custom-components)
9. [Formatting Options](#formatting-options)
10. [Theming & Styling](#theming--styling)
11. [Advanced Patterns](#advanced-patterns)

---

## Overview

Evidence is an open-source framework for building data products with SQL and Markdown. It uses:
- **ECharts** for charts
- **Leaflet** for maps
- **Shadcn** for UI components
- **Tailwind CSS** for styling
- **DuckDB** for SQL query execution

### Component Syntax

Components use angle bracket syntax similar to HTML:

```svelte
<ComponentName prop1=value prop2={expression} />
```

### Key Conventions

- **Query references**: Use curly braces `{query_name}`
- **String values**: Can omit quotes for simple values
- **Boolean props**: `prop=true` or just `prop`
- **Arrays/Objects**: Use curly braces `{['a', 'b']}`

---

## Data Binding Fundamentals

### Defining SQL Queries

Queries are defined in markdown code fences with a name:

```sql query_name
SELECT category, SUM(sales) as sales
FROM orders
GROUP BY 1
```

### Referencing Query Results

Pass query results to components using the `data` prop:

```svelte
<LineChart data={query_name} />
```

### Query Chaining

Reference other queries within SQL using `${}` syntax:

```sql derived_query
SELECT AVG(sales) as avg_sales
FROM ${query_name}
```

### Input Parameters

Filter queries dynamically with input values:

```sql filtered_query
SELECT * FROM orders
WHERE category = '${inputs.category_dropdown.value}'
```

### URL Parameters

Use templated page parameters:

```sql parameterized_query
SELECT * FROM orders
WHERE region = '${params.region}'
```

### SQL File Queries

Store reusable queries in `/queries/` directory and reference in frontmatter:

```yaml
---
queries:
  - sales_data: my_query.sql
---
```

### JavaScript Expressions

Access data in markdown using curly braces:

```markdown
Total orders: {orders.length}
First value: {orders_by_month[0].sales}
Sum: {orders.reduce((a, b) => a + b.sales, 0)}
```

### Loops

Iterate through data:

```svelte
{#each orders_by_month as month}
- Sales: <Value data={month} column=sales />
{/each}
```

### Conditionals

Control display based on data:

```svelte
{#if orders[0].sales > 1000}
  Sales exceeded target!
{:else}
  Below target.
{/if}
```

---

## Data Components

### Value

Display a formatted value inline in text.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Query name in curly braces |
| `column` | string | first column | Column to display |
| `row` | number | 0 | Zero-indexed row number |
| `fmt` | string | - | Value format |
| `agg` | string | - | Aggregation: sum, avg, min, median, max |
| `color` | string | - | Font color (CSS/hex/RGB/HSL) |
| `redNegatives` | boolean | false | Color negative values red |
| `placeholder` | string | - | Text when data unavailable |
| `emptySet` | string | error | error, warn, pass |
| `emptyMessage` | string | "No records" | Message for empty data |
| `description` | string | - | Tooltip text |

#### Examples

```svelte
<!-- Basic usage -->
Total sales: <Value data={sales} column=total fmt=usd />

<!-- With aggregation -->
Average: <Value data={orders} column=amount agg=avg fmt=usd0 />

<!-- Colored value -->
<Value data={sales} column=growth color="#85BB65" />
```

---

### BigValue

Display a large value with optional comparison and sparkline.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Query name |
| `value` | string | required | Column for main value |
| `title` | string | column name | Card heading |
| `fmt` | string | - | Value format |
| `minWidth` | string | - | Minimum width (e.g., "18%") |
| `maxWidth` | string | - | Maximum width |
| `link` | string | - | Navigation URL |
| `description` | string | - | Tooltip text |

**Comparison Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `comparison` | string | - | Column for comparison value |
| `comparisonFmt` | string | - | Comparison format |
| `comparisonTitle` | string | - | Comparison label |
| `comparisonDelta` | boolean | - | Show as delta |
| `downIsGood` | boolean | false | Invert color coding |
| `neutralMin` | number | 0 | Neutral range minimum |
| `neutralMax` | number | 0 | Neutral range maximum |

**Sparkline Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `sparkline` | string | - | Column for sparkline x-axis |
| `sparklineType` | string | line | line, area, bar |
| `sparklineColor` | string | - | Sparkline color |
| `sparklineYScale` | boolean | false | Truncate y-axis |

#### Examples

```svelte
<!-- Basic BigValue -->
<BigValue
  data={sales_summary}
  value=total_sales
  title="Total Sales"
  fmt=usd0
/>

<!-- With comparison -->
<BigValue
  data={sales_comparison}
  value=current_sales
  comparison=growth
  comparisonFmt=pct1
  comparisonTitle="vs. Last Month"
  comparisonDelta=true
/>

<!-- With sparkline -->
<BigValue
  data={sales_trend}
  value=total
  sparkline=month
  sparklineType="area"
/>
```

---

### Delta

Display an inline indicator showing value change.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | - | Query name |
| `column` | string | first | Column to display |
| `row` | number | 0 | Row index |
| `value` | number | - | Direct value (override data) |
| `fmt` | string | - | Value format |
| `downIsGood` | boolean | false | Invert colors |
| `showSymbol` | boolean | true | Show arrow |
| `showValue` | boolean | true | Show number |
| `text` | string | - | Text after value |
| `neutralMin` | number | - | Neutral range min |
| `neutralMax` | number | - | Neutral range max |
| `chip` | boolean | false | Badge style |
| `symbolPosition` | string | right | left or right |

#### Examples

```svelte
<!-- Basic delta -->
<Delta data={growth} column=percent fmt=pct1 />

<!-- With text -->
<Delta data={growth} column=change text="vs last month" />

<!-- Chip style -->
<Delta data={growth} column=percent chip=true />

<!-- Inverted colors -->
<Delta data={costs} column=change downIsGood=true />
```

---

### DataTable

Display a richly formatted, interactive data table.

#### DataTable Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Query name |
| `rows` | number/string | 10 | Rows before pagination (use "all" for all) |
| `title` | string | - | Table title |
| `subtitle` | string | - | Subtitle |

**Styling:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `headerColor` | string | - | Header background |
| `headerFontColor` | string | - | Header text color |
| `backgroundColor` | string | - | Table background |
| `rowShading` | boolean | false | Alternating row colors |
| `rowLines` | boolean | true | Row borders |
| `rowNumbers` | boolean | false | Show row index |
| `compact` | boolean | false | Compact layout |
| `wrapTitles` | boolean | false | Wrap column titles |

**Functionality:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `sortable` | boolean | true | Enable sorting |
| `sort` | string | - | Initial sort ("column asc/desc") |
| `search` | boolean | false | Add search bar |
| `downloadable` | boolean | true | Enable download |
| `link` | string | - | Column for row links |
| `showLinkCol` | boolean | false | Display link column |

**Totals & Grouping:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `totalRow` | boolean | false | Show totals |
| `totalRowColor` | string | - | Total row background |
| `groupBy` | string | - | Grouping column |
| `groupType` | string | accordion | accordion or section |
| `subtotals` | boolean | false | Show group totals |

#### Column Component Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | string | required | Column identifier |
| `title` | string | - | Override header |
| `description` | string | - | Tooltip text |
| `align` | string | left | left, center, right |
| `wrap` | boolean | false | Wrap text |
| `fmt` | string | - | Format code |
| `redNegatives` | boolean | false | Color negatives red |
| `totalAgg` | string | - | Aggregation function |
| `contentType` | string | - | Special rendering |

**Content Types:**
- `link` - Clickable links
- `image` - Display images
- `delta` - Delta indicators
- `colorscale` - Background color scale
- `html` - Raw HTML
- `sparkline`, `sparkarea`, `sparkbar` - Inline charts
- `bar` - Bar chart in cell

#### Examples

```svelte
<!-- Basic table -->
<DataTable data={orders} search=true />

<!-- Customized table -->
<DataTable
  data={sales}
  rows=20
  totalRow=true
  rowShading=true
  search=true
>
  <Column id=product title="Product Name" />
  <Column id=sales fmt=usd totalAgg=sum />
  <Column id=growth contentType=delta />
  <Column id=trend contentType=sparkline sparkY=values />
</DataTable>

<!-- Grouped table -->
<DataTable
  data={orders}
  groupBy=category
  subtotals=true
/>
```

---

## Chart Components

### Common Chart Props

Most charts share these props:

**Data Props:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Query name |
| `x` | string | first column | X-axis column |
| `y` | string/array | numeric columns | Y-axis column(s) |
| `series` | string | - | Multi-series grouping |
| `sort` | boolean | true | Apply sorting |
| `emptySet` | string | error | error, warn, pass |
| `emptyMessage` | string | "No records" | Empty state text |

**Formatting & Styling:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `xFmt`, `yFmt` | string | - | Axis formatting |
| `colorPalette` | array | - | Custom colors |
| `seriesColors` | object | - | Map series to colors |
| `fillOpacity` | number | varies | Transparency (0-1) |

**Axes:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `xAxisTitle`, `yAxisTitle` | string/boolean | - | Axis labels |
| `xGridlines`, `yGridlines` | boolean | varies | Show gridlines |
| `yMin`, `yMax` | number | - | Axis range |
| `yLog` | boolean | false | Logarithmic scale |

**Chart Display:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | string | - | Chart title |
| `subtitle` | string | - | Chart subtitle |
| `legend` | boolean | true | Show legend |
| `chartAreaHeight` | number | 180 | Min height (px) |
| `downloadableData` | boolean | true | CSV download |
| `downloadableImage` | boolean | true | Image download |

**Interactivity:**

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `connectGroup` | string | - | Sync tooltips across charts |
| `echartsOptions` | object | - | Custom ECharts config |
| `seriesOptions` | object | - | Series-level config |

---

### LineChart

Display data as connected lines over a continuous axis.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `y2` | string/array | - | Secondary y-axis |
| `y2SeriesType` | string | line | line, bar, scatter |
| `handleMissing` | string | gap | gap, connect, zero |
| `lineColor` | string | - | Line color |
| `lineOpacity` | number | 1 | Line transparency |
| `lineType` | string | solid | solid, dashed, dotted |
| `lineWidth` | number | 2 | Line thickness |
| `markers` | boolean | false | Show data points |
| `markerShape` | string | circle | Point shape |
| `markerSize` | number | 8 | Point size |
| `labels` | boolean | false | Show value labels |
| `labelPosition` | string | above | above, middle, below |
| `step` | boolean | false | Step line |
| `stepPosition` | string | middle | start, middle, end |

#### Examples

```svelte
<!-- Basic line chart -->
<LineChart
  data={sales_by_month}
  x=month
  y=sales
  title="Monthly Sales"
/>

<!-- Multi-series with markers -->
<LineChart
  data={sales_by_category}
  x=month
  y=sales
  series=category
  markers=true
  yFmt=usd0k
/>

<!-- With secondary axis -->
<LineChart
  data={sales_metrics}
  x=month
  y=revenue
  y2=growth_rate
  y2SeriesType=line
/>

<!-- Styled line -->
<LineChart
  data={trend}
  lineColor="#cf0d06"
  lineType="dashed"
  lineWidth=3
/>
```

---

### AreaChart

Display data as filled areas under lines.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | string | stacked | stacked, stacked100 |
| `handleMissing` | string | gap/zero | Missing value treatment |
| `fillOpacity` | number | 0.7 | Area transparency |
| `line` | boolean | true | Show line on area |

#### Examples

```svelte
<!-- Stacked area -->
<AreaChart
  data={revenue_by_category}
  x=month
  y=revenue
  series=category
/>

<!-- 100% stacked -->
<AreaChart
  data={market_share}
  x=quarter
  y=share
  series=company
  type=stacked100
/>
```

---

### BarChart

Display data as vertical or horizontal bars.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `type` | string | stacked | stacked, grouped, stacked100 |
| `swapXY` | boolean | false | Horizontal bars |
| `fillColor` | string | - | Bar color |
| `outlineWidth` | number | 0 | Border width |
| `outlineColor` | string | - | Border color |
| `labels` | boolean | false | Value labels |
| `labelPosition` | string | varies | inside or outside |
| `stackTotalLabel` | boolean | true | Stacked totals |

#### Examples

```svelte
<!-- Vertical bar chart -->
<BarChart
  data={sales_by_category}
  x=category
  y=sales
  yFmt=usd0k
/>

<!-- Grouped bars -->
<BarChart
  data={quarterly_sales}
  x=quarter
  y=sales
  series=region
  type=grouped
/>

<!-- Horizontal bar chart -->
<BarChart
  data={top_products}
  x=product
  y=sales
  swapXY=true
/>

<!-- With labels -->
<BarChart
  data={sales}
  x=category
  y=amount
  labels=true
  labelPosition=outside
/>
```

---

### ScatterPlot

Display data as individual points.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `tooltipTitle` | string | - | Point identifier in tooltip |
| `shape` | string | circle | circle, emptyCircle, rect, triangle, diamond |
| `pointSize` | number | 10 | Point size |
| `opacity` | number | 0.7 | Point transparency |
| `fillColor` | string | - | Point color |
| `outlineColor` | string | - | Border color |
| `outlineWidth` | number | 0 | Border width |

#### Examples

```svelte
<!-- Basic scatter plot -->
<ScatterPlot
  data={products}
  x=price
  y=sales
  tooltipTitle=name
/>

<!-- With series -->
<ScatterPlot
  data={products}
  x=price
  y=sales
  series=category
  shape=triangle
/>
```

---

### BubbleChart

Scatter plot with size dimension.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | string | required | Column for bubble size |
| `sizeFmt` | string | - | Size value format |
| `scaleTo` | number | - | Maximum bubble size |

#### Examples

```svelte
<BubbleChart
  data={market_data}
  x=gdp
  y=life_expectancy
  size=population
  series=continent
  tooltipTitle=country
/>
```

---

### Histogram

Display distribution of values.

#### Specific Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `x` | string | required | Column to summarize |
| `fillColor` | string | - | Bar color |
| `fillOpacity` | number | 1 | Transparency |

#### Examples

```svelte
<Histogram
  data={orders}
  x=order_value
  title="Order Value Distribution"
/>
```

---

### BoxPlot

Display statistical distribution with quartiles.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Box label column |
| `midpoint` | string | required | Median column |
| `intervalBottom` | string | - | Q1 column |
| `intervalTop` | string | - | Q3 column |
| `min`, `max` | string | - | Whisker columns |
| `confidenceInterval` | string | - | CI column |
| `swapXY` | boolean | false | Horizontal |

#### Examples

```svelte
<BoxPlot
  data={salary_stats}
  name=department
  midpoint=median_salary
  intervalBottom=q1
  intervalTop=q3
  min=min_salary
  max=max_salary
/>
```

---

### Heatmap

Display values in a grid with color intensity.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `x` | string | required | X-axis category |
| `y` | string | required | Y-axis category |
| `value` | string | required | Numeric column |
| `colorScale` | array | - | Gradient colors |
| `cellHeight` | number | 30 | Cell height (px) |
| `valueLabels` | boolean | true | Show values |
| `borders` | boolean | true | Cell borders |
| `nullsZero` | boolean | true | Treat nulls as zero |

#### Examples

```svelte
<Heatmap
  data={sales_matrix}
  x=day
  y=hour
  value=orders
  colorScale={['white', 'red']}
/>
```

---

### CalendarHeatmap

Display values on a calendar layout.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `date` | string | required | Date column |
| `value` | string | required | Numeric column |
| `colorScale` | array | - | Gradient colors |
| `yearLabel` | boolean | true | Show year |
| `monthLabel` | boolean | true | Show month |
| `dayLabel` | boolean | true | Show day |

#### Examples

```svelte
<CalendarHeatmap
  data={daily_commits}
  date=commit_date
  value=commit_count
  title="Git Activity"
/>
```

---

### FunnelChart

Display conversion funnel stages.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `nameCol` | string | required | Stage name column |
| `valueCol` | string | required | Stage value column |
| `labelPosition` | string | inside | left, right, inside |
| `showPercent` | boolean | false | Show percentages |
| `funnelSort` | string | none | none, ascending, descending |
| `funnelAlign` | string | center | left, right, center |

#### Examples

```svelte
<FunnelChart
  data={conversion_funnel}
  nameCol=stage
  valueCol=users
  showPercent=true
/>
```

---

### SankeyDiagram

Display flow between nodes.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `sourceCol` | string | required | Source node column |
| `targetCol` | string | required | Target node column |
| `valueCol` | string | required | Flow value column |
| `orient` | string | horizontal | horizontal, vertical |
| `nodeLabels` | string | full | name, value, full |
| `linkLabels` | string | - | full, value, percent |
| `linkColor` | string | base-content-muted | source, target, gradient |
| `nodeAlign` | string | justify | justify, left, right |

#### Examples

```svelte
<SankeyDiagram
  data={user_flow}
  sourceCol=source
  targetCol=target
  valueCol=users
  linkColor=gradient
/>
```

---

### Sparkline

Compact inline chart for single metrics.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `dateCol` | string | required | X-axis column |
| `valueCol` | string | required | Y-axis column |
| `type` | string | line | line, area, bar |
| `color` | string | - | Chart color |
| `height` | number | 15 | Height (px) |
| `width` | number | 50 | Width (px) |
| `yScale` | boolean | false | Truncate y-axis |
| `interactive` | boolean | true | Enable tooltips |

#### Examples

```svelte
Revenue trend: <Sparkline
  data={monthly_revenue}
  dateCol=month
  valueCol=revenue
  type=area
/>
```

---

### Mixed-Type Charts

Combine multiple chart types on same axes.

#### Usage

```svelte
<Chart data={metrics}>
  <Bar y=revenue />
  <Line y=growth name="Growth Rate" />
</Chart>
```

#### Available Primitives

- `<Bar />` - Bar series
- `<Line />` - Line series
- `<Area />` - Area series
- `<Scatter />` - Scatter points
- `<Bubble />` - Bubble series

---

### Custom ECharts

Access full ECharts feature set.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| `config` | object | ECharts configuration object |

#### Examples

```svelte
<ECharts config={{
  title: { text: 'Custom Chart' },
  tooltip: { formatter: '{b}: {c}' },
  series: [{
    type: 'treemap',
    data: [...query_data]
  }]
}} />
```

---

### Annotations

Add context to charts with reference elements.

#### ReferenceLine

Draw lines on charts (targets, dates, regression).

| Prop | Type | Description |
|------|------|-------------|
| `x`, `y` | number/string | Line position |
| `x2`, `y2` | number/string | End position (sloped) |
| `label` | string | Line label |
| `data` | query | Data-driven lines |
| `color` | string | Line color |
| `lineType` | string | solid, dashed, dotted |
| `lineWidth` | number | Thickness (default: 1.3) |
| `labelPosition` | string | Position options |

```svelte
<LineChart data={sales} x=month y=revenue>
  <ReferenceLine y=10000 label="Target" color=positive />
  <ReferenceLine x='2024-01-01' label="Launch" />
</LineChart>
```

#### ReferenceArea

Highlight regions on charts.

| Prop | Type | Description |
|------|------|-------------|
| `xMin`, `xMax` | number/string | X-axis range |
| `yMin`, `yMax` | number/string | Y-axis range |
| `label` | string | Area label |
| `color` | string | Fill color |
| `opacity` | number | Transparency |
| `border` | boolean | Show border |

```svelte
<LineChart data={sales} x=month y=revenue>
  <ReferenceArea
    xMin='2024-03-01'
    xMax='2024-06-01'
    label="Q2"
    color=warning
  />
</LineChart>
```

#### ReferencePoint

Highlight specific points.

| Prop | Type | Description |
|------|------|-------------|
| `x`, `y` | number/string | Point coordinates |
| `label` | string | Point label |
| `symbol` | string | Point shape |
| `symbolSize` | number | Shape size |

```svelte
<LineChart data={sales} x=month y=revenue>
  <ReferencePoint
    x='2024-05-01'
    y=15000
    label="Record High"
  />
</LineChart>
```

#### Callout

Draw attention with descriptive labels.

```svelte
<LineChart data={sales} x=month y=revenue>
  <Callout x='2024-02-01' y=8000 labelPosition=bottom>
    Seasonal dip due to
    holiday period
  </Callout>
</LineChart>
```

---

## Map Components

### Common Map Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title`, `subtitle` | string | - | Map labels |
| `height` | number | 300 | Height (px) |
| `legend` | boolean | true | Show legend |
| `legendPosition` | string | bottomLeft | Legend placement |
| `basemap` | string | - | Custom tile URL |
| `startingLat`, `startingLong` | number | - | Initial center |
| `startingZoom` | number | - | Initial zoom (1-18) |

---

### PointMap

Display points at lat/long coordinates.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `lat` | string | required | Latitude column |
| `long` | string | required | Longitude column |
| `pointName` | string | - | Point label column |
| `value` | string | - | Value column |
| `color` | string | - | Point color |
| `size` | number | 5 | Point size |
| `opacity` | number | - | Transparency |
| `colorPalette` | array | - | Gradient colors |
| `link` | string | - | Click URL column |
| `name` | string | - | Input name for selection |
| `tooltipType` | string | hover | hover or click |

#### Examples

```svelte
<PointMap
  data={store_locations}
  lat=latitude
  long=longitude
  pointName=store_name
  value=sales
  valueFmt=usd
  colorPalette={['blue', 'red']}
/>
```

---

### BubbleMap

Points with size dimension.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `lat`, `long` | string | required | Coordinates |
| `size` | string | required | Size column |
| `sizeFmt` | string | - | Size format |
| `maxSize` | number | 20 | Max bubble size |
| `value` | string | - | Color scale column |

#### Examples

```svelte
<BubbleMap
  data={cities}
  lat=lat
  long=lng
  size=population
  value=gdp_per_capita
  pointName=city_name
/>
```

---

### AreaMap

Choropleth map with GeoJSON regions.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `geoJsonUrl` | string | required | GeoJSON source |
| `areaCol` | string | required | Data area column |
| `geoId` | string | required | GeoJSON ID property |
| `value` | string | - | Color value column |
| `color` | string | - | Uniform color |
| `colorPalette` | array | - | Color gradient |
| `borderWidth` | number | 0.75 | Border thickness |
| `opacity` | number | 0.8 | Fill transparency |

#### Examples

```svelte
<AreaMap
  data={state_sales}
  geoJsonUrl='https://example.com/states.geojson'
  geoId=STATE_ID
  areaCol=state_code
  value=total_sales
  valueFmt=usd
/>
```

---

### USMap

Simplified US state choropleth.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `state` | string | required | State name column |
| `value` | string | required | Value column |
| `abbreviations` | boolean | false | Use state codes |
| `colorScale` | string | info | info, positive, negative |
| `colorPalette` | array | - | Custom colors |
| `filter` | boolean | false | Filterable legend |

#### Examples

```svelte
<USMap
  data={state_population}
  state=state_name
  value=population
  colorScale=positive
  fmt=num0
/>
```

---

## Input Components

### Dropdown

Single or multi-select dropdown menu.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `data` | query | required | Options query |
| `value` | string | required | Value column |
| `label` | string | value | Display column |
| `multiple` | boolean | false | Multi-select |
| `defaultValue` | string/array | - | Initial selection |
| `selectAllByDefault` | boolean | false | Select all initially |
| `noDefault` | boolean | false | No default selection |
| `title` | string | - | Dropdown label |
| `order` | string | - | Sort column |
| `where` | string | - | Filter clause |
| `disableSelectAll` | boolean | false | Hide select all |

#### Examples

```svelte
<!-- Single select -->
<Dropdown
  name=category
  data={categories}
  value=category_id
  label=category_name
  title="Select Category"
/>

<!-- Multi-select -->
<Dropdown
  name=regions
  data={regions}
  value=region_code
  multiple=true
  defaultValue={['US', 'CA']}
/>

<!-- Use in query -->
```sql
SELECT * FROM orders
WHERE category_id = '${inputs.category.value}'
```

#### DropdownOption

Hardcoded options:

```svelte
<Dropdown name=status>
  <DropdownOption value="active" valueLabel="Active" />
  <DropdownOption value="inactive" valueLabel="Inactive" />
</Dropdown>
```

---

### ButtonGroup

Toggle button selection.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `data` | query | - | Options query |
| `value` | string | - | Value column |
| `label` | string | value | Display column |
| `defaultValue` | string | - | Initial selection |
| `display` | string | buttons | buttons or tabs |
| `title` | string | - | Group label |
| `order` | string | - | Sort column |
| `where` | string | - | Filter clause |

#### Examples

```svelte
<ButtonGroup
  name=time_period
  data={periods}
  value=period_id
  label=period_name
  defaultValue="monthly"
/>

<!-- Tab style -->
<ButtonGroup
  name=view
  display=tabs
>
  <ButtonGroupItem value="chart" valueLabel="Chart View" default />
  <ButtonGroupItem value="table" valueLabel="Table View" />
</ButtonGroup>
```

---

### Slider

Numeric range slider.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `defaultValue` | number | - | Initial value |
| `min` | number | 0 | Minimum |
| `max` | number | 100 | Maximum |
| `step` | number | 1 | Increment |
| `size` | string | small | small, medium, large, full |
| `fmt` | string | - | Value format |
| `showMinMax` | boolean | true | Show range markers |
| `showInput` | boolean | false | Show input field |
| `data` | query | - | Data-driven range |
| `range` | string | - | Column for auto min/max |

#### Examples

```svelte
<Slider
  name=price_filter
  title="Max Price"
  min=0
  max=1000
  step=50
  fmt=usd0
/>

<!-- Data-driven range -->
<Slider
  name=date_slider
  data={orders}
  range=order_value
  size=large
/>
```

---

### DateInput / DateRange

Date selection with presets.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `data` | query | - | Date data source |
| `dates` | string | - | Date column |
| `range` | boolean | false | Enable range selection |
| `start`, `end` | string | - | Default dates (YYYY-MM-DD) |
| `title` | string | - | Component label |
| `presetRanges` | array | - | Available presets |
| `defaultValue` | string | - | Initial preset |

**Available Presets:**
- `'Last 7 Days'`, `'Last 30 Days'`, `'Last 90 Days'`
- `'Last 3 Months'`, `'Last 6 Months'`, `'Last 12 Months'`
- `'Last Month'`, `'Last Year'`
- `'Month to Date'`, `'Year to Date'`, `'All Time'`

#### Examples

```svelte
<!-- Date range picker -->
<DateRange
  name=date_filter
  data={orders}
  dates=order_date
  title="Order Date"
  presetRanges={['Last 30 Days', 'Last 90 Days', 'Year to Date']}
  defaultValue='Last 30 Days'
/>

<!-- Reference in query -->
```sql
SELECT * FROM orders
WHERE order_date BETWEEN '${inputs.date_filter.start}'
  AND '${inputs.date_filter.end}'
```

---

### TextInput

Free text entry.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `title` | string | - | Input label |
| `placeholder` | string | "Type to search" | Placeholder text |
| `defaultValue` | string | - | Initial value |

#### Examples

```svelte
<TextInput
  name=search
  title="Search Products"
  placeholder="Enter product name"
/>

<!-- Fuzzy search -->
{inputs.search.search('product_name')}
```

---

### Checkbox

Boolean toggle.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `name` | string | required | Input identifier |
| `title` | string | - | Checkbox label |
| `checked` | boolean | false | Initial state |

#### Examples

```svelte
<Checkbox
  name=include_inactive
  title="Include Inactive Products"
/>

<!-- Use in query -->
```sql
SELECT * FROM products
WHERE is_active = true
  OR ${inputs.include_inactive.value} = true
```

---

### DimensionGrid

Multi-dimensional selector.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Data source |
| `metric` | string | - | Aggregation expression |
| `name` | string | - | Input identifier |
| `title`, `subtitle` | string | - | Labels |
| `metricLabel` | string | - | Metric column label |
| `fmt` | string | - | Value format |
| `limit` | number | - | Rows per dimension |
| `multiple` | boolean | false | Multi-select |

#### Examples

```svelte
<DimensionGrid
  data={orders}
  metric='sum(sales)'
  name=dimension_filter
  multiple=true
/>
```

---

## UI Components

### Grid

Layout components in columns.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `cols` | number | 2 | Columns (1-6) |
| `gapSize` | string | md | none, sm, md, lg |

#### Examples

```svelte
<Grid cols=3>
  <BigValue data={metrics} value=revenue />
  <BigValue data={metrics} value=orders />
  <BigValue data={metrics} value=customers />
</Grid>

<!-- Group items in single cell -->
<Grid cols=2>
  <LineChart data={trend} />
  <Group>
    <BarChart data={breakdown} />
    <DataTable data={details} />
  </Group>
</Grid>
```

---

### Tabs

Tabbed content sections.

#### Tabs Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | string | - | URL-shareable tab state |
| `color` | string | base-content | Tab indicator color |
| `fullWidth` | boolean | false | Full width tabs |
| `background` | boolean | false | Background on active |

#### Tab Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | string | required | Tab label |
| `id` | string | - | Tab identifier |
| `printShowAll` | boolean | true | Show in print |

#### Examples

```svelte
<Tabs id="analysis-tabs">
  <Tab label="Overview">
    <LineChart data={overview} />
  </Tab>
  <Tab label="Details">
    <DataTable data={details} />
  </Tab>
</Tabs>
```

---

### Modal

Popup dialog with content.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `buttonText` | string | required | Trigger button text |
| `title` | string | - | Modal title |
| `open` | boolean | false | Initially open |

#### Examples

```svelte
<Modal buttonText="View Details" title="Sales Details">
  <DataTable data={sales_details} />
</Modal>
```

---

### Accordion

Collapsible content sections.

#### Accordion Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `single` | boolean | false | Only one open |
| `class` | string | - | Tailwind classes |

#### AccordionItem Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | string | required | Item header |
| `class` | string | - | Tailwind classes |

#### Examples

```svelte
<Accordion single>
  <AccordionItem title="Revenue Analysis">
    <LineChart data={revenue} />
  </AccordionItem>
  <AccordionItem title="Cost Breakdown">
    <BarChart data={costs} />
  </AccordionItem>
</Accordion>
```

---

### Details

Collapsible section with disclosure.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | string | "Details" | Section label |
| `open` | boolean | false | Initially expanded |
| `printShowAll` | boolean | true | Expand in print |

#### Examples

```svelte
<Details title="Methodology">
  This analysis uses...
</Details>
```

---

### Alert

Styled message container.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `status` | string | - | info, positive, warning, negative |

#### Examples

```svelte
<Alert status="warning">
  Data is 24 hours delayed.
</Alert>

<Alert status="positive">
  Report updated successfully!
</Alert>
```

---

### LinkButton / BigLink

Navigation buttons and links.

#### Props

| Prop | Type | Description |
|------|------|-------------|
| `url` | string | Navigation destination |

#### Examples

```svelte
<LinkButton url="/reports/sales">
  View Sales Report
</LinkButton>

<BigLink url="/dashboard">
  Go to Dashboard
</BigLink>
```

---

### LastRefreshed

Display data freshness timestamp.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `prefix` | string | "Last refreshed" | Label text |
| `printShowDate` | boolean | true | Full date in print |
| `dateFmt` | string | - | Date format |

#### Examples

```svelte
<LastRefreshed prefix="Data updated" />
```

---

### DownloadData

CSV download button.

#### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | query | required | Data to download |
| `text` | string | "Download" | Button text |
| `queryID` | string | "evidence_download" | Filename prefix |

#### Examples

```svelte
<DownloadData
  data={sales_report}
  text="Export CSV"
  queryID=sales_export
/>
```

---

## Custom Components

### Creating Custom Components

Store Svelte components in `/components/` directory.

#### Basic Structure

**`/components/SalesCard.svelte`:**

```svelte
<script>
  export let data;
  export let title = "Sales";
  import { BarChart, Value } from '@evidence-dev/core-components';
</script>

<div class="card">
  <h3>{title}</h3>
  <Value data={data} column=total fmt=usd />
  <BarChart data={data} x=category y=amount />
</div>

<style>
  .card { padding: 1rem; border: 1px solid #e5e7eb; }
</style>
```

**Usage in markdown:**

```svelte
<SalesCard data={sales_by_category} title="Q4 Sales" />
```

### Utility Functions

Evidence provides helper functions:

- `checkInputs` - Validate data and columns
- `ErrorChart` - Display error states
- `getDistinctValues` - Extract unique values
- `formatValue` - Apply formatting
- `getSortedData` - Sort datasets

### Component Plugins

Publish reusable components as npm packages for use across projects.

---

## Formatting Options

### Built-in Formats

**Dates:**
- `ddd` - Mon, Tue...
- `dddd` - Monday, Tuesday...
- `mmm` - Jan, Feb...
- `mmmm` - January, February...
- `yyyy` - 2024
- `shortdate` - 1/1/24
- `longdate` - January 1, 2024
- `fulldate` - Monday, January 1, 2024
- `mdy`, `dmy` - Date order variants
- `hms` - Time with seconds

**Currencies:**
- `usd`, `usd0`, `usd1`, `usd2` - US Dollar
- `eur`, `gbp`, `jpy`, `cny`, etc. - Other currencies
- Add `k`, `m`, `b` suffix for thousands/millions/billions
  - `usd0k` - $1K, `usd1m` - $1.5M

**Numbers:**
- `num0` through `num4` - Decimal places
- `num0k`, `num1m`, `num2b` - With magnitude
- `id` - No formatting
- `fract` - Fraction format
- `mult` - Multiplier format
- `sci` - Scientific notation

**Percentages:**
- `pct` - Auto decimals
- `pct0`, `pct1`, `pct2`, `pct3` - Fixed decimals

### Format Usage

**In components:**
```svelte
<Value data={sales} column=revenue fmt=usd0k />
<LineChart data={growth} yFmt=pct1 />
```

**SQL format tags:**
```sql
SELECT
  revenue AS revenue_usd,
  growth AS growth_pct
FROM sales
```

**Format function:**
```markdown
Revenue: {fmt(data[0].revenue, 'usd0k')}
```

### Custom Formats

Define in Evidence settings using Excel-style codes:
```
#,##0.00    - 1,234.56
0.00%       - 12.34%
$#,##0      - $1,234
```

---

## Theming & Styling

### Color Configuration

Define in `evidence.config.yaml`:

```yaml
appearance:
  default: system  # light, dark, system

colors:
  primary: '#3b82f6'
  secondary: '#6b7280'

colorPalettes:
  default: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
  custom:
    light: ['#bfdbfe', '#93c5fd', '#60a5fa']
    dark: ['#1e40af', '#1d4ed8', '#2563eb']
```

### Using Colors

**In components:**
```svelte
<LineChart
  data={sales}
  colorPalette={['#cf0d06', '#eb5752', '#e88a87']}
/>

<BarChart
  data={sales}
  seriesColors={{'North': '#3b82f6', 'South': '#ef4444'}}
/>
```

### Tailwind CSS

Evidence uses Tailwind for styling:

```svelte
<div class="p-4 bg-gray-100 rounded-lg">
  <h2 class="text-xl font-bold text-gray-800">Title</h2>
</div>
```

Apply markdown styling to HTML:
```svelte
<h1 class="markdown">Styled Heading</h1>
```

### Layout Customization

Create `/pages/+layout.svelte`:

```svelte
<script>
  import { EvidenceDefaultLayout } from '@evidence-dev/core-components';
</script>

<EvidenceDefaultLayout
  title="My App"
  logo="/logo.png"
  fullWidth={false}
  maxWidth={1400}
  hideSidebar={false}
  hideHeader={false}
/>
```

---

## Advanced Patterns

### Interactive Filtering

```svelte
<!-- Input -->
<Dropdown
  name=category
  data={categories}
  value=id
  label=name
/>

<!-- Filtered query -->
```sql filtered_sales
SELECT * FROM sales
WHERE category_id = '${inputs.category.value}'
```

<!-- Chart updates automatically -->
<LineChart data={filtered_sales} x=date y=amount />
```

### Synchronized Charts

```svelte
<Grid cols=2>
  <LineChart
    data={revenue}
    connectGroup="sales"
  />
  <BarChart
    data={orders}
    connectGroup="sales"
  />
</Grid>
```

### Conditional Rendering

```svelte
{#if sales[0].total > 100000}
  <Alert status="positive">
    Sales target exceeded!
  </Alert>
{:else}
  <Alert status="warning">
    Below target
  </Alert>
{/if}
```

### Dynamic Components

```svelte
{#each regions as region}
  <BigValue
    data={region}
    value=sales
    title={region.name}
  />
{/each}
```

### Parameterized Pages

Create `/pages/products/[product_id].md`:

```sql product_details
SELECT * FROM products
WHERE id = '${params.product_id}'
```

### Component Composition

```svelte
<Grid cols=3>
  <Group>
    <BigValue data={kpis} value=revenue title="Revenue" />
    <Sparkline data={trend} dateCol=date valueCol=revenue />
  </Group>

  <BigValue data={kpis} value=orders title="Orders" />

  <BigValue
    data={kpis}
    value=customers
    comparison=customer_growth
    comparisonDelta=true
  />
</Grid>

<Tabs>
  <Tab label="Charts">
    <LineChart data={monthly} x=month y=revenue />
  </Tab>
  <Tab label="Data">
    <DataTable data={monthly} search=true />
  </Tab>
</Tabs>
```

---

## Quick Reference

### Most Common Components

| Component | Primary Use |
|-----------|-------------|
| `<Value>` | Inline formatted value |
| `<BigValue>` | KPI display |
| `<DataTable>` | Data grid |
| `<LineChart>` | Time series |
| `<BarChart>` | Comparisons |
| `<Dropdown>` | Selection filter |
| `<Grid>` | Layout |
| `<Tabs>` | Content organization |

### Data Binding Syntax

| Pattern | Syntax |
|---------|--------|
| Query result | `data={query_name}` |
| Input value | `${inputs.name.value}` |
| URL parameter | `${params.name}` |
| JavaScript | `{expression}` |
| Loop | `{#each data as item}...{/each}` |
| Conditional | `{#if condition}...{:else}...{/if}` |

### Format Shortcuts

| Format | Example Output |
|--------|----------------|
| `usd0` | $1,234 |
| `usd1k` | $1.2K |
| `pct1` | 12.3% |
| `num0` | 1,234 |
| `shortdate` | 1/15/24 |

---

## Resources

- **Documentation**: https://docs.evidence.dev/
- **Components**: https://docs.evidence.dev/components/all-components
- **GitHub**: https://github.com/evidence-dev/evidence
- **Examples**: https://evidence.dev/examples


## Streaming & Replication — Kafka


> Source: `docs/data_engineering/kafka/Kafka Topic Mirroring _ Bento _ Fancy stream processing made operationally mundane.md`

---
title: "Kafka Topic Mirroring | Bento | Fancy stream processing made operationally mundane"
source: "https://warpstreamlabs.github.io/bento/cookbooks/kafka-mirroring"
author:
published:
created: 2025-12-30
description: "Learn how to mirror Kafka topics while preserving partition mapping."
tags:
  - "clippings"
---
Kafka-flavoured Bento (カフカ風弁当; Kafuka-fū Bentō), a favourite here at WarpStream Labs, is a quick-and-easy recipe you can whip up in minutes. This cookbook will illustrate how to use Bento for consuming and publishing events to Kafka, with the goal of **mirroring Kafka topics while preserving partition mappings**.

For example, the diagram below shows *partition preservation* of some process where `bento` consumes an event from `Partition 2` of `Topic A` and maps it to `Partition 2` of `Topic B`:

```markdown
Topic A                                                                  Topic B                       
+-----------------------------+                                          +-----------------------------+
|                             |                                          |                             |
|    +--------------------+   |                                          |   +--------------------+    |
| P1 |                    |   |                                          |   |                    | P1 |
|    +--------------------+   |                                          |   +--------------------+    |
|                             |       +--------------------------+       |                             |
|    +--------------------+   |       |                          |       |   +--------------------+    |
| P2 |                    |---------->|          bento           |---------->|                    | P2 |
|    +--------------------+   |       |                          |       |   +--------------------+    |
|                             |       +--------------------------+       |                             |
|    +--------------------+   |                                          |   +--------------------+    |
| P3 |                    |   |                                          |   |                    | P3 |
|    +--------------------+   |                                          |   +--------------------+    |
|                             |                                          |                             |
+-----------------------------+                                          +-----------------------------+
```

## Consuming Events

To start consuming data, we can use the [`kafka_franz input`](https://warpstreamlabs.github.io/bento/docs/components/inputs/kafka_franz) component. Here, we will read in all new events from the `foo` and `bar` topics.

```yaml
input:
  kafka_franz:
    consumer_group: bento_bridge_consumer
    seed_brokers: [ TODO ]
    topics: [ foo, bar ]
```

## Publishing Events

We can use the [`kafka_franz output`](https://warpstreamlabs.github.io/bento/docs/components/outputs/kafka_franz) component for publishing messages to a topic. As you'll see, this component is incredibly flexible, with several fields supporting [string interpolation](https://warpstreamlabs.github.io/bento/docs/configuration/interpolation/#bloblang-queries) for dynamic value setting.

Let's route all events received from `foo` and `bar` to some existing topics named `output-foo` and `output-bar`, respectively.

Fortunately, Bento makes this straightforward as the [`kafka_franz input`](https://warpstreamlabs.github.io/bento/docs/components/inputs/kafka_franz) component attaches useful [metadata](https://warpstreamlabs.github.io/bento/docs/components/inputs/kafka_franz/#metadata) to each message, including the source event's `kafka_key`, `kafka_topic`, and `kafka_partition`.

Using [string interpolation](https://warpstreamlabs.github.io/bento/docs/configuration/interpolation/#bloblang-queries), we can then extract the original topic name from the `kafka_topic` metadata field, prepend the `output-` prefix, and pass this as output to the `topic` field -- dynamically setting the topic destinations.

```yaml
output:
  kafka_franz:
    seed_brokers: [ TODO ]
    topic: 'output-${! metadata("kafka_topic") }'
```

Recall from earlier that we also wanted to preserve our partition mapping when writing to new topics. Again, we can use metadata to retrieve the original partition of each message in the source topic. We'll use the `kafka_partition` metadata field in conjunction with setting `partitioner` to `manual` -- overriding any other fancy partitioning algorithm in favour of preserving our initial mapping. Combining again with [string interpolation](https://warpstreamlabs.github.io/bento/docs/configuration/interpolation/#bloblang-queries), we get the following:

```yaml
output:
  kafka_franz:
    seed_brokers: [ TODO ]
    topic: 'output-${! metadata("kafka_topic") }'
    partition: ${! metadata("kafka_partition") }
    partitioner: manual
```

Voilà! The above config:

- Consumes events from the `foo` and `bar` topics
- Routes the output destination of events from `foo` to `output-foo` and from `bar` to `output-bar` using the `kafka_topic` metadata field
- Explicitly sets the message partition to that of the source message using the metadata field `kafka_partition`

For completeness, we can also route all consumed events back to their original source topic and partition.

```yaml
output:
  kafka_franz:
    seed_brokers: [ TODO ]
    topic: ${! metadata("kafka_topic") }
    partition: ${! metadata("kafka_partition") }
    partitioner: manual
```

## Regular Expression Matching

We begin by consuming from 2 topics: `foobar` and `foobaz`.

```yaml
input:
  kafka_franz:
    consumer_group: bento_bridge_consumer
    seed_brokers: [ TODO ]
    topics: [ foobar, foobaz ]
```

Notice that both topics share a common prefix of `foo`. It's easy to imagine a large or variable amount of topics needing to be consumed by the input. Luckily, we have tools for that as the [`kafka_franz input`](https://warpstreamlabs.github.io/bento/docs/components/inputs/kafka_franz) also has [regular expression](https://warpstreamlabs.github.io/bento/docs/components/inputs/kafka_franz#regexp_topics) matching capabilities.

Include your topics pattern as regex and include `regexp_topics: true` so that listed topics are interpreted as regex.

```yaml
input:
  kafka_franz:
    consumer_group: bento_bridge_consumer
    seed_brokers: [ TODO ]
    topics: [ foo.* ]
    regexp_topics: true
```

Now Bento will consume events from all topics with the prefix `foo`.

## Final Words

Wow, you're a natural, aren't you?

In this cookbook, we've explored how to use Bento to mirror Kafka topics while preserving partition mappings. We've covered:

- Consuming events from Kafka topics
- Publishing events to dynamically determined topics
- Preserving partition information when writing to new topics
- Regular expressions for matching and consuming from many topics

If you have any more questions, come [join our Discord!](https://console.warpstream.com/socials/discord)

Otherwise, happy streaming!

[Find more cookbooks](https://warpstreamlabs.github.io/bento/cookbooks)

## Streaming & Replication — RisingWave


> Source: `docs/data_engineering/risingwave/risingwave.md`

---
name: RisingWave Streaming Database Assistant
description: Expert assistant for RisingWave streaming database - helps with SQL patterns, stream processing, CDC pipelines, materialized views, and real-time analytics.
category: Development
tags: [risingwave, streaming, sql, real-time, cdc, materialized-views]
---

# RisingWave Streaming Database Assistant

You are a specialized assistant for RisingWave, the cloud-native streaming database. You have deep knowledge of streaming SQL, materialized views, CDC pipelines, and real-time analytics patterns.

## Your Expertise

You understand:
- **Streaming SQL** - Sources, sinks, materialized views, window functions, temporal joins
- **CDC Pipelines** - PostgreSQL CDC, MySQL CDC, Debezium format, replication patterns
- **Time Processing** - Watermarks, event time, tumbling/hopping/session windows
- **Data Architecture** - Stream-table duality, incremental computation, exactly-once semantics
- **Connectors** - Kafka, Kinesis, Pulsar, S3, PostgreSQL, ClickHouse, Elasticsearch, Iceberg
- **Performance** - Checkpoint tuning, parallelism, caching, index optimization
- **Deployment** - Docker, Kubernetes, RisingWave Cloud, production configuration

## Reference Materials

Always consult this file when needed:
- `/home/user/hackathon/risingwave-llms.txt` - Comprehensive RisingWave documentation

## Your Approach

1. **Understand the Use Case First**
   - Ask clarifying questions about data volume, latency requirements, and downstream consumers
   - Identify if this is analytics, CDC replication, event processing, or feature engineering
   - Understand the source systems and sink destinations

2. **Follow Streaming Best Practices**
   - Always define watermarks for event-time processing
   - Use temporal filters to bound state growth
   - Create indexes on frequently filtered columns
   - Choose appropriate window types for the use case
   - Use `EMIT ON WINDOW CLOSE` when results should only emit once per window

3. **Provide Complete Solutions**
   - Include full SQL with all required clauses
   - Specify connector configurations with all necessary parameters
   - Explain the data flow and processing semantics
   - Consider exactly-once delivery requirements

4. **Performance and Production Considerations**
   - Recommend appropriate parallelism settings
   - Suggest checkpoint intervals based on RPO requirements
   - Identify potential state growth issues
   - Consider downstream system capabilities

## Common Tasks You Can Help With

- **Source Configuration**: "How do I connect to Kafka with Avro and Schema Registry?"
- **CDC Setup**: "How do I replicate PostgreSQL tables to RisingWave?"
- **Materialized Views**: "How do I create a real-time aggregation with sliding windows?"
- **Sink Configuration**: "How do I write results to Iceberg/ClickHouse/Elasticsearch?"
- **Join Patterns**: "How do I join a stream with a slowly changing dimension?"
- **Deduplication**: "How do I deduplicate events by key keeping the latest?"
- **Window Processing**: "How do I calculate metrics over tumbling/hopping windows?"
- **Performance Tuning**: "How do I optimize my streaming job for higher throughput?"
- **Troubleshooting**: "Why is my materialized view not updating?"
- **Migration**: "How do I migrate from Flink/ksqlDB to RisingWave?"

## Quick Reference

### Core SQL Patterns

**Create Source (Kafka)**
```sql
CREATE SOURCE events (
  event_id VARCHAR,
  user_id INT,
  event_time TIMESTAMP,
  payload JSONB,
  WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'
) WITH (
  connector = 'kafka',
  topic = 'events',
  properties.bootstrap.server = 'localhost:9092',
  scan.startup.mode = 'earliest'
) FORMAT PLAIN ENCODE JSON;
```

**Create CDC Table (PostgreSQL)**
```sql
CREATE TABLE orders WITH (
  connector = 'postgres-cdc',
  hostname = 'localhost',
  port = '5432',
  username = 'user',
  password = 'password',
  database.name = 'mydb',
  schema.name = 'public',
  table.name = 'orders',
  slot.name = 'orders_slot'
);
```

**Materialized View with Window**
```sql
CREATE MATERIALIZED VIEW hourly_stats AS
SELECT
  window_start,
  window_end,
  user_id,
  COUNT(*) as event_count,
  SUM(amount) as total
FROM TUMBLE(events, event_time, INTERVAL '1 hour')
GROUP BY window_start, window_end, user_id;
```

**Temporal Join**
```sql
SELECT
  e.event_id,
  e.amount,
  u.name as user_name
FROM events e
JOIN users FOR SYSTEM_TIME AS OF PROCTIME() u
ON e.user_id = u.id;
```

**Create Sink (Kafka)**
```sql
CREATE SINK events_sink FROM mv WITH (
  connector = 'kafka',
  properties.bootstrap.server = 'localhost:9092',
  topic = 'output'
) FORMAT UPSERT ENCODE JSON;
```

### Window Types

| Window | Syntax | Use Case |
|--------|--------|----------|
| Tumbling | `TUMBLE(table, col, size)` | Non-overlapping fixed intervals |
| Hopping | `HOP(table, col, slide, size)` | Overlapping sliding windows |
| Session | `session(col, gap)` | Gap-based grouping (emit-on-close only) |

### Connector Types

**Sources**: kafka, postgres-cdc, mysql-cdc, kinesis, pulsar, nats, mqtt, s3, google_pubsub
**Sinks**: kafka, jdbc, redis, elasticsearch, clickhouse, iceberg, deltalake, bigquery, snowflake

### Key Functions

**Time Functions**
```sql
NOW(), CURRENT_TIMESTAMP
date_trunc('hour', ts)
ts + INTERVAL '1 day'
EXTRACT(HOUR FROM ts)
```

**JSON Functions**
```sql
payload->>'field'           -- Extract as text
payload->'nested'->'field'  -- Navigate nested
jsonb_array_elements(arr)   -- Unnest array
jsonb_build_object(...)     -- Construct object
```

**Aggregate Functions**
```sql
COUNT(*), SUM(), AVG(), MIN(), MAX()
ARRAY_AGG(), STRING_AGG(), JSONB_AGG()
PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY col)
```

**Window Functions**
```sql
ROW_NUMBER() OVER (PARTITION BY key ORDER BY ts)
LAG(col) OVER (PARTITION BY key ORDER BY ts)
SUM(col) OVER (... ROWS BETWEEN 10 PRECEDING AND CURRENT ROW)
```

## Architecture Patterns

### 1. Lambda Architecture Alternative
```
Sources → Materialized Views → Sinks
           (real-time)        (serving)
```

### 2. CDC Replication Pipeline
```
PostgreSQL/MySQL → CDC Source → MV (transform) → Sink (warehouse)
```

### 3. Event Sourcing
```
Event Stream → MV (aggregate) → MV (project) → Sink
```

### 4. Feature Store
```
Raw Events → MV (window agg) → MV (features) → Redis/JDBC Sink
```

## Anti-Patterns to Avoid

1. **Unbounded State** - Always use temporal filters or watermarks
2. **Missing Primary Keys** - Required for upsert sinks
3. **Low-Cardinality Joins** - Add filters before joining
4. **Default Configurations** - Tune checkpoints and parallelism
5. **Skipping Indexes** - They're cost-effective in RisingWave

## Troubleshooting Checklist

### Materialized View Not Updating
- [ ] Check source is receiving data: `SELECT COUNT(*) FROM source`
- [ ] Verify watermark isn't blocking: Check barrier latency
- [ ] Look for temporal filter issues: Is `NOW() - INTERVAL` too restrictive?
- [ ] Check for join issues: Is dimension table empty?

### High Latency
- [ ] Reduce checkpoint interval if RPO allows
- [ ] Increase parallelism: `SET streaming_parallelism = N`
- [ ] Add indexes on join keys
- [ ] Check for backpressure in sinks

### Out of Memory
- [ ] Add temporal filters to bound state
- [ ] Reduce memory cache sizes
- [ ] Increase compactor resources
- [ ] Check for unbounded joins

### Sink Not Producing
- [ ] Verify primary key matches sink requirements
- [ ] Check connector configuration
- [ ] Verify downstream system is accessible
- [ ] Check for serialization errors in logs

## Performance Tuning

### Streaming Parallelism
```sql
SET streaming_parallelism = 4;  -- For next CREATE MV
```

### Checkpoint Configuration
```sql
-- Per database
ALTER DATABASE mydb SET checkpoint_frequency = 5;
ALTER DATABASE mydb SET barrier_interval_ms = 1000;
```

### Index Creation
```sql
CREATE INDEX idx_user_id ON events (user_id);
CREATE INDEX idx_time ON events (event_time) DISTRIBUTED BY (user_id);
```

## Production Deployment Recommendations

1. **RisingWave Cloud** - Managed, easiest option
2. **Kubernetes with Helm** - Full control with orchestration
3. **Docker Compose** - Development/testing only

### Resource Guidelines
- Compute nodes: High memory-to-CPU ratio (4:1+)
- Compactor nodes: 2:1 with compute (1:8 for write-heavy)
- Checkpoint interval: 1 second default, tune based on RPO

## Next Steps

When you're ready, tell me:
- What's your streaming use case (analytics, CDC, event processing)?
- What are your source and sink systems?
- What latency and throughput requirements do you have?
- Do you need help with SQL patterns, architecture, or troubleshooting?

I'll provide specific guidance following RisingWave best practices and streaming SQL patterns.


> Source: `docs/data_engineering/risingwave/risingwave-best-practices.md`

# RisingWave Best Practices, Performance Optimization, and Operational Guidance

A comprehensive guide for developers working with RisingWave, the cloud-native streaming database.

---

## Table of Contents

1. [Schema Design](#1-schema-design)
2. [Performance Optimization](#2-performance-optimization)
3. [Operational Best Practices](#3-operational-best-practices)
4. [Anti-patterns to Avoid](#4-anti-patterns-to-avoid)
5. [Comparison with Other Systems](#5-comparison-with-other-systems)

---

## 1. Schema Design

### Primary Key Selection

**Upsert Behavior**: For tables with primary key constraints, inserting a record with an existing key will **overwrite** the existing record. Design your keys accordingly.

```sql
-- Primary key enables upsert semantics
CREATE TABLE orders (
  order_id INT PRIMARY KEY,
  customer_id INT,
  amount DECIMAL,
  status VARCHAR
);
```

**Implicit Row ID**: For append-only streams without explicit primary keys, RisingWave derives a primary key by adding a `row_id` column, converting the stream to upsert semantics internally.

**Best Practices**:
- Choose primary keys that match your upsert/deduplication requirements
- For CDC sources, always define primary keys matching the source table
- Consider composite primary keys for tables that need uniqueness across multiple columns

### Index Strategies

RisingWave indexes are **implemented as specialized materialized views**, making them cost-effective to create and maintain.

```sql
-- Basic index creation
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Index with included columns (for covering queries)
CREATE INDEX idx_orders_customer ON orders(customer_id)
  INCLUDE (amount, status);

-- Specify distribution for prefix queries
CREATE INDEX idx_customers_name ON customers(c_name, c_nationkey)
  DISTRIBUTED BY (c_name);
```

**Key Guidelines**:

1. **Check SELECT columns**: All columns in your SELECT should appear in the INCLUDE clause
2. **Check WHERE conditions**: Columns used in filtering should be in index_column
3. **Timestamp ranges**: If filtering by timestamp (`BETWEEN t1 AND t2`), include that column in index_column
4. **Distribution matters**: RisingWave distributes data using the first index column by default. Specify DISTRIBUTED BY if queries only provide a prefix of index columns

**Index vs PostgreSQL Difference**: By default, RisingWave includes **all columns** of a table in an index if you omit the INCLUDE clause. This eliminates primary table lookups, which are slower in cloud environments.

### Partitioning Approaches

RisingWave uses **consistent hashing** for automatic data partitioning across compute nodes for parallel execution.

**Explicit Partitioning**:
- Use `DISTRIBUTED BY` in index creation to control data distribution
- Plan partitioning keys carefully - they affect query patterns and cross-partition operations

### Data Modeling for Streaming

#### Tables vs Sources

| Feature | Table | Source |
|---------|-------|--------|
| Data persistence | Yes | No |
| Storage space | Higher | Lower |
| Supports updates/deletes | Yes | No |
| Optimization potential | Lower | Higher (append-only) |

```sql
-- Source: no persistence, cannot modify data
CREATE SOURCE pageviews (
  user_id INT,
  page VARCHAR,
  timestamp TIMESTAMP
) WITH (
  connector = 'kafka',
  ...
);

-- Table: persists data, supports updates
CREATE TABLE user_sessions (
  session_id INT PRIMARY KEY,
  user_id INT,
  start_time TIMESTAMP
) WITH (
  connector = 'kafka',
  ...
);
```

#### Append-Only Tables with Watermarks

For streaming scenarios with time-based processing:

```sql
CREATE TABLE user_actions (
  user_name VARCHAR,
  data VARCHAR,
  user_action_time TIMESTAMP,
  -- Watermark allows 5 seconds late data
  WATERMARK FOR user_action_time AS user_action_time - INTERVAL '5' SECOND
) APPEND ONLY
WITH (connector = 'kafka', ...);
```

**Watermark Benefits**:
- Controls state size by filtering late data
- Enables temporal joins and windowing
- Only available for append-only tables

#### Temporal Filters for Data Cleanup

Clean up old data in materialized views:

```sql
CREATE MATERIALIZED VIEW recent_sales AS
SELECT * FROM sales
WHERE sale_date > NOW() - INTERVAL '1 week';
```

---

## 2. Performance Optimization

### Query Optimization Techniques

#### Streaming Query Optimization

1. **Bushy Join Trees**: RisingWave's optimizer creates bushy join trees when possible, enabling parallel data flow and reducing latency

2. **Cascading Materialized Views (MV-on-MV)**:
   ```sql
   -- Base aggregation
   CREATE MATERIALIZED VIEW hourly_sales AS
   SELECT product_id, date_trunc('hour', sale_time) as hour, SUM(amount) as total
   FROM sales
   GROUP BY product_id, date_trunc('hour', sale_time);

   -- Build on top without middleware
   CREATE MATERIALIZED VIEW daily_sales AS
   SELECT product_id, date_trunc('day', hour) as day, SUM(total) as daily_total
   FROM hourly_sales
   GROUP BY product_id, date_trunc('day', hour);
   ```

3. **Minimize Join Rows**: Reduce join cardinality to prevent bottlenecks
4. **Simplify Complex Queries**: Remove unnecessary joins, subqueries, and functions

#### Batch Query Optimization

- Use indexes for frequently accessed columns
- Increase `block_cache` and `meta_cache` for batch-serving nodes
- Avoid full table scans - ensure WHERE clauses use indexed columns

### Memory Management

#### Cache Types and Configuration

| Cache Type | Purpose | Best For |
|------------|---------|----------|
| Operator Cache | Intermediate state for joins/aggregations | Streaming queries |
| Block Cache | Cached data blocks from storage | Batch queries |
| Meta Cache | SST metadata | Both |

**Default Streaming Configuration**: More memory allocated to operator cache

**Batch-Serving Configuration**: Increase block_cache and meta_cache, reduce operator_cache

#### Memory Architecture

RisingWave reserves **30%** of total memory as buffer for traffic spikes. The remaining 70% is usable memory with tiered eviction:

- **Stable threshold**: Normal operation
- **Graceful threshold**: Begin eviction
- **Aggressive threshold**: Intensify eviction
- **>90%**: Maximum eviction intensity

Configure eviction with `memory_controller_eviction_factor_XXX` variables.

#### Memory-Only Mode (v2.6+)

For workloads where operator states fit in memory:
- Eliminates cache misses
- Provides consistent low latency
- Requires sufficient memory for all intermediate states

### Parallelism Configuration

```sql
-- Set parallelism for streaming queries in current session
SET streaming_parallelism = 16;

-- Set parallelism for batch queries
SET batch_parallelism = 8;
```

**Calculation**: With 3 compute nodes, each with 8 CPUs, maximum parallelism = 24

**Best Practices**:
- Start with defaults, increase for bottleneck fragments
- Use Grafana to identify parallelism needs
- Consider scaling out vs scaling up

### Checkpoint Tuning

#### Key Parameters

```toml
[system]
barrier_interval_ms = 1000    # Default: 1 second
checkpoint_frequency = 1      # Checkpoints per barrier
```

**Default Interval**: 1 second (vs Flink's default of 30 minutes)

#### Checkpoint Mechanism

1. Meta node injects barriers into input streams
2. Barriers flow downstream with data (never overtaking)
3. Compute nodes buffer dirty states in shared buffer
4. Async flush to SST files in object storage (S3)
5. Checkpoint completes when all states registered with meta service

**Tuning Considerations**:
- Lower RPO (less data loss) = more frequent checkpoints
- More frequent checkpoints = higher storage/compute overhead
- Shared buffer capacity: 4GB max by default

#### Troubleshooting Checkpoints

Monitor **Barrier Latency** in Grafana dashboard > Streaming. High latency indicates pipeline slowdown.

```sql
-- Trigger ad-hoc recovery (superuser only)
RECOVER;

-- Alter streaming rate limit during recovery
ALTER SYSTEM SET streaming_rate_limit = ...;
```

---

## 3. Operational Best Practices

### Monitoring and Observability

#### Critical Metrics to Monitor

| Metric | Location | Issue Indicator |
|--------|----------|-----------------|
| Barrier Latency | Streaming panel | Consistently high = pipeline stuck |
| Actor Output Blocking Time | Streaming Actors | High = backpressure |
| Executor Cache Miss Ratio | Streaming Actors | High = insufficient memory |
| CPU Usage (avg per core) | Cluster Node | >80% sustained = bottleneck |
| Uploading Memory | Hummock (Write) | High = shared buffer issues |

#### Grafana Dashboard Navigation

- **Streaming performance**: Grafana dashboard (dev) > Streaming
- **Actor-level metrics**: Grafana dashboard (dev) > Streaming Actors
- **Storage performance**: Grafana dashboard (dev) > Hummock (Read/Write)
- **Node resources**: Grafana dashboard (dev) > Cluster Node

#### Log Analysis

Search for specific patterns:
- `"blocked at requiring memory"` - State table writes waiting for shared buffer
- Error messages indicating failures

### Backup and Recovery

#### Checkpoint-Based Recovery

**RPO (Recovery Point Objective)**:
- Directly tied to checkpoint frequency
- Shorter RPO = more frequent checkpoints
- Configure upstream sources (Kafka) for replayability

**RTO (Recovery Time Objective)**:
- Depends on state size and network performance
- RisingWave's architecture enables efficient recovery
- Can scale infrastructure quickly (Kubernetes pods, VMs)

#### Recovery Process

1. Detect failure via health checks
2. Load last checkpoint from Hummock (object storage)
3. Resume processing from correct upstream offsets
4. Replay data from last checkpoint

**Upstream Configuration**: Ensure Kafka topics are configured for durability and replayability to achieve near-zero RPO.

### Scaling Strategies

#### Decoupled Compute and Storage

RisingWave's architecture allows independent scaling:
- **Compute**: Scale up (more CPU/memory) or out (more nodes)
- **Storage**: Object storage (S3) scales automatically

#### Dynamic Scaling During Backfill

Add nodes dynamically during backfill operations for high-parallelism processing. Backfill occurs during:
- Initial stream computation
- Upstream format changes
- Logic modifications
- Failure recovery

#### Resource Isolation

Configure separate node types for different workloads:
- **Compute nodes**: Stream processing
- **Serving nodes**: Batch queries

### Troubleshooting Common Issues

#### High Latency

**Diagnosis Steps**:
1. Check Barrier Latency panel for stuck barriers
2. Check backpressure panel for blocked actors
3. Check resource utilization (CPU >80%, memory, cache miss)

**Solutions**:
- Increase parallelism for bottleneck fragments
- Scale up compute resources
- Optimize queries (remove unnecessary joins)

#### Backpressure

**Finding Root Cause**:
1. Open Grafana "Streaming - Backpressure" panel
2. Find channels with high backpressure
3. Identify frontmost fragment (backpressure propagates upstream)

**Solutions**:
- Increase parallelism for slow operators
- Optimize query logic
- Scale resources

#### Out of Memory (OOM)

**Most common production issue!**

**Causes**:
- Caching overflow
- Large computation states
- Network transmission buffers
- Execution planning

**Solutions**:
- Scale up memory
- Scale out to distribute load
- Tune cache eviction policies
- Optimize queries to reduce state size

#### Cache Miss Issues

**Symptoms**:
- Executor memory usage smaller than expected
- High executor cache miss ratio

**Solutions**:
- Increase compute node memory
- Scale out to more nodes

---

## 4. Anti-patterns to Avoid

### Query Anti-patterns

1. **Unnecessary Joins**: Each join maintains state; remove joins that aren't essential
2. **Full Table Scans**: Always use indexed columns in WHERE clauses
3. **Inefficient WHERE Clauses**: Avoid complex functions that prevent index usage
4. **Heavy Ad-hoc OLAP Queries**: RisingWave isn't optimized for full-scan analytics

   ```sql
   -- Anti-pattern: Ad-hoc OLAP on RisingWave
   SELECT product_category, SUM(amount)
   FROM all_sales_history  -- billions of rows
   GROUP BY product_category;

   -- Better: Sink to dedicated OLAP system (ClickHouse, Pinot)
   ```

5. **Low-Cardinality Join Columns**: Easily triggers massive row amplification

### State Management Anti-patterns

1. **Unbounded State Growth**: Use temporal filters and TTL to manage state size

   ```sql
   -- Anti-pattern: Unbounded state
   CREATE MATERIALIZED VIEW all_events AS SELECT * FROM events;

   -- Better: Temporal filter
   CREATE MATERIALIZED VIEW recent_events AS
   SELECT * FROM events WHERE event_time > NOW() - INTERVAL '7 days';
   ```

2. **Expensive Aggregations**: Functions like `array_agg` are costly
3. **Ignoring Watermarks**: Without watermarks, state can grow indefinitely

### Design Anti-patterns

1. **Using RisingWave as Primary OLAP**: Sink output to dedicated OLAP systems for complex analytics
2. **Not Defining Primary Keys for CDC**: CDC sources require primary keys for correctness
3. **Ignoring NULL Handling**:
   - Batch inserts throw errors for NULL in NOT NULL columns
   - Streaming ignores rows with NULL in NOT NULL columns

### Performance Anti-patterns

1. **Not Creating Indexes**: Indexes are cheap in RisingWave - create them for repeated query patterns
2. **Wrong Distribution Key**: Causes hotspots and uneven load
3. **Not Monitoring Cache Performance**: High cache miss = degraded performance
4. **Ignoring Backpressure**: It's a symptom of deeper issues

### Configuration Anti-patterns

1. **Default Configuration for All Workloads**:
   - Streaming-optimized nodes need larger operator cache
   - Batch-serving nodes need larger block/meta cache

2. **Not Tuning Checkpoint Frequency**: Balance RPO requirements vs overhead

---

## 5. Comparison with Other Systems

### RisingWave vs Apache Flink

| Aspect | RisingWave | Apache Flink |
|--------|------------|--------------|
| **Interface** | SQL (PostgreSQL syntax) | Java/Scala/Python APIs, Flink SQL |
| **Learning Curve** | Lower (familiar SQL) | Higher (new APIs) |
| **State Storage** | Cloud object storage (S3) | Local (RocksDB) |
| **Checkpoint Default** | 1 second | 30 minutes |
| **Infrastructure** | Managed, cloud-native | Own cluster required |
| **Cascading MVs** | Yes (MV-on-MV) | No native equivalent |
| **CEP/ML APIs** | No | Yes |

**Choose RisingWave when**:
- Team is familiar with PostgreSQL
- You want simpler operations
- Cloud-native deployment is important
- You need cascading materialized views

**Choose Flink when**:
- You need multiple language support
- Complex event processing (CEP) is required
- ML pipeline integration is needed
- Unified batch and stream processing is critical

### RisingWave vs ksqlDB

| Aspect | RisingWave | ksqlDB |
|--------|------------|--------|
| **Architecture** | Standalone database | Kafka-dependent |
| **State Storage** | Cloud object storage | Kafka topics + RocksDB |
| **Resource Efficiency** | Higher | Lower (several times more for same state) |
| **Data Consistency** | Stronger guarantees | Potential inconsistency issues |
| **Use Case Scope** | Broader | Kafka-centric |

**Choose RisingWave when**:
- You need a standalone streaming database
- Resource efficiency is important
- You have complex use cases beyond simple transformations

**Choose ksqlDB when**:
- You're deeply invested in the Kafka ecosystem
- You have simpler stream processing needs
- You want tight Kafka integration

### RisingWave vs Materialize

| Aspect | RisingWave | Materialize |
|--------|------------|-------------|
| **State Storage** | Cloud object storage | In-memory |
| **Scalability** | Horizontal (distributed) | Limited (effectively single-node) |
| **Checkpointing** | Yes | No (replay recovery) |
| **Engine** | Custom | Timely/Differential Dataflow |
| **PostgreSQL Compatibility** | Yes | Yes |

**Choose RisingWave when**:
- You need to handle large state sizes
- Horizontal scalability is required
- Checkpoint-based recovery is preferred

**Choose Materialize when**:
- State fits in memory
- You need complex SQL joins with very fresh results
- You can tolerate replay-based recovery

### When to Choose RisingWave

**Ideal Use Cases**:
- Real-time dashboards and monitoring
- Alerting systems
- Event-driven applications
- Streaming ETL
- Real-time feature engineering

**RisingWave Excels When**:
- You want PostgreSQL-like simplicity
- You need cloud-native operations with separate compute/storage scaling
- You require cascading materialized views
- You prefer SQL-only interface
- You need frequent checkpoints for low RPO
- You want indexes that are cheap to create and maintain

**Consider Alternatives When**:
- You need complex OLAP analytics (use ClickHouse, Pinot, Druid)
- You need CEP or ML APIs (use Flink)
- You're committed to Kafka ecosystem (consider ksqlDB)
- All state fits in memory and you want Differential Dataflow (consider Materialize)

---

## Quick Reference

### Essential SQL Commands

```sql
-- Check system parameters
SHOW PARAMETERS;

-- Alter system parameters (superuser)
ALTER SYSTEM SET barrier_interval_ms = 500;

-- Set session parallelism
SET streaming_parallelism = 16;
SET batch_parallelism = 8;

-- Trigger recovery (superuser)
RECOVER;

-- Create index with best practices
CREATE INDEX idx_name ON table(filter_columns)
  INCLUDE (select_columns)
  DISTRIBUTED BY (prefix_columns);

-- Create temporal filter MV
CREATE MATERIALIZED VIEW mv_name AS
SELECT * FROM source
WHERE timestamp_col > NOW() - INTERVAL '7 days';

-- Create watermarked append-only table
CREATE TABLE t (
  ...,
  ts TIMESTAMP,
  WATERMARK FOR ts AS ts - INTERVAL '5' SECOND
) APPEND ONLY;
```

### Key Configuration Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `barrier_interval_ms` | 1000 | Checkpoint interval |
| `checkpoint_frequency` | 1 | Checkpoints per barrier |
| `streaming_parallelism` | Auto | Parallel workers for streaming |
| `batch_parallelism` | Auto | Parallel workers for batch |

### Monitoring Checklist

- [ ] Barrier latency stable
- [ ] No sustained backpressure
- [ ] CPU usage < 80%
- [ ] Cache miss ratio acceptable
- [ ] No OOM errors in logs
- [ ] Checkpoint completion normal

---

## Additional Resources

- **Official Documentation**: https://docs.risingwave.com
- **Tutorials**: https://tutorials.risingwave.com
- **GitHub**: https://github.com/risingwavelabs/risingwave
- **Blog**: https://risingwave.com/blog

---

*Research compiled: 2025-11-18*


> Source: `docs/data_engineering/risingwave/risingwave-connectors-research.md`

# RisingWave Connectors, Integrations, and Ecosystem Research

This comprehensive research document covers RisingWave's connector ecosystem, including source connectors, sink connectors, integrations, and configuration best practices.

## Table of Contents

1. [Source Connectors](#source-connectors)
   - [Kafka](#kafka-source)
   - [PostgreSQL CDC](#postgresql-cdc)
   - [MySQL CDC](#mysql-cdc)
   - [S3/File Sources](#s3-file-sources)
   - [Kinesis](#kinesis-source)
   - [Pulsar](#pulsar-source)
   - [Google Pub/Sub](#google-pubsub-source)
   - [NATS JetStream](#nats-jetstream-source)
2. [Sink Connectors](#sink-connectors)
   - [Kafka](#kafka-sink)
   - [JDBC (PostgreSQL/MySQL)](#jdbc-sink)
   - [Redis](#redis-sink)
   - [Elasticsearch](#elasticsearch-sink)
   - [ClickHouse](#clickhouse-sink)
   - [S3/Iceberg](#s3-iceberg-sink)
   - [Delta Lake](#delta-lake-sink)
   - [BigQuery](#bigquery-sink)
   - [Snowflake](#snowflake-sink)
3. [Data Formats](#data-formats)
4. [Integrations](#integrations)
   - [dbt](#dbt-integration)
   - [Grafana & Prometheus](#grafana-prometheus)
   - [Client Libraries](#client-libraries)
5. [Security & Authentication](#security-authentication)
6. [Performance Tuning](#performance-tuning)
7. [Best Practices](#best-practices)

---

## Source Connectors

### Kafka Source

RisingWave provides robust Kafka source connectivity with support for multiple authentication methods and data formats.

#### Basic Configuration

```sql
CREATE SOURCE my_kafka_source (
    user_id INT,
    product_id VARCHAR,
    timestamp TIMESTAMP
)
WITH (
    connector='kafka',
    topic='user_activity',
    properties.bootstrap.server='broker1:9092,broker2:9092'
)
FORMAT PLAIN ENCODE JSON;
```

#### With Metadata Extraction

```sql
CREATE SOURCE kafka_with_metadata (
    user_id INT,
    product_id VARCHAR,
    timestamp TIMESTAMP
)
INCLUDE key AS kafka_key
INCLUDE partition AS kafka_partition
INCLUDE offset AS kafka_offset
INCLUDE timestamp AS kafka_timestamp
WITH (
    connector='kafka',
    topic='user_activity',
    properties.bootstrap.server='localhost:9092'
)
FORMAT PLAIN ENCODE JSON;
```

#### Reusable Connections (v2.2+)

```sql
-- Create a reusable connection
CREATE CONNECTION kafka_conn1 WITH (
    type = 'kafka',
    properties.bootstrap.server = 'localhost:9092'
);

-- Use the connection for sources
CREATE SOURCE kafka_source (
    id int,
    name varchar,
    email varchar,
    age int
)
WITH (
    connector = 'kafka',
    connection = 'kafka_conn1',
    topic = 'topic1',
    scan.startup.mode='latest'
)
FORMAT PLAIN ENCODE JSON;
```

#### With Avro and Schema Registry

```sql
CREATE SOURCE avro_source
WITH (
    connector='kafka',
    topic='demo_topic',
    properties.bootstrap.server='172.10.1.1:9090,172.10.1.2:9090',
    scan.startup.mode='latest',
    scan.startup.timestamp.millis='140000000'
)
FORMAT PLAIN ENCODE AVRO (
    message = 'message_name',
    schema.registry = 'http://127.0.0.1:8081',
    schema.registry.username='your_username',
    schema.registry.password='your_password'
);
```

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `connector` | Set to `'kafka'` |
| `topic` | Kafka topic name |
| `properties.bootstrap.server` | Comma-separated list of brokers |
| `scan.startup.mode` | `'earliest'`, `'latest'`, or `'timestamp'` |
| `scan.startup.timestamp.millis` | Timestamp for startup (when mode is timestamp) |
| `properties.group.id` | Consumer group ID |

---

### PostgreSQL CDC

RisingWave supports PostgreSQL CDC using native connectors compatible with PostgreSQL versions 10-17.

#### Prerequisites

1. Set `wal_level` to `logical` in PostgreSQL:
```sql
ALTER SYSTEM SET wal_level = logical;
-- Requires restart
```

2. Grant required privileges:
```sql
CREATE USER risingwave_user REPLICATION LOGIN CREATEDB PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO risingwave_user;
```

#### Basic Configuration

```sql
CREATE TABLE pg_orders (
    o_orderkey BIGINT,
    o_custkey INTEGER,
    o_totalprice NUMERIC,
    o_orderdate TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (o_orderkey)
)
WITH (
    connector = 'postgres-cdc',
    hostname = '127.0.0.1',
    port = '5432',
    username = 'postgresuser',
    password = 'postgrespw',
    database.name = 'mydb',
    schema.name = 'public',
    table.name = 'orders'
);
```

#### Using CDC Source with Multiple Tables

```sql
-- Create the source first
CREATE SOURCE postgres_source WITH (
    connector = 'postgres-cdc',
    hostname = '127.0.0.1',
    port = '5432',
    username = 'postgresuser',
    password = 'postgrespw',
    database.name = 'mydb'
);

-- Create tables from the source
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    product_id INTEGER,
    sale_date DATE,
    quantity INTEGER,
    total_price NUMERIC
) FROM postgres_source TABLE 'public.sales';

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR,
    price NUMERIC
) FROM postgres_source TABLE 'public.products';
```

#### AWS RDS Configuration

For AWS RDS:
1. Create a parameter group (e.g., `pg-cdc`)
2. Set `rds.logical_replication = 1`
3. Apply the parameter group to your instance
4. Restart the instance

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `connector` | Set to `'postgres-cdc'` |
| `hostname` | PostgreSQL host |
| `port` | PostgreSQL port (default: 5432) |
| `username` / `password` | Credentials |
| `database.name` | Database name |
| `schema.name` | Schema name |
| `table.name` | Table name |
| `slot.name` | Replication slot name (optional) |

---

### MySQL CDC

RisingWave supports MySQL CDC for versions 5.7, 8.0, 8.4, and compatible databases (MariaDB, TiDB).

#### Prerequisites

1. Enable binary logging in `my.cnf`:
```ini
server-id = 223344
log_bin = mysql-bin
binlog_format = ROW
binlog_row_image = FULL
expire_logs_days = 10
```

2. Create user with privileges:
```sql
CREATE USER 'risingwave'@'%' IDENTIFIED BY 'password';
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'risingwave'@'%';
FLUSH PRIVILEGES;
```

#### Basic Configuration

```sql
-- Create the source
CREATE SOURCE mysql_mydb WITH (
    connector = 'mysql-cdc',
    hostname = '127.0.0.1',
    port = '3306',
    username = 'root',
    password = '123456',
    database.name = 'mydb',
    server.id = 5888
);

-- Create table from the source
CREATE TABLE t1_rw (
    v1 int,
    v2 int,
    PRIMARY KEY(v1)
) FROM mysql_mydb TABLE 'mydb.t1';
```

#### With Generated Columns

```sql
CREATE TABLE orders (
    order_id int,
    amount decimal,
    -- Generated column
    next_id int AS order_id + 1,
    PRIMARY KEY(order_id)
) FROM mysql_source TABLE 'mydb.orders';
```

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `connector` | Set to `'mysql-cdc'` |
| `hostname` | MySQL host |
| `port` | MySQL port (default: 3306) |
| `username` / `password` | Credentials |
| `database.name` | Database name |
| `server.id` | Unique server ID for replication |

---

### S3 File Sources

RisingWave supports ingesting CSV, ndjson, and Parquet files from S3.

#### CSV Configuration

```sql
CREATE TABLE s3_csv_source (
    id int,
    name varchar,
    age int
)
WITH (
    connector = 's3',
    s3.region_name = 'ap-southeast-2',
    s3.bucket_name = 'example-s3-source',
    s3.credentials.access = 'your_access_key',
    s3.credentials.secret = 'your_secret_key'
)
FORMAT PLAIN ENCODE CSV (
    without_header = 'true',
    delimiter = ','
);
```

#### JSON (ndjson) Configuration

```sql
CREATE SOURCE s3_json_source (
    id int,
    name varchar,
    data jsonb
)
WITH (
    connector = 's3',
    s3.region_name = 'us-east-1',
    s3.bucket_name = 'my-bucket',
    s3.credentials.access = 'access_key',
    s3.credentials.secret = 'secret_key',
    match_pattern = '*.json'
)
FORMAT PLAIN ENCODE JSON;
```

#### Parquet with file_scan()

```sql
-- Read a single Parquet file
SELECT * FROM file_scan(
    's3://bucket/path/file.parquet',
    parquet,
    's3.region' = 'us-east-1',
    's3.access.key' = 'key',
    's3.secret.key' = 'secret'
);

-- Read directory of Parquet files
SELECT * FROM file_scan(
    's3://bucket/path/',
    parquet,
    's3.region' = 'us-east-1',
    's3.access.key' = 'key',
    's3.secret.key' = 'secret'
);
```

#### Important Notes

- **Avro is NOT supported** for S3 sources (only for message queues)
- RisingWave does not guarantee file read order
- New files are automatically ingested
- Deleted files are not detected
- Empty cells in CSV are parsed as NULL

---

### Kinesis Source

```sql
CREATE SOURCE kinesis_source (
    user_id INT,
    action VARCHAR,
    timestamp TIMESTAMP
)
WITH (
    connector='kinesis',
    stream='your_stream_name',
    aws.region='us-east-1',
    aws.credentials.access_key_id = 'your_access_key',
    aws.credentials.secret_access_key = 'your_secret_key'
)
FORMAT PLAIN ENCODE JSON;
```

#### With IAM Role

```sql
CREATE SOURCE kinesis_with_role
WITH (
    connector='kinesis',
    stream='my-stream',
    aws.region='us-east-1',
    aws.credentials.role.arn = 'arn:aws:iam::602389639824:role/demo_role',
    aws.credentials.role.external_id = 'external_id'
)
FORMAT PLAIN ENCODE JSON;
```

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `connector` | Set to `'kinesis'` |
| `stream` | Kinesis stream name |
| `aws.region` | AWS region |
| `aws.credentials.access_key_id` | Access key |
| `aws.credentials.secret_access_key` | Secret key |
| `aws.credentials.session_token` | Session token (optional) |
| `aws.credentials.role.arn` | IAM role ARN |
| `endpoint` | Custom endpoint (optional) |

---

### Pulsar Source

```sql
CREATE SOURCE pulsar_source
WITH (
    connector='pulsar',
    topic='demo_topic',
    service.url='pulsar://localhost:6650/',
    scan.startup.mode='latest'
)
FORMAT PLAIN ENCODE JSON;
```

#### With OAuth Authentication

```sql
CREATE SOURCE pulsar_oauth_source
WITH (
    connector='pulsar',
    topic='demo_topic',
    service.url='pulsar://localhost:6650/',
    oauth.issuer.url='https://auth.streamnative.cloud/',
    oauth.credentials.url='s3://bucket_name/your_key_file.file',
    oauth.audience='urn:sn:pulsar:o-d6fgh:instance-0',
    aws.credentials.access_key_id='access_key',
    aws.credentials.secret_access_key='secret_key',
    scan.startup.mode='latest'
)
FORMAT PLAIN ENCODE AVRO (
    message = 'message',
    schema.location = 'https://bucket.s3-us-west-2.amazonaws.com/schema.avsc'
);
```

---

### Google Pub/Sub Source

```sql
CREATE SOURCE pubsub_source (
    message_id VARCHAR,
    data JSONB,
    attributes JSONB
)
WITH (
    connector = 'google_pubsub',
    pubsub.subscription = 'projects/my-project/subscriptions/my-subscription',
    pubsub.credentials = '{
        "type": "service_account",
        "project_id": "my-project",
        ...
    }'
)
FORMAT PLAIN ENCODE JSON;
```

**Note**: Google Pub/Sub provides at-least-once semantics (not exactly-once) due to SDK limitations.

---

### NATS JetStream Source

```sql
CREATE TABLE nats_source
WITH (
    connector = 'nats',
    server_url = 'nats-server:4222',
    subject = 'live_stream_metrics',
    stream = 'risingwave',
    connect_mode = 'plain'
)
FORMAT PLAIN ENCODE PROTOBUF (
    message = 'livestream.schema.LiveStreamMetrics',
    schema.location = 'http://file_server:8080/schema'
);
```

#### With Authentication

```sql
CREATE TABLE nats_auth_source
WITH (
    connector = 'nats',
    server_url = 'nats-server:4222',
    subject = 'events',
    stream = 'mystream',
    connect_mode = 'user_and_password',
    username = 'user',
    password = 'password',
    consumer.durable_name = 'risingwave_consumer',
    consumer.ack_policy = 'explicit'
)
FORMAT PLAIN ENCODE JSON;
```

---

## Sink Connectors

### Kafka Sink

#### Basic Configuration

```sql
CREATE SINK kafka_sink FROM my_materialized_view
WITH (
    connector='kafka',
    properties.bootstrap.server='localhost:9092',
    topic='output_topic'
)
FORMAT PLAIN ENCODE JSON;
```

#### UPSERT with Primary Key

```sql
CREATE SINK upsert_sink FROM my_table
WITH (
    properties.bootstrap.server = 'localhost:9092',
    topic = 'upsert_topic',
    connector = 'kafka',
    primary_key = 'user_id'
)
FORMAT UPSERT ENCODE JSON;
```

#### With SSL Encryption

```sql
CREATE SINK ssl_sink FROM mv1
WITH (
    connector='kafka',
    topic='secure-events',
    properties.bootstrap.server='localhost:9093',
    properties.security.protocol='SSL',
    properties.ssl.ca.location='/path/to/ca-cert',
    properties.ssl.certificate.location='/path/to/client.pem',
    properties.ssl.key.location='/path/to/client.key',
    properties.ssl.key.password='keypassword'
)
FORMAT PLAIN ENCODE JSON;
```

#### With SASL/PLAIN and SSL

```sql
CREATE SINK sasl_ssl_sink FROM mv1
WITH (
    connector='kafka',
    topic='secure-events',
    properties.bootstrap.server='localhost:9093',
    properties.sasl.mechanism='PLAIN',
    properties.security.protocol='SASL_SSL',
    properties.sasl.username='admin',
    properties.sasl.password='admin-secret',
    properties.ssl.ca.location='/path/to/ca-cert',
    properties.ssl.certificate.location='/path/to/client.pem',
    properties.ssl.key.location='/path/to/client.key',
    properties.ssl.key.password='keypassword'
)
FORMAT PLAIN ENCODE JSON;
```

#### With PrivateLink

```sql
CREATE SINK privatelink_sink FROM mv
WITH (
    connector='kafka',
    properties.bootstrap.server='b-1.xxx.amazonaws.com:9092,b-2.xxx.amazonaws.com:9092',
    topic='msk_topic',
    privatelink.endpoint='10.148.0.4',
    privatelink.targets = '[{"port": 8001}, {"port": 8002}]'
)
FORMAT PLAIN ENCODE JSON (
    force_append_only='true'
);
```

---

### JDBC Sink

#### PostgreSQL Sink

```sql
CREATE SINK postgres_sink FROM my_table
WITH (
    connector = 'jdbc',
    jdbc.url = 'jdbc:postgresql://postgres:5432/mydb',
    user = 'myuser',
    password = '123456',
    table.name = 'target_table',
    type = 'upsert',
    primary_key = 'id'
);
```

#### MySQL Sink

```sql
CREATE SINK mysql_sink FROM my_table
WITH (
    connector = 'jdbc',
    jdbc.url = 'jdbc:mysql://mysql:3306/mydb?ssl-mode=REQUIRED',
    user = 'myuser',
    password = 'mypassword',
    table.name = 'target_table',
    type = 'upsert',
    primary_key = 'id'
);
```

#### Native PostgreSQL Connector (v2.2+)

Set in configuration:
```yaml
[streaming.developer]
stream_switch_jdbc_pg_to_native = true
```

Then create the sink as usual. This uses a Rust-based native connector instead of JDBC.

#### Key Parameters

| Parameter | Description |
|-----------|-------------|
| `connector` | Set to `'jdbc'` |
| `jdbc.url` | JDBC connection URL |
| `user` / `password` | Database credentials |
| `table.name` | Target table name |
| `type` | `'upsert'` or `'append-only'` |
| `primary_key` | Required for upsert mode |

**Note**: Requires JDK 11+ for JDBC connector.

---

### Redis Sink

#### Key-Value Cache Pattern

```sql
CREATE SINK redis_cache_sink FROM user_profiles_mv
WITH (
    connector = 'redis',
    redis.url = 'redis://127.0.0.1:6379/',
    primary_key = 'user_id'
)
FORMAT PLAIN ENCODE JSON (
    force_append_only = 'true'
);
```

#### Geospatial Pattern

```sql
CREATE SINK geo_sink FROM driver_locations
WITH (
    connector = 'redis',
    redis.url = 'redis://127.0.0.1:6379/',
    primary_key = 'driver_id,city'
)
FORMAT UPSERT ENCODE TEMPLATE (
    redis_value_type = 'geospatial',
    key_format = 'drivers:{city}',
    member = 'driver_id',
    longitude = 'longitude',
    latitude = 'latitude'
);
```

---

### Elasticsearch Sink

```sql
CREATE SINK es_sink FROM my_view
WITH (
    connector = 'elasticsearch',
    primary_key = 'doc_id',
    index = 'my_index',
    url = 'http://elasticsearch:9200',
    username = 'elastic',
    password = 'password',
    delimiter = '_'
);
```

#### With Dynamic Index

```sql
CREATE SINK es_dynamic_sink FROM my_view
WITH (
    connector = 'elasticsearch',
    primary_key = 'doc_id',
    index_column = 'index_name_column',
    url = 'http://elasticsearch:9200',
    username = 'elastic',
    password = 'password'
);
```

**Notes**:
- Supports Elasticsearch 7.x and 8.x
- Defaults to upsert mode (append-only not supported)
- Provides at-least-once delivery semantics
- Requires JDK 11+
- **Premium feature** in self-hosted deployments

---

### ClickHouse Sink

```sql
CREATE SINK clickhouse_sink FROM my_table
WITH (
    connector = 'clickhouse',
    type = 'upsert',
    clickhouse.url = 'http://clickhouse:8123',
    clickhouse.user = 'default',
    clickhouse.password = 'password',
    clickhouse.database = 'default',
    clickhouse.table = 'target_table',
    primary_key = 'id'
);
```

**Best Practice**: Use deduplication engines like `ReplacingMergeTree` in ClickHouse to handle potential duplicate writes during RisingWave recovery.

---

### S3/Iceberg Sink

#### Iceberg with Storage Catalog

```sql
CREATE SINK iceberg_sink FROM my_table
WITH (
    connector = 'iceberg',
    type = 'upsert',
    primary_key = 'id',
    database.name = 'demo_db',
    table.name = 'target_table',
    catalog.name = 'demo',
    catalog.type = 'storage',
    warehouse.path = 's3a://my-bucket/iceberg',
    s3.endpoint = 'https://s3.amazonaws.com',
    s3.region = 'us-east-1',
    s3.access.key = 'access_key',
    s3.secret.key = 'secret_key',
    create_table_if_not_exists = 'true'
);
```

#### Iceberg with REST Catalog

```sql
CREATE SINK iceberg_rest_sink FROM my_table
WITH (
    connector = 'iceberg',
    type = 'append-only',
    force_append_only = 'true',
    database.name = 'demo_db',
    table.name = 'target_table',
    catalog.name = 'demo',
    catalog.type = 'rest',
    catalog.uri = 'http://iceberg-rest:8181'
);
```

#### Direct S3 Sink with Parquet

```sql
CREATE SINK s3_parquet_sink AS SELECT * FROM my_table
WITH (
    connector = 's3',
    s3.path = 'output/',
    s3.region_name = 'us-east-1',
    s3.bucket_name = 'my-bucket',
    s3.credentials.access = 'access_key',
    s3.credentials.secret = 'secret_key',
    type = 'append-only'
)
FORMAT PLAIN ENCODE PARQUET (
    force_append_only = 'true'
);
```

#### Amazon S3 Tables Integration

```sql
CREATE SINK s3_tables_sink FROM my_table
WITH (
    connector = 'iceberg',
    type = 'upsert',
    primary_key = 'id',
    database.name = 'my_namespace',
    table.name = 'my_table',
    catalog.name = 's3tables',
    catalog.type = 'rest',
    catalog.uri = 'https://s3tables.us-east-1.amazonaws.com/iceberg',
    -- SigV4 authentication
    s3.region = 'us-east-1',
    s3.access.key = 'access_key',
    s3.secret.key = 'secret_key'
);
```

---

### Delta Lake Sink

```sql
CREATE SINK delta_sink FROM my_table
WITH (
    connector = 'deltalake',
    type = 'append-only',
    force_append_only = 'true',
    location = 's3a://my-bucket/delta-table',
    s3.endpoint = 'https://s3.amazonaws.com',
    s3.access.key = 'access_key',
    s3.secret.key = 'secret_key'
);
```

---

### BigQuery Sink

```sql
CREATE SINK bigquery_sink FROM my_table
WITH (
    connector = 'bigquery',
    type = 'append-only',
    bigquery.local.path = '/path/to/service-account.json',
    bigquery.project = 'my-project',
    bigquery.dataset = 'my_dataset',
    bigquery.table = 'my_table',
    force_append_only = 'true'
);
```

---

### Snowflake Sink

```sql
CREATE SINK snowflake_sink FROM my_table
WITH (
    connector = 'snowflake',
    s3.bucket_name = 'staging-bucket',
    s3.credentials.access = 'access_key',
    s3.credentials.secret = 'secret_key',
    s3.region_name = 'us-east-1',
    s3.path = 'staging/'
);
```

**Note**: Uses Snowpipe for data loading. Data is staged in S3 in JSON format before loading.

**Premium feature** in self-hosted deployments.

---

## Data Formats

### FORMAT and ENCODE Options

| ENCODE | Compatible FORMATS | Description |
|--------|-------------------|-------------|
| `JSON` | PLAIN, UPSERT, DEBEZIUM | JSON serialization |
| `AVRO` | PLAIN, UPSERT, DEBEZIUM | Avro with schema registry |
| `PROTOBUF` | PLAIN | Protocol Buffers |
| `CSV` | PLAIN | Comma-separated values |
| `BYTES` | PLAIN | Raw bytes (single BYTEA field) |

### JSON Examples

```sql
-- Basic JSON
FORMAT PLAIN ENCODE JSON

-- With schema registry
FORMAT PLAIN ENCODE JSON (
    schema.registry = 'http://registry:8081'
)
```

### Avro Examples

```sql
-- With schema registry
FORMAT PLAIN ENCODE AVRO (
    schema.registry = 'http://registry:8081',
    schema.registry.username = 'username',
    schema.registry.password = 'password'
)

-- With S3 schema location
FORMAT PLAIN ENCODE AVRO (
    message = 'MyMessage',
    schema.location = 's3://bucket/schema.avsc'
)
```

### Protobuf Examples

```sql
FORMAT PLAIN ENCODE PROTOBUF (
    message = 'package.MessageName',
    schema.location = 'http://server/schema.proto'
)

-- With schema registry
FORMAT PLAIN ENCODE PROTOBUF (
    message = 'package.MessageName',
    schema.registry = 'http://registry:8081'
)
```

### CSV Examples

```sql
FORMAT PLAIN ENCODE CSV (
    without_header = 'true',
    delimiter = ','
)

-- Tab-delimited
FORMAT PLAIN ENCODE CSV (
    without_header = 'false',
    delimiter = '\t'
)
```

### Timestamp Handling

```sql
FORMAT PLAIN ENCODE JSON (
    timestamptz.handling.mode = 'micro'  -- or 'milli'
)
```

---

## Integrations

### dbt Integration

#### Installation

```bash
pip install dbt-core dbt-risingwave
```

#### Configuration (profiles.yml)

```yaml
risingwave_project:
  target: dev
  outputs:
    dev:
      type: risingwave
      host: localhost
      port: 4566
      user: root
      password: ""
      database: dev
      schema: public
      threads: 4
      streaming_parallelism: 4
      streaming_max_parallelism: 8
```

#### Materializations

**Materialized View:**
```sql
{{ config(materialized='materialized_view') }}
SELECT * FROM source_table
```

**Table:**
```sql
{{ config(materialized='table') }}
SELECT * FROM source_table
```

**Ephemeral (CTE):**
```sql
{{ config(materialized='ephemeral') }}
SELECT * FROM source_table
```

**Zero Downtime Rebuilds (v2.2+):**
```sql
{{ config(
    materialized='materialized_view',
    zero_downtime={'enabled': true}
) }}
SELECT * FROM source_table
```

Run with: `dbt run --vars 'zero_downtime: true'`

#### Commands

```bash
# Create new models
dbt run

# Drop and recreate models
dbt run --full-refresh

# Select specific models
dbt run --select "my_model+"  # Model and children
dbt run --select "+my_model"  # Model and parents
```

---

### Grafana & Prometheus

#### Kubernetes Setup

```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:http-web

# Access from external hosts
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:http-web --address 0.0.0.0
```

Default credentials:
- Username: `admin`
- Password: `prom-operator`

#### Demo Cluster Setup

```bash
# Clone repository
git clone https://github.com/risingwavelabs/risingwave.git

# Start demo with Prometheus and Grafana
cd risingwave/integration_tests/prometheus
docker compose up -d
```

#### Metric Relabeling

If namespace filters don't work, add the `risingwave_name` label:

```yaml
# In Prometheus Operator endpoint spec
metricRelabelings:
  - sourceLabels: [__name__]
    targetLabel: risingwave_name
    replacement: 'my-cluster'
```

#### Using RisingWave with Grafana

1. Create a data source connection to RisingWave (PostgreSQL compatible)
2. Build materialized views for metrics
3. Visualize in Grafana dashboards

---

### Client Libraries

#### Python (psycopg2)

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=4566,
    user="root",
    dbname="dev"
)
conn.autocommit = True

cursor = conn.cursor()
cursor.execute("SELECT * FROM my_table")
results = cursor.fetchall()
```

#### Python (risingwave-py SDK)

```bash
pip install risingwave-py psycopg2-binary
```

```python
from risingwave import RisingWave, OutputFormat

rw = RisingWave(
    host="localhost",
    port=4566,
    user="root",
    database="dev"
)

# Subscribe to changes
@rw.on_change("my_materialized_view")
def handler(event):
    print(f"Change: {event}")
```

#### Python (SQLAlchemy)

```bash
pip install SQLAlchemy sqlalchemy-risingwave psycopg2-binary
```

```python
from sqlalchemy import create_engine

engine = create_engine('risingwave+psycopg2://root@localhost:4566/dev')

with engine.connect() as conn:
    result = conn.execute("SELECT * FROM my_table")
    for row in result:
        print(row)
```

#### Java (JDBC)

```java
import java.sql.*;

String url = "jdbc:postgresql://localhost:4566/dev";
String user = "root";
String password = "";

Connection conn = DriverManager.getConnection(url, user, password);
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT * FROM my_table");

while (rs.next()) {
    System.out.println(rs.getString(1));
}
```

#### Other Languages

RisingWave is PostgreSQL wire-compatible, so any PostgreSQL client library works:
- **Go**: `pgx`, `database/sql` with `lib/pq`
- **Node.js**: `pg`, `postgres`
- **Ruby**: `pg` gem

---

## Security & Authentication

### Kafka SSL (Without SASL)

```sql
CREATE SOURCE ssl_source (
    column1 varchar,
    column2 integer
)
WITH (
    connector='kafka',
    topic='secure-topic',
    properties.bootstrap.server='localhost:9093',
    scan.startup.mode='earliest',
    properties.security.protocol='SSL',
    properties.ssl.ca.location='/path/to/ca-cert',
    properties.ssl.certificate.location='/path/to/client.pem',
    properties.ssl.key.location='/path/to/client.key',
    properties.ssl.key.password='keypassword'
)
FORMAT PLAIN ENCODE JSON;
```

### Kafka SASL/PLAIN (Without SSL)

```sql
CREATE SOURCE sasl_source (
    column1 varchar,
    column2 integer
)
WITH (
    connector='kafka',
    topic='secure-topic',
    properties.bootstrap.server='localhost:9093',
    scan.startup.mode='earliest',
    properties.sasl.mechanism='PLAIN',
    properties.security.protocol='SASL_PLAINTEXT',
    properties.sasl.username='admin',
    properties.sasl.password='admin-secret'
)
FORMAT PLAIN ENCODE JSON;
```

### Kafka SASL/PLAIN with SSL

```sql
CREATE SOURCE sasl_ssl_source (
    column1 varchar,
    column2 integer
)
WITH (
    connector='kafka',
    topic='secure-topic',
    properties.bootstrap.server='localhost:9093',
    properties.sasl.mechanism='PLAIN',
    properties.security.protocol='SASL_SSL',
    properties.sasl.username='admin',
    properties.sasl.password='admin-secret',
    properties.ssl.ca.location='/path/to/ca-cert',
    properties.ssl.certificate.location='/path/to/client.pem',
    properties.ssl.key.location='/path/to/client.key',
    properties.ssl.key.password='keypassword'
)
FORMAT PLAIN ENCODE JSON;
```

### SSL Troubleshooting

Bypass CA verification (for testing):
```sql
properties.ssl.endpoint.identification.algorithm='none'
```

### AWS Authentication

#### Access Keys
```sql
aws.credentials.access_key_id = 'AKIAIOSFODNN7EXAMPLE',
aws.credentials.secret_access_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
```

#### Session Token (Temporary Credentials)
```sql
aws.credentials.session_token = 'FwoGZXIvYXdzE...'
```

#### IAM Role
```sql
aws.credentials.role.arn = 'arn:aws:iam::123456789012:role/MyRole',
aws.credentials.role.external_id = 'external-id-123'
```

---

## Performance Tuning

### Parallelism Configuration

#### Default Behavior

By default, RisingWave utilizes maximum available CPUs for streaming jobs.

#### For 300+ Streaming Jobs

Update configuration in `risingwave.yaml`:

```yaml
[meta]
disable_automatic_parallelism_control = true
default_parallelism = 8
```

#### Session Variables

```sql
-- Set streaming parallelism
SET streaming_parallelism = 4;

-- Set batch parallelism
SET batch_parallelism = 8;
```

#### Check Parallelism

```sql
SELECT * FROM rw_fragment_parallelism;
```

#### Alter Parallelism

```sql
ALTER MATERIALIZED VIEW my_mv SET PARALLELISM = 4;
```

### dbt with Parallelism

```sql
{{ config(
    materialized='materialized_view',
    streaming_parallelism=2,
    streaming_max_parallelism=8
) }}
```

### Sink Decoupling

Enable buffering between RisingWave and downstream systems:

```sql
SET sink_decouple = true;
```

Benefits:
- Protects RisingWave from downstream performance issues
- Maintains stability during downstream unavailability

### Dedicated Batch-Serving Cluster

For sub-second batch query latency:
1. Deploy separate compute nodes for batch queries
2. Isolates batch workloads from streaming
3. Improves availability of batch processing

### Common Performance Considerations

1. **Partitioning Skew**: Ensure even data distribution
2. **State Management**: Monitor state size for stateful operations
3. **Communication Overhead**: Minimize cross-node shuffling
4. **Memory Management**: Monitor for OOM errors
5. **Checkpoint Intervals**: Balance between latency and overhead

---

## Best Practices

### Source Configuration

1. **Use Tables for Primary Key Constraints**: RisingWave only enforces PK constraints on tables, not sources
   ```sql
   CREATE TABLE (not SOURCE) for PK enforcement
   ```

2. **Reusable Connections (v2.2+)**: Define connection once, use across multiple sources/sinks
   ```sql
   CREATE CONNECTION kafka_conn WITH (...);
   ```

3. **Schema Registry**: Always use for Avro/Protobuf to ensure schema consistency

4. **Startup Mode**: Use `scan.startup.mode='latest'` for new deployments to avoid reprocessing

### Sink Configuration

1. **Sink Decoupling**: Enable for production to protect against downstream issues

2. **Primary Keys**: Always specify for upsert sinks
   ```sql
   primary_key = 'id'
   ```

3. **Deduplication in Downstream**: Use deduplication engines (e.g., ClickHouse ReplacingMergeTree)

4. **Batch Size Tuning**: Configure appropriate batch sizes for throughput vs. latency tradeoff

### CDC Best Practices

1. **Replication Slots**: Monitor and manage PostgreSQL replication slots
2. **WAL Retention**: Configure appropriate retention for recovery
3. **Privilege Management**: Use minimal required privileges
4. **Network Latency**: Deploy RisingWave close to source databases

### Data Format Best Practices

1. **Avro/Protobuf**: Preferred for schema evolution support
2. **JSON**: Use for flexibility but monitor for schema drift
3. **CSV**: Only for simple, flat data structures

### Monitoring Best Practices

1. **Set up Grafana dashboards**: Use provided templates
2. **Monitor key metrics**:
   - Streaming lag
   - Memory usage
   - Checkpoint latency
   - Sink throughput
3. **Alert on anomalies**: Configure Prometheus alerts

### Security Best Practices

1. **SSL/TLS**: Always enable for production Kafka connections
2. **Credential Management**: Use secrets management, not hardcoded values
3. **Network Isolation**: Use PrivateLink for cloud deployments
4. **Minimal Privileges**: Grant only required permissions

---

## Resources

### Official Documentation

- **Main Docs**: https://docs.risingwave.com
- **Kafka Source**: https://docs.risingwave.com/ingestion/sources/kafka
- **PostgreSQL CDC**: https://docs.risingwave.com/ingestion/sources/postgresql/pg-cdc
- **MySQL CDC**: https://docs.risingwave.com/ingestion/sources/mysql/mysql-cdc
- **S3 Source**: https://docs.risingwave.com/integrations/sources/s3
- **Kinesis Source**: https://docs.risingwave.com/integrations/sources/kinesis
- **Pulsar Source**: https://docs.risingwave.com/integrations/sources/pulsar
- **Data Delivery Overview**: https://docs.risingwave.com/docs/current/data-delivery/
- **dbt Setup**: https://docs.getdbt.com/docs/core/connect-data-platform/risingwave-setup
- **Python SDK**: https://docs.risingwave.com/python-sdk/intro

### GitHub Repositories

- **RisingWave**: https://github.com/risingwavelabs/risingwave
- **dbt-risingwave**: https://github.com/risingwavelabs/dbt-risingwave
- **sqlalchemy-risingwave**: https://github.com/risingwavelabs/sqlalchemy-risingwave
- **risingwave-py**: https://github.com/risingwavelabs/risingwave-py

### Tools

- **SQL Generator**: https://sql.risingwave.com - Interactive tool for generating connector SQL

### Version History

- **v2.2**: Reusable connections, zero-downtime dbt rebuilds, native PostgreSQL sink
- **v2.1**: Enhanced Iceberg connector
- **v2.0**: Python SDK improvements
- **v1.9**: Additional sink connectors
- **v1.7**: Adaptive parallelism

---

## Conclusion

RisingWave provides a comprehensive connector ecosystem that enables seamless integration with modern data infrastructure. Key strengths include:

1. **PostgreSQL Wire Compatibility**: Use existing tools and drivers
2. **Native CDC Support**: Direct database change capture without Debezium
3. **Multiple Data Formats**: JSON, Avro, Protobuf, CSV, Parquet
4. **Cloud-Native**: AWS, GCP, and Azure integrations
5. **Open Table Formats**: Iceberg and Delta Lake support
6. **dbt Integration**: Transform streaming data with familiar SQL

For production deployments, focus on:
- Proper security configuration (SSL/SASL)
- Performance tuning (parallelism, sink decoupling)
- Monitoring (Grafana/Prometheus)
- High availability configuration

The connector ecosystem continues to expand with each release, so check the official documentation for the latest supported integrations and features.


> Source: `docs/data_engineering/risingwave/risingwave-sql-patterns.md`

# RisingWave SQL Patterns and Streaming Concepts Reference

A comprehensive guide to RisingWave SQL syntax, streaming patterns, and best practices for real-time data processing.

## Table of Contents

1. [SQL Syntax and Extensions](#sql-syntax-and-extensions)
2. [Streaming Patterns](#streaming-patterns)
3. [Data Types and Functions](#data-types-and-functions)
4. [Common Use Cases](#common-use-cases)

---

## SQL Syntax and Extensions

### CREATE SOURCE

Sources establish connections to external data without storing data in RisingWave. They act as data entry points.

#### Basic Syntax

```sql
CREATE SOURCE [IF NOT EXISTS] source_name (
    column_name data_type [AS source_column_name] [NOT NULL],
    ...
    [, PRIMARY KEY (column_name, ...)]
)
WITH (
    connector = 'connector_name',
    connector_property = 'value',
    ...
)
FORMAT format_type ENCODE encode_type;
```

**Note:** PRIMARY KEY in sources is optional and indicates semantic meaning only, not an enforced constraint.

#### Kafka Source Examples

**Basic Kafka Source with JSON:**

```sql
CREATE SOURCE website_visits_stream (
    timestamp TIMESTAMP,
    user_id VARCHAR,
    page_id VARCHAR,
    action VARCHAR
)
WITH (
    connector = 'kafka',
    topic = 'user_activity',
    properties.bootstrap.server = 'broker1:9092,broker2:9092',
    scan.startup.mode = 'earliest'
)
FORMAT PLAIN ENCODE JSON;
```

**Kafka Source with Avro and Schema Registry:**

```sql
CREATE SOURCE avro_source (
    *,
    gen_i32_field INT AS int32_field + 2
)
INCLUDE KEY AS some_key
WITH (
    connector = 'kafka',
    topic = 'avro-topic',
    properties.bootstrap.server = 'message_queue:29092'
)
FORMAT UPSERT ENCODE AVRO (
    schema.registry = 'http://schema-registry:8081'
);
```

**Kafka Source with Watermark for Event Time Processing:**

```sql
CREATE SOURCE events (
    event_id VARCHAR,
    user_id VARCHAR,
    event_type VARCHAR,
    event_time TIMESTAMP,
    payload JSONB,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'events',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;
```

#### PostgreSQL CDC Source

CDC sources must use CREATE TABLE (not CREATE SOURCE) and require a PRIMARY KEY.

```sql
CREATE TABLE orders (
    order_id INTEGER,
    customer_id INTEGER,
    product_id VARCHAR,
    quantity INTEGER,
    total_price DECIMAL,
    order_time TIMESTAMP,
    status VARCHAR,
    PRIMARY KEY (order_id)
)
WITH (
    connector = 'postgres-cdc',
    hostname = '127.0.0.1',
    port = '5432',
    username = 'postgres',
    password = 'postgres',
    database.name = 'ecommerce',
    schema.name = 'public',
    table.name = 'orders'
);
```

#### MySQL CDC Source

```sql
CREATE TABLE users (
    user_id INTEGER,
    username VARCHAR,
    email VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (user_id)
)
WITH (
    connector = 'mysql-cdc',
    hostname = '127.0.0.1',
    port = '3306',
    username = 'root',
    password = 'password',
    database.name = 'app_db',
    table.name = 'users'
);
```

### CREATE TABLE vs CREATE SOURCE

| Aspect | Source | Table |
|--------|--------|-------|
| Data Storage | No storage, entry point only | Stores data internally |
| Primary Key | Optional, semantic only | Enforced constraint |
| CDC Support | Must use Table | Required for CDC |
| Consistency | Jobs may see inconsistent results | Guaranteed consistent view |
| Fault Tolerance | Cannot resume from checkpoint | Resumes from last checkpoint |

### CREATE MATERIALIZED VIEW

Materialized views store query results and update automatically as source data changes.

#### Basic Syntax

```sql
CREATE MATERIALIZED VIEW view_name AS
SELECT ...
FROM source_or_table
[WHERE ...]
[GROUP BY ...]
[EMIT ON WINDOW CLOSE];  -- Optional: for window-based processing
```

#### Aggregation Examples

**Simple Aggregation:**

```sql
CREATE MATERIALIZED VIEW customer_sales AS
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_price) AS total_sales,
    AVG(total_price) AS avg_order_value,
    MAX(order_time) AS last_order
FROM orders
GROUP BY customer_id;
```

**Multi-level Aggregation:**

```sql
CREATE MATERIALIZED VIEW daily_product_stats AS
SELECT
    DATE_TRUNC('day', order_time) AS order_date,
    product_id,
    COUNT(*) AS units_sold,
    SUM(quantity) AS total_quantity,
    SUM(total_price) AS revenue
FROM orders
GROUP BY DATE_TRUNC('day', order_time), product_id;
```

### CREATE SINK

Sinks output processed data to external systems.

#### Basic Syntax

```sql
CREATE SINK [IF NOT EXISTS] sink_name
[FROM table_or_mv | AS select_query]
WITH (
    connector = 'connector_name',
    connector_parameter = 'value',
    ...
)
FORMAT format_type ENCODE encode_type [(encode_options)];
```

#### Kafka Sink

```sql
CREATE SINK orders_sink
FROM processed_orders
WITH (
    connector = 'kafka',
    topic = 'processed-orders',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT UPSERT ENCODE JSON;
```

**With Avro Encoding:**

```sql
CREATE SINK avro_sink
FROM analytics_results
WITH (
    connector = 'kafka',
    topic = 'analytics-output',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT UPSERT ENCODE AVRO (
    schema.registry = 'http://schema-registry:8081'
);
```

#### BigQuery Sink

```sql
CREATE SINK bigquery_sink
FROM daily_metrics
WITH (
    connector = 'bigquery',
    bigquery.local.path = '/path/to/credentials.json',
    bigquery.project = 'my-project',
    bigquery.dataset = 'analytics',
    bigquery.table = 'daily_metrics'
);
```

#### Snowflake Sink

```sql
CREATE SINK snowflake_sink
FROM processed_data
WITH (
    connector = 'snowflake',
    s3.bucket_name = 'staging-bucket',
    s3.credentials.access = 'ACCESS_KEY',
    s3.credentials.secret = 'SECRET_KEY',
    s3.region_name = 'us-east-1',
    s3.path = 'risingwave/staging'
);
```

### CREATE INDEX

Indexes speed up batch queries on non-primary columns.

```sql
-- Basic index
CREATE INDEX idx_orders_customer
ON orders (customer_id);

-- Index with included columns
CREATE INDEX idx_orders_time_customer
ON orders (order_time)
INCLUDE (customer_id, total_price);

-- Index on expression
CREATE INDEX idx_orders_date
ON orders (DATE_TRUNC('day', order_time));
```

---

## Streaming Patterns

### Time Window Functions

#### Tumbling Windows (Non-overlapping)

Fixed-size, contiguous, non-overlapping time intervals.

```sql
-- Count events per 5-minute window
CREATE MATERIALIZED VIEW events_per_window AS
SELECT
    window_start,
    window_end,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users
FROM TUMBLE(events, event_time, INTERVAL '5' MINUTE)
GROUP BY window_start, window_end;
```

**With Multiple Aggregations:**

```sql
CREATE MATERIALIZED VIEW traffic_metrics AS
SELECT
    window_start,
    window_end,
    page_id,
    COUNT(*) AS page_views,
    COUNT(DISTINCT user_id) AS unique_visitors,
    AVG(load_time_ms) AS avg_load_time
FROM TUMBLE(page_events, event_time, INTERVAL '10' MINUTE)
GROUP BY window_start, window_end, page_id;
```

#### Hopping (Sliding) Windows

Fixed-size windows that can overlap.

```sql
-- 2-minute window, sliding every 30 seconds
CREATE MATERIALIZED VIEW rolling_metrics AS
SELECT
    window_start,
    window_end,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount
FROM HOP(
    transactions,
    transaction_time,
    INTERVAL '30' SECOND,  -- Slide interval
    INTERVAL '2' MINUTE    -- Window size
)
GROUP BY window_start, window_end;
```

**Rolling Average Example:**

```sql
CREATE MATERIALIZED VIEW rolling_avg_price AS
SELECT
    window_start,
    window_end,
    symbol,
    AVG(price) AS avg_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM HOP(
    stock_ticks,
    tick_time,
    INTERVAL '1' MINUTE,   -- Update every minute
    INTERVAL '5' MINUTE    -- 5-minute rolling window
)
GROUP BY window_start, window_end, symbol;
```

#### Session Windows

Session windows are supported in batch mode and emit-on-window-close streaming mode.

```sql
-- Session windows with 30-minute gap
CREATE MATERIALIZED VIEW user_sessions AS
SELECT
    user_id,
    window_start AS session_start,
    window_end AS session_end,
    COUNT(*) AS events_in_session
FROM SESSION(
    user_events,
    event_time,
    INTERVAL '30' MINUTE
)
GROUP BY user_id, window_start, window_end
EMIT ON WINDOW CLOSE;
```

### Emit on Window Close

Generates final results only when windows close, improving performance for append-only sinks.

```sql
-- Define source with watermark
CREATE SOURCE sensor_readings (
    sensor_id VARCHAR,
    temperature DOUBLE,
    reading_time TIMESTAMP,
    WATERMARK FOR reading_time AS reading_time - INTERVAL '10' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'sensors',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;

-- Materialized view with emit on window close
CREATE MATERIALIZED VIEW avg_temperature AS
SELECT
    window_start,
    window_end,
    sensor_id,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp,
    MIN(temperature) AS min_temp
FROM TUMBLE(sensor_readings, reading_time, INTERVAL '1' MINUTE)
GROUP BY window_start, window_end, sensor_id
EMIT ON WINDOW CLOSE;
```

### Temporal Joins

Join streaming data with dimension tables using point-in-time lookups.

#### Append-only Temporal Join

```sql
-- Fact table (streaming)
CREATE SOURCE order_events (
    order_id VARCHAR,
    product_id VARCHAR,
    quantity INTEGER,
    order_time TIMESTAMP,
    WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'orders',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;

-- Dimension table
CREATE TABLE products (
    product_id VARCHAR PRIMARY KEY,
    product_name VARCHAR,
    category VARCHAR,
    price DECIMAL
);

-- Temporal join
CREATE MATERIALIZED VIEW enriched_orders AS
SELECT
    o.order_id,
    o.product_id,
    p.product_name,
    p.category,
    o.quantity,
    p.price * o.quantity AS total_amount,
    o.order_time
FROM order_events o
LEFT JOIN products p
    FOR SYSTEM_TIME AS OF PROCTIME()
    ON o.product_id = p.product_id;
```

#### Temporal Join with Delay Filter

Handle late-arriving dimension data:

```sql
CREATE MATERIALIZED VIEW enriched_orders_with_delay AS
SELECT
    o.order_id,
    o.product_id,
    p.product_name,
    o.quantity,
    o.order_time
FROM (
    SELECT * FROM order_events
    WHERE order_time + INTERVAL '5' SECOND < NOW()  -- Delay filter
) o
LEFT JOIN products p
    FOR SYSTEM_TIME AS OF PROCTIME()
    ON o.product_id = p.product_id;
```

### Interval Joins

Time-bounded joins between two streams.

```sql
-- Join clicks with impressions within a time window
CREATE MATERIALIZED VIEW click_through AS
SELECT
    i.impression_id,
    i.ad_id,
    i.user_id,
    c.click_time,
    i.impression_time
FROM impressions i
JOIN clicks c
    ON i.ad_id = c.ad_id
    AND i.user_id = c.user_id
    AND c.click_time BETWEEN i.impression_time
        AND i.impression_time + INTERVAL '1' HOUR;
```

### Deduplication Patterns

#### DISTINCT ON

```sql
-- Get latest order per customer
CREATE MATERIALIZED VIEW latest_orders AS
SELECT DISTINCT ON (customer_id)
    order_id,
    customer_id,
    order_time,
    total_price
FROM orders
ORDER BY customer_id, order_time DESC;
```

#### Deduplication with Window Functions

```sql
CREATE MATERIALIZED VIEW deduplicated_events AS
SELECT * FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY event_id
            ORDER BY event_time DESC
        ) AS rn
    FROM events
)
WHERE rn = 1;
```

### CDC Patterns

#### PostgreSQL CDC with Transformations

```sql
-- Source CDC table
CREATE TABLE source_orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    items JSONB,
    status VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
WITH (
    connector = 'postgres-cdc',
    hostname = 'postgres',
    port = '5432',
    username = 'cdc_user',
    password = 'password',
    database.name = 'app',
    schema.name = 'public',
    table.name = 'orders'
);

-- Transform CDC data
CREATE MATERIALIZED VIEW order_summary AS
SELECT
    id,
    customer_id,
    jsonb_array_length(items) AS item_count,
    status,
    CASE
        WHEN status = 'completed' THEN updated_at - created_at
        ELSE NULL
    END AS completion_time
FROM source_orders;
```

#### Multi-table CDC Join

```sql
-- CDC tables
CREATE TABLE cdc_customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR,
    email VARCHAR
)
WITH (connector = 'postgres-cdc', ...);

CREATE TABLE cdc_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    total DECIMAL
)
WITH (connector = 'postgres-cdc', ...);

-- Join CDC tables
CREATE MATERIALIZED VIEW customer_orders AS
SELECT
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS order_count,
    SUM(o.total) AS lifetime_value
FROM cdc_customers c
LEFT JOIN cdc_orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email;
```

---

## Data Types and Functions

### Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| `BOOLEAN` | True/false | `TRUE`, `FALSE` |
| `SMALLINT` | 2-byte integer | `32767` |
| `INTEGER` | 4-byte integer | `2147483647` |
| `BIGINT` | 8-byte integer | `9223372036854775807` |
| `REAL` | 4-byte float | `3.14` |
| `DOUBLE PRECISION` | 8-byte float | `3.141592653589793` |
| `NUMERIC` | Arbitrary precision | `123.456789` |
| `VARCHAR` | Variable-length string | `'hello'` |
| `BYTEA` | Binary data | `'\x48656c6c6f'` |
| `DATE` | Date without time | `'2024-01-15'` |
| `TIME` | Time without date | `'14:30:00'` |
| `TIMESTAMP` | Date and time | `'2024-01-15 14:30:00'` |
| `TIMESTAMPTZ` | Timestamp with timezone | `'2024-01-15 14:30:00+00'` |
| `INTERVAL` | Time span | `INTERVAL '1' DAY` |
| `JSONB` | Binary JSON | `'{"key": "value"}'` |
| `ARRAY` | Array type | `ARRAY[1, 2, 3]` |
| `STRUCT` | Composite type | `ROW(1, 'test')` |
| `MAP` | Key-value pairs | `MAP{'a': 1, 'b': 2}` |

### JSON/JSONB Functions

#### Extraction and Navigation

```sql
-- Extract values
SELECT
    data->'user'->>'name' AS user_name,           -- Text extraction
    data->'user'->'age' AS user_age,              -- JSON extraction
    data#>>'{user,address,city}' AS city,         -- Path extraction
    jsonb_extract_path_text(data, 'user', 'email') AS email
FROM events;
```

#### JSON Construction

```sql
-- Build JSON objects
SELECT
    jsonb_build_object(
        'user_id', user_id,
        'metrics', jsonb_build_object(
            'count', event_count,
            'total', total_amount
        )
    ) AS result
FROM user_metrics;

-- Aggregate to JSON array
SELECT
    user_id,
    jsonb_agg(
        jsonb_build_object(
            'event_type', event_type,
            'timestamp', event_time
        ) ORDER BY event_time
    ) AS events
FROM user_events
GROUP BY user_id;
```

#### JSON Manipulation

```sql
-- Object aggregation
SELECT
    jsonb_object_agg(key, value) AS config
FROM settings;

-- Strip nulls
SELECT jsonb_strip_nulls('{"a": 1, "b": null}'::jsonb);

-- Pretty print
SELECT jsonb_pretty(data) FROM events;

-- Convert to array
SELECT jsonb_to_array(items) FROM orders;
```

### Date/Time Functions

#### Current Time

```sql
SELECT
    NOW(),                              -- Current timestamp
    CURRENT_DATE,                       -- Current date
    CURRENT_TIME,                       -- Current time
    CURRENT_TIMESTAMP;                  -- Current timestamp with timezone
```

#### Extraction

```sql
SELECT
    EXTRACT(YEAR FROM order_time) AS year,
    EXTRACT(MONTH FROM order_time) AS month,
    EXTRACT(DAY FROM order_time) AS day,
    EXTRACT(HOUR FROM order_time) AS hour,
    EXTRACT(DOW FROM order_time) AS day_of_week,
    EXTRACT(EPOCH FROM order_time) AS unix_timestamp,
    DATE_PART('minute', order_time) AS minute
FROM orders;
```

#### Manipulation

```sql
SELECT
    DATE_TRUNC('hour', event_time) AS hour_start,
    DATE_TRUNC('day', event_time) AS day_start,
    event_time + INTERVAL '1' HOUR AS plus_one_hour,
    event_time - INTERVAL '30' MINUTE AS minus_30_min,
    AGE(NOW(), created_at) AS age
FROM events;
```

### Aggregate Functions

#### Basic Aggregates

```sql
SELECT
    COUNT(*) AS total_count,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(amount) AS total_amount,
    AVG(amount) AS average_amount,
    MIN(amount) AS min_amount,
    MAX(amount) AS max_amount,
    BOOL_AND(is_valid) AS all_valid,
    BOOL_OR(is_fraud) AS any_fraud
FROM transactions;
```

#### Statistical Functions

```sql
SELECT
    STDDEV_POP(amount) AS std_dev_pop,
    STDDEV_SAMP(amount) AS std_dev_sample,
    VAR_POP(amount) AS variance_pop,
    VAR_SAMP(amount) AS variance_sample
FROM transactions
GROUP BY category;
```

#### Ordered-Set Aggregates

```sql
SELECT
    category,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY amount) AS p95,
    MODE() WITHIN GROUP (ORDER BY status) AS most_common_status
FROM orders
GROUP BY category;
```

#### Array and String Aggregation

```sql
SELECT
    user_id,
    ARRAY_AGG(product_id ORDER BY order_time) AS products_ordered,
    STRING_AGG(product_name, ', ' ORDER BY order_time) AS product_list
FROM orders
GROUP BY user_id;
```

### Window Functions

```sql
SELECT
    order_id,
    customer_id,
    total_price,
    -- Ranking
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_time) AS order_num,
    RANK() OVER (PARTITION BY customer_id ORDER BY total_price DESC) AS price_rank,
    DENSE_RANK() OVER (ORDER BY total_price DESC) AS dense_rank,

    -- Navigation
    LAG(total_price, 1) OVER (PARTITION BY customer_id ORDER BY order_time) AS prev_order,
    LEAD(total_price, 1) OVER (PARTITION BY customer_id ORDER BY order_time) AS next_order,
    FIRST_VALUE(total_price) OVER (PARTITION BY customer_id ORDER BY order_time) AS first_order,
    LAST_VALUE(total_price) OVER (
        PARTITION BY customer_id
        ORDER BY order_time
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_order,

    -- Running aggregates
    SUM(total_price) OVER (PARTITION BY customer_id ORDER BY order_time) AS running_total,
    AVG(total_price) OVER (
        PARTITION BY customer_id
        ORDER BY order_time
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg
FROM orders;
```

### String Functions

```sql
SELECT
    -- Concatenation
    CONCAT(first_name, ' ', last_name) AS full_name,
    CONCAT_WS(', ', city, state, country) AS location,

    -- Case conversion
    UPPER(name) AS upper_name,
    LOWER(email) AS lower_email,
    INITCAP(title) AS title_case,

    -- Trimming
    TRIM(description) AS trimmed,
    LTRIM(code, '0') AS left_trimmed,
    RTRIM(path, '/') AS right_trimmed,

    -- Substring
    SUBSTRING(phone FROM 1 FOR 3) AS area_code,
    LEFT(zip_code, 5) AS zip5,
    RIGHT(account_number, 4) AS last_four,

    -- Search and replace
    POSITION('@' IN email) AS at_position,
    REPLACE(url, 'http://', 'https://') AS secure_url,

    -- Split
    SPLIT_PART(email, '@', 2) AS domain,
    REGEXP_SPLIT_TO_ARRAY(tags, ',') AS tag_array
FROM users;
```

#### Regular Expressions

```sql
SELECT
    -- Pattern matching
    REGEXP_MATCH(text, '\d{3}-\d{4}') AS phone_match,
    REGEXP_MATCHES(log_line, '(\w+)=(\w+)', 'g') AS key_values,

    -- Replacement
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS digits_only,

    -- Count matches
    REGEXP_COUNT(description, '\b\w+\b') AS word_count
FROM data;
```

---

## Common Use Cases

### Real-Time Analytics Dashboard

```sql
-- Source with watermark
CREATE SOURCE page_views (
    session_id VARCHAR,
    user_id VARCHAR,
    page_url VARCHAR,
    referrer VARCHAR,
    device_type VARCHAR,
    view_time TIMESTAMP,
    load_time_ms INTEGER,
    WATERMARK FOR view_time AS view_time - INTERVAL '10' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'page-views',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;

-- Real-time metrics per minute
CREATE MATERIALIZED VIEW realtime_metrics AS
SELECT
    window_start,
    window_end,
    COUNT(*) AS page_views,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT session_id) AS sessions,
    AVG(load_time_ms) AS avg_load_time,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY load_time_ms) AS p95_load_time
FROM TUMBLE(page_views, view_time, INTERVAL '1' MINUTE)
GROUP BY window_start, window_end
EMIT ON WINDOW CLOSE;

-- Traffic by device type
CREATE MATERIALIZED VIEW traffic_by_device AS
SELECT
    device_type,
    COUNT(*) AS views,
    COUNT(DISTINCT user_id) AS users
FROM page_views
GROUP BY device_type;

-- Top pages (rolling 5 minutes)
CREATE MATERIALIZED VIEW top_pages AS
SELECT
    window_start,
    page_url,
    COUNT(*) AS view_count
FROM HOP(page_views, view_time, INTERVAL '1' MINUTE, INTERVAL '5' MINUTE)
GROUP BY window_start, page_url
ORDER BY view_count DESC;
```

### Fraud Detection System

```sql
-- Transaction source
CREATE SOURCE transactions (
    transaction_id VARCHAR,
    card_id VARCHAR,
    merchant_id VARCHAR,
    amount DECIMAL,
    location VARCHAR,
    transaction_time TIMESTAMP,
    WATERMARK FOR transaction_time AS transaction_time - INTERVAL '5' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'transactions',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;

-- Velocity check: cards used more than 5 times in 5 minutes
CREATE MATERIALIZED VIEW high_velocity_cards AS
SELECT
    window_start,
    window_end,
    card_id,
    COUNT(*) AS transaction_count,
    SUM(amount) AS total_amount
FROM TUMBLE(transactions, transaction_time, INTERVAL '5' MINUTE)
GROUP BY window_start, window_end, card_id
HAVING COUNT(*) > 5;

-- Geographic anomaly: same card in different locations within 30 minutes
CREATE MATERIALIZED VIEW geo_anomalies AS
SELECT
    t1.card_id,
    t1.location AS location1,
    t2.location AS location2,
    t1.transaction_time AS time1,
    t2.transaction_time AS time2
FROM transactions t1
JOIN transactions t2
    ON t1.card_id = t2.card_id
    AND t1.location != t2.location
    AND t2.transaction_time BETWEEN t1.transaction_time
        AND t1.transaction_time + INTERVAL '30' MINUTE
    AND t1.transaction_time < t2.transaction_time;

-- High-value transactions
CREATE MATERIALIZED VIEW high_value_alerts AS
SELECT
    transaction_id,
    card_id,
    amount,
    merchant_id,
    transaction_time
FROM transactions
WHERE amount > 10000;
```

### Event-Driven Order Processing

```sql
-- Order events
CREATE TABLE order_events (
    order_id VARCHAR PRIMARY KEY,
    customer_id VARCHAR,
    status VARCHAR,
    items JSONB,
    total_amount DECIMAL,
    event_time TIMESTAMP
)
WITH (
    connector = 'kafka',
    topic = 'order-events',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT UPSERT ENCODE JSON;

-- Customer dimension
CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    tier VARCHAR,
    region VARCHAR
)
WITH (connector = 'postgres-cdc', ...);

-- Order fulfillment SLA tracking
CREATE MATERIALIZED VIEW order_sla_tracking AS
SELECT
    o.order_id,
    o.customer_id,
    c.tier,
    o.status,
    o.event_time,
    CASE
        WHEN c.tier = 'premium' THEN INTERVAL '4' HOUR
        WHEN c.tier = 'standard' THEN INTERVAL '24' HOUR
        ELSE INTERVAL '48' HOUR
    END AS sla_deadline,
    o.event_time + CASE
        WHEN c.tier = 'premium' THEN INTERVAL '4' HOUR
        WHEN c.tier = 'standard' THEN INTERVAL '24' HOUR
        ELSE INTERVAL '48' HOUR
    END AS due_by
FROM order_events o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'pending';

-- Revenue by region (real-time)
CREATE MATERIALIZED VIEW revenue_by_region AS
SELECT
    c.region,
    DATE_TRUNC('hour', o.event_time) AS hour,
    COUNT(*) AS order_count,
    SUM(o.total_amount) AS revenue
FROM order_events o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
GROUP BY c.region, DATE_TRUNC('hour', o.event_time);
```

### IoT Sensor Monitoring

```sql
-- Sensor data source
CREATE SOURCE sensor_data (
    sensor_id VARCHAR,
    metric_name VARCHAR,
    value DOUBLE,
    unit VARCHAR,
    reading_time TIMESTAMP,
    WATERMARK FOR reading_time AS reading_time - INTERVAL '30' SECOND
)
WITH (
    connector = 'kafka',
    topic = 'sensor-readings',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT PLAIN ENCODE JSON;

-- Sensor thresholds dimension
CREATE TABLE sensor_thresholds (
    sensor_id VARCHAR PRIMARY KEY,
    metric_name VARCHAR,
    min_value DOUBLE,
    max_value DOUBLE,
    alert_enabled BOOLEAN
);

-- Anomaly detection
CREATE MATERIALIZED VIEW sensor_anomalies AS
SELECT
    s.sensor_id,
    s.metric_name,
    s.value,
    t.min_value,
    t.max_value,
    s.reading_time,
    CASE
        WHEN s.value < t.min_value THEN 'below_threshold'
        WHEN s.value > t.max_value THEN 'above_threshold'
        ELSE 'normal'
    END AS status
FROM sensor_data s
JOIN sensor_thresholds t
    FOR SYSTEM_TIME AS OF PROCTIME()
    ON s.sensor_id = t.sensor_id
    AND s.metric_name = t.metric_name
WHERE t.alert_enabled = TRUE
    AND (s.value < t.min_value OR s.value > t.max_value);

-- Hourly aggregations
CREATE MATERIALIZED VIEW hourly_sensor_stats AS
SELECT
    window_start,
    window_end,
    sensor_id,
    metric_name,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV_SAMP(value) AS std_dev,
    COUNT(*) AS reading_count
FROM TUMBLE(sensor_data, reading_time, INTERVAL '1' HOUR)
GROUP BY window_start, window_end, sensor_id, metric_name
EMIT ON WINDOW CLOSE;
```

### CDC Data Replication Pipeline

```sql
-- Source: PostgreSQL CDC
CREATE TABLE source_products (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR,
    description TEXT,
    price DECIMAL,
    inventory INTEGER,
    category_id INTEGER,
    updated_at TIMESTAMP
)
WITH (
    connector = 'postgres-cdc',
    hostname = 'source-db',
    port = '5432',
    username = 'cdc_user',
    password = 'password',
    database.name = 'ecommerce',
    schema.name = 'public',
    table.name = 'products'
);

-- Transform and enrich
CREATE MATERIALIZED VIEW enriched_products AS
SELECT
    p.product_id,
    p.name,
    p.description,
    p.price,
    p.inventory,
    CASE
        WHEN p.inventory = 0 THEN 'out_of_stock'
        WHEN p.inventory < 10 THEN 'low_stock'
        ELSE 'in_stock'
    END AS stock_status,
    p.updated_at
FROM source_products p;

-- Sink to destination
CREATE SINK products_sink
FROM enriched_products
WITH (
    connector = 'kafka',
    topic = 'enriched-products',
    properties.bootstrap.server = 'localhost:9092'
)
FORMAT UPSERT ENCODE JSON;

-- Sink to data warehouse
CREATE SINK products_warehouse_sink
FROM enriched_products
WITH (
    connector = 'bigquery',
    bigquery.project = 'analytics-project',
    bigquery.dataset = 'ecommerce',
    bigquery.table = 'products'
);
```

---

## Performance Best Practices

### Index Optimization

```sql
-- Create indexes for frequently filtered columns
CREATE INDEX idx_orders_time ON orders (order_time);
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);

-- Index with included columns for covering queries
CREATE INDEX idx_orders_covering ON orders (customer_id)
INCLUDE (order_time, total_amount, status);
```

### Watermark Configuration

- Set watermark delay based on expected data latency
- Use `EMIT ON WINDOW CLOSE` for append-only sinks
- Consider late data handling requirements

```sql
-- Aggressive watermark for low-latency requirements
WATERMARK FOR event_time AS event_time - INTERVAL '1' SECOND

-- Conservative watermark for out-of-order data
WATERMARK FOR event_time AS event_time - INTERVAL '5' MINUTE
```

### Join Optimization

- Use temporal joins for fact-dimension patterns
- Use interval joins for time-bounded stream-stream joins
- Create indexes on dimension tables for lookup performance

```sql
-- Create index on dimension table for temporal join
CREATE INDEX idx_products_id ON products (product_id);

-- Use temporal join instead of regular join
SELECT * FROM orders o
LEFT JOIN products p
    FOR SYSTEM_TIME AS OF PROCTIME()
    ON o.product_id = p.product_id;
```

---

## Documentation References

- **CREATE SOURCE**: https://docs.risingwave.com/sql/commands/sql-create-source
- **CREATE MATERIALIZED VIEW**: https://docs.risingwave.com/sql/commands/sql-create-materialized-view
- **CREATE SINK**: https://docs.risingwave.com/sql/commands/sql-create-sink
- **Time Windows**: https://docs.risingwave.com/processing/sql/time-windows
- **Joins**: https://docs.risingwave.com/processing/sql/joins
- **Aggregate Functions**: https://docs.risingwave.com/sql/functions/aggregate
- **Window Functions**: https://docs.risingwave.com/sql/functions/window-functions
- **JSON Functions**: https://docs.risingwave.com/sql/functions/json
- **Date/Time Functions**: https://docs.risingwave.com/docs/current/sql-function-datetime/
- **Data Types**: https://docs.risingwave.com/sql/data-types/overview
- **Emit on Window Close**: https://docs.risingwave.com/processing/emit-on-window-close
- **PostgreSQL CDC**: https://docs.risingwave.com/ingestion/sources/postgresql/pg-cdc
- **MySQL CDC**: https://docs.risingwave.com/integrations/sources/mysql-cdc


## Streaming & Replication — OLake


> Source: `docs/data_engineering/olake/olake.md`

# OLake Database Replication Expert Assistant

You are an OLake expert assistant. When this skill is invoked, help users with OLake-related tasks including database replication setup, CDC configuration, Iceberg integration, performance optimization, and troubleshooting.

## Your Expertise

You have deep knowledge of:
- OLake architecture (direct-write, Go-Java hybrid, CDC mechanisms)
- Database replication from PostgreSQL, MySQL, MongoDB, Oracle
- Change Data Capture (CDC) with sub-second latency
- Apache Iceberg table format and catalog integration
- Integration with Lakekeeper, LakeFS, DuckDB, Trino, RisingWave
- Performance tuning (chunking strategies, parallelization, partitioning)
- Dagster orchestration for data pipelines
- Production deployment (Docker, Kubernetes, monitoring)
- Troubleshooting replication issues and performance bottlenecks

## Key Reference Materials

You have access to comprehensive OLake documentation in:
- `/home/user/hackathon/research/md/OLake_Comprehensive_Research.md` - Complete feature analysis, benchmarks, configuration
- `/home/user/hackathon/OLAKE_PATTERNS_ARCHITECTURE.md` - Architecture patterns and integration strategies
- `/home/user/hackathon/OLAKE_DATA_MODELS_SCHEMAS_ONTOLOGIES.md` - Data models, type mappings, API contracts
- `/home/user/hackathon/olake-llms.txt` - Quick reference and best practices
- `/home/user/hackathon/research/pdf/storage/Orchestrating PostgreSQL Backups to Iceberg on Cloudflare R2 with Dagster and OLake.md` - Dagster integration guide
- `/home/user/hackathon/research/pdf/storage/Integrating DuckLake, LakeFS, Lakekeeper, and OLake.md` - Lakehouse integration patterns

## When Helping Users

### 1. Initial Setup & Configuration

When users want to set up OLake for the first time:

**Ask diagnostic questions:**
- What is your source database? (PostgreSQL, MySQL, MongoDB, Oracle)
- What is your desired destination? (AWS S3, Cloudflare R2, MinIO, etc.)
- Which Iceberg catalog do you prefer? (Lakekeeper/REST, AWS Glue, JDBC, Hive)
- What is your data volume and change rate?
- Are you doing full load, CDC, or both?

**Provide step-by-step guidance:**

Example response for PostgreSQL CDC:
```
I'll help you set up OLake to replicate PostgreSQL to Iceberg. Here's the complete setup:

**Step 1: Enable logical replication on PostgreSQL**
```sql
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 4;
ALTER SYSTEM SET max_wal_senders = 4;
SELECT pg_reload_conf();
-- Restart PostgreSQL required

CREATE PUBLICATION olake_publication FOR ALL TABLES
  WITH (publish = 'insert,update,delete,truncate');

SELECT pg_create_logical_replication_slot('olake_slot', 'pgoutput');

GRANT SELECT ON ALL TABLES IN SCHEMA public TO olake_user;
```

**Step 2: Create source.json configuration**
```json
{
  "host": "postgres.example.com",
  "port": 5432,
  "database": "production_db",
  "username": "olake_user",
  "password": "${POSTGRES_PASSWORD}",
  "ssl": {"mode": "require"},
  "update_method": {
    "method": "cdc",
    "replication_slot": "olake_slot",
    "publication": "olake_publication",
    "initial_wait_time": 120
  },
  "chunking": {
    "method": "ctid",
    "chunk_size": 10000
  },
  "max_threads": 5
}
```

**Step 3: Create destination.json for Iceberg**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://lakekeeper.example.com/catalog",
    "rest_catalog_credential": "${LAKEKEEPER_TOKEN}",
    "iceberg_s3_path": "s3://lakehouse/warehouse",
    "s3_endpoint": "https://s3.amazonaws.com",
    "aws_region": "us-east-1",
    "aws_access_key": "${AWS_ACCESS_KEY}",
    "aws_secret_key": "${AWS_SECRET_KEY}",
    "iceberg_db": "production",
    "write_strategy": "multi-spec-concurrent",
    "compression": "zstd",
    "target_file_size_mb": 256
  }
}
```

**Step 4: Run discovery and sync**
```bash
docker run --rm -v $(pwd)/config:/mnt/config \
  olakego/source-postgres:latest \
  discover --config /mnt/config/source.json > config/streams.json

docker run --rm -v $(pwd)/config:/mnt/config -v $(pwd)/state:/state \
  olakego/source-postgres:latest \
  sync --config /mnt/config/source.json \
       --catalog /mnt/config/streams.json \
       --destination /mnt/config/destination.json
```
```

### 2. Performance Optimization

When users report slow replication or high latency:

**Diagnostic checklist:**
- What is the current throughput (rows/sec)?
- What is the CDC lag? (check `olake_cdc_lag_seconds` metric)
- How many tables are being replicated?
- What is the average row size?
- Are there any errors in the logs?

**Optimization strategies:**

**For throughput:**
```json
{
  "max_threads": 8,  // Increase table-level parallelism
  "chunking": {
    "method": "ctid",
    "chunk_size": 10000,
    "parallel_chunks": 16  // Increase chunk parallelism
  },
  "writer": {
    "write_strategy": "multi-spec-concurrent",  // Fastest write mode
    "max_concurrent_writes": 32
  }
}
```

**For CDC lag:**
```json
{
  "update_method": {
    "initial_wait_time": 60  // Reduce wait time
  },
  "writer": {
    "target_file_size_mb": 128  // Smaller files for faster commits
  }
}
```

**For large tables:**
```json
{
  "partition_spec": {
    "events": [
      {"type": "year", "field": "event_timestamp"},
      {"type": "month", "field": "event_timestamp"}
    ]
  }
}
```

### 3. Partitioning Strategy

When users ask about partitioning:

**Explain partitioning benefits:**
- Query performance: 10-100x faster with partition pruning
- File organization: Logical grouping of related data
- Lifecycle management: Easy to archive/delete old partitions
- Parallel processing: Each partition can be processed independently

**Recommend strategies based on use case:**

**Time-series data:**
```json
{
  "partition_spec": {
    "events": [
      {"type": "day", "field": "event_timestamp"}  // Daily partitions
    ],
    "metrics": [
      {"type": "month", "field": "metric_date"}  // Monthly for aggregated metrics
    ]
  }
}
```

**Categorical data:**
```json
{
  "partition_spec": {
    "users": [
      {"type": "identity", "field": "country_code"}  // Partition by country
    ],
    "orders": [
      {"type": "bucket", "field": "customer_id", "num_buckets": 16}  // Hash partitioning
    ]
  }
}
```

**Hybrid (time + category):**
```json
{
  "partition_spec": {
    "transactions": [
      {"type": "day", "field": "transaction_date"},
      {"type": "truncate", "field": "account_id", "width": 1000}
    ]
  }
}
```

### 4. Integration Patterns

**Lakekeeper + OLake:**
```python
# OLake writes to Iceberg via Lakekeeper REST catalog
# Query the replicated data:

from pyiceberg.catalog import RestCatalog

catalog = RestCatalog(
    name="lakekeeper",
    uri="https://lakekeeper.example.com/catalog",
    warehouse="main",
    token="<token>"
)

tables = catalog.list_tables("production")
# Tables replicated by OLake appear here

table = catalog.load_table("production.orders")
df = table.scan().to_pandas()
```

**Dagster + OLake:**
```python
from dagster import asset, op, job, ScheduleDefinition
import subprocess

@op
def sync_postgres_to_iceberg():
    result = subprocess.run([
        "docker", "run", "--rm",
        "-v", "/config:/mnt/config",
        "olakego/source-postgres:latest",
        "sync", "--config", "/mnt/config/source.json",
        "--catalog", "/mnt/config/streams.json",
        "--destination", "/mnt/config/destination.json"
    ], check=True)
    return result.returncode

@job
def postgres_replication():
    sync_postgres_to_iceberg()

# Hourly CDC sync
hourly_schedule = ScheduleDefinition(
    job=postgres_replication,
    cron_schedule="0 * * * *"
)
```

**RisingWave + OLake:**
```sql
-- RisingWave reads from OLake-replicated Iceberg tables
CREATE SOURCE orders_iceberg
WITH (
    connector = 'iceberg',
    type = 'append-only',
    warehouse.path = 's3://lakehouse/warehouse',
    catalog.type = 'rest',
    catalog.uri = 'https://lakekeeper.example.com/catalog',
    database.name = 'production',
    table.name = 'orders'
);

-- Real-time materialized view
CREATE MATERIALIZED VIEW hourly_metrics AS
SELECT
    DATE_TRUNC('hour', order_timestamp) AS hour,
    COUNT(*) AS order_count,
    SUM(total_amount) AS revenue
FROM orders_iceberg
GROUP BY 1;
```

**DuckDB + OLake:**
```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL iceberg; LOAD iceberg;")

# Query OLake-replicated Iceberg tables
result = con.execute("""
    SELECT
        DATE_TRUNC('day', order_date) AS day,
        COUNT(*) AS orders,
        SUM(total_amount) AS revenue
    FROM iceberg_scan('production.orders', allow_moved_paths := true)
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY 1
""").fetchdf()
```

### 5. Troubleshooting Common Issues

**Issue 1: CDC Lag Increasing**

Symptoms:
- `olake_cdc_lag_seconds > 60`
- Replication falling behind source changes

Diagnosis:
```sql
-- Check PostgreSQL replication slot lag
SELECT
    slot_name,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS lag
FROM pg_replication_slots
WHERE slot_name = 'olake_slot';
```

Solutions:
1. **Increase parallelism:**
   ```json
   {"max_threads": 10, "chunking": {"parallel_chunks": 20}}
   ```

2. **Optimize Iceberg writes:**
   ```json
   {"writer": {"write_strategy": "multi-spec-concurrent", "max_concurrent_writes": 32}}
   ```

3. **Scale up resources:**
   ```yaml
   resources:
     limits: {memory: "16Gi", cpu: "8"}
   ```

**Issue 2: Small File Problem**

Symptoms:
- Many small Parquet files (<10 MB)
- Query performance degrading

Diagnosis:
```sql
-- Count files per partition
SELECT
    partition,
    COUNT(*) AS file_count,
    AVG(file_size_in_bytes) / 1024 / 1024 AS avg_mb
FROM iceberg_metadata_log_entries
GROUP BY 1
HAVING COUNT(*) > 100;
```

Solutions:
1. **Increase target file size:**
   ```json
   {"writer": {"target_file_size_mb": 512}}
   ```

2. **Change write strategy:**
   ```json
   {"writer": {"write_strategy": "single-spec-concurrent"}}
   ```

3. **Run Iceberg compaction:**
   ```sql
   CALL system.rewrite_data_files('production.orders');
   ```

**Issue 3: Schema Evolution Failure**

Symptoms:
- New columns not appearing in Iceberg table
- Type mismatch errors

Solutions:
1. **Verify OLake detected schema change:**
   - Check logs for "Schema change detected"
   - Ensure `discover` was re-run if needed

2. **Check type compatibility:**
   - PostgreSQL JSONB → Iceberg string (serialized)
   - Arrays must be homogeneous in Iceberg
   - ENUM → string conversion

3. **Manual schema update (if needed):**
   ```sql
   ALTER TABLE production.orders
   ADD COLUMN discount_amount decimal(10,2);
   ```

**Issue 4: Connection Pool Exhaustion**

Symptoms:
- "remaining connection slots are reserved"
- Connection timeout errors

Solutions:
```json
{
  "source": {
    "max_threads": 3,  // Reduce concurrent connections
    "connection_pool_size": 10,
    "connection_timeout": 30
  }
}
```

Or increase PostgreSQL max_connections:
```sql
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

### 6. Monitoring & Alerting

**Setup Prometheus metrics:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'olake'
    static_configs:
      - targets: ['olake:8080']
```

**Key metrics to monitor:**
```prometheus
# Throughput
rate(olake_rows_synced_total[5m])
rate(olake_bytes_synced_total[5m])

# Latency
olake_cdc_lag_seconds

# Errors
rate(olake_sync_errors_total[5m])

# State
olake_current_lsn
olake_checkpoint_timestamp
```

**Alerting rules:**
```yaml
- alert: HighCDCLag
  expr: olake_cdc_lag_seconds > 60
  for: 5m
  annotations:
    summary: "OLake CDC lag exceeded 60 seconds"

- alert: SyncErrors
  expr: rate(olake_sync_errors_total[5m]) > 0.1
  for: 2m
  annotations:
    summary: "OLake sync errors detected"
```

### 7. Production Deployment Best Practices

**Docker Compose:**
```yaml
version: '3.8'
services:
  olake:
    image: olakego/source-postgres:latest
    volumes:
      - ./config:/mnt/config
      - ./state:/state
    environment:
      - STATE_DIR=/state
      - LOG_LEVEL=info
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - AWS_ACCESS_KEY=${AWS_ACCESS_KEY}
      - AWS_SECRET_KEY=${AWS_SECRET_KEY}
    command: >
      sync
      --config /mnt/config/source.json
      --catalog /mnt/config/streams.json
      --destination /mnt/config/destination.json
    restart: unless-stopped
    deploy:
      resources:
        limits: {memory: 8G, cpus: '4'}
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: olake-postgres
spec:
  serviceName: olake
  replicas: 1  # Single replica for CDC (state management)
  template:
    spec:
      containers:
      - name: olake
        image: olakego/source-postgres:latest
        resources:
          limits: {memory: "8Gi", cpu: "4"}
          requests: {memory: "4Gi", cpu: "2"}
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: olake-secrets
              key: postgres-password
        volumeMounts:
        - name: config
          mountPath: /mnt/config
        - name: state
          mountPath: /state
  volumeClaimTemplates:
  - metadata:
      name: state
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

**Secrets Management:**
```bash
# Use environment variables, never hardcode
export POSTGRES_PASSWORD=$(op read "op://vault/postgres/password")
export AWS_SECRET_KEY=$(op read "op://vault/aws/secret")
export LAKEKEEPER_TOKEN=$(op read "op://vault/lakekeeper/token")

# Or use SOPS for encrypted config files
sops -d config/source.encrypted.json > config/source.json
```

## Common User Scenarios

### Scenario: "I need to replicate PostgreSQL to S3 for analytics"

Response pattern:
1. Confirm requirements (volume, latency, budget)
2. Recommend OLake + Iceberg + Lakekeeper stack
3. Provide complete setup guide (see Initial Setup above)
4. Suggest partitioning strategy based on data characteristics
5. Recommend query engine (DuckDB for embedded, Trino for distributed)
6. Show cost comparison vs Fivetran (20x cheaper)

### Scenario: "Replication is slow, what should I do?"

Response pattern:
1. Ask for current metrics (throughput, lag, resource usage)
2. Review configuration (chunking, parallelism, write strategy)
3. Suggest optimization based on bottleneck:
   - CPU-bound: Increase parallelism
   - Memory-bound: Reduce chunk size or parallelism
   - Network-bound: Enable compression, increase batch size
   - Disk I/O-bound: Use faster storage, adjust file sizes
4. Provide optimized configuration
5. Show how to monitor improvements

### Scenario: "How do I add a new table to replication?"

Response pattern:
```
Adding a new table is straightforward:

**Option 1: Automatic (all tables)**
If you're using `FOR ALL TABLES` publication, the table will be automatically discovered on next sync.

**Option 2: Explicit table list**
1. Add table to source.json:
   ```json
   {"tables": ["public.users", "public.orders", "public.new_table"]}
   ```

2. Re-run discovery:
   ```bash
   docker run --rm -v $(pwd)/config:/mnt/config \
     olakego/source-postgres:latest \
     discover --config /mnt/config/source.json > config/streams.json
   ```

3. OLake will automatically create the Iceberg table on next sync
```

### Scenario: "Can I use OLake with multiple databases?"

Response pattern:
```
Yes! You have two options:

**Option 1: Separate OLake instances (recommended)**
- One OLake container per source database
- Independent state management and scaling
- Clearer monitoring and troubleshooting

Example:
```yaml
services:
  olake-db1:
    image: olakego/source-postgres:latest
    volumes:
      - ./config/db1:/mnt/config
      - ./state/db1:/state

  olake-db2:
    image: olakego/source-postgres:latest
    volumes:
      - ./config/db2:/mnt/config
      - ./state/db2:/state
```

**Option 2: Dagster orchestration with dynamic jobs**
```python
DATABASES = ["db1", "db2", "db3"]

@op
def sync_database(context, db_name: str):
    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"/config/{db_name}:/mnt/config",
        "olakego/source-postgres:latest",
        "sync", ...
    ])

@job
def sync_all_databases():
    for db in DATABASES:
        sync_database(db)
```
```

## Key Talking Points

### Performance
- **319,562 RPS peak** for PostgreSQL full load
- **Sub-second CDC latency** (P50 < 500ms)
- **20x cheaper** than Fivetran ($300 vs $6,000/month)
- **63x faster** than Airbyte for large-scale replication

### Architecture
- **Direct-write**: No Kafka needed (unlike Debezium)
- **Go-Java hybrid**: Performance + mature Iceberg libraries
- **ACID guarantees**: Full transactional consistency via Iceberg
- **Exactly-once semantics**: State checkpointing prevents duplicates

### Flexibility
- **4 source types**: PostgreSQL, MySQL, MongoDB, Oracle
- **4 catalog backends**: REST, Glue, JDBC, Hive
- **Any S3-compatible storage**: AWS, Cloudflare R2, MinIO, GCS, Azure Blob
- **Open source**: Apache 2.0 license, self-hosted

### Integration
- **Query engines**: DuckDB, Trino, Spark, Presto, RisingWave
- **Orchestration**: Dagster, Airflow, Prefect
- **Versioning**: LakeFS for Git-like data control
- **Catalog**: Lakekeeper for governance and security

## When NOT to Use OLake

Be honest about limitations:
- **Need 100+ source connectors?** → Recommend Airbyte or Fivetran
- **Kafka-first architecture?** → Debezium might be better fit
- **Sub-100ms latency required?** → Consider Estuary or custom streaming
- **Need GUI for configuration?** → OLake is CLI/config-file based (UI in beta)
- **Oracle CDC needed now?** → Wait for OLake Oracle CDC release, or use Debezium

## Resources to Reference

Always point users to:
- Official docs: https://olake.io/docs
- GitHub: https://github.com/OLakeHQ/olake
- Integration guides in `/home/user/hackathon/research/`
- Quick reference: `/home/user/hackathon/olake-llms.txt`

---

Remember: Your goal is to help users successfully replicate their databases to data lakes with OLake. Be thorough, provide complete examples, and always consider performance, cost, and operational simplicity.


> Source: `docs/data_engineering/olake/olake-database-replication-guide.md`

# OLake: Comprehensive Research Documentation

**Date:** 2025-11-18  
**Purpose:** In-depth analysis of OLake's core features, capabilities, and technical implementation for lakehouse data replication

---

## Executive Summary

OLake is an open-source, high-performance database replication tool built in Golang that captures changes from operational databases and loads them into data lakes using open table formats like Apache Iceberg. It positions itself as the fastest open-source solution for database-to-lakehouse pipelines, offering up to 27x faster CDC performance and 20x cost reduction compared to commercial alternatives.

**Key Statistics:**
- **PostgreSQL Full Load:** 319,562 RPS (46,262 RPS for 4 billion rows)
- **PostgreSQL CDC:** 36,982 RPS for 50 million changes
- **MongoDB:** 35,694 records/sec (230 million rows in 46 minutes for 664GB dataset)
- **MySQL:** 64,334 RPS for full load operations
- **Cost:** $300/month vs $6,000/month (Fivetran) or $7,200/month (Airbyte)

---

## 1. Source Connectors

### 1.1 PostgreSQL Connector

#### Supported Modes
OLake supports four distinct replication modes for PostgreSQL:

1. **Full Refresh**: Complete table snapshots
2. **Incremental Sync**: Delta updates based on cursor columns
3. **Pgoutput-based Full Refresh + CDC**: Initial snapshot followed by continuous CDC
4. **Strict CDC**: Pure change data capture without initial load

#### Connection Requirements
- PostgreSQL version 10 or higher
- Superuser or replication role privileges
- Network connectivity to PostgreSQL instance
- Compatible with AWS RDS, Aurora, and Supabase

#### Logical Replication Setup

**Step 1: Configure WAL Level**
```sql
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 4;
ALTER SYSTEM SET max_wal_senders = 4;
SELECT pg_reload_conf();
```

**Step 2: Grant Replication Permissions**
```sql
ALTER ROLE olake_user WITH REPLICATION;
```

**Step 3: Create Publication and Replication Slot**
```sql
CREATE PUBLICATION olake_publication FOR ALL TABLES 
  WITH (publish = 'insert,update,delete,truncate');

SELECT * FROM pg_create_logical_replication_slot('olake_slot', 'pgoutput');
```

#### Configuration Example (source.json)
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "production_db",
  "username": "olake_user",
  "password": "<PG_PASSWORD>",
  "ssl": { "mode": "disable" },
  "update_method": {
    "replication_slot": "olake_slot",
    "publication": "olake_publication",
    "initial_wait_time": 120
  },
  "max_threads": 5,
  "backoff_retry_count": 3
}
```

#### Chunking Strategies
PostgreSQL connector implements three chunking approaches for parallel processing:

1. **CTID-based chunking**: Uses PostgreSQL's internal tuple identifier for physical row addressing
2. **Primary key range chunking**: Splits data based on PK value ranges
3. **User-defined column chunking**: Allows custom partitioning on indexed columns

#### Authentication Methods
- Username/password authentication
- SSL/TLS encrypted connections
- IAM authentication for AWS RDS (via connection string parameters)
- Certificate-based authentication

### 1.2 MySQL Connector

#### Supported Modes
1. **Full Refresh**: Complete table snapshots
2. **Incremental Sync**: Cursor-based delta loading
3. **Binlog-based Full Refresh + CDC**: Snapshot + continuous replication
4. **Strict CDC**: Pure binlog-based CDC

#### Binlog Configuration Requirements
MySQL must be configured with:
- `binlog_format = ROW` (required for CDC)
- `binlog_row_image = FULL` (captures complete before/after images)
- Binary logging enabled
- Appropriate GTID settings for high availability setups

#### Configuration Example (source.json)
```json
{
  "hosts": ["mysql.example.com"],
  "username": "olake_user",
  "password": "<MYSQL_PASSWORD>",
  "database": "production",
  "port": 3306,
  "tls_skip_verify": false,
  "update_method": {
    "method": "binlog",
    "server_id": 12345
  },
  "max_threads": 8,
  "backoff_retry_count": 3
}
```

#### Chunking Strategies
1. **Auto-increment primary key ranges**: Optimal for tables with sequential IDs
2. **Indexed column-based chunking**: Leverages secondary indexes
3. **Partition-aware chunking**: Aligns with MySQL table partitioning

#### Performance Characteristics
- **Full Load:** 64,334 RPS (9x faster than Airbyte)
- **CDC:** 1,000,000 records/sec for 10GB datasets
- Low latency binlog reading with parallel processing

### 1.3 MongoDB Connector

#### Supported Modes
1. **Full Refresh**: Complete collection snapshots
2. **Incremental Sync**: Cursor-based incremental loading
3. **Oplog-based Full Refresh + CDC**: Initial snapshot + change streams
4. **Strict CDC**: Pure oplog/change stream replication

#### Requirements
- MongoDB replica set or sharded cluster (oplogs require replication)
- MongoDB 3.6+ for change streams
- Appropriate authentication credentials
- Read access to `local.oplog.rs` collection

#### Configuration Example (source.json)
```json
{
  "hosts": ["mongo1.example.com:27017", "mongo2.example.com:27017"],
  "username": "olake_user",
  "password": "<MONGO_PASSWORD>",
  "authdb": "admin",
  "replica_set": "rs0",
  "read_preference": "secondaryPreferred",
  "srv": false,
  "database": "production",
  "max_threads": 10,
  "backoff_retry_count": 3,
  "chunking_strategy": "objectid"
}
```

#### Chunking Strategies
MongoDB connector supports three intelligent chunking approaches:

1. **ObjectID-based chunking**: Leverages MongoDB's default `_id` field for time-based partitioning
2. **Shard key-based chunking**: Aligns with existing sharding strategy for optimal distribution
3. **Adaptive sampling chunking**: Analyzes collection statistics to determine optimal chunk boundaries

#### Performance Characteristics
- **Full Load:** 35,694 records/sec
- **Large Dataset:** 230 million rows (664GB) in 46 minutes
- **CDC Performance:** 20x faster than Airbyte, 15x faster than Debezium

#### Change Streams Implementation
- Multi-threaded per-stream approach
- Aggregation pipeline filtering for selective replication
- Resume token coordination for fault tolerance
- Transaction boundary preservation

### 1.4 Oracle Connector

#### Supported Modes
1. **Full Refresh**: Complete table snapshots
2. **Incremental Sync**: Timestamp or sequence-based incremental loading
3. **CDC**: In development (likely using LogMiner or XStream)

#### Configuration Example (source.json)
```json
{
  "host": "oracle.example.com",
  "username": "olake_user",
  "password": "<ORACLE_PASSWORD>",
  "service_name": "ORCL",
  "port": 1521,
  "max_threads": 5,
  "retry_count": 3,
  "jdbc_url_params": "?option=value",
  "ssl": {
    "enabled": false
  }
}
```

#### Status
- Full refresh and incremental sync: Fully supported
- CDC capabilities: Work in progress
- Compatible with Oracle 11g and higher

### 1.5 Kafka Connector (In Development)

#### Planned Capabilities
- Consume from Kafka topics
- Schema registry integration (Avro, Protobuf, JSON Schema)
- Offset management and checkpointing
- Consumer group configuration

#### Status
Listed as work-in-progress in OLake roadmap.

---

## 2. Change Data Capture (CDC) Implementation

### 2.1 CDC Architecture Overview

OLake implements a **direct-write CDC architecture** that eliminates intermediate buffering by embedding destination writers directly into source drivers. This design choice reduces latency by 40-60% compared to traditional queue-based approaches.

#### Core Components
1. **Single WAL/Binlog/Oplog Reader**: Maintains database log position
2. **Multi-writer Demultiplexer**: Distributes events to parallel writers
3. **Transaction Coordinator**: Preserves transaction boundaries
4. **State Manager**: Tracks replication progress and checkpoints

### 2.2 PostgreSQL CDC Deep Dive

#### Logical Replication Mechanism
OLake uses the `pgoutput` logical decoding plugin, which is PostgreSQL's native replication protocol:

**Process Flow:**
1. Client connects to replication slot
2. PostgreSQL streams WAL entries in real-time
3. OLake decodes pgoutput messages using `pglogrepl` library
4. Changes are demultiplexed to appropriate stream handlers
5. Each handler writes to Iceberg table maintaining transaction boundaries

#### CDC Message Types Handled
- **INSERT**: New row creations
- **UPDATE**: Row modifications (includes before/after images)
- **DELETE**: Row deletions
- **TRUNCATE**: Table truncation events
- **BEGIN/COMMIT**: Transaction boundaries

#### WAL Position Management
```json
{
  "stream_state": {
    "orders": {
      "lsn": "0/1A2B3C4D",
      "last_commit_time": "2025-01-15T10:30:45Z"
    }
  }
}
```

### 2.3 MySQL CDC Deep Dive

#### Binlog Reading Implementation
OLake leverages the `go-mysql` library to read MySQL binary logs:

**Process Flow:**
1. Connect to MySQL as a replication slave
2. Request binlog events starting from saved position
3. Parse row events (WriteRowsEvent, UpdateRowsEvent, DeleteRowsEvent)
4. Distribute events to parallel writers per table
5. Maintain transaction integrity through GTID tracking

#### GTID-based Position Tracking
```json
{
  "stream_state": {
    "products": {
      "gtid": "3E11FA47-71CA-11E3-9C27-E80844898F82:1-23",
      "binlog_file": "mysql-bin.000042",
      "binlog_position": 1234567
    }
  }
}
```

### 2.4 MongoDB CDC Deep Dive

#### Change Streams vs Oplog
OLake supports both approaches:

**Change Streams (Preferred for MongoDB 3.6+):**
- Native API with automatic resume capability
- Resume tokens for fault tolerance
- Transaction-aware change notifications

**Oplog Tailing (Legacy):**
- Direct reading of `local.oplog.rs`
- Manual resume token management
- Higher performance but requires more careful state handling

#### Resume Token Management
```json
{
  "stream_state": {
    "user_events": {
      "resume_token": {
        "_data": "8264B3C8F8000000012B042C0100296E5A100464..."
      },
      "last_operation_time": "2025-01-15T10:30:45Z"
    }
  }
}
```

### 2.5 Initial Snapshot vs Incremental Replication

#### Hybrid Sync Coordination
OLake implements a sophisticated hybrid approach:

**Phase 1: Initial Snapshot (Backfill)**
- Parallel chunked reads from source database
- Writes to Iceberg as initial snapshots
- Checkpoint tracking per chunk for resumability

**Phase 2: CDC Catchup**
- CDC reader starts from snapshot-consistent position
- Processes accumulated changes during backfill
- Merges/applies changes to Iceberg tables

**Phase 3: Continuous Replication**
- Real-time change application
- Sub-second latency from source commit to Iceberg availability
- Automatic schema evolution handling

#### Coordination Strategy
```
Timeline:
T0 ─────────────────────> T1 ─────────> T2 ────────────> Ongoing
│                         │            │
│                         │            │
Initial Snapshot         CDC          Continuous
(Parallel Chunks)      Catchup       Replication
                          
LSN/GTID Position:
─────────────[SNAPSHOT]──────────────────────>
              ↑
              └─ CDC starts here
```

### 2.6 State Management and Checkpointing

#### State Storage Architecture
OLake maintains multiple levels of state:

1. **Global State**: Overall sync progress
2. **Stream-level State**: Individual table/collection progress
3. **Chunk Tracking**: Processed chunks for resumability
4. **CDC Position**: LSN/GTID/resume token tracking

#### State File Structure (state.json)
```json
{
  "version": "1.0",
  "sync_id": "sync_abc123",
  "last_updated": "2025-01-15T10:30:45Z",
  "mode": "cdc",
  "streams": {
    "public.orders": {
      "sync_mode": "incremental_cdc",
      "state": {
        "type": "postgres_lsn",
        "lsn": "0/1A2B3C4D",
        "snapshot_completed": true,
        "last_commit_timestamp": "2025-01-15T10:30:44Z"
      },
      "chunks_completed": [
        {"start": 0, "end": 100000},
        {"start": 100001, "end": 200000}
      ]
    }
  },
  "statistics": {
    "records_processed": 1234567,
    "bytes_processed": 4567890123,
    "errors_encountered": 0
  }
}
```

#### Checkpoint Frequency
- **During Backfill**: Every 10,000 records or 1 minute (configurable)
- **During CDC**: Every transaction commit or every 1,000 changes
- **Failure Recovery**: Resume from last checkpoint with at-least-once semantics

### 2.7 Error Handling and Retry Logic

#### Error Classification
OLake categorizes errors into three types:

1. **Transient Errors**: Network blips, temporary resource unavailability
   - Strategy: Exponential backoff with jitter
   - Max retries: 3-5 attempts (configurable)
   - Example: Connection timeout, rate limiting

2. **Permanent Errors**: Schema mismatches, authentication failures
   - Strategy: Immediate failure with detailed logging
   - Requires manual intervention
   - Example: Invalid credentials, missing permissions

3. **Data Errors**: Invalid data format, constraint violations
   - Strategy: Skip with logging or dead-letter queue
   - Configurable behavior (fail vs skip vs DLQ)
   - Example: Type conversion failure, unique constraint violation

#### Retry Configuration
```json
{
  "retry_policy": {
    "max_retries": 3,
    "initial_backoff_ms": 1000,
    "max_backoff_ms": 30000,
    "backoff_multiplier": 2.0,
    "jitter": true
  }
}
```

#### Circuit Breaker Pattern
OLake implements circuit breaker for source database protection:
- Opens circuit after 5 consecutive failures
- Half-open state after 60 seconds
- Resets after 3 successful operations

---

## 3. Destination Writers: Apache Iceberg Focus

### 3.1 Iceberg Writer Architecture

OLake's Iceberg writer is implemented as a Java-based gRPC service that integrates with the official Apache Iceberg libraries. This hybrid Golang-Java architecture leverages the mature Iceberg ecosystem while maintaining OLake's high-performance Go core.

#### Components
1. **Go Driver**: Handles source data extraction and change processing
2. **gRPC Bridge**: Marshals data between Go and Java processes
3. **Java Iceberg Service**: Executes Iceberg operations (table creation, snapshot commits)
4. **Catalog Client**: Interfaces with various catalog backends

### 3.2 Catalog Integration

OLake supports four catalog types with comprehensive authentication options:

#### 3.2.1 AWS Glue Catalog

**Configuration Example:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "glue",
    "glue_catalog_id": "123456789012",
    "iceberg_s3_path": "s3://my-lakehouse/warehouse",
    "aws_region": "us-east-1",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "production"
  }
}
```

**Required AWS Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "glue:CreateTable",
        "glue:CreateDatabase",
        "glue:GetTable",
        "glue:GetDatabase",
        "glue:UpdateTable",
        "glue:DeleteTable"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-lakehouse/*",
        "arn:aws:s3:::my-lakehouse"
      ]
    }
  ]
}
```

**Features:**
- Native AWS integration
- IAM-based access control
- Automatic metadata encryption
- Cross-region replication support

#### 3.2.2 REST Catalog

REST catalog is the most flexible option, supporting multiple implementations:
- Nessie (Git-like data versioning)
- Polaris (Apache open catalog)
- Unity Catalog (Databricks)
- Lakekeeper (Rust-based open catalog)
- Cloudflare R2 S3 Tables

**Generic REST Configuration:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "http://catalog.example.com:8181",
    "iceberg_s3_path": "s3://my-lakehouse/warehouse",
    "s3_endpoint": "https://s3.amazonaws.com",
    "aws_region": "us-east-1",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "production"
  }
}
```

**Authentication Methods:**

1. **Bearer Token:**
```json
{
  "token": "<BEARER_TOKEN>"
}
```

2. **OAuth2:**
```json
{
  "oauth2_server_uri": "https://auth.example.com/oauth2/token",
  "credential": "client_id:client_secret",
  "scope": "catalog:read catalog:write"
}
```

3. **AWS Signature V4:**
```json
{
  "sigv4": {
    "service": "s3tables",
    "region": "us-east-1"
  }
}
```

**Cloudflare R2 S3 Tables Example:**
```json
{
  "catalog_type": "rest",
  "rest_catalog_url": "https://<account-id>.r2.cloudflarestorage.com/catalog",
  "iceberg_s3_path": "s3://<bucket-name>",
  "s3_endpoint": "https://<account-id>.r2.cloudflarestorage.com",
  "aws_region": "auto",
  "token": "<CLOUDFLARE_API_TOKEN>",
  "iceberg_db": "production"
}
```

#### 3.2.3 JDBC Catalog

**Configuration Example:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "jdbc",
    "jdbc_url": "jdbc:postgresql://catalog-db.example.com:5432/iceberg_catalog",
    "jdbc_username": "iceberg_user",
    "jdbc_password": "<JDBC_PASSWORD>",
    "iceberg_s3_path": "s3://my-lakehouse/warehouse",
    "aws_region": "us-east-1",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "production"
  }
}
```

**Supported Databases:**
- PostgreSQL (recommended)
- MySQL
- SQLite (development only)

**Schema:**
```sql
CREATE TABLE iceberg_tables (
  catalog_name VARCHAR(255),
  table_namespace VARCHAR(255),
  table_name VARCHAR(255),
  metadata_location TEXT,
  previous_metadata_location TEXT,
  PRIMARY KEY (catalog_name, table_namespace, table_name)
);

CREATE TABLE iceberg_namespace_properties (
  catalog_name VARCHAR(255),
  namespace VARCHAR(255),
  property_key VARCHAR(255),
  property_value TEXT,
  PRIMARY KEY (catalog_name, namespace, property_key)
);
```

#### 3.2.4 Hive Metastore Catalog

**Configuration Example:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "hive",
    "hive_metastore_uri": "thrift://hive-metastore.example.com:9083",
    "iceberg_s3_path": "s3://my-lakehouse/warehouse",
    "aws_region": "us-east-1",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "production"
  }
}
```

**Considerations:**
- Legacy option, REST catalog preferred for new deployments
- Requires Hive metastore infrastructure
- Limited transaction isolation compared to modern catalogs

### 3.3 Partition Strategies and Configuration

Iceberg partitioning in OLake is configured per-stream in the `streams.json` file:

#### Partition Specification Examples

**1. Time-based Partitioning (Most Common)**
```json
{
  "stream": "public.orders",
  "partition_spec": [
    {
      "field": "created_at",
      "transform": "day"
    }
  ]
}
```

**Supported Time Transforms:**
- `year(timestamp)`: Partition by year
- `month(timestamp)`: Partition by year-month
- `day(timestamp)`: Partition by date (YYYY-MM-DD)
- `hour(timestamp)`: Partition by hour

**2. Identity Partitioning (Categorical Data)**
```json
{
  "stream": "public.events",
  "partition_spec": [
    {
      "field": "event_type",
      "transform": "identity"
    },
    {
      "field": "created_at",
      "transform": "day"
    }
  ]
}
```

**3. Bucket Partitioning (Hash Distribution)**
```json
{
  "stream": "public.users",
  "partition_spec": [
    {
      "field": "user_id",
      "transform": "bucket[16]"
    }
  ]
}
```

**4. Truncate Partitioning (String Prefixes)**
```json
{
  "stream": "public.logs",
  "partition_spec": [
    {
      "field": "trace_id",
      "transform": "truncate[8]"
    },
    {
      "field": "timestamp",
      "transform": "hour"
    }
  ]
}
```

#### Partition Evolution

Iceberg supports changing partition strategies over time without rewriting data:

**Example Timeline:**
```
T0: No partitioning → identity partition spec
T1: Add day(timestamp) partition
T2: Change to hour(timestamp) for recent data

Result: Old data remains with original partitioning,
        new data uses new partitioning,
        queries work seamlessly across all data
```

**Configuration in streams.json:**
```json
{
  "stream": "public.events",
  "partition_spec": [
    {
      "field": "created_at",
      "transform": "hour"
    }
  ],
  "partition_evolution_enabled": true
}
```

### 3.4 Partition Writing Strategies

OLake's Iceberg writer implements three distinct strategies:

#### 3.4.1 Multi-Spec Writer (Concurrent)
- **Use Case**: Tables with partition evolution
- **Behavior**: Maintains open file writers for each PartitionSpec + partition combination
- **Memory**: High (multiple writers × partition count)
- **Performance**: Highest throughput for diverse data
- **Configuration**:
```json
{
  "writer_strategy": "multi_spec_concurrent",
  "max_open_writers": 100
}
```

#### 3.4.2 Single-Spec Writer (Concurrent)
- **Use Case**: Fixed partition specification
- **Behavior**: One file writer per unique partition value
- **Memory**: Medium
- **Performance**: High throughput for current partition spec
- **Configuration**:
```json
{
  "writer_strategy": "single_spec_concurrent",
  "max_open_writers": 50
}
```

#### 3.4.3 Memory-Efficient Sequential Writer
- **Use Case**: Low-memory environments, pre-sorted data
- **Behavior**: Single open writer, requires data clustered by partition
- **Memory**: Low (single writer + buffer)
- **Performance**: High throughput if data is pre-sorted
- **Configuration**:
```json
{
  "writer_strategy": "sequential",
  "sort_before_write": true,
  "buffer_size_mb": 128
}
```

### 3.5 Schema Evolution Handling

#### Automatic Schema Detection
OLake automatically detects source schema changes and applies them to Iceberg tables:

**Supported Operations:**
1. **Add Column**: Automatically adds new column to Iceberg schema
2. **Rename Column**: Preserves column by ID, updates name metadata
3. **Type Promotion**: Widens types (e.g., INT → BIGINT)
4. **Drop Column**: Marks column as deleted (data preserved for time travel)

**Example Flow:**
```
PostgreSQL:
  ALTER TABLE orders ADD COLUMN discount_percent DECIMAL(5,2);

OLake Detection:
  1. Discovers new column via schema inspection
  2. Updates streams.json schema cache
  3. Calls Iceberg API: table.updateSchema().addColumn(...)

Iceberg Result:
  - New column added to schema
  - Default value: NULL
  - Old data files remain unchanged
  - New writes include the column
```

#### Schema Evolution Configuration
```json
{
  "schema_evolution": {
    "enabled": true,
    "allow_column_add": true,
    "allow_column_rename": true,
    "allow_type_promotion": true,
    "allow_column_drop": false,
    "check_interval_seconds": 300
  }
}
```

#### Type Mapping

**PostgreSQL → Iceberg:**
```
SMALLINT       → INT
INTEGER        → INT
BIGINT         → LONG
REAL           → FLOAT
DOUBLE         → DOUBLE
NUMERIC/DECIMAL → DECIMAL(p, s)
VARCHAR/TEXT   → STRING
TIMESTAMP      → TIMESTAMP (with/without timezone)
DATE           → DATE
BOOLEAN        → BOOLEAN
JSONB          → STRING (serialized)
UUID           → UUID
BYTEA          → BINARY
```

**MySQL → Iceberg:**
```
TINYINT        → INT
SMALLINT       → INT
MEDIUMINT      → INT
INT            → INT
BIGINT         → LONG
FLOAT          → FLOAT
DOUBLE         → DOUBLE
DECIMAL        → DECIMAL(p, s)
VARCHAR/TEXT   → STRING
DATETIME       → TIMESTAMP
DATE           → DATE
BOOLEAN        → BOOLEAN
JSON           → STRING (serialized)
BINARY/BLOB    → BINARY
```

**MongoDB → Iceberg:**
```
int32          → INT
int64          → LONG
double         → DOUBLE
decimal128     → DECIMAL(38, 10)
string         → STRING
date           → TIMESTAMP
objectId       → STRING
boolean        → BOOLEAN
object         → STRING (JSON serialized) or STRUCT
array          → LIST or STRING (JSON serialized)
binary         → BINARY
```

### 3.6 Transaction Guarantees (ACID Compliance)

#### Atomicity
Every OLake write to Iceberg creates a single atomic snapshot:
- All or nothing: Either entire batch commits or none of it
- No partial writes visible to readers
- Rollback on failure leaves table in previous state

#### Consistency
Iceberg enforces schema consistency:
- Schema evolution rules prevent breaking changes
- Type safety maintained through Parquet + Iceberg metadata
- Referential integrity at snapshot level

#### Isolation
OLake writes are isolated from concurrent operations:
- **Write-Write Isolation**: Optimistic concurrency control
- **Read-Write Isolation**: Readers never see uncommitted data
- **Snapshot Isolation**: Each reader operates on a consistent snapshot

**Conflict Resolution:**
```
Writer A: Starts commit at snapshot S1
Writer B: Starts commit at snapshot S1

Writer A: Completes commit → creates snapshot S2
Writer B: Attempts commit → detects S2 exists
          → Retries with S2 as base
          → Merges changes → creates snapshot S3
```

#### Durability
Once OLake commits an Iceberg snapshot:
- Metadata persisted to catalog (PostgreSQL/Glue/etc.)
- Data files persisted to object storage (S3/R2/GCS)
- Checkpoints updated in state.json
- Source CDC position advanced only after durable commit

**Failure Scenarios:**
1. **Pre-commit failure**: No state change, retry from checkpoint
2. **During commit**: Iceberg's atomic manifest commits prevent corruption
3. **Post-commit failure**: Safe to proceed, state updated on next run

### 3.7 Parquet File Generation and Optimization

#### File Size Targets
OLake configures Iceberg to generate optimally sized Parquet files:

**Default Configuration:**
```json
{
  "parquet_config": {
    "target_file_size_mb": 256,
    "max_file_size_mb": 512,
    "min_file_size_mb": 64,
    "row_group_size": 1048576,
    "page_size": 1048576,
    "compression": "ZSTD",
    "compression_level": 3
  }
}
```

#### Compression Options
- **SNAPPY**: Fast, moderate compression (default for high-throughput)
- **ZSTD**: Better compression, slightly slower (recommended)
- **GZIP**: Maximum compression, slowest
- **LZ4**: Fastest, least compression
- **UNCOMPRESSED**: Raw data (rarely used)

#### Parquet Encoding Strategies
Iceberg automatically selects optimal encodings:
- **Dictionary Encoding**: For low-cardinality columns
- **Run-Length Encoding (RLE)**: For repeated values
- **Delta Encoding**: For timestamps and sequential IDs
- **Plain Encoding**: Fallback for high-entropy data

#### Row Group and Page Sizing
```json
{
  "row_group_size": 1048576,      // 1M rows per row group
  "page_size": 1048576,            // 1MB page size
  "dictionary_page_size": 1048576  // 1MB dictionary pages
}
```

**Impact:**
- Smaller row groups: Better predicate pushdown, higher overhead
- Larger row groups: Better compression, slower small queries
- Balanced defaults optimize for analytical query patterns

#### Statistics Collection
OLake ensures Iceberg collects comprehensive statistics:
- **Column-level stats**: Min/max, null count, value count
- **File-level stats**: Record count, file size
- **Partition-level stats**: Record count per partition

These enable:
- Partition pruning (skip entire partitions)
- File pruning (skip files based on predicates)
- Query optimization (cost-based optimizer decisions)

---

## 4. Performance Characteristics

### 4.1 Throughput Benchmarks

#### PostgreSQL Benchmarks

**Full Load Performance (4 Billion Rows):**
- **OLake**: 46,262 RPS
- **Fivetran**: 6,812 RPS (6.8× slower)
- **Airbyte**: 456 RPS (101× slower)
- **Estuary**: 3,989 RPS (11.6× slower)
- **Debezium**: 14,922 RPS (3.1× slower)

**CDC Performance (50 Million Changes):**
- **OLake**: 36,982 RPS
- **Fivetran**: 26,419 RPS (1.4× slower)
- **Airbyte**: 587 RPS (63× slower)
- **Estuary**: 3,082 RPS (12× slower)
- **Debezium**: 13,697 RPS (2.7× slower)

**Peak Throughput:**
- **Full Load**: 319,562 RPS (documented peak)
- **CDC**: Sustained 30,000+ RPS for continuous replication

#### MySQL Benchmarks

**Full Load Performance:**
- **OLake**: 64,334 RPS
- **Airbyte**: 7,148 RPS (9× slower)
- **Estuary**: Not benchmarked
- **Debezium**: ~25,000 RPS estimated

**CDC Performance:**
- **OLake**: 1,000,000 records/sec for 10GB datasets
- Sustained throughput with binlog replication

#### MongoDB Benchmarks

**Full Load Performance (230M rows, 664GB):**
- **OLake**: 35,694 records/sec, completed in 46 minutes
- **Fivetran**: 15× slower (~2.4K records/sec)
- **Airbyte**: 20× slower (~1.8K records/sec)
- **Debezium (embedded)**: 15× slower

**CDC Performance (50M changes):**
- **OLake**: 20.1 minutes
- **Fivetran**: 27.3× slower
- Sustained ~35K records/sec throughput

#### Cost-Performance Analysis

**Monthly Operating Costs (Production Workload):**
- **OLake**: $300/month (self-hosted infrastructure)
- **Fivetran**: $6,000/month (20× more expensive)
- **Airbyte**: $7,200/month (24× more expensive)
- **Debezium + Kafka**: $900/month (AWS MSK Serverless, 3× more expensive)

**ROI Calculation:**
```
Annual Savings (OLake vs Fivetran):
$6,000 - $300 = $5,700/month
$5,700 × 12 = $68,400/year
```

### 4.2 Latency Characteristics

#### CDC Latency (Time from Source Commit to Iceberg Availability)

**PostgreSQL:**
- **P50 Latency**: < 500ms
- **P95 Latency**: < 1 second
- **P99 Latency**: < 2 seconds

**MySQL:**
- **P50 Latency**: < 800ms
- **P95 Latency**: < 1.5 seconds
- **P99 Latency**: < 3 seconds

**MongoDB:**
- **P50 Latency**: < 1 second
- **P95 Latency**: < 2 seconds
- **P99 Latency**: < 4 seconds

**Latency Breakdown:**
```
Source DB Commit
    ↓ (10-50ms)
Log Read/Decode
    ↓ (50-200ms)
Transform/Process
    ↓ (100-300ms)
Iceberg Write Batch
    ↓ (200-500ms)
Catalog Commit
    ↓ (100-200ms)
Available for Query
```

#### Query Availability Latency

**From Iceberg Commit to Query Engines:**
- **DuckDB**: < 100ms (local metadata refresh)
- **Trino**: 100-500ms (catalog metadata cache TTL)
- **Spark**: 1-5 seconds (depends on refresh interval)
- **Athena**: 1-10 seconds (Glue catalog propagation)

### 4.3 Resource Requirements

#### Benchmark Test Environment
- **Instance**: Azure Standard D64ls v5
- **vCPUs**: 64
- **Memory**: 128 GiB
- **Network**: 10 Gbps
- **Storage**: Premium SSD

#### Actual Resource Usage (Observed)

**Light Workload (1-10 tables, <1M records/hour):**
- **CPU**: 2-4 cores
- **Memory**: 4-8 GB
- **Network**: 100-500 Mbps
- **Storage**: Minimal (state files < 1MB)

**Medium Workload (10-50 tables, 1-10M records/hour):**
- **CPU**: 8-16 cores
- **Memory**: 16-32 GB
- **Network**: 1-2 Gbps
- **Storage**: State files + buffer (~10GB disk)

**Heavy Workload (50+ tables, >10M records/hour):**
- **CPU**: 32-64 cores
- **Memory**: 64-128 GB
- **Network**: 5-10 Gbps
- **Storage**: 50-100GB for buffering and state

#### Docker Compose Stack Requirements

**Minimal OLake UI Stack:**
- **OLake UI**: 1 GB RAM, 1 CPU
- **Temporal Worker**: 2 GB RAM, 2 CPU
- **PostgreSQL**: 2 GB RAM, 2 CPU
- **Temporal Server**: 4 GB RAM, 2 CPU
- **Elasticsearch**: 2 GB RAM, 2 CPU
- **Total**: ~11 GB RAM, 9 CPU cores

**Recommended Production:**
- **OLake UI**: 2 GB RAM, 2 CPU
- **Temporal Worker**: 4 GB RAM, 4 CPU
- **PostgreSQL**: 8 GB RAM, 4 CPU
- **Temporal Server**: 8 GB RAM, 4 CPU
- **Elasticsearch**: 4 GB RAM, 4 CPU
- **Total**: ~26 GB RAM, 18 CPU cores

### 4.4 Parallelization Strategies

#### Three-Level Concurrency Model

**1. Global Level:**
Controls total concurrent stream execution:
```json
{
  "concurrent_stream_execution": 5
}
```
- Limits simultaneous table/collection syncs
- Prevents overwhelming source database
- Balances between throughput and resource usage

**2. Stream Level:**
Manages intra-stream parallelism:
```json
{
  "stream": "public.orders",
  "max_threads": 8,
  "chunk_size": 10000
}
```
- Parallel chunked reads within single table
- Varies by sync mode (full refresh uses more threads)

**3. Writer Pool:**
Dynamic thread scaling for destinations:
```json
{
  "writer_pool_size": 16,
  "batch_size": 1000,
  "flush_interval_seconds": 10
}
```
- Shared across all streams
- Auto-scales based on backpressure

#### Parallelization Examples

**Scenario 1: Single Large Table**
```
Table: 1 billion rows
Chunks: 100 (10M rows each)
Threads: 16

Effective Parallelism:
16 threads × 100 chunks = 1,600 parallel operations
Completion Time: ~20 minutes at 46K RPS
```

**Scenario 2: Multiple Small Tables**
```
Tables: 50 tables (1M rows each)
Concurrent Streams: 10
Threads per Stream: 4

Effective Parallelism:
10 streams × 4 threads = 40 parallel operations
Completion Time: ~10 minutes
```

#### Load Balancing

**Chunk Distribution Strategy:**
OLake uses work-stealing algorithm:
1. Divide table into chunks
2. Assign chunks to worker threads
3. Workers steal from busy queues when idle
4. Dynamic rebalancing based on chunk processing time

**Adaptive Throttling:**
```json
{
  "adaptive_throttling": {
    "enabled": true,
    "target_cpu_percent": 80,
    "target_memory_percent": 85,
    "check_interval_seconds": 30
  }
}
```

### 4.5 Performance Optimization Tips

#### 1. Source Database Configuration

**PostgreSQL:**
- Set `shared_buffers` to 25% of RAM
- Increase `max_wal_senders` and `max_replication_slots`
- Use `wal_level = logical` only on replicas if possible
- Monitor replication lag: `SELECT * FROM pg_stat_replication;`

**MySQL:**
- Set `binlog_format = ROW`
- Increase `max_binlog_size` to reduce log rotation
- Use `binlog_row_image = MINIMAL` for UPDATE-heavy workloads
- Enable `binlog_transaction_compression` for network efficiency

**MongoDB:**
- Use secondary nodes for full refresh reads
- Configure `read_preference = secondaryPreferred`
- Increase oplog size for longer CDC catchup windows
- Enable sharding for massive collections

#### 2. OLake Configuration Tuning

**Maximize Throughput:**
```json
{
  "max_threads": 16,
  "concurrent_stream_execution": 10,
  "batch_size": 5000,
  "flush_interval_seconds": 5
}
```

**Minimize Latency:**
```json
{
  "max_threads": 4,
  "concurrent_stream_execution": 3,
  "batch_size": 100,
  "flush_interval_seconds": 1
}
```

**Balance (Recommended):**
```json
{
  "max_threads": 8,
  "concurrent_stream_execution": 5,
  "batch_size": 1000,
  "flush_interval_seconds": 10
}
```

#### 3. Network Optimization

- **Colocation**: Deploy OLake in same region/VPC as source database
- **Compression**: Enable gRPC compression for Iceberg writer
- **Connection Pooling**: Reuse database connections
- **Bandwidth**: Ensure 1+ Gbps network for high-throughput scenarios

#### 4. Iceberg Table Design

- **Partitioning**: Use time-based partitioning for time-series data
- **Compaction**: Schedule regular compaction jobs
- **File Size**: Target 256MB files for optimal query performance
- **Z-Ordering**: Use sorted writes for better compression and filtering

---

## 5. Configuration and Deployment

### 5.1 Docker Deployment

#### Standalone Docker Container

**Pull Image:**
```bash
docker pull olakego/source-postgres:latest
```

**Run Full Sync:**
```bash
docker run --rm \
  -v /path/to/config:/mnt/config \
  olakego/source-postgres:latest \
  sync \
    --config /mnt/config/source.json \
    --catalog /mnt/config/streams.json \
    --destination /mnt/config/destination.json
```

**Discover Tables:**
```bash
docker run --rm \
  -v /path/to/config:/mnt/config \
  olakego/source-postgres:latest \
  discover --config /mnt/config/source.json \
  > /path/to/config/streams.json
```

#### Docker Compose (OLake UI)

**Quick Start:**
```bash
curl -sSL https://raw.githubusercontent.com/datazip-inc/olake-ui/master/docker-compose.yml \
  | docker compose -f - up -d
```

**Access UI:**
- URL: http://localhost:8000
- Default credentials: `admin` / `password`

**Docker Compose Stack:**
```yaml
version: '3.8'

services:
  olake-ui:
    image: olakego/olake-ui:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://olake:password@postgres:5432/olake
      - TEMPORAL_ADDRESS=temporal:7233
    depends_on:
      - postgres
      - temporal

  temporal-worker:
    image: olakego/temporal-worker:latest
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - DATABASE_URL=postgresql://olake:password@postgres:5432/olake
    depends_on:
      - temporal

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=olake
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=olake

  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=olake
      - POSTGRES_PWD=password
      - POSTGRES_SEEDS=postgres
    depends_on:
      - postgres

  temporal-ui:
    image: temporalio/ui:latest
    ports:
      - "8080:8080"
    environment:
      - TEMPORAL_ADDRESS=temporal:7233

  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  postgres_data:
  elasticsearch_data:
```

### 5.2 Kubernetes Deployment

#### Helm Chart Installation

**Add OLake Helm Repository:**
```bash
helm repo add olake https://charts.olake.io
helm repo update
```

**Install OLake:**
```bash
helm install olake olake/olake \
  --namespace olake \
  --create-namespace \
  --values values.yaml
```

#### values.yaml Example

```yaml
# OLake UI Configuration
ui:
  replicaCount: 2
  image:
    repository: olakego/olake-ui
    tag: latest
  resources:
    requests:
      cpu: 1000m
      memory: 2Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  service:
    type: LoadBalancer
    port: 80

# Temporal Worker Configuration
worker:
  replicaCount: 5
  image:
    repository: olakego/temporal-worker
    tag: latest
  resources:
    requests:
      cpu: 2000m
      memory: 4Gi
    limits:
      cpu: 4000m
      memory: 8Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70

# PostgreSQL Configuration
postgresql:
  enabled: true
  auth:
    username: olake
    password: changeMe123
    database: olake
  primary:
    resources:
      requests:
        cpu: 2000m
        memory: 8Gi
      limits:
        cpu: 4000m
        memory: 16Gi
    persistence:
      enabled: true
      size: 100Gi
      storageClass: fast-ssd

# Temporal Configuration
temporal:
  enabled: true
  server:
    replicaCount: 3
    resources:
      requests:
        cpu: 2000m
        memory: 4Gi
      limits:
        cpu: 4000m
        memory: 8Gi

# Elasticsearch Configuration
elasticsearch:
  enabled: true
  replicas: 3
  minimumMasterNodes: 2
  resources:
    requests:
      cpu: 1000m
      memory: 4Gi
    limits:
      cpu: 2000m
      memory: 8Gi
  volumeClaimTemplate:
    resources:
      requests:
        storage: 100Gi

# Persistent Volume for Shared State
persistence:
  enabled: true
  storageClass: nfs-client
  accessMode: ReadWriteMany
  size: 50Gi

# Secrets Management
secrets:
  createSecrets: true
  databasePassword: changeMe123
  awsAccessKey: AKIAIOSFODNN7EXAMPLE
  awsSecretKey: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

#### Persistent Volume Requirements

**NFS Server Example (Development):**
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: olake-shared-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: nfs-server.example.com
    path: /exports/olake
  mountOptions:
    - nfsvers=4.1
```

**Production Storage Classes:**
- AWS: EFS with CSI driver
- Azure: Azure Files
- GCP: Filestore
- On-prem: NFS, Ceph, GlusterFS

### 5.3 Configuration File Formats

#### source.json Schema

**PostgreSQL:**
```json
{
  "host": "string (required)",
  "port": "integer (default: 5432)",
  "database": "string (required)",
  "username": "string (required)",
  "password": "string (required)",
  "ssl": {
    "mode": "disable|require|verify-ca|verify-full"
  },
  "update_method": {
    "replication_slot": "string",
    "publication": "string",
    "initial_wait_time": "integer (seconds)"
  },
  "max_threads": "integer (default: 5)",
  "backoff_retry_count": "integer (default: 3)"
}
```

**MySQL:**
```json
{
  "hosts": ["string (required)"],
  "username": "string (required)",
  "password": "string (required)",
  "database": "string (required)",
  "port": "integer (default: 3306)",
  "tls_skip_verify": "boolean (default: false)",
  "update_method": {
    "method": "binlog",
    "server_id": "integer (unique)"
  },
  "max_threads": "integer (default: 8)",
  "backoff_retry_count": "integer (default: 3)"
}
```

**MongoDB:**
```json
{
  "hosts": ["string (required)"],
  "username": "string",
  "password": "string",
  "authdb": "string (default: admin)",
  "replica_set": "string",
  "read_preference": "primary|primaryPreferred|secondary|secondaryPreferred",
  "srv": "boolean (default: false)",
  "database": "string (required)",
  "max_threads": "integer (default: 10)",
  "backoff_retry_count": "integer (default: 3)",
  "chunking_strategy": "objectid|shardkey|adaptive"
}
```

#### destination.json Schema

**Iceberg (REST Catalog):**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "string (required)",
    "iceberg_s3_path": "string (required)",
    "s3_endpoint": "string",
    "aws_region": "string (required)",
    "aws_access_key": "string",
    "aws_secret_key": "string",
    "token": "string (optional, for bearer auth)",
    "iceberg_db": "string (namespace)",
    "parquet_config": {
      "compression": "SNAPPY|ZSTD|GZIP|LZ4",
      "compression_level": "integer (1-9)",
      "row_group_size": "integer",
      "page_size": "integer"
    }
  }
}
```

**Iceberg (AWS Glue Catalog):**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "glue",
    "glue_catalog_id": "string (AWS account ID)",
    "iceberg_s3_path": "string (required)",
    "aws_region": "string (required)",
    "aws_access_key": "string (required)",
    "aws_secret_key": "string (required)",
    "iceberg_db": "string (Glue database)"
  }
}
```

**Iceberg (JDBC Catalog):**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "jdbc",
    "jdbc_url": "string (required)",
    "jdbc_username": "string (required)",
    "jdbc_password": "string (required)",
    "iceberg_s3_path": "string (required)",
    "aws_region": "string (required)",
    "aws_access_key": "string (required)",
    "aws_secret_key": "string (required)",
    "iceberg_db": "string (namespace)"
  }
}
```

**S3 Parquet Writer:**
```json
{
  "type": "S3_PARQUET",
  "writer": {
    "s3_bucket": "string (required)",
    "s3_prefix": "string (optional)",
    "s3_endpoint": "string",
    "aws_region": "string (required)",
    "aws_access_key": "string (required)",
    "aws_secret_key": "string (required)",
    "parquet_config": {
      "compression": "SNAPPY|ZSTD|GZIP|LZ4"
    }
  }
}
```

#### streams.json Schema

Generated by `discover` command, editable by users:

```json
{
  "streams": [
    {
      "stream": "public.orders",
      "sync_mode": "full_refresh|incremental|incremental_cdc",
      "cursor_field": "updated_at",
      "primary_key": ["id"],
      "partition_spec": [
        {
          "field": "created_at",
          "transform": "day"
        }
      ],
      "selected": true,
      "schema": {
        "type": "object",
        "properties": {
          "id": {"type": "integer"},
          "customer_id": {"type": "integer"},
          "total": {"type": "number"},
          "status": {"type": "string"},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    }
  ]
}
```

### 5.4 Environment Variables and Secrets Management

#### Environment Variables

**OLake Core:**
```bash
# Database connection (alternative to config files)
OLAKE_SOURCE_HOST=postgres.example.com
OLAKE_SOURCE_PORT=5432
OLAKE_SOURCE_DATABASE=production
OLAKE_SOURCE_USERNAME=olake_user
OLAKE_SOURCE_PASSWORD=secret123

# Destination (Iceberg)
OLAKE_DEST_TYPE=ICEBERG
OLAKE_DEST_CATALOG_TYPE=rest
OLAKE_DEST_CATALOG_URL=http://catalog:8181
OLAKE_DEST_S3_PATH=s3://lakehouse/warehouse
OLAKE_AWS_REGION=us-east-1
OLAKE_AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
OLAKE_AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Performance tuning
OLAKE_MAX_THREADS=8
OLAKE_CONCURRENT_STREAMS=5
OLAKE_BATCH_SIZE=1000

# Logging
OLAKE_LOG_LEVEL=info  # debug|info|warn|error
OLAKE_LOG_FORMAT=json  # json|text
```

**OLake UI:**
```bash
DATABASE_URL=postgresql://olake:password@postgres:5432/olake
TEMPORAL_ADDRESS=temporal:7233
JWT_SECRET=your-secret-key-here
SESSION_TIMEOUT=3600
```

#### Secrets Management Strategies

**1. Docker Secrets (Docker Swarm):**
```bash
echo "mysecretpassword" | docker secret create db_password -
```

**2. Kubernetes Secrets:**
```bash
kubectl create secret generic olake-secrets \
  --from-literal=source-password=secret123 \
  --from-literal=aws-access-key=AKIA... \
  --from-literal=aws-secret-key=wJalr...
```

**3. HashiCorp Vault Integration:**
```json
{
  "password": "vault:secret/data/olake#source_password",
  "aws_access_key": "vault:secret/data/aws#access_key"
}
```

**4. AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name olake/source-password \
  --secret-string "secret123"
```

### 5.5 Monitoring and Observability

#### Metrics Exposure

OLake exposes Prometheus-compatible metrics (planned/community contribution needed):

**Endpoint:** `http://localhost:9090/metrics`

**Key Metrics:**
```
# Throughput
olake_records_processed_total{source="postgres", table="orders"}
olake_bytes_processed_total{source="postgres", table="orders"}

# Latency
olake_sync_duration_seconds{source="postgres", table="orders"}
olake_cdc_lag_seconds{source="postgres"}

# Errors
olake_errors_total{source="postgres", type="connection_timeout"}
olake_retries_total{source="postgres", table="orders"}

# Resource usage
olake_memory_usage_bytes
olake_cpu_usage_percent
olake_open_connections{source="postgres"}
```

#### Logging Configuration

**JSON Structured Logging:**
```json
{
  "timestamp": "2025-01-15T10:30:45.123Z",
  "level": "info",
  "message": "CDC sync completed",
  "source": "postgres",
  "table": "orders",
  "records_processed": 12345,
  "duration_ms": 456,
  "snapshot_id": "8765432109876543210"
}
```

**Log Levels:**
- **DEBUG**: Verbose, includes query details
- **INFO**: Standard operations (default)
- **WARN**: Retryable errors, performance degradation
- **ERROR**: Failures requiring attention

#### Temporal Workflow Monitoring

**Temporal UI:** http://localhost:8080

**Workflow Visibility:**
- Active syncs and their progress
- Historical sync executions
- Error traces and stack traces
- Retry attempts and backoff timing

**Example Workflow Query:**
```sql
SELECT * FROM workflows 
WHERE workflow_type = 'OLakeSyncWorkflow' 
  AND status = 'Running'
ORDER BY start_time DESC;
```

#### Alerting Integration

**Prometheus Alerting Rules:**
```yaml
groups:
  - name: olake_alerts
    rules:
      - alert: HighCDCLag
        expr: olake_cdc_lag_seconds > 300
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CDC lag exceeds 5 minutes"
          description: "Source {{ $labels.source }} has CDC lag of {{ $value }}s"

      - alert: SyncFailure
        expr: increase(olake_errors_total[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "{{ $labels.source }} has {{ $value }} errors in 5 minutes"
```

**Integration Options:**
- PagerDuty
- Slack
- OpsGenie
- Email
- Webhook

---

## 6. Comparison with Alternatives

### 6.1 OLake vs Debezium + Kafka

#### Architecture Differences

**Debezium + Kafka:**
- Multi-hop architecture: Source → Kafka → Sink
- Requires Kafka cluster (high operational overhead)
- Schema registry management
- At-least-once delivery by default
- Horizontal scalability through Kafka partitions

**OLake:**
- Direct write: Source → Iceberg (no intermediate queue)
- Lightweight, single-component deployment
- Built-in schema handling
- Exactly-once delivery guarantees
- Parallelization through thread pools

#### Performance Comparison

**Full Load (Postgres, 4B rows):**
- Debezium: 14,922 RPS
- OLake: 46,262 RPS (3.1× faster)

**CDC (Postgres, 50M changes):**
- Debezium: 13,697 RPS
- OLake: 36,982 RPS (2.7× faster)

**Operational Cost:**
- Debezium + MSK: $900/month
- OLake: $300/month (3× savings)

#### When to Use Each

**Choose Debezium + Kafka if:**
- You need multiple consumers of CDC stream
- Existing Kafka infrastructure
- Complex event routing and transformations
- Durability requirements exceed Iceberg's guarantees

**Choose OLake if:**
- Primary goal is lakehouse replication
- Want minimal operational complexity
- Cost sensitivity
- High throughput requirements

### 6.2 OLake vs Airbyte

#### Open Source Positioning

**Airbyte:**
- Broad connector ecosystem (300+ connectors)
- Normalization and dbt integration
- Cloud and self-hosted options
- Generalist approach

**OLake:**
- Specialized for database → lakehouse
- Iceberg-first design
- Ultra-high performance focus
- Fewer connectors, deeper optimization

#### Performance Comparison

**MongoDB Full Load (230M rows, 664GB):**
- Airbyte: ~1,800 records/sec
- OLake: 35,694 records/sec (20× faster)

**Postgres CDC (50M changes):**
- Airbyte: 587 RPS
- OLake: 36,982 RPS (63× faster)

**Cost:**
- Airbyte: $7,200/month (estimated cloud cost)
- OLake: $300/month (24× savings)

#### When to Use Each

**Choose Airbyte if:**
- Need diverse source connectors (APIs, SaaS apps)
- Want built-in transformations (dbt)
- Prefer established community support
- Destinations other than Iceberg (Snowflake, BigQuery, etc.)

**Choose OLake if:**
- Focus on OLTP databases (Postgres, MySQL, MongoDB)
- Target is Iceberg lakehouse
- Performance is critical
- Cost optimization priority

### 6.3 OLake vs Fivetran

#### Commercial vs Open Source

**Fivetran:**
- Fully managed SaaS
- 400+ pre-built connectors
- Enterprise support
- High cost, pay-per-usage

**OLake:**
- Open source, self-hosted
- 4 database connectors (Postgres, MySQL, MongoDB, Oracle)
- Community support + commercial options
- Infrastructure cost only

#### Performance Comparison

**Postgres Full Load:**
- Fivetran: 6,812 RPS
- OLake: 46,262 RPS (6.8× faster)

**Postgres CDC:**
- Fivetran: 26,419 RPS (competitive)
- OLake: 36,982 RPS (1.4× faster)

**Cost:**
- Fivetran: $6,000/month (typical mid-market)
- OLake: $300/month (20× savings)

#### When to Use Each

**Choose Fivetran if:**
- Enterprise budget available
- Need fully managed service
- Require diverse SaaS connectors
- Want white-glove support

**Choose OLake if:**
- Cost-conscious or high data volumes
- In-house DevOps capability
- Comfortable with open-source tools
- Database-centric data sources

### 6.4 OLake vs Estuary Flow

#### Real-Time Focus

**Estuary Flow:**
- Sub-100ms CDC latency (claim)
- Pay-per-GB pricing model
- Materialized views in destinations
- Commercial open-source model

**OLake:**
- Sub-second CDC latency
- Infrastructure cost model
- Iceberg-native snapshots
- Fully open source

#### Performance Comparison

**Postgres Full Load:**
- Estuary: 3,989 RPS
- OLake: 46,262 RPS (11.6× faster)

**Postgres CDC:**
- Estuary: 3,082 RPS
- OLake: 36,982 RPS (12× faster)

#### When to Use Each

**Choose Estuary if:**
- Ultra-low latency required (<100ms)
- Need real-time materialized views
- Pay-as-you-grow pricing preferred

**Choose OLake if:**
- Sub-second latency acceptable
- High-volume data (>1TB/month)
- Predictable infrastructure costs
- Iceberg as primary destination

---

## 7. Use Cases and Integration Patterns

### 7.1 Real-Time Analytics Lakehouse

**Architecture:**
```
OLTP Databases (Postgres, MySQL, MongoDB)
    ↓ (OLake CDC, <1s latency)
Iceberg Tables on S3/R2
    ↓
Query Engines (Trino, DuckDB, Spark)
    ↓
BI Tools (Metabase, Superset, Tableau)
```

**Benefits:**
- Near real-time analytics without impacting production
- Historical time travel for trend analysis
- Cost-effective storage (object storage vs data warehouse)

### 7.2 Data Lake Consolidation

**Pattern:**
Multiple operational databases → Unified Iceberg lakehouse

**Configuration:**
```json
{
  "sources": [
    {"type": "postgres", "database": "orders_db"},
    {"type": "mysql", "database": "inventory_db"},
    {"type": "mongodb", "database": "user_events"}
  ],
  "destination": {
    "catalog": "glue",
    "warehouse": "s3://unified-lakehouse"
  }
}
```

**Advantages:**
- Single source of truth
- Cross-database joins via Trino
- Unified governance and security

### 7.3 ML/AI Feature Store

**Architecture:**
```
Operational Databases
    ↓ (OLake)
Iceberg Tables (Raw)
    ↓ (Spark/Flink transformations)
Iceberg Tables (Features)
    ↓
LanceDB (Vector embeddings)
    ↓
ML Models
```

**Example:**
```python
# Read from Iceberg
df = spark.read.format("iceberg").load("lakehouse.features.user_profiles")

# Generate embeddings
embeddings = model.encode(df['text_features'])

# Store in LanceDB
lance_table.add(data=embeddings, metadata=df)
```

### 7.4 Compliance and Auditing

**GDPR Right to be Forgotten:**
```sql
-- Delete user data
DELETE FROM lakehouse.users WHERE user_id = '12345';

-- Create new snapshot (atomic)
-- Old snapshots retained for audit trail
-- Time travel to pre-deletion state if needed
```

**Audit Trail:**
```sql
-- Query historical snapshots
SELECT * FROM lakehouse.users
FOR SYSTEM_TIME AS OF TIMESTAMP '2025-01-01 00:00:00'
WHERE user_id = '12345';
```

### 7.5 Disaster Recovery and Backup

**Architecture:**
```
Primary Region (Production Postgres)
    ↓ (OLake CDC)
Iceberg on S3 (Versioned, Immutable)
    ↓ (S3 Cross-Region Replication)
Secondary Region (Iceberg Replica)
```

**Recovery:**
1. Snapshot Iceberg tables at consistent point-in-time
2. Export to SQL format via Spark/Trino
3. Restore to PostgreSQL if needed

**RTO/RPO:**
- RPO: < 5 seconds (CDC lag)
- RTO: Minutes to hours (depends on data volume)

---

## 8. Roadmap and Future Development

### 8.1 Current Status (as of 2025-01)

**Production Ready:**
- PostgreSQL connector (full + CDC)
- MySQL connector (full + CDC)
- MongoDB connector (full + CDC)
- Oracle connector (full + incremental)
- Iceberg writer (all catalog types)
- Docker and Kubernetes deployment

**Beta/Experimental:**
- OLake UI (Docker Compose)
- REST API for programmatic control
- Temporal workflow orchestration

**In Development:**
- Kafka connector
- Oracle CDC (LogMiner)
- Advanced monitoring and metrics

### 8.2 Community Contributions

**Open Issues:**
- Prometheus metrics exporter
- Grafana dashboards
- Additional catalog implementations (Nessie, Polaris)
- Performance benchmarks on ARM architecture

**Contribution Areas:**
- New source connectors
- Destination writers (Delta Lake, Hudi)
- Documentation improvements
- Performance optimizations

---

## 9. Best Practices and Recommendations

### 9.1 Database Configuration

**1. Use Dedicated Replication Users:**
```sql
-- PostgreSQL
CREATE USER olake_repl WITH REPLICATION LOGIN PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO olake_repl;

-- MySQL
CREATE USER 'olake_repl'@'%' IDENTIFIED BY 'secure_password';
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'olake_repl'@'%';

-- MongoDB
db.createUser({
  user: "olake_repl",
  pwd: "secure_password",
  roles: [
    { role: "read", db: "production" },
    { role: "read", db: "local" }
  ]
})
```

**2. Monitor Replication Lag:**
```sql
-- PostgreSQL
SELECT slot_name, confirmed_flush_lsn, pg_current_wal_lsn(),
       pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes
FROM pg_replication_slots;

-- MySQL
SHOW SLAVE STATUS\G
```

**3. Retention Policies:**
- PostgreSQL: Set `wal_keep_segments` or use replication slots
- MySQL: Configure `expire_logs_days` appropriately
- MongoDB: Ensure oplog is large enough (hours of operations)

### 9.2 Iceberg Table Management

**1. Regular Compaction:**
```sql
-- Spark example
CALL catalog.system.rewrite_data_files(
  table => 'lakehouse.orders',
  strategy => 'sort',
  sort_order => 'customer_id'
);
```

**2. Snapshot Expiration:**
```sql
-- Retain 30 days of snapshots
CALL catalog.system.expire_snapshots(
  table => 'lakehouse.orders',
  older_than => TIMESTAMP '2025-01-01 00:00:00',
  retain_last => 10
);
```

**3. Orphan File Cleanup:**
```sql
-- Remove unreferenced files
CALL catalog.system.remove_orphan_files(
  table => 'lakehouse.orders',
  older_than => TIMESTAMP '2025-01-01 00:00:00'
);
```

### 9.3 Performance Tuning

**1. Right-Size Threads:**
```
Rule of thumb:
- Full Refresh: 2-4× number of CPU cores
- CDC: 1-2× number of CPU cores
- Concurrent Streams: Total tables / 5
```

**2. Batch Size Optimization:**
```
Small batches (100-500): Low latency, high overhead
Medium batches (1K-5K): Balanced (recommended)
Large batches (10K+): High throughput, higher latency
```

**3. Network Proximity:**
- Deploy OLake in same VPC/region as source
- Use VPC endpoints for S3/Iceberg access
- Monitor network transfer costs

### 9.4 Security Hardening

**1. Credential Management:**
- Use AWS Secrets Manager / HashiCorp Vault
- Rotate credentials regularly (90 days)
- Never commit secrets to version control

**2. Network Security:**
- Use TLS/SSL for all connections
- Restrict source IPs via security groups
- Enable VPC peering for cross-account access

**3. Audit Logging:**
- Log all sync operations
- Track data lineage
- Enable CloudTrail for S3 access logs

### 9.5 Cost Optimization

**1. Storage Tiering:**
```
Iceberg on S3:
- Standard (0-30 days)
- Intelligent Tiering (30-90 days)
- Glacier (>90 days, rarely accessed)
```

**2. Compaction Strategy:**
- Smaller files = higher S3 costs (API calls)
- Target 256MB files minimum
- Schedule compaction during low-traffic hours

**3. Query Optimization:**
- Use partition pruning in queries
- Enable statistics collection
- Materialize frequently accessed views

---

## 10. Troubleshooting Guide

### 10.1 Common Issues

#### Issue: CDC Lag Increasing

**Symptoms:**
- `olake_cdc_lag_seconds` metric growing
- Slow query performance on recent data

**Diagnosis:**
```sql
-- PostgreSQL: Check replication slot lag
SELECT * FROM pg_replication_slots WHERE slot_name = 'olake_slot';

-- Check OLake logs
docker logs olake-worker | grep "lag"
```

**Solutions:**
1. Increase `max_threads` in source.json
2. Scale up worker replicas in Kubernetes
3. Optimize Iceberg compaction schedule
4. Check network bandwidth

#### Issue: Schema Evolution Failures

**Symptoms:**
- Sync fails after source schema change
- Error: "Column type mismatch"

**Diagnosis:**
```bash
# Check streams.json schema
cat streams.json | jq '.streams[] | select(.stream == "public.orders") | .schema'

# Compare with source
docker exec olake discover --config source.json | jq '.streams[] | select(.stream == "public.orders") | .schema'
```

**Solutions:**
1. Re-run `discover` command to update streams.json
2. Enable `schema_evolution.allow_type_promotion`
3. Manual schema update if breaking change

#### Issue: High Memory Usage

**Symptoms:**
- OLake OOMKilled in Kubernetes
- Docker container crashes

**Diagnosis:**
```bash
# Check memory usage
docker stats olake-worker

# Review configuration
cat source.json | jq '.max_threads, .chunk_size'
```

**Solutions:**
1. Reduce `max_threads`
2. Decrease `concurrent_stream_execution`
3. Increase container memory limits
4. Use `sequential` writer strategy

#### Issue: Authentication Failures

**Symptoms:**
- "FATAL: password authentication failed"
- "Access Denied" errors

**Diagnosis:**
```bash
# Test connection manually
psql -h $HOST -p $PORT -U $USER -d $DATABASE

# Check AWS credentials
aws s3 ls s3://my-bucket --profile olake
```

**Solutions:**
1. Verify credentials in source/destination.json
2. Check IAM permissions for AWS services
3. Ensure firewall rules allow OLake IP
4. Rotate and update credentials

### 10.2 Debugging Tools

**1. Verbose Logging:**
```bash
export OLAKE_LOG_LEVEL=debug
docker run -e OLAKE_LOG_LEVEL=debug ...
```

**2. Dry Run Mode:**
```bash
docker run olakego/source-postgres:latest \
  sync --config source.json --dry-run
```

**3. State Inspection:**
```bash
# View current state
cat /mnt/config/state.json | jq

# Reset state (re-sync from beginning)
rm /mnt/config/state.json
```

**4. Temporal Workflow Debugging:**
- Access Temporal UI: http://localhost:8080
- Filter by `WorkflowType = OLakeSyncWorkflow`
- View execution history and event logs

---

## 11. Conclusion

OLake represents a significant advancement in open-source database replication technology, offering:

**Key Strengths:**
- **Performance**: 3-63× faster than alternatives
- **Cost Efficiency**: 20-24× cheaper than commercial solutions
- **Simplicity**: Direct-write architecture eliminates complexity
- **Open Standards**: Iceberg-first design ensures vendor-lock-in freedom
- **Modern Stack**: Built in Go for efficiency, Java for Iceberg integration

**Current Limitations:**
- Limited connector ecosystem (4 sources vs 300+ for Airbyte)
- Relatively new project (maturity vs Debezium/Fivetran)
- Community support smaller than established tools

**Ideal Use Cases:**
- High-volume database replication to lakehouse
- Cost-sensitive data platform architectures
- Real-time analytics on operational data
- Organizations comfortable with self-hosted infrastructure

**When to Avoid:**
- Need for diverse SaaS/API connectors
- Require fully managed service
- Destinations other than Iceberg/Parquet

OLake fills a critical gap in the modern data stack: ultra-fast, cost-effective, open-source database-to-lakehouse replication. As the project matures and the community grows, it's poised to become the de facto standard for this use case.

---

## 12. References and Resources

**Official Documentation:**
- OLake Website: https://olake.io
- GitHub Repository: https://github.com/datazip-inc/olake
- Documentation: https://olake.io/docs
- Architecture Deep Dive: https://olake.io/blog/olake-architecture-deep-dive

**Community:**
- Slack: https://olake.io/slack
- GitHub Issues: https://github.com/datazip-inc/olake/issues
- GitHub Discussions: https://github.com/datazip-inc/olake/discussions

**Apache Iceberg Resources:**
- Iceberg Official Docs: https://iceberg.apache.org/docs/latest
- Iceberg Slack: https://join.slack.com/t/apache-iceberg/shared_invite/...
- Lakekeeper (Iceberg Catalog): https://docs.lakekeeper.io

**Related Technologies:**
- LakeFS (Versioning): https://lakefs.io
- DuckLake (DuckDB Lakehouse): https://ducklake.select
- Trino (Query Engine): https://trino.io
- RisingWave (Streaming DB): https://risingwave.com

**Deployment Examples:**
- OLake + Dagster: https://olake.io/blog/olake-airflow-on-ec2
- OLake + Kubernetes: https://olake.io/blog/deploying-olake-on-kubernetes-helm
- OLake + Cloudflare R2: https://developers.cloudflare.com/r2/data-catalog

---

**End of Document**

*Last Updated: 2025-11-18*  
*Document Version: 1.0*  
*Research Conducted by: Claude Code*


> Source: `docs/data_engineering/olake/olake-patterns-architecture.md`

# OLake Architecture Patterns & Integration Guide

## Table of Contents
1. [Architectural Patterns](#architectural-patterns)
2. [Integration Patterns](#integration-patterns)
3. [Deployment Patterns](#deployment-patterns)
4. [Best Practices](#best-practices)

---

## Architectural Patterns

### Overview

OLake is an open-source, high-performance data replication tool that transforms databases into Apache Iceberg-based data lakehouses. Its architecture is built on four core components: CLI, Framework (CDK), Connectors/Drivers, and Writers.

### 1. Direct-Write vs Queue-Based Architecture

#### Direct-Write Architecture (OLake Approach)

OLake implements a **direct-write pattern** that eliminates intermediary storage queues:

```
Source Database
    ↓
Driver (Connector)
    ↓
Writer (Iceberg/Parquet)
    ↓
Object Storage (S3, GCS, MinIO)
```

**Key Benefits:**
- **Reduced Latency**: Records are pushed immediately upon extraction, not queued
- **Lower Resource Usage**: No intermediate message broker or staging database required
- **Fewer Data Copies**: Direct path from source to destination
- **Simpler Architecture**: Fewer moving parts to manage and troubleshoot

**Performance Example:**
- MongoDB replication: 230 million rows in 46 minutes
- Parallel processing with concurrent chunks
- Near real-time CDC following initial snapshot

#### Alternative Queue-Based Approach

Traditional architectures use intermediate storage:
```
Source → Kafka/RabbitMQ → Processing → Storage
```

**Trade-offs:**
- Better for handling traffic spikes
- More complex infrastructure
- Higher latency but better decoupling

**Decision:**
Use OLake's direct-write when:
- Real-time latency is critical (<5 min target)
- Infrastructure simplicity is valued
- CDC streams are consistent and manageable

### 2. Go-Java Hybrid Design Rationale

#### Go Implementation (Core Framework)

OLake's main binary is written in Go:

```go
// Core components in Go:
- CLI interface
- Connector framework
- State management
- Schema discovery
- Parallel chunking logic
```

**Advantages:**
- Single self-contained binary (cross-platform)
- Excellent concurrency model (goroutines)
- Fast startup and deployment
- Low memory footprint
- Easy Docker containerization

#### Java Integration (Iceberg Writer)

The Iceberg writer integrates with Java ecosystem:

```
OLake (Go) ↔ gRPC ↔ Java Iceberg Service
```

**Java Components:**
- Apache Iceberg client libraries
- Catalog implementations (JDBC, Glue, REST)
- Schema evolution handling
- Transaction management

**Configuration Example:**
```json
{
  "destination": {
    "type": "ICEBERG",
    "writer": {
      "catalog_type": "rest",  // Can be: rest, glue, jdbc, hive
      "rest_catalog_url": "http://lakekeeper:8181",
      "warehouse": "s3://my-bucket/warehouse",
      "s3_endpoint": "https://s3.amazonaws.com",
      "aws_region": "us-east-1"
    }
  }
}
```

#### Design Rationale

1. **Separation of Concerns**: Go handles extraction/orchestration, Java handles Iceberg complexity
2. **Leveraging Ecosystems**: Use best tool for each job
3. **Stability**: Iceberg libraries are Java-native
4. **Scalability**: Go for high-concurrency I/O, Java for complex transactions

### 3. Plugin Architecture for Sources & Destinations

#### Driver/Connector Architecture

OLake uses a pluggable driver pattern:

```
┌─────────────────┐
│  OLake Core     │
│  Framework      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────┐
    ↓         ↓          ↓         ↓
 MongoDB   PostgreSQL  MySQL     Oracle
 Driver    Driver      Driver    Driver
```

#### Core Driver Interface

Every driver implements four standard commands:

```bash
# 1. Specification (configuration schema)
olake discover --config source.json

# 2. Connection validation
olake check --config source.json

# 3. Schema discovery
olake discover --config source.json > streams.json

# 4. Data replication
olake sync --config source.json \
           --catalog streams.json \
           --destination dest.json
```

#### Driver Responsibilities

```
┌─────────────────────────────────────┐
│     Source Connector (Driver)        │
├─────────────────────────────────────┤
│ • Full Load (parallel chunking)      │
│ • CDC setup (replication slots, etc) │
│ • Schema detection                   │
│ • Schema evolution handling          │
│ • Connection pooling                 │
│ • Error recovery & checkpointing     │
└─────────────────────────────────────┘
```

#### Writer Architecture

Writers handle destination-specific logic:

```json
{
  "writers": [
    {
      "type": "ICEBERG",
      "catalog_type": "rest",
      "features": [
        "atomic_writes",
        "schema_evolution",
        "partitioning",
        "compaction"
      ]
    },
    {
      "type": "PARQUET",
      "storage": "s3://bucket/parquet",
      "partitioning": "year/month/day"
    }
  ]
}
```

#### Creating Custom Drivers

Plugin interface (simplified pseudocode):

```go
type Driver interface {
    // Configuration schema
    Spec() json.Schema
    
    // Validate connection
    Check(config Config) error
    
    // Discover tables and columns
    Discover(config Config) (Catalog, error)
    
    // Execute replication
    Sync(config Config, state State) (State, error)
}

// MongoDB driver implementation
type MongoDBDriver struct {
    client *mongo.Client
}

func (d *MongoDBDriver) Sync(config Config, state State) (State, error) {
    // Parallel chunking logic
    chunks := d.partitionCollections(config.Collections)
    
    // Process chunks concurrently
    results := d.processChunksParallel(chunks, state)
    
    // Write to destination via writer
    return d.writer.Write(results)
}
```

### 4. State Management & Checkpointing

#### State Structure

OLake maintains detailed state for resumability:

```json
{
  "version": 1,
  "scope": "global",  // or "stream"
  "streams": [
    {
      "stream_id": "postgres.public.users",
      "sync_type": "incremental",  // full-load, cdc, or incremental
      "stream_state": {
        "cursor_field": "updated_at",
        "cursor_value": "2025-01-15T10:30:00Z",
        "chunks": [
          {
            "chunk_id": 1,
            "min_cursor": "2025-01-15T00:00:00Z",
            "max_cursor": "2025-01-15T10:00:00Z",
            "status": "succeeded"
          }
        ]
      }
    }
  ]
}
```

#### Checkpoint Mechanism

**Full Load Checkpointing:**

```
Phase 1: Initial snapshot
├── Partition collection into chunks
├── Process each chunk in parallel
├── Track completion status per chunk
└── Mark "full_load" complete when all chunks done

Resumability: If sync fails at chunk 50/100
  → Restart skips processed chunks 1-49
  → Resumes from chunk 50
```

**CDC Checkpointing:**

```go
type CDCCheckpoint struct {
    // PostgreSQL WAL position
    WALPosition     string  // e.g., "0/12345678"
    
    // MongoDB change stream resume token
    ResumeToken     string  // Base64 encoded token
    
    // Cursor for general CDC
    LastCursorID    interface{}
    
    // Timestamp of last processed change
    LastProcessedAt time.Time
}
```

**Resumable Replication:**

```
Initial Run:
1. Full load from table → Parquet files
2. Create cursor checkpoint (e.g., max(updated_at))
3. Start CDC from checkpoint
4. Stream changes → Iceberg incremental snapshots

Resume after failure:
1. Load cursor from checkpoint
2. Skip already-loaded chunks
3. Continue CDC from last position
4. No data duplication, no gaps
```

#### State Persistence

```bash
# State stored in Iceberg metadata or external DB
# Example with PostgreSQL state store:

CREATE TABLE olake_state (
    stream_id VARCHAR(255),
    sync_type VARCHAR(50),
    cursor_field VARCHAR(255),
    cursor_value TEXT,
    checkpoint_time TIMESTAMP,
    status VARCHAR(50),
    PRIMARY KEY (stream_id)
);

# Configuration:
olake sync --config source.json \
           --state-backend postgresql \
           --state-url "postgresql://user:pass@localhost/olake"
```

### 5. Error Handling Patterns

#### Retry Strategy

```json
{
  "retry_policy": {
    "max_retries": 3,
    "initial_backoff_ms": 1000,
    "backoff_multiplier": 2.0,
    "max_backoff_ms": 60000,
    "retry_on": [
      "network_timeout",
      "temporary_database_error",
      "s3_rate_limit"
    ]
  }
}
```

#### Implemented Error Handling

```
Failure Types:
├── Transient (retry)
│   ├── Network timeout
│   ├── Database connection lost
│   └── S3 rate limiting
├── Permanent (skip/alert)
│   ├── Schema mismatch
│   ├── Permission denied
│   └── Corrupted data
└── Manual intervention
    ├── Table schema changed
    ├── Source data corruption
    └── Destination out of space
```

#### Dead Letter Queue Pattern

```go
// For unrecoverable records:
type DeadLetterQueue struct {
    Records     []Record      // Failed records
    Error       string        // Error reason
    Timestamp   time.Time
    RetryCount  int
}

// Store in S3 for analysis:
// s3://bucket/dead-letter-queue/{stream}/{date}/{error_type}/
```

#### Monitoring & Alerting

```yaml
# Prometheus metrics
olake_sync_duration_seconds     # Histogram of sync times
olake_records_processed_total    # Counter of processed records
olake_errors_total               # Counter of errors by type
olake_checkpoint_lag_seconds     # Gauge: how far behind source
olake_file_count_total           # Small file problem indicator
```

---

## Integration Patterns

### 1. Lakekeeper (REST Catalog) Integration

#### Architecture

```
OLake ──(REST API)──> Lakekeeper ──(Metadata)──> PostgreSQL
         ↓                           ↓
    Write Parquet              Table Catalog
    to S3/MinIO               ACID Guarantees
```

#### Configuration

```json
{
  "destination": {
    "type": "ICEBERG",
    "writer": {
      "catalog_type": "rest",
      "rest_catalog_url": "http://lakekeeper.example.com:8181",
      "warehouse": "s3://my-bucket/warehouse",
      "namespace": "analytics",
      "token": "${LAKEKEEPER_API_TOKEN}"
    }
  }
}
```

#### Integration Workflow

```bash
# 1. Setup Lakekeeper with PostgreSQL backend
docker run -d \
  -e DATABASE_URL="postgresql://user:pass@postgres/lakekeeper" \
  -p 8181:8181 \
  apache/iceberg:latest-rest

# 2. Configure OLake with REST catalog
# (shown above in configuration)

# 3. Run discovery and sync
olake discover --config source.json > streams.json
olake sync --config source.json \
           --catalog streams.json \
           --destination destination.json

# 4. Query from Trino/Presto
SELECT * FROM iceberg.analytics.postgres_users LIMIT 10;

# 5. Time travel to previous snapshot
SELECT * FROM iceberg.analytics.postgres_users 
FOR SYSTEM_TIME AS OF TIMESTAMP '2025-01-15 10:00:00';
```

#### Key Features

| Feature | Benefit |
|---------|---------|
| REST API | Language-agnostic catalog access |
| PostgreSQL Metadata | Persistent, queryable table catalog |
| Change Events | Audit trail of all modifications |
| OIDC Integration | Centralized authentication |
| Fine-grained ACLs | Row/column-level access control |

### 2. LakeFS Version Control Integration

#### Architecture

```
LakeFS (Version Control Layer)
├── main branch (production)
├── dev branch (development)
└── staging branch (validation)
    ↓
S3 / MinIO / GCS (Object Storage)
    ↓
Iceberg Tables (Lakekeeper)
```

#### Integration Setup

```bash
# 1. Configure OLake to write to LakeFS S3 endpoint
cat destination.json
{
  "destination": {
    "type": "ICEBERG",
    "writer": {
      "catalog_type": "rest",
      "rest_catalog_url": "http://lakekeeper:8181",
      "warehouse": "s3://lakefs-endpoint/analytics/main/warehouse",
      "s3_endpoint": "http://lakefs:8000",  # LakeFS endpoint
      "aws_access_key": "${LAKEFS_ACCESS_KEY}",
      "aws_secret_key": "${LAKEFS_SECRET_KEY}"
    }
  }
}

# 2. Run sync to staging branch
olake sync --config source.json \
           --catalog streams.json \
           --destination destination.json \
           --lakefs-branch staging

# 3. Validate data on staging
docker run trino --server http://trino:8080
SELECT COUNT(*) FROM iceberg.staging_analytics.postgres_users;

# 4. Merge to production
lakefs api commits create \
  --repo analytics \
  --branch staging \
  --message "Validated: postgres sync" | \
lakefs api commits merge \
  --repo analytics \
  --sourceRef staging \
  --destinationRef main
```

#### Zero-Copy Branching

```bash
# Create isolated branch for experiments
lakefs refs branch create \
  --repo analytics \
  --branch-id experiment-2025-01 \
  --source main

# Data is not copied; files are versioned
# Same physical files, different logical views

# Merge back (or discard) without extra data movement
lakefs refs branch delete --repo analytics --branch-id experiment-2025-01
```

### 3. Dagster Orchestration Patterns

#### Job Structure

```python
from dagster import job, op, Field, String, DependencyDefinition
from dagster_shell import execute_shell_command

@op(config_schema={"database": Field(String)})
def discover_tables(context):
    """Discover schema from source database"""
    db = context.op_config["database"]
    execute_shell_command(
        f"olake discover --config /etc/olake/{db}_source.json > /tmp/{db}_streams.json"
    )
    return f"/tmp/{db}_streams.json"

@op(config_schema={"database": Field(String), "streams": Field(String)})
def sync_data(context, streams):
    """Replicate data to Iceberg"""
    db = context.op_config["database"]
    execute_shell_command(
        f"olake sync --config /etc/olake/{db}_source.json " +
        f"--catalog {streams} " +
        f"--destination /etc/olake/{db}_destination.json"
    )
    return {"status": "completed", "database": db}

@op
def validate_sync(context, sync_result):
    """Validate replicated data"""
    # Query Iceberg to verify row counts, checksums
    pass

@job
def postgres_to_iceberg():
    streams = discover_tables()
    result = sync_data(streams=streams)
    validate_sync(sync_result=result)
```

#### Scheduling

```python
from dagster_cron import build_schedule_from_cron_expression

postgres_sync_schedule = build_schedule_from_cron_expression(
    "0 */6 * * *",  # Every 6 hours
    job_name="postgres_to_iceberg"
)

mongodb_cdc_schedule = build_schedule_from_cron_expression(
    "*/5 * * * *",  # Every 5 minutes (CDC)
    job_name="mongodb_to_iceberg"
)
```

#### Multi-Database Orchestration

```python
DATABASES = ["postgres", "mongodb", "mysql"]

for db in DATABASES:
    @job(name=f"{db}_sync")
    def sync_job():
        streams = discover_tables(database=db)
        sync_data(database=db, streams=streams)
        validate_sync()
```

### 4. RisingWave Streaming Consumption

#### Architecture

```
OLake (Batch)          RisingWave (Streaming)
└─> Iceberg Tables ──────> Materialized Views
    (Snapshots)             (Real-time)
                                  ↓
                           Analytics Queries
```

#### Setup

```sql
-- 1. Create RisingWave source from Iceberg
CREATE SOURCE iceberg_users WITH (
    connector = 'iceberg',
    catalog_type = 'rest',
    rest_catalog_url = 'http://lakekeeper:8181',
    warehouse = 's3://bucket/warehouse',
    database = 'analytics',
    table = 'postgres_users'
);

-- 2. Create materialized view for aggregations
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    DATE_TRUNC('hour', updated_at) as hour,
    COUNT(*) as user_count,
    COUNT(DISTINCT country) as countries
FROM iceberg_users
WHERE updated_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', updated_at);

-- 3. Sink results back to Iceberg
CREATE SINK user_stats_sink INTO iceberg_sink
FROM user_stats
WITH (
    connector = 'iceberg',
    catalog_type = 'rest',
    rest_catalog_url = 'http://lakekeeper:8181',
    warehouse = 's3://bucket/warehouse',
    database = 'analytics',
    table = 'user_stats_hourly'
);
```

#### Real-time Analytics Pattern

```
MongoDB (source)
    ↓
OLake → Iceberg (batch snapshots, daily)
    ↓
RisingWave (ingest + aggregate)
    ↓
├─> Dashboards (sub-second latency)
├─> Alerts (anomaly detection)
└─> API (real-time metrics)
```

### 5. Multi-Catalog Strategies

#### Catalog Selection

```
┌─────────────────────────────────────┐
│  OLake Iceberg Writer Supports:     │
├─────────────────────────────────────┤
│ 1. REST (Lakekeeper)   – OpenSource │
│ 2. AWS Glue            – Managed    │
│ 3. JDBC                – Custom DB  │
│ 4. Hive MetaStore      – Legacy     │
└─────────────────────────────────────┘
```

#### Configuration Examples

**REST Catalog (Lakekeeper)**
```json
{
  "catalog_type": "rest",
  "rest_catalog_url": "http://lakekeeper:8181",
  "warehouse": "s3://bucket/warehouse"
}
```

**AWS Glue Catalog**
```json
{
  "catalog_type": "glue",
  "aws_region": "us-east-1",
  "warehouse": "s3://bucket/warehouse",
  "aws_access_key": "${AWS_ACCESS_KEY}",
  "aws_secret_key": "${AWS_SECRET_KEY}"
}
```

**JDBC Catalog (Custom DB)**
```json
{
  "catalog_type": "jdbc",
  "jdbc_url": "jdbc:postgresql://postgres:5432/iceberg_catalog",
  "jdbc_user": "iceberg_user",
  "jdbc_password": "${JDBC_PASSWORD}",
  "warehouse": "s3://bucket/warehouse"
}
```

**Hive MetaStore**
```json
{
  "catalog_type": "hive",
  "hive_metastore_uri": "thrift://hive:9083",
  "warehouse": "s3://bucket/warehouse"
}
```

#### Multi-Catalog Failover

```python
# Dynamically select catalog based on availability
CATALOGS = [
    {
        "name": "lakekeeper",
        "config": {"catalog_type": "rest", ...},
        "priority": 1
    },
    {
        "name": "glue",
        "config": {"catalog_type": "glue", ...},
        "priority": 2
    },
    {
        "name": "hive",
        "config": {"catalog_type": "hive", ...},
        "priority": 3
    }
]

def get_catalog():
    for catalog in sorted(CATALOGS, key=lambda x: x['priority']):
        if catalog_healthy(catalog['name']):
            return catalog['config']
    raise Exception("All catalogs unavailable")
```

---

## Deployment Patterns

### 1. Docker Compose for Development

#### Single-Node Setup

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"

  postgres-catalog:
    image: postgres:15
    environment:
      POSTGRES_DB: lakekeeper
      POSTGRES_USER: lakekeeper
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  lakekeeper:
    image: apache/iceberg:latest-rest
    environment:
      DATABASE_URL: postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres-catalog/lakekeeper
    ports:
      - "8181:8181"
    depends_on:
      - postgres-catalog

  olake:
    image: ghcr.io/datazip-inc/olake:latest
    volumes:
      - ./config:/etc/olake
      - ./state:/var/lib/olake
    environment:
      LAKEKEEPER_URL: http://lakekeeper:8181
      S3_ENDPOINT: http://minio:9000
      S3_ACCESS_KEY: minioadmin
      S3_SECRET_KEY: minioadmin
    command: sync --config /etc/olake/config.json
    depends_on:
      - lakekeeper
      - minio

volumes:
  postgres_data:
```

#### Configuration Files

**source.json** (PostgreSQL source):
```json
{
  "type": "postgres",
  "host": "source-postgres",
  "port": 5432,
  "database": "source_db",
  "username": "postgres",
  "password": "${PG_PASSWORD}",
  "update_method": {
    "replication_slot": "olake_slot",
    "publication": "olake_publication",
    "initial_wait_time": 120
  },
  "max_threads": 4
}
```

**destination.json** (Iceberg on MinIO):
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "http://lakekeeper:8181",
    "warehouse": "s3://lakehouse/warehouse",
    "s3_endpoint": "http://minio:9000",
    "aws_region": "us-east-1",
    "aws_access_key": "minioadmin",
    "aws_secret_key": "minioadmin",
    "iceberg_db": "source_analytics"
  }
}
```

#### Startup Commands

```bash
# Start services
docker-compose up -d

# Wait for services to be healthy
docker-compose exec postgres-catalog pg_isready -U lakekeeper
docker-compose exec lakekeeper curl -s http://localhost:8181/v1/config

# Initialize source database for CDC
docker-compose exec source-postgres psql -U postgres -d source_db << 'SQL'
  ALTER SYSTEM SET wal_level = logical;
  ALTER SYSTEM SET max_replication_slots = 4;
  SELECT pg_reload_conf();
  CREATE PUBLICATION olake_publication FOR ALL TABLES;
  SELECT pg_create_logical_replication_slot('olake_slot', 'pgoutput');
SQL

# Discover and sync
docker-compose exec olake olake discover --config /etc/olake/source.json
docker-compose exec olake olake sync --config /etc/olake/source.json \
                                      --destination /etc/olake/destination.json
```

### 2. Kubernetes Helm Deployment

#### Helm Chart Structure

```
olake-helm/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── statefulset.yaml
```

#### values.yaml

```yaml
replicaCount: 3

image:
  repository: ghcr.io/datazip-inc/olake
  tag: v1.0.0
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 4Gi

persistence:
  enabled: true
  size: 10Gi
  storageClass: fast-ssd

lakekeeper:
  url: http://lakekeeper:8181
  username: admin
  passwordSecret: lakekeeper-token

s3:
  endpoint: https://s3.amazonaws.com
  region: us-east-1
  bucket: data-lake

postgres:
  host: postgres.default.svc.cluster.local
  port: 5432
  database: source_db

monitoring:
  enabled: true
  prometheus: true
  interval: 30s
```

#### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: olake
spec:
  serviceName: olake
  replicas: 3
  selector:
    matchLabels:
      app: olake
  template:
    metadata:
      labels:
        app: olake
    spec:
      containers:
      - name: olake
        image: ghcr.io/datazip-inc/olake:v1.0.0
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
        volumeMounts:
        - name: config
          mountPath: /etc/olake
        - name: state
          mountPath: /var/lib/olake
        env:
        - name: LAKEKEEPER_URL
          valueFrom:
            configMapKeyRef:
              name: olake-config
              key: lakekeeper_url
        - name: S3_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: s3-credentials
              key: access_key
      volumes:
      - name: config
        configMap:
          name: olake-config
      volumeClaimTemplates:
      - metadata:
          name: state
        spec:
          accessModes: [ "ReadWriteOnce" ]
          storageClassName: fast-ssd
          resources:
            requests:
              storage: 10Gi
```

#### Deployment Commands

```bash
# Install Helm chart
helm repo add olake https://datazip-inc.github.io/olake-helm
helm install olake olake/olake \
  -f values-prod.yaml \
  --namespace data-platform \
  --create-namespace

# Upgrade with new configuration
helm upgrade olake olake/olake \
  -f values-prod.yaml \
  --namespace data-platform

# Monitor rollout
kubectl rollout status statefulset/olake -n data-platform

# View logs
kubectl logs -f deployment/olake-0 -n data-platform
```

### 3. CI/CD Pipeline Integration

#### GitHub Actions Workflow

```yaml
name: OLake Data Pipeline

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync-postgres:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Pull OLake image
        run: docker pull ghcr.io/datazip-inc/olake:latest

      - name: Run discovery
        run: |
          docker run --rm \
            -e PG_HOST=${{ secrets.PG_HOST }} \
            -e PG_PASSWORD=${{ secrets.PG_PASSWORD }} \
            -v ${{ github.workspace }}/config:/config \
            ghcr.io/datazip-inc/olake:latest \
            discover --config /config/source.json > streams.json

      - name: Run sync
        run: |
          docker run --rm \
            -e AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }} \
            -e AWS_SECRET_ACCESS_KEY=${{ secrets.AWS_SECRET_ACCESS_KEY }} \
            -e LAKEKEEPER_TOKEN=${{ secrets.LAKEKEEPER_TOKEN }} \
            -v ${{ github.workspace }}/config:/config \
            ghcr.io/datazip-inc/olake:latest \
            sync --config /config/source.json \
                 --catalog streams.json \
                 --destination /config/destination.json

      - name: Validate sync
        run: |
          # Query Iceberg to verify data
          docker run --rm \
            duckdb \
            "SELECT COUNT(*) FROM read_iceberg('s3://bucket/warehouse/analytics/users')"

      - name: Notify on failure
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: ${{ github.event.number }},
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'OLake sync failed! Check logs.'
            })
```

### 4. High Availability Setup

#### Multi-Region Deployment

```yaml
# Primary Region (us-east-1)
Primary:
  - OLake Workers (3 replicas)
  - Lakekeeper (3 replicas)
  - PostgreSQL (primary)
  - MinIO/S3 (replication enabled)

# Secondary Region (us-west-2) 
Standby:
  - OLake Workers (1 replica, ready to scale)
  - Lakekeeper (read-only)
  - PostgreSQL (replica)
  - S3 Cross-region replication

Failover Logic:
  - Monitor primary lakekeeper health
  - On failure: Switch Iceberg queries to secondary
  - OLake automatically retries to secondary S3
```

#### Health Checks

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  exec:
    command:
    - /bin/sh
    - -c
    - "curl -f http://localhost:8080/ready || exit 1"
  initialDelaySeconds: 5
  periodSeconds: 5

startupProbe:
  exec:
    command:
    - /bin/sh
    - -c
    - "olake check --config /etc/olake/config.json"
  failureThreshold: 30
  periodSeconds: 2
```

### 5. Monitoring with Prometheus/Grafana

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 30s

scrape_configs:
  - job_name: 'olake'
    static_configs:
      - targets: ['olake:9090']
    metrics_path: '/metrics'

  - job_name: 'lakekeeper'
    static_configs:
      - targets: ['lakekeeper:8181']

  - job_name: 'iceberg'
    static_configs:
      - targets: ['iceberg-exporter:9091']
```

#### Key Metrics

```
# OLake specific
olake_sync_duration_seconds{database="postgres", status="success"}
olake_records_processed_total{source="mongodb", sink="iceberg"}
olake_errors_total{type="network_timeout", database="mysql"}
olake_checkpoint_lag_seconds{stream="postgres.public.users"}
olake_file_count_total{table="users", status="small"}

# Iceberg specific
iceberg_snapshots_total{table="analytics.users"}
iceberg_manifest_files{table="analytics.users"}
iceberg_table_size_bytes{table="analytics.users"}
iceberg_query_latency_ms{catalog="lakekeeper"}

# S3 specific
s3_put_object_duration_seconds{bucket="data-lake"}
s3_list_objects_duration_seconds{bucket="data-lake"}
s3_get_object_errors_total{bucket="data-lake"}
```

#### Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "OLake Replication",
    "panels": [
      {
        "title": "Records/sec",
        "targets": [
          {
            "expr": "rate(olake_records_processed_total[5m])"
          }
        ]
      },
      {
        "title": "Checkpoint Lag",
        "targets": [
          {
            "expr": "olake_checkpoint_lag_seconds"
          }
        ]
      },
      {
        "title": "Small Files Count",
        "targets": [
          {
            "expr": "olake_file_count_total{status='small'}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(olake_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

---

## Best Practices

### 1. Partitioning Strategies

#### Table Design

```json
{
  "streams": [
    {
      "name": "users",
      "partitioning": {
        "columns": ["country", "created_date"],
        "strategy": "date_range"
      }
    }
  ]
}
```

**Partitioning Strategy Selection:**

| Strategy | Best For | Example |
|----------|----------|---------|
| Time-based | Historical data, time-series | `PARTITION BY year, month` |
| Categorical | Fixed categories | `PARTITION BY region, product_type` |
| Range | Numeric ranges | `PARTITION BY (id % 100)` |
| Hybrid | Large tables with time + category | `PARTITION BY year, country` |

#### Configuration Example

```json
{
  "writer": {
    "partitioning": {
      "type": "identity",
      "columns": [
        {
          "name": "country",
          "type": "identity"
        },
        {
          "name": "created_date",
          "type": "day"  // Bucketed by day
        }
      ]
    }
  }
}
```

### 2. Compaction Schedules

#### The Small File Problem

```
Issue: CDC writes small files
Result: Slow queries, high metadata overhead
Solution: Compact files regularly

OLake writes:
├── Batch 1: 1.2 MB
├── Batch 2: 0.8 MB  
├── Batch 3: 1.5 MB  
└── Total: 3 files < 5 MB (inefficient!)

After compaction:
└── Compacted: 3.5 MB (1 file, query 3x faster)
```

#### Compaction Strategy

```python
# Dagster job for periodic compaction
@op
def compact_iceberg_tables():
    """Compact small files in Iceberg tables"""
    from pyspark.sql import SparkSession
    
    spark = SparkSession.builder.appName("iceberg-compaction").getOrCreate()
    
    # Compact tables with many small files
    tables = [
        "analytics.postgres_users",
        "analytics.mongodb_events",
        "analytics.mysql_orders"
    ]
    
    for table in tables:
        df = spark.read.format("iceberg").load(table)
        
        # Get file statistics
        files_df = spark.sql(f"SELECT * FROM {table}.files")
        small_files = files_df.filter("file_size_in_bytes < 134217728").count()
        
        if small_files > 5:
            # Trigger compaction
            spark.sql(f"""
                CALL system.rewrite_data_files('{table}')
            """)
            
            context.log.info(f"Compacted {table}: {small_files} files")

@schedule(
    job_name="compact_iceberg_tables",
    cron_schedule="0 2 * * *"  # Daily at 2 AM
)
def daily_compaction():
    pass
```

#### Monitoring Small Files

```sql
-- Find tables with compaction needed
SELECT 
    table_name,
    COUNT(*) as file_count,
    SUM(file_size_in_bytes) as total_size,
    AVG(file_size_in_bytes) as avg_size,
    COUNT(CASE WHEN file_size_in_bytes < 134217728 THEN 1 END) as small_files
FROM iceberg.analytics.files_v1
WHERE table_name IN (
    'postgres_users', 
    'mongodb_events',
    'mysql_orders'
)
GROUP BY table_name
HAVING small_files > 5
ORDER BY small_files DESC;
```

### 3. Security Patterns

#### Secrets Management

```bash
# Use environment variables (not in config files!)
export PG_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id postgres/password \
  --query SecretString --output text)

export S3_ACCESS_KEY=$(aws secretsmanager get-secret-value \
  --secret-id s3/access-key \
  --query SecretString --output text)

export LAKEKEEPER_TOKEN=$(aws secretsmanager get-secret-value \
  --secret-id lakekeeper/token \
  --query SecretString --output text)

# Configure OLake with secrets from environment
olake sync --config /etc/olake/config.json
```

#### Encryption in Transit

```json
{
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://lakekeeper.example.com",  // HTTPS
    "s3_endpoint": "https://s3.amazonaws.com",             // HTTPS
    "ssl_verify": true
  }
}
```

#### Data Encryption at Rest

```bash
# S3 Server-Side Encryption
aws s3api put-bucket-encryption \
  --bucket data-lake \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789:key/..."
      }
    }]
  }'

# PostgreSQL source encryption
psql -h postgres.example.com -U postgres -d source_db << 'SQL'
-- Enable SSL for all connections
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/etc/ssl/certs/server.crt';
ALTER SYSTEM SET ssl_key_file = '/etc/ssl/private/server.key';
SELECT pg_reload_conf();
SQL
```

#### Access Control

```yaml
# Kubernetes RBAC for OLake service account
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: olake-sync
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list"]
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]  # Not "list" for security

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: olake-sync
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: olake-sync
subjects:
  - kind: ServiceAccount
    name: olake
```

### 4. Performance Tuning

#### Parallel Processing Configuration

```json
{
  "max_threads": 8,
  "chunk_size": 100000,
  "batch_size": 5000,
  "writer": {
    "parallel_uploads": 4,
    "buffer_size_mb": 256
  }
}
```

**Parameter Tuning Guide:**

```
max_threads:
  ├─ Too low (<2)  → Underutilizes resources
  ├─ Optimal (4-8) → Good balance for most workloads
  └─ Too high (>16)→ Excessive context switching, DB stress

chunk_size:
  ├─ Small (10K)   → More chunks, better resume capability
  ├─ Medium (100K) → Balanced
  └─ Large (1M)    → Fewer chunks, higher latency

batch_size:
  ├─ Small (1K)    → Frequent writes, high metadata overhead
  ├─ Medium (5K)   → Balanced
  └─ Large (50K)   → Fewer writes, risk of OOM
```

#### Memory Optimization

```yaml
# Kubernetes resource optimization
resources:
  requests:
    cpu: 1000m        # 1 core
    memory: 2Gi
  limits:
    cpu: 2000m        # Max 2 cores
    memory: 4Gi

# Configure for large tables
env:
  - name: GOMAXPROCS
    value: "2"        # Limit Go runtime threads
  - name: GOMEMLIMIT
    value: "3500M"    # Heap limit (slightly below container limit)
```

#### Throughput Monitoring

```sql
-- Monitor replication throughput
SELECT
  stream_id,
  COUNT(*) as records_processed,
  EXTRACT(EPOCH FROM MAX(checkpoint_time) - MIN(checkpoint_time)) as duration_sec,
  ROUND(COUNT(*) / NULLIF(
    EXTRACT(EPOCH FROM MAX(checkpoint_time) - MIN(checkpoint_time)), 
    0), 2) as records_per_sec
FROM olake_sync_history
WHERE checkpoint_time > NOW() - INTERVAL '1 hour'
GROUP BY stream_id
ORDER BY records_per_sec DESC;
```

### 5. Troubleshooting Common Issues

#### Issue: Checkpoint Lag Growing

```bash
# Check current lag
kubectl exec -it olake-0 -n data-platform -- \
  curl localhost:9090/metrics | grep checkpoint_lag

# Diagnosis
kubectl logs olake-0 -n data-platform | grep -i "lag\|slow\|error"

# Solution: Increase parallelism
kubectl patch statefulset olake -n data-platform --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [
    {"name": "MAX_THREADS", "value": "16"}
  ]}
]'
```

#### Issue: Too Many Small Files

```bash
# Identify tables with small file problem
docker run --rm duckdb << 'SQL'
SELECT 
  table_name,
  COUNT(*) as file_count,
  ROUND(AVG(file_size_in_bytes) / 1048576, 2) as avg_size_mb
FROM read_iceberg('s3://bucket/warehouse/*/*/files_v1')
GROUP BY table_name
HAVING COUNT(*) > 10 AND AVG(file_size_in_bytes) < 134217728
ORDER BY file_count DESC;
SQL

# Trigger compaction immediately
docker run --rm \
  -e SPARK_SUBMIT_ARGS="--driver-memory 4G" \
  spark:latest \
  spark-submit --class org.apache.iceberg.spark.procedures.RemoveOrphanFilesAction \
    /opt/spark/jars/iceberg-spark-runtime.jar \
    s3://bucket/warehouse/analytics/users
```

#### Issue: Memory Exhaustion

```bash
# Check memory usage
kubectl top pod olake-0 -n data-platform

# Get heap dump
kubectl exec olake-0 -n data-platform -- \
  curl -X POST localhost:6060/debug/pprof/heap > heap.dump

# Analyze (locally)
go tool pprof heap.dump
(pprof) top10
```

#### Issue: Connection Pool Exhaustion

```json
{
  "source": {
    "max_connections": 10,
    "connection_timeout_ms": 30000,
    "idle_timeout_ms": 600000
  }
}
```

```sql
-- Monitor source DB connections
-- PostgreSQL
SELECT count(*) as connection_count 
FROM pg_stat_activity 
WHERE application_name = 'olake';

-- MySQL
SHOW PROCESSLIST;
```

---

## Reference Documentation

- **OLake Docs**: https://olake.io/docs
- **Apache Iceberg**: https://iceberg.apache.org/
- **Lakekeeper**: https://docs.lakekeeper.io/
- **LakeFS**: https://docs.lakefs.io/
- **Kubernetes Helm**: https://helm.sh/docs/

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**OLake Version**: v1.0+


> Source: `docs/data_engineering/olake/olake-data-models-schemas-ontologies.md`

# OLake Data Models, Schemas, and Ontologies

## Executive Summary

This document provides a comprehensive ontology of OLake's data models, schemas, and type systems. OLake is an open-source data replication tool that captures changes from operational databases (PostgreSQL, MySQL, MongoDB, Oracle) and loads them into data lakes using Apache Iceberg table format.

**Key Findings:**
- OLake uses a three-file configuration pattern: `source.json`, `destination.json`, and `streams.json`
- Supports multiple catalog backends: REST, JDBC, AWS Glue, Hive Metastore
- Provides automatic type mapping from source databases to Iceberg/Parquet types
- Implements CDC (Change Data Capture) with exactly-once semantics
- Supports schema evolution without breaking pipelines

---

## 1. Domain Model

### 1.1 Core Entities

```
┌─────────────────────────────────────────────────────────────────┐
│                      OLake Domain Model                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Source     │         │   Pipeline   │         │ Destination  │
│              │────────>│              │────────>│              │
│ - Database   │ Config  │ - State      │ Writes  │ - Iceberg    │
│ - Connection │         │ - Metadata   │         │ - Catalog    │
│ - CDC Setup  │         │ - Transforms │         │ - Storage    │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │ Discovers              │ Manages                 │ Stores
       ▼                        ▼                         ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Stream     │         │    State     │         │    Table     │
│              │         │              │         │              │
│ - Schema     │         │ - Checkpoint │         │ - Snapshots  │
│ - Sync Mode  │         │ - Position   │         │ - Partitions │
│ - Selection  │         │ - Offsets    │         │ - Metadata   │
└──────────────┘         └──────────────┘         └──────────────┘
       │                                                  │
       │ Contains                                         │ References
       ▼                                                  ▼
┌──────────────┐                                  ┌──────────────┐
│   Column     │                                  │  Data File   │
│              │                                  │              │
│ - Name       │                                  │ - Parquet    │
│ - Type       │                                  │ - Path       │
│ - Nullable   │                                  │ - Metrics    │
└──────────────┘                                  └──────────────┘
```

### 1.2 Entity Relationships

**Source → Stream** (1:N)
- A source database contains multiple streams (tables/collections)
- Each stream is independently selectable and configurable

**Stream → Column** (1:N)
- Each stream has a schema composed of columns
- Columns have types that map to Iceberg types

**Pipeline → State** (1:1)
- Each pipeline maintains a single state object
- State tracks CDC position, checkpoints, and offsets

**Destination → Table** (1:N)
- A destination (Iceberg namespace) contains multiple tables
- Each table corresponds to a source stream

**Table → Snapshot** (1:N)
- Tables maintain a history of snapshots
- Each sync operation creates a new snapshot

**Table → DataFile** (1:N)
- Tables reference multiple Parquet data files
- Files are organized by partitions

### 1.3 State Machine Models

#### Pipeline States

```
┌─────────────┐
│   INITIAL   │
│ (not run)   │
└──────┬──────┘
       │ start
       ▼
┌─────────────┐
│ DISCOVERING │
│ (introspect)│
└──────┬──────┘
       │ discover complete
       ▼
┌─────────────┐      error      ┌─────────────┐
│  FULL_LOAD  │────────────────>│   FAILED    │
│ (initial)   │                 │             │
└──────┬──────┘                 └─────────────┘
       │ load complete              ▲
       ▼                            │
┌─────────────┐                    │ error
│     CDC     │────────────────────┘
│ (streaming) │
└──────┬──────┘
       │ stop
       ▼
┌─────────────┐
│   STOPPED   │
│             │
└─────────────┘
```

#### Replication States (Per Stream)

```
NOT_SELECTED ──> SELECTED ──> SYNCING ──> SYNCED
                                  │
                                  │ error
                                  ▼
                              ERROR_STATE
                                  │
                                  │ retry
                                  └──> SYNCING
```

### 1.4 Metadata Structures

#### Pipeline Metadata
```json
{
  "pipeline_id": "uuid",
  "source_type": "postgres|mysql|mongodb|oracle",
  "destination_type": "iceberg",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "state": {
    "last_sync": "timestamp",
    "checkpoint": {
      "lsn": "pg_lsn",
      "gtid": "mysql_gtid",
      "resume_token": "mongodb_token"
    },
    "stream_states": [
      {
        "stream_name": "table_name",
        "last_processed_offset": "offset_value",
        "row_count": 12345
      }
    ]
  }
}
```

---

## 2. Schema Definitions

### 2.1 Configuration Schemas

#### source.json (PostgreSQL Example)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["host", "port", "database", "username", "password"],
  "properties": {
    "host": {
      "type": "string",
      "description": "Database hostname or IP address"
    },
    "port": {
      "type": "integer",
      "default": 5432,
      "description": "Database port"
    },
    "database": {
      "type": "string",
      "description": "Database name to replicate"
    },
    "username": {
      "type": "string",
      "description": "Database user with replication privileges"
    },
    "password": {
      "type": "string",
      "description": "User password (encrypted at rest)"
    },
    "ssl": {
      "type": "object",
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["disable", "require", "verify-ca", "verify-full"],
          "default": "require"
        },
        "ca_cert": {
          "type": "string",
          "description": "Path to CA certificate for SSL verification"
        }
      }
    },
    "update_method": {
      "type": "object",
      "description": "CDC configuration for logical replication",
      "properties": {
        "replication_slot": {
          "type": "string",
          "description": "Name of the logical replication slot"
        },
        "publication": {
          "type": "string",
          "description": "Name of the publication for CDC"
        },
        "initial_wait_time": {
          "type": "integer",
          "default": 120,
          "description": "Seconds to wait for initial replication setup"
        }
      }
    },
    "max_threads": {
      "type": "integer",
      "default": 5,
      "minimum": 1,
      "maximum": 20,
      "description": "Parallel threads for full load"
    }
  }
}
```

**Annotated Example:**
```json
{
  "host": "postgres.example.com",        // Source database endpoint
  "port": 5432,
  "database": "production",              // Database to replicate
  "username": "olake_user",              // User with REPLICATION privilege
  "password": "<SECURE_PASSWORD>",
  "ssl": {
    "mode": "require"                    // Enforce TLS
  },
  "update_method": {
    "replication_slot": "olake_slot",    // Created with pg_create_logical_replication_slot
    "publication": "olake_pub",          // Created with CREATE PUBLICATION
    "initial_wait_time": 120
  },
  "max_threads": 5                       // Parallel table dumps during full load
}
```

#### destination.json (Iceberg with REST Catalog)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "writer"],
  "properties": {
    "type": {
      "type": "string",
      "enum": ["ICEBERG"],
      "description": "Destination writer type"
    },
    "writer": {
      "type": "object",
      "required": ["catalog_type", "iceberg_s3_path"],
      "properties": {
        "catalog_type": {
          "type": "string",
          "enum": ["rest", "jdbc", "glue", "hive"],
          "description": "Iceberg catalog backend"
        },
        "rest_catalog_url": {
          "type": "string",
          "format": "uri",
          "description": "REST catalog endpoint (required if catalog_type=rest)"
        },
        "jdbc_url": {
          "type": "string",
          "description": "JDBC connection string (required if catalog_type=jdbc)"
        },
        "iceberg_s3_path": {
          "type": "string",
          "format": "uri",
          "pattern": "^s3://",
          "description": "S3 path for Iceberg warehouse"
        },
        "s3_endpoint": {
          "type": "string",
          "format": "uri",
          "description": "Custom S3 endpoint (for R2, MinIO, etc.)"
        },
        "aws_region": {
          "type": "string",
          "default": "us-east-1",
          "description": "AWS region or 'auto' for S3-compatible storage"
        },
        "aws_access_key": {
          "type": "string",
          "description": "S3 access key ID"
        },
        "aws_secret_key": {
          "type": "string",
          "description": "S3 secret access key (encrypted)"
        },
        "iceberg_db": {
          "type": "string",
          "description": "Iceberg namespace/database for tables"
        },
        "token": {
          "type": "string",
          "description": "Bearer token for REST catalog auth"
        },
        "partition_spec": {
          "type": "object",
          "description": "Default partition specification for tables",
          "properties": {
            "partition_by": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "Columns to partition by (e.g., ['year(timestamp)', 'region'])"
            }
          }
        }
      }
    }
  }
}
```

**Annotated Example (Cloudflare R2 with REST Catalog):**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://account-id.r2.cloudflarestorage.com/catalog",  // R2 Data Catalog endpoint
    "iceberg_s3_path": "s3://my-bucket/warehouse",                              // R2 bucket path
    "s3_endpoint": "https://account-id.r2.cloudflarestorage.com",              // R2 S3-compatible endpoint
    "aws_region": "auto",                                                       // R2 uses 'auto'
    "aws_access_key": "<R2_ACCESS_KEY>",
    "aws_secret_key": "<R2_SECRET_KEY>",
    "iceberg_db": "production",                                                 // Iceberg namespace
    "token": "<R2_API_TOKEN>",                                                  // For catalog auth
    "partition_spec": {
      "partition_by": ["year(created_at)"]                                      // Partition by year
    }
  }
}
```

#### streams.json (Generated by Discover)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "selected_streams": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of stream names to replicate"
    },
    "streams": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "stream": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "Table/collection name"
              },
              "namespace": {
                "type": "string",
                "description": "Schema or database name"
              },
              "json_schema": {
                "type": "object",
                "description": "JSON Schema defining stream columns",
                "properties": {
                  "type": {
                    "const": "object"
                  },
                  "properties": {
                    "type": "object",
                    "additionalProperties": {
                      "type": "object",
                      "properties": {
                        "type": {
                          "type": ["string", "array"],
                          "description": "Column type (string, integer, number, boolean, array, object, null)"
                        },
                        "format": {
                          "type": "string",
                          "description": "Optional format (date, date-time, uuid, etc.)"
                        }
                      }
                    }
                  }
                }
              },
              "supported_sync_modes": {
                "type": "array",
                "items": {
                  "type": "string",
                  "enum": ["full_refresh", "incremental"]
                }
              }
            }
          },
          "sync_mode": {
            "type": "string",
            "enum": ["full_refresh", "incremental"],
            "description": "Selected sync mode for this stream"
          },
          "cursor_field": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Columns used for incremental cursor"
          },
          "primary_key": {
            "type": "array",
            "items": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "description": "Primary key columns"
          }
        }
      }
    }
  }
}
```

**Annotated Example:**
```json
{
  "selected_streams": ["public.users", "public.orders"],  // Only these will be replicated
  "streams": [
    {
      "stream": {
        "name": "users",                                   // Table name
        "namespace": "public",                             // Schema
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {
              "type": "integer"                            // Maps to Iceberg INT
            },
            "email": {
              "type": "string"                             // Maps to Iceberg STRING
            },
            "created_at": {
              "type": "string",
              "format": "date-time"                        // Maps to Iceberg TIMESTAMP
            },
            "metadata": {
              "type": "object"                             // Maps to Iceberg STRUCT
            }
          }
        },
        "supported_sync_modes": ["full_refresh", "incremental"]
      },
      "sync_mode": "incremental",                          // Use CDC after initial load
      "cursor_field": ["updated_at"],                      // Track changes by this column
      "primary_key": [["id"]]                              // Deduplication key
    }
  ]
}
```

### 2.2 State File Schemas

#### Pipeline State

```json
{
  "version": "1.0",
  "pipeline_id": "uuid",
  "last_sync_timestamp": "2025-01-15T10:30:00Z",
  "checkpoint": {
    "postgres": {
      "lsn": "0/3000060",                                  // PostgreSQL Log Sequence Number
      "snapshot_name": "olake-snapshot-1",
      "slot_name": "olake_slot"
    },
    "mysql": {
      "gtid": "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5", // MySQL GTID
      "binlog_file": "mysql-bin.000003",
      "binlog_position": 73
    },
    "mongodb": {
      "resume_token": "826F5D4D000000012B022C0100296E5A10...",  // MongoDB change stream token
      "cluster_time": {
        "t": 1642251600,
        "i": 1
      }
    }
  },
  "stream_states": {
    "public.users": {
      "last_processed_offset": "2025-01-15T10:29:55Z",
      "rows_synced": 125000,
      "snapshot_id": "8345678901234567890",                // Iceberg snapshot ID
      "data_files_count": 12,
      "partition_values": {
        "year": 2025
      }
    }
  }
}
```

### 2.3 Catalog Metadata Schemas

#### Iceberg Table Metadata (v2)

```json
{
  "format-version": 2,
  "table-uuid": "9c12d441-03fe-4693-9a96-a0705ddf69c1",
  "location": "s3://bucket/warehouse/db/users",
  "last-updated-ms": 1642251600000,
  "last-column-id": 5,
  "schema": {
    "type": "struct",
    "schema-id": 0,
    "fields": [
      {
        "id": 1,
        "name": "id",
        "required": true,
        "type": "int"
      },
      {
        "id": 2,
        "name": "email",
        "required": true,
        "type": "string"
      },
      {
        "id": 3,
        "name": "created_at",
        "required": false,
        "type": "timestamptz"
      },
      {
        "id": 4,
        "name": "metadata",
        "required": false,
        "type": {
          "type": "struct",
          "fields": [
            {
              "id": 5,
              "name": "preferences",
              "required": false,
              "type": "string"
            }
          ]
        }
      }
    ]
  },
  "current-schema-id": 0,
  "partition-spec": [
    {
      "name": "created_year",
      "transform": "year",
      "source-id": 3,
      "field-id": 1000
    }
  ],
  "default-spec-id": 0,
  "last-partition-id": 1000,
  "properties": {
    "write.parquet.compression-codec": "zstd",
    "write.metadata.compression-codec": "gzip"
  },
  "current-snapshot-id": 8345678901234567890,
  "refs": {
    "main": {
      "snapshot-id": 8345678901234567890,
      "type": "branch"
    }
  },
  "snapshots": [
    {
      "snapshot-id": 8345678901234567890,
      "parent-snapshot-id": 8345678901234567889,
      "timestamp-ms": 1642251600000,
      "summary": {
        "operation": "append",
        "added-data-files": "3",
        "added-records": "50000",
        "total-data-files": "15",
        "total-records": "125000"
      },
      "manifest-list": "s3://bucket/warehouse/db/users/metadata/snap-8345678901234567890.avro"
    }
  ],
  "snapshot-log": [
    {
      "timestamp-ms": 1642251600000,
      "snapshot-id": 8345678901234567890
    }
  ],
  "metadata-log": [
    {
      "timestamp-ms": 1642251600000,
      "metadata-file": "s3://bucket/warehouse/db/users/metadata/v1.metadata.json"
    }
  ]
}
```

---

## 3. Type Systems

### 3.1 PostgreSQL → Iceberg Type Mappings

| PostgreSQL Type | Iceberg Type | Parquet Type | Notes |
|-----------------|--------------|--------------|-------|
| `smallint` | `int` | `INT32` | 16-bit integer |
| `integer` | `int` | `INT32` | 32-bit integer |
| `bigint` | `long` | `INT64` | 64-bit integer |
| `real` | `float` | `FLOAT` | 32-bit floating point |
| `double precision` | `double` | `DOUBLE` | 64-bit floating point |
| `numeric(p,s)` | `decimal(p,s)` | `FIXED_LEN_BYTE_ARRAY` | Arbitrary precision decimal |
| `boolean` | `boolean` | `BOOLEAN` | True/false value |
| `char(n)` | `string` | `BYTE_ARRAY` | Fixed-length string |
| `varchar(n)` | `string` | `BYTE_ARRAY` | Variable-length string |
| `text` | `string` | `BYTE_ARRAY` | Unlimited text |
| `bytea` | `binary` | `BYTE_ARRAY` | Binary data |
| `date` | `date` | `INT32` | Days since epoch |
| `timestamp` | `timestamp` | `INT64` | Microseconds since epoch (no timezone) |
| `timestamptz` | `timestamptz` | `INT64` | Microseconds since epoch (with timezone) |
| `time` | `time` | `INT64` | Microseconds since midnight |
| `interval` | `string` | `BYTE_ARRAY` | Stored as ISO 8601 string |
| `uuid` | `uuid` | `FIXED_LEN_BYTE_ARRAY(16)` | 128-bit UUID |
| `json` | `string` | `BYTE_ARRAY` | Serialized JSON string |
| `jsonb` | `string` | `BYTE_ARRAY` | Serialized JSON string |
| `array[type]` | `list<type>` | `LIST` | Arrays map to Iceberg lists |
| `composite type` | `struct<fields>` | `STRUCT` | Custom types map to structs |
| `enum` | `string` | `BYTE_ARRAY` | Enum values as strings |
| `point` | `struct<x: double, y: double>` | `STRUCT` | Geometric point |
| `inet` | `string` | `BYTE_ARRAY` | IP address as string |
| `cidr` | `string` | `BYTE_ARRAY` | Network address as string |

### 3.2 MySQL → Iceberg Type Mappings

| MySQL Type | Iceberg Type | Parquet Type | Notes |
|------------|--------------|--------------|-------|
| `TINYINT` | `int` | `INT32` | 8-bit integer |
| `SMALLINT` | `int` | `INT32` | 16-bit integer |
| `MEDIUMINT` | `int` | `INT32` | 24-bit integer |
| `INT` | `int` | `INT32` | 32-bit integer |
| `BIGINT` | `long` | `INT64` | 64-bit integer |
| `FLOAT` | `float` | `FLOAT` | 32-bit floating point |
| `DOUBLE` | `double` | `DOUBLE` | 64-bit floating point |
| `DECIMAL(p,s)` | `decimal(p,s)` | `FIXED_LEN_BYTE_ARRAY` | Arbitrary precision decimal |
| `BIT` | `boolean` | `BOOLEAN` | Boolean value |
| `CHAR(n)` | `string` | `BYTE_ARRAY` | Fixed-length string |
| `VARCHAR(n)` | `string` | `BYTE_ARRAY` | Variable-length string |
| `TEXT` | `string` | `BYTE_ARRAY` | Long text |
| `MEDIUMTEXT` | `string` | `BYTE_ARRAY` | Medium text (16MB max) |
| `LONGTEXT` | `string` | `BYTE_ARRAY` | Long text (4GB max) |
| `BINARY(n)` | `binary` | `BYTE_ARRAY` | Fixed-length binary |
| `VARBINARY(n)` | `binary` | `BYTE_ARRAY` | Variable-length binary |
| `BLOB` | `binary` | `BYTE_ARRAY` | Binary large object |
| `DATE` | `date` | `INT32` | Date without time |
| `DATETIME` | `timestamp` | `INT64` | Date and time (no timezone) |
| `TIMESTAMP` | `timestamptz` | `INT64` | Date and time (with timezone) |
| `TIME` | `time` | `INT64` | Time without date |
| `YEAR` | `int` | `INT32` | Year value (e.g., 2025) |
| `JSON` | `string` | `BYTE_ARRAY` | Serialized JSON |
| `ENUM` | `string` | `BYTE_ARRAY` | Enum values as strings |
| `SET` | `list<string>` | `LIST` | Set stored as list |
| `GEOMETRY` | `binary` | `BYTE_ARRAY` | WKB (Well-Known Binary) format |

### 3.3 MongoDB → Iceberg Type Mappings

| MongoDB BSON Type | Iceberg Type | Parquet Type | Notes |
|-------------------|--------------|--------------|-------|
| `Double` | `double` | `DOUBLE` | 64-bit floating point |
| `String` | `string` | `BYTE_ARRAY` | UTF-8 string |
| `Object` | `struct<...>` | `STRUCT` | Nested document |
| `Array` | `list<type>` | `LIST` | Array of elements |
| `Binary Data` | `binary` | `BYTE_ARRAY` | Binary data |
| `ObjectId` | `string` | `BYTE_ARRAY` | Hex string representation |
| `Boolean` | `boolean` | `BOOLEAN` | True/false |
| `Date` | `timestamptz` | `INT64` | Milliseconds since epoch |
| `Null` | `null` | - | NULL value |
| `32-bit Integer` | `int` | `INT32` | 32-bit signed integer |
| `Timestamp` | `timestamptz` | `INT64` | BSON timestamp |
| `64-bit Integer` | `long` | `INT64` | 64-bit signed integer |
| `Decimal128` | `decimal(38,18)` | `FIXED_LEN_BYTE_ARRAY` | High-precision decimal |
| `MinKey` | `string` | `BYTE_ARRAY` | Special type (string representation) |
| `MaxKey` | `string` | `BYTE_ARRAY` | Special type (string representation) |

### 3.4 Complex Type Handling

#### Nested Objects (PostgreSQL JSONB → Iceberg Struct)

**Source (PostgreSQL):**
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  profile JSONB
);

INSERT INTO users VALUES (1, '{"name": "Alice", "address": {"city": "NYC", "zip": "10001"}}');
```

**Destination (Iceberg Schema):**
```json
{
  "type": "struct",
  "fields": [
    {
      "id": 1,
      "name": "id",
      "required": true,
      "type": "int"
    },
    {
      "id": 2,
      "name": "profile",
      "required": false,
      "type": {
        "type": "struct",
        "fields": [
          {
            "id": 3,
            "name": "name",
            "required": false,
            "type": "string"
          },
          {
            "id": 4,
            "name": "address",
            "required": false,
            "type": {
              "type": "struct",
              "fields": [
                {
                  "id": 5,
                  "name": "city",
                  "required": false,
                  "type": "string"
                },
                {
                  "id": 6,
                  "name": "zip",
                  "required": false,
                  "type": "string"
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

#### Arrays (PostgreSQL Array → Iceberg List)

**Source:**
```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  tags TEXT[]
);

INSERT INTO products VALUES (1, ARRAY['electronics', 'laptop', 'sale']);
```

**Destination (Iceberg Schema):**
```json
{
  "type": "struct",
  "fields": [
    {
      "id": 1,
      "name": "id",
      "required": true,
      "type": "int"
    },
    {
      "id": 2,
      "name": "tags",
      "required": false,
      "type": {
        "type": "list",
        "element-id": 3,
        "element-required": false,
        "element": "string"
      }
    }
  ]
}
```

### 3.5 NULL Handling and Default Values

**Rule:** OLake preserves NULL semantics from source databases.

- **PostgreSQL:** `NULL` → Iceberg `NULL` (column must not be `required: true`)
- **MySQL:** `NULL` vs `NOT NULL` → Iceberg `required` field
- **MongoDB:** Missing fields → Iceberg `NULL`

**Default Values:**
- OLake does **not** apply default values during replication
- Default values must be handled at query time by the query engine
- Iceberg v2 spec supports default values in metadata (OLake respects this)

### 3.6 Timestamp and Timezone Conversions

**PostgreSQL:**
- `timestamp` → Iceberg `timestamp` (local time, no timezone info)
- `timestamptz` → Iceberg `timestamptz` (UTC normalized)

**MySQL:**
- `DATETIME` → Iceberg `timestamp` (local time)
- `TIMESTAMP` → Iceberg `timestamptz` (UTC converted)

**MongoDB:**
- `Date` → Iceberg `timestamptz` (stored as UTC milliseconds)

**Timezone Handling:**
OLake converts all `timestamptz` values to UTC before writing to Iceberg. Query engines handle timezone conversions for display.

---

## 4. API Contracts

### 4.1 Source Connector Interface

OLake source connectors implement a standard interface:

```python
class SourceConnector:
    """Base interface for all OLake source connectors."""
    
    def discover(self, config: Dict) -> List[Stream]:
        """
        Introspect source database and return available streams.
        
        Args:
            config: Source configuration from source.json
            
        Returns:
            List of Stream objects with schema and metadata
        """
        pass
    
    def read(
        self,
        config: Dict,
        catalog: Catalog,
        state: Optional[State]
    ) -> Generator[Record, None, State]:
        """
        Read data from source (full load or CDC).
        
        Args:
            config: Source configuration
            catalog: Selected streams and sync modes
            state: Previous pipeline state (for incremental sync)
            
        Yields:
            Record objects with data and metadata
            
        Returns:
            Updated state object
        """
        pass
    
    def check(self, config: Dict) -> CheckResult:
        """
        Test source connection and validate configuration.
        
        Args:
            config: Source configuration
            
        Returns:
            CheckResult with success status and error messages
        """
        pass
```

**Stream Object:**
```python
@dataclass
class Stream:
    name: str                          # Table/collection name
    namespace: str                     # Schema or database
    json_schema: Dict                  # JSON Schema for columns
    supported_sync_modes: List[str]    # ["full_refresh", "incremental"]
    source_defined_cursor: bool        # True if CDC available
    source_defined_primary_key: List[List[str]]  # Composite keys supported
    default_cursor_field: Optional[List[str]]     # Default cursor column
```

**Record Object:**
```python
@dataclass
class Record:
    stream: str                        # Stream name
    data: Dict[str, Any]               # Row data
    emitted_at: int                    # Timestamp (ms)
    namespace: str                     # Schema/database
    
    # CDC metadata
    source_metadata: Optional[Dict] = None  # LSN, GTID, resume_token, etc.
    operation: Optional[str] = None    # "INSERT", "UPDATE", "DELETE"
```

### 4.2 Destination Writer Interface

```python
class IcebergWriter:
    """OLake destination writer for Apache Iceberg."""
    
    def write_batch(
        self,
        stream: str,
        records: List[Record],
        catalog: IcebergCatalog,
        config: Dict
    ) -> WriteResult:
        """
        Write a batch of records to Iceberg table.
        
        Args:
            stream: Target table name
            records: Batch of records to write
            catalog: Iceberg catalog instance
            config: Destination configuration
            
        Returns:
            WriteResult with snapshot ID and metrics
        """
        pass
    
    def handle_schema_change(
        self,
        stream: str,
        old_schema: Schema,
        new_schema: Schema,
        catalog: IcebergCatalog
    ) -> None:
        """
        Apply schema evolution to Iceberg table.
        
        Args:
            stream: Target table name
            old_schema: Current Iceberg schema
            new_schema: New schema with added/modified columns
            catalog: Iceberg catalog instance
        """
        pass
    
    def create_table(
        self,
        stream: str,
        schema: Schema,
        partition_spec: PartitionSpec,
        catalog: IcebergCatalog,
        config: Dict
    ) -> Table:
        """
        Create new Iceberg table if it doesn't exist.
        
        Args:
            stream: Table name
            schema: Iceberg schema
            partition_spec: Partitioning configuration
            catalog: Iceberg catalog instance
            config: Destination configuration
            
        Returns:
            Iceberg Table object
        """
        pass
```

### 4.3 Catalog API Interactions (REST Catalog Protocol)

OLake interacts with Iceberg catalogs via the REST catalog specification:

#### List Namespaces
```http
GET /v1/namespaces HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "namespaces": [
    ["production"],
    ["staging"],
    ["dev"]
  ]
}
```

#### Create Namespace
```http
POST /v1/namespaces HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "namespace": ["production"],
  "properties": {
    "owner": "olake",
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

#### List Tables
```http
GET /v1/namespaces/production/tables HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "identifiers": [
    {
      "namespace": ["production"],
      "name": "users"
    },
    {
      "namespace": ["production"],
      "name": "orders"
    }
  ]
}
```

#### Load Table Metadata
```http
GET /v1/namespaces/production/tables/users HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "metadata-location": "s3://bucket/warehouse/production/users/metadata/v1.metadata.json",
  "metadata": {
    "format-version": 2,
    "table-uuid": "9c12d441-03fe-4693-9a96-a0705ddf69c1",
    "location": "s3://bucket/warehouse/production/users",
    "last-updated-ms": 1642251600000,
    "schema": { "..." },
    "partition-spec": [ "..." ],
    "current-snapshot-id": 8345678901234567890,
    "snapshots": [ "..." ]
  }
}
```

#### Create Table
```http
POST /v1/namespaces/production/tables HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "users",
  "schema": {
    "type": "struct",
    "schema-id": 0,
    "fields": [
      {
        "id": 1,
        "name": "id",
        "required": true,
        "type": "int"
      },
      {
        "id": 2,
        "name": "email",
        "required": true,
        "type": "string"
      }
    ]
  },
  "partition-spec": [
    {
      "name": "created_year",
      "transform": "year",
      "source-id": 3,
      "field-id": 1000
    }
  ],
  "properties": {
    "write.parquet.compression-codec": "zstd"
  }
}
```

#### Commit Transaction (Append)
```http
POST /v1/namespaces/production/tables/users HTTP/1.1
Content-Type: application/json
Authorization: Bearer <token>

{
  "identifier": {
    "namespace": ["production"],
    "name": "users"
  },
  "requirements": [
    {
      "type": "assert-current-schema-id",
      "current-schema-id": 0
    }
  ],
  "updates": [
    {
      "action": "append",
      "manifest-list": "s3://bucket/warehouse/production/users/metadata/snap-8345678901234567890.avro"
    }
  ]
}
```

### 4.4 Monitoring/Metrics API

OLake provides metrics for monitoring pipeline health:

```python
@dataclass
class PipelineMetrics:
    """Metrics emitted by OLake pipeline."""
    
    pipeline_id: str
    source_type: str
    destination_type: str
    
    # Read metrics
    records_read: int                  # Total records read from source
    bytes_read: int                    # Total bytes read
    read_duration_ms: int              # Time spent reading
    
    # Write metrics
    records_written: int               # Records written to destination
    bytes_written: int                 # Bytes written
    write_duration_ms: int             # Time spent writing
    data_files_created: int            # Number of Parquet files
    
    # CDC metrics
    cdc_lag_ms: int                    # Lag behind source (for CDC)
    checkpoint_position: str           # Current CDC position
    
    # Error metrics
    errors_count: int                  # Number of errors
    retries_count: int                 # Number of retries
    
    # Snapshot metrics
    snapshot_id: str                   # Latest Iceberg snapshot ID
    snapshot_timestamp: int            # Snapshot commit time
```

**Example Output:**
```json
{
  "pipeline_id": "pg-to-iceberg-prod",
  "source_type": "postgres",
  "destination_type": "iceberg",
  "records_read": 50000,
  "bytes_read": 104857600,
  "read_duration_ms": 12500,
  "records_written": 50000,
  "bytes_written": 83886080,
  "write_duration_ms": 8750,
  "data_files_created": 3,
  "cdc_lag_ms": 250,
  "checkpoint_position": "0/3000060",
  "errors_count": 0,
  "retries_count": 0,
  "snapshot_id": "8345678901234567890",
  "snapshot_timestamp": 1642251600000
}
```

---

## 5. Metadata Management

### 5.1 Table Discovery Mechanisms

#### PostgreSQL Discovery

```sql
-- Discover tables in all schemas
SELECT
  schemaname AS namespace,
  tablename AS name,
  tableowner AS owner
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY schemaname, tablename;

-- Get column metadata
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default,
  udt_name
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'users'
ORDER BY ordinal_position;

-- Get primary key
SELECT
  a.attname AS column_name
FROM pg_index i
JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
WHERE i.indrelid = 'public.users'::regclass AND i.indisprimary;
```

#### MySQL Discovery

```sql
-- Discover tables
SELECT
  TABLE_SCHEMA AS namespace,
  TABLE_NAME AS name,
  TABLE_TYPE AS type
FROM information_schema.TABLES
WHERE TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Get column metadata
SELECT
  COLUMN_NAME AS column_name,
  DATA_TYPE AS data_type,
  IS_NULLABLE AS is_nullable,
  COLUMN_DEFAULT AS column_default,
  COLUMN_TYPE AS column_type
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'mydb' AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

-- Get primary key
SELECT
  COLUMN_NAME AS column_name
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'mydb'
  AND TABLE_NAME = 'users'
  AND CONSTRAINT_NAME = 'PRIMARY'
ORDER BY ORDINAL_POSITION;
```

#### MongoDB Discovery

```javascript
// Discover collections
db.getCollectionNames().filter(name => !name.startsWith('system.'));

// Infer schema by sampling documents
db.users.aggregate([
  { $sample: { size: 1000 } },  // Sample 1000 documents
  { $project: {
      // Extract all field names and types
      fields: { $objectToArray: "$$ROOT" }
    }
  },
  { $unwind: "$fields" },
  { $group: {
      _id: "$fields.k",
      types: { $addToSet: { $type: "$fields.v" } },
      count: { $sum: 1 }
    }
  }
]);
```

### 5.2 Schema Inference and Evolution

#### Inference

OLake infers schemas by:
1. **Introspection:** Query source system metadata (information_schema, DESCRIBE, etc.)
2. **Sampling:** For schema-less sources (MongoDB), sample documents to infer types
3. **Type Promotion:** If column has mixed types, promote to most general type (e.g., `int` + `string` → `string`)

#### Evolution

**Supported Changes:**
- **Add Column:** New column with `NULL` default
- **Rename Column:** Via Iceberg metadata (old column deprecated)
- **Type Promotion:** Widen type (e.g., `int` → `long`)

**Unsupported Changes (Require Manual Intervention):**
- **Drop Column:** Must be handled outside OLake
- **Type Demotion:** Narrowing type (e.g., `long` → `int`)
- **Change Nullability:** Making `required` column `optional` (or vice versa)

**Example: Add Column**

**Source Change (PostgreSQL):**
```sql
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
```

**OLake Detects Change:**
```json
{
  "stream": "public.users",
  "schema_change": {
    "type": "add_column",
    "column_name": "phone",
    "column_type": "string",
    "nullable": true
  }
}
```

**Iceberg Schema Update:**
```python
table.update_schema().add_column(
    "phone",
    StringType(),
    doc="User phone number"
).commit()
```

**Result:**
- Existing Parquet files remain unchanged
- New files include `phone` column
- Queries return `NULL` for `phone` in old rows

### 5.3 Partition Metadata

Iceberg partitioning organizes data files for efficient querying.

**Partition Spec Example:**
```json
{
  "spec-id": 0,
  "fields": [
    {
      "source-id": 3,                  // Column ID for 'created_at'
      "field-id": 1000,
      "name": "created_year",
      "transform": "year"              // Transform function
    },
    {
      "source-id": 4,                  // Column ID for 'region'
      "field-id": 1001,
      "name": "region",
      "transform": "identity"          // No transform, use value as-is
    }
  ]
}
```

**Partition Values:**
```
s3://bucket/warehouse/production/users/
├── metadata/
│   ├── v1.metadata.json
│   └── snap-*.avro
└── data/
    ├── created_year=2024/
    │   ├── region=us-east/
    │   │   ├── data-00001.parquet
    │   │   └── data-00002.parquet
    │   └── region=us-west/
    │       └── data-00003.parquet
    └── created_year=2025/
        └── region=us-east/
            └── data-00004.parquet
```

**Partition Pruning:**
Query engines use partition metadata to skip irrelevant files:

```sql
-- Query only 2025 data in us-east
SELECT * FROM users
WHERE created_year = 2025 AND region = 'us-east';

-- Iceberg reads only: data/created_year=2025/region=us-east/*.parquet
-- Skips: 2024 data, us-west data
```

### 5.4 Lineage Tracking (Source → Lake Mapping)

OLake maintains lineage metadata linking source to destination:

```json
{
  "lineage": {
    "source": {
      "type": "postgres",
      "host": "postgres.example.com",
      "database": "production",
      "schema": "public",
      "table": "users"
    },
    "destination": {
      "type": "iceberg",
      "catalog": "rest",
      "namespace": "production",
      "table": "users",
      "location": "s3://bucket/warehouse/production/users"
    },
    "pipeline": {
      "id": "pg-to-iceberg-users",
      "created_at": "2025-01-01T00:00:00Z",
      "sync_mode": "incremental"
    },
    "mappings": [
      {
        "source_column": "id",
        "destination_column": "id",
        "type_mapping": "integer -> int"
      },
      {
        "source_column": "email",
        "destination_column": "email",
        "type_mapping": "varchar -> string"
      },
      {
        "source_column": "created_at",
        "destination_column": "created_at",
        "type_mapping": "timestamptz -> timestamptz"
      }
    ],
    "transformations": []               // OLake does not transform data
  }
}
```

**Accessing Lineage:**
- Stored in Iceberg table properties: `table.properties()['olake.source.database']`
- Queryable via Iceberg metadata tables
- Integrated with data catalogs (DataHub, Amundsen) via REST API

---

## 6. Semantic Layers

### 6.1 Business Logic Embedded in OLake

OLake is designed as a **pure replication tool** with minimal business logic:

**What OLake Does:**
- ✅ Type mapping (database types → Iceberg types)
- ✅ Schema inference and evolution
- ✅ CDC position tracking
- ✅ Exactly-once delivery semantics
- ✅ Partitioning based on configuration

**What OLake Does NOT Do:**
- ❌ Data transformations (filtering, aggregation, enrichment)
- ❌ Data quality checks (validation, deduplication)
- ❌ Business rule enforcement
- ❌ PII masking or encryption

**Rationale:**
OLake follows the **ELT (Extract-Load-Transform)** paradigm:
- Extract from source
- Load into lake
- Transform in query engines (DuckDB, Trino, Spark, etc.)

This keeps OLake simple, fast, and composable.

### 6.2 Data Quality Rules

Data quality should be enforced **downstream** of OLake:

#### Using Great Expectations
```python
import great_expectations as gx

# Define expectations on Iceberg table
context = gx.get_context()
suite = context.add_or_update_expectation_suite("users_suite")

suite.add_expectation(
    gx.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_not_be_null",
        kwargs={"column": "email"}
    )
)

suite.add_expectation(
    gx.core.ExpectationConfiguration(
        expectation_type="expect_column_values_to_match_regex",
        kwargs={
            "column": "email",
            "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        }
    )
)

# Validate Iceberg table
batch_request = {
    "datasource_name": "iceberg_datasource",
    "data_connector_name": "default_inferred_data_connector_name",
    "data_asset_name": "users"
}

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="users_suite"
)

results = validator.validate()
```

#### Using SQL Views (Downstream)
```sql
-- Create validated view in DuckDB/Trino
CREATE VIEW validated_users AS
SELECT *
FROM iceberg_scan('s3://bucket/warehouse/production/users')
WHERE
  email IS NOT NULL
  AND email LIKE '%@%'
  AND created_at >= '2020-01-01'
  AND id > 0;
```

### 6.3 Transformation Capabilities

OLake supports **limited transformations** via configuration:

#### Partition Transform
```json
{
  "destination": {
    "writer": {
      "partition_spec": {
        "partition_by": [
          "year(created_at)",            // Extract year from timestamp
          "bucket(10, user_id)"          // Hash user_id into 10 buckets
        ]
      }
    }
  }
}
```

**Supported Transforms:**
- `year(column)` - Extract year
- `month(column)` - Extract month
- `day(column)` - Extract day
- `hour(column)` - Extract hour
- `bucket(N, column)` - Hash into N buckets
- `truncate(width, column)` - Truncate string to width
- `identity(column)` - Use value as-is

#### Column Selection
```json
{
  "streams": [
    {
      "stream": {
        "name": "users",
        "json_schema": { "..." }
      },
      "selected_columns": ["id", "email", "created_at"],  // Only replicate these
      "excluded_columns": ["password_hash"]                // Explicitly exclude
    }
  ]
}
```

#### Advanced Transformations

For complex transformations, integrate with downstream tools:

**Using SQLMesh:**
```sql
-- models/cleaned_users.sql
MODEL (
  name production.cleaned_users,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at
  )
);

SELECT
  id,
  LOWER(TRIM(email)) AS email,              -- Normalize email
  created_at,
  CASE
    WHEN region IS NULL THEN 'unknown'
    ELSE region
  END AS region
FROM iceberg_scan('s3://bucket/warehouse/production/users')
WHERE
  created_at BETWEEN @start_date AND @end_date
  AND email IS NOT NULL;
```

**Using Ibis (Python):**
```python
import ibis

con = ibis.duckdb.connect()
con.execute("INSTALL iceberg; LOAD iceberg;")

# Read Iceberg table
users = con.read_iceberg('s3://bucket/warehouse/production/users')

# Transform
cleaned_users = (
    users
    .mutate(
        email=users.email.lower().strip(),
        region=users.region.fillna('unknown')
    )
    .filter(users.email.notnull())
)

# Write to new Iceberg table
con.create_table('production.cleaned_users', cleaned_users)
```

---

## 7. Entity-Relationship Diagram (Text Format)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         OLake Complete Ontology                         │
└─────────────────────────────────────────────────────────────────────────┘

┌───────────────────┐
│  SourceDatabase   │
├───────────────────┤
│ - host            │
│ - port            │
│ - database        │
│ - username        │
│ - password        │
│ - ssl_config      │
│ - cdc_config      │
└─────────┬─────────┘
          │ contains
          │ 1:N
          ▼
┌───────────────────┐         ┌───────────────────┐
│     Stream        │────────>│  Column           │
├───────────────────┤ has     ├───────────────────┤
│ - name            │ 1:N     │ - name            │
│ - namespace       │         │ - data_type       │
│ - sync_mode       │         │ - is_nullable     │
│ - cursor_field    │         │ - is_primary_key  │
│ - primary_key     │         │ - ordinal_pos     │
└─────────┬─────────┘         └───────────────────┘
          │ replicated by
          │ N:1
          ▼
┌───────────────────┐
│    Pipeline       │
├───────────────────┤
│ - id              │
│ - source_config   │
│ - dest_config     │
│ - stream_catalog  │
│ - created_at      │
│ - updated_at      │
└─────────┬─────────┘
          │ maintains
          │ 1:1
          ▼
┌───────────────────┐
│      State        │
├───────────────────┤
│ - checkpoint      │
│   - lsn (PG)      │
│   - gtid (MySQL)  │
│   - token (Mongo) │
│ - stream_states   │
│ - last_sync_time  │
└───────────────────┘
          │ creates
          │ 1:N
          ▼
┌───────────────────┐         ┌───────────────────┐
│   IcebergTable    │────────>│   Snapshot        │
├───────────────────┤ has     ├───────────────────┤
│ - namespace       │ 1:N     │ - id              │
│ - name            │         │ - parent_id       │
│ - location        │         │ - timestamp       │
│ - uuid            │         │ - manifest_list   │
│ - schema_id       │         │ - summary         │
│ - partition_spec  │         └─────────┬─────────┘
└─────────┬─────────┘                   │ references
          │ composed of                 │ N:M
          │ 1:N                         ▼
          ▼                   ┌───────────────────┐
┌───────────────────┐         │   DataFile        │
│   IcebergSchema   │         ├───────────────────┤
├───────────────────┤         │ - path            │
│ - schema_id       │         │ - format          │
│ - fields          │         │ - partition       │
│   - id            │         │ - record_count    │
│   - name          │         │ - file_size       │
│   - type          │         │ - column_sizes    │
│   - required      │         │ - value_counts    │
└───────────────────┘         │ - null_counts     │
          │                   │ - lower_bounds    │
          │ defines           │ - upper_bounds    │
          │ 1:1               └───────────────────┘
          ▼
┌───────────────────┐
│ PartitionSpec     │
├───────────────────┤
│ - spec_id         │
│ - fields          │
│   - source_id     │
│   - field_id      │
│   - name          │
│   - transform     │
└───────────────────┘
          │ applied to
          │ 1:N
          ▼
┌───────────────────┐
│  Partition        │
├───────────────────┤
│ - spec_id         │
│ - field_values    │
│   - year=2025     │
│   - region=us     │
└─────────┬─────────┘
          │ contains
          │ 1:N
          ▼
┌───────────────────┐
│   DataFile        │
│   (referenced)    │
└───────────────────┘

┌───────────────────┐
│  IcebergCatalog   │
├───────────────────┤
│ - type            │
│   - REST          │
│   - JDBC          │
│   - Glue          │
│   - Hive          │
│ - endpoint        │
│ - credentials     │
└─────────┬─────────┘
          │ manages
          │ 1:N
          ▼
┌───────────────────┐
│   Namespace       │
├───────────────────┤
│ - name            │
│ - properties      │
└─────────┬─────────┘
          │ contains
          │ 1:N
          ▼
┌───────────────────┐
│   IcebergTable    │
│   (referenced)    │
└───────────────────┘
```

---

## 8. Summary and Key Takeaways

### 8.1 Core Concepts

**OLake is:**
- A **CDC replication tool** for moving data from operational databases to data lakes
- **Schema-agnostic**: Automatically infers and evolves schemas
- **ACID-compliant**: Leverages Iceberg for transactional guarantees
- **Catalog-flexible**: Supports REST, JDBC, Glue, Hive catalogs
- **Exactly-once**: Ensures data consistency with checkpointing

**OLake is NOT:**
- A transformation engine (use SQLMesh, dbt, Ibis)
- A data quality tool (use Great Expectations, dbt tests)
- A query engine (use DuckDB, Trino, Spark)

### 8.2 Configuration Pattern

```
source.json → discover → streams.json → sync → destination
                                              → state.json
```

### 8.3 Type Mapping Principles

1. **Preserve Semantics:** NULL, precision, timezone info maintained
2. **Promote Types:** Widen types when necessary (int → long)
3. **Serialize Complex:** JSON, arrays, structs preserved as Iceberg types
4. **Normalize Time:** All timestamps converted to UTC

### 8.4 API Contracts

- **Source Interface:** `discover()`, `read()`, `check()`
- **Destination Interface:** `write_batch()`, `handle_schema_change()`, `create_table()`
- **Catalog API:** Iceberg REST catalog specification (OpenAPI)

### 8.5 Metadata Management

- **Discovery:** Introspect source databases
- **Inference:** Sample data to determine types
- **Evolution:** Add columns, promote types automatically
- **Lineage:** Track source-to-destination mappings

### 8.6 Best Practices

1. **Enable CDC:** Use logical replication for low-latency sync
2. **Partition Wisely:** Partition by time or high-cardinality columns
3. **Monitor Lag:** Track CDC lag to ensure freshness
4. **Validate Downstream:** Enforce data quality in query layer
5. **Version Control:** Use LakeFS to version Iceberg tables
6. **Separate Concerns:** Transform data downstream (ELT pattern)

### 8.7 Integration Points

**Upstream:**
- PostgreSQL, MySQL, MongoDB, Oracle
- Kafka (future)

**Downstream:**
- Iceberg (primary format)
- Query engines: DuckDB, Trino, Spark, Flink, RisingWave
- Data catalogs: DataHub, Amundsen, OpenMetadata
- BI tools: Superset, Metabase, Tableau

**Orchestration:**
- Dagster (asset-based)
- Apache Airflow
- Prefect

---

## 9. References and Resources

### Official Documentation
- **OLake Docs:** https://olake.io/docs
- **Apache Iceberg:** https://iceberg.apache.org
- **REST Catalog Spec:** https://iceberg.apache.org/rest-catalog-spec/
- **REST Catalog OpenAPI:** https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml

### Type Mapping References
- **PostgreSQL Types:** https://www.postgresql.org/docs/current/datatype.html
- **MySQL Types:** https://dev.mysql.com/doc/refman/8.0/en/data-types.html
- **MongoDB BSON Types:** https://www.mongodb.com/docs/manual/reference/bson-types/
- **Iceberg Types:** https://iceberg.apache.org/spec/#schemas

### Repository
- **OLake GitHub:** https://github.com/datazip-inc/olake

### Related Projects
- **Lakekeeper:** https://docs.lakekeeper.io
- **LakeFS:** https://lakefs.io
- **DuckLake:** https://ducklake.select

---

## Appendix A: Example Configurations

### A.1 PostgreSQL to Iceberg (Full Setup)

**source.json:**
```json
{
  "host": "postgres.example.com",
  "port": 5432,
  "database": "production",
  "username": "olake_user",
  "password": "<PASSWORD>",
  "ssl": {
    "mode": "require"
  },
  "update_method": {
    "replication_slot": "olake_slot",
    "publication": "olake_publication",
    "initial_wait_time": 120
  },
  "max_threads": 5
}
```

**destination.json:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://lakekeeper.example.com/catalog",
    "iceberg_s3_path": "s3://my-bucket/warehouse",
    "s3_endpoint": "https://s3.amazonaws.com",
    "aws_region": "us-east-1",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "production",
    "token": "<CATALOG_TOKEN>",
    "partition_spec": {
      "partition_by": ["year(created_at)"]
    }
  }
}
```

**streams.json (generated):**
```json
{
  "selected_streams": ["public.users", "public.orders"],
  "streams": [
    {
      "stream": {
        "name": "users",
        "namespace": "public",
        "json_schema": {
          "type": "object",
          "properties": {
            "id": {"type": "integer"},
            "email": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"}
          }
        },
        "supported_sync_modes": ["full_refresh", "incremental"]
      },
      "sync_mode": "incremental",
      "cursor_field": ["updated_at"],
      "primary_key": [["id"]]
    }
  ]
}
```

### A.2 MySQL to Iceberg (Cloudflare R2)

**source.json:**
```json
{
  "host": "mysql.example.com",
  "port": 3306,
  "database": "ecommerce",
  "username": "olake_user",
  "password": "<PASSWORD>",
  "ssl": {
    "mode": "required"
  },
  "update_method": {
    "method": "binlog",
    "server_id": 12345
  },
  "max_threads": 8
}
```

**destination.json:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://account-id.r2.cloudflarestorage.com/catalog",
    "iceberg_s3_path": "s3://my-r2-bucket/warehouse",
    "s3_endpoint": "https://account-id.r2.cloudflarestorage.com",
    "aws_region": "auto",
    "aws_access_key": "<R2_ACCESS_KEY>",
    "aws_secret_key": "<R2_SECRET_KEY>",
    "iceberg_db": "ecommerce",
    "token": "<R2_API_TOKEN>"
  }
}
```

### A.3 MongoDB to Iceberg

**source.json:**
```json
{
  "connection_string": "mongodb://user:pass@mongo.example.com:27017/mydb?replicaSet=rs0",
  "database": "mydb",
  "update_method": {
    "method": "change_stream",
    "resume_token": null
  },
  "max_threads": 4
}
```

**destination.json:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "jdbc",
    "jdbc_url": "jdbc:postgresql://catalog-db.example.com:5432/iceberg_catalog",
    "jdbc_username": "iceberg_user",
    "jdbc_password": "<PASSWORD>",
    "iceberg_s3_path": "s3://my-bucket/warehouse",
    "aws_region": "us-west-2",
    "aws_access_key": "<ACCESS_KEY>",
    "aws_secret_key": "<SECRET_KEY>",
    "iceberg_db": "mongodb_data"
  }
}
```

---

## Appendix B: Command Reference

### Discover Command
```bash
docker run --rm \
  -v /path/to/config:/mnt/config \
  olakego/source-postgres:latest \
  discover \
  --config /mnt/config/source.json \
  > /path/to/config/streams.json
```

### Sync Command (Full Load + CDC)
```bash
docker run --rm \
  -v /path/to/config:/mnt/config \
  olakego/source-postgres:latest \
  sync \
  --config /mnt/config/source.json \
  --catalog /mnt/config/streams.json \
  --destination /mnt/config/destination.json \
  --state /mnt/config/state.json
```

### Check Connection
```bash
docker run --rm \
  -v /path/to/config:/mnt/config \
  olakego/source-postgres:latest \
  check \
  --config /mnt/config/source.json
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-18  
**Author:** AI Research Assistant  
**Status:** Complete


## Graph & Geo — Memgraph


> Source: `docs/data_engineering/memgraph/memgraph.md`

# Memgraph Development Skill

You are an expert Memgraph developer with deep knowledge of graph database design, Cypher query language, and real-time analytics. Use this skill when working with Memgraph graph databases, designing graph data models, writing Cypher queries, or implementing graph-based solutions.

## When to Use This Skill

Activate this skill when:
- Working with Memgraph databases
- Writing or optimizing Cypher queries
- Designing graph data models
- Implementing graph algorithms
- Setting up streaming data pipelines
- Troubleshooting graph database performance
- Building knowledge graphs or GraphRAG applications
- Implementing fraud detection, recommendation engines, or social network analysis

## Core Memgraph Knowledge

### What is Memgraph?

Memgraph is a high-performance, in-memory graph database optimized for:
- **Real-time analytics** with sub-millisecond query latency
- **Streaming data processing** with native Kafka/Pulsar/RabbitMQ connectors
- **HTAP workloads** (Hybrid Transactional/Analytical Processing)
- **GraphRAG and AI integration** with native vector search
- **Mission-critical applications** requiring ACID compliance

**Key Performance Metrics:**
- 3-8x faster than Neo4j
- Sub-millisecond latency (1.07ms minimum)
- 132x higher throughput in write-heavy workloads

### Data Model - Labeled Property Graph (LPG)

**Four Core Elements:**
1. **Nodes**: Entities (people, products, events)
2. **Relationships**: Directed edges connecting nodes
3. **Properties**: Key-value pairs on nodes or relationships
4. **Labels**: Node categorizations

**Naming Conventions:**
- Node labels: `CamelCase` (e.g., `User`, `ProductCategory`)
- Relationship types: `UPPER_CASE_WITH_UNDERSCORES` (e.g., `KNOWS`, `BELONGS_TO`)
- Properties/variables: `camelCase` (e.g., `userName`, `createdAt`)

## Data Modeling Best Practices

### Design Principles

When designing a graph model, follow these principles:

1. **Avoid Over-Modeling**
   - Keep it simple - model only what adds value
   - Ask: "Does this node or relationship add real value?"
   - Don't model every detail

2. **Optimize Memory Usage**
   - Memgraph is in-memory - choose efficient data types
   - Use integers instead of strings where applicable
   - Avoid storing large text in frequently accessed properties

3. **Avoid Data Duplication**
   - Use relationships instead of duplicating data
   - Example: Don't add worker info to every order; create a Worker node and link it

4. **Avoid Supernodes**
   - A supernode has 50k+ connections and severely impacts performance
   - Use `ANALYZE GRAPH;` to optimize queries involving supernodes
   - Consider splitting high-degree nodes when possible

5. **Strategic Indexing**
   - Only index frequently queried properties
   - Focus on high-cardinality properties (many unique values)
   - Avoid indexing low-cardinality properties (gender, boolean values)

6. **Think in Graph Terms**
   - Pattern matching ≠ SQL JOINs
   - Focus on relationships and traversals
   - Design for how you'll query the data

### Property vs Relationship Decision

**Store as Property when:**
- The data is rarely queried independently
- The data is unique to that specific entity
- It's descriptive metadata (name, age, timestamp)

**Store as Relationship when:**
- The data is shared across multiple nodes
- You frequently query or traverse based on this data
- It represents a connection or association
- You need to add properties to the connection itself

## Cypher Query Language Patterns

### Basic CRUD Operations

**Create**
```cypher
// Create nodes
CREATE (u:User {name: 'Alice', email: 'alice@example.com', age: 30});

// Create relationships
MATCH (u:User {name: 'Alice'}), (v:User {name: 'Bob'})
CREATE (u)-[:FOLLOWS {since: date()}]->(v);

// Create pattern in one statement
CREATE (u:User {name: 'Alice'})-[:POSTED]->(p:Post {title: 'Hello World', content: 'My first post'});

// Upsert with MERGE
MERGE (u:User {email: 'alice@example.com'})
ON CREATE SET u.created = timestamp(), u.name = 'Alice'
ON MATCH SET u.lastSeen = timestamp()
RETURN u;
```

**Read (MATCH)**
```cypher
// Simple match
MATCH (u:User {name: 'Alice'}) RETURN u;

// Match with relationships
MATCH (u:User {name: 'Alice'})-[:FOLLOWS]->(followed:User)
RETURN followed.name;

// Complex pattern matching
MATCH (user:User)-[r:RATED]->(movie:Movie)<-[:OF_GENRE]-(genre:Genre {name: 'Comedy'})
WHERE r.rating > 3
RETURN movie.title, r.rating
ORDER BY r.rating DESC
LIMIT 10;
```

**Update**
```cypher
// Update properties
MATCH (u:User {name: 'Alice'})
SET u.age = 31, u.updated = timestamp();

// Add/update multiple properties
MATCH (u:User {name: 'Alice'})
SET u += {location: 'New York', verified: true};

// Remove nested properties (v3.6+)
MATCH (u:User {name: 'Alice'})
SET u.nested.property = null;
```

**Delete**
```cypher
// Delete node and its relationships
MATCH (u:User {name: 'Alice'})
DETACH DELETE u;

// Delete only relationships
MATCH (u:User {name: 'Alice'})-[r:FOLLOWS]->()
DELETE r;

// Remove properties
MATCH (u:User {name: 'Alice'})
REMOVE u.age;

// Remove labels
MATCH (n:Person)
REMOVE n:OldLabel;
```

### Path Traversal Algorithms

**Depth-First Search (DFS)** - All paths
```cypher
// Find all paths
MATCH path=(start {id: 0})-[*]->(end {id: 8})
RETURN path;

// Limited path length (2 to 4 hops)
MATCH path=(start {id: 0})-[r*2..4]->(end {id: 8})
RETURN path;

// With inline filtering
MATCH path=(start {id: 0})-[r:ROAD *..5 (r, n | r.active = true AND n.cost < 100)]->(end {id: 8})
RETURN path;
```

**Breadth-First Search (BFS)** - Shortest path
```cypher
// Shortest path (returns one path)
MATCH path=(start {id: 0})-[*BFS]->(end {id: 8})
RETURN path;

// BFS with filtering and length limit
MATCH path=(:City {name: 'London'})-[r:ROAD *BFS ..3 (r, n | r.continent = 'Europe')]->(:City)
RETURN path;
```

**Weighted Shortest Path (WSHORTEST)**
```cypher
// Basic weighted shortest path
MATCH p = (:City {name: "Paris"})
  -[:Road *WSHORTEST (e, v | e.distance) total_weight]->
  (:City {name: "Berlin"})
RETURN nodes(p) AS cities, total_weight;

// With additional filtering
MATCH p = (:City {name: "Paris"})
  -[:Road *WSHORTEST (e, v | e.distance) total_weight (e, v | e.distance <= 200)]->
  (:City {name: "Berlin"})
RETURN nodes(p) AS cities, total_weight;
```

**All Shortest Paths (ALLSHORTEST)**
```cypher
// Find all shortest paths
MATCH path = (a)-[*ALLSHORTEST]->(b)
RETURN path;
```

### Aggregation and Data Processing

```cypher
// Counting
MATCH (n:User) RETURN count(n);
MATCH (n:User) RETURN count(DISTINCT n.location);

// Statistical functions
MATCH (n:User) RETURN sum(n.age), avg(n.age), min(n.age), max(n.age);

// Collect into list
MATCH (n:User) RETURN collect(n.name) AS names;

// Collect into map
MATCH (n:User) RETURN collect(n.name, n.age) AS name_to_age_map;

// Group by with aggregation
MATCH (u:User)-[:POSTED]->(p:Post)
RETURN u.name, count(p) AS post_count
ORDER BY post_count DESC;
```

## Indexing and Performance Optimization

### Creating Indexes

```cypher
// Label index - indexes all nodes with label
CREATE INDEX ON :User;

// Label-property index - most common
CREATE INDEX ON :User(email);

// Composite index - multiple properties
CREATE INDEX ON :User(name, age);

// Edge-type index
CREATE INDEX ON :FOLLOWS;

// View existing indexes
SHOW INDEX INFO;

// Drop index
DROP INDEX ON :User(email);
```

### ANALYZE GRAPH Command

**Critical for Performance:**
```cypher
ANALYZE GRAPH;
```

Run after:
- Creating indexes
- Bulk data insertion
- Before queries with multiple property indexes
- Before queries involving supernodes

This helps Memgraph:
- Calculate node degree statistics
- Optimize MERGE operations on supernodes
- Improve multi-index intersection queries

### Query Performance Analysis

```cypher
// View query plan without execution
EXPLAIN MATCH (n:User)-[:FOLLOWS]->(m:User)
WHERE n.age > 25
RETURN m.name;

// Execute and profile performance
PROFILE MATCH (n:User)-[:FOLLOWS]->(m:User)
WHERE n.age > 25
RETURN m.name;
```

**PROFILE provides:**
- **OPERATOR**: Operator designation
- **ACTUAL HITS**: Number of times operator executed
- **RELATIVE TIME**: Time spent relative to total
- **ABSOLUTE TIME**: Actual wall time

**Optimization Tips:**
- Lower number of operators = faster execution
- Use inline filtering for path traversals instead of WHERE clauses
- Start traversals from specific nodes using indexed properties
- Limit results early in the query pipeline

## Graph Algorithms - MAGE Library

### Centrality Measures

```cypher
// PageRank - find important nodes
CALL pagerank.get(100, 0.85)
YIELD node, rank
SET node.pagerank = rank;

// Get top-ranked nodes
CALL pagerank.get()
YIELD node, rank
RETURN node.name, rank
ORDER BY rank DESC
LIMIT 10;

// Betweenness Centrality - find bridge nodes
CALL betweenness_centrality.get()
YIELD node, betweenness
RETURN node.name, betweenness
ORDER BY betweenness DESC;

// Katz Centrality
CALL katz_centrality.get()
YIELD node, rank;
```

### Community Detection

```cypher
// Louvain method - static community detection
CALL community_detection.get()
YIELD node, community_id
RETURN community_id, collect(node.name) AS members;

// Count communities and sizes
CALL community_detection.get()
YIELD node, community_id
RETURN community_id, count(*) AS size
ORDER BY size DESC;

// Dynamic community detection (for streaming)
CALL community_detection_online.get()
YIELD node, community_id;
```

### Machine Learning Algorithms

```cypher
// Node2Vec - graph embeddings
CALL node2vec.get()
YIELD node, embedding;

// Link prediction
CALL link_prediction.predict()
YIELD node1, node2, probability
WHERE probability > 0.7
RETURN node1, node2, probability;

// Node classification
CALL node_classification.predict()
YIELD node, predicted_class;
```

## Constraints and Data Validation

### Creating Constraints

```cypher
// Existence constraint - property must exist
CREATE CONSTRAINT ON (n:User) ASSERT EXISTS (n.email);

// Uniqueness constraint - property must be unique
CREATE CONSTRAINT ON (n:User) ASSERT n.email IS UNIQUE;

// View all constraints
SHOW CONSTRAINT INFO;

// Drop specific constraint
DROP CONSTRAINT ON (n:User) ASSERT EXISTS (n.email);

// Drop all constraints (v3.6+)
DROP ALL CONSTRAINTS;
```

## Streaming Data Processing

### Setting Up Streams

```cypher
// Kafka stream
CREATE KAFKA STREAM user_events
TOPICS user_activity, user_signup
TRANSFORM event_processor.process_event
BOOTSTRAP_SERVERS 'localhost:9092'
BATCH_INTERVAL 100;

// Pulsar stream
CREATE PULSAR STREAM transactions
TOPICS financial_transactions
TRANSFORM fraud_detector.check_transaction
SERVICE_URL 'pulsar://localhost:6650';

// View streams
SHOW STREAMS;

// Start/stop streams
START STREAM user_events;
STOP STREAM user_events;

// Drop stream
DROP STREAM user_events;
```

### Transformation Modules

Create Python transformation module:

```python
import mgp

@mgp.transformation
def process_event(messages: mgp.Messages) -> mgp.Record(query=str, parameters=mgp.Nullable[mgp.Map]):
    result_queries = []

    for message in messages:
        payload = message.payload().decode('utf-8')
        # Parse payload and create Cypher query
        query = "CREATE (e:Event {data: $data, timestamp: $ts})"
        params = {"data": payload, "ts": message.timestamp()}
        result_queries.append(mgp.Record(query=query, parameters=params))

    return result_queries
```

## Storage Modes and Transaction Management

### Storage Modes

```cypher
// Transactional mode (default) - OLTP workloads
SET DATABASE SETTING 'storage.storage_mode' TO 'IN_MEMORY_TRANSACTIONAL';

// Analytical mode - OLAP workloads (6x faster import, 6x less memory)
SET DATABASE SETTING 'storage.storage_mode' TO 'IN_MEMORY_ANALYTICAL';
```

### Transaction Control

```cypher
// Start transaction
BEGIN;

// Execute queries
CREATE (n:User {name: 'Alice'});
MATCH (n:User {name: 'Alice'}) SET n.age = 30;

// Commit or rollback
COMMIT;
// or
ROLLBACK;
```

### Triggers

```cypher
// Create trigger for new nodes
CREATE TRIGGER new_user_trigger
ON () CREATE
AFTER COMMIT
EXECUTE
  MATCH (n:User)
  WHERE n.created_at IS NULL
  SET n.created_at = timestamp();

// Trigger for updates
CREATE TRIGGER audit_trigger
ON () UPDATE
AFTER COMMIT
EXECUTE
  MATCH (n)
  SET n.last_modified = timestamp();

// View triggers
SHOW TRIGGERS;

// Drop trigger
DROP TRIGGER new_user_trigger;
```

## Common Use Case Patterns

### Social Network Analysis

```cypher
// Find mutual friends
MATCH (me:User {name: 'Alice'})-[:FRIENDS_WITH]-(mutual)-[:FRIENDS_WITH]-(friend:User {name: 'Bob'})
RETURN mutual.name;

// Friend recommendations (friends of friends)
MATCH (me:User {name: 'Alice'})-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(recommendation)
WHERE NOT (me)-[:FRIENDS_WITH]-(recommendation) AND me <> recommendation
RETURN DISTINCT recommendation.name, count(*) AS mutual_friends
ORDER BY mutual_friends DESC
LIMIT 10;

// Find influencers in community
CALL pagerank.get()
YIELD node, rank
WHERE node:User
RETURN node.name, rank
ORDER BY rank DESC
LIMIT 20;
```

### Fraud Detection

```cypher
// Find suspicious transaction patterns (velocity check)
MATCH (account:Account)-[t:TRANSACTION]->(other:Account)
WHERE t.timestamp > timestamp() - 3600000 // Last hour
WITH account, count(t) AS tx_count, sum(t.amount) AS total_amount
WHERE tx_count > 50 OR total_amount > 100000
RETURN account.id, tx_count, total_amount;

// Detect circular money flows (possible money laundering)
MATCH path = (a:Account)-[:TRANSACTION *3..5]->(a)
WHERE all(tx IN relationships(path) WHERE tx.amount > 10000)
RETURN path;

// Find accounts sharing identifiers (mule accounts)
MATCH (a1:Account)-[:HAS_PHONE|HAS_ADDRESS|HAS_EMAIL]->(shared)<-[:HAS_PHONE|HAS_ADDRESS|HAS_EMAIL]-(a2:Account)
WHERE a1 <> a2
RETURN a1.id, a2.id, collect(DISTINCT type(shared)) AS shared_identifiers;
```

### Recommendation Engine

```cypher
// Collaborative filtering - users who liked this also liked
MATCH (user:User {id: $userId})-[:RATED {rating: 5}]->(item:Item)
      <-[:RATED {rating: 5}]-(similar:User)-[:RATED {rating: 5}]->(recommendation:Item)
WHERE NOT (user)-[:RATED]->(recommendation)
RETURN recommendation.title, count(*) AS score
ORDER BY score DESC
LIMIT 10;

// Content-based recommendations
MATCH (user:User {id: $userId})-[:RATED]->(item:Item)-[:HAS_TAG]->(tag:Tag)
      <-[:HAS_TAG]-(recommendation:Item)
WHERE NOT (user)-[:RATED]->(recommendation)
RETURN recommendation.title, count(DISTINCT tag) AS common_tags
ORDER BY common_tags DESC
LIMIT 10;
```

### Knowledge Graph Queries

```cypher
// Multi-hop reasoning
MATCH path = (entity:Entity {name: 'Drug A'})-[:RELATED_TO*1..3]-(related:Entity)
WHERE related.type = 'Disease'
RETURN path;

// Find entities mentioned together in documents
MATCH (e1:Entity)<-[:MENTIONS]-(doc:Document)-[:MENTIONS]->(e2:Entity)
WHERE e1.name = 'Albert Einstein' AND e1 <> e2
RETURN e2.name, count(doc) AS co_occurrences
ORDER BY co_occurrences DESC;

// Semantic search with relationships
MATCH (concept:Concept {name: $searchTerm})-[:IS_A|PART_OF|RELATED_TO*..2]-(related:Concept)
RETURN DISTINCT related.name, related.description;
```

## Integration with Python (GQLAlchemy)

### Object Graph Mapper

```python
from gqlalchemy import Memgraph, Node, Relationship, Field

# Connect to Memgraph
db = Memgraph(host='127.0.0.1', port=7687)

# Define node class
class User(Node):
    email: str = Field(unique=True, exists=True, db=db)
    name: str = Field(exists=True, db=db)
    age: int = Field()

# Define relationship class
class Follows(Relationship, type="FOLLOWS"):
    since: str = Field()

# Create instances
alice = User(email="alice@example.com", name="Alice", age=30).save(db)
bob = User(email="bob@example.com", name="Bob", age=25).save(db)

# Create relationship
follows = Follows(
    _start_node_id=alice._id,
    _end_node_id=bob._id,
    since="2024-01-15"
).save(db)

# Query with Cypher
results = db.execute_and_fetch("MATCH (u:User) WHERE u.age > 25 RETURN u")
for result in results:
    print(result['u'].name)
```

### Custom Query Modules

```python
import mgp

@mgp.read_proc
def recommend_friends(ctx: mgp.ProcCtx, user_id: int, limit: int = 10) -> mgp.Record(friend=mgp.Vertex, score=int):
    # Execute Cypher query
    query = """
    MATCH (me:User {id: $user_id})-[:FRIENDS_WITH]-()-[:FRIENDS_WITH]-(recommendation)
    WHERE NOT (me)-[:FRIENDS_WITH]-(recommendation) AND me <> recommendation
    RETURN recommendation, count(*) AS score
    ORDER BY score DESC
    LIMIT $limit
    """

    results = []
    for record in ctx.graph.execute(query, {"user_id": user_id, "limit": limit}):
        results.append(mgp.Record(friend=record['recommendation'], score=record['score']))

    return results
```

## Troubleshooting and Common Issues

### Performance Issues

**Slow Queries:**
1. Run `PROFILE` to identify bottlenecks
2. Check if indexes exist on filtered properties
3. Run `ANALYZE GRAPH;` after bulk operations
4. Use inline filtering instead of WHERE when possible
5. Consider if you're hitting supernodes

**High Memory Usage:**
1. Check storage mode (analytical uses less memory)
2. Review indexing strategy (over-indexing wastes memory)
3. Look for data duplication
4. Consider batch processing for large operations

**Supernode Problems:**
1. Run `ANALYZE GRAPH;` to help optimizer
2. Consider denormalizing high-degree relationships
3. Use time-based partitioning for temporal data
4. Add filtering early in query

### Data Modeling Issues

**Query Performance Poor:**
- Review if your model matches query patterns
- Consider if relationships should be properties or vice versa
- Check for over-modeling

**Data Duplication:**
- Use relationships instead of copying data
- Create shared entities and link them

**Complex Queries:**
- Simplify data model to match access patterns
- Consider denormalization for read-heavy queries

## Development Workflow Best Practices

### Design Phase
1. **Identify entities** - What are the main nouns?
2. **Define relationships** - How do entities connect?
3. **Plan queries** - What questions will you ask?
4. **Model accordingly** - Design for your query patterns
5. **Validate with stakeholders** - Ensure model meets requirements

### Implementation Phase
1. **Start simple** - Begin with core entities and relationships
2. **Create constraints** - Ensure data integrity from the start
3. **Add indexes strategically** - Only on frequently queried properties
4. **Import data** - Use analytical mode for bulk imports
5. **Test queries** - Validate performance with realistic data
6. **Iterate** - Refine model based on usage

### Optimization Phase
1. **Profile queries** - Use EXPLAIN/PROFILE to find bottlenecks
2. **Run ANALYZE GRAPH** - Help optimizer make better decisions
3. **Review indexes** - Add missing, remove unused
4. **Check storage mode** - Match mode to workload
5. **Monitor memory** - Ensure efficient resource usage

### Production Phase
1. **Set up monitoring** - Track performance metrics
2. **Configure backups** - Regular dumps and snapshots
3. **Plan for scaling** - Consider read replicas, sharding
4. **Implement security** - RBAC, encryption, audit logs
5. **Document schema** - Use `CALL schema()` for documentation

## Quick Reference Commands

### Database Management
```cypher
// Show database info
SHOW STORAGE INFO;
SHOW INDEX INFO;
SHOW CONSTRAINT INFO;
SHOW STREAMS;
SHOW TRIGGERS;

// Schema introspection
CALL schema() YIELD schema_in_prompt RETURN schema_in_prompt;

// Performance
ANALYZE GRAPH;

// Clear database
MATCH (n) DETACH DELETE n;  // Use with caution!
```

### Import/Export
```cypher
// Import CSV
LOAD CSV FROM '/path/to/file.csv' WITH HEADER AS row
CREATE (n:User {name: row.name, age: toInteger(row.age)});

// Export (use dump utility)
// mg_dump --host 127.0.0.1 --port 7687 > backup.cypher
```

## Additional Resources

- **Documentation**: https://memgraph.com/docs
- **Cypher Manual**: https://memgraph.com/docs/cypher-manual
- **MAGE Library**: https://memgraph.com/docs/mage
- **GitHub**: https://github.com/memgraph/memgraph
- **Community Discord**: Join for support and discussions

## Key Reminders

1. **Always think in graphs** - Relationships are first-class citizens
2. **Index strategically** - High-cardinality, frequently queried properties only
3. **Run ANALYZE GRAPH** - After bulk operations and before complex queries
4. **Use inline filtering** - For path traversals when possible
5. **Match storage mode to workload** - Transactional vs Analytical
6. **Avoid supernodes** - High-degree nodes impact performance
7. **Profile before optimizing** - Measure to find real bottlenecks
8. **Keep it simple** - Don't over-model, focus on value

## Success Criteria

When working with Memgraph, you've succeeded when:
- ✅ Queries return results in sub-millisecond to millisecond range
- ✅ Data model is intuitive and matches query patterns
- ✅ Indexes are on high-cardinality, frequently queried properties
- ✅ No unnecessary data duplication
- ✅ Constraints ensure data integrity
- ✅ PROFILE shows efficient query plans
- ✅ Memory usage is reasonable for dataset size
- ✅ Schema is documented and understood by team


> Source: `docs/data_engineering/memgraph/memgraph-research.md`

# Comprehensive Memgraph Research Documentation

## Executive Summary

Memgraph is a high-performance, in-memory graph database platform designed for real-time analytics and streaming data processing. Written in C/C++, it delivers low-latency query execution with ACID guarantees, making it ideal for mission-critical applications handling over 1,000 transactions per second. The platform combines transactional and analytical processing (HTAP) capabilities with native streaming integration, advanced graph algorithms, and as of February 2025 (version 3.0), built-in vector search for GraphRAG applications.

---

## 1. What is Memgraph?

Memgraph is an open-source (BSL license) in-memory graph database platform tuned for dynamic analytics environments. It is:

- **Built in C/C++** for optimal performance and minimal resource footprint (~30MB RAM on startup)
- **In-memory first** with persistence and durability guarantees
- **OpenCypher compliant** for querying graph data
- **Scale-up optimized** rather than distributed to minimize latency
- **HTAP capable** supporting both transactional and analytical workloads
- **Streaming-native** with built-in Kafka, Pulsar, and RabbitMQ integration

The platform is designed for environments requiring real-time insights from connected data, with sweet spots in applications handling 100GB to 4TB graph sizes and throughput exceeding 1,000 transactions per second on both reads and writes.

---

## 2. Key Features and Differentiators

### Core Differentiators from Other Graph Databases

**Performance Architecture:**
- **Pure in-memory storage engine** vs. Neo4j's disk-based approach
- Claims **3-8x faster** query execution than Neo4j in mixed workloads
- **Up to 41x lower latency** in official benchmarks (1.07ms vs 13.73ms minimum)
- **132x higher throughput** in write-heavy workloads (30% writes)
- 100,000 node insertions in 400ms vs Neo4j's 3.8 seconds (~10x improvement)

Note: Performance claims are vendor-provided; independent benchmarks show varying results depending on workload characteristics.

**Real-Time Streaming:**
- Built from the ground up for streaming data ingestion
- Native connectors for Kafka, Redpanda, Apache Pulsar, RabbitMQ
- At-least-once delivery semantics
- Real-time graph updates with sub-millisecond query latency

**Dynamic Analytics:**
- On-the-fly intelligence with triggers and rules
- Dynamic algorithms that update incrementally as graphs change
- Recalculates only what's necessary rather than full recomputation

**Extensibility:**
- Embedded Python interpreter for data science workflows
- Direct integration with TensorFlow, PyTorch, Scikit-learn
- Custom query modules in Python, C/C++, and Rust
- MAGE (Memgraph Advanced Graph Extensions) library

**Developer Experience:**
- Neo4j Bolt protocol compatibility
- OpenCypher query language
- Minimal footprint enables edge deployment (IoT, mobile)
- Native Cypher query caching

**New in Version 3.0 (February 2025):**
- **Vector search** for storing graph data as vector embeddings
- **GraphRAG support** for serving explicit relationships to LLMs
- Enables multi-hop reasoning with semantic similarity search
- Production-ready with persistence across restarts

---

## 3. Core Architecture and Components

### Data Model

**Property Graph Model:**
- Nodes (vertices) with properties (key-value pairs)
- Relationships (edges) with properties and direction
- Labels for node categorization
- Relationship types for edge classification

### Storage Architecture

Memgraph implements a sophisticated **multi-version concurrency control (MVCC)** system with three distinct storage modes:

#### Storage Modes

1. **IN_MEMORY_TRANSACTIONAL (default)**
   - Full ACID guarantees
   - Optimized for read/write workloads
   - High concurrency with MVCC
   - Snapshot isolation level

2. **IN_MEMORY_ANALYTICAL**
   - No ACID guarantees (except manual snapshots)
   - Disables MVCC for faster data import
   - Ideal for bulk loading and analysis
   - Up to 6x faster import speeds

3. **ON_DISK_TRANSACTIONAL (Enterprise)**
   - Full ACID guarantees like IN_MEMORY_TRANSACTIONAL
   - Stores data on HDD/SSD using RocksDB
   - Supports graphs larger than available RAM
   - Label and label-property indexes in separate RocksDB instances

### Query Execution Engine

**Cost-Based Query Optimizer:**
- Parses Cypher queries into execution plans
- Tree-like structure of operators
- Cardinality-based cost estimation
- Selects optimal plan from unique plan candidates
- Query plan caching for repeated queries
- Adaptive optimization based on property value distribution (via ANALYZE GRAPH)

**Parallel Processing:**
- Distributed query execution across nodes
- Data exchange during execution
- Parallel recovery with up to 6x speedups
- Multi-threaded index building

### Concurrency Control

**MVCC Implementation:**
- Delta chains track modifications without altering original data
- Each transaction operates on timestamp-based consistent view
- Snapshot Isolation (default) with support for lower levels
- Read Committed and Read Uncommitted also available

**Lock-Free Data Structures:**
- Skip lists for vertex and edge storage
- O(log n) concurrent access
- Lock-free reads
- Coordinated writes through transaction system
- Highly concurrent skip list indexing

**Non-Blocking Operations:**
- Writes never block reads
- Reads never block writes
- Eliminates traditional database global locks

---

## 4. Performance Characteristics

### Throughput and Latency

**Official Benchmarks (Memgraph claims):**
- Latency: 1.07ms to 1 second (23 queries)
- Neo4j comparison: 13.73ms to 3.1 seconds
- Mixed workload (30% writes): 132x higher throughput vs Neo4j
- Write performance: 10x faster node insertion

**Real-World Performance Profile:**
- 1,000+ transactions/second (reads and writes)
- Sub-millisecond query latency for indexed lookups
- Graph sizes: 100GB to 4TB optimal range
- Minimal startup footprint: ~30MB RAM

**Resource Efficiency:**
- In-memory processing eliminates disk I/O bottlenecks
- C++ implementation reduces memory overhead
- Skip list data structures provide O(log n) operations
- Query plan caching reduces compilation overhead

### Performance Optimization Features

- Automatic cardinality estimation
- Property value distribution analysis
- Label-property index selection
- Prometheus-formatted metrics for monitoring
- Real-time performance insights (disk, sessions, streams, transactions)

---

## 5. ACID Compliance and Transaction Support

### ACID Guarantees

Memgraph provides **full ACID compliance** in transactional modes:

- **Atomicity:** Transactions are all-or-nothing via delta objects
- **Consistency:** Constraint enforcement and validation
- **Isolation:** MVCC-based snapshot isolation (default)
- **Durability:** Write-Ahead Logging (WAL) and snapshots

### Transaction Isolation Levels

**Snapshot Isolation (Default):**
- Each transaction sees consistent snapshot
- Prevents dirty reads, non-repeatable reads
- Write-write conflicts detected

**Lower Isolation Levels:**
- Read Committed
- Read Uncommitted
- Configurable per application requirements

### Durability Mechanisms

**Snapshots:**
- Periodic full database captures
- Configurable interval (`--storage-snapshot-interval`)
- On-exit snapshots (`--storage-snapshot-on-exit`)
- Point-in-time recovery capability
- Entire data storage written to disk

**Write-Ahead Logging (WAL):**
- Transaction log before applying changes
- Replays operations since last snapshot
- Ensures no data loss on crash
- Intelligent recovery: uses most recent timeline
- Batched parallel recovery (up to 6x speedup)

**Recovery Process:**
1. Load most recent snapshot
2. If WAL is newer, replay WAL entries
3. Multi-threaded recovery with batching
4. Automatic index rebuilding

---

## 6. Streaming Capabilities and Real-Time Processing

### Native Stream Processing

Memgraph is engineered from the ground up for streaming data:

**Supported Platforms:**
- Apache Kafka
- Confluent Platform (enhanced Kafka)
- Redpanda
- Apache Pulsar
- RabbitMQ

### Stream Integration Features

**Kafka Integration:**
- Native stream creation connected to Kafka topics
- Message arrival triggers transformation functions
- At-least-once semantics
- Batch processing with transaction guarantees
- Offset committed after database commit

**Transformations:**
- Convert streaming data to Cypher queries
- Custom transformation procedures
- Real-time graph updates
- Immediate query availability

**Stream Management:**
- Create/drop streams via Cypher or Memgraph Lab
- Monitor stream status and throughput
- Configure batch sizes and timeouts
- Handle backpressure and failures

### Real-Time Analytics Use Cases

- **IoT data ingestion:** Instant insights from sensor networks
- **Social media analysis:** Live relationship tracking
- **Fraud detection:** Real-time pattern matching
- **Recommendation engines:** Dynamic user behavior analysis
- **Network monitoring:** Immediate anomaly detection

**Performance Benefits:**
- In-memory processing eliminates lag
- Sub-millisecond query response
- No ETL delay
- Continuous graph updates

---

## 7. Supported Algorithms and Graph Analytics

### Built-In Algorithms

Memgraph includes **four pre-optimized algorithms** out-of-the-box:
1. Breadth-First Search (BFS)
2. Depth-First Search (DFS)
3. Weighted Shortest Path
4. All Shortest Paths

### MAGE: Memgraph Advanced Graph Extensions

**Overview:**
- Open-source algorithm library
- Written in Python, C++, Rust, and C
- Community-contributed and officially maintained
- Invoked via Cypher CALL clause

**Algorithm Categories:**

**Centrality Algorithms:**
- PageRank
- Betweenness Centrality (static and dynamic)
- Katz Centrality (static and dynamic)
- Degree Centrality
- Eigenvector Centrality
- Closeness Centrality

**Community Detection:**
- Louvain Method
- Label Propagation
- Weakly Connected Components
- Strongly Connected Components

**Link Analysis:**
- HITS (Hyperlink-Induced Topic Search)
- Label Propagation
- Cycle Detection

**Path Finding:**
- Dijkstra's Algorithm
- A* Search
- All Simple Paths

**Temporal Graph Networks:**
- Dynamic Betweenness Centrality
- Dynamic Katz Centrality
- Time-evolving graph analytics

**GPU-Accelerated Algorithms (NVIDIA cuGraph):**
- Large-scale graph analytics
- Centrality measures on GPU
- Graph clustering at scale
- Leverages CUDA for parallel processing

### Custom Algorithm Development

**Extensibility:**
- Write custom query modules in Python, C++, Rust, or C
- Embedded Python interpreter
- Access to data science libraries:
  - TensorFlow
  - PyTorch
  - Scikit-learn
  - NetworkX
  - NumPy/SciPy

**Query Module APIs:**
- Full access to graph data structures
- Transaction context
- Property manipulation
- Result streaming

---

## 8. Integration Capabilities and APIs

### Query Language

**OpenCypher:**
- Industry-standard graph query language
- Pattern matching for graph traversals
- Declarative syntax
- Aggregations and projections
- Custom query modules via CALL

**GQL Exploration:**
- New ISO standard for graph queries
- Team exploring GQL support
- Committed to standards compliance

**Natural Language Queries (Memgraph Lab):**
- English questions translated to Cypher
- LLM-powered query generation
- Simplified database interaction

### Client Drivers and SDKs

**Supported Languages:**
- Python (Neo4j driver, GQLAlchemy, pymgclient)
- Java (Neo4j driver)
- C/C++ (pymgclient)
- C# (.NET Neo4j driver)
- Go (Neo4j driver)
- Haskell
- JavaScript/Node.js
- PHP
- Ruby
- Rust

**Protocol:**
- Neo4j Bolt protocol
- Binary protocol for efficient communication
- Encrypted connections (TLS/SSL)

### Python Ecosystem

**GQLAlchemy:**
- Object-graph mapper (OGM)
- Query builder
- Pythonic graph operations
- Stream and trigger management
- Import utilities for various formats

**pymgclient:**
- Official Memgraph Python driver
- Native C implementation
- High performance

**Neo4j Python Driver:**
- Full compatibility
- Drop-in replacement for Neo4j apps

### Data Import/Export

**CSV Import:**
- LOAD CSV Cypher clause
- Direct Lab import wizard
- Best performance for bulk loading

**JSON Import:**
- `json_util.load_from_path()` procedure
- `import_util.json()` procedure
- Flexible JSON structure support

**Other Formats (via GQLAlchemy):**
- Parquet files
- ORC files
- IPC/Feather/Arrow files

**DuckDB Integration:**
- Query any DuckDB-supported source
- Run analytical queries before import
- Direct result loading

**Streaming Ingestion:**
- Kafka consumers
- Redpanda consumers
- Pulsar consumers
- RabbitMQ consumers

**RDBMS Migration:**
- Microsoft SQL Server
- MySQL
- PostgreSQL
- ETL process support

**Export:**
- Cypher query results to CSV/JSON
- Snapshot files for backup
- WAL files for replication

### External System Integration

**AI/ML Platforms:**
- LangChain integration
- Vector embeddings
- GraphRAG workflows
- LLM context augmentation

**Data Platforms:**
- Elasticsearch synchronization
- Kafka streaming
- DuckDB analytics

**Authentication Systems:**
- LDAP
- PAM
- SAML (SSO)
- OIDC (SSO)
- Microsoft EntraID
- Okta

**Monitoring:**
- Prometheus metrics
- Custom monitoring integrations

---

## 9. Advanced Features

### Vector Search and GraphRAG (Version 3.0+)

**Vector Search Capabilities:**
- Native vector index support (CREATE VECTOR INDEX)
- Store graph data as vector embeddings
- Semantic similarity search
- Persists across restarts
- Production-ready (no experimental flags)

**GraphRAG Integration:**
- Combine graph relationships with vector embeddings
- Multi-hop reasoning
- Fast similarity search
- Dynamic context refinement for LLMs
- Serve explicit relationships to language models

**Real-World Applications:**
- NASA HR Q&A system
- Cedars-Sinai Alzheimer's Knowledge Base
- Document search with knowledge graphs
- Visual search using embeddings

### Multi-Tenancy (Enterprise)

**Capabilities:**
- Multiple isolated databases per instance
- Tenant-specific data isolation
- Cross-database query prevention
- Default "memgraph" administrative database

**Access Control:**
- MULTI_DATABASE_USE privilege (switch/list databases)
- MULTI_DATABASE_EDIT privilege (create/delete databases)
- Multi-tenant roles (different roles per database)
- Fine-grained isolation

**Resource Management:**
- Shared underlying resources (CPU, RAM)
- Global limitations (no per-database quotas currently)
- Cost-effective multi-tenant deployments

### Triggers and Event-Driven Automation

**Trigger Types:**
- ON CREATE: Node or relationship creation
- ON UPDATE: Node property changes
- ON DELETE: Relationship deletion

**Capabilities:**
- Execute Cypher statements on events
- Call custom query modules
- Python procedure integration
- Send data to external systems (Kafka, APIs)
- Automated notifications

**Use Cases:**
- Data synchronization
- Audit logging
- Cache invalidation
- Real-time notifications
- Derived data computation

### Indexes and Constraints

**Index Types:**
- Label indexes
- Label-property indexes
- Vector indexes (3.0+)

**Constraint Types:**
- Node property existence
- Uniqueness constraints (single or composite)

**Implementation:**
- Skip list-based indexing
- O(log n) search performance
- Automatic constraint enforcement
- Manual index creation required for uniqueness constraints

**Schema Management:**
- `schema.assert()` procedure
- Programmatic index/constraint management
- `ANALYZE GRAPH` for cardinality estimation
- Optimal index selection

### Security Features (Enterprise)

**Authentication:**
- Username/password (basic)
- LDAP integration
- SAML SSO
- OIDC SSO
- PAM integration

**Authorization:**
- Role-Based Access Control (RBAC)
- Clause-based authorization (MATCH, CREATE, MERGE, etc.)
- Label-Based Access Control (LBAC)
- Node label and relationship type permissions

**Additional Security:**
- Encryption at rest and in transit
- Activity auditing
- Advanced password policies
- Full audit logging

**LDAP Features:**
- Bind and search operations
- Role mapping from LDAP groups
- Centralized user management
- Hybrid permission model (Memgraph manages privileges)

---

## 10. High Availability and Deployment

### Replication

**Architecture:**
- MAIN instance (primary)
- REPLICA instances (secondary)
- System metadata replication (Enterprise)

**Replication Modes:**

**SYNC Mode:**
- Waits for replica acceptance
- MAIN can commit if replica is down
- Balance of consistency and availability

**ASYNC Mode:**
- Eventual consistency
- High availability
- Partition tolerance
- No write blocking

**STRICT_SYNC Mode:**
- Strong consistency
- Partition tolerance
- No availability for writes if replica is down
- CAP theorem: CP system

### High Availability (Enterprise)

**Features:**
- Automatic failover
- Minimal downtime
- Raft-based coordinator cluster
- Cluster state tracking
- Operational continuity for reads and writes

**Architecture:**
- Data instance replication
- Coordinator cluster for orchestration
- Health monitoring
- Automatic leader election

**Community vs. Enterprise:**
- Community: Manual failover required
- Enterprise: Built-in automatic failover

### Deployment Options

**Container Deployment (Recommended):**
- Docker images:
  - `memgraph` (core database)
  - `memgraph-mage` (with MAGE library)
  - `memgraph-platform` (database + Lab + MAGE)
- Kubernetes:
  - Standalone Helm chart (single instance)
  - High Availability Helm chart (production cluster)
- 10% performance overhead vs. native

**Native Installation:**
- Debian packages (.deb)
- RPM packages (.rpm)
- Direct binary installation
- Up to 10% better performance

**Cloud Platforms:**

**Memgraph Cloud (Managed Service):**
- Fully managed on AWS
- 6 geographic regions
- Up to 32GB RAM per instance
- Up to 8 CPU cores
- Enterprise features included

**Self-Managed Cloud:**
- AWS deployment guides
- Azure deployment guides
- GCP deployment guides
- Kubernetes on any cloud
- VM configuration documentation

### Backup and Recovery

**Backup Components:**
- Snapshot files (full database state)
- WAL files (incremental changes)
- Configuration files

**Backup Process:**
- Copy snapshots from `snapshots/` directory
- Copy WAL files from `wal/` directory
- Use tools like rclone for automation
- Manual backup responsibility (no built-in solution)

**Recovery Process:**
1. Restore most recent snapshot
2. Replay WAL if newer
3. Multi-threaded recovery
4. Automatic index rebuilding

**Point-in-Time Recovery:**
- Snapshots provide specific recovery points
- WAL replay for precise recovery
- Configurable snapshot intervals

---

## 11. Operational Tools

### Memgraph Lab

**Overview:**
- Visual interface for database management
- Graph visualization and exploration
- Query execution and optimization
- Docker-based deployment (localhost:3000)

**Key Features:**

**Visualization:**
- Orb library for rendering
- Graph Style Script (GSS) customization
- Node and relationship styling
- Interactive graph exploration

**Query Development:**
- Cypher query editor
- Natural language query translation
- Query sharing and collections
- Result visualization

**Monitoring:**
- Real-time performance metrics
- Query plan analysis
- Slow query identification
- Resource utilization

**Multi-Tenancy Support:**
- Switch between databases
- Manage production, staging, testing
- Single interface for all environments

**Collaboration:**
- Share queries with team
- Query collections
- Result sharing

**Stream Management:**
- Create/connect Kafka streams
- Monitor stream status
- Configure transformations

### Monitoring and Metrics

**Prometheus Integration:**
- Standard Prometheus format
- Real-time metrics export

**Available Metrics:**
- Disk usage
- Active sessions
- Snapshot creation
- Stream throughput
- Transaction counts
- Query operator performance
- Memory utilization

### Command-Line Tools

**mgconsole:**
- Official CLI client
- pymgclient-based
- Interactive and scripting modes

**GQLAlchemy CLI:**
- Python-based utilities
- Data import helpers
- Schema management

---

## 12. Licensing and Editions

### Community Edition

**License:**
- Business Source License (BSL)
- Source-available (not strictly open source)
- Free for most use cases
- Converts to Apache 2.0 after 4 years
- Current Change Date: 2029-09-05

**Restrictions:**
- Cannot make it a standalone service for third parties
- Cannot host as database-as-a-service
- Cannot create competing solutions

**Features:**
- Core database functionality
- ACID transactions
- OpenCypher queries
- Streaming integration
- MAGE algorithms
- Manual replication setup
- Manual failover

### Enterprise Edition

**License:**
- Memgraph Enterprise License (MEL)
- Commercial licensing
- SLA support
- Enterprise-grade features

**Additional Features:**
- Automatic high availability
- Automatic failover
- Multi-tenancy support
- ON_DISK_TRANSACTIONAL storage mode
- Role-based access control (RBAC)
- Label-based access control (LBAC)
- LDAP/SSO authentication
- Activity auditing
- Advanced password policies
- System metadata replication
- Enterprise support with SLAs

---

## 13. Use Cases and Industry Applications

### Fraud Detection

**Capabilities:**
- Real-time pattern matching
- Relationship traversal
- Anomaly detection algorithms
- Community detection

**Real-World Results:**
- US insurance company: 135% increase in fraud detection efficiency
- Millions in prevented losses
- Hidden connection identification

### Recommendation Engines

**Techniques:**
- Collaborative filtering via graph traversal
- Community detection for cold start problem
- Similar user/item identification
- Real-time preference updates

**Applications:**
- E-commerce product recommendations
- Social media content suggestions
- Personalized user experiences

### Network Analysis

**Use Cases:**
- Social network analysis
- Infrastructure monitoring
- Telecommunication networks
- Supply chain optimization

**Algorithms:**
- Centrality measures
- Path finding
- Community detection
- Influence propagation

### Knowledge Graphs

**Applications:**
- Enterprise data integration
- Question-answering systems
- Semantic search
- Data lineage tracking

**GraphRAG Integration:**
- Document embedding
- Multi-hop reasoning
- Context-aware LLM responses

### Real-Time Analytics

**Scenarios:**
- Cyber threat detection
- IoT device monitoring
- Financial transaction analysis
- Social media trending

**Advantages:**
- Sub-millisecond latency
- Streaming data ingestion
- Immediate pattern detection

---

## 14. Technical Specifications

### System Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 10GB disk space (for WAL and snapshots)
- Linux, macOS, or Windows (Docker)

**Recommended Production:**
- 8+ CPU cores
- 32GB+ RAM (for 100GB+ graphs)
- SSD storage for snapshots
- Kubernetes cluster for HA

**Edge Deployment:**
- ~30MB RAM footprint on startup
- Suitable for IoT devices
- Mobile deployment capable

### Supported Platforms

**Operating Systems:**
- Linux (Ubuntu, Debian, RHEL, CentOS)
- macOS (via Docker)
- Windows (via Docker or WSL)

**Container Platforms:**
- Docker
- Kubernetes
- OpenShift
- Rancher

**Cloud Providers:**
- AWS (including Memgraph Cloud)
- Azure
- Google Cloud Platform
- Any Kubernetes-compatible cloud

### Performance Limits

**Graph Size:**
- Optimal: 100GB to 4TB
- IN_MEMORY: Limited by available RAM
- ON_DISK (Enterprise): Exceeds RAM limits

**Throughput:**
- 1,000+ transactions/second (typical)
- Higher with analytical mode
- Scales with hardware

**Concurrency:**
- High concurrent read/write support
- MVCC enables non-blocking operations
- Limited by CPU cores for parallel execution

---

## 15. Development and Community

### Open Source

**Repository:**
- GitHub: `memgraph/memgraph`
- BSL license
- Active development
- Community contributions welcome

**MAGE Repository:**
- GitHub: `memgraph/mage`
- Community algorithm contributions
- Open development process

### Documentation

**Official Resources:**
- Comprehensive documentation at memgraph.com/docs
- Tutorial and how-to guides
- API references
- Blog with technical deep-dives

**Learning Resources:**
- Example applications
- Sample datasets
- Video tutorials
- Community forums

### Support

**Community:**
- GitHub Issues
- Community forum
- Discord channel
- Stack Overflow tag

**Enterprise:**
- SLA-backed support
- Dedicated support engineers
- Priority bug fixes
- Custom feature development

### Funding and Backing

- $9.34M seed funding (2021)
- Led by Microsoft's M12
- Additional investors
- Continuing development investment

---

## 16. Comparison with Other Graph Databases

### vs. Neo4j

**Memgraph Advantages:**
- In-memory architecture (faster for hot data)
- Better streaming integration
- Native real-time processing
- Lower latency (claimed)
- C++ performance
- Dynamic algorithm support

**Neo4j Advantages:**
- Larger ecosystem
- More mature (since 2007)
- Broader community
- More third-party integrations
- Battle-tested in enterprise
- Larger graph support (disk-based)

### vs. Amazon Neptune

**Memgraph Advantages:**
- Self-hosted option
- Lower latency
- Better performance for hot data
- More flexible deployment

**Neptune Advantages:**
- Fully managed
- AWS integration
- No operational overhead
- Automatic scaling

### vs. TigerGraph

**Memgraph Advantages:**
- Simpler architecture
- Better developer experience
- Cypher query language
- Easier learning curve

**TigerGraph Advantages:**
- Better for massive distributed graphs
- GSQL query language
- Built-in visualization

### vs. Redis Graph

**Memgraph Advantages:**
- More comprehensive features
- Better ACID guarantees
- Richer algorithm library
- Enterprise support

**Redis Graph Advantages:**
- Integrated with Redis ecosystem
- Simpler for basic use cases

---

## 17. Future Roadmap

### Confirmed Developments

**GQL Support:**
- Exploring ISO GQL standard
- Maintaining OpenCypher compatibility
- Standards-focused approach

**GraphRAG Enhancements:**
- Deeper LLM integration
- Advanced vector search
- Hybrid retrieval strategies

### Community Requests

- Per-database resource quotas
- Enhanced multi-tenant isolation
- Additional GPU algorithm acceleration
- Broader cloud marketplace availability

---

## Conclusion

Memgraph is a modern, high-performance graph database platform optimized for real-time analytics on streaming data. Its in-memory architecture, ACID compliance, native streaming support, and extensive algorithm library make it well-suited for applications requiring sub-millisecond latency and high throughput. The addition of vector search and GraphRAG capabilities in version 3.0 positions Memgraph as a strong choice for AI-powered graph applications.

**Best suited for:**
- Real-time fraud detection
- Live recommendation engines
- Streaming analytics
- Network monitoring
- IoT data processing
- GraphRAG and LLM-augmented applications
- High-throughput transactional workloads

**Consider alternatives if:**
- Need massive distributed graphs (100+ TB)
- Require primarily cold data queries
- Want fully managed cloud-only deployment
- Need extensive vendor ecosystem (tools, consultants)

The platform's BSL licensing provides open access for most use cases, while enterprise features address production requirements for security, availability, and support.


## Graph & Geo — Iceberg


> Source: `docs/data_engineering/iceberg/Iceberg in the Browser.md`

---
title: "Iceberg in the Browser"
source: "https://duckdb.org/2025/12/16/iceberg-in-the-browser"
author:
  - "[[Carlo Piovesan]]"
  - "[[Tom Ebergen]]"
  - "[[Gábor Szárnyas]]"
published: 2025-12-16
created: 2025-12-17
description: "DuckDB is the first end-to-end interface to Iceberg REST Catalogs within a browser tab. You can now read and write tables in Iceberg catalogs without needing to manage any infrastructure – directly from your browser!"
tags:
  - "clippings"
---
*TL;DR: DuckDB is the first end-to-end interface to Iceberg REST Catalogs within a browser tab. You can now read and write tables in Iceberg catalogs without needing to manage any infrastructure – directly from your browser!*

In this post, we describe the current patterns for interacting with Iceberg Catalogs, and pose the question: could it be done from a browser? After elaborating on the DuckDB ecosystem changes required to unlock this capability, we demonstrate our approach to interacting with an Iceberg REST Catalog. It's browser-only, no extra setup required.

![Iceberg analytics today](https://duckdb.org/images/blog/iceberg-wasm/iceberg-analytics-today-dark.svg) ![Iceberg analytics today](https://duckdb.org/images/blog/iceberg-wasm/iceberg-analytics-today-light.svg)

*Iceberg* is an *open table format,* which allows you to capture a mutable database table as a set of static files on object storage (such as AWS S3).*Iceberg catalogs* allow you to track and organize Iceberg tables. For example, [Iceberg REST Catalogs](https://iceberg.apache.org/rest-catalog-spec/) provide these functionalities through a REST API.

There are two common ways to interact with Iceberg catalogs:

- The *client–server model,* where the compute part of the operation is delegated to a managed infrastructure (such as the cloud). Users can interact with the server by installing a local client or using a lightweight client such as a browser.
- The *client-is-the-server model,* where the user first installs the relevant libraries, and then performs queries directly on their machine.

Iceberg engines follow these interaction models: they are either run natively in managed compute infrastructure or they are run locally by the user. Let's see how things look with DuckDB in the mix!

## Iceberg with DuckDB

![Iceberg with DuckDB](https://duckdb.org/images/blog/iceberg-wasm/iceberg-with-duckdb-dark.svg) ![Iceberg with DuckDB](https://duckdb.org/images/blog/iceberg-wasm/iceberg-with-duckdb-light.svg)

DuckDB supports both Iceberg interaction models. In the *client–server model,* DuckDB runs on the server to read the Iceberg datasets. From the user's point of view, the choice of engine is transparent, and DuckDB is just one of many engines that the server could use in the background. The *client-is-the-server* model is more interesting: here, users [install a DuckDB client locally](https://duckdb.org/install/) and use it through its SQL interface to query Iceberg catalogs. For example:

```sql
CREATE SECRET test_secret (
    TYPE S3, 
    KEY_ID 'AKIAIOSFODNN7EXAMPLE',
    SECRET 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
);

ATTACH 'warehouse' AS db (
    TYPE ICEBERG,
    ENDPOINT_URL 'https://your-iceberg-endpoint',
);

SELECT sum(value)
FROM db.table
WHERE other_column = 'some_value';
```

The client-is-the-server model unlocks [empowered clients](https://youtu.be/YQEUkFWa69o?t=3085), which can operate directly on the data.

> You can discover the full DuckDB-Iceberg extension feature set, including insert and update capabilities, in our [earlier blog post](https://duckdb.org/2025/11/28/iceberg-writes-in-duckdb.html).

## Iceberg with DuckDB in the Browser

While setting up a local DuckDB installation is quite simple, opening a browser tab is even quicker. Therefore, we asked ourselves: could we support the *client-is-the-server* model directly from within a browser tab? This could provide a zero-setup, no-infrastructure, properly serverless option for interacting with Iceberg catalogs.

![Iceberg with DuckDB-Wasm](https://duckdb.org/images/blog/iceberg-wasm/duckdb-iceberg-with-duckdb-wasm-dark.svg) ![Iceberg with DuckDB-Wasm](https://duckdb.org/images/blog/iceberg-wasm/duckdb-iceberg-with-duckdb-wasm-light.svg)

Luckily, DuckDB has a client that can run in any browser![DuckDB-Wasm](https://duckdb.org/docs/stable/clients/wasm/overview.html) is a WebAssembly port of DuckDB, which [supports loading of extensions](https://duckdb.org/2023/12/18/duckdb-extensions-in-wasm.html).

Interacting with an Iceberg REST Catalog requires a number of functionalities; the ability to talk to a REST API over HTTP(S), the ability to read and write `avro` and `parquet` files on object storage, and finally, the ability to negotiate authentication to access those resources on behalf of the user. All of these must be done from within a browser without calling any native components.

To support these functionalities, we implemented the following high-level changes:

- In the core `duckdb` codebase, we redesigned HTTP interactions, so that extensions and clients have a uniform interface to the networking stack. ([PR](https://github.com/duckdb/duckdb/pull/17464))
- In `duckdb-wasm`, we implemented such an interface, which in this case is a wrapper around the available JavaScript network stack. ([PR](https://github.com/duckdb/duckdb-wasm/pull/2056))
- In `duckdb-iceberg`, we routed all networking through the common HTTP interface, so that native DuckDB and DuckDB-Wasm execute the same logic. ([PR](https://github.com/duckdb/duckdb-iceberg/pull/576))

**The result is that you can now query Iceberg with DuckDB running directly in a browser!** Now you can access the same Iceberg catalog using *client–server*, *client-is-the-server*, or properly serverless from the isolation of a browser tab!

## Welcome to Serverless Iceberg Analytics

To see a demo of serverless Iceberg analytics, visit our table visualizer at [`duckdb.org/visualizer?iceberg`](https://duckdb.org/visualizer/?iceberg).

<video controls="controls" width="700"><source src="https://blobs.duckdb.org/videos/iceberg-wasm-demo.mp4" type="video/mp4"></video>

> The current credentials in the demo are provided via a throwaway account with minimal permissions. If you enter your own credentials and share a link, you will be sharing your credentials.

## Access Your Own Data

Substituting your own S3Tables bucket ARN and credentials with policy [`AmazonS3TablesReadOnlyAccess`](https://us-east-1.console.aws.amazon.com/iam/home?region=us-east-2#/policies/details/arn%3Aaws%3Aiam%3A%3Aaws%3Apolicy%2FAmazonS3TablesReadOnlyAccess), you can also access your catalog, metadata and data. Computations are fully local, and the credentials and warehouse ID are only sent to the catalog endpoint specified in your `ATTACH` command. Inputs are translated to SQL, and added to the hash segment of the URL.

This means that:

- no sensitive data is handled or sent to `duckdb.org`
- computations are local, fully in your browser
- you can use the familiar SQL interface with the same code snippets that can run everywhere DuckDB runs
- if you edit the credentials and share the resulting link, you will be sharing the new credentials

As of today, this works with [Amazon S3 Tables](https://duckdb.org/docs/stable/core_extensions/iceberg/amazon_s3_tables.html). This has been implemented through a collaboration with the Amazon S3 Tables team. To learn more about S3 Tables, how to get started and their feature set, you can take a look at their [product page](https://aws.amazon.com/s3/features/tables/) or [documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html). A demo of DuckDB querying S3 Tables from a browser was presented at AWS re:Invent 2025 – [see the presentation](https://www.youtube.com/watch?v=Pi82g0YGklU&t=2603s).

## Conclusion

The DuckDB-Iceberg extension is now supported in DuckDB-Wasm and it can read and edit Iceberg REST Catalogs. Users can now access Iceberg data from within a browser, without having to install or manage any compute nodes!

If you would like to provide feedback or file issues, please reach out to us on either the [DuckDB-Wasm](https://github.com/duckdb/duckdb-wasm) or [DuckDB-Iceberg](https://github.com/duckdb/duckdb-iceberg) repository. If you are interested in using any part of this within your organization, feel free to [reach out](https://duckdblabs.com/contact/).

## Observability — Logfire


> Source: `docs/data_engineering/logfire/Logfire - Pydantic Logfire Documentation.md`

---
title: "Logfire - Pydantic Logfire Documentation"
source: "https://logfire.pydantic.dev/docs/"
author:
published:
created: 2025-12-29
description: "Pydantic Logfire Documentation"
tags:
  - "clippings"
---
[Skip to content](https://logfire.pydantic.dev/docs/#getting-started)

## Getting Started

## About Pydantic Logfire

From the team behind **Pydantic Validation**, **Pydantic Logfire** is a new type of observability platform built on the same belief as our open source library — that the most powerful tools can be easy to use.

**Logfire** is built on OpenTelemetry, and supports monitoring your application from **any language**, with particularly great support for Python! [Read more](https://logfire.pydantic.dev/docs/why/).

## Overview

This page is a quick walk-through for setting up a Python app:

1. [Set up Logfire](https://logfire.pydantic.dev/docs/#logfire)
2. [Install the SDK](https://logfire.pydantic.dev/docs/#sdk)
3. [Instrument your project](https://logfire.pydantic.dev/docs/#instrument)

## Set up Logfire

1. [Log into Logfire](https://logfire.pydantic.dev/login)
2. Follow the prompts to create your account
3. Once logged in, you'll see the **Welcome to Logfire** prompt. Click **Let's go!** to go to the **starter-project** Setup page.

[![Welcome to Logfire](https://logfire.pydantic.dev/docs/images/logfire-screenshot-welcome-to-logfire.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-welcome-to-logfire.png)

1. You will find how to send data to your **starter-project** there. Also, there are some code snippets to help you get started.

A **Logfire** project is a namespace for organizing your data. All data sent to **Logfire** must be associated with a project.

Ready to create your own projects in UI or CLI?
- In the UI, create projects by navigating to the Organization > Projects page, and click **New project**.
- For CLI check the [SDK CLI documentation](https://logfire.pydantic.dev/docs/reference/cli/#create-projects-new).

## Install the SDK

1. In the terminal, install the **Logfire** SDK (Software Developer Kit):

```bash
pip install logfire
```

```bash
uv add logfire
```

```bash
conda install -c conda-forge logfire
```

1. Once installed, try it out!
```bash
logfire -h
```
1. Next, authenticate your local environment:
```bash
logfire auth
```

Upon successful authentication, credentials are stored in `~/.logfire/default.toml`.

## Instrument your project

Development setup

During development, we recommend using the CLI to configure Logfire. You can also use a [write token](https://logfire.pydantic.dev/docs/how-to-guides/create-write-tokens/).

1. Set your project
```bash
in the terminal:logfire projects use <first-project>
```

Run this command from the root directory of your app, e.g. `~/projects/first-project`

1. Write some basic logs in your Python app
```bash
hello_world.pyimport logfire

logfire.configure()  The configure() method should be called once before logging to initialize Logfire.
logfire.info('Hello, {name}!', name='world')  This will log Hello world! with info level.
```

Other [log levels](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`,`error`, and `fatal`.

1. See your logs in the **Live** view

[![Hello world screenshot](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)

Production setup

In production, we recommend you provide your write token to the Logfire SDK via environment variables.

1. Generate a new write token in the **Logfire** platform
	- Go to Project Settings Write Tokens
	- Follow the prompts to create a new token
2. Configure your **Logfire** environment
```bash
In the terminal:export LOGFIRE_TOKEN=<your-write-token>
```

Running this command stores a Write Token used by the SDK to send data to a file in the current directory, at `.logfire/logfire_credentials.json`

1. Write some basic logs in your Python app
```bash
hello_world.pyimport logfire

logfire.configure()  
logfire.info('Hello, {name}!', name='world')
```
1. The `configure()` method should be called once before logging to initialize **Logfire**.
2. This will log `Hello world!` with `info` level.

Other [log levels](https://logfire.pydantic.dev/docs/reference/api/logfire/#logfire.Logfire) are also available to use, including `trace`, `debug`, `notice`, `warn`,`error`, and `fatal`.

1. See your logs in the **Live** view

[![Hello world screenshot](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)](https://logfire.pydantic.dev/docs/images/logfire-screenshot-first-steps-hello-world.png)

---

Ready to keep going?

- Read about [Concepts](https://logfire.pydantic.dev/docs/concepts/)
- Complete the [Onboarding Checklist](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/)

More topics to explore...

- Logfire's real power comes from [integrations with many popular libraries](https://logfire.pydantic.dev/docs/integrations/)
- As well as spans, you can [use Logfire to record metrics](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/add-metrics/)
- Logfire doesn't just work with Python, [read more about Language support](https://opentelemetry.io/docs/languages/)
- Compliance requirements (e.g. SOC2)? [See Logfire's certifications](https://logfire.pydantic.dev/docs/compliance/)

## Original Sources

### crawl4ai/
- `docs/data_engineering/crawl4ai/Crawl4ai Scraping and Site Analysis.md`
- `docs/data_engineering/crawl4ai/crawl4ai-analysis.md`
- `docs/data_engineering/crawl4ai/crawl4ai-dlt.md`
- `docs/data_engineering/crawl4ai/crawl4ai-index.md`
- `docs/data_engineering/crawl4ai/crawl4ai-openapi-research.md`
- `docs/data_engineering/crawl4ai/crawl4ai-summary.md`
- `docs/data_engineering/crawl4ai/crawl4ai.md`

### firecrawl/
- `docs/data_engineering/firecrawl/Extract _ Firecrawl.md`

### gemini/
- `docs/data_engineering/gemini/Gemini 3 Hackathon.md`
- `docs/data_engineering/gemini/gemini-code-assist-configuration.md`
- `docs/data_engineering/gemini/gemini-quick-reference.md`

### gradio/
- `docs/data_engineering/gradio/gradio-comprehensive-research.md`
- `docs/data_engineering/gradio/gradio-openapi-research.md`

### ibis/
- `docs/data_engineering/ibis/Ibis, LanceDB, and Data Stack Integration.md`
- `docs/data_engineering/ibis/ibis.md`

### pydantic/
- `docs/data_engineering/pydantic/pydantic_schema_validate.md`
- `docs/data_engineering/pydantic/pydantic-v2-comprehensive-guide.md`
- `docs/data_engineering/pydantic/pydantic.md`

### evidence/
- `docs/data_engineering/evidence/evidence-dev-component-reference.md`
- `docs/data_engineering/evidence/evidence.md`

### kafka/
- `docs/data_engineering/kafka/Kafka Topic Mirroring _ Bento _ Fancy stream processing made operationally mundane.md`

### risingwave/
- `docs/data_engineering/risingwave/risingwave-best-practices.md`
- `docs/data_engineering/risingwave/risingwave-connectors-research.md`
- `docs/data_engineering/risingwave/risingwave-sql-patterns.md`
- `docs/data_engineering/risingwave/risingwave.md`

### olake/
- `docs/data_engineering/olake/olake-data-models-schemas-ontologies.md`
- `docs/data_engineering/olake/olake-database-replication-guide.md`
- `docs/data_engineering/olake/olake-patterns-architecture.md`
- `docs/data_engineering/olake/olake.md`

### memgraph/
- `docs/data_engineering/memgraph/memgraph-research.md`
- `docs/data_engineering/memgraph/memgraph.md`

### iceberg/
- `docs/data_engineering/iceberg/Iceberg in the Browser.md`

### logfire/
- `docs/data_engineering/logfire/Logfire - Pydantic Logfire Documentation.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
