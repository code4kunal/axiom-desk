from datetime import date, datetime, timedelta

import pytest
from axiom_data.calendar import (
    CalendarHorizonExceeded,
    TradingCalendar,
)
from axiom_data.pointintime import IST, NaiveTimestampRefused, RuleUnknown


@pytest.fixture
def calendar() -> TradingCalendar:
    return TradingCalendar()


@pytest.mark.parametrize("segment", ["equty", "currency", "commodity"])
def test_segment_without_holiday_data_is_rule_unknown(
    calendar: TradingCalendar, segment: str
) -> None:
    """A typo or a segment with no holiday rows must not report a regular session."""
    d = date(2024, 3, 29)  # Good Friday
    with pytest.raises(RuleUnknown):
        calendar.get_session(segment, d)
    with pytest.raises(RuleUnknown):
        calendar.is_regular_session_day(segment, d)


def test_listed_holiday_has_no_session_and_next_session_is_following_open(
    calendar: TradingCalendar,
) -> None:
    """A listed exchange holiday has no session; next is following open."""
    # 2024-03-29 is Good Friday (holiday)
    # 2024-03-30 (Saturday), 2024-03-31 (Sunday)
    # Next trading day is Monday 2024-04-01
    assert calendar.is_regular_session_day("equity", date(2024, 3, 29)) is False
    assert calendar.get_session("equity", date(2024, 3, 29)) is None

    # Query next session from Friday morning 10:00 IST on 2024-03-29
    ts = datetime(2024, 3, 29, 10, 0, tzinfo=IST)
    next_s = calendar.next_session("equity", ts)

    assert next_s.start == datetime(2024, 4, 1, 9, 15, tzinfo=IST)
    assert next_s.end == datetime(2024, 4, 1, 15, 30, tzinfo=IST)
    assert next_s.is_regular is True


def test_friday_after_close_gives_monday_or_tuesday_when_monday_is_holiday(
    calendar: TradingCalendar,
) -> None:
    """Friday 15:31 IST gives Monday 09:15 IST, or Tuesday when Monday is a holiday."""
    # Case 1: Normal weekend. Friday 2024-04-05 15:31 IST -> Monday 2024-04-08 09:15 IST
    ts_normal = datetime(2024, 4, 5, 15, 31, tzinfo=IST)
    s_normal = calendar.next_session("equity", ts_normal)
    assert s_normal.start == datetime(2024, 4, 8, 9, 15, tzinfo=IST)

    # Case 2: Monday is a holiday.
    # 2024-03-22 (Friday) -> 2024-03-25 (Monday) is Holi (exchange holiday)
    # Next session must be Tuesday 2024-03-26 09:15 IST
    ts_holi = datetime(2024, 3, 22, 15, 31, tzinfo=IST)
    s_holi = calendar.next_session("equity", ts_holi)
    assert s_holi.start == datetime(2024, 3, 26, 9, 15, tzinfo=IST)


def test_special_saturday_budget_session(calendar: TradingCalendar) -> None:
    """The special Saturday session on 2025-02-01 has own hours and is not regular."""
    budget_date = date(2025, 2, 1)  # Saturday
    assert calendar.is_regular_session_day("equity", budget_date) is False

    session = calendar.get_session("equity", budget_date)
    assert session is not None
    assert session.is_regular is False
    assert session.start == datetime(2025, 2, 1, 9, 15, tzinfo=IST)
    assert session.end == datetime(2025, 2, 1, 15, 30, tzinfo=IST)
    assert session.session_name == "Union Budget Special Session"


def test_muhurat_session(calendar: TradingCalendar) -> None:
    """A Muhurat session is open only inside its window, and is not a regular day."""
    # 2024-11-01 is Diwali Laxmi Pujan (Muhurat session: 18:00 to 19:00 IST)
    muhurat_date = date(2024, 11, 1)
    assert calendar.is_regular_session_day("equity", muhurat_date) is False

    session = calendar.get_session("equity", muhurat_date)
    assert session is not None
    assert session.is_regular is False
    assert session.start == datetime(2024, 11, 1, 18, 0, tzinfo=IST)
    assert session.end == datetime(2024, 11, 1, 19, 0, tzinfo=IST)

    # During normal day hours (e.g. 10:00 IST or 17:59 IST), it is closed
    assert calendar.is_inside_session("equity", datetime(2024, 11, 1, 10, 0, tzinfo=IST)) is False
    t_closed = datetime(2024, 11, 1, 17, 59, 59, tzinfo=IST)
    assert calendar.is_inside_session("equity", t_closed) is False

    # Inside Muhurat window
    assert calendar.is_inside_session("equity", datetime(2024, 11, 1, 18, 0, tzinfo=IST)) is True
    assert calendar.is_inside_session("equity", datetime(2024, 11, 1, 18, 30, tzinfo=IST)) is True
    assert calendar.is_inside_session("equity", datetime(2024, 11, 1, 19, 0, tzinfo=IST)) is False


def test_session_boundary_times(calendar: TradingCalendar) -> None:
    """09:14:59 IST outside; 09:15:00 inside; 15:30:00 outside (exclusive close)."""
    # 2024-04-08 (normal trading Monday)
    ts_before = datetime(2024, 4, 8, 9, 14, 59, tzinfo=IST)
    ts_open = datetime(2024, 4, 8, 9, 15, 0, tzinfo=IST)
    ts_mid = datetime(2024, 4, 8, 12, 0, 0, tzinfo=IST)
    ts_close = datetime(2024, 4, 8, 15, 30, 0, tzinfo=IST)
    ts_after = datetime(2024, 4, 8, 15, 30, 1, tzinfo=IST)

    assert calendar.is_inside_session("equity", ts_before) is False
    assert calendar.is_inside_session("equity", ts_open) is True
    assert calendar.is_inside_session("equity", ts_mid) is True
    assert calendar.is_inside_session("equity", ts_close) is False
    assert calendar.is_inside_session("equity", ts_after) is False


def test_naive_timestamp_refused(calendar: TradingCalendar) -> None:
    """A naive timestamp is refused."""
    naive_ts = datetime(2024, 4, 8, 10, 0, 0)
    with pytest.raises(NaiveTimestampRefused):
        calendar.is_inside_session("equity", naive_ts)
    with pytest.raises(NaiveTimestampRefused):
        calendar.next_session("equity", naive_ts)
    with pytest.raises(NaiveTimestampRefused):
        calendar.previous_session("equity", naive_ts)


def test_date_past_horizon_raises_horizon_error(calendar: TradingCalendar) -> None:
    """A date past the horizon raises the horizon error, as does a crossing range."""
    horizon = calendar.horizon
    past_horizon = horizon + timedelta(days=1)

    with pytest.raises(CalendarHorizonExceeded) as exc1:
        calendar.is_regular_session_day("equity", past_horizon)
    assert exc1.value.asked_date == past_horizon
    assert exc1.value.horizon == horizon

    with pytest.raises(CalendarHorizonExceeded):
        calendar.get_session("equity", past_horizon)

    with pytest.raises(CalendarHorizonExceeded):
        calendar.sessions_in_range("equity", horizon - timedelta(days=5), past_horizon)


def test_reference_rows_carry_synthetic_flag_and_calendar_reports_it() -> None:
    """Every holiday and special-session row has the flag; unverified rows give limitations."""
    import csv
    import importlib.resources

    ref = importlib.resources.files("axiom_data.reference")
    for name in ("holidays.csv", "special_sessions.csv"):
        rows = list(csv.DictReader(ref.joinpath(name).read_text(encoding="utf-8").splitlines()))
        assert all(r["published_at_synthetic"] in ("true", "false") for r in rows)
    c = TradingCalendar()
    assert "unverified rule" in c.limitations
    assert "synthetic publication date" in c.limitations
    assert {s.name for s in c.sources} == {"UNSOURCED"}
    assert TradingCalendar(holidays={}, special_sessions={}, session_hours={}).limitations == ()


def test_previous_session(calendar: TradingCalendar) -> None:
    # Monday morning 08:00 IST -> previous session was Friday 09:15-15:30
    ts = datetime(2024, 4, 8, 8, 0, tzinfo=IST)
    prev = calendar.previous_session("equity", ts)
    assert prev.start == datetime(2024, 4, 5, 9, 15, tzinfo=IST)
    assert prev.end == datetime(2024, 4, 5, 15, 30, tzinfo=IST)

    # Monday 16:00 IST -> previous session was Monday
    ts_post = datetime(2024, 4, 8, 16, 0, tzinfo=IST)
    prev_post = calendar.previous_session("equity", ts_post)
    assert prev_post.start == datetime(2024, 4, 8, 9, 15, tzinfo=IST)


def test_previous_regular_session_day(calendar: TradingCalendar) -> None:
    # On a normal regular session day, returns itself
    assert calendar.previous_regular_session_day("equity", date(2024, 4, 8)) == date(2024, 4, 8)
    # On Sunday 2024-04-07 -> returns Friday 2024-04-05
    assert calendar.previous_regular_session_day("equity", date(2024, 4, 7)) == date(2024, 4, 5)
    # On Holi Monday 2024-03-25 -> returns Friday 2024-03-22
    assert calendar.previous_regular_session_day("equity", date(2024, 3, 25)) == date(2024, 3, 22)
    # On special Saturday 2025-02-01 (Budget day, not regular) -> returns Friday 2025-01-31
    assert calendar.previous_regular_session_day("equity", date(2025, 2, 1)) == date(2025, 1, 31)


def test_coverage_end_constant_and_past_horizon_raises_rule_unknown(
    calendar: TradingCalendar,
) -> None:
    """Date past coverage_end must raise RuleUnknown, not be treated as a trading day (B3)."""
    from axiom_data.calendar import COVERAGE_END
    from axiom_data.pointintime import RuleUnknown

    assert calendar.horizon == COVERAGE_END
    past_date = COVERAGE_END + timedelta(days=1)
    with pytest.raises(RuleUnknown):
        calendar.is_regular_session_day("equity", past_date)
    with pytest.raises(RuleUnknown):
        calendar.get_session("equity", past_date)


def test_horizon_comes_from_coverage_constants_not_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    """The horizon is COVERAGE_START..COVERAGE_END, whatever years holidays.csv happens to hold."""
    import axiom_data.calendar as cal

    monkeypatch.setattr(cal, "COVERAGE_START", date(2020, 1, 1))
    monkeypatch.setattr(cal, "COVERAGE_END", date(2025, 12, 31))
    c = TradingCalendar()
    assert (c.start_date, c.horizon) == (date(2020, 1, 1), date(2025, 12, 31))
    with pytest.raises(CalendarHorizonExceeded):
        c.get_session("equity", date(2026, 1, 2))


def test_every_holiday_and_special_session_row_lies_inside_coverage() -> None:
    """Rows outside [COVERAGE_START, COVERAGE_END] would be silently unreachable."""
    import csv
    import importlib.resources

    from axiom_data.calendar import COVERAGE_END, COVERAGE_START

    ref = importlib.resources.files("axiom_data.reference")
    for name in ("holidays.csv", "special_sessions.csv"):
        rows = list(csv.DictReader(ref.joinpath(name).read_text(encoding="utf-8").splitlines()))
        assert rows
        for r in rows:
            assert COVERAGE_START <= date.fromisoformat(r["date"]) <= COVERAGE_END, (name, r)
