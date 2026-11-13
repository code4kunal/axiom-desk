import type { Metadata } from "next";
import { terms } from "@/landing/content";
import { LegalPage } from "@/landing/LegalPage";

export const metadata: Metadata = { title: terms.title, robots: { index: false } };

export default function Terms() {
  return <LegalPage copy={terms} />;
}
