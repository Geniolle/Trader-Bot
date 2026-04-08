from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.storage.models import Candle


class CandleQueryRepository:
    def list_candles(
        self,
        session: Session,
        symbol: str,
        timeframe: str,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int | None = None,
    ) -> list[Candle]:
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

        return list(session.scalars(stmt).all())