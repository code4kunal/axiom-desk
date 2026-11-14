"""Point-in-time reference data engine (KTD2).

One effective-dated row shape, two timestamps, one lookup primitive:
- effective_from (inclusive) and effective_to (exclusive, open when null)
- published_at: when the source made the fact public (circular date, announcement time, etc.)
- recorded_at: when the row entered Axiom
- source and licence_scope (KTD7)
- verified_against (KTD9)

The primitive resolves (key, on): among rows in force on `on` with published_at
no later than the end of `on` in IST, the latest recorded_at wins.
"""

import csv
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta, timezone
from io import StringIO
from typing import Any

from axiom_core.authz import Refused
from axiom_core.envelope import Source

IST = timezone(timedelta(hours=5, minutes=30), name="IST")


class RuleUnknown(Refused):
    """Raised when no rule row is in force for the asked key and date (R9)."""

    def __init__(self, rule: str, on: date | str) -> None:
        super().__init__(f"rule unknown: {rule} on {on}")
        self.rule = rule
        self.on = on


class NaiveTimestampRefused(Refused):
    """Raised when a timestamp is naive (lacks tzinfo) (KTD5)."""

    def __init__(self, msg: str = "naive timestamp is refused") -> None:
        super().__init__(msg)


def ensure_utc_aware(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware and convert it to UTC."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise NaiveTimestampRefused("naive timestamp is refused")
    return dt.astimezone(UTC)


def end_of_day_ist_utc(d: date) -> datetime:
    """End of date in IST, normalized to UTC."""
    end_ist = datetime.combine(d, time.max, tzinfo=IST)
    return end_ist.astimezone(UTC)


@dataclass(frozen=True)
class EffectiveDatedRow:
    """Standard point-in-time effective-dated row (KTD2)."""

    key: str
    effective_from: date
    effective_to: date | None
    published_at: datetime
    recorded_at: datetime
    source: str
    licence_scope: str = "public"
    verified_against: str = ""
    payload: dict[str, Any] = field(default_factory=dict[str, Any])

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("source must be non-empty")
        if not self.licence_scope:
            raise ValueError("licence_scope must be non-empty")
        if self.effective_to is not None and self.effective_from >= self.effective_to:
            raise ValueError(
                f"effective_from ({self.effective_from}) must precede "
                f"effective_to ({self.effective_to})"
            )
        # Verify aware and normalize to UTC
        pub = ensure_utc_aware(self.published_at)
        rec = ensure_utc_aware(self.recorded_at)
        object.__setattr__(self, "published_at", pub)
        object.__setattr__(self, "recorded_at", rec)

    @property
    def is_verified(self) -> bool:
        return bool(self.verified_against.strip())


@dataclass(frozen=True)
class LookupResult[T]:
    """Result of a point-in-time lookup carrying rows, sources, and R10 limitations."""

    value: T
    rows: tuple[EffectiveDatedRow, ...]

    @property
    def is_verified(self) -> bool:
        return all(r.is_verified for r in self.rows)

    @property
    def limitations(self) -> tuple[str, ...]:
        return () if self.is_verified else ("unverified rule",)

    @property
    def sources(self) -> tuple[Source, ...]:
        seen: set[tuple[str, str]] = set()
        res: list[Source] = []
        for r in self.rows:
            item = (r.source, r.licence_scope)
            if item not in seen:
                seen.add(item)
                res.append(Source(name=r.source, licence_scope=r.licence_scope))
        return tuple(res)


def _ranges_overlap(f1: date, t1: date | None, f2: date, t2: date | None) -> bool:
    """Check if [f1, t1) and [f2, t2) overlap."""
    start = max(f1, f2)
    end = min(t1 or date.max, t2 or date.max)
    return start < end


class PointInTimeTable:
    """In-memory table of effective-dated rows for a given rule or dataset."""

    def __init__(self, name: str, rows: Iterable[EffectiveDatedRow] = ()) -> None:
        self.name = name
        self._rows: list[EffectiveDatedRow] = []
        self.load(rows)

    def load(self, rows: Iterable[EffectiveDatedRow]) -> None:
        new_rows = list(rows)
        # Validate that no two rows for the same key and same recorded_at overlap in [from, to)
        by_key_and_rec: dict[tuple[str, datetime], list[EffectiveDatedRow]] = {}
        for r in new_rows:
            key_rec = (r.key, r.recorded_at)
            by_key_and_rec.setdefault(key_rec, []).append(r)

        for (k, rec), group in by_key_and_rec.items():
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    r1 = group[i]
                    r2 = group[j]
                    if _ranges_overlap(
                        r1.effective_from, r1.effective_to, r2.effective_from, r2.effective_to
                    ):
                        raise ValueError(
                            f"overlapping rows for key {k!r} with same recorded_at "
                            f"{rec.isoformat()}: [{r1.effective_from}, {r1.effective_to}) and "
                            f"[{r2.effective_from}, {r2.effective_to})"
                        )
        self._rows.extend(new_rows)

    def resolve(self, key: str, on: date | datetime) -> LookupResult[EffectiveDatedRow]:
        """Resolve the row in force for (key, on) as of end of on in IST (KTD2)."""
        if isinstance(on, datetime):
            if on.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            on_date = on.astimezone(IST).date()
        else:
            on_date = on

        end_of_on_utc = end_of_day_ist_utc(on_date)

        # Filter: matching key, published by end of on in IST
        matching = [
            r
            for r in self._rows
            if r.key == key
            and r.published_at <= end_of_on_utc
            and r.effective_from <= on_date
            and (r.effective_to is None or on_date < r.effective_to)
        ]

        if not matching:
            raise RuleUnknown(self.name, on_date)

        # Pick latest recorded_at
        winner = max(matching, key=lambda r: r.recorded_at)
        return LookupResult(value=winner, rows=(winner,))


def parse_csv_rule_rows(
    csv_text_or_io: str | StringIO,
    *,
    key_field: str = "key",
    default_key: str | None = None,
) -> list[EffectiveDatedRow]:
    """Parse reference CSV rows with standard columns."""
    f = StringIO(csv_text_or_io) if isinstance(csv_text_or_io, str) else csv_text_or_io
    reader = csv.DictReader(f)
    rows: list[EffectiveDatedRow] = []

    for row in reader:
        key = row[key_field].strip() if key_field in row else (default_key or "")
        if not key:
            raise ValueError(f"missing key in row: {row}")

        eff_from = date.fromisoformat(row["effective_from"].strip())
        eff_to_str = row.get("effective_to", "").strip()
        eff_to = date.fromisoformat(eff_to_str) if eff_to_str else None

        pub_str = row["published_at"].strip()
        pub_dt = datetime.fromisoformat(pub_str)
        pub_dt = ensure_utc_aware(pub_dt)

        rec_str = row["recorded_at"].strip()
        rec_dt = datetime.fromisoformat(rec_str)
        rec_dt = ensure_utc_aware(rec_dt)

        source = row["source"].strip()
        licence_scope = row.get("licence_scope", "public").strip() or "public"
        verified_against = row.get("verified_against", "").strip()

        # Any extra fields go into payload
        std_fields = {
            key_field,
            "effective_from",
            "effective_to",
            "published_at",
            "recorded_at",
            "source",
            "licence_scope",
            "verified_against",
        }
        payload = {k: v.strip() for k, v in row.items() if k not in std_fields}

        rows.append(
            EffectiveDatedRow(
                key=key,
                effective_from=eff_from,
                effective_to=eff_to,
                published_at=pub_dt,
                recorded_at=rec_dt,
                source=source,
                licence_scope=licence_scope,
                verified_against=verified_against,
                payload=payload,
            )
        )
    return rows
