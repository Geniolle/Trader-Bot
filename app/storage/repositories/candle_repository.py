from sqlalchemy.exc import IntegrityError

from app.models.domain.candle import Candle
from app.storage.models import CandleModel


class CandleRepository:
    def save_many(self, session, candles: list[Candle]) -> list[CandleModel]:
        saved_items: list[CandleModel] = []

        for candle in candles:
            db_obj = CandleModel(
                asset_id=candle.asset_id,
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                open_time=candle.open_time,
                close_time=candle.close_time,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
                source=candle.source,
            )

            session.add(db_obj)
            try:
                session.flush()
                saved_items.append(db_obj)
            except IntegrityError:
                session.rollback()
                db_existing = (
                    session.query(CandleModel)
                    .filter(
                        CandleModel.symbol == candle.symbol,
                        CandleModel.timeframe == candle.timeframe,
                        CandleModel.open_time == candle.open_time,
                    )
                    .first()
                )
                if db_existing is not None:
                    saved_items.append(db_existing)

        session.commit()

        for item in saved_items:
            try:
                session.refresh(item)
            except Exception:
                pass

        return saved_items