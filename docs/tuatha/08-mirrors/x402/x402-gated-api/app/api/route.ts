import { settlePayment, facilitator } from "thirdweb/x402";
import { createThirdwebClient } from "thirdweb";
import { abstractTestnet, } from "thirdweb/chains";

const client = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY!,
});

const thirdwebFacilitator = facilitator({
  client,
  serverWalletAddress: process.env.THIRDWEB_SERVER_WALLET_ADDRESS!,
});

export async function GET(request: Request) {
  const paymentData = request.headers.get("x-payment");

  // Verify and process the payment
  const result = await settlePayment({
    resourceUrl: "http://localhost:3000/api",
    method: "GET",
    paymentData,
    payTo: process.env.THIRDWEB_SERVER_WALLET_ADDRESS!,
    network: abstractTestnet,
    price: {
      amount: "10000",
      asset: {
        address: "0xe4C7fBB0a626ed208021ccabA6Be1566905E2dFc",
      },
    },
    facilitator: thirdwebFacilitator,
  });

  if (result.status === 200) {
    // Payment verified and settled successfully
    return Response.json({ data: "premium content" });
  } else {
    // Payment required
    return Response.json(result.responseBody, {
      status: result.status,
      headers: result.responseHeaders,
    });
  }
}
