import { anthropic } from "@ai-sdk/anthropic";
import { openai } from "@ai-sdk/openai";
import {
  customProvider,
} from "ai";

// custom provider with different model settings:
export const myProvider = customProvider({
  languageModels: {
    "gpt-5.1": openai("gpt-5.1"),
    "sonnet-3.7": anthropic("claude-3-7-sonnet-20250219"),
  },
});

export type modelID = Parameters<(typeof myProvider)["languageModel"]>["0"];

export const models: Record<modelID, string> = {
  "gpt-5.1": "ChatGPT 5.1",
  "sonnet-3.7": "Claude Sonnet 3.7",
};
