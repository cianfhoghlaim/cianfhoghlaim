import { Stagehand } from "@browserbasehq/stagehand";

async function main() {
  const stagehand = new Stagehand({
    env: "BROWSERBASE",
    model: "google/gemini-3-flash-preview",
  });
  await stagehand.init();

  const page = stagehand.context.pages()[0];
  await page.goto("https://news.ycombinator.com");

  // Let AI click
  await stagehand.act("click on the comments link for the top story");

  // Extract structured data
  const data = await stagehand.extract("extract the title and points of the top story");
  console.log(data);

  await stagehand.close();
}

main().catch(console.error);