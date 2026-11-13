from datetime import UTC, datetime

import pytest
from axiom_core.envelope import HandlerResult, Source

AS_OF = datetime(2026, 11, 12, 9, 15, tzinfo=UTC)
PUBLIC = (Source("nse-eod", "public"),)


def test_result_without_sources_cannot_exist() -> None:
    with pytest.raises(ValueError, match="sources"):
        HandlerResult(value=1, as_of=AS_OF, sources=(), method="m")


def test_result_without_timezone_aware_as_of_cannot_exist() -> None:
    with pytest.raises(ValueError, match="as_of"):
        HandlerResult(value=1, as_of=datetime(2026, 11, 12, 9, 15), sources=PUBLIC, method="m")
