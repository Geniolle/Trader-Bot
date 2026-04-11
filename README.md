# Trader-Bot — Backend

## Objetivo

Backend do sistema Trader Bot.

Este projeto é responsável por:
- API HTTP
- WebSocket em tempo real
- leitura e sincronização de candles
- integração com providers
- Stage Tests
- execução de runs
- métricas
- comparação de resultados
- persistência local

## Stack identificada

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic / pydantic-settings

## Estrutura principal

```text
app/
  api/
  core/
  engine/
  indicators/
  models/
  providers/
  registry/
  schemas/
  services/
  stage_tests/
  storage/
  strategies/
  utils/
  main.py
```

## API principal

O router central está em `app/api/v1/router.py` com prefixo:

```text
/api/v1
```

Áreas identificadas:
- health
- catalog
- stage-tests
- strategies
- runs
- batch-runs
- providers
- run-history
- run-metrics
- run-cases
- run-details
- candles
- ws

## Como executar

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Documentação complementar

- `docs/ESTRUTURA_TECNICA_BACKEND_Trader-Bot.md`
