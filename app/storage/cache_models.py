from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.storage.database import Base


def generate_uuid() -> str:
    return str(uuid4())


class CandleCoverageModel(Base):
    __tablename__ = "candle_coverages"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "timeframe",
            name="uq_candle_coverages_symbol_timeframe",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(20), nullable=False)

    covered_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    covered_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)

    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    last_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)