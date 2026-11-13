import itertools
import os
import signal
import sqlite3
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest
from axiom_core.audit import AuditLog
from axiom_core.authz import Authorizer, Forbidden, NotFound
from axiom_core.db import migrate
from axiom_core.envelope import JsonValue
from axiom_core.jobs import JobKind, JobService, QuotaExceeded, job_capabilities
from axiom_core.principals import Principal, PrincipalKind
from axiom_core.registry import Binding, Entitlements, Registry
from axiom_core.tenancy import Directory

ROOT = Path(__file__).resolve().parents[3]


def fold_score(params: Mapping[str, JsonValue], i: int) -> JsonValue:
    return {"fold": i, "score": i * 10}


def folds_kind(on_step: Callable[[int], None] | None = None) -> JobKind:
    def run_step(params: Mapping[str, JsonValue], i: int) -> JsonValue:
        if on_step is not None:
            on_step(i)
        return fold_score(params, i)

    return JobKind(
        name="folds",
        steps=lambda p: int(str(p["folds"])),
        run_step=run_step,
        cost=lambda p: float(str(p.get("cost", 1))),
    )


def make_service(conn: sqlite3.Connection, clock: Callable[[], float], kind: JobKind) -> JobService:
    return JobService(conn, clock, {kind.name: kind}, quota=2, approval_cost=100.0)


def user(directory: Directory, name: str = "ana") -> Principal:
    return directory.principal("desk", name)


def agent_for(name: str = "ana") -> Principal:
    return Principal(PrincipalKind.AGENT, "desk", name)


def test_three_fold_job_reports_each_partial_before_completion(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    seen: list[tuple[str, list[JsonValue]]] = []
    ana = user(directory)

    def observe(i: int) -> None:
        seen.append((jobs.status(ana, job_id).state, jobs.partials(ana, job_id)))

    jobs = make_service(conn, clock, folds_kind(observe))
    job_id = jobs.submit(ana, "folds", {"folds": 3}, request_id="r1")
    assert jobs.run_next() == job_id

    assert seen == [
        ("running", []),
        ("running", [fold_score({}, 0)]),
        ("running", [fold_score({}, 0), fold_score({}, 1)]),
    ]
    status = jobs.status(ana, job_id)
    assert (status.state, status.done, status.total) == ("done", 3, 3)
    assert jobs.result(ana, job_id) == [fold_score({}, i) for i in range(3)]


def test_cancelled_job_stops_and_keeps_completed_partials(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    ana = user(directory)

    def cancel_during_second_fold(i: int) -> None:
        if i == 1:
            jobs.cancel(ana, job_id)

    jobs = make_service(conn, clock, folds_kind(cancel_during_second_fold))
    job_id = jobs.submit(ana, "folds", {"folds": 3}, request_id="r1")
    jobs.run_next()

    assert jobs.status(ana, job_id).state == "cancelled"
    assert jobs.partials(ana, job_id) == [fold_score({}, 0), fold_score({}, 1)]
    with pytest.raises(ValueError, match="cancelled"):
        jobs.result(ana, job_id)


def test_cancelling_a_queued_job_means_it_never_runs(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    ana = user(directory)
    job_id = jobs.submit(ana, "folds", {"folds": 2}, request_id="r1")
    jobs.cancel(ana, job_id)
    assert jobs.status(ana, job_id).state == "cancelled"
    assert jobs.run_next() is None
    assert jobs.partials(ana, job_id) == []


class WorkerDied(Exception):
    pass


def test_orphaned_running_job_resumes_before_older_queued_work(
    conn: sqlite3.Connection, directory: Directory
) -> None:
    ticks = itertools.count()

    def clock() -> float:
        # each submit gets a later created_at, so age order is unambiguous
        return float(next(ticks))

    crash = [True]

    def die_once_on_second_fold(i: int) -> None:
        if i == 1 and crash:
            crash.pop()
            raise WorkerDied

    jobs = make_service(conn, clock, folds_kind(die_once_on_second_fold))
    ana = user(directory)
    older = jobs.submit(agent_for(), "folds", {"folds": 1, "cost": 500}, request_id="older")
    orphan = jobs.submit(ana, "folds", {"folds": 2}, request_id="orphan")
    with pytest.raises(WorkerDied):
        jobs.run_next()
    assert jobs.status(ana, orphan).state == "running"

    jobs.approve(ana, older)
    assert jobs.run_next() == orphan
    assert jobs.result(ana, orphan) == [fold_score({}, 0), fold_score({}, 1)]
    assert jobs.run_next() == older


def test_expensive_agent_job_waits_for_its_user_to_approve(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    cheap = jobs.submit(agent_for(), "folds", {"folds": 1, "cost": 5}, request_id="cheap")
    costly = jobs.submit(agent_for(), "folds", {"folds": 1, "cost": 500}, request_id="costly")
    ana = user(directory)

    assert jobs.status(ana, cheap).state == "queued"
    assert jobs.status(ana, costly).state == "awaiting_approval"
    assert jobs.run_next() == cheap
    assert jobs.run_next() is None

    with pytest.raises(Forbidden):
        jobs.approve(agent_for(), costly)
    with pytest.raises(Forbidden):
        jobs.approve(user(directory, "pam"), costly)
    jobs.approve(ana, costly)
    assert jobs.run_next() == costly
    assert jobs.status(ana, costly).state == "done"


def test_user_costly_job_needs_no_approval(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    job_id = jobs.submit(user(directory), "folds", {"folds": 1, "cost": 500}, request_id="r")
    assert jobs.status(user(directory), job_id).state == "queued"


def test_resubmitting_the_same_request_returns_the_same_job(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    ana = user(directory)
    first = jobs.submit(ana, "folds", {"folds": 1}, request_id="r1")
    assert jobs.submit(agent_for(), "folds", {"folds": 1}, request_id="r1") == first
    assert jobs.submit(ana, "folds", {"folds": 1}, request_id="r2") != first


def test_other_tenant_cannot_see_a_job(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    job_id = jobs.submit(user(directory), "folds", {"folds": 1}, request_id="r1")
    outsider = directory.principal("broker-b", "bob-admin")
    with pytest.raises(NotFound):
        jobs.status(outsider, job_id)
    with pytest.raises(NotFound):
        jobs.cancel(outsider, job_id)


def test_another_user_and_their_agent_cannot_see_or_cancel_a_job(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    ana = user(directory)
    job_id = jobs.submit(ana, "folds", {"folds": 1}, request_id="r1")
    for other in (user(directory, "pam"), agent_for("pam")):
        for read in (jobs.status, jobs.partials, jobs.result, jobs.cancel):
            with pytest.raises(NotFound):
                read(other, job_id)
    assert jobs.status(agent_for(), job_id).state == "queued"
    assert jobs.run_next() == job_id
    assert jobs.result(ana, job_id) == [fold_score({}, 0)]


def test_a_job_that_always_fails_is_given_up_and_the_queue_moves_on(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    def broken(i: int) -> None:
        raise WorkerDied

    poison = JobKind("poison", lambda p: 1, lambda p, i: broken(i), lambda p: 1.0)
    ok = folds_kind()
    jobs = JobService(conn, clock, {"poison": poison, "folds": ok}, max_attempts=3)
    ana = user(directory)
    bad = jobs.submit(ana, "poison", {}, request_id="bad")
    good = jobs.submit(ana, "folds", {"folds": 1}, request_id="good")

    for _ in range(3):
        with pytest.raises(WorkerDied):
            jobs.run_next()
    assert jobs.run_next() == bad
    assert jobs.status(ana, bad).state == "failed"
    assert jobs.run_next() == good
    assert jobs.status(ana, good).state == "done"


def test_a_job_whose_kind_the_worker_lacks_fails_instead_of_crashing(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    ana = user(directory)
    submitted = make_service(conn, clock, folds_kind())
    orphan = submitted.submit(ana, "folds", {"folds": 1}, request_id="r1")
    worker = JobService(conn, clock, {})
    assert worker.run_next() == orphan
    assert submitted.status(ana, orphan).state == "failed"
    assert worker.run_next() is None


def test_unknown_kind_is_refused(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    jobs = make_service(conn, clock, folds_kind())
    with pytest.raises(NotFound):
        jobs.submit(user(directory), "nope", {}, request_id="r1")


@pytest.fixture
def registry(
    conn: sqlite3.Connection, clock: Callable[[], float], audit: AuditLog, authz: Authorizer
) -> Registry:
    reg = Registry(authz, Entitlements(conn), audit)
    for cap in job_capabilities(make_service(conn, clock, folds_kind())):
        reg.register(cap)
    return reg


def test_job_capabilities_pass_the_registry_check(registry: Registry) -> None:
    assert registry.check() == []
    assert {c.name for c in registry.capabilities()} == {
        "jobs_submit",
        "jobs_status",
        "jobs_partial",
        "jobs_cancel",
        "jobs_result",
    }


@pytest.mark.parity
def test_submit_answers_the_same_on_every_surface(registry: Registry, directory: Directory) -> None:
    inputs: dict[str, JsonValue] = {"kind": "folds", "params": {"folds": 2}, "request_id": "p"}
    ids = {registry.call(user(directory), "jobs_submit", inputs, s).result_id for s in Binding}
    assert len(ids) == 1


def test_quota_refusal_reads_the_same_from_screen_and_agent(
    registry: Registry, directory: Directory
) -> None:
    ana = user(directory)
    for n in range(2):
        registry.call(
            ana,
            "jobs_submit",
            {"kind": "folds", "params": {"folds": 1}, "request_id": f"q{n}"},
            Binding.SCREEN,
        )
    messages: list[str] = []
    for principal, surface in ((ana, Binding.SCREEN), (agent_for(), Binding.AGENT)):
        with pytest.raises(QuotaExceeded) as err:
            registry.call(
                principal,
                "jobs_submit",
                {"kind": "folds", "params": {"folds": 1}, "request_id": "over"},
                surface,
            )
        messages.append(str(err.value))
    assert messages[0] == messages[1]
    assert "quota" in messages[0]


KINDS_MODULE = """
import os
import time
from pathlib import Path

from axiom_core.jobs import JobKind


def run_step(params, i):
    log = Path(params["log"])
    with log.open("a") as f:
        f.write(f"{i}\\n")
    if i == 1:
        gate = Path(params["gate"])
        while not gate.exists():
            time.sleep(0.02)
    return {"fold": i}


KINDS = {"folds": JobKind("folds", lambda p: 3, run_step, lambda p: 1.0)}
"""


def wait_for(predicate: Callable[[], bool], timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("timed out waiting")
        time.sleep(0.05)


def test_killed_worker_resumes_from_the_last_checkpoint(tmp_path: Path) -> None:
    (tmp_path / "test_kinds.py").write_text(textwrap.dedent(KINDS_MODULE))
    db = tmp_path / "records.db"
    log, gate = tmp_path / "steps.log", tmp_path / "gate"
    conn = sqlite3.connect(db)
    migrate(conn)
    audit = AuditLog(conn, time.time)
    directory = Directory(conn, audit)
    directory.bootstrap_admin("desk", "ada")
    ada = directory.principal("desk", "ada")
    params: dict[str, JsonValue] = {"log": str(log), "gate": str(gate)}
    stand_in = JobKind("folds", lambda p: 3, fold_score, lambda p: 1.0)
    jobs = JobService(conn, time.time, {"folds": stand_in})
    job_id = jobs.submit(ada, "folds", params, request_id="kill")

    env = {**os.environ, "PYTHONPATH": str(tmp_path)}
    cmd = [
        sys.executable,
        str(ROOT / "services" / "worker" / "main.py"),
        "--db",
        str(db),
        "--kinds",
        "test_kinds:KINDS",
    ]
    worker = subprocess.Popen(cmd, env=env)
    try:
        wait_for(lambda: log.exists() and log.read_text().splitlines() == ["0", "1"])
        assert jobs.partials(ada, job_id) == [{"fold": 0}]
        worker.send_signal(signal.SIGKILL)
        worker.wait(timeout=10)
    finally:
        if worker.poll() is None:
            worker.kill()

    gate.touch()
    done = subprocess.run(cmd, env=env, timeout=60, check=False)
    assert done.returncode == 0

    # fold 0 was checkpointed before the kill and never recomputed; fold 1 restarted
    assert log.read_text().splitlines() == ["0", "1", "1", "2"]
    assert jobs.status(ada, job_id).state == "done"
    assert jobs.result(ada, job_id) == [{"fold": 0}, {"fold": 1}, {"fold": 2}]
    conn.close()


def racing_kind(rival: Callable[[], object]) -> JobKind:
    """steps() runs after submit's existence and quota checks and before its insert, so the
    rival submit lands in exactly the window a concurrent request would."""
    racing = [True]

    def steps(params: Mapping[str, JsonValue]) -> int:
        if params.get("race") and racing:
            racing.pop()
            rival()
        return 1

    return JobKind(name="folds", steps=steps, run_step=fold_score, cost=lambda p: 1.0)


def test_racing_duplicate_submit_returns_the_same_job(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    ana = user(directory)
    params: dict[str, JsonValue] = {"race": True}
    jobs = make_service(
        conn, clock, racing_kind(lambda: jobs.submit(ana, "folds", params, request_id="r1"))
    )
    first = jobs.submit(ana, "folds", params, request_id="r1")
    assert first == jobs.submit(ana, "folds", params, request_id="r1")
    assert conn.execute("SELECT COUNT(*) FROM jobs").fetchone() == (1,)


def test_racing_submits_cannot_exceed_the_quota(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    ana = user(directory)
    jobs = make_service(
        conn, clock, racing_kind(lambda: jobs.submit(ana, "folds", {}, request_id="rival"))
    )
    jobs.submit(ana, "folds", {}, request_id="first")
    with pytest.raises(QuotaExceeded):
        jobs.submit(ana, "folds", {"race": True}, request_id="racer")
    (active,) = conn.execute("SELECT COUNT(*) FROM jobs WHERE state = 'queued'").fetchone()
    assert active == 2


class WorkerKilled(BaseException):
    pass


def test_attempts_reset_when_a_resumed_job_makes_progress(
    conn: sqlite3.Connection, clock: Callable[[], float], directory: Directory
) -> None:
    calls = itertools.count(1)

    def killed_on_even_calls(i: int) -> None:
        if next(calls) in (2, 4, 6):
            raise WorkerKilled

    jobs = make_service(conn, clock, folds_kind(killed_on_even_calls))
    ana = user(directory)
    job_id = jobs.submit(ana, "folds", {"folds": 10}, request_id="r1")
    for _ in range(3):
        with pytest.raises(WorkerKilled):
            jobs.run_next()
    assert jobs.run_next() == job_id
    status = jobs.status(ana, job_id)
    assert (status.state, status.done, status.total) == ("done", 10, 10)
