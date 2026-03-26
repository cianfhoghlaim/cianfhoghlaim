import { createThirdwebClient } from "thirdweb";

export const serverClient = createThirdwebClient({
  secretKey: process.env.THIRDWEB_SECRET_KEY!,
});

export const serverWalletAddress = process.env.THIRDWEB_SERVER_WALLET_ADDRESS!;