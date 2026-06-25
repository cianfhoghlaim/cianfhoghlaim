import { z } from "zod";
import { publicProcedure, o } from "../index";
import { runDuckLakeQuery } from "../queries";

const SUBJECT_RUBRIC: Record<string, string> = {
  english: "PCLM: Purpose, Coherence, Language, Mechanics (each band ~25%)",
  gaeilge: "Cumarsáid · Léamhthuiscint · Litríocht · Gramadach",
  mathematics: "Equation steps + final numerical answer (mark per step)",
  biology: "Mandatory keywords (10+) · experiment steps · diagram labels",
  chemistry: "Balanced equations · state symbols · calculation steps · significant figures",
  physics: "Definitions · units · formula manipulation · significant figures",
  geography: "SRPs (Significant Relevant Points): 2 marks per distinct factual point",
  history: "SRPs · historiographical perspective · primary source citation",
  irish: "Léamh · Scríbhneoireacht · Gramadach · Líofacht",
};

export const examsRouter = o.router({
  list: publicProcedure
    .input(
      z.object({
        subject: z.string().min(1).max(120),
        year: z.number().int().min(1999).max(2030),
        level: z
          .enum(["leaving_certificate", "junior_cycle", "leaving_certificate_applied"])
          .default("leaving_certificate"),
        materialType: z.enum(["exam_papers", "marking_schemes"]).default("exam_papers"),
      }),
    )
    .handler(async ({ input }) => {
      const sql = `
        SELECT level, subject, year, material_type, pdf_url, title,
               scraper, status, scraped_at
        FROM examinations.all_exam_materials
        WHERE subject = '${input.subject.replace(/'/g, "''")}'
          AND year = ${input.year}
          AND level = '${input.level}'
          AND material_type = '${input.materialType}'
        ORDER BY pdf_url
      `;
      return runDuckLakeQuery(sql, 200);
    }),

  summary: publicProcedure
    .input(z.object({ subject: z.string().min(1).max(120) }))
    .handler(async ({ input }) => {
      const rubric = SUBJECT_RUBRIC[input.subject.toLowerCase()] ?? "Generic SRPs / keywords";
      const sql = `
        SELECT year, count(*) AS schemes
        FROM examinations.all_exam_materials
        WHERE subject = '${input.subject.replace(/'/g, "''")}'
          AND material_type = 'marking_schemes'
          AND pdf_url IS NOT NULL AND pdf_url != ''
        GROUP BY year ORDER BY year DESC LIMIT 20
      `;
      const recent = await runDuckLakeQuery(sql, 20);
      return {
        subject: input.subject,
        rubric,
        recentYears: recent.map((r) => ({
          year: r.year as number,
          schemes: r.schemes as number,
        })),
      };
    }),
});
