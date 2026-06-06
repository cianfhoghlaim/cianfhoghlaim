# model ecosystem

> Auto-merged from subdirectory .md files on 2026-06-06

---


## File: docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/email.md

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


---


## File: docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/meta.md

---
guid: aitw-022
title: "Generative UIs and Structured Streaming"
description:
  We'll explore hard problems in building rich UIs that rely on streaming data from LLMs.
  ​Specifically, we'll talk through techniques for rendering **STRUCTURED** outputs from LLMs, with real-world examples of how to handle partially-streamed outputs over incomplete JSON data. We'll explore advanced needs like
  * Fields that should be required for stream to start
  * ​Rendering React Components with partial data
  ​* Handling nullable fields vs. yet-to-be-streamed fields
  * ​Building high-quality User feedback
  * ​Handling errors mid-stream
event_link: https://luma.com/2g1xfjts
eventDate: 2025-09-09T18:00:00Z
media:
  url: https://www.youtube.com/watch?v=RX8D5oJrV9k
  type: video/youtube
links:
  youtube: https://www.youtube.com/watch?v=RX8D5oJrV9k
  code: https://github.com/ai-that-works/ai-that-works/tree/main/2025-09-09-generative-uis
season: 2
episode: 22
event_type: episode
---

---


## File: docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/my-app/README.md

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---


## File: docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/README.md

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

---


## File: docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/backend/README.md


---


## File: docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/email.md

Hello First Name,

First, we owe you an apology—we've been so focused on upgrading our recording setup for better video quality that we forgot to send out our usual episode emails! The good news: the new setup is working great, and we just hit 2,000 subscribers! Thank you for your support and patience as we level up the viewing experience.

SPECIAL EVENT: AI That Works Unconference - San Francisco (Oct 12th)

Join us IN PERSON for our first unconference! This is a participant-driven event where YOU help shape the agenda. Bring your hardest AI engineering problems, share what you're building, and collaborate with fellow practitioners.

Limited spots available: https://luma.com/ai-that-works-unconf


Here's what you missed:

Bash vs. MCP - Token Efficient Coding Agent Tooling (Watch) Context windows are precious. We explored when to use Bash vs MCP for coding agents, revealing how naming conventions and tool design can dramatically impact token usage and accuracy.

Evals for Classification (Watch) Building production AI isn't just about accuracy—it's about understanding what "correct" means for YOUR users. We built evaluation dashboards for 1000+ category classification systems and showed how to iterate quickly with real user data.

Dynamic Schemas (Watch) Stop hardcoding schemas. We demonstrated how to build UIs that adapt to any data structure using LLM-generated schemas and dynamic React components—perfect for building flexible extraction pipelines.


All code examples are available on GitHub.

Next Episode: Anthropic Post Mortem (Oct 7th)

Anthropic experienced some fascinating bugs in August and wrote an incredibly transparent postmortem. We'll dive deep into what went wrong, why it happened, and what we can all learn from their experience.

Sign up here: https://luma.com/52d6lzpt

If you have questions about any episode, reply to this email or ask on Discord. We read everything!

Happy coding,
Best, Vaibhav & Dex

P.S. - We promise to get back to regular email updates now that our setup is dialed in!

---


## File: docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/frontend/README.md

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

---


## File: docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/meta.md

---
guid: aitw-025
title: "Dynamic Schemas"
description: |
  In this episode, Dex and Vaibhav explore the concept of dynamic UIs and how to build systems that can adapt to unknown data structures. They discuss the importance of dynamic schema generation, meta programming with LLMs, and the potential for creating dynamic React components. The conversation also delves into the execution and rendering of these dynamic schemas, highlighting the challenges and opportunities in this evolving field. They conclude with thoughts on future directions and the importance of building robust workflows around schema management.
event_link: https://luma.com/baml
eventDate: 2025-09-30T18:00:00Z
media:
  url: https://youtu.be/bak7-C--azc
  type: video/youtube
links:
  code: https://github.com/ai-that-works/ai-that-works/tree/main/2025-09-30-dyanmic-schemas
  youtube: https://youtu.be/bak7-C--azc
season: 2
episode: 25
event_type: episode
---

---


## File: docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/README.md


# 🦄 ai that works: Dynamic Schemas

> In this episode, Dex and Vaibhav explore the concept of dynamic UIs and how to build systems that can adapt to unknown data structures. They discuss the importance of dynamic schema generation, meta programming with LLMs, and the potential for creating dynamic React components.

[Video](https://youtu.be/bak7-C--azc) (1h27m)

[![Dynamic Schemas](https://img.youtube.com/vi/bak7-C--azc/0.jpg)](https://youtu.be/bak7-C--azc)


## Episode Overview

BAML can be leveraged to build a pipeline that can extract anything without knowing the schema in advance.

This is done via 2 steps:

1. Ask an LLM to describe a schema that could represent the content of the document.

2. Use the schema to extract the content by leveraging dynamic types.

## Whiteboards

<img width="8727" height="4644" alt="image" src="https://github.com/user-attachments/assets/410097e4-c2dd-490c-9ab2-c795ee80f0af" />


## Architecture

Backend is python + FASTAPI + BAML

Frontend is React

We try and stream whatever possible!

```bash
# Start the backend
cd backend
uv run fastapi run server.py --reload

```

```bash
# Start the frontend
cd frontend
pnpm dev
```

## Key Takeaways

- Dynamic schema generation enables systems to adapt to unknown data structures
- Meta programming with LLMs opens new possibilities for creating flexible components
- Building robust workflows around schema management is critical for production systems
- The execution and rendering of dynamic schemas presents both challenges and opportunities

## Resources

- [Session Recording](https://youtu.be/bak7-C--azc)
- [Discord Community](https://boundaryml.com/discord)
- Sign up for the next session on [Luma](https://lu.ma/baml)

---


## File: docs/meaisínfhoghlaim/baml/KCG_SUMMARY.md

# BAML — KCG Summary

## What It Is
Two workshop repositories from Boundary ML's "AI That Works" series demonstrating BAML (Basically A Made-up Language) — a domain-specific language for defining structured LLM outputs. The "Generative UIs" episode covers semantic streaming of partial, valid JSON objects for interactive AI experiences. The "Dynamic Schemas" episode demonstrates LLM-driven schema generation where the model first describes a schema, then extracts data against it — enabling extraction from unknown document structures.

## Why This Matters for Kings' College Galway
BAML is the structured-output backbone of the Celtic education pipeline. The generative UI pattern directly applies to the interactive Leaving Certificate problem solver: streaming structured step-by-step solutions (with LaTeX math, Irish translations, marking scheme points) as they generate, rather than waiting for the full response. The dynamic schema pattern enables extracting structured data from varied Irish curriculum documents (exam papers, syllabi, textbooks) without pre-defining schemas for every format — the LLM discovers the structure. This is essential for building a scalable ingestion pipeline that handles the full diversity of Celtic educational materials across exam boards (State Examinations Commission, CCEA, SQA, WJEC).

## Key Patterns Preserved
- `2025-09-09-generative-uis/README.md` — Generative UIs workshop: structured streaming patterns
- `2025-09-09-generative-uis/email.md` — Follow-up email with workshop resources
- `2025-09-09-generative-uis/meta.md` — Workshop metadata and links
- `2025-09-09-generative-uis/my-app/README.md` — Demo app: NextJS + BAML recipe generator
- `2025-09-30-dyanmic-schemas/README.md` — Dynamic schemas workshop: LLM-driven schema generation
- `2025-09-30-dyanmic-schemas/email.md` — Follow-up email with workshop resources
- `2025-09-30-dyanmic-schemas/meta.md` — Workshop metadata and links
- `2025-09-30-dyanmic-schemas/backend/README.md` — Backend: Python + FastAPI + BAML dynamic extraction
- `2025-09-30-dyanmic-schemas/frontend/README.md` — Frontend: React dynamic schema UI

## Source Files
Full source removed (2026-06-06). Available at:
- BAML: https://github.com/BoundaryML/baml

## What Was Removed
TypeScript/JavaScript source code, Python source, BAML schema files (.baml), React/NextJS components, package.json, lockfiles, CSS/HTML, Dockerfiles, CI/CD configs, Git metadata.

---


## File: docs/meaisínfhoghlaim/colpali/CHANGELOG.md

---
redirect: ../document-processing-reference.md
---

This content has been merged into [document-processing-reference.md](../document-processing-reference.md).

---


## File: docs/meaisínfhoghlaim/colpali/KCG_SUMMARY.md

# ColPali — KCG Summary

## What It Is
ColPali (Column-Paligemma) is a vision-language model for efficient document retrieval using visual embeddings. Instead of OCR → text → embedding pipelines, ColPali directly embeds document page images, capturing visual layout, tables, and formatting alongside text. Each document page produces a grid of patch-level embeddings (128-d per patch) enabling fine-grained visual search across document collections.

## Why This Matters for Kings' College Galway
ColPali is the chosen embedding backbone for the Leaving Certificate exam paper archive. Historical Irish exam papers contain complex mixed layouts (tables, formulae, diagrams, Irish/English bilingual sections) where traditional OCR-to-text pipelines lose critical visual context. ColPali's visual-first embedding preserves mathematical notation layout, graph structures, and bilingual text positioning — essential for accurate retrieval of past exam questions by topic. The patch-level embeddings enable finding specific diagrams or formula arrangements within dense exam pages. Combined with GaBERT for Irish text and BGE-M3 for multilingual, ColPali completes the multi-modal retrieval stack for the Celtic curriculum knowledge base.

## Key Patterns Preserved
- `README.md` — Redirect to document-processing-reference.md (content merged into main docs)
- `CHANGELOG.md` — Redirect to document-processing-reference.md (content merged into main docs)

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/illuin-tech/colpali

## What Was Removed
Python source code (.py), model configuration files (.json, .yaml), Jupyter notebooks, test files, package dependencies (pyproject.toml), Dockerfiles, CI/CD configs, Git metadata, data samples.

---


## File: docs/meaisínfhoghlaim/colpali/README.md

---
redirect: ../document-processing-reference.md
---

This content has been merged into [document-processing-reference.md](../document-processing-reference.md).

---


## File: docs/meaisínfhoghlaim/FIBO/CONTRIBUTING.md

# Contributing to FIBO

First off, thank you for considering contributing. Your help is greatly appreciated!

This document provides a set of guidelines for contributing to this project. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## How Can I Contribute?

There are two main ways you can contribute to this project:

### 1. Reporting Typos and Bugs

If you find a typo, a bug, or have a suggestion for improvement, please open an issue on GitHub. When creating an issue, please provide as much detail as possible, including:

- A clear and descriptive title.
- A detailed description of the issue or suggestion.
- Steps to reproduce the bug if applicable.

### 2. Submitting Community Pipelines

We encourage the community to share their own pipelines and examples. If you have a pipeline you'd like to share, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your changes.
3.  **Add your pipeline** to the `examples/community_pipelines/` directory. Please include a brief `README.md` within your pipeline's folder explaining what it does and how to use it.
4.  **Open a pull request** to the `main` branch of this repository.

When submitting a pull request, please ensure your code is well-documented and follows the existing coding style.

Thank you for your contributions!

---


## File: docs/meaisínfhoghlaim/FIBO/examples/README.md

# FIBO Inference Examples

This directory contains examples of how to use the FIBO inference scripts for different tasks.

## Tasks

The FIBO inference pipeline supports several tasks for generating and manipulating images.

### Generate

The `generate` task creates a structured JSON prompt from a short natural-language prompt using a Vision-Language Model (VLM), and then generates an image.

**Example:**
```bash
python generate.py --prompt "a majestic lion in the savannah" --output examples/outputs/generate.png
```

### Inspire

The `inspire` task takes an input image and uses the VLM to generate a structured JSON prompt that describes it. This prompt is then used to generate a new image.

**Example:**
```bash
python generate.py --image-path assets/zebra_balloons.jpeg --output examples/outputs/inspire.png
```

### Refine

The `refine` task modifies an existing structured JSON prompt based on editing instructions. This is useful for iterating on an idea without starting from scratch.

**Example:**
First, generate an image and its structured prompt:
```bash
python generate.py --prompt "a cat sitting on a mat" --output examples/outputs/refine_original.png
```
Then, refine it with editing instructions:
```bash
python generate.py --structured-prompt examples/outputs/refine_original.json --prompt "make the cat a dog" --output examples/outputs/refine_edited.png
```

### Raw (JSON)

The `raw` task allows you to provide a detailed, structured JSON prompt directly to the image generation pipeline, bypassing the VLM. This gives you maximum control over the output.

**Example:**
```bash
python generate.py --json-prompt examples/outputs/generate.json --output examples/outputs/generate_from_raw.png
```
You can also pass the JSON as a string.

## JSON Input Schema

When using the `raw` task, you provide a JSON object with a specific structure. Below is an overview of the schema and an example.

The main keys in the JSON prompt are:
- `short_description`: A brief summary of the image.
- `objects`: A list of objects in the scene, each with properties like `description`, `location`, `shape_and_color`, etc.
- `background_setting`: A description of the background.
- `lighting`: Details about the lighting conditions, direction, and shadows.
- `aesthetics`: Information about composition, color scheme, and mood.
- `photographic_characteristics`: Camera-related details like depth of field, focus, and angle.
- `style_medium`: The artistic medium (e.g., "photograph", "oil painting").
- `text_render`: Any text to be rendered in the image.
- `context`: Additional context or conceptual information about the image.
- `artistic_style`: The artistic style (e.g., "Surreal, realistic").

### Example JSON Input

Here is an example of a JSON prompt for the `raw` task.

```json
{
  "short_description": "A realistic image features a zebra standing on a concrete sidewalk next to a red fire hydrant. The zebra is positioned prominently in the center-right of the frame, facing towards the right with its head slightly lowered. The fire hydrant is in the bottom-left foreground. The background consists of a plain, light-colored wall, suggesting an urban or industrial setting. The lighting is even, highlighting the zebra's distinctive black and white stripes and the vibrant red of the hydrant.",
  "objects": [
    {
      "description": "A full-grown zebra with distinct black and white stripes covering its entire body. Its mane is short and upright, and its tail is long and bushy at the end. The zebra appears healthy and well-fed.",
      "location": "center-right",
      "relationship": "The zebra is standing next to the fire hydrant, appearing to be observing it or simply pausing in its vicinity.",
      "relative_size": "large within frame",
      "shape_and_color": "Elongated, equine shape with alternating black and white stripes.",
      "texture": "The zebra's coat appears smooth and short, typical of a mammal's fur. End of texture answer.",
      "appearance_details": "The stripes are sharply defined and vary in width and pattern across its body. Its muzzle is dark, and its eyes are dark and alert.",
      "number_of_objects": null,
      "pose": "Standing upright on all four legs, with its head slightly lowered and turned to its right.",
      "expression": "Calm and observant.",
      "clothing": null,
      "action": "Standing still.",
      "gender": "Unidentifiable.",
      "skin_tone_and_texture": null,
      "orientation": "Facing right."
    },
    {
      "description": "A classic red fire hydrant, cylindrical in shape with various valves and caps. It has a chain connecting two of its components.",
      "location": "bottom-left foreground",
      "relationship": "The fire hydrant is situated on the sidewalk, directly in front of the zebra's left front leg.",
      "relative_size": "medium",
      "shape_and_color": "Cylindrical, bright red.",
      "texture": "The fire hydrant appears to have a smooth, painted metallic surface with some visible wear and tear. End of texture answer.",
      "appearance_details": "It has a slightly weathered appearance, with some dirt or grime near its base.",
      "number_of_objects": null,
      "pose": null,
      "expression": null,
      "clothing": null,
      "action": null,
      "gender": null,
      "skin_tone_and_texture": null,
      "orientation": "Upright."
    }
  ],
  "background_setting": "The background is a plain, light gray concrete wall, suggesting an urban environment. Below the wall, there is a narrow strip of what appears to be dry grass or dirt, indicating a small patch of nature in an otherwise man-made setting. The ground is a concrete sidewalk with a curb separating it from a darker asphalt road.",
  "lighting": {
    "conditions": "Bright daylight",
    "direction": "Evenly lit, possibly from above or slightly front-lit.",
    "shadows": "Subtle, soft shadows are visible beneath the zebra and the fire hydrant, indicating a clear day with diffused light."
  },
  "aesthetics": {
    "composition": "Centered, with the zebra occupying the majority of the frame and the fire hydrant providing a contrasting element in the foreground.",
    "color_scheme": "Monochromatic (black and white) for the zebra, contrasted with a vibrant red for the hydrant and neutral grays for the background.",
    "mood_atmosphere": "Surreal and intriguing, due to the unexpected presence of a zebra in an urban setting."
  },
  "photographic_characteristics": {
    "depth_of_field": "Shallow, with the zebra and fire hydrant in sharp focus and the background slightly blurred.",
    "focus": "Sharp focus on subject.",
    "camera_angle": "Eye-level.",
    "lens_focal_length": "Standard."
  },
  "style_medium": "photograph",
  "text_render": [],
  "context": "This is an art piece or conceptual photograph, likely created digitally, that plays on the juxtaposition of a wild animal in an unexpected urban environment. It could be used for advertising, editorial content, or as a standalone piece of art designed to provoke thought or amusement.",
  "artistic_style": "Surreal, realistic"
}
```

---


## File: docs/meaisínfhoghlaim/FIBO/KCG_SUMMARY.md

# FIBO — KCG Summary

## What It Is
FIBO (Bria AI) is the first open-source, JSON-native text-to-image model trained exclusively on long structured captions (1,000+ words). With 8B parameters, it enables precise, reproducible control over lighting, composition, colour, and camera settings via VLM-guided JSON prompting. Supports iterative refinement, disentangled attribute control, and image-inspired generation. Trained on 100% licensed data.

## Why This Matters for Kings' College Galway
Structured, controllable image generation opens possibilities for generating culturally authentic Irish-language educational illustrations — from Celtic art and historical reconstructions to Leaving Certificate biology diagrams with bilingual labels. The JSON-structured prompt format aligns with the platform's BAML/structured-output pipeline for education content. FIBO's fine-tuning support (LoRA/LoKr) could adapt the model to Irish artistic styles and medieval manuscript illumination patterns, creating unique visual assets for Celtic Studies curriculum. The licensed-data training provides enterprise-grade legal clarity for commercial educational publishing.

## Key Patterns Preserved
- `README.md` — Full model documentation: features, quick start, inference, ComfyUI integration
- `CONTRIBUTING.md` — Contribution guidelines for the FIBO open-source project
- `src/fine_tuning/README.md` — Fine-tuning guide: LoRA/LoLKr adapters, regional prompting, inference
- `examples/README.md` — Example usage patterns and prompts

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/briaai/FIBO
- Hugging Face: https://huggingface.co/briaai/FIBO

## What Was Removed
Python source code, model weights/checkpoints (58M of .safetensors, .bin files), ComfyUI node definitions, Dockerfiles, CI/CD configs, example images (PNG/JPEG), package dependencies (pyproject.toml, requirements.txt), evaluation scripts, Git metadata.

---


## File: docs/meaisínfhoghlaim/FIBO/README.md

<p align="center">
  <img src="assets/Bria-logo.svg" width="200"/>
</p>

<p align="center">
  <!-- GitHub Repo -->
  <a href="https://huggingface.co/briaai/FIBO" target="_blank">
    <img
      alt="Hugging Face model card"
      src="https://img.shields.io/badge/Hugging%20Face-Model%20Card-FFD21E?logo=huggingface&logoColor=black&style=for-the-badge"
    />
  </a>
  &nbsp;

  <!-- Hugging Face Demo -->
  <a href="https://huggingface.co/spaces/briaai/FIBO" target="_blank">
    <img
      alt="Hugging Face Demo"
      src="https://img.shields.io/badge/Hugging%20Face-Demo-FFD21E?logo=huggingface&logoColor=black&style=for-the-badge"
    />
  </a>
  &nbsp;

  <!-- FIBO Demo on Bria (replace URL if you have a specific demo link) -->
  <a href="https://platform.bria.ai/labs/fibo" target="_blank">
    <img
      alt="FIBO Demo on Bria"
      src="https://img.shields.io/badge/FIBO%20Demo-Bria-6C47FF?style=for-the-badge"
    />
  </a>
  &nbsp;

  <!-- Bria Platform -->
  <a href="https://platform.bria.ai" target="_blank">
    <img
      alt="Bria Platform"
      src="https://img.shields.io/badge/Bria-Platform-0EA5E9?style=for-the-badge"
    />
  </a>
  &nbsp;

  <!-- Bria Discord -->
  <a href="https://discord.com/invite/Nxe9YW9zHS" target="_blank">
    <img
      alt="Bria Discord"
      src="https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white&style=for-the-badge"
    />
  </a>
   &nbsp;

  <!-- Bria Paper -->
  <a href="https://arxiv.org/abs/2511.06876" target="_blank">
    <img
      alt="Tech Paper"
      src="https://img.shields.io/badge/Tech%20Paper-lightgrey?logo=arxiv&logoColor=red&style=for-the-badge"
    />
  </a>
</p>
<p align="center">
  <img src="assets/car.001.jpeg" width="1024"/>
</p>

<p align="center">
  <b>FIBO is the first open-source, JSON-native text-to-image model trained exclusively on long structured captions.</b>
  <br><br>
  <i>Fibo sets a new standard for controllability, predictability, and disentanglement.</i>
</p>

<!-- ===================== MAIN CONTENT ===================== -->

<h2>🌍 What's FIBO?</h2>
<p>Most text-to-image models excel at imagination—but not control. <b>FIBO</b> is built for professional workflows, not casual use. Trained on <b>structured JSON captions up to 1,000+ words</b>, FIBO enables precise, reproducible control over lighting, composition, color, and camera settings. The structured captions foster native disentanglement, allowing targeted, iterative refinement without prompt drift. With only <b>8B parameters</b>, FIBO delivers high image quality, strong prompt adherence, and professional-grade control—<b>trained exclusively on licensed data</b>.</p>

<h2>🔑 Key Features</h2>
<ul>
  <li><b>VLM guided JSON-native prompting</b>: Incorporates any VLM to transform short prompts into structured schemas with 1,000+ words (lighting, camera, composition, DoF).</li>
  <li><b>Iterative controlled generation</b>: generate images from short prompts or keep refining and get inspiration from detailed JSONs and input images</li>
  <li><b>Disentangled control</b>: tweak a single attribute (e.g., camera angle) without breaking the scene.</li>
  <li><b>Enterprise-grade</b>: 100% licensed data; governance, repeatability, and legal clarity.</li>
  <li><b>Strong prompt adherence</b>: high alignment on PRISM-style evaluations.</li>
  <li><b>Built for production</b>: API endpoints (Bria Platform, Fal.ai, Replicate), ComfyUI nodes, and local inference.</li>
</ul>

<h2>🎨 Work with FIBO in Three Simple Modes</h2>

<ul>
  <li>
    <b>Generate:</b> Start with a quick idea. FIBO’s language model expands your short prompt into a rich, structured JSON prompt, then generates the image. 
    You get both the image and the expanded prompt.
  </li>
  <li>
    <b>Refine:</b> Continue from a detailed structured prompt add a short instruction - for example, “backlit,” “85 mm,” or “warmer skin tones.” 
    FIBO updates <i>only</i> the requested attributes, re-generates the image, and returns the refined prompt alongside it.
  </li>
  <li>
    <b>Inspire:</b> Provide an image instead of text. FIBO’s vision–language model extracts a detailed, structured prompt, blends it with your creative intent, and produces related images—ideal for inspiration without overreliance on the original.
  </li>
</ul>
<h2> News</h2>
<ul>
  <li>2025-11-11: Technical report is now available <a href="https://arxiv.org/abs/2511.06876">here</a> 🎉</li>
  <li>2025-11-11: Fine-tuning code is now available <a href="src/fine_tuning/README.md">here</a> 🎉</li>
  <li>2025-11-10: Add support for TeaCache to speed up generation by 3x with minimal quality loss 🏎️</li>
</ul>

<h2>⚡ Quick Start</h2>

</p>

<p align="center">
  <a href="https://huggingface.co/spaces/briaai/FIBO" target="_blank" style="text-decoration:none;">
    🚀 Try FIBO now →
  </a>
</p>

<p>FIBO is available everywhere you build, either as source-code and weights, ComfyUI nodes or API endpoints.</p>

<p><b>API Endpoint:</b></p>
<ul>
  <li><a href="https://docs.bria.ai/image-generation/v2-endpoints/image-generate">Bria.ai</a></li>
  <li><a href="https://fal.ai/models/bria/fibo/generate">Fal.ai</a></li>
  <li><a href="https://replicate.com/bria/fibo">Replicate</a></li>
</ul>

<p><b>ComfyUI:</b>
<ul>
  <li><a href="https://github.com/Bria-AI/ComfyUI-BRIA-API/blob/main/nodes/generate_image_node_v2.py">Generate Node</a></li>
  <li><a href="https://github.com/Bria-AI/ComfyUI-BRIA-API/blob/main/nodes/refine_image_node_v2.py">Refine Node</a></li>
</ul></p>

<p><b>Source-Code & Weights</b></p>

<ul>
  <li>The model is open source for non-commercial use with <a href="https://creativecommons.org/licenses/by-nc/4.0/deed.en">this license</a> </li>
  <li>For commercial use <a href="https://bria.ai/contact-us?hsCtaAttrib=114250296256">Click here</a>.</li>
</ul>
    
<h2>Quick Start Guide</h2>
<ol>
  <li>
    <p>Clone the repo</p>
    <pre><code class="language-bash">git clone https://github.com/Bria-AI/FIBO.git
cd FIBO
</code></pre>
  </li>
  <li>
  <p>Login to Hugging Face:</p>
  <p>
    Request model access at <a href="https://huggingface.co/briaai/FIBO" target="_blank">this link</a>
  </p>
  <pre><code class="language-bash">hf auth login</code></pre>
  </li>
  <li>
    <p>Install <code>uv</code>:</p>
    <p>Instructions taken from <a href="https://docs.astral.sh/uv/getting-started/installation/">here</a>.</p>
    <p>For linux systems this should be:</p>
    <pre><code class="language-bash">curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
</code></pre>
  </li>
  <li>
    <p>Install the dependencies:</p>
    <pre><code class="language-bash">uv sync
</code></pre>
  </li>
  <li>
    <p>Activate your <code>.venv</code> and set the Python env:</p>
    <pre><code class="language-bash">source .venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${PWD}
</code></pre>
  </li>
</ol>

## Development

This project uses a `Makefile` to streamline common development tasks.

To install dependencies and set up pre-commit hooks, run:

```bash
make install
```

The following commands are also available:

*   `make lint`: Run linters to check for code quality.
*   `make format`: Format the code according to the project's style guidelines.
*   `make check`: Run both linters and formatters.
*   `make clean`: Remove the virtual environment.
*   `make help`: Display a list of all available commands.

<h3>Gemini Setup</h3>

<p>To use Gemini as the Vision-Language Model (VLM) backend for FIBO, some additional setup is needed.</p>

<ol>
  <li>
    <p><b>Obtain a Gemini API Key</b><br/>
    Sign up for the <a href="https://aistudio.google.com/app/apikey">Google AI Studio (Gemini)</a> and create an API key.</p>
  </li>
  <li>
    <p><b>Set the API Key as an Environment Variable</b><br/>
    Store your Gemini API key in the <code>GOOGLE_API_KEY</code> environment variable:</p>
    <pre><code class="language-bash">export GOOGLE_API_KEY=your_google_api_key
</code></pre>
    <p>You can add the above line to your <code>.bashrc</code>, <code>.zshrc</code>, or similar shell profile for persistence.</p>
  </li>
</ol>
<h3>Generate</h3>

<p>FIBO uses a VLM that transforms short prompts into detailed structured prompts that are used to generate images. You can use the following code to generate images using Gemini via the Google API - **requires a GOOGLE_API_KEY**, or use --model-mode local to use the local VLM instead (FIBO-VLM):</p>

```bash
python generate.py --prompt "A hyper-detailed, ultra-fluffy owl sitting in the trees at night, looking directly at the camera with wide, adorable, expressive eyes. Its feathers are soft and voluminous, catching the cool moonlight with subtle silver highlights. The owl's gaze is curious and full of charm, giving it a whimsical, storybook-like personality." --seed 1 --output examples/outputs/generate.png
```

<p>To use the local VLM (FIBO-VLM) instead of Gemini, add <code>--model-mode local</code> to the command.</p>

```bash
python generate.py --prompt "A hyper-detailed, ultra-fluffy owl sitting in the trees at night, looking directly at the camera with wide, adorable, expressive eyes. Its feathers are soft and voluminous, catching the cool moonlight with subtle silver highlights. The owl's gaze is curious and full of charm, giving it a whimsical, storybook-like personality." --seed 1 --output examples/outputs/generate.png --model-mode local
```

<p><img src="assets/owl.png" alt="alt text" width="300"/></p>


<h3>Refine</h3>
<p>FIBO supports iterative generation. Given a structured prompt and an instruction, FIBO refines the output.</p>

```bash
python generate.py --structured-prompt examples/outputs/generate.json --prompt "make the owl brown" --output examples/outputs/refine.png
```
<table align="center">
  <tr>
    <td><img src="assets/make_owl_brown.png" alt="Make owl brown" width="100%"/><figcaption>Make owl brown</figcaption></td>
    <td><img src="assets/turn_owl_into_a_lemur_.png" alt="Turn owl into a lemur" width="100%"/><figcaption>Turn owl into a lemur</figcaption></td>
  </tr>
  <tr>
    <td><img src="assets/add_jungle_vegetation_to_the_dark_background.png" alt="Add jungle vegetation" width="100%"/><figcaption>Add jungle vegetation</figcaption></td>
    <td><img src="assets/add_sunlight.png" alt="Add sunlight" width="100%"/><figcaption>Add sunlight</figcaption></td>
  </tr>
</table>

<h3>Inspire</h3>
<p>Start from an image as inspiration and let Fibo regenerate a variation of it or merge your creative intent into the next generation</p>

```bash
python generate.py --image-path assets/original.png --output examples/outputs/inspire.png
```
```bash
python generate.py --image-path assets/original.png --prompt "Make futuristic" --output examples/outputs/inspire-prompt.png
```

<table align="center">
  <tr>
    <td><img src="assets/original.png" alt="original image" width="100%" title="original image" /><figcaption>original image</figcaption></td>
    <td><img src="assets/no_prompt.png" alt="No prompt" width="100%" title="No prompt" /><figcaption>No prompt</figcaption></td>
    <td><img src="assets/make_futuristic.png" alt="Make futuristic" width="100%" title="Make futuristic" /><figcaption>Make futuristic</figcaption></td>
  </tr>
</table>

<h3> Faster Inference with TeaCache</h3>
<p>Enable TeaCache to speed up generation by <b>3x</b> with minimal quality loss:</p>

```bash
python generate.py --prompt "your prompt" --enable-teacache
```

<p>Adjust the threshold for speed/quality tradeoff (default 1.0, recommended 0.6-1.0):</p>

```bash
python generate.py --prompt "your prompt" --enable-teacache --teacache-threshold 0.8
```

<table align="center">
  <tr>
    <td><img src="examples/outputs/generated_without_teacache.png" alt="Without TeaCache" width="100%"/><figcaption>Without TeaCache (baseline)</figcaption></td>
    <td><img src="examples/outputs/generated_teacache.png" alt="With TeaCache" width="100%"/><figcaption>With TeaCache (3x faster)</figcaption></td>
  </tr>
</table>

<p>see the examples in the <a href="examples">examples</a> directory for more details.</p>

<h2>🧠 Training and Architecture</h2>

<p><strong>FIBO</strong> is an 8B-parameter DiT-based, flow-matching text-to-image model trained <strong>exclusively on licensed data</strong> and on <strong>&gt;long, structured JSON captions</strong> (~1,000 words each), enabling strong prompt adherence and professional-grade control. It uses <strong>SmolLM3-3B</strong> as the text encoder with a novel <strong>DimFusion</strong> conditioning architecture for efficient long-caption training, and <strong>Wan 2.2</strong> as the VAE. The structured supervision promotes native disentanglement for targeted, iterative refinement without prompt drift, while VLM-assisted prompting expands short user intents, fills in missing details, and extracts/edits structured prompts from images using our fine-tuned <strong>Qwen-2.5</strong>-based VLM or <strong>Gemini 2.5 Flash</strong>. For reproducibility, we provide the assistant system prompt and the structured-prompt JSON schema across the “Generate,” “Refine,” and “Inspire” modes.</p>
<p><img src="assets/arch.png" alt="architecture" /></p>


<h2 id="data-distribution">Data Distribution</h2>

<p>FIBO was trained on curated set of image–caption pairs selected from ~1B image dataset as shown in the dataset distribution. All assets are vetted for commercial use, attribution traceability, and regional compliance under GDPR and the EU AI Act. This broad and balanced dataset ensures FIBO’s ability to generalize across a wide range of visual domains, from realistic human imagery to graphic design and product visualization, while maintaining full licensing compliance.</p>

<p><img src="assets/DataAttr.png" alt="alt text" width="800"/></p>

<h2 id="Evaluation">Evaluation</h2>

<!-- ===================== BENCHMARK TABLE FIGURE ===================== -->
<h3 id="PRISM Benchmark model-comparison">PRISM Benchmark Model Comparison</h3>

<p>Using a licensed-data subset of PRISM-Bench, we evaluate image–text alignment and aesthetics. <strong>FIBO</strong> outperforms comparable open-source baselines, suggesting strong prompt adherence, controllability and aesthetics from structured-caption training.</p>

<img src="assets/Benchmark.png" alt="Benchmark Chart" width="800"/>

<h2 id="More Samples">More Samples</h2>

<p>Generate</p>
<div class="image-row">
  <figure>
    <img src="assets/Generate.png"/>
  </figure>
</div>

<p>Inspire & Refine</p>
<div class="image-row">
  <figure>
  <img src="assets/Refine.png"/>
  </figure>
</div>

<h2> 💬 Contact Us</h2>
<p>If you have questions about this repository, feedback to share, or want to contribute directly, we welcome your issues and pull requests on GitHub. Your contributions help make FIBO better for everyone.</p>

<p>If you're passionate about fundamental research, we're hiring full-time employees (FTEs) and research interns. Don't wait - reach out to us at <a href="mailto:hr@bria.ai">hr@bria.ai</a></p>

## Citation

We kindly encourage citation of our work if you find it useful.

```bibtex
@misc{gutflaish2025generating,
  title         = {Generating an Image From 1,000 Words: Enhancing Text-to-Image With Structured Captions},
  author        = {Gutflaish, Eyal and Kachlon, Eliran and Zisman, Hezi and Hacham, Tal and Sarid, Nimrod and Visheratin, Alexander and Huberman, Saar and Davidi, Gal and Bukchin, Guy and Goldberg, Kfir and Mokady, Ron},
  year          = {2025},
  eprint        = {2511.06876},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CV},
  doi           = {10.48550/arXiv.2511.06876},
  url           = {https://arxiv.org/abs/2511.06876}
}
```

<p align="center"><b>🤗 <a href="https://huggingface.co/briaai/FIBO " target="_blank">Like FIBO on Hugging Face</a> to support responsible generative AI!</b></p>

---


## File: docs/meaisínfhoghlaim/FIBO/src/fine_tuning/README.md

# FIBO Fine-Tuning Guide

This guide explains how to fine-tune the FIBO model using LoRA (Low-Rank Adaptation) and generate images with the fine-tuned checkpoints.

## Overview

The fine-tuning process uses LoRA to efficiently adapt the FIBO transformer model to your custom dataset. Training saves checkpoints at regular intervals, which can then be used for image generation.

## Dataset Format

Your training dataset should be organized as follows:

```
dataset_directory/
├── image1.jpg
├── image2.jpg
├── ...
└── metadata.csv
```

The `metadata.csv` file should have two columns:
- `file_name`: Name of the image file
- `caption`: JSON-formatted structured prompt describing the image. Consider using constant phrasing (like a trigger word) or "freezing" JSON fields that should have common content across all images (e.g., "style_medium").

Example `metadata.csv`:
```csv
file_name,caption
image1.jpg,"{""short_description"":""A charming bear..."",""objects"":[...]}"
image2.jpg,"{""short_description"":""Another bear..."",""objects"":[...]}"
```

**Note**: The captions must be valid JSON strings. The training script will validate and normalize them automatically.

## Fine-Tuning

### Basic Training Command

```bash
python src/fine_tuning/fine_tune_fibo.py \
  --checkpointing_steps 250 \
  --max_train_steps 1010 \
  --output_dir example_finetune_results \
  --dataset_name briaai/fine_tune_example \
  --lora_rank 64 \
  --train_batch_size 1 \
  --gradient_accumulation_steps 4 \
  --gradient_checkpointing 1
```

### Key Parameters

- `--dataset_name`: Path to your dataset directory (containing images and `metadata.csv`)
- `--output_dir`: Directory where checkpoints will be saved
- `--lora_rank`: LoRA rank (higher = more capacity, default: 128). Common values: 32, 64, 128
- `--train_batch_size`: Batch size per device (default: 1)
- `--gradient_accumulation_steps`: Number of steps to accumulate gradients before updating (default: 4)
- `--max_train_steps`: Total number of training steps
- `--checkpointing_steps`: Save checkpoint every N steps (default: 250)
- `--learning_rate`: Learning rate (default: 1.0 for Prodigy optimizer)
- `--gradient_checkpointing`: Enable gradient checkpointing to save memory (1 = enabled)

### Additional Useful Parameters

- `--caption_column`: Column name in metadata.csv containing captions (default: "caption")
- `--image_column`: Column name in metadata.csv containing image filenames (default: "image")
- `--repeats`: Number of times to repeat each training sample (default: 1)
- `--resume_from_checkpoint`: Resume from a checkpoint path or "latest" (default: "no")
- `--optimizer`: Optimizer type - "prodigy" (default) or "adamw"
- `--mixed_precision`: Mixed precision training - "bf16" (default), "fp16", or "no"


## Checkpoints

During training, checkpoints are saved in the `output_dir` as:
```
output_dir/
├── checkpoint_250/
├── checkpoint_500/
├── checkpoint_750/
└── checkpoint_final/
```

Each checkpoint directory contains:
- Training state (optimizer, scheduler, etc.)
- LoRA weights (saved in a format compatible with `FluxLoraLoaderMixin`)

## Image Generation with Fine-Tuned Checkpoints

After training, you can generate images using your fine-tuned LoRA weights.

### Basic Generation Command

```bash
python src/fine_tuning/generate_with_lora.py \
  --pretrained_model_name_or_path briaai/FIBO \
  --lora_ckpt_path example_finetune_results/checkpoint_final \
  --structured_prompt_path example_structured_prompt.json \
  --output_image_path generated_image.png \
  --seed 42
```

### Parameters

- `--pretrained_model_name_or_path`: Base FIBO model path (default: "briaai/FIBO")
- `--lora_ckpt_path`: Path to the checkpoint directory containing LoRA weights (e.g., `checkpoint_final`)
- `--structured_prompt_path`: Path to a JSON file containing the structured prompt
- `--output_image_path`: Where to save the generated image
- `--seed`: Random seed for reproducibility (default: 42)

### Prompt Format

The `--structured_prompt_path` argument should point to a JSON file containing a structured prompt. This prompt should use the same format as the captions you used for training. If your training set included certain fields with repeating content, or a recurring trigger word, make sure to also include those in your generation prompt for best results.

```json
{
  "short_description": "A charming, cartoon-style brown bear...",
  "objects": [...],
  "background_setting": "...",
  "lighting": {...},
  "aesthetics": {...},
  ...
}
```

## Tips

1. **LoRA Rank**: Start with `--lora_rank 64` for most use cases. Increase to 128 for more complex adaptations, or decrease to 32 for simpler tasks.

2. **Training Steps**: Monitor your training loss. Typically 1000-2000 steps is sufficient, but this depends on your dataset size and complexity.

3. **Batch Size**: With `--train_batch_size 1` and `--gradient_accumulation_steps 4`, the effective batch size is 4. Adjust based on your GPU memory.

> **Note:** If your dataset contains images of multiple resolutions (i.e., images are not all the same size), you may encounter issues with `--train_batch_size` greater than 1. In such cases, set the batch size to 1 to avoid shape mismatches.

4. **Memory Optimization**: Enable `--gradient_checkpointing 1` to reduce memory usage at the cost of slightly slower training.

5. **Resuming Training**: Use `--resume_from_checkpoint latest` to resume from the most recent checkpoint, or specify a path like `--resume_from_checkpoint checkpoint_500`.

6. **Multi-GPU Training**: The script supports distributed training. Use `accelerate launch` for multi-GPU setups.

## Environment Variables for Distributed Training

For optimal performance in multi-GPU/distributed training setups (especially on AWS with EFA), you may want to set the following environment variables before running the training script:

```bash
export NCCL_DEBUG=WARN
export FI_PROVIDER=efa
export FI_EFA_USE_DEVICE_RDMA=1
export NCCL_MIN_NCHANNELS=8
export NCCL_NET_GDR_LEVEL=PHB
export NCCL_P2P_LEVEL=NVL
export CUDA_DEVICE_MAX_CONNECTIONS=1
export CUDA_LAUNCH_BLOCKING=0
export NCCL_IB_DISABLE=0
```

These settings optimize NCCL communication for AWS EFA (Elastic Fabric Adapter) and improve multi-GPU training performance. You can add these to your shell profile or set them before running the training command.

## Troubleshooting

- **Invalid JSON captions**: Ensure all captions in `metadata.csv` are valid JSON. The script will raise an error with details if validation fails.

- **Out of memory**: Reduce `--train_batch_size`, increase `--gradient_accumulation_steps`, or enable `--gradient_checkpointing`.

- **Checkpoint not found**: Verify the checkpoint path exists and contains LoRA weights. The path should point to a `checkpoint_N` directory, not the parent `output_dir`.


---


## File: docs/meaisínfhoghlaim/federated/KCG_SUMMARY.md

# Federated Learning — KCG Summary

## What It Is
Two complementary projects for privacy-preserving federated machine learning. `syft-flwr` is an open-source framework combining Flower's federated learning with OpenMined's SyftBox protocol for trustless cross-silo training. `flwr` (fantastic-enigma) is a companion repo demonstrating federated supervised fine-tuning of LLMs (Llama 3.2 1B, Pythia 70M) using the Flower AI framework.

## Why This Matters for Kings' College Galway
Federated learning enables training Celtic language models on student data distributed across schools without centralising sensitive educational records — critical for GDPR compliance in Irish classrooms. The FedRAG notebook demonstrates privacy-preserving RAG across distributed document sources, directly applicable to Leaving Certificate curriculum materials held by different schools. The FL diabetes prediction pattern translates to distributed educational assessment models (predicting student performance from private gradebooks). SyftBox's trustless protocol is ideal for inter-institutional collaboration between Irish-language schools (Gaelscoileanna) where no single party should hold all data.

## Key Patterns Preserved
- `syft-flwr/README.md` — Main framework overview: Flower + SyftBox integration for federated learning
- `syft-flwr/RELEASE.md` — Release process documentation for syft-flwr
- `syft-flwr/docs/message_flow.md` — Architecture: how messages flow between Flower and SyftBox nodes
- `syft-flwr/notebooks/fl-diabetes-prediction/README.md` — Multi-round federated model training walkthrough
- `syft-flwr/notebooks/federated-analytics-diabetes/README.md` — Privacy-preserving statistical queries across distributed datasets
- `syft-flwr/notebooks/fedrag/README.md` — Federated RAG with remote data science workflow
- `flwr/README.md` — Federated LLM finetuning playground with Flower

## Source Files
Full source removed (2026-06-06). Available at:
- syft-flwr: https://github.com/OpenMined/syft-flwr
- flwr: https://github.com/adap/flower

## What Was Removed
Python source code, Jupyter notebook .ipynb files, model checkpoints, package dependencies (pyproject.toml, uv.lock), Dockerfiles, CI/CD configs, training data, images/gifs, Git metadata.

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/docs/message_flow.md

# RPC Message Flow in Syft-FLWR:

1. Server (grid.py): `flower_message_to_bytes() → rpc.send() → filesystem`
2. Client (flower_client.py): `Filesystem → bytes_to_flower_message() → Flower processing`
3. Response (flower_client.py): `Process → _handle_normal_message() → response`

## Filesystem
"Filesystem" in SyftBox context means SyftBox's peer-to-peer file synchronization network that enables distributed communication without direct connections between parties.

1. Server Side (`grid.py`):
`future = rpc.send(url=url, body=msg_bytes, client=self._client)`
2. `rpc.send()` (`rpc.py`): `syft_request.dump(req_path)`  # Writes to local filesystem
3. File Location (`rpc.py`):
```python
local_path = syft_request.url.to_local_path(client.workspace.datasites)
req_path = local_path / f"{syft_request.id}.request"
```
Concrete Example:

- URL: `syft://user@domain.com/app_data/flwr/flwr_app_name/rpc/messages`
- File Path:
`~/SyftBox/datasites/user@domain.com/app_data/flwr/app_name/rpc/messages/{uuid}.request`

### Request / Response Flow
1. Write: Server creates `.request` file in target user's datasite directory
2. Sync: SyftBox daemon (installed with the SyftBox client via https://syftbox.net) syncs file across network to recipient's machine
3. Watch: Recipient's `SyftEvents` watches filesystem and triggers on new `.request` files
4. Process: Handler processes request and writes `.response` file
5. Sync Back: Response file syncs back to sender

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/federated-analytics-diabetes/fed-analytics-diabetes/README.md

# Federated Analytics on Diabetes Dataset


## References
- https://syftbox.net
- [Federated Analytics with Flower and Pandas](https://flower.ai/blog/2023-01-24-federated-analytics-pandas/)
- https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database/
- https://github.com/OpenMined/syftbox
- https://github.com/OpenMined/syft-flwr
- https://github.com/adap/flower/
- https://github.com/OpenMined/rds
- https://github.com/elarsiad/diabetes-prediction-keras
---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/federated-analytics-diabetes/README.md

# Federated Analytics with `syft_flwr`

## Introduction

In this tutorial, we will walk through a practical implementation of a federated analyics workflow, e.g. finding mean and historgram of some private datasets and then aggregate them, using [syft_flwr](https://github.com/OpenMined/syft-flwr) — a framework that combines the flexibility of [Flower](https://github.com/adap/flower/) (a popular federated learning framework) with the privacy-preserving networking capabilities of [syftbox](https://www.syftbox.net/).

![FL Training Process](./images/fed-analytics.gif)

## Set up

### Clone the project
```bash
git clone https://github.com/OpenMined/syft-flwr.git _tmp \
		&& mv _tmp/notebooks/federated-analytics-diabetes . \
		&& rm -rf _tmp && cd federated-analytics-diabetes
```

### Setup python virtual environment
Assume that you have python and the [uv](https://docs.astral.sh/uv/) package manager installed. Now let's create a virtual python environment with `jupyter` installed:
```bash
uv sync
```

## Workflow

### Local Setup
The set of notebooks in `local/` shows how things work with 2 data owners and 1 data scientists, whose datasites all stay in a local SyftBox network on your machine.

Please start with the `do1.ipynb`, then go to the `do2.ipynb`, and finally `ds.ipynb`, and switch hats when necessary when indicated to do so.

### Distributed setup
In the distributed setup in `distributed/`, we have the exact same workflow except that each DO's datasite and the DS's datasite run on different machines, and they communicate using the SyftBox client. There are detailed instructions to install the SyftBox client in the notebooks.

## References
- https://syftbox.net
- https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database/
- https://github.com/OpenMined/syftbox
- https://github.com/OpenMined/syft-flwr
- https://github.com/adap/flower/
- https://github.com/OpenMined/rds

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fedrag/fedrag_v1/README.md

---
title: Federated RAG (FedRAG)
tags: [fedrag, llm]
dataset: [PubMed, StatPearls, Textbooks, Wikipedia, PubMedQA, BioASQ]
framework: [FAISS, transformers]
---

# Federated Retrieval Augmented Generation (FedRAG)

Large Language Models (LLMs) benefit from Retrieval Augmented Generation (RAG) pipelines, which ground their responses
in external data to improve performance. However, organizations often store data in isolated data silos, constraining
classical RAG approaches that rely on centralized data access. By combining Federated Learning with RAG we can query
data across distributed silos without the need to centrally aggregate data, while respecting data privacy.

> \[!NOTE\]
> This example uses Flower's Message API which remains a preview feature and subject to change.
> Both `ClientApp` and `ServerApp` operate directly on the [Message](https://flower.ai/docs/framework/ref-api/flwr.common.Message.html)
> and [RecordDict](https://flower.ai/docs/framework/ref-api/flwr.common.RecordDict.html) objects.

## Advanced FedRAG Examples

This example provides the building blocks to develop more advanced Federated RAG pipelines, such as enhancing domain-specific
fine-tuned LLMs [\[1\]](#ref1), using confidential compute environments for secure document re-ranking and LLM inference
[\[2\]](#ref2), and applying collaborative ANN searches on encrypted data with homomorphic encryption
and multiplicative caching for improved performance [\[3\]](#ref3).

## FedRAG Pipeline Overview

The figure below demonstrates an overview of the Federated RAG pipeline.

![image info](../images/FedRAG.png)

Given a user query, the server broadcasts the query to each client. Every client retrieves the relevant (top-k)
documents related to the given query and sends them back to the server. The server merges and ranks the retrieved
documents and passes the re-ranked documents as context to the augmented query prompt submitted to the LLM.

## Setup the Example

### System Prerequisites

Depending on whether you are running on macOS, RHEL, Debian please make sure
that the following packages are already installed in your system `wget`, `git-lfs`.

<details>
<summary> Installation instructions for different OS </summary>

```
# wget is used to download .tar files from the Web
# git-lfs is used to download large files from the Hugging Face respository

# macOS
brew install wget
brew install git-lfs

# RHEL
yum install wget
yum install git-lfs

# Ubuntu/Debian
apt install wget
apt install git-lfs

# Windows
# If you are on Windows, it is highly recommended to make use of WSL with Ubuntu to run your Flower apps.
# Then, you can install the packages using the above Ubuntu commands.
# Extra tip: with WSL you can also make use of the NVIDIA GPU in your Windows host.

# enable Git LFS in your Git environment
# (holds for all systems)
git lfs install
```

</details>

### Clone the Example

Start by cloning the example project:

```shell
git clone --depth=1 https://github.com/adap/flower.git _tmp \
        && mv _tmp/examples/fedrag . \
        && rm -rf _tmp \
        && cd fedrag
```

This will create a new directory called `fedrag`.

### Install Dependencies

To install all dependencies required to run the example, from the top-level `fedrag` directory execute the following command:

```bash
pip install -e .
```

### Download & Index Corpus

Before you run the Flower engine, please make sure you have downloaded the corpus we need for document retrieval
and created the respective document indices. To accomplish this, run the following helper bash script:

```bash
./data/prepare.sh
```

By default, the above script will download the `Textbooks` and `StatPearls` corpora and create an index
for each corpus using the first `100` chunks (documents). The processed data will be downloaded under the `data/corpus`
directory. The total required disk space for all the documents of `Textbooks` and `StatPearls` is around `3GBs`.

To download all corpora and create an index for all files, please run the following command:

```bash
./data/prepare.sh --datasets "pubmed" "statpearls" "textbooks" "wikipedia" --index_num_chunks 0
```

The total disk space for the all documents of all four corpora is around `120GBs`.

> \[!NOTE\]
> Please note that for each corpus, its corresponding index might need exactly the same disk space as the documents being indexed.

For an individualized breakdown of the disk space, number of documents, number of snippets, and the domain of each
corpus, please refer to the [README.md](data/README.md) file under the `data` directory.

For more details regarding how each corpus is downloaded and how the corresponding index is created,
please read the section below as well the previously referenced [README.md](data/README.md).

All corpora used in this work were derived from the MedRAG toolkit [\[4\]](#ref4).

## Run with Simulation Engine

From the top-level directory for this example, launch the simulation:

```bash
flwr run .
```

## Expected Results

At the end of execution you should see a message in the console that will show the name of
each QA dataset (`pubmedqa`, `bioasq`), the total number of evaluated questions, total number
of answered questions, accuracy, and the mean wall-clock execution time for all answered questions.

For instance, the returned result would look like follows:

| **QA Dataset** | **#Questions** | **#Answered** | **Accuracy** | **Time (secs)** |
| :------------: | :------------: | :-----------: | :----------: | :-------------: |
|    PubMedQA    |       10       |       8       |     0.53     |      6.03       |
|     BioASQ     |       10       |       9       |     0.61     |      5.83       |

## FedRAG Pipeline Description

### Corpus, Indices & Benchmark Datasets

**Corpus.** The example supports the following corpora for document retrieval:

1. PubMed
2. Textbooks
3. StatPearls
4. Wikipedia

By default, the example uses the `Textbooks` and `StatPearls` corpora.

> \[!NOTE\]
> The example uses by default the `Textbooks` and `StatPearls` corpora to demonstrate the FedRAG pipeline,
> because the number of documents for `PubMed` and `Wikipedia` are extremely large and downloading and index creation
> can take a lot of time. Please see the instructions [README.md](data/README.md) file on how to
> download the rest of the corpora.

**Index.** For document indexing and retrieval, the example uses the [FAISS](https://github.com/facebookresearch/faiss)
library.

> \[!NOTE\]
> The example creates by default an index using the first 100 downloaded chunks (i.e., 100 documents).
> We do so in order to quickly create an index for each corpus and bootstrap the example.
> If you want to create an index for all files, please set the `index_num_chunks` flag to `0`.

**QA Datasets.** For QA benchmarking, the example supports the following benchmark datasets:

1. PubMedQA
2. BioASQ
3. MMLU
4. MedQA
5. MedMCQA

By default, the example will evaluate the first `10` questions of the `PubMedQA` and `BioASQ` QA datasets.
To evaluate all the questions from the benchmark dataset, you can disable or comment out the `server-qa-num`
value in the `pyproject.toml` file.

Please see also the section below on how to enable more QA datasets.
All the curated QA benchmark datasets are downloaded from the [MIRAGE](https://github.com/Teddy-XiongGZ/MIRAGE) benchmark \[1\].

For more details regarding corpus downloading, pre-processing, and indexing steps,
please read the [README.md](../fedrag/data/README.md) file under the `data` directory.

### Document Retrieval and Merge

**Retrieval.** The clients use their local FAISS index to retrieve documents from their local document store.
The `k-nn` value defined in the `[tool.flwr.app.config]` section of the `pyproject.yaml` file controls how many
documents will be retrieved by each client and sent back to the server. The current implementation of document retrieval
for the FAISS index is built with `IndexIVFFlat` and uses the `faiss.METRIC_L2` metric, which means that the lower
the score of a retrieved document the better, since L2 Distance measures dissimilarity.

**Merge.** Once documents and their associated retrieval scores are received by the server, the server merges the retrieved
documents into a single ranked list, either by sorting the documents based on the retrieval score; the lower the score the
more relevant the document is to the query, since we are using the `L2` Euclidean distance. Alternatively, you can use
the simple yet effective Reciprocal Rank Fusion (RRF) method [\[5\]](#ref5). To smooth ranking differences during merging, using RRF,
you can change the `k-rrf`value defined in the `[tool.flwr.app.config]` section of the `pyproject.yaml` file. Even though
this is a simple merging technique, you should feel free to extend this and define other merging approaches,
such as using a Re-Ranker model.

> \[!NOTE\]
> If you set `k-rrf=0` then only the retrieval score is considering when merging the retrieved documents,
> while if you set `k-rrf>0` then the retrieved documents are merged using the RRF method.

### Pipeline Configuration

The current example uses the Message API to carry out the communication between the server and the clients. For every
question in the benchmark QA dataset, the server submits the question (query) once to each client and the clients
retrieve the related documents from their respective local document store. Therefore, the server needs only one round
of communication for each question. The properties that are directly related to the execution of the FedRAG application
can be found under the `[tool.flwr.app.config]` section in the `pyproject.yaml` file. These are:

```yaml
server-qa-datasets = ... # the datasets that the server will use to evaluate the FedRAG pipeline
server-qa-num = ... # how many questions should be evaluated per benchmark dataset
clients-corpus-names = ... # the corpus held by each client participating in the federation environment
k-rrf = ... # the value of the reciprocal rank fusion used by the server to merge the retrieved documents
k-nn = ... # the value of the k nearest neighbors (top-k) documents retrieved at each client and server after merge
server-llm-hfpath = ... # the Hugging Face name/path of the LLM model used by the server to execute the RAG query
```

By default, the current example uses the following two corpora `Textbooks, StatPearls` distributed
across 2 clients, with each client holding one corpus (out of the two). For QA evaluation, the server submits
questions from the following two benchmark QA datasets: `PubMedQA, BioASQ`. For the values
of `k-rrf` and `k-nn`, we use `60` and `8` respectively and for the LLM hosted at the server we use HF's
SmolLM model (`HuggingFaceTB/SmolLM2-1.7B-Instruct`) because for Llama models, we need first to accept the terms.

Specifically, the default values are set as:

```yaml
server-qa-datasets = "pubmedqa|bioasq"
server-qa-num = 10
clients-corpus-names = "Textbooks|StatPearls"
k-rrf = 60
k-nn = 8
server-llm-hfpath = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
```

> \[!NOTE\]
> The vertical bar in the value of the `server-qa-datasets` is used to pass the name of multiple benchmark
> datasets. Analogously, the vertical bar in the value of the `clients-corpus-names` is used to assign each corpus
> to each client in a Round-Robin fashion, e.g., `Textbooks -> Client 1, StatPearls -> Client 2,  Textbooks-> Client 3,  StatPearls -> Client 4, Textbooks -> Client 5, etc ...`

Based on the computing resources you will use to run the example, please feel free to modify the Hugging Face model path
`server-llm-hfpath` and use a larger model to execute the RAG query. Moreover, if you like, you can perform or introduce
another merging operation at the server-side over the retrieved documents instead of using the simple RRF approach.

### Enable GPU

Given that the clients do not need to use the GPU to perform the retrieval of the documents from the document store,
it is recommended to enable GPU access only at the server side, since this will allow the server to load the LLM into
the GPU and execute the RAG queries much faster. To do so, you need to set the following property to `true`:

```
server-llm-use-gpu = "true"
```

If you also want to use a GPU at the client-side, you need to set the following property to a positive fractional number,
for instance to `0.1`.

```
options.backend.client-resources.num-gpus = 0.1
```

## References

1. <a id="ref1"></a> Jung, Jincheol, Hongju Jeong, and Eui-Nam Huh. "Federated Learning and RAG Integration: A Scalable Approach for Medical Large Language Models." arXiv preprint arXiv:2412.13720 (2024).

2. <a id="ref2"></a> Addison, Parker, Minh-Tuan H. Nguyen, Tomislav Medan, Jinali Shah, Mohammad T. Manzari, Brendan McElrone, Laksh Lalwani, Aboli More, Smita Sharma, Holger R. Roth, Isaac Yang, Chester Chen, Daguang Xu, Yan Cheng, Andrew Feng, and Ziyue Xu. "C-FedRAG: A Confidential Federated Retrieval-Augmented Generation System." arXiv preprint arXiv:2412.13163 (2024).

3. <a id="ref3"></a> Zhao, Dongfang. "FRAG: Toward Federated Vector Database Management for Collaborative and Secure Retrieval-Augmented Generation." arXiv preprint arXiv:2410.13272 (2024).

4. <a id="ref4"></a> Xiong, Guangzhi, Qiao Jin, Zhiyong Lu, and Aidong Zhang. "Benchmarking retrieval-augmented generation for medicine." In Findings of the Association for Computational Linguistics ACL 2024, pp. 6233-6251. 2024.

5. <a id="ref5"></a> Cormack, Gordon V., Charles LA Clarke, and Stefan Buettcher. "Reciprocal rank fusion outperforms condorcet and individual rank learning methods." In Proceedings of the 32nd international ACM SIGIR conference on Research and development in information retrieval, pp. 758-759. 2009.

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fedrag/README.md

# Federated Retrieval Augmented Generation (FedRAG) via Remote Data Science (RDS) for Privacy-Preserving Question Answering
Valuable knowledge is distributed across organizations worldwide, each protecting their data due to privacy regulations and competitive advantages. Traditional AI systems require centralizing all this data, which is often impossible or illegal. Federated RAG solves this by enabling AI systems to search and learn from documents across multiple organizations without moving or exposing the actual data. Crucially, with remote data science workflow, data owners maintain complete sovereignty—they review every computational job submitted to their systems and explicitly approve or reject requests based on their policies. This consent-based approach enables powerful AI assistants that respect data boundaries while allowing organizations to contribute to shared intelligence without compromising their proprietary information.

![overview](./images/fedrag-rds.gif)


## Set up

### Clone the project
```bash
git clone https://github.com/OpenMined/syft-flwr.git _tmp \
		&& mv _tmp/notebooks/fedrag . \
		&& rm -rf _tmp && cd fedrag
```

### Setup python virtual environment
Assume that you have python and the [uv](https://docs.astral.sh/uv/) package manager installed. Now let's create a virtual python environment with `jupyter` installed:
```bash
uv sync
source .venv/bin/activate
```

## Workflow

### Local Setup
The set of notebooks in `local/` shows how things work with 2 data owners and 1 data scientists, whose datasites all stay in a local SyftBox network on your machine.

Please start with the `do1.ipynb`, then go to the `do2.ipynb`, and finally `ds.ipynb`, and switch hats when necessary when indicated to do so.

### Distributed setup (TODO)
In the distributed setup in `distributed/`, we have the exact same workflow except that each DO's datasite and the DS's datasite run on different machines, and they communicate using the SyftBox client. There are detailed instructions to install the SyftBox client in the notebooks.

#### Distributed setup with Docker
1. Build and run the `syftbox-client` image according to https://github.com/OpenMined/syftbox/blob/main/docker/README.md
2. Attaching VSCode to the container. If you have 3 different emails, you can run 3 clients in 3 different containers

## References
- https://syftbox.net
- https://github.com/OpenMined/syftbox
- https://github.com/OpenMined/syft-flwr
- https://github.com/adap/flower/
- https://flower.ai/docs/examples/fedrag.html
---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fl-diabetes-prediction/fl-diabetes-prediction/README.md

# Federated Learning for Diabetes Prediction

A federated learning application for diabetes prediction using the Pima Indians Diabetes Database. This project leverages [Flower](https://flower.ai/) for federated learning orchestration and [SyftBox](https://github.com/OpenMined/syftbox) for privacy-preserving distributed computation.

## Overview

This application trains a neural network to predict diabetes onset using federated learning, enabling multiple data owners to collaboratively train a model without sharing their raw data. The project supports both local simulation mode and distributed deployment across multiple SyftBox nodes.

## Features

- **Federated Learning**: Decentralized training across multiple clients using Flower framework
- **Privacy-Preserving**: Data remains with data owners; only model updates are shared
- **Imbalanced Data Handling**: Uses SMOTE (Synthetic Minority Over-sampling Technique) for class balancing
- **Advanced Neural Architecture**: Deep neural network with batch normalization and dropout
- **Dual Execution Modes**:
  - Local simulation for development and testing
  - Distributed mode via SyftBox for real-world deployment
- **Model Persistence**: Automatic model checkpointing after each round

## Architecture

### Model

The neural network architecture consists of:
- **Input Layer**: 6 features (after preprocessing)
- **Hidden Layers**:
  - Layer 1: 32 units with BatchNorm, LeakyReLU, and Dropout (0.2)
  - Layer 2: 24 units with BatchNorm, LeakyReLU, and Dropout (0.25)
  - Layer 3: 16 units with BatchNorm and LeakyReLU
- **Output Layer**: Single unit with Sigmoid activation (binary classification)

See `fl_diabetes_prediction/task.py:31` for implementation details.

### Dataset

**Source**: [Pima Indians Diabetes Database](https://huggingface.co/datasets/khoaguin/pima-indians-diabetes-database)

**Features**:
- Pregnancies
- Glucose
- Blood Pressure
- BMI (Body Mass Index)
- Diabetes Pedigree Function
- Age

**Preprocessing**:
- Removed `SkinThickness` and `Insulin` features
- Imputed zero values with mean/median
- Applied SMOTE for class balancing
- Standardized features using StandardScaler

**Partitioning**: IID (Independent and Identically Distributed) partitioning across clients

## Installation

### Requirements

- Python >= 3.12
- UV package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
cd fl-diabetes-prediction
```

2. Install dependencies using UV:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

### Local Simulation

Run federated learning locally with simulated clients:

```bash
flwr run .
```

This will:
- Simulate 2 supernodes (clients) locally
- Run 2 federated learning rounds
- Save model weights to `./weights/` directory

**Configuration**: Edit `pyproject.toml` to adjust:
- `num-server-rounds`: Number of training rounds
- `num-supernodes`: Number of simulated clients

### Distributed Mode (SyftBox)

For distributed deployment across real SyftBox nodes:

1. **Setup SyftBox nodes**:
   - Configure data owner (DO) nodes
   - Configure data scientist (DS) aggregator node

2. **Configure endpoints** in `pyproject.toml`:
```toml
[tool.syft_flwr]
datasites = [
    "do1@openmined.org",
    "do2@openmined.org",
]
aggregator = "ds@openmined.org"
```

3. **Run the application**:
   - On each DO node: `python main.py` (runs as client)
   - On DS node: `python main.py` (runs as server)

The system automatically detects whether to run as client or server based on the email configuration.

### Jupyter Notebooks

Example notebooks are available in:
- `local/`: Local execution examples
  - `do1.ipynb`, `do2.ipynb`: Data owner notebooks
  - `ds.ipynb`: Data scientist aggregator notebook
- `distributed/`: Distributed execution examples

## Project Structure

```
fl-diabetes-prediction/
├── fl_diabetes_prediction/
│   ├── __init__.py
│   ├── task.py           # Model, data loading, training logic
│   ├── client_app.py     # Flower client implementation
│   ├── server_app.py     # Flower server implementation
│   └── main.py           # SyftBox entry point
├── pyproject.toml        # Project configuration
├── weights/              # Saved model checkpoints
└── README.md
```

## Configuration

### Flower App Configuration (`pyproject.toml`)

```toml
[tool.flwr.app.config]
num-server-rounds = 2        # Number of FL rounds
partition-id = 0             # Client partition ID
num-partitions = 1           # Total number of partitions

[tool.flwr.federations.local-simulation.options]
num-supernodes = 2          # Number of simulated clients
```

### Strategy

Uses `FedAvgWithModelSaving` strategy (see `server_app.py:55`):
- **Algorithm**: Federated Averaging (FedAvg)
- **Model Saving**: Automatic checkpointing after each round
- **Metrics Aggregation**: Weighted average by dataset size
- **Fault Tolerance**: Configurable via `pyproject.toml` (default: 50% failure tolerance)
  - Min Available Clients: 1 (can start with 1 out of 2 clients)
  - Min Fit Clients: 1 (needs 1 client minimum per training round)
  - Min Evaluate Clients: 1 (needs 1 client minimum per evaluation)

## Fault Tolerance

The system is designed to handle client failures during federated learning:

### Configuration

**Default Setup (50% failure tolerance)**:
- **Total Clients**: 2
- **Minimum Required**: 1
- **Failure Tolerance**: Can continue with 1 out of 2 clients (50% failure)

### How It Works

1. **min-available-clients**: Minimum clients needed to start a federation (default: 1)
2. **min-fit-clients**: Minimum clients needed per training round (default: 1)
3. **min-evaluate-clients**: Minimum clients needed per evaluation round (default: 1)
4. **fraction-fit**: Fraction of available clients to **sample** per round (default: 0.5)
   - With 2 clients: samples 1 client per round (50% × 2 = 1)
   - Prevents waiting for failed clients that were already sampled
5. **fraction-evaluate**: Fraction of available clients to sample for evaluation (default: 0.5)

### Customizing Fault Tolerance

Edit `pyproject.toml` to adjust fault tolerance:

```toml
[tool.flwr.app.config]
min-available-clients = 1   # Start with at least 1 client
min-fit-clients = 1          # Train with at least 1 client
min-evaluate-clients = 1     # Evaluate with at least 1 client
fraction-fit = 0.5           # Sample 50% of clients per round
fraction-evaluate = 0.5      # Sample 50% of clients for evaluation

[tool.flwr.federations.local-simulation.options]
num-supernodes = 2  # Total number of clients
```

**Examples for 50% failure tolerance**:
- **2 clients, fraction=0.5**: Samples 1 client/round (current default)
- **4 clients, fraction=0.5**: Samples 2 clients/round (more robust)
- **10 clients, fraction=0.5**: Samples 5 clients/round (production scale)

**Important**: Using `fraction-fit < 1.0` ensures the server doesn't get stuck waiting for failed clients that were already sampled in a round.

### Testing Fault Tolerance

To test client failure scenarios locally:

1. Start with `num-supernodes = 2` in `pyproject.toml`
2. Run `flwr run .`
3. The system will continue even if 1 client fails or disconnects

## Training Details

- **Optimizer**: Adam (lr=0.001, weight_decay=0.0005)
- **Loss Function**: Binary Cross-Entropy (BCELoss)
- **Batch Size**: 10 (training), full dataset (testing)
- **Local Epochs**: 1 per round (configurable)
- **Device Support**: CUDA, MPS (Apple Silicon), XPU, or CPU

## Development

### Running Tests

```bash
# Add test commands here
```

### Adding New Features

1. Model modifications: Edit `fl_diabetes_prediction/task.py`
2. Client behavior: Edit `fl_diabetes_prediction/client_app.py`
3. Server strategy: Edit `fl_diabetes_prediction/server_app.py`

## License

Apache-2.0

## Publisher

OpenMined

## Dependencies

Key dependencies:
- `flwr-datasets>=0.5.0` - Federated dataset utilities
- `torch>=2.8.0` - Deep learning framework
- `scikit-learn==1.6.1` - Machine learning utilities
- `imblearn` - Imbalanced data handling (SMOTE)
- `syft_flwr==0.4.0` - SyftBox integration
- `loguru` - Logging
- `pandas` - Data manipulation

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**: The code automatically falls back to CPU if GPU is unavailable
2. **SMOTE k_neighbors Error**: Handled automatically by adjusting k_neighbors based on minority class count
3. **Model Loading**: Ensure `weights/` directory exists for model checkpointing

### Logs

The application uses `loguru` for logging. Check console output for detailed execution information.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- Tests pass (when available)
- Documentation is updated

## Resources

- [Flower Documentation](https://flower.ai/docs/)
- [SyftBox Repository](https://github.com/OpenMined/syftbox)
- [Pima Indians Diabetes Database](https://huggingface.co/datasets/khoaguin/pima-indians-diabetes-database)
- [OpenMined](https://www.openmined.org/)

## Contact

For questions or issues, please open an issue in the repository.

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fl-diabetes-prediction/README.md

# Diabetes Prediction with `syft_flwr`

## Introduction

In this tutorial, we'll walk through a practical federated learning implementation for diabetes prediction using [syft_flwr](https://github.com/OpenMined/syft-flwr) — a framework that combines the flexibility of [Flower](https://github.com/adap/flower/) (a popular federated learning framework) with the privacy-preserving networking capabilities of [syftbox](https://www.syftbox.net/).

![FL Training Process](./images/fltraining.gif)

## Set up

### Clone the project
```bash
git clone https://github.com/OpenMined/syft-flwr.git _tmp \
		&& mv _tmp/notebooks/fl-diabetes-prediction . \
		&& rm -rf _tmp && cd fl-diabetes-prediction
```

### Setup python virtual environment
Assume that you have python and the [uv](https://docs.astral.sh/uv/) package manager installed. Now let's create a virtual python environment with all dependencies installed:
```bash
uv sync
```

### Local Setup
The set of notebooks in `local/` shows how things work with 2 data owners and 1 data scientists, whose datasites all stay in a local SyftBox network on your machine.

Please start with the `do1.ipynb`, then go to the `do2.ipynb`, and finally `ds.ipynb`, and switch hats when necessary when indicated to do so.

### Distributed setup
In the distributed setup in `distributed/`, we have the exact same workflow except that each DO's datasite and the DS's datasite run on different machines,and they communicate using the SyftBox client. There are detailed instructions to install the SyftBox client in the notebooks.

## References
- https://syftbox.net
- https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database/
- https://github.com/OpenMined/syftbox
- https://github.com/OpenMined/syft-flwr
- https://github.com/adap/flower/
- https://github.com/OpenMined/rds
- https://github.com/elarsiad/diabetes-prediction-keras

---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/README.md

# syft_flwr

`syft_flwr` is an open source framework that facilitate federated learning (FL) projects using [Flower](https://github.com/adap/flower) over the [SyftBox](https://github.com/OpenMined/syftbox) protocol

![FL Training Process](https://github.com/OpenMined/syft-flwr/raw/main/notebooks/fl-diabetes-prediction/images/fltraining.gif)

## Example Usages
Please look at the `notebooks/` folder for example use cases:
-  [FL diabetes prediction](notebooks/fl-diabetes-prediction/README.md) shows how to train a federated model over distributed machines for multiple rounds
-  [Federated analytics](notebooks/federated-analytics-diabetes/README.md) shows how to query statistics from private datasets from distributed machines and then aggregate them
-  [FedRAG (Federated RAG)](notebooks/fedrag/README.md) demonstrates privacy-preserving question answering using Retrieval Augmented Generation across distributed document sources with remote data science workflow

## Development
### Releasing
See [RELEASE.md](RELEASE.md) for the complete release process.
---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/RELEASE.md

# Release Process

This document describes how to release new versions of syft-flwr.

## Overview

The release process is fully automated using GitHub Actions. It handles version bumping, dependency updates, testing, building, and publishing to PyPI in a single workflow.

## Quick Release

1. **Go to Actions tab** → **Release** workflow
2. **Click "Run workflow"**
3. **Select options:**
   - **bump_type**: `patch`, `minor`, or `major`
   - **skip_publish**: `false` (uncheck for production release)
4. **Click "Run workflow"**

The workflow will automatically:
- Bump the version and create a git tag
- Update all lock files and dependencies
- Run tests to ensure everything works
- Build and validate the package
- Push changes to main
- Publish to PyPI
- Create a GitHub release
- Update notebook lock files with the published version

## Testing a Release

To test the release process without making any permanent changes:

1. Set **skip_publish** to `true` (check the box)
2. The workflow will:
   - ✅ Test version bumping and dependency updates
   - ✅ Build and validate the package
   - ❌ Skip git commits/pushes (no permanent changes)
   - ❌ Skip PyPI upload
   - ❌ Skip GitHub release creation
   - ❌ Skip notebook lock file updates
3. Review the workflow logs to ensure everything works correctly
4. **No cleanup needed** - no permanent changes are made

## What the Workflow Does

### Step-by-step process:

1. **Setup Environment**
   - Checkout main branch
   - Install Python, uv, just, and dependencies

2. **Version Bump**
   - Uses `just bump <type>` which internally:
     - Runs `cz bump` to update version and create commit/tag
     - Updates main project's `uv.lock`
     - Updates notebook `pyproject.toml` files (but not their locks yet)
     - Amends everything into a single atomic commit

3. **Testing & Building**
   - Runs full test suite (`just test`)
   - Builds package (`just build`)
   - Tests the built package can be imported and has correct version

4. **Publishing**
   - Pushes commit and tags to main
   - Uploads to PyPI (unless `skip_publish=true`)
   - Creates GitHub release with auto-generated changelog

5. **Post-publish Updates**
   - Waits 30 seconds for PyPI to index
   - Updates notebook lock files with the published version
   - Commits and pushes the lock file updates

## Manual Release Steps (if needed)

If you need to release manually:

```bash
# 1. Bump version
just bump patch  # or minor/major

# 2. Run tests
just test

# 3. Build package
just build

# 4. Push to GitHub
git push origin main --tags

# 5. Upload to PyPI
uvx twine upload dist/* --username __token__ --password <token>

# 6. Update notebook locks (after PyPI publication)
just update-notebook-locks
git add notebooks/*/uv.lock
git commit -m "chore: update notebook locks"
git push origin main
```

## Troubleshooting

### Common Issues:

**Notebook lock updates fail:**
- The new version might not be available on PyPI yet
- Wait a few minutes and run `just update-notebook-locks` manually

**Tests fail:**
- Fix the failing tests before attempting release
- The workflow will abort if tests fail

**PyPI upload fails:**
- Ensure `OM_PYPI_TOKEN` secret is set in repository settings
- Check if the version already exists on PyPI

**Version conflicts:**
- If the version already exists, you'll need to bump to a higher version
- Never reuse version numbers

## Version Strategy

- **Patch** (0.3.1 → 0.3.2): Bug fixes, small improvements
- **Minor** (0.3.1 → 0.4.0): New features, backward compatible
- **Major** (0.3.1 → 1.0.0): Breaking changes

## Development Workflow

1. **Feature development** happens in feature branches
2. **Merge to main** when ready
3. **Run release workflow** to publish new version
4. **Notebook updates** are handled automatically

This ensures main branch is always releasable and dependencies stay in sync.
---


## File: docs/meaisínfhoghlaim/federated/syft-flwr/tests/assets/code/fed-analytics-diabetes/README.md

# Federated Analytics on Diabetes Dataset


## References
- https://syftbox.net
- [Federated Analytics with Flower and Pandas](https://flower.ai/blog/2023-01-24-federated-analytics-pandas/)
- https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database/
- https://github.com/OpenMined/syftbox
- https://github.com/OpenMined/syft-flwr
- https://github.com/adap/flower/
- https://github.com/OpenMined/rds
- https://github.com/elarsiad/diabetes-prediction-keras
---


## File: docs/meaisínfhoghlaim/sam-audio/CODE_OF_CONDUCT.md

# Code of Conduct

## Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to make participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, sex characteristics, gender identity and expression,
level of experience, education, socio-economic status, nationality, personal
appearance, race, religion, or sexual identity and orientation.

## Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or
advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic
address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a
professional setting

## Our Responsibilities

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

## Scope

This Code of Conduct applies within all project spaces, and it also applies when
an individual is representing the project or its community in public spaces.
Examples of representing a project or community include using an official
project e-mail address, posting via an official social media account, or acting
as an appointed representative at an online or offline event. Representation of
a project may be further defined and clarified by project maintainers.

This Code of Conduct also applies outside the project spaces when there is a
reasonable belief that an individual's behavior may have a negative impact on
the project or its community.

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team at <opensource-conduct@meta.com>. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project team is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

## Attribution

This Code of Conduct is adapted from the [Contributor Covenant][homepage], version 1.4,
available at https://www.contributor-covenant.org/version/1/4/code-of-conduct.html

[homepage]: https://www.contributor-covenant.org

For answers to common questions about this code of conduct, see
https://www.contributor-covenant.org/faq

---


## File: docs/meaisínfhoghlaim/sam-audio/CONTRIBUTING.md

# Contributing to segment-anything-model-audio
We want to make contributing to this project as easy and transparent as
possible.

## Pull Requests
We actively welcome your pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. If you haven't already, complete the Contributor License Agreement ("CLA").

## Contributor License Agreement ("CLA")
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Facebook's open source projects.

Complete your CLA here: <https://code.facebook.com/cla>

## Issues
We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

Facebook has a [bounty program](https://www.facebook.com/whitehat/) for the safe
disclosure of security bugs. In those cases, please go through the process
outlined on that page and do not file a public issue.

## License
By contributing to segment-anything-model-audio, you agree that your contributions will be licensed
under the LICENSE file in the root directory of this source tree.
---


## File: docs/meaisínfhoghlaim/sam-audio/eval/README.md

# Evaluation

This directory contains the evaluation code to reproduce the results from the SAM-Audio paper. The evaluation framework supports multiple datasets, prompting modes (text-only, span, visual), and metrics.

## Setup

Before running evaluation, ensure you have:

1. Installed the SAM-Audio package and its dependencies
2. Authenticated with Hugging Face to access the model checkpoints (see main [README](../README.md))

## Quick Start

Run evaluation on the default setting (instr-pro):

```bash
python main.py
```

You can also use multiple GPUs to speed up evaluation:

```bash
torchrun --nproc_per_node=<ngpus> python main.py
```

Evaluate on a specific setting:

```bash
python main.py --setting sfx
```

Evaluate on multiple settings:

```bash
python main.py --setting sfx speech music
```

## Available Evaluation Settings

Run `python main.py --help` to see all available settings

## Command Line Options

```bash
python main.py [OPTIONS]
```

### Options:

- `-s, --setting` - Which setting(s) to evaluate (default: `instr-pro`)
  - Choices: See available settings above
  - Can specify multiple settings: `--setting sfx speech music`

- `--cache-path` - Where to cache downloaded datasets (default: `~/.cache/sam_audio`)

- `-p, --checkpoint-path` - Model checkpoint to evaluate (default: `facebook/sam-audio-1b`)
  - Can use local path or Hugging Face model ID

- `-b, --batch-size` - Batch size for evaluation (default: `1`)

- `-w, --num-workers` - Number of data loading workers (default: `4`)

- `-c, --candidates` - Number of reranking candidates (default: `8`)

## Evaluation Metrics

The evaluation framework computes the following metrics:

- **Judge** - SAM Audio Judge quality assessment metric
- **Aesthetic** - Aesthetic quality metric
- **CLAP** - Audio-text alignment metric (CLAP similarity)
- **ImageBind** - Audio-video alignment metric (for visual settings only)

## Output

Results are saved to the `results/` directory as JSON files, one per setting:

```
results/
├── sfx.json
├── speech.json
└── music.json
```

Each JSON file contains the averaged metric scores across all samples in that setting.

Example output:
```json
{
    "JudgeOverall": "4.386",
    "JudgeFaithfulness": "4.708",
    "JudgeRecall": "4.934",
    "JudgePrecision": "4.451",
    "ContentEnjoyment": "5.296",
    "ContentUsefulness": "6.903",
    "ProductionComplexity": "4.301",
    "ProductionQuality": "7.100",
    "CLAPSimilarity": "0.271"
}
```

---


## File: docs/meaisínfhoghlaim/sam-audio/KCG_SUMMARY.md

# SAM-Audio — KCG Summary

## What It Is
SAM-Audio (Meta FAIR) is a foundation model for isolating any sound in audio using text, visual, or temporal prompts. It separates specific sounds from complex audio mixtures based on natural language descriptions, visual cues from video, or time spans. Built on the Perception-Encoder Audio-Visual (PE-AV) backbone, it represents the audio-domain extension of Meta's Segment Anything paradigm.

## Why This Matters for Kings' College Galway
Irish-language speech data is one of the scarcest resources in Celtic NLP. SAM-Audio's text-prompted sound separation could isolate Irish speech from noisy classroom recordings, improving ASR training data quality for Whisper-Irish fine-tuning. The visual prompting capability could segment Irish-language content from educational videos (TG4, RTÉ archive), extracting clean audio for the Common Voice Irish dataset. Temporal prompting enables isolating specific Irish phrases from long-form recordings — critical for building pronunciation datasets for Leaving Certificate Irish oral exam preparation.

## Key Patterns Preserved
- `README.md` — Main documentation: setup, text prompting, visual prompting, temporal prompting, evaluation
- `CONTRIBUTING.md` — Contribution guidelines for Meta open-source projects
- `CODE_OF_CONDUCT.md` — Meta's code of conduct
- `eval/README.md` — Evaluation methodology and benchmarks

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/facebookresearch/sam-audio
- Hugging Face: https://huggingface.co/facebook/sam-audio-large

## What Was Removed
Python source code (.py, .pxd, .pyx, Cython), CUDA kernels, C++ source, model checkpoint files, audio sample files (.wav, .mp3), Dockerfiles, CI/CD configs, package dependencies (setup.py, pyproject.toml), compiled extensions (.so), evaluation data, Git metadata.

---


## File: docs/meaisínfhoghlaim/sam-audio/README.md

<div align="center">

# SAM-Audio

![CI](https://github.com/facebookresearch/sam-audio/actions/workflows/ci.yaml/badge.svg)

![model_image](assets/sam_audio_main_model.png)

</div>

Segment Anything Model for Audio [[**Blog**](https://ai.meta.com/blog/sam-audio/)] [[**Paper**](https://ai.meta.com/research/publications/sam-audio-segment-anything-in-audio/)] [[**Demo**](https://aidemos.meta.com/segment-anything/editor/segment-audio)]

SAM-Audio is a foundation model for isolating any sound in audio using text, visual, or temporal prompts. It can separate specific sounds from complex audio mixtures based on natural language descriptions, visual cues from video, or time spans.

SAM-Audio and the Judge model crucially rely on [Perception-Encoder Audio-Visual (PE-AV)](https://huggingface.co/facebook/pe-av-large), which you can read more about [here](https://ai.meta.com/research/publications/pushing-the-frontier-of-audiovisual-perception-with-large-scale-multimodal-correspondence-learning/)

## Setup

**Requirements:**
- Python >= 3.10
- CUDA-compatible GPU (recommended)

Install dependencies:

```bash
pip install .
```

## Usage

⚠️ Before using SAM Audio, please request access to the checkpoints on the SAM Audio
Hugging Face [repo](https://huggingface.co/facebook/sam-audio-large). Once accepted, you
need to be authenticated to download the checkpoints. You can do this by running
the following [steps](https://huggingface.co/docs/huggingface_hub/en/quick-start#authentication)
(e.g. `hf auth login` after generating an access token.)

### Basic Text Prompting

```python
from sam_audio import SAMAudio, SAMAudioProcessor
import torchaudio
import torch

model = SAMAudio.from_pretrained("facebook/sam-audio-large")
processor = SAMAudioProcessor.from_pretrained("facebook/sam-audio-large")
model = model.eval().cuda()

file = "<audio file>" # audio file path or torch tensor
description = "<description>"

batch = processor(
    audios=[file],
    descriptions=[description],
).to("cuda")

with torch.inference_mode():
    # NOTE: `predict_spans` and `reranking_candidates` have a large impact on performance.
    # Setting `predict_span=True` and `reranking_candidates=8` will give you better results at the cost of
    # latency and memory. See the "Span Prediction" section below for more details
   result = model.separate(batch, predict_spans=False, reranking_candidates=1)

# Save separated audio
sample_rate = processor.audio_sampling_rate
torchaudio.save("target.wav", result.target.cpu(), sample_rate)      # The isolated sound
torchaudio.save("residual.wav", result.residual.cpu(), sample_rate)  # Everything else
```

### Prompting Methods

SAM-Audio supports three types of prompts:

1. **Text Prompting**: Describe the sound you want to isolate using natural language
   ```python
   processor(audios=[audio], descriptions=["A man speaking"])
   ```

2. **Visual Prompting**: Use video frames and masks to isolate sounds associated with visual objects
   ```python
   processor(audios=[video], descriptions=[""], masked_videos=processor.mask_videos([frames], [mask]))
   ```

3. **Span Prompting**: Specify time ranges where the target sound occurs
   ```python
   processor(audios=[audio], descriptions=["A horn honking"], anchors=[[["+", 6.3, 7.0]]])
   ```

See the [examples](examples) directory for more detailed examples

### Span Prediction (Optional for Text Prompting)

We also provide support for automatically predicting the spans based on the text description, which is especially helpful for separating non-ambience sound events.  You can enable this by adding `predict_spans=True` in your call to `separate`

```python
with torch.inference_mode()
   outputs = model.separate(batch, predict_spans=True)

# To further improve performance (at the expense of latency), you can add candidate re-ranking
with torch.inference_mode():
   outputs = model.separate(batch, predict_spans=True, reranking_candidates=8)
```

### Re-Ranking

We provide the following models to assess the quality of the separated audio:

- [CLAP](https://github.com/LAION-AI/CLAP): measures the similarity between the target audio and text description
- [Judge](https://huggingface.co/facebook/sam-audio-judge): measures the overall separation quality across 3 axes: precision, recall, and faithfulness (see the [model card](https://huggingface.co/facebook/sam-audio-judge#output-format) for more details)
- [ImageBind](https://github.com/facebookresearch/ImageBind): for visual prompting, we measure the imagebind embedding similarity between the separated audio and the masked input video

We provide support for generating multiple candidates (by setting `reranking_candidates=<k>` in your call to `separate`), which will generate `k` audios, and choose the best one based on the ranking models mentioned above

# Models

Below is a table of each of the models we released along with their overall subjective evaluation scores

| Model    | General SFX | Speech | Speaker | Music | Instr(wild) | Instr(pro) |
|----------|-------------|--------|---------|-------|-------------|------------|
| [`sam-audio-small`](https://huggingface.co/facebook/sam-audio-small) | 3.62        | 3.99   | 3.12    | 4.11  | 3.56        | 4.24       |
| [`sam-audio-base`](https://huggingface.co/facebook/sam-audio-base)   | 3.28        | 4.25   | 3.57    | 3.87  | 3.66        | 4.27       |
| [`sam-audio-large`](https://huggingface.co/facebook/sam-audio-large) | 3.50        | 4.03   | 3.60    | 4.22  | 3.66        | 4.49       |

We additional release another variant (in each size) that is better specifically on correctness of target sound as well as visual prompting:
- [`sam-audio-small-tv`](https://huggingface.co/facebook/sam-audio-small-tv)
- [`sam-audio-base-tv`](https://huggingface.co/facebook/sam-audio-base-tv)
- [`sam-audio-large-tv`](https://huggingface.co/facebook/sam-audio-large-tv)

## Evaluation

See the [eval](eval) directory for instructions and scripts to reproduce results from the paper

## Contributing

See [contributing](CONTRIBUTING.md) and [code of conduct](CODE_OF_CONDUCT.md) for more information.

## License

This project is licensed under the SAM License - see the [LICENSE](LICENSE) file for details.

---


## File: docs/meaisínfhoghlaim/sam3d_objects/KCG_SUMMARY.md

# SAM 3D Objects — KCG Summary

## What It Is
3D object data related to Meta's Segment Anything Model (SAM) ecosystem — likely SAM 3D or 3D object segmentation assets. Contains no markdown documentation; composed entirely of 3D data files (.obj, .glb, .ply, etc.).

## Why This Matters for Kings' College Galway
3D object segmentation connects to Celtic cultural heritage digitisation — creating 3D models of archaeological artefacts (Ogham stones, high crosses, metalwork) that can be interactively explored in the Túatha educational MMO. SAM-based segmentation could automate the extraction of individual objects from photogrammetry scans of Irish heritage sites. The 3D data processing patterns inform handling of spatial educational content in the Babylon.js-based Túatha platform.

## Key Patterns Preserved
- *(No markdown files existed in this repository)*

## Source Files
Full source removed (2026-06-06). No canonical GitHub URL identified — files likely from Meta's SAM ecosystem or related 3D research.

## What Was Removed
3D model files (.obj, .glb, .ply, .stl), texture images, material definitions, animation data, metadata files, Git metadata. No markdown documentation existed.

---


## File: docs/meaisínfhoghlaim/sam3d-api/README.md

# SAM 2 Segmentation + Sam-3d-objects 3D Generation API 🔧✨

A small FastAPI service that:

- Runs Meta's Segment Anything Model 2 (SAM 2) to produce segmentation masks from point clicks
- Invokes the `sam-3d-objects` pipeline to generate a 3D Gaussian splat and export a PLY/GIF

This repo contains a single HTTP API (`api.py`) and a subprocess wrapper (`generate_3d_subprocess.py`) which runs the heavier Sam-3d-objects inference in a separate process to avoid GPU/spconv state issues.

![preview](https://github.com/user-attachments/assets/6f0d652f-7c91-4c77-8e1d-70359b187d49)

> 🚧 **Note**
>
> This project is meant to work in conjunction with the mobile app - [Sam3D Mobile](https://github.com/andrisgauracs/sam3d-mobile)

---

## Features ✅

- POST `/segment` — single-point segmentation (returns one or multiple masks)
- POST `/segment-binary` — multi-point segmentation that returns a masked image (PNG, base64)
- POST `/generate-3d` — async 3D generation from image+mask (returns a task_id to poll)
- GET `/generate-3d-status/{task_id}` — poll for PLY/GIF results or error
- GET `/assets-list` — list saved PLY/GIF assets
- Health check: GET `/health`

---

## Requirements & Ops ⚙️

- Python 3.10+ recommended
- GPU recommended for speed (CUDA supported); MPS fallback is used on macOS where available
- Optional: `open3d` for mesh simplification (not required)

Dependencies are in `requirements.txt` and the repo includes `setup.sh` to bootstrap `sam-3d-objects` and a Conda environment.

Key packages include: `fastapi`, `uvicorn`, `torch`, `transformers`, `opencv-python`, `trimesh`, etc.

---

## Quick Setup (summary) 🛠️

1. Install the Hugging Face CLI and authenticate:

```bash
pip install 'huggingface-hub[cli]<1.0'
hf auth login
```

2. Run the repo setup (clones `sam-3d-objects`, creates conda env, installs deps, and downloads checkpoints):

```bash
source setup.sh
```

3. Ensure the `sam-3d-objects` repository and checkpoints are present under the repository root (the setup script places them at `./sam-3d-objects`).

> Note: The subprocess currently uses fixed paths and expects:
>
> - `./sam-3d-objects/notebook`
> - `./sam-3d-objects/checkpoints/hf/pipeline.yaml`
>   Do not rely on changing these paths via environment variables unless you update the code.

---

## Environment variables and notes ❗

Note: The subprocess expects the following fixed paths (relative to the repo root):

- `./sam-3d-objects/notebook` — the `sam-3d-objects` notebook folder required by the subprocess (fixed path).
- `./sam-3d-objects/checkpoints/hf/pipeline.yaml` — the `sam-3d-objects` pipeline config (fixed path used by the subprocess).

Important runtime environment requirements (these are already set in `api.py` and `generate_3d_subprocess.py` but are useful to know):

- Several env vars are set before importing `torch` / `spconv` to avoid tuning issues (e.g., `SPCONV_TUNE_DEVICE`, `SPCONV_ALGO_TIME_LIMIT`).
- For macOS, `PYTORCH_ENABLE_MPS_FALLBACK=1` is set as a fallback.

> ⚠️ The 3D generation is executed in a subprocess (`generate_3d_subprocess.py`) to avoid state conflicts with spconv / Sam-3d-objects. The subprocess expects the Sam-3d-objects repo and the checkpoints to be available.

---

## Running the API (development) ▶️

You can run the app directly with Python, or use **Uvicorn** (recommended) for a cleaner server and easy configuration.

### Launch with Uvicorn (development)

Auto-reload (recommended for development):

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

Simple run (no reload):

```bash
python api.py
# or
uvicorn api:app --host 0.0.0.0 --port 8000 --log-level info
```

### Launch with Uvicorn/Gunicorn (production)

Run with multiple worker processes (recommended in production when you want process-level parallelism):

Using Gunicorn + Uvicorn worker class:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 api:app --log-level info
```

Or using Uvicorn's `--workers` flag directly:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

Notes & tips:

- Use `--reload` only in development (it restarts the process on file changes).
- Tune `--workers` (or Gunicorn `-w`) based on CPU and memory. If your workload is GPU-bound, avoid starting multiple processes that compete for the same GPU unless appropriately isolated.
- Ensure `CUDA_VISIBLE_DEVICES` (or equivalent GPU pinning) is set for your production service manager (systemd, container, or supervisor). Also ensure the required `sam-3d-objects` folders and checkpoint file exist at `./sam-3d-objects/notebook` and `./sam-3d-objects/checkpoints/hf/pipeline.yaml`.
- For long-running/production deployments, consider a process manager (systemd, docker-compose, k8s) and a reverse proxy (NGINX) for TLS, buffering, and routing.

Visit the interactive docs: http://localhost:8000/docs

---

## Endpoints & Examples 📡

All requests that take images or masks expect base64-encoded PNG/JPEG payloads.

### Health

- GET `/health`

Example:

```bash
curl http://localhost:8000/health
```

---

### Segment (single point)

- POST `/segment`

Body (JSON):

```json
{
  "image": "<base64 PNG/JPEG>",
  "x": 200,
  "y": 150,
  "multimask_output": true,
  "mask_threshold": 0.0
}
```

Response: JSON with `masks` (base64 PNGs), `scores`, and `image_shape`.

cURL example (using jq for compact output):

```bash
curl -s -X POST http://localhost:8000/segment \
  -H 'Content-Type: application/json' \
  -d '{"image":"<BASE64>","x":200,"y":150}' | jq .
```

---

### Segment Binary (multi-point, returns masked PNG)

- POST `/segment-binary`

Body:

```json
{
  "image": "<base64 image>",
  "points": [
    { "x": 200, "y": 150 },
    { "x": 220, "y": 170 }
  ],
  "previous_mask": "<optional base64 mask PNG>",
  "mask_threshold": 0.0
}
```

Response: JSON containing `mask` (base64 PNG) and `score`.

---

### Generate 3D (async)

- POST `/generate-3d`

Body:

```json
{
  "image": "<base64 image>",
  "mask": "<base64 binary mask PNG>",
  "seed": 42
}
```

Response: `{ "task_id": "<uuid>", "status": "queued" }` — poll `/generate-3d-status/{task_id}` for updates.

Poll example:

```bash
curl http://localhost:8000/generate-3d-status/<task_id> | jq .
```

When completed, the status contains `output_b64` (PLY or GIF), `output_type` (`"ply"`/`"gif"`), `ply_url` (public `/assets/...` path), and `mesh_url` if a mesh or GLB was generated.

### GLB export & mesh outputs

The subprocess attempts to export a textured GLB (native or via `to_glb`) as the primary mesh output when available. Notes:

- If GLB export succeeds, the `/generate-3d-status/{task_id}` response will include `mesh_url` (e.g. `/assets/mesh_<id>.glb`) and the API will also return `mesh_b64` and `mesh_size_bytes` when you poll the task status.
- The GLB/mesh is saved in the `assets/` folder and is accessible at the `mesh_url` path exposed by the API.

Example: download and save the mesh (server returns `mesh_b64`):

```bash
curl -s http://localhost:8000/generate-3d-status/<task_id> | jq -r '.mesh_b64' | base64 --decode > result.glb
```

Troubleshooting & tips for GLB/mesh export:

- The subprocess prints detailed debug lines; check the subprocess stdout logs for markers such as `MESH_URL_START` / `MESH_URL_END`, `PLY_URL_START` / `PLY_URL_END`, or warnings about `to_glb()`.
- If the pipeline returns unexpected structures (for example, `mesh` as a `list`), the subprocess will try to select a mesh-like element. If none is suitable, `to_glb()` will be skipped and a warning will be printed — the PLY or GIF output may still be available.
- If `to_glb()` raises an AttributeError (for example, because an object in the list is not a mesh with `.vertices`), the subprocess now catches the error and continues; inspect the logs and the pipeline output to find and fix the root cause.
- Native GLB export may require additional sam-3d-objects dependencies (texture baking, etc.) and can be GPU/CPU intensive.

---

---

### Assets

- GET `/assets-list` — lists files saved to the `assets/` folder with metadata.

---

## Example Python client snippet 🧪

```python
import base64, requests

# Read image and encode
with open('input.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')

resp = requests.post('http://localhost:8000/segment', json={
    'image': img_b64,
    'x': 200, 'y': 150
})
print(resp.json())
```

---

## Troubleshooting & Tips 💡

- If models fail to load, ensure you authenticated with the Hugging Face CLI and downloaded checkpoints via `setup.sh`.
- The 3D generation may require a GPU and substantial memory — the subprocess prints memory and timing info to stdout for debugging.
- Install `open3d` if you want full mesh simplification (note: CPU intensive).
- If you run into `spconv` tuning/float64 issues, ensure the env vars are set before importing `torch` (the code already sets them early).

> ⚠️ Large PLY files may be written in ASCII/UTF-8 format by the post-processing step; validate that clients can handle large base64 payloads when polling for results.

---

## Development Notes & Contribution 🔭

- The heavy Sam-3d-objects logic is executed in `generate_3d_subprocess.py`; the API enqueues a background task which spawns that subprocess.
- Keep subprocess isolation when experimenting with `spconv` and GPU settings.

Contributions welcome — open issues or PRs with improvements, examples, and CI tests.

---

## License

MIT

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/awf.md

## AWF Land Use and Land Cover Mapping

OlmoEarth-v1-FT-AWF-Base is a model fine-tuned from OlmoEarth-v1-Base for predicting land use and land cover type in southern Kenya using Sentinel-2 satellite images.

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-AWF-Base/blob/main/model.ckpt
- Annotation GeoJSONs: https://huggingface.co/datasets/allenai/olmoearth_projects_awf/tree/main
- rslearn dataset: https://huggingface.co/datasets/allenai/olmoearth_projects_awf/blob/main/dataset.tar

## Model Details

The model inputs twelve timesteps of satellite image data, one [Sentinel-2 L2A](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a) mosaic per 30-day period.

The model is trained to predict land use and land cover type for every pixel within each 16x16 input patches.

The model (window size: 16x16, patch size: 4) achieves 89.5% overall accuracy on the validation set. The table below summarizes our experiments with different window sizes, patch sizes, and input modalities. Overall, models using Sentinel-2 only perform better.

| Window Size | Patch Size | Modalities | Accuracy (%) |
|--------------|-------------|-------------|---------------|
| 16×16 | 1 | Sentinel-2 | 90.4 |
| 16×16 | 1 | Sentinel-2 + Sentinel-1 | 83.1 |
| 16×16 | 4 | Sentinel-2 | 89.5 |
| 16×16 | 4 | Sentinel-2 + Sentinel-1 | 83.1 |
| 32×32 | 4 | Sentinel-2 | 88.5 |
| 32×32 | 4 | Sentinel-2 + Sentinel-1 | 83.1 |

## Training Data

The model is trained on point labels generated by [African Wildlife Foundation](https://www.awf.org/). There're in total 1469 labeled points across 9 categories: agriculture/settlement, grassland/barren, shrubland/savanna, herbaceous wetland, lava forest, montane forest, woodland forest (>40% canopy), urban/dense development, and open water. The AWF team used Planet imagery as the main reference to annotate these points.

Each sample include its longitude, latitude, time range (2023-01 to 2023-12), and land use /land cover type. For each sample, we generate an rslearn window centered on the location, covering one year of data. We use rslearn to obtain twelve Sentinel-2 and Sentinel-1 imagery during that time range, with one per 30-day period.

The dataset is split spatially into training (75%) and validation (25%) sets, based on a 128×128-pixel grid hashed into the two splits.

## Inference

Inference is documented in [the main README](../README.md). The prediction request geometry should have start and end timestamps that covers one year, ideally from 2023-01-01 to 2023-12-31 to match the training data. Inference runs on all 1024×1024 grid cells intersecting the geometry, using satellite images from the specified time range.

Here's the [inference output](https://olmoearth.allenai.org/viewer/d591a8ce-c97d-4a23-a520-a1aa1363ce22#8.76/-2.9277/37.3573) for the Amboseli national park region.

## Fine-tuning

Fine-tuning is documented in [the main README](../README.md).

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/ecosystem_type_mapping.md

## Ecosystem Type Mapping

OlmoEarth-v1-FT-EcosystemTypeMapping-Base is a model fine-tuned from OlmoEarth-v1-Base
on expert-annotated ecosystem type data provided by [Global Ecosystem Atlas](https://globalecosystemsatlas.org/).
It is trained specifically for the north Africa region. The categories correspond to those in
the [IUCN Gloabl Ecosystem Typology](https://global-ecosystems.org/page/typology).

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-EcosystemTypeMapping-Base/blob/main/model.ckpt

## Model Details

The model inputs six timesteps of Sentinel-2 L2A satellite images, with one mosaic per
30-day period over a 270-day time range (some timesteps may be skipped if not enough
Sentinel-2 images are available).

It processes each 32x32 crop of the input image separately, and predicts the
predominant ecosystem type in each crop.

It achieves 64.8% accuracy on our test set.

## Training Data

The model is trained on ecosystem type data from [Global Ecosystem Atlas](https://globalecosystemsatlas.org/).
They will release the dataset in 2026.

## Inference

Inference is documented in [the main README](../README.md). The 180-day time range
starting at the start timestamp in the prediction request geometry will be used to
obtain the Sentinel-2 30-day mosaics; images from the preceding 90 days may be used if
there are some 30-day periods during the 180-day time range with no Sentinel-2
coverage. The end timestamp won't be used and can be set arbitrarily, e.g. set 180 days
after the start timestamp.

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/forest_loss_driver.md

## Forest Loss Driver Classification

OlmoEarth-v1-FT-ForestLossDriver-Base is a model fine-tuned from OlmoEarth-v1-Base for
classifying forest loss drivers. It is trained to operate over
[GLAD-S2 forest loss alerts](https://data.globalforestwatch.org/datasets/gfw::integrated-deforestation-alerts/about),
which are updated weekly and report the locations of forest loss. Thus, instead of
detecting forest loss from scratch, we take connected components of GLAD-S2 forest loss
pixels and extend them with a driver classification that predicts the cause of the
forest loss.

The driver categories are:

- Agriculture
- Mining
- Airstrip
- Road
- Logging
- Burned
- Landslide
- Hurricane
- River
- None

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base/resolve/main/model.ckpt
- rslearn dataset: https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/forest_loss_driver/20251029/dataset.tar

## Model Details

For each connected component of GLAD-S2 forest loss pixels, the model inputs two image
time series that are 64x64 pixels (at 10 m/pixel) centered at the center of the
connected component. The first time series consists of four Sentinel-2 L2A images
captured before the forest loss, while the second time series consists of four
Sentinel-2 L2A images captured after the forest loss.

The model classifies the forest loss driver, with 10 classes (see above). It achieves
an accuracy of 76.1% on our validation set. Here is the confusion matrix:

| Category  | Ag | Airstrip | Burned | Hurricane | Landslide | Logging | Mining | None | River | Road |
| --------  | -- | -------- | ------ | --------- | --------- | ------- | ------ | ---- | ----- | ---- |
| Ag        | 37 |      0   |      2 |         0 |         0 |       0 |      0 |    2 |     0 |    3 |
| Airstrip  |  0 |      0   |      0 |         0 |         0 |       0 |      0 |    0 |     0 |    0 |
| Burned    |  2 |      0   |     21 |         3 |         0 |       0 |      0 |    4 |     0 |    0 |
| Hurricane |  0 |      0   |      0 |         6 |         0 |       0 |      0 |    0 |     0 |    0 |
| Landslide |  0 |      0   |      0 |         0 |         1 |       0 |      0 |    0 |     0 |    0 |
| Logging   |  0 |      0   |      0 |         2 |         0 |       2 |      0 |    0 |     0 |    0 |
| Minning   |  0 |      0   |      0 |         0 |         0 |       0 |      1 |    0 |     0 |    0 |
| None      |  2 |      0   |      1 |         1 |         0 |       2 |      0 |   11 |     0 |    1 |
| River     |  0 |      0   |      0 |         0 |         0 |       0 |      0 |    1 |     0 |    0 |
| Road      |  0 |      0   |      0 |         0 |         0 |       0 |      0 |    0 |     0 |    4 |

## Training Data

The model is trained on forest loss driver annotations produced by Amazon Conservation
Association. Each annotation specifies a polygon and timestamp that originate from a
GLAD-S2 alert, along with the driver category. We use rslearn to obtain the four
pre-forest-loss Sentinel-2 L2A images and four post-forest-loss images.

We split the dataset into 75% train and 25% val.

The training data is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en).

## Inference

Inference is documented in [the main README](../README.md). The prediction request
geometry consists of one GeoJSON polygon for each connected component of GLAD-S2 alert
pixels that should be processed.

The prediction request geometry can be generated from the
[GLAD alert files on GCS](https://console.cloud.google.com/storage/browser/earthenginepartners-hansen/S2alert/):

```
python -m olmoearth_projects.main projects.forest_loss_driver extract_alerts --extract_alerts_args.gcs_tiff_filenames+=080W_20S_070W_10S.tif --extract_alerts_args.out_fname='prediction_request_geometry.geojson' --extract_alerts_args.days=90
```

Here, the `gcs_tiff_filenames` is a list of GLAD-S2 tiles to process (see the GCS link
above for the available tiles) and `days` specifies the time range (it will cover this
many days from the current timestamp into the past).

If you open the `prediction_request_geometry.geojson` in qgis, you should see several
small polygons. The model will be applied on a 128x128 pixel window centered at each of
these polygons.

To run inference:

```
mv prediction_request_geometry.geojson olmoearth_run_data/forest_loss_driver/prediction_request_geometry.geojson
mkdir -p ./checkpoints
wget -O checkpoints/forest_loss_driver.ckpt https://huggingface.co/allenai/OlmoEarth-v1-FT-ForestLossDriver-Base/resolve/main/model.ckpt
export NUM_WORKERS=32
export WANDB_PROJECT=forest_loss_driver
export WANDB_NAME=forest_loss_driver
export WANDB_ENTITY=YOUR_WANDB_ENTITY
python -m olmoearth_projects.main olmoearth_run olmoearth_run --config_path $PWD/olmoearth_run_data/forest_loss_driver/ --checkpoint_path $PWD/checkpoints/forest_loss_driver.ckpt --scratch_path project_data/forest_loss_driver/
```

## Fine-tuning

Fine-tuning is documented in [the main README](../README.md).

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/internal.md

## Ai2-Internal Documentation

## Model Development Workflow

This section covers where project-specific code, configs, and rslearn datasets should
be stored while a model is being developed.

For projects that need to use rslearn directly initially:
1. Add code like data curation and programmatic window creation to `rslp/[project_name]`
   in rslearn_projects.
2. Add rslearn dataset and model configs to `data/[project_name]/[version_id]/` (in
   rslearn_projects). Document the version history in data/[project_name]/README.md.
3. Put the rslearn dataset in `/weka/dfive-default/rslearn-eai/datasets/[project_name]/[version_id]`.
   Document the available rslearn datasets (version history) in `data/[project_name]/README.md`.
4. Run data materialization and fine-tuning jobs from rslearn_projects. See
   `rslp/common/README.md` for some details about how to launch these jobs.

Once ready for fine-tuning and/or prediction runs in OlmoEarth platform:
1. Copy configs to `olmoearth_run_data/[project_name]/[version_id]` in
   olmoearth_projects. `olmoearth_run_data/[project_name]/` should document where the
   configs came from and anything special about the olmoearth_run.yaml.
2. Add any new supporting code relevant for deploying on OlmoEarth platform to
   `olmoearth_projects/[project_name]`.
3. If running inference only, copy the checkpoint from WEKA to
   `gs://rslearn-eai/model_checkpoints/[project_name]/[version].ckpt` so that the
   platform has access to it.

Also see `docs/internal.md` in rslearn_projects for basic info about using that
repository.

## WEKA Dataset Locations

### LFMC

- Dataset used for training: `/weka/dfive-default/rslearn-eai/datasets/lfmc/20251023/woody/scratch/dataset`
- Here is a copy that should be same as above but maybe with some unneeded layers removed: `/weka/dfive-default/olmoearth_release_data/rslearn_datasets/lfmc/`

Note that olmoearth_evals uses `/weka/dfive-default/rslearn-eai/datasets/lfmc/20250626/`
which is an older version of the dataset.

### Ecosystem Type Mapping

- Dataset used for training: `/weka/dfive-default/rslearn-eai/datasets/geo/dataset_v2/dataset/`

### Forest Loss Driver

- Dataset used for training: `/weka/dfive-default/rslearn-eai/datasets/forest_loss_driver/dataset_v1/combined/`

### Mangrove Classification

- Dataset used for training: `/weka/dfive-default/rslearn-eai/datasets/mangrove/classification/20250626/`

### Solar Farm Segmentation

- Dataset used for training: `/weka/dfive-default/rslearn-eai/datasets/solar_farm/dataset_v1/20250605/`

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/lfmc.md

## Live Fuel Moisture Content (LFMC) Mapping

OlmoEarth-v1-FT-LFMC-Base is a model fine-tuned from OlmoEarth-v1-Base for predicting
the live fuel moisture content of woody vegetation from Sentinel-2 and Sentinel-1
satellite images.

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt
- Annotation GeoJSONs: [[annotation_features.geojson](https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/annotation_features.geojson) [annotation_task_features.geojson](https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/annotation_task_features.geojson)]
- rslearn dataset: https://storage.googleapis.com/ai2-olmoearth-projects-public-data/projects/lfmc/20251029/dataset.tar

## Model Details

The model inputs twelve timesteps of satellite image data, with one
[Sentinel-1 RTC](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc)
mosaic and one
[Sentinel-2 L2A](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a)
mosaic per 14-day period.

At each pixel, it regresses the LFMC of woody vegetation.

It achieves a mean squared error of 580.6 on our test set.

## Training Data

The model is trained on the [Globe-LFMC 2.0 dataset](https://springernature.figshare.com/articles/dataset/Globe-LFMC-2_0/25413790?backTo=%2Fcollections%2FGlobe-LFMC_2_0_An_enhanced_and_updated_database_for_Live_Fuel_Moisture_Content_research_%2F6980418&file=45049786)
by Marta Yebra et al. We use the subset of the data in the continental US.

Each sample in the dataset specifies a longitude, latitude, timestamp, fuel type, and
LFMC value. We only use the woody fuel type subset for this model. For each sample, we
create an rslearn window centered at the sample's longitude/latitude and with time
range equal to the 168 days ending at the sample's timestamp. We use rslearn to obtain
twelve Sentinel-2 and Sentinel-1 images during that time range, with one per 14-day period.

We split the dataset into train, val, and test splits spatially, where 128x128 pixel
grid cells are assigned via hash to train (70%), val (20%), or test (10%).

The training data is released under [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

## Inference

Inference is documented in [the main README](../README.md). The prediction request
geometry should have start timestamp equal to the timestamp for which you want to make
the LFMC prediction (e.g., the current timestamp). The end timestamp won't be used and
can be set arbitrarily, e.g. set equal to the start timestamp.

## Fine-tuning

Fine-tuning is documented in [the main README](../README.md).

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/mangrove.md

## Mangrove Extent Mapping

OlmoEarth-v1-FT-Mangrove-Base is a model fine-tuned from OlmoEarth-v1-Base for preddicting mangrove extent from Sentinel-2.

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-Mangrove-Base/resolve/main/model.ckpt
- Annotation GeoJsons: https://huggingface.co/allenai/olmoearth_projects_mangrove/blob/main/annotation_features.geojson
- rslearn dataset: https://huggingface.co/allenai/olmoearth_projects_mangrove/resolve/main/mangrove.tar

## Model Details

The model inputs twelve timesteps of satellite image data with one
mosaic [Sentinel-2 L2A](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a)
mosaic per 30-day period.

At every 2 by 2 patch it outputs a classification of mangrove, water or other.

The model achieves strong performance on the validation set with an overall accuracy of 97.6%.


## Training Data

The model is trained on data provided by [Global Mangrove Watch](https://www.mangrovealliance.org/global-mangrove-watch) available at https://zenodo.org/records/17394267.
The dataset is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Each sample in the dataset specifies a longitude, latitude, a start and end time (1 year apart), and a class label. For each sample we create a 12 month time series of Sentinel 2 data within the time bounds.

We split the dataset into train, val, splits , where each 2 by 2 pixel
grid cells are assigned via hash to train (87.5%), val (12.5%).

## Inference

Inference is documented in [the main README](../README.md). The prediction request
geometry should have start timestamp set 12 months prior to the date in which you would like to classify mangrove extent.

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/nandi.md

## Nandi Crop Type Mapping

OlmoEarth-v1-FT-Nandi-Base is a model fine-tuned from OlmoEarth-v1-Base for predicting crop and land-cover type across the Nandi county in Kenya using Sentinel-2 satellite images.

Here are relevant links for fine-tuning and applying the model per the documentation in
[the main README](../README.md):

- Model checkpoint: https://huggingface.co/allenai/OlmoEarth-v1-FT-Nandi-Base/blob/main/model.ckpt
- Annotation GeoJSONs: https://huggingface.co/datasets/allenai/olmoearth_projects_nandi/tree/main
- rslearn dataset: https://huggingface.co/datasets/allenai/olmoearth_projects_nandi/blob/main/dataset.tar

## Model Details

The model inputs twelve timesteps of satellite image data, one [Sentinel-2 L2A](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a) mosaic per 30-day period.

The model is trained to predict crop and land-cover type for every pixel within each 16×16 input patches.

The model (window size: 16x16, patch size: 1) achieves an overall accuracy of 87.3% on our validation set. The table below summarizes our experiments with different patch sizes and input modalities. Overall, mnodels using patch size 1 perform the best.

| Window Size | Patch Size | Modalities | Accuracy (%) |
|--------------|-------------|-------------|---------------|
| 16×16 | 1 | Sentinel-2 | 87.3 |
| 16×16 | 1 | Sentinel-2 + Sentinel-1 | TBD |
| 16×16 | 2 | Sentinel-2 | 86.5 |
| 16×16 | 2 | Sentinel-2 + Sentinel-1 | 86.7 |
| 16×16 | 4 | Sentinel-2 | 81.9 |
| 16×16 | 4 | Sentinel-2 + Sentinel-1 | 82.2 |

## Training Data

The model is trained on ground-truth labels collected by [CGIAR/IFPRI](https://www.ifpri.org/). The original dataset includes 819 labeled polygons, from which we sampled training points. To improve coverage, we added extra point samples from ESA WorldCover (since the original dataset lacked Water and Built-up classes) and additional Tree samples annotated in the Studio to correct misclassification of natural forest areas as Coffee.

In total, the dataset covers 10 categories: coffee, maize, sugarcane, tea, vegetables, legumes, grassland, trees, water, and built-up.

Each sample includes its longitude, latitude, time range (2022-09 to 2023-09), and crop or land-cover type. For each sample, we generate an rslearn window centered on the location, covering one year of data. We use rslearn to obtain twelve Sentinel-2 and Sentinel-1 imagery during that time range, with one per 30-day period.

The dataset is split spatially into training (75%) and validation (25%) sets, based on a 128×128-pixel grid hashed into the two splits.

## Inference

Inference is documented in [the main README](../README.md). The prediction request geometry should have start and end timestamps that covers one year, ideally from 2022-09-01 to 2023-09-01 to match the training data. However, you can also run inference for other one-year periods, such as 2018-09-01 to 2019-09-01. Inference runs on all 1024×1024 grid cells intersecting the geometry, using satellite images from the specified time range.

Here's the [inference output](https://olmoearth.allenai.org/viewer/6b1e4537-ea68-47f3-9a11-61ca2d468fd0#9.55/0.2218/35.1037) for the whole Nandi county.

## Fine-tuning

Fine-tuning is documented in [the main README](../README.md).

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/docs/tutorials/FinetuneOlmoEarthSegmentation.md

# Fine-tuning OlmoEarth for Burned Area Detection - A Tutorial

| # | Section |
| - | - |
| 0 | [Goal](#0-goal) |
| 1 | [Environment Setup](#1-environment-setup) |
| 2 | [Prepare the Dataset](#2-prepare-the-dataset) |
| 3 | [Define the Training Configuration](#3-define-the-training-configuration) |
| 4 | [Launch Fine-Tuning](#4-launch-fine-tuning) |
| 5 | [Run Inference With Your Fine-Tuned Model](#5-run-inference-with-your-fine-tuned-model) |


## 0. Goal
Let's build a burned area detection model using OlmoEarth. We will fine-tune the base model on a burned area mapping task and use it to detect fire perimeters for previously unseen fires.


## 1. Environment Setup
We recommend installing using `uv`. See [Installing uv](https://docs.astral.sh/uv/getting-started/installation/) for instructions. Once uv is installed, run:
```shell
git clone https://github.com/allenai/olmoearth_projects.git
cd olmoearth_projects
uv sync
source .venv/bin/activate
```

## 2. Preparing the Dataset
Let's start by using fire perimeter data from CalFire. These come as polygons associated with a contained date, which we will use to determine when our satellite snapshots should be captured (within 4 weeks of the contained date).

### 2a. Data Download, Filtering, and Label Creation
The following script downloads the data from CalFire and prepares it for training. It specifically:
- Downloads the data from CalFire ([data viewer](https://experience.arcgis.com/experience/b72eede32897423683a94c61bf9d3027))
- Filters out fires that happened before 2020 and creates a "label" column (label value = 'burnt' for fire polygons)
- Creates negative polygons (label value = 'unburnt') by drawing ring polygons around each fire perimeter, with a 150m gap to account for uncertainty
- Projects all polygons to EPSG:4326

<p align="center">
  <img src="./FinetuneOlmoEarthSegmentation/Example%20fire%20polygons.png" alt="Description" width="200">
  <br>
  <em>Figure 1: Example of 'burnt' and 'unburnt' ring polygons</em>
</p>

First, set `SRC_DATA_DIR` to the directory where you want to store the downloaded CalFire dataset.
```shell
export SRC_DATA_DIR=/path/to/your/data  # Replace with your desired data directory
python3 ./docs/tutorials/FinetuneOlmoEarthSegmentation/adhoc_scripts/Calfire_data_prep.py --data-dir $SRC_DATA_DIR --gap-width 150
```

### 2b. Window Geometry Design

To prepare the dataset for fine-tuning, we need to create spatiotemporal windows. A *window* roughly corresponds to a training or validation/test example. It defines a geographic area coupled with a time range over which we want the model to make predictions.

In our case, each window should be large enough to encompass its corresponding polygon, with a minimum size that ensures the model can receive a consistent input size. The following script creates windows with a minimum size of 128×128 pixels around each polygon, and stores it in the *task_geom* field, which will be used to build the windows

**Note:** This step is specific to our use case, where polygons have varied shapes and sizes. If you're working with uniformly sized polygons or point data, you may prefer to use identical window sizes for all samples.
```shell
python3 ./docs/tutorials/FinetuneOlmoEarthSegmentation/adhoc_scripts/Calfire_taskgeom_creation.py $SRC_DATA_DIR/Calfp_2020-2025.gdb --min_box_size_pix 128
```

<p align="center">
  <img src="./FinetuneOlmoEarthSegmentation/Example%20windows.png" alt="Example windows" width="300">
  <br>
  <em>Figure 2: Example of 'burnt' and 'unburnt' windows</em>
</p>

### 2c. Creating the Standardized Annotation Files
The `olmoearth_run` tool can fully automate the dataset ingestion and preparation pipeline, provided it receives standardized GeoJSON annotation files. The following script takes our polygon and window geometries (from the output file `Calfp_2020-2025_bbox.gdb` created in step 2b) and converts them into the GeoJSON format expected by `olmoearth_run`.

We specify the window/task geometry column created in step 2b using the `--taskgeom-col` parameter. This annotation creation step can be reused for most input GIS files and enforces the standardized format expected by `olmoearth_run`.

First, set `PROJECT_PATH` to the directory where you want to store the project configuration files.
```shell
export PROJECT_PATH=./docs/tutorials/FinetuneOlmoEarthSegmentation/config
python ./scripts/oer_annotation_creation.py $SRC_DATA_DIR/Calfp_2020-2025_bbox.gdb --outdir $PROJECT_PATH --id-col polygon_id --taskgeom-col task_geom
```

### 2d. Building windows
Now that our window and polygon geometries are ready for `olmoearth_run`, we need to specify how it should interpret them and build the associated dataset windows. This is configured in the `olmoearth_run.yaml` config file located [here](./FinetuneOlmoEarthSegmentation/config/olmoearth_run.yaml).

For example, here's our window preparation configuration. The `PolygonToRasterWindowPreparer` class rasterizes our 'burnt' and 'unburnt' polygons onto the window/task footprints defined in step 2b. Since we want to fully leverage the resolution of Sentinel-2 data, we specify the `window_resolution` as 10m. Additionally, we configure a spatial split for our train/validation/test sets using a grid size of 1000 pixels (10km).

```yaml
window_prep:
  labeled_window_preparer:
    class_path: olmoearth_run.runner.tools.labeled_window_preparers.polygon_to_raster_window_preparer.PolygonToRasterWindowPreparer
    init_args:
      window_resolution: 10.0

  data_splitter:
    class_path: olmoearth_run.runner.tools.data_splitters.spatial_data_splitter.SpatialDataSplitter
    init_args:
      train_prop: 0.7
      val_prop: 0.15
      test_prop: 0.15
      grid_size: 1000
  label_layer: "label"
  label_property: "category"
  group_name: "spatial_split_10km"
  split_property: "split"
```



Now let's use `olmoearth_run` to build these windows:

```shell
export OER_DATASET_PATH=/path/to/your/oerun_dataset/folder # Replace with desired dataset folder path
python -m olmoearth_projects.main olmoearth_run prepare_labeled_windows --project_path $PROJECT_PATH --scratch_path $OER_DATASET_PATH
```

### 2e. Remote Sensing Data
At this point, we need to create a `dataset.json` file that defines our dataset schema: which layers exist, their type (raster/vector), formats, and optionally how to auto-populate them via a `data_source`. This dataset.json file should live in our project path.

In our case, we have created our windows and label layer in raster format, so we need to reflect this in the configuration. Additionally, we specify the remote sensing data we want to add to our dataset as a covariate: Sentinel-2.

```json
{
    "layers": {
        "label": {
            "type": "raster",
            "band_sets": [
                {
                "bands": ["label"],
                "dtype": "uint8"
                }
            ]
        },
        "sentinel2_l2a": {
            "type": "raster",
            "band_sets": [
                {
                "bands": [
                    "B02",
                    "B03",
                    "B04",
                    "B08"
                ],
                "dtype": "uint16"
                },
                {
                "bands": [
                    "B05",
                    "B06",
                    "B07",
                    "B8A",
                    "B11",
                    "B12"
                ],
                "dtype": "uint16",
                "zoom_offset": -1
                },
                {
                "bands": [
                    "B01",
                    "B09"
                ],
                "dtype": "uint16",
                "zoom_offset": -2
                }
            ],
            "data_source": {
                "cache_dir": "cache/planetary_computer",
                "duration": "45d",
                "harmonize": true,
                "ingest": false,
                "query": { "eo:cloud_cover": { "lt": 50 }},
                "name": "rslearn.data_sources.planetary_computer.Sentinel2",
                "sort_by": "eo:cloud_cover"
            }

        }
    }
}
```

You can find more information about how to set up your `dataset.json` config file [here](https://github.com/allenai/rslearn/blob/master/docs/DatasetConfig.md).


Now let's launch the Sentinel-2 data fetching and stitching process to match our windows:

```shell
python -m olmoearth_projects.main olmoearth_run build_dataset_from_windows --project_path $PROJECT_PATH --scratch_path $OER_DATASET_PATH
```


## 3. Define the Training Configuration

Four flavors of OlmoEarth are available on Hugging Face [here](https://huggingface.co/collections/allenai/olmoearth).

Depending on the complexity of your task, your fine-tuning budget, and your GPU memory, you can select from different encoder model sizes:


  - **OlmoEarth nano:** model_id: `OLMOEARTH_V1_NANO` | Num parameters: 1.4M
  - **OlmoEarth tiny:** model_id: `OLMOEARTH_V1_TINY` | Num parameters: 6.2M
  - **OlmoEarth base:** model_id: `OLMOEARTH_V1_BASE` | Num parameters: ~90M
  - **OlmoEarth large:** model_id: `OLMOEARTH_V1_LARGE` | Num parameters: ~300M

Now we need to design our model architecture, training loop, and evaluation metrics, and define how the data should be pre-processed and sent to the model. Behind the scenes, we use Lightning to coordinate and run the fine-tuning job. This allows us to configure every aspect of the job in a single configuration file.

You can find the full `model.yaml` file [here](./FinetuneOlmoEarthSegmentation/config/model.yaml):

Here are a few noteworthy extracts.

Our model uses the `OLMOEARTH_V1_BASE` encoder and decodes the embedded tokens with a UNet architecture, so that each input pixel is predicted by the model.

```yaml
model:
  class_path: rslearn.train.lightning_module.RslearnLightningModule
  init_args:
    model:
      class_path: rslearn.models.multitask.MultiTaskModel
      init_args:
        encoder:
          - class_path: rslearn.models.olmoearth_pretrain.model.OlmoEarth
            init_args:
                model_id: "OLMOEARTH_V1_BASE"  # Replace with your selected model
                patch_size: 4
        decoders:
          burnscar_segmentation:
          - class_path: rslearn.models.unet.UNetDecoder
            init_args:
              in_channels:
                - [4, 768]
              out_channels: 2
              conv_layers_per_resolution: 2
              kernel_size: 3
              num_channels:
                '1': 128
                '2': 256
                '4': 512
          - class_path: rslearn.train.tasks.segmentation.SegmentationHead
```

The data configuration specifies the Sentinel-2 normalization preprocessing (using OlmoEarth's default normalization) and defines the patch size and data splits:

```yaml
data:
  # ... (dataset path, inputs, task configuration)
  default_config:
      transforms:
        - class_path: rslearn.models.olmoearth_pretrain.norm.OlmoEarthNormalize
          init_args:
            band_names:
              sentinel2_l2a: ["B02", "B03", "B04", "B08", "B05", "B06", "B07", "B8A", "B11", "B12", "B01", "B09"]
      patch_size: 128 # Size of random crops within the input window
    train_config:
      groups: ["spatial_split_10km"]
      tags:
        split: "train"
    val_config:
      groups: ["spatial_split_10km"]
      patch_size: 128
      load_all_patches: true  # Load all patches (no random crops) for validation in sliding window fashion
      tags:
        split: "val"
```

You can find more information about how to set up the `model.yaml` config file [here](https://github.com/allenai/rslearn/blob/master/docs/ModelConfig.md).


## 4. Launching Fine-Tuning

First, let's verify how many data points we have in our different splits:
```shell
export GROUP_NAME="spatial_split_10km"  # Use the group name from your olmoearth_run.yaml
find $OER_DATASET_PATH/dataset/windows/$GROUP_NAME -maxdepth 2 -name "metadata.json" -exec cat {} \; | grep -oE "train|val|test" | sort | uniq -c | awk 'BEGIN{printf "{"} {printf "%s\"%s\": %d", (NR>1?", ":""), $2, $1} END{print "}"}'
```

Now let's fine-tune the model. Set up your environment variables and run the fine-tuning command:
```shell
export WANDB_PROJECT="oe_burn-scar-finetuning"  # Replace with your WandB project name
export WANDB_NAME="burn-scar_seg_s2_p4_c128_unet_lr1e4"  # Replace with your experiment name
export WANDB_ENTITY="your-wandb-entity"  # Replace with your WandB entity

python -m olmoearth_projects.main olmoearth_run finetune \
  --project_path $PROJECT_PATH \
  --scratch_path $OER_DATASET_PATH
```

The model should reach ~96% F1 score after 30 epochs.


## 5. Running Inference With Your Fine-Tuned Model

First let's create a `prediction_request_geometry.geojson` in our project folder to indicate our AOI (where we would like the model to make predictions). For this we use a window corresponding to a 'burnt' polygon from our test set:

```json
{
  "features": [
    {
      "geometry": {
        "coordinates": [
                  [[-121.368852,38.875384],
                    [-121.326357,38.875384],
                    [-121.326357,38.901207],
                    [-121.368852,38.901207],
                    [-121.368852,38.875384]]
                ],
        "type": "Polygon"
      },
      "properties": {
        "oe_start_time": "2020-06-23T00:00:00+00:00",
        "oe_end_time": "2020-07-23T00:00:00+00:00"
      },
      "type": "Feature"
    }
  ],
  "type": "FeatureCollection"
}

```

Let's add a few configuration lines to `olmoearth_run.yaml` to specify:
- partition_strategies:
  - partition_request_geometry: how to split the AOI into partitions
  - prepare_window_geometries: how to create windows within partitions
- postprocessing_strategies: how to merge results

```yaml
partition_strategies:
  partition_request_geometry:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 0.25 # (angle in degrees)

  prepare_window_geometries:
    class_path: olmoearth_run.runner.tools.partitioners.grid_partitioner.GridPartitioner
    init_args:
      grid_size: 1024 # (in pixels)
      output_projection:
        class_path: rslearn.utils.geometry.Projection
        init_args:
          crs: EPSG:3857
          x_resolution: 10
          y_resolution: -10
      use_utm: true

postprocessing_strategies:
  process_dataset:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff

  process_partition:
    class_path: olmoearth_run.runner.tools.postprocessors.combine_geotiff.CombineGeotiff

```

Finally, we specify how the dataloader should handle our prediction windows under the **data** section of our `model.yaml`.
By default, our prediction windows will be automatically created under the group: "group_partition_0". We set `load_all_patches: true` so that each patch (of size 128) within our window is visited in a sliding window fashion, with an overlap of 12.5% between patches (or 16 pixels our of 128).
```yaml
    predict_config:
      groups: ["group_partition_0"]
      patch_size: 128
      load_all_patches: true
      overlap_ratio: 0.125  # 16 / 128
      skip_targets: true
```

Now let's run the inference command:
```shell
unset TRAINER_DATA_PATH
unset DATASET_PATH
export CHECKPOINT_PATH=/path/to/your/best/checkpoint.ckpt  # Replace with path to your trained model, which by default should be located at ${OER_DATASET_PATH}/trainer_checkpoints/{your_desired_checkpoint}.ckpt

python -m olmoearth_projects.main olmoearth_run olmoearth_run \
  --config_path $PROJECT_PATH \
  --scratch_path $OER_DATASET_PATH \
  --checkpoint_path $CHECKPOINT_PATH
```

By default, the predicted windows are mosaiced together in the results folder.
We can now visualize our predictions:
```
qgis  ${OER_DATASET_PATH}/results/results_raster/{your_result_geotif}.tif
```

<p align="center">
  <img src="./FinetuneOlmoEarthSegmentation/fire_pred.jpg" alt="Example windows" width="700">
  <br>
  <em>Figure 3: Fire perimeter prediction (left) and ground truth (right) on unseen window</em>
</p>


<p align="center">
  <img src="./FinetuneOlmoEarthSegmentation/controlled_fire.png" alt="Example windows" width="350">
  <br>
  <em>Figure 4: Model picking up controlled fire (purple) at the edge <br> of the prediction window (light blue) months after it happened</em>
</p>

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/KCG_SUMMARY.md

# OLMo Earth Projects — KCG Summary

## What It Is
Allen AI's repository of configuration files, model checkpoint references, and documentation for remote sensing models built on the OLMo Earth foundation model. Includes tools and tutorials for fine-tuning OLMo Earth on satellite imagery tasks: forest loss driver classification, mangrove mapping, ecosystem type mapping, land use classification, and live fuel moisture content mapping.

## Why This Matters for Kings' College Galway
Remote sensing and satellite imagery analysis maps to Irish geography and environmental studies in the curriculum. OLMo Earth's fine-tuning patterns for segmentation and classification demonstrate how to adapt large vision models to domain-specific tasks — directly transferable to adapting document vision models for historical Irish manuscript layout analysis. The geospatial data processing pipeline (rslearn + olmoearth_run) provides patterns for handling large-scale educational image datasets, such as digitised Leaving Certificate exam papers spanning decades. Fine-tuning foundation models for specialised domains is the core skill needed for Celtic language model adaptation.

## Key Patterns Preserved
- `README.md` — Project overview: available models, installation, tutorial links
- `docs/awf.md` — Land use / land cover mapping in Southern Kenya
- `docs/ecosystem_type_mapping.md` — Ecosystem type classification model
- `docs/forest_loss_driver.md` — Forest loss driver classification
- `docs/lfmc.md` — Live Fuel Moisture Content mapping
- `docs/mangrove.md` — Mangrove mapping model
- `docs/nandi.md` — Nandi region land cover mapping
- `docs/internal.md` — Allen AI internal infrastructure notes
- `docs/tutorials/FinetuneOlmoEarthSegmentation.md` — Fine-tuning OLMo Earth for segmentation tasks
- `olmoearth_projects/olmoearth_run/README.md` — OLMo Earth runner tooling
- `olmoearth_projects/utils/label_quality/README.md` — Label quality assessment utilities
- `olmoearth_run_data/mozambique_lulc/README.md` — Mozambique land use dataset
- `olmoearth_run_data/sample/README.md` — Sample data configuration
- `olmoearth_run_data/satlas_solar_farm/README.md` — Solar farm detection data

## Source Files
Full source removed (2026-06-06). Available at:
- GitHub: https://github.com/allenai/olmoearth_projects

## What Was Removed
Python source code, YAML/TOML configuration files, Jupyter notebooks, JSON data files, satellite image data (GeoTIFF, etc.), package dependencies (pyproject.toml, uv.lock), Dockerfiles, CI/CD configs, Git metadata.

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_projects/olmoearth_run/README.md

Here is example:

```
python -m olmoearth_projects.main olmoearth_run olmoearth_run --config_path olmoearth_run_data/satlas/solar_farm/ --scratch_path /tmp/scratch/
```

So in `olmoearth_run/satlas/solar_farm/` we have:

- `dataset.json`: the rslearn dataset configuration file.
- `model.yaml`: the rslearn model configuration file.
- `olmoearth_run.yaml`: new YAML file containing oerun pre/post processing config.
- `prediction_request_geometry.geojson`: the GeoJSON input to the olmoearth_run partition and window generation.


In the `olmoearth_run_data/sample` directory, we can also run training window preparation, which
depends on:

- `dataset.json`: the rslearn dataset configuration file.
- `olmoearth_run.yaml`: new YAML file containiner the window_prep config
- `annotation_features.geojson`: annotation geojson FeatureCollection exported from Studio
- `annotation_task_features.geojson`: the Studio task geojson Features corresponding to the above

Run with:

```
uv run python -m olmoearth_projects.main olmoearth_run prepare_labeled_windows \
    --project_path $(pwd)/olmoearth_run_data/sample \
    --scratch_path /tmp/scratch
```

to produce a new dataset at:

```
/tmp/scratch/dataset
```

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_projects/utils/label_quality/README.md

# Label Quality

`olmoearth_projects` demonstrates how OlmoEarth can be applied to downstream applications.
Specifically, given a set of labels, `olmoearth_projects` demonstrates how to finetune, evaluate and apply OlmoEarth over a spatial area.

The quality of the model's predictions depend on the quality of the labels.
Assessing the quality of the labels is best done by domain experts.
However, the functions in this folder also provide some indication of how well suited a set of labels are for mapping.

#### Spatial Clustering

This function assesses how spatially clustered classes are.
In general, we'd like different classes to be well spatially distributed:

```
xoxoxox
oxoxoxo
xoxoxox
```
is more desirable than
```
xxx
xxx
   ooo
   ooo
```
We measure this by running a spatial KNN on the dataset - for each instance in the dataset, we define its class
to be the mode of the K nearest (spatial) points. High accuracies indicate high spatial clustering.

### Spatial extent

This function assesses how much of the total labelled area each class occupies.
In general, we would like each class to occupy a large fraction of the total labelled area:

```
x xox x
ox x xo
x xox x
```
is more desirable then
```
x x x x
 x xoxo
x xoxox
```
For each class, this is measured as `(area covered by all the labels in the class) / (area covered by all the labels)`.

### Label imbalance

This function assesses the fraction of labels belonging to each class: `(number of labels in a class) / (total number of labels)`.

### Examples

An example of how to run this is on an rslearn dataset is in [the `mozambique_lulc` project](../../projects/mozambique_lulc/check_label_quality.py):

```console
$ python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 --split train

Checking label quality for 4881 instances.
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃         Check name ┃ Metric                ┃               Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│    label_imbalance │ Bare Ground           │ 0.12681827494365908 │
│    label_imbalance │ Trees                 │ 0.09813562794509322 │
│    label_imbalance │ Cropland              │ 0.27760704773611966 │
│    label_imbalance │ Flooded Vegetation    │  0.1024380249948781 │
│    label_imbalance │ Water                 │ 0.11391108379430445 │
│    label_imbalance │ Rangeland             │ 0.10530628969473468 │
│    label_imbalance │ Buildings             │  0.1757836508912108 │
│ spatial_clustering │ Bare Ground_f1        │  0.7763055339049103 │
│ spatial_clustering │ Trees_f1              │               0.918 │
│ spatial_clustering │ Cropland_f1           │  0.8201489890031926 │
│ spatial_clustering │ Flooded Vegetation_f1 │  0.6470588235294118 │
│ spatial_clustering │ Water_f1              │  0.5609756097560976 │
│ spatial_clustering │ Rangeland_f1          │  0.7097480832420592 │
│ spatial_clustering │ Buildings_f1          │  0.9638554216867469 │
│     spatial_extent │ Bare Ground           │   0.906388431021162 │
│     spatial_extent │ Trees                 │  0.8143211426450099 │
│     spatial_extent │ Cropland              │  0.8178565572914295 │
│     spatial_extent │ Flooded Vegetation    │  0.8195186876112993 │
│     spatial_extent │ Water                 │  0.8015534585021155 │
│     spatial_extent │ Rangeland             │  0.9892764881988351 │
│     spatial_extent │ Buildings             │  0.7256137393021044 │
└────────────────────┴───────────────────────┴─────────────────────┘
```

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/mozambique_lulc/README.md

# Mozambique LULC and Crop Type Classification

This project has two main tasks:
	1.	Land Use/Land Cover (LULC) and cropland classification
	2.	Crop type classification

The annotations come from field surveys across three provinces in Mozambique: Gaza, Zambezia, and Manica.

For LULC classification, the train/test splits are:
- Gaza: 2,262 / 970
- Manica: 1,917 / 822
- Zambezia: 1,225 / 525

### Generating the data
```
export DATASET_PATH=/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251113

python /weka/dfive-default/gabrielt/olmoearth_projects/olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py --gpkg_dir /weka/dfive-default/yawenz/datasets/mozambique/train_test_samples --ds_path $DATASET_PATH --window_size 32

python /weka/dfive-default/gabrielt/olmoearth_projects/olmoearth_projects/projects/mozambique_lulc/create_windows_for_lulc.py --gpkg_dir /weka/dfive-default/yawenz/datasets/mozambique/train_test_samples --ds_path $DATASET_PATH --window_size 32 --crop_type
```
You will then need to copy a `config.json` into `$DATASET_PATH`.

The config being used is available in [config.json](config.json). This config requires [rslearn_projects](https://github.com/allenai/rslearn_projects) in your environment.

Once the config is copied into the dataset root, the following commands can be run:

```
rslearn dataset prepare --root $DATASET_PATH --workers 64 --no-use-initial-job --retry-max-attempts 8 --retry-backoff-seconds 60

python -m rslp.main common launch_data_materialization_jobs --image yawenzzzz/rslp20251112h --ds_path $DATASET_PATH --clusters+=ai2/neptune-cirrascale --num_jobs 5
```
Finally - we treat this as a segmentation task, not as a classification task (this makes inference faster, without hurting performance). This means the point labels need to be transformed into rasters:

```
python olmoearth_projects/projects/mozambique_lulc/create_label_raster.py --ds_path $DATASET_PATH
```

Within `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc` there are four versions of the data:
- `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251023`, which only has the train and test split as defined in the gpkg files
- `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251113`, which splits the training data into train and val data using a spatial split (introduced in [this commit](https://github.com/allenai/olmoearth_projects/pull/28/commits/1cfb86d40c8e2ccba830eb80410d1248544877c9)). This leads to the following train / val / test splits (with `val_ratio = 0.2`):
    - Gaza: 1,802 / 460 / 970
	- Manica: 1,564 / 353 / 822
	- Zambezia: 949 / 276 / 525
	- For crop type mapping, the following train / val / test splits, per class: `'corn': {'train': 917, 'val': 191, 'test': 3709}, 'sesame': {'train': 384, 'val': 0, 'test': 383}, 'beans': {'train': 932, 'val': 224, 'test': 417}, 'rice': {'train': 648, 'val': 512, 'test': 863}, 'millet': {'train': 36, 'val': 0, 'test': 57}, 'cassava': {'train': 685, 'val': 133, 'test': 201}, 'sorghum': {'train': 52, 'val': 0, 'test': 41},`
- `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251114` which aligns the dates for all provinces (as in [this commit](https://github.com/allenai/olmoearth_projects/pull/28/commits/07ee7ef22a383b2c71ef6acab3171df8387924bd)).
- `/weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202`, which aligns the dates and the `dataset.json` & `config.json` so that 8 months of data are exported. We also update the val ratio to 0.1 to yield the following splits:
    - crop type mapping: `'corn': {'train': 917, 'val': 191, 'test': 3709}, 'sesame': {'train': 384, 'val': 0, 'test': 383}, 'beans': {'train': 932, 'val': 224, 'test': 417}, 'rice': {'train': 648, 'val': 512, 'test': 863}, 'millet': {'train': 36, 'val': 0, 'test': 57}, 'cassava': {'train': 685, 'val': 133, 'test': 201}, 'sorghum': {'train': 52, 'val': 0, 'test': 41},`
	- LULC: `{'Trees': {'train': 479, 'val': 56, 'test': 229}, 'Cropland': {'train': 1355, 'val': 159, 'test': 649}, 'Buildings': {'train': 858, 'val': 89, 'test': 406}, 'Bare Ground': {'train': 619, 'val': 50, 'test': 288}, 'Water': {'train': 556, 'val': 55, 'test': 263}, 'Rangeland': {'train': 514, 'val': 57, 'test': 245}, 'Flooded Vegetation': {'train': 500, 'val': 57, 'test': 237}`.

#### Assessing label quality

Label quality can be assessed by running the `check_label_quality.py` script:

```console
$ python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 --split train

Checking label quality for 4881 instances.
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃         Check name ┃ Metric                ┃               Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│    label_imbalance │ Bare Ground           │ 0.12681827494365908 │
│    label_imbalance │ Trees                 │ 0.09813562794509322 │
│    label_imbalance │ Cropland              │ 0.27760704773611966 │
│    label_imbalance │ Flooded Vegetation    │  0.1024380249948781 │
│    label_imbalance │ Water                 │ 0.11391108379430445 │
│    label_imbalance │ Rangeland             │ 0.10530628969473468 │
│    label_imbalance │ Buildings             │  0.1757836508912108 │
│ spatial_clustering │ Bare Ground_f1        │  0.7763055339049103 │
│ spatial_clustering │ Trees_f1              │               0.918 │
│ spatial_clustering │ Cropland_f1           │  0.8201489890031926 │
│ spatial_clustering │ Flooded Vegetation_f1 │  0.6470588235294118 │
│ spatial_clustering │ Water_f1              │  0.5609756097560976 │
│ spatial_clustering │ Rangeland_f1          │  0.7097480832420592 │
│ spatial_clustering │ Buildings_f1          │  0.9638554216867469 │
│     spatial_extent │ Bare Ground           │   0.906388431021162 │
│     spatial_extent │ Trees                 │  0.8143211426450099 │
│     spatial_extent │ Cropland              │  0.8178565572914295 │
│     spatial_extent │ Flooded Vegetation    │  0.8195186876112993 │
│     spatial_extent │ Water                 │  0.8015534585021155 │
│     spatial_extent │ Rangeland             │  0.9892764881988351 │
│     spatial_extent │ Buildings             │  0.7256137393021044 │
└────────────────────┴───────────────────────┴─────────────────────┘
```
and for crop type:
```console
$ python olmoearth_projects/projects/mozambique_lulc/check_label_quality.py --ds_path /weka/dfive-default/rslearn-eai/datasets/crop/mozambique_lulc/20251202 --split train --crop_type

Checking label quality for 3821 instances.
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃         Check name ┃ Metric     ┃                 Value ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│    label_imbalance │ beans      │     0.260664747448312 │
│    label_imbalance │ corn       │   0.24522376341271918 │
│    label_imbalance │ cassava    │   0.18503009683328972 │
│    label_imbalance │ sesame     │   0.10049725202826486 │
│    label_imbalance │ rice       │   0.18555352002093692 │
│    label_imbalance │ sorghum    │  0.013609002878827532 │
│    label_imbalance │ millet     │   0.00942161737764983 │
│ spatial_clustering │ beans_f1   │    0.9885401096163426 │
│ spatial_clustering │ corn_f1    │    0.9946581196581196 │
│ spatial_clustering │ cassava_f1 │    0.9728571428571429 │
│ spatial_clustering │ sesame_f1  │                   1.0 │
│ spatial_clustering │ rice_f1    │    0.9943661971830987 │
│ spatial_clustering │ sorghum_f1 │    0.9902912621359223 │
│ spatial_clustering │ millet_f1  │                   1.0 │
│     spatial_extent │ beans      │    0.7829124125842517 │
│     spatial_extent │ corn       │    0.8357589381957512 │
│     spatial_extent │ cassava    │    0.9383923435655623 │
│     spatial_extent │ sesame     │ 0.0003614488654102921 │
│     spatial_extent │ rice       │    0.7653946614854196 │
│     spatial_extent │ sorghum    │ 3.266172530759744e-07 │
│     spatial_extent │ millet     │ 0.0001509740414169792 │
└────────────────────┴────────────┴───────────────────────┘
```

### Finetuning

Currently, we use [rslearn_projects](github.com/allenai/rslearn_projects) for finetuning, using [rslp_finetuning.yaml](rslp_finetuning.yaml) and [rslp_finetuning_croptype.yaml](rslp_finetuning_croptype.yaml).  With `rslean_projects` installed (and access to Beaker), finetuning can then be run with the following command:

```
python -m rslp.main olmoearth_pretrain launch_finetune --image_name yawenzzzz/rslp20251112h --config_paths+=olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml --cluster+=ai2/saturn --rslp_project <MY_RSLP_PROJECT_NAME> --experiment_id <MY_EXPERIMENT_ID>
```

### Testing

Obtaining test results consisted of the following:
1. Spin up an interactive beaker session with a GPU: `beaker session create --remote --bare --budget ai2/es-platform --cluster ai2/saturn --mount src=weka,ref=dfive-default,dst=/weka/dfive-default --image beaker://yawenzzzz/rslp20251112h --gpus 1`
2. Go to the olmoearth projects folder on weka (to easily `git pull`) changes: `cd /weka/dfive-default/gabrielt/olmoearth_projects`
3. Add the `RSLP_PREFIX` to the environment, `export RSLP_PREFIX=/weka/dfive-default/rslearn-eai`
4. Run testing: `python -m rslp.rslearn_main model test --config olmoearth_run_data/mozambique_lulc/rslp_finetuning.yaml --rslp_experiment <MY_EXPERIMENT_ID> --rslp_project <MY_RSLP_PROJECT_NAME> --force_log=true --load_best=true --verbose true`

### Inference

All inference is done on [OlmoEarth Studio](https://olmoearth.allenai.org/). Polygons around the provinces were manually drawn (within Studio).

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/sample/README.md

# ES Runner Local Development Guide

## What is olmoearth_runner?

OlmoEarthRunner provides:

- the [OlmoEarthRunPredictRunner](https://github.com/allenai/olmoearth_run/blob/develop/src/olmoearth_run/runner/local/predict_runner.py)
- the [OlmoEarthRunFineTuneRunner](https://github.com/allenai/olmoearth_run/blob/develop/src/olmoearth_run/runner/local/fine_tune_runner.py)

classes, which can be used to run prediction and fine-tuning pipelines outside of the olmoearth_run service architecture


## Setting up your environment

- Install `oerunner` (olmoearth-run) in your development environment.
  ```
  pip install olmoearth-run @ git+https://github.com/allenai/olmoearth-run.git
  ```
- Following the project structure below, create a directory in the `rslearn-projects/olmoearth_run_data/` directory. This directory will contain all the necessary files for your prediction or fine-tuning pipeline.

## Project Structure
- `checkpoint.ckpt`:  This is the model checkpoint file. It is required for running inference. If you are only building datasets, this file is not required.  Note: You probably don't want to check this file into git repository.
- `dataset.json`: This is the rslearn dataset definition file.
- `olmoearth_run.yaml`: This file defines the behavior of the olmoearth_runner including partitioning, postprocessing, training window prep, etc..
- `model.yaml`: This is the rslearn (pytorch) model definition file.
- `annotation_features.geojson`: Labeled annotation feature collection, exported from Studio. Only required for labeled window prep.
- `annotation_task_features.geojson`: Studio tasks for the annotation features, also exported from Studio. Only required for labeled window prep.
- `prediction/test-request1.geojson`: This directory contains the prediction requests in GeoJSON format. Each file represents a set of prediction requests for a specific region or time period.  Many different prediction requests can be defined within a single file as separate features in the feature collection. The olmoearth_runner will partition these requests into smaller tasks based on the partition strategies defined in `olmoearth_run.yaml#partition_strategies`

## Fine-Tuning

Fine-tuning is encapsulated in the Fine Tuning Workflow, accessible through `OlmoEarthRunFineTuneRunner`. It currently only exposes a method for preparing labeled RSLearn windows from geojson feature collections exported through Earth System Studio. Using it requires your `olmoearth_run.yaml` to define the following data processing pipeline:

```yaml
window_prep:
  sampler:
  labeled_window_preparer:
  data_splitter:
```

### sampler

Technically optional, defaulting to `NoopSampler`. These classes receive a `list[AnnotationTask]` and are expected to return the same, filtered down by whatever needs your application has.

### labeled_window_preparer

Transforms individual `AnnotationTask` instances to `list[LabeledWindow[LabeledSTGeometry]]` or `LabeledWindowPreparer[list[RasterLabel]]` depending on whether vector or raster label output layers are desired, respectively.

Available window preparers:
  - `PointToPixelWindowPreparer` - Converts each annotation feature in a Studio task to a 1x1pixel window with a vector class label
  - `PolygonToRasterWindowPreparer` - Converts a Studio task + its (multi/)polygon annotations into a uint8 2d class matrix

### data_splitter

Given a `LabeledWindow`, assign it to `train`, `val`, or `test`.

Available data splitters:
  - `RandomDataSplitter` - weighted random assignment

### Run a pipeline end-to-end

A fully functional `olmoearth_run.yaml` and set of `.geojson` files is available in `olmoearth_run_data/sample` as a reference example.
Exercise it via:

```
python -m olmoearth_projects.main olmoearth_run prepare_labeled_windows \
    --project_path olmoearth_run_data/sample \
    --scratch_path /tmp/scratch
```

to produce labeled training windows at:

```
/tmp/scratch/dataset
```

### Getting the geojson files

Window labeling requires ES Studio Task + Annotation-formatted FeatureCollection files. The best way to get compliant
data is to upload your raw data via Studio's Command Center "Add Dataset" feature, and export to the desired
format via the "Export Annotations" tab. This will create the required data files in gcs, that you can then download to your working location.

### Writing Your Own Samplers

You may supply your own data samplers by creating a new class that implements the `SamplerInterface` class in the `olmoearth_run.runner.tools.samplers.sampler_interface` module. You can then specify your custom sampler in the `olmoearth_run.yaml` file. This
class must be importable via your PYTHONPATH. Include it as code in this repository or as a new implementation in olmoearth_run.git.

### Writing Your Own LabeledWindowPreparers

You may supply new implementations for converting raw Studio Tasks + Annotations into LabeledWindows. To do so, implement
either `olmoearth_run.runner.tools.labeled_window_preparers.labeled_window_preparer.RasterLabelsWindowPreparer` (for rasterized targets) or `olmoearth_run.runner.tools.labeled_window_preparers.labeled_window_preparer.VectorLabelsWindowPreparer` (for vector targets). As with Samplers, these must be importable from your PYTHONPATH and can be referenced by class path in `olmoearth_run.yaml`. Include as code in this repository or contribute directly to earth-system-run.git.

### Writing Your Own DataPartitioners

You may supply your own data partitioners to determine test/eval/train split assignment for a LabeledWindow. To do so, implement `olmoearth_run.runner.tools.data_splitter.data_splitter_interface.DataSplitterInterface`.

## Inference

Inference is encapsulated in the Prediction Workflow, accessible through `OlmoEarthRunPredictRunner`. It requires your `olmoearth_run.yaml` define:

- partitioning strategy
- post-processing strategy

### Partitioning Strategies
These stanzas defines how olmoearth_runner will break the inference request into multiple request geometries for compute parallelization (equivalent to rslearn window groups) and prediction window geometries.

Partitioning strategies can be mixed and matched for flexible development.
  - partition_request_geometry
  - prepare_window_geometries

Available partitioners:
- `FixedWindowPartitioner` - Given a fixed window size, this partitioner will create partitions of that size for each lat/lon or polygon centroid in the prediction request.
- `GridPartitioner` - Given a grid size, this partitioner will create partitions based on the grid cells that intersect with the prediction request.
- NoopPartitioner - Does not partition the prediction request. This is useful for testing or when you want to run the entire prediction request as a single task.

Example `olmoearth_run.yaml`. This will leave the original input as a single partition, but will create individual windows of size 128x128 pixels for each feature.
```yaml
partition_request_geometry:
  class_path: olmoearth_run.tools.partitioners.noop_partitioner.NoopPartitioner
  init_args:

prepare_window_geometries:
  class_path: olmoearth_run.tools.partitioners.fixed_window_partitioner.FixedWindowPartitioner
  init_args:
    window_size: 128 # intended to be a pixel value
```

### Post-Processing Strategies
There are 3 different stages to postprocessing:
  - `postprocess_window()` - This is the stage where individual model outputs are converted into a digestible artifact for the next stage.
  - `postprocess_partition()` - This is the stage where the outputs from the window postprocessors are combined into a single per-partition artifact.
  - `postprocess_dataset()` - This is the final stage of postprocessing where the partition level outputs are combined into a artifact.

### Samples

#### Run a pipeline end-to-end

The simplest way to run a pipeline is to use the `olmoearth-run-local-predict` CLI command.  This command will run the entire pipeline end-to-end including partitioning, dataset building, inference, post-processing, and combining the final outputs.
```
$ olmoearth-run-local-predict
```

If you want more flexibility, you can use the `OlmoEarthRunPredictRunner` class directly.  The following example shows how to run the entire pipeline end-to-end using the `OlmoEarthRunPredictRunner` class.  Note: This example may become out of date very quickly due to ongoing changes in the OlmoEarthRunPredictRunner class.  Refer to the olmoearth_run repo for the most up-to-date information.

```python file=run_pipeline.py
from pathlib import Path
from olmoearth_run.runner.local.predict_runner import OlmoEarthRunPredictRunner

config_path = Path(__file__).parent

runner = OlmoEarthRunPredictRunner(
    project_path=config_path,
    scratch_path=config_path / "scratch",
)
partitions = runner.partition()
for partition_id in partitions:
    runner.build_dataset(partition_id)
    runner.run_inference(partition_id)
    runner.postprocess(partition_id)

runner.combine(partitions)
```

#### Run dataset building for the entire prediction request.
```python file=run_dataset_building.py
from pathlib import Path
from olmoearth_run.runner.local.predict_runner import OlmoEarthRunPredictRunner

config_path = Path(__file__).parent

runner = OlmoEarthRunPredictRunner(
    project_path=config_path,
    scratch_path=config_path / "scratch",
)

for partition_id in runner.partition():
    runner.build_dataset(partition_id)
```

#### Run inference for a single partition.
(Assumes you have an existing materialized dataset for the partition.)
```python file=run_inference_single_partition.py
from pathlib import Path
from olmoearth_run.runner.local.predict_runner import OlmoEarthRunPredictRunner

config_path = Path(__file__).parent

runner = OlmoEarthRunPredictRunner(
    project_path=config_path,
    scratch_path=config_path / "scratch",
)
partition_id = 'my-existing-partition-id'  # Replace with the actual partition ID you want to run
runner.run_inference(partition_id)
```

#### Run inference for a single window.
Since we don't expose window-level inference via the runner API, you can configure your partitioners to produce limited sets of partitions and windows.

```yaml file=olmoearth_run.yaml
partition_request_geometry:
  class_path: olmoearth_run.runner.tools.partitioners.noop_partitioner.NoopPartitioner
  init_args:

prepare_window_geometries:
  class_path: olmoearth_run.runner.tools.partitioners.fixed_window_partitioner.FixedWindowPartitioner
  init_args:
    window_size: 128 # intended to be a pixel value
    limit: 1  # This will limit window generation to a single window per large partition, effectively allowing you to run inference on a single window.
```

```python file=run_inference_single_window.py
from pathlib import Path
from olmoearth_run.runner.local.predict_runner import OlmoEarthRunPredictRunner

config_path = Path(__file__).parent

runner = OlmoEarthRunPredictRunner(
    project_path=config_path,
    scratch_path=config_path / "scratch",
)
partition_id = 'my-existing-partition-id'  # Replace with the actual partition ID you want to run
partitions = runner.partition()
for partition_id in partitions:
    runner.run_inference(partition_id)
```

### Writing Your Own Partitioners
You may supply your own partitioners by creating a new class that implements the ` PartitionInterface` class in the `olmoearth_run.runner.tools.partitioners.partition_interface` module.  You can then specify your custom partitioner in the `olmoearth_run.yaml` file.  This class must exist on your PYTHONPATH and be importable by the olmoearth_runner.  As such we recommend you place your custom partitioner in the `olmoearth_projects/common/partitioners` directory of this repository to ensure it gets installed into the final Dockerimage artifact.

### Writing your own post-processing strategies
You may supply your own post-processing strategies by creating a new class that implements the `PostprocessInterface` class in the `olmoearth_run.runner.tools.postprocessors.postprocess_inferface` module.  You can then specify your custom post-processing strategy in the `postprocessing_strategies.yaml` file.  This class must exist on your `PYTHONPATH` and be importable by the olmoearth_runner.  As such we recommend you place your custom post-processing strategy in the `olmoearth_projects/common/postprocessing` directory of this repository to ensure it gets installed into the final Docker image artifact.

#### Testing Partitioner & Post-Processing Implementations
See the [olmoearth_run](https://github.com/allenai/olmoearth_run) repository for tests covering existing [partitioner](https://github.com/allenai/olmoearth_run/tree/develop/tests/unit/olmoearth_run/runner/tools/partitioners) and [post-processor](https://github.com/allenai/olmoearth_run/tree/develop/tests/unit/olmoearth_run/runner/tools/postprocessors) implementations.

## Longer Term Vision / Model Development Workflow
1. ML folk will create the requisite configs in a directory like this one.
2. Any additional or alternate requirements will be specified in a requirements.txt file in the same directory.
3. When a PR is created, CI will perform a docker build using the main Dockerfile in the root of the repo, but ensure any deviations from the main requirements.txt are merged into the main requirements.txt at build time so that the docker image is built with the correct requirements. This will allow developers to use this docker image for things like beaker runs or other executions (if needed.)
4. When the PR is merged, the docker build from above will be performed again, but the final image will be published to olmoearth_run as a new "model" (model version?) using the configurations in this directory.  (TODO: Should we consider "versioning" models in olmoearth_run?)
5. Once the "model" has been published to olmoearth_run, fine-tuning can be performed using olmoearth_run. (Longer term I think we can use a standard versioned helios image for this, but for now we can use the bespoke images created in the previous step.)
6. (Presumably) Once the fine-tuning is complete, olmoearth_run will publish the final model (with weights) to olmoearth_run as a (new?) model (version?).  OlmoEarth Run can then be used to run predictions with this final model.

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/satlas_solar_farm/README.md

The checkpoint is at:

```
gs://ai2-rslearn-projects-data/projects/2025_06_06_helios_finetuning/v2_satlas_solar_farm_128_ts_helios_per_mod_patchdisc_contrastive_fix_esrun/checkpoints/epoch=9999-step=99999.ckpt
```

Note that this checkpoint needed conversion from the original file below due to not
being able to change the task name.

```
/weka/dfive-default/rslearn-eai/projects/2025_06_06_helios_finetuning/v2_satlas_solar_farm_128_ts_helios_per_mod_patchdisc_contrastive_fix/checkpoints/epoch\=9999-step\=99999.ckpt
```

---


## File: docs/meaisínfhoghlaim/olmoearth_projects/README.md

## OlmoEarth Projects

This repository contains configuration files, model checkpoint references, and
documentation for several remote sensing models built on top of OlmoEarth at Ai2. It
also includes tooling and tutorials for building new models using various components of
OlmoEarth.

The models available here are:

- [Live Fuel Moisture Content Mapping](docs/lfmc.md)
- [Forest Loss Driver Classification](docs/forest_loss_driver.md)
- [Mangrove Mapping](docs/mangrove.md)
- [Ecosystem Type Mapping](docs/ecosystem_type_mapping.md)
- [Land Use / Land Cover Mapping in Southern Kenya](docs/awf.md)

The links above provide more details about the training data and intended use case for
each model.

Here are tutorials for applying OlmoEarth for new tasks:

- [Fine-tuning OlmoEarth for Segmentation](docs/tutorials/FinetuneOlmoEarthSegmentation.md)
- [Computing Embeddings using OlmoEarth](https://github.com/allenai/rslearn/blob/master/docs/examples/OlmoEarthEmbeddings.md)
- [Fine-tuning OlmoEarth in rslearn](https://github.com/allenai/rslearn/blob/master/docs/examples/FinetuneOlmoEarth.md)

These tutorials use all or a subset of the components of OlmoEarth:

- [olmoearth_pretrain](https://github.com/allenai/olmoearth_pretrain/), the OlmoEarth
  pre-trained model.
- [rslearn](https://github.com/allenai/rslearn/), our tool for obtaining satellite
  images and other geospatial data from online data sources, and for fine-tuning
  remote sensing foundation models.
- [olmoearth_run](https://pypi.org/project/olmoearth-runner/), our higher-level
  infrastructure that automates various steps on top of rslearn such as window creation
  and inference post-processing.

## Installation

We recommend installing using uv. See
[Installing uv](https://docs.astral.sh/uv/getting-started/installation/) for
instructions to install uv. Once uv is installed:

```
git clone https://github.com/allenai/olmoearth_projects.git
cd olmoearth_projects
uv sync
source .venv/bin/activate
```

## Applying Existing Models

There are three steps to applying the models in this repository:

1. Customize the prediction request geometry, which specifies the spatial and temporal
   extent to run the model on.
2. Execute the olmoearth_run steps to build an rslearn dataset for inference, and to
   apply the model on the dataset.
3. Collect and visualize the outputs.

### Customizing the Prediction Request Geometry

The configuration files for each project are stored under
`olmoearth_run_data/PROJECT_NAME/`. There are three configuration files:

- `dataset.json`: this is an rslearn dataset configuration file that specifies the
  types of satellite images that need to be downloaded to run the model, and how to
  obtain them. Most models rely on some combination of Sentinel-1 and Sentinel-2
  satellite images, and are configured to download those images from Microsoft
  Planetary Computer.
- `model.yaml`: this is an rslearn model configuration file that specifies the model
  architecture, fine-tuning hyperparameters, data loading steps, etc.
- `olmoearth_run.yaml`: this is an olmoearth_run configuration file that specifies how
  the prediction request geometry should be translated into rslearn windows, and how
  the inference outputs should be combined together.

Some projects also include an example `prediction_request_geometry.geojson`, but this
will need to be modified to specify your target region. The spatial extent is specified
with standard GeoJSON features; you can use [geojson.io](https://geojson.io/) to draw
polygons on a map and get the corresponding GeoJSON. The temporal extent is specified
using properties on each feature:

```jsonc
{
  "type": "FeatureCollection",
  "properties": {},
  "features": [
    {
      "type": "Feature",
      "geometry": {
        // ...
      },
      "properties": {
        "oe_start_time": "2024-01-01T00:00:00+00:00",
        "oe_end_time": "2024-02-01T00:00:00+00:00"
      },
    }
  ]
}
```

Here, the `oe_start_time` and `oe_end_time` indicate that the prediction for the
location of this feature should be based on satellite images around January 2024. The
per-model documentation details how these timestamps should be chosen. Some models like
forest loss driver classification provide project-specific tooling for generating the
prediction request geometry.

### Executing olmoearth_run

Consult the per-model documentation to download the associated fine-tuned model
checkpoint. For example:

```
mkdir ./checkpoints
wget https://huggingface.co/allenai/OlmoEarth-v1-FT-LFMC-Base/resolve/main/model.ckpt -O checkpoints/lfmc.ckpt
```

Set needed environment variables:

```
export NUM_WORKERS=32
export WANDB_PROJECT=lfmc
export WANDB_NAME=lfmc_inference_run
export WANDB_ENTITY=YOUR_WANDB_ENTITY
```

Then, execute olmoearth_run:

```
mkdir ./project_data
python -m olmoearth_projects.main olmoearth_run olmoearth_run --config_path $PWD/olmoearth_run_data/lfmc/ --checkpoint_path $PWD/checkpoints/lfmc.ckpt --scratch_path project_data/lfmc/
```

### Visualizing Outputs

The results directory (`project_data/lfmc/results/results_raster/` in the example)
should be populated with one or more GeoTIFFs. You can visualize this in GIS software
like qgis:

```
qgis project_data/lfmc/results/results_raster/*.tif
```

## Reproducing Fine-tuning for Existing Models

We have released model checkpoints for each of the fine-tuned models in this
repository, but you can reproduce the model by fine-tuning the pre-trained OlmoEarth
checkpoint on each task training dataset.

First, consult the per-model documentation above for the URL of the rslearn dataset tar
file, and download and extract it. For example, for the LFMC model:

```
wget https://huggingface.co/datasets/allenai/olmoearth_projects_lfmc/blob/main/dataset.tar
tar xvf dataset.tar
```

Set environment variables expected by the fine-tuning procedure (uses W&B)

```
export DATASET_PATH=/path/to/extracted/data/
export NUM_WORKERS=32
export TRAINER_DATA_PATH=./trainer_data
export PREDICTION_OUTPUT_LAYER=output
export WANDB_PROJECT=olmoearth_projects
export WANDB_NAME=my_training_run
export WANDB_ENTITY=...
```

Then run fine-tuning using the model configuration file in the `olmoearth_run_data`,
e.g.:

```
rslearn model fit --config olmoearth_run_data/lfmc/model.yaml
```

Losses and metrics should then be logged to your W&B. The checkpoint would be saved in
the TRAINER_DATA_PATH (e.g. `./trainer_data`); two checkpoints should be saved, the
latest checkpoint (`last.ckpt`) and the best checkpoint (`epoch=....ckpt`). You can use
the best checkpoint for the Applying Existing Models section in lieu of the checkpoint
that we proivde.

If training fails halfway, you can resume it from `last.ckpt`:

```
rslearn model fit --config olmoearth_run_data/lfmc/model.yaml --ckpt_path $TRAINER_DATA_PATH/last.ckpt
```

## License

This code is licensed under the [OlmoEarth Artifact License](LICENSE).

---


## File: docs/meaisínfhoghlaim/audio/Aligning Gaelic Script for QwenVL Finetuning.md

---
redirect: ../INDEX.md
---

This content is related to [Celtic Language AI](../celtic/CELTIC_LANGUAGES_AI_RESOURCES.md) and model serving documentation.

---


## File: docs/meaisínfhoghlaim/audio/LLM based TTS models.md

---
redirect: ../INDEX.md
---

This content is related to [Celtic Language AI](../celtic/CELTIC_LANGUAGES_AI_RESOURCES.md) and model serving documentation.

---


## File: docs/meaisínfhoghlaim/audio/Scraping Irish Audio Files.md

---
redirect: ../INDEX.md
---

This content is related to [Celtic Language AI](../celtic/CELTIC_LANGUAGES_AI_RESOURCES.md) and model serving documentation.

---


## File: docs/meaisínfhoghlaim/ml-models/celtic-ocr.md

# **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supervised Data Generation to Edge Inference**

## **1\. Introduction: The Intersection of Philology and Edge AI**

The digitization of cultural heritage and the operationalization of low-resource languages represent two of the most compelling frontiers in modern artificial intelligence. The specific challenge of developing a bilingual Handwritten Text Recognition (HTR) system for Irish and English—capable of running locally on iOS devices—necessitates a sophisticated convergence of computer vision, natural language processing, and hardware-aware engineering. Unlike printed text, which adheres to rigid typographic standards, handwriting exhibits high variance in stroke, slant, and spacing. In the context of the Irish language, this complexity is often compounded by the historical presence of the *Cló Gaelach* (Gaelic type) or distinct insular scripts in older manuscripts, as well as the code-switching nature of modern bilingual datasets.  
Traditional Optical Character Recognition (OCR) pipelines, historically dependent on Tesseract or similar LSTM-based engines, often fail to capture the nuanced semantic context required to disambiguate difficult handwriting. They operate primarily on visual pattern matching of character glyphs. The advent of Vision-Language Models (VLMs) fundamentally alters this landscape. By projecting visual features into the same embedding space as a Large Language Model (LLM), VLMs allow the transcription process to be guided by linguistic probability. The model does not merely "see" the shape of a letter; it "reads" the likelihood of a word appearing in an Irish sentence structure, essentially hallucinating the correct text constrained by the visual evidence.  
However, the deployment of such massive parameter models on resource-constrained edge devices like the iPhone presents a formidable engineering barrier. While cloud-based inference is trivial, the requirement for on-device inference—driven by privacy, latency, and offline accessibility—demands a rigorous analysis of model compression, memory management, and specialized runtime environments like Apple's CoreML and MLX. Furthermore, the efficacy of any machine learning model is strictly bounded by the quality of its training data. The user’s proposal to utilize **ColPali**, a retrieval-oriented VLM, to construct a training dataset from unaligned page transcriptions introduces a novel paradigm of "weakly-supervised" annotation.  
This report provides an exhaustive technical analysis of this end-to-end pipeline. It dissects the architectural compatibility of **Unsloth** for fine-tuning, evaluates the viability of **Apple's ml-fastvlm** versus the **MLX** framework for deployment, and rigorously examines the mathematical mechanisms of **ColPali** for generating ground-truth bounding boxes. The analysis indicates that while direct compatibility between Unsloth and ml-fastvlm is architecturally obstructed by divergent vision encoders, a robust pathway exists via the MLX ecosystem, enabling the deployment of state-of-the-art Qwen2-VL models on Apple Silicon with high fidelity.

## **2\. Theoretical Foundations of Weakly-Supervised Dataset Generation**

The primary bottleneck in training HTR systems for specific domains (such as Irish manuscripts) is the scarcity of line-level annotated data. Most available data exists as "weakly labeled" pairs: a full image of a page and a full transcription of that page, without the coordinate geometry linking specific text lines to specific pixel regions. Manually drawing bounding boxes is prohibitively expensive. The proposed utilization of **ColPali** to automate this alignment exploits the model's unique architecture to bridge the gap between retrieval and localization.

### **2.1 The ColPali Architecture: Contextualized Late Interaction**

To understand how ColPali can be repurposed for data generation, one must first analyze its retrieval mechanism. Traditional dense retrieval systems (Bi-Encoders) compress an entire document image into a single vector embedding. While efficient for search, this compression results in a massive loss of spatial fidelity. ColPali, built upon the **PaliGemma** VLM, adopts the **ColBERT** (Contextualized Late Interaction over BERT) paradigm, applying it to the visual domain.1  
In ColPali, an image is not encoded into one vector, but into a grid of vectors. The Vision Transformer (ViT) backbone—typically SigLIP-So400m—processes the image at a resolution (e.g., $448 \\times 448$) and outputs a feature map. This map is projected into a sequence of patch embeddings. For a standard input, ColPali generates $32 \\times 32 \= 1024$ visual tokens, where each token represents a specific rectangular region of the image. Crucially, these visual tokens are projected into the same latent space as the text tokens of the language model.3  
The retrieval score $S(q, d)$ between a text query $q$ and a document image $d$ is calculated using the MaxSim operator:

$$S(q, d) \= \\sum\_{i=1}^{|q|} \\max\_{j=1}^{|d|} (E\_{q\_i} \\cdot E\_{d\_j})$$  
Here, $E\_{q\_i}$ is the embedding of the $i$-th token of the text query, and $E\_{d\_j}$ is the embedding of the $j$-th visual patch. This formula dictates that for every word in the query, the model searches for the single most similar patch in the image, and the total score is the sum of these maximum similarities.

### **2.2 Algorithmic Transformation: Attention-to-Geometry**

The user's insight—to use ColPali for indexing and matching to avoid alignment problems—can be operationalized into a rigorous segmentation algorithm. Since the MaxSim operator explicitly links text tokens to image patches, the internal state of the model during this calculation contains the localization data required to build the HTR dataset. By treating a single line of the transcription as the "query" and the full page as the "document," we can extract the **Attention Map** (or Similarity Map) to spatially locate the handwriting.5  
The process of generating the dataset follows a multi-stage pipeline:

1. **Indexing (Forward Pass):** The full page of the Irish manuscript is passed through the ColPali vision encoder. This results in a tensor of shape $$, representing the 1024 patches, each with a 128-dimensional embedding.  
2. **Querying:** A specific line from the transcription (e.g., *"Tá sé páirteach..."*) is tokenized and embedded by the text encoder.  
3. **Similarity Matrix Computation:** A dot product is computed between every text token embedding and every image patch embedding. This yields a matrix of shape $\[N\_{text}, 1024\]$.  
4. **Heatmap Aggregation:** To visualize where the whole line is located, one aggregates this matrix across the text dimension. A common approach is to sum the similarity scores for each patch, resulting in a $$ vector. This vector is reshaped back into a $32 \\times 32$ grid.7  
5. **Upscaling and Thresholding:** The $32 \\times 32$ grid is low-resolution. To derive a usable bounding box:  
   * The grid is bi-linearly interpolated up to the original image resolution (e.g., $2000 \\times 3000$).  
   * A thresholding algorithm (such as **Otsu’s Binarization**) is applied to the heatmap to separate the "active" regions (the text) from the background.9  
   * Contour detection algorithms (like those in OpenCV) identify the bounding rectangle of the largest connected component.11

This algorithm effectively converts the "soft" attention of the VLM into "hard" coordinates for cropping.

### **2.3 Resolving Alignment Challenges in Bilingual Text**

Irish manuscripts often contain mixed scripts or bilingual marginalia. A traditional OCR engine might struggle to differentiate between the main Irish text and English annotations, or might fail to recognize the *Cló Gaelach* entirely. ColPali offers a distinct advantage here: **Semantic Grounding**.  
Because ColPali utilizes a Language Model (Gemma-2B/PaliGemma), it understands the semantic content of the query. If the query is an Irish sentence, the model will attend to the visual features that correspond to those specific words, even if the handwriting is stylized. This is distinct from layout analysis models (like YOLO trained on generic documents) which only look for "text-like" blobs. ColPali aligns the *meaning* of the text to the *pixels*, making it robust against layout noise or interlineations common in handwritten datasets.12  
However, the analysis indicates a critical limitation: **Granularity**. The $32 \\times 32$ patch grid implies that each patch covers a significant area (roughly $60 \\times 60$ pixels on a standard scan). While this is sufficient for identifying the general region of a line, it is not pixel-perfect. The bounding boxes generated via this weakly-supervised method will be "loose." For finetuning Qwen2-VL, this is actually acceptable, as VLMs are generally robust to some background noise around the text, provided the text itself is fully contained.14

## **3\. Deep Dive: The Qwen2-VL Architecture and Unsloth Optimization**

With the dataset of image-text pairs generated via ColPali, the focus shifts to the recognition model. The user has specifically identified **Qwen2-VL** and the **Unsloth** framework. This choice is technically sound; Qwen2-VL represents the current state-of-the-art in open-weights VLMs, outperforming larger proprietary models in OCR benchmarks like DocVQA and OCRBench.15

### **3.1 Qwen2-VL: Naive Dynamic Resolution and M-ROPE**

The suitability of Qwen2-VL for HTR lies in its handling of visual inputs. Traditional VLMs (like the original LLaVA) resize all images to a fixed square (e.g., $336 \\times 336$). For handwriting, which often consists of long, narrow lines or vertically oriented marginalia, this resizing introduces disastrous distortion or downsampling artifacts that obliterate the fine details of the stroke.  
Qwen2-VL introduces **Naive Dynamic Resolution**. It does not enforce a fixed input size. Instead, it processes the image at its native resolution (constrained by a min\_pixels and max\_pixels hyperparameter range). The image is divided into patches of $14 \\times 14$. A line of handwriting that is $1000 \\times 50$ pixels will be tokenized into a sequence of patches that preserves this aspect ratio.17  
To manage this variable sequence length, Qwen2-VL employs **M-ROPE (Multimodal Rotary Positional Embedding)**. Standard ROPE encodes position in a 1D sequence. M-ROPE decomposes the positional embedding into three components: temporal (for video), height, and width. This allows the LLM to understand the 2D spatial relationships of the visual tokens regardless of the grid shape. This is critical for HTR, where the model must track the horizontal progression of cursive script across the image.18

### **3.2 Unsloth: The Mathematics of Efficiency**

Training a VLM like Qwen2-VL (even the 2B version) can be VRAM-intensive due to the long sequence lengths generated by high-resolution images. **Unsloth** provides the necessary optimization infrastructure to make this feasible on consumer-grade or mid-tier hardware.17  
Unsloth optimizes the fine-tuning process not through quantization (though it supports it) but through the manual derivation of backpropagation gradients. In standard PyTorch, the autograd engine constructs a graph that stores intermediate activations for every operation. Unsloth replaces standard Transformer modules (like MLP and Self-Attention) with custom implementations where the backward pass is mathematically derived and implemented in **OpenAI Triton** kernels.19  
**Key Optimizations for Qwen2-VL:**

* **Gradient Checkpointing:** Unsloth manages activation recomputation more efficiently, reducing VRAM usage by up to 60%. This allows for larger batch sizes or higher resolution inputs (higher max\_pixels), which is directly correlated with HTR accuracy.  
* **LoRA Integration:** Unsloth natively integrates Low-Rank Adaptation (LoRA). For HTR, it is recommended to target not just the attention layers (q\_proj, v\_proj) but also the MLP layers (gate\_proj, up\_proj, down\_proj). This "all-linear" targeting has been shown to improve the model's ability to learn new syntactic patterns, such as the specific grammar of Irish.20  
* **Bfloat16 Support:** Unsloth leverages bfloat16 precision, which prevents the numerical instability often seen in mixed-precision training of VLMs, particularly with the large gradient norms associated with visual encoders.

### **3.3 Fine-Tuning Strategy for Irish HTR**

To finetune Qwen2-VL via Unsloth for this specific application, the following configuration is optimal:

* **Model:** unsloth/Qwen2-VL-2B-Instruct-bnb-4bit. The 2B model is selected to fit within the iOS memory budget. The 4-bit quantization (bnb-4bit) enables training on GPUs with as little as 12GB VRAM.20  
* **Vision Tower:** Typically frozen. However, if the Irish handwriting is stylistically divergent from the pre-training data (which is mostly web data and standard OCR datasets), one might consider applying LoRA adapters to the vision tower as well. Unsloth allows setting target\_modules to include vision encoder layers, though this increases VRAM usage.22  
* **Data Formatting:** The dataset must be converted to the conversational format:  
  JSON  
  {  
    "messages":  
      },  
      {  
        "role": "assistant",   
        "content": \[{"type": "text", "text": "Lá breá grianmhar a bhí ann."}\]  
      }  
    \]  
  }

  This format aligns the visual perception with the instruction-following capability of the model.20

## **4\. Architectural Divergence: ml-fastvlm vs. MLX**

A central component of the user's query is the investigation of Apple's ml-fastvlm repository. The analysis reveals a critical architectural schism that impacts the deployment strategy.

### **4.1 Deconstructing ml-fastvlm and FastViT**

ml-fastvlm is the official implementation of the **FastVLM** paper (CVPR 2025). Its primary goal is to solve the latency bottleneck of Vision Transformers on edge devices. Standard ViTs (like the SigLIP encoder in Qwen2-VL) use global self-attention, which scales quadratically with the number of tokens ($O(N^2)$). On mobile chips, this is computationally expensive.23  
FastVLM replaces the standard Transformer vision encoder with **FastViT-HD**. FastViT is a hybrid architecture that uses **structural reparameterization**. During training, it uses complex blocks (RepMixer) that capture diverse features. During inference, these blocks collapse into a single $3 \\times 3$ convolution. This creates a model that is extremely fast on the Apple Neural Engine (ANE), which is optimized for convolutions.25  
The Incompatibility:  
The weights of the Qwen2-VL model (fine-tuned via Unsloth) correspond to a SigLIP-like Vision Transformer. The ml-fastvlm codebase expects a FastViT convolutional encoder. These are fundamentally different neural architectures. One cannot simply "export" the Unsloth Qwen2-VL weights into ml-fastvlm. To use ml-fastvlm, the user would need to:

1. Initialize a FastVLM architecture (FastViT encoder \+ Qwen2 LLM).  
2. Perform **Pre-training (Stage 1 & 2\)** to align the FastViT encoder with the LLM, requiring massive image-text datasets (e.g., LLaVA-665k).  
3. Perform **Supervised Fine-Tuning** on the Irish dataset.

This process is computationally expensive and redundant given the existence of Qwen2-VL. Therefore, ml-fastvlm is **not recommended** for this specific pipeline unless extreme latency optimization (sub-50ms) is the primary constraint over development time.25

### **4.2 The Solution: MLX and mlx-vlm**

**MLX** is Apple's array framework designed specifically for Apple Silicon (M-series and A-series chips). It provides a unified memory model, allowing the CPU and GPU to access the same data without copying, which is crucial for memory-heavy VLMs.27  
The **mlx-vlm** library (and the associated mlx-swift-examples) provides native support for the standard Qwen2-VL architecture. This includes the implementation of the specific ViT encoder, the M-ROPE positional embeddings, and the dynamic resolution preprocessing logic.28  
**Advantages of MLX for iOS Deployment:**

* **Architecture Parity:** It supports the exact model architecture trained by Unsloth.  
* **Conversion Pipeline:** There is a direct, supported path to convert Hugging Face weights (safetensors) to MLX format (weights.npz).  
* **Quantization:** MLX offers 4-bit and 8-bit quantization that is highly optimized for the A-series GPU. A 2B parameter Qwen2-VL model quantized to 4-bits requires approximately 1.2GB \- 1.5GB of RAM.30 This fits comfortably within the "wired memory" limits of modern iPhones (which typically have 6GB or 8GB of RAM), leaving sufficient headroom for the iOS operating system and the application's UI.

### **4.3 CoreML vs. MLX**

The user also inquired about CoreML. While coremltools is the standard for iOS ML, it struggles with the dynamism of Large Language Models and VLMs.

* **Static Graph Requirement:** CoreML traditionally prefers static computation graphs. Qwen2-VL's dynamic resolution (where the number of visual tokens changes per image) and the autoregressive nature of text generation are difficult to express efficiently in CoreML without padding to fixed sizes, which wastes computation.32  
* **ANE Limitations:** The Apple Neural Engine (ANE) lacks support for certain operations required by modern Transformers (like specific types of casting or complex attention masks), forcing fallback to the GPU or CPU. MLX, by contrast, is designed to execute dynamic graphs efficiently on the GPU/CPU immediately.27

**Verdict:** For LLMs and VLMs on iOS today, MLX is the superior choice over pure CoreML.

## **5\. Deployment Implementation Roadmap**

The following roadmap outlines the step-by-step execution of the project, integrating the missing details identified in the analysis.

### **Phase 1: Data Curation (Python/ColPali)**

1. **Ingest:** Load the scanned Irish manuscript pages and their corresponding transcriptions.  
2. **Index:** Use the colpali-engine to encode all page images into patch embeddings.  
3. **Localize:**  
   * Iterate through each line of the transcription.  
   * Compute the MaxSim attention map between the line text and the page image.  
   * Apply **Gaussian smoothing** to the raw attention map to reduce noise.  
   * Apply **Otsu's thresholding** to binarize the map.  
   * Extract the bounding box of the active region.  
   * *Refinement:* Expand the bounding box by 10-15% (padding) to ensure no ascenders/descenders are clipped.  
4. **Crop & Save:** Generate the training pairs: {"image": "crop\_001.jpg", "text": "Agus ansin dúirt sé..."}.

### **Phase 2: Fine-Tuning (Python/Unsloth)**

1. **Setup:** Initialize FastVisionModel from Unsloth with load\_in\_4bit=True.  
2. **Configure LoRA:**  
   * r (rank): 16 or 32\.  
   * target\_modules: \["q\_proj", "k\_proj", "v\_proj", "o\_proj", "gate\_proj", "up\_proj", "down\_proj"\].  
   * *Crucial:* Ensure use\_gradient\_checkpointing="unsloth" is enabled to save VRAM.  
3. **Train:** Run the SFTTrainer (Supervised Fine-Tuning Trainer) on the generated dataset. Monitor the validation loss on a held-out set of Irish handwriting to prevent overfitting to the specific scribal hand.20  
4. **Fuse:** Once training is complete, fuse the LoRA adapters back into the base model using model.save\_pretrained\_merged(...). This is essential because the mobile inference engine requires a single static model file, not a base+adapter configuration.20

### **Phase 3: Conversion (Python/MLX)**

1. **Install:** pip install mlx-vlm.  
2. **Convert:** Use the conversion script to transform the fused Hugging Face model to MLX format.  
   Bash  
   python \-m mlx\_vlm.convert \--hf-path./qwen2-vl-irish-fused \--quantize \--q-bits 4 \--mlx-path./qwen2-vl-irish-4bit

   This command performs the quantization (reducing weights to 4-bit integers) and saves the weights.npz and config.json.33

### **Phase 4: iOS Development (Swift)**

1. **Dependencies:** Add the mlx-swift and mlx-swift-examples packages to the Xcode project.  
2. **Model Loading:** Use the VLMModelFactory to load the model from the local bundle (or download it from Hugging Face).  
3. **Inference Logic:**  
   * Preprocess the camera input or selected image. *Note: Ensure the Swift preprocessor matches the min\_pixels / max\_pixels used during Unsloth training.*  
   * Pass the image and the prompt (e.g., "Transcribe this text") to the generate() function.  
   * Handle the output stream to display text in real-time.  
4. **Performance Tuning:** Monitoring the "Wired Memory" gauge in Xcode Instruments is vital. If memory pressure is too high, reduce the KV-cache quantization to 4-bit or limit the maximum sequence length (context window) since HTR tasks typically require short outputs.34

## **6\. Comparative Analysis: Model Specifications**

The following tables summarize the critical decision points in the architecture.  
**Table 1: Inference Engine Comparison for iOS VLMs**

| Feature | Apple ml-fastvlm | MLX (mlx-vlm) | CoreML |
| :---- | :---- | :---- | :---- |
| **Vision Encoder** | FastViT (Hybrid ConvNet) | SigLIP/ViT (Transformer) | Various (Static) |
| **Qwen2-VL Support** | **No** (Requires retraining) | **Yes** (Native) | **Partial** (Complex conversion) |
| **Dynamic Resolution** | Limited | **Full** (Naive Dynamic) | Difficult (Requires padding) |
| **Memory Efficiency** | High (ANE Optimized) | High (Unified Memory) | Moderate |
| **Dev Effort** | High (Research Code) | Low (Python-to-Swift) | Very High |
| **Best Use Case** | Ultra-low latency, fixed tasks | Generative AI, RAG, HTR | Classical CV, Classification |

**Table 2: Estimated Resource Footprint on iOS (iPhone 15 Pro)**

| Model Variant | Quantization | RAM Usage (Est.) | Inference Speed (Text) | Suitability |
| :---- | :---- | :---- | :---- | :---- |
| Qwen2-VL-2B | FP16 | \~4.5 GB | Slow | **Low** (OOM Risk) |
| Qwen2-VL-2B | 4-bit | **\~1.2 GB** | **\~40 tok/sec** | **High** (Production Ready) |
| Qwen2-VL-7B | 4-bit | \~4.0 GB | \~15 tok/sec | **Moderate** (Pro models only) |

**Table 3: Unsloth Training Metrics (Qwen2-VL-2B)**

| Metric | Standard Hugging Face | Unsloth | Improvement |
| :---- | :---- | :---- | :---- |
| VRAM Usage (2B) | \~14 GB | **\~6 GB** | \-58% |
| Training Speed | 1x | **1.8x \- 2x** | \+80% |
| Batch Size | Low | High | Stability |

## **7\. Future Directions and Bilingual Considerations**

While the primary goal is HTR, the bilingual nature of the data (Irish/English) presents opportunities for "Agentic HTR." Instead of simple transcription, the app could leverage the Qwen2-VL language capabilities to perform tasks like:

* **Translation:** "Transcribe and translate this Irish text to English."  
* **Summarization:** "Summarize the content of this handwritten note."  
* **Entity Extraction:** "List all names and dates found in this manuscript."

These capabilities are inherent to the VLM architecture and are preserved when deploying via MLX (unlike specialized OCR models which only output text). To ensure the model does not "forget" English while learning Irish handwriting, the training dataset should be a mix (e.g., 70% Irish crops, 30% English/Generic crops) to act as regularization.

## **8\. Conclusion**

The development of a bilingual HTR app for Irish on iOS is not only possible but feasible with high performance using the proposed pipeline. By rejecting the architectural rigidity of ml-fastvlm in favor of the **MLX** ecosystem, the developer gains access to the cutting-edge **Qwen2-VL** architecture. Simultaneously, the innovative application of **ColPali** as a weak supervisor solves the chronic lack of annotated data for the Irish language. This integration of retrieval-augmented data generation, efficiency-optimized training via **Unsloth**, and hardware-accelerated inference via **MLX** constitutes a robust, modern solution for mobile Document AI.

#### **Works cited**

1. ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2407.01449v5](https://arxiv.org/html/2407.01449v5)  
2. \[2407.01449\] ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2407.01449](https://arxiv.org/abs/2407.01449)  
3. Advanced Retrieval with ColPali & Qdrant Vector Database, accessed December 15, 2025, [https://qdrant.tech/blog/qdrant-colpali/](https://qdrant.tech/blog/qdrant-colpali/)  
4. Scaling ColPali to billions of PDFs with Vespa, accessed December 15, 2025, [https://blog.vespa.ai/scaling-colpali-to-billions/](https://blog.vespa.ai/scaling-colpali-to-billions/)  
5. illuin-tech/colpali: The code used to train and run inference ... \- GitHub, accessed December 15, 2025, [https://github.com/illuin-tech/colpali](https://github.com/illuin-tech/colpali)  
6. Spatially-Grounded Document Retrieval via Patch-to-Region Relevance Propagation \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2512.02660v1](https://arxiv.org/html/2512.02660v1)  
7. ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2407.01449v2](https://arxiv.org/html/2407.01449v2)  
8. ColPali: Enhancing Financial Report Analysis with Multimodal RAG and Gemini, accessed December 15, 2025, [https://learnopencv.com/multimodal-rag-with-colpali/](https://learnopencv.com/multimodal-rag-with-colpali/)  
9. Bounding box extraction from attention maps. \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/figure/Bounding-box-extraction-from-attention-maps\_fig2\_386577739](https://www.researchgate.net/figure/Bounding-box-extraction-from-attention-maps_fig2_386577739)  
10. Image Thresholding \- OpenCV Documentation, accessed December 15, 2025, [https://docs.opencv.org/4.x/d7/d4d/tutorial\_py\_thresholding.html](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)  
11. How to get the feature bounded by the detected box in object detection? \#6311 \- GitHub, accessed December 15, 2025, [https://github.com/ultralytics/ultralytics/issues/6311](https://github.com/ultralytics/ultralytics/issues/6311)  
12. Transforming Product Discovery and Interpretation Using Vision–Language Models \- MDPI, accessed December 15, 2025, [https://www.mdpi.com/0718-1876/20/3/191](https://www.mdpi.com/0718-1876/20/3/191)  
13. Introduction to OCR Free Vision RAG using Colpali For Complex Documents, accessed December 15, 2025, [https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introduction-to-ocr-free-vision-rag-using-colpali-for-complex-documents/4276357](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introduction-to-ocr-free-vision-rag-using-colpali-for-complex-documents/4276357)  
14. Spatially-Grounded Document Retrieval via Patch-to-Region Relevance Propagation, accessed December 15, 2025, [https://www.researchgate.net/publication/398269244\_Spatially-Grounded\_Document\_Retrieval\_via\_Patch-to-Region\_Relevance\_Propagation](https://www.researchgate.net/publication/398269244_Spatially-Grounded_Document_Retrieval_via_Patch-to-Region_Relevance_Propagation)  
15. Qwen2-VL | OpenLM.ai, accessed December 15, 2025, [https://openlm.ai/qwen2-vl/](https://openlm.ai/qwen2-vl/)  
16. Qwen/Qwen2-VL-2B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct)  
17. unsloth/Qwen2-VL-2B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct](https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct)  
18. unsloth/Qwen2-VL-2B-Instruct-bnb-4bit \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct-bnb-4bit](https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct-bnb-4bit)  
19. Make LLM Fine-tuning 2x faster with Unsloth and TRL \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/blog/unsloth-trl](https://huggingface.co/blog/unsloth-trl)  
20. Qwen2 Vision Finetuning Unsloth \- Kaggle, accessed December 15, 2025, [https://www.kaggle.com/code/danielhanchen/qwen2-vision-finetuning-unsloth-kaggle](https://www.kaggle.com/code/danielhanchen/qwen2-vision-finetuning-unsloth-kaggle)  
21. Fine-tune Llama3 with function calling via MLX-LM | by Anchen \- Medium, accessed December 15, 2025, [https://medium.com/@anchen.li/fine-tune-llama3-with-function-calling-via-mlx-lm-5ebbee41558f](https://medium.com/@anchen.li/fine-tune-llama3-with-function-calling-via-mlx-lm-5ebbee41558f)  
22. Vision Fine-tuning | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/basics/vision-fine-tuning](https://docs.unsloth.ai/basics/vision-fine-tuning)  
23. apple/ml-fastvlm: This repository contains the official ... \- GitHub, accessed December 15, 2025, [https://github.com/apple/ml-fastvlm](https://github.com/apple/ml-fastvlm)  
24. FastVLM: Efficient Vision Encoding for Vision Language Models : r/apple \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/apple/comments/1m7gb3j/fastvlm\_efficient\_vision\_encoding\_for\_vision/](https://www.reddit.com/r/apple/comments/1m7gb3j/fastvlm_efficient_vision_encoding_for_vision/)  
25. Fastvlm: Efficient Vision Encoding For Vision Language Models | PDF \- Scribd, accessed December 15, 2025, [https://www.scribd.com/document/863828552/2412-13303v2](https://www.scribd.com/document/863828552/2412-13303v2)  
26. FastVLM: Efficient Vision Encoding for Vision Language Models \- CVF Open Access, accessed December 15, 2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu\_FastVLM\_Efficient\_Vision\_Encoding\_for\_Vision\_Language\_Models\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.pdf)  
27. MLX Swift: Run LLMs and VLMs in iOS Apps \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/swift/comments/1j4v70y/mlx\_swift\_run\_llms\_and\_vlms\_in\_ios\_apps/](https://www.reddit.com/r/swift/comments/1j4v70y/mlx_swift_run_llms_and_vlms_in_ios_apps/)  
28. Qwen2-VL Best Practice — swift 2.6.1 documentation \- Read the Docs, accessed December 15, 2025, [https://swift2x-en.readthedocs.io/en/latest/Multi-Modal/qwen2-vl-best-practice.html](https://swift2x-en.readthedocs.io/en/latest/Multi-Modal/qwen2-vl-best-practice.html)  
29. mlx-community/Qwen2-VL-2B-4bit \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/mlx-community/Qwen2-VL-2B-4bit](https://huggingface.co/mlx-community/Qwen2-VL-2B-4bit)  
30. README.md · riddhimanrana/fastvlm-0.5b-captions at main \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/riddhimanrana/fastvlm-0.5b-captions/blob/main/README.md](https://huggingface.co/riddhimanrana/fastvlm-0.5b-captions/blob/main/README.md)  
31. Speed Benchmark \- Qwen, accessed December 15, 2025, [https://qwen.readthedocs.io/en/v2.0/benchmark/speed\_benchmark.html](https://qwen.readthedocs.io/en/v2.0/benchmark/speed_benchmark.html)  
32. Load and Convert Model Workflow — Guide to Core ML Tools \- Apple, accessed December 15, 2025, [https://apple.github.io/coremltools/docs-guides/source/load-and-convert-model.html](https://apple.github.io/coremltools/docs-guides/source/load-and-convert-model.html)  
33. mlx-community/Jan-v2-VL-high-8bit-mlx \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/mlx-community/Jan-v2-VL-high-8bit-mlx](https://huggingface.co/mlx-community/Jan-v2-VL-high-8bit-mlx)  
34. llm-tool \- ml-explore/mlx-swift-examples \- GitHub, accessed December 15, 2025, [https://github.com/ml-explore/mlx-swift-examples/blob/main/Tools/llm-tool/README.md](https://github.com/ml-explore/mlx-swift-examples/blob/main/Tools/llm-tool/README.md)
---


## File: docs/meaisínfhoghlaim/ml-models/federated-marketplace.md

# **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device Vision Intelligence**

## **Executive Summary**

The digital economy stands at a precipice where the centralization of artificial intelligence conflicts with the imperative for data privacy and the distributed nature of data generation. A new architectural paradigm, synthesized from the principles of "Crypteolas" (Crypto-Federated Learning), is emerging to resolve this tension. This report presents a comprehensive technical and economic blueprint for a decentralized marketplace that leverages the computational power of consumer iOS devices to perform advanced computer vision tasks—specifically Optical Character Recognition (OCR), Handwritten Text Recognition (HTR), and Vision-Language Model (VLM) inference—while maintaining absolute data sovereignty.  
The proposed architecture envisions a network where iPhone users utilize their devices to scan, transcribe, and translate private documents. Instead of uploading this sensitive data to a central cloud for model training, the device utilizes Apple’s MLX framework and the Apple Vision API to perform local fine-tuning of VLM adapters (e.g., LoRA). These local intelligence updates are then commoditized. External agents—autonomous software entities representing researchers, corporations, or other algorithms—utilize the x402 "Payment Required" protocol to purchase access to this intelligence. They pay for ephemeral API access to the device's vision capabilities or fund federated learning rounds to aggregate local insights into a global model using the Flower framework and PySyft for privacy preservation.  
This report argues that the convergence of Apple Silicon’s unified memory architecture, the agentic interoperability of the x402 protocol, and the secure aggregation capabilities of modern federated learning frameworks creates a viable foundation for a "pay-for-compute" economy. This system transforms the iPhone from a passive consumption device into an active, revenue-generating node in a global, decentralized intelligence grid, fundamentally realigning the incentives of the AI economy toward privacy and user ownership.

## ---

**1\. The Crypteolas Paradigm: Convergence of Crypto and Federated Learning**

The term "Crypteolas" refers to the specific intersection of cryptographic incentives and federated learning architectures, a domain often described in academic literature as EdgeFL-Crypto. This paradigm shifts the focus from centralized data lakes to decentralized data grids, where the model travels to the data, and trust is established not by authority, but by cryptographic proof and economic stake.

### **1.1 Theoretical Foundations: From EdgeFL to Crypteolas**

Recent research into EdgeFL-Crypto architectures 1 highlights the efficacy of "Federated Split Learning" in high-frequency, low-latency environments such as cryptocurrency volatility prediction. This research demonstrates that federated learning can provide significant performance boosts—up to a 7.7% reduction in Root Mean Square Error (RMSE)—by leveraging distributed intelligence rather than centralized training. The "Crypteolas" concept extends this by embedding an economic layer directly into the learning protocol.  
In a traditional Federated Learning (FL) setup, participation is often altruistic or coerced (e.g., part of a terms-of-service agreement). In the Crypteolas model, participation is transactional. The iOS device acts as a sovereign entity that "sells" gradient updates. This aligns with the findings in blockchain-based federated learning literature, which posits that immutable audit trails and smart contract-based registries are essential for accountability and fairness in distributed systems.2 By logging model provenance and training participation on a blockchain, the system creates a "Proof of Training" that allows buyers to verify the utility of the contributions they are purchasing without inspecting the raw, private data.3

### **1.2 The Marketplace of Private Intelligence**

The core innovation of this proposal is the commoditization of "private intelligence." Traditional data marketplaces sell datasets, which requires data to change hands, violating privacy. The Crypteolas marketplace sells *insights* derived from data.

* **The Asset:** The asset is not the scanned image of a medical receipt or a handwritten diary entry; it is the *gradient update* generated by a VLM fine-tuned on that document.  
* **The Mechanism:** The mechanism is "Federated Sharing." Buyers pay to aggregate these gradients. The global model improves its ability to read handwriting or translate technical documents without ever "seeing" the source documents.  
* **The Agentic Economy:** The participants in this market are largely autonomous agents. An AI agent representing a logistics company might autonomously detect a drop in OCR accuracy for waybills and automatically dispatch x402 payments to thousands of iPhones to fine-tune a model on recent waybill formats.4

This architecture mirrors the ambitions of platforms like FLock.io, which use blockchain for model coordination and slashing mechanisms to penalize malicious actors 5, and Felt Labs, which facilitates training on distributed data.6 However, the proposed system is distinct in its reliance on high-performance mobile edge computing (Apple Silicon) as the primary compute substrate.

### **1.3 Why iOS? The Hardware Advantage**

The feasibility of this marketplace rests on the capabilities of the edge device. The iPhone, particularly models with A16 Bionic chips and later, possesses a unique architecture suitable for this task:

* **Unified Memory Architecture (UMA):** Unlike traditional architectures where data must be copied between CPU and GPU memory, Apple Silicon allows both processors to access the same memory pool. This is critical for running memory-intensive VLMs and performing training tasks without the latency of data transfer.7  
* **Apple Neural Engine (ANE):** A dedicated NPU optimized for matrix multiplication, essential for efficient inference of vision models and OCR tasks via the Vision framework.8  
* **Privacy Hardware:** The Secure Enclave provides a hardware root of trust for generating the cryptographic signatures required for x402 payments and authenticating the device's contribution to the federated network.

## ---

**2\. The On-Device Intelligence Stack: Vision, OCR, and VLMs**

To participate in the Crypteolas marketplace, the iOS device must perform complex perception and reasoning tasks. This requires a sophisticated stack merging native Apple frameworks with open-source LLM technologies.

### **2.1 The Vision Pipeline: OCR and HTR**

The foundational layer of the data processing pipeline is the extraction of raw text from images. The system utilizes Apple's Vision framework, specifically the VNRecognizeTextRequest API.

* **Optical Character Recognition (OCR):** For printed text, Apple's Vision framework offers state-of-the-art performance, running entirely on-device with minimal energy consumption. It provides bounding box information, allowing the system to map text back to specific regions of the image.  
* **Handwritten Text Recognition (HTR):** The user query specifically emphasizes HTR. The Vision framework supports HTR natively, but its accuracy can vary depending on style and legibility. In this architecture, the Vision framework serves as the "Proposer." It generates an initial transcription of the handwriting.  
* **The VLM Refinement Step:** This is where the value add occurs. A locally running Vision-Language Model (VLM), such as a quantized version of Qwen-VL or Llama-3-Vision, receives both the image embedding and the raw text proposed by the Vision framework. The VLM is prompted to "Correct the following transcription based on the image." This leverages the VLM's semantic understanding to correct HTR errors that a pure pattern-matching OCR system might miss (e.g., correcting "barn" to "born" based on the sentence context "I was born in 1990").

### **2.2 Running VLMs on iOS: GGUF and MLX**

The user explicitly mentions using **GGUF** models on iPhone. GGUF is a file format designed for fast inference of Large Language Models on CPUs and GPUs, popularized by llama.cpp.9

#### **2.2.1 The GGUF Pathway via llama.cpp**

* **Implementation:** Using llama.cpp libraries compiled for iOS, the application can load GGUF models ranging from 2B to 7B parameters. Benchmarks on A17 Pro chips show that 4-bit quantized models can achieve inference speeds of 20-30 tokens per second, which is sufficient for real-time interaction.9  
* **Role:** GGUF is ideal for the *inference* side of the marketplace. When a buyer pays for "API Access" to the device to scan a document, the app uses the efficient GGUF runtime to process the request.

#### **2.2.2 The MLX Pathway for Training**

While GGUF/llama.cpp is excellent for inference, it is not primarily designed for *training* or fine-tuning on Apple Silicon. For the "Federated Learning" aspect of the user's request, the architecture must leverage **MLX**, Apple's array framework designed for machine learning research on Apple Silicon.7

* **MLX Swift:** MLX provides a native Swift API that allows developers to build and train models directly in iOS apps without bridging to Python. This is crucial for performance and integration with other iOS subsystems.11  
* **Fine-Tuning:** The application uses MLX to load a VLM (which can be converted from GGUF or PyTorch formats into MLX's native format). It then performs **Low-Rank Adaptation (LoRA)** fine-tuning.  
* **The Workflow:**  
  1. User scans a handwritten note.  
  2. Apple Vision suggests text.  
  3. User manually corrects the text (creating Ground Truth).  
  4. The app uses MLX to run a training step (backpropagation), updating the LoRA adapter weights to minimize the loss between the model's prediction and the user's correction.  
  5. This "fine-tuned adapter" becomes the product sold in the federated marketplace.

### **2.3 Optimization via FastVLM**

To ensure this process does not render the phone unusable, the architecture should incorporate **FastVLM** principles.13 FastVLM is a research architecture that optimizes the vision encoding step, reducing the Time-To-First-Token (TTFT). Since the vision encoder is often the bottleneck at high resolutions, implementing FastVLM within the MLX environment allows the device to process high-resolution document scans efficiently, balancing the trade-off between accuracy (requiring high res) and latency/thermal throttling.

### **2.4 Translation and Semantic Understanding**

The VLM provides capabilities beyond simple transcription.

* **Translation:** The VLM can be prompted to "Transcribe and Translate this French menu into English JSON." This utilizes the model's pre-trained multilingual capabilities.  
* **Structuring:** The model can convert unstructured OCR data (a jumble of text) into structured formats (JSON with keys like "Date," "Total," "Merchant"), adding significant value for buyers looking for structured data streams.

## ---

**3\. The Economic Layer: Agentic Payments via x402**

The "marketplace" is defined by the exchange of value. The **x402 protocol** (Payment Required) serves as the standard for this exchange, enabling "Agentic Payments"—transactions initiated and settled by software agents without human intervention.4

### **3.1 The x402 Protocol Architecture**

x402 revives the long-dormant HTTP 402 status code to create a native payment layer for the web.

* **The Handshake:**  
  1. **Request:** A Buyer Agent (e.g., a server aggregating medical data) makes an HTTP request to the iOS device's endpoint: POST /api/federated/contribute.  
  2. **Challenge:** The iOS device (Server) checks for a valid payment token. If absent, it returns 402 Payment Required. The response body contains payment metadata: the required amount (e.g., 0.05 USDC), the chain (Base), and the recipient address.4  
  3. **Payment:** The Buyer Agent parses this metadata. Using its own embedded wallet, it signs a transaction transferring the funds. Crucially, x402 often leverages **EIP-3009** (Transfer with Authorization) or similar gasless signatures, allowing the Buyer to prove payment capabilities without waiting for full block confirmation for every micro-transaction.15  
  4. **Fulfillment:** The Buyer resends the request with the signed payment payload in the X-Payment or Authorization header. The iOS device verifies the signature (using a lightweight client or a trusted Facilitator) and accepts the federated contribution.16

### **3.2 x402 vs. L402: The Strategic Choice**

The user request mentions x402, but research snippets also highlight L402 (built on Bitcoin Lightning).17

* **L402 (Lightning):** Uses Macaroons for authentication and Lightning invoices for settlement. It is excellent for high-frequency, sub-cent privacy-preserving payments. However, running a Lightning node or managing channels on iOS is technically complex and resource-intensive.17  
* **x402 (EVM/Stablecoins):** Native to HTTP and works seamlessly with EVM chains like Base. It supports stablecoins (USDC), which is critical for a marketplace where participants (data sellers) want predictable value. The integration of x402 is generally more straightforward for web-native agents and supports the "smart contract" logic required for federated governance (staking/slashing).18  
* **Conclusion:** For this architecture, **x402** is the optimal choice for the primary payment rail due to its stablecoin support and ease of integration with the existing DeFi ecosystem, though L402 remains a viable alternative for purely Bitcoin-centric implementations.

### **3.3 Wallet Integration on iOS**

To participate, the iPhone must have a wallet.

* **Embedded Wallets:** The application utilizes an embedded wallet SDK (like Coinbase Wallet SDK or Web3Auth 20) to generate a non-custodial wallet for the user.  
* **Session Keys:** To enable "agentic" behavior (where the phone automatically sells data while the user sleeps), the user authorizes a "Session Key." This key has limited permissions (e.g., "Can sign transactions to accept payments, cannot withdraw funds") and allows the background process to negotiate x402 handshakes autonomously.

### **3.4 The Role of Facilitators**

Since the iPhone cannot run a full blockchain node to verify every transaction, the x402 architecture uses "Facilitators".21 These are trusted (or trust-minimized) relay nodes. The iPhone sends the payment proof provided by the Buyer to the Facilitator. The Facilitator checks the blockchain state and returns a cryptographically signed receipt to the iPhone, confirming the payment is valid. This allows the iPhone to serve the resource immediately without waiting for block finality.

## ---

**4\. Federated Orchestration: Flower and PySyft**

The mechanism for aggregating the "intelligence" sold by the devices is Federated Learning. The architecture employs **Flower (flwr)** for orchestration and **PySyft** for privacy preservation.

### **4.1 Flower on iOS: The Swift Client**

Flower is a framework-agnostic FL platform that scales to millions of clients.

* **Architecture:** The iOS app implements a FlowerClient subclass using the Flower Swift SDK (currently experimental/in-development but functionally describable).22  
* **Communication:** The client connects to a Flower Server (the Aggregator) via gRPC. This connection is persistent or established periodically via background tasks.  
* **Training Round:**  
  1. The Server sends a FitIns (Fit Instructions) message containing the global model weights and training configuration (learning rate, epochs).  
  2. The iOS client deserializes these weights. Since the weights arrive as byte arrays, the client must convert them into MLX Arrays.23  
  3. The client triggers the local MLX training loop, fine-tuning the model on the user's private scanned documents (OCR/HTR data).  
  4. The client computes the updated weights (or gradients) and serializes them back into a FitRes (Fit Result) message to send back to the server.

### **4.2 Privacy Preservation with PySyft**

To ensure that the updates sent via Flower do not leak information about the specific documents scanned (e.g., a specific name in a medical record), **PySyft** is integrated into the workflow.

* **Differential Privacy (DP):** Before the gradients are serialized for Flower, the iOS client applies Local Differential Privacy. It clips the gradients to a maximum norm (limiting the impact of any single data point) and adds Gaussian noise. This mathematically guarantees that the server cannot reverse-engineer the original data from the update.25  
* **Secure Aggregation (SMPC):** PySyft enables Secure Multi-Party Computation. The iOS devices can participate in a secure aggregation protocol where they mask their updates with random noise that cancels out only when all updates are summed at the server. This ensures the server sees *only* the aggregate result, never the individual updates.26  
* **SwiftSyft:** The iOS specific library, SwiftSyft, allows these PySyft protocols to run natively on the device, bridging the gap between the MLX training loop and the Flower communication layer.25

### **4.3 The "Pay-to-Federate" Workflow**

This is the synthesis of Crypteolas and x402.

1. **Job Posting:** A Buyer (e.g., a medical research group) posts a "Training Job" to the Federation Smart Contract, funding it with 10,000 USDC.  
2. **Selection:** The Flower Server selects 1,000 eligible iOS clients (those with relevant data who have staked tokens).  
3. **Payment Negotiation:** The Flower Server initiates the connection. The iOS clients respond with 402 Payment Required.  
4. **Escrow/Streaming:** The Smart Contract opens a payment stream or escrows funds. The iOS clients receive a proof of this funding.  
5. **Execution:** The clients perform the training round via MLX.  
6. **Settlement:** Upon successful submission of the gradients (verified by the server), the Smart Contract releases the pro-rated payment to the individual wallets of the iOS users.

## ---

**5\. Architectural Synthesis: The Marketplace in Action**

This section details the end-to-end flow of the system, illustrating how the user's "finetuned models" and "scanned images" are monetized.

### **5.1 Scenario A: Selling API Access (Inference)**

* **Context:** A user has a highly tuned model for reading 19th-century cursive handwriting (fine-tuned on their personal collection of letters).  
* **The Buyer:** A genealogy website's autonomous agent needs to transcribe a batch of old letters.  
* **The Flow:**  
  1. **Discovery:** The Buyer discovers the user's node via a decentralized registry (DHT or Blockchain) advertising "19th Century Handwriting Expert".  
  2. **Request:** The Buyer sends the image data to the iPhone's public endpoint (via a secure tunnel like ngrok or libp2p).  
  3. **x402 Gate:** The iPhone responds 402 Payment Required: 0.05 USDC.  
  4. **Payment:** The Buyer signs and sends the payment.  
  5. **Inference:** The iPhone accepts the payment, runs the image through its fine-tuned MLX VLM, extracts the text, and returns the JSON transcription.  
  6. **Result:** The user earns money for their device's unique "skill."

### **5.2 Scenario B: Selling Gradients (Federated Training)**

* **Context:** A consortium wants to build a global "Medical Receipt OCR" model.  
* **The Seller:** A user who frequently scans medical bills for personal expense tracking.  
* **The Flow:**  
  1. **Federation:** The user's device joins the "Medical Receipt" federation managed by Flower.  
  2. **Training:** At night, while charging, the device downloads the global model. It runs a training pass on the user's local receipts using MLX.  
  3. **Privacy:** SwiftSyft adds noise to the gradients.  
  4. **Submission:** The device uploads the gradients to the Flower Server.  
  5. **Reward:** The Federation Contract verifies the submission and streams x402 payments to the user's wallet based on the "Shapley Value" of their contribution (i.e., how much their data improved the model).28

## ---

**6\. Challenges, Security, and Mitigations**

### **6.1 Data Heterogeneity (Non-IID Data)**

* **Challenge:** Data on personal devices is highly skewed (Non-Independent and Identically Distributed). One user has only receipts, another only nature photos. This can destabilize federated learning.  
* **Mitigation:** The Flower server employs **Clustered Federated Learning**. It groups clients with similar data distributions into cohorts and trains specialized "Expert" models rather than a single monolithic model. The x402 metadata can include high-level, privacy-preserving tags (e.g., "Domain: Finance") to aid in this clustering without revealing content.

### **6.2 Poisoning Attacks**

* **Challenge:** Malicious users might submit random noise or adversarial gradients to degrade the model, just to collect the participation reward ("Free-riding").  
* **Mitigation:** **Staking and Slashing.** To participate in a paid round, the iOS user (via the app) must stake a small amount of tokens. The server validates a subset of updates against a known validation set. If a client's update consistently increases the loss (degrades the model), their stake is slashed (confiscated) by the smart contract.5

### **6.3 Resource Constraints**

* **Challenge:** Training VLMs is memory and battery intensive.  
* **Mitigation:**  
  * **LoRA/QLoRA:** Only training adapters reduces memory usage by 90%+.  
  * **Scheduling:** The app strictly limits training to when the device is plugged in and connected to Wi-Fi (BGProcessingTask).  
  * **Entitlements:** The app requests the Increased Memory Limit entitlement to prevent iOS from terminating the process during memory spikes.29

## ---

**7\. Implementation Roadmap**

### **Phase 1: The Local Intelligence Node**

* **Objective:** Build the iOS app capable of capture, OCR, and local VLM fine-tuning.  
* **Tech Stack:** Swift, SwiftUI, Vision Framework, MLX Swift.  
* **Key Deliverable:** A functional "Scanner" app that learns the user's corrections over time using a local LoRA adapter.

### **Phase 2: The Agentic Interface**

* **Objective:** Integrate the wallet and x402 protocol.  
* **Tech Stack:** Coinbase Wallet SDK, Node.js (for x402 middleware logic, potentially running locally or via a relay).  
* **Key Deliverable:** The app can receive testnet USDC for processing an image request from an external script.

### **Phase 3: The Federated Marketplace**

* **Objective:** Connect to the Flower server and enable privacy-preserving aggregation.  
* **Tech Stack:** Flower Swift SDK, SwiftSyft, Smart Contracts (Solidity).  
* **Key Deliverable:** A fully decentralized loop where the global model improves via user contributions, and users are automatically compensated.

## ---

**Conclusion**

The convergence of "Crypteolas" incentives, agentic x402 payments, and the raw power of Apple Silicon creates the conditions for a new digital economy. This report has outlined a viable architecture for a Decentralized Autonomous Knowledge Market. By enabling iPhones to securely fine-tune Vision-Language Models on private data and establishing a trustless, agentic payment rail for that intelligence, we can move beyond the extractive era of "Big AI."  
This system solves the **Cold Start Problem** of Federated Learning by providing direct economic incentives for participation. It solves the **Privacy Problem** of AI by ensuring raw data never leaves the device. And it solves the **Access Problem** by creating a liquid marketplace where any agent can purchase bespoke, high-quality intelligence from the edge. The technical path is complex, requiring deep integration of MLX, Flower, and Blockchain protocols, but the components are now mature enough to make this vision a reality.

### **Data Tables and Comparisons**

#### **Table 1: Comparison of Payment Protocols for Agentic Markets**

| Feature | x402 (Payment Required) | L402 (Lightning Network) | Implication for iOS Marketplace |
| :---- | :---- | :---- | :---- |
| **Settlement Layer** | EVM / Stablecoins (USDC) | Bitcoin Lightning Network | **x402** is preferred for stability and DeFi interoperability. |
| **Privacy** | Pseudonymous (Wallet Address) | High (Onion Routing) | **L402** offers better privacy but higher complexity. |
| **Client Complexity** | Low (Signing Messages) | High (Channel Management) | **x402** is lighter for mobile background tasks. |
| **Agent Support** | High (Coinbase AgentKit, etc.) | High (LangChain Tools) | Both have strong tooling, but **x402** aligns with web standards. |
| **Use Case** | API Access, Model Subscriptions | Streaming Micro-payments | **x402** suits the "Job" nature of FL training rounds. |

#### **Table 2: On-Device Compute Stack for Crypteolas**

| Component | Technology | Role in Marketplace |
| :---- | :---- | :---- |
| **Vision Encoder** | **Apple Vision / FastVLM** | Fast extraction of text/features; reduces VLM load. |
| **Inference Engine** | **llama.cpp (GGUF)** | Efficient, broad compatibility for serving API requests. |
| **Training Engine** | **MLX Swift** | Native, unified memory training for LoRA adapters. |
| **Orchestrator** | **Flower (Swift SDK)** | Manages the federated rounds and communication. |
| **Privacy** | **SwiftSyft** | Adds noise (DP) and manages Secure Aggregation. |

#### **Table 3: Economic Incentives & Governance**

| Role | Action | Incentive/Penalty |
| :---- | :---- | :---- |
| **Data Seller (iPhone)** | Submits Gradient Update | Earns USDC (x402) based on Shapley Value. |
| **Data Seller (iPhone)** | Submits Malicious Update | Staked USDC is slashed (burned). |
| **Buyer (Agent)** | Requests Training Round | Pays USDC to Federation Contract. |
| **Validator (Node)** | Audits Gradient Quality | Earns fee for validating updates (Proof of Training). |

#### **Works cited**

1. (PDF) EdgeFL-Crypto: Federated Split Learning Architecture for IoT- Based Cryptocurrency Volatility Prediction in Edge-Cloud Environments \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/publication/397265328\_EdgeFL-Crypto\_Federated\_Split\_Learning\_Architecture\_for\_IoT-\_Based\_Cryptocurrency\_Volatility\_Prediction\_in\_Edge-Cloud\_Environments](https://www.researchgate.net/publication/397265328_EdgeFL-Crypto_Federated_Split_Learning_Architecture_for_IoT-_Based_Cryptocurrency_Volatility_Prediction_in_Edge-Cloud_Environments)  
2. \[2108.06912\] Blockchain-based Trustworthy Federated Learning Architecture \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2108.06912](https://arxiv.org/abs/2108.06912)  
3. Blockchain-based federated learning architecture \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/figure/Blockchain-based-federated-learning-architecture\_fig3\_380101342](https://www.researchgate.net/figure/Blockchain-based-federated-learning-architecture_fig3_380101342)  
4. X402 Protocol: What It Is, How It Works, and Why It Matters, accessed December 15, 2025, [https://vidrihmarko.medium.com/x402-protocol-what-it-is-how-it-works-and-why-it-matters-2b6bc889ee7f](https://vidrihmarko.medium.com/x402-protocol-what-it-is-how-it-works-and-why-it-matters-2b6bc889ee7f)  
5. FLock \- Federated Machine Learning On the Blockchain, accessed December 15, 2025, [https://www.flock.io/](https://www.flock.io/)  
6. Federated Learning Labs: FELT, accessed December 15, 2025, [https://feltlabs.ai/](https://feltlabs.ai/)  
7. Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU, accessed December 15, 2025, [https://machinelearning.apple.com/research/exploring-llms-mlx-m5](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)  
8. Deploying Transformers on the Apple Neural Engine \- Apple Machine Learning Research, accessed December 15, 2025, [https://machinelearning.apple.com/research/neural-engine-transformers](https://machinelearning.apple.com/research/neural-engine-transformers)  
9. Performance of llama.cpp on Apple Silicon A-series \#4508 \- GitHub, accessed December 15, 2025, [https://github.com/ggml-org/llama.cpp/discussions/4508](https://github.com/ggml-org/llama.cpp/discussions/4508)  
10. Building iOS app with llama cpp \- anyone familiar? : r/LocalLLaMA \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1ncy4nz/building\_ios\_app\_with\_llama\_cpp\_anyone\_familiar/](https://www.reddit.com/r/LocalLLaMA/comments/1ncy4nz/building_ios_app_with_llama_cpp_anyone_familiar/)  
11. ml-explore/mlx-swift: Swift API for MLX \- GitHub, accessed December 15, 2025, [https://github.com/ml-explore/mlx-swift](https://github.com/ml-explore/mlx-swift)  
12. On-device ML research with MLX and Swift, accessed December 15, 2025, [https://swift.org/blog/mlx-swift/](https://swift.org/blog/mlx-swift/)  
13. FastVLM: Efficient Vision Encoding for Vision Language Models \- Apple Machine Learning Research, accessed December 15, 2025, [https://machinelearning.apple.com/research/fast-vision-language-models](https://machinelearning.apple.com/research/fast-vision-language-models)  
14. How to Implement a Crypto Paywall with x402 Payment Protocol | Quicknode Guides, accessed December 15, 2025, [https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required](https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required)  
15. What is x402? \- Ledger, accessed December 15, 2025, [https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402](https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402)  
16. x402 \- Payment Required | Internet-Native Payments Standard, accessed December 15, 2025, [https://www.x402.org/](https://www.x402.org/)  
17. What Is L402, Lightning-Powered Payments for AI Agents? \- BingX, accessed December 15, 2025, [https://bingx.com/en/learn/article/what-is-l402-payments-for-ai-agents-on-lightning-network-how-does-it-work](https://bingx.com/en/learn/article/what-is-l402-payments-for-ai-agents-on-lightning-network-how-does-it-work)  
18. x402: An AI-Native Payment Protocol for the Web | by Jung-Hua Liu | Oct, 2025 | Medium, accessed December 15, 2025, [https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936](https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936)  
19. When AI Pays the Bill: How AI Agents Will Transact Using Coinbase’s X402 Protocol, accessed December 15, 2025, [https://medium.com/@deadwin/when-ai-pays-the-bill-how-ai-agents-will-transact-using-coinbases-x402-protocol-fc2de513db63](https://medium.com/@deadwin/when-ai-pays-the-bill-how-ai-agents-will-transact-using-coinbases-x402-protocol-fc2de513db63)  
20. Embedded Wallets SDK for iOS | MetaMask developer documentation, accessed December 15, 2025, [https://docs.metamask.io/embedded-wallets/sdk/ios/](https://docs.metamask.io/embedded-wallets/sdk/ios/)  
21. OrbytLabz/x402python: native python library for the x402 standard on Solana. \- GitHub, accessed December 15, 2025, [https://github.com/OrbytLabz/x402python](https://github.com/OrbytLabz/x402python)  
22. FLiOS \- A Flower SDK for iOS Devices with Example, accessed December 15, 2025, [https://flower.ai/docs/examples/ios.html](https://flower.ai/docs/examples/ios.html)  
23. Quickstart iOS \- Flower Framework, accessed December 15, 2025, [https://flower.ai/docs/framework/tutorial-quickstart-ios.html](https://flower.ai/docs/framework/tutorial-quickstart-ios.html)  
24. tutorial-quickstart-mlx.rst.txt \- Flower AI, accessed December 15, 2025, [https://flower.ai/docs/framework/\_sources/tutorial-quickstart-mlx.rst.txt](https://flower.ai/docs/framework/_sources/tutorial-quickstart-mlx.rst.txt)  
25. OpenMinedSwiftSyft on CocoaPods.org, accessed December 15, 2025, [https://cocoapods.org/pods/OpenMinedSwiftSyft](https://cocoapods.org/pods/OpenMinedSwiftSyft)  
26. What is PySyft, and how does it relate to federated learning? \- Milvus, accessed December 15, 2025, [https://milvus.io/ai-quick-reference/what-is-pysyft-and-how-does-it-relate-to-federated-learning](https://milvus.io/ai-quick-reference/what-is-pysyft-and-how-does-it-relate-to-federated-learning)  
27. OpenMined/SwiftSyft: The official Syft worker for iOS, built in Swift \- GitHub, accessed December 15, 2025, [https://github.com/OpenMined/SwiftSyft](https://github.com/OpenMined/SwiftSyft)  
28. Federated Learning Incentive Mechanism with Supervised Fuzzy Shapley Value \- MDPI, accessed December 15, 2025, [https://www.mdpi.com/2075-1680/13/4/254](https://www.mdpi.com/2075-1680/13/4/254)  
29. Exploring MLX Swift: Configuring Different Models \- Rudrank Riyam, accessed December 15, 2025, [https://rudrank.com/exploring-mlx-swift-configuring-different-models](https://rudrank.com/exploring-mlx-swift-configuring-different-models)
---


## File: docs/meaisínfhoghlaim/ml-models/README.md

# ML Models

This directory contains research on AI/ML models for the Anam platform.

## Contents

- `whisper-celtic-asr.md` - Speech recognition for Celtic languages
- `celtic-ocr.md` - Handwriting recognition (FedOCR)
- `qwen-vlm-assessment.md` - Visual assessment validation
- `fibo-asset-generation.md` - Celtic art/NFT generation
- `fine-tuning-strategy.md` - Unsloth + federated approaches

## Model Catalog

### Speech & Language
| Model | Purpose | Languages |
|-------|---------|-----------|
| Whisper (fine-tuned) | ASR | Irish, Scottish Gaelic, Manx, Welsh |
| gaBERT | NLU | Irish |
| UCCIX | Translation | Celtic languages |

### Vision & Generation
| Model | Purpose | Use Case |
|-------|---------|----------|
| Qwen2.5-VL | Assessment | Validate generated content |
| FIBO (Bria) | Image Gen | Celtic art NFTs |
| ColPali | Embeddings | Document visual search |

### Fine-Tuning Stack
- **Unsloth** - Efficient LoRA/QLoRA training
- **MLX** - Apple Silicon optimization
- **Flower** - Federated learning orchestration

## Proof of Learn (PoL) Validation

```
Student Submission (Voice/Handwriting)
    ↓ (Whisper/OCR on-device)
Local Transcription
    ↓ (Consensus validation)
Verified Learning
    ↓ (Tuath minting)
Token Reward
```

## Celtic Art Generation Pipeline

1. **Reference**: SVG Celtic knot patterns
2. **ControlNet**: Enforce topology
3. **FIBO**: JSON-native generation
4. **Metadata**: Embed provenance in NFT

---


## File: docs/meaisínfhoghlaim/ml-models/unsloth-catalog.md

---
title: "Unsloth Model Catalog | Unsloth Documentation"
source: "https://docs.unsloth.ai/get-started/unsloth-model-catalog"
author:
published: 2025-12-12
created: 2025-12-15
description:
tags:
  - "clippings"
---
Unsloth model catalog for all our [Dynamic](https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs) GGUF, 4-bit, 16-bit models on Hugging Face.

[DeepSeek](https://docs.unsloth.ai/get-started/unsloth-model-catalog#deepseek-models) [Llama](https://docs.unsloth.ai/get-started/unsloth-model-catalog#llama-models) [Gemma](https://docs.unsloth.ai/get-started/unsloth-model-catalog#gemma-models) [Qwen](https://docs.unsloth.ai/get-started/unsloth-model-catalog#qwen-models) [Mistral](https://docs.unsloth.ai/get-started/unsloth-model-catalog#mistral-models) [Phi](https://docs.unsloth.ai/get-started/unsloth-model-catalog#phi-models)

**GGUFs** let you run models in tools like Ollama, Open WebUI, and llama.cpp.**Instruct (4-bit)** safetensors can be used for inference or fine-tuning.

#### DeepSeek models:

#### Llama models:

Model

Variant

GGUF

Instruct (4-bit)

#### Gemma models:

#### Qwen models:

Model

Variant

GGUF

Instruct (4-bit)

[**Qwen3-VL**](https://docs.unsloth.ai/models/qwen3-vl-how-to-run-and-fine-tune)

2B-Instruct

[link](https://huggingface.co/unsloth/Qwen3-VL-2B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-2B-Instruct-unsloth-bnb-4bit)

2B-Thinking

[link](https://huggingface.co/unsloth/Qwen3-VL-2B-Thinking-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-2B-Thinking-unsloth-bnb-4bit)

4B-Instruct

[link](https://huggingface.co/unsloth/Qwen3-VL-4B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit)

4B-Thinking

[link](https://huggingface.co/unsloth/Qwen3-VL-4B-Thinking-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-4B-Thinking-unsloth-bnb-4bit)

8B-Instruct

[link](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-8B-Instruct-unsloth-bnb-4bit)

8B-Thinking

[link](https://huggingface.co/unsloth/Qwen3-VL-8B-Thinking-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-VL-8B-Thinking-unsloth-bnb-4bit)

**Qwen3-Coder**

30B-A3B

[link](https://huggingface.co/unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF)

—

480B-A35B

[link](https://huggingface.co/unsloth/Qwen3-Coder-480B-A35B-Instruct-GGUF)

—

[**Qwen3-2507**](https://docs.unsloth.ai/models/qwen3-next)

30B-A3B-Instruct

[link](https://huggingface.co/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF)

—

30B-A3B-Thinking

[link](https://huggingface.co/unsloth/Qwen3-30B-A3B-Thinking-2507-GGUF)

—

235B-A22B-Thinking

[link](https://huggingface.co/unsloth/Qwen3-235B-A22B-Thinking-2507-GGUF/)

—

235B-A22B-Instruct

[link](https://huggingface.co/unsloth/Qwen3-235B-A22B-Instruct-2507-GGUF/)

—

**Qwen 3**

0.6 B

[link](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-0.6B-unsloth-bnb-4bit)

1.7 B

[link](https://huggingface.co/unsloth/Qwen3-1.7B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-1.7B-unsloth-bnb-4bit)

4 B

[link](https://huggingface.co/unsloth/Qwen3-4B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-4B-unsloth-bnb-4bit)

8 B

[link](https://huggingface.co/unsloth/Qwen3-8B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-8B-unsloth-bnb-4bit)

14 B

[link](https://huggingface.co/unsloth/Qwen3-14B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-14B-unsloth-bnb-4bit)

30 B-A3B

[link](https://huggingface.co/unsloth/Qwen3-30B-A3B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-30B-A3B-bnb-4bit)

32 B

[link](https://huggingface.co/unsloth/Qwen3-32B-GGUF)

[link](https://huggingface.co/unsloth/Qwen3-32B-unsloth-bnb-4bit)

235 B-A22B

[link](https://huggingface.co/unsloth/Qwen3-235B-A22B-GGUF)

—

3 B

[link](https://huggingface.co/unsloth/Qwen2.5-Omni-3B-GGUF)

—

7 B

[link](https://huggingface.co/unsloth/Qwen2.5-Omni-7B-GGUF)

—

3 B

[link](https://huggingface.co/unsloth/Qwen2.5-VL-3B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-VL-3B-Instruct-unsloth-bnb-4bit)

7 B

[link](https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-VL-7B-Instruct-unsloth-bnb-4bit)

32 B

[link](https://huggingface.co/unsloth/Qwen2.5-VL-32B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-VL-32B-Instruct-unsloth-bnb-4bit)

72 B

[link](https://huggingface.co/unsloth/Qwen2.5-VL-72B-Instruct-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-VL-72B-Instruct-unsloth-bnb-4bit)

**Qwen 2.5**

0.5 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-0.5B-Instruct-bnb-4bit)

1.5 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-1.5B-Instruct-bnb-4bit)

3 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-3B-Instruct-bnb-4bit)

7 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-7B-Instruct-bnb-4bit)

14 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-14B-Instruct-bnb-4bit)

32 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-32B-Instruct-bnb-4bit)

72 B

—

[link](https://huggingface.co/unsloth/Qwen2.5-72B-Instruct-bnb-4bit)

0.5 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-0.5B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-0.5B-Instruct-bnb-4bit)

1.5 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-1.5B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit)

3 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-3B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-3B-Instruct-bnb-4bit)

7 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-7B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit)

14 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-14B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-14B-Instruct-bnb-4bit)

32 B

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-32B-Instruct-128K-GGUF)

[link](https://huggingface.co/unsloth/Qwen2.5-Coder-32B-Instruct-bnb-4bit)

**QwQ**

32 B

[link](https://huggingface.co/unsloth/QwQ-32B-GGUF)

[link](https://huggingface.co/unsloth/QwQ-32B-unsloth-bnb-4bit)

**QVQ (preview)**

72 B

—

[link](https://huggingface.co/unsloth/QVQ-72B-Preview-bnb-4bit)

1.5 B

—

[link](https://huggingface.co/unsloth/Qwen2-1.5B-Instruct-bnb-4bit)

7 B

—

[link](https://huggingface.co/unsloth/Qwen2-7B-Instruct-bnb-4bit)

72 B

—

[link](https://huggingface.co/unsloth/Qwen2-72B-Instruct-bnb-4bit)

2 B

—

[link](https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct-unsloth-bnb-4bit)

7 B

—

[link](https://huggingface.co/unsloth/Qwen2-VL-7B-Instruct-unsloth-bnb-4bit)

72 B

—

[link](https://huggingface.co/unsloth/Qwen2-VL-72B-Instruct-bnb-4bit)

#### Mistral models:

#### Phi models:

[Previous Unsloth Notebooks](https://docs.unsloth.ai/get-started/unsloth-notebooks) [Next Installation](https://docs.unsloth.ai/get-started/install-and-update)

Last updated

Was this helpful?
---


## Original Sources

- `docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/email.md`
- `docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/meta.md`
- `docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/my-app/README.md`
- `docs/meaisínfhoghlaim/baml/2025-09-09-generative-uis/README.md`
- `docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/backend/README.md`
- `docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/email.md`
- `docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/frontend/README.md`
- `docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/meta.md`
- `docs/meaisínfhoghlaim/baml/2025-09-30-dyanmic-schemas/README.md`
- `docs/meaisínfhoghlaim/baml/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/colpali/CHANGELOG.md`
- `docs/meaisínfhoghlaim/colpali/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/colpali/README.md`
- `docs/meaisínfhoghlaim/FIBO/CONTRIBUTING.md`
- `docs/meaisínfhoghlaim/FIBO/examples/README.md`
- `docs/meaisínfhoghlaim/FIBO/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/FIBO/README.md`
- `docs/meaisínfhoghlaim/FIBO/src/fine_tuning/README.md`
- `docs/meaisínfhoghlaim/federated/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/docs/message_flow.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/federated-analytics-diabetes/fed-analytics-diabetes/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/federated-analytics-diabetes/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fedrag/fedrag_v1/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fedrag/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fl-diabetes-prediction/fl-diabetes-prediction/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/notebooks/fl-diabetes-prediction/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/README.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/RELEASE.md`
- `docs/meaisínfhoghlaim/federated/syft-flwr/tests/assets/code/fed-analytics-diabetes/README.md`
- `docs/meaisínfhoghlaim/sam-audio/CODE_OF_CONDUCT.md`
- `docs/meaisínfhoghlaim/sam-audio/CONTRIBUTING.md`
- `docs/meaisínfhoghlaim/sam-audio/eval/README.md`
- `docs/meaisínfhoghlaim/sam-audio/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/sam-audio/README.md`
- `docs/meaisínfhoghlaim/sam3d_objects/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/sam3d-api/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/awf.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/ecosystem_type_mapping.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/forest_loss_driver.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/internal.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/lfmc.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/mangrove.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/nandi.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/docs/tutorials/FinetuneOlmoEarthSegmentation.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_projects/olmoearth_run/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_projects/utils/label_quality/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/mozambique_lulc/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/sample/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/olmoearth_run_data/satlas_solar_farm/README.md`
- `docs/meaisínfhoghlaim/olmoearth_projects/README.md`
- `docs/meaisínfhoghlaim/audio/Aligning Gaelic Script for QwenVL Finetuning.md`
- `docs/meaisínfhoghlaim/audio/LLM based TTS models.md`
- `docs/meaisínfhoghlaim/audio/Scraping Irish Audio Files.md`
- `docs/meaisínfhoghlaim/ml-models/celtic-ocr.md`
- `docs/meaisínfhoghlaim/ml-models/federated-marketplace.md`
- `docs/meaisínfhoghlaim/ml-models/README.md`
- `docs/meaisínfhoghlaim/ml-models/unsloth-catalog.md`
