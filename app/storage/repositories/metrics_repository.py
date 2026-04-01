from app.models.domain.strategy_metrics import StrategyMetrics
from app.storage.models import StrategyMetricsModel


class StrategyMetricsRepository:
    def save(self, session, metrics: StrategyMetrics) -> StrategyMetricsModel:
        db_obj = StrategyMetricsModel(
            run_id=metrics.run_id,
            total_cases=metrics.total_cases,
            total_hits=metrics.total_hits,
            total_fails=metrics.total_fails,
            total_timeouts=metrics.total_timeouts,
            hit_rate=metrics.hit_rate,
            fail_rate=metrics.fail_rate,
            timeout_rate=metrics.timeout_rate,
            avg_bars_to_resolution=metrics.avg_bars_to_resolution,
            avg_time_to_resolution_seconds=metrics.avg_time_to_resolution_seconds,
            avg_mfe=metrics.avg_mfe,
            avg_mae=metrics.avg_mae,
        )

        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj