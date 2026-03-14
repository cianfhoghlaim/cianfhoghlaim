#!/usr/bin/env python3

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    # "postgresql://cocoindex:cocoindex@host.docker.internal:5433/cocoindex"
    # "postgresql://cocoindex:cocoindex@localhost:5433/cocoindex"
    os.environ.get("COCOINDEX_DATABASE_URL")
)

# psycopg3 also supports autocommit at connection level
conn.autocommit = True

with conn.cursor() as cur:
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

conn.close()
