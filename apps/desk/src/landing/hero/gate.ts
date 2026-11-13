export type GateInputs = {
  webgl2: boolean;
  reducedMotion: boolean;
  deviceMemory: number | undefined;
  saveData: boolean | undefined;
  effectiveType: string | undefined;
  viewportHeight: number;
};

// Everything except WebGL, which can only be probed after load. Self-contained (no outer
// references): its source is inlined into the blocking head script that reserves the pin box.
export function pinGate(i: Omit<GateInputs, "webgl2">): boolean {
  return (
    !i.reducedMotion &&
    (i.deviceMemory === undefined || i.deviceMemory >= 4) &&
    i.saveData !== true &&
    i.effectiveType !== "slow-2g" &&
    i.effectiveType !== "2g" &&
    i.effectiveType !== "3g" &&
    // Keeps portrait phones, excludes landscape phones.
    i.viewportHeight >= 600
  );
}

// The 3D ring loads only when this holds; otherwise the poster is final.
export function gate(i: GateInputs): boolean {
  return i.webgl2 && pinGate(i);
}

type Nav = Navigator & { deviceMemory?: number; connection?: { saveData?: boolean; effectiveType?: string } };

export function readGateInputs(webgl2: boolean): GateInputs {
  const nav = navigator as Nav;
  return {
    webgl2,
    reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    deviceMemory: nav.deviceMemory,
    saveData: nav.connection?.saveData,
    effectiveType: nav.connection?.effectiveType,
    viewportHeight: innerHeight,
  };
}

// The head-script form: same inputs read inline, so the pin box is decided before first paint.
export const pinScript = `if((${pinGate.toString()})({reducedMotion:matchMedia("(prefers-reduced-motion: reduce)").matches,deviceMemory:navigator.deviceMemory,saveData:navigator.connection&&navigator.connection.saveData,effectiveType:navigator.connection&&navigator.connection.effectiveType,viewportHeight:innerHeight}))document.documentElement.dataset.hero="pin";`;
