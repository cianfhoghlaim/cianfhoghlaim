import axios from "axios";
import { NextResponse } from "next/server";
import { createSigner, withPaymentInterceptor } from "x402-axios";
import OpenAI from "openai";

export async function GET(): Promise<Response> {
  try {
    const privateKey = process.env.PRIVATE_KEY as string | undefined;
    const openaiApiKey = process.env.OPENAI_API_KEY as string | undefined;
    if (!privateKey) {
      return NextResponse.json({ error: "Missing PRIVATE_KEY" }, { status: 500 });
    }
    if (!openaiApiKey) {
      return NextResponse.json({ error: "Missing OPENAI_API_KEY" }, { status: 500 });
    }

    // configure axios to speak 402
    const signer = await createSigner("solana-devnet", privateKey);

    const api = withPaymentInterceptor(
      axios.create({
        baseURL: "https://biznews.x402.bot"
      }),
      signer,
    );

    // Purchase curated business news headlines
    const newsResponse = await api.get("/news");
    const raw = newsResponse.data as unknown;
    const articles = normalizeArticles(raw).slice(0, 6);

    if (articles.length === 0) {
      return NextResponse.json(
        { error: "No articles returned from news source" },
        { status: 502 },
      );
    }

    // Analyze with OpenAI and return a single, best idea
    const openai = new OpenAI({ apiKey: openaiApiKey });
    const prompt = buildPrompt(articles);
    console.log("prompt: ", prompt);

    const completion = await openai.responses.create({
      model: "o4-mini",
      tools: [{
        type: "web_search_preview",
        search_context_size: "medium"
      }],
      input: prompt,
    });

    const content = completion.output_text ?? "";
    console.log("content: ", content);
    const parsed = parseJsonFromText(content);
    console.log("parsed: ", parsed);
    if (!parsed) {
      return NextResponse.json(
        { error: "Failed to parse model output", raw: content },
        { status: 502 },
      );
    }

    return NextResponse.json(parsed, { status: 200 });
  } catch (error) {
    console.error(error);
    return NextResponse.json(
      { error: "Failed to generate idea-of-the-day" },
      { status: 502 },
    );
  }
}

type InputArticle = {
  title?: string;
  url?: string;
  link?: string;
  summary?: string;
  description?: string;
  content?: string;
};

type NormalizedArticle = {
  title: string;
  url: string | undefined;
  summary: string;
};

function normalizeArticles(raw: unknown): NormalizedArticle[] {
  const list: unknown[] = Array.isArray(raw)
    ? raw
    : typeof raw === "object" && raw !== null && Array.isArray((raw as Record<string, unknown>).articles)
    ? ((raw as Record<string, unknown>).articles as unknown[])
    : [];

  return list
    .map((item) => coerceInputArticle(item))
    .map((a) => {
      const title = String(a.title ?? "Untitled");
      const url = typeof a.url === "string" ? a.url : typeof a.link === "string" ? a.link : undefined;
      const summarySource =
        typeof a.summary === "string"
          ? a.summary
          : typeof a.description === "string"
          ? a.description
          : typeof a.content === "string"
          ? a.content
          : "";
      const summary = summarySource ? String(summarySource).slice(0, 800) : "";
      return { title, url, summary };
    })
    .filter((a) => Boolean(a.title));
}

function coerceInputArticle(u: unknown): InputArticle {
  if (typeof u === "object" && u !== null) {
    return u as InputArticle;
  }
  return {} as InputArticle;
}

function buildPrompt(articles: NormalizedArticle[]): string {
  const articlesBlock = JSON.stringify(articles, null, 2);
  return [
    "You are a pragmatic startup analyst. You produce concise, actionable, strictly-JSON outputs only.",
    "You are given a curated list of news headlines and articles along with their URLs that affect businesses.",
    "They may affect existing businesses or create new business opportunities.",
    "Search all of the articles for additional information that may be relevant to the opportunity.",
    "Analyze all the articles and pick the one that creates the strongest opportunity for a new startup.",
    "Return STRICT JSON only, matching exactly this schema:",
    JSON.stringify(
      {
        opportunity: "<what is the business opportunity>",
        tam: {
          estimate: "<dollar estimate and units, e.g., $2B/year>",
          methodology: "<1-2 sentence method to estimate TAM>",
        },
        whyNow: "<why is now the right time>",
        gettingStarted: ["<step 1>", "<step 2>", "<step 3>"],
        source: { title: "<headline title>", url: "<link to article>" },
      },
      null,
      2,
    ),
    "Do not include any narration, explanations, or code fences.",
    "Here are the headlines:",
    articlesBlock,
  ].join("\n\n");
}

function parseJsonFromText(text: string): unknown | null {
  if (!text) return null;
  const trimmed = text.trim();
  // Strip Markdown code fences if present
  const fenceMatch = trimmed.match(/```[a-zA-Z]*\n([\s\S]*?)\n```/);
  const candidate = fenceMatch ? fenceMatch[1] : trimmed;
  try {
    return JSON.parse(candidate);
  } catch {
    // Try to find the first {...} block
    const jsonLike = candidate.match(/\{[\s\S]*\}$/);
    if (jsonLike) {
      try {
        return JSON.parse(jsonLike[0]);
      } catch {}
    }
    return null;
  }
}


