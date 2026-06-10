# KCG_SUMMARY: Genizah Search — Cairo Genizah AI Semantic Search Application

## What It Is
This is the core code for the Cairo Genizah AI Project (cairogenizah.ai), the only web application supporting true semantic search of the Cairo Genizah — a collection of over 400,000 Jewish manuscript fragments discovered in the Ben Ezra Synagogue in Cairo. The stack combines a React front-end with a Python back-end, using Elasticsearch for search and Neo4j for graph database relationships. It uses the Mirador IIIF viewer for manuscript image display.

## Why This Matters for Kings' College Galway
While focused on Jewish manuscripts, the Genizah Search application demonstrates the complete stack for building a manuscript exploration platform — semantic search, IIIF image viewing, and graph-based relationship exploration. For Kings' College Galway's **teanga** platform, this provides the architectural blueprint for building a similar exploration interface for Irish manuscript collections (Dúchas, ISOS, Irish Script on Screen). The semantic search patterns are directly transferable to Irish-language text corpora, and the React+Python architecture patterns inform the school's own full-stack development curriculum.

## Key Patterns Preserved
- `readme.md` — Project overview, technology stack (React, Python, Elasticsearch, Neo4j, Mirador IIIF viewer)

## Source Files
Full source code was removed on 2026-06-06. The original project is at cairogenizah.ai. This skeleton preserves the architectural description and tech stack decisions.

## What Was Removed
- React front-end application source code
- Python back-end API source code
- Elasticsearch index configurations and mappings
- Neo4j graph database schema and queries
- Docker and deployment configurations
- IIIF manifest generation code
- Test suites
