import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from axiom_api.app import Services, build_services, create_app
from axiom_core.db import migrate
from axiom_core.envelope import Source
from axiom_core.registry import Binding
from axiom_core.session import VerifiedClaims
from axiom_core.tenancy import Role
from fastapi.testclient import TestClient

AS_OF = datetime(2026, 11, 12, 9, 15, tzinfo=UTC)


class Clock:
    now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def services() -> Iterator[Services]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    migrate(conn)
    svc = build_services(conn, Clock())
    svc.directory.bootstrap_admin("desk", "ada")
    svc.directory.grant(svc.directory.principal("desk", "ada"), "desk", "ana", Role.ANALYST)
    yield svc
    conn.close()


def sign_in(svc: Services, user: str) -> str:
    return svc.sessions.sign_in(VerifiedClaims(subject=user, tenant_id="desk", amr=("mfa",)))


@pytest.mark.parity
def test_screen_and_agent_read_the_same_latest_published_run(services: Services) -> None:
    services.runs.publish("regime", AS_OF, {"state": "risk-on"}, (Source("nse-eod", "public"),))
    latest = services.runs.publish(
        "regime", AS_OF, {"state": "risk-off"}, (Source("nse-eod", "public"),)
    )
    token = sign_in(services, "ana")

    response = TestClient(create_app(services)).post(
        "/capabilities/runs_latest",
        json={"kind": "regime"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    screen = response.json()

    agent = services.registry.call(
        services.sessions.agent_principal(token), "runs_latest", {"kind": "regime"}, Binding.AGENT
    )
    assert screen["value"]["run_id"] == agent.value["run_id"] == latest.id
    assert screen["result_id"] == agent.result_id


@pytest.mark.parity
def test_every_registered_capability_answers_its_parity_fixture_on_every_surface(
    services: Services,
) -> None:
    services.runs.publish("regime", AS_OF, {"state": "risk-on"}, (Source("nse-eod", "public"),))
    principal = services.directory.principal("desk", "ana")
    for capability in services.registry.capabilities():
        assert capability.parity_inputs is not None, capability.name
        ids = {
            services.registry.call(
                principal, capability.name, capability.parity_inputs, s
            ).result_id
            for s in capability.bindings
        }
        assert len(ids) == 1, capability.name


def test_request_without_a_session_is_refused(services: Services) -> None:
    client = TestClient(create_app(services))
    assert client.post("/capabilities/runs_latest", json={"kind": "regime"}).status_code == 401
    bad = {"Authorization": "Bearer forged"}
    assert (
        client.post("/capabilities/runs_latest", json={"kind": "regime"}, headers=bad).status_code
        == 401
    )


def test_tenant_in_the_request_body_cannot_override_the_session(services: Services) -> None:
    token = sign_in(services, "ana")
    response = TestClient(create_app(services)).post(
        "/capabilities/runs_latest",
        json={"kind": "regime", "tenant_id": "broker-b"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_generated_artifacts_match_the_registry(services: Services) -> None:
    from axiom_api import codegen

    assert codegen.drift(services.registry) == []
