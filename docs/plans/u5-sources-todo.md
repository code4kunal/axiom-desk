# U5 Reference Data Sources TODO

This document tracks every row in `packages/data/src/axiom_data/reference/` whose primary regulatory circular or official exchange notice has not been directly read and verified against primary PDF sources.

Per review rule B1: *"Never invent a circular number. For every row where you cannot point to a primary document you actually read, set source to UNSOURCED. Keep verified_against blank."*

**Due before 2026-12-31:** add 2027 exchange holidays to `holidays.csv` and raise `COVERAGE_END` in `calendar.py`. Until then every date after 2026-12-31 is refused (CalendarHorizonExceeded).

**Total UNSOURCED rows: 296**

## `asset_class_roles.csv` (15 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `equity` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `fno` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `mutual_fund` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `etf` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `commodity_etf_sgb` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `reit_invit` | `2019-01-01` | Verify asset class role basket-eligible against SEBI/exchange instrument regulations or desk policy |
| `gsec_tbill_sdl` | `2019-01-01` | Verify asset class role broker-executable only against SEBI/exchange instrument regulations or desk policy |
| `corporate_bond` | `2019-01-01` | Verify asset class role tracking only against SEBI/exchange instrument regulations or desk policy |
| `international_fund_fof` | `2019-01-01` | Verify asset class role investable while open to inflows against SEBI/exchange instrument regulations or desk policy |
| `global_index` | `2019-01-01` | Verify asset class role analysis-only against SEBI/exchange instrument regulations or desk policy |
| `fx` | `2019-01-01` | Verify asset class role analysis-only against SEBI/exchange instrument regulations or desk policy |
| `global_commodity` | `2019-01-01` | Verify asset class role analysis-only against SEBI/exchange instrument regulations or desk policy |
| `foreign_yield` | `2019-01-01` | Verify asset class role analysis-only against SEBI/exchange instrument regulations or desk policy |
| `foreign_stock` | `2019-01-01` | Verify asset class role out of scope against SEBI/exchange instrument regulations or desk policy |
| `crypto` | `2019-01-01` | Verify asset class role out of scope against SEBI/exchange instrument regulations or desk policy |

## `contract_value.csv` (4 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `NSE:NIFTY` | `2019-01-01` | Verify historical minimum contract value 500000 against primary exchange circular |
| `NSE:ALL` | `2019-01-01` | Verify historical minimum contract value 500000 against primary exchange circular |
| `BSE:SENSEX` | `2019-01-01` | Verify historical minimum contract value 500000 against primary exchange circular |
| `BSE:ALL` | `2019-01-01` | Verify historical minimum contract value 500000 against primary exchange circular |

## `expiry_margin_rules.csv` (2 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `NSE:ALL` | `2019-01-01` | Verify historical calendar spread margin benefit true against primary circular |
| `BSE:ALL` | `2019-01-01` | Verify historical calendar spread margin benefit true against primary circular |

## `expiry_rules.csv` (21 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `NSE:NIFTY:weekly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:NIFTY:weekly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:NIFTY:monthly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:NIFTY:monthly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:BANKNIFTY:weekly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:BANKNIFTY:weekly` | `2023-09-01` | Verify expiry weekday Wednesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:BANKNIFTY:weekly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:BANKNIFTY:monthly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:BANKNIFTY:monthly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:ALL:weekly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:ALL:weekly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:ALL:monthly` | `2019-01-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `NSE:ALL:monthly` | `2025-09-01` | Verify expiry weekday Tuesday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:SENSEX:weekly` | `2019-01-01` | Verify expiry weekday Friday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:SENSEX:weekly` | `2025-09-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:SENSEX:monthly` | `2019-01-01` | Verify expiry weekday Friday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:SENSEX:monthly` | `2025-09-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:ALL:weekly` | `2019-01-01` | Verify expiry weekday Friday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:ALL:weekly` | `2025-09-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:ALL:monthly` | `2019-01-01` | Verify expiry weekday Friday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |
| `BSE:ALL:monthly` | `2025-09-01` | Verify expiry weekday Thursday against primary exchange circular (e.g. BankNifty Wed shift, Sep 2025 Tuesday shift) |

## `holidays.csv` (236 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `equity` | `2019-03-04` | Verify holiday Maha Shivratri on 2019-03-04 against primary annual exchange holiday circular |
| `fno` | `2019-03-04` | Verify holiday Maha Shivratri on 2019-03-04 against primary annual exchange holiday circular |
| `equity` | `2019-03-21` | Verify holiday Holi on 2019-03-21 against primary annual exchange holiday circular |
| `fno` | `2019-03-21` | Verify holiday Holi on 2019-03-21 against primary annual exchange holiday circular |
| `equity` | `2019-04-17` | Verify holiday Mahavir Jayanti on 2019-04-17 against primary annual exchange holiday circular |
| `fno` | `2019-04-17` | Verify holiday Mahavir Jayanti on 2019-04-17 against primary annual exchange holiday circular |
| `equity` | `2019-04-19` | Verify holiday Good Friday on 2019-04-19 against primary annual exchange holiday circular |
| `fno` | `2019-04-19` | Verify holiday Good Friday on 2019-04-19 against primary annual exchange holiday circular |
| `equity` | `2019-04-29` | Verify holiday Lok Sabha Election on 2019-04-29 against primary annual exchange holiday circular |
| `fno` | `2019-04-29` | Verify holiday Lok Sabha Election on 2019-04-29 against primary annual exchange holiday circular |
| `equity` | `2019-05-01` | Verify holiday Maharashtra Day on 2019-05-01 against primary annual exchange holiday circular |
| `fno` | `2019-05-01` | Verify holiday Maharashtra Day on 2019-05-01 against primary annual exchange holiday circular |
| `equity` | `2019-06-05` | Verify holiday Id-Ul-Fitr on 2019-06-05 against primary annual exchange holiday circular |
| `fno` | `2019-06-05` | Verify holiday Id-Ul-Fitr on 2019-06-05 against primary annual exchange holiday circular |
| `equity` | `2019-08-12` | Verify holiday Bakri Id on 2019-08-12 against primary annual exchange holiday circular |
| `fno` | `2019-08-12` | Verify holiday Bakri Id on 2019-08-12 against primary annual exchange holiday circular |
| `equity` | `2019-08-15` | Verify holiday Independence Day on 2019-08-15 against primary annual exchange holiday circular |
| `fno` | `2019-08-15` | Verify holiday Independence Day on 2019-08-15 against primary annual exchange holiday circular |
| `equity` | `2019-09-02` | Verify holiday Ganesh Chaturthi on 2019-09-02 against primary annual exchange holiday circular |
| `fno` | `2019-09-02` | Verify holiday Ganesh Chaturthi on 2019-09-02 against primary annual exchange holiday circular |
| `equity` | `2019-09-10` | Verify holiday Muharram on 2019-09-10 against primary annual exchange holiday circular |
| `fno` | `2019-09-10` | Verify holiday Muharram on 2019-09-10 against primary annual exchange holiday circular |
| `equity` | `2019-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2019-10-02 against primary annual exchange holiday circular |
| `fno` | `2019-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2019-10-02 against primary annual exchange holiday circular |
| `equity` | `2019-10-08` | Verify holiday Dussehra on 2019-10-08 against primary annual exchange holiday circular |
| `fno` | `2019-10-08` | Verify holiday Dussehra on 2019-10-08 against primary annual exchange holiday circular |
| `equity` | `2019-10-21` | Verify holiday Assembly Election on 2019-10-21 against primary annual exchange holiday circular |
| `fno` | `2019-10-21` | Verify holiday Assembly Election on 2019-10-21 against primary annual exchange holiday circular |
| `equity` | `2019-10-27` | Verify holiday Diwali Laxmi Pujan on 2019-10-27 against primary annual exchange holiday circular |
| `fno` | `2019-10-27` | Verify holiday Diwali Laxmi Pujan on 2019-10-27 against primary annual exchange holiday circular |
| `equity` | `2019-10-28` | Verify holiday Diwali Balipratipada on 2019-10-28 against primary annual exchange holiday circular |
| `fno` | `2019-10-28` | Verify holiday Diwali Balipratipada on 2019-10-28 against primary annual exchange holiday circular |
| `equity` | `2019-11-12` | Verify holiday Gurunanak Jayanti on 2019-11-12 against primary annual exchange holiday circular |
| `fno` | `2019-11-12` | Verify holiday Gurunanak Jayanti on 2019-11-12 against primary annual exchange holiday circular |
| `equity` | `2019-12-25` | Verify holiday Christmas on 2019-12-25 against primary annual exchange holiday circular |
| `fno` | `2019-12-25` | Verify holiday Christmas on 2019-12-25 against primary annual exchange holiday circular |
| `equity` | `2020-02-21` | Verify holiday Maha Shivratri on 2020-02-21 against primary annual exchange holiday circular |
| `fno` | `2020-02-21` | Verify holiday Maha Shivratri on 2020-02-21 against primary annual exchange holiday circular |
| `equity` | `2020-03-10` | Verify holiday Holi on 2020-03-10 against primary annual exchange holiday circular |
| `fno` | `2020-03-10` | Verify holiday Holi on 2020-03-10 against primary annual exchange holiday circular |
| `equity` | `2020-04-02` | Verify holiday Ram Navami on 2020-04-02 against primary annual exchange holiday circular |
| `fno` | `2020-04-02` | Verify holiday Ram Navami on 2020-04-02 against primary annual exchange holiday circular |
| `equity` | `2020-04-06` | Verify holiday Mahavir Jayanti on 2020-04-06 against primary annual exchange holiday circular |
| `fno` | `2020-04-06` | Verify holiday Mahavir Jayanti on 2020-04-06 against primary annual exchange holiday circular |
| `equity` | `2020-04-10` | Verify holiday Good Friday on 2020-04-10 against primary annual exchange holiday circular |
| `fno` | `2020-04-10` | Verify holiday Good Friday on 2020-04-10 against primary annual exchange holiday circular |
| `equity` | `2020-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2020-04-14 against primary annual exchange holiday circular |
| `fno` | `2020-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2020-04-14 against primary annual exchange holiday circular |
| `equity` | `2020-05-01` | Verify holiday Maharashtra Day on 2020-05-01 against primary annual exchange holiday circular |
| `fno` | `2020-05-01` | Verify holiday Maharashtra Day on 2020-05-01 against primary annual exchange holiday circular |
| `equity` | `2020-05-25` | Verify holiday Id-Ul-Fitr on 2020-05-25 against primary annual exchange holiday circular |
| `fno` | `2020-05-25` | Verify holiday Id-Ul-Fitr on 2020-05-25 against primary annual exchange holiday circular |
| `equity` | `2020-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2020-10-02 against primary annual exchange holiday circular |
| `fno` | `2020-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2020-10-02 against primary annual exchange holiday circular |
| `equity` | `2020-11-16` | Verify holiday Diwali Balipratipada on 2020-11-16 against primary annual exchange holiday circular |
| `fno` | `2020-11-16` | Verify holiday Diwali Balipratipada on 2020-11-16 against primary annual exchange holiday circular |
| `equity` | `2020-11-30` | Verify holiday Gurunanak Jayanti on 2020-11-30 against primary annual exchange holiday circular |
| `fno` | `2020-11-30` | Verify holiday Gurunanak Jayanti on 2020-11-30 against primary annual exchange holiday circular |
| `equity` | `2020-12-25` | Verify holiday Christmas on 2020-12-25 against primary annual exchange holiday circular |
| `fno` | `2020-12-25` | Verify holiday Christmas on 2020-12-25 against primary annual exchange holiday circular |
| `equity` | `2021-01-26` | Verify holiday Republic Day on 2021-01-26 against primary annual exchange holiday circular |
| `fno` | `2021-01-26` | Verify holiday Republic Day on 2021-01-26 against primary annual exchange holiday circular |
| `equity` | `2021-03-11` | Verify holiday Maha Shivratri on 2021-03-11 against primary annual exchange holiday circular |
| `fno` | `2021-03-11` | Verify holiday Maha Shivratri on 2021-03-11 against primary annual exchange holiday circular |
| `equity` | `2021-03-29` | Verify holiday Holi on 2021-03-29 against primary annual exchange holiday circular |
| `fno` | `2021-03-29` | Verify holiday Holi on 2021-03-29 against primary annual exchange holiday circular |
| `equity` | `2021-04-02` | Verify holiday Good Friday on 2021-04-02 against primary annual exchange holiday circular |
| `fno` | `2021-04-02` | Verify holiday Good Friday on 2021-04-02 against primary annual exchange holiday circular |
| `equity` | `2021-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2021-04-14 against primary annual exchange holiday circular |
| `fno` | `2021-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2021-04-14 against primary annual exchange holiday circular |
| `equity` | `2021-04-21` | Verify holiday Ram Navami on 2021-04-21 against primary annual exchange holiday circular |
| `fno` | `2021-04-21` | Verify holiday Ram Navami on 2021-04-21 against primary annual exchange holiday circular |
| `equity` | `2021-05-13` | Verify holiday Id-Ul-Fitr on 2021-05-13 against primary annual exchange holiday circular |
| `fno` | `2021-05-13` | Verify holiday Id-Ul-Fitr on 2021-05-13 against primary annual exchange holiday circular |
| `equity` | `2021-07-21` | Verify holiday Bakri Id on 2021-07-21 against primary annual exchange holiday circular |
| `fno` | `2021-07-21` | Verify holiday Bakri Id on 2021-07-21 against primary annual exchange holiday circular |
| `equity` | `2021-08-19` | Verify holiday Muharram on 2021-08-19 against primary annual exchange holiday circular |
| `fno` | `2021-08-19` | Verify holiday Muharram on 2021-08-19 against primary annual exchange holiday circular |
| `equity` | `2021-09-10` | Verify holiday Ganesh Chaturthi on 2021-09-10 against primary annual exchange holiday circular |
| `fno` | `2021-09-10` | Verify holiday Ganesh Chaturthi on 2021-09-10 against primary annual exchange holiday circular |
| `equity` | `2021-10-15` | Verify holiday Dussehra on 2021-10-15 against primary annual exchange holiday circular |
| `fno` | `2021-10-15` | Verify holiday Dussehra on 2021-10-15 against primary annual exchange holiday circular |
| `equity` | `2021-11-04` | Verify holiday Diwali Laxmi Pujan on 2021-11-04 against primary annual exchange holiday circular |
| `fno` | `2021-11-04` | Verify holiday Diwali Laxmi Pujan on 2021-11-04 against primary annual exchange holiday circular |
| `equity` | `2021-11-05` | Verify holiday Diwali Balipratipada on 2021-11-05 against primary annual exchange holiday circular |
| `fno` | `2021-11-05` | Verify holiday Diwali Balipratipada on 2021-11-05 against primary annual exchange holiday circular |
| `equity` | `2021-11-19` | Verify holiday Gurunanak Jayanti on 2021-11-19 against primary annual exchange holiday circular |
| `fno` | `2021-11-19` | Verify holiday Gurunanak Jayanti on 2021-11-19 against primary annual exchange holiday circular |
| `equity` | `2022-01-26` | Verify holiday Republic Day on 2022-01-26 against primary annual exchange holiday circular |
| `fno` | `2022-01-26` | Verify holiday Republic Day on 2022-01-26 against primary annual exchange holiday circular |
| `equity` | `2022-03-01` | Verify holiday Maha Shivratri on 2022-03-01 against primary annual exchange holiday circular |
| `fno` | `2022-03-01` | Verify holiday Maha Shivratri on 2022-03-01 against primary annual exchange holiday circular |
| `equity` | `2022-03-18` | Verify holiday Holi on 2022-03-18 against primary annual exchange holiday circular |
| `fno` | `2022-03-18` | Verify holiday Holi on 2022-03-18 against primary annual exchange holiday circular |
| `equity` | `2022-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2022-04-14 against primary annual exchange holiday circular |
| `fno` | `2022-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2022-04-14 against primary annual exchange holiday circular |
| `equity` | `2022-04-15` | Verify holiday Good Friday on 2022-04-15 against primary annual exchange holiday circular |
| `fno` | `2022-04-15` | Verify holiday Good Friday on 2022-04-15 against primary annual exchange holiday circular |
| `equity` | `2022-05-03` | Verify holiday Id-Ul-Fitr on 2022-05-03 against primary annual exchange holiday circular |
| `fno` | `2022-05-03` | Verify holiday Id-Ul-Fitr on 2022-05-03 against primary annual exchange holiday circular |
| `equity` | `2022-08-09` | Verify holiday Muharram on 2022-08-09 against primary annual exchange holiday circular |
| `fno` | `2022-08-09` | Verify holiday Muharram on 2022-08-09 against primary annual exchange holiday circular |
| `equity` | `2022-08-15` | Verify holiday Independence Day on 2022-08-15 against primary annual exchange holiday circular |
| `fno` | `2022-08-15` | Verify holiday Independence Day on 2022-08-15 against primary annual exchange holiday circular |
| `equity` | `2022-08-31` | Verify holiday Ganesh Chaturthi on 2022-08-31 against primary annual exchange holiday circular |
| `fno` | `2022-08-31` | Verify holiday Ganesh Chaturthi on 2022-08-31 against primary annual exchange holiday circular |
| `equity` | `2022-10-05` | Verify holiday Dussehra on 2022-10-05 against primary annual exchange holiday circular |
| `fno` | `2022-10-05` | Verify holiday Dussehra on 2022-10-05 against primary annual exchange holiday circular |
| `equity` | `2022-10-24` | Verify holiday Diwali Laxmi Pujan on 2022-10-24 against primary annual exchange holiday circular |
| `fno` | `2022-10-24` | Verify holiday Diwali Laxmi Pujan on 2022-10-24 against primary annual exchange holiday circular |
| `equity` | `2022-10-26` | Verify holiday Diwali Balipratipada on 2022-10-26 against primary annual exchange holiday circular |
| `fno` | `2022-10-26` | Verify holiday Diwali Balipratipada on 2022-10-26 against primary annual exchange holiday circular |
| `equity` | `2022-11-08` | Verify holiday Gurunanak Jayanti on 2022-11-08 against primary annual exchange holiday circular |
| `fno` | `2022-11-08` | Verify holiday Gurunanak Jayanti on 2022-11-08 against primary annual exchange holiday circular |
| `equity` | `2023-01-26` | Verify holiday Republic Day on 2023-01-26 against primary annual exchange holiday circular |
| `fno` | `2023-01-26` | Verify holiday Republic Day on 2023-01-26 against primary annual exchange holiday circular |
| `equity` | `2023-03-07` | Verify holiday Holi on 2023-03-07 against primary annual exchange holiday circular |
| `fno` | `2023-03-07` | Verify holiday Holi on 2023-03-07 against primary annual exchange holiday circular |
| `equity` | `2023-03-30` | Verify holiday Ram Navami on 2023-03-30 against primary annual exchange holiday circular |
| `fno` | `2023-03-30` | Verify holiday Ram Navami on 2023-03-30 against primary annual exchange holiday circular |
| `equity` | `2023-04-04` | Verify holiday Mahavir Jayanti on 2023-04-04 against primary annual exchange holiday circular |
| `fno` | `2023-04-04` | Verify holiday Mahavir Jayanti on 2023-04-04 against primary annual exchange holiday circular |
| `equity` | `2023-04-07` | Verify holiday Good Friday on 2023-04-07 against primary annual exchange holiday circular |
| `fno` | `2023-04-07` | Verify holiday Good Friday on 2023-04-07 against primary annual exchange holiday circular |
| `equity` | `2023-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2023-04-14 against primary annual exchange holiday circular |
| `fno` | `2023-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2023-04-14 against primary annual exchange holiday circular |
| `equity` | `2023-05-01` | Verify holiday Maharashtra Day on 2023-05-01 against primary annual exchange holiday circular |
| `fno` | `2023-05-01` | Verify holiday Maharashtra Day on 2023-05-01 against primary annual exchange holiday circular |
| `equity` | `2023-06-29` | Verify holiday Bakri Id on 2023-06-29 against primary annual exchange holiday circular |
| `fno` | `2023-06-29` | Verify holiday Bakri Id on 2023-06-29 against primary annual exchange holiday circular |
| `equity` | `2023-08-15` | Verify holiday Independence Day on 2023-08-15 against primary annual exchange holiday circular |
| `fno` | `2023-08-15` | Verify holiday Independence Day on 2023-08-15 against primary annual exchange holiday circular |
| `equity` | `2023-09-19` | Verify holiday Ganesh Chaturthi on 2023-09-19 against primary annual exchange holiday circular |
| `fno` | `2023-09-19` | Verify holiday Ganesh Chaturthi on 2023-09-19 against primary annual exchange holiday circular |
| `equity` | `2023-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2023-10-02 against primary annual exchange holiday circular |
| `fno` | `2023-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2023-10-02 against primary annual exchange holiday circular |
| `equity` | `2023-10-24` | Verify holiday Dussehra on 2023-10-24 against primary annual exchange holiday circular |
| `fno` | `2023-10-24` | Verify holiday Dussehra on 2023-10-24 against primary annual exchange holiday circular |
| `equity` | `2023-11-14` | Verify holiday Diwali Balipratipada on 2023-11-14 against primary annual exchange holiday circular |
| `fno` | `2023-11-14` | Verify holiday Diwali Balipratipada on 2023-11-14 against primary annual exchange holiday circular |
| `equity` | `2023-11-27` | Verify holiday Gurunanak Jayanti on 2023-11-27 against primary annual exchange holiday circular |
| `fno` | `2023-11-27` | Verify holiday Gurunanak Jayanti on 2023-11-27 against primary annual exchange holiday circular |
| `equity` | `2023-12-25` | Verify holiday Christmas on 2023-12-25 against primary annual exchange holiday circular |
| `fno` | `2023-12-25` | Verify holiday Christmas on 2023-12-25 against primary annual exchange holiday circular |
| `equity` | `2024-01-22` | Verify holiday Special Ram Mandir Holiday on 2024-01-22 against primary annual exchange holiday circular |
| `fno` | `2024-01-22` | Verify holiday Special Ram Mandir Holiday on 2024-01-22 against primary annual exchange holiday circular |
| `equity` | `2024-01-26` | Verify holiday Republic Day on 2024-01-26 against primary annual exchange holiday circular |
| `fno` | `2024-01-26` | Verify holiday Republic Day on 2024-01-26 against primary annual exchange holiday circular |
| `equity` | `2024-03-08` | Verify holiday Maha Shivratri on 2024-03-08 against primary annual exchange holiday circular |
| `fno` | `2024-03-08` | Verify holiday Maha Shivratri on 2024-03-08 against primary annual exchange holiday circular |
| `equity` | `2024-03-25` | Verify holiday Holi on 2024-03-25 against primary annual exchange holiday circular |
| `fno` | `2024-03-25` | Verify holiday Holi on 2024-03-25 against primary annual exchange holiday circular |
| `equity` | `2024-03-29` | Verify holiday Good Friday on 2024-03-29 against primary annual exchange holiday circular |
| `fno` | `2024-03-29` | Verify holiday Good Friday on 2024-03-29 against primary annual exchange holiday circular |
| `equity` | `2024-04-11` | Verify holiday Id-Ul-Fitr on 2024-04-11 against primary annual exchange holiday circular |
| `fno` | `2024-04-11` | Verify holiday Id-Ul-Fitr on 2024-04-11 against primary annual exchange holiday circular |
| `equity` | `2024-04-17` | Verify holiday Ram Navami on 2024-04-17 against primary annual exchange holiday circular |
| `fno` | `2024-04-17` | Verify holiday Ram Navami on 2024-04-17 against primary annual exchange holiday circular |
| `equity` | `2024-05-01` | Verify holiday Maharashtra Day on 2024-05-01 against primary annual exchange holiday circular |
| `fno` | `2024-05-01` | Verify holiday Maharashtra Day on 2024-05-01 against primary annual exchange holiday circular |
| `equity` | `2024-05-20` | Verify holiday Lok Sabha Election on 2024-05-20 against primary annual exchange holiday circular |
| `fno` | `2024-05-20` | Verify holiday Lok Sabha Election on 2024-05-20 against primary annual exchange holiday circular |
| `equity` | `2024-06-17` | Verify holiday Bakri Id on 2024-06-17 against primary annual exchange holiday circular |
| `fno` | `2024-06-17` | Verify holiday Bakri Id on 2024-06-17 against primary annual exchange holiday circular |
| `equity` | `2024-07-17` | Verify holiday Muharram on 2024-07-17 against primary annual exchange holiday circular |
| `fno` | `2024-07-17` | Verify holiday Muharram on 2024-07-17 against primary annual exchange holiday circular |
| `equity` | `2024-08-15` | Verify holiday Independence Day on 2024-08-15 against primary annual exchange holiday circular |
| `fno` | `2024-08-15` | Verify holiday Independence Day on 2024-08-15 against primary annual exchange holiday circular |
| `equity` | `2024-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2024-10-02 against primary annual exchange holiday circular |
| `fno` | `2024-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2024-10-02 against primary annual exchange holiday circular |
| `equity` | `2024-11-01` | Verify holiday Diwali Laxmi Pujan on 2024-11-01 against primary annual exchange holiday circular |
| `fno` | `2024-11-01` | Verify holiday Diwali Laxmi Pujan on 2024-11-01 against primary annual exchange holiday circular |
| `equity` | `2024-11-15` | Verify holiday Gurunanak Jayanti on 2024-11-15 against primary annual exchange holiday circular |
| `fno` | `2024-11-15` | Verify holiday Gurunanak Jayanti on 2024-11-15 against primary annual exchange holiday circular |
| `equity` | `2024-11-20` | Verify holiday Maharashtra Assembly Election on 2024-11-20 against primary annual exchange holiday circular |
| `fno` | `2024-11-20` | Verify holiday Maharashtra Assembly Election on 2024-11-20 against primary annual exchange holiday circular |
| `equity` | `2024-12-25` | Verify holiday Christmas on 2024-12-25 against primary annual exchange holiday circular |
| `fno` | `2024-12-25` | Verify holiday Christmas on 2024-12-25 against primary annual exchange holiday circular |
| `equity` | `2025-02-26` | Verify holiday Maha Shivratri on 2025-02-26 against primary annual exchange holiday circular |
| `fno` | `2025-02-26` | Verify holiday Maha Shivratri on 2025-02-26 against primary annual exchange holiday circular |
| `equity` | `2025-03-14` | Verify holiday Holi on 2025-03-14 against primary annual exchange holiday circular |
| `fno` | `2025-03-14` | Verify holiday Holi on 2025-03-14 against primary annual exchange holiday circular |
| `equity` | `2025-03-31` | Verify holiday Id-Ul-Fitr on 2025-03-31 against primary annual exchange holiday circular |
| `fno` | `2025-03-31` | Verify holiday Id-Ul-Fitr on 2025-03-31 against primary annual exchange holiday circular |
| `equity` | `2025-04-10` | Verify holiday Mahavir Jayanti on 2025-04-10 against primary annual exchange holiday circular |
| `fno` | `2025-04-10` | Verify holiday Mahavir Jayanti on 2025-04-10 against primary annual exchange holiday circular |
| `equity` | `2025-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2025-04-14 against primary annual exchange holiday circular |
| `fno` | `2025-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2025-04-14 against primary annual exchange holiday circular |
| `equity` | `2025-04-18` | Verify holiday Good Friday on 2025-04-18 against primary annual exchange holiday circular |
| `fno` | `2025-04-18` | Verify holiday Good Friday on 2025-04-18 against primary annual exchange holiday circular |
| `equity` | `2025-05-01` | Verify holiday Maharashtra Day on 2025-05-01 against primary annual exchange holiday circular |
| `fno` | `2025-05-01` | Verify holiday Maharashtra Day on 2025-05-01 against primary annual exchange holiday circular |
| `equity` | `2025-08-15` | Verify holiday Independence Day on 2025-08-15 against primary annual exchange holiday circular |
| `fno` | `2025-08-15` | Verify holiday Independence Day on 2025-08-15 against primary annual exchange holiday circular |
| `equity` | `2025-08-27` | Verify holiday Ganesh Chaturthi on 2025-08-27 against primary annual exchange holiday circular |
| `fno` | `2025-08-27` | Verify holiday Ganesh Chaturthi on 2025-08-27 against primary annual exchange holiday circular |
| `equity` | `2025-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2025-10-02 against primary annual exchange holiday circular |
| `fno` | `2025-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2025-10-02 against primary annual exchange holiday circular |
| `equity` | `2025-10-21` | Verify holiday Diwali Laxmi Pujan on 2025-10-21 against primary annual exchange holiday circular |
| `fno` | `2025-10-21` | Verify holiday Diwali Laxmi Pujan on 2025-10-21 against primary annual exchange holiday circular |
| `equity` | `2025-10-22` | Verify holiday Diwali Balipratipada on 2025-10-22 against primary annual exchange holiday circular |
| `fno` | `2025-10-22` | Verify holiday Diwali Balipratipada on 2025-10-22 against primary annual exchange holiday circular |
| `equity` | `2025-11-05` | Verify holiday Gurunanak Jayanti on 2025-11-05 against primary annual exchange holiday circular |
| `fno` | `2025-11-05` | Verify holiday Gurunanak Jayanti on 2025-11-05 against primary annual exchange holiday circular |
| `equity` | `2025-12-25` | Verify holiday Christmas on 2025-12-25 against primary annual exchange holiday circular |
| `fno` | `2025-12-25` | Verify holiday Christmas on 2025-12-25 against primary annual exchange holiday circular |
| `equity` | `2026-01-26` | Verify holiday Republic Day on 2026-01-26 against primary annual exchange holiday circular |
| `fno` | `2026-01-26` | Verify holiday Republic Day on 2026-01-26 against primary annual exchange holiday circular |
| `equity` | `2026-03-03` | Verify holiday Holi on 2026-03-03 against primary annual exchange holiday circular |
| `fno` | `2026-03-03` | Verify holiday Holi on 2026-03-03 against primary annual exchange holiday circular |
| `equity` | `2026-03-20` | Verify holiday Id-Ul-Fitr on 2026-03-20 against primary annual exchange holiday circular |
| `fno` | `2026-03-20` | Verify holiday Id-Ul-Fitr on 2026-03-20 against primary annual exchange holiday circular |
| `equity` | `2026-04-03` | Verify holiday Good Friday on 2026-04-03 against primary annual exchange holiday circular |
| `fno` | `2026-04-03` | Verify holiday Good Friday on 2026-04-03 against primary annual exchange holiday circular |
| `equity` | `2026-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2026-04-14 against primary annual exchange holiday circular |
| `fno` | `2026-04-14` | Verify holiday Dr. Ambedkar Jayanti on 2026-04-14 against primary annual exchange holiday circular |
| `equity` | `2026-05-01` | Verify holiday Maharashtra Day on 2026-05-01 against primary annual exchange holiday circular |
| `fno` | `2026-05-01` | Verify holiday Maharashtra Day on 2026-05-01 against primary annual exchange holiday circular |
| `equity` | `2026-05-27` | Verify holiday Bakri Id on 2026-05-27 against primary annual exchange holiday circular |
| `fno` | `2026-05-27` | Verify holiday Bakri Id on 2026-05-27 against primary annual exchange holiday circular |
| `equity` | `2026-06-26` | Verify holiday Muharram on 2026-06-26 against primary annual exchange holiday circular |
| `fno` | `2026-06-26` | Verify holiday Muharram on 2026-06-26 against primary annual exchange holiday circular |
| `equity` | `2026-08-15` | Verify holiday Independence Day on 2026-08-15 against primary annual exchange holiday circular |
| `fno` | `2026-08-15` | Verify holiday Independence Day on 2026-08-15 against primary annual exchange holiday circular |
| `equity` | `2026-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2026-10-02 against primary annual exchange holiday circular |
| `fno` | `2026-10-02` | Verify holiday Mahatma Gandhi Jayanti on 2026-10-02 against primary annual exchange holiday circular |
| `equity` | `2026-10-20` | Verify holiday Dussehra on 2026-10-20 against primary annual exchange holiday circular |
| `fno` | `2026-10-20` | Verify holiday Dussehra on 2026-10-20 against primary annual exchange holiday circular |
| `equity` | `2026-11-08` | Verify holiday Diwali Laxmi Pujan on 2026-11-08 against primary annual exchange holiday circular |
| `fno` | `2026-11-08` | Verify holiday Diwali Laxmi Pujan on 2026-11-08 against primary annual exchange holiday circular |
| `equity` | `2026-11-09` | Verify holiday Diwali Balipratipada on 2026-11-09 against primary annual exchange holiday circular |
| `fno` | `2026-11-09` | Verify holiday Diwali Balipratipada on 2026-11-09 against primary annual exchange holiday circular |
| `equity` | `2026-11-24` | Verify holiday Gurunanak Jayanti on 2026-11-24 against primary annual exchange holiday circular |
| `fno` | `2026-11-24` | Verify holiday Gurunanak Jayanti on 2026-11-24 against primary annual exchange holiday circular |
| `equity` | `2026-12-25` | Verify holiday Christmas on 2026-12-25 against primary annual exchange holiday circular |
| `fno` | `2026-12-25` | Verify holiday Christmas on 2026-12-25 against primary annual exchange holiday circular |

## `position_limits.csv` (2 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `NSE:INDEX` | `2019-01-01` | Verify historical position limit 500cr_or_15pct_oi against primary SEBI circular |
| `BSE:INDEX` | `2019-01-01` | Verify historical position limit 500cr_or_15pct_oi against primary SEBI circular |

## `session_hours.csv` (4 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `equity` | `2019-01-01` | Verify regular session hours 09:15:00-15:30:00 against market operational circular |
| `fno` | `2019-01-01` | Verify regular session hours 09:15:00-15:30:00 against market operational circular |
| `currency` | `2019-01-01` | Verify regular session hours 09:00:00-17:00:00 against market operational circular |
| `commodity` | `2019-01-01` | Verify regular session hours 09:00:00-23:30:00 against market operational circular |

## `special_sessions.csv` (6 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `equity` | `2024-11-01` | Verify special session Muhurat Trading (18:00:00-19:00:00) against exchange notice |
| `fno` | `2024-11-01` | Verify special session Muhurat Trading (18:00:00-19:00:00) against exchange notice |
| `equity` | `2025-02-01` | Verify special session Union Budget Special Session (09:15:00-15:30:00) against exchange notice |
| `fno` | `2025-02-01` | Verify special session Union Budget Special Session (09:15:00-15:30:00) against exchange notice |
| `equity` | `2025-10-21` | Verify special session Muhurat Trading (18:15:00-19:15:00) against exchange notice |
| `fno` | `2025-10-21` | Verify special session Muhurat Trading (18:15:00-19:15:00) against exchange notice |

## `weekly_eligibility.csv` (6 rows)

| Key | Effective From / Date | What a Human Must Check |
|---|---|---|
| `NSE:NIFTY` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |
| `NSE:BANKNIFTY` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |
| `NSE:FINNIFTY` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |
| `NSE:MIDCPNIFTY` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |
| `BSE:SENSEX` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |
| `BSE:BANKEX` | `2019-01-01` | Verify historical weekly option eligibility true against exchange product launch circular |

## Rows citing a SEBI circular that has not been read (12 rows)

These rows carry `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` or `SEBI/HO/MRD/TPD-1/P/CIR/2025/79` as `source`. They are not UNSOURCED and are not counted in the total above, but nobody has read the primary circular. Each needs a human to open the circular, confirm the number, its date and the row's value, and only then fill `verified_against`. `verified_against` stays blank and the source values are unchanged until then.

| File | Key | Effective From | Source | Value to check |
|---|---|---|---|---|
| `contract_value.csv` | `NSE:NIFTY` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | min_contract_value 1500000 |
| `contract_value.csv` | `NSE:ALL` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | min_contract_value 1500000 |
| `contract_value.csv` | `BSE:SENSEX` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | min_contract_value 1500000 |
| `contract_value.csv` | `BSE:ALL` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | min_contract_value 1500000 |
| `expiry_margin_rules.csv` | `NSE:ALL` | `2025-02-01` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | calendar_spread_benefit false |
| `expiry_margin_rules.csv` | `BSE:ALL` | `2025-02-01` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | calendar_spread_benefit false |
| `weekly_eligibility.csv` | `NSE:BANKNIFTY` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | weekly_eligible false |
| `weekly_eligibility.csv` | `NSE:FINNIFTY` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | weekly_eligible false |
| `weekly_eligibility.csv` | `NSE:MIDCPNIFTY` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | weekly_eligible false |
| `weekly_eligibility.csv` | `BSE:BANKEX` | `2024-11-20` | `SEBI/HO/MRD/TPD-1/P/CIR/2024/132` | weekly_eligible false |
| `position_limits.csv` | `NSE:INDEX` | `2025-12-06` | `SEBI/HO/MRD/TPD-1/P/CIR/2025/79` | position_limit_rule 1500cr_net |
| `position_limits.csv` | `BSE:INDEX` | `2025-12-06` | `SEBI/HO/MRD/TPD-1/P/CIR/2025/79` | position_limit_rule 1500cr_net |

