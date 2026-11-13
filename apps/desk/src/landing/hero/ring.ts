import {
  BoxGeometry,
  Color,
  DirectionalLight,
  HemisphereLight,
  InstancedMesh,
  Mesh,
  MeshBasicMaterial,
  MeshStandardMaterial,
  Object3D,
  PerspectiveCamera,
  RingGeometry,
  Scene,
  TorusGeometry,
  WebGLRenderer,
} from "three";

// Colours come from the page's tokens so the canvas matches the poster in either theme.
export type Palette = { raised: string; inkDim: string; brass: string; geru: string };

export type Ring = {
  setProgress(p: number): void;
  setPointer(x: number, y: number): void;
  setPalette(p: Palette): void;
  frame(dt: number): boolean;
  resize(w: number, h: number): void;
  dispose(): void;
};

const DEG = Math.PI / 180;
// Basket weights (large-cap, mid/small-cap, gilts, gold, cash, international via LRS) at 0–40% and
// at 70–100%: equity 61 → 42, gilts 18 → 29, gold 9 → 17, the rest unchanged.
const W0 = [40, 21, 18, 9, 6, 6];
const W1 = [28, 14, 29, 17, 6, 6];
const GAP = 1.2 * DEG;

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const span = (p: number, a: number, b: number) => clamp01((p - a) / (b - a));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

// Needle and tilt per scroll progress: the states sit at 0, 0.4, 0.7 and 1.
export function pose(p: number) {
  const sweep = span(p, 0, 0.4);
  return {
    needle: lerp(30, -8, sweep) * DEG, // +z is counter-clockwise: 30° left of top, swept 38° to 8° right
    tilt: (p <= 0.7 ? lerp(0, 12, sweep) : lerp(12, 0, span(p, 0.7, 1))) * DEG,
    geru: span(p, 0.2, 0.4),
    reweight: span(p, 0.4, 0.7),
  };
}

const STATES = [0, 0.4, 0.7, 1];

// Scroll px → ring progress, piecewise linear through the scroll positions where each caption docks
// ([start, dock 40, dock 70, dock card]), so the ring changes state the instant its caption does.
export function keyframe(y: number, docks: readonly number[]): number {
  if (y <= docks[0]!) return 0;
  for (let i = 1; i < docks.length; i++)
    if (y < docks[i]!) return lerp(STATES[i - 1]!, STATES[i]!, (y - docks[i - 1]!) / (docks[i]! - docks[i - 1]!));
  return 1;
}

export function createRing(
  canvas: HTMLCanvasElement,
  palette: Palette,
  opts: { dpr: number; preserveDrawingBuffer?: boolean },
): Ring {
  const renderer = new WebGLRenderer({
    canvas,
    antialias: true,
    powerPreference: "low-power",
    preserveDrawingBuffer: opts.preserveDrawingBuffer ?? false,
  });
  renderer.setPixelRatio(opts.dpr);

  const scene = new Scene();
  const camera = new PerspectiveCamera(30, 1, 0.1, 20);
  camera.position.set(0, 0, 5.3);

  scene.add(new HemisphereLight(0xffffff, 0x2a221c, 1.1));
  const sun = new DirectionalLight(0xffffff, 1.6);
  sun.position.set(2, 3, 4);
  scene.add(sun);

  const instrument = new Object3D();
  scene.add(instrument);

  const ring = new Mesh(
    new TorusGeometry(1.0, 0.085, 16, 96),
    new MeshStandardMaterial({ color: 0x2a221c, roughness: 0.7, metalness: 0.15 }),
  );
  instrument.add(ring);

  const brassMat = new MeshStandardMaterial({ roughness: 0.35, metalness: 0.8, emissiveIntensity: 0.3 });

  // 360 graduations, one instanced mesh; every tenth is long. Unlit, coloured per instance, so brass
  // and the geru state read as their exact tokens on a dim LCD (lit metal muddied the state colour).
  const tickMat = new MeshBasicMaterial({ color: 0xffffff });
  const ticks = new InstancedMesh(new BoxGeometry(0.008, 1, 0.012), tickMat, 360);
  const dummy = new Object3D();
  for (let i = 0; i < 360; i++) {
    const a = i * DEG;
    const len = i % 10 === 0 ? 0.11 : 0.05;
    const r = 1.12 + len / 2;
    dummy.position.set(-Math.sin(a) * r, Math.cos(a) * r, 0);
    dummy.rotation.set(0, 0, a);
    dummy.scale.set(1, len, 1);
    dummy.updateMatrix();
    ticks.setMatrixAt(i, dummy.matrix);
    ticks.setColorAt(i, new Color(1, 1, 1));
  }
  instrument.add(ticks);

  // Six-arc basket annulus, unlit; the large-cap arc is the active one.
  const arcMat = new MeshBasicMaterial();
  const activeMat = new MeshBasicMaterial();
  const arcs = W0.map((_, i) => new Mesh(new RingGeometry(0.5, 0.74, 24, 1), i === 0 ? activeMat : arcMat));
  arcs.forEach((m) => instrument.add(m));

  const needle = new Mesh(new BoxGeometry(0.018, 0.86, 0.02), brassMat);
  needle.geometry.translate(0, 0.43, 0.03);
  instrument.add(needle);

  let progress = 0;
  let target = { x: 0, y: 0 };
  const tilt = { x: 0, y: 0 };
  let dirty = true;
  let colors = { brass: new Color(), geru: new Color() };

  let laidOut = -1;
  function layoutArcs(t: number) {
    if (t === laidOut) return;
    laidOut = t;
    const w = W0.map((v, i) => lerp(v, W1[i]!, t));
    const total = w.reduce((a, b) => a + b, 0);
    let start = Math.PI / 2; // top, running clockwise
    w.forEach((v, i) => {
      const len = (v / total) * Math.PI * 2;
      const m = arcs[i]!;
      m.geometry.dispose();
      m.geometry = new RingGeometry(0.5, 0.74, Math.max(4, Math.round(len / (6 * DEG))), 1, start - len + GAP / 2, len - GAP);
      start -= len;
    });
  }

  function apply() {
    const s = pose(progress);
    needle.rotation.z = s.needle;
    const tmp = new Color();
    for (let i = 0; i < 360; i++) {
      // Distance (degrees) from the needle; ticks within 20° turn geru as deterioration sets in.
      const d = Math.abs(((((i * DEG - s.needle) / DEG) % 360) + 540) % 360 - 180);
      const k = d < 20 ? s.geru * (1 - d / 20) : 0;
      ticks.setColorAt(i, tmp.copy(colors.brass).lerp(colors.geru, k));
    }
    if (ticks.instanceColor) ticks.instanceColor.needsUpdate = true;
    layoutArcs(s.reweight);
    return s.tilt;
  }

  let baseTilt = 0;
  function setPalette(p: Palette) {
    renderer.setClearColor(p.raised, 1);
    colors = { brass: new Color(p.brass), geru: new Color(p.geru) };
    brassMat.color.set(p.brass);
    brassMat.emissive.set(p.brass);
    arcMat.color.set(p.inkDim);
    activeMat.color.set(p.brass);
    baseTilt = apply();
    dirty = true;
  }
  setPalette(palette);

  return {
    setProgress(p) {
      if (p === progress) return;
      progress = p;
      baseTilt = apply();
      dirty = true;
    },
    // Pointer in -1..1; the ring leans up to 6° toward it.
    setPointer(x, y) {
      target = { x: -y * 6 * DEG, y: x * 6 * DEG };
      dirty = true;
    },
    setPalette,
    // Returns whether it drew, so the caller can stop its loop when idle.
    frame(dt) {
      const k = 1 - Math.exp(-dt / 0.12); // 0.12 s lerp, never a spring
      tilt.x += (target.x - tilt.x) * k;
      tilt.y += (target.y - tilt.y) * k;
      const settling = Math.abs(target.x - tilt.x) + Math.abs(target.y - tilt.y) > 1e-4;
      if (!dirty && !settling) return false;
      instrument.rotation.set(-baseTilt + tilt.x, tilt.y, 0);
      renderer.render(scene, camera);
      dirty = false;
      return true;
    },
    resize(w, h) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      dirty = true;
    },
    dispose() {
      scene.traverse((o) => {
        if (o instanceof Mesh || o instanceof InstancedMesh) o.geometry.dispose();
      });
      [brassMat, tickMat, arcMat, activeMat, ring.material as MeshStandardMaterial].forEach((m) => m.dispose());
      renderer.dispose();
    },
  };
}
