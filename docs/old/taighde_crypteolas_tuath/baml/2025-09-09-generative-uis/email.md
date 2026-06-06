Hello First Name,



Thanks for joining our latest 🦄 AI That Works session where we dove into one of the most underrated aspects of building great AI apps: Streaming.



The full recording is now on YouTube, and all the code examples are available on GitHub.



We explored how to go beyond basic token-by-token streaming to create fluid, interactive, and truly modern user experiences. Here’s a quick recap of the key takeaways:

Stop Streaming Broken JSON: Streaming raw JSON from an LLM gives you useless, un-parseable chunks until the very end. The BAML approach is to provide a stream of semantically valid, partial objects, so at every step, your application has a real, usable data structure to work with.
Control Your Stream Declaratively: Instead of writing messy frontend logic full of null checks, you can control streaming behavior directly in your BAML schema with simple attributes. Use @@stream.done to ensure an object (like a recipe ingredient) only appears once it's fully formed, which also provides powerful type-safety guarantees in your UI code.
Streaming is a UX Superpower: The goal isn't just to show text faster; it's to build better apps. Semantic streaming lets you create interactive UIs that respond in real-time and give users control. Check out our live Recipe demo or this interactive Todo List to see it in action.
Enable Parallel Workflows: Because you can get complete, validated objects as they are generated, you can kick off downstream tasks immediately. Imagine an agent that researches a list of topics; as soon as the first topic is streamed, you can start the deep-dive research for it while the rest of the list is still being generated.


If you remember one thing from this session:
The difference between a good and a great AI app is often the user experience. Move beyond streaming raw tokens and start streaming structured, semantically valid objects. It simplifies your frontend code and unlocks a new level of interactivity for your users.



Want to dive deeper into the mechanics? Check out our blog post on Semantic Streaming.



Our next session is on September 16th, and it's a fun one: Bash vs. MCP - token efficient coding agent tooling. We'll explore what's better for helping coding agents do more with fewer tokens, covering:

The token efficiency and downsides of JSON for agent tooling.
Writing your own drop-ins for MCP tools.
Advanced tricks like using .shims to force uv instead of pip or bun instead of npm.


Sign up here: https://luma.com/kbjf88pm



If you have any questions, reply to this email or ask on Discord. We read every message! 



Happy coding 🧑‍💻



Best,
Vaibhav & Dex

