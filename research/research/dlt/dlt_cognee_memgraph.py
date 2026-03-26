# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
import marimo

__generated_with = "0.17.8"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cognee x Memgraph integration

    This notebook demonstrates how to integrate
    [Cognee](https://github.com/cognee-ai/cognee) with
    [Memgraph](https://memgraph.com), a graph database platform, to automatically
    convert unstructured text into a semantically searchable knowledge graph using
    Large Language Models (LLMs).

    Cognee is an AI-powered toolkit for cognitive search and graph-based knowledge
    representation. It uses LLMs to break down natural language into structured
    concepts and relationships, storing them as graphs in Memgraph for further
    querying and visualization.

    This notebook demonstrates how to convert Hacker News threadsinto a live
    semantic knowledge graph using LLM-powered processing via Cognee and real-time
    graph storage via Memgraph.


    ## Prerequisites

    To follow along, you'll need:

    1. **Docker**: Ensure [Docker](https://www.docker.com/) is installed and running
       in the background.

    2. **Memgraph**: The easiest way to run Memgraph is using the following
       commands:

    For Linux/macOS: `curl https://install.memgraph.com | sh`

    For Windows: `iwr https://windows.memgraph.com | iex`

    This will launch Memgraph at `localhost:3000`.

    3. **Python 3.10+**: For our pipeline

    4. **OpenAI API Key**: For LLM processing

    5. **Neccessary dependencies**: To install, open your terminal and run:
    """)
    return


@app.cell
def _():
    # '%pip install cognee dlt requests python-dateutil neo4j python-dotenv' command supported automatically in marimo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Environment setup

    We'll load the environment variables used to configure the LLM and graph
    database providers. These will be pulled from a `.env` file (which you must
    create securely — don’t share API keys!). In this example, we're using OpenAI.

    Create a file named `.env` in your project root with the following content:

    ```
    # LLM Configuration
    LLM_API_KEY=sk-your-openai-api-key
    LLM_MODEL=openai/gpt-4o-mini
    LLM_PROVIDER=openai
    EMBEDDING_PROVIDER=openai
    EMBEDDING_MODEL=openai/text-embedding-3-large

    # Memgraph Configuration
    GRAPH_DATABASE_PROVIDER=memgraph
    GRAPH_DATABASE_URL=bolt://localhost:7687
    GRAPH_DATABASE_USERNAME="\"
    GRAPH_DATABASE_PASSWORD="\"

    # Hacker News API
    HN_API_BASE=https://hacker-news.firebaseio.com/v0
    ```

    ## Building the pipeline

    Let's first load our environment in notebook:
    """)
    return


@app.cell
def _():
    from dotenv import load_dotenv
    import os

    load_dotenv()
    return (load_dotenv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data extraction from HackerNews

    Our pipeline starts by extracting data from the Hacker News API:
    """)
    return


@app.cell
def _():
    import dlt
    import requests
    from typing import Iterator, Dict, Any
    from datetime import datetime
    import time

    HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

    @dlt.resource(table_name="posts", write_disposition="merge", primary_key="id")
    def get_posts_incremental(
        updated_at=dlt.sources.incremental("time", initial_value=0)
    ) -> Iterator[Dict[str, Any]]:
        """Extract posts from Hacker News API with incremental loading"""

        # Get latest stories
        top_stories_response = requests.get(f"{HN_API_BASE}/topstories.json")
        top_story_ids = top_stories_response.json()

        new_stories_response = requests.get(f"{HN_API_BASE}/newstories.json")
        new_story_ids = new_stories_response.json()

        all_story_ids = list(set(top_story_ids + new_story_ids))[:20]

        print(f"Total story IDs to check: {len(all_story_ids)}")

        for story_id in all_story_ids:
            try:
                item_response = requests.get(f"{HN_API_BASE}/item/{story_id}.json")
                if item_response.status_code == 200:
                    item = item_response.json()

                    if item and item.get('type') == 'story':
                        item_time = item.get('time', 0)
                        if item_time > updated_at.last_value:
                            # Prepare data for Cognee processing
                            item['created_at'] = datetime.fromtimestamp(item['time'])
                            item['extracted_at'] = datetime.now()
                            item['content_for_cognee'] = f"Title: {item.get('title', '')}. {item.get('text', '')}"
                        
                            print(f"Yielding post ID {item['id']} titled: {item.get('title', '')}")

                            yield item
                        else:
                            print(f"Skipping post {item.get('id')} (old)")

                time.sleep(0.1)  # Rate limiting

            except Exception as e:
                print(f"Error fetching story {story_id}: {e}")
                continue
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Cognee integration for knowledge graph generation

    Now, you may integrate Cognee to process the extracted text and build your
    knowledge graph:
    """)
    return


@app.cell
def _(load_dotenv):
    import cognee
    import asyncio
    load_dotenv()

    class CogneeMemgraphProcessor:

        def __init__(self):
            pass

        async def process_posts(self, posts_data):
            """Process posts through Cognee to build knowledge graph"""
            for post in posts_data:
                try:
                    content = post.get('content_for_cognee', '')
                    if content:
                        print(f"Adding post to Cognee: {post.get('title', '')}")  # Add post content to Cognee
                        await cognee.add(content, dataset_name='hackernews_posts')
                    metadata = {'post_id': post.get('id'), 'author': post.get('by'), 'score': post.get('score', 0), 'url': post.get('url'), 'created_at': post.get('created_at')}
                    metadata_str = '. '.join((f'{k}: {v}' for k, v in metadata.items()))
                    await cognee.add(metadata, dataset_name='hackernews_metadata')
                except Exception as e:
                    print(f"Error processing post {post.get('id')}: {e}")  # Add metadata as structured data
            print('Building knowledge graph with Cognee...')
            await cognee.cognify()
            print('Knowledge graph construction completed!')

        async def search_knowledge_graph(self, query: str):
            """Perform semantic search on the knowledge graph"""
            results = await cognee.search(query_text=query)
            return results  # Build the knowledge graph
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualize your data in Memgraph

    Now that the graph is created, we can explore it in the UI by visiting
    `http://localhost:3000/`.

    ### Explore the graph

    Use Cypher queries to explore your knowledge graph:

    ```
    -- View the entire graph structure
    MATCH p=()-[]-() RETURN p LIMIT 100;

    -- Find all entities related to "AI" or "artificial intelligence"
    MATCH (n)
    WHERE n.name CONTAINS "AI" OR n.name CONTAINS "artificial intelligence"
    RETURN n;

    -- Discover relationships between programming languages
    MATCH (lang1)-[r]-(lang2)
    WHERE lang1.type = "programming_language" AND lang2.type = "programming_language"
    RETURN lang1, r, lang2;

    -- Find the most connected entities (high centrality)
    MATCH (n)-[r]-()
    RETURN n.name, count(r) as connections
    ORDER BY connections DESC
    LIMIT 10;
    ```


    ## Conclusion

    This integration demonstrates how fast-moving online discussions, like those on Hacker News, can be transformed into queryable knowledge graphs using Cognee and Memgraph.

    By combining the Hacker News API with AI-based semantic understanding and high-performance graph database technology, you’ve created a system that can:

    - **Automatically understand** the semantic content of discussions
    - **Discover hidden relationships** between concepts and entities
    - **Enable smart search** that goes beyond keyword matching
    - **Provide visual insights** through graph exploration
    - **Scale to handle** large volumes of real-time data

    The future of knowledge management lies in systems that can think, reason, and discover insights the way humans. With this integration, you’re one step closer to that reality!
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
