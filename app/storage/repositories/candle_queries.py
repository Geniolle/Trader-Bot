from __future__ import annotations

from app.storage.models import CandleModel


class CandleQueryRepository:
    def list_all_by_symbol_timeframe(
        self,
        session,
        symbol: str,
        timeframe: str,
    ) -> list[CandleModel]:
        return (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
            )
            .order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
            .all()
        )

    def latest_by_symbol_timeframe(
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

    def list_forward_from_open_time(
        self,
        session,
        symbol: str,
        timeframe: str,
        open_time,
        limit: int | None = None,
    ) -> list[CandleModel]:
        query = (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time > open_time,
            )
            .order_by(CandleModel.open_time.asc(), CandleModel.id.asc())
        )

        if isinstance(limit, int) and limit > 0:
            query = query.limit(limit)

        return query.all()

    def list_by_symbol_timeframe_range(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at=None,
        end_at=None,
    ) -> list[CandleModel]:
        query = session.query(CandleModel).filter(
            CandleModel.symbol == symbol,
            CandleModel.timeframe == timeframe,
        )

        if start_at is not None:
            query = query.filter(CandleModel.open_time >= start_at)

        if end_at is not None:
            query = query.filter(CandleModel.close_time <= end_at)

        return query.order_by(CandleModel.open_time.asc(), CandleModel.id.asc()).all()

    def list_by_filters(
        self,
        session,
        symbol: str,
        timeframe: str,
        start_at=None,
        end_at=None,
        limit: int | None = 500,
    ) -> list[CandleModel]:
        query = session.query(CandleModel).filter(
            CandleModel.symbol == symbol,
            CandleModel.timeframe == timeframe,
        )

        if start_at is not None:
            query = query.filter(CandleModel.open_time >= start_at)

        if end_at is not None:
            query = query.filter(CandleModel.close_time <= end_at)

        query = query.order_by(CandleModel.open_time.asc(), CandleModel.id.asc())

        if isinstance(limit, int) and limit > 0:
            query = query.limit(limit)

        return query.all()