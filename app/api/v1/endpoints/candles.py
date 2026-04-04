from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from app.schemas.run import CandleListResponse, CandleResponse
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository

router = APIRouter(prefix="/candles", tags=["candles"])


def normalize_timeframe(value: str) -> str:
    normalized = value.strip().lower()

    aliases = {
        "1min": "1m",
        "3min": "3m",
        "5min": "5m",
        "15min": "15m",
        "30min": "30m",
        "60min": "1h",
        "1hr": "1h",
        "4hr": "4h",
        "1day": "1d",
    }

    return aliases.get(normalized, normalized)


def timeframe_to_window(timeframe: str, mode: str) -> timedelta:
    normalized = normalize_timeframe(timeframe)

    if mode == "incremental":
        mapping = {
            "1m": timedelta(hours=2),
            "3m": timedelta(hours=4),
            "5m": timedelta(hours=6),
            "15m": timedelta(hours=12),
            "30m": timedelta(days=1),
            "1h": timedelta(days=2),
            "4h": timedelta(days=7),
            "1d": timedelta(days=30),
        }
        return mapping.get(normalized, timedelta(hours=6))

    mapping = {
        "1m": timedelta(days=1),
        "3m": timedelta(days=1),
        "5m": timedelta(days=1),
        "15m": timedelta(days=3),
        "30m": timedelta(days=3),
        "1h": timedelta(days=15),
        "4h": timedelta(days=15),
        "1d": timedelta(days=60),
    }
    return mapping.get(normalized, timedelta(days=15))


@router.get("", response_model=CandleListResponse)
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
    mode: str = Query(default="full", pattern="^(full|incremental)$"),
) -> CandleListResponse:
    session = SessionLocal()
    try:
        normalized_symbol = symbol.strip().upper()
        normalized_timeframe = normalize_timeframe(timeframe)

        effective_end_at = end_at or datetime.utcnow()

        if start_at is not None:
            effective_start_at = start_at
        else:
            effective_start_at = effective_end_at - timeframe_to_window(
                normalized_timeframe,
                mode,
            )

        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=effective_start_at,
            end_at=effective_end_at,
            limit=limit,
        )

        items = [
            CandleResponse(
                id=row.id,
                asset_id=row.asset_id,
                symbol=row.symbol,
                timeframe=row.timeframe,
                open_time=row.open_time,
                close_time=row.close_time,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
                source=row.source,
            )
            for row in rows
        ]

        first_open_time = items[0].open_time if items else None
        last_close_time = items[-1].close_time if items else None

        return CandleListResponse(
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            mode=mode,
            count=len(items),
            start_at=effective_start_at,
            end_at=effective_end_at,
            first_open_time=first_open_time,
            last_close_time=last_close_time,
            items=items,
        )
    finally:
        session.close()