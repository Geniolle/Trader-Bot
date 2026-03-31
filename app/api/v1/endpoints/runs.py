from fastapi import APIRouter, HTTPException

from app.core.settings import get_settings
from app.engine.run_engine import RunEngine
from app.models.domain.candle import Candle
from app.models.domain.enums import RunMode
from app.models.domain.strategy_config import StrategyConfig
from app.models.domain.strategy_run import StrategyRun
from app.providers.factory import MarketDataProviderFactory
from app.registry.strategy_registry import build_strategy_registry
from app.schemas.run import (
    HistoricalRunRequest,
    HistoricalRunResponse,
    build_historical_run_response,
)
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository
from app.storage.repositories.case_repository import StrategyCaseRepository
from app.storage.repositories.metrics_repository import StrategyMetricsRepository
from app.storage.repositories.run_repository import StrategyRunRepository
from app.utils.ids import generate_id

router = APIRouter(prefix="/runs", tags=["runs"])


def _map_db_rows_to_domain_candles(rows) -> list[Candle]:
    return [
        Candle(
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


@router.post("/historical", response_model=HistoricalRunResponse)
def run_historical(request: HistoricalRunRequest) -> HistoricalRunResponse:
    settings = get_settings()
    registry = build_strategy_registry()

    if not registry.has(request.strategy_key):
        raise HTTPException(
            status_code=404,
            detail=f"Strategy not found: {request.strategy_key}",
        )

    strategy = registry.get(request.strategy_key)

    config_id = generate_id("cfg")
    run_id = generate_id("run")

    config = StrategyConfig(
        id=config_id,
        strategy_key=request.strategy_key,
        name=f"{request.strategy_key}-historical",
        timeframe=request.timeframe,
        parameters=request.parameters,
        timeout_bars=request.timeout_bars,
        enabled=True,
    )

    run = StrategyRun(
        id=run_id,
        strategy_config_id=config.id,
        mode=RunMode.HISTORICAL,
        symbol=request.symbol,
        timeframe=request.timeframe,
        start_at=request.start_at,
        end_at=request.end_at,
    )
    run.strategy_key = request.strategy_key

    session = SessionLocal()
    try:
        db_candles = CandleQueryRepository().list_by_symbol_timeframe_range(
            session=session,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_at=request.start_at,
            end_at=request.end_at,
        )

        if db_candles:
            candles = _map_db_rows_to_domain_candles(db_candles)
        else:
            try:
                provider = MarketDataProviderFactory().get_provider(settings.market_data_provider)
                candles = provider.get_historical_candles(
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    start_at=request.start_at,
                    end_at=request.end_at,
                )
            except KeyError as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            if not candles:
                raise HTTPException(
                    status_code=400,
                    detail="No candles returned for the requested period",
                )

            CandleRepository().save_many(session, candles)

        if not candles:
            raise HTTPException(
                status_code=400,
                detail="No candles available for the requested period",
            )

        engine = RunEngine()
        result = engine.run(
            run=run,
            strategy=strategy,
            config=config,
            candles=candles,
        )
        result["run"].strategy_key = request.strategy_key

        StrategyRunRepository().save(session, result["run"])
        StrategyCaseRepository().save_many(session, result["closed_cases"])
        StrategyMetricsRepository().save(session, result["metrics"])
    finally:
        session.close()

    return build_historical_run_response(result)