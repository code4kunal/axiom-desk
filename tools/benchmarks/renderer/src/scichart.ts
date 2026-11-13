import {
  DateTimeNumericAxis,
  EAutoRange,
  FastCandlestickRenderableSeries,
  MouseWheelZoomModifier,
  NumberRange,
  NumericAxis,
  OhlcDataSeries,
  SciChartSurface,
  VerticalLineAnnotation,
  ZoomPanModifier,
} from "scichart";
import { BAR_SECONDS } from "./replay.ts";
import type { ChartRenderer, SyncBus } from "./types.ts";

let configured = false;
function configure() {
  if (configured) return;
  configured = true;
  // The community licence is non-commercial only, so a commercial desk evaluation needs a trial or paid key.
  const key = import.meta.env.VITE_SCICHART_LICENSE_KEY as string | undefined;
  if (!key) throw new Error("Set VITE_SCICHART_LICENSE_KEY in tools/benchmarks/renderer/.env.local (trial or commercial key).");
  SciChartSurface.setRuntimeLicenseKey(key);
  // Served from node_modules by vite.config.ts so the run never depends on a CDN.
  SciChartSurface.configure({ wasmUrl: "/scichart-wasm/scichart.wasm" });
}

/** Candidate B: SciChart.js used only as the drawing layer; data, replay and sync stay ours. */
export async function createSciChart(el: HTMLElement, bus: SyncBus): Promise<ChartRenderer> {
  configure();
  const div = document.createElement("div");
  div.style.cssText = "position:absolute;inset:0";
  el.appendChild(div);

  // `create` shares one WebGL/WebGPU context across surfaces, which is the multi-chart path.
  const { sciChartSurface: surface, wasmContext } = await SciChartSurface.create(div);
  const x = new DateTimeNumericAxis(wasmContext);
  const y = new NumericAxis(wasmContext, { autoRange: EAutoRange.Always, growBy: new NumberRange(0.05, 0.05) });
  surface.xAxes.add(x);
  surface.yAxes.add(y);

  const data = new OhlcDataSeries(wasmContext, { dataIsSortedInX: true, containsNaN: false });
  surface.renderableSeries.add(
    new FastCandlestickRenderableSeries(wasmContext, {
      dataSeries: data,
      strokeUp: "#26a269",
      brushUp: "#26a269",
      strokeDown: "#c01c28",
      brushDown: "#c01c28",
      dataPointWidth: 0.7,
    }),
  );
  surface.chartModifiers.add(new ZoomPanModifier(), new MouseWheelZoomModifier());

  const cross = new VerticalLineAnnotation({ x1: 0, stroke: "#999", strokeDashArray: [4, 4], isHidden: true });
  surface.annotations.add(cross);

  // Setting a sibling's range fires its visibleRangeChanged; the flag stops that echoing back round the bus.
  let applying = false;
  x.visibleRangeChanged.subscribe((args) => {
    if (!applying && args) bus.range(api, args.visibleRange.min, args.visibleRange.max);
  });
  div.addEventListener("pointermove", (e) => {
    const r = surface.seriesViewRect;
    // shortcut: assumes seriesViewRect is in device pixels (UNVERIFIED); fine for the spike, check before U14 core.
    const t = x.getCurrentCoordinateCalculator().getDataValue(e.offsetX * devicePixelRatio - r.left);
    api.setCrosshair(t);
    bus.crosshair(api, t);
  });
  div.addEventListener("pointerleave", () => {
    api.setCrosshair(null);
    bus.crosshair(api, null);
  });

  const api: ChartRenderer = {
    setBars(bars) {
      data.clear();
      data.appendRange(
        bars.map((b) => b.time),
        bars.map((b) => b.open),
        bars.map((b) => b.high),
        bars.map((b) => b.low),
        bars.map((b) => b.close),
      );
      const last = bars[bars.length - 1]?.time ?? 0;
      api.setRange(last - 200 * BAR_SECONDS, last + 10 * BAR_SECONDS);
    },
    update(b, isNew) {
      if (isNew) data.append(b.time, b.open, b.high, b.low, b.close);
      else data.update(data.count() - 1, b.open, b.high, b.low, b.close);
    },
    setCrosshair(t) {
      cross.isHidden = t === null;
      if (t !== null) cross.x1 = t;
    },
    setRange(from, to) {
      applying = true;
      x.visibleRange = new NumberRange(from, to);
      applying = false;
    },
    destroy() {
      surface.delete();
      el.replaceChildren();
    },
  };
  return api;
}
