import { z } from "zod";

// ============================================================================
// User Schemas
// ============================================================================

export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  createdAt: z.date(),
});

export const NewUserSchema = z.object({
  email: z.string().email(),
  name: z.string(),
  password: z.string().min(8),
});

export type User = z.infer<typeof UserSchema>;
export type NewUser = z.infer<typeof NewUserSchema>;

// ============================================================================
// Todo Schemas
// ============================================================================

export const TodoSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  completed: z.boolean(),
  userId: z.string(),
  createdAt: z.date(),
});

export const CreateTodoSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
});

export const UpdateTodoSchema = z.object({
  id: z.string(),
  title: z.string().min(1).max(200).optional(),
  description: z.string().max(1000).optional(),
  completed: z.boolean().optional(),
});

export type Todo = z.infer<typeof TodoSchema>;
export type CreateTodo = z.infer<typeof CreateTodoSchema>;
export type UpdateTodo = z.infer<typeof UpdateTodoSchema>;

// ============================================================================
// Auth Schemas
// ============================================================================

export const CredentialSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

export const TokenSchema = z.object({
  token: z.string(),
  expiresAt: z.date(),
});

export type Credential = z.infer<typeof CredentialSchema>;
export type Token = z.infer<typeof TokenSchema>;

// ============================================================================
// MCP Tool Schemas
// ============================================================================

export const AddNumbersInputSchema = z.object({
  a: z.number().describe("First number to add"),
  b: z.number().describe("Second number to add"),
});

export const SearchInputSchema = z.object({
  query: z.string().describe("Search query string"),
  limit: z.number().min(1).max(100).default(10).describe("Maximum number of results"),
});

export const AnalyzeTextInputSchema = z.object({
  text: z.string().describe("Text to analyze"),
  includeEntities: z.boolean().default(true).describe("Include named entities"),
  includeSentiment: z.boolean().default(true).describe("Include sentiment analysis"),
});

// ============================================================================
// AI Chat Schemas
// ============================================================================

export const ChatMessageSchema = z.object({
  role: z.enum(["user", "assistant", "system"]),
  content: z.string(),
});

export const ChatRequestSchema = z.object({
  messages: z.array(ChatMessageSchema),
  model: z.string().default("claude-3-5-sonnet-20241022"),
  temperature: z.number().min(0).max(1).default(0.7).optional(),
});

export type ChatMessage = z.infer<typeof ChatMessageSchema>;
export type ChatRequest = z.infer<typeof ChatRequestSchema>;
