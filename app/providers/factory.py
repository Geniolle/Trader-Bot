# app/providers/factory.py

from app.providers.base import BaseMarketDataProvider
from app.providers.mock import MockMarketDataProvider
from app.providers.twelvedata import TwelveDataProvider


class MarketDataProviderFactory:
    def __init__(self) -> None:
        self._providers: dict[str, type[BaseMarketDataProvider]] = {
            "mock": MockMarketDataProvider,
            "twelvedata": TwelveDataProvider,
        }

    def get_provider(self, provider_name: str) -> BaseMarketDataProvider:
        normalized_name = (provider_name or "").strip().lower()
        provider_class = self._providers.get(normalized_name)

        if provider_class is None:
            available = ", ".join(self.list_providers())
            raise KeyError(
                f"Provider not found: {provider_name}. Available providers: {available}"
            )

        return provider_class()

    def list_providers(self) -> list[str]:
        return sorted(self._providers.keys())