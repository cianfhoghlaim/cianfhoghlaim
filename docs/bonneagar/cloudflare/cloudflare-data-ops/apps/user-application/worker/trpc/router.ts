import { t } from "@/worker/trpc/trpc-instance";
import { linksTrpcRoutes } from "@/worker/trpc/routers/links";
import { evaluationsTrpcRoutes } from "@/worker/trpc/routers/evaluations";

export const appRouter = t.router({
  links: linksTrpcRoutes,
  evaluations: evaluationsTrpcRoutes,
});

export type AppRouter = typeof appRouter;
