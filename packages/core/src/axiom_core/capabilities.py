from pydantic import BaseModel

from axiom_core.authz import Action, NotFound
from axiom_core.envelope import HandlerResult
from axiom_core.registry import ALL_BINDINGS, CallContext, Capability
from axiom_core.runs import RunStore


class LatestRunInput(BaseModel):
    kind: str


def latest_run(runs: RunStore) -> Capability:
    def handler(ctx: CallContext, inputs: LatestRunInput) -> HandlerResult:
        run = runs.latest(inputs.kind)
        if run is None:
            raise NotFound("run", inputs.kind)
        return HandlerResult(
            value={"run_id": run.id, "kind": run.kind, "payload": run.payload},
            as_of=run.as_of,
            sources=run.sources,
            method="latest published run",
        )

    return Capability(
        name="runs_latest",
        summary="Latest published run of a kind (for example the current regime)",
        inputs=LatestRunInput,
        handler=handler,
        permission=Action.READ,
        bindings=ALL_BINDINGS,
        version="1",
        parity_inputs={"kind": "regime"},
    )
