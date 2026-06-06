/**
 * Better Auth Server Configuration with SIWE (Sign In With Ethereum)
 *
 * Implements ERC-4361 standard for Ethereum wallet authentication
 * Supports multi-chain: Ethereum, Polygon, Arbitrum, Base, Cronos
 * Uses Drizzle ORM for persistence
 */

import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { siwe } from "better-auth/plugins";
import { generateRandomString } from "better-auth/crypto";
import { verifyMessage, createPublicClient, http, type Address } from "viem";
import { mainnet } from "viem/chains";
import { db, user, session, account, verification } from "../../db";

// Create viem client for ENS lookups
const viemClient = createPublicClient({
  chain: mainnet,
  transport: http(process.env.MAINNET_RPC_URL || "https://eth.llamarpc.com"),
});

// Supported chains for SIWE
export const SUPPORTED_CHAINS = {
  1: "Ethereum",
  25: "Cronos",
  137: "Polygon",
  8453: "Base",
  42161: "Arbitrum",
  10: "Optimism",
  43114: "Avalanche",
  56: "BNB Chain",
} as const;

export type SupportedChainId = keyof typeof SUPPORTED_CHAINS;

// Validate if chain is supported
export function isSupportedChain(chainId: number): chainId is SupportedChainId {
  return chainId in SUPPORTED_CHAINS;
}

export const auth = betterAuth({
  // Database configuration using Drizzle adapter
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: {
      user,
      session,
      account,
      verification,
    },
  }),

  // App configuration
  appName: "Crypteolas",
  baseURL: process.env.BETTER_AUTH_URL || process.env.APP_URL || "http://localhost:3000",
  secret: process.env.BETTER_AUTH_SECRET || process.env.AUTH_SECRET,

  // Email configuration (disabled for Web3-first auth)
  emailAndPassword: {
    enabled: false,
  },

  // Social providers (optional, for non-Web3 users)
  socialProviders: {
    github: {
      enabled: !!process.env.GITHUB_CLIENT_ID,
      clientId: process.env.GITHUB_CLIENT_ID || "",
      clientSecret: process.env.GITHUB_CLIENT_SECRET || "",
    },
  },

  plugins: [
    siwe({
      // Domain for SIWE message generation
      domain: process.env.APP_DOMAIN || "crypto.localhost",

      // Email domain for creating accounts when not anonymous
      emailDomainName: process.env.EMAIL_DOMAIN || "crypto.local",

      // Allow sign-in without email (Web3-native)
      anonymous: true,

      // Statement shown in wallet signature request
      statement: "Sign in to Crypteolas - Your DeFi Analytics Platform",

      // Generate cryptographically secure nonce
      getNonce: async () => {
        const nonce = generateRandomString(32);
        return nonce;
      },

      // Verify SIWE message signature using viem
      verifyMessage: async ({ message, signature, address }) => {
        try {
          const isValid = await verifyMessage({
            address: address as Address,
            message,
            signature: signature as `0x${string}`,
          });
          return isValid;
        } catch (error) {
          console.error("SIWE verification failed:", error);
          return false;
        }
      },

      // ENS name and avatar lookup
      ensLookup: async ({ walletAddress }) => {
        try {
          const ensName = await viemClient.getEnsName({
            address: walletAddress as Address,
          });

          let ensAvatar: string | null = null;
          if (ensName) {
            ensAvatar = await viemClient.getEnsAvatar({
              name: ensName,
            });
          }

          return {
            name: ensName || walletAddress,
            avatar: ensAvatar || "",
          };
        } catch (error) {
          console.error("ENS lookup failed:", error);
          return {
            name: walletAddress,
            avatar: "",
          };
        }
      },

      // Hook: after successful sign-in, update user with Web3 data
      onSignIn: async ({ user: signedInUser, siweData }) => {
        // You can access chain ID and other SIWE data here
        console.log(`User ${signedInUser.id} signed in from wallet ${siweData?.address}`);
      },
    }),
  ],

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },

  // Rate limiting
  rateLimit: {
    window: 60, // 1 minute
    max: 100,   // 100 requests per minute
  },

  // Advanced options
  advanced: {
    // Use secure cookies in production
    useSecureCookies: process.env.NODE_ENV === "production",
    // Cookie domain for subdomain support
    cookieDomain: process.env.COOKIE_DOMAIN,
  },

  // Trusted origins for CORS
  trustedOrigins: [
    process.env.APP_URL || "http://localhost:3000",
    ...(process.env.TRUSTED_ORIGINS?.split(",") || []),
  ],
});

export type Auth = typeof auth;

// Helper functions for server-side auth checks

/**
 * Get session from request headers
 */
export async function getSession(request: Request) {
  const sessionData = await auth.api.getSession({
    headers: request.headers,
  });
  return sessionData;
}

/**
 * Require authenticated session (throws if not authenticated)
 */
export async function requireSession(request: Request) {
  const sessionData = await getSession(request);
  if (!sessionData?.session || !sessionData?.user) {
    throw new Error("Unauthorized: No valid session");
  }
  return sessionData;
}

/**
 * Get wallet address from session
 */
export async function getWalletAddress(request: Request): Promise<string | null> {
  const sessionData = await getSession(request);
  // The wallet address is stored in the user's accounts for SIWE
  // Or directly on the user if we've extended the schema
  return sessionData?.user?.walletAddress || null;
}

/**
 * Validate that the session user owns the specified wallet
 */
export async function validateWalletOwnership(
  request: Request,
  walletAddress: string
): Promise<boolean> {
  const sessionWallet = await getWalletAddress(request);
  if (!sessionWallet) return false;
  return sessionWallet.toLowerCase() === walletAddress.toLowerCase();
}
