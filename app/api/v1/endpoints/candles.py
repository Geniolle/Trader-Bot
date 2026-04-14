from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from app.schemas.run import CandleResponse
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository

router = APIRouter(prefix="/candles", tags=["candles"])


def _to_response(row) -> CandleResponse:
    return CandleResponse(
        id=row.id,
        asset_id=row.asset_id,
        symbol=row.symbol,
        timeframe=row.timeframe,
        open_time=row.open_time,
        close_time=row.close_time,
        open=row.open,
        high=row.high,
        low=row.low,
        close=row.close,
        volume=row.volume,
        source=row.source,
    )


@router.get("", response_model=list[CandleResponse])
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1, le=50000),
    mode: str | None = Query(default=None),
) -> list[CandleResponse]:
    """
    Endpoint local-only.

    Regras:
    - se vier start_at/end_at, devolve o histórico local dentro do intervalo
    - se não vier intervalo, devolve todo o histórico local do symbol/timeframe
    - mode é aceito por compatibilidade com o frontend, mas aqui não muda a fonte
    """
    session = SessionLocal()
    try:
        repo = CandleQueryRepository()

        rows = repo.list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        return [_to_response(row) for row in rows]
    finally:
        session.close()


@router.get("/latest", response_model=CandleResponse | None)
def get_latest_local_candle(
    symbol: str = Query(...),
    timeframe: str = Query(...),
) -> CandleResponse | None:
    """
    Devolve o último candle local guardado para symbol/timeframe.
    Este endpoint é a base correta para a lógica:
    - histórico para trás = BD local
    - atualização para a frente = pedir ao provider só após este candle
    """
    session = SessionLocal()
    try:
        row = CandleQueryRepository().latest_by_symbol_timeframe(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
        )

        if row is None:
            return None

        return _to_response(row)
    finally:
        session.close()