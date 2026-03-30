"""
Dagster definitions for crypteolas - crypto analytics data pipeline.

Assets are organized by domain:
- api_sources: External API data ingestion (CoinGecko, DeFiLlama, Binance, Subgraphs)
- document_scraping: Protocol documentation with Firecrawl
- processing: Document indexing (CocoIndex) and knowledge graph (Cognee)
- analytics: Crypto analytics transformations

Jobs, schedules, and sensors are defined separately.
"""
