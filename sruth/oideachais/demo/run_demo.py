#!/usr/bin/env python3
"""
Oideachas - Celtic Education Curriculum Processing Demo.

Demonstrates the complete flow:
1. DLT data ingestion from curriculum sources (NCCA, SEC, curriculumonline)
2. Curriculum document processing and embedding
3. Semantic search across educational content
4. BAML schema extraction for structured data
5. Knowledge graph queries (geospatial, curriculum relationships)
6. Dagster asset orchestration
7. Observability integration (Datadog, MLflow, Langfuse)

Usage:
    cd sruth/oideachais
    python demo/run_demo.py
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# This demo uses mock data and requires no external dependencies
# All demonstrations are offline with pre-populated example data


# ============================================================================
# MOCK DATA FOR OFFLINE DEMO
# ============================================================================

MOCK_CURRICULUM_DATA = {
    "junior_cycle_irish": {
        "subject": "Irish",
        "level": "Junior Cycle",
        "learning_outcomes": [
            "Communicate in Irish with confidence and fluency",
            "Understand and respond to spoken Irish",
            "Read and comprehend Irish texts independently",
            "Write in Irish for various purposes and audiences",
        ],
        "strands": ["Communicative Competence", "Language Awareness", "Cultural Awareness"],
    },
    "senior_cycle_mathematics": {
        "subject": "Mathematics",
        "level": "Senior Cycle",
        "learning_outcomes": [
            "Apply mathematical concepts to real-world problems",
            "Use algebraic and calculus techniques",
            "Analyze statistical data and probability",
        ],
        "strands": ["Statistics and Probability", "Geometry and Trigonometry", "Functions", "Calculus"],
    },
}

MOCK_SEARCH_RESULTS = [
    {
        "title": "Junior Cycle Irish - Communication Skills",
        "content_type": "curriculum",
        "subject": "Irish",
        "level": "Junior Cycle",
        "score": 0.92,
        "snippet": "Students develop the ability to communicate effectively in Irish...",
    },
    {
        "title": "Irish Language Curriculum Specification",
        "content_type": "curriculum",
        "subject": "Irish",
        "level": "Junior Cycle",
        "score": 0.88,
        "snippet": "This curriculum specification for Junior Cycle Irish...",
    },
]

MOCK_GEOSPATIAL_DATA = {
    "ireland": {
        "total_schools": 4012,
        "regions": {
            "Leinster": 1650,
            "Munster": 1120,
            "Connacht": 780,
            "Ulster": 462,
        },
    },
    "wales": {
        "total_schools": 1485,
        "regions": {
            "North Wales": 620,
            "Mid Wales": 340,
            "South Wales": 525,
        },
    },
}

MOCK_CELTIC_LANGUAGES = [
    {
        "language": "Irish",
        "native_name": "Gaeilge",
        "speakers": 1700000,
        "nations": ["Ireland"],
        "resources": 4500,
    },
    {
        "language": "Welsh",
        "native_name": "Cymraeg",
        "speakers": 880000,
        "nations": ["Wales"],
        "resources": 3200,
    },
    {
        "language": "Scottish Gaelic",
        "native_name": "Gàidhlig",
        "speakers": 60000,
        "nations": ["Scotland"],
        "resources": 1800,
    },
    {
        "language": "Breton",
        "native_name": "Brezhoneg",
        "speakers": 200000,
        "nations": ["France (Brittany)"],
        "resources": 1200,
    },
]


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

async def demo_dlt_sources():
    """Demonstrate DLT data sources."""
    print("\n" + "=" * 80)
    print("1. DLT DATA SOURCES DEMO")
    print("=" * 80)

    print("\n--- Available DLT Sources ---")
    sources = [
        ("Ireland", 8, ["NCCA", "SEC", "Curriculumonline", "Dept of Education"]),
        ("UK", 12, ["GOV.UK", "Education Scotland", "Welsh Government", "NI Direct"]),
        ("Celtic", 6, ["Dúchas.ie", "Tearma.ie", "Gaelic Portraits", "Welsh Books"]),
        ("Geospatial", 4, ["CSO Ireland", "ONS UK", "Boundaries", "School Locations"]),
    ]

    print(f"{'Nation':<12} {'Sources':<8} {'Examples'}")
    print("-" * 80)
    for nation, count, examples in sources:
        print(f"{nation:<12} {count:<8} {', '.join(examples[:2])}")

    print("\n--- Sample DLT Pipeline Configuration ---")
    print("""
# Example: NCCA Curriculum Pipeline
import dlt
from sruth.oideachais.dlt_sources.ireland import ncca_source

pipeline = dlt.pipeline(
    pipeline_name="ncca_curriculum",
    destination="duckdb",
    dataset_name="irish_education",
)

# Run partitioned crawl
info = pipeline.run(ncca_source(
    cycle="junior_cycle",
    subject="irish",
    language="en",
))

print(f"Loaded {info.loads_count} documents")
    """)


async def demo_document_processing():
    """Demonstrate curriculum document processing."""
    print("\n" + "=" * 80)
    print("2. CURRICULUM DOCUMENT PROCESSING DEMO")
    print("=" * 80)

    print("\n--- Processing Pipeline ---")
    steps = [
        ("1. Ingestion", "DLT REST API / Firecrawl scraping"),
        ("2. Parsing", "PDF extraction, HTML cleaning"),
        ("3. Chunking", "Semantic splitting by learning outcomes"),
        ("4. Embedding", "BGE-M3 batch embeddings (min 100)"),
        ("5. Storage", "LanceDB vectors + DuckDB metadata"),
    ]

    for step, description in steps:
        print(f"  {step:<15} {description}")

    print("\n--- Sample Curriculum Document ---")
    for key, data in MOCK_CURRICULUM_DATA.items():
        print(f"\n  Subject: {data['subject']} ({data['level']})")
        print(f"  Strands: {', '.join(data['strands'])}")
        print(f"  Learning Outcomes:")
        for outcome in data['learning_outcomes'][:2]:
            print(f"    - {outcome}")


async def demo_semantic_search():
    """Demonstrate semantic search capabilities."""
    print("\n" + "=" * 80)
    print("3. SEMANTIC SEARCH DEMO")
    print("=" * 80)

    query = "How to teach Irish language communication skills"

    print(f"\n--- Query: '{query}' ---")
    print("\n--- Search Results (Hybrid Vector + Keyword) ---")

    for i, result in enumerate(MOCK_SEARCH_RESULTS, 1):
        print(f"\n  Result {i}:")
        print(f"    Title: {result['title']}")
        print(f"    Subject: {result['subject']}")
        print(f"    Level: {result['level']}")
        print(f"    Score: {result['score']:.3f}")
        print(f"    Snippet: {result['snippet'][:80]}...")

    print("\n--- Search Configuration ---")
    print("""
# Example: Hybrid Search with LanceDB
from lancedb import connect

db = connect("./storage/data/lancedb")
table = db.open_table("curriculum_embeddings")

# Hybrid search (vector + keyword)
results = table.search(query).limit(5).to_list()

# Rerank with Jina API (15-20% precision boost)
reranked = rerank_results(results, query, provider="jina")
    """)


async def demo_baml_extraction():
    """Demonstrate BAML schema extraction."""
    print("\n" + "=" * 80)
    print("4. BAML SCHEMA EXTRACTION DEMO")
    print("=" * 80)

    print("\n--- Type-Safe LLM Extraction ---")
    print("""
# BAML Schema Definition (baml_src/curriculum.baml)

enum Subject {
    Irish
    Mathematics
    English
    History
    Geography
}

enum Level {
    JuniorCycle
    SeniorCycle
    Primary
}

class LearningOutcome {
    name string
    description string
    strand string
    level Level
}

class CurriculumDocument {
    subject Subject
    level Level
    learning_outcomes LearningOutcome[]
    assessment_methods string[]
}

# Extract structured data from curriculum text
extract CurriculumDocument from document_text
    """)

    print("\n--- Example Extraction ---")
    mock_extraction = {
        "subject": "Irish",
        "level": "JuniorCycle",
        "learning_outcomes": [
            {"name": "Communication", "strand": "Communicative Competence"},
            {"name": "Cultural Awareness", "strand": "Cultural Awareness"},
        ],
        "assessment_methods": ["Classroom-Based Assessment", "Final Examination"],
    }
    print(json.dumps(mock_extraction, indent=2))


async def demo_knowledge_graph():
    """Demonstrate knowledge graph capabilities."""
    print("\n" + "=" * 80)
    print("5. KNOWLEDGE GRAPH DEMO")
    print("=" * 80)

    print("\n--- Geospatial Query Example ---")
    print("\nQuery: Schools in Munster region with Irish-medium education")
    print("\n--- Cypher Query ---")
    print("""
MATCH (s:School)-[LOCATED_IN]->(r:Region {name: 'Munster'})
WHERE s.language_of_instruction = 'Irish'
RETURN s.name, s.enrollment, s.address
ORDER BY s.enrollment DESC
LIMIT 10
    """)

    print("\n--- Sample Geospatial Data ---")
    for nation, data in MOCK_GEOSPATIAL_DATA.items():
        print(f"\n  {nation.capitalize()}:")
        print(f"    Total Schools: {data['total_schools']:,}")
        print(f"    Regions:")
        for region, count in data['regions'].items():
            print(f"      - {region}: {count:,} schools")

    print("\n--- Curriculum Relationship Graph ---")
    print("""
Nodes:
  - Subject (Irish, Mathematics, History)
  - Strand (Communicative Competence, Statistics)
  - LearningOutcome
  - AssessmentMethod

Relationships:
  - (Subject)-[HAS_STRAND]->(Strand)
  - (Strand)-[CONTAINS_OUTCOME]->(LearningOutcome)
  - (LearningOutcome)-[ASSESSED_BY]->(AssessmentMethod)
    """)


async def demo_dagster_assets():
    """Demonstrate Dagster asset orchestration."""
    print("\n" + "=" * 80)
    print("6. DAGSTER ASSETS DEMO")
    print("=" * 80)

    print("\n--- Asset Groups ---")
    asset_groups = [
        ("Ireland Education", 8, ["ncca_curriculum", "sec_exams", "school_statistics"]),
        ("UK Education", 12, ["gov_uk_curriculum", "ofqual_data", "school_performance"]),
        ("Celtic Language", 6, ["duchas_folklore", "tearma_terminology", "gaelic_resources"]),
        ("Geospatial", 4, ["irish_boundaries", "uk_boundaries", "school_locations"]),
        ("Embeddings", 3, ["curriculum_vectors", "exam_vectors", "folklore_vectors"]),
        ("Search", 2, ["curriculum_search_index", "multilingual_search_index"]),
    ]

    print(f"{'Group':<25} {'Assets':<8} {'Examples'}")
    print("-" * 80)
    for group, count, examples in asset_groups:
        print(f"{group:<25} {count:<8} {', '.join(examples[:2])}")

    print("\n--- Sample Asset Definition ---")
    print("""
@asset(
    group_name="ireland_education",
    metadata={"source": "NCCA", "nation": "ireland"},
)
def junior_cycle_irish_curriculum(context) -> pd.DataFrame:
    '''Extract and process Junior Cycle Irish curriculum from NCCA.'''
    source = ncca_source(
        cycle="junior_cycle",
        subject="irish",
        language="en",
    )

    # Run DLT pipeline
    pipeline = dlt.pipeline(destination="duckdb")
    info = pipeline.run(source)

    # Return as DataFrame for downstream assets
    return info.df
    """)


async def demo_celtic_languages():
    """Demonstrate Celtic language processing."""
    print("\n" + "=" * 80)
    print("7. CELTIC LANGUAGE PROCESSING DEMO")
    print("=" * 80)

    print("\n--- Supported Celtic Languages ---")
    print(f"{'Language':<20} {'Native':<15} {'Speakers':<12} {'Resources':<10}")
    print("-" * 80)
    for lang in MOCK_CELTIC_LANGUAGES:
        print(f"{lang['language']:<20} {lang['native_name']:<15} {lang['speakers']:<12,} {lang['resources']:<10,}")

    print("\n--- Language-Specific Features ---")
    print("""
Irish (Gaeilge):
  - Dialect support: Connacht, Munster, Ulster
  - Models: UCCIX-Llama2-13B-Instruct, GaBERT
  - NCCA curriculum + SEC exam papers

Welsh (Cymraeg):
  - Curriculum: Curriculum for Wales
  - Corpora: Welsh Books Council, Geiriadur Prifysgol Cymru
  - Models: Welsh variants of BERT, T5

Scottish Gaelic (Gàidhlig):
  - Sources: Gaelic Portraits, Bòrd na Gàidhlig
  - Curriculum: Scottish Government Education Scotland
  - Dialects: Mainland, Island

Breton (Brezhoneg):
  - Sources: Ofis Publik ar Brezhoneg
  - Corpora: Dictionnaire de Breton, Divi Kervella
    """)


async def demo_observability():
    """Demonstrate observability integration."""
    print("\n" + "=" * 80)
    print("8. OBSERVABILITY STACK DEMO")
    print("=" * 80)

    print("\n--- Integrated Observability Tools ---")
    tools = [
        ("Datadog APM", "Distributed tracing", "API latency, error rates"),
        ("Datadog LLMObs", "LLM monitoring", "Token usage, costs, model performance"),
        ("MLflow", "Experiment tracking", "Embedding metrics, model comparisons"),
        ("Langfuse", "LLM cost tracking", "Per-query costs, token consumption"),
        ("Ragas", "RAG evaluation", "Faithfulness, answer relevancy"),
        ("Kafka", "Event streaming", "Real-time data pipeline events"),
    ]

    print(f"{'Tool':<20} {'Purpose':<25} {'Metrics'}")
    print("-" * 80)
    for tool, purpose, metrics in tools:
        print(f"{tool:<20} {purpose:<25} {metrics}")

    print("\n--- Example: Datadog LLMObs Span ---")
    print("""
from observability import GeminiLLMSpan

with GeminiLLMSpan("gemini-2.0-flash", query) as span:
    response = await llm.generate(query)

    span.set_response(
        response=response.content,
        input_tokens=150,
        output_tokens=300,
        metadata={"domain": "curriculum", "nation": "ireland"}
    )
    """)


async def demo_multilingual_search():
    """Demonstrate multilingual search across Celtic languages."""
    print("\n" + "=" * 80)
    print("9. MULTILINGUAL SEARCH DEMO")
    print("=" * 80)

    queries = [
        ("English", "Irish language learning outcomes"),
        ("Irish", "Toradh foghlama don Ghaeilge"),
        ("Welsh", "Canlyniadau dysgu Gaeleg yng Nghymru"),
    ]

    print("\n--- Cross-Language Semantic Search ---")
    print("Query: 'learning outcomes for language education'")
    print("\n--- Results by Language ---")

    for lang, query in queries:
        print(f"\n  {lang}: {query}")
        print(f"    Mode: BGE-M3 multilingual embeddings")
        print(f"    Results: Found 5 relevant documents")

    print("\n--- Translation Pipeline ---")
    print("""
# CocoIndex Translation Flow
from cocoindex_flows import curriculum_translation

# Translate curriculum documents
translated = curriculum_translation(
    documents=["junior_cycle_irish.pdf"],
    source_lang="en",
    target_lang="ga",
    batch_size=100,  # Mandatory minimum
)

# Store bilingual versions
lancedb_table.add(translated)
    """)


async def demo_api_endpoints():
    """Show available API endpoints."""
    print("\n" + "=" * 80)
    print("10. API ENDPOINTS OVERVIEW")
    print("=" * 80)

    endpoints = [
        ("GET /health", "Health check", None),
        ("GET /curriculum/search", "Semantic search", [("query", "string"), ("limit", "int")]),
        ("GET /curriculum/:nation/:subject", "Get curriculum by subject", None),
        ("POST /curriculum/embed", "Embed document", [("text", "string"), ("subject", "string")]),
        ("GET /geospatial/schools", "Query schools by location", [("region", "string"), ("radius", "float")]),
        ("GET /celtic/languages", "List Celtic languages", None),
        ("POST /celtic/translate", "Translate text", [("text", "string"), ("source", "lang"), ("target", "lang")]),
        ("GET /knowledge/graph/query", "Cypher graph query", [("query", "cypher")]),
    ]

    print(f"{'Endpoint':<35} {'Description':<30} {'Parameters'}")
    print("-" * 80)
    for endpoint, description, params in endpoints:
        param_str = ", ".join([f"{k}={v}" for k, v in params]) if params else "-"
        print(f"{endpoint:<35} {description:<30} {param_str}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("OIDEACHAS - CELTIC EDUCATION CURRICULUM PROCESSING")
    print("Unified Platform for Irish, UK, and Celtic Language Education")
    print("=" * 80)
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Demo Mode: Offline (using mock data)")

    try:
        await demo_dlt_sources()
        await demo_document_processing()
        await demo_semantic_search()
        await demo_baml_extraction()
        await demo_knowledge_graph()
        await demo_dagster_assets()
        await demo_celtic_languages()
        await demo_observability()
        await demo_multilingual_search()
        await demo_api_endpoints()

        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)

        print("\n--- Next Steps ---")
        print("\nTo run the full platform:")
        print("  cd sruth/oideachais")
        print("  uv sync")
        print("  dagster dev -m dagster_defs.definitions  # Start Dagster UI")
        print("  uvicorn api.main:app --reload             # Start FastAPI")
        print("\nTo run data pipelines:")
        print("  python -m dlt_sources.ireland.ncca")
        print("  python -m dlt_sources.uk.gov_uk")
        print("  python -m dlt_sources.celtic.duchas")
        print("\nTo create embeddings:")
        print("  python -m cocoindex_flows.curriculum_embedding")
        print("  python -m cocoindex_flows.geospatial_indexing")
        print("\nTo query with agents:")
        print("  python -m agents.adk.root_agent")
        print("\nFor observability:")
        print("  # Configure .env.local with DATADOG, MLFLOW, LANGFUSE credentials")
        print("  # Events are automatically tracked")

    except Exception as e:
        print(f"\n[!] Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
