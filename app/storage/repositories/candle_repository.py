from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from app.models.domain.candle import Candle
from app.storage.models import CandleModel


def _new_uuid() -> str:
    return str(uuid4())


class CandleRepository:
    def save_many(self, session, candles: list[Candle]) -> list[CandleModel]:
        saved_items: list[CandleModel] = []

        for candle in candles:
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
                continue

            db_obj = CandleModel(
                id=_new_uuid(),
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
                session.commit()
                saved_items.append(db_obj)
            except (IntegrityError, FlushError):
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
                    continue

                raise
            except Exception:
                session.rollback()
                raise

        return saved_items