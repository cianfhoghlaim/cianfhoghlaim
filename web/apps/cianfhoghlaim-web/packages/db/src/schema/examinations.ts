import {
  pgTable,
  text,
  integer,
  timestamp,
  varchar,
  boolean,
} from "drizzle-orm/pg-core";

export const examMaterials = pgTable("examinations.all_exam_materials", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  level: varchar("level", { length: 60 }).notNull(),
  subject: varchar("subject", { length: 120 }).notNull(),
  year: integer("year").notNull(),
  materialType: varchar("material_type", { length: 30 }).notNull(),
  pdfUrl: text("pdf_url"),
  title: text("title"),
  scraper: varchar("scraper", { length: 30 }).default("unknown"),
  status: varchar("status", { length: 50 }).default("pending"),
  contentHash: varchar("content_hash", { length: 64 }),
  scrapedAt: timestamp("scraped_at", { withTimezone: true }).defaultNow(),
});

export const curriculumPages = pgTable("curriculum.curriculum_pages", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  cycle: varchar("cycle", { length: 60 }).notNull(),
  subject: varchar("subject", { length: 120 }).notNull(),
  language: varchar("language", { length: 10 }).notNull(),
  source: varchar("source", { length: 30 }),
  url: text("url").unique(),
  content: text("content"),
  scrapedAt: timestamp("scraped_at", { withTimezone: true }).defaultNow(),
});

export const pdfDownloads = pgTable("curriculum.pdf_downloads", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  url: text("url").unique().notNull(),
  status: varchar("status", { length: 50 }).notNull().default("pending"),
  sizeBytes: integer("size_bytes"),
  contentHash: varchar("content_hash", { length: 64 }),
  downloadedAt: timestamp("downloaded_at", { withTimezone: true }).defaultNow(),
});

export const markingSchemes = pgTable("examinations.marking_schemes", {
  id: integer("id").primaryKey().generatedAlwaysAsIdentity(),
  level: varchar("level", { length: 60 }).notNull(),
  subject: varchar("subject", { length: 120 }).notNull(),
  year: integer("year").notNull(),
  materialType: varchar("material_type", { length: 30 }).default("marking_schemes"),
  pdfUrl: text("pdf_url"),
  title: text("title"),
  scraper: varchar("scraper", { length: 30 }).default("unknown"),
  status: varchar("status", { length: 50 }).default("pending"),
  scrapedAt: timestamp("scraped_at", { withTimezone: true }).defaultNow(),
});
