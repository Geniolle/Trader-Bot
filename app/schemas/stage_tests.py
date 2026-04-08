from typing import List

from pydantic import BaseModel, Field


class StageTestOptionItem(BaseModel):
    symbol: str
    timeframe: str
    candles_count: int
    first_candle: str
    last_candle: str


class StageTestOptionsResponse(BaseModel):
    items: List[StageTestOptionItem]
    refreshed_at: str


class StageTestRunRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    timeframe: str = Field(..., min_length=1)
    strategy: str = Field(default="default", min_length=1)
    min_candles: int = Field(default=1, ge=1)
    extra_args: List[str] = Field(default_factory=list)


class StageTestRunResponse(BaseModel):
    ok: bool
    command: List[str]
    symbol: str
    timeframe: str
    strategy: str
    stdout: str
    stderr: str
    return_code: int