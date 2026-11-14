import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import pytest
from axiom_chartmath.bars import IST, Bar, SessionCalendar
from axiom_chartmath.profile import (
    ProfileParams,
    back_adjust,
    carried_levels,
    composite,
    current_balance,
    expiry_cycle,
    session_profiles,
)

GOLDEN = Path(__file__).parents[3] / "specs" / "quant" / "golden" / "profile"
CAL = SessionCalendar(frozenset({date(2026, 11, 10)}))
ROW5 = ProfileParams(row_size=5.0)


def load(name: str) -> dict[str, Any]:
    return json.loads((GOLDEN / f"{name}.json").read_text())


def to_bars(raw: list[dict[str, Any]]) -> list[Bar]:
    return [
        Bar(
            datetime.fromisoformat(b["ts"]), b["open"], b["high"], b["low"], b["close"], b["volume"]
        )
        for b in raw
    ]


def session(day: date, ranges: list[tuple[float, float]], volume: float = 1000.0) -> list[Bar]:
    """One bar per 30-minute period from 09:15, each spanning (low, high)."""
    start = datetime.combine(day, time(9, 15), IST)
    return [
        Bar(start + timedelta(minutes=30 * i), lo, hi, lo, hi, volume)
        for i, (lo, hi) in enumerate(ranges)
    ]


def trading_days(start: date, n: int) -> list[date]:
    days: list[date] = []
    d = start
    while len(days) < n:
        if d.weekday() < 5 and d not in CAL.holidays:
            days.append(d)
        d += timedelta(days=1)
    return days


@pytest.mark.golden
def test_hand_checked_session_gives_the_golden_poc_value_area_and_single_prints() -> None:
    g = load("session")
    [p] = session_profiles(to_bars(g["bars"]), CAL, ProfileParams(**g["params"]))
    want = g["expected"]
    assert {str(p.price(r)): c for r, c in p.tpo.items()} == {
        str(float(k)): v for k, v in want["tpo"].items()
    }
    got = {
        "poc": p.poc,
        "value_low": p.value_low,
        "value_high": p.value_high,
        "vpoc": p.vpoc,
        "volume_value_low": p.volume_value_low,
        "volume_value_high": p.volume_value_high,
        "ib_high": p.ib_high,
        "ib_low": p.ib_low,
        "single_prints": list(p.single_prints),
        "poor_high": p.poor_high,
        "poor_low": p.poor_low,
        "half_periods": [i for i, period in enumerate(p.periods) if period.half],
    }
    assert got == {k: v for k, v in want.items() if k != "tpo"}


def test_the_1515_period_is_flagged_half() -> None:
    [p] = session_profiles(to_bars(load("session")["bars"]), CAL, ROW5)
    assert len(p.periods) == 13
    assert [x.half for x in p.periods] == [False] * 12 + [True]
    assert p.periods[12].start == datetime(2026, 11, 4, 15, 15, tzinfo=IST)


def test_a_row_size_change_bumps_the_parameter_version() -> None:
    assert ProfileParams(row_size=5.0).version == ProfileParams(row_size=5.0).version
    assert ProfileParams(row_size=5.0).version != ProfileParams(row_size=10.0).version
    assert (
        ProfileParams(row_size=5.0).version != ProfileParams(row_size=5.0, lvn_ratio=0.25).version
    )
    bars = to_bars(load("session")["bars"])
    assert session_profiles(bars, CAL, ROW5)[0].params_version == ROW5.version


def test_composites_refuse_mixed_parameter_versions() -> None:
    bars = to_bars(load("session")["bars"])
    a = session_profiles(bars, CAL, ROW5)
    b = session_profiles(bars, CAL, ProfileParams(row_size=10.0))
    with pytest.raises(ValueError, match="version"):
        composite([*a, *b])


def balance_sessions(ranges: list[tuple[float, float]]) -> list[Bar]:
    days = trading_days(date(2026, 11, 2), len(ranges))
    return [bar for d, r in zip(days, ranges, strict=True) for bar in session(d, [r])]


def test_current_balance_starts_on_the_session_balance_began() -> None:
    # one flat period per session: value is the middle 70% of each range.
    # s0 sits apart; s1..s4 overlap each other in value, so balance began at s1.
    profiles = session_profiles(
        balance_sessions([(100, 200), (300, 400), (310, 390), (320, 400), (305, 385)]), CAL, ROW5
    )
    assert profiles[0].value_high < profiles[1].value_low
    assert [p.session for p in current_balance(profiles)] == [p.session for p in profiles[1:]]


def test_current_balance_falls_back_to_five_sessions_without_a_balance_start() -> None:
    # every session overlaps the one before back to the first: no observed start
    overlapping = session_profiles(
        balance_sessions(
            [(305, 395), (300, 400), (310, 390), (320, 400), (305, 385), (300, 380), (310, 400)]
        ),
        CAL,
        ROW5,
    )
    assert [p.session for p in current_balance(overlapping)] == [
        p.session for p in overlapping[-5:]
    ]
    # today moved away from yesterday's value: imbalance, so no balance to start from
    breakout = session_profiles(
        balance_sessions([(300, 400), (310, 390), (320, 400), (305, 385), (300, 380), (600, 700)]),
        CAL,
        ROW5,
    )
    assert [p.session for p in current_balance(breakout)] == [p.session for p in breakout[-5:]]


def test_expiry_cycle_runs_from_the_last_expiry_to_today() -> None:
    profiles = session_profiles(
        balance_sessions([(100, 120)] * 8), CAL, ROW5
    )  # 2-4, 5, 6, 9, 11, 12 Nov (10 Nov holiday)
    expiries = [date(2026, 10, 27), date(2026, 11, 3), date(2026, 11, 24)]
    cycle = expiry_cycle(profiles, expiries)
    assert [p.session for p in cycle] == [
        p.session for p in profiles if p.session > date(2026, 11, 3)
    ]


def test_a_40_point_roll_adds_no_false_hvn_once_basis_adjusted() -> None:
    # two sessions on the old contract and two on the new, same shape, new contract 40 points rich
    days = trading_days(date(2026, 11, 23), 4)
    hump = [(23990.0, 24010.0)] * 12

    def shifted(k: float) -> list[tuple[float, float]]:
        return [(lo + k, hi + k) for lo, hi in hump]

    raw = [
        *session(days[0], hump),
        *session(days[1], hump),
        *session(days[2], shifted(40)),
        *session(days[3], shifted(40)),
    ]
    roll = datetime.combine(days[2], time(9, 15), IST)
    spliced = composite(session_profiles(raw, CAL, ROW5))
    assert len(spliced.hvn) == 2  # the splice shows two value areas that never traded
    adjusted = composite(session_profiles(back_adjust(raw, [(roll, 40.0)]), CAL, ROW5))
    assert adjusted.hvn == (24040.0,)
    assert adjusted.lvn == ()


def test_a_naked_poc_is_carried_until_a_later_session_trades_through_it() -> None:
    days = trading_days(date(2026, 11, 2), 3)
    bars = [
        *session(days[0], [(100, 140), (115, 125), (115, 125)]),  # POC 120
        *session(days[1], [(150, 180), (160, 170)]),  # stays above 120
        *session(days[2], [(110, 130)]),  # trades back through 120
    ]
    profiles = session_profiles(bars, CAL, ROW5)
    assert profiles[0].poc == 120

    def first_session_naked_pocs(upto: int) -> list[float]:
        levels = carried_levels(profiles[:upto])
        return [lv.price for lv in levels if lv.kind == "naked_poc" and lv.session == days[0]]

    assert first_session_naked_pocs(2) == [120]
    assert first_session_naked_pocs(3) == []


def test_single_prints_and_poor_extremes_carry_until_traded() -> None:
    g = load("session")
    day0 = to_bars(g["bars"])
    later = session(date(2026, 11, 5), [(24055, 24070)])  # stays inside 24055-24070
    profiles = session_profiles([*day0, *later], CAL, ROW5)
    kinds = {(lv.kind, lv.price) for lv in carried_levels(profiles)}
    assert ("single_print", 24050.0) in kinds
    assert ("poor_high", 24075.0) in kinds
    fill = session(date(2026, 11, 6), [(24045, 24080)])
    kinds = {
        (lv.kind, lv.price)
        for lv in carried_levels(session_profiles([*day0, *later, *fill], CAL, ROW5))
    }
    assert ("single_print", 24050.0) not in kinds
    assert ("poor_high", 24075.0) not in kinds
