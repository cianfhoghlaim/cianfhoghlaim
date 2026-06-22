// TODO: implement Better Auth server integration with SIWE (Sign In With
// Ethereum). Until then this stub exposes a typed interface.

export interface AuthServer {
  verifySiwe: (message: string, signature: string) => Promise<{ address: string }>;
  createSession: (userId: string) => Promise<{ sessionId: string }>;
  revokeSession: (sessionId: string) => Promise<void>;
}

export function getAuthServer(): AuthServer {
  return {
    async verifySiwe() {
      throw new Error("auth/server: not yet implemented");
    },
    async createSession() {
      throw new Error("auth/server: not yet implemented");
    },
    async revokeSession() {
      throw new Error("auth/server: not yet implemented");
    },
  };
}
