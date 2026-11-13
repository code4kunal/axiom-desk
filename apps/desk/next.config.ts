import type { NextConfig } from "next";
import { PHASE_PRODUCTION_BUILD } from "next/constants";

export default function config(phase: string): NextConfig {
  // Rewrites are fixed at build: a production build without the API origin would ship a desk that cannot sign in.
  const api = process.env.AXIOM_API_ORIGIN;
  if (!api && phase === PHASE_PRODUCTION_BUILD) throw new Error("AXIOM_API_ORIGIN must be set for next build");
  return {
    reactStrictMode: true,
    poweredByHeader: false,
    // Same origin for the browser: /auth/* is proxied to the API, so its cookies stay first-party.
    rewrites: async () => (api ? [{ source: "/auth/:path*", destination: `${api}/auth/:path*` }] : []),
  };
}
