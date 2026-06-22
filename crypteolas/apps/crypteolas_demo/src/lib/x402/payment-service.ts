// TODO: implement the x402 payment service that records payment events to
// the local Drizzle-backed PostgreSQL database.

export interface PaymentRecord {
  id: string;
  userId: string;
  featureId: string;
  amount: string;
  asset: string;
  network: string;
  txHash: string;
  createdAt: string;
}

export async function recordPayment(_args: {
  userId: string;
  featureId: string;
  amount: string;
  asset: string;
  network: string;
  txHash: string;
}): Promise<PaymentRecord> {
  throw new Error("x402/payment-service: not yet implemented");
}
