"use client";

import { Dialog } from "radix-ui";
import { useRef, useState, type CSSProperties } from "react";
import { brokers, shell } from "./content";

const mailto = `mailto:${brokers.contact}?subject=${encodeURIComponent(brokers.subject)}`;

// R10: the desk address as text, Copy, and a mailto with the subject. No fields, nothing stored or sent.
// The trigger is a real mailto link, so it still works before hydration or without JS.
export function BrokerDialog({ className, style }: { className: string; style: CSSProperties }) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "copied" | "failed">("idle");
  const address = useRef<HTMLParagraphElement>(null);
  const copyButton = useRef<HTMLButtonElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  async function copy() {
    try {
      await navigator.clipboard.writeText(brokers.contact);
      setStatus("copied");
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setStatus("idle"), 2000);
    } catch {
      // Clipboard denied (permission or insecure context): select the text so the visitor can copy it.
      getSelection()?.selectAllChildren(address.current!);
      setStatus("failed");
    }
  }

  return (
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        clearTimeout(timer.current);
        setStatus("idle");
      }}
    >
      <Dialog.Trigger asChild>
        <a href={mailto} data-reveal style={style} className={className} onClick={(e) => {
            // Stops the mailto navigation; Radix then skips its own toggle, so open here.
            e.preventDefault();
            setOpen(true);
          }}>
          {brokers.action}
        </a>
      </Dialog.Trigger>
      <Dialog.Portal>
        {/* Opaque ground, not a scrim: DESIGN.md bans alpha, and the section headline must not show through. */}
        <Dialog.Overlay className="overlay fixed inset-0 z-50 bg-ground" style={{ "--rise": "0px" } as CSSProperties} />
        <Dialog.Content
          onOpenAutoFocus={(e) => {
            // Start on the primary action, not on Close.
            e.preventDefault();
            copyButton.current?.focus();
          }}
          className="overlay fixed inset-0 z-50 m-auto h-fit w-[min(480px,calc(100vw-32px))] rounded-2 border border-ink bg-raised p-4 md:p-6">
          <div className="flex items-start justify-between gap-4">
            <Dialog.Title className="pt-2 font-display text-[28px] leading-[1.05] font-bold tracking-[-0.015em] text-ink">
              {brokers.action}
            </Dialog.Title>
            <Dialog.Close className="-mr-2 flex h-12 min-w-12 items-center justify-center px-2 font-mono text-label font-medium uppercase text-ink-dim hover:text-ink">
              {shell.close}
            </Dialog.Close>
          </div>
          <Dialog.Description className="mt-2 text-body text-ink-dim">{brokers.dialogLede}</Dialog.Description>
          <p
            ref={address}
            className="mt-6 rounded-1 border border-hairline bg-ground px-4 py-3 font-mono text-[20px] font-medium break-all text-ink select-all"
          >
            {brokers.contact}
          </p>
          {status === "failed" && <p className="mt-2 text-body text-ink-dim">{brokers.copyFailed}</p>}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6">
            <button
              ref={copyButton}
              type="button"
              onClick={copy}
              className="flex h-12 items-center justify-center rounded-2 bg-brass-mark px-6 font-body text-ui font-medium text-on-brass sm:min-w-44"
            >
              {status === "copied" ? brokers.copied : brokers.copy}
            </button>
            <a href={mailto} className="link flex h-12 items-center justify-center text-ui font-medium sm:justify-start">
              {brokers.mail}
            </a>
          </div>
          <p aria-live="polite" className="sr-only">
            {status === "copied" ? brokers.copiedStatus : status === "failed" ? brokers.copyFailed : ""}
          </p>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
