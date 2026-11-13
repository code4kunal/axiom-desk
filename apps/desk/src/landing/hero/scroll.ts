import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
// Mobile address-bar show/hide must not re-measure the box; orientation change still refreshes.
ScrollTrigger.config({ ignoreMobileResize: true });

// Scrubs the scroll position across the box CSS already reserved. No GSAP pin, no spacer: CSS sticky
// pins, so native hash and back/forward restoration keep working. Reports scroll px, smoothed by scrub.
export function scrubBox(box: HTMLElement, onScroll: (y: number) => void, onRefresh: () => void): () => void {
  const proxy = { p: 0 };
  const tween = gsap.to(proxy, {
    p: 1,
    ease: "none",
    onUpdate: () => {
      const st = tween.scrollTrigger!;
      onScroll(st.start + proxy.p * (st.end - st.start));
    },
    scrollTrigger: { trigger: box, start: "top top+=48", end: "bottom bottom", scrub: 0.8, onRefresh },
  });
  // Below 768 the dock points follow the statement's line count, which moves when the fonts land.
  void document.fonts.ready.then(() => ScrollTrigger.refresh());
  return () => {
    tween.scrollTrigger?.kill();
    tween.kill();
  };
}
