"""The built-in indicator registry.

Each indicator is a generator: send it the next bar, it yields every output for that bar
(None until the output's warm-up is met). Feeding bars one at a time is the incremental
update; `compute` is the same stepper run over a whole series, so the two cannot drift.
"""

import inspect
from collections.abc import Callable, Generator, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from axiom_chartmath.bars import Bar, SessionCalendar

Out = dict[str, float | None]
Stepper = Generator[Out, Bar, None]
Warmup = Callable[[Mapping[str, Any]], int | dict[str, int]]


@dataclass(frozen=True)
class Indicator:
    name: str
    version: int
    group: str
    reference: str
    defaults: Mapping[str, Any]
    make: Callable[..., Stepper]
    # first bar index at which each output is defined on gapless bars; None when it depends on
    # completed sessions or an anchor rather than a bar count
    warmup: Warmup | None
    session: bool


REGISTRY: dict[str, Indicator] = {}


def register(
    name: str,
    *,
    group: str,
    reference: str,
    warmup: Warmup | None,
    version: int = 1,
    session: bool = False,
) -> Callable[[Callable[..., Stepper]], Callable[..., Stepper]]:
    def add(make: Callable[..., Stepper]) -> Callable[..., Stepper]:
        params = inspect.signature(make).parameters.values()
        defaults = {p.name: p.default for p in params if p.name != "calendar"}
        REGISTRY[name] = Indicator(name, version, group, reference, defaults, make, warmup, session)
        return make

    return add


def stream(name: str, calendar: SessionCalendar | None = None, **params: Any) -> Stepper:
    """A primed stepper: `.send(bar)` returns that bar's outputs."""
    spec = REGISTRY[name]
    if spec.session:
        if calendar is None:
            raise ValueError(f"{name} resets on the trading calendar; pass calendar=")
        stepper = spec.make(calendar=calendar, **params)
    else:
        stepper = spec.make(**params)
    next(stepper)
    return stepper


def compute(
    name: str, bars: Iterable[Bar], calendar: SessionCalendar | None = None, **params: Any
) -> dict[str, list[float | None]]:
    stepper = stream(name, calendar, **params)
    rows = [stepper.send(bar) for bar in bars]
    if not rows:
        return {}
    return {key: [row[key] for row in rows] for key in rows[0]}


def chart_defaults(intraday: bool) -> tuple[list[tuple[str, dict[str, int]]], bool]:
    """Studies a new chart opens with, and whether the TPO profile is on.

    Candles are the renderer's default; the F&O panes (strike ladder, positioning) are not
    indicators and are added by the chart, not here.
    """
    if intraday:
        return [("volume", {}), ("session_vwap", {})], True
    return [("volume", {}), ("sma", {"period": 50}), ("sma", {"period": 200})], False
