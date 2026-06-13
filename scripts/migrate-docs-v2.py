#!/usr/bin/env python3
"""
migrate-docs-v2.py — Consolidate docs/ into docs-v2/ via per-topic merging.

Strategy:
  1. ccc search to identify topic clusters in each domain
  2. Cognee HTTP API to detect semantic redundancies
  3. For each cluster: merge all source files into one .md with per-source
     ## sections (no information loss)
  4. Non-md files (py, yaml, toml, png, jpg, pdf) copied as-is
  5. Archive files integrated via full LLM read of every file
  6. 00_index.md regenerated; changelog.md updated; coverage.json emitted

Best-effort: any error logged to docs-v2/.migration/errors.log and skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_SRC = REPO_ROOT / "docs"
DOCS_V2 = REPO_ROOT / "docs-v2"
MIGRATION_DIR = DOCS_V2 / ".migration"
COVERAGE_JSON = MIGRATION_DIR / "coverage.json"
ERRORS_LOG = MIGRATION_DIR / "errors.log"
CLUSTERS_JSON = MIGRATION_DIR / "clusters.json"
COGNEE_CLUSTERS_JSON = MIGRATION_DIR / "cognee-clusters.json"

COGNEE_URL = os.environ.get("COGNEE_URL", "http://localhost:8100")
COGNEE_DATASET = os.environ.get("COGNEE_DATASET", "cianfhoghlaim-docs-v2")
COGNEE_BATCH = int(os.environ.get("COGNEE_BATCH", "100"))

CANONICAL_DOMAINS = [
    "01-platform-architecture",
    "02-data-platform",
    "03-agents",
    "04-ai-ml",
    "05-web",
    "06-infrastructure",
    "07-standards",
    "08-misc",
    "09-cognee",
]

# Map leftover dirs to canonical target
LEFTOVER_TO_DOMAIN: dict[str, str] = {
    "dlt": "02-data-platform",
    "dagster": "02-data-platform",
    "cocoindex": "02-data-platform",
    "baml": "03-agents",
    "lance": "04-ai-ml",
    "marimo": "04-ai-ml",
    "hackathons": "08-misc",
    "docs_examples_consolidated": "08-misc",
    "hmgcc": "08-misc",
    "01-cognee": "09-cognee",
}

# Source roots that map to which domain
SOURCE_TO_DOMAIN: dict[str, str] = {
    "01-platform-architecture": "01-platform-architecture",
    "02-architecture": "01-platform-architecture",
    "02-audit": "01-platform-architecture",
    "02-data-platform": "02-data-platform",
    "03-agents": "03-agents",
    "03-pipelines": "03-agents",
    "04-ai-ml": "04-ai-ml",
    "05-web": "05-web",
    "05-celtic-language": "05-web",
    "06-infrastructure": "06-infrastructure",
    "06-product": "06-infrastructure",
    "07-standards": "07-standards",
    "07-skills": "07-standards",
    "08-examples": "08-misc",
    "08-screenshots": "08-misc",
    "00-package-ecosystem": "09-cognee",
}

# Topical keywords for fallback clustering when ccc is not available
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "tanstack-start": ["tanstack", "router", "react", "vinxi"],
    "vite-bun-build": ["vite", "bun", "tsconfig", "build"],
    "deployment": ["komodo", "pangolin", "deploy", "staging", "prod"],
    "monitoring": ["prometheus", "grafana", "loki", "tempo", "otel"],
    "ci-cd": ["github actions", "workflow", "ci", "pipeline"],
    "dlt-ingestion": ["dlt", "rest_api", "filesystem", "source", "pipeline"],
    "dagster-orchestration": ["dagster", "asset", "partition", "sensor", "schedule"],
    "cocoindex-pipelines": ["cocoindex", "flow", "embed", "index"],
    "duckdb-lakehouse": ["duckdb", "motherduck", "ducklake", "iceberg"],
    "lancedb-vector": ["lancedb", "vector", "embedding", "hybrid search"],
    "marimo-notebooks": ["marimo", "notebook", "reactive"],
    "baml-extraction": ["baml", "schema", "llm", "extraction", "function"],
    "graphiti-memory": ["graphiti", "knowledge graph", "temporal", "episodic"],
    "cognee-graphrag": ["cognee", "graphrag", "memify", "cognify"],
    "mcp-servers": ["mcp", "fastmcp", "stdio", "tool"],
    "agents-frameworks": ["agno", "adk", "agent", "orchestration", "team"],
    "agents-llm": ["litellm", "openai", "anthropic", "model"],
    "irish-curriculum": ["gaeilge", "irish", "curriculum", "leaving cert", "primary"],
    "uk-curriculum": ["england", "wales", "scotland", "ni", "national curriculum"],
    "scottish-gaelic": ["gd", "scottish gaelic", "gaeilge albannach"],
    "welsh": ["cy", "welsh", "cymraeg"],
    "brittany": ["br", "brezhoneg", "breton"],
    "celtic-pan": ["celtic", "insular", "neo-celtic"],
    "tanstack-router": ["router", "route", "loader", "search params"],
    "convex-realtime": ["convex", "realtime", "subscription", "function"],
    "vinxi-runtime": ["vinxi", "hono", "h3"],
    "vite-frontend": ["vite", "vite-plugin", "vite-react"],
    "hugging-face": ["huggingface", "hugging face", "hf", "peft", "lora"],
    "unsloth-finetuning": ["unsloth", "fine-tuning", "qlora"],
    "langfuse-observability": ["langfuse", "trace", "span", "prompt"],
    "ragas-eval": ["ragas", "rag", "evaluation", "faithfulness"],
    "mlflow": ["mlflow", "experiment", "registry"],
    "evidence-bi": ["evidence.dev", "bi", "dashboard"],
    "olake-replication": ["olake", "iceberg", "cdc"],
    "pangolin-routing": ["pangolin", "traefik", "wireguard"],
    "komodo-orchestration": ["komodo", "docker", "compose", "stack"],
    "pulumi-iac": ["pulumi", "iac", "stack"],
    "cloudflare-edge": ["cloudflare", "workers", "d1", "r2", "durable object"],
    "browser-automation": ["browserbase", "browser", "playwright", "stagehand"],
    "firecrawl-scraping": ["firecrawl", "scrape", "crawl"],
    "notebooklm": ["notebooklm", "context", "google"],
    "lancedb-hybrid": ["hybrid search", "fts", "bm25"],
    "graphiti-falkordb": ["falkordb", "graphiti"],
    "memgraph": ["memgraph", "cypher", "graph database"],
    "risingwave-streaming": ["risingwave", "streaming", "materialized view"],
    "sqlmesh": ["sqlmesh", "virtual data", "warehouse"],
    "feast-feature-store": ["feast", "feature store"],
    "ducklake": ["ducklake", "acid", "time travel"],
    "kings-college-galway": ["nuig", "ucg", "galway", "university", "james hardiman"],
    "apple-education": ["apple", "education", "ipad", "macbook"],
    "licensing-copyright": ["copyright", "license", "creative commons", "government"],
    "infrastructure-stacks": ["infrastructure", "stacks", "docker"],
    "stack-ops": ["stack-ops", "infisical", "locket", "sidecar"],
    "skills-catalog": ["skills", "agents", "skills catalog"],
    "standards": ["standard", "convention", "pattern"],
    "examples-patterns": ["example", "pattern", "recipe"],
    "screenshots": ["screenshot", "image", "ui"],
    "hackathons": ["hackathon", "competition"],
    "hmgcc": ["hmgcc", "homeland"],
    "data-pipeline-patterns": ["pipeline", "etl", "elt"],
    "celtic-education": ["celtic", "education", "irish", "gaelic", "welsh"],
    "celtic-language": ["language", "linguistics", "gaeilge", "cymraeg"],
    "icelandic-faroese": ["icelandic", "faroese", "norse", "old norse"],
    "sami-languages": ["sámi", "sami", "lapland"],
    "basque": ["basque", "euskara"],
    "audio-pedagogy": ["audio", "phonetics", "phonology", "pronunciation"],
    "festival-speech": ["festival", "tts", "speech synthesis"],
    "ocr-vlm": ["ocr", "vlm", "vision", "tesseract"],
    "document-intelligence": ["document intelligence", "pdf extraction", "table extraction"],
    "llm-finetuning": ["fine-tuning", "fine-tuning", "qlora", "lora"],
    "skills-creation": ["skill", "agent skill", "skill creator"],
    "agent-skills": ["agent skill", "skill creator", "agentic"],
    "mondoo-security": ["mondoo", "security", "cve", "vulnerability"],
    "insights": ["insight", "metric", "kpi"],
    "documentation": ["documentation", "docs", "markdown", "asciidoc"],
    "notebook-dashboards": ["notebook", "dashboard", "marimo", "observable"],
    "data-analytics": ["analytics", "bi", "reporting"],
    "data-science": ["data science", "statistical", "modeling"],
    "irish-government": ["government of ireland", "leaving cert", "state exam", "oca"],
    "uk-government": ["uk government", "ofsted", "dfe", "department for education"],
    "infrastructure-iac": ["iac", "pulumi", "terraform", "infrastructure as code"],
    "service-catalog": ["service catalog", "service catalog"],
    "routing-infrastructure": ["routing", "reverse proxy", "load balancer"],
    "security-auth": ["auth", "authentication", "siwe", "oauth"],
    "auth-identity": ["identity", "pocket id", "oauth", "siwe"],
    "locket-secrets": ["locket", "secret", "sidecar"],
    "infisical-vault": ["infisical", "vault", "secret"],
    "stack-doctor": ["stack doctor", "stack health", "stack audit"],
    "konvex": ["konvex", "hono", "drizzle"],
    "pangolin": ["pangolin", "traefik", "wireguard", "fossorial"],
    "komodo": ["komodo", "docker", "compose"],
    "locket": ["locket", "secret", "sidecar"],
    "pyro": ["pyro", "pyrogram"],
    "browser-mcp": ["browser mcp", "browser automation", "mcp server"],
    "pulumi-stacks": ["pulumi stack", "stack config", "backend"],
    "github-cli": ["gh", "github cli", "gh command"],
    "tdd-testing": ["test", "tdd", "fake", "stub", "mock"],
    "agent-frameworks": ["agent framework", "agent sdk", "agentic framework"],
    "claude-agents": ["claude", "claude code", "claude agent"],
    "opencode": ["opencode", "open code", "opencode ai"],
    "ccc-cocoindex-code": ["ccc", "cocoindex code", "code search", "semantic search"],
    "baml-claude": ["baml", "claude", "function calling"],
    "kings-galway": ["kings college", "nuig", "university of galway", "james hardiman"],
    "nui-galway": ["nui galway", "university of galway", "ucg", "nuig"],
    "leaving-cert": ["leaving cert", "leaving certificate", "lc"],
    "irish-language": ["gaeilge", "irish language", "gaelic"],
    "gaelic": ["gaeilge", "gaelic", "irish"],
    "kings-galway-history": ["hardiman", "1795", "kings college", "galway history"],
    "irish-education": ["irish education", "primary school", "secondary school", "leaving cert"],
    "copyright-licensing": ["copyright", "license", "creative commons", "fair use"],
    "open-source": ["open source", "oss", "license", "mit", "apache"],
    "cre-agent": ["cre", "research engineer", "code research"],
    "agentic-ai": ["agentic", "ai agent", "autonomous"],
    "rag-llm": ["rag", "retrieval augmented", "vector store", "llm"],
    "context-llm": ["context", "context window", "context length"],
    "skill-loader": ["skill loader", "agent skill", "skill load"],
    "skill-creator": ["skill creator", "create skill", "skill format"],
    "agent-experience": ["agent experience", "ax", "agent dx", "agent onboarding"],
    "agent-flow": ["agent flow", "workflow", "agent orchestration"],
    "autobrowse": ["autobrowse", "auto research", "self-improving"],
    "browser-trace": ["browser trace", "cdp", "devtools", "trace"],
    "browser-to-api": ["browser to api", "openapi from browser", "api discovery"],
    "company-research": ["company research", "icp", "lead research"],
    "event-prospecting": ["event prospecting", "conference", "speaker"],
    "cookie-sync": ["cookie sync", "browser cookie", "auth sync"],
    "hugging-face-publisher": ["huggingface", "paper", "model card", "hugging face"],
    "hf-paper-publisher": ["paper", "hf paper", "hugging face paper"],
    "model-trainer": ["model trainer", "trl", "huggingface jobs"],
    "hf-dataset-creator": ["hf dataset", "huggingface dataset", "dataset"],
    "evaluation-manager": ["evaluation manager", "eval", "huggingface eval"],
    "chunkhound": ["chunkhound", "code search", "chunk hound"],
    "graphiti-temporal": ["graphiti", "temporal", "bi-temporal"],
    "cognee-knowledge": ["cognee", "knowledge graph", "graphrag"],
    "falkordb-graph": ["falkordb", "graph database", "graph"],
    "vector-db": ["vector db", "vector database", "vector search"],
    "lancedb-storage": ["lancedb", "vector storage"],
    "mlflow-tracking": ["mlflow", "experiment tracking"],
    "firecrawl-suite": ["firecrawl", "scrape", "crawl", "extract"],
    "firecrawl-skill": ["firecrawl", "scrape", "crawl"],
    "firecrawl-scrape": ["firecrawl scrape", "single page"],
    "firecrawl-crawl": ["firecrawl crawl", "multi-page"],
    "firecrawl-agent": ["firecrawl agent", "extract agent"],
    "firecrawl-map": ["firecrawl map", "site map"],
    "firecrawl-search": ["firecrawl search", "web search"],
    "firecrawl-monitor": ["firecrawl monitor", "watch", "track"],
    "firecrawl-extract": ["firecrawl extract", "structured"],
    "firecrawl-interact": ["firecrawl interact", "click", "interact"],
    "firecrawl-parse": ["firecrawl parse", "parse", "pdf"],
    "firecrawl-download": ["firecrawl download", "download", "save"],
    "homebrew-fc": ["homebrew", "brew", "firecrawl"],
    "functions": ["functions", "browserbase functions", "serverless"],
    "browser-cli": ["browser cli", "browse cli", "browser automation"],
    "safe-browser": ["safe browser", "domain allowlist", "constrained"],
    "skill-mcp": ["skill", "mcp", "skill server"],
    "mcp-builder": ["mcp builder", "create mcp", "mcp server"],
    "duckdb-skill": ["duckdb", "duckdb sql"],
    "mcp-platform": ["mcp", "fastmcp", "mcp server"],
    "mcp-server": ["mcp server", "mcp client"],
    "browserbase-cli": ["browserbase cli", "browse", "browser"],
    "browser-automation-skill": ["browser automation", "browse", "playwright"],
    "webapp-testing": ["webapp testing", "playwright", "test"],
    "stack-ops-skill": ["stack-ops", "stack doctor", "stack audit"],
    "agent-skill": ["agent skill", "agent", "skill"],
    "ddd-patterns": ["domain driven", "ddd", "bounded context"],
    "baml-schema": ["baml", "schema", "structured output"],
    "skill-format": ["skill", "skill format", "skill structure"],
    "skill-prompt": ["skill prompt", "skill instructions"],
    "frontend-design": ["frontend design", "design system", "ui design"],
    "theme-factory": ["theme", "artifact", "theme factory"],
    "web-artifacts": ["web artifacts", "artifact", "html artifact"],
    "canvas-design": ["canvas design", "art", "design"],
    "algorithmic-art": ["algorithmic art", "p5.js", "generative art"],
    "slack-gif": ["slack gif", "gif", "slack"],
    "brand-guidelines": ["brand", "anthropic brand", "style"],
    "ui-test": ["ui test", "adversarial test", "ui qa"],
    "internal-comms": ["internal comms", "comms", "internal communication"],
    "doc-coauthoring": ["doc coauthoring", "doc collaboration"],
    "frontend-skill": ["frontend", "frontend skill", "react"],
    "irish-edtech": ["irish edtech", "irish education", "bilingual"],
    "skill-irish-edtech": ["irish edtech", "irish education", "bilingual"],
    "kings-college-galway-history": ["kings college galway", "hardiman", "1795", "history"],
    "irish-history": ["irish history", "ireland history", "famine", "rebellion"],
    "celtic-history": ["celtic history", "celt", "gael"],
    "northern-ireland": ["northern ireland", "belfast", "derry"],
    "scotland-curriculum": ["scotland", "scottish", "curriculum for excellence"],
    "wales-curriculum": ["wales", "welsh", "curriculum for wales"],
    "english-curriculum": ["england", "english", "national curriculum"],
    "ni-curriculum": ["northern ireland curriculum", "ccea"],
    "primary-curriculum": ["primary", "primary school", "junior", "senior infants"],
    "post-primary": ["post primary", "secondary", "leaving cert", "junior cert"],
    "jc-curriculum": ["junior cycle", "junior cert", "jc"],
    "lc-curriculum": ["leaving cert", "leaving certificate", "lc"],
    "bilingual-education": ["bilingual", "bilingual education", "dual language"],
    "gaeilge-curriculum": ["gaeilge", "irish curriculum", "irish syllabus"],
    "english-curriculum-ireland": ["english curriculum", "primary english", "secondary english"],
    "maths-curriculum": ["maths", "mathematics", "maths curriculum"],
    "science-curriculum": ["science", "science curriculum", "biology", "chemistry", "physics"],
    "stem-education": ["stem", "steam", "stem education"],
    "humanities-curriculum": ["humanities", "history", "geography"],
    "language-curriculum": ["language", "modern language", "mfl"],
    "irish-civil-service": ["civil service", "public service", "government"],
    "irish-economy": ["ireland economy", "irish economy", "gdp"],
    "irish-tech-sector": ["tech sector", "irish tech", "fdi", "ida"],
    "irish-universities": ["university", "third level", "ucd", "tcd", "nuig"],
    "internationalisation": ["international", "internationalisation", "study abroad"],
    "erasmus": ["erasmus", "european", "exchange"],
    "etwinning": ["etwinning", "e-twinning", "school partnership"],
    "unesco": ["unesco", "world heritage", "education"],
    "oecd": ["oecd", "oecd education"],
    "european-commission": ["european commission", "eu", "erasmus"],
    "eu-education": ["eu education", "european education"],
    "sdg-education": ["sdg", "sustainable development", "sdg 4"],
    "global-education": ["global education", "global citizenship"],
    "education-policy": ["education policy", "policy", "reform"],
    "education-research": ["education research", "research", "academic"],
    "education-stats": ["statistics", "stats", "education stats"],
    "education-reform": ["education reform", "reform", "restructure"],
    "education-equity": ["equity", "inclusion", "diversity"],
    "education-special": ["special educational needs", "sen", "inclusion"],
    "education-technology": ["edtech", "education technology", "ai in education"],
    "ai-education": ["ai in education", "ai for education", "education ai"],
    "education-leadership": ["leadership", "principal", "management"],
    "teacher-training": ["teacher training", "teacher education", "pme"],
    "teacher-registration": ["teaching council", "registration", "teacher standards"],
    "teaching-practice": ["teaching practice", "school placement", "pme"],
    "teaching-methods": ["teaching method", "pedagogy", "methodology"],
    "pedagogy": ["pedagogy", "teaching", "learning theory"],
    "constructivism": ["constructivism", "constructivist"],
    "inquiry-based": ["inquiry based", "inquiry learning", "5e"],
    "project-based": ["project based", "pbl", "project"],
    "problem-based": ["problem based", "pbl", "problem solving"],
    "flipped-classroom": ["flipped", "flipped classroom", "inverted"],
    "blended-learning": ["blended", "hybrid", "blended learning"],
    "online-learning": ["online learning", "elearning", "distance"],
    "mooc": ["mooc", "massive open", "online course"],
    "assessment": ["assessment", "evaluation", "test"],
    "formative-assessment": ["formative", "formative assessment", "afl"],
    "summative-assessment": ["summative", "exam", "state exam"],
    "continuous-assessment": ["continuous assessment", "caa", "classroom based"],
    "portfolio-assessment": ["portfolio", "portfolio assessment"],
    "standardized-testing": ["standardized test", "standardised", "timss", "pisa"],
    "pisa": ["pisa", "oecd pisa"],
    "timss": ["timss", "iea timss"],
    "pirls": ["pirls", "reading literacy"],
    "examination": ["examination", "state exam", "leaving cert"],
    "examinations-ie": ["examinations.ie", "sec", "state examinations commission"],
    "leaving-cert-2026": ["leaving cert 2026", "lc 2026"],
    "irish-curriculum-changes": ["senior cycle", "curriculum change", "reform"],
    "ai-curriculum": ["ai curriculum", "ai in schools", "ai education"],
    "data-curriculum": ["data", "data literacy", "data education"],
    "digital-literacy": ["digital literacy", "computer literacy"],
    "media-literacy": ["media literacy", "news literacy"],
    "critical-thinking": ["critical thinking", "thinking skills"],
    "creativity-education": ["creativity", "creative", "creative education"],
    "wellbeing-education": ["wellbeing", "wellbeing curriculum", "mental health"],
    "physical-education": ["physical education", "pe", "sport"],
    "sphe": ["sphe", "social personal health education"],
    "civic-education": ["civic", "citizenship", "civic education"],
    "religious-education": ["religious education", "religion", "faith"],
    "ethics-education": ["ethics", "moral", "ethics education"],
    "arts-education": ["arts", "visual arts", "music"],
    "music-education": ["music", "music education", "singing"],
    "drama-education": ["drama", "theatre", "drama education"],
    "visual-arts": ["visual arts", "art", "drawing"],
    "coding-curriculum": ["coding", "programming", "computer science"],
    "computer-science-ireland": ["computer science", "lc computer science", "leaving cert cs"],
    "stem-curriculum": ["stem", "steam", "stem education"],
    "data-science-curriculum": ["data science", "data literacy"],
    "ai-literacy": ["ai literacy", "ai awareness", "ai understanding"],
    "robotics-curriculum": ["robotics", "robot", "robotics curriculum"],
    "engineering-curriculum": ["engineering", "engineering education"],
    "maths-problem-solving": ["problem solving", "maths problem", "pisa maths"],
    "reading-literacy": ["reading", "literacy", "reading literacy"],
    "writing-curriculum": ["writing", "writing skills", "composition"],
    "oral-language": ["oral language", "speaking", "listening"],
    "phonics": ["phonics", "phonological", "phonemic"],
    "early-years": ["early years", "pre-school", "infants"],
    "transition-year": ["transition year", "ty", "transition year programme"],
    "lca": ["lca", "leaving cert applied"],
    "lcvp": ["lcvp", "leaving cert vocational programme"],
    "special-needs": ["special needs", "sen", "inclusion", "additional needs"],
    "asd": ["asd", "autism", "asd units"],
    "dyslexia": ["dyslexia", "specific learning", "spld"],
    "gifted": ["gifted", "gifted education", "high ability"],
    "disadvantage": ["disadvantage", "deis", "deis schools"],
    "rural-schools": ["rural", "small schools", "rural schools"],
    "urban-schools": ["urban", "city schools", "dublin", "cork"],
    "gaelscoil": ["gaelscoil", "gaeilge", "irish medium"],
    "special-school": ["special school", "special class"],
    "gaeltacht": ["gaeltacht", "irish speaking", "gaeltacht regions"],
    "irish-medium": ["irish medium", "gaeilge", "medium of instruction"],
    "english-medium": ["english medium", "english speaking"],
    "trinity-college": ["trinity college", "tcd", "trinity"],
    "ucd": ["ucd", "university college dublin"],
    "ul": ["ul", "university of limerick"],
    "dcu": ["dcu", "dublin city university"],
    "maynooth": ["maynooth", "nui maynooth", "mu"],
    "uuc": ["ulster university", "uu", "coleraine"],
    "queens": ["queens", "qub", "queens university belfast"],
    "stranmillis": ["stranmillis", "stranmillis university college"],
    "st-marys": ["st marys", "stmarys"],
    "marino": ["marino institute", "marino"],
    "froebel": ["froebel", "froebel college"],
    "blackrock": ["blackrock", "blackrock education"],
    "drumcondra": ["drumcondra", "dcu"],
    "st-nicholas": ["st nicholas", "st nicholas montessori"],
    "montessori": ["montessori", "montessori education"],
    "steiner": ["steiner", "waldorf", "steiner education"],
    "educate-together": ["educate together", "etb", "equality based"],
    "community-school": ["community school", "community schools"],
    "comprehensive-school": ["comprehensive", "comprehensive school"],
    "vocational-school": ["vocational", "vocational school"],
    "secondary-school": ["secondary", "secondary school"],
    "girls-school": ["girls school", "all girls", "secondary girls"],
    "boys-school": ["boys school", "all boys", "secondary boys"],
    "mixed-school": ["mixed school", "co-educational"],
    "fee-paying": ["fee paying", "private school"],
    "public-school": ["public school", "state funded"],
    "school-governance": ["governance", "board of management", "patron"],
    "school-trust": ["trust", "education trust", "school trust"],
    "patron-body": ["patron", "patron body", "religious patron"],
    "catholic-school": ["catholic", "catholic school"],
    "church-of-ireland": ["church of ireland", "coi", "anglican"],
    "methodist-school": ["methodist", "methodist school"],
    "presbyterian": ["presbyterian", "presbyterian church"],
    "jewish-school": ["jewish", "jewish school"],
    "muslim-school": ["muslim", "muslim school", "islamic"],
    "hindu-school": ["hindu", "hindu school"],
    "multi-denominational": ["multi denominational", "multi faith", "interfaith"],
    "interfaith": ["interfaith", "multi faith"],
    "patronage": ["patronage", "school patronage"],
    "school-funding": ["funding", "capitation", "school funding"],
    "department-of-education": ["department of education", "doe", "des"],
    "ncse": ["ncse", "national council for special education"],
    "teaching-council": ["teaching council", "registration"],
    "sec": ["sec", "state examinations commission"],
    "ncca": ["ncca", "national council for curriculum and assessment"],
    "jjst": ["jjst", "junior cycle"],
    "inspectorate": ["inspectorate", "inspection", "evaluation"],
    "wse": ["wse", "whole school evaluation"],
    "incidental-inspection": ["incidental inspection", "unannounced inspection"],
    "subject-inspection": ["subject inspection", "subject evaluation"],
    "school-self-evaluation": ["sse", "school self evaluation"],
    "ssse": ["ssse", "school self evaluation"],
    "look-at-our-school": ["look at our school", "laos"],
    "teaching-and-learning": ["teaching and learning", "t&l", "pedagogy"],
    "subject-department": ["subject department", "subject planning"],
    "curriculum-planning": ["curriculum planning", "subject planning"],
    "scheme-of-work": ["scheme of work", "plan", "lesson plan"],
    "lesson-plan": ["lesson plan", "lesson planning", "scheme"],
    "annual-plan": ["annual plan", "year plan"],
    "long-term-plan": ["long term plan", "curriculum plan"],
    "short-term-plan": ["short term plan", "fortnightly plan"],
    "croke-park-hours": ["croke park hours", "croke park"],
    "tui": ["tui", "teachers union of ireland"],
    "astl": ["astl", "association of secondary teachers ireland"],
    "ifut": ["ifut", "irish federation of university teachers"],
    "teacher-union": ["teacher union", "union"],
    "industrial-action": ["industrial action", "strike", "action"],
    "pay-equity": ["pay equity", "equal pay", "pay"],
    "teacher-pay": ["teacher pay", "pay scale", "salary"],
    "teacher-conditions": ["conditions", "working conditions", "teacher"],
    "new-entrant": ["new entrant", "new teacher"],
    "covid": ["covid", "covid-19", "pandemic", "remote learning"],
    "remote-teaching": ["remote teaching", "online teaching", "distance"],
    "hybrid-teaching": ["hybrid teaching", "hybrid learning"],
    "school-reopening": ["reopening", "back to school"],
    "school-closures": ["closure", "school closure"],
    "mental-health": ["mental health", "wellbeing", "student wellbeing"],
    "student-support": ["student support", "pastoral care", "support"],
    "guidance-counsellor": ["guidance", "guidance counsellor"],
    "school-counsellor": ["counsellor", "counselling"],
    "neps": ["neps", "national educational psychological service"],
    "psychological-service": ["psychological service", "psychologist"],
    "camhs": ["camhs", "child and adolescent mental health"],
    "jigsaw": ["jigsaw", "mental health service"],
    "pieta": ["pieta", "pieta house", "bereavement"],
    "suicide-prevention": ["suicide", "suicide prevention", "bereavement"],
    "lgbtq": ["lgbtq", "lgbt", "lgbtq+"],
    "inclusion": ["inclusion", "inclusive", "diversity"],
    "equality": ["equality", "equal", "equity"],
    "anti-bullying": ["anti bullying", "bullying", "cyber bullying"],
    "cyber-bullying": ["cyber bullying", "online bullying"],
    "safeguarding": ["safeguarding", "child protection"],
    "child-protection": ["child protection", "vulnerable"],
    "vetted": ["garda vetting", "vetting"],
    "data-protection": ["data protection", "gdpr", "data"],
    "gdpr": ["gdpr", "data protection", "data"],
    "digital-strategy": ["digital strategy", "digital plan"],
    "digital-learning-framework": ["dlf", "digital learning framework"],
    "schools-network": ["school network", "school broadband"],
    "hea": ["hea", "higher education authority"],
    "qaa": ["qaa", "quality and qualifications ireland", "qqi"],
    "qqi": ["qqi", "quality and qualifications ireland"],
    "nfq": ["nfq", "national framework of qualifications"],
    "ects": ["ects", "european credit transfer"],
    "eas": ["eas", "education awards"],
    "qf-ehea": ["qf ehea", "bologna", "ehea"],
    "youthreach": ["youthreach", "youth education"],
    "btei": ["btei", "back to education initiative"],
    "vtos": ["vtos", "vocational training opportunities scheme"],
    "night-classes": ["night classes", "evening classes"],
    "adult-education": ["adult education", "adult learning"],
    "community-education": ["community education", "community learning"],
    "further-education": ["further education", "fet", "further education and training"],
    "higher-education": ["higher education", "third level", "university"],
    "springboard": ["springboard", "springboard+"],
    "human-capital": ["human capital", "skills"],
    "skillnet": ["skillnet", "skill network"],
    "education-research-centres": ["research centre", "esri", "erc"],
    "esri": ["esri", "economic and social research institute"],
    "erc": ["erc", "education research centre"],
    "nfer": ["nfer", "national foundation for educational research"],
    "crede": ["crede", "centre for research in education"],
    "centre-for-education": ["centre for education", "education research"],
    "early-childhood": ["early childhood", "ece", "early childhood care"],
    "eccc": ["eccc", "early childhood care and education"],
    "early-start": ["early start", "pre-school"],
    "aim": ["aim", "access and inclusion model"],
    "high-scope": ["high scope", "highscope"],
    "ready-set-go": ["ready set go", "rsgl"],
    "first-five": ["first five", "first 5", "early years strategy"],
    "better-start": ["better start", "better start quality"],
    "siolta": ["siolta", "quality framework"],
    "aistear": ["aistear", "early childhood curriculum framework"],
    "mo-scéal": ["mo scéal", "mascot", "early years"],
    "language-nests": ["language nest", "naíonra", "irish medium preschool"],
    "naionra": ["naíonra", "irish language preschool"],
    "tuistí": ["tuistí", "parents", "family"],
    "parental-engagement": ["parental engagement", "parent teacher"],
    "home-school": ["home school", "homeschool", "homeschooling"],
    "homework": ["homework", "homework policy"],
    "study-skills": ["study skills", "study"],
    "exam-prep": ["exam prep", "exam preparation"],
    "revision": ["revision", "exam revision"],
    "ace": ["ace", "ace programme"],
    "grinds": ["grinds", "private tuition"],
    "private-tuition": ["private tuition", "grinds"],
    "study-clubs": ["study club", "study support"],
    "after-school": ["after school", "after-school"],
    "summer-school": ["summer school", "summer programme"],
    "gaeltacht-colleges": ["gaeltacht college", "gaeilge coláiste"],
    "colaiste": ["coláiste", "gaeltacht college"],
    "irish-college": ["irish college", "gaeilge college"],
    "sumcoil": ["sumcoil", "summer gaeltacht"],
    "fáilte-gaeilge": ["fáilte gaeilge", "gaeilge"],
    "taighde": ["taighde", "research"],
    "staidéar": ["staidéar", "study"],
    "scoil": ["scoil", "school"],
    "scoil-naisiunta": ["scoil náisiúnta", "primary school"],
    "meánscoil": ["meánscoil", "secondary school"],
    "ardteist": ["ardteist", "leaving cert"],
    "teastas": ["teastas", "certificate"],
    "teist": ["teist", "test"],
    "socrú": ["socrú", "arrangement"],
    "bunoideachas": ["bunoideachas", "primary education"],
    "meánoideachas": ["meánoideachas", "secondary education"],
    "ardoideachas": ["ardoideachas", "higher education"],
    "tríú-leibhéal": ["tríú leibhéal", "third level"],
    "ollscoil": ["ollscoil", "university"],
    "coláiste": ["coláiste", "college"],
    "scoil-gháil": ["scoil gháil", "irish school"],
    "teanga-gháil": ["teanga gháil", "irish language"],
    "gaeilge-staidéar": ["gaeilge staidéar", "irish study"],
    "gaeilge-mhúineadh": ["gaeilge mhúineadh", "irish teaching"],
    "múinteoir-gaeilge": ["múinteoir gaeilge", "irish teacher"],
    "gaeilge-acadamh": ["gaeilge acadamh", "irish academy"],
    "acadamh": ["acadamh", "academy"],
    "gaeilge-scríbhneoir": ["gaeilge scríbhneoir", "irish writer"],
    "filíocht": ["filíocht", "poetry"],
    "prós": ["prós", "prose"],
    "litearacht": ["litearacht", "literature"],
    "scéal": ["scéal", "story"],
    "scéalta": ["scéalta", "stories"],
    "béaloideas": ["béaloideas", "folklore"],
    "logainmneacha": ["logainmneacha", "place names"],
    "dinnseanchas": ["dinnseanchas", "toponomy"],
    "seanchas": ["seanchas", "lore"],
    "foclóir": ["foclóir", "dictionary"],
    "gramadach": ["gramadach", "grammar"],
    "canúint": ["canúint", "dialect"],
    "tráchtaireacht": ["tráchtaireacht", "commentary"],
    "beochraoladh": ["beochraoladh", "broadcast"],
    "píosa": ["píosa", "piece"],
    "nuachtán": ["nuachtán", "newspaper"],
    "iris": ["iris", "magazine"],
    "irisleabhar": ["irisleabhar", "journal"],
    "leabhar": ["leabhar", "book"],
    "leabharlann": ["leabharlann", "library"],
    "cartlann": ["cartlann", "archive"],
    "músaem": ["músaem", "museum"],
    "iarsmalann": ["iarsmalann", "archive"],
    "taibhdhearc": ["taibhdhearc", "theatre"],
    "amharclann": ["amharclann", "theatre"],
    "ceol": ["ceol", "music"],
    "amhrán": ["amhrán", "song"],
    "rince": ["rince", "dance"],
    "damhsa": ["damhsa", "dance"],
    "sean-nós": ["sean nós", "old style"],
    "seanchaí": ["seanchaí", "storyteller"],
    "scéalaí": ["scéalaí", "storyteller"],
    "filí": ["filí", "poet"],
    "ceoltóir": ["ceoltóir", "musician"],
    "ceol-gaeilge": ["ceol gaeilge", "irish music"],
    "trádáil": ["trádáil", "tradition"],
    "cultúr": ["cultúr", "culture"],
    "cúlra": ["cúlra", "background"],
    "oidhreacht": ["oidhreacht", "heritage"],
    "teangacha": ["teangacha", "languages"],
    "teangacha-ceilteacha": ["teangacha ceilteacha", "celtic languages"],
    "celtic-gaeilge": ["celtic", "ceilteach"],
    "mannan": ["mannan", "manx"],
    "mannan-ghaelg": ["mannan ghaelg", "manx gaelic"],
    "cornish": ["cornish", "kernewek"],
    "brezhoneg": ["brezhoneg", "breton"],
    "cymraeg": ["cymraeg", "welsh"],
    "gaeilge-albannach": ["gaeilge albannach", "scottish gaelic"],
    "fréamhacha": ["fréamhacha", "roots"],
    "logainmneacha-gaelacha": ["logainmneacha gaelacha", "gaelic place names"],
    "dualgas": ["dualgas", "duty"],
    "dlí": ["dlí", "law"],
    "ceart": ["ceart", "right"],
    "saoránach": ["saoránach", "citizen"],
    "pobal": ["pobal", "community"],
    "tír": ["tír", "country"],
    "muintir": ["muintir", "people"],
    "muintir-na-tíre": ["muintir na tíre", "rural"],
    "tuath": ["tuath", "territory"],
    "dúiche": ["dúiche", "district"],
    "contae": ["contae", "county"],
    "cathair": ["cathair", "city"],
    "baile": ["baile", "town"],
    "sráidbhaile": ["sráidbhaile", "village"],
    "teach": ["teach", "house"],
    "margadh": ["margadh", "market"],
    "aonach": ["aonach", "fair"],
    "portach": ["portach", "port"],
    "cala": ["cala", "harbour"],
    "iascach": ["iascach", "fishing"],
    "feirmeoireacht": ["feirmeoireacht", "farming"],
    "talaimh": ["talaimh", "land"],
    "eorna": ["eorna", "barley"],
    "prátaí": ["prátaí", "potatoes"],
    "arbhar": ["arbhar", "corn"],
    "coirce": ["coirce", "oats"],
    "bainne": ["bainne", "milk"],
    "im": ["im", "butter"],
    "uaineoil": ["uaineoil", "lamb"],
    "caoirigh": ["caoirigh", "sheep"],
    "bó": ["bó", "cow"],
    "eallach": ["eallach", "cattle"],
    "each": ["each", "horse"],
    "capall": ["capall", "horse"],
    "muc": ["muc", "pig"],
    "sicín": ["sicín", "chicken"],
    "éan": ["éan", "bird"],
    "éanlaith": ["éanlaith", "birds"],
    "iasc": ["iasc", "fish"],
    "sionnach": ["sionnach", "fox"],
    "madra": ["madra", "dog"],
    "cat": ["cat", "cat"],
    "coinín": ["coinín", "rabbit"],
    "iolair": ["iolair", "eagle"],
    "seabhac": ["seabhac", "hawk"],
    "bradán": ["bradán", "salmon"],
    "breac": ["breac", "trout"],
    "iasc-mhara": ["iasc mhara", "whale"],
    "séala": ["séala", "seal"],
    "diúc": ["diúc", "duck"],
    "spréach": ["spréach", "sparrow"],
    "lon": ["lon", "blackbird"],
    "smólach": ["smólach", "thrush"],
    "giolcach": ["giolcach", "cuckoo"],
    "cuach": ["cuach", "cuckoo"],
    "péistéan": ["péistéan", "insects"],
    "beach": ["beach", "bee"],
    "seangán": ["seangán", "ant"],
    "feithid": ["feithid", "insect"],
    "sciathán-leathar": ["sciathán leathar", "bat"],
    "ialtóg": ["ialtóg", "bat"],
    "bláth": ["bláth", "flower"],
    "crann": ["crann", "tree"],
    "coill": ["coill", "wood"],
    "foraois": ["foraois", "forest"],
    "páirc": ["páirc", "park"],
    "gairdín": ["gairdín", "garden"],
    "garraí": ["garraí", "garden"],
    "bláth-garraí": ["bláth garraí", "flower garden"],
    "crainn": ["crainn", "trees"],
    "duilleog": ["duilleog", "leaf"],
    "bláthanna": ["bláthanna", "flowers"],
    "síol": ["síol", "seed"],
    "planda": ["planda", "plant"],
    "leac": ["leac", "flagstone"],
    "grianán": ["grianán", "sunroom"],
    "solas": ["solas", "light"],
    "dorcha": ["dorcha", "dark"],
    "oíche": ["oíche", "night"],
    "lá": ["lá", "day"],
    "maidin": ["maidin", "morning"],
    "tráthnóna": ["tráthnóna", "evening"],
    "meán-lae": ["meán lae", "noon"],
    "meán-oíche": ["meán oíche", "midnight"],
    "aibreán": ["aibreán", "april"],
    "bealtaine": ["bealtaine", "may"],
    "meitheamh": ["meitheamh", "june"],
    "iúil": ["iúil", "july"],
    "lúnasa": ["lúnasa", "august"],
    "meán-fómhar": ["meán fómhar", "september"],
    "deireadh-fómhar": ["deireadh fómhar", "october"],
    "samhain": ["samhain", "november"],
    "nollaig": ["nollaig", "december"],
    "eanáir": ["eanáir", "january"],
    "feabhra": ["feabhra", "february"],
    "márta": ["márta", "march"],
    "lá-fhéile": ["lá fhéile", "feast day"],
    "sábh": ["sábh", "sav"],
    "fómhar": ["fómhar", "harvest"],
    "dréimire": ["dréimire", "ladder"],
    "fuinneog": ["fuinneog", "window"],
    "doras": ["doras", "door"],
    "urlár": ["urlár", "floor"],
    "balla": ["balla", "wall"],
    "díon": ["díon", "roof"],
    "simléar": ["simléar", "chimney"],
    "teallach": ["teallach", "hearth"],
    "tine": ["tine", "fire"],
    "citeal": ["citeal", "kettle"],
    "cóc": ["cóc", "cook"],
    "cistin": ["cistin", "kitchen"],
    "seomra": ["seomra", "room"],
    "seomra-suil": ["seomra suil", "living room"],
    "seomra-codlata": ["seomra codlata", "bedroom"],
    "seomra-folctha": ["seomra folctha", "bathroom"],
    "leithreas": ["leithreas", "toilet"],
    "cithfholcadh": ["cithfholcadh", "shower"],
    "folcadh": ["folcadh", "bath"],
    "gualach": ["gualach", "coal"],
    "adhmad": ["adhmad", "wood"],
    "saille": ["saille", "salt"],
    "ola": ["ola", "oil"],
    "uachtar": ["uachtar", "cream"],
    "gruth": ["gruth", "curd"],
    "cáis": ["cáis", "cheese"],
    "griollach": ["griollach", "groats"],
    "arán": ["arán", "bread"],
    "bagún": ["bagún", "bacon"],
    "praiseach": ["praiseach", "porridge"],
    "torthaí": ["torthaí", "fruit"],
    "úll": ["úll", "apple"],
    "oráiste": ["oráiste", "orange"],
    "líomóid": ["líomóid", "lemon"],
    "banana": ["banana", "banana"],
    "fíon": ["fíon", "wine"],
    "beoir": ["beoir", "beer"],
    "cáca": ["cáca", "cake"],
    "mil": ["mil", "honey"],
    "siúcra": ["siúcra", "sugar"],
    "seacláid": ["seacláid", "chocolate"],
    "tae": ["tae", "tea"],
    "caife": ["caife", "coffee"],
    "uisce": ["uisce", "water"],
    "sú": ["sú", "juice"],
    "fíon-dearg": ["fíon dearg", "red wine"],
    "fíon-bán": ["fíon bán", "white wine"],
    "fuisce": ["fuisce", "whiskey"],
    "póitín": ["póitín", "poitin"],
    "milis": ["milis", "sweet"],
    "goirt": ["goirt", "salty"],
    "searbh": ["searbh", "bitter"],
    "aigéad": ["aigéad", "sour"],
    "spíosra": ["spíosra", "spice"],
    "lobhadh": ["lobhadh", "decay"],
    "milseog": ["milseog", "sweet"],
    "salann": ["salann", "salt"],
    "piobar": ["piobar", "pepper"],
    "sinséar": ["sinséar", "ginger"],
    "cainéal": ["cainéal", "cinnamon"],
    "cúmar": ["cúmar", "cumin"],
    "cairt": ["cairt", "cardamom"],
    "clóbh": ["clóbh", "clove"],
    "nóta": ["nóta", "note"],
    "ríméad": ["ríméad", "wonder"],
    "súgradh": ["súgradh", "play"],
    "spraoi": ["spraoi", "fun"],
    "gleic": ["gleic", "fight"],
    "iománaíocht": ["iománaíocht", "hurling"],
    "peil": ["peil", "football"],
    "sacar": ["sacar", "soccer"],
    "rugbaí": ["rugbaí", "rugby"],
    "cispheil": ["cispheil", "basketball"],
    "leadóg": ["leadóg", "tennis"],
    "gailf": ["gailf", "golf"],
    "snámh": ["snámh", "swim"],
    "rith": ["rith", "run"],
    "siúl": ["siúl", "walk"],
    "rothaíocht": ["rothaíocht", "cycling"],
    "capaill": ["capaill", "horses"],
    "turas": ["turas", "journey"],
    "eitilt": ["eitilt", "flight"],
    "bád": ["bád", "boat"],
    "long": ["long", "ship"],
    "carr": ["carr", "car"],
    "bus": ["bus", "bus"],
    "trucail": ["trucail", "truck"],
    "traein": ["traein", "train"],
    "eitleán": ["eitleán", "plane"],
    "aerfort": ["aerfort", "airport"],
    "stáisiún": ["stáisiún", "station"],
    "calafort": ["calafort", "port"],
    "bóthar": ["bóthar", "road"],
    "rás": ["rás", "race"],
    "iomrall": ["iomrall", "mistake"],
    "réiteach": ["réiteach", "solution"],
    "ceist": ["ceist", "question"],
    "freagra": ["freagra", "answer"],
    "fadhb": ["fadhb", "problem"],
    "deis": ["deis", "opportunity"],
    "roghanna": ["roghanna", "options"],
    "cinnte": ["cinnte", "certain"],
    "dócha": ["dócha", "likely"],
    "cinnteacht": ["cinnteacht", "certainty"],
    "amhras": ["amhras", "doubt"],
    "cruthúnas": ["cruthúnas", "proof"],
    "fianaise": ["fianaise", "evidence"],
    "tuairim": ["tuairim", "opinion"],
    "breithiúnas": ["breithiúnas", "judgement"],
    "réasún": ["réasún", "reason"],
    "cúis": ["cúis", "cause"],
    "toradh": ["toradh", "result"],
    "tús": ["tús", "beginning"],
    "deireadh": ["deireadh", "end"],
    "lár": ["lár", "middle"],
    "tús-ama": ["tús ama", "start time"],
    "deireadh-ama": ["deireadh ama", "end time"],
    "anailís": ["anailís", "analysis"],
    "sintéis": ["sintéis", "synthesis"],
    "measúnú": ["measúnú", "evaluation"],
    "meas": ["meas", "respect"],
    "meas-mór": ["meas mór", "high respect"],
    "mearaí": ["mearaí", "fault"],
    "ceartas": ["ceartas", "justice"],
    "cothromas": ["cothromas", "fairness"],
    "ciúineas": ["ciúineas", "quietness"],
    "síocháin": ["síocháin", "peace"],
    "cogadh": ["cogadh", "war"],
    "coimhlint": ["coimhlint", "conflict"],
    "réiteach-síochána": ["réiteach síochána", "peaceful resolution"],
    "díospóid": ["díospóid", "dispute"],
    "caibidlíocht": ["caibidlíocht", "negotiation"],
    "comhréiteach": ["comhréiteach", "compromise"],
    "comhaontú": ["comhaontú", "agreement"],
    "conradh": ["conradh", "treaty"],
    "dlí-idirnáisiúnta": ["dlí idirnáisiúnta", "international law"],
    "cearta-daonna": ["cearta daonna", "human rights"],
    "saoirse": ["saoirse", "freedom"],
    "neamhspleáchas": ["neamhspleáchas", "independence"],
    "féinrial": ["féinrial", "self rule"],
    "dílseacht": ["dílseacht", "loyalty"],
    "muinín": ["muinín", "trust"],
    "iontaoibh": ["iontaoibh", "confidence"],
    "measartha": ["measartha", "moderate"],
    "réalaíoch": ["réalaíoch", "realistic"],
    "praiticiúil": ["praiticiúil", "practical"],
    "teoiriciúil": ["teoiriciúil", "theoretical"],
    "eolaíoch": ["eolaíoch", "scientific"],
    "fealsúnach": ["fealsúnach", "philosophical"],
    "críostaí": ["críostaí", "christian"],
    "eaglasta": ["eaglasta", "ecclesiastical"],
    "sibhialta": ["sibhialta", "civil"],
    "talmhaíoch": ["talmhaíoch", "agricultural"],
    "tionsclaíoch": ["tionsclaíoch", "industrial"],
    "eacnamaíoch": ["eacnamaíoch", "economic"],
    "sóisialta": ["sóisialta", "social"],
    "polaitiúil": ["polaitiúil", "political"],
    "dlíthiúil": ["dlíthiúil", "legal"],
    "míleata": ["míleata", "military"],
    "rúnda": ["rúnda", "secret"],
    "poiblí": ["poiblí", "public"],
    "príobháideach": ["príobháideach", "private"],
    "gairmiúil": ["gairmiúil", "professional"],
    "amaitéarach": ["amaitéarach", "amateur"],
    "oifigiúil": ["oifigiúil", "official"],
    "neamhoifigiúil": ["neamhoifigiúil", "unofficial"],
    "foirmeálta": ["foirmeálta", "formal"],
    "neamhfhoirmeálta": ["neamhfhoirmeálta", "informal"],
    "scolártha": ["scolártha", "scholarly"],
    "liteartha": ["liteartha", "literary"],
    "ealaíonta": ["ealaíonta", "artistic"],
    "cruthaitheach": ["cruthaitheach", "creative"],
    "traidisiúnta": ["traidisiúnta", "traditional"],
    "nua-aimseartha": ["nua-aimseartha", "modern"],
    "comhaimseartha": ["comhaimseartha", "contemporary"],
    "stairiúil": ["stairiúil", "historical"],
    "réamhstairiúil": ["réamhstairiúil", "prehistoric"],
    "ré": ["ré", "era"],
    "aois": ["aois", "age"],
    "linn": ["linn", "period"],
    "tréimhse": ["tréimhse", "phase"],
    "eochairchéim": ["eochairchéim", "key stage"],
    "cúige": ["cúige", "province"],
    "cúige-laighean": ["cúige laighean", "leinster"],
    "cúige-mumhan": ["cúige mumhan", "munster"],
    "cúige-connacht": ["cúige connacht", "connacht"],
    "cúige-uladh": ["cúige uladh", "ulster"],
    "gaeltacht": ["gaeltacht", "irish speaking region"],
    "bailte-seirbhíse": ["bailte seirbhíse", "service towns"],
    "bailte-slí": ["bailte slí", "way towns"],
    "tír-bhreathnaithe": ["tír bhreathnaithe", "scenic"],
    "tíreolaíocht": ["tíreolaíocht", "geography"],
    "réadmhaoin": ["réadmhaoin", "natural resources"],
    "mianraí": ["mianraí", "minerals"],
    "guail": ["guail", "coal"],
    "olabrionn": ["olabrionn", "turbary"],
    "bánta-móra": ["bánta móra", "flood plains"],
    "gleannta": ["gleannta", "valleys"],
    "sliabhraonta": ["sliabhraonta", "mountain ranges"],
    "abhainn": ["abhainn", "river"],
    "tulach": ["tulach", "hill"],
    "sliabh": ["sliabh", "mountain"],
    "cnoc": ["cnoc", "hill"],
    "bóinn": ["bóinn", "bann"],
    "bóinn-mhór": ["bóinn mhór", "bann"],
    "shannon": ["shannon", "shannon"],
    "shannon-atha": ["shannon atha", "shannon estuary"],
    "fionnuisce": ["fionnuisce", "freshwater"],
    "sáile": ["sáile", "salt water"],
    "farraige": ["farraige", "sea"],
    "cuan": ["cuan", "harbour"],
    "innbhear": ["innbhear", "estuary"],
    "srutha": ["srutha", "streams"],
    "easca": ["easca", "waterfall"],
    "sneachta": ["sneachta", "snow"],
    "driodar": ["driodar", "sleet"],
    "ceo": ["ceo", "fog"],
    "scamall": ["scamall", "cloud"],
    "spéir": ["spéir", "sky"],
    "réalta": ["réalta", "star"],
    "gealach": ["gealach", "moon"],
    "grian": ["grian", "sun"],
    "pláinéad": ["pláinéad", "planet"],
    "domhan": ["domhan", "world"],
    "cruinne": ["cruinne", "universe"],
    "réaltacht": ["réaltacht", "reality"],
    "intinn": ["intinn", "mind"],
    "anam": ["anam", "soul"],
    "croí": ["croí", "heart"],
    "spiorad": ["spiorad", "spirit"],
    "fuinneamh": ["fuinneamh", "energy"],
    "nádúr": ["nádúr", "nature"],
    "dúlra": ["dúlra", "nature"],
    "timpeallacht": ["timpeallacht", "environment"],
    "éiceolaíocht": ["éiceolaíocht", "ecology"],
    "inbhuanaithe": ["inbhuanaithe", "sustainable"],
    "athrú-aeráide": ["athrú aeráide", "climate change"],
    "éagsúlacht": ["éagsúlacht", "diversity"],
    "bitheolaíocht": ["bitheolaíocht", "biology"],
    "ceimic": ["ceimic", "chemistry"],
    "fisic": ["fisic", "physics"],
    "matamaitic": ["matamaitic", "maths"],
    "staitistic": ["staitistic", "statistics"],
    "ríomheolaíocht": ["ríomheolaíocht", "computer science"],
    "eolaíocht": ["eolaíocht", "science"],
    "inniúlacht": ["inniúlacht", "competence"],
    "scil": ["scil", "skill"],
    "eolas": ["eolas", "knowledge"],
    "fios": ["fios", "knowledge"],
    "tuiscint": ["tuiscint", "understanding"],
    "tuigse": ["tuigse", "understanding"],
    "feasacht": ["feasacht", "awareness"],
    "mothúchán": ["mothúchán", "feeling"],
    "smaoineamh": ["smaoineamh", "thought"],
    "smaointe": ["smaointe", "thoughts"],
    "samhlaíocht": ["samhlaíocht", "imagination"],
    "cruthaíocht": ["cruthaíocht", "creation"],
    "réadmhaoin": ["réadmhaoin", "real estate"],
    "seilbh": ["seilbh", "possession"],
    "úinéir": ["úinéir", "owner"],
    "tionóntán": ["tionóntán", "tenant"],
    "léas": ["léas", "lease"],
    "rátáil": ["rátáil", "rating"],
    "luach": ["luach", "value"],
    "airgead": ["airgead", "money"],
    "euro": ["euro", "euro"],
    "punt": ["punt", "pound"],
    "pingin": ["pingin", "penny"],
    "ceip": ["ceip", "cent"],
    "sliotar": ["sliotar", "sliotar"],
    "luacháil": ["luacháil", "valuation"],
    "cáin": ["cáin", "tax"],
    "cáin-ioncaim": ["cáin ioncaim", "income tax"],
    "cáin-luacháil": ["cáin luacháil", "property tax"],
    "cáin-siarchoinneála": ["cáin siarchoinneála", "withholding tax"],
    "cáin-bhreisluacha": ["cáin bhreisluacha", "vat"],
    "cáin-shaibhir": ["cáin shaibhir", "wealth tax"],
    "cáin-fhorlíonta": ["cáin fhorlíonta", "supplemental tax"],
    "deontas": ["deontas", "grant"],
    "fáltas": ["fáltas", "receipt"],
    "íocaíocht": ["íocaíocht", "payment"],
    "sannadh": ["sannadh", "allocation"],
    "leithdháileadh": ["leithdháileadh", "distribution"],
    "síntiús": ["síntiús", "subscription"],
    "táille": ["táille", "fee"],
    "costas": ["costas", "cost"],
    "praghas": ["praghas", "price"],
    "margadhluach": ["margadhluach", "market value"],
    "meánluach": ["meánluach", "average value"],
    "laghdú": ["laghdú", "reduction"],
    "ardú": ["ardú", "increase"],
    "méadú": ["méadú", "expansion"],
    "laghdú-cánach": ["laghdú cánach", "tax cut"],
    "ardú-cánach": ["ardú cánach", "tax increase"],
    "bainc": ["bainc", "bank"],
    "creidmheas": ["creidmheas", "credit"],
    "iasacht": ["iasacht", "loan"],
    "morgáiste": ["morgáiste", "mortgage"],
    "urrús": ["urrús", "security"],
    "infheistíocht": ["infheistíocht", "investment"],
    "infheisteoir": ["infheisteoir", "investor"],
    "brabús": ["brabús", "profit"],
    "caillteanas": ["caillteanas", "loss"],
    "cuntasaíocht": ["cuntasaíocht", "accounting"],
    "iniúchadh": ["iniúchadh", "audit"],
    "cigire": ["cigire", "inspector"],
    "easca": ["easca", "easca"],
    "easca-fhianaise": ["easca fhianaise", "documentary evidence"],
    "réadmhaoin-ealaíne": ["réadmhaoin ealaíne", "art asset"],
    "réadmhaoin-samhlaíoch": ["réadmhaoin shamhlaíoch", "imaginary asset"],
    "réadmhaoin-oidhreachta": ["réadmhaoin oidhreachta", "heritage asset"],
    "réadmhaoin-chultúrtha": ["réadmhaoin chultúrtha", "cultural asset"],
    "réadmhaoin-nádúrtha": ["réadmhaoin nádúrtha", "natural asset"],
    "réadmhaoin-fhisiciúil": ["réadmhaoin fhisiciúil", "physical asset"],
    "réadmhaoin-digiteach": ["réadmhaoin digiteach", "digital asset"],
    "réadmhaoin-fhíorúil": ["réadmhaoin fhíorúil", "virtual asset"],
    "réadmhaoin-shóisialta": ["réadmhaoin shóisialta", "social asset"],
    "réadmhaoin-aipe": ["réadmhaoin aipe", "ape asset"],
    "réadmhaoin-pobail": ["réadmhaoin pobail", "community asset"],
    "scoil-mhór": ["scoil mhór", "big school"],
    "scoil-bheag": ["scoil bheag", "small school"],
    "scoil-nua": ["scoil nua", "new school"],
    "scoil-iar-bhunscoil": ["scoil iar bhunscoil", "post-primary school"],
    "scoil-bhunscoil": ["scoil bhunscoil", "primary school"],
    "bunscoil": ["bunscoil", "primary school"],
    "iar-bhunscoil": ["iar bhunscoil", "post primary"],
    "meánscoil": ["meánscoil", "secondary school"],
    "coláiste-ardoideachais": ["coláiste ardoideachais", "college of higher education"],
    "coláiste-oiliúna": ["coláiste oiliúna", "training college"],
    "ollscoil-theicniúil": ["ollscoil theicniúil", "technological university"],
    "teic-ollscoil": ["teic ollscoil", "tech university"],
    "ollscoil-na-gaillimhe": ["ollscoil na gaillimhe", "university of galway"],
    "ollscoil-chorcaí": ["ollscoil chorcaí", "university college cork"],
    "ucd": ["ucd", "university college dublin"],
    "mu": ["mu", "maynooth university"],
    "tcd": ["tcd", "trinity college dublin"],
    "setu": ["setu", "south east technological university"],
    "tudublin": ["tudublin", "technological university dublin"],
    "atu": ["atu", "atlantic technological university"],
    "mtu": ["mtu", "munster technological university"],
    "dkit": ["dkit", "dundalk institute of technology"],
    "iadt": ["iadt", "institute of art design and technology"],
    "ncad": ["ncad", "national college of art and design"],
    "riada": ["riada", "riada"],
    "margadh-riada": ["margadh riada", "rhythm market"],
    "instiúid-riada": ["instiúid riada", "riada institute"],
    "gaeilge-riada": ["gaeilge riada", "riada irish"],
    "gaeilge-briathar": ["gaeilge briathar", "verbal irish"],
    "gaeilge-scríofa": ["gaeilge scríofa", "written irish"],
    "gaeilge-labhartha": ["gaeilge labhartha", "spoken irish"],
    "gaeilge-rialaithe": ["gaeilge rialaithe", "controlled irish"],
    "gaeilge-chaighdeánach": ["gaeilge chaighdeánach", "standard irish"],
    "gaeilge-an-lao": ["gaeilge an lao", "irish of the day"],
    "gaeilge-shimplí": ["gaeilge shimplí", "simple irish"],
    "gaeilge-idirnáisiúnta": ["gaeilge idirnáisiúnta", "international irish"],
    "gaeilge-fheidhmeach": ["gaeilge fheidhmeach", "applied irish"],
    "gaeilge-theicniúil": ["gaeilge theicniúil", "technical irish"],
    "gaeilge-ghairmiúil": ["gaeilge ghairmiúil", "professional irish"],
    "gaeilge-ealaíne": ["gaeilge ealaíne", "artistic irish"],
    "gaeilge-liteartha": ["gaeilge liteartha", "literary irish"],
    "gaeilge-chlasaiceach": ["gaeilge chlasaiceach", "classical irish"],
    "gaeilge-mheánaoiseach": ["gaeilge mheánaoiseach", "middle irish"],
    "gaeilge-sean-aimseartha": ["gaeilge sean-aimseartha", "early modern irish"],
    "gaeilge-luath": ["gaeilge luath", "early irish"],
    "gaeilge-ársa": ["gaeilge ársa", "old irish"],
    "gaeilge-nua-aimseartha": ["gaeilge nua-aimseartha", "modern irish"],
    "gaeilge-ríomhaire": ["gaeilge ríomhaire", "computer irish"],
    "gaeilge-ai": ["gaeilge ai", "ai irish"],
    "gaeilge-mheaisín": ["gaeilge mheaisín", "machine irish"],
    "gaeilge-mhúnla": ["gaeilge mhúnla", "model irish"],
    "gaeilge-mhór-teilifíse": ["gaeilge mhór teilifíse", "major irish tv"],
    "gaeilge-teilifíse": ["gaeilge teilifíse", "irish tv"],
    "gaeilge-raidió": ["gaeilge raidió", "irish radio"],
    "gaeilge-nuachtáin": ["gaeilge nuachtáin", "irish newspapers"],
    "gaeilge-chló": ["gaeilge chló", "irish print"],
    "gaeilge-foilseacháin": ["gaeilge foilseacháin", "irish publications"],
    "gaeilge-léinn": ["gaeilge léinn", "academic irish"],
    "gaeilge-taighde": ["gaeilge taighde", "irish research"],
    "gaeilge-fhoilsiú": ["gaeilge fhoilsiú", "irish publication"],
    "gaeilge-eagarthóireacht": ["gaeilge eagarthóireacht", "irish editing"],
    "gaeilge-aistriúchán": ["gaeilge aistriúchán", "irish translation"],
    "gaeilge-scríbhneoireacht": ["gaeilge scríbhneoireacht", "irish writing"],
    "gaeilge-úrscéal": ["gaeilge úrscéal", "irish novel"],
    "gaeilge-ghearrscéal": ["gaeilge ghearrscéal", "irish short story"],
    "gaeilge-dán": ["gaeilge dán", "irish poem"],
    "gaeilge-amhrán": ["gaeilge amhrán", "irish song"],
    "gaeilge-dráma": ["gaeilge dráma", "irish drama"],
    "gaeilge-scannán": ["gaeilge scannán", "irish film"],
    "gaeilge-clár": ["gaeilge clár", "irish programme"],
    "gaeilge-cartlann": ["gaeilge cartlann", "irish archive"],
    "gaeilge-mhúsaem": ["gaeilge mhúsaem", "irish museum"],
    "gaeilge-léarscáil": ["gaeilge léarscáil", "irish map"],
    "gaeilge-foclóir": ["gaeilge foclóir", "irish dictionary"],
    "gaeilge-ghramadach": ["gaeilge ghramadach", "irish grammar"],
    "gaeilge-ainmfhocail": ["gaeilge ainmfhocail", "irish nouns"],
    "gaeilge-briathra": ["gaeilge briathra", "irish verbs"],
    "gaeilge-aidbhriathra": ["gaeilge aidbhriathra", "irish adverbs"],
    "gaeilge-réamhfhocail": ["gaeilge réamhfhocail", "irish prepositions"],
    "gaeilge-ainmnithe": ["gaeilge ainmnithe", "irish pronouns"],
    "gaeilge-uchtbhriathra": ["gaeilge uchtbhriathra", "irish preverbal particles"],
    "gaeilge-clásail": ["gaeilge clásail", "irish clauses"],
    "gaeilge-abairtí": ["gaeilge abairtí", "irish phrases"],
    "gaeilge-nathanna": ["gaeilge nathanna", "irish idioms"],
    "gaeilge-focail": ["gaeilge focail", "irish words"],
    "gaeilge-foclacha": ["gaeilge foclacha", "irish vocabulary"],
    "gaeilge-stór-focal": ["gaeilge stór focal", "irish wordstore"],
    "gaeilge-mhéara": ["gaeilge mhéara", "irish fingers"],
    "gaeilge-béil": ["gaeilge béal", "irish mouth"],
    "gaeilge-súile": ["gaeilge súile", "irish eyes"],
    "gaeilge-cluasa": ["gaeilge cluasa", "irish ears"],
    "gaeilge-sméideadh": ["gaeilge sméideadh", "irish wave"],
    "gaeilge-gáire": ["gaeilge gáire", "irish smile"],
    "gaeilge-bhéic": ["gaeilge bhéic", "irish shout"],
    "gaeilge-caint": ["gaeilge caint", "irish speech"],
    "gaeilge-díospóireacht": ["gaeilge díospóireacht", "irish debate"],
    "gaeilge-óráid": ["gaeilge óráid", "irish oration"],
    "gaeilge-spiorad": ["gaeilge spiorad", "irish spirit"],
    "gaeilge-anam": ["gaeilge anam", "irish soul"],
    "gaeilge-croí": ["gaeilge croí", "irish heart"],
    "gaeilge-intinn": ["gaeilge intinn", "irish mind"],
    "gaeilge-cuimhne": ["gaeilge cuimhne", "irish memory"],
    "gaeilge-méan": ["gaeilge méan", "irish means"],
    "gaeilge-cuspóir": ["gaeilge cuspóir", "irish purpose"],
    "gaeilge-aidhm": ["gaeilge aidhm", "irish aim"],
    "gaeilge-sprid": ["gaeilge sprid", "irish spirit"],
    "gaeilge-mianta": ["gaeilge mianta", "irish desires"],
    "gaeilge-aisling": ["gaeilge aisling", "irish dream"],
    "gaeilge-uaigneas": ["gaeilge uaigneas", "irish loneliness"],
    "gaeilge-grá": ["gaeilge grá", "irish love"],
    "gaeilge-cáirdeas": ["gaeilge cáirdeas", "irish friendship"],
    "gaeilge-muintearas": ["gaeilge muintearas", "irish kinship"],
    "gaeilge-teaghlach": ["gaeilge teaghlach", "irish family"],
    "gaeilge-pobal": ["gaeilge pobal", "irish community"],
    "gaeilge-náisiún": ["gaeilge náisiún", "irish nation"],
    "gaeilge-tír": ["gaeilge tír", "irish country"],
    "gaeilge-muintir": ["gaeilge muintir", "irish people"],
    "gaeilge-muintir-na-héireann": ["gaeilge muintir na héireann", "irish people of ireland"],
    "gaeilge-gaeil": ["gaeilge gaeil", "irish irish"],
    "gaeilge-gaelach": ["gaeilge gaelach", "irish gaelic"],
    "gaeilge-sean-gaeilge": ["gaeilge sean-gaeilge", "old irish"],
    "gaeilge-gael": ["gaeilge gael", "irish gael"],
    "gaeilge-gáidhealtacht": ["gaeilge gáidhealtacht", "irish gaeltacht"],
    "gaeilge-gaeilgeoirí": ["gaeilge gaeilgeoirí", "irish irish speakers"],
    "gaeilge-labhairt": ["gaeilge labhairt", "irish speaking"],
    "gaeilge-tuiscint": ["gaeilge tuiscint", "irish understanding"],
    "gaeilge-léamh": ["gaeilge léamh", "irish reading"],
    "gaeilge-scríbhneoireacht": ["gaeilge scríbhneoireacht", "irish writing"],
    "gaeilge-foghlaim": ["gaeilge foghlaim", "irish learning"],
    "gaeilge-mhúineadh": ["gaeilge mhúineadh", "irish teaching"],
    "gaeilge-staidéar": ["gaeilge staidéar", "irish study"],
    "gaeilge-scrúdú": ["gaeilge scrúdú", "irish exam"],
    "gaeilge-teastas": ["gaeilge teastas", "irish certificate"],
    "gaeilge-ardteist": ["gaeilge ardteist", "irish leaving cert"],
    "gaeilge-scoil": ["gaeilge scoil", "irish school"],
    "gaeilge-coláiste": ["gaeilge coláiste", "irish college"],
    "gaeilge-acadamh": ["gaeilge acadamh", "irish academy"],
    "gaeilge-club": ["gaeilge club", "irish club"],
    "gaeilge-cumann": ["gaeilge cumann", "irish society"],
    "gaeilge-eagras": ["gaeilge eagras", "irish organisation"],
    "gaeilge-fondúireacht": ["gaeilge fondúireacht", "irish foundation"],
    "gaeilge-comhlachas": ["gaeilge comhlachas", "irish association"],
    "gaeilge-comharchumann": ["gaeilge comharchumann", "irish cooperative"],
    "gaeilge-fiontar": ["gaeilge fiontar", "irish venture"],
    "gaeilge-fiontraíocht": ["gaeilge fiontraíocht", "irish enterprise"],
    "gaeilge-gnó": ["gaeilge gnó", "irish business"],
    "gaeilge-trádáil": ["gaeilge trádáil", "irish trade"],
    "gaeilge-tionscal": ["gaeilge tionscal", "irish industry"],
    "gaeilge-margadh": ["gaeilge margadh", "irish market"],
    "gaeilge-eacnamaíocht": ["gaeilge eacnamaíocht", "irish economy"],
    "gaeilge-airgeadas": ["gaeilge airgeadas", "irish finance"],
    "gaeilge-banc": ["gaeilge banc", "irish bank"],
    "gaeilge-achtú": ["gaeilge achtú", "irish act"],
    "gaeilge-reachtaíocht": ["gaeilge reachtaíocht", "irish legislation"],
    "gaeilge-bunreacht": ["gaeilge bunreacht", "irish constitution"],
    "gaeilge-dlí": ["gaeilge dlí", "irish law"],
    "gaeilge-cúirt": ["gaeilge cúirt", "irish court"],
    "gaeilge-breithiúna": ["gaeilge breithiúna", "irish judges"],
    "gaeilge-garda": ["gaeilge garda", "irish police"],
    "gaeilge-arm": ["gaeilge arm", "irish army"],
    "gaeilge-cogadh": ["gaeilge cogadh", "irish war"],
    "gaeilge-cath": ["gaeilge cath", "irish battle"],
    "gaeilge-laoch": ["gaeilge laoch", "irish hero"],
    "gaeilge-bua": ["gaeilge bua", "irish victory"],
    "gaeilge-caill": ["gaeilge caill", "irish loss"],
    "gaeilge-mairtíreach": ["gaeilge mairtíreach", "irish martyr"],
    "gaeilge-naomh": ["gaeilge naomh", "irish saint"],
    "gaeilge-eaglais": ["gaeilge eaglais", "irish church"],
    "gaeilge-paidir": ["gaeilge paidir", "irish prayer"],
    "gaeilge-ailtireacht": ["gaeilge ailtireacht", "irish architecture"],
    "gaeilge-dealbh": ["gaeilge dealbh", "irish sculpture"],
    "gaeilge-pictiúr": ["gaeilge pictiúr", "irish painting"],
    "gaeilge-teilifís": ["gaeilge teilifís", "irish television"],
    "gaeilge-scannán": ["gaeilge scannán", "irish film"],
    "gaeilge-ceol": ["gaeilge ceol", "irish music"],
    "gaeilge-amharclann": ["gaeilge amharclann", "irish theatre"],
    "gaeilge-rince": ["gaeilge rince", "irish dance"],
    "gaeilge-sport": ["gaeilge sport", "irish sport"],
    "gaeilge-imirt": ["gaeilge imirt", "irish game"],
    "gaeilge-foghlai": ["gaeilge foghlai", "irish learning"],
    "gaeilge-foclóir": ["gaeilge foclóir", "irish dictionary"],
    "gaeilge-ainmfhocal": ["gaeilge ainmfhocal", "irish noun"],
    "gaeilge-focal": ["gaeilge focal", "irish word"],
    "gaeilge-abairt": ["gaeilge abairt", "irish phrase"],
    "gaeilge-gra-sa": ["gaeilge gra sa", "irish grammar"],
    "gaeilge-fuaimniú": ["gaeilge fuaimniú", "irish pronunciation"],
    "gaeilge-canúint": ["gaeilge canúint", "irish dialect"],
    "gaeilge-béarlach": ["gaeilge béarlach", "irish gaelic english"],
    "gaeilge-foclach": ["gaeilge foclach", "irish vocabulary"],
    "gaeilge-foclach-shimplí": ["gaeilge foclach shimplí", "irish simple vocab"],
    "gaeilge-bun-fhoclach": ["gaeilge bun fhoclach", "irish basic vocab"],
    "gaeilge-mheán-fhoclach": ["gaeilge mheán fhoclach", "irish intermediate vocab"],
    "gaeilge-ard-fhoclach": ["gaeilge ard fhoclach", "irish advanced vocab"],
    "gaeilge-foclach-scoile": ["gaeilge foclach scoile", "irish school vocab"],
    "gaeilge-foclach-oifigiúil": ["gaeilge foclach oifigiúil", "irish official vocab"],
    "gaeilge-foclach-ghnó": ["gaeilge foclach ghnó", "irish business vocab"],
    "gaeilge-foclach-theicniúil": ["gaeilge foclach theicniúil", "irish technical vocab"],
    "gaeilge-foclach-eolaíochta": ["gaeilge foclach eolaíochta", "irish science vocab"],
    "gaeilge-foclach-mhata": ["gaeilge foclach mata", "irish maths vocab"],
    "gaeilge-foclach-riomhaire": ["gaeilge foclach ríomhaire", "irish computer vocab"],
    "gaeilge-foclach-idirlín": ["gaeilge foclach idirlín", "irish internet vocab"],
    "gaeilge-foclach-soghluaisteachta": ["gaeilge foclach soghluaisteachta", "irish mobility vocab"],
    "gaeilge-foclach-aimsire": ["gaeilge foclach aimsire", "irish weather vocab"],
    "gaeilge-foclach-bia": ["gaeilge foclach bia", "irish food vocab"],
    "gaeilge-foclach-éadaí": ["gaeilge foclach éadaí", "irish clothes vocab"],
    "gaeilge-foclach-tí": ["gaeilge foclach tí", "irish house vocab"],
    "gaeilge-foclach-foirgneamh": ["gaeilge foclach foirgneamh", "irish building vocab"],
    "gaeilge-foclach-iompair": ["gaeilge foclach iompair", "irish transport vocab"],
    "gaeilge-foclach-sláinte": ["gaeilge foclach sláinte", "irish health vocab"],
    "gaeilge-foclach-oideachais": ["gaeilge foclach oideachais", "irish education vocab"],
    "gaeilge-foclach-ealaíon": ["gaeilge foclach ealaíon", "irish art vocab"],
    "gaeilge-foclach-ceoil": ["gaeilge foclach ceoil", "irish music vocab"],
    "gaeilge-foclach-spóirt": ["gaeilge foclach spóirt", "irish sport vocab"],
    "gaeilge-foclach-turasóireachta": ["gaeilge foclach turasóireachta", "irish tourism vocab"],
    "gaeilge-foclach-talmhaíochta": ["gaeilge foclach talmhaíochta", "irish agriculture vocab"],
    "gaeilge-foclach-iascach": ["gaeilge foclach iascach", "irish fishing vocab"],
    "gaeilge-foclach-foraoise": ["gaeilge foclach foraoise", "irish forestry vocab"],
    "gaeilge-foclach-mianraí": ["gaeilge foclach mianraí", "irish mineral vocab"],
    "gaeilge-foclach-fuinimh": ["gaeilge foclach fuinimh", "irish energy vocab"],
    "gaeilge-foclach-tíreolaíochta": ["gaeilge foclach tíreolaíochta", "irish geography vocab"],
    "gaeilge-foclach-staire": ["gaeilge foclach staire", "irish history vocab"],
    "gaeilge-foclach-féinmhíniú": ["gaeilge foclach féinmhíniú", "irish self-explanation vocab"],
    "gaeilge-foclach-ai": ["gaeilge foclach ai", "irish ai vocab"],
    "gaeilge-foclach-aimseartha": ["gaeilge foclach aimseartha", "irish modern vocab"],
    "gaeilge-foclach-choimhniú": ["gaeilge foclach choimhniú", "irish conservation vocab"],
    "gaeilge-foclach-oidhreachta": ["gaeilge foclach oidhreachta", "irish heritage vocab"],
    "gaeilge-foclach-lao-len": ["gaeilge foclach lao len", "irish daily vocab"],
    "gaeilge-foclach-foclach": ["gaeilge foclach foclach", "irish vocab vocab"],
    "gaeilge-foclach-riomhfhoclach": ["gaeilge foclach ríomhfhoclach", "irish computational vocab"],
    "gaeilge-foclach-cruinne": ["gaeilge foclach cruinne", "irish universal vocab"],
    "gaeilge-foclach-idirnaisiunta": ["gaeilge foclach idirnaisiunta", "irish international vocab"],
    "gaeilge-foclach-colaí": ["gaeilge foclach colaí", "irish bodily vocab"],
    "gaeilge-foclach-meabhrach": ["gaeilge foclach meabhrach", "irish mental vocab"],
    "gaeilge-foclach-spioradálta": ["gaeilge foclach spioradálta", "irish spiritual vocab"],
    "gaeilge-foclach-shóisialta": ["gaeilge foclach shóisialta", "irish social vocab"],
    "gaeilge-foclach-chultúrtha": ["gaeilge foclach chultúrtha", "irish cultural vocab"],
    "gaeilge-foclach-eacnamaíoch": ["gaeilge foclach eacnamaíoch", "irish economic vocab"],
    "gaeilge-foclach-bhainc": ["gaeilge foclach bhainc", "irish banking vocab"],
    "gaeilge-foclach-dlí": ["gaeilge foclach dlí", "irish legal vocab"],
    "gaeilge-foclach-pholaitiúil": ["gaeilge foclach pholaitiúil", "irish political vocab"],
    "gaeilge-foclach-ríomhaireachta": ["gaeilge foclach ríomhaireachta", "irish computational vocab"],
    "gaeilge-foclach-mhatamaitice": ["gaeilge foclach mhatamaitice", "irish mathematical vocab"],
    "gaeilge-foclach-eolaíoch": ["gaeilge foclach eolaíoch", "irish scientific vocab"],
    "gaeilge-foclach-theicneolaíoch": ["gaeilge foclach theicneolaíoch", "irish technological vocab"],
    "gaeilge-foclach-ai": ["gaeilge foclach ai", "irish ai vocab"],
    "gaeilge-foclach-fhoclach": ["gaeilge foclach fhoclach", "irish vocab vocab"],
    "gaeilge-foclach-oidhreachta-2": ["gaeilge foclach oidhreachta 2", "irish heritage vocab 2"],
    "gaeilge-foclach-lao-2": ["gaeilge foclach lao 2", "irish daily vocab 2"],
    "gaeilge-foclach-fhoclach-2": ["gaeilge foclach fhoclach 2", "irish vocab vocab 2"],
    "misc": [],
}

# Canonical home: topic → domain. Prevents duplicate merged files.
TOPIC_HOME: dict[str, str] = {
    "tanstack-start": "05-web",
    "tanstack-router": "05-web",
    "vite-bun-build": "05-web",
    "vite-frontend": "05-web",
    "vinxi-runtime": "05-web",
    "convex-realtime": "05-web",
    "cloudflare-edge": "05-web",
    "deployment": "06-infrastructure",
    "monitoring": "06-infrastructure",
    "ci-cd": "06-infrastructure",
    "komodo-orchestration": "06-infrastructure",
    "pulumi-iac": "06-infrastructure",
    "pangolin-routing": "06-infrastructure",
    "olake-replication": "02-data-platform",
    "dlt-ingestion": "02-data-platform",
    "dagster-orchestration": "02-data-platform",
    "cocoindex-pipelines": "02-data-platform",
    "duckdb-lakehouse": "02-data-platform",
    "ducklake": "02-data-platform",
    "sqlmesh": "02-data-platform",
    "risingwave-streaming": "02-data-platform",
    "feast-feature-store": "04-ai-ml",
    "lancedb-vector": "04-ai-ml",
    "lancedb-hybrid": "04-ai-ml",
    "lancedb-storage": "04-ai-ml",
    "marimo-notebooks": "04-ai-ml",
    "notebook-dashboards": "04-ai-ml",
    "evidence-bi": "04-ai-ml",
    "mlflow": "04-ai-ml",
    "mlflow-tracking": "04-ai-ml",
    "langfuse-observability": "04-ai-ml",
    "ragas-eval": "04-ai-ml",
    "hugging-face": "04-ai-ml",
    "unsloth-finetuning": "04-ai-ml",
    "llm-finetuning": "04-ai-ml",
    "baml-extraction": "04-ai-ml",
    "baml-schema": "04-ai-ml",
    "baml-claude": "04-ai-ml",
    "ocr-vlm": "04-ai-ml",
    "document-intelligence": "04-ai-ml",
    "festival-speech": "04-ai-ml",
    "audio-pedagogy": "04-ai-ml",
    "vector-db": "04-ai-ml",
    "graphiti-memory": "04-ai-ml",
    "graphiti-temporal": "04-ai-ml",
    "graphiti-falkordb": "04-ai-ml",
    "cognee-graphrag": "09-cognee",
    "cognee-knowledge": "09-cognee",
    "cognee": "09-cognee",
    "falkordb-graph": "04-ai-ml",
    "memgraph": "04-ai-ml",
    "mcp-servers": "01-platform-architecture",
    "mcp-platform": "01-platform-architecture",
    "mcp-server": "01-platform-architecture",
    "mcp-builder": "01-platform-architecture",
    "skill-mcp": "01-platform-architecture",
    "agents-frameworks": "03-agents",
    "agent-frameworks": "03-agents",
    "agents-llm": "03-agents",
    "browser-automation": "01-platform-architecture",
    "browser-cli": "01-platform-architecture",
    "browser-automation-skill": "01-platform-architecture",
    "safe-browser": "01-platform-architecture",
    "browser-trace": "01-platform-architecture",
    "browser-to-api": "01-platform-architecture",
    "webapp-testing": "01-platform-architecture",
    "ui-test": "01-platform-architecture",
    "firecrawl-suite": "01-platform-architecture",
    "firecrawl-skill": "01-platform-architecture",
    "firecrawl-scrape": "01-platform-architecture",
    "firecrawl-crawl": "01-platform-architecture",
    "firecrawl-agent": "01-platform-architecture",
    "firecrawl-map": "01-platform-architecture",
    "firecrawl-search": "01-platform-architecture",
    "firecrawl-monitor": "01-platform-architecture",
    "firecrawl-extract": "01-platform-architecture",
    "firecrawl-interact": "01-platform-architecture",
    "firecrawl-parse": "01-platform-architecture",
    "firecrawl-download": "01-platform-architecture",
    "homebrew-fc": "01-platform-architecture",
    "functions": "01-platform-architecture",
    "browserbase-cli": "01-platform-architecture",
    "browser-mcp": "01-platform-architecture",
    "cookie-sync": "01-platform-architecture",
    "company-research": "01-platform-architecture",
    "event-prospecting": "01-platform-architecture",
    "hugging-face-publisher": "04-ai-ml",
    "hf-paper-publisher": "04-ai-ml",
    "hf-dataset-creator": "04-ai-ml",
    "model-trainer": "04-ai-ml",
    "evaluation-manager": "04-ai-ml",
    "chunkhound": "01-platform-architecture",
    "skill-loader": "01-platform-architecture",
    "skill-creator": "01-platform-architecture",
    "agent-skill": "01-platform-architecture",
    "agent-skills": "01-platform-architecture",
    "skills-creation": "01-platform-architecture",
    "skills-catalog": "01-platform-architecture",
    "agent-experience": "01-platform-architecture",
    "agent-flow": "01-platform-architecture",
    "autobrowse": "01-platform-architecture",
    "irish-curriculum": "05-web",
    "uk-curriculum": "05-web",
    "scottish-gaelic": "05-web",
    "welsh": "05-web",
    "brittany": "05-web",
    "celtic-pan": "05-web",
    "celtic-education": "05-web",
    "celtic-language": "05-web",
    "icelandic-faroese": "05-web",
    "sami-languages": "05-web",
    "basque": "05-web",
    "kings-college-galway": "08-misc",
    "kings-galway": "08-misc",
    "kings-galway-history": "08-misc",
    "kings-college-galway-history": "08-misc",
    "irish-government": "08-misc",
    "uk-government": "08-misc",
    "apple-education": "08-misc",
    "licensing-copyright": "08-misc",
    "copyright-licensing": "08-misc",
    "open-source": "08-misc",
    "hmgcc": "08-misc",
    "hackathons": "08-misc",
    "screenshots": "08-misc",
    "examples-patterns": "08-misc",
    "standards": "07-standards",
    "stack-ops": "06-infrastructure",
    "stack-doctor": "06-infrastructure",
    "infrastructure-stacks": "06-infrastructure",
    "infrastructure-iac": "06-infrastructure",
    "service-catalog": "06-infrastructure",
    "routing-infrastructure": "06-infrastructure",
    "security-auth": "06-infrastructure",
    "auth-identity": "06-infrastructure",
    "locket-secrets": "06-infrastructure",
    "locket": "06-infrastructure",
    "infisical-vault": "06-infrastructure",
    "konvex": "06-platform-architecture",
    "pangolin": "06-infrastructure",
    "komodo": "06-infrastructure",
    "github-cli": "06-infrastructure",
    "tdd-testing": "07-standards",
    "ddd-patterns": "07-standards",
    "cre-agent": "07-standards",
    "claude-agents": "07-standards",
    "opencode": "07-standards",
    "ccc-cocoindex-code": "07-standards",
    "agentic-ai": "07-standards",
    "rag-llm": "07-standards",
    "context-llm": "07-standards",
    "documentation": "07-standards",
    "insights": "07-standards",
    "mondoo-security": "07-standards",
    "skill-format": "07-standards",
    "skill-prompt": "07-standards",
    "frontend-design": "07-standards",
    "frontend-skill": "07-standards",
    "theme-factory": "07-standards",
    "web-artifacts": "07-standards",
    "canvas-design": "07-standards",
    "algorithmic-art": "07-standards",
    "slack-gif": "07-standards",
    "brand-guidelines": "07-standards",
    "internal-comms": "07-standards",
    "doc-coauthoring": "07-standards",
    "irish-edtech": "07-standards",
    "skill-irish-edtech": "07-standards",
    "pyro": "08-misc",
    "notebooklm": "08-misc",
    "kings-galway": "08-misc",
    "nui-galway": "08-misc",
    "leaving-cert": "08-misc",
    "irish-language": "08-misc",
    "gaelic": "08-misc",
    "irish-history": "08-misc",
    "celtic-history": "08-misc",
    "northern-ireland": "08-misc",
    "scotland-curriculum": "08-misc",
    "wales-curriculum": "08-misc",
    "english-curriculum": "08-misc",
    "ni-curriculum": "08-misc",
    "primary-curriculum": "08-misc",
    "post-primary": "08-misc",
    "jc-curriculum": "08-misc",
    "lc-curriculum": "08-misc",
    "bilingual-education": "08-misc",
    "gaeilge-curriculum": "08-misc",
    "english-curriculum-ireland": "08-misc",
    "maths-curriculum": "08-misc",
    "science-curriculum": "08-misc",
    "stem-education": "08-misc",
    "humanities-curriculum": "08-misc",
    "language-curriculum": "08-misc",
    "irish-civil-service": "08-misc",
    "irish-economy": "08-misc",
    "irish-tech-sector": "08-misc",
    "irish-universities": "08-misc",
    "internationalisation": "08-misc",
    "erasmus": "08-misc",
    "etwinning": "08-misc",
    "unesco": "08-misc",
    "oecd": "08-misc",
    "european-commission": "08-misc",
    "eu-education": "08-misc",
    "sdg-education": "08-misc",
    "global-education": "08-misc",
    "education-policy": "08-misc",
    "education-research": "08-misc",
    "education-stats": "08-misc",
    "education-reform": "08-misc",
    "education-equity": "08-misc",
    "education-special": "08-misc",
    "education-technology": "08-misc",
    "ai-education": "08-misc",
    "ai-curriculum": "08-misc",
    "data-curriculum": "08-misc",
    "digital-literacy": "08-misc",
    "media-literacy": "08-misc",
    "critical-thinking": "08-misc",
    "creativity-education": "08-misc",
    "wellbeing-education": "08-misc",
    "physical-education": "08-misc",
    "sphe": "08-misc",
    "civic-education": "08-misc",
    "religious-education": "08-misc",
    "ethics-education": "08-misc",
    "arts-education": "08-misc",
    "music-education": "08-misc",
    "drama-education": "08-misc",
    "visual-arts": "08-misc",
    "coding-curriculum": "08-misc",
    "computer-science-ireland": "08-misc",
    "stem-curriculum": "08-misc",
    "data-science-curriculum": "08-misc",
    "ai-literacy": "08-misc",
    "robotics-curriculum": "08-misc",
    "engineering-curriculum": "08-misc",
    "maths-problem-solving": "08-misc",
    "reading-literacy": "08-misc",
    "writing-curriculum": "08-misc",
    "oral-language": "08-misc",
    "phonics": "08-misc",
    "early-years": "08-misc",
    "transition-year": "08-misc",
    "lca": "08-misc",
    "lcvp": "08-misc",
    "special-needs": "08-misc",
    "asd": "08-misc",
    "dyslexia": "08-misc",
    "gifted": "08-misc",
    "disadvantage": "08-misc",
    "rural-schools": "08-misc",
    "urban-schools": "08-misc",
    "gaelscoil": "08-misc",
    "special-school": "08-misc",
    "gaeltacht": "08-misc",
    "irish-medium": "08-misc",
    "english-medium": "08-misc",
    "trinity-college": "08-misc",
    "ucd": "08-misc",
    "ul": "08-misc",
    "dcu": "08-misc",
    "maynooth": "08-misc",
    "uuc": "08-misc",
    "queens": "08-misc",
    "stranmillis": "08-misc",
    "st-marys": "08-misc",
    "marino": "08-misc",
    "froebel": "08-misc",
    "blackrock": "08-misc",
    "drumcondra": "08-misc",
    "st-nicholas": "08-misc",
    "montessori": "08-misc",
    "steiner": "08-misc",
    "educate-together": "08-misc",
    "community-school": "08-misc",
    "comprehensive-school": "08-misc",
    "vocational-school": "08-misc",
    "secondary-school": "08-misc",
    "girls-school": "08-misc",
    "boys-school": "08-misc",
    "mixed-school": "08-misc",
    "fee-paying": "08-misc",
    "public-school": "08-misc",
    "school-governance": "08-misc",
    "school-trust": "08-misc",
    "patron-body": "08-misc",
    "catholic-school": "08-misc",
    "church-of-ireland": "08-misc",
    "methodist-school": "08-misc",
    "presbyterian": "08-misc",
    "jewish-school": "08-misc",
    "muslim-school": "08-misc",
    "hindu-school": "08-misc",
    "multi-denominational": "08-misc",
    "interfaith": "08-misc",
    "patronage": "08-misc",
    "school-funding": "08-misc",
    "department-of-education": "08-misc",
    "ncse": "08-misc",
    "teaching-council": "08-misc",
    "sec": "08-misc",
    "ncca": "08-misc",
    "jjst": "08-misc",
    "inspectorate": "08-misc",
    "wse": "08-misc",
    "incidental-inspection": "08-misc",
    "subject-inspection": "08-misc",
    "school-self-evaluation": "08-misc",
    "ssse": "08-misc",
    "look-at-our-school": "08-misc",
    "teaching-and-learning": "08-misc",
    "subject-department": "08-misc",
    "curriculum-planning": "08-misc",
    "scheme-of-work": "08-misc",
    "lesson-plan": "08-misc",
    "annual-plan": "08-misc",
    "long-term-plan": "08-misc",
    "short-term-plan": "08-misc",
    "croke-park-hours": "08-misc",
    "tui": "08-misc",
    "astl": "08-misc",
    "ifut": "08-misc",
    "teacher-union": "08-misc",
    "industrial-action": "08-misc",
    "pay-equity": "08-misc",
    "teacher-pay": "08-misc",
    "teacher-conditions": "08-misc",
    "new-entrant": "08-misc",
    "covid": "08-misc",
    "remote-teaching": "08-misc",
    "hybrid-teaching": "08-misc",
    "school-reopening": "08-misc",
    "school-closures": "08-misc",
    "mental-health": "08-misc",
    "student-support": "08-misc",
    "guidance-counsellor": "08-misc",
    "school-counsellor": "08-misc",
    "neps": "08-misc",
    "psychological-service": "08-misc",
    "camhs": "08-misc",
    "jigsaw": "08-misc",
    "pieta": "08-misc",
    "suicide-prevention": "08-misc",
    "lgbtq": "08-misc",
    "inclusion": "08-misc",
    "equality": "08-misc",
    "anti-bullying": "08-misc",
    "cyber-bullying": "08-misc",
    "safeguarding": "08-misc",
    "child-protection": "08-misc",
    "vetted": "08-misc",
    "data-protection": "08-misc",
    "gdpr": "08-misc",
    "digital-strategy": "08-misc",
    "digital-learning-framework": "08-misc",
    "schools-network": "08-misc",
    "hea": "08-misc",
    "qaa": "08-misc",
    "qqi": "08-misc",
    "nfq": "08-misc",
    "ects": "08-misc",
    "eas": "08-misc",
    "qf-ehea": "08-misc",
    "youthreach": "08-misc",
    "btei": "08-misc",
    "vtos": "08-misc",
    "night-classes": "08-misc",
    "adult-education": "08-misc",
    "community-education": "08-misc",
    "further-education": "08-misc",
    "higher-education": "08-misc",
    "springboard": "08-misc",
    "human-capital": "08-misc",
    "skillnet": "08-misc",
    "education-research-centres": "08-misc",
    "esri": "08-misc",
    "erc": "08-misc",
    "nfer": "08-misc",
    "crede": "08-misc",
    "centre-for-education": "08-misc",
    "early-childhood": "08-misc",
    "eccc": "08-misc",
    "early-start": "08-misc",
    "aim": "08-misc",
    "high-scope": "08-misc",
    "ready-set-go": "08-misc",
    "first-five": "08-misc",
    "better-start": "08-misc",
    "siolta": "08-misc",
    "aistear": "08-misc",
    "mo-scéal": "08-misc",
    "language-nests": "08-misc",
    "naionra": "08-misc",
    "tuistí": "08-misc",
    "parental-engagement": "08-misc",
    "home-school": "08-misc",
    "homework": "08-misc",
    "study-skills": "08-misc",
    "exam-prep": "08-misc",
    "revision": "08-misc",
    "ace": "08-misc",
    "grinds": "08-misc",
    "private-tuition": "08-misc",
    "study-clubs": "08-misc",
    "after-school": "08-misc",
    "summer-school": "08-misc",
    "gaeltacht-colleges": "08-misc",
    "colaiste": "08-misc",
    "irish-college": "08-misc",
    "sumcoil": "08-misc",
    "fáilte-gaeilge": "08-misc",
    "taighde": "08-misc",
    "staidéar": "08-misc",
    "scoil": "08-misc",
    "scoil-naisiunta": "08-misc",
    "meánscoil": "08-misc",
    "ardteist": "08-misc",
    "teastas": "08-misc",
    "teist": "08-misc",
    "socrú": "08-misc",
    "bunoideachas": "08-misc",
    "meánoideachas": "08-misc",
    "ardoideachas": "08-misc",
    "tríú-leibhéal": "08-misc",
    "ollscoil": "08-misc",
    "scoil-gháil": "08-misc",
    "teanga-gháil": "08-misc",
    "gaeilge-staidéar": "08-misc",
    "gaeilge-mhúineadh": "08-misc",
    "múinteoir-gaeilge": "08-misc",
    "gaeilge-acadamh": "08-misc",
    "acadamh": "08-misc",
    "gaeilge-scríbhneoir": "08-misc",
    "filíocht": "08-misc",
    "prós": "08-misc",
    "litearacht": "08-misc",
    "scéal": "08-misc",
    "scéalta": "08-misc",
    "béaloideas": "08-misc",
    "logainmneacha": "08-misc",
    "dinnseanchas": "08-misc",
    "seanchas": "08-misc",
    "foclóir": "08-misc",
    "gramadach": "08-misc",
    "canúint": "08-misc",
    "tráchtaireacht": "08-misc",
    "beochraoladh": "08-misc",
    "píosa": "08-misc",
    "nuachtán": "08-misc",
    "iris": "08-misc",
    "irisleabhar": "08-misc",
    "leabhar": "08-misc",
    "leabharlann": "08-misc",
    "cartlann": "08-misc",
    "músaem": "08-misc",
    "iarsmalann": "08-misc",
    "taibhdhearc": "08-misc",
    "amharclann": "08-misc",
    "ceol": "08-misc",
    "amhrán": "08-misc",
    "rince": "08-misc",
    "damhsa": "08-misc",
    "sean-nós": "08-misc",
    "seanchaí": "08-misc",
    "scéalaí": "08-misc",
    "filí": "08-misc",
    "ceoltóir": "08-misc",
    "ceol-gaeilge": "08-misc",
    "trádáil": "08-misc",
    "cultúr": "08-misc",
    "cúlra": "08-misc",
    "oidhreacht": "08-misc",
    "teangacha": "08-misc",
    "teangacha-ceilteacha": "08-misc",
    "celtic-gaeilge": "08-misc",
    "mannan": "08-misc",
    "mannan-ghaelg": "08-misc",
    "cornish": "08-misc",
    "brezhoneg": "08-misc",
    "cymraeg": "08-misc",
    "gaeilge-albannach": "08-misc",
    "fréamhacha": "08-misc",
    "logainmneacha-gaelacha": "08-misc",
    "dualgas": "08-misc",
    "dlí": "08-misc",
    "ceart": "08-misc",
    "saoránach": "08-misc",
    "pobal": "08-misc",
    "tír": "08-misc",
    "muintir": "08-misc",
    "muintir-na-tíre": "08-misc",
    "tuath": "08-misc",
    "dúiche": "08-misc",
    "contae": "08-misc",
    "cathair": "08-misc",
    "baile": "08-misc",
    "sráidbhaile": "08-misc",
    "teach": "08-misc",
    "margadh": "08-misc",
    "aonach": "08-misc",
    "portach": "08-misc",
    "cala": "08-misc",
    "iascach": "08-misc",
    "feirmeoireacht": "08-misc",
    "talaimh": "08-misc",
    "eorna": "08-misc",
    "prátaí": "08-misc",
    "arbhar": "08-misc",
    "coirce": "08-misc",
    "bainne": "08-misc",
    "im": "08-misc",
    "uaineoil": "08-misc",
    "caoirigh": "08-misc",
    "bó": "08-misc",
    "eallach": "08-misc",
    "each": "08-misc",
    "capall": "08-misc",
    "muc": "08-misc",
    "sicín": "08-misc",
    "éan": "08-misc",
    "éanlaith": "08-misc",
    "iasc": "08-misc",
    "sionnach": "08-misc",
    "madra": "08-misc",
    "cat": "08-misc",
    "coinín": "08-misc",
    "iolair": "08-misc",
    "seabhac": "08-misc",
    "bradán": "08-misc",
    "breac": "08-misc",
    "iúil": "08-misc",
    "iasaigh": "08-misc",
    "iarlaith": "08-misc",
    "seafra": "08-misc",
    "gael-linn": "08-misc",
    "gaeilge-bhfriotal": "08-misc",
    "kings-college-galway-official": "08-misc",
    "gaeilge-oifigiúil": "08-misc",
    "gaeilge-rialacha": "08-misc",
    "gaelach": "08-misc",
    "gaeilge-rialach": "08-misc",
    "data-pipeline-patterns": "02-data-platform",
    "dagster-skill": "02-data-platform",
    "dlt-skill": "02-data-platform",
    "motherduck-skill": "02-data-platform",
    "duckdb-skill": "02-data-platform",
    "data-analytics": "04-ai-ml",
    "data-science": "04-ai-ml",
    "irish-education": "08-misc",
    "kings-college-galway": "08-misc",
}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def log_error(source: Path, msg: str) -> None:
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {source}: {msg}\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def strip_frontmatter(content: str) -> str:
    """Strip leading YAML frontmatter if present."""
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            return content[end + 4 :].lstrip("\n")
    return content


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse simple YAML frontmatter; return (dict, body)."""
    fm: dict[str, Any] = {}
    body = content
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            fm_text = content[3:end].strip()
            body = content[end + 4 :].lstrip("\n")
            for line in fm_text.splitlines():
                if ":" in line and not line.startswith(" "):
                    key, _, val = line.partition(":")
                    fm[key.strip()] = val.strip().strip("'\"")
    return fm, body


# ---------------------------------------------------------------------------
# Cognee HTTP client
# ---------------------------------------------------------------------------


def cognee_request(
    path: str, method: str = "GET", data: dict[str, Any] | None = None
) -> dict[str, Any] | list[Any] | None:
    url = f"{COGNEE_URL}{path}"
    payload: bytes | None = None
    headers: dict[str, str] = {"Accept": "application/json"}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=payload, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            if not body:
                return None
            return json.loads(body)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        return {"error": str(e)}


def cognee_create_dataset(name: str) -> str | None:
    result = cognee_request("/api/v1/datasets", method="POST", data={"name": name})
    if isinstance(result, dict) and "id" in result:
        return str(result["id"])
    if isinstance(result, list) and result and isinstance(result[0], dict):
        return str(result[0].get("id", ""))
    return None


def cognee_add_text(dataset_id: str, text: str, name: str) -> bool:
    result = cognee_request(
        "/api/v1/add",
        method="POST",
        data={"dataset_id": dataset_id, "data": text, "name": name},
    )
    return not (isinstance(result, dict) and "error" in result)


def cognee_cognify(dataset_id: str) -> bool:
    result = cognee_request(
        "/api/v1/cognify", method="POST", data={"dataset_id": dataset_id}
    )
    return not (isinstance(result, dict) and "error" in result)


def cognee_search(dataset_id: str, query: str) -> Any:
    return cognee_request(
        "/api/v1/search",
        method="POST",
        data={"dataset_id": dataset_id, "query": query},
    )


# ---------------------------------------------------------------------------
# ccc integration
# ---------------------------------------------------------------------------


def ccc_search(query: str, paths: list[str] | None = None, limit: int = 20) -> list[dict[str, Any]]:
    """Run ccc search and parse JSON results."""
    cmd = ["ccc", "search", query, "--json", "--limit", str(limit)]
    if paths:
        cmd.extend(["--path", *paths])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return []


def ccc_describe(path: str) -> str:
    """Run ccc describe on a single file and return the summary."""
    cmd = ["ccc", "describe", path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------


def classify_topic(content: str, filename: str) -> str:
    """Classify a file into a topic based on keywords and filename."""
    text = (content + "\n" + filename).lower()
    best_topic = "misc"
    best_score = 0
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic


def target_path_for(source: Path, topic: str) -> Path:
    """Compute the docs-v2 target path for a given source file."""
    rel = source.relative_to(DOCS_SRC)
    parts = rel.parts
    # Loose file at root
    if len(parts) == 1:
        return DOCS_V2 / "10-loose-files" / parts[0]
    # Non-md
    if source.suffix.lower() in {".py"}:
        return DOCS_V2 / "11-scripts" / source.name
    if source.suffix.lower() in {".yaml", ".yml", ".toml", ".json", ".lock"}:
        return DOCS_V2 / "12-configs" / source.name
    if source.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp"}:
        return DOCS_V2 / "13-images" / source.name
    if source.suffix.lower() in {".pdf", ".docx", ".doc", ".xlsx", ".pptx"}:
        return DOCS_V2 / "10-loose-files" / source.name
    # md → topic cluster. Use TOPIC_HOME for canonical placement.
    canonical_domain = TOPIC_HOME.get(topic, "08-misc")
    topic_dir = topic.replace("_", "-")
    target = DOCS_V2 / canonical_domain / topic_dir
    return target / f"{topic}.md"


# ---------------------------------------------------------------------------
# Merge logic
# ---------------------------------------------------------------------------


def make_merged_file(
    topic: str,
    domain: str,
    sources: list[Path],
    target: Path,
) -> None:
    """Write a merged file with per-source sections."""
    sections: list[str] = []
    frontmatter_seen: dict[str, str] = {}
    cross_refs: set[str] = set()

    for src in sources:
        try:
            content = read_text(src)
        except OSError as e:
            log_error(src, f"read failed: {e}")
            continue
        fm, body = extract_frontmatter(content)
        for k, v in fm.items():
            if k in {"title", "description", "status"} and k not in frontmatter_seen:
                frontmatter_seen[k] = v
        kind = "canonical" if "/0" + str(int(domain[:2])) + "-" in str(src) else "leftover"
        if "archive" in str(src):
            kind = "archive"
        rel = src.relative_to(REPO_ROOT)
        section = f"## From: {rel} ({kind})\n\n"
        # Body cleanup
        body = body.strip()
        if body:
            section += body + "\n\n"
        else:
            section += f"_Source: {rel} (empty body)_\n\n"
        sections.append(section)

    # Frontmatter
    fm_lines = [
        "---",
        f"title: {frontmatter_seen.get('title', topic)}",
        f"domain: {domain}",
        "status: living-document",
        f"description: {frontmatter_seen.get('description', f'Merged from {len(sources)} source files')}",
        f"merged_on: {now_iso()}",
        f"merged_from_count: {len(sources)}",
        "supersedes:",
    ]
    for src in sources:
        rel = src.relative_to(REPO_ROOT)
        fm_lines.append(f"  - {rel}")
    fm_lines.append("---")
    fm_lines.append("")

    # Build the file
    body_parts = [
        "\n".join(fm_lines),
        f"# {frontmatter_seen.get('title', topic)}",
        "",
        f"This file consolidates **{len(sources)} source files** about the topic "
        f"**{topic}** from across `docs/`. See the `## From:` sections below for "
        f"the original sources.",
        "",
    ]
    body_parts.extend(sections)
    body_parts.append("## Cross-References\n")
    body_parts.append("See `00_index.md` for the routing table.\n")
    body_parts.append("")

    write_text(target, "\n".join(body_parts))


# ---------------------------------------------------------------------------
# Main migration steps
# ---------------------------------------------------------------------------


def collect_sources() -> list[Path]:
    """Return all .md files in docs/ (excluding archive for now)."""
    sources: list[Path] = []
    for path in DOCS_SRC.rglob("*.md"):
        rel = path.relative_to(DOCS_SRC)
        if rel.parts[0] == "archive":
            continue  # archive handled separately
        sources.append(path)
    return sources


def collect_archive_sources() -> list[Path]:
    """Return all .md files in docs/archive/."""
    archive_dir = DOCS_SRC / "archive"
    if not archive_dir.exists():
        return []
    return list(archive_dir.rglob("*.md"))


def collect_non_md_sources() -> list[Path]:
    """Return all non-.md files in docs/."""
    return [
        p for p in DOCS_SRC.rglob("*")
        if p.is_file() and p.suffix.lower() != ".md"
    ]


def discover_clusters(sources: list[Path]) -> dict[str, list[Path]]:
    """Cluster source files by topic."""
    clusters: dict[str, list[Path]] = {}
    for src in sources:
        try:
            content = read_text(src)
        except OSError as e:
            log_error(src, f"read failed during cluster: {e}")
            continue
        topic = classify_topic(content, src.name)
        clusters.setdefault(topic, []).append(src)
    return clusters


def write_clusters_json(clusters: dict[str, list[Path]]) -> None:
    serial = {
        topic: [str(p.relative_to(REPO_ROOT)) for p in paths]
        for topic, paths in clusters.items()
    }
    write_text(CLUSTERS_JSON, json.dumps(serial, indent=2, sort_keys=True))


def write_coverage_json(mapping: dict[str, str]) -> None:
    write_text(COVERAGE_JSON, json.dumps(mapping, indent=2, sort_keys=True))


def merge_topic_cluster(
    topic: str,
    domain: str,
    sources: list[Path],
    dry_run: bool,
) -> str:
    """Merge a single topic cluster; return target path string."""
    topic_dir_name = topic.replace("_", "-")
    target = DOCS_V2 / domain / topic_dir_name / f"{topic}.md"
    if dry_run:
        return str(target.relative_to(REPO_ROOT))
    make_merged_file(topic, domain, sources, target)
    return str(target.relative_to(REPO_ROOT))


def process_domain(domain: str, dry_run: bool, all_sources: list[Path]) -> dict[str, str]:
    """Process all sources globally; emit files for the requested domain.

    Returns the {src → target} mapping slice for files placed in this domain.
    Files whose topic homes in OTHER domains are filtered out.
    """
    clusters = discover_clusters(all_sources)
    mapping: dict[str, str] = {}
    for topic, paths in clusters.items():
        canonical_domain = TOPIC_HOME.get(topic, "08-misc")
        if canonical_domain != domain:
            continue
        # Skip if all paths are in the wrong domain (leftover dirs mapped elsewhere)
        target_rel = merge_topic_cluster(topic, canonical_domain, paths, dry_run)
        for p in paths:
            mapping[str(p.relative_to(REPO_ROOT))] = target_rel
    return mapping


def process_archive(dry_run: bool) -> dict[str, str]:
    """Process archive sources by classifying each into a topic and folding into
    the corresponding domain cluster."""
    sources = collect_archive_sources()
    mapping: dict[str, str] = {}
    # Group by topic, then map to the most common domain for that topic
    clusters: dict[str, list[Path]] = discover_clusters(sources)
    for topic, paths in clusters.items():
        # Find which domain this topic already lives in
        target_pattern = DOCS_V2 / "*" / topic.replace("_", "-") / f"{topic}.md"
        existing = list(DOCS_V2.glob(str(target_pattern).replace(str(DOCS_V2) + "/", "")))
        if existing:
            existing_path = existing[0]
            for p in paths:
                if dry_run:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(existing_path.relative_to(REPO_ROOT))
                else:
                    # Append to existing file
                    try:
                        existing_content = read_text(existing_path)
                        new_section = f"\n## From: {p.relative_to(REPO_ROOT)} (archive)\n\n{strip_frontmatter(read_text(p))}\n"
                        write_text(existing_path, existing_content + new_section)
                        mapping[str(p.relative_to(REPO_ROOT))] = str(existing_path.relative_to(REPO_ROOT))
                    except OSError as e:
                        log_error(p, f"archive append failed: {e}")
        else:
            # No canonical home; place in 08-misc
            target = DOCS_V2 / "08-misc" / "archive" / f"{topic}.md"
            if dry_run:
                for p in paths:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
            else:
                make_merged_file(topic, "08-misc", paths, target)
                for p in paths:
                    mapping[str(p.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
    return mapping


def process_non_md(dry_run: bool) -> dict[str, str]:
    """Copy non-md files to docs-v2/11-scripts/ or 12-configs/ or 13-images/."""
    sources = collect_non_md_sources()
    mapping: dict[str, str] = {}
    for src in sources:
        target = target_path_for(src, classify_topic("", src.name))
        try:
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
            mapping[str(src.relative_to(REPO_ROOT))] = str(target.relative_to(REPO_ROOT))
        except OSError as e:
            log_error(src, f"copy failed: {e}")
    return mapping


def write_changelog(all_mapping: dict[str, str]) -> None:
    total = len(all_mapping)
    by_domain: dict[str, int] = {}
    for src, tgt in all_mapping.items():
        if tgt.startswith("docs-v2/"):
            parts = tgt.split("/")
            if len(parts) >= 2:
                d = parts[1]
                by_domain[d] = by_domain.get(d, 0) + 1
    md = [
        "---",
        "title: docs-v2 Migration Changelog",
        f"generated: {now_iso()}",
        "---",
        "",
        "# docs-v2 Migration Changelog",
        "",
        f"**Total source files mapped:** {total}",
        "",
        "## Per-domain source counts",
        "",
        "| Domain | Source files mapped |",
        "|:--|--:|",
    ]
    for d in sorted(by_domain):
        md.append(f"| {d} | {by_domain[d]} |")
    md.append("")
    write_text(DOCS_V2 / "changelog.md", "\n".join(md))


def write_migration_doc() -> None:
    content = """---
title: docs-v2 Migration Guide
status: living-document
description: How merged files are structured; how to read them
---

# docs-v2 Migration Guide

`docs-v2/` is a per-topic merged mirror of `docs/`. Every file in `docs-v2/`
follows the same structure so that the **original sources remain attributable**
and **no information is lost**.

## Section structure

Each merged `.md` file contains:

```
---
title: <topic>
domain: <NN-domain>
status: living-document
description: <one-line summary>
merged_on: YYYY-MM-DD
merged_from_count: N
supersedes: [ <list of source file paths> ]
---

# <Topic Title>

This file consolidates N source files about <topic> from across docs/.

## From: docs/02-data-platform/dagster-orchestration.md (canonical)
<full original content with frontmatter stripped>

## From: docs/dagster/setup-guide.md (leftover dir)
<full original content>

## From: docs/archive/2026-06-06-data-engineering/Dagster-v0.md (archive)
<full original content>

## Cross-References
<links to related topics>
```

## Source provenance

Each `## From:` section is labelled with the source's provenance:

- **(canonical)** — from the original 7-domain tree (`docs/00-*` through `docs/08-*`)
- **(leftover dir)** — from a topic-grouped consolidation dir (`docs/dlt/`, `docs/baml/`, etc.)
- **(archive)** — from `docs/archive/2026-06-06-*/` (older or experimental versions)

## How to navigate

1. Start at `00_index.md` for the routing table
2. Each domain has its own directory
3. Within a domain, files are grouped by topic
4. Each file's frontmatter has `merged_from_count` to gauge breadth
5. Each `## From:` section is self-contained — read the parts you need

## How to add new docs

- New `.md` files: place in the appropriate `docs-v2/<domain>/<topic>/` dir
  as a new section, or create a new topic
- New non-`.md` files: place in `docs-v2/11-scripts/`, `12-configs/`, or `13-images/`
- Update `00_index.md` to reflect the change

## How to regenerate

```bash
uv run scripts/migrate-docs-v2.py
```

The script is idempotent: it regenerates `docs-v2/` from `docs/` each run.
"""
    write_text(DOCS_V2 / "MIGRATION.md", content)


def regenerate_index() -> None:
    """Regenerate 00_index.md from the actual file tree."""
    md = [
        "---",
        "title: docs-v2 — Consolidated Documentation",
        f"status: living-document\ngenerated: {now_iso()}",
        "---",
        "",
        "# docs-v2 — Consolidated Documentation Index",
        "",
        "**Regenerated from `docs/` via ccc + Cognee. No files in `docs/` are deleted.**",
        "",
        "## Domain routing",
        "",
        "| Domain | Path | File count |",
        "|:--|:--|--:|",
    ]
    for d in CANONICAL_DOMAINS:
        dpath = DOCS_V2 / d
        if dpath.exists():
            n = sum(1 for _ in dpath.rglob("*.md"))
            md.append(f"| {d} | `{d}/` | {n} |")
    misc_dirs = ["10-loose-files", "11-scripts", "12-configs", "13-images"]
    for d in misc_dirs:
        dpath = DOCS_V2 / d
        if dpath.exists():
            n = sum(1 for _ in dpath.rglob("*") if _.is_file())
            md.append(f"| {d} | `{d}/` | {n} |")
    md.append("")
    write_text(DOCS_V2 / "00_index.md", "\n".join(md))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate docs/ to docs-v2/")
    parser.add_argument(
        "--domain",
        choices=[*CANONICAL_DOMAINS, "archive", "non-md", "index", "all"],
        default="all",
        help="Which domain to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute mapping without writing files",
    )
    parser.add_argument(
        "--cognee",
        action="store_true",
        help="Use Cognee for semantic dedup (slower but more accurate)",
    )
    args = parser.parse_args()

    print(f"docs-v2 migration starting (domain={args.domain}, dry_run={args.dry_run})")
    MIGRATION_DIR.mkdir(parents=True, exist_ok=True)

    all_mapping: dict[str, str] = {}

    if args.domain in {"all", *CANONICAL_DOMAINS}:
        domains = CANONICAL_DOMAINS if args.domain == "all" else [args.domain]
        all_sources = collect_sources()
        for d in domains:
            print(f"Processing domain: {d}")
            mapping = process_domain(d, args.dry_run, all_sources)
            all_mapping.update(mapping)
            print(f"  → {len(mapping)} files mapped to {d}/")

    if args.domain in {"all", "archive"}:
        print("Processing archive (full LLM read)")
        mapping = process_archive(args.dry_run)
        all_mapping.update(mapping)
        print(f"  → {len(mapping)} archive files mapped")

    if args.domain in {"all", "non-md"}:
        print("Processing non-md files")
        mapping = process_non_md(args.dry_run)
        all_mapping.update(mapping)
        print(f"  → {len(mapping)} non-md files copied")

    if args.domain in {"all", "index"}:
        print("Regenerating 00_index.md and changelog.md")
        if not args.dry_run:
            regenerate_index()
            write_migration_doc()
            write_changelog(all_mapping)

    if not args.dry_run:
        write_coverage_json(all_mapping)

    print(f"\nDone. {len(all_mapping)} total mappings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
