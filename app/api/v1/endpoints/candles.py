# app/api/v1/endpoints/candles.py

from datetime import datetime
import asyncio
import json
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.schemas.run import CandleResponse
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository

router = APIRouter(prefix="/candles", tags=["candles"])

# --- Mapeadores existentes mantidos para compatibilidade ---

def _map_rows_to_response(rows) -> list[CandleResponse]:
    return [
        CandleResponse(
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
        for row in rows
    ]

def _map_domain_candles_to_response(candles) -> list[CandleResponse]:
    return [
        CandleResponse(
            id=getattr(candle, "id", None),
            asset_id=candle.asset_id,
            symbol=candle.symbol,
            timeframe=candle.timeframe,
            open_time=candle.open_time,
            close_time=candle.close_time, open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
            source=candle.source,
        )
        for candle in candles
    ]

# --- Rota GET Original (Histórico) ---

@router.get("", response_model=list[CandleResponse])
def list_candles(
    symbol: str = Query(...),
    timeframe: str = Query(...),
    start_at: datetime = Query(...),
    end_at: datetime = Query(...),
    limit: int = Query(default=500, ge=1, le=5000),
    mode: str | None = Query(default="full"),
) -> list[CandleResponse]:
    session = SessionLocal()
    try:
        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )

        if rows:
            return _map_rows_to_response(rows)

        settings = get_settings()

        try:
            provider = MarketDataProviderFactory().get_provider(
                settings.market_data_provider
            )
            candles = provider.get_historical_candles(
                symbol=symbol,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erro no provider: {exc}")

        if not candles:
            return []

        CandleRepository().save_many(session, candles)
        return _map_domain_candles_to_response(candles[:limit])
    finally:
        session.close()

# --- NOVA ROTA WEBSOCKET (Real-time) ---

@router.websocket("/ws")
async def websocket_candles(websocket: WebSocket, symbol: str = None, timeframe: str = "1m"):
    """
    Endpoint de WebSocket para enviar atualizações de candles em tempo real.
    """
    await websocket.accept()
    
    # Se o símbolo não vier via query params, podemos tentar receber via primeira mensagem
    if not symbol:
        try:
            initial_data = await websocket.receive_text()
            symbol = json.loads(initial_data).get("symbol")
        except:
            await websocket.close(code=1003)
            return

    try:
        while True:
            session = SessionLocal()
            try:
                # 1. Busca a última vela guardada no banco de dados para este símbolo
                # Nota: Assumimos que o seu Bot de coleta está rodando em paralelo 
                # e alimentando a tabela 'candles' na market_research_lab.db
                latest_rows = CandleQueryRepository().list_by_filters(
                    session=session,
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=1  # Queremos apenas a mais recente
                )

                if latest_rows:
                    candle = latest_rows[0]
                    # Formata o dado conforme o CandleResponse espera
                    payload = {
                        "time": int(candle.open_time.timestamp()),
                        "open": float(candle.open),
                        "high": float(candle.high),
                        "low": float(candle.low),
                        "close": float(candle.close),
                        "volume": float(candle.volume) if candle.volume else 0
                    }
                    await websocket.send_json(payload)
                
            finally:
                session.close()
            
            # 2. Aguarda um intervalo antes de checar a DB novamente (ex: 1 segundo)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"Client disconnected for symbol: {symbol}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()