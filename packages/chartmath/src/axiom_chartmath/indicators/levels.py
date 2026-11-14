from collections.abc import Callable, Generator, Hashable
from datetime import date

from axiom_chartmath.bars import Bar, SessionCalendar
from axiom_chartmath.indicators.primitives import primed
from axiom_chartmath.indicators.registry import Out, Stepper, register

HLC = tuple[float, float, float]


def _prior(
    calendar: SessionCalendar, period: Callable[[date], Hashable]
) -> Generator[HLC | None, Bar, None]:
    """High, low and close of the last completed period (day, week, month) before the bar's own.

    Only session bars count, so a holiday or pre-open print never forms or moves a period.
    """
    current: Hashable = None
    running: HLC | None = None
    prior: HLC | None = None
    out: HLC | None = None
    while True:
        bar = yield out
        d = calendar.session_date(bar.ts)
        if d is None:
            out = None
            continue
        key = period(d)
        if running is None or key != current:
            current, prior = key, running or prior
            running = (bar.high, bar.low, bar.close)
        else:
            running = (max(running[0], bar.high), min(running[1], bar.low), bar.close)
        out = prior


def _from_prior_day(calendar: SessionCalendar, f: Callable[[float, float, float], Out]) -> Stepper:
    prior = primed(_prior(calendar, lambda d: d))
    none = dict.fromkeys(f(1.0, 0.0, 0.0))
    out: Out = {}
    while True:
        bar = yield out
        hlc = prior.send(bar)
        out = none if hlc is None else f(*hlc)


def _classic(h: float, lo: float, c: float) -> Out:
    pp = (h + lo + c) / 3
    return {
        "pivot": pp,
        "r1": 2 * pp - lo,
        "r2": pp + (h - lo),
        "r3": h + 2 * (pp - lo),
        "s1": 2 * pp - h,
        "s2": pp - (h - lo),
        "s3": lo - 2 * (h - pp),
    }


def _camarilla(h: float, lo: float, c: float) -> Out:
    r = (h - lo) * 1.1
    return {
        "r1": c + r / 12,
        "r2": c + r / 6,
        "r3": c + r / 4,
        "r4": c + r / 2,
        "s1": c - r / 12,
        "s2": c - r / 6,
        "s3": c - r / 4,
        "s4": c - r / 2,
    }


def _cpr(h: float, lo: float, c: float) -> Out:
    pp = (h + lo + c) / 3
    bc = (h + lo) / 2
    tc = 2 * pp - bc
    return {"pivot": pp, "top": max(tc, bc), "bottom": min(tc, bc)}


@register(
    "pivots_classic",
    group="levels",
    reference=(
        "Floor pivots from the previous session: P = (H+L+C)/3, R1 = 2P-L, S1 = 2P-H, "
        "R2 = P+(H-L), S2 = P-(H-L), R3 = H+2(P-L), S3 = L-2(H-P)."
    ),
    warmup=None,
    session=True,
)
def pivots_classic(calendar: SessionCalendar) -> Stepper:
    return _from_prior_day(calendar, _classic)


@register(
    "camarilla",
    group="levels",
    reference="Camarilla from the previous session: C +/- (H-L)*1.1/12, /6, /4, /2 for levels 1-4.",
    warmup=None,
    session=True,
)
def camarilla(calendar: SessionCalendar) -> Stepper:
    return _from_prior_day(calendar, _camarilla)


@register(
    "cpr",
    group="levels",
    reference=(
        "Central pivot range from the previous session: P = (H+L+C)/3, BC = (H+L)/2, "
        "TC = 2P-BC; top and bottom are the larger and smaller of TC and BC."
    ),
    warmup=None,
    session=True,
)
def cpr(calendar: SessionCalendar) -> Stepper:
    return _from_prior_day(calendar, _cpr)


@register(
    "previous_levels",
    group="levels",
    reference=(
        "High and low of the previous trading day, ISO week and calendar month, over session "
        "bars only."
    ),
    warmup=None,
    session=True,
)
def previous_levels(calendar: SessionCalendar) -> Stepper:
    day = primed(_prior(calendar, lambda d: d))
    week = primed(_prior(calendar, lambda d: d.isocalendar()[:2]))
    month = primed(_prior(calendar, lambda d: (d.year, d.month)))
    out: Out = {}
    while True:
        bar = yield out
        out = {}
        for name, src in (("day", day), ("week", week), ("month", month)):
            hlc = src.send(bar)
            out[f"{name}_high"] = None if hlc is None else hlc[0]
            out[f"{name}_low"] = None if hlc is None else hlc[1]
