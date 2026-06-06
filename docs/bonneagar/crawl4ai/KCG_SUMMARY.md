# Crawl4AI — KCG Summary

## What It Is
A Firecrawl LLMs.txt Generator — a Python script that crawls any website using the Firecrawl API's map and scrape endpoints, generates AI-powered titles and descriptions via OpenAI's GPT-4o-mini, and produces standardized `llms.txt` and `llms-full.txt` files for making website content accessible to Large Language Models.

## Why This Matters for Kings' College Galway
The llms.txt generation pattern is how we structure website content for our AI curriculum agents. When our Dagster pipelines ingest educational websites (examinations.ie, curriculumonline.ie, ncca.ie), the llms.txt format provides a machine-readable index that our RAG systems use for context retrieval. The parallel-processing Firecrawl pattern is directly used in our `sruth-browser` automation client for scaling content extraction across multiple educational domains. This tool bridges the gap between web scraping and AI-ready content packaging — essential for our Celtic language curriculum corpus pipeline where we need to transform scattered web content into structured, LLM-optimized formats.

## Key Patterns Preserved
- `firecrawl/README.md` — Complete tool documentation including installation, usage, configuration, and API integration patterns

## Source Files
Full source removed (2026-06-06), available at the original GitHub repository.

## What Was Removed
Python source files (llms_txt_generator.py), requirements.txt, package configuration, and all non-documentation files.
