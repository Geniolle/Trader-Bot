from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy.orm import aliased

from app.registry.strategy_registry import build_strategy_registry
from app.schemas.stage_tests import (
    StageTestLatestRunResponse,
    StageTestSummaryResponse,
)
from app.storage.database import SessionLocal
from app.storage.models import StrategyMetricsModel, StrategyRunModel

router = APIRouter(prefix="/stage-tests", tags=["stage-tests"])


def _to_float(value) -> float:
    if value is None:
        return 0.0

    if isinstance(value, Decimal):
        return float(value)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@router.get("", response_model=list[StageTestSummaryResponse])
def list_stage_tests() -> list[StageTestSummaryResponse]:
    registry = build_strategy_registry()
    session = SessionLocal()

    try:
        metrics_alias = aliased(StrategyMetricsModel)

        run_rows = (
            session.query(StrategyRunModel, metrics_alias)
            .outerjoin(metrics_alias, metrics_alias.run_id == StrategyRunModel.id)
            .order_by(
                StrategyRunModel.started_at.desc(),
                StrategyRunModel.id.desc(),
            )
            .all()
        )

        aggregated: dict[str, StageTestSummaryResponse] = {}

        for strategy in registry.list_strategies():
            definition = strategy.definition

            aggregated[definition.key] = StageTestSummaryResponse(
                strategy_key=definition.key,
                strategy_name=definition.name,
                strategy_description=definition.description,
                strategy_category=definition.category,
                total_runs=0,
                total_cases=0,
                total_hits=0,
                total_fails=0,
                total_timeouts=0,
                hit_rate=0.0,
                fail_rate=0.0,
                timeout_rate=0.0,
                last_run=None,
            )

        for run_row, metrics_row in run_rows:
            strategy_key = getattr(run_row, "strategy_key", None) or ""
            if not strategy_key:
                continue

            if strategy_key not in aggregated:
                aggregated[strategy_key] = StageTestSummaryResponse(
                    strategy_key=strategy_key,
                    strategy_name=strategy_key,
                    strategy_description=None,
                    strategy_category=None,
                    total_runs=0,
                    total_cases=0,
                    total_hits=0,
                    total_fails=0,
                    total_timeouts=0,
                    hit_rate=0.0,
                    fail_rate=0.0,
                    timeout_rate=0.0,
                    last_run=None,
                )

            item = aggregated[strategy_key]
            item.total_runs += 1

            if metrics_row is not None:
                item.total_cases += int(metrics_row.total_cases or 0)
                item.total_hits += int(metrics_row.total_hits or 0)
                item.total_fails += int(metrics_row.total_fails or 0)
                item.total_timeouts += int(metrics_row.total_timeouts or 0)

            if item.last_run is None:
                item.last_run = StageTestLatestRunResponse(
                    run_id=run_row.id,
                    status=run_row.status,
                    symbol=run_row.symbol,
                    timeframe=run_row.timeframe,
                    started_at=run_row.started_at,
                    finished_at=run_row.finished_at,
                )

        for item in aggregated.values():
            if item.total_cases > 0:
                item.hit_rate = round((item.total_hits / item.total_cases) * 100, 2)
                item.fail_rate = round((item.total_fails / item.total_cases) * 100, 2)
                item.timeout_rate = round((item.total_timeouts / item.total_cases) * 100, 2)
            else:
                item.hit_rate = 0.0
                item.fail_rate = 0.0
                item.timeout_rate = 0.0

        return sorted(
            aggregated.values(),
            key=lambda item: item.strategy_name.lower(),
        )
    finally:
        session.close()