from axiom_chartmath.indicators.registry import Out, Stepper, register


@register(
    "delivery_pct",
    group="india",
    reference="Delivered quantity / traded volume * 100 (NSE daily delivery data).",
    warmup=lambda c: 0,
)
def delivery_pct() -> Stepper:
    out: Out = {}
    while True:
        bar = yield out
        dq = bar.delivery_qty
        out = {"delivery_pct": None if dq is None or not bar.volume else 100 * dq / bar.volume}


@register(
    "futures_oi",
    group="india",
    reference="Futures open interest and its change from the previous bar, drawn on price.",
    warmup=lambda c: {"oi": 0, "oi_change": 1},
)
def futures_oi() -> Stepper:
    prev: float | None = None
    out: Out = {}
    while True:
        bar = yield out
        oi = bar.oi
        out = {"oi": oi, "oi_change": None if oi is None or prev is None else oi - prev}
        prev = oi
