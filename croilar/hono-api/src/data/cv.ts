import { Hono } from "hono";
import { query } from "./duckdb";

interface CvEntry {
  filepath: string; category: string; filename: string;
  extracted_text: string; page_count: number;
}

const cvRoutes = new Hono();

cvRoutes.get("/entries", (c) => {
  const category = c.req.query("category");
  try {
    let sql = `SELECT filepath, category, filename, extracted_text, page_count FROM cv_data.cv_raw`;
    const params: unknown[] = [];
    if (category) {
      sql += ` WHERE category = ?`;
      params.push(category);
    }
    const entries = query<CvEntry>(sql, ...params);
    // Truncate text for list view
    const trimmed = entries.map((e) => ({
      ...e,
      extracted_text: e.extracted_text?.slice(0, 500) ?? "",
    }));
    return c.json({ entries: trimmed });
  } catch {
    return c.json({ entries: [] });
  }
});

cvRoutes.get("/entries/:category", (c) => {
  const cat = c.req.param("category");
  try {
    const entries = query<CvEntry>(
      `SELECT filepath, category, filename, extracted_text, page_count
       FROM cv_data.cv_raw WHERE category = ?`, cat,
    );
    return c.json({ entries });
  } catch {
    return c.json({ entries: [] });
  }
});

cvRoutes.get("/search", (c) => {
  const q = c.req.query("q") ?? "";
  try {
    const entries = query<CvEntry>(
      `SELECT filepath, category, filename, extracted_text, page_count
       FROM cv_data.cv_raw
       WHERE extracted_text ILIKE '%' || ? || '%'
       LIMIT 20`, q,
    );
    return c.json({ entries });
  } catch {
    return c.json({ entries: [] });
  }
});

export default cvRoutes;
