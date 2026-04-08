from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models import Candle


class CandleQueryRepository:
    def _build_stmt(
        self,
        symbol: str,
        timeframe: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int | None = None,
    ):
        stmt = (
            select(Candle)
            .where(Candle.symbol == symbol)
            .where(Candle.timeframe == timeframe)
            .order_by(Candle.open_time.asc())
        )

        if start_at is not None:
            stmt = stmt.where(Candle.open_time >= start_at)

        if end_at is not None:
            stmt = stmt.where(Candle.open_time <= end_at)

        if limit is not None:
            stmt = stmt.limit(limit)

        return stmt

    def list_by_filters(
        self,
        session: Session,
        symbol: str,
        timeframe: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int | None = None,
    ) -> list[Candle]:
        stmt = self._build_stmt(
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )
        return list(session.scalars(stmt).all())

    def list_candles(
        self,
        session: Session,
        symbol: str,
        timeframe: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int | None = None,
    ) -> list[Candle]:
        return self.list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )