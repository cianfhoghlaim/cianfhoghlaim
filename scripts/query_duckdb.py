import os

import duckdb

db_path = os.getenv("CURRICULUM_UNIFIED_DB_PATH", "data/curriculum_unified.duckdb")
con = duckdb.connect(db_path)
print("Pages Count:", con.execute("SELECT count(*) FROM curriculum.curriculum_pages").fetchone()[0])
print("URLs:", con.execute("SELECT url FROM curriculum.curriculum_pages LIMIT 3").fetchall())
