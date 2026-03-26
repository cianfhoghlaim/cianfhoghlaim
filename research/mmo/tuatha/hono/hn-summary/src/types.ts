export type AppEnv = {
	Bindings: Cloudflare.Env;
};

export type ArticleSummary = {
	article: string | null | undefined;
	summary: string | null | undefined;
};
