<script context="module">
    import { mapPath } from 'services/http';
    import { readMarkdown } from 'utils/markdown';
    import { errorMessage } from 'utils/messenger';

	export async function preload(page, session) {
        const { locale } = page.params;
        const path = mapPath(`data/article.json?${new URLSearchParams(page.params).toString()}`, session);
        const response = await this.fetch(path);
        const data = await response.json();

		if (response.status === 200) {
            const { metadata, toc, content } = readMarkdown(data.markdown, page.path);

            if (!!metadata.public && metadata.public === 'true') {
                return {
                    basePath: page.path,
                    metadata,
                    monolingual: data.monolingual,
                    toc,
                    content,
                    articles: data.articles
                };
            } else {
                this.error(404, errorMessage(404, locale));
            }
		} else {
			this.error(response.status, data.message);
		}
    };
</script>

<script>
    import Resource from 'components/Resource.svelte'

    export let basePath;
    export let metadata;
    export let monolingual;
    export let toc;
    export let content;
    export let articles;
</script>

<Resource {basePath} {metadata} {monolingual} {toc} {content} {articles}/>