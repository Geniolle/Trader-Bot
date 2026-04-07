from app.storage.models import CandleModel


class CandleUpsertRepository:
    def upsert_many(
        self,
        session,
        candles,
    ) -> int:
        if not candles:
            return 0

        symbol = candles[0].symbol
        timeframe = candles[0].timeframe
        open_times = [item.open_time for item in candles]

        existing_rows = (
            session.query(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.timeframe == timeframe,
                CandleModel.open_time.in_(open_times),
            )
            .all()
        )

        existing_map = {row.open_time: row for row in existing_rows}
        inserted_or_updated = 0

        for candle in candles:
            row = existing_map.get(candle.open_time)

            if row is None:
                row = CandleModel(
                    asset_id=candle.asset_id,
                    symbol=candle.symbol,
                    timeframe=candle.timeframe,
                    open_time=candle.open_time,
                    close_time=candle.close_time,
                    open=candle.open,
                    high=candle.high,
                    low=candle.low,
                    close=candle.close,
                    volume=candle.volume,
                    source=candle.source,
                )
                session.add(row)
                inserted_or_updated += 1
                continue

            row.asset_id = candle.asset_id
            row.close_time = candle.close_time
            row.open = candle.open
            row.high = candle.high
            row.low = candle.low
            row.close = candle.close
            row.volume = candle.volume
            row.source = candle.source
            inserted_or_updated += 1

        session.flush()
        return inserted_or_updated