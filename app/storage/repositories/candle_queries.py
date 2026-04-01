from app.storage.models import CandleModel


class CandleQueryRepository:
    def list_by_symbol_timeframe_range(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at,
        end_at,
    ) -> list[CandleModel]:
        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time >= start_at,
                CandleModel.close_time <= end_at,
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
        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time >= start_at,
                CandleModel.close_time <= end_at,
            )
            .order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
            .limit(limit)
            .all()
        )