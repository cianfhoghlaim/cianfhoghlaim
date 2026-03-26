import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://x402.payai.network";
  return [
    {
      url: `${siteUrl}/`,
      changeFrequency: "weekly",
      priority: 0.8,
    },
  ];
}


