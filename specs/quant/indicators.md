# Built-in indicators: formulas and golden values

Code: `packages/chartmath/src/axiom_chartmath/indicators/`. Goldens: `specs/quant/golden/indicators/<name>.json`, one per registered indicator. Test: `uv run pytest packages/chartmath -m golden`.

## Rules every indicator follows

- **Pure and incremental.** Each indicator is a generator: send it the next bar, it returns that bar's outputs. Feeding bars one at a time is the live update; a full recompute is the same stepper run over the series. A test checks the two agree after every one of 500 appended bars.
- **Warm-up.** An output is `None` until it has enough bars. Each indicator declares its warm-up per output (the bar index of the first value on gapless bars). The test checks the declaration against the reference's own first value and that nothing is emitted earlier. Session-based indicators declare none: they start after the first session (VWAP) or after one completed session (levels).
- **Wilder smoothing** for RSI, ATR and ADX/DMI: seed with the mean of the first n values, then `(prev*(n-1) + x)/n`. The SMA-smoothed (Cutler) RSI is checked to fail the RSI golden.
- **EMA seed:** the SMA of the first n inputs, `k = 2/(n+1)` (TA-Lib's default).
- **Session reset:** session indicators take a `SessionCalendar`: 09:15–15:30 IST on weekdays that are not holidays. A bar outside a session (pre-open, holiday print) draws nothing and changes no state. The calendar here is passed in; it is a fixture until the platform trading calendar lands.
- **Corporate actions:** inputs are adjusted before any indicator runs: `adjust_splits(bars, [(ex_date, factor)])` divides earlier prices and multiplies earlier volume and delivery by the factor (2.0 for a 1:2 split). Tested: a 1:2 split leaves the adjusted SMA flat where the raw SMA shows a fall.
- **Versions:** every indicator has a `version` (all 1 today). Each golden records the version it was made for and the test fails when they differ, so a formula change has to ship as a new version with a new golden. Evidence cards cite `name@version`.
- **Tolerance:** `|got - golden| <= 1e-9 + 1e-9*|golden|`, and `None` must line up exactly.

## Golden sources

`generate.py` in the golden folder writes `bars.csv` (500 seeded bars, seed 20261114, a log-normal walk around 100 with OHLC and volume) and every TA-Lib golden. It runs outside the project environment, so TA-Lib is never a project dependency:

```
uv run --no-project specs/quant/golden/indicators/generate.py
```

Pinned: ta-lib 0.8.3 (TA-Lib C 0.8.3), numpy 2.5.4. TradingView exports: **NOT RUN** (none available here).

| Indicator | Version | Reference formula | Golden from | Defaults |
|---|---|---|---|---|
| sma | 1 | mean of last n closes | TA-Lib `SMA` | 20 |
| ema | 1 | SMA seed, k = 2/(n+1) | TA-Lib `EMA` | 20 |
| wma | 1 | weights 1..n, newest n | TA-Lib `WMA` | 20 |
| hma | 1 | WMA(2·WMA(n/2) − WMA(n), ⌊√n⌋) | TA-Lib `WMA` composed | 20 |
| vwma | 1 | Σ(C·V)/ΣV over n | TA-Lib `SUM` composed | 20 |
| dema | 1 | 2·EMA − EMA(EMA) | TA-Lib `DEMA` | 20 |
| tema | 1 | 3·EMA − 3·EMA² + EMA³ | TA-Lib `TEMA` | 20 |
| supertrend | 1 | see hand fixture | hand-computed | 10, 3 |
| ichimoku | 1 | midprice(9), midprice(26), their mean, midprice(52); unshifted | TA-Lib `MIDPRICE` composed | 9, 26, 52 |
| psar | 1 | Wilder parabolic SAR, TA-Lib start rule | TA-Lib `SAR` | 0.02, 0.2 |
| adx | 1 | +DI, −DI, ADX (Wilder) | TA-Lib `PLUS_DI`, `MINUS_DI`, `ADX` | 14 |
| donchian | 1 | HH(n), LL(n), mean | TA-Lib `MAX`/`MIN` composed | 20 |
| keltner | 1 | EMA(n) ± m·ATR(a) | TA-Lib `EMA` + `ATR` composed | 20, 10, 2 |
| rsi | 1 | Wilder RSI | TA-Lib `RSI` | 14 |
| macd | 1 | EMA(12) − EMA(26), signal EMA(9) | TA-Lib `EMA` composed | 12, 26, 9 |
| stochastic | 1 | slow %K = SMA3 of fast %K, %D = SMA3 of %K | TA-Lib `STOCH` | 14, 3, 3 |
| stoch_rsi | 1 | slow stochastic over RSI(14) | TA-Lib `RSI` + `STOCH` composed | 14, 14, 3, 3 |
| cci | 1 | (TP − SMA(TP)) / (0.015 · mean abs dev) | TA-Lib `CCI` | 20 |
| williams_r | 1 | −100·(HH − C)/(HH − LL) | TA-Lib `WILLR` | 14 |
| roc | 1 | 100·(C/C[n] − 1) | TA-Lib `ROC` | 10 |
| mfi | 1 | money-flow index | TA-Lib `MFI` | 14 |
| bollinger | 1 | SMA ± m·population sd; %B; bandwidth | TA-Lib `BBANDS`, %B and bandwidth by arithmetic on its bands | 20, 2 |
| atr | 1 | Wilder ATR | TA-Lib `ATR` | 14 |
| historical_volatility | 1 | 100·√252·population sd of ln(C/C₋₁) over n | TA-Lib `STDDEV` composed | 20, 252 |
| chandelier | 1 | HH(n) − m·ATR(n); LL(n) + m·ATR(n) | TA-Lib `MAX`/`MIN` + `ATR` composed | 22, 3 |
| volume | 1 | the bar's volume | the input column | — |
| obv | 1 | on-balance volume from the first bar's volume | TA-Lib `OBV` | — |
| ad | 1 | Σ ((C−L)−(H−C))/(H−L)·V | TA-Lib `AD` | — |
| cmf | 1 | Σ MFM·V / ΣV over n | TA-Lib `SUM` composed | 20 |
| relative_volume | 1 | V / mean V of the n bars before | TA-Lib `SMA` composed, shifted one bar | 20 |
| session_vwap | 1 | see hand fixture | hand-computed | — |
| anchored_vwap | 1 | see hand fixture | hand-computed | anchor |
| pivots_classic | 1 | floor pivots | hand-computed | — |
| camarilla | 1 | Camarilla | hand-computed | — |
| cpr | 1 | central pivot range | hand-computed | — |
| previous_levels | 1 | previous day, week, month H/L | hand-computed | — |
| delivery_pct | 1 | 100·delivered/traded | hand-computed | — |
| futures_oi | 1 | OI and its bar-on-bar change | hand-computed | — |

"Composed" means the golden is plain arithmetic over TA-Lib outputs, written in `generate.py` beside the TA-Lib call, because TA-Lib has no single function for it.

### Conventions where references differ

- **True range on bar 0** is undefined (no previous close), as in TA-Lib, so ATR's first value is at bar n, the mean of TR over bars 1..n. TradingView counts bar 0's high − low and starts one bar earlier (recalled, UNVERIFIED).
- **ADX/DMI** follows TA-Lib exactly: the DM and TR sums start from n − 1 values (bars 1..n−1), then `S − S/n + x`. Wilder's book sums n values first. The two differ in the early bars and converge as the smoothing forgets the seed.
- **MACD** is the difference of two independently SMA-seeded EMAs, with the signal EMA seeded on the first nine MACD values. TA-Lib's own `MACD` function re-seeds the fast EMA at the slow EMA's first bar and holds all outputs to bar 33. The golden uses TA-Lib's `EMA`, not its `MACD`; the two converge after the warm-up.
- **Stochastic** emits %K and %D together once %D is defined (TA-Lib aligns them; TradingView draws %K two bars earlier, recalled, UNVERIFIED).
- **Ichimoku** values are unshifted; the chart draws the spans 26 bars ahead and the lagging line is the close drawn 26 bars back, so it is not a separate output.
- **Bollinger** uses population sd (divide by n), as TA-Lib does (TradingView's default is also population sd: recalled, UNVERIFIED). %B is `None` when the band has zero width.
- **Historical volatility** annualises with 252 trading days.
- **Supertrend direction** is `1` up, `-1` down (TradingView's sign is the reverse: recalled, UNVERIFIED).
- **MFI** reports 0 when total money flow is under 1 (TA-Lib's rule).

## Hand-computed goldens

Each fixture is the `bars` array inside its JSON. The arithmetic below is what the JSON numbers were taken from; nothing came from the library.

### Session fixture (session_vwap, pivots_classic, camarilla, cpr, previous_levels)

Calendar: 09:15–15:30 IST, fixture holiday **Tue 3 Nov 2026**. Bars (H, L, C, V); typical price TP = (H+L+C)/3:

| Bar (IST) | H | L | C | V | TP | In session? |
|---|---|---|---|---|---|---|
| Fri 23 Oct 09:15 | 120 | 90 | 105 | 100 | 105 | yes |
| Wed 28 Oct 09:15 | 102 | 98 | 100 | 100 | 100 | yes |
| 28 Oct 11:15 | 106 | 100 | 103 | 200 | 103 | yes |
| 28 Oct 13:15 | 105 | 99 | 102 | 100 | 102 | yes |
| Thu 29 Oct 09:00 | 101 | 101 | 101 | 50 | 101 | no, pre-open |
| 29 Oct 09:15 | 108 | 102 | 105 | 100 | 105 | yes |
| 29 Oct 11:15 | 110 | 104 | 107 | 300 | 107 | yes |
| 29 Oct 13:15 | 109 | 103 | 103 | 100 | 105 | yes |
| Fri 30 Oct 09:15 | 107 | 101 | 104 | 200 | 104 | yes |
| 30 Oct 11:15 | 105 | 97 | 98 | 200 | 100 | yes |
| 30 Oct 13:15 | 100 | 94 | 97 | 100 | 97 | yes |
| Mon 2 Nov 09:15 | 99 | 93 | 96 | 100 | 96 | yes |
| 2 Nov 11:15 | 101 | 95 | 98 | 100 | 98 | yes |
| 2 Nov 13:15 | 103 | 97 | 100 | 200 | 100 | yes |
| Tue 3 Nov 09:15 | 200 | 190 | 195 | 999 | 195 | no, holiday |
| Wed 4 Nov 09:15 | 104 | 98 | 101 | 100 | 101 | yes |
| 4 Nov 11:15 | 106 | 100 | 103 | 100 | 103 | yes |
| 4 Nov 13:15 | 105 | 99 | 102 | 200 | 102 | yes |

Session H/L/C: 23 Oct 120/90/105; 28 Oct 106/98/102; 29 Oct 110/102/103; 30 Oct 107/94/97; 2 Nov 103/93/100; 4 Nov 106/98/102.

**Session VWAP** = ΣTP·V / ΣV from the session's first bar; variance = ΣTP²·V/ΣV − VWAP²; bands at ±1 and ±2 sd.

| Bar | ΣTP·V | ΣV | VWAP | ΣTP²·V / ΣV | variance |
|---|---|---|---|---|---|
| 23 Oct 09:15 | 10500 | 100 | 105 | 11025 | 0 |
| 28 Oct 09:15 | 10000 | 100 | 100 | 10000 | 0 |
| 28 Oct 11:15 | 30600 | 300 | 102 | 3121800/300 = 10406 | 10406 − 10404 = 2 |
| 28 Oct 13:15 | 40800 | 400 | 102 | 4162200/400 = 10405.5 | 1.5 |
| 29 Oct 09:00 | — | — | None (pre-open) | — | — |
| 29 Oct 09:15 | 10500 | 100 | 105 | 11025 | 0 (reset: nothing from 28 Oct) |
| 29 Oct 11:15 | 42600 | 400 | 106.5 | 4537200/400 = 11343 | 11343 − 11342.25 = 0.75 |
| 29 Oct 13:15 | 53100 | 500 | 106.2 | 5639700/500 = 11279.4 | 11279.4 − 11278.44 = 0.96 |
| 30 Oct 09:15 | 20800 | 200 | 104 | 10816 | 0 |
| 30 Oct 11:15 | 40800 | 400 | 102 | 4163200/400 = 10408 | 4 |
| 30 Oct 13:15 | 50500 | 500 | 101 | 5104100/500 = 10208.2 | 7.2 |
| 2 Nov 09:15 | 9600 | 100 | 96 | 9216 | 0 |
| 2 Nov 11:15 | 19400 | 200 | 97 | 1882000/200 = 9410 | 1 |
| 2 Nov 13:15 | 39400 | 400 | 98.5 | 3882000/400 = 9705 | 9705 − 9702.25 = 2.75 |
| 3 Nov 09:15 | — | — | None (holiday) | — | — |
| 4 Nov 09:15 | 10100 | 100 | 101 | 10201 | 0 |
| 4 Nov 11:15 | 20400 | 200 | 102 | 2081000/200 = 10405 | 1 |
| 4 Nov 13:15 | 40800 | 400 | 102 | 4161800/400 = 10404.5 | 0.5 |

Upper/lower bands are VWAP ± √variance and ± 2√variance (e.g. 28 Oct 11:15: 102 ± 1.41421356…).

**Levels from the previous session** (every bar of a session sees the same values; 23 Oct, the pre-open bar and the holiday bar see None). P = (H+L+C)/3.

| Session | Previous session H/L/C | P | Classic R1 / R2 / R3 | Classic S1 / S2 / S3 |
|---|---|---|---|---|
| 28 Oct | 23 Oct 120/90/105 | 105 | 2P−L = 120; P+(H−L) = 135; H+2(P−L) = 150 | 2P−H = 90; P−(H−L) = 75; L−2(H−P) = 60 |
| 29 Oct | 28 Oct 106/98/102 | 102 | 106; 110; 114 | 98; 94; 90 |
| 30 Oct | 29 Oct 110/102/103 | 105 | 108; 113; 116 | 100; 97; 92 |
| 2 Nov | 30 Oct 107/94/97 | 298/3 = 99.333… | 104.666…; 112.333…; 117.666… | 91.666…; 86.333…; 78.666… |
| 4 Nov | 2 Nov 103/93/100 (not the 3 Nov holiday) | 296/3 = 98.666… | 104.333…; 108.666…; 114.333… | 94.333…; 88.666…; 84.333… |

Camarilla: C ± (H−L)·1.1/12, /6, /4, /2 for levels 1–4. 28 Oct (range 30, C 105): R1–R4 107.75, 110.5, 113.25, 121.5; S1–S4 102.25, 99.5, 96.75, 88.5. 29 Oct (range 8, C 102): 102.733…, 103.466…, 104.2, 106.4 / 101.266…, 100.533…, 99.8, 97.6. 30 Oct (range 8, C 103): 103.733…, 104.466…, 105.2, 107.4 / 102.266…, 101.533…, 100.8, 98.6. 2 Nov (range 13, C 97): 98.191…, 99.383…, 100.575, 104.15 / 95.808…, 94.616…, 93.425, 89.85. 4 Nov (range 10, C 100): 100.916…, 101.833…, 102.75, 105.5 / 99.083…, 98.166…, 97.25, 94.5.

CPR: BC = (H+L)/2, TC = 2P − BC, top/bottom = larger/smaller. 28 Oct: P 105, BC 105, TC 105. 29 Oct: 102, 102, 102. 30 Oct: P 105, BC 106, TC 104 → top 106, bottom 104. 2 Nov: P 99.333…, BC 100.5, TC 98.166… → top 100.5, bottom 98.166…. 4 Nov: P 98.666…, BC 98, TC 99.333… → top 99.333…, bottom 98. Without the holiday the 3 Nov print would be a session and 4 Nov's pivot would be (200+190+195)/3 = 195; the test checks that it is not.

Previous levels (day / ISO week / month high–low): 23 Oct: none. 28–30 Oct (week 44): previous day is the prior session; previous week is week 43 = 23 Oct only → 120/90; previous month none (no September data). 2 and 4 Nov (week 45, November): previous week = 28–30 Oct → max H 110, min L 94; previous month = October → 120/90. Previous day on 4 Nov is 2 Nov (103/93), skipping the holiday.

### Supertrend (period 3, multiplier 1)

Bars 10–19 Oct 2026, H/L/C: (10,8,9) (11,9,10) (12,10,11) (13,11,12) (14,12,13) (12,9,9) (9,6,7) (10,7,9.5) (13,10,12.5) (14,12,13.5).

TR from bar 1: 2, 2, 2, 2, max(3, |12−13|, |9−13|) = 4, max(3, 0, 3) = 3, max(3, 3, 0) = 3, max(3, 3.5, 0.5) = 3.5, max(2, 1.5, 0.5) = 2.
ATR(3) Wilder: bar 3 = (2+2+2)/3 = 2; bar 4 = (2·2+2)/3 = 2; bar 5 = (4+4)/3 = 8/3; bar 6 = (16/3+3)/3 = 25/9; bar 7 = (50/9+3)/3 = 77/27; bar 8 = (154/27+3.5)/3 = 248.5/81; bar 9 = (497/81+2)/3 = 659/243.

| Bar | hl2 | raw upper / lower | final upper / lower | direction | line |
|---|---|---|---|---|---|
| 3 | 12 | 14 / 10 | 14 / 10 (first value) | down | 14 |
| 4 | 13 | 15 / 11 | upper: 15 ≥ 14 and prev close 12 ≤ 14 → 14; lower 11 > 10 → 11 | close 13 ≤ 14 → down | 14 |
| 5 | 10.5 | 13.1667 / 7.8333 | upper 79/6 < 14 → 79/6; lower 7.83 ≤ 11 and prev close 13 ≥ 11 → 11 | 9 ≤ 79/6 → down | 79/6 = 13.1667 |
| 6 | 7.5 | 92.5/9 / 42.5/9 | upper 10.2778; lower: prev close 9 < 11 → reset to 4.7222 | 7 ≤ 10.28 → down | 10.2778 |
| 7 | 8.5 | 11.3519 / 5.6481 | upper stays 10.2778; lower 5.6481 > 4.72 → 5.6481 | 9.5 ≤ 10.28 → down | 10.2778 |
| 8 | 11.5 | 14.5679 / 8.4321 | upper stays 10.2778; lower 8.4321 | 12.5 > 10.2778 → **up** | 11.5 − 248.5/81 = 8.4321 |
| 9 | 13 | 15.7119 / 10.2881 | upper: prev close 12.5 > 10.28 → 15.7119; lower 10.2881 | up and 13.5 ≥ 10.2881 → up | 13 − 659/243 = 10.2881 |

### Anchored VWAP (anchor Tue 13 Oct 2026 09:15 IST, an expiry session) on the supertrend bars

V = 1000 per bar. TP from bar 3: 12, 13, 10, 22/3, 26.5/3, 35.5/3, 39.5/3. In units of 1000 volume:

| Bar | ΣTP | n | VWAP | ΣTP² / n | variance |
|---|---|---|---|---|---|
| 0–2 | — | — | None (before anchor) | — | — |
| 3 | 12 | 1 | 12 | 144 | 0 |
| 4 | 25 | 2 | 12.5 | 313/2 = 156.5 | 0.25 |
| 5 | 35 | 3 | 35/3 | 413/3 | 413/3 − 1225/9 = 14/9 |
| 6 | 127/3 | 4 | 127/12 | 4201/36 | 4201/36 − 16129/144 = 675/144 |
| 7 | 153.5/3 | 5 | 307/30 | 4903.25/45 | 4.24 |
| 8 | 63 | 6 | 10.5 | 6163.5/54 | 35/9 |
| 9 | 228.5/3 | 7 | 228.5/21 | 7723.75/63 | 1854/441 |

### India fixture (delivery_pct, futures_oi)

| Bar | V | delivered | OI | delivery % | OI change |
|---|---|---|---|---|---|
| 10 Oct | 1000 | 400 | 10000 | 40 | None |
| 11 Oct | 2000 | 500 | 12000 | 25 | +2000 |
| 12 Oct | 1500 | 1500 | 11500 | 100 | −500 |
| 13 Oct | 800 | none | 11500 | None | 0 |

## Not built, or built without an independent golden

- **PCR and the India VIX overlay: moved to plan unit U12.** Both need a second input series (option-chain put and call OI, the India VIX series) that the bar type does not carry, and no feed shape for them exists yet. They are data alignment rather than formulas: PCR = put OI / call OI per bar, the overlay draws VIX closes on the price chart.
- **Volume profile** is built in the profile module (`specs/quant/profile.md`), not as a per-bar indicator.
- **TradingView exports: NOT RUN.** No export is available here; every TA-Lib-covered indicator has a TA-Lib golden instead.
- **Hand fixtures** cover supertrend, session and anchored VWAP, classic and Camarilla pivots, CPR, previous levels, delivery % and futures OI. They are independent of the code but small; a second source (TradingView exports, NSE delivery files) should replace them when available.
