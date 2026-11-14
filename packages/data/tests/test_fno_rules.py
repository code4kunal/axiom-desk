import csv
import json
import sqlite3
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from axiom_core.authz import Refused
from axiom_data.fno_rules import FnoRulesEngine, MalformedRule
from axiom_data.instruments import InstrumentStore
from axiom_data.pointintime import EffectiveDatedRow, RuleUnknown


@pytest.fixture
def fno(conn: sqlite3.Connection) -> FnoRulesEngine:
    fixtures_dir = Path(__file__).parent / "fixtures"
    with open(fixtures_dir / "contracts.json", encoding="utf-8") as f:
        c_data = json.load(f)
    with open(fixtures_dir / "ban_list.json", encoding="utf-8") as f:
        b_data = json.load(f)

    engine = FnoRulesEngine(conn)
    engine.load_fixtures(contracts_data=c_data, ban_data=b_data)
    return engine


def test_ae2_nifty_weekly_expiry_thursday_to_tuesday(fno: FnoRulesEngine) -> None:
    """Covers AE2: Nifty weekly for 2025-08-25 is 2025-08-28; for 2025-09-01 is 2025-09-02."""
    # Week of 2025-08-25 (before Sep 2025 move -> Thursday)
    exp_aug = fno.resolve_expiry(
        exchange="NSE",
        underlying="NIFTY",
        cycle="weekly",
        target_date=date(2025, 8, 25),
        as_of=date(2025, 8, 25),
    )
    assert exp_aug == date(2025, 8, 28)  # Thursday

    # Week of 2025-09-01 (from Sep 2025 move -> Tuesday)
    exp_sep = fno.resolve_expiry(
        exchange="NSE",
        underlying="NIFTY",
        cycle="weekly",
        target_date=date(2025, 9, 1),
        as_of=date(2025, 9, 1),
    )
    assert exp_sep == date(2025, 9, 2)  # Tuesday


def test_nifty_monthly_expiry_aug_and_sep_2025(fno: FnoRulesEngine) -> None:
    """Nifty monthly for Aug 2025 is 2025-08-28 and for Sep 2025 is 2025-09-30."""
    # Aug 2025 monthly -> last Thursday is 2025-08-28
    exp_aug = fno.resolve_expiry(
        exchange="NSE",
        underlying="NIFTY",
        cycle="monthly",
        target_date=date(2025, 8, 15),
        as_of=date(2025, 8, 15),
    )
    assert exp_aug == date(2025, 8, 28)

    # Sep 2025 monthly -> last Tuesday is 2025-09-30
    exp_sep = fno.resolve_expiry(
        exchange="NSE",
        underlying="NIFTY",
        cycle="monthly",
        target_date=date(2025, 9, 15),
        as_of=date(2025, 9, 15),
    )
    assert exp_sep == date(2025, 9, 30)


def test_expiry_on_exchange_holiday_moves_to_previous_regular_session(
    fno: FnoRulesEngine,
) -> None:
    """A rule-derived expiry on an exchange holiday moves to previous regular session."""
    # 2024-03-29 is Good Friday. Thursday 2024-03-28 is regular.
    exp_bse = fno.resolve_expiry(
        exchange="BSE",
        underlying="SENSEX",
        cycle="weekly",
        target_date=date(2024, 3, 25),
        as_of=date(2024, 3, 25),
    )
    assert exp_bse == date(2024, 3, 28)  # shifted from Friday 29 to Thursday 28


def test_muhurat_holiday_shifts_expiry_to_monday(fno: FnoRulesEngine) -> None:
    """Nifty weekly for week of 2025-10-20 resolves to Monday 2025-10-20 (Diwali Muhurat)."""
    exp = fno.resolve_expiry(
        exchange="NSE",
        underlying="NIFTY",
        cycle="weekly",
        target_date=date(2025, 10, 20),
        as_of=date(2025, 10, 20),
    )
    # Tuesday 2025-10-21 is a holiday (Muhurat session only, not regular session)
    # Previous regular session is Monday 2025-10-20
    assert exp == date(2025, 10, 20)


def test_banknifty_weekly_discontinuation_date(fno: FnoRulesEngine) -> None:
    """As of 2024-11-15, BankNifty weekly for 2024-11-25 is refused; for 2024-11-11 resolves."""
    # Week of 2024-11-11: candidate is Wednesday 2024-11-13 (before 2024-11-20 cut-off)
    exp_valid = fno.resolve_expiry(
        exchange="NSE",
        underlying="BANKNIFTY",
        cycle="weekly",
        target_date=date(2024, 11, 11),
        as_of=date(2024, 11, 11),
    )
    assert exp_valid == date(2024, 11, 13)

    # Week of 2024-11-25: candidate is Wednesday 2024-11-27 (on or after 2024-11-20 -> discontinued)
    with pytest.raises(Refused, match="weekly expiry not eligible"):
        fno.resolve_expiry(
            exchange="NSE",
            underlying="BANKNIFTY",
            cycle="weekly",
            target_date=date(2024, 11, 25),
            as_of=date(2024, 11, 15),
        )


def test_as_of_point_in_time_contract_records(fno: FnoRulesEngine) -> None:
    """As of 2025-07-15, Sep 2025 Nifty monthly ignores contracts published later."""
    # NIFTY_LATE_PUBLISHED_FUT was published on 2025-07-20
    # NIFTY_SEP_2025_FUT published on 2025-01-01 had expiry 2025-09-25
    exp_early = fno.get_contract_expiry("NIFTY_SEP_2025_FUT", on=date(2025, 7, 15))
    assert exp_early == date(2025, 9, 25)

    # Re-dating published on 2025-08-20 changed it to 2025-09-30
    exp_late = fno.get_contract_expiry("NIFTY_SEP_2025_FUT", on=date(2025, 8, 25))
    assert exp_late == date(2025, 9, 30)


def test_contract_lot_revision_point_in_time(fno: FnoRulesEngine) -> None:
    """Contract whose lot revised mid-life returns old lot before revision, new lot from it."""
    lot_before = fno.get_contract_lot("NIFTY_LOT_REVISED_FUT", on=date(2024, 11, 19))
    assert lot_before == 50

    lot_after = fno.get_contract_lot("NIFTY_LOT_REVISED_FUT", on=date(2024, 11, 20))
    assert lot_after == 25


def test_minimum_contract_value_change(fno: FnoRulesEngine) -> None:
    """Minimum contract value is old value on 2024-11-19 and ₹15 lakh on 2024-11-20."""
    rules_before = fno.get_contract_rules("NSE", "NIFTY", on=date(2024, 11, 19))
    assert rules_before.min_contract_value == 500000

    rules_after = fno.get_contract_rules("NSE", "NIFTY", on=date(2024, 11, 20))
    assert rules_after.min_contract_value == 1500000


def test_calendar_spread_benefit_change(fno: FnoRulesEngine) -> None:
    """Calendar-spread benefit on expiry day is available on 2025-01-31 and not on 2025-02-01."""
    rules_before = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 1, 31))
    assert rules_before.calendar_spread_benefit is True

    rules_after = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 2, 1))
    assert rules_after.calendar_spread_benefit is False


def test_ban_list_day_and_removal(fno: FnoRulesEngine) -> None:
    """Stock in ban list on D is banned on D and not on D+1 when D+1's list is loaded without it."""
    assert fno.is_banned("NSE", "RELIANCE_EQ", on=date(2024, 8, 1)) is True
    assert fno.is_banned("NSE", "RELIANCE_EQ", on=date(2024, 8, 2)) is False


def test_ban_status_date_without_coverage_raises_rule_unknown(fno: FnoRulesEngine) -> None:
    """Ban status on a date with no ban_list_days row raises RuleUnknown."""
    with pytest.raises(RuleUnknown) as exc:
        fno.is_banned("NSE", "RELIANCE_EQ", on=date(2024, 8, 3))
    assert exc.value.rule == "ban_list_days"


def test_ae3_rule_asked_before_first_row_raises_rule_unknown(fno: FnoRulesEngine) -> None:
    """Covers AE3: A rule asked for a date before its first row raises RuleUnknown."""
    with pytest.raises(RuleUnknown):
        fno.get_contract_rules("NSE", "NIFTY", on=date(2018, 6, 1))


def test_unverified_rule_limitation(fno: FnoRulesEngine) -> None:
    """An answer built on an unverified row carries R10 limitation and synthetic date limitation."""
    rules = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 9, 2))
    assert rules.is_verified is False
    assert "unverified rule" in rules.limitations
    assert "synthetic publication date" in rules.limitations


def test_weekly_synthetic_flag_survives_clean_monthly_row(fno: FnoRulesEngine) -> None:
    """A synthetic weekly row surfaces its flag even when the monthly row is clean."""
    ts = datetime(2025, 11, 1, tzinfo=UTC)
    clean_monthly = EffectiveDatedRow(
        key="NSE:BANKNIFTY:monthly",
        effective_from=date(2025, 9, 1),
        effective_to=None,
        published_at=ts,
        recorded_at=ts,
        source="TEST",
        verified_against="TEST",
        payload={"expiry_weekday": "Tuesday", "published_at_synthetic": "false"},
    )
    fno._expiry_rules_table.load([clean_monthly])  # pyright: ignore[reportPrivateUsage]
    # 2025-12-10: every other table resolves to a real circular, so only the weekly row is synthetic
    rules = fno.get_contract_rules("NSE", "BANKNIFTY", on=date(2025, 12, 10))
    assert "synthetic publication date" in rules.limitations


@pytest.mark.parametrize(
    ("table", "key", "column"),
    [
        ("_contract_value_table", "NSE:NIFTY", "min_contract_value"),
        ("_expiry_rules_table", "NSE:NIFTY:monthly", "expiry_weekday"),
    ],
)
def test_row_missing_a_needed_column_raises_malformed_rule(
    fno: FnoRulesEngine, table: str, key: str, column: str
) -> None:
    """A row without the column is refused by name, not given a made-up default."""
    ts = datetime(2026, 1, 1, tzinfo=UTC)
    row = EffectiveDatedRow(
        key=key,
        effective_from=date(2026, 1, 1),
        effective_to=None,
        published_at=ts,
        recorded_at=ts,
        source="TEST",
        verified_against="TEST",
        payload={},
    )
    getattr(fno, table).load([row])
    with pytest.raises(MalformedRule, match=column):
        fno.get_contract_rules("NSE", "NIFTY", on=date(2026, 6, 1))


def test_position_limit_index_rule_only_for_index_underlyings(fno: FnoRulesEngine) -> None:
    """A stock underlying must not be given the index position-limit rule."""
    nifty = fno.get_contract_rules("NSE", "NIFTY", on=date(2026, 1, 5))
    assert nifty.position_limit_rule == "1500cr_net"

    stock = fno.get_contract_rules("NSE", "RELIANCE", on=date(2026, 1, 5))
    assert stock.position_limit_rule == ""
    assert any("position limit" in lim for lim in stock.limitations)


def test_golden_rule_dates(fno: FnoRulesEngine) -> None:
    """Every row in golden_rule_dates.csv matches the lookup (KTD8)."""
    golden_path = Path(__file__).parent / "fixtures" / "golden_rule_dates.csv"
    with open(golden_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) >= 7

    for row in rows:
        rule_name = row["rule"].strip()
        key = row["key"].strip()
        on_date = date.fromisoformat(row["date"].strip())
        expected = row["expected"].strip()

        if expected == "not_stored":
            continue

        parts = key.split(":")
        exchange = parts[0]
        underlying = parts[1]

        rules = fno.get_contract_rules(exchange, underlying, on=on_date)
        if rule_name == "contract_value":
            assert str(rules.min_contract_value) == expected
        elif rule_name == "weekly_eligibility":
            assert str(rules.weekly_eligible).lower() == expected.lower()
        elif rule_name == "expiry_margin_rules":
            assert str(rules.calendar_spread_benefit).lower() == expected.lower()
        elif rule_name == "expiry_rules":
            cycle = "weekly"
            assert rules.expiry_weekdays[cycle].lower() == expected.lower()
        elif rule_name == "position_limits":
            assert rules.position_limit_rule == expected


def test_every_change_date_day_before_and_day_of(fno: FnoRulesEngine) -> None:
    """For every rule change date, day before returns old and day of returns new (KTD8)."""
    # 1. contract_value change on 2024-11-20
    r_cv_pre = fno.get_contract_rules("NSE", "NIFTY", on=date(2024, 11, 19))
    r_cv_post = fno.get_contract_rules("NSE", "NIFTY", on=date(2024, 11, 20))
    assert r_cv_pre.min_contract_value == 500000
    assert r_cv_post.min_contract_value == 1500000

    # 2. weekly_eligibility for BankNifty change on 2024-11-20
    r_bn_pre = fno.get_contract_rules("NSE", "BANKNIFTY", on=date(2024, 11, 19))
    r_bn_post = fno.get_contract_rules("NSE", "BANKNIFTY", on=date(2024, 11, 20))
    assert r_bn_pre.weekly_eligible is True
    assert r_bn_post.weekly_eligible is False

    # 3. expiry_margin_rules change on 2025-02-01
    r_em_pre = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 1, 31))
    r_em_post = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 2, 1))
    assert r_em_pre.calendar_spread_benefit is True
    assert r_em_post.calendar_spread_benefit is False

    # 4. expiry_rules change on 2025-09-01
    r_prev = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 8, 31)).expiry_weekdays["weekly"]
    r_curr = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 9, 1)).expiry_weekdays["weekly"]
    assert r_prev.lower() == "thursday"
    assert r_curr.lower() == "tuesday"

    # 5. position_limits change on 2025-12-06
    pl_prev = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 12, 5)).position_limit_rule
    pl_curr = fno.get_contract_rules("NSE", "NIFTY", on=date(2025, 12, 6)).position_limit_rule
    assert pl_prev == "500cr_or_15pct_oi"
    assert pl_curr == "1500cr_net"


def test_banned_stock_through_contract_rules_is_banned(
    fno: FnoRulesEngine, conn: sqlite3.Connection
) -> None:
    """The ban list is keyed by instrument id; the underlying symbol is mapped first."""
    path = Path(__file__).parent / "fixtures" / "instruments.json"
    InstrumentStore(conn).load_fixture_data(json.loads(path.read_text(encoding="utf-8")))
    assert fno.get_contract_rules("NSE", "RELIANCE", on=date(2024, 8, 1)).is_banned is True
    assert fno.get_contract_rules("NSE", "RELIANCE", on=date(2024, 8, 2)).is_banned is False


def test_unmapped_underlying_ban_status_is_unknown(fno: FnoRulesEngine) -> None:
    """No symbol-to-id mapping: never report False, say unknown and why."""
    rules = fno.get_contract_rules("NSE", "RELIANCE", on=date(2024, 8, 1))
    assert rules.is_banned is None
    assert any("ban status unknown" in lim for lim in rules.limitations)
