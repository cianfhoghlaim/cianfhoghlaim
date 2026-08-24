/**
 * TanStack AI + TanStack DB + TanStack Form — the 2026 reactive stack.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. The 5 web apps consume this module to access the canonical
 * TanStack AI agent client, the reactive DB collection API, and the
 * form state management.
 */

import { useChat } from "@tanstack/ai/react";
import { useLiveQuery } from "@tanstack/db/react";
import { useForm } from "@tanstack/react-form";

/**
 * The canonical Cianfhoghlaim AI chat client. Backed by the
 * Convex agent table (see `web/packages/db/convex/schema.ts`).
 */
export function useCianfhoghlaimChat() {
  return useChat({
    api: "/api/chat",
    credentials: "include",
  });
}

/**
 * Reactive DB query (TanStack DB) — the successor to TanStack Query for
 * Convex-backed tables. Used by the 5 web apps for live-data subscriptions.
 */
export function useCianfhoghlaimLiveQuery<T>(
  queryFn: () => Promise<T[]>,
  deps: unknown[] = [],
): readonly [T[] | undefined, boolean, Error | null] {
  return useLiveQuery(queryFn, deps);
}

/**
 * Canonical form state for Cianfhoghlaim form submissions.
 * Replaces Formik / React Hook Form / custom form state.
 */
export function useCianfhoghlaimForm<TFormSchema>(
  schema: TFormSchema,
  options: Parameters<typeof useForm<TFormSchema>>[1] = {} as any,
) {
  return useForm<TFormSchema>({
    validators: { onChange: schema as any },
    ...options,
  });
}

export { useChat, useLiveQuery, useForm };
