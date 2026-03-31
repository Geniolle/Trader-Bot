from decimal import Decimal

from fastapi import APIRouter, Query

from app.schemas.comparison import (
    StrategyComparisonItemResponse,
    StrategyComparisonResponse,
)
from app.storage.database import SessionLocal
from app.storage.repositories.comparison_queries import StrategyComparisonQueryRepository

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.get("/strategies", response_model=StrategyComparisonResponse)
def compare_strategies(
    symbol: str | None = Query(default=None),
    timeframe: str | None = Query(default=None),
    strategy_key: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=5000),
) -> StrategyComparisonResponse:
    session = SessionLocal()
    try:
        grouped = StrategyComparisonQueryRepository().compare_by_strategy(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            strategy_key=strategy_key,
            limit=limit,
        )

        results: list[StrategyComparisonItemResponse] = []

        for key, items in grouped.items():
            total_runs = len(items)
            total_cases = sum(item[1].total_cases for item in items)
            total_hits = sum(item[1].total_hits for item in items)
            total_fails = sum(item[1].total_fails for item in items)
            total_timeouts = sum(item[1].total_timeouts for item in items)

            items_with_cases = [item for item in items if item[1].total_cases > 0]
            runs_with_cases = len(items_with_cases)

            if runs_with_cases > 0:
                avg_hit_rate = (
                    sum(item[1].hit_rate for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
                avg_fail_rate = (
                    sum(item[1].fail_rate for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
                avg_timeout_rate = (
                    sum(item[1].timeout_rate for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
                avg_bars_to_resolution = (
                    sum(item[1].avg_bars_to_resolution for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
                avg_time_to_resolution_seconds = (
                    sum(
                        item[1].avg_time_to_resolution_seconds
                        for item in items_with_cases
                    )
                    / Decimal(runs_with_cases)
                )
                avg_mfe = (
                    sum(item[1].avg_mfe for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
                avg_mae = (
                    sum(item[1].avg_mae for item in items_with_cases)
                    / Decimal(runs_with_cases)
                )
            else:
                avg_hit_rate = Decimal("0")
                avg_fail_rate = Decimal("0")
                avg_timeout_rate = Decimal("0")
                avg_bars_to_resolution = Decimal("0")
                avg_time_to_resolution_seconds = Decimal("0")
                avg_mfe = Decimal("0")
                avg_mae = Decimal("0")

            results.append(
                StrategyComparisonItemResponse(
                    strategy_key=key,
                    total_runs=total_runs,
                    total_cases=total_cases,
                    total_hits=total_hits,
                    total_fails=total_fails,
                    total_timeouts=total_timeouts,
                    avg_hit_rate=avg_hit_rate,
                    avg_fail_rate=avg_fail_rate,
                    avg_timeout_rate=avg_timeout_rate,
                    avg_bars_to_resolution=avg_bars_to_resolution,
                    avg_time_to_resolution_seconds=avg_time_to_resolution_seconds,
                    avg_mfe=avg_mfe,
                    avg_mae=avg_mae,
                )
            )

        results.sort(key=lambda item: (item.avg_hit_rate, item.total_cases), reverse=True)

        return StrategyComparisonResponse(
            symbol=symbol,
            timeframe=timeframe,
            strategy_key=strategy_key,
            total_groups=len(results),
            results=results,
        )
    finally:
        session.close()