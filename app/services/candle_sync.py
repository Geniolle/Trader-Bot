# app/services/candle_sync.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from threading import Lock
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models.domain.candle import Candle
from app.providers.factory import MarketDataProviderFactory
from app.storage.models import CandleModel
from app.storage.repositories.candle_queries import CandleQueryRepository


@dataclass
class CandleSyncResult:
    candles: list[Candle]
    source: str
    cache_hit: bool
    db_hit: bool
    provider_hit: bool
    missing_filled: bool
    requested_start_at: datetime
    requested_end_at: datetime
    newly_persisted_count: int


class CandleSyncService:
    _memory_cache: dict[str, tuple[datetime, list[Candle]]] = {}
    _rate_limit_until: datetime | None = None
    _lock = Lock()

    def __init__(self) -> None:
        self.settings = get_settings()
        self.query_repo = CandleQueryRepository()
        self.provider_factory = MarketDataProviderFactory()

    def get_or_sync_candles(
        self,
        *,
        session: Session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
        market_type: str | None = None,
        catalog: str | None = None,
    ) -> CandleSyncResult:
        normalized_symbol = symbol.strip().upper()
        normalized_timeframe = timeframe.strip().lower()
        requested_start_at = self._ensure_naive_utc(start_at)
        requested_end_at = self._ensure_naive_utc(end_at)

        cache_key = self._build_cache_key(
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=requested_start_at,
            end_at=requested_end_at,
        )

        cached = self._get_memory_cache(cache_key)
        if cached is not None:
            return CandleSyncResult(
                candles=cached,
                source="memory_cache",
                cache_hit=True,
                db_hit=False,
                provider_hit=False,
                missing_filled=False,
                requested_start_at=requested_start_at,
                requested_end_at=requested_end_at,
                newly_persisted_count=0,
            )

        local_candles = self._load_local_candles(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=requested_start_at,
            end_at=requested_end_at,
        )

        if self._has_sufficient_local_coverage(
            candles=local_candles,
            timeframe=normalized_timeframe,
            start_at=requested_start_at,
            end_at=requested_end_at,
        ):
            self._set_memory_cache(cache_key, local_candles)
            return CandleSyncResult(
                candles=local_candles,
                source="database",
                cache_hit=False,
                db_hit=True,
                provider_hit=False,
                missing_filled=False,
                requested_start_at=requested_start_at,
                requested_end_at=requested_end_at,
                newly_persisted_count=0,
            )

        if self._is_rate_limited():
            return CandleSyncResult(
                candles=local_candles,
                source="database_rate_limited",
                cache_hit=False,
                db_hit=bool(local_candles),
                provider_hit=False,
                missing_filled=False,
                requested_start_at=requested_start_at,
                requested_end_at=requested_end_at,
                newly_persisted_count=0,
            )

        provider = self.provider_factory.get_provider(self.settings.market_data_provider)

        provider_symbol = self._map_symbol_for_provider(
            symbol=normalized_symbol,
            market_type=market_type,
            catalog=catalog,
        )

        fetch_start_at = requested_start_at
        if local_candles:
            last_close_time = max(self._ensure_naive_utc(item.close_time) for item in local_candles)
            overlap = self._timeframe_delta(normalized_timeframe) * 2
            fetch_start_at = max(requested_start_at, last_close_time - overlap)

        fetched = provider.get_historical_candles(
            symbol=provider_symbol,
            timeframe=normalized_timeframe,
            start_at=fetch_start_at,
            end_at=requested_end_at,
        )

        normalized_fetched = [
            self._normalize_provider_candle(
                candle=item,
                original_symbol=normalized_symbol,
                timeframe=normalized_timeframe,
            )
            for item in fetched
        ]

        newly_persisted_count = self._persist_candles(
            session=session,
            candles=normalized_fetched,
        )

        final_candles = self._load_local_candles(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=requested_start_at,
            end_at=requested_end_at,
        )

        self._set_memory_cache(cache_key, final_candles)

        return CandleSyncResult(
            candles=final_candles,
            source=provider.provider_name(),
            cache_hit=False,
            db_hit=bool(local_candles),
            provider_hit=True,
            missing_filled=newly_persisted_count > 0,
            requested_start_at=requested_start_at,
            requested_end_at=requested_end_at,
            newly_persisted_count=newly_persisted_count,
        )

    def notify_rate_limit(self, cooldown_seconds: int = 300) -> None:
        with self._lock:
            self.__class__._rate_limit_until = datetime.now(timezone.utc) + timedelta(
                seconds=cooldown_seconds
            )

    def _is_rate_limited(self) -> bool:
        with self._lock:
            until = self.__class__._rate_limit_until
            if until is None:
                return False
            if datetime.now(timezone.utc) >= until:
                self.__class__._rate_limit_until = None
                return False
            return True

    def _build_cache_key(
        self,
        *,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> str:
        return f"{symbol}|{timeframe}|{start_at.isoformat()}|{end_at.isoformat()}"

    def _get_memory_cache(self, key: str) -> list[Candle] | None:
        with self._lock:
            item = self.__class__._memory_cache.get(key)
            if item is None:
                return None

            expires_at, candles = item
            if datetime.now(timezone.utc) >= expires_at:
                self.__class__._memory_cache.pop(key, None)
                return None

            return candles

    def _set_memory_cache(self, key: str, candles: list[Candle]) -> None:
        ttl_seconds = 20
        with self._lock:
            self.__class__._memory_cache[key] = (
                datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
                candles,
            )

    def _load_local_candles(
        self,
        *,
        session: Session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Candle]:
        rows = self.query_repo.list_by_symbol_timeframe_range(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
        )

        candles: list[Candle] = []
        for row in rows:
            candles.append(
                Candle(
                    asset_id=row.asset_id,
                    symbol=row.symbol,
                    timeframe=row.timeframe,
                    open_time=row.open_time,
                    close_time=row.close_time,
                    open=Decimal(str(row.open)),
                    high=Decimal(str(row.high)),
                    low=Decimal(str(row.low)),
                    close=Decimal(str(row.close)),
                    volume=Decimal(str(row.volume)),
                    source=row.source,
                )
            )

        return candles

    def _persist_candles(self, *, session: Session, candles: list[Candle]) -> int:
        persisted = 0

        for candle in candles:
            row = CandleModel(
                asset_id=candle.asset_id,
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                open_time=self._ensure_naive_utc(candle.open_time),
                close_time=self._ensure_naive_utc(candle.close_time),
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                source=candle.source,
            )
            session.add(row)

            try:
                session.commit()
                persisted += 1
            except IntegrityError:
                session.rollback()

        return persisted

    def _normalize_provider_candle(
        self,
        *,
        candle: Candle,
        original_symbol: str,
        timeframe: str,
    ) -> Candle:
        return Candle(
            asset_id=candle.asset_id,
            symbol=original_symbol,
            timeframe=timeframe,
            open_time=self._ensure_naive_utc(candle.open_time),
            close_time=self._ensure_naive_utc(candle.close_time),
            open=Decimal(str(candle.open)),
            high=Decimal(str(candle.high)),
            low=Decimal(str(candle.low)),
            close=Decimal(str(candle.close)),
            volume=Decimal(str(candle.volume)),
            source=candle.source,
        )

    def _has_sufficient_local_coverage(
        self,
        *,
        candles: list[Candle],
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> bool:
        if not candles:
            return False

        first_open = min(self._ensure_naive_utc(item.open_time) for item in candles)
        last_close = max(self._ensure_naive_utc(item.close_time) for item in candles)
        tolerance = self._timeframe_delta(timeframe) * 2

        return first_open <= start_at + tolerance and last_close >= end_at - tolerance

    def _timeframe_delta(self, timeframe: str) -> timedelta:
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
        return mapping.get(timeframe, timedelta(minutes=5))

    def _map_symbol_for_provider(
        self,
        *,
        symbol: str,
        market_type: str | None,
        catalog: str | None,
    ) -> str:
        market_type_value = (market_type or "").strip().lower()
        catalog_value = (catalog or "").strip().lower()

        if market_type_value == "forex":
            if "/" in symbol:
                return symbol
            if len(symbol) == 6:
                return f"{symbol[:3]}/{symbol[3:]}"
            return symbol

        if market_type_value in {"cripto", "crypto"}:
            if catalog_value == "spot":
                if symbol.endswith("USDT") and len(symbol) > 4:
                    return f"{symbol[:-4]}/USDT"
                if symbol.endswith("USD") and len(symbol) > 3:
                    return f"{symbol[:-3]}/USD"

        return symbol

    def _ensure_naive_utc(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)