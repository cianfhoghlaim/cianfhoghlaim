import { arbitrum } from "thirdweb/chains";
import { getDefaultToken } from "thirdweb/react";

export const PRICE_PER_INFERENCE_TOKEN_WEI = 1; // 0.000001 USDC
export const MAX_INFERENCE_TOKENS_PER_CALL = 10000; // 10k inference tokens per query max

export const paymentChain = arbitrum;
export const paymentToken = getDefaultToken(paymentChain, "USDC")!;