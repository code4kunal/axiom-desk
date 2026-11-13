"use client";

import { useSyncExternalStore } from "react";
import { shell } from "./content";
import { readChoice, setTheme, subscribeChoice, type ThemeChoice } from "./theme";

const next: Record<ThemeChoice, ThemeChoice> = { system: "dark", dark: "light", light: "system" };

// Interim control: cycles System → Dark → Light until the theme menu replaces the click.
export function ThemeButton() {
  const choice = useSyncExternalStore(subscribeChoice, readChoice, () => "system" as const);
  return (
    <button
      type="button"
      onClick={() => setTheme(next[choice])}
      className="flex h-12 w-full items-center justify-center whitespace-nowrap rounded-2 border border-ink-dim px-4 font-body text-ui font-medium text-ink hover:border-ink md:w-auto md:self-start"
    >
      {shell.theme} · {shell.themeChoices[choice]}
    </button>
  );
}
