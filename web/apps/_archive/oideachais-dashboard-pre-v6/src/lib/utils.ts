/**
 * `~/lib/utils` — the local class-name helper.
 *
 * The shadcn-style components under `src/components/` import `cn` from
 * `~/lib/utils` by convention. The canonical implementation lives in the
 * shared UI package, so this module simply re-exports it rather than
 * duplicating the `clsx` + `tailwind-merge` composition.
 */

export { cn } from "@cianfhoghlaim/ui-kit";
