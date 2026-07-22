---
name: effect-ts
description: Expert assistance for building robust TypeScript applications with Effect. Use when users need type-safe error handling, dependency injection, concurrency primitives, or functional programming patterns.
---

# Effect - TypeScript Effect System

**Version:** 3.x | **Last Updated:** 2025-01

## Overview

Effect is a powerful TypeScript framework providing a functional effect system:

- **Type-Safe Errors**: All errors tracked at the type level
- **Dependency Injection**: Layer-based service composition
- **Concurrency**: Fiber-based lightweight threading
- **Streaming**: Pull-based stream processing
- **Rich Standard Library**: Comprehensive utilities

**Documentation**: https://effect.website

## When to Use This Skill

Activate when users need:

- "Handle errors with full type safety"
- "Implement dependency injection"
- "Build concurrent applications"
- "Use functional programming patterns"
- "Process data streams"

## Core Concepts

### 1. The Effect Type

```typescript
import { Effect } from "effect"

// Effect<A, E, R>
// A = Success type
// E = Error type
// R = Requirements/Dependencies

// Effect that succeeds with number, never fails, no dependencies
const succeed: Effect.Effect<number, never, never> = Effect.succeed(42)

// Effect that can fail with string
const mayFail: Effect.Effect<number, string, never> =
  Effect.fail("Something went wrong")

// Effect that requires a Database service
const withDeps: Effect.Effect<User, NotFoundError, Database> =
  Effect.gen(function* () {
    const db = yield* Database
    return yield* db.findUser("123")
  })
```

### 2. Generator Syntax (Effect.gen)

```typescript
import { Effect } from "effect"

const program = Effect.gen(function* () {
  // Yield effects to execute them
  const user = yield* fetchUser(userId)
  const posts = yield* fetchPosts(user.id)

  // Use standard control flow
  if (posts.length === 0) {
    return { user, posts: [], message: "No posts" }
  }

  // Map over arrays with effects
  const enriched = yield* Effect.all(
    posts.map((post) => enrichPost(post))
  )

  return { user, posts: enriched }
})
```

### 3. Pipe Syntax

```typescript
import { Effect, pipe } from "effect"

const program = pipe(
  fetchUser(userId),
  Effect.flatMap((user) => fetchPosts(user.id)),
  Effect.map((posts) => posts.length),
  Effect.catchAll((error) => Effect.succeed(0)),
  Effect.tap((count) => Effect.log(`Found ${count} posts`))
)

// Or using fluent API
const program2 = fetchUser(userId).pipe(
  Effect.flatMap((user) => fetchPosts(user.id)),
  Effect.map((posts) => posts.length)
)
```

### 4. Error Handling

```typescript
import { Effect, Data } from "effect"

// Define tagged errors
class NotFoundError extends Data.TaggedError("NotFoundError")<{
  readonly id: string
}> {}

class ValidationError extends Data.TaggedError("ValidationError")<{
  readonly field: string
  readonly message: string
}> {}

// Handle errors by tag
const program = Effect.gen(function* () {
  const user = yield* fetchUser(id).pipe(
    Effect.catchTag("NotFoundError", (error) =>
      Effect.succeed(createDefaultUser(error.id))
    ),
    Effect.catchTag("ValidationError", (error) =>
      Effect.fail(new BadRequestError(error.message))
    )
  )
  return user
})

// Catch all errors
const withFallback = fetchUser(id).pipe(
  Effect.catchAll((error) => Effect.succeed(defaultUser))
)

// Retry with schedule
import { Schedule } from "effect"

const withRetry = fetchUser(id).pipe(
  Effect.retry({
    times: 3,
    schedule: Schedule.exponential("100 millis")
  })
)
```

### 5. Services and Layers

```typescript
import { Context, Effect, Layer } from "effect"

// Define service interface
class UserRepository extends Context.Tag("UserRepository")<
  UserRepository,
  {
    readonly findById: (id: string) => Effect.Effect<User, NotFoundError>
    readonly save: (user: User) => Effect.Effect<void, DatabaseError>
  }
>() {}

// Live implementation
const UserRepositoryLive = Layer.effect(
  UserRepository,
  Effect.gen(function* () {
    const db = yield* Database

    return {
      findById: (id) =>
        Effect.gen(function* () {
          const result = yield* db.query(`SELECT * FROM users WHERE id = ?`, [id])
          if (!result) return yield* Effect.fail(new NotFoundError({ id }))
          return result
        }),

      save: (user) =>
        db.query(`INSERT INTO users VALUES (?, ?)`, [user.id, user.name]).pipe(
          Effect.asVoid
        )
    }
  })
)

// Test implementation
const UserRepositoryTest = Layer.succeed(UserRepository, {
  findById: (id) => Effect.succeed({ id, name: "Test User" }),
  save: () => Effect.void
})

// Use service
const getUserEmail = (id: string) =>
  Effect.gen(function* () {
    const repo = yield* UserRepository
    const user = yield* repo.findById(id)
    return user.email
  })

// Provide dependencies
const program = getUserEmail("123").pipe(
  Effect.provide(UserRepositoryLive)
)
```

### 6. Layer Composition

```typescript
import { Layer } from "effect"

// Compose layers
const InfraLayer = Layer.mergeAll(
  DatabaseLive,
  CacheLive,
  LoggerLive
)

const RepositoryLayer = Layer.mergeAll(
  UserRepositoryLive,
  PostRepositoryLive
).pipe(Layer.provide(InfraLayer))

const ServiceLayer = Layer.mergeAll(
  UserServiceLive,
  PostServiceLive
).pipe(Layer.provide(RepositoryLayer))

// Provide to program
const main = program.pipe(Effect.provide(ServiceLayer))

// Run
Effect.runPromise(main)
```

### 7. Concurrency (Fibers)

```typescript
import { Effect, Fiber } from "effect"

const program = Effect.gen(function* () {
  // Fork a fiber (background execution)
  const fiber = yield* Effect.fork(longRunningTask)

  // Do other work
  yield* otherWork

  // Join fiber and get result
  const result = yield* Fiber.join(fiber)
  return result
})

// Parallel execution
const parallel = Effect.all([
  fetchUser(id),
  fetchPosts(id),
  fetchComments(id)
])

// With concurrency limit
const limited = Effect.all(
  items.map(processItem),
  { concurrency: 5 }
)

// Race (first to complete wins)
const race = Effect.race(
  fetchFromCache,
  fetchFromDatabase
)

// Timeout
const withTimeout = fetchData().pipe(
  Effect.timeout("5 seconds")
)
```

### 8. Resource Management

```typescript
import { Effect } from "effect"

// Scoped resources
const program = Effect.scoped(
  Effect.gen(function* () {
    const connection = yield* acquireConnection
    const result = yield* useConnection(connection)
    return result
    // Connection automatically released
  })
)

// Acquire/Release pattern
const withConnection = Effect.acquireRelease(
  openConnection(),
  (conn) => closeConnection(conn)
)

// Add finalizers
const program2 = Effect.gen(function* () {
  yield* Effect.addFinalizer(() =>
    Effect.log("Cleaning up resources")
  )
  return yield* doWork()
})
```

### 9. Streams

```typescript
import { Stream, Effect } from "effect"

// Create streams
const stream1 = Stream.make(1, 2, 3, 4, 5)
const stream2 = Stream.fromIterable([1, 2, 3])
const stream3 = Stream.fromEffect(fetchData())

// Transform streams
const processed = Stream.make(1, 2, 3, 4, 5).pipe(
  Stream.map((n) => n * 2),
  Stream.filter((n) => n > 5),
  Stream.take(10)
)

// Consume streams
const result = Stream.make(1, 2, 3).pipe(
  Stream.runCollect // Collect to array
)

const sum = Stream.make(1, 2, 3).pipe(
  Stream.runFold(0, (acc, n) => acc + n)
)

// Resource-safe streaming
const fileStream = Stream.acquireRelease(
  openFile("data.txt"),
  (file) => closeFile(file)
).pipe(
  Stream.flatMap((file) => Stream.fromReadable(file))
)
```

### 10. Schema Validation

```typescript
import { Schema } from "@effect/schema"
import { Effect } from "effect"

// Define schema
const User = Schema.Struct({
  id: Schema.Number,
  name: Schema.String,
  email: Schema.String.pipe(Schema.pattern(/^.+@.+$/)),
  age: Schema.Number.pipe(Schema.between(0, 120)),
})

// Infer type
type User = Schema.Schema.Type<typeof User>

// Decode (validate)
const program = Effect.gen(function* () {
  const raw = yield* fetchData()
  const user = yield* Schema.decode(User)(raw)
  return user
})

// Transformations
const DateFromString = Schema.transform(
  Schema.String,
  Schema.Date,
  {
    decode: (s) => new Date(s),
    encode: (d) => d.toISOString()
  }
)

// Branded types
const UserId = Schema.Number.pipe(Schema.brand("UserId"))
type UserId = Schema.Schema.Type<typeof UserId>
```

### 11. Scheduling

```typescript
import { Effect, Schedule } from "effect"

// Built-in schedules
const fixed = Schedule.spaced("1 second")
const exponential = Schedule.exponential("100 millis", 2.0)
const fibonacci = Schedule.fibonacci("100 millis")
const limited = Schedule.recurs(5)

// Combine schedules
const combined = Schedule.exponential("100 millis").pipe(
  Schedule.intersect(Schedule.recurs(5)),
  Schedule.jittered
)

// Retry with schedule
const robust = fetchData().pipe(
  Effect.retry({
    schedule: combined,
    while: (error) => error.retryable
  })
)

// Repeat with schedule
const repeated = checkStatus().pipe(
  Effect.repeat(Schedule.spaced("5 seconds"))
)
```

### 12. Testing

```typescript
import { it, expect } from "@effect/vitest"
import { Effect, Layer, TestClock } from "effect"

// Test with Effect
it.effect("should find user by id", () =>
  Effect.gen(function* () {
    const service = yield* UserService
    const user = yield* service.findById("123")
    expect(user.name).toBe("Test User")
  }).pipe(Effect.provide(TestLayer))
)

// Test with TestClock
it.effect("should handle time-dependent logic", () =>
  Effect.gen(function* () {
    const fiber = yield* Effect.fork(
      Effect.sleep("5 minutes").pipe(
        Effect.flatMap(() => performAction())
      )
    )

    // Advance test clock
    yield* TestClock.adjust("5 minutes")

    const result = yield* Fiber.join(fiber)
    expect(result).toBe(expectedValue)
  })
)
```

## Common Combinators

| Combinator | Purpose |
|------------|---------|
| `Effect.map` | Transform success value |
| `Effect.flatMap` | Chain dependent effects |
| `Effect.tap` | Side effect without changing value |
| `Effect.catchAll` | Handle all errors |
| `Effect.catchTag` | Handle specific error by tag |
| `Effect.retry` | Retry on failure |
| `Effect.timeout` | Add timeout |
| `Effect.all` | Run effects in parallel |
| `Effect.race` | First to complete wins |
| `Effect.fork` | Run in background fiber |

## Running Effects

```typescript
// Run as Promise
await Effect.runPromise(effect)

// Run synchronously
Effect.runSync(effect)

// Run with callback
Effect.runCallback(effect, (exit) => {
  // Handle exit
})

// Run as forked fiber
const fiber = Effect.runFork(effect)
```

## Best Practices

1. **Prefer Effect.gen**: More readable than pipe for sequential logic
2. **Use Tagged Errors**: Enable type-safe error handling with `catchTag`
3. **Keep Service Ops Pure**: Service methods should return `Effect<A, E, never>`
4. **Layer Composition**: Build layers hierarchically
5. **Test with Layers**: Use test layers for easy mocking
6. **Scope Resources**: Use `Effect.scoped` for automatic cleanup
7. **Await All Promises**: Use `yield*` for every effect

## When to Use Effect

**Use Effect When:**
- Complex error handling requirements
- Multiple dependencies to manage
- Concurrent operations
- Resource management
- Comprehensive testing needs

**Skip Effect When:**
- Simple scripts
- Tight bundle constraints
- Team unfamiliar with FP

## Troubleshooting

### Type Errors with Context
- Ensure service implementations return `Effect<A, E, never>`
- Dependencies are internal to Layer implementation

### Missing Dependencies
- Check all required layers are provided
- Verify layer composition order

### Fiber Not Completing
- Ensure `Fiber.join` is called
- Check for unhandled errors in fiber

## KCG integration patterns (round-9 deep dive)

The 3 long-form references document Effect's integration
into the KCG stack. The synthesised patterns:

### 1. Effect → TanStack Start (isomorphic server fns)

The canonical pattern is `Effect.runPromise()` inside a
`createServerFn` handler:

```typescript
import { createServerFn } from "@tanstack/react-start";
import { Effect } from "effect";
import { z } from "zod";
import * as UserService from "./services/user";

const getUserEffect = (id: string) =>
  Effect.gen(function* (_) {
    const userService = yield* _(UserService.UserService);
    return yield* _(userService.getUser(id));
  });

export const getUser = createServerFn({ method: "GET" })
  .validator(zodValidator(z.object({ id: z.string() })))
  .handler(async ({ data }) =>
    Effect.runPromise(
      getUserEffect(data.id).pipe(
        Effect.provide(UserService.UserServiceLive),
      ),
    ),
  );
```

**Loader caveat:** TanStack Start **loaders** are
isomorphic (run on server during SSR **and** on client
during navigation). Either use `createServerFn` for
server-only Effect code, or ensure your Effect services
work in both environments.

For validation, swap Zod for **Effect Schema** to keep the
error type in the Effect channel:

```typescript
const effectMiddleware = createMiddleware().server(
  async ({ next, data }) => {
    const validated = await Effect.runPromise(
      Schema.decodeUnknown(UserSchema)(data),
    );
    return next({ context: { validated } });
  },
);
```

### 2. Effect → Convex (Confect / @maple/convex-effect)

Two mature community wrappers bridge Convex's Promise
API to Effect:

| Library | Approach | Best for |
|:--|:--|:--|:--|
| **Confect** (`@rjdellecese/confect`) | Deep integration with Effect Schema; replaces Convex validators | New projects fully on Effect |
| **@maple/convex-effect** | Lightweight 1:1 API mapping | Existing Convex projects adding Effect services |

**Critical tsconfig** for Confect: set
`exactOptionalPropertyTypes: false` (a `convex-js`
limitation, not Confect's). This conflicts with Effect
Schema's recommended `true`, so document the trade-off in
your `tsconfig.json`.

**Where Effect shines in Convex** (in increasing order of
value):

1. **Actions** — full Effect.gen, can do I/O, scheduling,
   external APIs. The action returns a Promise at the
   Convex boundary; inside, you have full Effect
   composition
2. **Mutations** — Effect.gen works, but you must keep it
   deterministic (no `Effect.tryPromise` against an
   external API inside a mutation)
3. **Queries** — same determinism constraint; Effect is
   useful for type-safe data shaping but no I/O

### 3. Effect 3.x quick reference (the essentials)

The 2,400-line `comprehensive-research.md` covers the
whole surface. The minimum to be productive in KCG:

```typescript
// Service definition
class UserRepository extends Context.Tag("UserRepository")<
  UserRepository,
  { findById: (id: string) => Effect.Effect<User, NotFoundError> }
>() {}

// Layer (live impl)
const UserRepositoryLive = Layer.effect(
  UserRepository,
  Effect.gen(function* () {
    const db = yield* Database;
    return {
      findById: (id) =>
        Effect.gen(function* () {
          const row = yield* db.query("SELECT * FROM users WHERE id = $1", [id]);
          if (!row) return yield* Effect.fail(new NotFoundError({ id }));
          return row;
        }),
    };
  }),
);

// Tagged error
class NotFoundError extends Data.TaggedError("NotFoundError")<{
  readonly id: string;
}> {}

// Compose
const main = program.pipe(
  Effect.provide(Layer.merge(DatabaseLive, UserRepositoryLive)),
  Effect.catchTag("NotFoundError", (e) => Effect.succeed(null)),
);

Effect.runPromise(main);
```

**Combinators to memorise:** `Effect.gen` (generator
syntax for sequential logic), `Effect.all([...], {
concurrency: 5 })` (parallel with limit), `Effect.race(a,
b)` (first wins), `Effect.catchTag("Foo", handler)`
(type-safe error handling), `Effect.timeout("5s")`,
`Effect.fork` (background fiber), `Effect.scoped` (auto
cleanup).

### 4. When to use Effect in KCG

**Use Effect when:**

- The handler has > 2 dependencies (services, repos,
  caches) — Layer composition beats manual DI
- You need type-safe error handling across the call chain
- The function does I/O and you want retry / timeout /
  circuit-breaker baked in
- The team is comfortable with FP

**Skip Effect when:**

- The handler is a 5-line CRUD wrapper
- The team has no FP experience (steep learning curve)
- The bundle size matters (Effect is ~50 KB minzipped)

In the KCG stack, Effect is the **canonical choice for
sruth/cianfhoghlaim/web server functions** (curriculum, leabharlann,
agent handlers) and the **Convex Actions** that wrap
external LLM calls.

See `references/comprehensive-research.md` for the full
2,400-line reference, and `references/tanstack-start-integration.md`
/ `references/convex-integration.md` for the integration
deep-dives.

## Resources

- **Documentation**: https://effect.website
- **API Reference**: https://effect-ts.github.io/effect/
- **GitHub**: https://github.com/Effect-TS/effect
- **Discord**: Active community support
