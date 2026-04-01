from decimal import Decimal

from app.indicators.ema import exponential_moving_average
from app.models.domain.candle import Candle
from app.models.domain.enums import CaseOutcome, StrategyCategory
from app.models.domain.strategy_case import StrategyCase
from app.models.domain.strategy_config import StrategyConfig
from app.models.domain.strategy_definition import StrategyDefinition
from app.models.domain.strategy_run import StrategyRun
from app.strategies.base import BaseStrategy
from app.strategies.decisions import CaseCloseDecision, TriggerDecision


class EmaCrossStrategy(BaseStrategy):
    definition = StrategyDefinition(
        key="ema_cross",
        name="EMA Cross",
        version="1.0.0",
        description=(
            "Detects a bullish crossover where the short EMA crosses above "
            "the long EMA, using percentage target and invalidation."
        ),
        category=StrategyCategory.TREND_FOLLOWING,
    )

    def warmup_period(self, config: StrategyConfig) -> int:
        short_period = int(config.parameters.get("ema_short_period", 9))
        long_period = int(config.parameters.get("ema_long_period", 21))
        return max(short_period, long_period)

    def calculate_indicators(
        self,
        candles: list[Candle],
        config: StrategyConfig,
    ) -> dict:
        short_period = int(config.parameters.get("ema_short_period", 9))
        long_period = int(config.parameters.get("ema_long_period", 21))

        closes = [candle.close for candle in candles]

        short_ema = exponential_moving_average(closes, short_period)
        long_ema = exponential_moving_average(closes, long_period)

        return {
            "short_ema": short_ema,
            "long_ema": long_ema,
        }

    def check_trigger(
        self,
        candles: list[Candle],
        index: int,
        config: StrategyConfig,
    ) -> TriggerDecision:
        if index < 1:
            return TriggerDecision(
                triggered=False,
                reason="not_enough_candles_for_cross",
            )

        previous_slice = candles[:index]
        current_slice = candles[: index + 1]

        previous_indicators = self.calculate_indicators(previous_slice, config)
        current_indicators = self.calculate_indicators(current_slice, config)

        previous_short = previous_indicators["short_ema"]
        previous_long = previous_indicators["long_ema"]
        current_short = current_indicators["short_ema"]
        current_long = current_indicators["long_ema"]

        if (
            previous_short is None
            or previous_long is None
            or current_short is None
            or current_long is None
        ):
            return TriggerDecision(
                triggered=False,
                reason="indicators_not_ready",
            )

        crossed_up = previous_short <= previous_long and current_short > current_long

        if crossed_up:
            return TriggerDecision(
                triggered=True,
                reason="ema_bullish_cross_confirmed",
                metadata={
                    "previous_short_ema": str(previous_short),
                    "previous_long_ema": str(previous_long),
                    "current_short_ema": str(current_short),
                    "current_long_ema": str(current_long),
                },
            )

        return TriggerDecision(
            triggered=False,
            reason="trigger_conditions_not_met",
        )

    def create_case(
        self,
        candles: list[Candle],
        index: int,
        config: StrategyConfig,
        run: StrategyRun,
    ) -> StrategyCase:
        current_candle = candles[index]

        target_percent = Decimal(str(config.parameters.get("target_percent", "2")))
        stop_percent = Decimal(str(config.parameters.get("stop_percent", "1")))
        timeout_bars = int(config.timeout_bars)

        entry_price = current_candle.close
        target_price = entry_price * (Decimal("1") + (target_percent / Decimal("100")))
        invalidation_price = entry_price * (Decimal("1") - (stop_percent / Decimal("100")))

        timeout_at = None
        if timeout_bars > 0:
            candle_duration = current_candle.close_time - current_candle.open_time
            timeout_at = current_candle.close_time + (candle_duration * timeout_bars)

        return StrategyCase(
            run_id=run.id or "run-placeholder",
            strategy_config_id=config.id or "config-placeholder",
            asset_id=run.asset_id,
            symbol=run.symbol,
            timeframe=run.timeframe,
            trigger_time=current_candle.close_time,
            trigger_candle_time=current_candle.close_time,
            entry_time=current_candle.close_time,
            entry_price=entry_price,
            target_price=target_price,
            invalidation_price=invalidation_price,
            timeout_at=timeout_at,
            metadata={
                "strategy_key": self.definition.key,
                "target_percent": str(target_percent),
                "stop_percent": str(stop_percent),
            },
        )

    def update_case(
        self,
        case: StrategyCase,
        candle: Candle,
        config: StrategyConfig,
    ) -> StrategyCase:
        updated_case = case.model_copy(deep=True)

        favorable_move = candle.high - updated_case.entry_price
        adverse_move = updated_case.entry_price - candle.low

        if favorable_move > updated_case.max_favorable_excursion:
            updated_case.max_favorable_excursion = favorable_move

        if adverse_move > updated_case.max_adverse_excursion:
            updated_case.max_adverse_excursion = adverse_move

        updated_case.bars_to_resolution += 1

        return updated_case

    def should_close_case(
        self,
        case: StrategyCase,
        candle: Candle,
        config: StrategyConfig,
    ) -> CaseCloseDecision:
        if candle.high >= case.target_price:
            return CaseCloseDecision(
                should_close=True,
                outcome=CaseOutcome.HIT,
                reason="target_percent_reached",
                close_price=case.target_price,
            )

        if candle.low <= case.invalidation_price:
            return CaseCloseDecision(
                should_close=True,
                outcome=CaseOutcome.FAIL,
                reason="stop_percent_reached",
                close_price=case.invalidation_price,
            )

        if case.timeout_at is not None and candle.close_time >= case.timeout_at:
            return CaseCloseDecision(
                should_close=True,
                outcome=CaseOutcome.TIMEOUT,
                reason="timeout_reached",
                close_price=candle.close,
            )

        return CaseCloseDecision(
            should_close=False,
            reason="case_remains_open",
        )

    def close_case(
        self,
        case: StrategyCase,
        candle: Candle,
        config: StrategyConfig,
        decision: CaseCloseDecision,
    ) -> StrategyCase:
        if not decision.should_close or decision.outcome is None:
            raise ValueError("close_case called without a valid close decision")

        updated_case = case.model_copy(deep=True)
        updated_case.status = updated_case.status.CLOSED
        updated_case.outcome = decision.outcome
        updated_case.close_time = candle.close_time
        updated_case.close_price = decision.close_price or candle.close

        updated_case.metadata = {
            **updated_case.metadata,
            "close_reason": decision.reason,
            **decision.metadata,
        }

        return updated_case