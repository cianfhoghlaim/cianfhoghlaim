import { extract, type FeedEntry } from "@extractus/feed-extractor";

export type FeedEntryWithComments = FeedEntry & { comments: string };

export async function getFeed() {
	const data = await extract("https://news.ycombinator.com/rss", {
		getExtraEntryFields(entryData) {
			return {
				comments: (entryData as FeedEntryWithComments).comments,
			};
		},
	});
	return data.entries as FeedEntryWithComments[];
}
