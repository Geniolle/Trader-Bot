from fastapi import APIRouter, HTTPException

from app.schemas.run import StrategyMetricsResponse
from app.storage.database import SessionLocal
from app.storage.repositories.metrics_queries import StrategyMetricsQueryRepository

router = APIRouter(prefix="/run-metrics", tags=["run-metrics"])


@router.get("/{run_id}", response_model=StrategyMetricsResponse)
def get_run_metrics(run_id: str) -> StrategyMetricsResponse:
    session = SessionLocal()
    try:
        row = StrategyMetricsQueryRepository().get_by_run_id(session, run_id)

        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Metrics not found for run_id: {run_id}",
            )

        return StrategyMetricsResponse(
            run_id=row.run_id,
            total_cases=row.total_cases,
            total_hits=row.total_hits,
            total_fails=row.total_fails,
            total_timeouts=row.total_timeouts,
            hit_rate=row.hit_rate,
            fail_rate=row.fail_rate,
            timeout_rate=row.timeout_rate,
            avg_bars_to_resolution=row.avg_bars_to_resolution,
            avg_time_to_resolution_seconds=row.avg_time_to_resolution_seconds,
            avg_mfe=row.avg_mfe,
            avg_mae=row.avg_mae,
        )
    finally:
        session.close()