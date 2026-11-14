import math
from collections import deque

from axiom_chartmath.indicators import primitives as p
from axiom_chartmath.indicators.registry import Out, Stepper, register


@register(
    "sma", group="trend", reference="Mean of the last n closes.", warmup=lambda c: c["period"] - 1
)
def sma(period: int = 20) -> Stepper:
    s = p.primed(p.sma(period))
    out: Out = {}
    while True:
        bar = yield out
        out = {"sma": s.send(bar.close)}


@register(
    "ema",
    group="trend",
    reference="EMA of close, k = 2/(n+1), seeded with the SMA of the first n closes.",
    warmup=lambda c: c["period"] - 1,
)
def ema(period: int = 20) -> Stepper:
    s = p.primed(p.ema(period))
    out: Out = {}
    while True:
        bar = yield out
        out = {"ema": s.send(bar.close)}


@register(
    "wma",
    group="trend",
    reference="Linearly weighted mean of the last n closes, newest weight n.",
    warmup=lambda c: c["period"] - 1,
)
def wma(period: int = 20) -> Stepper:
    s = p.primed(p.wma(period))
    out: Out = {}
    while True:
        bar = yield out
        out = {"wma": s.send(bar.close)}


@register(
    "hma",
    group="trend",
    reference="Hull: WMA(2*WMA(close, n//2) - WMA(close, n), floor(sqrt(n))).",
    warmup=lambda c: c["period"] - 1 + math.isqrt(c["period"]) - 1,
)
def hma(period: int = 20) -> Stepper:
    half, full = p.primed(p.wma(period // 2)), p.primed(p.wma(period))
    hull = p.primed(p.wma(math.isqrt(period)))
    out: Out = {}
    while True:
        bar = yield out
        a, b = half.send(bar.close), full.send(bar.close)
        out = {"hma": hull.send(None if a is None or b is None else 2 * a - b)}


@register(
    "vwma",
    group="trend",
    reference="Sum(close*volume)/sum(volume) over n bars.",
    warmup=lambda c: c["period"] - 1,
)
def vwma(period: int = 20) -> Stepper:
    pv: deque[float] = deque(maxlen=period)
    v: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        pv.append(bar.close * bar.volume)
        v.append(bar.volume)
        total = sum(v)
        out = {"vwma": sum(pv) / total if len(v) == period and total else None}


@register(
    "dema",
    group="trend",
    reference="2*EMA - EMA(EMA), each EMA SMA-seeded.",
    warmup=lambda c: 2 * (c["period"] - 1),
)
def dema(period: int = 20) -> Stepper:
    e1, e2 = p.primed(p.ema(period)), p.primed(p.ema(period))
    out: Out = {}
    while True:
        bar = yield out
        a = e1.send(bar.close)
        b = e2.send(a)
        out = {"dema": p.diff(None if a is None else 2 * a, b)}


@register(
    "tema",
    group="trend",
    reference="3*EMA - 3*EMA(EMA) + EMA(EMA(EMA)), each EMA SMA-seeded.",
    warmup=lambda c: 3 * (c["period"] - 1),
)
def tema(period: int = 20) -> Stepper:
    e1, e2, e3 = (p.primed(p.ema(period)) for _ in range(3))
    out: Out = {}
    while True:
        bar = yield out
        a = e1.send(bar.close)
        b = e2.send(a)
        c = e3.send(b)
        out = {"tema": None if a is None or b is None or c is None else 3 * a - 3 * b + c}


@register(
    "supertrend",
    group="trend",
    reference=(
        "Bands hl2 +/- multiplier*ATR (Wilder). The lower band only rises and the upper only "
        "falls unless the previous close broke them. Direction starts down, turns up on a close "
        "above the upper band and down on a close below the lower; the line is the active band. "
        "direction: 1 up, -1 down."
    ),
    warmup=lambda c: c["period"],
)
def supertrend(period: int = 10, multiplier: float = 3.0) -> Stepper:
    atr = p.primed(p.atr(period))
    prev: tuple[float, float, float, bool] | None = None  # close, lower, upper, up
    out: Out = {}
    while True:
        bar = yield out
        a = atr.send(bar)
        if a is None:
            out = {"supertrend": None, "direction": None}
            continue
        mid = (bar.high + bar.low) / 2
        lower, upper = mid - multiplier * a, mid + multiplier * a
        if prev is None:
            up = False
        else:
            close_1, lower_1, upper_1, up_1 = prev
            if not (lower > lower_1 or close_1 < lower_1):
                lower = lower_1
            if not (upper < upper_1 or close_1 > upper_1):
                upper = upper_1
            up = bar.close >= lower if up_1 else bar.close > upper
        prev = (bar.close, lower, upper, up)
        out = {"supertrend": lower if up else upper, "direction": 1.0 if up else -1.0}


@register(
    "ichimoku",
    group="trend",
    reference=(
        "Tenkan = midprice(9), kijun = midprice(26), senkou A = (tenkan+kijun)/2, senkou B = "
        "midprice(52); midprice(n) = (highest high + lowest low)/2. Values are unshifted: the "
        "chart draws the spans 26 bars ahead. The lagging line is the close drawn 26 bars back."
    ),
    warmup=lambda c: {
        "tenkan": c["tenkan"] - 1,
        "kijun": c["kijun"] - 1,
        "senkou_a": max(c["tenkan"], c["kijun"]) - 1,
        "senkou_b": c["senkou_b"] - 1,
    },
)
def ichimoku(tenkan: int = 9, kijun: int = 26, senkou_b: int = 52) -> Stepper:
    t, k, b = (
        p.primed(p.midprice(tenkan)),
        p.primed(p.midprice(kijun)),
        p.primed(p.midprice(senkou_b)),
    )
    out: Out = {}
    while True:
        bar = yield out
        tv, kv = t.send(bar), k.send(bar)
        out = {
            "tenkan": tv,
            "kijun": kv,
            "senkou_a": None if tv is None or kv is None else (tv + kv) / 2,
            "senkou_b": b.send(bar),
        }


@register(
    "psar",
    group="trend",
    reference=(
        "Wilder's parabolic SAR as TA-Lib computes it: the first trend is short when bar 1 has a "
        "minus directional move, else long; the acceleration factor starts at `acceleration`, "
        "steps by it on each new extreme, and caps at `maximum`."
    ),
    warmup=lambda c: 1,
)
def psar(acceleration: float = 0.02, maximum: float = 0.2) -> Stepper:
    acceleration = min(acceleration, maximum)
    bar = yield {}
    first = bar
    bar = yield {"psar": None}
    diff_p, diff_m = bar.high - first.high, first.low - bar.low
    long = not (diff_m > 0 and diff_p < diff_m)
    ep, sar = (bar.high, first.low) if long else (bar.low, first.high)
    af = acceleration
    new_low, new_high = bar.low, bar.high
    while True:
        prev_low, prev_high = new_low, new_high
        new_low, new_high = bar.low, bar.high
        if long:
            if new_low <= sar:
                long, sar = False, max(ep, prev_high, new_high)
                out = sar
                af, ep = acceleration, new_low
                sar = max(sar + af * (ep - sar), prev_high, new_high)
            else:
                out = sar
                if new_high > ep:
                    ep, af = new_high, min(af + acceleration, maximum)
                sar = min(sar + af * (ep - sar), prev_low, new_low)
        elif new_high >= sar:
            long, sar = True, min(ep, prev_low, new_low)
            out = sar
            af, ep = acceleration, new_high
            sar = min(sar + af * (ep - sar), prev_low, new_low)
        else:
            out = sar
            if new_low < ep:
                ep, af = new_low, min(af + acceleration, maximum)
            sar = max(sar + af * (ep - sar), prev_high, new_high)
        bar = yield {"psar": out}


@register(
    "adx",
    group="trend",
    reference=(
        "Wilder DMI/ADX as TA-Lib computes it: +DM/-DM and TR are summed over bars 1..n-1, then "
        "smoothed S = S - S/n + x; DI = 100*DM/TR from bar n; ADX = mean of the first n DX, then "
        "Wilder-smoothed."
    ),
    warmup=lambda c: {"plus_di": c["period"], "minus_di": c["period"], "adx": 2 * c["period"] - 1},
)
def adx(period: int = 14) -> Stepper:
    n = period
    bar = yield {}
    prev = bar
    pdm = mdm = tr = 0.0
    dx_sum = 0.0
    adx_value: float | None = None
    i = 0
    out: Out = {"plus_di": None, "minus_di": None, "adx": None}
    while True:
        bar = yield out
        i += 1
        diff_p, diff_m = bar.high - prev.high, prev.low - bar.low
        dp = diff_p if diff_p > 0 and diff_p > diff_m else 0.0
        dm = diff_m if diff_m > 0 and diff_p < diff_m else 0.0
        t = max(bar.high - bar.low, abs(bar.high - prev.close), abs(bar.low - prev.close))
        prev = bar
        if i < n:
            pdm, mdm, tr = pdm + dp, mdm + dm, tr + t
            continue
        pdm, mdm, tr = pdm - pdm / n + dp, mdm - mdm / n + dm, tr - tr / n + t
        plus, minus = (0.0, 0.0) if p.is_zero(tr) else (100 * pdm / tr, 100 * mdm / tr)
        dx = (
            None
            if p.is_zero(tr) or p.is_zero(plus + minus)
            else 100 * abs(minus - plus) / (plus + minus)
        )
        if i < 2 * n:
            dx_sum += dx or 0.0
            if i == 2 * n - 1:
                adx_value = dx_sum / n
        elif dx is not None and adx_value is not None:
            adx_value = (adx_value * (n - 1) + dx) / n
        out = {"plus_di": plus, "minus_di": minus, "adx": adx_value}


@register(
    "donchian",
    group="trend",
    reference="Highest high and lowest low of the last n bars, and their mean.",
    warmup=lambda c: c["period"] - 1,
)
def donchian(period: int = 20) -> Stepper:
    highs: deque[float] = deque(maxlen=period)
    lows: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        highs.append(bar.high)
        lows.append(bar.low)
        if len(highs) < period:
            out = {"upper": None, "middle": None, "lower": None}
        else:
            hh, ll = max(highs), min(lows)
            out = {"upper": hh, "middle": (hh + ll) / 2, "lower": ll}


@register(
    "keltner",
    group="trend",
    reference="EMA(close, n) +/- multiplier * Wilder ATR(atr_period).",
    warmup=lambda c: max(c["period"] - 1, c["atr_period"]),
)
def keltner(period: int = 20, atr_period: int = 10, multiplier: float = 2.0) -> Stepper:
    mid, atr = p.primed(p.ema(period)), p.primed(p.atr(atr_period))
    out: Out = {}
    while True:
        bar = yield out
        m, a = mid.send(bar.close), atr.send(bar)
        if m is None or a is None:
            out = {"upper": None, "middle": m, "lower": None}
        else:
            out = {"upper": m + multiplier * a, "middle": m, "lower": m - multiplier * a}
