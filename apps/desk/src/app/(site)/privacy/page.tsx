import type { Metadata } from "next";
import { privacy } from "@/landing/content";
import { LegalPage } from "@/landing/LegalPage";

export const metadata: Metadata = { title: privacy.title, robots: { index: false } };

export default function Privacy() {
  return <LegalPage copy={privacy} />;
}
