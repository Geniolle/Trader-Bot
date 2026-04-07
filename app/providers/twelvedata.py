# app/providers/twelvedata.py

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.settings import get_settings
from app.models.domain.candle import Candle
from app.providers.base import BaseMarketDataProvider

logger = logging.getLogger(__name__)


class TwelveDataProvider(BaseMarketDataProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def provider_name(self) -> str:
        return "twelvedata"

    def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Candle]:
        if not self.settings.twelvedata_api_key:
            raise ValueError("Twelve Data API key is not configured")

        provider_symbol = self._normalize_symbol_for_provider(symbol)
        interval = self._map_timeframe_to_interval(timeframe)

        logger.info(
            {
                "event": "twelvedata_request_debug",
                "original_symbol": symbol,
                "provider_symbol": provider_symbol,
                "timeframe": timeframe,
                "interval": interval,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
            }
        )

        params = {
            "symbol": provider_symbol,
            "interval": interval,
            "start_date": start_at.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end_at.strftime("%Y-%m-%d %H:%M:%S"),
            "outputsize": 5000,
            "order": "asc",
            "format": "JSON",
        }

        url = f"{self.settings.twelvedata_base_url}/time_series?{urlencode(params)}"

        request = Request(
            url,
            headers={
                "Authorization": f"apikey {self.settings.twelvedata_api_key}",
                "Accept": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/136.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "close",
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            logger.error(
                {
                    "event": "twelvedata_http_error",
                    "status_code": exc.code,
                    "symbol": symbol,
                    "provider_symbol": provider_symbol,
                    "timeframe": timeframe,
                    "raw_body": raw_body,
                }
            )
            try:
                error_payload = json.loads(raw_body)
                message = error_payload.get("message", raw_body)
                status = error_payload.get("status", "error")
                code = error_payload.get("code", exc.code)
                raise ValueError(
                    f"Twelve Data API error ({code}, {status}): {message}"
                ) from exc
            except json.JSONDecodeError:
                raise ValueError(
                    f"Twelve Data HTTP error {exc.code}: {raw_body}"
                ) from exc
        except URLError as exc:
            logger.error(
                {
                    "event": "twelvedata_network_error",
                    "symbol": symbol,
                    "provider_symbol": provider_symbol,
                    "timeframe": timeframe,
                    "reason": str(exc.reason),
                }
            )
            raise ValueError(f"Twelve Data network error: {exc.reason}") from exc

        if payload.get("status") == "error":
            message = payload.get("message", "Unknown Twelve Data API error")
            code = payload.get("code", "unknown")
            logger.error(
                {
                    "event": "twelvedata_api_error",
                    "symbol": symbol,
                    "provider_symbol": provider_symbol,
                    "timeframe": timeframe,
                    "code": code,
                    "message": message,
                }
            )
            raise ValueError(f"Twelve Data API error ({code}): {message}")

        values = payload.get("values", [])
        if not isinstance(values, list):
            raise ValueError("Unexpected Twelve Data response format")

        candles: list[Candle] = []
        for item in values:
            close_time = self._parse_twelvedata_datetime(item["datetime"])
            open_time = self._infer_open_time(close_time, timeframe)

            candles.append(
                Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    open_time=open_time,
                    close_time=close_time,
                    open=Decimal(item["open"]),
                    high=Decimal(item["high"]),
                    low=Decimal(item["low"]),
                    close=Decimal(item["close"]),
                    volume=Decimal(item.get("volume", "0") or "0"),
                    source=self.provider_name(),
                )
            )

        logger.info(
            {
                "event": "twelvedata_response_ok",
                "symbol": symbol,
                "provider_symbol": provider_symbol,
                "timeframe": timeframe,
                "candles_count": len(candles),
            }
        )

        return candles

    def _normalize_symbol_for_provider(self, symbol: str) -> str:
        normalized = symbol.strip().upper()

        if "/" in normalized:
            return normalized

        if len(normalized) == 6 and normalized.isalpha():
            return f"{normalized[:3]}/{normalized[3:]}"

        return normalized

    def _map_timeframe_to_interval(self, timeframe: str) -> str:
        mapping = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "45m": "45min",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "1d": "1day",
            "1w": "1week",
            "1mo": "1month",
        }

        if timeframe not in mapping:
            raise ValueError(f"Unsupported timeframe for Twelve Data: {timeframe}")

        return mapping[timeframe]

    def _parse_twelvedata_datetime(self, value: str) -> datetime:
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unsupported datetime format from Twelve Data: {value}")

    def _infer_open_time(self, close_time: datetime, timeframe: str) -> datetime:
        if timeframe == "1m":
            return close_time - timedelta(minutes=1)
        if timeframe == "5m":
            return close_time - timedelta(minutes=5)
        if timeframe == "15m":
            return close_time - timedelta(minutes=15)
        if timeframe == "30m":
            return close_time - timedelta(minutes=30)
        if timeframe == "45m":
            return close_time - timedelta(minutes=45)
        if timeframe == "1h":
            return close_time - timedelta(hours=1)
        if timeframe == "2h":
            return close_time - timedelta(hours=2)
        if timeframe == "4h":
            return close_time - timedelta(hours=4)
        if timeframe == "1d":
            return close_time - timedelta(days=1)
        if timeframe == "1w":
            return close_time - timedelta(weeks=1)
        if timeframe == "1mo":
            return close_time - timedelta(days=30)

        raise ValueError(f"Unsupported timeframe for open_time inference: {timeframe}")