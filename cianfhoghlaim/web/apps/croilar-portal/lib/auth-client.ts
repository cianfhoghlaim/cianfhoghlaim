import { createAuthClient } from "better-auth/react";
import { genericOAuthClient } from "better-auth/client/plugins";

const baseURL = typeof window !== "undefined"
  ? window.location.origin
  : process.env.AUTH_BASE_URL || "http://localhost:3001";

export const authClient = createAuthClient({
  baseURL,
  plugins: [genericOAuthClient()],
});

export const {
  signIn,
  signUp,
  signOut,
  useSession,
  getSession,
} = authClient;
