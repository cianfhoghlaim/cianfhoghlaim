// TODO: implement the x402 payment middleware that gates premium API
// endpoints behind per-request USDC payments on Cronos/Base. The TanStack
// Start route handler can wrap a loader with this function.
//
// Reference: https://github.com/coinbase/x402

import type { RequestEvent } from "@tanstack/react-start/server";

export interface PaymentInfo {
  amount: string;
  asset: string;
  network: "cronos" | "base";
  txHash: string;
  payer: string;
}

export interface PaidHandlerContext {
  request: Request;
  paymentInfo: PaymentInfo;
}

export function withPayment<T = unknown>(
  _opts: { featureId: string; description: string; price?: string },
  _handler: (request: Request, paymentInfo: PaymentInfo) => Promise<Response> | Response,
) {
  return async (event: RequestEvent) => {
    throw new Error("x402/middleware: not yet implemented");
  };
}
