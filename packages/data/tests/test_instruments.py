import csv
import json
import sqlite3
from datetime import date
from pathlib import Path

import pytest
from axiom_core.db import migrate
from axiom_data.instruments import (
    Instrument,
    InstrumentStore,
)


@pytest.fixture
def store(conn: sqlite3.Connection) -> InstrumentStore:
    fixture_path = Path(__file__).parent / "fixtures" / "instruments.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
    s = InstrumentStore(conn)
    s.load_fixture_data(data)
    return s


def test_ae1_sp500_refused_as_basket_member_with_tracking_etf(store: InstrumentStore) -> None:
    """Covers AE1: S&P 500 refused as basket member with reason analysis-only, ETF suggested."""
    spx = store.get_instrument("SPX_INDEX")
    assert spx is not None

    eligibility = store.check_eligibility(spx, purpose="basket_member", on=date(2026, 11, 13))
    assert eligibility.status == "refused"
    assert eligibility.reason == "analysis-only"
    assert "MO_SP500_ETF" in eligibility.suggestions


def test_sp500_refused_as_order_draft_leg(store: InstrumentStore) -> None:
    """S&P 500 index is refused as an order-draft leg."""
    spx = store.get_instrument("SPX_INDEX")
    assert spx is not None

    eligibility = store.check_eligibility(spx, purpose="order_draft_leg", on=date(2026, 11, 13))
    assert eligibility.status == "refused"
    assert eligibility.reason == "analysis-only"


def test_nse_equity_allowed(store: InstrumentStore) -> None:
    """An NSE equity is allowed as a basket member and an order-draft leg."""
    rel = store.get_instrument("RELIANCE_EQ")
    assert rel is not None

    e1 = store.check_eligibility(rel, purpose="basket_member", on=date(2026, 11, 13))
    assert e1.status == "allowed"

    e2 = store.check_eligibility(rel, purpose="order_draft_leg", on=date(2026, 11, 13))
    assert e2.status == "allowed"


def test_gsec_conditional_on_broker(store: InstrumentStore) -> None:
    """A G-Sec is conditional, naming broker execution as the condition."""
    gsec = store.get_instrument("GSEC_10Y_2034")
    assert gsec is not None

    e1 = store.check_eligibility(gsec, purpose="basket_member", on=date(2026, 11, 13))
    assert e1.status == "conditional"
    assert e1.condition == "broker execution"

    e2 = store.check_eligibility(gsec, purpose="order_draft_leg", on=date(2026, 11, 13))
    assert e2.status == "conditional"
    assert e2.condition == "broker execution"


def test_corporate_bond_tracking_vs_order(store: InstrumentStore) -> None:
    """Corporate bond allowed as basket tracking member and refused as order-draft leg."""
    bond = store.get_instrument("HDFC_CORP_BOND")
    assert bond is not None

    e_track = store.check_eligibility(bond, purpose="basket_tracking_member", on=date(2026, 11, 13))
    assert e_track.status == "allowed"

    e_order = store.check_eligibility(bond, purpose="order_draft_leg", on=date(2026, 11, 13))
    assert e_order.status == "refused"
    assert e_order.reason == "tracking only"

    e_basket = store.check_eligibility(bond, purpose="basket_member", on=date(2026, 11, 13))
    assert e_basket.status == "refused"


def test_international_fof_inflows_override(store: InstrumentStore) -> None:
    """International FoF allowed before closed-to-inflows override date and refused from it."""
    fof = store.get_instrument("FRANKLIN_US_FOF")
    assert fof is not None

    # Override starts on 2024-03-15
    e_before = store.check_eligibility(fof, purpose="basket_member", on=date(2024, 3, 14))
    assert e_before.status == "allowed"

    e_on = store.check_eligibility(fof, purpose="basket_member", on=date(2024, 3, 15))
    assert e_on.status == "refused"
    assert e_on.reason == "closed to inflows"


def test_tracking_ended_not_suggested(store: InstrumentStore) -> None:
    """A tracking ETF whose tracking row ended before D is not suggested on D."""
    spx = store.get_instrument("SPX_INDEX")
    assert spx is not None

    # In fixtures, OLD_SP500_ETF tracking row ended on 2023-01-01
    # On 2022-06-01: OLD_SP500_ETF is active
    sug_2022 = store.get_tracking_investables(spx.instrument_id, on=date(2022, 6, 1))
    assert "OLD_SP500_ETF" in sug_2022

    # On 2024-06-01: OLD_SP500_ETF has ended, not suggested
    sug_2024 = store.get_tracking_investables(spx.instrument_id, on=date(2024, 6, 1))
    assert "OLD_SP500_ETF" not in sug_2024
    assert "MO_SP500_ETF" in sug_2024


def test_symbol_renamed_point_in_time(store: InstrumentStore) -> None:
    """Symbol renamed on date X resolves to same instrument id before/after X; old unresolvable."""
    # RENAMED_STOCK had OLDTICKER until 2024-05-01, then NEWTICKER from 2024-05-01
    inst_before = store.resolve_identifier("symbol", "OLDTICKER", on=date(2024, 4, 30))
    assert inst_before is not None
    assert inst_before.instrument_id == "RENAMED_STOCK"

    inst_after = store.resolve_identifier("symbol", "NEWTICKER", on=date(2024, 5, 1))
    assert inst_after is not None
    assert inst_after.instrument_id == "RENAMED_STOCK"

    # Old ticker does not resolve on or after 2024-05-01
    assert store.resolve_identifier("symbol", "OLDTICKER", on=date(2024, 5, 1)) is None
    # New ticker does not resolve before 2024-05-01
    assert store.resolve_identifier("symbol", "NEWTICKER", on=date(2024, 4, 30)) is None


def test_every_asset_class_has_role(store: InstrumentStore) -> None:
    """Every asset class in asset_class_roles.csv has a role on 2026-11-13."""
    ref_dir = Path(__file__).parent.parent / "src" / "axiom_data" / "reference"
    csv_path = ref_dir / "asset_class_roles.csv"
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        asset_classes = [row["asset_class"].strip() for row in reader]

    test_date = date(2026, 11, 13)
    for ac in asset_classes:
        dummy = Instrument(
            instrument_id=f"DUMMY_{ac}",
            asset_class=ac,
            kind="dummy",
            exchange="NSE",
            name="Dummy",
            source="TEST",
            licence_scope="public",
        )
        role_res = store.get_role(dummy, on=test_date)
        assert role_res.role != ""
        assert role_res.role in (
            "basket-eligible",
            "broker-executable only",
            "tracking only",
            "investable while open to inflows",
            "analysis-only",
            "out of scope",
        )


def test_missing_licence_scope_refused_at_load(conn: sqlite3.Connection) -> None:
    """A row without licence_scope is refused at load."""
    store = InstrumentStore(conn)

    with pytest.raises(ValueError, match="licence_scope"):
        store.load_instruments(
            [
                {
                    "instrument_id": "BAD_INST",
                    "asset_class": "equity",
                    "kind": "equity",
                    "exchange": "NSE",
                    "name": "Bad",
                    "source": "S",
                    "licence_scope": "",
                }
            ]
        )

    with pytest.raises(ValueError, match="licence_scope"):
        store.load_identifiers(
            [
                {
                    "instrument_id": "INST_1",
                    "identifier_type": "symbol",
                    "value": "SYM",
                    "effective_from": "2024-01-01",
                    "published_at": "2024-01-01T00:00:00Z",
                    "recorded_at": "2024-01-01T00:00:00Z",
                    "source": "S",
                    "licence_scope": "",
                }
            ]
        )


def test_migration_on_fresh_and_existing_db() -> None:
    """Migration applies on a fresh DB and on a DB already migrated."""
    c = sqlite3.connect(":memory:")
    migrate(c)
    # verify tables exist
    query = (
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name IN ('instruments', 'instrument_identifiers')"
    )
    cursor = c.execute(query)
    tables = {r[0] for r in cursor.fetchall()}
    assert "instruments" in tables
    assert "instrument_identifiers" in tables

    # Running migrate again should be a no-op
    migrate(c)
    c.close()
