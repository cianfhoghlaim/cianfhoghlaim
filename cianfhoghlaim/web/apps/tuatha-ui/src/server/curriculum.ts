/**
 * Curriculum Server Functions
 *
 * TanStack Start server functions for Celtic curriculum data, backed by
 * a curriculum API (when available) with rich local fallback data.
 */

import { createServerFn } from "@tanstack/react-start";

export interface CurriculumItem {
  id: string;
  nation: string;
  level: string;
  subject: string;
  title: string;
  contentPreview: string;
  learningOutcomes: string[];
  difficulty: "beginner" | "intermediate" | "advanced";
}

export interface CurriculumSearchResult {
  items: CurriculumItem[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
  nextCursor?: string;
}

export interface CurriculumSearchInput {
  query?: string;
  nation?: "ireland" | "wales" | "scotland" | "all";
  level?: string;
  subject?: string;
  page?: number;
  pageSize?: number;
  cursor?: string;
}

const apiUrl = process.env.API_URL || "http://localhost:8000";

export const searchCurriculum = createServerFn({ method: "GET" }).handler(
  async (opts: { data?: CurriculumSearchInput }): Promise<CurriculumSearchResult> => {
    const { query, nation = "all", level, subject, page = 1, pageSize = 20, cursor } = (opts.data ?? {}) as CurriculumSearchInput;

    const params = new URLSearchParams();
    if (query) params.set("query", query);
    if (nation !== "all") params.set("nation", nation);
    if (level) params.set("level", level);
    if (subject) params.set("subject", subject);
    params.set("page", page.toString());
    params.set("page_size", pageSize.toString());
    if (cursor) params.set("cursor", cursor);

    try {
      const response = await fetch(`${apiUrl}/api/curriculum/search?${params.toString()}`);
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const result = await response.json();
      return {
        items: (result.items ?? []).map(transformCurriculumItem),
        total: result.total,
        page: result.page,
        pageSize: result.page_size,
        hasMore: result.has_more,
        nextCursor: result.next_cursor,
      };
    } catch {
      return getMockCurriculumData(query, nation, page, pageSize);
    }
  },
);

export const getCurriculumById = createServerFn({ method: "GET" }).handler(
  async (opts: { data?: { id: string } }): Promise<CurriculumItem | null> => {
    const { id } = (opts.data ?? {}) as { id: string };
    if (!id) return null;

    try {
      const response = await fetch(`${apiUrl}/api/curriculum/${id}`);
      if (!response.ok) {
        if (response.status === 404) return null;
        throw new Error(`API error: ${response.status}`);
      }
      return transformCurriculumItem(await response.json());
    } catch {
      return getMockCurriculumItem(id);
    }
  },
);

export const getCurriculumLevels = createServerFn({ method: "GET" }).handler(
  async (opts: { data?: { nation?: string } }): Promise<string[]> => {
    const { nation } = (opts.data ?? {}) as { nation?: string };
    const levelsByNation: Record<string, string[]> = {
      ireland: ["primary", "junior_cycle", "leaving_cert"],
      wales: ["key_stage_3", "gcse", "a_level"],
      scotland: ["national_5", "higher", "advanced_higher"],
    };
    if (nation && levelsByNation[nation]) {
      return levelsByNation[nation];
    }
    return ["beginner", "intermediate", "advanced"];
  },
);

export const getCurriculumSubjects = createServerFn({ method: "GET" }).handler(
  async (): Promise<string[]> => [
    "language", "literature", "culture", "history", "geography",
  ],
);

function transformCurriculumItem(item: Record<string, unknown>): CurriculumItem {
  return {
    id: item.id as string,
    nation: item.nation as string,
    level: item.level as string,
    subject: item.subject as string,
    title: item.title as string,
    contentPreview: (item.content_preview || item.content || "") as string,
    learningOutcomes: (item.learning_outcomes || []) as string[],
    difficulty: (item.difficulty || "beginner") as CurriculumItem["difficulty"],
  };
}

function getAllMockCurriculum(): CurriculumItem[] {
  return [
    { id: "cur-001", nation: "ireland", level: "junior_cycle", subject: "language", title: "Basic Irish Greetings", contentPreview: "Learn essential Irish greetings including Dia duit, Slán, and Go raibh maith agat.", learningOutcomes: ["Greet others in Irish", "Say goodbye in Irish", "Express thanks in Irish"], difficulty: "beginner" },
    { id: "cur-002", nation: "ireland", level: "junior_cycle", subject: "language", title: "The Irish Verb \"Bí\" (To Be)", contentPreview: "Master the most important verb in Irish - the verb \"to be\" in its various forms.", learningOutcomes: ["Use \"tá\" and \"níl\" correctly", "Form questions with \"an bhfuil\"", "Understand the difference between copula and substantive verb"], difficulty: "beginner" },
    { id: "cur-003", nation: "wales", level: "gcse", subject: "language", title: "Welsh Mutations", contentPreview: "Understand soft, nasal, and aspirate mutations in Welsh.", learningOutcomes: ["Apply soft mutation correctly", "Recognize nasal mutation contexts", "Use aspirate mutation after \"a\" and \"gyda\""], difficulty: "intermediate" },
    { id: "cur-004", nation: "scotland", level: "national_5", subject: "literature", title: "Scottish Gaelic Poetry", contentPreview: "Explore traditional and modern Gaelic poetry from the Highlands.", learningOutcomes: ["Analyze traditional Gaelic verse forms", "Discuss themes in Gaelic poetry", "Recite selected poems"], difficulty: "intermediate" },
    { id: "cur-005", nation: "ireland", level: "leaving_cert", subject: "culture", title: "The Ulster Cycle", contentPreview: "Study the great mythological cycle featuring Cú Chulainn and the Red Branch Knights.", learningOutcomes: ["Summarize the Táin Bó Cúailnge", "Analyze the character of Cú Chulainn", "Discuss themes of honor and heroism"], difficulty: "advanced" },
  ];
}

function getMockCurriculumData(
  query: string | undefined,
  nation: string,
  page: number,
  pageSize: number,
): CurriculumSearchResult {
  let filtered = nation === "all" ? getAllMockCurriculum() : getAllMockCurriculum().filter((i) => i.nation === nation);
  if (query) {
    const q = query.toLowerCase();
    filtered = filtered.filter((i) => i.title.toLowerCase().includes(q) || i.contentPreview.toLowerCase().includes(q));
  }
  const start = (page - 1) * pageSize;
  const items = filtered.slice(start, start + pageSize);
  return {
    items,
    total: filtered.length,
    page,
    pageSize,
    hasMore: start + pageSize < filtered.length,
    nextCursor: start + pageSize < filtered.length ? `cursor-${page + 1}` : undefined,
  };
}

function getMockCurriculumItem(id: string): CurriculumItem | null {
  return getAllMockCurriculum().find((i) => i.id === id) || null;
}
