from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.schemas.run import CandleResponse
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository

router = APIRouter(prefix="/candles", tags=["candles"])


def _build_candle_response(row) -> CandleResponse:
    return CandleResponse(
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


def _normalize_provider(provider: str | None) -> str:
    settings = get_settings()
    resolved = (provider or settings.market_data_provider or "mock").strip().lower()

    if not resolved:
        return "mock"

    return resolved


def _timeframe_to_delta(timeframe: str) -> timedelta:
    mapping = {
        "1m": timedelta(minutes=1),
        "3m": timedelta(minutes=3),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "45m": timedelta(minutes=45),
        "1h": timedelta(hours=1),
        "2h": timedelta(hours=2),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
        "1w": timedelta(weeks=1),
        "1mo": timedelta(days=30),
    }

    delta = mapping.get(timeframe)
    if delta is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported timeframe: {timeframe}",
        )

    return delta


def _resolve_range(
    *,
    timeframe: str,
    mode: str,
    start_at: datetime | None,
    end_at: datetime | None,
    limit: int,
) -> tuple[datetime, datetime]:
    now = datetime.utcnow()
    delta = _timeframe_to_delta(timeframe)

    normalized_mode = (mode or "full").strip().lower()

    if normalized_mode == "incremental":
        resolved_end = end_at or now
        resolved_start = start_at or (resolved_end - (delta * 3))

        if resolved_start >= resolved_end:
            resolved_start = resolved_end - (delta * 3)

        return resolved_start, resolved_end

    resolved_end = end_at or now
    bars = max(limit, 300)
    resolved_start = start_at or (resolved_end - (delta * bars))

    if resolved_start >= resolved_end:
        resolved_start = resolved_end - (delta * bars)

    return resolved_start, resolved_end


def _sync_candles_if_needed(
    *,
    session,
    provider_name: str,
    symbol: str,
    timeframe: str,
    start_at: datetime,
    end_at: datetime,
) -> None:
    settings = get_settings()

    if not settings.candle_cache_enabled:
        return

    if not settings.candle_cache_sync_on_read:
        return

    if start_at >= end_at:
        return

    try:
        market_provider = MarketDataProviderFactory().get_provider(provider_name)
    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Provider not found: {provider_name}",
        ) from exc

    try:
        candles = market_provider.get_historical_candles(
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Provider sync failed for {provider_name}: {exc}",
        ) from exc

    if not candles:
        return

    CandleRepository().save_many(session=session, candles=candles)


@router.get("", response_model=list[CandleResponse])
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    provider: str | None = Query(default=None),
    mode: str = Query(default="full"),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
) -> list[CandleResponse]:
    session = SessionLocal()
    try:
        provider_name = _normalize_provider(provider)
        resolved_start_at, resolved_end_at = _resolve_range(
            timeframe=timeframe,
            mode=mode,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        _sync_candles_if_needed(
            session=session,
            provider_name=provider_name,
            symbol=symbol,
            timeframe=timeframe,
            start_at=resolved_start_at,
            end_at=resolved_end_at,
        )

        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=resolved_start_at,
            end_at=resolved_end_at,
            limit=limit,
            source=provider_name,
        )

        return [_build_candle_response(row) for row in rows]
    finally:
        session.close()


@router.get("/latest", response_model=CandleResponse)
def get_latest_candle(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    provider: str | None = Query(default=None),
) -> CandleResponse:
    session = SessionLocal()
    try:
        provider_name = _normalize_provider(provider)
        settings = get_settings()

        timeframe_delta = _timeframe_to_delta(timeframe)
        reconcile_bars = max(settings.candle_cache_reconcile_bars, 3)
        sync_end_at = datetime.utcnow()
        sync_start_at = sync_end_at - (timeframe_delta * reconcile_bars)

        _sync_candles_if_needed(
            session=session,
            provider_name=provider_name,
            symbol=symbol,
            timeframe=timeframe,
            start_at=sync_start_at,
            end_at=sync_end_at,
        )

        row = CandleQueryRepository().get_latest(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            source=provider_name,
        )

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No candle found for symbol={symbol}, "
                    f"timeframe={timeframe}, provider={provider_name}"
                ),
            )

        return _build_candle_response(row)
    finally:
        session.close()