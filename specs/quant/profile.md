# Market profile math: definitions and golden values

Code: `packages/chartmath/src/axiom_chartmath/profile/`. Golden: `specs/quant/golden/profile/session.json`. Test: `uv run pytest packages/chartmath/tests/test_profile.py`. Definitions follow `docs/research/2026-11-14-market-profile-order-flow-patterns.md` section 1; where that note leaves a choice open, the choice made is stated here.

## Definitions

- **Session:** 09:15–15:30 IST on trading days (`SessionCalendar`). Bars outside it are ignored. Index profiles are built on index futures bars; the caller passes futures, not spot.
- **Rows:** row r covers prices [r·row_size, (r+1)·row_size). A bar touches every row from its low's row to its high's row.
- **TPO periods:** 30 minutes from 09:15, so 13 periods; the last (15:15–15:30) is 15 minutes and flagged `half`, for day-type thresholds to leave out. A period prints one TPO on every row its range touched.
- **Initial balance:** high and low of the first two periods (09:15–10:15). `None` if the session has no bars in that hour.
- **Volume at price:** each bar's volume is spread evenly over the rows it spans.
- **POC:** the row with the most TPOs (vPOC: most volume). Ties go to the row nearest the middle of the session's range, then the lower row.
- **Value area (70%):** two-row method. From the POC, compare the sum of the next two rows above with the next two below and add the larger pair, until the area holds at least 70% of the total. When one side is exhausted the other is used. **Equal pairs add both sides** (a choice: the research note leaves ties open), so a flat profile stays centred. Computed for TPOs and for volume.
- **Single prints:** rows with one TPO that have a row with two or more TPOs both above and below them. Rows with one TPO at the session's extreme are tails, not single prints.
- **Poor high / poor low:** the session's top (bottom) row has two or more TPOs.
- **HVN / LVN:** volume at price smoothed with a Gaussian of sigma 2 rows (kernel cut at 3 sigma, rows outside the profile count 0). HVN: a local maximum above 0.6 × the smoothed peak. LVN: an interior local minimum below 0.3 × the smoothed peak. The cut-offs are engineering convention.
- **Parameters and version:** `ProfileParams(row_size, value_area=0.70, hvn_ratio=0.6, lvn_ratio=0.3, smoothing_rows=2.0)`. `version` is a hash of all fields; every profile carries it. Any change, a row size included, gives a new version. Composites and carried levels refuse to mix versions, since rows of different sizes do not line up.

## Nested timeframes and carried levels

- **Today:** the session profile.
- **Current balance:** a run of sessions whose value areas each overlap the session before. Balance began on the first session of the run that ends today, provided the session before the run had value elsewhere. If today's value does not overlap yesterday's, or the run reaches back to the first session in the data (no observed start), the composite falls back to the last 5 sessions. This rule is a choice; the research note does not pin one down.
- **Expiry cycle:** sessions after the last expiry before today, up to today. Expiry dates come from the SEBI calendar in force (Tuesday expiries for contracts from 1 Sep 2025); the expiry session belongs to the cycle it ends.
- **Basis-adjusted continuous future:** `back_adjust(bars, [(first bar of new contract, new − old price)])` moves every bar before each roll by its basis. Composites are built on adjusted bars, so a roll adds no false structure.
- **Carried levels:** a naked POC or an unfilled single print stays carried until a later session trades its row. A poor high clears when a later session trades above it, a poor low when one trades below.
- **VWAP bands:** session and anchored VWAP with ±1 and ±2 volume-weighted sd are the `session_vwap` and `anchored_vwap` indicators (`specs/quant/indicators.md`); the anchored golden is anchored on an expiry session and hand-computed there.

## Golden session (hand-checked)

**Substitution:** no recorded NIFTY futures session is available here, so the golden is a synthetic session shaped like one: Wed 4 Nov 2026, prices 24015–24075, row size 5, one bar per 30-minute period. Replace it with a hand-checked recorded session when the data exists.

Periods (offsets from 24000; each bar spans low to high):

| Period | Start | Low–High | Rows (offsets) | TPOs | Volume | Volume per row |
|---|---|---|---|---|---|---|
| A | 09:15 | 20–40 | 20 25 30 35 40 | 5 | 5000 | 1000 |
| B | 09:45 | 15–35 | 15 20 25 30 35 | 5 | 5000 | 1000 |
| C | 10:15 | 25–45 | 25 30 35 40 45 | 5 | 5000 | 1000 |
| D | 10:45 | 45–65 | 45 50 55 60 65 | 5 | 10000 | 2000 |
| E | 11:15 | 55–70 | 55 60 65 70 | 4 | 4000 | 1000 |
| F | 11:45 | 60–70 | 60 65 70 | 3 | 3000 | 1000 |
| G | 12:15 | 55–65 | 55 60 65 | 3 | 3000 | 1000 |
| H | 12:45 | 60–75 | 60 65 70 75 | 4 | 4000 | 1000 |
| I | 13:15 | 65–75 | 65 70 75 | 3 | 3000 | 1000 |
| J | 13:45 | 60–70 | 60 65 70 | 3 | 3000 | 1000 |
| K | 14:15 | 60–70 | 60 65 70 | 3 | 3000 | 1000 |
| L | 14:45 | 65–75 | 65 70 75 | 3 | 3000 | 1000 |
| M (half) | 15:15 | 70–75 | 70 75 | 2 | 1000 | 500 |

TPO count per row: 15: B = 1; 20: AB = 2; 25: ABC = 3; 30: 3; 35: 3; 40: AC = 2; 45: CD = 2; 50: D = 1; 55: DEG = 3; 60: DEFGHJK = 7; 65: DEFGHIJKL = 9; 70: EFHIJKLM = 8; 75: HILM = 4. Total 48.

- **POC** = 24065 (9 TPOs).
- **TPO value area**, target 0.7 × 48 = 33.6: start 9 at 65. Above (70, 75) = 12 vs below (60, 55) = 10 → add above, 21. Above exhausted; below (60, 55) = 10 → 31. Below (50, 45) = 1 + 2 = 3 → 34 ≥ 33.6. **VAL 24045, VAH 24075.**
- **Single prints:** 24050 (one TPO, rows with ≥ 2 above at 55 and below at 45). Row 15 has one TPO but nothing below it: a tail, not a single print.
- **Poor high:** top row 75 has 4 TPOs → yes. **Poor low:** bottom row 15 has 1 → no.
- **IB:** A and B → high 24040, low 24015.
- **Half period:** M (index 12, 15:15).

Volume per row (thousands): 15: 1; 20: 2; 25: 3; 30: 3; 35: 3; 40: 2; 45: 1 + 2 = 3; 50: 2; 55: 2 + 1 + 1 = 4; 60: 2 + 6 = 8; 65: 2 + 8 = 10; 70: 7 + 0.5 = 7.5; 75: 3 + 0.5 = 3.5. Total 52, target 0.7 × 52 = 36.4.

- **vPOC** = 24065 (10).
- **Volume value area:** start 10. Above (70, 75) = 11 vs below (60, 55) = 12 → below, 22. Above 11 vs below (50, 45) = 5 → above, 33. Above exhausted; below 5 → 38 ≥ 36.4. **VAL 24045, VAH 24075.**

## Scenario fixtures (in the test file)

- **Balance start:** five one-period sessions with ranges 100–200, 300–400, 310–390, 320–400, 305–385. A flat one-period profile's value area is the middle of its range (e.g. 300–400: 21 rows, target 14.7; from 350, two rows each side per step: 1, 5, 9, 13, 17 TPOs → 310–390). The first session's value (110–190) does not touch the second's (310–390); the second to fifth overlap each other, so balance began on the second.
- **Fallback:** seven mutually overlapping sessions (no observed start) and a run ending in a 600–700 breakout (today outside yesterday's value) both give the last five sessions.
- **40-point roll:** two sessions on the old contract and two on the new, each twelve periods of 23990–24010 (new: +40). Spliced raw, the composite has two HVNs (24000 and 24040) that the market never traded as one auction. Back-adjusted by +40, it has one HVN at 24040 and no LVN.
- **Naked POC:** session 1 POC 120 (ranges 100–140, 115–125, 115–125: rows 115/120/125 tie at 3 TPOs, 120 is nearest the middle); session 2 trades 150–180 and leaves it naked; session 3 trades 110–130 and clears it.

## Not built here

- **Day-type thresholds** (and so the use of the half flag) belong to the auction model, which is not in this package; the profile only flags the half period.
- **Weekly and monthly value as reference levels:** `composite()` over the week's or month's sessions gives them; no separate helper.
- **Non-default labelling** of changed settings: the parameter version identifies a changed set, and labelling is the chart's job.
- **HVN/LVN goldens** are structural (count and position on the roll fixture), not hand-computed smoothed values.
