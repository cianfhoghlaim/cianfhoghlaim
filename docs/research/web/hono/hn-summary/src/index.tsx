import { Hono } from "hono";
import { raw } from "hono/html";
import { jsxRenderer } from "hono/jsx-renderer";
import { getArticleAndSummary } from "./lib/article";
import { getFeed } from "./lib/hacker-news";
import type { AppEnv } from "./types";

const app = new Hono<AppEnv>();

app.use(
	"*",
	jsxRenderer(({ children }) => {
		return (
			<html lang="en">
				<head>
					<link
						rel="stylesheet"
						href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"
					/>
				</head>
				<body class="container">{children}</body>
			</html>
		);
	}),
);

app.get("/", async (c) => {
	const items = await getFeed();

	return c.render(
		<>
			<h1>Hacker News Summary</h1>
			{
				await Promise.all(
					items?.map(async (entry) => {
						const result = await getArticleAndSummary({
							ai: c.env.AI,
							articlesKV: c.env.articles,
							url: entry.link!,
						});
						return (
							<details>
								{/** biome-ignore lint/a11y/useSemanticElements: using summary container */}
								<summary role="button" class="outline contrast">
									{entry.title}
								</summary>
								<article>
									<header>
										<a
											href={entry.link}
											target="_blank"
											rel="nofollow noopener"
										>
											Article
										</a>
										{" | "}
										<a
											href={entry.comments}
											target="_blank"
											rel="nofollow noopener"
										>
											Comments
										</a>
									</header>
									{result.article ? (
										<div>
											<h2>Summary</h2>
											{result.summary ? (
												raw(result.summary)
											) : (
												<p>Summary unavailable.</p>
											)}
											<hr />
											<h2>Article</h2>
											{raw(result.article)}
										</div>
									) : (
										<h2>Unable to retrieve article.</h2>
									)}
								</article>
							</details>
						);
					}),
				)
			}
		</>,
	);
});

app.notFound((c) => {
	return c.render(<h1>Not found - {c.req.path}</h1>);
});

app.onError((error, c) => {
	c.status(500);
	return c.render(<h1>Error - {error.message}</h1>);
});

export default app;
