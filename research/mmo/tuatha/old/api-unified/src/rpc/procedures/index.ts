import { os, ORPCError } from "@orpc/server";
import { z } from "zod";
import {
  TodoSchema,
  CreateTodoSchema,
  UpdateTodoSchema,
  UserSchema,
  NewUserSchema,
  CredentialSchema,
  TokenSchema,
} from "../../../contracts/schemas.js";

// ============================================================================
// In-memory storage (replace with real database)
// ============================================================================

const todos: Map<string, any> = new Map();
const users: Map<string, any> = new Map();

// Seed some data
todos.set("1", {
  id: "1",
  title: "Build unified API",
  description: "Combine MCP and oRPC in Hono",
  completed: false,
  userId: "1",
  createdAt: new Date(),
});

users.set("1", {
  id: "1",
  email: "demo@example.com",
  name: "Demo User",
  createdAt: new Date(),
});

// ============================================================================
// Context type
// ============================================================================

type AppContext = {
  userId?: string;
  headers?: Headers;
};

// ============================================================================
// Base procedure with context
// ============================================================================

export const publicProcedure = os.$context<AppContext>();

// ============================================================================
// Auth Middleware
// ============================================================================

export const authedProcedure = publicProcedure.use(async ({ context, next }) => {
  const userId = context.userId;

  if (!userId) {
    throw new ORPCError({
      code: "UNAUTHORIZED",
      message: "Authentication required",
    });
  }

  return next({
    context: {
      ...context,
      userId,
    },
  });
});

// ============================================================================
// Todo Procedures
// ============================================================================

export const createTodo = authedProcedure
  .input(CreateTodoSchema)
  .output(TodoSchema)
  .handler(async ({ context, input }) => {
    const id = String(todos.size + 1);
    const todo = {
      id,
      title: input.title,
      description: input.description,
      completed: false,
      userId: context.userId,
      createdAt: new Date(),
    };

    todos.set(id, todo);
    return todo;
  });

export const getTodos = authedProcedure
  .input(
    z.object({
      limit: z.number().min(1).max(100).default(10),
      completed: z.boolean().optional(),
    })
  )
  .output(z.array(TodoSchema))
  .handler(async ({ context, input }) => {
    const userTodos = Array.from(todos.values())
      .filter((todo) => todo.userId === context.userId)
      .filter((todo) =>
        input.completed !== undefined ? todo.completed === input.completed : true
      )
      .slice(0, input.limit);

    return userTodos;
  });

export const updateTodo = authedProcedure
  .input(UpdateTodoSchema)
  .output(TodoSchema)
  .handler(async ({ context, input }) => {
    const todo = todos.get(input.id);

    if (!todo) {
      throw new ORPCError({
        code: "NOT_FOUND",
        message: "Todo not found",
      });
    }

    if (todo.userId !== context.userId) {
      throw new ORPCError({
        code: "FORBIDDEN",
        message: "You do not have permission to update this todo",
      });
    }

    const updated = {
      ...todo,
      ...input,
    };

    todos.set(input.id, updated);
    return updated;
  });

export const deleteTodo = authedProcedure
  .input(z.object({ id: z.string() }))
  .output(z.object({ success: z.boolean() }))
  .handler(async ({ context, input }) => {
    const todo = todos.get(input.id);

    if (!todo) {
      throw new ORPCError({
        code: "NOT_FOUND",
        message: "Todo not found",
      });
    }

    if (todo.userId !== context.userId) {
      throw new ORPCError({
        code: "FORBIDDEN",
        message: "You do not have permission to delete this todo",
      });
    }

    todos.delete(input.id);
    return { success: true };
  });

// ============================================================================
// Auth Procedures
// ============================================================================

export const signup = publicProcedure
  .input(NewUserSchema)
  .output(TokenSchema)
  .handler(async ({ input }) => {
    // Check if user exists
    const existingUser = Array.from(users.values()).find(
      (u) => u.email === input.email
    );

    if (existingUser) {
      throw new ORPCError({
        code: "CONFLICT",
        message: "User with this email already exists",
      });
    }

    // Create new user
    const id = String(users.size + 1);
    const user = {
      id,
      email: input.email,
      name: input.name,
      createdAt: new Date(),
    };

    users.set(id, user);

    // Return token
    return {
      token: `token-${id}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
    };
  });

export const signin = publicProcedure
  .input(CredentialSchema)
  .output(TokenSchema)
  .handler(async ({ input }) => {
    const user = Array.from(users.values()).find(
      (u) => u.email === input.email
    );

    if (!user) {
      throw new ORPCError({
        code: "UNAUTHORIZED",
        message: "Invalid credentials",
      });
    }

    return {
      token: `token-${user.id}`,
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24 hours
    };
  });

export const me = authedProcedure.output(UserSchema).handler(async ({ context }) => {
  const user = users.get(context.userId);

  if (!user) {
    throw new ORPCError({
      code: "NOT_FOUND",
      message: "User not found",
    });
  }

  return user;
});

// ============================================================================
// Public Info Procedures
// ============================================================================

export const health = publicProcedure
  .output(
    z.object({
      status: z.string(),
      timestamp: z.date(),
      uptime: z.number(),
    })
  )
  .handler(async () => ({
    status: "healthy",
    timestamp: new Date(),
    uptime: process.uptime(),
  }));

export const info = publicProcedure
  .output(
    z.object({
      name: z.string(),
      version: z.string(),
      features: z.array(z.string()),
    })
  )
  .handler(async () => ({
    name: "api-unified",
    version: "1.0.0",
    features: ["MCP Tools", "oRPC Procedures", "AI Streaming Chat", "OpenAPI Docs"],
  }));
