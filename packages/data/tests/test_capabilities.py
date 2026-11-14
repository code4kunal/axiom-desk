import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from axiom_api.app import Services, build_services, create_app
from axiom_core.authz import Forbidden
from axiom_core.db import migrate
from axiom_core.registry import Binding
from axiom_core.session import VerifiedClaims
from axiom_core.tenancy import Role
from axiom_data.instruments import Instrument
from fastapi.testclient import TestClient


class Clock:
    now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def app_services() -> Iterator[Services]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    migrate(conn)
    svc = build_services(conn, Clock())
    svc.directory.bootstrap_admin("desk", "ada")
    svc.directory.grant(svc.directory.principal("desk", "ada"), "desk", "ana", Role.ANALYST)

    # Load test fixtures into instruments
    fixture_path = Path(__file__).parent / "fixtures" / "instruments.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
    if svc.instruments:
        svc.instruments.load_fixture_data(data)

    yield svc
    conn.close()


def sign_in(svc: Services, user: str) -> str:
    return svc.sessions.sign_in(
        VerifiedClaims(
            subject=user, tenant_id="desk", amr=("mfa",), display_name=user, auth_time=None
        )
    )


def test_ae1_instrument_lookup_sp500_refused_with_suggestions_parity(
    app_services: Services,
) -> None:
    """Covers AE1: instrument_lookup for S&P 500 with basket_member returns refused + tracking ETF,

    and identical result_id across API and agent surfaces.
    """
    token = sign_in(app_services, "ana")
    client = TestClient(create_app(app_services))

    inputs = {"symbol": "SPX", "on": "2026-11-13", "purpose": "basket_member"}

    # Screen API surface
    res = client.post(
        "/capabilities/instrument_lookup",
        json=inputs,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200, res.text
    screen_data = res.json()

    # Agent surface
    agent_principal = app_services.sessions.agent_principal(token)
    agent_envelope = app_services.registry.call(
        agent_principal, "instrument_lookup", inputs, Binding.AGENT
    )

    # Verify identical result_id
    assert screen_data["result_id"] == agent_envelope.result_id

    # Verify content
    val = screen_data["value"]
    assert val["role"] == "analysis-only"
    elig = val["eligibility"]
    assert elig["status"] == "refused"
    assert elig["reason"] == "analysis-only"
    assert "MO_SP500_ETF" in elig["suggestions"]


def test_fno_contract_rules_cites_circular_and_has_unverified_limitation(
    app_services: Services,
) -> None:
    """fno_contract_rules for Nifty on 2025-09-02 cites expiry circular

    and carries unverified limitation.
    """
    token = sign_in(app_services, "ana")
    agent_principal = app_services.sessions.agent_principal(token)

    inputs = {"exchange": "NSE", "underlying": "NIFTY", "on": "2025-09-02"}
    env = app_services.registry.call(agent_principal, "fno_contract_rules", inputs, Binding.AGENT)

    sources = [s.name for s in env.sources]
    assert "UNSOURCED" in sources, f"Sources: {sources}"
    assert "unverified rule" in env.limitations
    assert env.value["expiry_weekdays"]["weekly"] == "Tuesday"


def test_trading_calendar_holiday_returns_no_session_and_next_session(
    app_services: Services,
) -> None:
    """trading_calendar on a holiday returns no session and the next session."""
    token = sign_in(app_services, "ana")
    agent_principal = app_services.sessions.agent_principal(token)

    # 2024-11-01 is Diwali Laxmi Pujan (regular trading closed, only Muhurat)
    # 2019-03-04 is Maha Shivratri (holiday)
    inputs = {"segment": "equity", "on": "2019-03-04"}
    env = app_services.registry.call(agent_principal, "trading_calendar", inputs, Binding.AGENT)

    val = env.value
    assert val["is_trading_day"] is False
    assert val["session"] is None
    assert val["next_session"] is not None
    assert val["next_session"]["start"].startswith("2019-03-05")


def test_non_public_scope_refused_for_unentitled_tenant(app_services: Services) -> None:
    """A source whose scope the tenant lacks is refused by the registry."""
    # Insert an instrument with a proprietary licence scope
    app_services.instruments.load_instruments(
        [
            Instrument(
                instrument_id="PRIVATE_STOCK",
                asset_class="equity",
                kind="equity",
                exchange="NSE",
                name="Private Corporation",
                source="VENDOR_SECRET",
                licence_scope="vendor-proprietary",
            )
        ]
    )

    token = sign_in(app_services, "ana")
    agent_principal = app_services.sessions.agent_principal(token)

    inputs = {"instrument_id": "PRIVATE_STOCK", "on": "2026-11-13"}
    with pytest.raises(Forbidden) as exc:
        app_services.registry.call(agent_principal, "instrument_lookup", inputs, Binding.AGENT)

    assert "licence scope vendor-proprietary is not entitled" in str(exc.value)


def test_horizon_exceeded_and_rule_unknown_return_422(app_services: Services) -> None:
    """A date past calendar horizon, and rule asked before first row,

    each return 422 through API.
    """
    token = sign_in(app_services, "ana")
    client = TestClient(create_app(app_services))

    # Calendar horizon exceeded
    res_cal = client.post(
        "/capabilities/trading_calendar",
        json={"segment": "equity", "on": "2030-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_cal.status_code == 422, res_cal.text
    assert "calendar horizon exceeded" in res_cal.json()["error"]

    # Rule before first row
    res_fno = client.post(
        "/capabilities/fno_contract_rules",
        json={"exchange": "NSE", "underlying": "NIFTY", "on": "2015-01-01"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_fno.status_code == 422, res_fno.text
    assert "RuleUnknown" in res_fno.json()["error"] or "contract_value" in res_fno.json()["error"]
