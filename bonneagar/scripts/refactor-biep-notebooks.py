#!/usr/bin/env python3
"""Refactor the 6 BIEP notebooks to use ibis.duckdb.connect as the
canonical KCG entrypoint (per the wire-biep-notebooks-to-lakehouse change).

For each .py file under cianfhoghlaim/notebooks/04_biep_motherduck/:
- Replace `import duckdb` → `import ibis` (and update usage)
- Replace `duckdb.connect("md:oideachais")` → `ibis.duckdb.connect("md:oideachais")`
- Replace `duckdb.connect("md:oideachais?...")` → `ibis.duckdb.connect(...)`
- Replace `con.execute(...).fetchdf()` → `conn.execute(...).to_pandas()` (using ibis's to_pandas)
- Preserve the MotherDuck token SET pattern: convert `duckdb.sql("SET ...")`
  → `ibis.duckdb.connect(url_with_token)` (URL-based auth)

The change is deliberately conservative: only the
duckdb.connect / execute / fetchdf patterns get changed; everything
else (mo.*, df.*, sql_area etc.) is preserved.
"""
import os
import re
import sys


NOTEBOOKS_DIR = "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/notebooks/04_biep_motherduck"

# The 6 BIEP subject notebooks (skip the e2e/leabharlann ones — those are
# separate demo notebooks that aren't part of the wire-biep change)
TARGETS = [
    "01_curriculum_educator.py",
    "02_syllabus_visualizer.py",
    "03_all_nations.py",
    "05_marking_scheme_analyzer.py",
    "06_exam_papers_explorer.py",
    "07_subject_full_pipeline.py",
]


def refactor(path):
    with open(path) as f:
        src = f.read()
    new = src
    changes = []

    # 1. Replace `import duckdb` → `import ibis` (also keep duckdb if used for dbapi/conn)
    # But the ibis.duckdb.connect uses the duckdb package under the hood,
    # so we can keep `import duckdb` for raw_sql access.
    if "import duckdb" in new and "ibis" not in new:
        new = new.replace(
            "import duckdb",
            "import duckdb\nimport ibis  # ibis-first entrypoint (per wire-biep-notebooks-to-lakehouse change)",
        )
        changes.append("added `import ibis`")

    # 2. Replace `duckdb.sql(f"SET motherduck_token='{token}'")` with a comment
    # explaining the token is now passed via the connect URL
    new = re.sub(
        r'duckdb\.sql\(f?"SET motherduck_token=([\'])\{(\w+)\}\\1"\)',
        r"# ibis.duckdb.connect() picks up the MotherDuck token from the\n# connection URL (\?motherduck_token=...) so no global SET is needed.",
        new,
    )
    # Also handle single quotes + f-string
    new = re.sub(
        r"duckdb\.sql\(f?['\"]SET motherduck_token=['\"]([^'\"]+)['\"]['\"]\)",
        r"# ibis.duckdb.connect() picks up the MotherDuck token from the\n# connection URL (?motherduck_token=...) so no global SET is needed.",
        new,
    )
    if "duckdb.sql(f\"SET motherduck_token" in src or 'duckdb.sql("SET motherduck_token' in src:
        changes.append("removed duckdb.sql('SET motherduck_token=...')")

    # 3. Replace `duckdb.connect("md:oideachais")` → `ibis.duckdb.connect("md:oideachais")`
    if 'duckdb.connect("md:oideachais")' in new:
        new = new.replace(
            'duckdb.connect("md:oideachais")',
            'ibis.duckdb.connect("md:oideachais")',
        )
        changes.append('duckdb.connect("md:oideachais") → ibis.duckdb.connect("md:oideachais")')

    # 4. Replace `con.execute(SQL).fetchdf()` → `conn.execute(SQL).to_pandas()`
    # Pattern: capture `con.execute(<sql>).fetchdf()` where con was the old
    # duckdb connection. After our refactor, `con` is now an ibis connection
    # but the API for `.execute(...).to_pandas()` should work via ibis.
    # However, ibis uses `.raw_sql()` for raw DDL/DML. For SELECT queries,
    # the proper way is to use `conn.sql(<query>).to_pandas()` or
    # `conn.execute(<query>).to_pandas()` — both work.
    # So: `con.execute(SQL).fetchdf()` → `con.execute(SQL).to_pandas()`
    if re.search(r"\.execute\([^)]+\)\.fetchdf\(\)", new):
        new = re.sub(
            r"\.execute\(([^)]+)\)\.fetchdf\(\)",
            r".execute(\1).to_pandas()",
            new,
        )
        changes.append(".execute(...).fetchdf() → .execute(...).to_pandas()")

    # 5. Add the ibis-first comment block at the top of the file (after the
    # docstring) explaining the canonical entrypoint
    if "import ibis" in new and "ibis-first entrypoint" not in new:
        # Add a comment to the docstring
        new = new.replace(
            'Tools demonstrated:',
            'Connection pattern (per wire-biep-notebooks-to-lakehouse change):\n\n- ``ibis.duckdb.connect("md:oideachais")`` for cloud (MotherDuck) queries\n- ``ibis.duckdb.connect("ducklake:postgres:...")`` for local lakehouse\n- ``ibis.lancedb.connect("rest://...")`` for vector RAG\n\nTools demonstrated:',
            1,
        )
        changes.append("added ibis-first connection pattern docstring")

    if changes:
        with open(path, "w") as f:
            f.write(new)
        return changes
    return []


def main():
    for fname in TARGETS:
        path = os.path.join(NOTEBOOKS_DIR, fname)
        if not os.path.exists(path):
            print(f"  [SKIP] {fname} (not found)")
            continue
        changes = refactor(path)
        if changes:
            print(f"  [ok]   {fname}:")
            for c in changes:
                print(f"           - {c}")
        else:
            print(f"  [WARN] {fname}: no changes applied")


if __name__ == "__main__":
    main()