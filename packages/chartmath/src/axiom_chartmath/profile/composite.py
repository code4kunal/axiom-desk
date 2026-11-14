"""Composite profiles over nested timeframes and the reference levels sessions carry forward."""

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime

from axiom_chartmath.bars import Bar
from axiom_chartmath.profile.tpo import Distribution, SessionProfile, distribution, row_of

FALLBACK_SESSIONS = 5


def composite(profiles: Sequence[SessionProfile]) -> Distribution:
    """Sum of the sessions' TPO and volume rows. All must share one parameter version."""
    _one_version(profiles)
    tpo: dict[int, int] = defaultdict(int)
    volume: dict[int, float] = defaultdict(float)
    for p in profiles:
        for r, c in p.tpo.items():
            tpo[r] += c
        for r, v in p.volume.items():
            volume[r] += v
    return distribution(tpo, volume, profiles[0].params)


def _one_version(profiles: Sequence[SessionProfile]) -> None:
    # rows from different row sizes or cut-offs are not comparable
    versions = {p.params_version for p in profiles}
    if len(versions) != 1:
        raise ValueError(f"profiles need one parameter version, got {sorted(versions)}")


def _overlap(a: Distribution, b: Distribution) -> bool:
    return a.value_low <= b.value_high and b.value_low <= a.value_high


def current_balance(profiles: Sequence[SessionProfile]) -> Sequence[SessionProfile]:
    """Sessions since the market last entered balance, else the last five.

    Balance is a run of sessions whose value areas each overlap the session before. It began on
    the first session of the run that ends today, provided the session before that run shows
    value elsewhere. Today outside yesterday's value, or a run reaching back past the data,
    has no observed start, so the rolling five sessions stand in.
    """
    start = len(profiles) - 1
    while start > 0 and _overlap(profiles[start], profiles[start - 1]):
        start -= 1
    if start == len(profiles) - 1 or start == 0:
        return profiles[-FALLBACK_SESSIONS:]
    return profiles[start:]


def expiry_cycle(
    profiles: Sequence[SessionProfile], expiries: Iterable[date]
) -> Sequence[SessionProfile]:
    """Sessions after the last expiry before today, up to today. `expiries` is the SEBI calendar
    in force; an expiry session belongs to the cycle it ends."""
    today = profiles[-1].session
    last = max((e for e in expiries if e < today), default=None)
    return [p for p in profiles if last is None or p.session > last]


def back_adjust(bars: Iterable[Bar], rolls: Iterable[tuple[datetime, float]]) -> list[Bar]:
    """Basis-adjusted continuous futures: `(first bar on the new contract, new - old price)`.

    Every bar before a roll moves by that roll's basis, so a roll adds no false structure.
    """
    rolls = list(rolls)
    out: list[Bar] = []
    for bar in bars:
        shift = sum(basis for ts, basis in rolls if bar.ts < ts)
        out.append(
            bar
            if not shift
            else replace(
                bar,
                open=bar.open + shift,
                high=bar.high + shift,
                low=bar.low + shift,
                close=bar.close + shift,
            )
        )
    return out


@dataclass(frozen=True)
class Level:
    kind: str  # naked_poc, single_print, poor_high, poor_low
    price: float
    session: date


def carried_levels(profiles: Sequence[SessionProfile]) -> list[Level]:
    """Naked POCs, unfilled single prints and unrepaired poor highs and lows still open after
    the last session. A POC or single print clears once a later session trades its row; a poor
    high clears on a later trade above it, a poor low on one below."""
    _one_version(profiles)
    out: list[Level] = []
    for i, p in enumerate(profiles):
        rs = p.params.row_size
        later = [(min(q.tpo), max(q.tpo)) for q in profiles[i + 1 :]]
        top, bottom = max(p.tpo), min(p.tpo)
        if not _traded(row_of(p.poc, rs), later):
            out.append(Level("naked_poc", p.poc, p.session))
        out += [
            Level("single_print", s, p.session)
            for s in p.single_prints
            if not _traded(row_of(s, rs), later)
        ]
        if p.poor_high and not any(hi > top for _, hi in later):
            out.append(Level("poor_high", p.price(top), p.session))
        if p.poor_low and not any(lo < bottom for lo, _ in later):
            out.append(Level("poor_low", p.price(bottom), p.session))
    return out


def _traded(row: int, ranges: list[tuple[int, int]]) -> bool:
    return any(lo <= row <= hi for lo, hi in ranges)
