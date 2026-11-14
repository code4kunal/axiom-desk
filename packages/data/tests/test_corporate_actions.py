import json
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path
from typing import cast

import pytest
from axiom_data.corporate_actions import (
    Bar,
    CorporateAction,
    CorporateActionAdjuster,
    MalformedCorporateAction,
)
from axiom_data.pointintime import IST, NaiveTimestampRefused


def _bar(d: date, p: float, v: float = 100.0) -> Bar:
    return Bar(date=d, open=p, high=p, low=p, close=p, volume=v)


@pytest.fixture
def adjuster(conn: sqlite3.Connection) -> CorporateActionAdjuster:
    fixture_path = Path(__file__).parent / "fixtures" / "corporate_actions.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(data["corporate_actions"])
    return adj


def _sample_bars() -> list[Bar]:
    return [
        _bar(date(2024, 5, 13), 2000.0, 100.0),
        _bar(date(2024, 5, 14), 2000.0, 100.0),
        _bar(date(2024, 5, 15), 1000.0, 200.0),  # ex-date
        _bar(date(2024, 5, 16), 1020.0, 210.0),
    ]


def test_split_halves_prices_and_doubles_volume_before_ex_date(
    adjuster: CorporateActionAdjuster,
) -> None:
    """Split 1 to 2 halves prices and doubles volume before ex-date."""
    # Action SPLIT_1_TO_2 has ex_date 2024-05-15
    bars = _sample_bars()
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 5, 20))
    adj_bars = res.bars

    # Bars before ex-date (May 13, May 14) are halved in price, doubled in volume
    assert adj_bars[0].close == 1000.0
    assert adj_bars[0].volume == 200.0
    assert adj_bars[1].close == 1000.0
    assert adj_bars[1].volume == 200.0

    # Bars on or after ex-date (May 15, May 16) remain unchanged
    assert adj_bars[2].close == 1000.0
    assert adj_bars[2].volume == 200.0
    assert adj_bars[3].close == 1020.0
    assert adj_bars[3].volume == 210.0


def test_bonus_one_for_one_gives_same_factor_as_split(conn: sqlite3.Connection) -> None:
    """A bonus of 1 for every 1 held ((1, 2)) gives the same factor as a 1:2 split."""
    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(
        [
            {
                "action_id": "BONUS_TEST",
                "recorded_at": "2024-01-01T00:00:00Z",
                "instrument_id": "TEST_STOCK",
                "type": "bonus",
                "status": "active",
                "ex_date": "2024-05-15",
                "from_qty": 1,
                "to_qty": 2,
                "published_at": "2024-01-01T00:00:00Z",
                "source": "TEST",
                "licence_scope": "public",
            }
        ]
    )
    bars = _sample_bars()
    res = adj.adjust_bars("TEST_STOCK", bars, as_of=date(2024, 5, 20))
    assert res.bars[0].close == 1000.0
    assert res.bars[0].volume == 200.0


def test_two_splits_multiply(conn: sqlite3.Connection) -> None:
    """Two splits multiply: bars before both get both factors, bars between get one."""
    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(
        [
            {
                "action_id": "SPLIT_1",
                "recorded_at": "2023-01-01T00:00:00Z",
                "instrument_id": "MULTISPLIT",
                "type": "split",
                "status": "active",
                "ex_date": "2023-06-01",
                "from_qty": 1,
                "to_qty": 2,  # factor 1/2
                "published_at": "2023-01-01T00:00:00Z",
                "source": "TEST",
                "licence_scope": "public",
            },
            {
                "action_id": "SPLIT_2",
                "recorded_at": "2024-01-01T00:00:00Z",
                "instrument_id": "MULTISPLIT",
                "type": "split",
                "status": "active",
                "ex_date": "2024-06-01",
                "from_qty": 1,
                "to_qty": 2,  # factor 1/2
                "published_at": "2024-01-01T00:00:00Z",
                "source": "TEST",
                "licence_scope": "public",
            },
        ]
    )

    bars = [
        _bar(date(2023, 1, 1), 4000.0, 100.0),
        _bar(date(2023, 10, 1), 2000.0, 200.0),
        _bar(date(2024, 7, 1), 1000.0, 400.0),
    ]

    res = adj.adjust_bars("MULTISPLIT", bars, as_of=date(2024, 12, 1))
    adj_bars = res.bars

    # Bar before both splits: 4000 * 0.5 * 0.5 = 1000, volume 100 * 2 * 2 = 400
    assert adj_bars[0].close == 1000.0
    assert adj_bars[0].volume == 400.0

    # Bar between splits: 2000 * 0.5 = 1000, volume 200 * 2 = 400
    assert adj_bars[1].close == 1000.0
    assert adj_bars[1].volume == 400.0

    # Bar after both splits: unchanged
    assert adj_bars[2].close == 1000.0
    assert adj_bars[2].volume == 400.0


def test_action_not_applied_before_ex_date(adjuster: CorporateActionAdjuster) -> None:
    """As of a date before ex-date, the action is not applied."""
    bars = _sample_bars()
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 5, 14))

    # As of May 14 (before ex-date), prices must remain unadjusted
    assert res.bars[0].close == 2000.0
    assert res.bars[0].volume == 100.0


def test_late_announcement_not_applied_as_of_past_date(adjuster: CorporateActionAdjuster) -> None:
    """An action published after D is not applied as of D even though ex-date is before D."""
    bars = [
        _bar(date(2024, 4, 1), 2000.0, 100.0),
        _bar(date(2024, 4, 12), 1000.0, 200.0),
    ]

    # As of 2024-04-15: publication hasn't happened yet!
    res_early = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 4, 15))
    assert res_early.bars[0].close == 2000.0

    # As of 2024-04-25: published, so applied!
    res_late = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 4, 25))
    assert res_late.bars[0].close == 1000.0


def test_corrected_bonus_ratio_applies_once_at_corrected_ratio(
    adjuster: CorporateActionAdjuster,
) -> None:
    """Bonus ratio corrected in later version applies once, at corrected ratio."""
    bars = [
        _bar(date(2024, 2, 1), 3000.0, 100.0),
    ]

    # As of 2024-03-01: version 2 wins, factor is 1/2 (not 1/3, and not both multiplied!)
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 3, 1))
    assert res.bars[0].close == 1500.0  # 3000 * (1/2)


def test_cancelled_action_not_applied(adjuster: CorporateActionAdjuster) -> None:
    """An action cancelled before D is not applied as of D."""
    bars = [
        _bar(date(2024, 2, 15), 2000.0, 100.0),
    ]
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 3, 15))
    assert res.bars[0].close == 2000.0


def test_moved_ex_date_applies_at_corrected_date(adjuster: CorporateActionAdjuster) -> None:
    """An action whose ex-date moved applies only at corrected ex-date."""
    bars = [
        _bar(date(2024, 6, 8), 2000.0, 100.0),
        _bar(date(2024, 6, 15), 2000.0, 100.0),
        _bar(date(2024, 6, 22), 1000.0, 200.0),
    ]
    # As of 2024-06-25: corrected ex_date 2024-06-20 applies
    # bars on June 8 and June 15 (both < June 20) get halved
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 6, 25))
    assert res.bars[0].close == 1000.0
    assert res.bars[1].close == 1000.0
    assert res.bars[2].close == 1000.0


def test_cash_dividend_leaves_price_adjusted_bars_unchanged(
    adjuster: CorporateActionAdjuster,
) -> None:
    """A cash dividend leaves price-adjusted bars unchanged."""
    bars = [
        _bar(date(2024, 6, 28), 1000.0, 100.0),
        _bar(date(2024, 7, 2), 990.0, 100.0),
    ]
    # Default total_return=False
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 7, 10), total_return=False)
    assert res.bars[0].close == 1000.0


def test_total_return_mode_dividend_scaling(adjuster: CorporateActionAdjuster) -> None:
    """Total-return mode with ₹10 dividend and prior close ₹1,000 scales earlier bars by 0.99."""
    bars = [
        _bar(date(2024, 6, 28), 1000.0, 100.0),
        _bar(date(2024, 7, 2), 990.0, 100.0),
    ]
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 7, 10), total_return=True)
    # Earlier bar: 1000 * (1 - 10/1000) = 990.0
    assert pytest.approx(res.bars[0].close) == 990.0
    # Later bar unchanged
    assert res.bars[1].close == 990.0


def test_total_return_without_prior_bar_returns_limitation(conn: sqlite3.Connection) -> None:
    """Total-return mode with no bar before ex-date returns limitation instead of guessing close."""
    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(
        [
            {
                "action_id": "DIV_NO_PRIOR",
                "recorded_at": "2024-01-01T00:00:00Z",
                "instrument_id": "DIV_STOCK",
                "type": "dividend",
                "status": "active",
                "ex_date": "2024-07-01",
                "amount": "10.00",
                "published_at": "2024-01-01T00:00:00Z",
                "source": "TEST",
                "licence_scope": "public",
            }
        ]
    )
    bars = [
        _bar(date(2024, 7, 1), 990.0, 100.0),
    ]
    res = adj.adjust_bars("DIV_STOCK", bars, as_of=date(2024, 7, 10), total_return=True)
    assert any("skipped: no prior close bar available" in lim for lim in res.limitations)
    assert res.bars[0].close == 990.0


def test_demerger_leaves_bars_unchanged_and_returns_limitation(
    adjuster: CorporateActionAdjuster,
) -> None:
    """A demerger leaves bars unchanged and returns its limitation."""
    bars = [
        _bar(date(2024, 8, 25), 1000.0, 100.0),
        _bar(date(2024, 9, 5), 900.0, 100.0),
    ]
    res = adjuster.adjust_bars("RELIANCE_EQ", bars, as_of=date(2024, 9, 10))
    assert res.bars[0].close == 1000.0
    assert any("unhandled corporate action: demerger" in lim for lim in res.limitations)


def test_corporate_action_published_at_required_refuses_none() -> None:
    """published_at is required; None must be refused when building CorporateAction."""
    with pytest.raises((ValueError, TypeError)):
        CorporateAction(
            action_id="ACT1",
            recorded_at=datetime(2024, 1, 1, 0, 0, tzinfo=UTC),
            instrument_id="STOCK",
            type="split",
            status="active",
            ex_date=date(2024, 5, 15),
            published_at=cast(datetime, None),
            source="TEST",
        )


def test_corporate_action_utc_normalization_and_naive_refusal(conn: sqlite3.Connection) -> None:
    """CorporateAction normalizes recorded_at and published_at to UTC,

    rejects naive, and gives identical results.
    """
    # 1. Naive datetime refused
    with pytest.raises(NaiveTimestampRefused):
        CorporateAction(
            action_id="NAIVE",
            recorded_at=datetime(2024, 1, 1, 12, 0),  # naive
            instrument_id="STOCK",
            type="split",
            status="active",
            ex_date=date(2024, 5, 15),
            published_at=datetime(2024, 1, 1, 12, 0, tzinfo=UTC),
            source="TEST",
        )

    # 2. Same instant written in IST vs UTC gives identical normalized values and results
    dt_utc = datetime(2024, 5, 14, 20, 0, tzinfo=UTC)  # 20:00 UTC on May 14
    dt_ist = datetime(2024, 5, 15, 1, 30, tzinfo=IST)  # 01:30 IST on May 15 == 20:00 UTC on May 14

    act_utc = CorporateAction(
        action_id="ACT_UTC",
        recorded_at=dt_utc,
        instrument_id="STOCK_UTC",
        type="split",
        status="active",
        ex_date=date(2024, 5, 15),
        published_at=dt_utc,
        source="TEST",
        from_qty=1,
        to_qty=2,
    )
    act_ist = CorporateAction(
        action_id="ACT_IST",
        recorded_at=dt_ist,
        instrument_id="STOCK_IST",
        type="split",
        status="active",
        ex_date=date(2024, 5, 15),
        published_at=dt_ist,
        source="TEST",
        from_qty=1,
        to_qty=2,
    )
    assert act_ist.published_at.tzinfo == UTC
    assert act_ist.published_at == act_utc.published_at
    assert act_ist.recorded_at.tzinfo == UTC
    assert act_ist.recorded_at == act_utc.recorded_at

    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions([act_utc, act_ist])

    res_utc = adj.get_actions_as_of("STOCK_UTC", as_of=date(2024, 5, 15))
    res_ist = adj.get_actions_as_of("STOCK_IST", as_of=date(2024, 5, 15))
    assert len(res_utc) == len(res_ist) == 1
    assert res_utc[0].published_at == res_ist[0].published_at


def test_zero_or_negative_ratio_refused_at_load(conn: sqlite3.Connection) -> None:
    """A ratio with zero or negative quantity is refused at load."""
    adj = CorporateActionAdjuster(conn)
    with pytest.raises(ValueError, match="positive"):
        adj.load_corporate_actions(
            [
                {
                    "action_id": "BAD_SPLIT",
                    "recorded_at": "2024-01-01T00:00:00Z",
                    "instrument_id": "STOCK",
                    "type": "split",
                    "ex_date": "2024-05-15",
                    "from_qty": 0,
                    "to_qty": 2,
                    "published_at": "2024-01-01T00:00:00Z",
                    "source": "TEST",
                    "licence_scope": "public",
                }
            ]
        )


def test_split_and_bonus_require_from_and_to_qty() -> None:
    """from_qty and to_qty are required for split and bonus at construction."""
    with pytest.raises(ValueError, match="requires from_qty and to_qty"):
        CorporateAction(
            action_id="SPLIT_NO_QTY",
            recorded_at=datetime(2024, 1, 1, tzinfo=UTC),
            instrument_id="STOCK",
            type="split",
            status="active",
            ex_date=date(2024, 5, 15),
            published_at=datetime(2024, 1, 1, tzinfo=UTC),
            source="TEST",
            from_qty=None,
            to_qty=None,
        )


def test_dividend_at_or_above_prior_close_skipped(conn: sqlite3.Connection) -> None:
    """A dividend >= prior close must not flip prices negative; skip with limitation."""
    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(
        [
            {
                "action_id": "HUGE_DIV",
                "recorded_at": "2024-01-01T00:00:00Z",
                "instrument_id": "STOCK",
                "type": "dividend",
                "ex_date": "2024-05-15",
                "amount": "1200.00",
                "published_at": "2024-01-01T00:00:00Z",
                "source": "TEST",
            }
        ]
    )
    bars = [
        _bar(date(2024, 5, 14), 1000.0, 100.0),
        _bar(date(2024, 5, 15), 100.0, 100.0),
    ]
    res = adj.adjust_bars("STOCK", bars, as_of=date(2024, 5, 20), total_return=True)
    # Price must not flip negative
    assert res.bars[0].close == 1000.0
    assert any("skipped" in lim for lim in res.limitations)


@pytest.mark.parametrize("amount", ["-1.50", "0", "0.00", None])
def test_dividend_amount_must_be_positive(amount: str | None) -> None:
    """Negative, zero or missing dividend amount is refused at construction."""
    with pytest.raises(MalformedCorporateAction):
        CorporateAction(
            action_id="DIV",
            recorded_at=datetime(2024, 1, 1, tzinfo=UTC),
            instrument_id="STOCK",
            type="dividend",
            status="active",
            ex_date=date(2024, 5, 15),
            published_at=datetime(2024, 1, 1, tzinfo=UTC),
            source="TEST",
            amount=amount,
        )


def test_bad_dividend_amount_raises_refused(conn: sqlite3.Connection) -> None:
    """A bad amount string must raise a clear Refused subclass, not a bare ValueError."""
    from axiom_core.authz import Refused

    adj = CorporateActionAdjuster(conn)
    adj.load_corporate_actions(
        [
            {
                "action_id": "BAD_DIV",
                "recorded_at": "2024-01-01T00:00:00Z",
                "instrument_id": "STOCK",
                "type": "dividend",
                "ex_date": "2024-05-15",
                "amount": "not-a-number",
                "published_at": "2024-01-01T00:00:00Z",
                "source": "TEST",
            }
        ]
    )
    bars = [_bar(date(2024, 5, 14), 1000.0, 100.0)]
    with pytest.raises(Refused):
        adj.adjust_bars("STOCK", bars, as_of=date(2024, 5, 20), total_return=True)
