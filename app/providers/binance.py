import json
from datetime import datetime
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.settings import get_settings
from app.models.domain.candle import Candle
from app.providers.base import BaseMarketDataProvider


class BinanceProvider(BaseMarketDataProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    def provider_name(self) -> str:
        return "binance"

    def get_historical_candles(
        self,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
    ) -> list[Candle]:
        interval = self._map_timeframe_to_interval(timeframe)
        normalized_symbol = self._normalize_symbol(symbol)

        params = {
            "symbol": normalized_symbol,
            "interval": interval,
            "startTime": int(start_at.timestamp() * 1000),
            "endTime": int(end_at.timestamp() * 1000),
            "limit": 1000,
        }

        url = f"{self.settings.binance_base_url}/api/v3/klines?{urlencode(params)}"

        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Trader-Bot/1.0",
            },
        )

        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raw_body = exc.read().decode("utf-8", errors="replace")
            try:
                error_payload = json.loads(raw_body)
                message = error_payload.get("msg", raw_body)
                raise ValueError(
                    f"Binance HTTP error {exc.code}: {message}"
                ) from exc
            except json.JSONDecodeError:
                raise ValueError(
                    f"Binance HTTP error {exc.code}: {raw_body}"
                ) from exc
        except URLError as exc:
            raise ValueError(f"Binance network error: {exc.reason}") from exc

        if not isinstance(payload, list):
            raise ValueError("Unexpected Binance response format")

        candles: list[Candle] = []

        for item in payload:
            if not isinstance(item, list) or len(item) < 7:
                continue

            open_time = datetime.utcfromtimestamp(item[0] / 1000)
            close_time = datetime.utcfromtimestamp(item[6] / 1000)

            candles.append(
                Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    open_time=open_time,
                    close_time=close_time,
                    open=Decimal(str(item[1])),
                    high=Decimal(str(item[2])),
                    low=Decimal(str(item[3])),
                    close=Decimal(str(item[4])),
                    volume=Decimal(str(item[5])),
                    source=self.provider_name(),
                )
            )

        return candles

    def _normalize_symbol(self, symbol: str) -> str:
        return (
            symbol.replace("/", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
            .upper()
        )

    def _map_timeframe_to_interval(self, timeframe: str) -> str:
        mapping = {
            "1m": "1m",
            "3m": "3m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "2h": "2h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w",
            "1mo": "1M",
        }

        if timeframe not in mapping:
            raise ValueError(f"Unsupported timeframe for Binance: {timeframe}")

        return mapping[timeframe]