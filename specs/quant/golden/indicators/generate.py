# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["ta-lib==0.8.3", "numpy==2.5.4"]
# ///
"""Regenerate the TA-Lib golden files for the built-in indicators.

Run from the repo root, outside the project environment (TA-Lib is not a project dependency):

    uv run --no-project specs/quant/golden/indicators/generate.py

Writes bars.csv (the fixed seeded series) and one <indicator>.json per TA-Lib-covered
indicator. Hand-computed goldens (session and India indicators, supertrend) are written by
hand and are not touched here. Every expected value below comes from TA-Lib functions, or
plain arithmetic over TA-Lib outputs where TA-Lib has no single function.
"""

import csv
import json
import math
from pathlib import Path

import numpy as np
import talib

HERE = Path(__file__).parent
SEED = 20261114
N = 500
SOURCE = f"TA-Lib {talib.__ta_version__.decode().split()[0]} via ta-lib-python {talib.__version__}"


def make_bars() -> dict[str, np.ndarray]:
    rng = np.random.default_rng(SEED)
    close = np.round(100 * np.exp(np.cumsum(rng.normal(0, 0.015, N))), 2)
    open_ = np.round(np.concatenate([[100.0], close[:-1]]) * (1 + rng.normal(0, 0.003, N)), 2)
    high = np.round(np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, N))), 2)
    low = np.round(np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, N))), 2)
    volume = rng.integers(50_000, 500_000, N).astype(float)
    return {"open": open_, "high": high, "low": low, "close": close, "volume": volume}


def write_bars(b: dict[str, np.ndarray]) -> None:
    days = np.busday_offset("2025-06-02", np.arange(N), roll="forward")
    with (HERE / "bars.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for i in range(N):
            w.writerow(
                [
                    str(days[i]),
                    *(f"{b[k][i]:.2f}" for k in ("open", "high", "low", "close")),
                    int(b["volume"][i]),
                ]
            )


def series(a: np.ndarray) -> list[float | None]:
    return [None if math.isnan(x) else float(x) for x in a]


def write(name: str, params: dict[str, float], outputs: dict[str, np.ndarray], how: str) -> None:
    record = {
        "indicator": name,
        "version": 1,
        "params": params,
        "bars": "bars.csv",
        "source": SOURCE,
        "how": how,
        "tolerance": {"rel": 1e-9, "abs": 1e-9},
        "outputs": {k: series(v) for k, v in outputs.items()},
    }
    (HERE / f"{name}.json").write_text(json.dumps(record, indent=1) + "\n")


def shift(a: np.ndarray, k: int) -> np.ndarray:
    return np.concatenate([np.full(k, np.nan), a[:-k]])


def main() -> None:
    b = make_bars()
    write_bars(b)
    h, lw, c, v = (b[k] for k in ("high", "low", "close", "volume"))

    write("sma", {"period": 20}, {"sma": talib.SMA(c, 20)}, "SMA")
    write("ema", {"period": 20}, {"ema": talib.EMA(c, 20)}, "EMA (SMA seed)")
    write("wma", {"period": 20}, {"wma": talib.WMA(c, 20)}, "WMA")
    hma = talib.WMA(2 * talib.WMA(c, 10) - talib.WMA(c, 20), 4)
    write("hma", {"period": 20}, {"hma": hma}, "WMA(2*WMA(c,10)-WMA(c,20), 4)")
    vwma = talib.SUM(c * v, 20) / talib.SUM(v, 20)
    write("vwma", {"period": 20}, {"vwma": vwma}, "SUM(c*v,20)/SUM(v,20)")
    write("dema", {"period": 20}, {"dema": talib.DEMA(c, 20)}, "DEMA")
    write("tema", {"period": 20}, {"tema": talib.TEMA(c, 20)}, "TEMA")
    tenkan, kijun, span_b = (
        talib.MIDPRICE(h, lw, 9),
        talib.MIDPRICE(h, lw, 26),
        talib.MIDPRICE(h, lw, 52),
    )
    write(
        "ichimoku",
        {"tenkan": 9, "kijun": 26, "senkou_b": 52},
        {"tenkan": tenkan, "kijun": kijun, "senkou_a": (tenkan + kijun) / 2, "senkou_b": span_b},
        "MIDPRICE(9), MIDPRICE(26), their mean, MIDPRICE(52); unshifted",
    )
    write(
        "psar", {"acceleration": 0.02, "maximum": 0.2}, {"psar": talib.SAR(h, lw, 0.02, 0.2)}, "SAR"
    )
    write(
        "adx",
        {"period": 14},
        {
            "plus_di": talib.PLUS_DI(h, lw, c, 14),
            "minus_di": talib.MINUS_DI(h, lw, c, 14),
            "adx": talib.ADX(h, lw, c, 14),
        },
        "PLUS_DI, MINUS_DI, ADX",
    )
    up, lo = talib.MAX(h, 20), talib.MIN(lw, 20)
    write(
        "donchian",
        {"period": 20},
        {"upper": up, "middle": (up + lo) / 2, "lower": lo},
        "MAX(h,20), MIN(l,20), their mean",
    )
    mid, atr10 = talib.EMA(c, 20), talib.ATR(h, lw, c, 10)
    write(
        "keltner",
        {"period": 20, "atr_period": 10, "multiplier": 2},
        {"upper": mid + 2 * atr10, "middle": mid, "lower": mid - 2 * atr10},
        "EMA(c,20) +/- 2*ATR(10)",
    )

    write("rsi", {"period": 14}, {"rsi": talib.RSI(c, 14)}, "RSI (Wilder)")
    fast, slow = talib.EMA(c, 12), talib.EMA(c, 26)
    line = fast - slow
    signal = talib.EMA(line, 9)
    write(
        "macd",
        {"fast": 12, "slow": 26, "signal": 9},
        {"macd": line, "signal": signal, "histogram": line - signal},
        "EMA(c,12)-EMA(c,26); EMA(macd,9) over the defined macd values",
    )
    k, d = talib.STOCH(h, lw, c, 14, 3, 0, 3, 0)
    write("stochastic", {"k": 14, "k_smooth": 3, "d": 3}, {"k": k, "d": d}, "STOCH(14,3,SMA,3,SMA)")
    r = talib.RSI(c, 14)
    sk, sd = talib.STOCH(r, r, r, 14, 3, 0, 3, 0)
    write(
        "stoch_rsi",
        {"rsi": 14, "stoch": 14, "k": 3, "d": 3},
        {"k": sk, "d": sd},
        "STOCH over RSI(14): STOCH(rsi,rsi,rsi,14,3,SMA,3,SMA)",
    )
    write("cci", {"period": 20}, {"cci": talib.CCI(h, lw, c, 20)}, "CCI")
    write("williams_r", {"period": 14}, {"williams_r": talib.WILLR(h, lw, c, 14)}, "WILLR")
    write("roc", {"period": 10}, {"roc": talib.ROC(c, 10)}, "ROC")
    write("mfi", {"period": 14}, {"mfi": talib.MFI(h, lw, c, v, 14)}, "MFI")

    bu, bm, bl = talib.BBANDS(c, 20, 2, 2, 0)
    write(
        "bollinger",
        {"period": 20, "multiplier": 2},
        {
            "upper": bu,
            "middle": bm,
            "lower": bl,
            "percent_b": (c - bl) / (bu - bl),
            "bandwidth": (bu - bl) / bm,
        },
        "BBANDS(20,2,2,SMA) population stddev; %B=(c-lower)/(upper-lower); bw=(upper-lower)/middle",
    )
    write("atr", {"period": 14}, {"atr": talib.ATR(h, lw, c, 14)}, "ATR (Wilder)")
    logret = np.concatenate([[np.nan], np.log(c[1:] / c[:-1])])
    write(
        "historical_volatility",
        {"period": 20, "annualisation": 252},
        {"hv": talib.STDDEV(logret, 20, 1) * math.sqrt(252) * 100},
        "STDDEV(ln(c/c[-1]),20) population * sqrt(252) * 100",
    )
    atr22 = talib.ATR(h, lw, c, 22)
    write(
        "chandelier",
        {"period": 22, "multiplier": 3},
        {"long_stop": talib.MAX(h, 22) - 3 * atr22, "short_stop": talib.MIN(lw, 22) + 3 * atr22},
        "MAX(h,22)-3*ATR(22); MIN(l,22)+3*ATR(22)",
    )

    write("volume", {}, {"volume": v}, "the input volume")
    write("obv", {}, {"obv": talib.OBV(c, v)}, "OBV (first value = first volume)")
    write("ad", {}, {"ad": talib.AD(h, lw, c, v)}, "AD")
    mfv = np.where(h > lw, ((c - lw) - (h - c)) / np.where(h > lw, h - lw, 1.0), 0.0) * v
    write(
        "cmf",
        {"period": 20},
        {"cmf": talib.SUM(mfv, 20) / talib.SUM(v, 20)},
        "SUM(mfm*v,20)/SUM(v,20)",
    )
    write(
        "relative_volume",
        {"period": 20},
        {"rvol": v / shift(talib.SMA(v, 20), 1)},
        "v / SMA(v,20) of the 20 bars before",
    )


if __name__ == "__main__":
    main()
