"""Job worker: runs queued jobs until none are left, resuming any job a killed worker left running.

uv run python services/worker/main.py --db axiom.db --kinds package.module:KINDS
"""

import argparse
import importlib
import sqlite3
import sys
import time
from collections.abc import Mapping
from typing import cast

from axiom_core.db import migrate
from axiom_core.jobs import JobKind, JobService


def load_kinds(spec: str) -> dict[str, JobKind]:
    module, _, attr = spec.partition(":")
    found: object = getattr(importlib.import_module(module), attr)
    if not isinstance(found, Mapping):
        raise SystemExit(f"{spec} is not a mapping of job kinds")
    kinds: dict[str, JobKind] = {}
    for name, kind in cast(Mapping[object, object], found).items():
        if not isinstance(name, str) or not isinstance(kind, JobKind):
            raise SystemExit(f"{spec}: {name!r} is not a job kind")
        kinds[name] = kind
    return kinds


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--kinds", required=True, help="module:attribute holding the job kinds")
    args = parser.parse_args(argv)
    conn = sqlite3.connect(args.db)
    migrate(conn)
    jobs = JobService(conn, time.time, load_kinds(args.kinds))
    while jobs.run_next() is not None:
        pass
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
