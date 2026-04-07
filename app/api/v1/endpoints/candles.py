from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.providers.twelvedata import ProviderQuotaExceededError
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
    normalized_symbol = symbol.strip().upper()
    normalized_timeframe = timeframe.strip().lower()

    session = SessionLocal()
    try:
        try:
            if sync:
                CandleCacheSyncService().ensure_range(
                    session=session,
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    start_at=start_at,
                    end_at=end_at,
                )
        except ProviderQuotaExceededError as exc:
            cached_rows = CandleQueryRepository().list_by_filters(
                session=session,
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
            )

            if cached_rows:
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
                    for row in cached_rows
                ]

            raise HTTPException(status_code=429, detail=str(exc)) from exc

        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
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