/**
 * Effect-TS Convex client wrapper
 *
 * Wraps ConvexReactClient in an Effect-TS Layer so it can be:
 * - Mocked in unit tests (provide a test layer with canned responses)
 * - Replaced with a streaming SSE variant
 * - Combined with other Effect services (Langfuse tracing, BAML extraction)
 *
 * The default layer lazily constructs ConvexReactClient from VITE_CONVEX_URL.
 * Override at test time with `Layer.succeed(ConvexClient, mockClient)`.
 *
 * Pattern: https://github.com/Effect-TS/effect (Effect 3.x)
 */
import { Effect, Layer, Context, Redacted } from "effect";
import { ConvexReactClient } from "convex/react";

export interface ConvexClientService {
  readonly client: ConvexReactClient | null;
  readonly url: Redacted.Redacted<string> | null;
}

export class ConvexClient extends Context.Tag("ConvexClient")<
  ConvexClient,
  ConvexClientService
>() {}

/**
 * Production layer: read VITE_CONVEX_URL, build client once.
 * In SSR / build / test, VITE_CONVEX_URL may be undefined, in which
 * case the client is null and consumers fall back to mock data.
 */
export const ConvexClientLive = Layer.effect(
  ConvexClient,
  Effect.gen(function* () {
    const url = process.env.VITE_CONVEX_URL;
    if (!url) {
      return ConvexClient.of({ client: null, url: null });
    }
    const redacted = Redacted.make(url);
    const client = new ConvexReactClient(url);
    return ConvexClient.of({ client, url: redacted });
  }),
);

/**
 * Test layer: provide a stub client. Use with `Layer.succeed` in tests.
 */
export const ConvexClientTest = (stubUrl = "https://test.convex.cloud") =>
  Layer.succeed(
    ConvexClient,
    ConvexClient.of({
      client: new ConvexReactClient(stubUrl),
      url: Redacted.make(stubUrl),
    }),
  );
