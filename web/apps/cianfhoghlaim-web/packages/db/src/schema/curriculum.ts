import { pgTable, serial, integer, text, varchar, timestamp } from "drizzle-orm/pg-core";

export const syllabusPages = pgTable("curriculum.syllabus_pages", {
  id: serial("id").primaryKey(),
  cycle: varchar("cycle", { length: 60 }).notNull(),
  subject: varchar("subject", { length: 120 }).notNull(),
  language: varchar("language", { length: 10 }).notNull().default("en"),
  source: varchar("source", { length: 30 }).default("ncca"),
  url: text("url").unique(),
  content: text("content"),
  scrapedAt: timestamp("scraped_at", { withTimezone: true }).defaultNow(),
});

export const extractedText = pgTable("curriculum.pdf_extracted_text", {
  id: serial("id").primaryKey(),
  pdfUrl: text("pdf_url").notNull(),
  pageNum: integer("page_num").notNull(),
  text: text("text"),
  ocrEngine: varchar("ocr_engine", { length: 30 }),
  extractedAt: timestamp("extracted_at", { withTimezone: true }).defaultNow(),
});
