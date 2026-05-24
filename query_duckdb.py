import duckdb
con = duckdb.connect('curriculum_unified.duckdb')
print("Pages Count:", con.execute('SELECT count(*) FROM curriculum.curriculum_pages').fetchone()[0])
print("URLs:", con.execute('SELECT url FROM curriculum.curriculum_pages LIMIT 3').fetchall())
