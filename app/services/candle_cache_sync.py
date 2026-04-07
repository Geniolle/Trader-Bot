from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.storage.cache_models import CandleCoverageModel
from app.storage.models import CandleModel
from app.storage.repositories.candle_coverages import CandleCoverageRepository
from app.storage.repositories.candle_upserts import CandleUpsertRepository


@dataclass(frozen=True)
class SyncRange:
    start_at: datetime
    end_at: datetime


class CandleCacheSyncService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.provider_factory = MarketDataProviderFactory()
        self.coverage_repo = CandleCoverageRepository()
        self.upsert_repo = CandleUpsertRepository()

    def ensure_range(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> dict:
        normalized_symbol = self._normalize_symbol(symbol)
        normalized_timeframe = self._normalize_timeframe(timeframe)

        if start_at >= end_at:
            return {
                "synced": False,
                "reason": "invalid_range",
                "ranges_requested": 0,
                "candles_written": 0,
            }

        if not self.settings.candle_cache_enabled:
            return {
                "synced": False,
                "reason": "cache_disabled",
                "ranges_requested": 0,
                "candles_written": 0,
            }

        coverage = self.coverage_repo.get_by_symbol_timeframe(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
        )

        ranges = self._build_sync_ranges(
            coverage=coverage,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
        )

        if not ranges:
            return {
                "synced": False,
                "reason": "cache_hit",
                "ranges_requested": 0,
                "candles_written": 0,
            }

        provider = self.provider_factory.get_provider(self.settings.market_data_provider)
        total_written = 0

        try:
            for sync_range in ranges:
                candles = provider.get_historical_candles(
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    start_at=sync_range.start_at,
                    end_at=sync_range.end_at,
                )

                if candles:
                    total_written += self.upsert_repo.upsert_many(
                        session=session,
                        candles=candles,
                    )

                self.coverage_repo.upsert_coverage(
                    session=session,
                    symbol=normalized_symbol,
                    timeframe=normalized_timeframe,
                    covered_from=sync_range.start_at,
                    covered_to=sync_range.end_at,
                    provider_name=provider.provider_name(),
                )

            session.commit()

            return {
                "synced": True,
                "reason": "provider_sync",
                "ranges_requested": len(ranges),
                "candles_written": total_written,
            }
        except Exception as exc:
            session.rollback()

            has_local_rows = self._has_any_local_candles(
                session=session,
                symbol=normalized_symbol,
                timeframe=normalized_timeframe,
                start_at=start_at,
                end_at=end_at,
            )

            if has_local_rows:
                return {
                    "synced": False,
                    "reason": "provider_failed_using_local_cache",
                    "ranges_requested": len(ranges),
                    "candles_written": 0,
                    "error": str(exc),
                }

            raise

    def _build_sync_ranges(
        self,
        coverage: CandleCoverageModel | None,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[SyncRange]:
        if coverage is None or coverage.covered_from is None or coverage.covered_to is None:
            return [SyncRange(start_at=start_at, end_at=end_at)]

        ranges: list[SyncRange] = []

        if start_at < coverage.covered_from:
            ranges.append(
                SyncRange(
                    start_at=start_at,
                    end_at=min(end_at, coverage.covered_from),
                )
            )

        if end_at > coverage.covered_to:
            ranges.append(
                SyncRange(
                    start_at=max(start_at, coverage.covered_to),
                    end_at=end_at,
                )
            )

        reconcile_bars = max(self.settings.candle_cache_reconcile_bars, 0)
        if reconcile_bars > 0 and end_at >= coverage.covered_to:
            delta = self._timeframe_to_timedelta(timeframe)
            reconcile_start = max(
                start_at,
                coverage.covered_to - (delta * reconcile_bars),
            )
            ranges.append(
                SyncRange(
                    start_at=reconcile_start,
                    end_at=end_at,
                )
            )

        return self._merge_ranges(ranges)

    def _merge_ranges(self, ranges: list[SyncRange]) -> list[SyncRange]:
        valid_ranges = [
            item
            for item in ranges
            if item.start_at < item.end_at
        ]

        if not valid_ranges:
            return []

        valid_ranges.sort(key=lambda item: item.start_at)

        merged: list[SyncRange] = [valid_ranges[0]]

        for current in valid_ranges[1:]:
            last = merged[-1]

            if current.start_at <= last.end_at:
                merged[-1] = SyncRange(
                    start_at=last.start_at,
                    end_at=max(last.end_at, current.end_at),
                )
                continue

            merged.append(current)

        return merged

    def _has_any_local_candles(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> bool:
        row = (
            session.query(CandleModel.id)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time >= start_at,
                CandleModel.close_time <= end_at,
            )
            .first()
        )
        return row is not None

    def _normalize_symbol(self, value: str) -> str:
        return value.strip().upper()

    def _normalize_timeframe(self, value: str) -> str:
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

    def _timeframe_to_timedelta(self, timeframe: str) -> timedelta:
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
        }

        if timeframe in mapping:
            return mapping[timeframe]

        if timeframe == "1mo":
            return timedelta(days=30)

        return timedelta(minutes=1)