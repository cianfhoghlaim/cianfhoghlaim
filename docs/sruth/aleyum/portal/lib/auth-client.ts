import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: typeof window !== "undefined"
    ? window.location.origin
    : process.env.AUTH_BASE_URL || "http://localhost:3001",
});

export const {
  signIn,
  signOut,
  signUp,
  useSession,
} = authClient;
