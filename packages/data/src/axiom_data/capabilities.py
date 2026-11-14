"""Registry capabilities for reference data, trading calendar, and F&O rules (U6).

Provides:
- instrument_lookup: point-in-time instrument identity, role and basket eligibility.
- trading_calendar: segment session status, holidays and adjacent sessions.
- fno_contract_rules: point-in-time contract rules, expiry weekdays, lot value and ban status.
"""

from datetime import date, datetime, time
from typing import Any

from axiom_core.authz import Action, NotFound
from axiom_core.envelope import HandlerResult, Source
from axiom_core.registry import ALL_BINDINGS, CallContext, Capability
from pydantic import BaseModel

from axiom_data.calendar import Session, TradingCalendar
from axiom_data.fno_rules import FnoRulesEngine
from axiom_data.instruments import InstrumentStore
from axiom_data.pointintime import IST, NaiveTimestampRefused


class InstrumentLookupInput(BaseModel):
    on: str
    symbol: str | None = None
    instrument_id: str | None = None
    purpose: str | None = None


def instrument_lookup(instruments: InstrumentStore) -> Capability:
    def handler(ctx: CallContext, inputs: InstrumentLookupInput) -> HandlerResult:
        on_date = date.fromisoformat(inputs.on)
        inst = None
        if inputs.instrument_id:
            inst = instruments.get_instrument(inputs.instrument_id)
        elif inputs.symbol:
            inst = instruments.resolve_identifier("symbol", inputs.symbol, on_date)
        else:
            raise ValueError("either symbol or instrument_id must be provided")

        if inst is None:
            target = inputs.symbol or inputs.instrument_id or ""
            raise NotFound("instrument", target)

        role_res = instruments.get_role(inst, on_date)
        elig_dict = None
        if inputs.purpose is not None:
            elig = instruments.check_eligibility(inst, inputs.purpose, on_date)
            elig_dict = {
                "status": elig.status,
                "condition": elig.condition,
                "reason": elig.reason,
                "suggestions": list(elig.suggestions),
            }

        value = {
            "identity": {
                "instrument_id": inst.instrument_id,
                "asset_class": inst.asset_class,
                "kind": inst.kind,
                "exchange": inst.exchange,
                "name": inst.name,
            },
            "role": role_res.role,
            "eligibility": elig_dict,
        }

        # Deduplicate sources preserving order
        raw_sources = [
            Source(inst.source, inst.licence_scope),
            Source(role_res.source, role_res.licence_scope),
        ]
        seen_s: set[tuple[str, str]] = set()
        uniq_sources: list[Source] = []
        for s in raw_sources:
            key_s = (s.name, s.licence_scope)
            if key_s not in seen_s:
                seen_s.add(key_s)
                uniq_sources.append(s)

        limitations = list(role_res.limitations)
        if not role_res.is_verified and "unverified rule" not in limitations:
            limitations.append("unverified rule")

        as_of = datetime.combine(on_date, time(23, 59, 59), tzinfo=IST)
        return HandlerResult(
            value=value,
            as_of=as_of,
            sources=tuple(uniq_sources),
            method="point-in-time instrument lookup",
            limitations=tuple(limitations),
        )

    return Capability(
        name="instrument_lookup",
        summary="Point-in-time instrument resolution, asset-class role and eligibility",
        inputs=InstrumentLookupInput,
        handler=handler,
        permission=Action.READ,
        bindings=ALL_BINDINGS,
        version="1",
        parity_inputs={"symbol": "SPX", "on": "2026-11-13", "purpose": "basket_member"},
    )


class TradingCalendarInput(BaseModel):
    segment: str
    on: str | None = None
    timestamp: str | None = None


def _format_session(s: Session | None) -> dict[str, Any] | None:
    if s is None:
        return None
    return {
        "start": s.start.isoformat(),
        "end": s.end.isoformat(),
        "is_regular": s.is_regular,
        "session_name": s.session_name,
    }


def trading_calendar(calendar: TradingCalendar) -> Capability:
    def handler(ctx: CallContext, inputs: TradingCalendarInput) -> HandlerResult:
        if inputs.timestamp is not None:
            ts = datetime.fromisoformat(inputs.timestamp)
            if ts.tzinfo is None:
                raise NaiveTimestampRefused("naive timestamp is refused")
            d = ts.astimezone(IST).date()
            ref_dt = ts
        elif inputs.on is not None:
            d = date.fromisoformat(inputs.on)
            ref_dt = datetime.combine(d, time(0, 0, 0), tzinfo=IST)
        else:
            raise ValueError("either 'on' or 'timestamp' must be provided")

        session = calendar.get_session(inputs.segment, d)
        is_trading_day = session is not None

        prev_session = calendar.previous_session(inputs.segment, ref_dt)
        if session is not None:
            next_session = calendar.next_session(inputs.segment, session.end)
        else:
            next_session = calendar.next_session(inputs.segment, ref_dt)

        value = {
            "segment": inputs.segment,
            "on": d.isoformat(),
            "is_trading_day": is_trading_day,
            "session": _format_session(session),
            "previous_session": _format_session(prev_session),
            "next_session": _format_session(next_session),
        }

        as_of = datetime.combine(d, time(23, 59, 59), tzinfo=IST)
        return HandlerResult(
            value=value,
            as_of=as_of,
            sources=(Source("exchange-calendar", "public"),),
            method="trading calendar lookup",
            limitations=(),
        )

    return Capability(
        name="trading_calendar",
        summary="Trading session status, holidays and adjacent sessions per segment",
        inputs=TradingCalendarInput,
        handler=handler,
        permission=Action.READ,
        bindings=ALL_BINDINGS,
        version="1",
        parity_inputs={"segment": "equity", "on": "2026-11-13"},
    )


class FnoContractRulesInput(BaseModel):
    exchange: str
    underlying: str
    on: str


def fno_contract_rules(rules: FnoRulesEngine) -> Capability:
    def handler(ctx: CallContext, inputs: FnoContractRulesInput) -> HandlerResult:
        on_date = date.fromisoformat(inputs.on)
        res = rules.get_contract_rules(inputs.exchange, inputs.underlying, on_date)
        value = {
            "exchange": res.exchange,
            "underlying": res.underlying,
            "on": res.on.isoformat(),
            "min_contract_value": res.min_contract_value,
            "weekly_eligible": res.weekly_eligible,
            "calendar_spread_benefit": res.calendar_spread_benefit,
            "expiry_weekdays": res.expiry_weekdays,
            "position_limit_rule": res.position_limit_rule,
            "is_banned": res.is_banned,
        }
        as_of = datetime.combine(res.on, time(23, 59, 59), tzinfo=IST)
        return HandlerResult(
            value=value,
            as_of=as_of,
            sources=res.sources,
            method="point-in-time F&O contract rules resolution",
            limitations=res.limitations,
        )

    return Capability(
        name="fno_contract_rules",
        summary="F&O contract rules, expiry cycle weekdays, lot value and ban status",
        inputs=FnoContractRulesInput,
        handler=handler,
        permission=Action.READ,
        bindings=ALL_BINDINGS,
        version="1",
        parity_inputs={"exchange": "NSE", "underlying": "NIFTY", "on": "2026-11-13"},
    )
