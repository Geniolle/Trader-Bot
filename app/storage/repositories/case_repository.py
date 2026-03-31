import json

from app.models.domain.strategy_case import StrategyCase
from app.storage.models import StrategyCaseModel


class StrategyCaseRepository:
    def save_many(self, session, cases: list[StrategyCase]) -> list[StrategyCaseModel]:
        db_items: list[StrategyCaseModel] = []

        for case in cases:
            db_obj = StrategyCaseModel(
                id=case.id,
                run_id=case.run_id,
                strategy_config_id=case.strategy_config_id,
                asset_id=case.asset_id,
                symbol=case.symbol,
                timeframe=case.timeframe,
                trigger_time=case.trigger_time,
                trigger_candle_time=case.trigger_candle_time,
                entry_time=case.entry_time,
                entry_price=case.entry_price,
                target_price=case.target_price,
                invalidation_price=case.invalidation_price,
                timeout_at=case.timeout_at,
                status=case.status.value,
                outcome=case.outcome.value if case.outcome else None,
                close_time=case.close_time,
                close_price=case.close_price,
                bars_to_resolution=case.bars_to_resolution,
                max_favorable_excursion=case.max_favorable_excursion,
                max_adverse_excursion=case.max_adverse_excursion,
                metadata_json=json.dumps(case.metadata),
            )
            db_items.append(db_obj)
            session.add(db_obj)

        session.commit()

        for item in db_items:
            session.refresh(item)

        return db_items