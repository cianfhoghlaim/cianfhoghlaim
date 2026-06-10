# KCG_SUMMARY: eScriptorium — Historical Document Transcription Platform

## What It Is
eScriptorium is a full Django-based web application developed under the Scripta, RESILIENCE, and Biblissima+ EU research projects for transcribing, annotating, translating, and publishing historical documents. It integrates the Kraken OCR engine for automatic text recognition and provides a collaborative platform for humanities researchers working with manuscript collections.

## Why This Matters for Kings' College Galway
Ireland holds one of the richest manuscript traditions in Europe — from the Book of Kells to the National Folklore Collection's 740,000+ pages of Schools' Collection material. eScriptorium's architecture demonstrates how to build a production-grade platform for digitising and transcribing historical Irish-language manuscripts. For Kings' College Galway's **teanga** curriculum, this provides the pattern for a student-facing tool where learners could collaboratively transcribe and annotate historical Irish texts, connecting them directly with Ireland's literary heritage while building practical digital humanities skills.

## Key Patterns Preserved
- `README.md` — Project overview, technology stack (Django, Postgres, Elasticsearch, Redis, Celery, Kraken), funding sources, and steering committee
- `INSTALL-ubuntu.md` — Complete Ubuntu 18.04/20.04 installation guide covering system dependencies, database setup, and development server configuration
- `app/apps/imports/README.md` — Import module documentation

## Source Files
Full source code was removed on 2026-06-06. The original repository is available at gitlab.com/scripta/escriptorium. This skeleton preserves documentation to inform platform architecture decisions for the Kings' College Galway transcription stack.

## What Was Removed
- Django application source code (Python, HTML templates, CSS, JavaScript)
- Kraken OCR model files and configuration
- Docker and deployment configurations
- Database migration files
- Front-end static assets and build tooling
- Test suites and CI/CD configuration
- Nginx and uWSGI configuration
- Celery task definitions
- Elasticsearch index mappings
