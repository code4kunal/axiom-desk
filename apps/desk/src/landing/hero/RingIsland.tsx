"use client";

import { useEffect } from "react";
import { gate, readGateInputs } from "./gate";

// Upgrades the pinned 0% poster to the live ring. Only when the head script pinned the hero and, after
// load and idle, WebGL2 and the full gate pass; otherwise neither three nor GSAP is ever downloaded.
export function RingIsland() {
  useEffect(() => {
    const html = document.documentElement;
    if (html.dataset.hero !== "pin") return;
    let cleanup = () => {};
    let cancelled = false;

    async function start() {
      const probe = document.createElement("canvas").getContext("webgl2");
      probe?.getExtension("WEBGL_lose_context")?.loseContext();
      if (cancelled || !gate(readGateInputs(probe !== null))) return;
      const [{ createRing, keyframe }, { scrubBox }] = await Promise.all([import("./ring"), import("./scroll")]);
      const box = document.getElementById("season");
      const plate = box?.querySelector<HTMLElement>(".hero-poster .hero-plate");
      if (cancelled || !box || !plate) return;

      const css = getComputedStyle(html);
      const palette = () => ({
        raised: css.getPropertyValue("--color-raised").trim(),
        inkDim: css.getPropertyValue("--color-ink-dim").trim(),
        brass: css.getPropertyValue("--color-brass-mark").trim(),
        geru: css.getPropertyValue("--color-geru").trim(),
      });

      const canvas = document.createElement("canvas");
      canvas.setAttribute("aria-hidden", "true");
      canvas.className = "absolute inset-0 size-full opacity-0 transition-opacity duration-[480ms] ease-reveal";
      plate.append(canvas);
      const ring = createRing(canvas, palette(), { dpr: Math.min(devicePixelRatio, 1.5) });
      ring.resize(plate.clientWidth, plate.clientHeight);

      // Render only while the plate is on screen and something changed; frame() reports when idle.
      let raf = 0;
      let last = 0;
      let inView = true;
      const tick = (t: number) => {
        raf = 0;
        if (!inView) return;
        const drew = ring.frame(last ? (t - last) / 1000 : 1 / 60);
        last = t;
        if (!drew) return void (last = 0);
        canvas.style.opacity = "1"; // fades in after the first drawn frame
        raf = requestAnimationFrame(tick);
      };
      const kick = () => {
        if (!raf) raf = requestAnimationFrame(tick);
      };

      const io = new IntersectionObserver(([e]) => {
        inView = e!.isIntersecting;
        if (inView) kick();
      });
      io.observe(plate);
      const ro = new ResizeObserver(() => {
        ring.resize(plate.clientWidth, plate.clientHeight);
        kick();
      });
      ro.observe(plate);
      const mo = new MutationObserver(() => {
        ring.setPalette(palette());
        kick();
      });
      mo.observe(html, { attributes: true, attributeFilter: ["data-theme"] });

      // Dock points: where each caption's natural (unstuck) top meets the rail, in scroll px.
      let docks = [0, 1, 2, 3];
      const measure = () => {
        docks = [...box.querySelectorAll<HTMLElement>(".hero-rail, .hero-track")].map((el) => {
          const railTop = parseFloat(getComputedStyle(el).top);
          el.style.position = "static";
          const top = el.getBoundingClientRect().top + scrollY;
          el.style.position = "";
          return top - railTop;
        });
      };
      measure();
      const stopScroll = scrubBox(
        box,
        (y) => {
          ring.setProgress(keyframe(y, docks));
          kick();
        },
        measure,
      );

      const fine = matchMedia("(pointer: fine)").matches;
      const onPointer = (e: PointerEvent) => {
        const r = plate.getBoundingClientRect();
        const clamp = (v: number) => Math.max(-1, Math.min(1, v));
        ring.setPointer(clamp((e.clientX - r.left) / r.width * 2 - 1), clamp((e.clientY - r.top) / r.height * 2 - 1));
        kick();
      };
      if (fine) addEventListener("pointermove", onPointer, { passive: true });

      cleanup = () => {
        cancelAnimationFrame(raf);
        stopScroll();
        io.disconnect();
        ro.disconnect();
        mo.disconnect();
        removeEventListener("pointermove", onPointer);
        ring.dispose();
        canvas.remove();
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

    return () => {
      cancelled = true;
      removeEventListener("load", run);
      cleanup();
    };
  }, []);
  return null;
}
