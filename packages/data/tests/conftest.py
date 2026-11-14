import sqlite3
from collections.abc import Iterator

import pytest
from axiom_core.db import migrate


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    c = sqlite3.connect(":memory:")
    migrate(c)
    yield c
    c.close()
