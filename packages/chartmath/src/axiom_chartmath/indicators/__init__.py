"""Built-in indicators. Importing this package registers every indicator in REGISTRY."""

from axiom_chartmath.indicators import india, levels, momentum, trend, volatility, volume
from axiom_chartmath.indicators.registry import (
    REGISTRY,
    Indicator,
    chart_defaults,
    compute,
    stream,
)

__all__ = [
    "REGISTRY",
    "Indicator",
    "chart_defaults",
    "compute",
    "india",
    "levels",
    "momentum",
    "stream",
    "trend",
    "volatility",
    "volume",
]
