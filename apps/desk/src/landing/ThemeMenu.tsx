"use client";

import { DropdownMenu } from "radix-ui";
import { useSyncExternalStore } from "react";
import { shell } from "./content";
import { readChoice, setTheme, subscribeChoice, type ThemeChoice } from "./theme";

const CHOICES = ["system", "dark", "light"] as const;

// Header theme control (R13, R14): System / Dark / Light as menu radio items; the choice persists and the
// head script applies it before the next first paint.
export function ThemeMenu() {
  const choice = useSyncExternalStore(subscribeChoice, readChoice, () => "system" as const);
  return (
    <DropdownMenu.Root modal={false}>
      <DropdownMenu.Trigger className="flex h-10 items-center gap-2 self-center whitespace-nowrap rounded-2 border border-hairline px-3 font-mono text-label font-medium uppercase text-ink hover:border-ink-dim data-[state=open]:border-ink">
        <span className="text-ink-dim max-sm:sr-only">{shell.theme}</span>
        <span aria-hidden className="text-ink-dim max-sm:hidden">
          ·
        </span>
        {shell.themeChoices[choice]}
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="end"
          sideOffset={4}
          className="overlay overlay-menu z-50 min-w-[200px] rounded-2 border border-ink bg-raised p-1"
        >
          <DropdownMenu.RadioGroup value={choice} onValueChange={(v) => setTheme(v as ThemeChoice)}>
            {CHOICES.map((c) => (
              <DropdownMenu.RadioItem
                key={c}
                value={c}
                className="relative flex h-12 cursor-default items-center rounded-1 pr-4 pl-8 font-body text-ui font-medium text-ink outline-none select-none data-[highlighted]:bg-ground data-[highlighted]:outline-2 data-[highlighted]:outline-offset-[-2px] data-[highlighted]:outline-brass-line"
              >
                <DropdownMenu.ItemIndicator className="absolute left-3 size-1.5 bg-ink" />
                {shell.themeChoices[c]}
              </DropdownMenu.RadioItem>
            ))}
          </DropdownMenu.RadioGroup>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
