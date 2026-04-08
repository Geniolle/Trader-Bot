from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.database import Base


class Candle(Base):
    __tablename__ = "candles"

    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "timeframe",
            "open_time",
            name="uq_candles_symbol_timeframe_open_time",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    asset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String, nullable=False, index=True)
    open_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    close_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)


class CandleCoverage(Base):
    __tablename__ = "candle_coverages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    timeframe: Mapped[str] = mapped_column(String, nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source: Mapped[str | None] = mapped_column(String, nullable=True)


class StrategyRun(Base):
    __tablename__ = "strategy_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    strategy_name: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    symbol: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    timeframe: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class StrategyMetric(Base):
    __tablename__ = "strategy_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    metric_key: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    metric_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class StrategyCase(Base):
    __tablename__ = "strategy_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    run_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    case_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    symbol: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    timeframe: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    direction: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    entry_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    entry_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    exit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# Compatibilidade com nomes antigos usados noutros ficheiros
CandleModel = Candle
CandleCoverageModel = CandleCoverage
StrategyRunModel = StrategyRun
StrategyMetricModel = StrategyMetric
StrategyCaseModel = StrategyCase


__all__ = [
    "Candle",
    "CandleModel",
    "CandleCoverage",
    "CandleCoverageModel",
    "StrategyRun",
    "StrategyRunModel",
    "StrategyMetric",
    "StrategyMetricModel",
    "StrategyCase",
    "StrategyCaseModel",
]