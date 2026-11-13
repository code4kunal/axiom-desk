import type { Metadata } from "next";
import { Anek_Latin, Eczar, Martian_Mono } from "next/font/google";
import type { ReactNode } from "react";
import { meta, shell } from "@/landing/content";
import { Nav } from "@/landing/Nav";
import { Footer } from "@/landing/sections/Footer";
import { themeScript } from "@/landing/theme";
import { pinScript } from "@/landing/hero/gate";
import { posterPreloadScript } from "@/landing/hero/Poster";
import "./globals.css";

const display = Eczar({ weight: ["700", "800"], subsets: ["latin"], display: "optional", variable: "--ff-display" });
const body = Anek_Latin({ weight: ["400", "500", "600"], subsets: ["latin"], display: "swap", variable: "--ff-body" });
const mono = Martian_Mono({ weight: ["400", "500"], subsets: ["latin"], display: "swap", variable: "--ff-mono" });

export const metadata: Metadata = {
  // shortcut: falls back to localhost until a domain exists; set SITE_URL at deploy so cards resolve.
  metadataBase: new URL(process.env.SITE_URL ?? "http://localhost:3000"),
  title: { default: meta.title, template: "%s · Axiom" },
  description: meta.description,
  openGraph: {
    title: meta.ogTitle,
    description: meta.ogDescription,
    type: "website",
    locale: "en_IN",
    images: [{ url: "/og/og-1200x630.jpg", width: 1200, height: 630, alt: meta.ogDescription }],
  },
  twitter: { card: "summary_large_image", title: meta.ogTitle, description: meta.ogDescription, images: ["/og/og-1200x630.jpg"] },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // data-theme is set by the head script before hydration, so React must not flag it.
    <html lang="en-IN" suppressHydrationWarning className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <head>
        {/* Async, so it runs as soon as parsed instead of waiting for the stylesheet like the inline script
            below: the LCP poster request starts with the fonts, not after the CSS. It resolves the theme itself. */}
        <script async src={`data:text/javascript,${encodeURIComponent(themeScript + posterPreloadScript)}`} />
        <script dangerouslySetInnerHTML={{ __html: `${themeScript}document.documentElement.dataset.js="";${pinScript}` }} />
      </head>
      <body>
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:fixed focus:inset-x-0 focus:top-0 focus:z-30 focus:flex focus:h-12 focus:items-center focus:border-b focus:border-hairline focus:bg-raised focus:px-4 focus:text-ui"
        >
          {shell.skip}
        </a>
        <Nav />
        <main id="main">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
