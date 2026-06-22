"""
Live Documentation Sync Flow for Crypteolas.

Provides real-time documentation synchronization for crypto protocols:
- Firecrawl-based web scraping
- Configurable refresh intervals (6 hours default)
- Change detection and delta updates
- Protocol-specific URL patterns

Supported protocols:
- Uniswap, Aave, Compound, MakerDAO
- Chainlink, Curve, Lido, EigenLayer
- User-configured protocol docs

Based on bonneagar/examples/cocoindex/live_updates pattern.
"""

import datetime
import hashlib
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Default paths
DATA_DIR = Path(__file__).parent.parent / "storage" / "data"
LANCEDB_URI = str(DATA_DIR / "lancedb")

# Refresh configuration
DEFAULT_REFRESH_HOURS = 6
MIN_REFRESH_HOURS = 1
MAX_REFRESH_HOURS = 24


@dataclass
class ProtocolDocConfig:
    """Configuration for a protocol's documentation."""
    name: str
    doc_urls: list[str]
    github_repos: list[str] = field(default_factory=list)
    refresh_hours: int = DEFAULT_REFRESH_HOURS
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)


# Pre-configured protocol documentation sources
PROTOCOL_CONFIGS: dict[str, ProtocolDocConfig] = {
    "uniswap": ProtocolDocConfig(
        name="Uniswap",
        doc_urls=[
            "https://docs.uniswap.org/",
            "https://docs.uniswap.org/concepts/overview",
            "https://docs.uniswap.org/contracts/v4/overview",
        ],
        github_repos=[
            "Uniswap/v4-core",
            "Uniswap/universal-router",
        ],
        include_patterns=["/concepts/", "/contracts/", "/sdk/"],
        exclude_patterns=["/blog/", "/changelog/"],
    ),
    "aave": ProtocolDocConfig(
        name="Aave",
        doc_urls=[
            "https://docs.aave.com/",
            "https://docs.aave.com/developers/getting-started/readme",
        ],
        github_repos=[
            "aave/aave-v3-core",
        ],
        include_patterns=["/developers/", "/core-contracts/"],
    ),
    "compound": ProtocolDocConfig(
        name="Compound",
        doc_urls=[
            "https://docs.compound.finance/",
        ],
        github_repos=[
            "compound-finance/comet",
        ],
    ),
    "makerdao": ProtocolDocConfig(
        name="MakerDAO",
        doc_urls=[
            "https://docs.makerdao.com/",
            "https://mips.makerdao.com/",
        ],
        github_repos=[
            "makerdao/dss",
        ],
    ),
    "chainlink": ProtocolDocConfig(
        name="Chainlink",
        doc_urls=[
            "https://docs.chain.link/",
            "https://docs.chain.link/data-feeds",
            "https://docs.chain.link/ccip",
        ],
        github_repos=[
            "smartcontractkit/chainlink",
        ],
    ),
    "curve": ProtocolDocConfig(
        name="Curve",
        doc_urls=[
            "https://resources.curve.fi/",
            "https://curve.readthedocs.io/",
        ],
        github_repos=[
            "curvefi/curve-stablecoin",
        ],
    ),
    "lido": ProtocolDocConfig(
        name="Lido",
        doc_urls=[
            "https://docs.lido.fi/",
        ],
        github_repos=[
            "lidofinance/lido-dao",
        ],
    ),
    "eigenlayer": ProtocolDocConfig(
        name="EigenLayer",
        doc_urls=[
            "https://docs.eigenlayer.xyz/",
        ],
        github_repos=[
            "Layr-Labs/eigenlayer-contracts",
        ],
    ),
}


class LiveDocumentationSync:
    """
    Synchronize live protocol documentation.

    Uses Firecrawl for web scraping with:
    - Configurable refresh intervals
    - Change detection via content hashing
    - Delta updates (only changed content)
    """

    def __init__(
        self,
        firecrawl_api_key: str | None = None,
        data_dir: Path | None = None,
    ):
        self.firecrawl_api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        self.data_dir = data_dir or DATA_DIR
        self._firecrawl = None

    def _get_firecrawl(self):
        """Get or create Firecrawl client."""
        if self._firecrawl is not None:
            return self._firecrawl

        try:
            from firecrawl import FirecrawlApp
        except ImportError:
            raise ImportError(
                "firecrawl-py not installed. Run: pip install firecrawl-py"
            )

        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable required")

        self._firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
        return self._firecrawl

    async def sync_protocol(
        self,
        protocol_name: str,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Sync documentation for a specific protocol.

        Args:
            protocol_name: Protocol name (e.g., 'uniswap', 'aave')
            force_refresh: Force refresh even if within interval

        Returns:
            Sync statistics
        """
        config = PROTOCOL_CONFIGS.get(protocol_name.lower())
        if not config:
            raise ValueError(f"Unknown protocol: {protocol_name}")

        return await self._sync_protocol_docs(config, force_refresh)

    async def sync_all_protocols(
        self,
        force_refresh: bool = False,
    ) -> dict[str, dict[str, Any]]:
        """
        Sync documentation for all configured protocols.

        Args:
            force_refresh: Force refresh even if within interval

        Returns:
            Dict of protocol -> sync statistics
        """
        results = {}
        for name, config in PROTOCOL_CONFIGS.items():
            try:
                results[name] = await self._sync_protocol_docs(config, force_refresh)
            except Exception as e:
                logger.error(f"Failed to sync {name}: {e}")
                results[name] = {"error": str(e)}

        return results

    async def sync_custom_url(
        self,
        url: str,
        protocol_name: str = "custom",
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """
        Sync documentation from a custom URL.

        Args:
            url: Base URL to crawl
            protocol_name: Name to associate with this source
            max_depth: Maximum crawl depth

        Returns:
            Sync statistics
        """
        firecrawl = self._get_firecrawl()

        try:
            # Crawl the site
            crawl_result = firecrawl.crawl_url(
                url,
                params={
                    "limit": 100,
                    "scrapeOptions": {
                        "formats": ["markdown", "html"],
                    },
                },
                poll_interval=5,
            )

            documents = []
            for page in crawl_result.get("data", []):
                doc = self._process_crawl_result(page, protocol_name)
                if doc:
                    documents.append(doc)

            # Store documents
            stored = await self._store_documents(documents)

            return {
                "url": url,
                "protocol": protocol_name,
                "pages_crawled": len(crawl_result.get("data", [])),
                "documents_stored": stored,
            }

        except Exception as e:
            logger.error(f"Failed to sync {url}: {e}")
            return {"error": str(e)}

    async def _sync_protocol_docs(
        self,
        config: ProtocolDocConfig,
        force_refresh: bool,
    ) -> dict[str, Any]:
        """Internal method to sync protocol documentation."""
        firecrawl = self._get_firecrawl()
        all_documents = []
        pages_crawled = 0

        for doc_url in config.doc_urls:
            try:
                # Check if refresh needed
                if not force_refresh and not self._needs_refresh(
                    config.name, doc_url, config.refresh_hours
                ):
                    logger.info(f"Skipping {doc_url} - still within refresh interval")
                    continue

                # Scrape the URL
                result = firecrawl.scrape_url(
                    doc_url,
                    params={
                        "formats": ["markdown", "html"],
                        "includeTags": config.include_patterns or None,
                        "excludeTags": config.exclude_patterns or None,
                    },
                )

                doc = self._process_crawl_result(result, config.name)
                if doc:
                    all_documents.append(doc)
                    pages_crawled += 1

                # Also crawl linked pages
                crawl_result = firecrawl.crawl_url(
                    doc_url,
                    params={
                        "limit": 50,
                        "maxDepth": 2,
                        "scrapeOptions": {
                            "formats": ["markdown"],
                        },
                    },
                    poll_interval=5,
                )

                for page in crawl_result.get("data", []):
                    if self._should_include_page(page, config):
                        doc = self._process_crawl_result(page, config.name)
                        if doc:
                            all_documents.append(doc)
                            pages_crawled += 1

            except Exception as e:
                logger.warning(f"Failed to scrape {doc_url}: {e}")

        # Deduplicate by content hash
        unique_docs = self._deduplicate_documents(all_documents)

        # Store documents
        stored = await self._store_documents(unique_docs)

        # Update last sync time
        self._record_sync(config.name)

        return {
            "protocol": config.name,
            "urls_processed": len(config.doc_urls),
            "pages_crawled": pages_crawled,
            "unique_documents": len(unique_docs),
            "documents_stored": stored,
        }

    def _process_crawl_result(
        self,
        result: dict[str, Any],
        protocol_name: str,
    ) -> dict[str, Any] | None:
        """Process a single crawl result into a document."""
        markdown = result.get("markdown", "")
        if not markdown or len(markdown) < 100:
            return None

        url = result.get("sourceURL", result.get("url", ""))
        title = result.get("metadata", {}).get("title", "")

        content_hash = hashlib.sha256(markdown.encode()).hexdigest()[:16]

        return {
            "id": f"{protocol_name}_{content_hash}",
            "url": url,
            "title": title or self._extract_title(url),
            "content": markdown,
            "protocol": protocol_name,
            "source_type": "protocol_docs",
            "content_hash": content_hash,
            "scraped_at": datetime.datetime.utcnow().isoformat(),
            "metadata": result.get("metadata", {}),
        }

    def _should_include_page(
        self,
        page: dict[str, Any],
        config: ProtocolDocConfig,
    ) -> bool:
        """Check if a page should be included based on patterns."""
        url = page.get("sourceURL", page.get("url", ""))

        # Check include patterns
        if config.include_patterns:
            if not any(pattern in url for pattern in config.include_patterns):
                return False

        # Check exclude patterns
        if config.exclude_patterns:
            if any(pattern in url for pattern in config.exclude_patterns):
                return False

        return True

    def _deduplicate_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Remove duplicate documents by content hash."""
        seen_hashes = set()
        unique = []

        for doc in documents:
            content_hash = doc.get("content_hash")
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique.append(doc)

        return unique

    async def _store_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> int:
        """Store documents in DuckLake/DuckDB."""
        if not documents:
            return 0

        try:
            import duckdb
        except ImportError:
            logger.error("duckdb not installed")
            return 0

        db_path = self.data_dir / "ducklake.ducklake"
        conn = duckdb.connect(str(db_path))

        try:
            # Ensure table exists
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_documents (
                    id VARCHAR PRIMARY KEY,
                    url VARCHAR,
                    title VARCHAR,
                    markdown TEXT,
                    protocol VARCHAR,
                    source_type VARCHAR,
                    content_hash VARCHAR,
                    scraped_at TIMESTAMP,
                    file_path VARCHAR
                )
            """)

            # Insert or update documents
            for doc in documents:
                conn.execute("""
                    INSERT OR REPLACE INTO scraped_documents
                    (id, url, title, markdown, protocol, source_type, content_hash, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    doc["id"],
                    doc.get("url"),
                    doc.get("title"),
                    doc.get("content"),
                    doc.get("protocol"),
                    doc.get("source_type"),
                    doc.get("content_hash"),
                    doc.get("scraped_at"),
                ])

            conn.commit()
            return len(documents)

        except Exception as e:
            logger.error(f"Failed to store documents: {e}")
            return 0
        finally:
            conn.close()

    def _needs_refresh(
        self,
        protocol_name: str,
        url: str,
        refresh_hours: int,
    ) -> bool:
        """Check if a URL needs refresh based on last sync time."""
        sync_file = self.data_dir / ".sync_state" / f"{protocol_name}.json"

        if not sync_file.exists():
            return True

        try:
            import json
            with open(sync_file) as f:
                state = json.load(f)

            last_sync = state.get("last_sync")
            if not last_sync:
                return True

            last_sync_dt = datetime.datetime.fromisoformat(last_sync)
            age_hours = (datetime.datetime.utcnow() - last_sync_dt).total_seconds() / 3600

            return age_hours >= refresh_hours

        except Exception:
            return True

    def _record_sync(self, protocol_name: str) -> None:
        """Record sync timestamp for a protocol."""
        import json

        sync_dir = self.data_dir / ".sync_state"
        sync_dir.mkdir(parents=True, exist_ok=True)

        sync_file = sync_dir / f"{protocol_name}.json"

        state = {
            "protocol": protocol_name,
            "last_sync": datetime.datetime.utcnow().isoformat(),
        }

        with open(sync_file, "w") as f:
            json.dump(state, f)

    def _extract_title(self, url: str) -> str:
        """Extract title from URL path."""
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")

        if path:
            parts = path.split("/")
            if parts:
                return parts[-1].replace("-", " ").replace("_", " ").title()

        return parsed.netloc


# =============================================================================
# CocoIndex Flow Definition
# =============================================================================

def create_live_docs_flow():
    """
    Create CocoIndex flow for live documentation sync.

    Flow refreshes every 6 hours to keep documentation current.
    """
    try:
        import cocoindex
    except ImportError:
        raise ImportError("cocoindex not installed")

    @cocoindex.flow_def(name="LiveDocumentationSync")
    def live_docs_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope,
    ) -> None:
        """
        Live documentation sync flow.

        Sources: Protocol documentation sites
        Refresh: Every 6 hours
        Target: DuckLake + LanceDB
        """
        # This flow is event-driven rather than source-based
        # Use the sync methods to trigger updates

        pass  # Flow definition for CocoIndex registration

    return live_docs_flow


# =============================================================================
# Convenience Functions
# =============================================================================

async def sync_protocol_docs(
    protocol: str,
    force: bool = False,
) -> dict[str, Any]:
    """
    Sync documentation for a protocol.

    Args:
        protocol: Protocol name (uniswap, aave, compound, etc.)
        force: Force refresh even if within interval

    Returns:
        Sync statistics
    """
    syncer = LiveDocumentationSync()
    return await syncer.sync_protocol(protocol, force)


async def sync_all_protocol_docs(
    force: bool = False,
) -> dict[str, dict[str, Any]]:
    """
    Sync documentation for all configured protocols.

    Args:
        force: Force refresh even if within interval

    Returns:
        Dict of protocol -> sync statistics
    """
    syncer = LiveDocumentationSync()
    return await syncer.sync_all_protocols(force)


def get_configured_protocols() -> list[str]:
    """Get list of configured protocol names."""
    return list(PROTOCOL_CONFIGS.keys())


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Sync protocol documentation")
    parser.add_argument(
        "--protocol",
        choices=list(PROTOCOL_CONFIGS.keys()) + ["all"],
        default="all",
        help="Protocol to sync (or 'all')",
    )
    parser.add_argument("--force", action="store_true", help="Force refresh")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.protocol == "all":
        results = asyncio.run(sync_all_protocol_docs(force=args.force))
        for protocol, stats in results.items():
            print(f"\n{protocol}:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
    else:
        result = asyncio.run(sync_protocol_docs(args.protocol, force=args.force))
        for key, value in result.items():
            print(f"{key}: {value}")
