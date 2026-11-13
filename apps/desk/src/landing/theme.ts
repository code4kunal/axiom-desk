export type Theme = "dark" | "light";
export type ThemeChoice = Theme | "system";

export const THEME_KEY = "axiom-theme";

// Self-contained (no outer references): its source is inlined into the head script.
export function resolveTheme(read: () => string | null, systemDark: boolean): Theme {
  try {
    const v = read();
    if (v === "dark" || v === "light") return v;
  } catch {
    // Storage blocked (private mode, sandboxed iframe): the system preference decides.
  }
  return systemDark ? "dark" : "light";
}

// Runs blocking in <head> so the first painted frame already has the right theme.
export const themeScript = `document.documentElement.dataset.theme=(${resolveTheme.toString()})(function(){return localStorage.getItem(${JSON.stringify(THEME_KEY)})},matchMedia("(prefers-color-scheme: dark)").matches);`;

let current: ThemeChoice | null = null;
const listeners = new Set<() => void>();

export function readChoice(): ThemeChoice {
  if (current) return current;
  try {
    const v = localStorage.getItem(THEME_KEY);
    return v === "dark" || v === "light" ? v : "system";
  } catch {
    return "system";
  }
}

export function subscribeChoice(fn: () => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

// shortcut: "system" is resolved once per call, not live; add a matchMedia change listener if visitors ask.
export function setTheme(choice: ThemeChoice): void {
  current = choice;
  try {
    if (choice === "system") localStorage.removeItem(THEME_KEY);
    else localStorage.setItem(THEME_KEY, choice);
  } catch {
    // Choice can't persist; still apply it for this page view.
  }
  listeners.forEach((fn) => fn());
  document.documentElement.dataset.theme =
    choice === "system" ? resolveTheme(() => null, matchMedia("(prefers-color-scheme: dark)").matches) : choice;
}
