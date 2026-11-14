from pathlib import Path

from axiom_api.codegen import ROOT, app_registry
from axiom_core.registry import Registry

MANIFEST = ROOT / "specs" / "charts" / "capabilities.txt"


def manifest_names(path: Path) -> list[str]:
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def manifest_problems(registry: Registry, path: Path) -> list[str]:
    registered = {c.name for c in registry.capabilities()}
    checked = registry.check()
    problems: list[str] = []
    for name in manifest_names(path):
        if name not in registered:
            problems.append(f"{name}: in the chart manifest but not registered")
        problems += [p for p in checked if p.startswith(f"{name}:")]
    return problems


def test_every_chart_capability_in_the_manifest_is_registered_with_its_bindings() -> None:
    assert MANIFEST.is_file()
    assert manifest_problems(app_registry(), MANIFEST) == []


def test_a_manifest_name_without_a_registration_fails(tmp_path: Path) -> None:
    manifest = tmp_path / "capabilities.txt"
    manifest.write_text("# header\nruns_latest\n\nchart_strike_ladder\n")
    assert manifest_names(manifest) == ["runs_latest", "chart_strike_ladder"]
    assert manifest_problems(app_registry(), manifest) == [
        "chart_strike_ladder: in the chart manifest but not registered"
    ]
