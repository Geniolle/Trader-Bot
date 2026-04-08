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

    print("###################################################################################")
    print("[CANDLES] INICIO")
    print(f"[CANDLES] SYMBOL={normalized_symbol}")
    print(f"[CANDLES] TIMEFRAME={normalized_timeframe}")
    print(f"[CANDLES] START_AT={start_at}")
    print(f"[CANDLES] END_AT={end_at}")
    print(f"[CANDLES] LIMIT={limit}")
    print(f"[CANDLES] MODE={mode}")
    print(f"[CANDLES] SYNC={sync}")

    session = SessionLocal()
    try:
        try:
            if sync:
                print("[CANDLES] A chamar CandleCacheSyncService.ensure_range()")
                CandleCacheSyncService().ensure_range(
                    session=session,
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    start_at=start_at,
                    end_at=end_at,
                    limit=limit,
                    sync=sync,
                    mode=mode,
                )
                print("[CANDLES] ensure_range() concluído sem exceção")
        except ProviderQuotaExceededError as exc:
            print("[CANDLES] ProviderQuotaExceededError capturada")
            print(f"[CANDLES] ERRO_QUOTA={exc}")

            cached_rows = CandleQueryRepository().list_by_filters(
                session=session,
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
            )

            print(f"[CANDLES] CACHE_ROWS={len(cached_rows)}")

            if cached_rows:
                print("[CANDLES] A devolver cache local")
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

            print("[CANDLES] Sem cache local, a devolver HTTP 429")
            raise HTTPException(status_code=429, detail=str(exc)) from exc

        print("[CANDLES] A consultar base local após sync")
        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        print(f"[CANDLES] ROWS_FINAL={len(rows)}")

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
        print("[CANDLES] FIM")
        print("###################################################################################")
        session.close()