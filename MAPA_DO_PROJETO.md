# MAPA DO PROJETO

- **Raiz analisada:** `G:/O meu disco/python/Trader-bot`
- **Gerado em:** 2026-04-16 13:14:39 UTC
- **Ficheiro de saída:** `MAPA_DO_PROJETO.md`
- **Total de ficheiros analisados:** 113

## Objetivo deste ficheiro

Este documento é reescrito automaticamente e tenta explicar o papel de cada ficheiro, as ligações internas, endpoints, integrações HTTP/WS e pontos de entrada do projeto.

## Estrutura de pastas analisadas

```text
├── app
│   ├── api
│   │   ├── routes
│   │   │   ├── __init__.py
│   │   │   ├── stage_tests.py
│   │   │   └── strategies.py
│   │   ├── v1
│   │   │   ├── endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── batch_runs.py
│   │   │   │   ├── candles.py
│   │   │   │   ├── catalog.py
│   │   │   │   ├── comparisons.py
│   │   │   │   ├── health.py
│   │   │   │   ├── providers.py
│   │   │   │   ├── run_cases.py
│   │   │   │   ├── run_details.py
│   │   │   │   ├── run_history.py
│   │   │   │   ├── run_metrics.py
│   │   │   │   ├── runs.py
│   │   │   │   ├── stage_tests.py
│   │   │   │   ├── strategies.py
│   │   │   │   └── ws.py
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   └── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── instrument_catalog.py
│   │   ├── logging.py
│   │   └── settings.py
│   ├── engine
│   │   ├── __init__.py
│   │   ├── case_engine.py
│   │   ├── metrics_engine.py
│   │   └── run_engine.py
│   ├── indicators
│   │   ├── __init__.py
│   │   ├── atr.py
│   │   ├── bollinger.py
│   │   ├── ema.py
│   │   ├── macd.py
│   │   ├── rsi.py
│   │   └── sma.py
│   ├── models
│   │   ├── domain
│   │   │   ├── __init__.py
│   │   │   ├── asset.py
│   │   │   ├── candle.py
│   │   │   ├── enums.py
│   │   │   ├── strategy_case.py
│   │   │   ├── strategy_config.py
│   │   │   ├── strategy_definition.py
│   │   │   ├── strategy_metrics.py
│   │   │   └── strategy_run.py
│   │   └── __init__.py
│   ├── providers
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── binance.py
│   │   ├── factory.py
│   │   ├── mock.py
│   │   └── twelvedata.py
│   ├── registry
│   │   ├── __init__.py
│   │   └── strategy_registry.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── batch_run.py
│   │   ├── catalog.py
│   │   ├── comparison.py
│   │   ├── provider.py
│   │   ├── run.py
│   │   ├── run_details.py
│   │   ├── stage_tests.py
│   │   └── strategy.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── candle_cache_sync.py
│   │   ├── candle_sync.py
│   │   ├── candlestick_confirmation.py
│   │   ├── candlestick_intelligence.py
│   │   ├── case_snapshot.py
│   │   ├── catalog_service.py
│   │   ├── comparison_service.py
│   │   ├── mock_market_data_service.py
│   │   ├── realtime_ws.py
│   │   └── stage_tests_service.py
│   ├── stage_tests
│   │   ├── catalog.py
│   │   ├── runner.py
│   │   └── strategy_mapper.py
│   ├── storage
│   │   ├── repositories
│   │   │   ├── candle_coverages.py
│   │   │   ├── candle_queries.py
│   │   │   ├── candle_repository.py
│   │   │   ├── candle_upserts.py
│   │   │   ├── case_queries.py
│   │   │   ├── case_repository.py
│   │   │   ├── comparison_queries.py
│   │   │   ├── metrics_queries.py
│   │   │   ├── metrics_repository.py
│   │   │   ├── run_queries.py
│   │   │   └── run_repository.py
│   │   ├── __init__.py
│   │   ├── cache_models.py
│   │   ├── database.py
│   │   └── models.py
│   ├── strategies
│   │   ├── __init__.py
│   │   ├── analysis_snapshot_builder.py
│   │   ├── base.py
│   │   ├── bollinger_reversal.py
│   │   ├── bollinger_walk_the_band.py
│   │   ├── catalog.py
│   │   ├── decisions.py
│   │   ├── ema_cross.py
│   │   ├── ff_fd.py
│   │   ├── ff_fd_mapper.py
│   │   └── rsi_reversal.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── datetime_utils.py
│   │   └── ids.py
│   ├── __init__.py
│   └── main.py
├── scripts
│   └── migrate_normalize_candles_symbols.py
├── tests
│   ├── test_comparisons.py
│   └── test_run_engine.py
├── gerar_mapa_projeto.py
└── gerar_mapa_projeto_v2.py
```

## Distribuição por linguagem

| Linguagem | Quantidade |
|---|---:|
| python | 113 |

## Distribuição por categoria

| Categoria | Quantidade |
|---|---:|
| api | 21 |
| config | 1 |
| engine | 5 |
| entrypoint | 1 |
| model | 10 |
| provider | 6 |
| repository | 11 |
| schema | 9 |
| service | 11 |
| source | 21 |
| storage | 4 |
| strategy | 13 |

## Pontos de maior impacto

- `app/models/domain/candle.py` | referenciado por `22` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/models/domain/enums.py` | referenciado por `16` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/core/settings.py` | referenciado por `14` ficheiro(s) | usa `0` ficheiro(s) | papel: Centraliza configurações e constantes
- `app/storage/models.py` | referenciado por `13` ficheiro(s) | usa `1` ficheiro(s) | papel: Lógica de suporte do projeto
- `app/models/domain/strategy_run.py` | referenciado por `13` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/models/domain/strategy_config.py` | referenciado por `13` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/storage/database.py` | referenciado por `12` ficheiro(s) | usa `1` ficheiro(s) | papel: Lógica de suporte do projeto
- `app/models/domain/strategy_case.py` | referenciado por `12` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/schemas/run.py` | referenciado por `10` ficheiro(s) | usa `3` ficheiro(s) | papel: Define contratos de dados e serialização
- `app/strategies/base.py` | referenciado por `9` ficheiro(s) | usa `6` ficheiro(s) | papel: Implementa regras de estratégia
- `app/strategies/decisions.py` | referenciado por `8` ficheiro(s) | usa `1` ficheiro(s) | papel: Implementa regras de estratégia
- `app/models/domain/strategy_definition.py` | referenciado por `7` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou persistência
- `app/providers/factory.py` | referenciado por `6` ficheiro(s) | usa `4` ficheiro(s) | papel: Integra fontes externas de dados
- `app/storage/repositories/candle_queries.py` | referenciado por `6` ficheiro(s) | usa `1` ficheiro(s) | papel: Lê ou grava dados na camada de persistência
- `app/indicators/bollinger.py` | referenciado por `5` ficheiro(s) | usa `1` ficheiro(s) | papel: Lógica de suporte do projeto

## Endpoints detectados

- `GET /api/stage-tests/options` → `app/api/routes/stage_tests.py` (get_stage_test_options)
- `POST /api/stage-tests/run` → `app/api/routes/stage_tests.py` (post_stage_test_run)
- `GET /strategies` → `app/api/routes/strategies.py` (list_strategies)
- `POST /batch-runs/historical` → `app/api/v1/endpoints/batch_runs.py` (run_batch_historical)
- `GET /candles` → `app/api/v1/endpoints/candles.py` (list_candles)
- `GET /candles/latest` → `app/api/v1/endpoints/candles.py` (get_latest_candle)
- `GET /catalog/products` → `app/api/v1/endpoints/catalog.py` (list_products)
- `GET /catalog/products/{product_code}` → `app/api/v1/endpoints/catalog.py` (get_product)
- `GET /catalog/products/{product_code}/subproducts/{subproduct_code}` → `app/api/v1/endpoints/catalog.py` (get_subproduct_items)
- `GET /comparisons/strategies` → `app/api/v1/endpoints/comparisons.py` (compare_strategies)
- `GET /health` → `app/api/v1/endpoints/health.py` (healthcheck)
- `GET /providers` → `app/api/v1/endpoints/providers.py` (list_providers)
- `GET /run-cases/{run_id}` → `app/api/v1/endpoints/run_cases.py` (list_run_cases)
- `GET /run-details/{run_id}` → `app/api/v1/endpoints/run_details.py` (get_run_details)
- `GET /run-history` → `app/api/v1/endpoints/run_history.py` (list_run_history)
- `DELETE /run-history` → `app/api/v1/endpoints/run_history.py` (clear_run_history)
- `GET /run-metrics/{run_id}` → `app/api/v1/endpoints/run_metrics.py` (get_run_metrics)
- `POST /run-metrics/{run_id}/recalculate` → `app/api/v1/endpoints/run_metrics.py` (recalculate_run_metrics)
- `POST /runs/historical` → `app/api/v1/endpoints/runs.py` (run_historical)
- `GET /options` → `app/api/v1/endpoints/stage_tests.py` (get_stage_test_options)
- `POST /run` → `app/api/v1/endpoints/stage_tests.py` (post_stage_test_run)
- `GET /strategies` → `app/api/v1/endpoints/strategies.py` (list_strategies)
- `WEBSOCKET /ws` → `app/api/v1/endpoints/ws.py` (websocket_feed)
- `GET /health` → `app/main.py` (health)

## Integrações HTTP detectadas

- `app/core/settings.py` → `https://api.binance.com`, `https://api.twelvedata.com`
- `app/main.py` → `http://127.0.0.1:5173`, `http://localhost:5173`

## Integrações WebSocket detectadas

- Nenhuma integração WebSocket detectada automaticamente.

## Mapa ficheiro a ficheiro

### `app/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/api/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/api/routes/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/api/routes/stage_tests.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1263 bytes
- **Linhas:** 38 totais | 33 não vazias | 0 comentários
- **Hash lógico:** `5e6918c9d4043979cb43f988fada1cbfe97ed7a0`
- **Funções principais:** `get_stage_test_options`, `post_stage_test_run`
- **Endpoints:** `GET /api/stage-tests/options` (get_stage_test_options); `POST /api/stage-tests/run` (post_stage_test_run)
- **Imports/refs brutas:** `app.schemas.stage_tests`, `app.services.stage_tests_service`, `fastapi`
- **Usa internamente:** `app/schemas/stage_tests.py`, `app/services/stage_tests_service.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /api/stage-tests/options, POST /api/stage-tests/run. Funções principais: get_stage_test_options, post_stage_test_run. Depende de: app/schemas/stage_tests.py, app/services/stage_tests_service.py.

### `app/api/routes/strategies.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 226 bytes
- **Linhas:** 12 totais | 7 não vazias | 1 comentários
- **Hash lógico:** `e5e58a9124cc01a0a72b0e2da2f0db5a0ff386f5`
- **Funções principais:** `list_strategies`
- **Endpoints:** `GET /strategies` (list_strategies)
- **Imports/refs brutas:** `...strategies.catalog`, `fastapi`
- **Usa internamente:** `app/strategies/catalog.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /strategies. Funções principais: list_strategies. Depende de: app/strategies/catalog.py.

### `app/api/v1/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/api/v1/endpoints/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/api/v1/endpoints/batch_runs.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 6014 bytes
- **Linhas:** 160 totais | 138 não vazias | 0 comentários
- **Hash lógico:** `0060d3f34b41a0eb195f0dae0b9d8e39920947bc`
- **Funções principais:** `_map_db_rows_to_domain_candles`, `run_batch_historical`
- **Endpoints:** `POST /batch-runs/historical` (run_batch_historical)
- **Imports/refs brutas:** `app.core.settings`, `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.providers.factory`, `app.registry.strategy_registry`, `app.schemas.batch_run`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.storage.repositories.case_repository`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_repository`, `app.utils.ids`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/providers/factory.py`, `app/registry/strategy_registry.py`, `app/schemas/batch_run.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_repository.py`, `app/utils/ids.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: POST /batch-runs/historical. Funções principais: _map_db_rows_to_domain_candles, run_batch_historical. Depende de: app/core/settings.py, app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/candles.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 6839 bytes
- **Linhas:** 237 totais | 194 não vazias | 0 comentários
- **Hash lógico:** `131d53d3b548d6cbddd6ad819da6ecad798cea5f`
- **Funções principais:** `_build_candle_response`, `_normalize_provider`, `_timeframe_to_delta`, `_resolve_range`, `_sync_candles_if_needed`, `list_candles`, `get_latest_candle`
- **Endpoints:** `GET /candles` (list_candles); `GET /candles/latest` (get_latest_candle)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `datetime`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /candles, GET /candles/latest. Funções principais: _build_candle_response, _normalize_provider, _timeframe_to_delta, _resolve_range, _sync_candles_if_needed, list_candles. Depende de: app/core/settings.py, app/providers/factory.py, app/schemas/run.py, app/storage/database.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/catalog.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1413 bytes
- **Linhas:** 52 totais | 39 não vazias | 0 comentários
- **Hash lógico:** `276d3261bedda55d69b98392a41a83ec39020d52`
- **Funções principais:** `list_products`, `get_product`, `get_subproduct_items`
- **Endpoints:** `GET /catalog/products` (list_products); `GET /catalog/products/{product_code}` (get_product); `GET /catalog/products/{product_code}/subproducts/{subproduct_code}` (get_subproduct_items)
- **Imports/refs brutas:** `app.schemas.catalog`, `app.services.catalog_service`, `fastapi`
- **Usa internamente:** `app/schemas/catalog.py`, `app/services/catalog_service.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /catalog/products, GET /catalog/products/{product_code}, GET /catalog/products/{product_code}/subproducts/{subproduct_code}. Funções principais: list_products, get_product, get_subproduct_items. Depende de: app/schemas/catalog.py, app/services/catalog_service.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/comparisons.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1093 bytes
- **Linhas:** 32 totais | 27 não vazias | 0 comentários
- **Hash lógico:** `75d81acb49dc35bbb997ee42337b2c1ca1eaa609`
- **Funções principais:** `compare_strategies`
- **Endpoints:** `GET /comparisons/strategies` (compare_strategies)
- **Imports/refs brutas:** `app.schemas.comparison`, `app.services.comparison_service`, `app.storage.database`, `app.storage.repositories.comparison_queries`, `fastapi`
- **Usa internamente:** `app/schemas/comparison.py`, `app/services/comparison_service.py`, `app/storage/database.py`, `app/storage/repositories/comparison_queries.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /comparisons/strategies. Funções principais: compare_strategies. Depende de: app/schemas/comparison.py, app/services/comparison_service.py, app/storage/database.py, app/storage/repositories/comparison_queries.py.

### `app/api/v1/endpoints/health.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 316 bytes
- **Linhas:** 16 totais | 11 não vazias | 0 comentários
- **Hash lógico:** `a22f579e6deceddfb54d2077185224ee87432f66`
- **Funções principais:** `healthcheck`
- **Endpoints:** `GET /health` (healthcheck)
- **Imports/refs brutas:** `app.core.settings`, `fastapi`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /health. Funções principais: healthcheck. Depende de: app/core/settings.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/providers.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 579 bytes
- **Linhas:** 18 totais | 13 não vazias | 0 comentários
- **Hash lógico:** `b5aa9fb8b29de75400a70dbe3ad8dc4a23308866`
- **Funções principais:** `list_providers`
- **Endpoints:** `GET /providers` (list_providers)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.schemas.provider`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/schemas/provider.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /providers. Funções principais: list_providers. Depende de: app/core/settings.py, app/providers/factory.py, app/schemas/provider.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/run_cases.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1708 bytes
- **Linhas:** 45 totais | 39 não vazias | 0 comentários
- **Hash lógico:** `d859a2ed24869447524b606fc8e915d6a7ae03cc`
- **Funções principais:** `list_run_cases`
- **Endpoints:** `GET /run-cases/{run_id}` (list_run_cases)
- **Imports/refs brutas:** `app.schemas.run`, `app.storage.database`, `app.storage.repositories.case_queries`, `fastapi`, `json`
- **Usa internamente:** `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /run-cases/{run_id}. Funções principais: list_run_cases. Depende de: app/schemas/run.py, app/storage/database.py, app/storage/repositories/case_queries.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/run_details.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 4210 bytes
- **Linhas:** 102 totais | 90 não vazias | 1 comentários
- **Hash lógico:** `e643d772542d301c3c234f843482fecae23c069e`
- **Funções principais:** `get_run_details`
- **Endpoints:** `GET /run-details/{run_id}` (get_run_details)
- **Imports/refs brutas:** `app.schemas.run`, `app.schemas.run_details`, `app.storage.database`, `app.storage.repositories.case_queries`, `app.storage.repositories.metrics_queries`, `app.storage.repositories.run_queries`, `fastapi`, `json`
- **Usa internamente:** `app/schemas/run.py`, `app/schemas/run_details.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /run-details/{run_id}. Funções principais: get_run_details. Depende de: app/schemas/run.py, app/schemas/run_details.py, app/storage/database.py, app/storage/repositories/case_queries.py, app/storage/repositories/metrics_queries.py, app/storage/repositories/run_queries.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/run_history.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 2524 bytes
- **Linhas:** 72 totais | 63 não vazias | 1 comentários
- **Hash lógico:** `460fb02f08c46d57d7faf8312a7647902f8ea053`
- **Funções principais:** `list_run_history`, `clear_run_history`
- **Endpoints:** `GET /run-history` (list_run_history); `DELETE /run-history` (clear_run_history)
- **Imports/refs brutas:** `app.schemas.run`, `app.storage.database`, `app.storage.models`, `app.storage.repositories.run_queries`, `fastapi`
- **Usa internamente:** `app/schemas/run.py`, `app/storage/database.py`, `app/storage/models.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /run-history, DELETE /run-history. Funções principais: list_run_history, clear_run_history. Depende de: app/schemas/run.py, app/storage/database.py, app/storage/models.py, app/storage/repositories/run_queries.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/run_metrics.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 5933 bytes
- **Linhas:** 143 totais | 124 não vazias | 0 comentários
- **Hash lógico:** `6e951e92e69d7849fe9da46a6c9638e612757207`
- **Funções principais:** `_map_case_row_to_domain`, `get_run_metrics`, `recalculate_run_metrics`
- **Endpoints:** `GET /run-metrics/{run_id}` (get_run_metrics); `POST /run-metrics/{run_id}/recalculate` (recalculate_run_metrics)
- **Imports/refs brutas:** `app.engine.metrics_engine`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.case_queries`, `app.storage.repositories.metrics_queries`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_queries`, `fastapi`, `json`
- **Usa internamente:** `app/engine/metrics_engine.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /run-metrics/{run_id}, POST /run-metrics/{run_id}/recalculate. Funções principais: _map_case_row_to_domain, get_run_metrics, recalculate_run_metrics. Depende de: app/engine/metrics_engine.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/schemas/run.py, app/storage/database.py, app/storage/repositories/case_queries.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/runs.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 8002 bytes
- **Linhas:** 208 totais | 182 não vazias | 0 comentários
- **Hash lógico:** `b0eada43b088e4a5d83b65c6c5517609b1d12283`
- **Funções principais:** `_map_db_rows_to_domain_candles`, `run_historical`
- **Endpoints:** `POST /runs/historical` (run_historical)
- **Imports/refs brutas:** `app.core.settings`, `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.providers.factory`, `app.registry.strategy_registry`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.storage.repositories.case_repository`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_repository`, `app.utils.ids`, `fastapi`, `logging`, `time`
- **Usa internamente:** `app/core/settings.py`, `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/providers/factory.py`, `app/registry/strategy_registry.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_repository.py`, `app/utils/ids.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: POST /runs/historical. Funções principais: _map_db_rows_to_domain_candles, run_historical. Depende de: app/core/settings.py, app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/stage_tests.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1370 bytes
- **Linhas:** 41 totais | 35 não vazias | 0 comentários
- **Hash lógico:** `bf59eddf8ed2c92dd41ce41ef9ac1eaa642eaa41`
- **Funções principais:** `get_stage_test_options`, `post_stage_test_run`
- **Endpoints:** `GET /options` (get_stage_test_options); `POST /run` (post_stage_test_run)
- **Imports/refs brutas:** `app.schemas.stage_tests`, `app.services.stage_tests_service`, `fastapi`
- **Usa internamente:** `app/schemas/stage_tests.py`, `app/services/stage_tests_service.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /options, POST /run. Funções principais: get_stage_test_options, post_stage_test_run. Depende de: app/schemas/stage_tests.py, app/services/stage_tests_service.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/strategies.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 576 bytes
- **Linhas:** 17 totais | 12 não vazias | 0 comentários
- **Hash lógico:** `cba81d9f1fab620400844a38bfbf0569206cc599`
- **Funções principais:** `list_strategies`
- **Endpoints:** `GET /strategies` (list_strategies)
- **Imports/refs brutas:** `app.registry.strategy_registry`, `app.schemas.strategy`, `fastapi`
- **Usa internamente:** `app/registry/strategy_registry.py`, `app/schemas/strategy.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: GET /strategies. Funções principais: list_strategies. Depende de: app/registry/strategy_registry.py, app/schemas/strategy.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/endpoints/ws.py`

- **Papel provável:** Expõe endpoints HTTP/WebSocket
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 13985 bytes
- **Linhas:** 463 totais | 387 não vazias | 0 comentários
- **Hash lógico:** `ed92f3721450b915b5540a206e6bc477dae8f7ba`
- **Funções principais:** `normalize_symbol`, `normalize_timeframe`, `normalize_datetime`, `timeframe_to_timedelta`, `timeframe_to_window`, `floor_time_to_bucket`, `serialize_candle_row`, `load_initial_candles`, `load_last_closed_candle`, `build_tick_from_last_closed`, `try_build_live_tick`, `emit_heartbeat`, `emit_provider_error`, `websocket_feed`
- **Endpoints:** `WEBSOCKET /ws` (websocket_feed)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.providers.twelvedata`, `app.storage.database`, `app.storage.repositories.candle_queries`, `asyncio`, `datetime`, `decimal`, `fastapi`, `json`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/providers/twelvedata.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe endpoints HTTP/WebSocket. Rotas detectadas: WEBSOCKET /ws. Funções principais: normalize_symbol, normalize_timeframe, normalize_datetime, timeframe_to_timedelta, timeframe_to_window, floor_time_to_bucket. Depende de: app/core/settings.py, app/providers/factory.py, app/providers/twelvedata.py, app/storage/database.py, app/storage/repositories/candle_queries.py. Referenciado por: app/api/v1/router.py.

### `app/api/v1/router.py`

- **Papel provável:** Configura roteamento da API
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1639 bytes
- **Linhas:** 35 totais | 32 não vazias | 0 comentários
- **Hash lógico:** `47af89d15b7a26db15d43b251e7463d071b6978a`
- **Imports/refs brutas:** `app.api.v1.endpoints.batch_runs`, `app.api.v1.endpoints.candles`, `app.api.v1.endpoints.catalog`, `app.api.v1.endpoints.health`, `app.api.v1.endpoints.providers`, `app.api.v1.endpoints.run_cases`, `app.api.v1.endpoints.run_details`, `app.api.v1.endpoints.run_history`, `app.api.v1.endpoints.run_metrics`, `app.api.v1.endpoints.runs`, `app.api.v1.endpoints.stage_tests`, `app.api.v1.endpoints.strategies`, `app.api.v1.endpoints.ws`, `fastapi`
- **Usa internamente:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/catalog.py`, `app/api/v1/endpoints/health.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/stage_tests.py`, `app/api/v1/endpoints/strategies.py`, `app/api/v1/endpoints/ws.py`
- **Referenciado por:** `app/main.py`
- **Resumo técnico:** Configura roteamento da API. Depende de: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/catalog.py, app/api/v1/endpoints/health.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/run_cases.py. Referenciado por: app/main.py.

### `app/core/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/core/instrument_catalog.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 9610 bytes
- **Linhas:** 253 totais | 238 não vazias | 0 comentários
- **Hash lógico:** `96abc09f86cc1456759edb7e28c09b2c41c458d8`
- **Classes principais:** `InstrumentCatalogService`
- **Imports/refs brutas:** `copy`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: InstrumentCatalogService.

### `app/core/logging.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1269 bytes
- **Linhas:** 42 totais | 31 não vazias | 0 comentários
- **Hash lógico:** `8226bf9fbe68defc15aff7af3f5bcf5cf721de8f`
- **Funções principais:** `setup_logging`, `get_logger`
- **Imports/refs brutas:** `app.core.settings`, `logging`, `sys`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/main.py`, `app/services/candle_cache_sync.py`, `app/services/candle_sync.py`, `app/services/realtime_ws.py`, `app/services/stage_tests_service.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: setup_logging, get_logger. Depende de: app/core/settings.py. Referenciado por: app/main.py, app/services/candle_cache_sync.py, app/services/candle_sync.py, app/services/realtime_ws.py, app/services/stage_tests_service.py.

### `app/core/settings.py`

- **Papel provável:** Centraliza configurações e constantes
- **Categoria:** `config`
- **Linguagem:** `python`
- **Tamanho:** 1533 bytes
- **Linhas:** 46 totais | 33 não vazias | 0 comentários
- **Hash lógico:** `6be02341fdd4606e0455aecd9346a28e64929160`
- **Classes principais:** `Settings`
- **Funções principais:** `get_settings`
- **Integrações HTTP:** `https://api.binance.com`, `https://api.twelvedata.com`
- **Imports/refs brutas:** `functools`, `pydantic`, `pydantic_settings`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/health.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/core/logging.py`, `app/main.py`, `app/providers/binance.py`, `app/providers/twelvedata.py`, `app/services/candle_sync.py`, `app/services/stage_tests_service.py`, `app/stage_tests/runner.py`, `app/storage/database.py`
- **Resumo técnico:** Centraliza configurações e constantes. Classes principais: Settings. Funções principais: get_settings. Integrações HTTP: https://api.binance.com, https://api.twelvedata.com. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/health.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py.

### `app/engine/__init__.py`

- **Papel provável:** Orquestra lógica principal de execução
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Orquestra lógica principal de execução.

### `app/engine/case_engine.py`

- **Papel provável:** Orquestra lógica principal de execução
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 1089 bytes
- **Linhas:** 36 totais | 31 não vazias | 0 comentários
- **Hash lógico:** `c4f3df8ecbc95ddb61a3a719cda0a413655b5c35`
- **Classes principais:** `CaseEngine`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.strategies.base`, `app.strategies.decisions`
- **Usa internamente:** `app/models/domain/candle.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/engine/run_engine.py`
- **Resumo técnico:** Orquestra lógica principal de execução. Classes principais: CaseEngine. Depende de: app/models/domain/candle.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/strategies/base.py, app/strategies/decisions.py. Referenciado por: app/engine/run_engine.py.

### `app/engine/metrics_engine.py`

- **Papel provável:** Orquestra lógica principal de execução
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 2548 bytes
- **Linhas:** 70 totais | 57 não vazias | 0 comentários
- **Hash lógico:** `b75032fdb3cf6ed6a2b37921f3f967acc3af56c9`
- **Classes principais:** `MetricsEngine`
- **Imports/refs brutas:** `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_metrics`, `decimal`
- **Usa internamente:** `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_metrics.py`
- **Referenciado por:** `app/api/v1/endpoints/run_metrics.py`, `app/engine/run_engine.py`
- **Resumo técnico:** Orquestra lógica principal de execução. Classes principais: MetricsEngine. Depende de: app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_metrics.py. Referenciado por: app/api/v1/endpoints/run_metrics.py, app/engine/run_engine.py.

### `app/engine/run_engine.py`

- **Papel provável:** Orquestra lógica principal de execução
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 3781 bytes
- **Linhas:** 105 totais | 86 não vazias | 0 comentários
- **Hash lógico:** `cf4869f56ffdc7127d7c76f2fd356860e358b7ab`
- **Classes principais:** `RunEngine`
- **Imports/refs brutas:** `app.engine.case_engine`, `app.engine.metrics_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.strategies.base`
- **Usa internamente:** `app/engine/case_engine.py`, `app/engine/metrics_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/strategies/base.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Orquestra lógica principal de execução. Classes principais: RunEngine. Depende de: app/engine/case_engine.py, app/engine/metrics_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, tests/test_run_engine.py.

### `app/indicators/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/indicators/atr.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1478 bytes
- **Linhas:** 52 totais | 37 não vazias | 1 comentários
- **Hash lógico:** `38924fb18b41a74c2d0505c658903fd5072db781`
- **Funções principais:** `average_true_range`, `average_true_range_series`
- **Imports/refs brutas:** `app.models.domain.candle`, `decimal`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: average_true_range, average_true_range_series. Depende de: app/models/domain/candle.py. Referenciado por: app/services/case_snapshot.py.

### `app/indicators/bollinger.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 945 bytes
- **Linhas:** 36 totais | 24 não vazias | 0 comentários
- **Hash lógico:** `9bf9c3575c51534083ae68e5e6c81fbcdffd2fa8`
- **Funções principais:** `bollinger_bands`
- **Imports/refs brutas:** `app.indicators.sma`, `decimal`, `math`
- **Usa internamente:** `app/indicators/sma.py`
- **Referenciado por:** `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ff_fd.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: bollinger_bands. Depende de: app/indicators/sma.py. Referenciado por: app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ff_fd.py.

### `app/indicators/ema.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1134 bytes
- **Linhas:** 45 totais | 30 não vazias | 1 comentários
- **Hash lógico:** `e12a7bc4885b49cccef3c88a4cf54855d0b9365d`
- **Funções principais:** `exponential_moving_average`, `exponential_moving_average_series`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/indicators/macd.py`, `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/ema_cross.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: exponential_moving_average, exponential_moving_average_series. Referenciado por: app/indicators/macd.py, app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/ema_cross.py.

### `app/indicators/macd.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 2752 bytes
- **Linhas:** 102 totais | 78 não vazias | 1 comentários
- **Hash lógico:** `c1d6f3b763dd618cf11c4697764a6088a08311e5`
- **Funções principais:** `macd`, `macd_series`
- **Imports/refs brutas:** `app.indicators.ema`, `decimal`
- **Usa internamente:** `app/indicators/ema.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: macd, macd_series. Depende de: app/indicators/ema.py. Referenciado por: app/services/case_snapshot.py.

### `app/indicators/rsi.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1625 bytes
- **Linhas:** 54 totais | 37 não vazias | 1 comentários
- **Hash lógico:** `5fcb98018ef96c1a7aba470bc520e24bdc696bd3`
- **Funções principais:** `relative_strength_index`, `relative_strength_index_series`, `_build_rsi`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: relative_strength_index, relative_strength_index_series, _build_rsi. Referenciado por: app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/rsi_reversal.py.

### `app/indicators/sma.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 324 bytes
- **Linhas:** 12 totais | 8 não vazias | 0 comentários
- **Hash lógico:** `998482d21bc498f3c0393aa6e78f857b3aa316cc`
- **Funções principais:** `simple_moving_average`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/indicators/bollinger.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: simple_moving_average. Referenciado por: app/indicators/bollinger.py.

### `app/main.py`

- **Papel provável:** Ponto de entrada da aplicação
- **Categoria:** `entrypoint`
- **Linguagem:** `python`
- **Tamanho:** 3393 bytes
- **Linhas:** 114 totais | 87 não vazias | 0 comentários
- **Hash lógico:** `82e705287472d27675e3f13dd0532d02a9918471`
- **Funções principais:** `_resolve_sqlite_path`, `_get_sqlite_runtime_info`, `on_startup`, `health`
- **Endpoints:** `GET /health` (health)
- **Integrações HTTP:** `http://127.0.0.1:5173`, `http://localhost:5173`
- **Imports/refs brutas:** `app.api.v1.router`, `app.core.logging`, `app.core.settings`, `app.storage.database`, `app.storage.models`, `fastapi`, `fastapi.middleware.cors`, `pathlib`, `sqlalchemy`, `typing`
- **Usa internamente:** `app/api/v1/router.py`, `app/core/logging.py`, `app/core/settings.py`, `app/storage/database.py`, `app/storage/models.py`
- **Resumo técnico:** Ponto de entrada da aplicação. Rotas detectadas: GET /health. Funções principais: _resolve_sqlite_path, _get_sqlite_runtime_info, on_startup, health. Integrações HTTP: http://127.0.0.1:5173, http://localhost:5173. Depende de: app/api/v1/router.py, app/core/logging.py, app/core/settings.py, app/storage/database.py, app/storage/models.py.

### `app/models/__init__.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Define modelos de domínio ou persistência.

### `app/models/domain/__init__.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Define modelos de domínio ou persistência.

### `app/models/domain/asset.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 378 bytes
- **Linhas:** 14 totais | 11 não vazias | 0 comentários
- **Hash lógico:** `bc44d9f9849945550895a599daa83fdb5d904a7a`
- **Classes principais:** `Asset`
- **Imports/refs brutas:** `app.models.domain.enums`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: Asset. Depende de: app/models/domain/enums.py.

### `app/models/domain/candle.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 408 bytes
- **Linhas:** 18 totais | 15 não vazias | 0 comentários
- **Hash lógico:** `6c2860e8d3b3296fe597323f75df5cab220550b4`
- **Classes principais:** `Candle`
- **Imports/refs brutas:** `datetime`, `decimal`, `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/indicators/atr.py`, `app/providers/base.py`, `app/providers/binance.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`, `app/services/candlestick_intelligence.py`, `app/services/case_snapshot.py`, `app/services/mock_market_data_service.py`, `app/stage_tests/runner.py`, `app/storage/repositories/candle_repository.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: Candle. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/case_engine.py, app/engine/run_engine.py, app/indicators/atr.py, app/providers/base.py.

### `app/models/domain/enums.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 786 bytes
- **Linhas:** 41 totais | 29 não vazias | 0 comentários
- **Hash lógico:** `a8e2d2bb1405638d497bdd649ae5b313a0fa137c`
- **Classes principais:** `MarketType`, `RunMode`, `RunStatus`, `CaseStatus`, `CaseOutcome`, `StrategyCategory`
- **Imports/refs brutas:** `enum`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/engine/metrics_engine.py`, `app/engine/run_engine.py`, `app/models/domain/asset.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/decisions.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: MarketType, RunMode, RunStatus, CaseStatus, CaseOutcome, StrategyCategory. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/run_metrics.py, app/api/v1/endpoints/runs.py, app/engine/metrics_engine.py, app/engine/run_engine.py, app/models/domain/asset.py.

### `app/models/domain/strategy_case.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 932 bytes
- **Linhas:** 36 totais | 26 não vazias | 0 comentários
- **Hash lógico:** `4d89d1cd1c5eb943b73f5897c2d1c7dabe221dcb`
- **Classes principais:** `StrategyCase`
- **Imports/refs brutas:** `app.models.domain.enums`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/api/v1/endpoints/run_metrics.py`, `app/engine/case_engine.py`, `app/engine/metrics_engine.py`, `app/engine/run_engine.py`, `app/schemas/run.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: StrategyCase. Depende de: app/models/domain/enums.py. Referenciado por: app/api/v1/endpoints/run_metrics.py, app/engine/case_engine.py, app/engine/metrics_engine.py, app/engine/run_engine.py, app/schemas/run.py, app/strategies/base.py.

### `app/models/domain/strategy_config.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 393 bytes
- **Linhas:** 14 totais | 12 não vazias | 0 comentários
- **Hash lógico:** `112afbfc33c59f7a7cfe214e1ca6a2a7e5449784`
- **Classes principais:** `StrategyConfig`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/services/case_snapshot.py`, `app/stage_tests/runner.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: StrategyConfig. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/case_engine.py, app/engine/run_engine.py, app/services/case_snapshot.py, app/stage_tests/runner.py.

### `app/models/domain/strategy_definition.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 269 bytes
- **Linhas:** 11 totais | 8 não vazias | 0 comentários
- **Hash lógico:** `70e12f8cfd3ce2020423dfb961a102de9177aa74`
- **Classes principais:** `StrategyDefinition`
- **Imports/refs brutas:** `app.models.domain.enums`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/schemas/strategy.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: StrategyDefinition. Depende de: app/models/domain/enums.py. Referenciado por: app/schemas/strategy.py, app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/ff_fd.py.

### `app/models/domain/strategy_metrics.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 532 bytes
- **Linhas:** 20 totais | 15 não vazias | 0 comentários
- **Hash lógico:** `b795b372ec8d564585adbc0ff4aca64fc692d3c4`
- **Classes principais:** `StrategyMetrics`
- **Imports/refs brutas:** `decimal`, `pydantic`
- **Referenciado por:** `app/engine/metrics_engine.py`, `app/schemas/run.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: StrategyMetrics. Referenciado por: app/engine/metrics_engine.py, app/schemas/run.py.

### `app/models/domain/strategy_run.py`

- **Papel provável:** Define modelos de domínio ou persistência
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 648 bytes
- **Linhas:** 23 totais | 19 não vazias | 0 comentários
- **Hash lógico:** `6538d2114feb6da9685fe5c100747e9fd6164228`
- **Classes principais:** `StrategyRun`
- **Imports/refs brutas:** `app.models.domain.enums`, `datetime`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/run_engine.py`, `app/schemas/run.py`, `app/stage_tests/runner.py`, `app/storage/repositories/run_repository.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou persistência. Classes principais: StrategyRun. Depende de: app/models/domain/enums.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/run_engine.py, app/schemas/run.py, app/stage_tests/runner.py, app/storage/repositories/run_repository.py.

### `app/providers/__init__.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Integra fontes externas de dados.

### `app/providers/base.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 28 totais | 23 não vazias | 1 comentários
- **Hash lógico:** `eba6e47ba63af53a6b2eef272491a1920cea06af`
- **Classes principais:** `BaseMarketDataProvider`
- **Imports/refs brutas:** `abc`, `app.models.domain.candle`, `datetime`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/providers/binance.py`, `app/providers/factory.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`
- **Resumo técnico:** Integra fontes externas de dados. Classes principais: BaseMarketDataProvider. Depende de: app/models/domain/candle.py. Referenciado por: app/providers/binance.py, app/providers/factory.py, app/providers/mock.py, app/providers/twelvedata.py.

### `app/providers/binance.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 3923 bytes
- **Linhas:** 122 totais | 103 não vazias | 0 comentários
- **Hash lógico:** `c4104a51a8cbd59de92894d944c2796fc87fa5ae`
- **Classes principais:** `BinanceProvider`
- **Imports/refs brutas:** `app.core.settings`, `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`, `json`, `urllib.error`, `urllib.parse`, `urllib.request`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/providers/factory.py`
- **Resumo técnico:** Integra fontes externas de dados. Classes principais: BinanceProvider. Depende de: app/core/settings.py, app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/providers/factory.py.

### `app/providers/factory.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 873 bytes
- **Linhas:** 24 totais | 18 não vazias | 0 comentários
- **Hash lógico:** `b8d17241f4f3d86e89dc62184149e4c200a7c549`
- **Classes principais:** `MarketDataProviderFactory`
- **Imports/refs brutas:** `app.providers.base`, `app.providers.binance`, `app.providers.mock`, `app.providers.twelvedata`
- **Usa internamente:** `app/providers/base.py`, `app/providers/binance.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/services/candle_sync.py`
- **Resumo técnico:** Integra fontes externas de dados. Classes principais: MarketDataProviderFactory. Depende de: app/providers/base.py, app/providers/binance.py, app/providers/mock.py, app/providers/twelvedata.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py, app/services/candle_sync.py.

### `app/providers/mock.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 1975 bytes
- **Linhas:** 72 totais | 58 não vazias | 1 comentários
- **Hash lógico:** `cef3e6f31419b40f10752eed30d3b00109e71f81`
- **Classes principais:** `MockMarketDataProvider`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`
- **Usa internamente:** `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/providers/factory.py`
- **Resumo técnico:** Integra fontes externas de dados. Classes principais: MockMarketDataProvider. Depende de: app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/providers/factory.py.

### `app/providers/twelvedata.py`

- **Papel provável:** Integra fontes externas de dados
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 9140 bytes
- **Linhas:** 262 totais | 216 não vazias | 0 comentários
- **Hash lógico:** `f635c7d0acef6a7e265cfbdaff91d22dcf6b67a3`
- **Classes principais:** `ProviderQuotaExceededError`, `ProviderTemporaryCooldownError`, `TwelveDataProvider`
- **Funções principais:** `ensure_naive_utc`
- **Imports/refs brutas:** `app.core.settings`, `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`, `json`, `math`, `threading`, `urllib.error`, `urllib.parse`, `urllib.request`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/api/v1/endpoints/ws.py`, `app/providers/factory.py`
- **Resumo técnico:** Integra fontes externas de dados. Classes principais: ProviderQuotaExceededError, ProviderTemporaryCooldownError, TwelveDataProvider. Funções principais: ensure_naive_utc. Depende de: app/core/settings.py, app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/api/v1/endpoints/ws.py, app/providers/factory.py.

### `app/registry/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/registry/strategy_registry.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 1616 bytes
- **Linhas:** 47 totais | 32 não vazias | 1 comentários
- **Hash lógico:** `74e45755d24a0616ef7de290f9edbcfbdadbf041`
- **Classes principais:** `StrategyRegistry`
- **Funções principais:** `build_strategy_registry`
- **Imports/refs brutas:** `app.strategies.base`, `app.strategies.bollinger_reversal`, `app.strategies.bollinger_walk_the_band`, `app.strategies.ema_cross`, `app.strategies.rsi_reversal`
- **Usa internamente:** `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/rsi_reversal.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/strategies.py`, `app/stage_tests/runner.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: StrategyRegistry. Funções principais: build_strategy_registry. Depende de: app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/rsi_reversal.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/strategies.py, app/stage_tests/runner.py.

### `app/schemas/__init__.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Define contratos de dados e serialização.

### `app/schemas/batch_run.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 861 bytes
- **Linhas:** 35 totais | 25 não vazias | 0 comentários
- **Hash lógico:** `3ab556ba4bdbaa820776c3ea3f1e77afd1e750db`
- **Classes principais:** `BatchStrategyItemRequest`, `BatchHistoricalRunRequest`, `BatchHistoricalRunItemResponse`, `BatchHistoricalRunResponse`
- **Imports/refs brutas:** `app.schemas.run`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/schemas/run.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: BatchStrategyItemRequest, BatchHistoricalRunRequest, BatchHistoricalRunItemResponse, BatchHistoricalRunResponse. Depende de: app/schemas/run.py. Referenciado por: app/api/v1/endpoints/batch_runs.py.

### `app/schemas/catalog.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 906 bytes
- **Linhas:** 40 totais | 28 não vazias | 0 comentários
- **Hash lógico:** `d7ad1e840618aef83d1f5b08cf25ade1854b4586`
- **Classes principais:** `CatalogProductSummary`, `CatalogSubproduct`, `CatalogInstrument`, `CatalogProductsResponse`, `CatalogProductResponse`, `CatalogItemsResponse`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/catalog.py`, `app/services/catalog_service.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: CatalogProductSummary, CatalogSubproduct, CatalogInstrument, CatalogProductsResponse, CatalogProductResponse, CatalogItemsResponse. Referenciado por: app/api/v1/endpoints/catalog.py, app/services/catalog_service.py.

### `app/schemas/comparison.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 27 totais | 22 não vazias | 0 comentários
- **Hash lógico:** `d87e345e99e070dfe37bc28ef7f4c61528e05b91`
- **Classes principais:** `StrategyComparisonItemResponse`, `StrategyComparisonResponse`
- **Imports/refs brutas:** `decimal`, `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `app/services/comparison_service.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: StrategyComparisonItemResponse, StrategyComparisonResponse. Referenciado por: app/api/v1/endpoints/comparisons.py, app/services/comparison_service.py.

### `app/schemas/provider.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 128 bytes
- **Linhas:** 6 totais | 4 não vazias | 0 comentários
- **Hash lógico:** `9637c0ed0cfe25447a290bdd5c2f1681b372e2f6`
- **Classes principais:** `ProviderListResponse`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/providers.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: ProviderListResponse. Referenciado por: app/api/v1/endpoints/providers.py.

### `app/schemas/run.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 5756 bytes
- **Linhas:** 187 totais | 162 não vazias | 1 comentários
- **Hash lógico:** `8d5f2c3a503a42572da6b105b3e1e91d9f8fefb4`
- **Classes principais:** `HistoricalRunRequest`, `CandleResponse`, `CandleListResponse`, `StrategyRunResponse`, `StrategyCaseResponse`, `StrategyMetricsResponse`, `HistoricalRunResponse`
- **Funções principais:** `build_run_response`, `build_case_response`, `build_metrics_response`, `build_historical_run_response`
- **Imports/refs brutas:** `app.models.domain.strategy_case`, `app.models.domain.strategy_metrics`, `app.models.domain.strategy_run`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/models/domain/strategy_case.py`, `app/models/domain/strategy_metrics.py`, `app/models/domain/strategy_run.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/schemas/batch_run.py`, `app/schemas/run_details.py`, `app/services/mock_market_data_service.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: HistoricalRunRequest, CandleResponse, CandleListResponse, StrategyRunResponse, StrategyCaseResponse, StrategyMetricsResponse. Funções principais: build_run_response, build_case_response, build_metrics_response, build_historical_run_response. Depende de: app/models/domain/strategy_case.py, app/models/domain/strategy_metrics.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py, app/api/v1/endpoints/run_metrics.py.

### `app/schemas/run_details.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 312 bytes
- **Linhas:** 13 totais | 10 não vazias | 0 comentários
- **Hash lógico:** `3c1d5ee3864095487e1e6764b1d72477ae3ae5bf`
- **Classes principais:** `RunDetailsResponse`
- **Imports/refs brutas:** `app.schemas.run`, `pydantic`
- **Usa internamente:** `app/schemas/run.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: RunDetailsResponse. Depende de: app/schemas/run.py. Referenciado por: app/api/v1/endpoints/run_details.py.

### `app/schemas/stage_tests.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 2440 bytes
- **Linhas:** 71 totais | 57 não vazias | 0 comentários
- **Hash lógico:** `4f5ac7ed06eccf8e6da5b4433aa3906a10221027`
- **Classes principais:** `StageTestStrategyOptionResponse`, `StageTestOptionItemResponse`, `StageTestOptionsResponse`, `StageTestRunRequest`, `StageTestMetricsResponse`, `StageTestRunResponse`
- **Imports/refs brutas:** `__future__`, `pydantic`, `typing`
- **Referenciado por:** `app/api/routes/stage_tests.py`, `app/api/v1/endpoints/stage_tests.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: StageTestStrategyOptionResponse, StageTestOptionItemResponse, StageTestOptionsResponse, StageTestRunRequest, StageTestMetricsResponse, StageTestRunResponse. Referenciado por: app/api/routes/stage_tests.py, app/api/v1/endpoints/stage_tests.py.

### `app/schemas/strategy.py`

- **Papel provável:** Define contratos de dados e serialização
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 579 bytes
- **Linhas:** 21 totais | 16 não vazias | 0 comentários
- **Hash lógico:** `edd4fcdca0c18b70f1661713b7dde3a5c4ebb4ae`
- **Classes principais:** `StrategyListItemResponse`
- **Funções principais:** `build_strategy_list_item`
- **Imports/refs brutas:** `app.models.domain.strategy_definition`, `pydantic`
- **Usa internamente:** `app/models/domain/strategy_definition.py`
- **Referenciado por:** `app/api/v1/endpoints/strategies.py`
- **Resumo técnico:** Define contratos de dados e serialização. Classes principais: StrategyListItemResponse. Funções principais: build_strategy_list_item. Depende de: app/models/domain/strategy_definition.py. Referenciado por: app/api/v1/endpoints/strategies.py.

### `app/services/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/services/candle_cache_sync.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 2681 bytes
- **Linhas:** 70 totais | 61 não vazias | 9 comentários
- **Hash lógico:** `8976dbbb231cfe93dc8d2cc570a6f8de5c804b23`
- **Classes principais:** `CandleCacheSyncService`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.storage.cache_models`, `typing`
- **Usa internamente:** `app/core/logging.py`, `app/storage/cache_models.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: CandleCacheSyncService. Depende de: app/core/logging.py, app/storage/cache_models.py.

### `app/services/candle_sync.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 9184 bytes
- **Linhas:** 242 totais | 205 não vazias | 6 comentários
- **Hash lógico:** `512d9f0568e0b2d794b34b9b7457b00a979aaff4`
- **Classes principais:** `CandleSyncResult`, `CandleSyncService`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.core.settings`, `app.providers.factory`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.utils.datetime_utils`, `dataclasses`, `datetime`
- **Usa internamente:** `app/core/logging.py`, `app/core/settings.py`, `app/providers/factory.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/utils/datetime_utils.py`
- **Referenciado por:** `app/services/realtime_ws.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: CandleSyncResult, CandleSyncService. Depende de: app/core/logging.py, app/core/settings.py, app/providers/factory.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py, app/utils/datetime_utils.py. Referenciado por: app/services/realtime_ws.py.

### `app/services/candlestick_confirmation.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 18148 bytes
- **Linhas:** 521 totais | 402 não vazias | 1 comentários
- **Hash lógico:** `92c56e47118d9e0cb0d7b3eb7159d01158641843`
- **Funções principais:** `_safe_str`, `_to_decimal`, `_append_unique`, `_normalize_direction`, `_is_buy`, `_is_sell`, `_is_bullish_pattern`, `_is_bearish_pattern`, `_extract_active_patterns`, `_has_favorable_pattern`, `_has_contrary_pattern`, `_trigger_is_favorable`, `_trigger_is_against_setup`, `_price_supports_setup`, `_rsi_supports_setup`, `_rsi_against_setup`, `_macd_supports_setup`, `_structure_supports_setup`, `_adx_strength`, `_macro_points_and_reasons`, `_apply_quality_ceiling`, `_raw_confirmation_score`, `_score_to_label`, `score_phase_3_confirmation`, `build_phase_3_confirmation_from_snapshot`
- **Imports/refs brutas:** `__future__`, `decimal`, `typing`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: _safe_str, _to_decimal, _append_unique, _normalize_direction, _is_buy, _is_sell.

### `app/services/candlestick_intelligence.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 47792 bytes
- **Linhas:** 1374 totais | 1116 não vazias | 1 comentários
- **Hash lógico:** `4e9e9859705063bb1ce1f53a77189afac1f5fcee`
- **Funções principais:** `decimal_to_str`, `clamp`, `safe_ratio`, `normalize_direction`, `normalize_entry_location`, `normalize_cross_state`, `candle_color`, `candle_body`, `candle_range`, `upper_wick`, `lower_wick`, `body_ratio`, `upper_wick_ratio`, `lower_wick_ratio`, `close_position`, `classify_single_candle_pattern`, `classify_strength_class`, `build_candle_feature`, `is_bullish`, `is_bearish`, `body_midpoint`, `has_meaningful_body`, `is_small_star_body`, `strong_bearish_context`, `strong_bullish_context`, `detect_bullish_engulfing`, `detect_bearish_engulfing`, `detect_bullish_harami`, `detect_bearish_harami`, `detect_piercing_line`
- **Imports/refs brutas:** `__future__`, `app.models.domain.candle`, `decimal`, `typing`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: decimal_to_str, clamp, safe_ratio, normalize_direction, normalize_entry_location, normalize_cross_state. Depende de: app/models/domain/candle.py. Referenciado por: app/services/case_snapshot.py.

### `app/services/case_snapshot.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 34181 bytes
- **Linhas:** 996 totais | 797 não vazias | 1 comentários
- **Hash lógico:** `4eb67da677daa5d627fc59d19501f9e24be19b48`
- **Funções principais:** `build_case_metadata_snapshot`, `as_str`, `resolve_setup_direction`, `classify_cross_state`, `slope_label`, `classify_ema_alignment`, `classify_price_vs_average`, `classify_rsi_zone`, `classify_macd_state`, `calculate_band_position`, `classify_session`, `build_candle_stats`, `classify_candle_type`, `classify_market_structure`, `classify_entry_location`, `distance_to_recent_support`, `distance_to_recent_resistance`, `distance_to_level`, `classify_atr_regime`, `calculate_vwap`, `calculate_volume_ratio`, `calculate_volume_zscore`, `classify_volume_signal`, `classify_volume_context`, `calculate_bollinger_z_score`, `calculate_distance_outside_band`, `calculate_distance_from_nearest_band`, `average_directional_index_series`, `decimal_sqrt`, `quantize_decimal`
- **Imports/refs brutas:** `__future__`, `app.indicators.atr`, `app.indicators.bollinger`, `app.indicators.ema`, `app.indicators.macd`, `app.indicators.rsi`, `app.models.domain.candle`, `app.models.domain.strategy_config`, `app.services.candlestick_intelligence`, `decimal`
- **Usa internamente:** `app/indicators/atr.py`, `app/indicators/bollinger.py`, `app/indicators/ema.py`, `app/indicators/macd.py`, `app/indicators/rsi.py`, `app/models/domain/candle.py`, `app/models/domain/strategy_config.py`, `app/services/candlestick_intelligence.py`
- **Referenciado por:** `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: build_case_metadata_snapshot, as_str, resolve_setup_direction, classify_cross_state, slope_label, classify_ema_alignment. Depende de: app/indicators/atr.py, app/indicators/bollinger.py, app/indicators/ema.py, app/indicators/macd.py, app/indicators/rsi.py, app/models/domain/candle.py. Referenciado por: app/strategies/ema_cross.py, app/strategies/ff_fd.py, app/strategies/rsi_reversal.py.

### `app/services/catalog_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 6104 bytes
- **Linhas:** 169 totais | 155 não vazias | 0 comentários
- **Hash lógico:** `889a5748a6217e573487c17c9cc7cd7d10fd3926`
- **Classes principais:** `CatalogService`
- **Imports/refs brutas:** `app.schemas.catalog`
- **Usa internamente:** `app/schemas/catalog.py`
- **Referenciado por:** `app/api/v1/endpoints/catalog.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: CatalogService. Depende de: app/schemas/catalog.py. Referenciado por: app/api/v1/endpoints/catalog.py.

### `app/services/comparison_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 3481 bytes
- **Linhas:** 98 totais | 82 não vazias | 0 comentários
- **Hash lógico:** `42beb4992fc5d74c7017db321d270faa45f47342`
- **Classes principais:** `ComparisonService`
- **Imports/refs brutas:** `app.schemas.comparison`, `app.storage.repositories.comparison_queries`, `decimal`
- **Usa internamente:** `app/schemas/comparison.py`, `app/storage/repositories/comparison_queries.py`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `tests/test_comparisons.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: ComparisonService. Depende de: app/schemas/comparison.py, app/storage/repositories/comparison_queries.py. Referenciado por: app/api/v1/endpoints/comparisons.py, tests/test_comparisons.py.

### `app/services/mock_market_data_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 1915 bytes
- **Linhas:** 66 totais | 53 não vazias | 0 comentários
- **Hash lógico:** `49938784647ef9d3a27dbee3ad67fb0ccd3c9cc9`
- **Classes principais:** `MockMarketDataService`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.schemas.run`, `datetime`, `decimal`, `fastapi`
- **Usa internamente:** `app/models/domain/candle.py`, `app/schemas/run.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: MockMarketDataService. Depende de: app/models/domain/candle.py, app/schemas/run.py.

### `app/services/realtime_ws.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 18269 bytes
- **Linhas:** 539 totais | 461 não vazias | 0 comentários
- **Hash lógico:** `ed141d5f4354e14860e5ba6667f3f8f969cbbdc1`
- **Classes principais:** `SubscriptionKey`, `RealtimeSubscriptionWorker`, `RealtimeWSManager`
- **Funções principais:** `row_to_ws_candle`
- **Imports/refs brutas:** `app.core.logging`, `app.services.candle_sync`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.utils.datetime_utils`, `asyncio`, `collections`, `dataclasses`, `datetime`, `fastapi`, `json`, `typing`
- **Usa internamente:** `app/core/logging.py`, `app/services/candle_sync.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/utils/datetime_utils.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: SubscriptionKey, RealtimeSubscriptionWorker, RealtimeWSManager. Funções principais: row_to_ws_candle. Depende de: app/core/logging.py, app/services/candle_sync.py, app/storage/database.py, app/storage/repositories/candle_queries.py, app/utils/datetime_utils.py.

### `app/services/stage_tests_service.py`

- **Papel provável:** Ficheiro de testes
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 13602 bytes
- **Linhas:** 448 totais | 357 não vazias | 1 comentários
- **Hash lógico:** `e8806e77192c99354df21aca6fcd4b41b055a05f`
- **Funções principais:** `utc_now_iso`, `normalize_symbol`, `get_db_path`, `connect_db`, `list_stage_test_options`, `validate_symbol_timeframe`, `validate_strategy`, `build_stage_test_command`, `extract_metrics_from_stdout`, `extract_analysis_from_metrics`, `extract_cases_from_metrics`, `run_stage_test`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.core.settings`, `app.stage_tests.catalog`, `datetime`, `json`, `os`, `shlex`, `sqlite3`, `subprocess`, `typing`, `urllib.parse`
- **Usa internamente:** `app/core/logging.py`, `app/core/settings.py`, `app/stage_tests/catalog.py`
- **Referenciado por:** `app/api/routes/stage_tests.py`, `app/api/v1/endpoints/stage_tests.py`
- **Resumo técnico:** Ficheiro de testes. Funções principais: utc_now_iso, normalize_symbol, get_db_path, connect_db, list_stage_test_options, validate_symbol_timeframe. Depende de: app/core/logging.py, app/core/settings.py, app/stage_tests/catalog.py. Referenciado por: app/api/routes/stage_tests.py, app/api/v1/endpoints/stage_tests.py.

### `app/stage_tests/catalog.py`

- **Papel provável:** Ficheiro de testes
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1628 bytes
- **Linhas:** 54 totais | 44 não vazias | 4 comentários
- **Hash lógico:** `22696643bbd4a0f97b077e27bbbb956d1e4c2eb3`
- **Funções principais:** `list_stage_test_strategies`, `get_stage_test_strategy_keys`, `is_valid_stage_test_strategy`
- **Imports/refs brutas:** `__future__`, `typing`
- **Referenciado por:** `app/services/stage_tests_service.py`
- **Resumo técnico:** Ficheiro de testes. Funções principais: list_stage_test_strategies, get_stage_test_strategy_keys, is_valid_stage_test_strategy. Referenciado por: app/services/stage_tests_service.py.

### `app/stage_tests/runner.py`

- **Papel provável:** Ficheiro de testes
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 38365 bytes
- **Linhas:** 1109 totais | 922 não vazias | 1 comentários
- **Hash lógico:** `b7e2ec4b5db38137f6a4ebc91ce2a239051dc06d`
- **Funções principais:** `normalize_symbol`, `get_db_path`, `get_existing_candle_columns`, `load_candles_rows`, `parse_value`, `get_constructor_fields`, `instantiate_model`, `build_candle`, `parse_extra_args`, `build_strategy_config`, `build_strategy_run`, `safe_attr`, `decision_is_triggered`, `decision_should_close`, `summarize_case_outcome`, `pct`, `to_jsonable`, `read_case_metadata`, `read_analysis_snapshot_from_case`, `normalize_direction`, `build_rules_from_snapshot`, `build_indicators_from_snapshot`, `get_phase3_confirmation`, `build_case_metadata_summary`, `build_analysis_from_case`, `serialize_case`, `select_best_analysis_case`, `debug_first_serialized_case`, `main`
- **Imports/refs brutas:** `__future__`, `app.core.settings`, `app.models.domain.candle`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.registry.strategy_registry`, `app.stage_tests.strategy_mapper`, `argparse`, `datetime`, `decimal`, `inspect`, `json`, `os`, `sqlite3`, `typing`, `urllib.parse`, `uuid`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/registry/strategy_registry.py`, `app/stage_tests/strategy_mapper.py`
- **Resumo técnico:** Ficheiro de testes. Funções principais: normalize_symbol, get_db_path, get_existing_candle_columns, load_candles_rows, parse_value, get_constructor_fields. Depende de: app/core/settings.py, app/models/domain/candle.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py, app/registry/strategy_registry.py, app/stage_tests/strategy_mapper.py.

### `app/stage_tests/strategy_mapper.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 2447 bytes
- **Linhas:** 87 totais | 72 não vazias | 4 comentários
- **Hash lógico:** `0e2467c2320caed69074b60bb49bb95da7e6662e`
- **Funções principais:** `normalize_stage_test_strategy_key`, `resolve_runtime_strategy_key`, `get_default_parameters`
- **Imports/refs brutas:** `__future__`, `typing`
- **Referenciado por:** `app/stage_tests/runner.py`
- **Resumo técnico:** Implementa regras de estratégia. Funções principais: normalize_stage_test_strategy_key, resolve_runtime_strategy_key, get_default_parameters. Referenciado por: app/stage_tests/runner.py.

### `app/storage/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/storage/cache_models.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 192 bytes
- **Linhas:** 9 totais | 7 não vazias | 1 comentários
- **Hash lógico:** `52072be65157a06e768f3e6ab9a370801cef5636`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/services/candle_cache_sync.py`, `app/storage/repositories/candle_coverages.py`
- **Resumo técnico:** Lógica de suporte do projeto. Depende de: app/storage/models.py. Referenciado por: app/services/candle_cache_sync.py, app/storage/repositories/candle_coverages.py.

### `app/storage/database.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 555 bytes
- **Linhas:** 33 totais | 23 não vazias | 0 comentários
- **Hash lógico:** `81bf997066601a643ee9170c4557681647936180`
- **Classes principais:** `Base`
- **Funções principais:** `get_db_session`
- **Imports/refs brutas:** `app.core.settings`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/comparisons.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/main.py`, `app/services/realtime_ws.py`, `app/storage/models.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: Base. Funções principais: get_db_session. Depende de: app/core/settings.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/comparisons.py, app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py.

### `app/storage/models.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 5110 bytes
- **Linhas:** 120 totais | 94 não vazias | 1 comentários
- **Hash lógico:** `f5311203ca497e3a84cab96a2d3561f00043bd97`
- **Classes principais:** `Candle`, `CandleCoverage`, `StrategyRun`, `StrategyMetric`, `StrategyCase`
- **Imports/refs brutas:** `__future__`, `app.storage.database`, `datetime`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/database.py`
- **Referenciado por:** `app/api/v1/endpoints/run_history.py`, `app/main.py`, `app/storage/cache_models.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/candle_upserts.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/comparison_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_queries.py`, `app/storage/repositories/run_repository.py`
- **Resumo técnico:** Lógica de suporte do projeto. Classes principais: Candle, CandleCoverage, StrategyRun, StrategyMetric, StrategyCase. Depende de: app/storage/database.py. Referenciado por: app/api/v1/endpoints/run_history.py, app/main.py, app/storage/cache_models.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py, app/storage/repositories/candle_upserts.py.

### `app/storage/repositories/candle_coverages.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1780 bytes
- **Linhas:** 64 totais | 54 não vazias | 0 comentários
- **Hash lógico:** `60f15feb936cb9c6409454d20a7f4f51e7f0e0ef`
- **Classes principais:** `CandleCoverageRepository`
- **Imports/refs brutas:** `app.storage.cache_models`, `datetime`
- **Usa internamente:** `app/storage/cache_models.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: CandleCoverageRepository. Depende de: app/storage/cache_models.py.

### `app/storage/repositories/candle_queries.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2070 bytes
- **Linhas:** 72 totais | 61 não vazias | 0 comentários
- **Hash lógico:** `b847d2b098718bb0457047e52d9c47455beb9c38`
- **Classes principais:** `CandleQueryRepository`
- **Imports/refs brutas:** `app.storage.models`, `datetime`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/services/candle_sync.py`, `app/services/realtime_ws.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: CandleQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py, app/services/candle_sync.py, app/services/realtime_ws.py.

### `app/storage/repositories/candle_repository.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2304 bytes
- **Linhas:** 75 totais | 60 não vazias | 0 comentários
- **Hash lógico:** `0341f7b8e7c3e091e9be566b4a72b178e538d086`
- **Classes principais:** `CandleRepository`
- **Funções principais:** `_new_uuid`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.storage.models`, `sqlalchemy.exc`, `sqlalchemy.orm.exc`, `uuid`
- **Usa internamente:** `app/models/domain/candle.py`, `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/runs.py`, `app/services/candle_sync.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: CandleRepository. Funções principais: _new_uuid. Depende de: app/models/domain/candle.py, app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/runs.py, app/services/candle_sync.py.

### `app/storage/repositories/candle_upserts.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2250 bytes
- **Linhas:** 70 totais | 57 não vazias | 0 comentários
- **Hash lógico:** `1ed1333bee7e11b3c3ab739cabbb64350515cb5d`
- **Classes principais:** `CandleUpsertRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `collections.abc`, `sqlalchemy.dialects.sqlite`, `sqlalchemy.orm`, `typing`
- **Usa internamente:** `app/storage/models.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: CandleUpsertRepository. Depende de: app/storage/models.py.

### `app/storage/repositories/case_queries.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 409 bytes
- **Linhas:** 11 totais | 9 não vazias | 0 comentários
- **Hash lógico:** `bbd8d8e99e481408d75f877cfc9a19b348a12f9a`
- **Classes principais:** `StrategyCaseQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyCaseQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_metrics.py.

### `app/storage/repositories/case_repository.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 518 bytes
- **Linhas:** 16 totais | 12 não vazias | 0 comentários
- **Hash lógico:** `dcaf2d0c62d5b45919984ceaa419b155f1e6ade4`
- **Classes principais:** `StrategyCaseRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyCaseRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

### `app/storage/repositories/comparison_queries.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1344 bytes
- **Linhas:** 41 totais | 32 não vazias | 0 comentários
- **Hash lógico:** `d47fe4f0ee3c6faaa334dafacc8a61e6c052f146`
- **Classes principais:** `StrategyComparisonQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `app/services/comparison_service.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyComparisonQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/comparisons.py, app/services/comparison_service.py.

### `app/storage/repositories/metrics_queries.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 690 bytes
- **Linhas:** 22 totais | 17 não vazias | 1 comentários
- **Hash lógico:** `0ef6eebfd48a7aa36f7b0995c96fe6c4f56b823f`
- **Classes principais:** `StrategyMetricsQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyMetricsQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_metrics.py.

### `app/storage/repositories/metrics_repository.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 533 bytes
- **Linhas:** 16 totais | 12 não vazias | 0 comentários
- **Hash lógico:** `b0a63bb558e2181a220d2800dfc57dd3e065c716`
- **Classes principais:** `StrategyMetricsRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyMetricsRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/run_metrics.py, app/api/v1/endpoints/runs.py.

### `app/storage/repositories/run_queries.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1316 bytes
- **Linhas:** 42 totais | 34 não vazias | 0 comentários
- **Hash lógico:** `e26595f83d77bcc366c62df003495c0cde8b3376`
- **Classes principais:** `StrategyRunQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyRunQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py, app/api/v1/endpoints/run_metrics.py.

### `app/storage/repositories/run_repository.py`

- **Papel provável:** Lê ou grava dados na camada de persistência
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1050 bytes
- **Linhas:** 30 totais | 26 não vazias | 0 comentários
- **Hash lógico:** `ff11b3d00847d6c41e9d93ddeef4f598b78a2cea`
- **Classes principais:** `StrategyRunRepository`
- **Imports/refs brutas:** `app.models.domain.strategy_run`, `app.storage.models`
- **Usa internamente:** `app/models/domain/strategy_run.py`, `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Lê ou grava dados na camada de persistência. Classes principais: StrategyRunRepository. Depende de: app/models/domain/strategy_run.py, app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

### `app/strategies/__init__.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Implementa regras de estratégia.

### `app/strategies/analysis_snapshot_builder.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 10346 bytes
- **Linhas:** 281 totais | 211 não vazias | 1 comentários
- **Hash lógico:** `570c6b0cac6e196c1dc69db3300f1896a3370e22`
- **Funções principais:** `_decimal_to_str`, `_classify_price_vs_ema`, `_classify_ema_alignment`, `_classify_slope`, `_classify_structure`, `_classify_rsi_zone`, `_classify_macd_proxy`, `_body_ratio`, `_classify_candle_type`, `_distance_label`, `build_analysis_snapshot`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.indicators.ema`, `app.indicators.rsi`, `app.models.domain.candle`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/indicators/ema.py`, `app/indicators/rsi.py`, `app/models/domain/candle.py`
- **Referenciado por:** `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`
- **Resumo técnico:** Implementa regras de estratégia. Funções principais: _decimal_to_str, _classify_price_vs_ema, _classify_ema_alignment, _classify_slope, _classify_structure, _classify_rsi_zone. Depende de: app/indicators/bollinger.py, app/indicators/ema.py, app/indicators/rsi.py, app/models/domain/candle.py. Referenciado por: app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py.

### `app/strategies/base.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 2607 bytes
- **Linhas:** 93 totais | 83 não vazias | 0 comentários
- **Hash lógico:** `74a0aed3b982929c049803d1dc2cfadbef63f2fb`
- **Classes principais:** `BaseStrategy`
- **Imports/refs brutas:** `abc`, `app.models.domain.candle`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.decisions`
- **Usa internamente:** `app/models/domain/candle.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/registry/strategy_registry.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: BaseStrategy. Depende de: app/models/domain/candle.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py, app/models/domain/strategy_run.py, app/strategies/decisions.py. Referenciado por: app/engine/case_engine.py, app/engine/run_engine.py, app/registry/strategy_registry.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py.

### `app/strategies/bollinger_reversal.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 12061 bytes
- **Linhas:** 323 totais | 275 não vazias | 1 comentários
- **Hash lógico:** `78e1969e8f393d468270bab6e214ecfc5307c427`
- **Classes principais:** `BollingerReversalStrategy`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.analysis_snapshot_builder`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: BollingerReversalStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

### `app/strategies/bollinger_walk_the_band.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 10867 bytes
- **Linhas:** 299 totais | 253 não vazias | 1 comentários
- **Hash lógico:** `d2a3f92827b30ac612f225d433389bb803d69d83`
- **Classes principais:** `BollingerWalkTheBandStrategy`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.analysis_snapshot_builder`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: BollingerWalkTheBandStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

### `app/strategies/catalog.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 138 bytes
- **Linhas:** 7 totais | 5 não vazias | 1 comentários
- **Hash lógico:** `2133564ca58200f04d11d18bf699a9bfd7929cf0`
- **Imports/refs brutas:** `.ff_fd`
- **Usa internamente:** `app/strategies/ff_fd.py`
- **Referenciado por:** `app/api/routes/strategies.py`
- **Resumo técnico:** Implementa regras de estratégia. Depende de: app/strategies/ff_fd.py. Referenciado por: app/api/routes/strategies.py.

### `app/strategies/decisions.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 546 bytes
- **Linhas:** 20 totais | 14 não vazias | 0 comentários
- **Hash lógico:** `b502205e25bf8bd2360d2dbb39943f8ad6266af8`
- **Classes principais:** `TriggerDecision`, `CaseCloseDecision`
- **Imports/refs brutas:** `app.models.domain.enums`, `decimal`, `pydantic`, `typing`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/engine/case_engine.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: TriggerDecision, CaseCloseDecision. Depende de: app/models/domain/enums.py. Referenciado por: app/engine/case_engine.py, app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/ff_fd.py.

### `app/strategies/ema_cross.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 17319 bytes
- **Linhas:** 442 totais | 382 não vazias | 1 comentários
- **Hash lógico:** `90ad7f9da2bd44f69f7fed5249d16b58d4819a10`
- **Classes principais:** `EmaCrossStrategy`
- **Imports/refs brutas:** `__future__`, `app.indicators.ema`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/ema.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: EmaCrossStrategy. Depende de: app/indicators/ema.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

### `app/strategies/ff_fd.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 12232 bytes
- **Linhas:** 348 totais | 298 não vazias | 1 comentários
- **Hash lógico:** `590355fc0f0b74f3d3d08e5e0f46dfa95be3d58f`
- **Classes principais:** `FfFdStrategy`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/strategies/catalog.py`, `app/strategies/ff_fd_mapper.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: FfFdStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/strategies/catalog.py, app/strategies/ff_fd_mapper.py.

### `app/strategies/ff_fd_mapper.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 21 totais | 18 não vazias | 1 comentários
- **Hash lógico:** `27bade996cb03551d5dd9b34d99f1eb3a40f40f0`
- **Funções principais:** `to_run_case_item`
- **Imports/refs brutas:** `app.strategies.ff_fd`
- **Usa internamente:** `app/strategies/ff_fd.py`
- **Resumo técnico:** Implementa regras de estratégia. Funções principais: to_run_case_item. Depende de: app/strategies/ff_fd.py.

### `app/strategies/rsi_reversal.py`

- **Papel provável:** Implementa regras de estratégia
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 7836 bytes
- **Linhas:** 222 totais | 186 não vazias | 1 comentários
- **Hash lógico:** `b4960f3e929f13e25783b43cf2d32c64a7cb98a5`
- **Classes principais:** `RsiReversalStrategy`
- **Imports/refs brutas:** `app.indicators.rsi`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/rsi.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementa regras de estratégia. Classes principais: RsiReversalStrategy. Depende de: app/indicators/rsi.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

### `app/utils/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Hash lógico:** `da39a3ee5e6b4b0d3255bfef95601890afd80709`
- **Resumo técnico:** Lógica de suporte do projeto.

### `app/utils/datetime_utils.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 2547 bytes
- **Linhas:** 79 totais | 58 não vazias | 0 comentários
- **Hash lógico:** `73a4380e9071541bcce9ed5dc6c5d5fb33bf5bfa`
- **Funções principais:** `ensure_naive_utc`, `timeframe_to_timedelta`, `floor_open_time`
- **Imports/refs brutas:** `datetime`
- **Referenciado por:** `app/services/candle_sync.py`, `app/services/realtime_ws.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: ensure_naive_utc, timeframe_to_timedelta, floor_open_time. Referenciado por: app/services/candle_sync.py, app/services/realtime_ws.py.

### `app/utils/ids.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 98 bytes
- **Linhas:** 5 totais | 3 não vazias | 0 comentários
- **Hash lógico:** `a223988a9ca2f43e1e0f3ad530b912c626d63fe4`
- **Funções principais:** `generate_id`
- **Imports/refs brutas:** `uuid`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: generate_id. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

### `gerar_mapa_projeto.py`

- **Papel provável:** Configura roteamento da API
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 33891 bytes
- **Linhas:** 972 totais | 823 não vazias | 4 comentários
- **Hash lógico:** `1c7e1a73a80d1a17a84133216dcaebc412261086`
- **Classes principais:** `EndpointInfo`, `FileInfo`
- **Funções principais:** `utc_now_iso`, `safe_read_text`, `sha1_text`, `count_comment_lines`, `normalize_posix`, `guess_language`, `guess_category`, `looks_like_binary_or_too_large`, `iter_project_files`, `extract_python_imports`, `extract_python_classes_functions`, `extract_python_router_prefix`, `extract_python_endpoints`, `extract_js_imports`, `extract_functions_by_regex`, `extract_classes_by_regex`, `extract_outbound_http`, `extract_outbound_ws`, `python_module_candidates_from_path`, `resolve_python_import`, `resolve_js_import`, `detect_probable_role`, `build_summary`, `analyze_file`, `build_relationships`, `enrich_roles_and_summaries`, `build_tree`, `build_overview`, `render_markdown`, `build_cache_payload`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time`, `typing`
- **Resumo técnico:** Configura roteamento da API. Classes principais: EndpointInfo, FileInfo. Funções principais: utc_now_iso, safe_read_text, sha1_text, count_comment_lines, normalize_posix, guess_language.

### `gerar_mapa_projeto_v2.py`

- **Papel provável:** Configura roteamento da API
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 43464 bytes
- **Linhas:** 939 totais | 822 não vazias | 1 comentários
- **Hash lógico:** `bc8303333e4ebf428026d932bfc0418b45083b5a`
- **Classes principais:** `EndpointInfo`, `FileInfo`
- **Funções principais:** `utc_now_iso`, `safe_read_text`, `sha1_text`, `count_comment_lines`, `normalize_posix`, `guess_language`, `guess_category`, `looks_like_binary_or_too_large`, `iter_project_files`, `extract_python_imports`, `extract_python_classes_functions`, `extract_python_router_prefix`, `extract_python_endpoints`, `extract_js_imports`, `extract_functions_by_regex`, `extract_classes_by_regex`, `extract_outbound_http`, `extract_outbound_ws`, `resolve_python_import`, `resolve_js_import`, `infer_project_profiles`, `detect_probable_role_generic`, `detect_probable_role_trader_bot`, `detect_workflow_generic`, `detect_workflow_trader_bot`, `build_summary`, `analyze_file`, `build_relationships`, `enrich_infos`, `build_tree`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time`, `typing`
- **Resumo técnico:** Configura roteamento da API. Classes principais: EndpointInfo, FileInfo. Funções principais: utc_now_iso, safe_read_text, sha1_text, count_comment_lines, normalize_posix, guess_language.

### `scripts/migrate_normalize_candles_symbols.py`

- **Papel provável:** Lógica de suporte do projeto
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 8268 bytes
- **Linhas:** 272 totais | 219 não vazias | 0 comentários
- **Hash lógico:** `0db5876fd6d1829afd2f93af53aa435fa137be04`
- **Funções principais:** `normalize_symbol_for_matching`, `normalize_symbol_for_storage`, `table_exists`, `fetch_all_candles`, `build_dedup_key`, `choose_best_row`, `preview_summary`, `build_migrated_rows`, `backup_database_file`, `recreate_candles_table`, `insert_migrated_rows`, `replace_old_table`, `print_after_summary`, `main`
- **Imports/refs brutas:** `__future__`, `pathlib`, `sqlite3`, `typing`
- **Resumo técnico:** Lógica de suporte do projeto. Funções principais: normalize_symbol_for_matching, normalize_symbol_for_storage, table_exists, fetch_all_candles, build_dedup_key, choose_best_row.

### `tests/test_comparisons.py`

- **Papel provável:** Ficheiro de testes
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 5886 bytes
- **Linhas:** 182 totais | 160 não vazias | 0 comentários
- **Hash lógico:** `b1a657bb9eaef638181ea8c891728205451c1b16`
- **Classes principais:** `DummyMetrics`, `DummyRun`, `DummyComparisonRepository`
- **Funções principais:** `test_compare_strategies_ignores_zero_case_runs_for_averages`, `test_compare_strategies_returns_zero_averages_when_all_runs_have_zero_cases`
- **Imports/refs brutas:** `app.services.comparison_service`, `decimal`
- **Usa internamente:** `app/services/comparison_service.py`
- **Resumo técnico:** Ficheiro de testes. Classes principais: DummyMetrics, DummyRun, DummyComparisonRepository. Funções principais: test_compare_strategies_ignores_zero_case_runs_for_averages, test_compare_strategies_returns_zero_averages_when_all_runs_have_zero_cases. Depende de: app/services/comparison_service.py.

### `tests/test_run_engine.py`

- **Papel provável:** Orquestra lógica principal de execução
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 8338 bytes
- **Linhas:** 273 totais | 238 não vazias | 0 comentários
- **Hash lógico:** `6b1492741ff12fe54ac7cb1901fe76e47a3ec7c3`
- **Classes principais:** `_BaseDummyStrategy`, `ClosingStrategy`, `NeverClosingStrategy`
- **Funções principais:** `build_candle`, `build_run`, `build_config`, `test_run_engine_closes_case_during_loop`, `test_run_engine_finalizes_open_case_as_timeout_at_end`
- **Imports/refs brutas:** `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.strategies.base`, `app.strategies.decisions`, `datetime`, `decimal`
- **Usa internamente:** `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Resumo técnico:** Orquestra lógica principal de execução. Classes principais: _BaseDummyStrategy, ClosingStrategy, NeverClosingStrategy. Funções principais: build_candle, build_run, build_config, test_run_engine_closes_case_during_loop, test_run_engine_finalizes_open_case_as_timeout_at_end. Depende de: app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py.
