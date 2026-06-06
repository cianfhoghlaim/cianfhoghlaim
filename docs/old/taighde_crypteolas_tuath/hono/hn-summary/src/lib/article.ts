import { Readability } from "@mozilla/readability";
import DOMPurify from "dompurify";
import { parseHTML } from "linkedom";
import type { ArticleSummary } from "../types";
import summarize from "./summarize";

export async function getArticleAndSummary(options: {
	articlesKV: KVNamespace;
	ai: Ai;
	url: string;
}) {
	// let result: ArticleSummary | null = null;

	let result = await options.articlesKV.get<ArticleSummary>(
		options.url,
		"json",
	);

	if (result) {
		return result;
	}

	const response = await fetch(options.url, {
		cf: {
			cacheTtl: 60 * 60 * 24,
			cacheEverything: true,
		},
	});
	const html = await response.text();
	const { document } = parseHTML(html);
	[...document.getElementsByTagName("img")].forEach((link) => {
		link.src = new URL(link.src, options.url).href;
	});
	[...document.getElementsByTagName("a")].forEach((link) => {
		link.href = new URL(link.href, options.url).href;
		link.setAttribute("target", "_blank");
		link.setAttribute("rel", "noopener nofollow");
	});

	let reader: Readability | null = null;

	try {
		reader = new Readability(document);
	} catch (error) {
		console.error("Readability error", (error as Error).message, options.url);
	}

	result = {
		article: null,
		summary: null,
	};

	if (!reader) {
		await options.articlesKV.put(options.url, JSON.stringify(result));
		return result;
	}

	const article = reader?.parse();

	if (article?.content) {
		const { window } = parseHTML("");
		const purify = DOMPurify(window);
		const cleanArticle = purify.sanitize(article.content);

		console.log("Summarizing:", options.url);
		const summary = await summarize(options.ai, options.url, cleanArticle);

		result = {
			article: cleanArticle,
			summary,
		};
	}

	await options.articlesKV.put(options.url, JSON.stringify(result));

	return result;
}
