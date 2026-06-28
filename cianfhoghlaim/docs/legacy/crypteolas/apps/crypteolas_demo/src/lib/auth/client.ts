// TODO: implement Better Auth client integration with SIWE (Sign In With
// Ethereum). Until then this stub exposes a typed interface so the React
// components can import it without breaking. See
// tuatha/apps/crypteolas_demo/STATUS.md.

export interface AuthClient {
  signIn: (args: { walletAddress?: string; email?: string }) => Promise<{ sessionId: string }>;
  signOut: () => Promise<void>;
  getSession: () => Promise<{ sessionId: string; userId: string } | null>;
  onAuthStateChange: (cb: (session: { sessionId: string; userId: string } | null) => void) => () => void;
}

export function getAuthClient(): AuthClient {
  return {
    async signIn() {
      throw new Error("auth/client: not yet implemented");
    },
    async signOut() {
      throw new Error("auth/client: not yet implemented");
    },
    async getSession() {
      return null;
    },
    onAuthStateChange() {
      return () => {};
    },
  };
}
