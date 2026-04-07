from dataclasses import dataclass
from datetime import datetime

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository
from app.utils.datetime_utils import ensure_naive_utc, timeframe_to_timedelta


@dataclass
class CandleSyncResult:
    symbol: str
    timeframe: str
    used_provider: bool
    fetched_count: int
    reason: str


class CandleSyncService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.query_repository = CandleQueryRepository()
        self.write_repository = CandleRepository()

    def ensure_local_coverage(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
        provider_name: str | None = None,
    ) -> CandleSyncResult:
        normalized_symbol = symbol.strip().upper()
        normalized_timeframe = timeframe.strip().lower()
        normalized_start_at = ensure_naive_utc(start_at)
        normalized_end_at = ensure_naive_utc(end_at)

        rows = self.query_repository.list_by_symbol_timeframe_range(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=normalized_start_at,
            end_at=normalized_end_at,
        )

        latest_local = self.write_repository.get_latest(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
        )

        if rows and latest_local is not None:
            latest_local_close_time = ensure_naive_utc(latest_local.close_time)
            if latest_local_close_time >= normalized_end_at:
                return CandleSyncResult(
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    used_provider=False,
                    fetched_count=0,
                    reason="local_coverage_ok",
                )

        provider = MarketDataProviderFactory().get_provider(
            provider_name or self.settings.market_data_provider
        )

        if latest_local is None:
            bootstrap_limit = self._bootstrap_limit_for_timeframe(normalized_timeframe)
            bootstrap_start = max(
                normalized_start_at,
                normalized_end_at
                - (timeframe_to_timedelta(normalized_timeframe) * bootstrap_limit),
            )

            candles = provider.get_historical_candles(
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=bootstrap_start,
                end_at=normalized_end_at,
            )

            if candles:
                self.write_repository.save_many(session, candles)

            return CandleSyncResult(
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                used_provider=True,
                fetched_count=len(candles),
                reason="bootstrap_recent_window",
            )

        latest_close = ensure_naive_utc(latest_local.close_time)
        latest_open = ensure_naive_utc(latest_local.open_time)

        if latest_close >= normalized_end_at:
            return CandleSyncResult(
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                used_provider=False,
                fetched_count=0,
                reason="local_latest_already_current",
            )

        gap_start = latest_open
        gap_end = normalized_end_at

        missing_bars = self._count_bars_between(
            timeframe=normalized_timeframe,
            start_at=gap_start,
            end_at=gap_end,
        )

        if missing_bars <= 0:
            return CandleSyncResult(
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                used_provider=False,
                fetched_count=0,
                reason="nothing_to_sync",
            )

        max_gap_bars = max(10, self.settings.candles_gap_fill_max_bars)
        if missing_bars > max_gap_bars:
            gap_start = max(
                normalized_start_at,
                normalized_end_at
                - (timeframe_to_timedelta(normalized_timeframe) * max_gap_bars),
            )

        candles = provider.get_historical_candles(
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=gap_start,
            end_at=gap_end,
        )

        if candles:
            self.write_repository.save_many(session, candles)

        return CandleSyncResult(
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            used_provider=True,
            fetched_count=len(candles),
            reason="gap_fill",
        )

    def _bootstrap_limit_for_timeframe(self, timeframe: str) -> int:
        if timeframe in {"1d", "1w", "1mo"}:
            return max(10, self.settings.candles_bootstrap_limit_daily)
        return max(10, self.settings.candles_bootstrap_limit_intraday)

    def _count_bars_between(
        self,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> int:
        step = timeframe_to_timedelta(timeframe)
        seconds = max(0, int((end_at - start_at).total_seconds()))
        step_seconds = max(1, int(step.total_seconds()))
        return seconds // step_seconds