# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "crawl4ai>=0.4.0",
#     "pydantic>=2.0.0",
#     "polars>=1.0.0",
#     "altair>=5.0.0",
#     "pandas>=2.0.0",
#     "python-dotenv>=1.0.0",
#     "plotly>=5.0.0",
# ]
# ///

import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Crawl4AI: Web Scraping & Content Extraction

    This notebook demonstrates Crawl4AI's capabilities:

    1. **Async Web Crawling** - High-performance concurrent crawling
    2. **LLM Extraction** - Structured data extraction with schemas
    3. **Multi-Config Crawling** - URL pattern matching for different strategies
    4. **Adaptive Crawling** - Statistical & embedding-based relevance scoring
    5. **Docker Integration** - Webhook-based async processing

    > Based on patterns from `/data/examples/crawl4ai/`
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    import json
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    return mo, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Basic Async Crawling

    Crawl4AI provides an async-first API for high-performance web scraping.
    """)
    return


@app.cell
def _(mo):
    # URL input
    crawl_url = mo.ui.text(
        value="https://docs.anthropic.com/en/docs/about-claude/models",
        label="URL to Crawl",
        placeholder="Enter URL to crawl..."
    )
    crawl_url
    return (crawl_url,)


@app.cell
def _():
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
    return AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


@app.cell
def _(mo):
    # Stealth mode options for anti-detection
    stealth_mode = mo.ui.checkbox(value=True, label="Enable Stealth Mode (bypass Cloudflare)")
    stealth_mode
    return (stealth_mode,)


@app.cell
def _(mo):
    run_crawl_btn = mo.ui.run_button(label="Crawl URL")
    run_crawl_btn
    return (run_crawl_btn,)


@app.cell
async def _(
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    crawl_url,
    mo,
    run_crawl_btn,
    stealth_mode,
):
    crawl_result = None

    if run_crawl_btn.value:
        with mo.status.spinner(title="Crawling..."):
            # Configure browser with stealth mode for anti-detection
            _browser_config = BrowserConfig(
                headless=True,
                enable_stealth=stealth_mode.value,
                # Use realistic user agent
                user_agent_mode="random" if stealth_mode.value else None,
            )

            _config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=1,
                # Wait for Cloudflare challenge to complete
                wait_until="networkidle",  # Wait for network to be idle
                page_timeout=60000,  # 60 second timeout for slow challenges
                delay_before_return_html=3.0,  # Extra delay after page load
            )

            async with AsyncWebCrawler(config=_browser_config) as _crawler:
                crawl_result = await _crawler.arun(
                    url=crawl_url.value,
                    config=_config,
                )

            if crawl_result.success:
                mo.md(f"""
**Crawl Successful!**

- **URL:** {crawl_result.url}
- **Status Code:** {crawl_result.status_code}
- **Markdown Length:** {len(crawl_result.markdown)} characters
- **Links Found:** {len(crawl_result.links.get('internal', [])) + len(crawl_result.links.get('external', []))}
- **Stealth Mode:** {"Enabled" if stealth_mode.value else "Disabled"}
                """)
            else:
                mo.md(f"**Crawl Failed:** {crawl_result.error_message}")
    else:
        mo.md("*Click 'Crawl URL' to start*")
    return (crawl_result,)


@app.cell
def _(crawl_result):
    crawl_result.markdown
    return


@app.cell
def _(crawl_result, mo):
    # Display markdown preview
    if crawl_result and crawl_result.success:
        preview_length = min(2000, len(crawl_result.markdown))
        mo.md(f"""
        ### Markdown Preview (first {preview_length} chars)

        ```markdown
        {crawl_result.markdown[:preview_length]}...
        ```
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. LLM-Based Structured Extraction

    Extract structured data using Pydantic schemas and LLM processing.
    """)
    return


@app.cell
def _():
    from pydantic import BaseModel, Field
    from typing import List, Optional
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    from crawl4ai import LLMConfig
    return BaseModel, Field, LLMConfig, LLMExtractionStrategy, List, Optional


@app.cell
def _(BaseModel, Field, List, Optional):
    # Define extraction schema
    class PageSummary(BaseModel):
        """Schema for extracting page summaries."""
        title: str = Field(..., description="Page title")
        summary: str = Field(..., description="2-3 sentence summary")
        key_topics: List[str] = Field(..., description="Main topics covered")
        code_examples: Optional[int] = Field(None, description="Number of code examples")

    class ModelPricing(BaseModel):
        """Schema for extracting API pricing information."""
        model_name: str = Field(..., description="Name of the model")
        input_price: Optional[str] = Field(None, description="Price per input token")
        output_price: Optional[str] = Field(None, description="Price per output token")
        context_window: Optional[str] = Field(None, description="Context window size")
    return (ModelPricing,)


@app.cell
def _(mo, os):
    # LLM configuration
    llm_provider = mo.ui.dropdown(
        options=["openai/gpt-4o-mini", "openai/gpt-4o", "ollama/llama3.2"],
        value="openai/gpt-4o-mini",
        label="LLM Provider"
    )

    api_key_input = mo.ui.text(
        value=os.environ.get("OPENAI_API_KEY", ""),
        label="API Key",
        placeholder="Your API key",
        kind="password"
    )

    mo.hstack([llm_provider, api_key_input])
    return api_key_input, llm_provider


@app.cell
def _(mo):
    extract_url = mo.ui.text(
        value="https://openai.com/api/pricing/",
        label="URL for Extraction",
        placeholder="Enter URL..."
    )

    extraction_instruction = mo.ui.text_area(
        value="Extract all AI model pricing information including model names, input costs, and output costs.",
        label="Extraction Instruction"
    )

    mo.vstack([extract_url, extraction_instruction])
    return extract_url, extraction_instruction


@app.cell
def _(mo):
    run_extract_btn = mo.ui.run_button(label="Run LLM Extraction")
    run_extract_btn
    return (run_extract_btn,)


@app.cell
async def _(
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
    LLMExtractionStrategy,
    ModelPricing,
    api_key_input,
    extract_url,
    extraction_instruction,
    llm_provider,
    mo,
    run_extract_btn,
):
    extraction_result = None

    if run_extract_btn.value and api_key_input.value:
        with mo.status.spinner(title="Running LLM extraction..."):
            _browser_config = BrowserConfig(headless=True)

            _crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=1,
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=LLMConfig(
                        provider=llm_provider.value,
                        api_token=api_key_input.value
                    ),
                    schema=ModelPricing.model_json_schema(),
                    extraction_type="schema",
                    instruction=extraction_instruction.value,
                    extra_args={
                        "temperature": 0,
                        "max_tokens": 2000
                    }
                ),
            )

            try:
                async with AsyncWebCrawler(config=_browser_config) as _crawler:
                    extraction_result = await _crawler.arun(
                        url=extract_url.value,
                        config=_crawler_config
                    )

                if extraction_result.success and extraction_result.extracted_content:
                    import json as _json
                    extracted_data = _json.loads(extraction_result.extracted_content)
                    mo.md(f"""
                    **Extraction Complete!**

                    ```json
                    {_json.dumps(extracted_data, indent=2)[:2000]}
                    ```
                    """)
                else:
                    mo.md(f"**Extraction failed or no content:** {extraction_result.error_message}")
            except Exception as e:
                mo.md(f"**Error:** {e}")
    else:
        mo.md("*Configure API key and click 'Run LLM Extraction'*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Multi-Config URL Matching

    Apply different scraping strategies based on URL patterns.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    from crawl4ai import CrawlerRunConfig, MatchMode
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

    configs = [
        # PDF documents - special handling
        CrawlerRunConfig(
            url_matcher="*.pdf",
            scraping_strategy=PDFContentScrapingStrategy()
        ),

        # Blog/article pages - content filtering
        CrawlerRunConfig(
            url_matcher=["*/blog/*", "*/article/*", "*/news/*"],
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48)
            )
        ),

        # Dynamic pages requiring JavaScript
        CrawlerRunConfig(
            url_matcher=lambda url: 'github.com' in url,
            js_code="window.scrollTo(0, document.body.scrollHeight);",
            wait_for="css:.repository-content"
        ),

        # API endpoints - JSON handling
        CrawlerRunConfig(
            url_matcher=[
                "*.json",
                lambda url: 'api' in url or 'httpbin.org' in url
            ],
            match_mode=MatchMode.OR,
        ),

        # Complex matcher with AND logic
        CrawlerRunConfig(
            url_matcher=[
                lambda url: url.startswith('https://'),
                "*.org/*",
                lambda url: any(doc in url for doc in ['docs', 'documentation']),
                lambda url: not url.endswith(('.pdf', '.json'))
            ],
            match_mode=MatchMode.AND,
        ),
    ]

    # Crawl multiple URLs with automatic config matching
    results = await crawler.arun_many(urls=urls, config=configs)
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Adaptive Crawling Strategies

    Crawl4AI supports two adaptive strategies for relevance-based crawling:

    - **Statistical Strategy**: Fast, keyword-based scoring
    - **Embedding Strategy**: Semantic similarity using embeddings
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    from crawl4ai import AdaptiveCrawler, AdaptiveConfig, LLMConfig

    # Statistical Strategy (fast, keyword-based)
    config_statistical = AdaptiveConfig(
        strategy="statistical",
        max_pages=10,
        top_k_links=3,
        min_gain_threshold=0.05,
    )

    # Embedding Strategy (semantic understanding)
    config_embedding = AdaptiveConfig(
        strategy="embedding",
        max_pages=10,
        embedding_llm_config=LLMConfig(
            provider='openai/text-embedding-3-small',
            api_token=os.getenv('OPENAI_API_KEY')
        ),
        embedding_k_exp=4.0,
        n_query_variations=12
    )

    async with AsyncWebCrawler(verbose=False) as crawler:
        adaptive = AdaptiveCrawler(crawler, config_embedding)

        result = await adaptive.digest(
            start_url="https://docs.python.org/3/library/asyncio.html",
            query="async await context managers coroutines"
        )

        # Get most relevant pages
        relevant_pages = adaptive.get_relevant_content(top_k=5)

        for page in relevant_pages:
            print(f"URL: {page['url']}")
            print(f"Relevance Score: {page['score']:.2%}")
            print(f"Content Preview: {page['content'][:200]}")
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. JavaScript Execution

    Handle dynamic pages by executing JavaScript before content extraction.
    """)
    return


@app.cell
def _(mo):
    js_url = mo.ui.text(
        value="https://news.ycombinator.com",
        label="URL with JavaScript"
    )

    js_code = mo.ui.text_area(
        value="""window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1000));
    window.scrollTo(0, 0);""",
        label="JavaScript to Execute"
    )

    mo.vstack([js_url, js_code])
    return js_code, js_url


@app.cell
def _(mo):
    run_js_btn = mo.ui.run_button(label="Crawl with JavaScript")
    run_js_btn
    return (run_js_btn,)


@app.cell
async def _(
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    js_code,
    js_url,
    mo,
    run_js_btn,
):
    js_result = None

    if run_js_btn.value:
        with mo.status.spinner(title="Executing JavaScript and crawling..."):
            _js_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                js_code=[js_code.value],
                wait_for="css:body",
                scan_full_page=True,
                scroll_delay=0.2,
            )

            async with AsyncWebCrawler() as _js_crawler:
                js_result = await _js_crawler.arun(
                    url=js_url.value,
                    config=_js_config
                )

            if js_result.success:
                mo.md(f"""
                **JavaScript Crawl Complete!**

                - **Markdown Length:** {len(js_result.markdown)} chars
                - **Internal Links:** {len(js_result.links.get('internal', []))}
                - **Images:** {len(js_result.media.get('images', []))}
                """)
            else:
                mo.md(f"**Failed:** {js_result.error_message}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Docker Integration with Hooks

    Crawl4AI can run in Docker with customizable hooks at various stages.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Hook System Architecture

    8 hook points are available:

    1. `on_browser_created` - Browser instance ready
    2. `on_page_context_created` - Block resources, set viewport
    3. `on_user_agent_updated` - User agent changes
    4. `before_goto` - Add headers, authentication
    5. `after_goto` - Page loaded
    6. `on_execution_started` - JS execution starting
    7. `before_retrieve_html` - Scroll, interact with page
    8. `before_return_html` - Final processing, collect metrics

    ```python
    # Performance optimization hook
    async def performance_hook(page, context, **kwargs):
        # Block heavy resources
        await context.route(
            "**/*.{png,jpg,jpeg,gif,webp,svg,ico}",
            lambda route: route.abort()
        )
        await context.route("**/analytics/*", lambda route: route.abort())
        await context.route("**/ads/*", lambda route: route.abort())
        return page

    # Authentication headers hook
    async def auth_hook(page, context, url, **kwargs):
        await page.set_extra_http_headers({
            'X-API-Key': 'your-api-key',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        return page

    # Page analytics hook
    async def analytics_hook(page, context, **kwargs):
        metrics = await page.evaluate('''
            () => ({
                title: document.title,
                images: document.images.length,
                links: document.links.length,
                scripts: document.scripts.length,
            })
        ''')
        print(f"Page metrics: {metrics}")
        return page

    # Use with Docker client
    from crawl4ai.docker_client import Crawl4aiDockerClient

    async with Crawl4aiDockerClient(base_url="http://localhost:8000") as client:
        results = await client.crawl(
            urls=["https://example.com"],
            hooks={
                "on_page_context_created": performance_hook,
                "before_goto": auth_hook,
                "before_return_html": analytics_hook,
            },
            hooks_timeout=30
        )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Webhook-Based Async Processing

    For long-running crawl jobs, use webhooks to receive completion notifications.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    import requests

    CRAWL4AI_BASE_URL = "http://localhost:8000"

    # Submit crawl job with webhook
    def submit_crawl_job(urls, webhook_url, include_data=False):
        payload = {
            "urls": urls,
            "browser_config": {"headless": True},
            "crawler_config": {"cache_mode": "bypass"},
            "webhook_config": {
                "webhook_url": webhook_url,
                "webhook_data_in_payload": include_data,
                # Optional authentication
                # "webhook_headers": {"X-Webhook-Secret": "your-secret"}
            }
        }

        response = requests.post(
            f"{CRAWL4AI_BASE_URL}/crawl/job",
            json=payload
        )

        if response.ok:
            return response.json()['task_id']
        return None

    # Flask webhook handler
    from flask import Flask, request, jsonify

    app = Flask(__name__)

    @app.route('/webhooks/crawl-complete', methods=['POST'])
    def handle_webhook():
        payload = request.json
        task_id = payload['task_id']
        status = payload['status']

        if status == 'completed':
            if 'data' in payload:
                # Process inline results
                for result in payload['data'].get('results', []):
                    print(f"Crawled: {result.get('url')}")
            else:
                # Fetch results from API
                results = requests.get(
                    f"{CRAWL4AI_BASE_URL}/crawl/job/{task_id}"
                ).json()

        return jsonify({"status": "received"}), 200
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Table Extraction & Data Analysis

    Extract tables from web pages for data analysis.
    """)
    return


@app.cell
def _(mo):
    table_url = mo.ui.text(
        value="https://en.wikipedia.org/wiki/List_of_largest_technology_companies_by_revenue",
        label="URL with Tables"
    )
    table_url
    return (table_url,)


@app.cell
def _(mo):
    run_table_btn = mo.ui.run_button(label="Extract Tables")
    run_table_btn
    return (run_table_btn,)


@app.cell
async def _(
    AsyncWebCrawler,
    CacheMode,
    CrawlerRunConfig,
    mo,
    run_table_btn,
    table_url,
):
    import pandas as pd

    table_result = None
    extracted_tables = []

    if run_table_btn.value:
        with mo.status.spinner(title="Extracting tables..."):
            _table_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                table_score_threshold=5,  # Minimum score for table detection
                keep_data_attributes=True,
                scan_full_page=True,
            )

            async with AsyncWebCrawler() as _table_crawler:
                table_result = await _table_crawler.arun(
                    url=table_url.value,
                    config=_table_config
                )

            if table_result.success:
                tables = table_result.media.get("tables", [])
                mo.md(f"**Found {len(tables)} tables**")

                for _i, table in enumerate(tables[:3]):  # Show first 3
                    if table.get("rows") and table.get("headers"):
                        try:
                            _df = pd.DataFrame(
                                table["rows"],
                                columns=table["headers"]
                            )
                            extracted_tables.append(_df)
                        except Exception as e:
                            print(f"Error parsing table {_i}: {e}")
            else:
                mo.md(f"**Failed:** {table_result.error_message}")
    return (extracted_tables,)


@app.cell
def _(extracted_tables, mo):
    if extracted_tables:
        for _i, _df in enumerate(extracted_tables):
            mo.md(f"### Table {_i+1}")
            mo.ui.table(_df.head(10), selection=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Patterns Summary

    ### Basic Crawling
    ```python
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://example.com")
        markdown = result.markdown
        links = result.links
    ```

    ### LLM Extraction
    ```python
    config = CrawlerRunConfig(
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(provider="openai/gpt-4o"),
            schema=MyPydanticModel.model_json_schema(),
            instruction="Extract specific data..."
        )
    )
    ```

    ### Multi-URL Crawling
    ```python
    results = await crawler.arun_many(
        urls=url_list,
        config=configs  # List of configs for pattern matching
    )
    ```

    ### Adaptive Crawling
    ```python
    adaptive = AdaptiveCrawler(crawler, AdaptiveConfig(
        strategy="embedding",
        max_pages=10
    ))
    result = await adaptive.digest(start_url, query)
    relevant = adaptive.get_relevant_content(top_k=5)
    ```

    ### Docker Client
    ```python
    async with Crawl4aiDockerClient(base_url=DOCKER_URL) as client:
        results = await client.crawl(
            urls=["https://example.com"],
            hooks={"before_goto": my_hook}
        )
    ```
    """)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
