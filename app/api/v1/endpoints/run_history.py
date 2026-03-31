from fastapi import APIRouter, Query

from app.schemas.run import StrategyRunResponse
from app.storage.database import SessionLocal
from app.storage.repositories.run_queries import StrategyRunQueryRepository

router = APIRouter(prefix="/run-history", tags=["run-history"])


@router.get("", response_model=list[StrategyRunResponse])
def list_run_history(
    symbol: str | None = Query(default=None),
    timeframe: str | None = Query(default=None),
    strategy_key: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[StrategyRunResponse]:
    session = SessionLocal()
    try:
        rows = StrategyRunQueryRepository().list_runs_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            strategy_key=strategy_key,
            limit=limit,
        )

        return [
            StrategyRunResponse(
                id=row.id,
                strategy_key=getattr(row, "strategy_key", None),
                strategy_config_id=row.strategy_config_id,
                mode=row.mode,
                asset_id=row.asset_id,
                symbol=row.symbol,
                timeframe=row.timeframe,
                start_at=row.start_at,
                end_at=row.end_at,
                status=row.status,
                total_candles_processed=row.total_candles_processed,
                total_cases_opened=row.total_cases_opened,
                total_cases_closed=row.total_cases_closed,
                started_at=row.started_at,
                finished_at=row.finished_at,
            )
            for row in rows
        ]
    finally:
        session.close()