from collections import deque
from collections.abc import Generator

from axiom_chartmath.indicators import primitives as p
from axiom_chartmath.indicators.registry import Out, Stepper, register


def _rsi(n: int) -> Generator[float | None, float, None]:
    prev = yield None
    gain, loss = p.primed(p.wilder(n)), p.primed(p.wilder(n))
    out: float | None = None
    while True:
        x = yield out
        change = x - prev
        prev = x
        g, lo = gain.send(max(change, 0.0)), loss.send(max(-change, 0.0))
        if g is None or lo is None:
            continue
        out = 0.0 if p.is_zero(g + lo) else 100 * g / (g + lo)


@register(
    "rsi",
    group="momentum",
    reference="Wilder RSI: 100*G/(G+L), G and L Wilder-smoothed mean gain and loss.",
    warmup=lambda c: c["period"],
)
def rsi(period: int = 14) -> Stepper:
    r = p.primed(_rsi(period))
    out: Out = {}
    while True:
        bar = yield out
        out = {"rsi": r.send(bar.close)}


@register(
    "macd",
    group="momentum",
    reference="EMA(fast) - EMA(slow), signal = EMA(signal) of that line, histogram = the gap.",
    warmup=lambda c: {
        "macd": c["slow"] - 1,
        "signal": c["slow"] + c["signal"] - 2,
        "histogram": c["slow"] + c["signal"] - 2,
    },
)
def macd(fast: int = 12, slow: int = 26, signal: int = 9) -> Stepper:
    f, s, sig = p.primed(p.ema(fast)), p.primed(p.ema(slow)), p.primed(p.ema(signal))
    out: Out = {}
    while True:
        bar = yield out
        line = p.diff(f.send(bar.close), s.send(bar.close))
        sv = sig.send(line)
        out = {"macd": line, "signal": sv, "histogram": p.diff(line, sv)}


@register(
    "stochastic",
    group="momentum",
    reference=(
        "Slow stochastic: %K = SMA(k_smooth) of 100*(C-LL)/(HH-LL) over k bars; %D = SMA(d) of %K."
    ),
    warmup=lambda c: c["k"] + c["k_smooth"] + c["d"] - 3,
)
def stochastic(k: int = 14, k_smooth: int = 3, d: int = 3) -> Stepper:
    s = p.primed(p.stoch(k, k_smooth, d))
    out: Out = {}
    while True:
        bar = yield out
        kd = s.send((bar.high, bar.low, bar.close))
        out = {"k": None, "d": None} if kd is None else {"k": kd[0], "d": kd[1]}


@register(
    "stoch_rsi",
    group="momentum",
    reference=(
        "Slow stochastic over RSI(rsi): stoch(rsi, rsi, rsi, stoch), %K = SMA(k), %D = SMA(d)."
    ),
    warmup=lambda c: c["rsi"] + c["stoch"] + c["k"] + c["d"] - 3,
)
def stoch_rsi(rsi: int = 14, stoch: int = 14, k: int = 3, d: int = 3) -> Stepper:
    r, s = p.primed(_rsi(rsi)), p.primed(p.stoch(stoch, k, d))
    out: Out = {}
    while True:
        bar = yield out
        rv = r.send(bar.close)
        kd = s.send(None if rv is None else (rv, rv, rv))
        out = {"k": None, "d": None} if kd is None else {"k": kd[0], "d": kd[1]}


@register(
    "cci",
    group="momentum",
    reference="(TP - SMA(TP)) / (0.015 * mean absolute deviation of TP), TP = (H+L+C)/3.",
    warmup=lambda c: c["period"] - 1,
)
def cci(period: int = 20) -> Stepper:
    win: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        tp = p.typical(bar.high, bar.low, bar.close)
        win.append(tp)
        if len(win) < period:
            out = {"cci": None}
            continue
        mean = sum(win) / period
        dev = sum(abs(x - mean) for x in win) / period
        out = {"cci": (tp - mean) / (0.015 * dev) if tp != mean and dev != 0 else 0.0}


@register(
    "williams_r",
    group="momentum",
    reference="-100 * (HH - C) / (HH - LL) over n bars.",
    warmup=lambda c: c["period"] - 1,
)
def williams_r(period: int = 14) -> Stepper:
    hl = p.primed(p.high_low(period))
    out: Out = {}
    while True:
        bar = yield out
        hl_n = hl.send(bar)
        if hl_n is None:
            out = {"williams_r": None}
            continue
        hh, ll = hl_n
        out = {"williams_r": (hh - bar.close) / ((hh - ll) / -100) if hh != ll else 0.0}


@register(
    "roc",
    group="momentum",
    reference="100 * (C / C[n bars ago] - 1).",
    warmup=lambda c: c["period"],
)
def roc(period: int = 10) -> Stepper:
    win: deque[float] = deque(maxlen=period + 1)
    out: Out = {}
    while True:
        bar = yield out
        win.append(bar.close)
        if len(win) <= period:
            out = {"roc": None}
        else:
            out = {"roc": (bar.close / win[0] - 1) * 100 if win[0] != 0 else 0.0}


@register(
    "mfi",
    group="momentum",
    reference=(
        "100 * positive / (positive + negative) money flow over n bars; money flow = TP*volume, "
        "positive when TP rises, negative when it falls, neither when unchanged."
    ),
    warmup=lambda c: c["period"],
)
def mfi(period: int = 14) -> Stepper:
    flows: deque[tuple[float, float]] = deque(maxlen=period)
    prev_tp: float | None = None
    out: Out = {}
    while True:
        bar = yield out
        tp = p.typical(bar.high, bar.low, bar.close)
        if prev_tp is not None:
            mf = tp * bar.volume
            flows.append((mf if tp > prev_tp else 0.0, mf if tp < prev_tp else 0.0))
        prev_tp = tp
        if len(flows) < period:
            out = {"mfi": None}
            continue
        pos = sum(f[0] for f in flows)
        total = pos + sum(f[1] for f in flows)
        # TA-Lib reports 0 when total money flow is under 1
        out = {"mfi": 100 * pos / total if total >= 1.0 else 0.0}
