from datetime import datetime

from app.storage.models import CandleModel
from app.utils.datetime_utils import ensure_naive_utc


class CandleQueryRepository:
    def list_by_symbol_timeframe_range(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at,
        end_at,
    ) -> list[CandleModel]:
        normalized_start_at = ensure_naive_utc(start_at)
        normalized_end_at = ensure_naive_utc(end_at)

        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time >= normalized_start_at,
                CandleModel.close_time <= normalized_end_at,
            )
            .order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
            .all()
        )

    def list_by_filters(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at,
        end_at,
        limit: int = 500,
    ) -> list[CandleModel]:
        normalized_start_at = ensure_naive_utc(start_at)
        normalized_end_at = ensure_naive_utc(end_at)

        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time >= normalized_start_at,
                CandleModel.close_time <= normalized_end_at,
            )
            .order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
            .limit(limit)
            .all()
        )

    def get_latest_by_symbol_timeframe(
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