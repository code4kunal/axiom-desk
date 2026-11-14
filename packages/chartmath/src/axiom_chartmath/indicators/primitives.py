"""Float-stream building blocks. Each takes the next value (None while an upstream input is still
warming up, which passes through without touching state) and yields its output."""

import math
from collections import deque
from collections.abc import Generator

from axiom_chartmath.bars import Bar

Stream = Generator[float | None, float | None, None]
BarStream = Generator[float | None, Bar, None]


def primed[Y, S](g: Generator[Y, S, None]) -> Generator[Y, S, None]:
    next(g)
    return g


def is_zero(x: float) -> bool:
    # TA-Lib's TA_IS_ZERO tolerance, so degenerate bars resolve the same way as the reference
    return -1e-14 < x < 1e-14


def sma(n: int) -> Stream:
    win: deque[float] = deque(maxlen=n)
    out: float | None = None
    while True:
        x = yield out
        if x is None:
            out = None
            continue
        win.append(x)
        out = sum(win) / n if len(win) == n else None


def ema(n: int) -> Stream:
    """EMA with k = 2/(n+1), seeded with the SMA of the first n values (TA-Lib's default seed)."""
    k = 2 / (n + 1)
    seed: list[float] = []
    out: float | None = None
    while True:
        x = yield out
        if x is None:
            out = None
            continue
        if out is None and len(seed) < n:
            seed.append(x)
            out = sum(seed) / n if len(seed) == n else None
        elif out is not None:
            out = (x - out) * k + out


def wilder(n: int) -> Stream:
    """Wilder's smoothing (RMA): SMA of the first n values, then (prev*(n-1) + x)/n."""
    seed: list[float] = []
    out: float | None = None
    while True:
        x = yield out
        if x is None:
            out = None
            continue
        if out is None and len(seed) < n:
            seed.append(x)
            out = sum(seed) / n if len(seed) == n else None
        elif out is not None:
            out = (out * (n - 1) + x) / n


def wma(n: int) -> Stream:
    win: deque[float] = deque(maxlen=n)
    denom = n * (n + 1) / 2
    out: float | None = None
    while True:
        x = yield out
        if x is None:
            out = None
            continue
        win.append(x)
        out = sum((i + 1) * v for i, v in enumerate(win)) / denom if len(win) == n else None


def pstdev(n: int) -> Stream:
    """Population standard deviation over n values, as TA-Lib computes it: sqrt(E[x^2] - E[x]^2)."""
    win: deque[float] = deque(maxlen=n)
    out: float | None = None
    while True:
        x = yield out
        if x is None:
            out = None
            continue
        win.append(x)
        if len(win) < n:
            out = None
            continue
        mean = sum(win) / n
        var = sum(v * v for v in win) / n - mean * mean
        out = math.sqrt(var) if var >= 1e-14 else 0.0


def true_range() -> BarStream:
    """True range; undefined on the first bar, which has no previous close (TA-Lib convention)."""
    prev_close: float | None = None
    out: float | None = None
    while True:
        bar = yield out
        out = (
            None
            if prev_close is None
            else max(bar.high - bar.low, abs(bar.high - prev_close), abs(bar.low - prev_close))
        )
        prev_close = bar.close


def atr(n: int) -> BarStream:
    """Wilder ATR: first value is the mean of the first n true ranges, at bar n."""
    tr = primed(true_range())
    smooth = primed(wilder(n))
    out: float | None = None
    while True:
        bar = yield out
        out = smooth.send(tr.send(bar))


def stoch(
    k: int, k_smooth: int, d: int
) -> Generator[tuple[float, float] | None, tuple[float, float, float] | None, None]:
    """Slow stochastic over (high, low, close): %K smoothed by SMA, %D = SMA of %K. Both emit
    together once %D is defined, matching TA-Lib's aligned STOCH outputs."""
    highs: deque[float] = deque(maxlen=k)
    lows: deque[float] = deque(maxlen=k)
    slow_k = primed(sma(k_smooth))
    slow_d = primed(sma(d))
    out: tuple[float, float] | None = None
    while True:
        hlc = yield out
        if hlc is None:
            out = None
            continue
        high, low, close = hlc
        highs.append(high)
        lows.append(low)
        fast: float | None = None
        if len(highs) == k:
            hh, ll = max(highs), min(lows)
            fast = (close - ll) / ((hh - ll) / 100) if hh != ll else 0.0
        sk = slow_k.send(fast)
        sd = slow_d.send(sk)
        out = None if sk is None or sd is None else (sk, sd)


def midprice(n: int) -> BarStream:
    highs: deque[float] = deque(maxlen=n)
    lows: deque[float] = deque(maxlen=n)
    out: float | None = None
    while True:
        bar = yield out
        highs.append(bar.high)
        lows.append(bar.low)
        out = (max(highs) + min(lows)) / 2 if len(highs) == n else None


def diff(a: float | None, b: float | None, scale: float = 1.0) -> float | None:
    """a - scale*b, or None while either side is warming up."""
    return None if a is None or b is None else a - scale * b
