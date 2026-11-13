"use client";

import { useEffect } from "react";
import { sections } from "./content";

// One client island: section reveals (CSS transitions toggled once per element) and the nav's
// current section. Without JS nothing is hidden: the hidden state needs html[data-js].
export function Observers() {
  useEffect(() => {
    const reveal = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          (e.target as HTMLElement).dataset.shown = "";
          reveal.unobserve(e.target);
        }),
      { threshold: 0.2 },
    );
    document.querySelectorAll("[data-reveal]").forEach((el) => reveal.observe(el));
    // Hands the reveals from the CSS failsafe to this observer.
    document.documentElement.dataset.observing = "";

    const links = document.querySelectorAll<HTMLAnchorElement>("nav a[href^='/#']");
    const current = new IntersectionObserver(
      (entries) =>
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          links.forEach((a) =>
            a.getAttribute("href") === `/#${e.target.id}`
              ? a.setAttribute("aria-current", "location")
              : a.removeAttribute("aria-current"),
          );
        }),
      // A section is current while it crosses a thin band just under the rail.
      { rootMargin: "-64px 0px -85% 0px" },
    );
    sections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) current.observe(el);
    });
    return () => {
      reveal.disconnect();
      current.disconnect();
    };
  }, []);
  return null;
}
