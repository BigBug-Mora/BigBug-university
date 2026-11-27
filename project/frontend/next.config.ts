import type { NextConfig } from "next";

const config: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  // Keep the configured OAuth callback origin when Next.js builds a request URL.
  skipProxyUrlNormalize: true,
  async headers() {
    return ["/buyer/:path*", "/seller/:path*", "/sign-in", "/api/auth/:path*"].map(
      (source) => ({
        source,
        headers: [{ key: "Cache-Control", value: "private, no-store" }],
      }),
    );
  },
};

export default config;
