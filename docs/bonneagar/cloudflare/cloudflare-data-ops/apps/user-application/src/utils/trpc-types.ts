import type { inferRouterOutputs } from "@trpc/server";
import type { AppRouter } from "@/worker/trpc/router";

type TRPCOutput = inferRouterOutputs<AppRouter>;
export type LinkListItem = TRPCOutput["links"]["linkList"];
