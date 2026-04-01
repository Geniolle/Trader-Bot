from app.storage.models import StrategyMetricsModel


class StrategyMetricsQueryRepository:
    def get_by_run_id(self, session, run_id: str) -> StrategyMetricsModel | None:
        return (
            session.query(StrategyMetricsModel)
            .filter(StrategyMetricsModel.run_id == run_id)
            .first()
        )