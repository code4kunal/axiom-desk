"""The result envelope every engine response carries."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

type JsonValue = Any  # any value json.dumps accepts


def canonical(value: JsonValue) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def digest(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()


@dataclass(frozen=True)
class Source:
    name: str
    licence_scope: str


@dataclass(frozen=True)
class HandlerResult:
    """What a capability handler returns. It cannot exist without sources and a zoned as_of."""

    value: JsonValue
    as_of: datetime
    sources: tuple[Source, ...]
    method: str
    limitations: tuple[str, ...] = ()
    evidence_ref: str | None = None
    calibration_status: str | None = None

    def __post_init__(self) -> None:
        if not self.sources:
            raise ValueError("a result must name its sources")
        if self.as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")


@dataclass(frozen=True)
class Envelope:
    result_id: str
    capability: str
    version: str
    inputs_hash: str
    value: JsonValue
    as_of: datetime
    method: str
    sources: tuple[Source, ...]
    limitations: tuple[str, ...] = field(default=())
    evidence_ref: str | None = None
    calibration_status: str | None = None

    @classmethod
    def wrap(cls, capability: str, version: str, inputs: JsonValue, r: HandlerResult) -> "Envelope":
        inputs_hash = digest(canonical(inputs))
        result_id = (
            "res_"
            + digest(capability, version, inputs_hash, r.as_of.isoformat(), canonical(r.value))[:32]
        )
        return cls(
            result_id=result_id,
            capability=capability,
            version=version,
            inputs_hash=inputs_hash,
            value=r.value,
            as_of=r.as_of,
            method=r.method,
            sources=r.sources,
            limitations=r.limitations,
            evidence_ref=r.evidence_ref,
            calibration_status=r.calibration_status,
        )

    def to_json(self) -> dict[str, JsonValue]:
        return {
            "result_id": self.result_id,
            "capability": self.capability,
            "version": self.version,
            "inputs_hash": self.inputs_hash,
            "value": self.value,
            "as_of": self.as_of.isoformat(),
            "method": self.method,
            "sources": [{"name": s.name, "licence_scope": s.licence_scope} for s in self.sources],
            "limitations": list(self.limitations),
            "evidence_ref": self.evidence_ref,
            "calibration_status": self.calibration_status,
        }
