# MAPA DO PROJETO

- **Gerado em:** 2026-04-16 10:56:13 UTC
- **Ficheiro de saída:** `MAPA_DO_PROJETO.md`
- **Raiz principal:** `G:/O meu disco/python/Trader-bot`

## Objetivo deste ficheiro

Este documento é reescrito automaticamente e tenta explicar o papel de cada ficheiro, os workflows críticos, as ligações internas, endpoints, integrações externas e, quando possível, o contrato backend <-> frontend.

## Ligações backend <-> frontend

- Nenhum repositório ligado foi analisado. Use `--linked-root` ou coloque o repositório irmão ao lado desta raiz.

## Projeto analisado: `Trader-bot`

- **Raiz:** `G:/O meu disco/python/Trader-bot`
- **Perfis detetados:** trader_bot_backend
- **Total de ficheiros:** 126

### Workflows críticos detectados
- Run histórica: `app/api/v1/endpoints/runs.py` -> query local de candles -> fallback para provider -> persistência de candles -> `app/engine/run_engine.py` -> persistência de runs/cases/métricas.
- Leitura de candles: `app/api/v1/endpoints/candles.py` -> `SessionLocal` -> `candle_queries.py` -> resposta serializada.
- Providers: `providers.py` -> `settings.py` -> `factory.py` -> devolução do provider ativo e lista disponível.
- Detalhe de run: `run_details.py` -> `run_queries.py` + `case_queries.py` + `metrics_queries.py` -> payload único para UI/diagnóstico.
- Estratégias: `strategy_registry.py` regista classes concretas em `app/strategies/`, consumidas por endpoints e engine.

### Estrutura

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
├── check_after_migration.py
├── check_candles.py
├── check_candles_edges_normalized.py
├── check_candles_normalized.py
├── check_case.py
├── check_db.py
├── check_symbol_variants.py
├── debug_db_runtime.py
├── find_cases_on_date.py
├── gerar_mapa_projeto.py
├── gerar_mapa_projeto_v2.py
├── gerar_mapa_projeto_v3.py
├── list_recent_strategy_cases.py
├── list_recent_strategy_runs.py
└── project_map_generator.py
```

### Distribuição por linguagem

| Linguagem | Quantidade |
|---|---:|
| python | 126 |

### Distribuição por categoria

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
| source | 32 |
| storage | 4 |
| strategy | 15 |

### Pontos de maior impacto

- `app/models/domain/candle.py` | referenciado por `22` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/models/domain/enums.py` | referenciado por `16` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/core/settings.py` | referenciado por `15` ficheiro(s) | usa `0` ficheiro(s) | papel: Centraliza settings globais do backend
- `app/storage/models.py` | referenciado por `13` ficheiro(s) | usa `1` ficheiro(s) | papel: Define tabelas e modelos persistidos
- `app/storage/database.py` | referenciado por `13` ficheiro(s) | usa `1` ficheiro(s) | papel: Configura engine SQLAlchemy e sessões da base de dados
- `app/models/domain/strategy_run.py` | referenciado por `13` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/models/domain/strategy_config.py` | referenciado por `13` ficheiro(s) | usa `0` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/models/domain/strategy_case.py` | referenciado por `12` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/schemas/run.py` | referenciado por `10` ficheiro(s) | usa `3` ficheiro(s) | papel: Contrato de entrada/saída da API
- `app/strategies/base.py` | referenciado por `9` ficheiro(s) | usa `6` ficheiro(s) | papel: Implementação concreta de estratégia de trading
- `app/strategies/decisions.py` | referenciado por `8` ficheiro(s) | usa `1` ficheiro(s) | papel: Implementação concreta de estratégia de trading
- `app/models/domain/strategy_definition.py` | referenciado por `7` ficheiro(s) | usa `1` ficheiro(s) | papel: Define modelos de domínio ou base de dados
- `app/providers/factory.py` | referenciado por `6` ficheiro(s) | usa `4` ficheiro(s) | papel: Resolve e instancia o provider de dados de mercado
- `app/storage/repositories/candle_queries.py` | referenciado por `6` ficheiro(s) | usa `1` ficheiro(s) | papel: Repositório de leitura/escrita na persistência
- `app/indicators/bollinger.py` | referenciado por `5` ficheiro(s) | usa `1` ficheiro(s) | papel: Lógica de suporte do projeto

### Endpoints detectados

- `GET /api/stage-tests/options` -> `app/api/routes/stage_tests.py` (get_stage_test_options)
- `POST /api/stage-tests/run` -> `app/api/routes/stage_tests.py` (post_stage_test_run)
- `GET /strategies` -> `app/api/routes/strategies.py` (list_strategies)
- `POST /batch-runs/historical` -> `app/api/v1/endpoints/batch_runs.py` (run_batch_historical)
- `GET /candles` -> `app/api/v1/endpoints/candles.py` (list_candles)
- `GET /candles/latest` -> `app/api/v1/endpoints/candles.py` (get_latest_candle)
- `GET /catalog/products` -> `app/api/v1/endpoints/catalog.py` (list_products)
- `GET /catalog/products/{product_code}` -> `app/api/v1/endpoints/catalog.py` (get_product)
- `GET /catalog/products/{product_code}/subproducts/{subproduct_code}` -> `app/api/v1/endpoints/catalog.py` (get_subproduct_items)
- `GET /comparisons/strategies` -> `app/api/v1/endpoints/comparisons.py` (compare_strategies)
- `GET /health` -> `app/api/v1/endpoints/health.py` (healthcheck)
- `GET /providers` -> `app/api/v1/endpoints/providers.py` (list_providers)
- `GET /run-cases/{run_id}` -> `app/api/v1/endpoints/run_cases.py` (list_run_cases)
- `GET /run-details/{run_id}` -> `app/api/v1/endpoints/run_details.py` (get_run_details)
- `GET /run-history` -> `app/api/v1/endpoints/run_history.py` (list_run_history)
- `DELETE /run-history` -> `app/api/v1/endpoints/run_history.py` (clear_run_history)
- `GET /run-metrics/{run_id}` -> `app/api/v1/endpoints/run_metrics.py` (get_run_metrics)
- `POST /run-metrics/{run_id}/recalculate` -> `app/api/v1/endpoints/run_metrics.py` (recalculate_run_metrics)
- `POST /runs/historical` -> `app/api/v1/endpoints/runs.py` (run_historical)
- `GET /options` -> `app/api/v1/endpoints/stage_tests.py` (get_stage_test_options)
- `POST /run` -> `app/api/v1/endpoints/stage_tests.py` (post_stage_test_run)
- `GET /strategies` -> `app/api/v1/endpoints/strategies.py` (list_strategies)
- `WEBSOCKET /ws` -> `app/api/v1/endpoints/ws.py` (websocket_feed)
- `GET /health` -> `app/main.py` (health)

### Integrações HTTP/WS detetadas

- `app/api/routes/stage_tests.py` -> `/api/stage-tests`
- `app/api/v1/endpoints/catalog.py` -> `/products/{product_code}`, `/products/{product_code}/subproducts/{subproduct_code}`
- `app/api/v1/endpoints/run_metrics.py` -> `/{run_id}/recalculate`
- `app/api/v1/router.py` -> `/api/v1`
- `app/core/settings.py` -> `https://api.binance.com`, `https://api.twelvedata.com`
- `app/main.py` -> `http://127.0.0.1:5173`, `http://localhost:5173`
- `gerar_mapa_projeto_v3.py` -> `/candles/latest`, `/run-details/{id}`, `/stage-tests/options`, `/stage-tests/run`
- `project_map_generator.py` -> `/storage/repositories/`

### Mapa ficheiro a ficheiro

#### `app/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/api/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/api/routes/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/api/routes/stage_tests.py`

- **Papel provável:** Expõe endpoints HTTP ou WebSocket
- **Workflow:** Recebe pedido externo, chama a camada interna associada e devolve resposta.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1263 bytes
- **Linhas:** 38 totais | 33 não vazias | 0 comentários
- **Funções principais:** `get_stage_test_options`, `post_stage_test_run`
- **Endpoints:** `GET /api/stage-tests/options` (get_stage_test_options); `POST /api/stage-tests/run` (post_stage_test_run)
- **Integrações HTTP:** `/api/stage-tests`
- **Paths/contratos encontrados:** `/api/stage-tests`
- **Imports/refs brutas:** `app.schemas.stage_tests`, `app.services.stage_tests_service`, `fastapi`
- **Usa internamente:** `app/schemas/stage_tests.py`, `app/services/stage_tests_service.py`
- **Resumo técnico:** Expõe endpoints HTTP ou WebSocket. Recebe pedido externo, chama a camada interna associada e devolve resposta. Rotas detectadas: GET /api/stage-tests/options, POST /api/stage-tests/run. Funções principais: get_stage_test_options, post_stage_test_run. Depende de: app/schemas/stage_tests.py, app/services/stage_tests_service.py.

#### `app/api/routes/strategies.py`

- **Papel provável:** Expõe endpoints HTTP ou WebSocket
- **Workflow:** Recebe pedido externo, chama a camada interna associada e devolve resposta.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 226 bytes
- **Linhas:** 12 totais | 7 não vazias | 1 comentários
- **Funções principais:** `list_strategies`
- **Endpoints:** `GET /strategies` (list_strategies)
- **Imports/refs brutas:** `...strategies.catalog`, `fastapi`
- **Usa internamente:** `app/strategies/catalog.py`
- **Resumo técnico:** Expõe endpoints HTTP ou WebSocket. Recebe pedido externo, chama a camada interna associada e devolve resposta. Rotas detectadas: GET /strategies. Funções principais: list_strategies. Depende de: app/strategies/catalog.py.

#### `app/api/v1/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/api/v1/endpoints/__init__.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.

#### `app/api/v1/endpoints/batch_runs.py`

- **Papel provável:** Endpoint ligado a runs, métricas, casos ou detalhe de execução
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 6014 bytes
- **Linhas:** 160 totais | 138 não vazias | 0 comentários
- **Tags:** `api_endpoint`, `runs`
- **Funções principais:** `_map_db_rows_to_domain_candles`, `run_batch_historical`
- **Endpoints:** `POST /batch-runs/historical` (run_batch_historical)
- **Imports/refs brutas:** `app.core.settings`, `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.providers.factory`, `app.registry.strategy_registry`, `app.schemas.batch_run`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.storage.repositories.case_repository`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_repository`, `app.utils.ids`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/providers/factory.py`, `app/registry/strategy_registry.py`, `app/schemas/batch_run.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_repository.py`, `app/utils/ids.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a runs, métricas, casos ou detalhe de execução. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: POST /batch-runs/historical. Funções principais: _map_db_rows_to_domain_candles, run_batch_historical. Depende de: app/core/settings.py, app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/candles.py`

- **Papel provável:** Expõe leitura de candles persistidos
- **Workflow:** Fluxo: request HTTP -> SessionLocal -> CandleQueryRepository.list_by_filters -> transformação para CandleResponse -> resposta da API.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 6839 bytes
- **Linhas:** 237 totais | 194 não vazias | 0 comentários
- **Funções principais:** `_build_candle_response`, `_normalize_provider`, `_timeframe_to_delta`, `_resolve_range`, `_sync_candles_if_needed`, `list_candles`, `get_latest_candle`
- **Endpoints:** `GET /candles` (list_candles); `GET /candles/latest` (get_latest_candle)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `datetime`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe leitura de candles persistidos. Fluxo: request HTTP -> SessionLocal -> CandleQueryRepository.list_by_filters -> transformação para CandleResponse -> resposta da API. Rotas detectadas: GET /candles, GET /candles/latest. Funções principais: _build_candle_response, _normalize_provider, _timeframe_to_delta, _resolve_range, _sync_candles_if_needed, list_candles. Depende de: app/core/settings.py, app/providers/factory.py, app/schemas/run.py, app/storage/database.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/catalog.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1413 bytes
- **Linhas:** 52 totais | 39 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Funções principais:** `list_products`, `get_product`, `get_subproduct_items`
- **Endpoints:** `GET /catalog/products` (list_products); `GET /catalog/products/{product_code}` (get_product); `GET /catalog/products/{product_code}/subproducts/{subproduct_code}` (get_subproduct_items)
- **Integrações HTTP:** `/products/{product_code}`, `/products/{product_code}/subproducts/{subproduct_code}`
- **Paths/contratos encontrados:** `/products/{product_code}`, `/products/{product_code}/subproducts/{subproduct_code}`
- **Imports/refs brutas:** `app.schemas.catalog`, `app.services.catalog_service`, `fastapi`
- **Usa internamente:** `app/schemas/catalog.py`, `app/services/catalog_service.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: GET /catalog/products, GET /catalog/products/{product_code}, GET /catalog/products/{product_code}/subproducts/{subproduct_code}. Funções principais: list_products, get_product, get_subproduct_items. Depende de: app/schemas/catalog.py, app/services/catalog_service.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/comparisons.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1093 bytes
- **Linhas:** 32 totais | 27 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Funções principais:** `compare_strategies`
- **Endpoints:** `GET /comparisons/strategies` (compare_strategies)
- **Imports/refs brutas:** `app.schemas.comparison`, `app.services.comparison_service`, `app.storage.database`, `app.storage.repositories.comparison_queries`, `fastapi`
- **Usa internamente:** `app/schemas/comparison.py`, `app/services/comparison_service.py`, `app/storage/database.py`, `app/storage/repositories/comparison_queries.py`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: GET /comparisons/strategies. Funções principais: compare_strategies. Depende de: app/schemas/comparison.py, app/services/comparison_service.py, app/storage/database.py, app/storage/repositories/comparison_queries.py.

#### `app/api/v1/endpoints/health.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 316 bytes
- **Linhas:** 16 totais | 11 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Funções principais:** `healthcheck`
- **Endpoints:** `GET /health` (healthcheck)
- **Imports/refs brutas:** `app.core.settings`, `fastapi`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: GET /health. Funções principais: healthcheck. Depende de: app/core/settings.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/providers.py`

- **Papel provável:** Expõe providers disponíveis e provider ativo
- **Workflow:** Fluxo: ler settings -> instanciar MarketDataProviderFactory -> listar providers -> devolver provider ativo e lista disponível.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 579 bytes
- **Linhas:** 18 totais | 13 não vazias | 0 comentários
- **Funções principais:** `list_providers`
- **Endpoints:** `GET /providers` (list_providers)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.schemas.provider`, `fastapi`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/schemas/provider.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Expõe providers disponíveis e provider ativo. Fluxo: ler settings -> instanciar MarketDataProviderFactory -> listar providers -> devolver provider ativo e lista disponível. Rotas detectadas: GET /providers. Funções principais: list_providers. Depende de: app/core/settings.py, app/providers/factory.py, app/schemas/provider.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/run_cases.py`

- **Papel provável:** Endpoint ligado a runs, métricas, casos ou detalhe de execução
- **Workflow:** Fluxo: request HTTP -> query de casos -> desserializar metadata_json -> devolver lista de casos.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1708 bytes
- **Linhas:** 45 totais | 39 não vazias | 0 comentários
- **Tags:** `api_endpoint`, `runs`
- **Funções principais:** `list_run_cases`
- **Endpoints:** `GET /run-cases/{run_id}` (list_run_cases)
- **Imports/refs brutas:** `app.schemas.run`, `app.storage.database`, `app.storage.repositories.case_queries`, `fastapi`, `json`
- **Usa internamente:** `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a runs, métricas, casos ou detalhe de execução. Fluxo: request HTTP -> query de casos -> desserializar metadata_json -> devolver lista de casos. Rotas detectadas: GET /run-cases/{run_id}. Funções principais: list_run_cases. Depende de: app/schemas/run.py, app/storage/database.py, app/storage/repositories/case_queries.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/run_details.py`

- **Papel provável:** Endpoint ligado a runs, métricas, casos ou detalhe de execução
- **Workflow:** Fluxo: request HTTP -> ler run + métricas + casos -> agregar em RunDetailsResponse.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 4210 bytes
- **Linhas:** 102 totais | 90 não vazias | 1 comentários
- **Tags:** `api_endpoint`, `runs`
- **Funções principais:** `get_run_details`
- **Endpoints:** `GET /run-details/{run_id}` (get_run_details)
- **Imports/refs brutas:** `app.schemas.run`, `app.schemas.run_details`, `app.storage.database`, `app.storage.repositories.case_queries`, `app.storage.repositories.metrics_queries`, `app.storage.repositories.run_queries`, `fastapi`, `json`
- **Usa internamente:** `app/schemas/run.py`, `app/schemas/run_details.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a runs, métricas, casos ou detalhe de execução. Fluxo: request HTTP -> ler run + métricas + casos -> agregar em RunDetailsResponse. Rotas detectadas: GET /run-details/{run_id}. Funções principais: get_run_details. Depende de: app/schemas/run.py, app/schemas/run_details.py, app/storage/database.py, app/storage/repositories/case_queries.py, app/storage/repositories/metrics_queries.py, app/storage/repositories/run_queries.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/run_history.py`

- **Papel provável:** Endpoint ligado a runs, métricas, casos ou detalhe de execução
- **Workflow:** Fluxo: request HTTP -> SessionLocal -> query de runs -> mapear linhas -> resposta.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 2524 bytes
- **Linhas:** 72 totais | 63 não vazias | 1 comentários
- **Tags:** `api_endpoint`, `runs`
- **Funções principais:** `list_run_history`, `clear_run_history`
- **Endpoints:** `GET /run-history` (list_run_history); `DELETE /run-history` (clear_run_history)
- **Imports/refs brutas:** `app.schemas.run`, `app.storage.database`, `app.storage.models`, `app.storage.repositories.run_queries`, `fastapi`
- **Usa internamente:** `app/schemas/run.py`, `app/storage/database.py`, `app/storage/models.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a runs, métricas, casos ou detalhe de execução. Fluxo: request HTTP -> SessionLocal -> query de runs -> mapear linhas -> resposta. Rotas detectadas: GET /run-history, DELETE /run-history. Funções principais: list_run_history, clear_run_history. Depende de: app/schemas/run.py, app/storage/database.py, app/storage/models.py, app/storage/repositories/run_queries.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/run_metrics.py`

- **Papel provável:** Endpoint ligado a runs, métricas, casos ou detalhe de execução
- **Workflow:** Fluxo: request HTTP -> query de métricas -> validar existência -> devolver payload.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 5933 bytes
- **Linhas:** 143 totais | 124 não vazias | 0 comentários
- **Tags:** `api_endpoint`, `runs`
- **Funções principais:** `_map_case_row_to_domain`, `get_run_metrics`, `recalculate_run_metrics`
- **Endpoints:** `GET /run-metrics/{run_id}` (get_run_metrics); `POST /run-metrics/{run_id}/recalculate` (recalculate_run_metrics)
- **Integrações HTTP:** `/{run_id}/recalculate`
- **Paths/contratos encontrados:** `/{run_id}/recalculate`
- **Imports/refs brutas:** `app.engine.metrics_engine`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.case_queries`, `app.storage.repositories.metrics_queries`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_queries`, `fastapi`, `json`
- **Usa internamente:** `app/engine/metrics_engine.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a runs, métricas, casos ou detalhe de execução. Fluxo: request HTTP -> query de métricas -> validar existência -> devolver payload. Rotas detectadas: GET /run-metrics/{run_id}, POST /run-metrics/{run_id}/recalculate. Funções principais: _map_case_row_to_domain, get_run_metrics, recalculate_run_metrics. Depende de: app/engine/metrics_engine.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/schemas/run.py, app/storage/database.py, app/storage/repositories/case_queries.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/runs.py`

- **Papel provável:** Executa runs históricas e faz fallback para provider quando faltam candles locais
- **Workflow:** Fluxo: request HTTP -> validar strategy no registry -> tentar ler candles locais -> se não existirem, usar provider configurado -> gravar candles -> executar RunEngine -> gravar run/cases/métricas -> devolver HistoricalRunResponse.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 8002 bytes
- **Linhas:** 208 totais | 182 não vazias | 0 comentários
- **Funções principais:** `_map_db_rows_to_domain_candles`, `run_historical`
- **Endpoints:** `POST /runs/historical` (run_historical)
- **Imports/refs brutas:** `app.core.settings`, `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.providers.factory`, `app.registry.strategy_registry`, `app.schemas.run`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.storage.repositories.case_repository`, `app.storage.repositories.metrics_repository`, `app.storage.repositories.run_repository`, `app.utils.ids`, `fastapi`, `logging`, `time`
- **Usa internamente:** `app/core/settings.py`, `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/providers/factory.py`, `app/registry/strategy_registry.py`, `app/schemas/run.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_repository.py`, `app/utils/ids.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Executa runs históricas e faz fallback para provider quando faltam candles locais. Fluxo: request HTTP -> validar strategy no registry -> tentar ler candles locais -> se não existirem, usar provider configurado -> gravar candles -> executar RunEngine -> gravar run/cases/métricas -> devolver HistoricalRunResponse. Rotas detectadas: POST /runs/historical. Funções principais: _map_db_rows_to_domain_candles, run_historical. Depende de: app/core/settings.py, app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/stage_tests.py`

- **Papel provável:** Endpoint ligado a Stage Tests
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1370 bytes
- **Linhas:** 41 totais | 35 não vazias | 0 comentários
- **Tags:** `api_endpoint`, `stage_tests`
- **Funções principais:** `get_stage_test_options`, `post_stage_test_run`
- **Endpoints:** `GET /options` (get_stage_test_options); `POST /run` (post_stage_test_run)
- **Imports/refs brutas:** `app.schemas.stage_tests`, `app.services.stage_tests_service`, `fastapi`
- **Usa internamente:** `app/schemas/stage_tests.py`, `app/services/stage_tests_service.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint ligado a Stage Tests. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: GET /options, POST /run. Funções principais: get_stage_test_options, post_stage_test_run. Depende de: app/schemas/stage_tests.py, app/services/stage_tests_service.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/strategies.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 576 bytes
- **Linhas:** 17 totais | 12 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Funções principais:** `list_strategies`
- **Endpoints:** `GET /strategies` (list_strategies)
- **Imports/refs brutas:** `app.registry.strategy_registry`, `app.schemas.strategy`, `fastapi`
- **Usa internamente:** `app/registry/strategy_registry.py`, `app/schemas/strategy.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: GET /strategies. Funções principais: list_strategies. Depende de: app/registry/strategy_registry.py, app/schemas/strategy.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/endpoints/ws.py`

- **Papel provável:** Endpoint do backend
- **Workflow:** Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 13985 bytes
- **Linhas:** 463 totais | 387 não vazias | 0 comentários
- **Tags:** `api_endpoint`
- **Funções principais:** `normalize_symbol`, `normalize_timeframe`, `normalize_datetime`, `timeframe_to_timedelta`, `timeframe_to_window`, `floor_time_to_bucket`, `serialize_candle_row`, `load_initial_candles`, `load_last_closed_candle`, `build_tick_from_last_closed`, `try_build_live_tick`, `emit_heartbeat`, `emit_provider_error`, `websocket_feed`
- **Endpoints:** `WEBSOCKET /ws` (websocket_feed)
- **Imports/refs brutas:** `app.core.settings`, `app.providers.factory`, `app.providers.twelvedata`, `app.storage.database`, `app.storage.repositories.candle_queries`, `asyncio`, `datetime`, `decimal`, `fastapi`, `json`
- **Usa internamente:** `app/core/settings.py`, `app/providers/factory.py`, `app/providers/twelvedata.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`
- **Referenciado por:** `app/api/v1/router.py`
- **Resumo técnico:** Endpoint do backend. Fluxo: receber pedido da API -> validar parâmetros -> chamar camada de domínio/persistência -> devolver resposta serializada. Rotas detectadas: WEBSOCKET /ws. Funções principais: normalize_symbol, normalize_timeframe, normalize_datetime, timeframe_to_timedelta, timeframe_to_window, floor_time_to_bucket. Depende de: app/core/settings.py, app/providers/factory.py, app/providers/twelvedata.py, app/storage/database.py, app/storage/repositories/candle_queries.py. Referenciado por: app/api/v1/router.py.

#### `app/api/v1/router.py`

- **Papel provável:** Agrega os routers versionados da API /api/v1
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `api`
- **Linguagem:** `python`
- **Tamanho:** 1639 bytes
- **Linhas:** 35 totais | 32 não vazias | 0 comentários
- **Integrações HTTP:** `/api/v1`
- **Paths/contratos encontrados:** `/api/v1`
- **Imports/refs brutas:** `app.api.v1.endpoints.batch_runs`, `app.api.v1.endpoints.candles`, `app.api.v1.endpoints.catalog`, `app.api.v1.endpoints.health`, `app.api.v1.endpoints.providers`, `app.api.v1.endpoints.run_cases`, `app.api.v1.endpoints.run_details`, `app.api.v1.endpoints.run_history`, `app.api.v1.endpoints.run_metrics`, `app.api.v1.endpoints.runs`, `app.api.v1.endpoints.stage_tests`, `app.api.v1.endpoints.strategies`, `app.api.v1.endpoints.ws`, `fastapi`
- **Usa internamente:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/catalog.py`, `app/api/v1/endpoints/health.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/stage_tests.py`, `app/api/v1/endpoints/strategies.py`, `app/api/v1/endpoints/ws.py`
- **Referenciado por:** `app/main.py`
- **Resumo técnico:** Agrega os routers versionados da API /api/v1. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Depende de: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/catalog.py, app/api/v1/endpoints/health.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/run_cases.py. Referenciado por: app/main.py.

#### `app/core/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/core/instrument_catalog.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 9610 bytes
- **Linhas:** 253 totais | 238 não vazias | 0 comentários
- **Classes principais:** `InstrumentCatalogService`
- **Imports/refs brutas:** `copy`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: InstrumentCatalogService.

#### `app/core/logging.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1269 bytes
- **Linhas:** 42 totais | 31 não vazias | 0 comentários
- **Funções principais:** `setup_logging`, `get_logger`
- **Imports/refs brutas:** `app.core.settings`, `logging`, `sys`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/main.py`, `app/services/candle_cache_sync.py`, `app/services/candle_sync.py`, `app/services/realtime_ws.py`, `app/services/stage_tests_service.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: setup_logging, get_logger. Depende de: app/core/settings.py. Referenciado por: app/main.py, app/services/candle_cache_sync.py, app/services/candle_sync.py, app/services/realtime_ws.py, app/services/stage_tests_service.py.

#### `app/core/settings.py`

- **Papel provável:** Centraliza settings globais do backend
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `config`
- **Linguagem:** `python`
- **Tamanho:** 1533 bytes
- **Linhas:** 46 totais | 33 não vazias | 0 comentários
- **Classes principais:** `Settings`
- **Funções principais:** `get_settings`
- **Integrações HTTP:** `https://api.binance.com`, `https://api.twelvedata.com`
- **Imports/refs brutas:** `functools`, `pydantic`, `pydantic_settings`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/health.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/core/logging.py`, `app/main.py`, `app/providers/binance.py`, `app/providers/twelvedata.py`, `app/services/candle_sync.py`, `app/services/stage_tests_service.py`, `app/stage_tests/runner.py`, `app/storage/database.py`, `debug_db_runtime.py`
- **Resumo técnico:** Centraliza settings globais do backend. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: Settings. Funções principais: get_settings. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/health.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py.

#### `app/engine/__init__.py`

- **Papel provável:** Orquestra lógica principal
- **Workflow:** Recebe entidades de domínio, coordena a lógica principal e produz um resultado agregado.
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Orquestra lógica principal. Recebe entidades de domínio, coordena a lógica principal e produz um resultado agregado.

#### `app/engine/case_engine.py`

- **Papel provável:** Atualiza e fecha casos ao longo dos candles
- **Workflow:** Fluxo: receber caso aberto + candle -> strategy.update_case -> strategy.should_close_case -> fechar quando aplicável.
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 1089 bytes
- **Linhas:** 36 totais | 31 não vazias | 0 comentários
- **Classes principais:** `CaseEngine`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.strategies.base`, `app.strategies.decisions`
- **Usa internamente:** `app/models/domain/candle.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/engine/run_engine.py`
- **Resumo técnico:** Atualiza e fecha casos ao longo dos candles. Fluxo: receber caso aberto + candle -> strategy.update_case -> strategy.should_close_case -> fechar quando aplicável. Classes principais: CaseEngine. Depende de: app/models/domain/candle.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/strategies/base.py, app/strategies/decisions.py. Referenciado por: app/engine/run_engine.py.

#### `app/engine/metrics_engine.py`

- **Papel provável:** Consolida métricas de resultados
- **Workflow:** Fluxo: receber casos fechados -> contar outcomes -> calcular taxas e médias -> devolver StrategyMetrics.
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 2548 bytes
- **Linhas:** 70 totais | 57 não vazias | 0 comentários
- **Classes principais:** `MetricsEngine`
- **Imports/refs brutas:** `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_metrics`, `decimal`
- **Usa internamente:** `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_metrics.py`
- **Referenciado por:** `app/api/v1/endpoints/run_metrics.py`, `app/engine/run_engine.py`
- **Resumo técnico:** Consolida métricas de resultados. Fluxo: receber casos fechados -> contar outcomes -> calcular taxas e médias -> devolver StrategyMetrics. Classes principais: MetricsEngine. Depende de: app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_metrics.py. Referenciado por: app/api/v1/endpoints/run_metrics.py, app/engine/run_engine.py.

#### `app/engine/run_engine.py`

- **Papel provável:** Orquestra a execução integral de uma run
- **Workflow:** Fluxo: iterar candles -> atualizar casos abertos -> avaliar trigger da estratégia -> abrir novos casos -> fechar run -> calcular métricas.
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 3781 bytes
- **Linhas:** 105 totais | 86 não vazias | 0 comentários
- **Classes principais:** `RunEngine`
- **Imports/refs brutas:** `app.engine.case_engine`, `app.engine.metrics_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.strategies.base`
- **Usa internamente:** `app/engine/case_engine.py`, `app/engine/metrics_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/strategies/base.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Orquestra a execução integral de uma run. Fluxo: iterar candles -> atualizar casos abertos -> avaliar trigger da estratégia -> abrir novos casos -> fechar run -> calcular métricas. Classes principais: RunEngine. Depende de: app/engine/case_engine.py, app/engine/metrics_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, tests/test_run_engine.py.

#### `app/indicators/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/indicators/atr.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1478 bytes
- **Linhas:** 52 totais | 37 não vazias | 1 comentários
- **Funções principais:** `average_true_range`, `average_true_range_series`
- **Imports/refs brutas:** `app.models.domain.candle`, `decimal`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: average_true_range, average_true_range_series. Depende de: app/models/domain/candle.py. Referenciado por: app/services/case_snapshot.py.

#### `app/indicators/bollinger.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 945 bytes
- **Linhas:** 36 totais | 24 não vazias | 0 comentários
- **Funções principais:** `bollinger_bands`
- **Imports/refs brutas:** `app.indicators.sma`, `decimal`, `math`
- **Usa internamente:** `app/indicators/sma.py`
- **Referenciado por:** `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ff_fd.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: bollinger_bands. Depende de: app/indicators/sma.py. Referenciado por: app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ff_fd.py.

#### `app/indicators/ema.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1134 bytes
- **Linhas:** 45 totais | 30 não vazias | 1 comentários
- **Funções principais:** `exponential_moving_average`, `exponential_moving_average_series`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/indicators/macd.py`, `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/ema_cross.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: exponential_moving_average, exponential_moving_average_series. Referenciado por: app/indicators/macd.py, app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/ema_cross.py.

#### `app/indicators/macd.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 2752 bytes
- **Linhas:** 102 totais | 78 não vazias | 1 comentários
- **Funções principais:** `macd`, `macd_series`
- **Imports/refs brutas:** `app.indicators.ema`, `decimal`
- **Usa internamente:** `app/indicators/ema.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: macd, macd_series. Depende de: app/indicators/ema.py. Referenciado por: app/services/case_snapshot.py.

#### `app/indicators/rsi.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1625 bytes
- **Linhas:** 54 totais | 37 não vazias | 1 comentários
- **Funções principais:** `relative_strength_index`, `relative_strength_index_series`, `_build_rsi`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/services/case_snapshot.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: relative_strength_index, relative_strength_index_series, _build_rsi. Referenciado por: app/services/case_snapshot.py, app/strategies/analysis_snapshot_builder.py, app/strategies/rsi_reversal.py.

#### `app/indicators/sma.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 324 bytes
- **Linhas:** 12 totais | 8 não vazias | 0 comentários
- **Funções principais:** `simple_moving_average`
- **Imports/refs brutas:** `decimal`
- **Referenciado por:** `app/indicators/bollinger.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: simple_moving_average. Referenciado por: app/indicators/bollinger.py.

#### `app/main.py`

- **Papel provável:** Inicializa a API FastAPI do backend Trader-Bot
- **Workflow:** Recebe pedido externo, chama a camada interna associada e devolve resposta.
- **Categoria:** `entrypoint`
- **Linguagem:** `python`
- **Tamanho:** 3393 bytes
- **Linhas:** 114 totais | 87 não vazias | 0 comentários
- **Funções principais:** `_resolve_sqlite_path`, `_get_sqlite_runtime_info`, `on_startup`, `health`
- **Endpoints:** `GET /health` (health)
- **Integrações HTTP:** `http://127.0.0.1:5173`, `http://localhost:5173`
- **Imports/refs brutas:** `app.api.v1.router`, `app.core.logging`, `app.core.settings`, `app.storage.database`, `app.storage.models`, `fastapi`, `fastapi.middleware.cors`, `pathlib`, `sqlalchemy`, `typing`
- **Usa internamente:** `app/api/v1/router.py`, `app/core/logging.py`, `app/core/settings.py`, `app/storage/database.py`, `app/storage/models.py`
- **Resumo técnico:** Inicializa a API FastAPI do backend Trader-Bot. Recebe pedido externo, chama a camada interna associada e devolve resposta. Rotas detectadas: GET /health. Funções principais: _resolve_sqlite_path, _get_sqlite_runtime_info, on_startup, health. Depende de: app/api/v1/router.py, app/core/logging.py, app/core/settings.py, app/storage/database.py, app/storage/models.py.

#### `app/models/__init__.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/models/domain/__init__.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/models/domain/asset.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 378 bytes
- **Linhas:** 14 totais | 11 não vazias | 0 comentários
- **Classes principais:** `Asset`
- **Imports/refs brutas:** `app.models.domain.enums`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: Asset. Depende de: app/models/domain/enums.py.

#### `app/models/domain/candle.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 408 bytes
- **Linhas:** 18 totais | 15 não vazias | 0 comentários
- **Classes principais:** `Candle`
- **Imports/refs brutas:** `datetime`, `decimal`, `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/indicators/atr.py`, `app/providers/base.py`, `app/providers/binance.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`, `app/services/candlestick_intelligence.py`, `app/services/case_snapshot.py`, `app/services/mock_market_data_service.py`, `app/stage_tests/runner.py`, `app/storage/repositories/candle_repository.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: Candle. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/case_engine.py, app/engine/run_engine.py, app/indicators/atr.py, app/providers/base.py.

#### `app/models/domain/enums.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 786 bytes
- **Linhas:** 41 totais | 29 não vazias | 0 comentários
- **Classes principais:** `MarketType`, `RunMode`, `RunStatus`, `CaseStatus`, `CaseOutcome`, `StrategyCategory`
- **Imports/refs brutas:** `enum`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/engine/metrics_engine.py`, `app/engine/run_engine.py`, `app/models/domain/asset.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/decisions.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: MarketType, RunMode, RunStatus, CaseStatus, CaseOutcome, StrategyCategory. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/run_metrics.py, app/api/v1/endpoints/runs.py, app/engine/metrics_engine.py, app/engine/run_engine.py, app/models/domain/asset.py.

#### `app/models/domain/strategy_case.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 932 bytes
- **Linhas:** 36 totais | 26 não vazias | 0 comentários
- **Classes principais:** `StrategyCase`
- **Imports/refs brutas:** `app.models.domain.enums`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/api/v1/endpoints/run_metrics.py`, `app/engine/case_engine.py`, `app/engine/metrics_engine.py`, `app/engine/run_engine.py`, `app/schemas/run.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyCase. Depende de: app/models/domain/enums.py. Referenciado por: app/api/v1/endpoints/run_metrics.py, app/engine/case_engine.py, app/engine/metrics_engine.py, app/engine/run_engine.py, app/schemas/run.py, app/strategies/base.py.

#### `app/models/domain/strategy_config.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 393 bytes
- **Linhas:** 14 totais | 12 não vazias | 0 comentários
- **Classes principais:** `StrategyConfig`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/services/case_snapshot.py`, `app/stage_tests/runner.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyConfig. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/case_engine.py, app/engine/run_engine.py, app/services/case_snapshot.py, app/stage_tests/runner.py.

#### `app/models/domain/strategy_definition.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 269 bytes
- **Linhas:** 11 totais | 8 não vazias | 0 comentários
- **Classes principais:** `StrategyDefinition`
- **Imports/refs brutas:** `app.models.domain.enums`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/schemas/strategy.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyDefinition. Depende de: app/models/domain/enums.py. Referenciado por: app/schemas/strategy.py, app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/ff_fd.py.

#### `app/models/domain/strategy_metrics.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 532 bytes
- **Linhas:** 20 totais | 15 não vazias | 0 comentários
- **Classes principais:** `StrategyMetrics`
- **Imports/refs brutas:** `decimal`, `pydantic`
- **Referenciado por:** `app/engine/metrics_engine.py`, `app/schemas/run.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyMetrics. Referenciado por: app/engine/metrics_engine.py, app/schemas/run.py.

#### `app/models/domain/strategy_run.py`

- **Papel provável:** Define modelos de domínio ou base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `model`
- **Linguagem:** `python`
- **Tamanho:** 648 bytes
- **Linhas:** 23 totais | 19 não vazias | 0 comentários
- **Classes principais:** `StrategyRun`
- **Imports/refs brutas:** `app.models.domain.enums`, `datetime`, `pydantic`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/engine/run_engine.py`, `app/schemas/run.py`, `app/stage_tests/runner.py`, `app/storage/repositories/run_repository.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Define modelos de domínio ou base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyRun. Depende de: app/models/domain/enums.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/engine/run_engine.py, app/schemas/run.py, app/stage_tests/runner.py, app/storage/repositories/run_repository.py.

#### `app/providers/__init__.py`

- **Papel provável:** Provider de integração com dados de mercado
- **Workflow:** Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Tags:** `provider`
- **Resumo técnico:** Provider de integração com dados de mercado. Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno.

#### `app/providers/base.py`

- **Papel provável:** Provider de integração com dados de mercado
- **Workflow:** Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 28 totais | 23 não vazias | 1 comentários
- **Tags:** `provider`
- **Classes principais:** `BaseMarketDataProvider`
- **Imports/refs brutas:** `abc`, `app.models.domain.candle`, `datetime`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/providers/binance.py`, `app/providers/factory.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`
- **Resumo técnico:** Provider de integração com dados de mercado. Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno. Classes principais: BaseMarketDataProvider. Depende de: app/models/domain/candle.py. Referenciado por: app/providers/binance.py, app/providers/factory.py, app/providers/mock.py, app/providers/twelvedata.py.

#### `app/providers/binance.py`

- **Papel provável:** Provider de integração com dados de mercado
- **Workflow:** Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 3923 bytes
- **Linhas:** 122 totais | 103 não vazias | 0 comentários
- **Tags:** `provider`
- **Classes principais:** `BinanceProvider`
- **Paths/contratos encontrados:** `/Trader-Bot/1.0`, `/application/json`
- **Imports/refs brutas:** `app.core.settings`, `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`, `json`, `urllib.error`, `urllib.parse`, `urllib.request`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/providers/factory.py`
- **Resumo técnico:** Provider de integração com dados de mercado. Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno. Classes principais: BinanceProvider. Depende de: app/core/settings.py, app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/providers/factory.py.

#### `app/providers/factory.py`

- **Papel provável:** Resolve e instancia o provider de dados de mercado
- **Workflow:** Fluxo: receber nome do provider -> escolher classe concreta -> devolver instância pronta.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 873 bytes
- **Linhas:** 24 totais | 18 não vazias | 0 comentários
- **Classes principais:** `MarketDataProviderFactory`
- **Imports/refs brutas:** `app.providers.base`, `app.providers.binance`, `app.providers.mock`, `app.providers.twelvedata`
- **Usa internamente:** `app/providers/base.py`, `app/providers/binance.py`, `app/providers/mock.py`, `app/providers/twelvedata.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/providers.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/services/candle_sync.py`
- **Resumo técnico:** Resolve e instancia o provider de dados de mercado. Fluxo: receber nome do provider -> escolher classe concreta -> devolver instância pronta. Classes principais: MarketDataProviderFactory. Depende de: app/providers/base.py, app/providers/binance.py, app/providers/mock.py, app/providers/twelvedata.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/providers.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py, app/services/candle_sync.py.

#### `app/providers/mock.py`

- **Papel provável:** Provider de integração com dados de mercado
- **Workflow:** Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 1975 bytes
- **Linhas:** 72 totais | 58 não vazias | 1 comentários
- **Tags:** `provider`
- **Classes principais:** `MockMarketDataProvider`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`
- **Usa internamente:** `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/providers/factory.py`
- **Resumo técnico:** Provider de integração com dados de mercado. Recebe parâmetros de mercado, consulta a origem externa e normaliza o retorno. Classes principais: MockMarketDataProvider. Depende de: app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/providers/factory.py.

#### `app/providers/twelvedata.py`

- **Papel provável:** Busca candles históricos no TwelveData e converte para o formato interno
- **Workflow:** Fluxo: receber symbol/timeframe/período -> construir request HTTP ao TwelveData -> validar payload -> converter para Candle interno.
- **Categoria:** `provider`
- **Linguagem:** `python`
- **Tamanho:** 9140 bytes
- **Linhas:** 262 totais | 216 não vazias | 0 comentários
- **Classes principais:** `ProviderQuotaExceededError`, `ProviderTemporaryCooldownError`, `TwelveDataProvider`
- **Funções principais:** `ensure_naive_utc`
- **Paths/contratos encontrados:** `/application/json`
- **Imports/refs brutas:** `app.core.settings`, `app.models.domain.candle`, `app.providers.base`, `datetime`, `decimal`, `json`, `math`, `threading`, `urllib.error`, `urllib.parse`, `urllib.request`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/providers/base.py`
- **Referenciado por:** `app/api/v1/endpoints/ws.py`, `app/providers/factory.py`
- **Resumo técnico:** Busca candles históricos no TwelveData e converte para o formato interno. Fluxo: receber symbol/timeframe/período -> construir request HTTP ao TwelveData -> validar payload -> converter para Candle interno. Classes principais: ProviderQuotaExceededError, ProviderTemporaryCooldownError, TwelveDataProvider. Funções principais: ensure_naive_utc. Depende de: app/core/settings.py, app/models/domain/candle.py, app/providers/base.py. Referenciado por: app/api/v1/endpoints/ws.py, app/providers/factory.py.

#### `app/registry/__init__.py`

- **Papel provável:** Regista e expõe estratégias disponíveis
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Tags:** `registry`
- **Resumo técnico:** Regista e expõe estratégias disponíveis. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/registry/strategy_registry.py`

- **Papel provável:** Regista e expõe estratégias disponíveis
- **Workflow:** Fluxo: instanciar estratégias concretas -> registar por key -> permitir lookup pelas APIs e engine.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 1616 bytes
- **Linhas:** 47 totais | 32 não vazias | 1 comentários
- **Tags:** `registry`
- **Classes principais:** `StrategyRegistry`
- **Funções principais:** `build_strategy_registry`
- **Imports/refs brutas:** `app.strategies.base`, `app.strategies.bollinger_reversal`, `app.strategies.bollinger_walk_the_band`, `app.strategies.ema_cross`, `app.strategies.rsi_reversal`
- **Usa internamente:** `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/rsi_reversal.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/strategies.py`, `app/stage_tests/runner.py`
- **Resumo técnico:** Regista e expõe estratégias disponíveis. Fluxo: instanciar estratégias concretas -> registar por key -> permitir lookup pelas APIs e engine. Classes principais: StrategyRegistry. Funções principais: build_strategy_registry. Depende de: app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/rsi_reversal.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/strategies.py, app/stage_tests/runner.py.

#### `app/schemas/__init__.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Tags:** `schema`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/schemas/batch_run.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 861 bytes
- **Linhas:** 35 totais | 25 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `BatchStrategyItemRequest`, `BatchHistoricalRunRequest`, `BatchHistoricalRunItemResponse`, `BatchHistoricalRunResponse`
- **Imports/refs brutas:** `app.schemas.run`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/schemas/run.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: BatchStrategyItemRequest, BatchHistoricalRunRequest, BatchHistoricalRunItemResponse, BatchHistoricalRunResponse. Depende de: app/schemas/run.py. Referenciado por: app/api/v1/endpoints/batch_runs.py.

#### `app/schemas/catalog.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 906 bytes
- **Linhas:** 40 totais | 28 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `CatalogProductSummary`, `CatalogSubproduct`, `CatalogInstrument`, `CatalogProductsResponse`, `CatalogProductResponse`, `CatalogItemsResponse`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/catalog.py`, `app/services/catalog_service.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: CatalogProductSummary, CatalogSubproduct, CatalogInstrument, CatalogProductsResponse, CatalogProductResponse, CatalogItemsResponse. Referenciado por: app/api/v1/endpoints/catalog.py, app/services/catalog_service.py.

#### `app/schemas/comparison.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 27 totais | 22 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `StrategyComparisonItemResponse`, `StrategyComparisonResponse`
- **Imports/refs brutas:** `decimal`, `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `app/services/comparison_service.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyComparisonItemResponse, StrategyComparisonResponse. Referenciado por: app/api/v1/endpoints/comparisons.py, app/services/comparison_service.py.

#### `app/schemas/provider.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 128 bytes
- **Linhas:** 6 totais | 4 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `ProviderListResponse`
- **Imports/refs brutas:** `pydantic`
- **Referenciado por:** `app/api/v1/endpoints/providers.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: ProviderListResponse. Referenciado por: app/api/v1/endpoints/providers.py.

#### `app/schemas/run.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 5756 bytes
- **Linhas:** 187 totais | 162 não vazias | 1 comentários
- **Tags:** `schema`
- **Classes principais:** `HistoricalRunRequest`, `CandleResponse`, `CandleListResponse`, `StrategyRunResponse`, `StrategyCaseResponse`, `StrategyMetricsResponse`, `HistoricalRunResponse`
- **Funções principais:** `build_run_response`, `build_case_response`, `build_metrics_response`, `build_historical_run_response`
- **Imports/refs brutas:** `app.models.domain.strategy_case`, `app.models.domain.strategy_metrics`, `app.models.domain.strategy_run`, `datetime`, `decimal`, `pydantic`
- **Usa internamente:** `app/models/domain/strategy_case.py`, `app/models/domain/strategy_metrics.py`, `app/models/domain/strategy_run.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/schemas/batch_run.py`, `app/schemas/run_details.py`, `app/services/mock_market_data_service.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: HistoricalRunRequest, CandleResponse, CandleListResponse, StrategyRunResponse, StrategyCaseResponse, StrategyMetricsResponse. Funções principais: build_run_response, build_case_response, build_metrics_response, build_historical_run_response. Depende de: app/models/domain/strategy_case.py, app/models/domain/strategy_metrics.py, app/models/domain/strategy_run.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py, app/api/v1/endpoints/run_metrics.py.

#### `app/schemas/run_details.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 312 bytes
- **Linhas:** 13 totais | 10 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `RunDetailsResponse`
- **Imports/refs brutas:** `app.schemas.run`, `pydantic`
- **Usa internamente:** `app/schemas/run.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: RunDetailsResponse. Depende de: app/schemas/run.py. Referenciado por: app/api/v1/endpoints/run_details.py.

#### `app/schemas/stage_tests.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 2440 bytes
- **Linhas:** 71 totais | 57 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `StageTestStrategyOptionResponse`, `StageTestOptionItemResponse`, `StageTestOptionsResponse`, `StageTestRunRequest`, `StageTestMetricsResponse`, `StageTestRunResponse`
- **Imports/refs brutas:** `__future__`, `pydantic`, `typing`
- **Referenciado por:** `app/api/routes/stage_tests.py`, `app/api/v1/endpoints/stage_tests.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StageTestStrategyOptionResponse, StageTestOptionItemResponse, StageTestOptionsResponse, StageTestRunRequest, StageTestMetricsResponse, StageTestRunResponse. Referenciado por: app/api/routes/stage_tests.py, app/api/v1/endpoints/stage_tests.py.

#### `app/schemas/strategy.py`

- **Papel provável:** Contrato de entrada/saída da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `schema`
- **Linguagem:** `python`
- **Tamanho:** 579 bytes
- **Linhas:** 21 totais | 16 não vazias | 0 comentários
- **Tags:** `schema`
- **Classes principais:** `StrategyListItemResponse`
- **Funções principais:** `build_strategy_list_item`
- **Imports/refs brutas:** `app.models.domain.strategy_definition`, `pydantic`
- **Usa internamente:** `app/models/domain/strategy_definition.py`
- **Referenciado por:** `app/api/v1/endpoints/strategies.py`
- **Resumo técnico:** Contrato de entrada/saída da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: StrategyListItemResponse. Funções principais: build_strategy_list_item. Depende de: app/models/domain/strategy_definition.py. Referenciado por: app/api/v1/endpoints/strategies.py.

#### `app/services/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/services/candle_cache_sync.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 2681 bytes
- **Linhas:** 70 totais | 61 não vazias | 9 comentários
- **Classes principais:** `CandleCacheSyncService`
- **Paths/contratos encontrados:** `/N/A`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.storage.cache_models`, `typing`
- **Usa internamente:** `app/core/logging.py`, `app/storage/cache_models.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: CandleCacheSyncService. Depende de: app/core/logging.py, app/storage/cache_models.py.

#### `app/services/candle_sync.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 9184 bytes
- **Linhas:** 242 totais | 205 não vazias | 6 comentários
- **Classes principais:** `CandleSyncResult`, `CandleSyncService`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.core.settings`, `app.providers.factory`, `app.storage.repositories.candle_queries`, `app.storage.repositories.candle_repository`, `app.utils.datetime_utils`, `dataclasses`, `datetime`
- **Usa internamente:** `app/core/logging.py`, `app/core/settings.py`, `app/providers/factory.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/utils/datetime_utils.py`
- **Referenciado por:** `app/services/realtime_ws.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: CandleSyncResult, CandleSyncService. Depende de: app/core/logging.py, app/core/settings.py, app/providers/factory.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py, app/utils/datetime_utils.py. Referenciado por: app/services/realtime_ws.py.

#### `app/services/candlestick_confirmation.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 18148 bytes
- **Linhas:** 521 totais | 402 não vazias | 1 comentários
- **Funções principais:** `_safe_str`, `_to_decimal`, `_append_unique`, `_normalize_direction`, `_is_buy`, `_is_sell`, `_is_bullish_pattern`, `_is_bearish_pattern`, `_extract_active_patterns`, `_has_favorable_pattern`, `_has_contrary_pattern`, `_trigger_is_favorable`, `_trigger_is_against_setup`, `_price_supports_setup`, `_rsi_supports_setup`, `_rsi_against_setup`, `_macd_supports_setup`, `_structure_supports_setup`, `_adx_strength`, `_macro_points_and_reasons`, `_apply_quality_ceiling`, `_raw_confirmation_score`, `_score_to_label`, `score_phase_3_confirmation`, `build_phase_3_confirmation_from_snapshot`
- **Imports/refs brutas:** `__future__`, `decimal`, `typing`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: _safe_str, _to_decimal, _append_unique, _normalize_direction, _is_buy, _is_sell.

#### `app/services/candlestick_intelligence.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 47792 bytes
- **Linhas:** 1374 totais | 1116 não vazias | 1 comentários
- **Funções principais:** `decimal_to_str`, `clamp`, `safe_ratio`, `normalize_direction`, `normalize_entry_location`, `normalize_cross_state`, `candle_color`, `candle_body`, `candle_range`, `upper_wick`, `lower_wick`, `body_ratio`, `upper_wick_ratio`, `lower_wick_ratio`, `close_position`, `classify_single_candle_pattern`, `classify_strength_class`, `build_candle_feature`, `is_bullish`, `is_bearish`, `body_midpoint`, `has_meaningful_body`, `is_small_star_body`, `strong_bearish_context`, `strong_bullish_context`, `detect_bullish_engulfing`, `detect_bearish_engulfing`, `detect_bullish_harami`, `detect_bearish_harami`, `detect_piercing_line`
- **Imports/refs brutas:** `__future__`, `app.models.domain.candle`, `decimal`, `typing`
- **Usa internamente:** `app/models/domain/candle.py`
- **Referenciado por:** `app/services/case_snapshot.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: decimal_to_str, clamp, safe_ratio, normalize_direction, normalize_entry_location, normalize_cross_state. Depende de: app/models/domain/candle.py. Referenciado por: app/services/case_snapshot.py.

#### `app/services/case_snapshot.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 34181 bytes
- **Linhas:** 996 totais | 797 não vazias | 1 comentários
- **Funções principais:** `build_case_metadata_snapshot`, `as_str`, `resolve_setup_direction`, `classify_cross_state`, `slope_label`, `classify_ema_alignment`, `classify_price_vs_average`, `classify_rsi_zone`, `classify_macd_state`, `calculate_band_position`, `classify_session`, `build_candle_stats`, `classify_candle_type`, `classify_market_structure`, `classify_entry_location`, `distance_to_recent_support`, `distance_to_recent_resistance`, `distance_to_level`, `classify_atr_regime`, `calculate_vwap`, `calculate_volume_ratio`, `calculate_volume_zscore`, `classify_volume_signal`, `classify_volume_context`, `calculate_bollinger_z_score`, `calculate_distance_outside_band`, `calculate_distance_from_nearest_band`, `average_directional_index_series`, `decimal_sqrt`, `quantize_decimal`
- **Imports/refs brutas:** `__future__`, `app.indicators.atr`, `app.indicators.bollinger`, `app.indicators.ema`, `app.indicators.macd`, `app.indicators.rsi`, `app.models.domain.candle`, `app.models.domain.strategy_config`, `app.services.candlestick_intelligence`, `decimal`
- **Usa internamente:** `app/indicators/atr.py`, `app/indicators/bollinger.py`, `app/indicators/ema.py`, `app/indicators/macd.py`, `app/indicators/rsi.py`, `app/models/domain/candle.py`, `app/models/domain/strategy_config.py`, `app/services/candlestick_intelligence.py`
- **Referenciado por:** `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: build_case_metadata_snapshot, as_str, resolve_setup_direction, classify_cross_state, slope_label, classify_ema_alignment. Depende de: app/indicators/atr.py, app/indicators/bollinger.py, app/indicators/ema.py, app/indicators/macd.py, app/indicators/rsi.py, app/models/domain/candle.py. Referenciado por: app/strategies/ema_cross.py, app/strategies/ff_fd.py, app/strategies/rsi_reversal.py.

#### `app/services/catalog_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 6104 bytes
- **Linhas:** 169 totais | 155 não vazias | 0 comentários
- **Classes principais:** `CatalogService`
- **Paths/contratos encontrados:** `/AUD/JPY`, `/AUD/USD`, `/EUR/GBP`, `/EUR/JPY`, `/EUR/USD`, `/GBP/JPY`, `/GBP/USD`, `/NZD/USD`, `/USD/CAD`, `/USD/CHF`, `/USD/JPY`
- **Imports/refs brutas:** `app.schemas.catalog`
- **Usa internamente:** `app/schemas/catalog.py`
- **Referenciado por:** `app/api/v1/endpoints/catalog.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: CatalogService. Depende de: app/schemas/catalog.py. Referenciado por: app/api/v1/endpoints/catalog.py.

#### `app/services/comparison_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 3481 bytes
- **Linhas:** 98 totais | 82 não vazias | 0 comentários
- **Classes principais:** `ComparisonService`
- **Imports/refs brutas:** `app.schemas.comparison`, `app.storage.repositories.comparison_queries`, `decimal`
- **Usa internamente:** `app/schemas/comparison.py`, `app/storage/repositories/comparison_queries.py`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `tests/test_comparisons.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: ComparisonService. Depende de: app/schemas/comparison.py, app/storage/repositories/comparison_queries.py. Referenciado por: app/api/v1/endpoints/comparisons.py, tests/test_comparisons.py.

#### `app/services/mock_market_data_service.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 1915 bytes
- **Linhas:** 66 totais | 53 não vazias | 0 comentários
- **Classes principais:** `MockMarketDataService`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.schemas.run`, `datetime`, `decimal`, `fastapi`
- **Usa internamente:** `app/models/domain/candle.py`, `app/schemas/run.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: MockMarketDataService. Depende de: app/models/domain/candle.py, app/schemas/run.py.

#### `app/services/realtime_ws.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 18269 bytes
- **Linhas:** 539 totais | 461 não vazias | 0 comentários
- **Classes principais:** `SubscriptionKey`, `RealtimeSubscriptionWorker`, `RealtimeWSManager`
- **Funções principais:** `row_to_ws_candle`
- **Imports/refs brutas:** `app.core.logging`, `app.services.candle_sync`, `app.storage.database`, `app.storage.repositories.candle_queries`, `app.utils.datetime_utils`, `asyncio`, `collections`, `dataclasses`, `datetime`, `fastapi`, `json`, `typing`
- **Usa internamente:** `app/core/logging.py`, `app/services/candle_sync.py`, `app/storage/database.py`, `app/storage/repositories/candle_queries.py`, `app/utils/datetime_utils.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: SubscriptionKey, RealtimeSubscriptionWorker, RealtimeWSManager. Funções principais: row_to_ws_candle. Depende de: app/core/logging.py, app/services/candle_sync.py, app/storage/database.py, app/storage/repositories/candle_queries.py, app/utils/datetime_utils.py.

#### `app/services/stage_tests_service.py`

- **Papel provável:** Ficheiro de testes
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `service`
- **Linguagem:** `python`
- **Tamanho:** 13602 bytes
- **Linhas:** 448 totais | 357 não vazias | 1 comentários
- **Funções principais:** `utc_now_iso`, `normalize_symbol`, `get_db_path`, `connect_db`, `list_stage_test_options`, `validate_symbol_timeframe`, `validate_strategy`, `build_stage_test_command`, `extract_metrics_from_stdout`, `extract_analysis_from_metrics`, `extract_cases_from_metrics`, `run_stage_test`
- **Imports/refs brutas:** `__future__`, `app.core.logging`, `app.core.settings`, `app.stage_tests.catalog`, `datetime`, `json`, `os`, `shlex`, `sqlite3`, `subprocess`, `typing`, `urllib.parse`
- **Usa internamente:** `app/core/logging.py`, `app/core/settings.py`, `app/stage_tests/catalog.py`
- **Referenciado por:** `app/api/routes/stage_tests.py`, `app/api/v1/endpoints/stage_tests.py`
- **Resumo técnico:** Ficheiro de testes. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: utc_now_iso, normalize_symbol, get_db_path, connect_db, list_stage_test_options, validate_symbol_timeframe. Depende de: app/core/logging.py, app/core/settings.py, app/stage_tests/catalog.py. Referenciado por: app/api/routes/stage_tests.py, app/api/v1/endpoints/stage_tests.py.

#### `app/stage_tests/catalog.py`

- **Papel provável:** Ficheiro de testes
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 1628 bytes
- **Linhas:** 54 totais | 44 não vazias | 4 comentários
- **Funções principais:** `list_stage_test_strategies`, `get_stage_test_strategy_keys`, `is_valid_stage_test_strategy`
- **Imports/refs brutas:** `__future__`, `typing`
- **Referenciado por:** `app/services/stage_tests_service.py`
- **Resumo técnico:** Ficheiro de testes. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: list_stage_test_strategies, get_stage_test_strategy_keys, is_valid_stage_test_strategy. Referenciado por: app/services/stage_tests_service.py.

#### `app/stage_tests/runner.py`

- **Papel provável:** Ficheiro de testes
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 38365 bytes
- **Linhas:** 1109 totais | 922 não vazias | 1 comentários
- **Funções principais:** `normalize_symbol`, `get_db_path`, `get_existing_candle_columns`, `load_candles_rows`, `parse_value`, `get_constructor_fields`, `instantiate_model`, `build_candle`, `parse_extra_args`, `build_strategy_config`, `build_strategy_run`, `safe_attr`, `decision_is_triggered`, `decision_should_close`, `summarize_case_outcome`, `pct`, `to_jsonable`, `read_case_metadata`, `read_analysis_snapshot_from_case`, `normalize_direction`, `build_rules_from_snapshot`, `build_indicators_from_snapshot`, `get_phase3_confirmation`, `build_case_metadata_summary`, `build_analysis_from_case`, `serialize_case`, `select_best_analysis_case`, `debug_first_serialized_case`, `main`
- **Imports/refs brutas:** `__future__`, `app.core.settings`, `app.models.domain.candle`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.registry.strategy_registry`, `app.stage_tests.strategy_mapper`, `argparse`, `datetime`, `decimal`, `inspect`, `json`, `os`, `sqlite3`, `typing`, `urllib.parse`, `uuid`
- **Usa internamente:** `app/core/settings.py`, `app/models/domain/candle.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/registry/strategy_registry.py`, `app/stage_tests/strategy_mapper.py`
- **Resumo técnico:** Ficheiro de testes. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: normalize_symbol, get_db_path, get_existing_candle_columns, load_candles_rows, parse_value, get_constructor_fields. Depende de: app/core/settings.py, app/models/domain/candle.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py, app/registry/strategy_registry.py, app/stage_tests/strategy_mapper.py.

#### `app/stage_tests/strategy_mapper.py`

- **Papel provável:** Implementa regras de estratégia
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 2447 bytes
- **Linhas:** 87 totais | 72 não vazias | 4 comentários
- **Funções principais:** `normalize_stage_test_strategy_key`, `resolve_runtime_strategy_key`, `get_default_parameters`
- **Imports/refs brutas:** `__future__`, `typing`
- **Referenciado por:** `app/stage_tests/runner.py`
- **Resumo técnico:** Implementa regras de estratégia. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: normalize_stage_test_strategy_key, resolve_runtime_strategy_key, get_default_parameters. Referenciado por: app/stage_tests/runner.py.

#### `app/storage/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/storage/cache_models.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 192 bytes
- **Linhas:** 9 totais | 7 não vazias | 1 comentários
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/services/candle_cache_sync.py`, `app/storage/repositories/candle_coverages.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Depende de: app/storage/models.py. Referenciado por: app/services/candle_cache_sync.py, app/storage/repositories/candle_coverages.py.

#### `app/storage/database.py`

- **Papel provável:** Configura engine SQLAlchemy e sessões da base de dados
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 555 bytes
- **Linhas:** 33 totais | 23 não vazias | 0 comentários
- **Classes principais:** `Base`
- **Funções principais:** `get_db_session`
- **Imports/refs brutas:** `app.core.settings`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/core/settings.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/comparisons.py`, `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/main.py`, `app/services/realtime_ws.py`, `app/storage/models.py`, `debug_db_runtime.py`
- **Resumo técnico:** Configura engine SQLAlchemy e sessões da base de dados. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: Base. Funções principais: get_db_session. Depende de: app/core/settings.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/comparisons.py, app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py.

#### `app/storage/models.py`

- **Papel provável:** Define tabelas e modelos persistidos
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `storage`
- **Linguagem:** `python`
- **Tamanho:** 5110 bytes
- **Linhas:** 120 totais | 94 não vazias | 1 comentários
- **Classes principais:** `Candle`, `CandleCoverage`, `StrategyRun`, `StrategyMetric`, `StrategyCase`
- **Imports/refs brutas:** `__future__`, `app.storage.database`, `datetime`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/database.py`
- **Referenciado por:** `app/api/v1/endpoints/run_history.py`, `app/main.py`, `app/storage/cache_models.py`, `app/storage/repositories/candle_queries.py`, `app/storage/repositories/candle_repository.py`, `app/storage/repositories/candle_upserts.py`, `app/storage/repositories/case_queries.py`, `app/storage/repositories/case_repository.py`, `app/storage/repositories/comparison_queries.py`, `app/storage/repositories/metrics_queries.py`, `app/storage/repositories/metrics_repository.py`, `app/storage/repositories/run_queries.py`, `app/storage/repositories/run_repository.py`
- **Resumo técnico:** Define tabelas e modelos persistidos. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: Candle, CandleCoverage, StrategyRun, StrategyMetric, StrategyCase. Depende de: app/storage/database.py. Referenciado por: app/api/v1/endpoints/run_history.py, app/main.py, app/storage/cache_models.py, app/storage/repositories/candle_queries.py, app/storage/repositories/candle_repository.py, app/storage/repositories/candle_upserts.py.

#### `app/storage/repositories/candle_coverages.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1780 bytes
- **Linhas:** 64 totais | 54 não vazias | 0 comentários
- **Tags:** `candles`, `repository`
- **Classes principais:** `CandleCoverageRepository`
- **Imports/refs brutas:** `app.storage.cache_models`, `datetime`
- **Usa internamente:** `app/storage/cache_models.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: CandleCoverageRepository. Depende de: app/storage/cache_models.py.

#### `app/storage/repositories/candle_queries.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros de mercado/período -> consultar CandleModel -> ordenar e limitar -> devolver linhas da base.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2070 bytes
- **Linhas:** 72 totais | 61 não vazias | 0 comentários
- **Tags:** `candles`, `repository`
- **Classes principais:** `CandleQueryRepository`
- **Imports/refs brutas:** `app.storage.models`, `datetime`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/runs.py`, `app/api/v1/endpoints/ws.py`, `app/services/candle_sync.py`, `app/services/realtime_ws.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros de mercado/período -> consultar CandleModel -> ordenar e limitar -> devolver linhas da base. Classes principais: CandleQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/runs.py, app/api/v1/endpoints/ws.py, app/services/candle_sync.py, app/services/realtime_ws.py.

#### `app/storage/repositories/candle_repository.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber candles de domínio -> inserir em CandleModel -> deduplicar por constraint -> commit -> refresh.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2304 bytes
- **Linhas:** 75 totais | 60 não vazias | 0 comentários
- **Tags:** `candles`, `repository`
- **Classes principais:** `CandleRepository`
- **Funções principais:** `_new_uuid`
- **Imports/refs brutas:** `app.models.domain.candle`, `app.storage.models`, `sqlalchemy.exc`, `sqlalchemy.orm.exc`, `uuid`
- **Usa internamente:** `app/models/domain/candle.py`, `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/candles.py`, `app/api/v1/endpoints/runs.py`, `app/services/candle_sync.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber candles de domínio -> inserir em CandleModel -> deduplicar por constraint -> commit -> refresh. Classes principais: CandleRepository. Funções principais: _new_uuid. Depende de: app/models/domain/candle.py, app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/candles.py, app/api/v1/endpoints/runs.py, app/services/candle_sync.py.

#### `app/storage/repositories/candle_upserts.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 2250 bytes
- **Linhas:** 70 totais | 57 não vazias | 0 comentários
- **Tags:** `candles`, `repository`
- **Classes principais:** `CandleUpsertRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `collections.abc`, `sqlalchemy.dialects.sqlite`, `sqlalchemy.orm`, `typing`
- **Usa internamente:** `app/storage/models.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: CandleUpsertRepository. Depende de: app/storage/models.py.

#### `app/storage/repositories/case_queries.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 409 bytes
- **Linhas:** 11 totais | 9 não vazias | 0 comentários
- **Tags:** `repository`
- **Classes principais:** `StrategyCaseQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_cases.py`, `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyCaseQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_cases.py, app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_metrics.py.

#### `app/storage/repositories/case_repository.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 518 bytes
- **Linhas:** 16 totais | 12 não vazias | 0 comentários
- **Tags:** `repository`
- **Classes principais:** `StrategyCaseRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyCaseRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

#### `app/storage/repositories/comparison_queries.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1344 bytes
- **Linhas:** 41 totais | 32 não vazias | 0 comentários
- **Tags:** `repository`
- **Classes principais:** `StrategyComparisonQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/comparisons.py`, `app/services/comparison_service.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyComparisonQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/comparisons.py, app/services/comparison_service.py.

#### `app/storage/repositories/metrics_queries.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 690 bytes
- **Linhas:** 22 totais | 17 não vazias | 1 comentários
- **Tags:** `repository`
- **Classes principais:** `StrategyMetricsQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyMetricsQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_metrics.py.

#### `app/storage/repositories/metrics_repository.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 533 bytes
- **Linhas:** 16 totais | 12 não vazias | 0 comentários
- **Tags:** `repository`
- **Classes principais:** `StrategyMetricsRepository`
- **Imports/refs brutas:** `__future__`, `app.storage.models`, `sqlalchemy`, `sqlalchemy.orm`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/run_metrics.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyMetricsRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/run_metrics.py, app/api/v1/endpoints/runs.py.

#### `app/storage/repositories/run_queries.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1316 bytes
- **Linhas:** 42 totais | 34 não vazias | 0 comentários
- **Tags:** `repository`, `runs`
- **Classes principais:** `StrategyRunQueryRepository`
- **Imports/refs brutas:** `app.storage.models`
- **Usa internamente:** `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/run_details.py`, `app/api/v1/endpoints/run_history.py`, `app/api/v1/endpoints/run_metrics.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyRunQueryRepository. Depende de: app/storage/models.py. Referenciado por: app/api/v1/endpoints/run_details.py, app/api/v1/endpoints/run_history.py, app/api/v1/endpoints/run_metrics.py.

#### `app/storage/repositories/run_repository.py`

- **Papel provável:** Repositório de leitura/escrita na persistência
- **Workflow:** Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos.
- **Categoria:** `repository`
- **Linguagem:** `python`
- **Tamanho:** 1050 bytes
- **Linhas:** 30 totais | 26 não vazias | 0 comentários
- **Tags:** `repository`, `runs`
- **Classes principais:** `StrategyRunRepository`
- **Imports/refs brutas:** `app.models.domain.strategy_run`, `app.storage.models`
- **Usa internamente:** `app/models/domain/strategy_run.py`, `app/storage/models.py`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Repositório de leitura/escrita na persistência. Fluxo: receber filtros ou entidades -> executar query/commit -> devolver linhas ou objetos persistidos. Classes principais: StrategyRunRepository. Depende de: app/models/domain/strategy_run.py, app/storage/models.py. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

#### `app/strategies/__init__.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Tags:** `strategy`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.

#### `app/strategies/analysis_snapshot_builder.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 10346 bytes
- **Linhas:** 281 totais | 211 não vazias | 1 comentários
- **Tags:** `strategy`
- **Funções principais:** `_decimal_to_str`, `_classify_price_vs_ema`, `_classify_ema_alignment`, `_classify_slope`, `_classify_structure`, `_classify_rsi_zone`, `_classify_macd_proxy`, `_body_ratio`, `_classify_candle_type`, `_distance_label`, `build_analysis_snapshot`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.indicators.ema`, `app.indicators.rsi`, `app.models.domain.candle`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/indicators/ema.py`, `app/indicators/rsi.py`, `app/models/domain/candle.py`
- **Referenciado por:** `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Funções principais: _decimal_to_str, _classify_price_vs_ema, _classify_ema_alignment, _classify_slope, _classify_structure, _classify_rsi_zone. Depende de: app/indicators/bollinger.py, app/indicators/ema.py, app/indicators/rsi.py, app/models/domain/candle.py. Referenciado por: app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py.

#### `app/strategies/base.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 2607 bytes
- **Linhas:** 93 totais | 83 não vazias | 0 comentários
- **Tags:** `strategy`
- **Classes principais:** `BaseStrategy`
- **Imports/refs brutas:** `abc`, `app.models.domain.candle`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.decisions`
- **Usa internamente:** `app/models/domain/candle.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/engine/case_engine.py`, `app/engine/run_engine.py`, `app/registry/strategy_registry.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: BaseStrategy. Depende de: app/models/domain/candle.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py, app/models/domain/strategy_run.py, app/strategies/decisions.py. Referenciado por: app/engine/case_engine.py, app/engine/run_engine.py, app/registry/strategy_registry.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py.

#### `app/strategies/bollinger_reversal.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 12061 bytes
- **Linhas:** 323 totais | 275 não vazias | 1 comentários
- **Tags:** `strategy`
- **Classes principais:** `BollingerReversalStrategy`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.analysis_snapshot_builder`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: BollingerReversalStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

#### `app/strategies/bollinger_walk_the_band.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 10867 bytes
- **Linhas:** 299 totais | 253 não vazias | 1 comentários
- **Tags:** `strategy`
- **Classes principais:** `BollingerWalkTheBandStrategy`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.strategies.analysis_snapshot_builder`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/strategies/analysis_snapshot_builder.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: BollingerWalkTheBandStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

#### `app/strategies/catalog.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 138 bytes
- **Linhas:** 7 totais | 5 não vazias | 1 comentários
- **Tags:** `strategy`
- **Imports/refs brutas:** `.ff_fd`
- **Usa internamente:** `app/strategies/ff_fd.py`
- **Referenciado por:** `app/api/routes/strategies.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Depende de: app/strategies/ff_fd.py. Referenciado por: app/api/routes/strategies.py.

#### `app/strategies/decisions.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 546 bytes
- **Linhas:** 20 totais | 14 não vazias | 0 comentários
- **Tags:** `strategy`
- **Classes principais:** `TriggerDecision`, `CaseCloseDecision`
- **Imports/refs brutas:** `app.models.domain.enums`, `decimal`, `pydantic`, `typing`
- **Usa internamente:** `app/models/domain/enums.py`
- **Referenciado por:** `app/engine/case_engine.py`, `app/strategies/base.py`, `app/strategies/bollinger_reversal.py`, `app/strategies/bollinger_walk_the_band.py`, `app/strategies/ema_cross.py`, `app/strategies/ff_fd.py`, `app/strategies/rsi_reversal.py`, `tests/test_run_engine.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: TriggerDecision, CaseCloseDecision. Depende de: app/models/domain/enums.py. Referenciado por: app/engine/case_engine.py, app/strategies/base.py, app/strategies/bollinger_reversal.py, app/strategies/bollinger_walk_the_band.py, app/strategies/ema_cross.py, app/strategies/ff_fd.py.

#### `app/strategies/ema_cross.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 17319 bytes
- **Linhas:** 442 totais | 382 não vazias | 1 comentários
- **Tags:** `strategy`
- **Classes principais:** `EmaCrossStrategy`
- **Imports/refs brutas:** `__future__`, `app.indicators.ema`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/ema.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: EmaCrossStrategy. Depende de: app/indicators/ema.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

#### `app/strategies/ff_fd.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 12232 bytes
- **Linhas:** 348 totais | 298 não vazias | 1 comentários
- **Tags:** `strategy`
- **Classes principais:** `FfFdStrategy`
- **Paths/contratos encontrados:** `/FF/FD`
- **Imports/refs brutas:** `app.indicators.bollinger`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/bollinger.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/strategies/catalog.py`, `app/strategies/ff_fd_mapper.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: FfFdStrategy. Depende de: app/indicators/bollinger.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/strategies/catalog.py, app/strategies/ff_fd_mapper.py.

#### `app/strategies/ff_fd_mapper.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 687 bytes
- **Linhas:** 21 totais | 18 não vazias | 1 comentários
- **Tags:** `strategy`
- **Funções principais:** `to_run_case_item`
- **Imports/refs brutas:** `app.strategies.ff_fd`
- **Usa internamente:** `app/strategies/ff_fd.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Funções principais: to_run_case_item. Depende de: app/strategies/ff_fd.py.

#### `app/strategies/rsi_reversal.py`

- **Papel provável:** Implementação concreta de estratégia de trading
- **Workflow:** Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 7836 bytes
- **Linhas:** 222 totais | 186 não vazias | 1 comentários
- **Tags:** `strategy`
- **Classes principais:** `RsiReversalStrategy`
- **Imports/refs brutas:** `app.indicators.rsi`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_definition`, `app.models.domain.strategy_run`, `app.services.case_snapshot`, `app.strategies.base`, `app.strategies.decisions`, `decimal`
- **Usa internamente:** `app/indicators/rsi.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_definition.py`, `app/models/domain/strategy_run.py`, `app/services/case_snapshot.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Referenciado por:** `app/registry/strategy_registry.py`
- **Resumo técnico:** Implementação concreta de estratégia de trading. Fluxo: receber candles/config -> calcular indicadores -> avaliar trigger -> criar/update/fechar casos conforme a lógica da estratégia. Classes principais: RsiReversalStrategy. Depende de: app/indicators/rsi.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_definition.py. Referenciado por: app/registry/strategy_registry.py.

#### `app/utils/__init__.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 0 bytes
- **Linhas:** 0 totais | 0 não vazias | 0 comentários
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `app/utils/datetime_utils.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 2547 bytes
- **Linhas:** 79 totais | 58 não vazias | 0 comentários
- **Funções principais:** `ensure_naive_utc`, `timeframe_to_timedelta`, `floor_open_time`
- **Imports/refs brutas:** `datetime`
- **Referenciado por:** `app/services/candle_sync.py`, `app/services/realtime_ws.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: ensure_naive_utc, timeframe_to_timedelta, floor_open_time. Referenciado por: app/services/candle_sync.py, app/services/realtime_ws.py.

#### `app/utils/ids.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 98 bytes
- **Linhas:** 5 totais | 3 não vazias | 0 comentários
- **Funções principais:** `generate_id`
- **Imports/refs brutas:** `uuid`
- **Referenciado por:** `app/api/v1/endpoints/batch_runs.py`, `app/api/v1/endpoints/runs.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: generate_id. Referenciado por: app/api/v1/endpoints/batch_runs.py, app/api/v1/endpoints/runs.py.

#### `check_after_migration.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 633 bytes
- **Linhas:** 39 totais | 32 não vazias | 0 comentários
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `check_candles.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 382 bytes
- **Linhas:** 14 totais | 9 não vazias | 0 comentários
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `check_candles_edges_normalized.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 852 bytes
- **Linhas:** 49 totais | 42 não vazias | 0 comentários
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `check_candles_normalized.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 530 bytes
- **Linhas:** 27 totais | 21 não vazias | 0 comentários
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `check_case.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 379 bytes
- **Linhas:** 26 totais | 20 não vazias | 0 comentários
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `check_db.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 3576 bytes
- **Linhas:** 139 totais | 118 não vazias | 0 comentários
- **Funções principais:** `print_title`, `main`
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `pathlib`, `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: print_title, main.

#### `check_symbol_variants.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 552 bytes
- **Linhas:** 30 totais | 24 não vazias | 0 comentários
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `debug_db_runtime.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 548 bytes
- **Linhas:** 20 totais | 15 não vazias | 0 comentários
- **Imports/refs brutas:** `app.core.settings`, `app.storage.database`, `os`, `pathlib`
- **Usa internamente:** `app/core/settings.py`, `app/storage/database.py`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Depende de: app/core/settings.py, app/storage/database.py.

#### `find_cases_on_date.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 552 bytes
- **Linhas:** 34 totais | 28 não vazias | 0 comentários
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `gerar_mapa_projeto.py`

- **Papel provável:** Configura roteamento da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 33891 bytes
- **Linhas:** 972 totais | 823 não vazias | 4 comentários
- **Classes principais:** `EndpointInfo`, `FileInfo`
- **Funções principais:** `utc_now_iso`, `safe_read_text`, `sha1_text`, `count_comment_lines`, `normalize_posix`, `guess_language`, `guess_category`, `looks_like_binary_or_too_large`, `iter_project_files`, `extract_python_imports`, `extract_python_classes_functions`, `extract_python_router_prefix`, `extract_python_endpoints`, `extract_js_imports`, `extract_functions_by_regex`, `extract_classes_by_regex`, `extract_outbound_http`, `extract_outbound_ws`, `python_module_candidates_from_path`, `resolve_python_import`, `resolve_js_import`, `detect_probable_role`, `build_summary`, `analyze_file`, `build_relationships`, `enrich_roles_and_summaries`, `build_tree`, `build_overview`, `render_markdown`, `build_cache_payload`
- **Paths/contratos encontrados:** `/{base}/index.js`, `/{base}/index.jsx`, `/{base}/index.ts`, `/{base}/index.tsx`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time`, `typing`
- **Resumo técnico:** Configura roteamento da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: EndpointInfo, FileInfo. Funções principais: utc_now_iso, safe_read_text, sha1_text, count_comment_lines, normalize_posix, guess_language.

#### `gerar_mapa_projeto_v2.py`

- **Papel provável:** Configura roteamento da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 43464 bytes
- **Linhas:** 939 totais | 822 não vazias | 1 comentários
- **Classes principais:** `EndpointInfo`, `FileInfo`
- **Funções principais:** `utc_now_iso`, `safe_read_text`, `sha1_text`, `count_comment_lines`, `normalize_posix`, `guess_language`, `guess_category`, `looks_like_binary_or_too_large`, `iter_project_files`, `extract_python_imports`, `extract_python_classes_functions`, `extract_python_router_prefix`, `extract_python_endpoints`, `extract_js_imports`, `extract_functions_by_regex`, `extract_classes_by_regex`, `extract_outbound_http`, `extract_outbound_ws`, `resolve_python_import`, `resolve_js_import`, `infer_project_profiles`, `detect_probable_role_generic`, `detect_probable_role_trader_bot`, `detect_workflow_generic`, `detect_workflow_trader_bot`, `build_summary`, `analyze_file`, `build_relationships`, `enrich_infos`, `build_tree`
- **Paths/contratos encontrados:** `/app/api/v1/endpoints`, `/app/api/v1/endpoints/candles.py`, `/app/api/v1/endpoints/providers.py`, `/app/api/v1/endpoints/run_cases.py`, `/app/api/v1/endpoints/run_details.py`, `/app/api/v1/endpoints/run_history.py`, `/app/api/v1/endpoints/run_metrics.py`, `/app/api/v1/endpoints/runs.py`, `/app/api/v1/endpoints/strategies.py`, `/app/api/v1/router.py`, `/app/core/settings.py`, `/app/engine`, `/app/engine/case_engine.py`, `/app/engine/metrics_engine.py`, `/app/engine/run_engine.py`, `/app/main.py`, `/app/providers`, `/app/providers/factory.py`, `/app/providers/twelvedata.py`, `/app/registry/strategy_registry.py`, `/app/storage/database.py`, `/app/storage/models.py`, `/app/storage/repositories`, `/app/storage/repositories/candle_queries.py`, `/app/storage/repositories/candle_repository.py`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time`, `typing`
- **Resumo técnico:** Configura roteamento da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: EndpointInfo, FileInfo. Funções principais: utc_now_iso, safe_read_text, sha1_text, count_comment_lines, normalize_posix, guess_language.

#### `gerar_mapa_projeto_v3.py`

- **Papel provável:** Configura roteamento da API
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 61887 bytes
- **Linhas:** 1412 totais | 1224 não vazias | 2 comentários
- **Classes principais:** `EndpointInfo`, `FileInfo`, `ProjectAnalysis`, `ContractLink`
- **Funções principais:** `utc_now_iso`, `safe_read_text`, `sha1_text`, `count_comment_lines`, `normalize_posix`, `guess_language`, `guess_category`, `looks_like_binary_or_too_large`, `iter_project_files`, `extract_python_imports`, `extract_python_classes_functions`, `extract_python_router_prefix`, `extract_python_endpoints`, `extract_js_imports`, `extract_functions_by_regex`, `extract_classes_by_regex`, `normalize_url_like`, `extract_outbound_http`, `extract_outbound_ws`, `extract_path_refs`, `resolve_python_import`, `resolve_js_import`, `infer_project_profiles`, `detect_probable_role_generic`, `detect_probable_role_trader_bot_backend`, `detect_probable_role_trader_bot_frontend`, `detect_workflow_generic`, `detect_workflow_trader_bot_backend`, `detect_workflow_trader_bot_frontend`, `build_summary`
- **Integrações HTTP:** `/candles/latest`, `/run-details/{id}`, `/stage-tests/options`, `/stage-tests/run`
- **Paths/contratos encontrados:** `/candles/latest`, `/run-details/{id}`, `/stage-tests/options`, `/stage-tests/run`, `/app/api/v1/endpoints`, `/app/api/v1/endpoints/candles.py`, `/app/api/v1/endpoints/providers.py`, `/app/api/v1/endpoints/run_cases.py`, `/app/api/v1/endpoints/run_details.py`, `/app/api/v1/endpoints/run_history.py`, `/app/api/v1/endpoints/run_metrics.py`, `/app/api/v1/endpoints/runs.py`, `/app/api/v1/router.py`, `/app/core/settings.py`, `/app/engine/case_engine.py`, `/app/engine/metrics_engine.py`, `/app/engine/run_engine.py`, `/app/main.py`, `/app/providers`, `/app/providers/factory.py`, `/app/providers/twelvedata.py`, `/app/registry`, `/app/registry/strategy_registry.py`, `/app/schemas`, `/app/storage/database.py`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `hashlib`, `json`, `os`, `pathlib`, `re`, `sys`, `time`, `typing`
- **Resumo técnico:** Configura roteamento da API. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: EndpointInfo, FileInfo, ProjectAnalysis, ContractLink. Funções principais: utc_now_iso, safe_read_text, sha1_text, count_comment_lines, normalize_posix, guess_language.

#### `list_recent_strategy_cases.py`

- **Papel provável:** Implementa regras de estratégia
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 519 bytes
- **Linhas:** 34 totais | 28 não vazias | 0 comentários
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Implementa regras de estratégia. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `list_recent_strategy_runs.py`

- **Papel provável:** Implementa regras de estratégia
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `strategy`
- **Linguagem:** `python`
- **Tamanho:** 505 bytes
- **Linhas:** 34 totais | 28 não vazias | 0 comentários
- **Paths/contratos encontrados:** `/EUR/USD`
- **Imports/refs brutas:** `sqlite3`
- **Resumo técnico:** Implementa regras de estratégia. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.

#### `project_map_generator.py`

- **Papel provável:** Consome HTTP
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 27553 bytes
- **Linhas:** 757 totais | 655 não vazias | 0 comentários
- **Classes principais:** `FileInfo`
- **Funções principais:** `is_text_file`, `should_ignore`, `read_text_safe`, `clean_line`, `first_meaningful_lines`, `extract_leading_comment`, `normalize_module_to_path`, `try_candidates`, `resolve_python_import`, `resolve_js_import`, `classify_role`, `summarize_from_role`, `parse_python`, `parse_jsts`, `collect_files`, `build_reverse_graph`, `section_global_overview`, `section_detected_workflows`, `format_list`, `file_section`, `build_document`, `main`
- **Integrações HTTP:** `/storage/repositories/`
- **Paths/contratos encontrados:** `/storage/repositories`, `/app/api/v1/endpoints/candles.py`, `/app/api/v1/endpoints/runs.py`, `/app/engine/run_engine.py`, `/app/main.py`, `/app/providers/factory.py`, `/app/providers/twelvedata.py`, `/app/schemas/run.py`, `/app/storage/repositories/candle_queries.py`, `/app/storage/repositories/candle_repository.py`, `/app/storage/repositories/run_repository.py`, `/web/src/hooks/useCandles.ts`, `/web/src/hooks/useRealtimeFeed.ts`, `/web/src/main.tsx`, `/{base}/__init__.py`, `/{mod_path}/__init__.py`
- **Imports/refs brutas:** `__future__`, `argparse`, `ast`, `collections`, `dataclasses`, `datetime`, `os`, `pathlib`, `re`, `typing`
- **Resumo técnico:** Consome HTTP. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: FileInfo. Funções principais: is_text_file, should_ignore, read_text_safe, clean_line, first_meaningful_lines, extract_leading_comment.

#### `scripts/migrate_normalize_candles_symbols.py`

- **Papel provável:** Lógica de suporte do projeto
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 8268 bytes
- **Linhas:** 272 totais | 219 não vazias | 0 comentários
- **Funções principais:** `normalize_symbol_for_matching`, `normalize_symbol_for_storage`, `table_exists`, `fetch_all_candles`, `build_dedup_key`, `choose_best_row`, `preview_summary`, `build_migrated_rows`, `backup_database_file`, `recreate_candles_table`, `insert_migrated_rows`, `replace_old_table`, `print_after_summary`, `main`
- **Imports/refs brutas:** `__future__`, `pathlib`, `sqlite3`, `typing`
- **Resumo técnico:** Lógica de suporte do projeto. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Funções principais: normalize_symbol_for_matching, normalize_symbol_for_storage, table_exists, fetch_all_candles, build_dedup_key, choose_best_row.

#### `tests/test_comparisons.py`

- **Papel provável:** Ficheiro de testes
- **Workflow:** Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte.
- **Categoria:** `source`
- **Linguagem:** `python`
- **Tamanho:** 5886 bytes
- **Linhas:** 182 totais | 160 não vazias | 0 comentários
- **Classes principais:** `DummyMetrics`, `DummyRun`, `DummyComparisonRepository`
- **Funções principais:** `test_compare_strategies_ignores_zero_case_runs_for_averages`, `test_compare_strategies_returns_zero_averages_when_all_runs_have_zero_cases`
- **Imports/refs brutas:** `app.services.comparison_service`, `decimal`
- **Usa internamente:** `app/services/comparison_service.py`
- **Resumo técnico:** Ficheiro de testes. Lê dependências necessárias, executa a sua responsabilidade principal e devolve dados para a camada seguinte. Classes principais: DummyMetrics, DummyRun, DummyComparisonRepository. Funções principais: test_compare_strategies_ignores_zero_case_runs_for_averages, test_compare_strategies_returns_zero_averages_when_all_runs_have_zero_cases. Depende de: app/services/comparison_service.py.

#### `tests/test_run_engine.py`

- **Papel provável:** Orquestra lógica principal
- **Workflow:** Recebe entidades de domínio, coordena a lógica principal e produz um resultado agregado.
- **Categoria:** `engine`
- **Linguagem:** `python`
- **Tamanho:** 8338 bytes
- **Linhas:** 273 totais | 238 não vazias | 0 comentários
- **Classes principais:** `_BaseDummyStrategy`, `ClosingStrategy`, `NeverClosingStrategy`
- **Funções principais:** `build_candle`, `build_run`, `build_config`, `test_run_engine_closes_case_during_loop`, `test_run_engine_finalizes_open_case_as_timeout_at_end`
- **Imports/refs brutas:** `app.engine.run_engine`, `app.models.domain.candle`, `app.models.domain.enums`, `app.models.domain.strategy_case`, `app.models.domain.strategy_config`, `app.models.domain.strategy_run`, `app.strategies.base`, `app.strategies.decisions`, `datetime`, `decimal`
- **Usa internamente:** `app/engine/run_engine.py`, `app/models/domain/candle.py`, `app/models/domain/enums.py`, `app/models/domain/strategy_case.py`, `app/models/domain/strategy_config.py`, `app/models/domain/strategy_run.py`, `app/strategies/base.py`, `app/strategies/decisions.py`
- **Resumo técnico:** Orquestra lógica principal. Recebe entidades de domínio, coordena a lógica principal e produz um resultado agregado. Classes principais: _BaseDummyStrategy, ClosingStrategy, NeverClosingStrategy. Funções principais: build_candle, build_run, build_config, test_run_engine_closes_case_during_loop, test_run_engine_finalizes_open_case_as_timeout_at_end. Depende de: app/engine/run_engine.py, app/models/domain/candle.py, app/models/domain/enums.py, app/models/domain/strategy_case.py, app/models/domain/strategy_config.py, app/models/domain/strategy_run.py.
