"""Long-running jobs that behave the same whether a screen or the agent starts them.

A job is a kind plus params, split into steps (folds or date blocks). The worker commits each
step's result as it finishes, so a killed worker resumes from the last finished step.
"""

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

from axiom_core.authz import Action, Forbidden, NotFound
from axiom_core.db import Connection
from axiom_core.envelope import HandlerResult, JsonValue, Source, canonical, digest
from axiom_core.principals import Principal, PrincipalKind
from axiom_core.registry import ALL_BINDINGS, CallContext, Capability, Entitlements

Params = Mapping[str, JsonValue]
SOURCE = Source("axiom-jobs", Entitlements.PUBLIC)


class JobState(StrEnum):
    QUEUED = "queued"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    CANCELLED = "cancelled"
    DONE = "done"
    FAILED = "failed"


ACTIVE = (JobState.QUEUED, JobState.RUNNING, JobState.AWAITING_APPROVAL)


@dataclass(frozen=True)
class JobKind:
    name: str
    steps: Callable[[Params], int]
    run_step: Callable[[Params, int], JsonValue]
    cost: Callable[[Params], float]


@dataclass(frozen=True)
class JobStatus:
    id: str
    kind: str
    state: str
    done: int
    total: int


@dataclass(frozen=True)
class _JobRow:
    user_id: str
    kind: str
    state: str
    total: int


class QuotaExceeded(Forbidden):
    pass


class JobService:
    def __init__(
        self,
        conn: Connection,
        clock: Callable[[], float],
        kinds: Mapping[str, JobKind],
        *,
        quota: int = 4,
        approval_cost: float = 100.0,
        max_attempts: int = 3,
    ) -> None:
        self._conn = conn
        self.clock = clock
        self._kinds = kinds
        self._quota = quota
        self._approval_cost = approval_cost
        self._max_attempts = max_attempts

    def submit(self, principal: Principal, kind: str, params: Params, *, request_id: str) -> str:
        """Queue a job. The same request_id from the same user returns the existing job."""
        job_kind = self._kinds.get(kind)
        if job_kind is None:
            raise NotFound("job kind", kind)
        job_id = "job_" + digest(principal.tenant_id, principal.user_id, request_id)[:24]
        if self._find(principal, job_id) is not None:
            return job_id
        needs_approval = (
            principal.kind is PrincipalKind.AGENT and job_kind.cost(params) > self._approval_cost
        )
        # The quota check and the duplicate check live in the insert itself, so a concurrent
        # submit cannot slip between check and write.
        with self._conn:
            inserted = self._conn.execute(
                "INSERT INTO jobs (id, tenant_id, user_id, submitted_by, kind, params, state, "
                "total, created_at) SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? "
                "WHERE (SELECT COUNT(*) FROM jobs WHERE tenant_id = ? AND user_id = ? "
                f"AND state IN ({','.join('?' * len(ACTIVE))})) < ? "
                "ON CONFLICT(id) DO NOTHING",
                (
                    job_id,
                    principal.tenant_id,
                    principal.user_id,
                    principal.kind.value,
                    kind,
                    canonical(dict(params)),
                    JobState.AWAITING_APPROVAL if needs_approval else JobState.QUEUED,
                    job_kind.steps(params),
                    self.clock(),
                    principal.tenant_id,
                    principal.user_id,
                    *ACTIVE,
                    self._quota,
                ),
            ).rowcount
        if inserted or self._find(principal, job_id) is not None:
            return job_id
        raise QuotaExceeded(f"job quota reached: {self._quota} active jobs")

    def approve(self, principal: Principal, job_id: str) -> None:
        """Only the human the job runs for can release an agent job held for cost."""
        row = self._get(principal, job_id, any_user=True)
        if principal.kind is not PrincipalKind.USER or principal.user_id != row.user_id:
            raise Forbidden("only the job's own user can approve it")
        with self._conn:
            self._conn.execute(
                "UPDATE jobs SET state = 'queued' WHERE id = ? AND state = 'awaiting_approval'",
                (job_id,),
            )

    def cancel(self, principal: Principal, job_id: str) -> None:
        self._get(principal, job_id)
        with self._conn:
            self._conn.execute("UPDATE jobs SET cancel_requested = 1 WHERE id = ?", (job_id,))
            self._conn.execute(
                "UPDATE jobs SET state = 'cancelled' "
                "WHERE id = ? AND state IN ('queued', 'awaiting_approval')",
                (job_id,),
            )

    def status(self, principal: Principal, job_id: str) -> JobStatus:
        row = self._get(principal, job_id)
        return JobStatus(job_id, row.kind, row.state, self._done_count(job_id), row.total)

    def partials(self, principal: Principal, job_id: str) -> list[JsonValue]:
        self._get(principal, job_id)
        return self._steps(job_id)

    def result(self, principal: Principal, job_id: str) -> list[JsonValue]:
        state = self._get(principal, job_id).state
        if state != JobState.DONE:
            raise ValueError(f"job {job_id} is {state}, no result")
        return self._steps(job_id)

    def run_next(self) -> str | None:
        # shortcut: one worker per records DB, so an orphaned 'running' job is simply resumed;
        # add a lease with expiry before running more than one worker.
        row = self._conn.execute(
            "SELECT id, kind, params, total, attempts FROM jobs "
            "WHERE state IN ('running', 'queued') "
            "ORDER BY state = 'running' DESC, created_at, id LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        job_id, kind, raw_params, total, attempts = row
        job_kind = self._kinds.get(kind)
        # A step that raises, or kills the process, every time would otherwise be resumed
        # forever and block every job queued behind it.
        if job_kind is None or attempts >= self._max_attempts:
            with self._conn:
                self._conn.execute("UPDATE jobs SET state = 'failed' WHERE id = ?", (job_id,))
            return job_id
        params: Params = json.loads(raw_params)
        with self._conn:
            self._conn.execute(
                "UPDATE jobs SET state = 'running', attempts = attempts + 1 WHERE id = ?",
                (job_id,),
            )
        for step in range(self._done_count(job_id), total):
            if self._cancel_requested(job_id):
                break
            value = job_kind.run_step(params, step)
            with self._conn:
                self._conn.execute(
                    "INSERT INTO job_steps VALUES (?, ?, ?)", (job_id, step, canonical(value))
                )
                # attempts counts runs in a row without progress, not lifetime resumes
                self._conn.execute("UPDATE jobs SET attempts = 0 WHERE id = ?", (job_id,))
        end = JobState.CANCELLED if self._cancel_requested(job_id) else JobState.DONE
        with self._conn:
            self._conn.execute("UPDATE jobs SET state = ? WHERE id = ?", (end, job_id))
        return job_id

    def _cancel_requested(self, job_id: str) -> bool:
        (flag,) = self._conn.execute(
            "SELECT cancel_requested FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        return bool(flag)

    def _done_count(self, job_id: str) -> int:
        (count,) = self._conn.execute(
            "SELECT COUNT(*) FROM job_steps WHERE job_id = ?", (job_id,)
        ).fetchone()
        return count

    def _steps(self, job_id: str) -> list[JsonValue]:
        rows = self._conn.execute(
            "SELECT result FROM job_steps WHERE job_id = ? ORDER BY step", (job_id,)
        )
        return [json.loads(r[0]) for r in rows]

    def _find(self, principal: Principal, job_id: str, *, any_user: bool = False) -> _JobRow | None:
        row = self._conn.execute(
            "SELECT tenant_id, user_id, kind, state, total FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        # Another tenant's job, or another user's, reads as missing. A user's agent carries
        # that user's id, so it sees the user's jobs.
        if row is None or row[0] != principal.tenant_id:
            return None
        if not any_user and row[1] != principal.user_id:
            return None
        return _JobRow(row[1], row[2], row[3], row[4])

    def _get(self, principal: Principal, job_id: str, *, any_user: bool = False) -> _JobRow:
        row = self._find(principal, job_id, any_user=any_user)
        if row is None:
            raise NotFound("job", job_id)
        return row


class SubmitInput(BaseModel):
    kind: str
    params: dict[str, Any]
    request_id: str


class JobInput(BaseModel):
    job_id: str


def job_capabilities(jobs: JobService) -> list[Capability]:
    def wrap(value: JsonValue, method: str) -> HandlerResult:
        as_of = datetime.fromtimestamp(jobs.clock(), UTC)
        return HandlerResult(value=value, as_of=as_of, sources=(SOURCE,), method=method)

    def status_value(s: JobStatus) -> JsonValue:
        return {"job_id": s.id, "kind": s.kind, "state": s.state, "done": s.done, "total": s.total}

    def submit(ctx: CallContext, i: SubmitInput) -> HandlerResult:
        job_id = jobs.submit(ctx.principal, i.kind, i.params, request_id=i.request_id)
        return wrap(status_value(jobs.status(ctx.principal, job_id)), "job submitted")

    def status(ctx: CallContext, i: JobInput) -> HandlerResult:
        return wrap(status_value(jobs.status(ctx.principal, i.job_id)), "job status")

    def partial(ctx: CallContext, i: JobInput) -> HandlerResult:
        return wrap(jobs.partials(ctx.principal, i.job_id), "finished steps so far")

    def cancel(ctx: CallContext, i: JobInput) -> HandlerResult:
        jobs.cancel(ctx.principal, i.job_id)
        return wrap(status_value(jobs.status(ctx.principal, i.job_id)), "job cancel requested")

    def result(ctx: CallContext, i: JobInput) -> HandlerResult:
        return wrap(jobs.result(ctx.principal, i.job_id), "job result")

    job_ref: dict[str, JsonValue] = {"job_id": "job_parity"}
    submit_ref: dict[str, JsonValue] = {"kind": "folds", "params": {}, "request_id": "parity"}
    specs: list[tuple[str, str, type[BaseModel], Callable[..., HandlerResult], Params]] = [
        ("jobs_submit", "Start a long-running job", SubmitInput, submit, submit_ref),
        ("jobs_status", "State and progress of a job", JobInput, status, job_ref),
        ("jobs_partial", "Results of the steps a job has finished", JobInput, partial, job_ref),
        ("jobs_cancel", "Stop a job, keeping finished steps", JobInput, cancel, job_ref),
        ("jobs_result", "Full result of a finished job", JobInput, result, job_ref),
    ]
    return [
        Capability(
            name=name,
            summary=summary,
            inputs=inputs,
            handler=handler,
            permission=Action.READ,
            bindings=ALL_BINDINGS,
            version="1",
            parity_inputs=fixture,
        )
        for name, summary, inputs, handler, fixture in specs
    ]
