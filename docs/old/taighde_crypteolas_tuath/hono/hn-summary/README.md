# Hacker News Summary

Summarize the articles from the front-page of hacker news.

View the deployed app [here](https://hn-summary.cj-syntax.workers.dev/).

Built with:
* [hono](https://hono.dev/)
* Cloudflare
  * [Workers](https://developers.cloudflare.com/workers/)
  * [KV](https://developers.cloudflare.com/kv/)
  * [AI](https://developers.cloudflare.com/workers-ai/)
* [@extractus/feed-extractor](https://www.npmjs.com/package/@extractus/feed-extractor)
* [@mozilla/readability](https://www.npmjs.com/package/@mozilla/readability)

# Setup

```bash
pnpm install
pnpm run dev
```

[For generating/synchronizing types based on your Worker configuration run](https://developers.cloudflare.com/workers/wrangler/commands/#types):

```bash
pnpm run cf-typegen
```

# Deploy

```bash
pnpm run deploy
```
