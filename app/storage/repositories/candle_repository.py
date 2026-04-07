from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.models.domain.candle import Candle
from app.storage.models import CandleModel
from app.utils.datetime_utils import ensure_naive_utc


class CandleRepository:
    def save_many(self, session, candles: list[Candle]) -> list[CandleModel]:
        saved_items: list[CandleModel] = []

        for candle in candles:
            normalized_open_time = ensure_naive_utc(candle.open_time)
            normalized_close_time = ensure_naive_utc(candle.close_time)

            db_existing = self.get_by_unique_key(
                session=session,
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                open_time=normalized_open_time,
            )

            if db_existing is not None:
                db_existing.asset_id = candle.asset_id
                db_existing.close_time = normalized_close_time
                db_existing.open = candle.open
                db_existing.high = candle.high
                db_existing.low = candle.low
                db_existing.close = candle.close
                db_existing.volume = candle.volume
                db_existing.source = candle.source
                session.add(db_existing)
                session.flush()
                saved_items.append(db_existing)
                continue

            db_obj = CandleModel(
                asset_id=candle.asset_id,
                symbol=candle.symbol,
                timeframe=candle.timeframe,
                open_time=normalized_open_time,
                close_time=normalized_close_time,
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
                db_existing = self.get_by_unique_key(
                    session=session,
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    open_time=normalized_open_time,
                )
                if db_existing is not None:
                    db_existing.asset_id = candle.asset_id
                    db_existing.close_time = normalized_close_time
                    db_existing.open = candle.open
                    db_existing.high = candle.high
                    db_existing.low = candle.low
                    db_existing.close = candle.close
                    db_existing.volume = candle.volume
                    db_existing.source = candle.source
                    session.add(db_existing)
                    session.flush()
                    saved_items.append(db_existing)

        session.commit()

        for item in saved_items:
            try:
                session.refresh(item)
            except Exception:
                pass

        return saved_items

    def get_by_unique_key(
        self,
        session,
        symbol: str,
        timeframe: str,
        open_time: datetime,
    ) -> CandleModel | None:
        normalized_open_time = ensure_naive_utc(open_time)

        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time == normalized_open_time,
            )
            .first()
        )

    def get_latest(
        self,
        session,
        symbol: str,
        timeframe: str,
    ) -> CandleModel | None:
        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
            )
            .order_by(CandleModel.open_time.desc(), CandleModel.id.desc())
            .first()
        )