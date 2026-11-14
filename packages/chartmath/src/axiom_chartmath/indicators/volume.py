import math
from collections import deque
from datetime import date, datetime

from axiom_chartmath.bars import Bar, SessionCalendar
from axiom_chartmath.indicators.primitives import typical
from axiom_chartmath.indicators.registry import Out, Stepper, register


@register("volume", group="volume", reference="The bar's traded volume.", warmup=lambda c: 0)
def volume() -> Stepper:
    out: Out = {}
    while True:
        bar = yield out
        out = {"volume": bar.volume}


@register(
    "obv",
    group="volume",
    reference="On-balance volume: starts at the first bar's volume, +V on an up close, -V on down.",
    warmup=lambda c: 0,
)
def obv() -> Stepper:
    bar = yield {}
    total, prev = bar.volume, bar.close
    while True:
        bar = yield {"obv": total}
        if bar.close > prev:
            total += bar.volume
        elif bar.close < prev:
            total -= bar.volume
        prev = bar.close


def _mfm(bar: Bar) -> float:
    rng = bar.high - bar.low
    return ((bar.close - bar.low) - (bar.high - bar.close)) / rng if rng > 0 else 0.0


@register(
    "ad",
    group="volume",
    reference="Accumulation/distribution: running sum of ((C-L)-(H-C))/(H-L) * V.",
    warmup=lambda c: 0,
)
def ad() -> Stepper:
    total = 0.0
    out: Out = {}
    while True:
        bar = yield out
        total += _mfm(bar) * bar.volume
        out = {"ad": total}


@register(
    "cmf",
    group="volume",
    reference="Chaikin money flow: sum(((C-L)-(H-C))/(H-L) * V) / sum(V) over n bars.",
    warmup=lambda c: c["period"] - 1,
)
def cmf(period: int = 20) -> Stepper:
    mfv: deque[float] = deque(maxlen=period)
    vol: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        mfv.append(_mfm(bar) * bar.volume)
        vol.append(bar.volume)
        total = sum(vol)
        out = {"cmf": sum(mfv) / total if len(vol) == period and total else None}


@register(
    "relative_volume",
    group="volume",
    reference="Volume / mean volume of the n bars before it.",
    warmup=lambda c: c["period"],
)
def relative_volume(period: int = 20) -> Stepper:
    prior: deque[float] = deque(maxlen=period)
    out: Out = {}
    while True:
        bar = yield out
        mean = sum(prior) / period
        out = {"rvol": bar.volume / mean if len(prior) == period and mean else None}
        prior.append(bar.volume)


VWAP_KEYS = ("vwap", "upper_1", "lower_1", "upper_2", "lower_2")
NO_VWAP: Out = dict.fromkeys(VWAP_KEYS)


def vwap_bands(pv: float, v: float, p2v: float) -> Out:
    """VWAP of typical price with volume-weighted sd bands at 1 and 2 from running sums."""
    if not v:
        return NO_VWAP
    vwap = pv / v
    sd = math.sqrt(max(p2v / v - vwap * vwap, 0.0))
    return {
        "vwap": vwap,
        "upper_1": vwap + sd,
        "lower_1": vwap - sd,
        "upper_2": vwap + 2 * sd,
        "lower_2": vwap - 2 * sd,
    }


@register(
    "session_vwap",
    group="volume",
    reference=(
        "VWAP of (H+L+C)/3 from the session's first bar, reset at 09:15 IST each trading day, "
        "with volume-weighted sd bands at 1 and 2. Bars outside a session draw nothing."
    ),
    warmup=None,
    session=True,
)
def session_vwap(calendar: SessionCalendar) -> Stepper:
    day: date | None = None
    pv = v = p2v = 0.0
    out: Out = {}
    while True:
        bar = yield out
        d = calendar.session_date(bar.ts)
        if d is None:
            out = NO_VWAP
            continue
        if d != day:
            day, pv, v, p2v = d, 0.0, 0.0, 0.0
        tp = typical(bar.high, bar.low, bar.close)
        pv, v, p2v = pv + tp * bar.volume, v + bar.volume, p2v + tp * tp * bar.volume
        out = vwap_bands(pv, v, p2v)


@register(
    "anchored_vwap",
    group="volume",
    reference=(
        "VWAP of (H+L+C)/3 from the first bar at or after `anchor` (ISO time: a click, an expiry, "
        "results or a gap day), never reset, with volume-weighted sd bands at 1 and 2."
    ),
    warmup=None,
)
def anchored_vwap(anchor: str) -> Stepper:
    start = datetime.fromisoformat(anchor)
    if start.tzinfo is None:
        raise ValueError("anchor needs a timezone offset, e.g. 2026-11-04T09:15:00+05:30")
    pv = v = p2v = 0.0
    out: Out = {}
    while True:
        bar = yield out
        if bar.ts < start:
            out = NO_VWAP
            continue
        tp = typical(bar.high, bar.low, bar.close)
        pv, v, p2v = pv + tp * bar.volume, v + bar.volume, p2v + tp * tp * bar.volume
        out = vwap_bands(pv, v, p2v)
