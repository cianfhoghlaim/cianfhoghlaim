export default {
  providers: [
    {
      domain: process.env.BETTER_AUTH_ISSUER_URL!,
      applicationID: process.env.BETTER_AUTH_CLIENT_ID!,
    },
  ],
};
