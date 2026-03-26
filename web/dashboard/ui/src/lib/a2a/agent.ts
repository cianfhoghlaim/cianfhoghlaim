/**
 * A2A Agent for Celtic Education Platform
 *
 * Agent-to-agent communication wrapper that integrates with AG-UI protocol
 * for streaming responses from A2A-compatible education agents.
 */

import { randomUUID } from "./uuid";
import {
  convertAGUIMessagesToA2A,
  convertA2AEventToAGUIEvents,
  EventType,
  type BaseEvent,
} from "./utils";
import type {
  A2AMessage,
  A2AStreamEvent,
  A2AAgentRunResultSummary,
  ConvertedA2AMessages,
  MessageSendConfiguration,
  MessageSendParams,
  SurfaceTracker,
  AGUIMessage,
} from "./types";

/**
 * A2A Client interface for agent communication
 */
export interface A2AClient {
  sendMessage(params: MessageSendParams): Promise<A2AClientResponse>;
  sendMessageStream?(
    params: MessageSendParams
  ): AsyncGenerator<A2AStreamEvent, void, undefined>;
  resubscribeTask?(
    taskId: string
  ): AsyncGenerator<A2AStreamEvent, void, undefined>;
  isErrorResponse(response: A2AClientResponse): boolean;
}

export interface A2AClientResponse {
  result?: A2AStreamEvent;
  error?: {
    code?: number;
    message?: string;
  };
}

/**
 * Configuration for A2AAgent
 */
export interface A2AAgentConfig {
  client: A2AClient;
  debug?: boolean;
  agentName?: string;
}

/**
 * Input for running an agent
 */
export interface RunAgentInput {
  threadId: string;
  runId: string;
  messages?: AGUIMessage[];
}

/**
 * Event subscriber interface
 */
export interface EventSubscriber {
  next: (event: BaseEvent) => void;
  error?: (error: Error) => void;
  complete?: () => void;
}

const EXTENSION_URI = "https://a2ui.org/ext/a2a-ui/v0.1";

/**
 * A2A Agent class for Celtic education platform
 *
 * Wraps A2A client for seamless integration with AG-UI protocol,
 * enabling communication between education agents (curriculum,
 * research, translation, corpus, geospatial, statistics).
 */
export class A2AAgent {
  private readonly client: A2AClient;
  private readonly messageIdMap = new Map<string, string>();
  private readonly debug: boolean;
  private readonly agentName?: string;

  constructor(config: A2AAgentConfig) {
    if (!config.client) {
      throw new Error("A2AAgent requires a configured A2AClient instance.");
    }

    this.client = config.client;
    this.debug = config.debug ?? false;
    this.agentName = config.agentName;
    this.initializeExtension(this.client);
  }

  /**
   * Run the agent with the given input
   */
  async run(
    input: RunAgentInput,
    subscriber: EventSubscriber
  ): Promise<A2AAgentRunResultSummary> {
    const runStarted = {
      type: EventType.RUN_STARTED,
      threadId: input.threadId,
      runId: input.runId,
    };
    subscriber.next(runStarted);

    if (!input.messages?.length) {
      const runFinished = {
        type: EventType.RUN_FINISHED,
        threadId: input.threadId,
        runId: input.runId,
      };
      subscriber.next(runFinished);
      subscriber.complete?.();
      return { messages: [], rawEvents: [] };
    }

    try {
      const converted = this.prepareConversation(input);

      if (!converted.latestUserMessage) {
        const runFinished = {
          type: EventType.RUN_FINISHED,
          threadId: input.threadId,
          runId: input.runId,
        };
        subscriber.next(runFinished);
        subscriber.complete?.();
        return { messages: [], rawEvents: [] };
      }

      const sendParams = this.createSendParams(converted, input);
      const surfaceTracker = this.createSurfaceTracker();

      let result: A2AAgentRunResultSummary;

      try {
        result = await this.streamMessage(sendParams, subscriber, surfaceTracker);
      } catch (streamError) {
        if (this.debug) {
          console.warn("A2A streaming failed, falling back to blocking mode:", streamError);
        }
        result = await this.fallbackToBlocking(
          sendParams,
          subscriber,
          streamError as Error,
          surfaceTracker
        );
      }

      const runFinished = {
        type: EventType.RUN_FINISHED,
        threadId: input.threadId,
        runId: input.runId,
      };
      subscriber.next(runFinished);
      subscriber.complete?.();

      return result;
    } catch (error) {
      const runError = {
        type: EventType.RUN_ERROR,
        message: (error as Error).message ?? "Unknown A2A error",
      };
      subscriber.next(runError);
      subscriber.error?.(error as Error);
      throw error;
    }
  }

  /**
   * Run as an Observable-like async generator
   */
  async *runStream(input: RunAgentInput): AsyncGenerator<BaseEvent, A2AAgentRunResultSummary, undefined> {
    const events: BaseEvent[] = [];
    let resolvePromise: ((value: A2AAgentRunResultSummary) => void) | null = null;
    let rejectPromise: ((error: Error) => void) | null = null;

    const resultPromise = new Promise<A2AAgentRunResultSummary>((resolve, reject) => {
      resolvePromise = resolve;
      rejectPromise = reject;
    });

    const subscriber: EventSubscriber = {
      next: (event) => {
        events.push(event);
      },
      error: (error) => {
        rejectPromise?.(error);
      },
      complete: () => {
        // Completion handled by run()
      },
    };

    // Start the run in the background
    const runPromise = this.run(input, subscriber).then(
      (result) => {
        resolvePromise?.(result);
        return result;
      },
      (error) => {
        rejectPromise?.(error);
        throw error;
      }
    );

    // Yield events as they come in
    let lastIndex = 0;
    while (true) {
      // Check if there are new events
      while (lastIndex < events.length) {
        yield events[lastIndex];
        lastIndex++;
      }

      // Check if the run is complete
      const raceResult = await Promise.race([
        runPromise.then(() => "done" as const),
        new Promise<"continue">((resolve) => setTimeout(() => resolve("continue"), 10)),
      ]);

      if (raceResult === "done") {
        // Yield any remaining events
        while (lastIndex < events.length) {
          yield events[lastIndex];
          lastIndex++;
        }
        break;
      }
    }

    return await resultPromise;
  }

  private prepareConversation(input: RunAgentInput): ConvertedA2AMessages {
    return convertAGUIMessagesToA2A(input.messages ?? [], {
      contextId: input.threadId,
    });
  }

  private createSendParams(
    converted: ConvertedA2AMessages,
    input: RunAgentInput
  ): MessageSendParams {
    const latest = converted.latestUserMessage as A2AMessage;

    const message: A2AMessage = {
      ...latest,
      messageId: latest.messageId ?? randomUUID(),
      contextId: converted.contextId ?? input.threadId,
    };

    const configuration: MessageSendConfiguration = {
      acceptedOutputModes: ["text", "data"],
    };

    return {
      message,
      configuration,
    };
  }

  private async streamMessage(
    params: MessageSendParams,
    subscriber: EventSubscriber,
    surfaceTracker?: SurfaceTracker
  ): Promise<A2AAgentRunResultSummary> {
    if (!this.client.sendMessageStream) {
      throw new Error("Client does not support streaming");
    }

    const aggregatedText = new Map<string, string>();
    const rawEvents: A2AStreamEvent[] = [];
    const tracker = surfaceTracker ?? this.createSurfaceTracker();

    const stream = this.client.sendMessageStream(params);
    for await (const chunk of stream) {
      rawEvents.push(chunk);
      const events = convertA2AEventToAGUIEvents(chunk, {
        role: "assistant",
        messageIdMap: this.messageIdMap,
        onTextDelta: ({ messageId, delta }) => {
          aggregatedText.set(
            messageId,
            (aggregatedText.get(messageId) ?? "") + delta
          );
        },
        getCurrentText: (messageId) => aggregatedText.get(messageId),
        source: this.agentName ?? "a2a",
        surfaceTracker: tracker,
      });
      for (const event of events) {
        subscriber.next(event);
      }
    }

    return {
      messages: Array.from(aggregatedText.entries()).map(([messageId, text]) => ({
        messageId,
        text,
      })),
      rawEvents,
    };
  }

  private async fallbackToBlocking(
    params: MessageSendParams,
    subscriber: EventSubscriber,
    _error: Error,
    surfaceTracker?: SurfaceTracker
  ): Promise<A2AAgentRunResultSummary> {
    const configuration: MessageSendConfiguration = {
      ...params.configuration,
      acceptedOutputModes: params.configuration?.acceptedOutputModes ?? ["text"],
      blocking: true,
    };

    return this.blockingMessage(
      {
        ...params,
        configuration,
      },
      subscriber,
      surfaceTracker
    );
  }

  private async blockingMessage(
    params: MessageSendParams,
    subscriber: EventSubscriber,
    surfaceTracker?: SurfaceTracker
  ): Promise<A2AAgentRunResultSummary> {
    const response = await this.client.sendMessage(params);

    if (this.client.isErrorResponse(response)) {
      const errorMessage =
        response.error?.message ?? "Unknown error from A2A agent";
      if (this.debug) {
        console.error("A2A sendMessage error", response.error);
      }
      throw new Error(errorMessage);
    }

    const aggregatedText = new Map<string, string>();
    const rawEvents: A2AStreamEvent[] = [];
    const tracker = surfaceTracker ?? this.createSurfaceTracker();

    const result = response.result as A2AStreamEvent;
    rawEvents.push(result);

    const events = convertA2AEventToAGUIEvents(result, {
      role: "assistant",
      messageIdMap: this.messageIdMap,
      onTextDelta: ({ messageId, delta }) => {
        aggregatedText.set(
          messageId,
          (aggregatedText.get(messageId) ?? "") + delta
        );
      },
      getCurrentText: (messageId) => aggregatedText.get(messageId),
      source: this.agentName ?? "a2a",
      surfaceTracker: tracker,
    });

    for (const event of events) {
      subscriber.next(event);
    }

    return {
      messages: Array.from(aggregatedText.entries()).map(([messageId, text]) => ({
        messageId,
        text,
      })),
      rawEvents,
    };
  }

  private initializeExtension(client: A2AClient) {
    const addExtensionHeader = (headers: Headers) => {
      const existingValue = headers.get("X-A2A-Extensions") ?? "";
      const values = existingValue
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);

      if (!values.includes(EXTENSION_URI)) {
        values.push(EXTENSION_URI);
        headers.set("X-A2A-Extensions", values.join(", "));
      }
    };

    const patchFetch = () => {
      if (typeof globalThis === "undefined" || !globalThis.fetch) {
        return () => {};
      }

      const originalFetch = globalThis.fetch;
      const extensionFetch: typeof fetch = async (input, init) => {
        const headers = new Headers(init?.headers);
        addExtensionHeader(headers);
        const nextInit: RequestInit = {
          ...init,
          headers,
        };
        return originalFetch(input, nextInit);
      };

      globalThis.fetch = extensionFetch;

      return () => {
        globalThis.fetch = originalFetch;
      };
    };

    const wrapPromise = async <T>(operation: () => Promise<T>): Promise<T> => {
      const restore = patchFetch();
      try {
        return await operation();
      } finally {
        restore();
      }
    };

    const wrapStream = <T>(
      original:
        | ((...args: unknown[]) => AsyncGenerator<T, void, undefined>)
        | undefined
    ) => {
      if (!original) {
        return undefined;
      }

      return function wrapped(this: unknown, ...args: unknown[]) {
        const restore = patchFetch();
        const iterator = original.apply(this, args);

        const wrappedIterator = (async function* () {
          try {
            for await (const value of iterator) {
              yield value;
            }
          } finally {
            restore();
          }
        })();

        return wrappedIterator;
      };
    };

    const originalSendMessage = client.sendMessage.bind(client);
    client.sendMessage = (params) =>
      wrapPromise(() => originalSendMessage(params));

    if (client.sendMessageStream) {
      const originalSendMessageStream = client.sendMessageStream.bind(client);
      const wrappedSendMessageStream = wrapStream(originalSendMessageStream);
      if (wrappedSendMessageStream) {
        client.sendMessageStream =
          wrappedSendMessageStream as typeof client.sendMessageStream;
      }
    }

    if (client.resubscribeTask) {
      const originalResubscribeTask = client.resubscribeTask.bind(client);
      const wrappedResubscribeTask = wrapStream(originalResubscribeTask);
      if (wrappedResubscribeTask) {
        client.resubscribeTask =
          wrappedResubscribeTask as typeof client.resubscribeTask;
      }
    }
  }

  private createSurfaceTracker(): SurfaceTracker {
    const seenSurfaceIds = new Set<string>();
    return {
      has: (surfaceId: string) => seenSurfaceIds.has(surfaceId),
      add: (surfaceId: string) => {
        seenSurfaceIds.add(surfaceId);
      },
    };
  }
}

/**
 * Create an A2A client for a specific education agent endpoint
 */
export function createEducationA2AClient(
  baseUrl: string,
  agentType?: string
): A2AClient {
  const endpoint = agentType ? `${baseUrl}/agents/${agentType}` : baseUrl;

  return {
    async sendMessage(params: MessageSendParams): Promise<A2AClientResponse> {
      const response = await fetch(`${endpoint}/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        return {
          error: {
            code: response.status,
            message: `HTTP error: ${response.statusText}`,
          },
        };
      }

      const result = await response.json();
      return { result };
    },

    async *sendMessageStream(
      params: MessageSendParams
    ): AsyncGenerator<A2AStreamEvent, void, undefined> {
      const response = await fetch(`${endpoint}/message/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              return;
            }
            try {
              const event = JSON.parse(data) as A2AStreamEvent;
              yield event;
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    },

    isErrorResponse(response: A2AClientResponse): boolean {
      return response.error !== undefined;
    },
  };
}
