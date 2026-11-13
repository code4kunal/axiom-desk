import { WEIGHTS_A, WEIGHTS_B } from "./weights.ts";
import {
  BufferAttribute,
  BufferGeometry,
  CircleGeometry,
  Color,
  Group,
  Mesh,
  MeshBasicMaterial,
  PerspectiveCamera,
  Plane,
  PlaneGeometry,
  Points,
  Raycaster,
  Scene,
  ShaderMaterial,
  Vector2,
  Vector3,
  WebGLRenderer,
} from "three";

// The basket drawn as points (docs/design/landing-palette-v2.md §4). Colours come from the page's
// tokens: ground for the clear colour, ink for equity and the needle, -mark tokens for the rest.
export type Palette = {
  ground: string;
  ink: string;
  inkFaint: string;
  geruMark: string;
  marks: [equity: string, gilts: string, gold: string, cash: string, intl: string];
  dark: boolean;
};

export type Ring = {
  setProgress(p: number): void;
  // Pointer in CSS px relative to the canvas, or null when it leaves.
  setPointer(x: number | null, y?: number): void;
  // Basket class under the pointer (0 equity … 4 intl), or -1.
  focus(): number;
  setPalette(p: Palette): void;
  frame(dt: number, t: number): void;
  resize(w: number, h: number): void;
  dispose(): void;
};

export { WEIGHTS_A, WEIGHTS_B };

const TAU = Math.PI * 2;
const DEG = Math.PI / 180;
const REST = Math.PI / 2 + 0.35; // needle at rest: just left of 12 o'clock

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const smooth = (a: number, b: number, x: number) => {
  const t = clamp01((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};

// Shader inputs per scroll progress (states sit at 0, 0.4, 0.7, 1).
export function pose(p: number) {
  const s = p * 100;
  return {
    needle: -38 * DEG * Math.min(1, s / 40), // offset from rest; +z is counter-clockwise
    sweep: smooth(8, 40, s), // rim turns geru outward from the needle
    fray: smooth(12, 40, s) * (1 - smooth(68, 100, s)), // rim frays near the needle, calms by 100
    mix: smooth(44, 74, s), // money that moves lifts out and settles in its new colour
    tilt: s < 40 ? 1 + 0.6 * (s / 40) : s < 70 ? 1.6 : 1.6 * (1 - smooth(70, 100, s)),
  };
}

const STATES = [0, 0.4, 0.7, 1];

// Scroll px → ring progress, piecewise linear through the scroll positions where each caption docks
// ([start, dock 40, dock 70, dock card]), so the ring changes state the instant its caption does.
export function keyframe(y: number, docks: readonly number[]): number {
  if (y <= docks[0]!) return 0;
  for (let i = 1; i < docks.length; i++)
    if (y < docks[i]!) {
      const t = (y - docks[i - 1]!) / (docks[i]! - docks[i - 1]!);
      return STATES[i - 1]! + (STATES[i]! - STATES[i - 1]!) * t;
    }
  return 1;
}

function cumulative(w: number[]) {
  const total = w.reduce((a, b) => a + b, 0);
  let acc = 0;
  return w.map((x) => (acc += x) / total);
}
const CUM_A = cumulative(WEIGHTS_A);
const CUM_B = cumulative(WEIGHTS_B);
const classAt = (cum: number[], t: number) => cum.findIndex((c) => t < c);

const vertexShader = /* glsl */ `
attribute vec3 cA; attribute vec3 cB; attribute float aSeed, aKind, aAng, aClsA, aClsB;
uniform float uTime, uMix, uSweep, uFray, uNeedle, uFocus, uSize, uDpr, uLight; uniform vec3 uPointer, uRest, uGeru;
varying vec3 vCol; varying float vAlpha;
float angDist(float a, float b){ return abs(mod(a - b + 3.14159265, 6.2831853) - 3.14159265); }
void main(){
  vec3 p = position; float t = uTime;
  float cls = mix(aClsA, aClsB, step(0.5, uMix));
  if (aKind < 0.5) {
    float r = length(p.xy), a = aAng;
    float changed = step(0.5, abs(aClsA - aClsB));
    float m = smoothstep(0.0, 1.0, clamp((uMix - aSeed*0.35)/0.65, 0.0, 1.0));
    r += changed * sin(m*3.14159) * 0.14;
    a += changed * sin(m*3.14159) * 0.08;
    r += sin(t*0.7 + aSeed*6.2831) * 0.006;
    p.xy = vec2(cos(a), sin(a)) * r;
    vCol = mix(cA, cB, m);
  } else {
    float k = uSweep * (1.0 - smoothstep(0.0, 2.6, angDist(aAng, uNeedle)));
    vCol = mix(uRest, uGeru, smoothstep(0.15, 0.6, k));
    float fr = uFray * (1.0 - smoothstep(0.0, 1.6, angDist(aAng, uNeedle)));
    float r = length(p.xy) + fr * (0.04 + 0.18*fract(aSeed*7.3)) * (0.5 + 0.5*sin(t*2.1 + aSeed*30.0));
    r += sin(t*0.9 + aSeed*6.2831) * 0.004;
    p.xy = vec2(cos(aAng), sin(aAng)) * r;
  }
  vec2 d = p.xy - uPointer.xy; float L = length(d);
  float push = pow(max(0.0, 1.0 - L/0.30), 2.0);
  p.xy += (L > 1e-4 ? d/L : vec2(0.0)) * push * 0.16;
  float focus = (uFocus > -0.5 && aKind < 0.5) ? (abs(cls - uFocus) < 0.5 ? 1.0 : 0.0) : -1.0;
  float sz = uSize * ((focus > 0.5) ? 1.55 : 1.0) * (1.0 + push*0.8);
  vAlpha = (focus < -0.5) ? mix(0.86, 1.0, uLight) : (focus > 0.5 ? 1.0 : 0.3);
  if (aKind > 0.5) { vAlpha = 0.95; sz *= 1.15; }
  vec4 mv = modelViewMatrix * vec4(p, 1.0);
  gl_Position = projectionMatrix * mv;
  gl_PointSize = sz * uDpr * (3.2 / -mv.z);
}`;

const fragmentShader = /* glsl */ `
precision mediump float; varying vec3 vCol; varying float vAlpha; uniform float uDark;
void main(){
  float d = length(gl_PointCoord - 0.5); if (d > 0.5) discard;
  vec3 c = vCol; if (uDark > 0.5) c += (1.0 - smoothstep(0.0, 0.3, d)) * 0.18;
  gl_FragColor = vec4(c, smoothstep(0.5, 0.28, d) * vAlpha);
  #include <colorspace_fragment>
}`; // colours are linear after Color.set(); the chunk writes them back as sRGB, so they match the tokens

export function createRing(
  canvas: HTMLCanvasElement,
  palette: Palette,
  opts: { dpr: number; narrow: boolean; preserveDrawingBuffer?: boolean },
): Ring {
  const renderer = new WebGLRenderer({
    canvas,
    antialias: false,
    powerPreference: "low-power",
    preserveDrawingBuffer: opts.preserveDrawingBuffer ?? false,
  });
  renderer.setPixelRatio(opts.dpr);

  // One buffer, two populations: the basket band (annulus r 0.62–1.0) and the regime rim.
  const NB = opts.narrow ? 3800 : 6500;
  const NR = opts.narrow ? 700 : 1000;
  const N = NB + NR;
  const pos = new Float32Array(N * 3);
  const cA = new Float32Array(N * 3);
  const cB = new Float32Array(N * 3);
  const seed = new Float32Array(N);
  const kind = new Float32Array(N);
  const ang = new Float32Array(N);
  const clsA = new Float32Array(N);
  const clsB = new Float32Array(N);
  let rnd = 1337; // seeded, so the poster and the live ring draw the same points
  const R = () => (rnd = (rnd * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < NB; i++) {
    const t = (i + R() * 0.9) / NB;
    const a = REST + t * TAU;
    const r = 0.62 + 0.38 * Math.sqrt(R());
    pos.set([Math.cos(a) * r, Math.sin(a) * r, (R() - 0.5) * 0.04], i * 3);
    ang[i] = a;
    seed[i] = R();
    clsA[i] = classAt(CUM_A, t);
    clsB[i] = classAt(CUM_B, t);
  }
  for (let i = NB; i < N; i++) {
    const a = R() * TAU;
    const r = 1.075 + R() * 0.025;
    pos.set([Math.cos(a) * r, Math.sin(a) * r, 0], i * 3);
    ang[i] = a;
    seed[i] = R();
    kind[i] = 1;
    clsA[i] = clsB[i] = -1;
  }

  const geo = new BufferGeometry();
  geo.setAttribute("position", new BufferAttribute(pos, 3));
  geo.setAttribute("cA", new BufferAttribute(cA, 3));
  geo.setAttribute("cB", new BufferAttribute(cB, 3));
  geo.setAttribute("aSeed", new BufferAttribute(seed, 1));
  geo.setAttribute("aKind", new BufferAttribute(kind, 1));
  geo.setAttribute("aAng", new BufferAttribute(ang, 1));
  geo.setAttribute("aClsA", new BufferAttribute(clsA, 1));
  geo.setAttribute("aClsB", new BufferAttribute(clsB, 1));

  const u = {
    uTime: { value: 0 },
    uMix: { value: 0 },
    uSweep: { value: 0 },
    uFray: { value: 0 },
    uNeedle: { value: REST },
    uPointer: { value: new Vector3(9, 9, 0) },
    uFocus: { value: -1 },
    uSize: { value: 4.8 },
    uDpr: { value: opts.dpr },
    uRest: { value: new Color() },
    uGeru: { value: new Color() },
    uDark: { value: 0 },
    uLight: { value: 1 },
  };
  const mat = new ShaderMaterial({ transparent: true, depthWrite: false, uniforms: u, vertexShader, fragmentShader });
  const group = new Group();
  group.add(new Points(geo, mat));

  // Needle: solid ink line r 0.30–0.60 with a hub, each over a ground keyline 2px wider. Built at unit
  // width and scaled to CSS px on resize, so the line stays 2px at any canvas size.
  const inkMat = new MeshBasicMaterial({ depthTest: false });
  const keyMat = new MeshBasicMaterial({ depthTest: false });
  const bar = new PlaneGeometry(0.3, 1);
  const disc = new CircleGeometry(1, 24);
  const parts: [Mesh, number][] = [
    [new Mesh(bar, keyMat), 6],
    [new Mesh(disc, keyMat), 5.5],
    [new Mesh(bar, inkMat), 2],
    [new Mesh(disc, inkMat), 3.5],
  ];
  const needle = new Group();
  parts.forEach(([m], i) => {
    m.position.x = m.geometry === bar ? 0.45 : 0.3;
    m.renderOrder = i < 2 ? 1 : 2;
    needle.add(m);
  });
  needle.position.z = 0.03;
  group.add(needle);

  const scene = new Scene();
  scene.add(group);
  const camera = new PerspectiveCamera(30, 1, 0.1, 20);
  camera.position.z = 4.6;

  function setPalette(p: Palette) {
    const marks = p.marks.map((c) => new Color(c));
    const ink = new Color(p.ink);
    for (let i = 0; i < N; i++) {
      const a = clsA[i]! >= 0 ? marks[clsA[i]!]! : ink;
      const b = clsB[i]! >= 0 ? marks[clsB[i]!]! : ink;
      cA.set([a.r, a.g, a.b], i * 3);
      cB.set([b.r, b.g, b.b], i * 3);
    }
    geo.attributes.cA!.needsUpdate = true;
    geo.attributes.cB!.needsUpdate = true;
    u.uRest.value.set(p.inkFaint);
    u.uGeru.value.set(p.geruMark);
    u.uDark.value = p.dark ? 1 : 0;
    u.uLight.value = p.dark ? 0 : 1;
    inkMat.color.set(p.ink);
    keyMat.color.set(p.ground);
    renderer.setClearColor(p.ground, 1); // opaque: the poster beneath must never show through
  }
  setPalette(palette);

  let tiltScale = 1;
  let progress = 0;
  function setProgress(p: number) {
    progress = p;
    const s = pose(p);
    u.uNeedle.value = REST + s.needle;
    needle.rotation.z = u.uNeedle.value;
    u.uSweep.value = s.sweep;
    u.uFray.value = s.fray;
    u.uMix.value = s.mix;
    tiltScale = s.tilt;
  }
  setProgress(0);

  // The hand: the pointer is unprojected onto the ring's plane each move.
  const ray = new Raycaster();
  const ndc = new Vector2();
  const hit = new Vector3();
  const plane = new Plane();
  const normal = new Vector3();
  let width = 1;
  let ptrOn = false;
  const ptr = { x: 0, y: 0 }; // target in ndc
  const lean = { x: 0, y: 0 }; // smoothed
  const rot = { x: 0, y: 0 };
  let focused = -1;

  return {
    setProgress,
    setPointer(x, y = 0) {
      ptrOn = x !== null && x >= 0 && y >= 0 && x <= width && y <= width;
      if (!ptrOn || x === null) return;
      ndc.set((x / width) * 2 - 1, -((y / width) * 2 - 1));
      ptr.x = ndc.x;
      ptr.y = ndc.y;
      ray.setFromCamera(ndc, camera);
      plane.setFromNormalAndCoplanarPoint(normal.set(0, 0, 1).applyQuaternion(group.quaternion), group.position);
      if (ray.ray.intersectPlane(plane, hit)) u.uPointer.value.copy(group.worldToLocal(hit));
    },
    focus: () => focused,
    setPalette,
    frame(dt, t) {
      u.uTime.value = t;
      const k = 1 - Math.exp(-dt * 5);
      lean.x += ((ptrOn ? ptr.x : 0) - lean.x) * k;
      lean.y += ((ptrOn ? ptr.y : 0) - lean.y) * k;
      const idle = Math.sin(t * 0.35) * 0.035; // ±2° yaw on an 18 s sine
      const kr = 1 - Math.exp(-dt * 6.3);
      rot.x += ((-0.22 + lean.y * 0.16 + idle) * tiltScale - rot.x) * kr;
      rot.y += ((lean.x * 0.22 - idle * 0.6) * tiltScale - rot.y) * kr;
      group.rotation.set(rot.x, rot.y, 0);
      if (!ptrOn) u.uPointer.value.set(9, 9, 0);
      focused = -1;
      if (ptrOn) {
        const p = u.uPointer.value;
        const r = Math.hypot(p.x, p.y);
        if (r > 0.58 && r < 1.06) {
          const a = (((Math.atan2(p.y, p.x) - REST) % TAU) + TAU) % TAU;
          focused = classAt(progress >= 0.58 ? CUM_B : CUM_A, a / TAU);
        }
      }
      u.uFocus.value = focused;
      renderer.render(scene, camera);
    },
    resize(w, h) {
      width = w;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      u.uSize.value = w < 420 ? 4.2 : 4.8;
      const px = 2.465 / w; // world units per CSS px at this canvas width
      for (const [m, size] of parts) m.scale.set(m.geometry === bar ? 1 : size * px, size * px, 1);
    },
    dispose() {
      geo.dispose();
      bar.dispose();
      disc.dispose();
      [mat, inkMat, keyMat].forEach((m) => m.dispose());
      renderer.dispose();
      renderer.forceContextLoss(); // dispose() keeps the GL context; free it before GC does
    },
  };
}
