"use client";

import { ConnectButton, ConnectButtonProps } from "thirdweb/react";
import { client } from "../lib/thirdweb.client";
import { paymentChain, paymentToken } from "../lib/constants";
import { createWallet, inAppWallet } from "thirdweb/wallets";

const wallets = [
    inAppWallet({
        auth: {
            options: ["google", "email", "passkey"],
        }
    }),
    createWallet("io.metamask"),
    createWallet("com.coinbase.wallet"),
    createWallet("me.rainbow"),
    createWallet("io.rabby"),
    createWallet("com.okex.wallet"),
]

export const connectOptions: ConnectButtonProps = {
  client: client,
  wallets: wallets,
  chain: paymentChain,
  connectButton: {
    label: "Sign in",
  },
  supportedTokens: {
    [paymentChain.id]: [paymentToken],
  },
  detailsButton: {
    displayBalanceToken: {
      [paymentChain.id]: paymentToken.address,
    },
  },
}

export function SignInButton() {
  return (
    <ConnectButton
      {...connectOptions}
    />
  );
}
