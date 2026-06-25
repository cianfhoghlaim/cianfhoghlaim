// Type shims for TanStack Start 1.145 server functions
// The createServerFn type defaults to OptionalFetcher<undefined, undefined>
// which forces callers to pass no arguments. These casts make the actual
// call pattern (fetcher({ data: TInput })) work without using `any` everywhere.

declare module "@tanstack/react-start" {
  interface ServerFnBuilder<TRegister, TMethod, TMiddlewares, TInputValidator> {
    handler: <T>(fn: (opts: { data?: unknown; context: unknown; signal: AbortSignal }) => Promise<T> | T) => unknown;
  }
}

export {};
