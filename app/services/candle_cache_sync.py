from __future__ import annotations

from app.core.logging import get_logger
from app.storage.cache_models import CandleCoverageModel

logger = get_logger(__name__)


class CandleCacheSyncService:
    def __init__(self) -> None:
        logger.info("###################################################################################")
        logger.info("[CANDLE_CACHE_SYNC] INIT")
        logger.info(
            "[CANDLE_CACHE_SYNC] COVERAGE_MODEL=%s",
            CandleCoverageModel.__name__,
        )
        logger.info(
            "[CANDLE_CACHE_SYNC] COVERAGE_TABLE=%s",
            getattr(CandleCoverageModel, "__tablename__", "N/A"),
        )
        logger.info("###################################################################################")

    def ensure_range(
        self,
        symbol,
        timeframe,
        start_at,
        end_at,
        limit=5000,
        sync=True,
    ):
        logger.info("###################################################################################")
        logger.info("[CANDLE_CACHE_SYNC] INICIO")
        logger.info("[CANDLE_CACHE_SYNC] SYMBOL=%s", symbol)
        logger.info("[CANDLE_CACHE_SYNC] TIMEFRAME=%s", timeframe)
        logger.info("[CANDLE_CACHE_SYNC] START_AT=%s", start_at)
        logger.info("[CANDLE_CACHE_SYNC] END_AT=%s", end_at)
        logger.info("[CANDLE_CACHE_SYNC] LIMIT=%s", limit)
        logger.info("[CANDLE_CACHE_SYNC] SYNC=%s", sync)
        logger.info("[CANDLE_CACHE_SYNC] MODEL=%s", CandleCoverageModel.__name__)
        logger.info(
            "[CANDLE_CACHE_SYNC] TABLE=%s",
            getattr(CandleCoverageModel, "__tablename__", "N/A"),
        )

        # Mantém aqui a tua lógica real existente
        logger.info("[CANDLE_CACHE_SYNC] FIM")
        logger.info("###################################################################################")