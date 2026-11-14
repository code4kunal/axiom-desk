import csv
import json
import math
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

import pytest
from axiom_chartmath.bars import IST, Bar, SessionCalendar, adjust_splits
from axiom_chartmath.indicators import REGISTRY, chart_defaults, compute, stream

GOLDEN = Path(__file__).parents[3] / "specs" / "quant" / "golden" / "indicators"
Series = dict[str, list[float | None]]


def load(name: str) -> dict[str, Any]:
    return json.loads((GOLDEN / f"{name}.json").read_text())


def seeded_bars() -> list[Bar]:
    with (GOLDEN / "bars.csv").open() as f:
        return [
            Bar(
                datetime.combine(date.fromisoformat(r["date"]), time(9, 15), IST),
                float(r["open"]),
                float(r["high"]),
                float(r["low"]),
                float(r["close"]),
                float(r["volume"]),
            )
            for r in csv.DictReader(f)
        ]


def golden_bars(g: dict[str, Any]) -> list[Bar]:
    if g["bars"] == "bars.csv":
        return seeded_bars()
    return [
        Bar(
            datetime.fromisoformat(b["ts"]),
            b["open"],
            b["high"],
            b["low"],
            b["close"],
            b["volume"],
            oi=b.get("oi"),
            delivery_qty=b.get("delivery_qty"),
        )
        for b in g["bars"]
    ]


def golden_calendar(g: dict[str, Any]) -> SessionCalendar:
    return SessionCalendar(frozenset(date.fromisoformat(d) for d in g.get("holidays", [])))


def run(name: str, g: dict[str, Any]) -> Series:
    return compute(name, golden_bars(g), calendar=golden_calendar(g), **g["params"])


def mismatches(got: Series, want: Series, rel: float = 1e-9, abs_: float = 1e-9) -> list[str]:
    assert set(got) == set(want), f"outputs {sorted(got)} != golden {sorted(want)}"
    out: list[str] = []
    for key, expected in want.items():
        assert len(got[key]) == len(expected)
        for i, (a, b) in enumerate(zip(got[key], expected, strict=True)):
            same = (a is None and b is None) or (
                a is not None and b is not None and math.isclose(a, b, rel_tol=rel, abs_tol=abs_)
            )
            if not same:
                out.append(f"{key}[{i}]: got {a}, golden {b}")
    return out


@pytest.mark.golden
@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_every_indicator_matches_its_golden(name: str) -> None:
    g = load(name)
    assert g["version"] == REGISTRY[name].version, "a formula change needs a new version and golden"
    bad = mismatches(run(name, g), g["outputs"], g["tolerance"]["rel"], g["tolerance"]["abs"])
    assert not bad, bad[:5]


FIXED_WARMUP = sorted(n for n, spec in REGISTRY.items() if spec.warmup is not None)


@pytest.mark.golden
@pytest.mark.parametrize("name", FIXED_WARMUP)
def test_no_value_before_declared_warmup(name: str) -> None:
    spec = REGISTRY[name]
    assert spec.warmup is not None
    g = load(name)
    declared = spec.warmup({**spec.defaults, **g["params"]})
    for key, values in run(name, g).items():
        w = declared if isinstance(declared, int) else declared[key]
        assert all(v is None for v in values[:w]), f"{key} emitted before warm-up {w}"
        assert values[w] is not None, f"{key} not emitted at warm-up {w}"
        # the declared warm-up is also where the reference starts
        assert next(i for i, v in enumerate(g["outputs"][key]) if v is not None) == w


def cutler_rsi(closes: list[float], n: int) -> list[float | None]:
    out: list[float | None] = [None] * len(closes)
    for i in range(n, len(closes)):
        diffs = [closes[j] - closes[j - 1] for j in range(i - n + 1, i + 1)]
        gain = sum(d for d in diffs if d > 0) / n
        loss = sum(-d for d in diffs if d < 0) / n
        out[i] = 100 * gain / (gain + loss)
    return out


@pytest.mark.golden
def test_rsi_uses_wilder_smoothing_and_the_sma_variant_fails() -> None:
    g = load("rsi")
    closes = [b.close for b in seeded_bars()]
    assert mismatches({"rsi": cutler_rsi(closes, 14)}, g["outputs"])
    assert not mismatches(run("rsi", g), g["outputs"])


@pytest.mark.parametrize("name", sorted(REGISTRY))
def test_incremental_update_equals_full_recompute(name: str) -> None:
    g = load(name)
    bars = golden_bars(g)
    cal = golden_calendar(g)
    live = stream(name, calendar=cal, **g["params"])
    for k, bar in enumerate(bars, start=1):
        step = live.send(bar)
        full = compute(name, bars[:k], calendar=cal, **g["params"])
        assert step == {key: values[-1] for key, values in full.items()}, f"bar {k}"


SESSION = load("session_vwap")


def test_session_vwap_resets_at_0915_and_skips_the_holiday() -> None:
    bars = golden_bars(SESSION)
    out = run("session_vwap", SESSION)["vwap"]
    ts = [b.ts for b in bars]
    pre_open = ts.index(datetime(2026, 10, 29, 9, 0, tzinfo=IST))
    holiday = ts.index(datetime(2026, 11, 3, 9, 15, tzinfo=IST))
    assert out[pre_open] is None
    assert out[pre_open + 1] == 105  # (108 + 102 + 105) / 3, nothing carried from 28 Oct
    assert out[holiday] is None
    assert out[holiday + 1] == 101  # (104 + 98 + 101) / 3
    # without the fixture holiday the 3 Nov bar becomes a session of its own
    no_holiday = compute("session_vwap", bars, calendar=SessionCalendar())["vwap"]
    assert no_holiday[holiday] == 195


def test_cpr_after_the_holiday_uses_the_last_trading_session() -> None:
    g = load("cpr")
    bars = golden_bars(g)
    out = run("cpr", g)
    after = [b.ts for b in bars].index(datetime(2026, 11, 4, 9, 15, tzinfo=IST))
    # 2 Nov: H 103, L 93, C 100 -> pivot 296/3, bc 98, tc 2*pivot - bc
    assert out["pivot"][after] == pytest.approx(296 / 3)
    assert out["bottom"][after] == pytest.approx(98)
    assert out["top"][after] == pytest.approx(2 * 296 / 3 - 98)
    no_holiday = compute("cpr", bars, calendar=SessionCalendar())
    assert no_holiday["pivot"][after] == pytest.approx(195)  # (200 + 190 + 195) / 3


def test_a_one_to_two_split_leaves_the_adjusted_sma_continuous() -> None:
    days = [d for i in range(30) if (d := date(2026, 9, 1 + i)).weekday() < 5]
    ex = days[10]
    bars = [
        Bar(datetime.combine(d, time(9, 15), IST), p, p, p, p, 1000)
        for d in days
        for p in [100.0 if d < ex else 50.0]
    ]
    raw = compute("sma", bars, period=5)["sma"]
    assert raw[12] == 70  # (100*2 + 50*3) / 5: unadjusted, the split reads as a fall
    adjusted = adjust_splits(bars, [(ex, 2.0)])
    assert compute("sma", adjusted, period=5)["sma"][4:] == [50.0] * (len(days) - 4)
    assert adjusted[0].volume == 2000


def test_session_indicators_need_a_calendar() -> None:
    with pytest.raises(ValueError, match="calendar"):
        compute("session_vwap", golden_bars(SESSION))


def test_new_charts_open_with_defaults_by_interval() -> None:
    assert chart_defaults(intraday=True) == ([("volume", {}), ("session_vwap", {})], True)
    assert chart_defaults(intraday=False) == (
        [("volume", {}), ("sma", {"period": 50}), ("sma", {"period": 200})],
        False,
    )
    for intraday in (True, False):
        studies, _ = chart_defaults(intraday)
        for name, params in studies:
            assert set(params) <= set(REGISTRY[name].defaults)
