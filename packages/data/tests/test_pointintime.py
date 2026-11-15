from datetime import UTC, date, datetime, timezone

import pytest
from axiom_data.pointintime import (
    IST,
    EffectiveDatedRow,
    NaiveTimestampRefused,
    PointInTimeTable,
    RuleUnknown,
    ensure_utc_aware,
    parse_csv_rule_rows,
)


def _dt(year: int, month: int, day: int, hour: int = 0, tz: timezone = UTC) -> datetime:
    return datetime(year, month, day, hour, 0, 0, tzinfo=tz)


def test_inclusive_start() -> None:
    """A row in force from 2024-11-20 answers for 2024-11-20 and not for 2024-11-19."""
    table = PointInTimeTable("test_rule")
    table.load(
        [
            EffectiveDatedRow(
                key="NIFTY",
                effective_from=date(2024, 11, 20),
                effective_to=None,
                published_at=_dt(2024, 10, 1),
                recorded_at=_dt(2024, 10, 1),
                source="SEBI/2024/132",
                verified_against="SEBI/2024/132",
            )
        ]
    )

    # Answers for 2024-11-20
    res = table.resolve("NIFTY", date(2024, 11, 20))
    assert res.value.key == "NIFTY"
    assert res.is_verified is True
    assert res.limitations == ()

    # Not for 2024-11-19
    with pytest.raises(RuleUnknown) as exc:
        table.resolve("NIFTY", date(2024, 11, 19))
    assert exc.value.rule == "test_rule"
    assert str(date(2024, 11, 19)) in str(exc.value)


def test_exclusive_end() -> None:
    """A row ending 2025-09-01 does not answer for 2025-09-01."""
    table = PointInTimeTable("test_rule")
    table.load(
        [
            EffectiveDatedRow(
                key="NIFTY",
                effective_from=date(2024, 1, 1),
                effective_to=date(2025, 9, 1),
                published_at=_dt(2023, 12, 1),
                recorded_at=_dt(2023, 12, 1),
                source="CIRCULAR/1",
                verified_against="CIRCULAR/1",
            )
        ]
    )

    # Answers for 2025-08-31
    res = table.resolve("NIFTY", date(2025, 8, 31))
    assert res.value.effective_to == date(2025, 9, 1)

    # Does not answer for 2025-09-01
    with pytest.raises(RuleUnknown):
        table.resolve("NIFTY", date(2025, 9, 1))


def test_date_before_first_row_raises_rule_unknown() -> None:
    """A date before the first row raises RuleUnknown naming the rule and the date."""
    table = PointInTimeTable("expiry_rule")
    table.load(
        [
            EffectiveDatedRow(
                key="NIFTY",
                effective_from=date(2020, 1, 1),
                effective_to=None,
                published_at=_dt(2019, 12, 1),
                recorded_at=_dt(2019, 12, 1),
                source="CIRCULAR/0",
            )
        ]
    )

    with pytest.raises(RuleUnknown) as exc:
        table.resolve("NIFTY", date(2018, 6, 1))
    assert exc.value.rule == "expiry_rule"
    assert "2018-06-01" in str(exc.value)


def test_gap_between_rows_raises_rule_unknown() -> None:
    """A gap between two rows raises RuleUnknown for a date inside the gap."""
    table = PointInTimeTable("test_rule")
    table.load(
        [
            EffectiveDatedRow(
                key="K",
                effective_from=date(2020, 1, 1),
                effective_to=date(2021, 1, 1),
                published_at=_dt(2019, 12, 1),
                recorded_at=_dt(2019, 12, 1),
                source="S1",
            ),
            EffectiveDatedRow(
                key="K",
                effective_from=date(2022, 1, 1),
                effective_to=date(2023, 1, 1),
                published_at=_dt(2019, 12, 1),
                recorded_at=_dt(2019, 12, 1),
                source="S2",
            ),
        ]
    )

    with pytest.raises(RuleUnknown):
        table.resolve("K", date(2021, 6, 1))


def test_overlapping_rows_same_recorded_at_fail_at_load() -> None:
    """Two rows for the same key and date with the same recorded_at fail at load."""
    rec = _dt(2024, 1, 1)
    rows = [
        EffectiveDatedRow(
            key="NIFTY",
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 6, 1),
            published_at=_dt(2023, 12, 1),
            recorded_at=rec,
            source="S1",
        ),
        EffectiveDatedRow(
            key="NIFTY",
            effective_from=date(2024, 3, 1),
            effective_to=date(2024, 9, 1),
            published_at=_dt(2023, 12, 1),
            recorded_at=rec,
            source="S2",
        ),
    ]

    table = PointInTimeTable("test_rule")
    with pytest.raises(ValueError, match="overlapping rows"):
        table.load(rows)


def test_loading_same_csv_twice_raises_overlapping_error() -> None:
    """Loading the same CSV rows twice must raise ValueError for overlapping ranges."""
    csv_text = (
        "key,effective_from,effective_to,published_at,recorded_at,source,licence_scope,"
        "verified_against\n"
        "NIFTY,2024-01-01,2024-12-31,2023-12-01T00:00:00Z,2023-12-01T00:00:00Z,CIRCULAR/1,"
        "public,CIRCULAR/1\n"
    )
    rows1 = parse_csv_rule_rows(csv_text)
    rows2 = parse_csv_rule_rows(csv_text)
    table = PointInTimeTable("test_rule", rows1)
    with pytest.raises(ValueError, match="overlapping rows"):
        table.load(rows2)


def test_synthetic_published_at_adds_limitation() -> None:
    """When a row has published_at_synthetic=true,

    limitations includes 'synthetic publication date'.
    """
    row = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2024, 1, 1),
        effective_to=None,
        published_at=_dt(2023, 12, 1),
        recorded_at=_dt(2023, 12, 1),
        source="CIRCULAR/1",
        verified_against="CIRCULAR/1",
        payload={"published_at_synthetic": "true"},
    )
    table = PointInTimeTable("test_rule", [row])
    res = table.resolve("NIFTY", date(2024, 6, 1))
    assert "synthetic publication date" in res.limitations


def test_correction_recorded_later_wins() -> None:
    """A correction recorded today for a 2025 row is the answer for a 2025 lookup."""
    initial = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2025, 1, 1),
        effective_to=None,
        published_at=_dt(2024, 12, 1),
        recorded_at=_dt(2024, 12, 1),
        source="S1",
        payload={"lot_size": 50},
    )
    correction = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2025, 1, 1),
        effective_to=None,
        published_at=_dt(2024, 12, 15),
        recorded_at=_dt(2025, 1, 10),
        source="S2",
        payload={"lot_size": 75},
    )

    table = PointInTimeTable("test_rule", [initial, correction])
    res = table.resolve("NIFTY", date(2025, 2, 1))
    assert res.value.payload["lot_size"] == 75


def test_backfill_today_with_past_published_at_answers_past_lookup() -> None:
    """A row backfilled today with a 2023 published_at answers a 2023 lookup."""
    backfilled = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2023, 1, 1),
        effective_to=date(2024, 1, 1),
        published_at=_dt(2023, 1, 1),
        recorded_at=_dt(2026, 11, 14),  # recorded today
        source="ARCHIVE",
        payload={"value": "historical"},
    )

    table = PointInTimeTable("test_rule", [backfilled])
    res = table.resolve("NIFTY", date(2023, 6, 1))
    assert res.value.payload["value"] == "historical"


def test_published_at_d_plus_one_not_visible_on_d() -> None:
    """A row published on D+1 is not visible to a lookup on D."""
    row = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2024, 1, 1),
        effective_to=None,
        published_at=_dt(2024, 5, 2, 10, tz=IST),  # published May 2nd 10:00 AM IST
        recorded_at=_dt(2024, 5, 2, 10, tz=IST),
        source="NEWS",
    )

    table = PointInTimeTable("test_rule", [row])
    # Lookup on May 1st (D) -> end of May 1st IST is 2024-05-01 23:59:59.999999 IST
    # row was published on May 2nd (D+1), so it must not be visible!
    with pytest.raises(RuleUnknown):
        table.resolve("NIFTY", date(2024, 5, 1))

    # Lookup on May 2nd -> visible
    res = table.resolve("NIFTY", date(2024, 5, 2))
    assert res.value.key == "NIFTY"


def test_unverified_rule_limitation() -> None:
    """A row with empty verified_against marks the result unverified; a filled one does not."""
    unverified_row = EffectiveDatedRow(
        key="K1",
        effective_from=date(2024, 1, 1),
        effective_to=None,
        published_at=_dt(2024, 1, 1),
        recorded_at=_dt(2024, 1, 1),
        source="S1",
        verified_against="",
    )
    verified_row = EffectiveDatedRow(
        key="K2",
        effective_from=date(2024, 1, 1),
        effective_to=None,
        published_at=_dt(2024, 1, 1),
        recorded_at=_dt(2024, 1, 1),
        source="S2",
        verified_against="NSE/2024/001",
    )

    table = PointInTimeTable("test_rule", [unverified_row, verified_row])

    res1 = table.resolve("K1", date(2024, 6, 1))
    assert res1.is_verified is False
    assert "unverified rule" in res1.limitations
    assert res1.sources[0].name == "S1"

    res2 = table.resolve("K2", date(2024, 6, 1))
    assert res2.is_verified is True
    assert res2.limitations == ()
    assert res2.sources[0].name == "S2"


def test_naive_timestamp_rejected() -> None:
    """A naive published_at or recorded_at is rejected, and stored values are UTC (KTD5)."""
    naive_dt = datetime(2024, 1, 1, 0, 0, 0)  # naive

    with pytest.raises(NaiveTimestampRefused):
        ensure_utc_aware(naive_dt)

    with pytest.raises(NaiveTimestampRefused):
        EffectiveDatedRow(
            key="NIFTY",
            effective_from=date(2024, 1, 1),
            effective_to=None,
            published_at=naive_dt,
            recorded_at=_dt(2024, 1, 1),
            source="S",
        )

    # An aware non-UTC timestamp is stored in UTC
    ist_dt = datetime(2024, 1, 1, 5, 30, 0, tzinfo=IST)
    row = EffectiveDatedRow(
        key="NIFTY",
        effective_from=date(2024, 1, 1),
        effective_to=None,
        published_at=ist_dt,
        recorded_at=ist_dt,
        source="S",
    )
    assert row.published_at.tzinfo == UTC
    assert row.published_at.hour == 0  # 5:30 IST is 0:00 UTC


def test_naive_datetime_passed_to_resolve_refused() -> None:
    """A naive timestamp passed to resolve is refused."""
    table = PointInTimeTable("test_rule")
    with pytest.raises(NaiveTimestampRefused):
        table.resolve("NIFTY", datetime(2024, 1, 1, 12, 0))


def test_parse_csv_rule_rows() -> None:
    csv_header = (
        "key,effective_from,effective_to,published_at,recorded_at,"
        "source,licence_scope,verified_against,extra_val\n"
    )
    csv_row = (
        "NIFTY,2024-11-20,,2024-10-01T00:00:00Z,2024-10-01T00:00:00Z,"
        "SEBI/2024/132,public,,1500000\n"
    )
    csv_data = csv_header + csv_row
    rows = parse_csv_rule_rows(csv_data)
    assert len(rows) == 1
    r = rows[0]
    assert r.key == "NIFTY"
    assert r.effective_from == date(2024, 11, 20)
    assert r.effective_to is None
    assert r.payload["extra_val"] == "1500000"
    assert r.is_verified is False
