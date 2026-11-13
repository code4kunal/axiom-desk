import type { ReactNode } from "react";
import { Nav } from "@/landing/Nav";
import { Footer } from "@/landing/sections/Footer";

export default function SiteLayout({ children }: { children: ReactNode }) {
  return (
    <>
      <Nav />
      <main id="main">{children}</main>
      <Footer />
    </>
  );
}
