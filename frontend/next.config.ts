import type { NextConfig } from "next";

// The backend URL as seen from the Next.js server process (not the browser).
// In docker-compose this is the service name (e.g. http://backend:8000); locally
// it's http://localhost:8000; on Render it's the backend service's full external
// URL (e.g. via `fromService: { envVarKey: RENDER_EXTERNAL_URL }` in render.yaml).
// The browser never talks to this URL directly — it only ever calls /api/... on
// its own origin, which Next.js proxies here. This keeps auth cookies same-origin
// with zero CORS configuration needed.
const rawBackendUrl = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";
// Defensive: if this ever arrives as a bare host (no scheme) from a platform's
// service-reference mechanism, assume https rather than failing the rewrite.
const BACKEND_INTERNAL_URL = /^https?:\/\//.test(rawBackendUrl)
  ? rawBackendUrl
  : `https://${rawBackendUrl}`;

const nextConfig: NextConfig = {
  // Without this, Next.js's own trailing-slash redirect fires BEFORE the rewrite
  // below, stripping the slash from e.g. /api/v1/auth/register/ — then Django's
  // APPEND_SLASH middleware redirects it right back, causing an infinite
  // redirect loop between the two. This makes the rewrite pass the path through
  // untouched so Django's own slash handling is the only one that applies.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_INTERNAL_URL}/api/:path*`,
      },
      {
        source: "/media/:path*",
        destination: `${BACKEND_INTERNAL_URL}/media/:path*`,
      },
    ];
  },
};

export default nextConfig;
