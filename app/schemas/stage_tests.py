from datetime import datetime

from pydantic import BaseModel


class StageTestLatestRunResponse(BaseModel):
    run_id: str | None = None
    status: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class StageTestSummaryResponse(BaseModel):
    strategy_key: str
    strategy_name: str
    strategy_description: str | None = None
    strategy_category: str | None = None

    total_runs: int = 0
    total_cases: int = 0
    total_hits: int = 0
    total_fails: int = 0
    total_timeouts: int = 0

    hit_rate: float = 0
    fail_rate: float = 0
    timeout_rate: float = 0

    last_run: StageTestLatestRunResponse | None = None