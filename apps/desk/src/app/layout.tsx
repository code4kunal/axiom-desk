import type { Metadata } from "next";
import { Hind, Martel, Martian_Mono } from "next/font/google";
import type { ReactNode } from "react";
import { meta, shell } from "@/landing/content";
import { Nav } from "@/landing/Nav";
import { Footer } from "@/landing/sections/Footer";
import { themeScript } from "@/landing/theme";
import "./globals.css";

const display = Martel({ weight: ["700", "800"], subsets: ["latin"], display: "optional", variable: "--ff-display" });
const body = Hind({ weight: ["400", "500", "600"], subsets: ["latin"], display: "swap", variable: "--ff-body" });
const mono = Martian_Mono({ weight: ["400", "500"], subsets: ["latin"], display: "swap", variable: "--ff-mono" });

export const metadata: Metadata = {
  title: { default: meta.title, template: "%s · Axiom" },
  description: meta.description,
  openGraph: { title: meta.ogTitle, description: meta.ogDescription, type: "website", locale: "en_IN" },
  twitter: { card: "summary_large_image", title: meta.ogTitle, description: meta.ogDescription },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    // data-theme is set by the head script before hydration, so React must not flag it.
    <html lang="en-IN" suppressHydrationWarning className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: `${themeScript}document.documentElement.dataset.js="";` }} />
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
