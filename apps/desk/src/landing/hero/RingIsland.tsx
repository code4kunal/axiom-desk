"use client";

import { useEffect } from "react";
import { hero } from "../content";
import { gate, pinGate, readGateInputs } from "./gate";

const MARKS = ["equity", "gilts", "gold", "cash", "intl"] as const;

// Scroll px where each caption (0, 40, 70, card) docks: its natural (unstuck) top meets the rail.
function measureDocks(box: HTMLElement) {
  return [...box.querySelectorAll<HTMLElement>(".hero-rail, .hero-track")].map((el) => {
    const railTop = parseFloat(getComputedStyle(el).top);
    el.style.position = "static";
    const top = el.getBoundingClientRect().top + scrollY;
    el.style.position = "";
    return top - railTop;
  });
}

// Pinned hero only. The regime word and the legend follow the docked caption on every pinned visit;
// the live ring replaces the poster only when, after load and idle, WebGL2 and the full gate pass.
// Otherwise neither three nor GSAP is ever downloaded.
export function RingIsland() {
  useEffect(() => {
    const html = document.documentElement;
    const box = document.getElementById("season");
    const plate = box?.querySelector<HTMLElement>(".hero-poster .hero-plate");
    if (html.dataset.hero !== "pin" || !box || !plate) return;
    const hole = plate.querySelector<HTMLElement>(".hero-hole")!;
    const cells = [...box.querySelectorAll<HTMLElement>(".hero-legend [data-k]")];

    // Word and legend: a cut at each dock, never interpolated.
    let docks = measureDocks(box);
    let shown = -1;
    const showDock = () => {
      const i = docks.filter((d) => scrollY >= d - 1).length - 1;
      if (i === shown) return;
      shown = i;
      const h = hero.hole[i <= 0 ? 0 : 1]!;
      const word = hole.firstElementChild as HTMLElement;
      word.textContent = h.word;
      word.dataset.tone = h.tone;
      hole.lastElementChild!.textContent = h.note;
      const words = i >= 2 ? hero.legend.after : hero.legend.before;
      cells.forEach((c, k) => (c.querySelector("dd")!.textContent = words[k]!));
    };
    let pending = 0;
    const onScroll = () => {
      pending ||= requestAnimationFrame(() => {
        pending = 0;
        showDock();
      });
    };
    const onResize = () => {
      // Rotated to landscape (or otherwise below the gate): fall back to the stacked hero for good.
      if (!pinGate(readGateInputs(true))) {
        delete html.dataset.hero;
        return unpin();
      }
      docks = measureDocks(box);
      shown = -1;
      showDock();
    };
    showDock();
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onResize);
    void document.fonts.ready.then(onResize);

    let cleanup = () => {};
    let cancelled = false;

    async function start() {
      const probe = document.createElement("canvas").getContext("webgl2");
      probe?.getExtension("WEBGL_lose_context")?.loseContext();
      if (cancelled || !gate(readGateInputs(probe !== null))) return;
      const [{ createRing, keyframe }, { scrubBox }] = await Promise.all([import("./ring"), import("./scroll")]);
      if (cancelled) return;

      const css = getComputedStyle(html);
      const v = (name: string) => css.getPropertyValue(`--color-${name}`).trim();
      const palette = () => ({
        ground: v("ground"),
        ink: v("ink"),
        inkFaint: v("ink-faint"),
        geruMark: v("geru-mark"),
        marks: MARKS.map((m) => v(`${m}-mark`)) as [string, string, string, string, string],
        dark: html.dataset.theme === "dark",
      });

      const canvas = document.createElement("canvas");
      canvas.setAttribute("aria-hidden", "true");
      canvas.className = "absolute inset-0 size-full opacity-0 transition-opacity duration-[480ms] ease-reveal";
      plate!.insertBefore(canvas, hole);
      const tag = document.createElement("div");
      tag.setAttribute("aria-hidden", "true");
      tag.className =
        "pointer-events-none absolute top-0 left-0 z-20 hidden rounded-1 bg-ink px-2 py-1.5 font-mono text-label whitespace-nowrap text-ground uppercase";
      plate!.append(tag);

      const ring = createRing(canvas, palette(), { dpr: Math.min(devicePixelRatio, 1.5), narrow: innerWidth < 768 });
      ring.resize(plate!.clientWidth, plate!.clientHeight);

      // Idle breath runs continuously, but only while the plate is on screen.
      let raf = 0;
      let last = 0;
      let inView = true;
      let focused = -1;
      const t0 = performance.now();
      const tick = (t: number) => {
        raf = 0;
        if (!inView) return;
        ring.frame(last ? Math.min(0.1, (t - last) / 1000) : 1 / 60, (t - t0) / 1000);
        last = t;
        canvas.style.opacity = "1"; // fades in after the first drawn frame
        const f = ring.focus();
        if (f !== focused) {
          focused = f;
          cells.forEach((c, k) => c.toggleAttribute("data-hot", k === f));
          tag.classList.toggle("hidden", f < 0);
          if (f >= 0) tag.textContent = `${hero.legend.labels[f]} · ${cells[f]!.querySelector("dd")!.textContent}`;
        }
        raf = requestAnimationFrame(tick);
      };
      const kick = () => {
        if (!raf) raf = requestAnimationFrame(tick);
      };

      const io = new IntersectionObserver(([e]) => {
        inView = e!.isIntersecting;
        last = 0;
        if (inView) kick();
      });
      io.observe(plate!);
      const ro = new ResizeObserver(() => ring.resize(plate!.clientWidth, plate!.clientHeight));
      ro.observe(plate!);
      const mo = new MutationObserver(() => ring.setPalette(palette()));
      mo.observe(html, { attributes: true, attributeFilter: ["data-theme"] });

      const stopScroll = scrubBox(
        box!,
        (y) => ring.setProgress(keyframe(y, docks)),
        () => (docks = measureDocks(box!)),
      );

      const onPointer = (e: PointerEvent) => {
        const r = canvas.getBoundingClientRect();
        const x = e.clientX - r.left;
        const y = e.clientY - r.top;
        ring.setPointer(x, y);
        tag.style.transform = `translate(${x + 14}px, ${y + 14}px)`;
      };
      const offPointer = () => ring.setPointer(null);
      const fine = matchMedia("(pointer: fine)").matches;
      if (fine) {
        addEventListener("pointermove", onPointer, { passive: true });
        document.addEventListener("pointerleave", offPointer);
      }
      kick();

      cleanup = () => {
        cleanup = () => {}; // ring.dispose() loses the context, which fires webglcontextlost below
        cancelAnimationFrame(raf);
        stopScroll();
        io.disconnect();
        ro.disconnect();
        mo.disconnect();
        removeEventListener("pointermove", onPointer);
        document.removeEventListener("pointerleave", offPointer);
        cells.forEach((c) => c.removeAttribute("data-hot"));
        ring.dispose();
        canvas.remove();
        tag.remove();
      };

      // Context lost: stop, fade the canvas out over the poster beneath (which never unmounted).
      canvas.addEventListener("webglcontextlost", () => {
        const done = cleanup;
        cleanup = () => {};
        canvas.style.transitionDuration = "200ms";
        canvas.style.opacity = "0";
        setTimeout(done, 200);
      });
    }

    const idle = (cb: () => void) =>
      "requestIdleCallback" in window ? requestIdleCallback(cb, { timeout: 2000 }) : setTimeout(cb, 200);
    const run = () => idle(() => void start());
    if (document.readyState === "complete") run();
    else addEventListener("load", run, { once: true });

    function unpin() {
      cancelled = true;
      cancelAnimationFrame(pending);
      removeEventListener("load", run);
      removeEventListener("scroll", onScroll);
      removeEventListener("resize", onResize);
      cleanup();
    }
    return unpin;
  }, []);
  return null;
}
