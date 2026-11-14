"""TPO and volume profiles for one session, and the distribution statistics shared by composites.

Rows are integer indices: row r covers prices [r*row_size, (r+1)*row_size).
"""

import hashlib
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta

from axiom_chartmath.bars import IST, Bar, SessionCalendar

PERIOD = timedelta(minutes=30)
IB_PERIODS = 2


@dataclass(frozen=True)
class ProfileParams:
    """Per-instrument profile parameters. Any change gives a new `version`, which every profile
    carries, so a profile is only compared with others built the same way."""

    row_size: float
    value_area: float = 0.70
    hvn_ratio: float = 0.6
    lvn_ratio: float = 0.3
    smoothing_rows: float = 2.0

    @property
    def version(self) -> str:
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:12]


def row_of(price: float, row_size: float) -> int:
    return math.floor(round(price / row_size, 9))


def price_of(row: int, row_size: float) -> float:
    return round(row * row_size, 9)


def poc_row(counts: Mapping[int, float]) -> int:
    lo, hi = min(counts), max(counts)
    top = max(counts.values())
    mid = (lo + hi) / 2
    return min((r for r, c in counts.items() if c == top), key=lambda r: (abs(r - mid), r))


def value_area_rows(counts: Mapping[int, float], share: float) -> tuple[int, int]:
    """Two-row method: from the POC, add the busier of the next two rows above or below until the
    area holds `share` of the total. Equal pairs add both sides, so a flat profile stays centred."""
    lo = hi = poc_row(counts)
    bottom, top = min(counts), max(counts)
    acc, target = counts[lo], share * sum(counts.values())
    while acc < target and (lo > bottom or hi < top):
        up = [r for r in (hi + 1, hi + 2) if r <= top]
        down = [r for r in (lo - 1, lo - 2) if r >= bottom]
        su = sum(counts.get(r, 0) for r in up)
        sd = sum(counts.get(r, 0) for r in down)
        take_up = bool(up) and (not down or su >= sd)
        take_down = bool(down) and (not up or sd >= su)
        if take_up:
            hi, acc = up[-1], acc + su
        if take_down:
            lo, acc = down[-1], acc + sd
    return lo, hi


def smoothed(counts: Mapping[int, float], sigma: float) -> dict[int, float]:
    reach = math.ceil(3 * sigma)
    kernel = {k: math.exp(-(k * k) / (2 * sigma * sigma)) for k in range(-reach, reach + 1)}
    norm = sum(kernel.values())
    rows = range(min(counts), max(counts) + 1)
    return {r: sum(w * counts.get(r + k, 0) for k, w in kernel.items()) / norm for r in rows}


@dataclass(frozen=True)
class Distribution:
    params: ProfileParams
    tpo: Mapping[int, int]
    volume: Mapping[int, float]
    poc: float
    value_low: float
    value_high: float
    vpoc: float | None
    volume_value_low: float | None
    volume_value_high: float | None
    hvn: tuple[float, ...]
    lvn: tuple[float, ...]

    @property
    def params_version(self) -> str:
        return self.params.version

    def price(self, row: int) -> float:
        return price_of(row, self.params.row_size)


def distribution(
    tpo: Mapping[int, int], volume: Mapping[int, float], params: ProfileParams
) -> Distribution:
    rs = params.row_size
    va_lo, va_hi = value_area_rows(tpo, params.value_area)
    vpoc = vlo = vhi = None
    hvn: list[int] = []
    lvn: list[int] = []
    if sum(volume.values()) > 0:
        vpoc = price_of(poc_row(volume), rs)
        lo, hi = value_area_rows(volume, params.value_area)
        vlo, vhi = price_of(lo, rs), price_of(hi, rs)
        s = smoothed(volume, params.smoothing_rows)
        peak = max(s.values())
        rows = sorted(s)
        hvn = [
            r
            for r in rows
            if s[r] >= s.get(r - 1, 0.0)
            and s[r] > s.get(r + 1, 0.0)
            and s[r] > params.hvn_ratio * peak
        ]
        lvn = [
            r
            for r in rows[1:-1]
            if s[r] <= s[r - 1] and s[r] < s[r + 1] and s[r] < params.lvn_ratio * peak
        ]
    return Distribution(
        params=params,
        tpo=dict(sorted(tpo.items())),
        volume=dict(sorted(volume.items())),
        poc=price_of(poc_row(tpo), rs),
        value_low=price_of(va_lo, rs),
        value_high=price_of(va_hi, rs),
        vpoc=vpoc,
        volume_value_low=vlo,
        volume_value_high=vhi,
        hvn=tuple(price_of(r, rs) for r in hvn),
        lvn=tuple(price_of(r, rs) for r in lvn),
    )


@dataclass(frozen=True)
class Period:
    start: datetime
    low: float
    high: float
    # the 15:15-15:30 period is 15 minutes; flagged so day-type thresholds can leave it out
    half: bool


@dataclass(frozen=True)
class SessionProfile(Distribution):
    session: date
    periods: tuple[Period, ...]
    ib_low: float | None
    ib_high: float | None
    single_prints: tuple[float, ...]
    poor_high: bool
    poor_low: bool


def session_profiles(
    bars: Iterable[Bar], calendar: SessionCalendar, params: ProfileParams
) -> list[SessionProfile]:
    """One profile per trading session, from bars of any interval up to 30 minutes.

    Each 30-minute period from 09:15 IST prints one TPO on every row it traded; each bar's volume
    is spread evenly over the rows it spans. Bars outside a session are ignored.
    """
    by_day: dict[date, list[Bar]] = defaultdict(list)
    for bar in bars:
        d = calendar.session_date(bar.ts)
        if d is not None:
            by_day[d].append(bar)
    return [_session(d, day_bars, calendar, params) for d, day_bars in sorted(by_day.items())]


def _session(
    day: date, bars: list[Bar], calendar: SessionCalendar, params: ProfileParams
) -> SessionProfile:
    rs = params.row_size
    open_ = datetime.combine(day, calendar.open, IST)
    close = datetime.combine(day, calendar.close, IST)
    ranges: dict[int, tuple[float, float]] = {}
    volume: dict[int, float] = defaultdict(float)
    for bar in bars:
        i = (bar.ts - open_) // PERIOD
        lo, hi = ranges.get(i, (bar.low, bar.high))
        ranges[i] = (min(lo, bar.low), max(hi, bar.high))
        rows = range(row_of(bar.low, rs), row_of(bar.high, rs) + 1)
        for r in rows:
            volume[r] += bar.volume / len(rows)
    tpo: dict[int, int] = defaultdict(int)
    periods: list[Period] = []
    for i, (lo, hi) in sorted(ranges.items()):
        for r in range(row_of(lo, rs), row_of(hi, rs) + 1):
            tpo[r] += 1
        start = open_ + i * PERIOD
        periods.append(Period(start, lo, hi, half=start + PERIOD > close))
    ib = [p for p in periods if p.start < open_ + IB_PERIODS * PERIOD]
    bottom, top = min(tpo), max(tpo)
    below: set[int] = set()
    seen = False
    for r in range(bottom, top + 1):
        if seen and tpo.get(r, 0) == 1:
            below.add(r)
        seen = seen or tpo.get(r, 0) >= 2
    singles: list[int] = []
    seen = False
    for r in range(top, bottom - 1, -1):
        if seen and r in below:
            singles.append(r)
        seen = seen or tpo.get(r, 0) >= 2
    singles.reverse()
    return SessionProfile(
        **vars(distribution(tpo, volume, params)),
        session=day,
        periods=tuple(periods),
        ib_low=min((p.low for p in ib), default=None),
        ib_high=max((p.high for p in ib), default=None),
        single_prints=tuple(price_of(r, rs) for r in singles),
        poor_high=tpo[top] >= 2,
        poor_low=tpo[bottom] >= 2,
    )
