from datetime import datetime

from app.storage.models import CandleModel


class CandleQueryRepository:
    def list_by_symbol_timeframe_range(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
        source: str | None = None,
    ) -> list[CandleModel]:
        query = session.query(CandleModel).filter(
            CandleModel.symbol == symbol,
            CandleModel.timeframe == timeframe,
            CandleModel.open_time >= start_at,
            CandleModel.close_time <= end_at,
        )

        if source:
            query = query.filter(CandleModel.source == source)

        return query.order_by(CandleModel.open_time.asc(), CandleModel.id.asc()).all()

    def list_by_filters(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime,
        limit: int = 500,
        source: str | None = None,
    ) -> list[CandleModel]:
        query = session.query(CandleModel).filter(
            CandleModel.symbol == symbol,
            CandleModel.timeframe == timeframe,
            CandleModel.open_time >= start_at,
            CandleModel.close_time <= end_at,
        )

        if source:
            query = query.filter(CandleModel.source == source)

        return (
            query.order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
            .limit(limit)
            .all()
        )

    def get_latest(
        self,
        session,
        symbol: str,
        timeframe: str,
        source: str | None = None,
    ) -> CandleModel | None:
        query = session.query(CandleModel).filter(
            CandleModel.symbol == symbol,
            CandleModel.timeframe == timeframe,
        )

        if source:
            query = query.filter(CandleModel.source == source)

        return (
            query.order_by(CandleModel.open_time.desc(), CandleModel.id.desc())
            .first()
        )