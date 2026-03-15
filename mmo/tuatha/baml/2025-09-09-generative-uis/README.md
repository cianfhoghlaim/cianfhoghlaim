# 🦄 ai that works: Generative UIs and Structured Streaming

> Moving beyond basic token-by-token streaming to create fluid, interactive, and truly modern AI user experiences with semantic streaming of structured objects.

[Video](https://www.youtube.com/watch?v=RX8D5oJrV9k) (1h)

[![Generative UIs and Structured Streaming](https://img.youtube.com/vi/RX8D5oJrV9k/0.jpg)](https://www.youtube.com/watch?v=RX8D5oJrV9k)

## Episode Summary

This week's 🦄 ai that works session dove into one of the most underrated aspects of building great AI apps: **Streaming**.

We explored how to go beyond basic token-by-token streaming to create fluid, interactive, and truly modern user experiences. The session covered practical implementations using NextJS, FastAPI, and more, demonstrating how semantic streaming can transform your AI applications.

The key insight: streaming isn't just about showing text faster—it's about building better apps. By streaming semantically valid, partial objects instead of broken JSON chunks, you can create interactive UIs that respond in real-time and give users control.

## The One Thing to Remember

> The difference between a good and a great AI app is often the user experience. Move beyond streaming raw tokens and start streaming structured, semantically valid objects. It simplifies your frontend code and unlocks a new level of interactivity for your users.

## Key Takeaways

- **Stop Streaming Broken JSON**: The BAML approach provides a stream of semantically valid, partial objects, so at every step, your application has a real, usable data structure to work with
- **Control Your Stream Declaratively**: Control streaming behavior directly in your BAML schema with simple attributes like `@@stream.done` to ensure objects only appear once they're fully formed
- **Streaming is a UX Superpower**: Create interactive UIs that respond in real-time and give users control, not just show text faster
- **Enable Parallel Workflows**: Get complete, validated objects as they're generated, allowing downstream tasks to start immediately while generation continues

## Live Demos

- [Recipe Generator Demo](https://baml-examples.vercel.app/examples/get-recipe) - See semantic streaming in action
- [Interactive Todo List](https://baml-examples.vercel.app/examples/todo-llm) - Experience real-time structured updates

## Resources

- [Session Recording](https://www.youtube.com/watch?v=RX8D5oJrV9k)
- [Code Examples on GitHub](https://github.com/ai-that-works/ai-that-works/tree/main/2025-09-09-generative-uis)
- [Blog Post: Semantic Streaming](https://boundaryml.com/blog/launch-week-day-4)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://luma.com/kbjf88pm)

## Next Session

**AI That Works: Bash vs. MCP - Token Efficient Coding Agent Tooling** - September 16, 2025

We'll explore what's better for helping coding agents do more with fewer tokens:
- The token efficiency and downsides of JSON for agent tooling
- Writing your own drop-ins for MCP tools
- Advanced tricks like using `.shims` to force `uv` instead of `pip` or `bun` instead of `npm`

[RSVP for the next session](https://luma.com/kbjf88pm)

## Whiteboards

<img width="4605" height="2714" alt="image" src="https://github.com/user-attachments/assets/4c6db50d-d051-4ef9-a8e6-bbbbb4e231b2" />

Token based streaming (note each digit comes out in sequence - 1, 10, 100, etc)
![Semantic Streaming vs Token-based](https://github.com/user-attachments/assets/dbe713a8-b335-4b3d-b5eb-4346755052f1)

Semantic streaming (note each digit only comes out when it's complete)
![Semantic Streaming](https://github.com/user-attachments/assets/8c359082-8361-4f6d-94e4-7ad5bb82d64c)

See if you spot the difference here between token streaming vs semantic streaming

https://github.com/user-attachments/assets/78c83f23-130b-4a41-89ff-7a24aee4e596




## Code Walkthrough

<!-- Add code walkthrough details here -->
