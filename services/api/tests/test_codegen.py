from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import pytest
from axiom_api import codegen
from axiom_core.authz import Action
from axiom_core.envelope import HandlerResult
from axiom_core.registry import ALL_BINDINGS, CallContext, Capability
from pydantic import BaseModel


class Leg(BaseModel):
    strike: float
    side: Literal["buy", "sell"]
    lots: int = 1


class StrategyInput(BaseModel):
    legs: list[Leg]


class Criteria(BaseModel):
    field: str | None = None
    all_of: list["Criteria"] = []


class ScreenInput(BaseModel):
    root: Criteria


class StrategyOutput(BaseModel):
    net_premium: float
    legs: list[Leg]


def handler(ctx: CallContext, inputs: BaseModel) -> HandlerResult:
    return HandlerResult(value={}, as_of=datetime(2026, 11, 14, tzinfo=UTC), sources=(), method="")


def cap(name: str, inputs: type[BaseModel], output: type[BaseModel] | None = None) -> Capability:
    return Capability(
        name=name,
        summary=name,
        inputs=inputs,
        handler=handler,
        permission=Action.READ,
        bindings=ALL_BINDINGS,
        version="1",
        parity_inputs={},
        output=output,
    )


def generated(*caps: Capability) -> str:
    registry = codegen.app_registry()
    for c in caps:
        registry.register(c)
    return codegen.render(registry)[codegen.OUT / "src" / "generated.ts"]


def test_list_of_models_emits_a_named_type() -> None:
    ts = generated(cap("chart_strategy", StrategyInput))
    assert "export interface ChartStrategyInput {\n  legs: Array<Leg>;\n}" in ts
    assert (
        'export interface Leg {\n  strike: number;\n  side: "buy" | "sell";\n  lots?: number;\n}'
        in ts
    )


def test_recursive_model_emits_a_self_referencing_type() -> None:
    ts = generated(cap("screen_build", ScreenInput))
    assert "export interface ScreenBuildInput {\n  root: Criteria;\n}" in ts
    assert (
        "export interface Criteria {\n  field?: string | null;\n  all_of?: Array<Criteria>;\n}"
        in ts
    )


def test_output_model_types_the_envelope_value() -> None:
    ts = generated(cap("chart_strategy", StrategyInput, StrategyOutput))
    assert (
        "export interface ChartStrategyOutput {\n  net_premium: number;\n  legs: Array<Leg>;\n}"
        in ts
    )
    assert "  chart_strategy: ChartStrategyOutput;" in ts
    assert "  runs_latest: unknown;" in ts
    assert ts.count("export interface Leg {") == 1


def test_two_different_models_with_one_name_are_refused() -> None:
    class Leg(BaseModel):
        note: str

    class Other(BaseModel):
        legs: list[Leg]

    with pytest.raises(ValueError, match="Leg"):
        generated(cap("chart_strategy", StrategyInput), cap("other", Other))


def test_check_fails_when_the_generated_file_drifts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(codegen, "ROOT", tmp_path)
    monkeypatch.setattr(codegen, "OUT", tmp_path)
    assert codegen.main([]) == 0
    assert codegen.main(["--check"]) == 0
    target = tmp_path / "src" / "generated.ts"
    target.write_text(target.read_text() + "// hand edit\n")
    assert codegen.main(["--check"]) == 1
    assert "generated.ts: stale, rerun codegen" in capsys.readouterr().err
