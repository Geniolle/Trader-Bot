from datetime import datetime

from fastapi import APIRouter, Query

from app.core.settings import get_settings
from app.schemas.run import CandleResponse
from app.services.candle_cache_sync import CandleCacheSyncService
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository

router = APIRouter(prefix="/candles", tags=["candles"])


@router.get("", response_model=list[CandleResponse])
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    limit: int = Query(default=500, ge=1, le=5000),
    mode: str = Query(default="full"),
    sync: bool = Query(default=True),
) -> list[CandleResponse]:
    settings = get_settings()
    session = SessionLocal()

    try:
        if settings.candle_cache_enabled and settings.candle_cache_sync_on_read and sync:
            CandleCacheSyncService().ensure_range(
                session=session,
                symbol=symbol,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
            )

        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol.strip().upper(),
            timeframe=timeframe.strip().lower(),
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        return [
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
    finally:
        session.close()