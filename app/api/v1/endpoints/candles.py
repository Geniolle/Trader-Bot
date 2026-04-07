# app/api/v1/endpoints/candles.py

from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.schemas.run import CandleResponse
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository

router = APIRouter(prefix="/candles", tags=["candles"])


def _map_rows_to_response(rows) -> list[CandleResponse]:
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


def _map_domain_candles_to_response(candles) -> list[CandleResponse]:
    return [
        CandleResponse(
            id=getattr(candle, "id", None),
            asset_id=candle.asset_id,
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            open_time=candle.open_time,
            close_time=candle.close_time,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
            source=candle.source,
        )
        for candle in candles
    ]


@router.get("", response_model=list[CandleResponse])
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    limit: int = Query(default=500, ge=1, le=5000),
    mode: str | None = Query(default="full"),
) -> list[CandleResponse]:
    session = SessionLocal()
    try:
        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        if rows:
            return _map_rows_to_response(rows)

        settings = get_settings()

        try:
            provider = MarketDataProviderFactory().get_provider(
                settings.market_data_provider
            )
            candles = provider.get_historical_candles(
                symbol=symbol,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
            )
        except KeyError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter candles do provider: {exc}",
            ) from exc

        if not candles:
            return []

        CandleRepository().save_many(session, candles)

        rows_after_save = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        if rows_after_save:
            return _map_rows_to_response(rows_after_save)

        return _map_domain_candles_to_response(candles[:limit])
    finally:
        session.close()