# app/schemas/stage_tests.py
# Endpoints:
# - GET  /api/v1/stage-tests/options
# - POST /api/v1/stage-tests/run

from __future__ import annotations

from pydantic import BaseModel, Field


class StageTestStrategyOptionResponse(BaseModel):
    key: str = Field(..., description="Chave técnica da estratégia")
    label: str = Field(..., description="Nome visual da estratégia")
    description: str | None = Field(default=None, description="Descrição resumida")


class StageTestOptionItemResponse(BaseModel):
    symbol: str = Field(..., description="Símbolo normalizado")
    timeframe: str = Field(..., description="Timeframe disponível")
    candles_count: int = Field(..., description="Total de candles disponíveis")
    first_candle: str | None = Field(default=None, description="Primeiro candle disponível")
    last_candle: str | None = Field(default=None, description="Último candle disponível")


class StageTestOptionsResponse(BaseModel):
    strategies: list[StageTestStrategyOptionResponse]
    items: list[StageTestOptionItemResponse]
    refreshed_at: str


class StageTestRunRequest(BaseModel):
    symbol: str
    timeframe: str
    strategy: str
    min_candles: int = Field(default=1, ge=1)
    extra_args: list[str] = Field(default_factory=list)


class StageTestMetricsResponse(BaseModel):
    strategy_class: str
    runtime_strategy: str
    total_candles: int
    warmup: int
    triggers: int
    open_cases_final: int
    closed_cases: int
    hits: int
    fails: int
    timeouts: int
    others: int
    hit_rate: float
    fail_rate: float
    timeout_rate: float
    first_candle: str | None = None
    last_candle: str | None = None


class StageTestRunResponse(BaseModel):
    ok: bool
    command: list[str]
    symbol: str
    timeframe: str
    strategy: str
    stdout: str
    stderr: str
    return_code: int
    metrics: StageTestMetricsResponse | None = None