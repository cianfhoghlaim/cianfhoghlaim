import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  transpilePackages: ['geist'],
  images: {
    remotePatterns: [
      {
        hostname: 'vercel.com',
      },
    ],
  },
  webpack: (config) => {
    config.externals.push("pino-pretty", "lokijs", "encoding");
    return config;
  },
};

export default nextConfig;
