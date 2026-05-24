# Celtic Language AI Skill

## Context
When assuming the `ai-engineer` persona, utilize this skill to understand how to process and extract Gaelic/Celtic educational texts safely.

## Core Mandates
1. **Schema-Aligned Parsing:** Do not use raw JSON prompts. You MUST use BAML (`baml_src/`) for extracting named entities (`logainm.baml`, `tearma.baml`) from Irish texts to guarantee compile-time LLM safety.
2. **Models:** Utilize `gemma-2.0-flash` for broad text extraction. For multi-column PDFs (like SEC Irish Exam papers), rely on vision-language models (`glm4.6v` or `colpali`) orchestrated via LiteLLM.
3. **Graph Integration:** Extracted learning outcomes must be temporally mapped using the Graphiti MCP server, establishing semantic links like `PREREQUISITE_FOR`.
