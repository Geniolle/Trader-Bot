from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.providers.twelvedata import ProviderQuotaExceededError
from app.schemas.run import CandleResponse
from app.services.candle_cache_sync import CandleCacheSyncService
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.core.logging import get_logger

# Instancia o logger padrão do projeto
logger = get_logger(__name__)

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

    # O nosso logger vistoso para o Mercado!
    logger.info("###################################################################################")
    logger.info(f"📊 [MERCADO] A carregar gráfico -> Símbolo: {normalized_symbol} | TimeFrame: {normalized_timeframe}")
    logger.info(f"[CANDLES] INÍCIO | START_AT={start_at} | END_AT={end_at} | LIMIT={limit} | MODE={mode} | SYNC={sync}")

    session = SessionLocal()
    try:
        try:
            if sync:
                logger.info("[CANDLES] A chamar CandleCacheSyncService.ensure_range()")
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
                logger.info("[CANDLES] ensure_range() concluído sem exceção")
        except ProviderQuotaExceededError as exc:
            logger.warning("[CANDLES] ProviderQuotaExceededError capturada")
            logger.warning(f"[CANDLES] ERRO_QUOTA={exc}")

            cached_rows = CandleQueryRepository().list_by_filters(
                session=session,
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
            )

            logger.info(f"[CANDLES] CACHE_ROWS={len(cached_rows)}")

            if cached_rows:
                logger.info("📊 [MERCADO] A devolver cache local devido a limite da API")
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

            logger.error("[CANDLES] Sem cache local, a devolver HTTP 429 (Limite API Excedido)")
            raise HTTPException(status_code=429, detail=str(exc)) from exc

        logger.info("[CANDLES] A consultar base local após sync")
        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        logger.info(f"📊 [MERCADO] Gráfico carregado com sucesso: {len(rows)} velas encontradas.")

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
        logger.info("[CANDLES] FIM")
        logger.info("###################################################################################")
        session.close()