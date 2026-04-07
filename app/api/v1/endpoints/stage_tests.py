# app/api/v1/endpoints/stage_tests.py

from fastapi import APIRouter, Query

from app.registry.strategy_registry import build_strategy_registry
from app.schemas.stage_tests import (
    StageTestLatestRunResponse,
    StageTestSummaryItemResponse,
)
from app.storage.database import SessionLocal
from app.storage.repositories.metrics_queries import StrategyMetricsQueryRepository
from app.storage.repositories.run_queries import StrategyRunQueryRepository

router = APIRouter(prefix="/stage-tests", tags=["stage-tests"])


@router.get("", response_model=list[StageTestSummaryItemResponse])
def list_stage_tests(
    symbol: str | None = Query(default=None),
    timeframe: str | None = Query(default=None),
) -> list[StageTestSummaryItemResponse]:
    registry = build_strategy_registry()
    registered_strategies = registry.list_strategies()

    summary_by_strategy: dict[str, dict] = {}

    for strategy in registered_strategies:
        definition = strategy.definition
        summary_by_strategy[definition.key] = {
            "strategy_key": definition.key,
            "strategy_name": definition.name,
            "strategy_description": definition.description,
            "strategy_category": definition.category.value,
            "total_runs": 0,
            "total_cases": 0,
            "total_hits": 0,
            "total_fails": 0,
            "total_timeouts": 0,
            "hit_rate": 0.0,
            "fail_rate": 0.0,
            "timeout_rate": 0.0,
            "last_run": None,
        }

    session = SessionLocal()
    try:
        run_rows = StrategyRunQueryRepository().list_runs(session=session)

        if symbol:
            run_rows = [row for row in run_rows if row.symbol == symbol]

        if timeframe:
            run_rows = [row for row in run_rows if row.timeframe == timeframe]

        run_ids = [row.id for row in run_rows]
        metrics_rows = StrategyMetricsQueryRepository().list_by_run_ids(
            session=session,
            run_ids=run_ids,
        )
        metrics_by_run_id = {row.run_id: row for row in metrics_rows}

        for run_row in run_rows:
            strategy_key = (getattr(run_row, "strategy_key", "") or "").strip()

            if not strategy_key:
                strategy_key = "sem_estrategia"

            if strategy_key not in summary_by_strategy:
                summary_by_strategy[strategy_key] = {
                    "strategy_key": strategy_key,
                    "strategy_name": strategy_key,
                    "strategy_description": None,
                    "strategy_category": "unknown",
                    "total_runs": 0,
                    "total_cases": 0,
                    "total_hits": 0,
                    "total_fails": 0,
                    "total_timeouts": 0,
                    "hit_rate": 0.0,
                    "fail_rate": 0.0,
                    "timeout_rate": 0.0,
                    "last_run": None,
                }

            summary = summary_by_strategy[strategy_key]
            metrics_row = metrics_by_run_id.get(run_row.id)

            total_cases = int(metrics_row.total_cases) if metrics_row is not None else int(
                run_row.total_cases_closed
            )
            total_hits = int(metrics_row.total_hits) if metrics_row is not None else 0
            total_fails = int(metrics_row.total_fails) if metrics_row is not None else 0
            total_timeouts = int(metrics_row.total_timeouts) if metrics_row is not None else 0

            summary["total_runs"] += 1
            summary["total_cases"] += total_cases
            summary["total_hits"] += total_hits
            summary["total_fails"] += total_fails
            summary["total_timeouts"] += total_timeouts

            if summary["last_run"] is None:
                summary["last_run"] = StageTestLatestRunResponse(
                    run_id=run_row.id,
                    status=run_row.status,
                    symbol=run_row.symbol,
                    timeframe=run_row.timeframe,
                    started_at=run_row.started_at,
                    finished_at=run_row.finished_at,
                )

        response_items: list[StageTestSummaryItemResponse] = []

        for item in summary_by_strategy.values():
            total_cases = item["total_cases"]
            total_hits = item["total_hits"]
            total_fails = item["total_fails"]
            total_timeouts = item["total_timeouts"]

            hit_rate = (total_hits / total_cases * 100) if total_cases > 0 else 0.0
            fail_rate = (total_fails / total_cases * 100) if total_cases > 0 else 0.0
            timeout_rate = (
                total_timeouts / total_cases * 100 if total_cases > 0 else 0.0
            )

            response_items.append(
                StageTestSummaryItemResponse(
                    strategy_key=item["strategy_key"],
                    strategy_name=item["strategy_name"],
                    strategy_description=item["strategy_description"],
                    strategy_category=item["strategy_category"],
                    total_runs=item["total_runs"],
                    total_cases=total_cases,
                    total_hits=total_hits,
                    total_fails=total_fails,
                    total_timeouts=total_timeouts,
                    hit_rate=round(hit_rate, 2),
                    fail_rate=round(fail_rate, 2),
                    timeout_rate=round(timeout_rate, 2),
                    last_run=item["last_run"],
                )
            )

        return sorted(
            response_items,
            key=lambda item: item.strategy_name.lower(),
        )
    finally:
        session.close()