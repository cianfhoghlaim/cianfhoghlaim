import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { genericOAuth } from "better-auth/plugins";
// import { mcp } from "better-auth/plugins"; // Disabled - causes redirect loop
import { db } from "../db/drizzle";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    // mcp({ loginPage: "/login" }), // Disabled - causes redirect loop on /login
    genericOAuth({
      config: [
        {
          providerId: "pocketid",
          clientId: process.env.POCKETID_CLIENT_ID!,
          clientSecret: process.env.POCKETID_CLIENT_SECRET!,
          discoveryUrl: `${process.env.POCKETID_ISSUER || "https://auth.cianfhoghlaim.ie"}/.well-known/openid-configuration`,
          scopes: ["openid", "profile", "email", "groups"],
        },
      ],
    }),
  ],
  trustedOrigins: [
    "http://localhost:3001",
    "https://aleyum.cianfhoghlaim.ie",
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
