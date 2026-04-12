# app/api/v1/endpoints/candles.py

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.core.logging import get_logger
from app.providers.twelvedata import ProviderQuotaExceededError
from app.schemas.run import CandleResponse
from app.services.candle_cache_sync import CandleCacheSyncService
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository

logger = get_logger(__name__)

router = APIRouter(prefix="/candles", tags=["candles"])


def timeframe_to_minimum_candles(timeframe: str) -> int:
    normalized = (timeframe or "").strip().lower()

    if normalized in {"1m", "3m", "5m"}:
        return 30
    if normalized in {"15m", "30m"}:
        return 20
    if normalized == "1h":
        return 12
    if normalized == "4h":
        return 8
    if normalized == "1d":
        return 5

    return 10


def timeframe_to_minutes(timeframe: str) -> int:
    normalized = (timeframe or "").strip().lower()

    if normalized == "1m":
        return 1
    if normalized == "3m":
        return 3
    if normalized == "5m":
        return 5
    if normalized == "15m":
        return 15
    if normalized == "30m":
        return 30
    if normalized == "1h":
        return 60
    if normalized == "4h":
        return 240
    if normalized == "1d":
        return 1440

    return 5


def rows_to_response(rows: list) -> list[CandleResponse]:
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


def load_local_rows(
    *,
    session,
    symbol: str,
    timeframe: str,
    start_at: datetime,
    end_at: datetime,
    limit: int,
) -> list:
    return CandleQueryRepository().list_by_filters(
        session=session,
        symbol=symbol,
        timeframe=timeframe,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )


def load_best_local_rows(
    *,
    session,
    symbol: str,
    timeframe: str,
    start_at: datetime,
    end_at: datetime,
    limit: int,
) -> list:
    minimum_candles = timeframe_to_minimum_candles(timeframe)
    timeframe_minutes = timeframe_to_minutes(timeframe)

    requested_rows = load_local_rows(
        session=session,
        symbol=symbol,
        timeframe=timeframe,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )

    logger.info(
        "[CANDLES] LOCAL_RANGE_PRINCIPAL | COUNT=%s | MIN_REQUIRED=%s",
        len(requested_rows),
        minimum_candles,
    )

    if len(requested_rows) >= minimum_candles:
        return requested_rows

    fallback_multipliers = [3, 6, 12, 24]
    best_rows = requested_rows

    for multiplier in fallback_multipliers:
        fallback_start = end_at - timedelta(
            minutes=timeframe_minutes * max(limit, minimum_candles) * multiplier
        )

        fallback_rows = load_local_rows(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=fallback_start,
            end_at=end_at,
            limit=limit,
        )

        logger.info(
            "[CANDLES] LOCAL_FALLBACK_RANGE | MULTIPLIER=%s | START_AT=%s | END_AT=%s | COUNT=%s",
            multiplier,
            fallback_start,
            end_at,
            len(fallback_rows),
        )

        if len(fallback_rows) > len(best_rows):
            best_rows = fallback_rows

        if len(best_rows) >= minimum_candles:
            logger.info(
                "[CANDLES] LOCAL_FALLBACK_SUCESSO | COUNT=%s | MIN_REQUIRED=%s",
                len(best_rows),
                minimum_candles,
            )
            return best_rows

    if best_rows:
        logger.warning(
            "[CANDLES] LOCAL_FALLBACK_PARCIAL | COUNT=%s | MIN_REQUIRED=%s",
            len(best_rows),
            minimum_candles,
        )
    else:
        logger.warning("[CANDLES] LOCAL_FALLBACK_SEM_DADOS")

    return best_rows


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
    minimum_candles = timeframe_to_minimum_candles(normalized_timeframe)

    logger.info(
        "###################################################################################"
    )
    logger.info(
        "📊 [MERCADO] A carregar gráfico -> Símbolo: %s | TimeFrame: %s",
        normalized_symbol,
        normalized_timeframe,
    )
    logger.info(
        "[CANDLES] INÍCIO | START_AT=%s | END_AT=%s | LIMIT=%s | MODE=%s | SYNC=%s | MIN_REQUIRED=%s",
        start_at,
        end_at,
        limit,
        mode,
        sync,
        minimum_candles,
    )

    session = SessionLocal()
    try:
        local_before_sync = load_best_local_rows(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        logger.info(
            "[CANDLES] LOCAL_BEFORE_SYNC | COUNT=%s",
            len(local_before_sync),
        )

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
            logger.warning("[CANDLES] ERRO_QUOTA=%s", exc)

            fallback_rows = local_before_sync or load_best_local_rows(
                session=session,
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=start_at,
                end_at=end_at,
                limit=limit,
            )

            logger.info(
                "[CANDLES] QUOTA_FALLBACK_LOCAL | COUNT=%s",
                len(fallback_rows),
            )

            if fallback_rows:
                logger.info(
                    "📊 [MERCADO] Provider sem quota. A devolver histórico local."
                )
                return rows_to_response(fallback_rows)

            logger.error(
                "[CANDLES] Sem histórico local, a devolver HTTP 429 (Limite API Excedido)"
            )
            raise HTTPException(status_code=429, detail=str(exc)) from exc

        logger.info("[CANDLES] A consultar base local após sync")
        rows_after_sync = load_best_local_rows(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        logger.info(
            "[CANDLES] LOCAL_AFTER_SYNC | COUNT=%s",
            len(rows_after_sync),
        )

        if rows_after_sync:
            logger.info(
                "📊 [MERCADO] Gráfico carregado com sucesso: %s velas encontradas.",
                len(rows_after_sync),
            )
            return rows_to_response(rows_after_sync)

        if local_before_sync:
            logger.warning(
                "[CANDLES] Pós-sync sem dados suficientes. A devolver histórico local pré-sync | COUNT=%s",
                len(local_before_sync),
            )
            return rows_to_response(local_before_sync)

        logger.warning("[CANDLES] Sem velas disponíveis após sync e sem fallback local")
        return []

    finally:
        logger.info("[CANDLES] FIM")
        logger.info(
            "###################################################################################"
        )
        session.close()