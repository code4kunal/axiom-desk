"""Generate the TypeScript types, agent tool list and command index from the registry.

uv run python -m axiom_api.codegen          write the generated files
uv run python -m axiom_api.codegen --check  fail on registry problems or stale generated files
"""

import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from axiom_core.db import migrate
from axiom_core.registry import Registry

from axiom_api.app import build_services

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "packages" / "registry-ts"

ENVELOPE_TS = """\
export interface Source {
  name: string;
  licence_scope: string;
}

export interface Envelope<T = unknown> {
  result_id: string;
  capability: string;
  version: string;
  inputs_hash: string;
  value: T;
  as_of: string;
  method: string;
  sources: Source[];
  limitations: string[];
  evidence_ref: string | null;
  calibration_status: string | null;
}
"""


def ts_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return schema["$ref"].rsplit("/", 1)[-1]
    if "enum" in schema:
        return " | ".join(json.dumps(v) for v in schema["enum"])
    if "anyOf" in schema:
        return " | ".join(ts_type(s) for s in schema["anyOf"])
    kind = schema.get("type")
    if kind == "array":
        return f"Array<{ts_type(schema.get('items', {}))}>"
    if kind == "object" and "properties" in schema:
        return (
            "{ " + " ".join(f"{p}: {ts_type(s)};" for p, s in schema["properties"].items()) + " }"
        )
    scalar = {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}
    return scalar.get(str(kind), "null" if kind == "null" else "unknown")


def ts_declaration(name: str, schema: dict[str, Any]) -> str:
    if "properties" not in schema and schema.get("type") != "object":
        return f"export type {name} = {ts_type(schema)};\n"
    required = set(schema.get("required", []))
    fields = [
        f"  {p}{'' if p in required else '?'}: {ts_type(s)};"
        for p, s in schema.get("properties", {}).items()
    ]
    return f"export interface {name} {{\n" + "\n".join(fields) + "\n}\n"


def pascal(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def render(registry: Registry) -> dict[Path, str]:
    defs: dict[str, dict[str, Any]] = {}

    def top_level(schema: dict[str, Any]) -> dict[str, Any]:
        for name, body in schema.get("$defs", {}).items():
            if defs.setdefault(name, body) != body:
                raise ValueError(f"two different models are both named {name}; rename one")
        # A recursive root model comes back as a $ref to its own definition.
        return defs[ts_type(schema)] if "$ref" in schema else schema

    cap_blocks: list[str] = []
    names: list[str] = []
    outputs: list[str] = []
    for cap in registry.capabilities():
        cap_blocks.append(f"/** {cap.summary} */")
        inputs = top_level(cap.inputs.model_json_schema())
        cap_blocks.append(ts_declaration(f"{pascal(cap.name)}Input", inputs))
        output = "unknown"
        if cap.output is not None:
            output = f"{pascal(cap.name)}Output"
            schema = top_level(cap.output.model_json_schema(mode="serialization"))
            cap_blocks.append(ts_declaration(output, schema))
        names.append(cap.name)
        outputs.append(output)
    blocks = [
        "// Generated from the capability registry by `uv run python -m axiom_api.codegen`.",
        "// Do not edit by hand.",
        "",
        ENVELOPE_TS,
        *(ts_declaration(name, defs[name]) for name in sorted(defs)),
        *cap_blocks,
    ]
    blocks.append(
        "export interface CapabilityInputs {\n"
        + "\n".join(f"  {n}: {pascal(n)}Input;" for n in names)
        + "\n}\n"
    )
    blocks.append(
        "export interface CapabilityOutputs {\n"
        + "\n".join(f"  {n}: {o};" for n, o in zip(names, outputs, strict=True))
        + "\n}\n"
    )
    blocks.append("export type CapabilityName = keyof CapabilityInputs;\n")
    blocks.append(f"export const capabilityNames: CapabilityName[] = {json.dumps(names)};\n")
    return {
        OUT / "src" / "generated.ts": "\n".join(blocks),
        OUT / "generated" / "agent-tools.json": json.dumps(registry.tool_list(), indent=2) + "\n",
        OUT / "generated" / "command-index.json": json.dumps(registry.command_index(), indent=2)
        + "\n",
    }


def drift(registry: Registry) -> list[str]:
    return [
        str(path.relative_to(ROOT))
        for path, text in render(registry).items()
        if not path.exists() or path.read_text() != text
    ]


def app_registry() -> Registry:
    conn = sqlite3.connect(":memory:")
    migrate(conn)
    return build_services(conn, time.time).registry


def main(argv: list[str]) -> int:
    registry = app_registry()
    if "--check" in argv:
        problems = registry.check() + [f"{p}: stale, rerun codegen" for p in drift(registry)]
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1 if problems else 0
    for path, text in render(registry).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
