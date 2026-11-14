import math
from collections import deque

from axiom_chartmath.indicators import primitives as p
from axiom_chartmath.indicators.registry import Out, Stepper, register


@register(
    "bollinger",
    group="volatility",
    reference=(
        "SMA(n) +/- multiplier * population sd of the last n closes; %B = (C-lower)/(upper-lower), "
        "bandwidth = (upper-lower)/middle."
    ),
    warmup=lambda c: c["period"] - 1,
)
def bollinger(period: int = 20, multiplier: float = 2.0) -> Stepper:
    mid, sd = p.primed(p.sma(period)), p.primed(p.pstdev(period))
    none: Out = dict.fromkeys(("upper", "middle", "lower", "percent_b", "bandwidth"))
    out: Out = {}
    while True:
        bar = yield out
        m, s = mid.send(bar.close), sd.send(bar.close)
        if m is None or s is None:
            out = none
            continue
        upper, lower = m + multiplier * s, m - multiplier * s
        out = {
            "upper": upper,
            "middle": m,
            "lower": lower,
            # a flat window has no band to sit inside
            "percent_b": (bar.close - lower) / (upper - lower) if upper != lower else None,
            "bandwidth": (upper - lower) / m if m else None,
        }


@register(
    "atr",
    group="volatility",
    reference="Wilder ATR: mean of the first n true ranges (from bar 1), then Wilder-smoothed.",
    warmup=lambda c: c["period"],
)
def atr(period: int = 14) -> Stepper:
    a = p.primed(p.atr(period))
    out: Out = {}
    while True:
        bar = yield out
        out = {"atr": a.send(bar)}


@register(
    "historical_volatility",
    group="volatility",
    reference="100 * sqrt(annualisation) * population sd of the last n log returns ln(C/C[-1]).",
    warmup=lambda c: c["period"],
)
def historical_volatility(period: int = 20, annualisation: int = 252) -> Stepper:
    sd = p.primed(p.pstdev(period))
    scale = math.sqrt(annualisation) * 100
    prev: float | None = None
    out: Out = {}
    while True:
        bar = yield out
        s = sd.send(None if prev is None else math.log(bar.close / prev))
        prev = bar.close
        out = {"hv": None if s is None else s * scale}


@register(
    "chandelier",
    group="volatility",
    reference="Long stop = HH(n) - multiplier*ATR(n); short stop = LL(n) + multiplier*ATR(n).",
    warmup=lambda c: c["period"],
)
def chandelier(period: int = 22, multiplier: float = 3.0) -> Stepper:
    a = p.primed(p.atr(period))
    highs: deque[float] = deque(maxlen=period)
    lows: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        highs.append(bar.high)
        lows.append(bar.low)
        av = a.send(bar)
        if av is None:
            out = {"long_stop": None, "short_stop": None}
        else:
            out = {
                "long_stop": max(highs) - multiplier * av,
                "short_stop": min(lows) + multiplier * av,
            }
