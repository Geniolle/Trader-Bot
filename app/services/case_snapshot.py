# app/services/case_snapshot.py

from decimal import Decimal

from app.indicators.atr import average_true_range_series
from app.indicators.bollinger import bollinger_bands
from app.indicators.ema import exponential_moving_average_series
from app.indicators.macd import macd_series
from app.indicators.rsi import relative_strength_index_series
from app.models.domain.candle import Candle
from app.models.domain.strategy_config import StrategyConfig


EMA_PERIODS = [5, 10, 20, 30, 40]


def build_case_metadata_snapshot(
    candles: list[Candle],
    index: int,
    config: StrategyConfig,
) -> dict:
    if index < 0 or index >= len(candles):
        raise IndexError("index out of range for candles snapshot")

    current_candle = candles[index]
    current_slice = candles[: index + 1]
    previous_slice = candles[:index]

    closes = [candle.close for candle in current_slice]

    ema_values = {}
    ema_previous_values = {}

    for period in EMA_PERIODS:
        current_series = exponential_moving_average_series(closes, period)
        ema_values[period] = current_series[-1] if current_series else None
        ema_previous_values[period] = current_series[-2] if len(current_series) >= 2 else None

    bollinger_period = int(config.parameters.get("bollinger_period", 20))
    bollinger_stddev = Decimal(str(config.parameters.get("bollinger_stddev", 2)))

    current_bands = bollinger_bands(closes, bollinger_period, bollinger_stddev)
    previous_bands = None
    if previous_slice:
        previous_bands = bollinger_bands(
            [candle.close for candle in previous_slice],
            bollinger_period,
            bollinger_stddev,
        )

    rsi_period = int(config.parameters.get("rsi_period", 14))
    rsi_series = relative_strength_index_series(closes, rsi_period)
    current_rsi = rsi_series[-1] if rsi_series else None
    previous_rsi = rsi_series[-2] if len(rsi_series) >= 2 else None

    macd_values = macd_series(closes, fast_period=12, slow_period=26, signal_period=9)
    current_macd = macd_values[-1] if macd_values else {"macd_line": None, "signal_line": None, "histogram": None}
    previous_macd = macd_values[-2] if len(macd_values) >= 2 else {"macd_line": None, "signal_line": None, "histogram": None}

    atr_period = int(config.parameters.get("atr_period", 14))
    atr_series = average_true_range_series(current_slice, atr_period)
    current_atr = atr_series[-1] if atr_series else None

    lower_band = middle_band = upper_band = None
    previous_lower = previous_middle = previous_upper = None

    if current_bands is not None:
        lower_band, middle_band, upper_band = current_bands

    if previous_bands is not None:
        previous_lower, previous_middle, previous_upper = previous_bands

    previous_candle = candles[index - 1] if index > 0 else None

    ema_alignment = classify_ema_alignment(ema_values)
    market_structure = classify_market_structure(current_slice)
    candle_stats = build_candle_stats(current_candle)
    session = classify_session(current_candle.open_time.hour)
    rsi_zone = classify_rsi_zone(current_rsi)
    macd_state = classify_macd_state(current_macd, previous_macd)
    atr_regime = classify_atr_regime(current_slice, current_atr, atr_period)

    price_vs_ema_20 = classify_price_vs_average(current_candle.close, ema_values.get(20))
    price_vs_ema_40 = classify_price_vs_average(current_candle.close, ema_values.get(40))

    trend_confirmed_long = (
        ema_alignment == "bullish"
        and price_vs_ema_20 == "above"
        and price_vs_ema_40 == "above"
        and slope_label(ema_values.get(20), ema_previous_values.get(20)) == "up"
    )

    trend_confirmed_short = (
        ema_alignment == "bearish"
        and price_vs_ema_20 == "below"
        and price_vs_ema_40 == "below"
        and slope_label(ema_values.get(20), ema_previous_values.get(20)) == "down"
    )

    closed_below_lower_band = bool(lower_band is not None and current_candle.close < lower_band)
    closed_above_upper_band = bool(upper_band is not None and current_candle.close > upper_band)

    reentered_inside_band_long = bool(
        previous_candle is not None
        and previous_lower is not None
        and lower_band is not None
        and previous_candle.close < previous_lower
        and current_candle.close > lower_band
    )

    reentered_inside_band_short = bool(
        previous_candle is not None
        and previous_upper is not None
        and upper_band is not None
        and previous_candle.close > previous_upper
        and current_candle.close < upper_band
    )

    candle_range = current_candle.high - current_candle.low
    candle_range_vs_atr = None
    if current_atr is not None and current_atr > 0:
        candle_range_vs_atr = candle_range / current_atr

    snapshot = {
        "snapshot_version": "1.0",
        "trigger_context": {
            "reference_time": current_candle.close_time.isoformat(),
            "reference_price": as_str(current_candle.close),
            "session": session,
            "day_of_week": current_candle.open_time.strftime("%A").lower(),
            "hour_of_day": current_candle.open_time.hour,
        },
        "trend": {
            "ema_5": as_str(ema_values.get(5)),
            "ema_10": as_str(ema_values.get(10)),
            "ema_20": as_str(ema_values.get(20)),
            "ema_30": as_str(ema_values.get(30)),
            "ema_40": as_str(ema_values.get(40)),
            "ema_alignment": ema_alignment,
            "price_vs_ema_20": price_vs_ema_20,
            "price_vs_ema_40": price_vs_ema_40,
            "ema_5_slope": slope_label(ema_values.get(5), ema_previous_values.get(5)),
            "ema_10_slope": slope_label(ema_values.get(10), ema_previous_values.get(10)),
            "ema_20_slope": slope_label(ema_values.get(20), ema_previous_values.get(20)),
            "ema_30_slope": slope_label(ema_values.get(30), ema_previous_values.get(30)),
            "ema_40_slope": slope_label(ema_values.get(40), ema_previous_values.get(40)),
        },
        "bollinger": {
            "period": bollinger_period,
            "stddev": as_str(bollinger_stddev),
            "upper": as_str(upper_band),
            "middle": as_str(middle_band),
            "lower": as_str(lower_band),
            "bandwidth": as_str((upper_band - lower_band) if upper_band is not None and lower_band is not None else None),
            "close_position_in_band": as_str(
                calculate_band_position(current_candle.close, lower_band, upper_band)
            ),
            "closed_below_lower_band": closed_below_lower_band,
            "closed_above_upper_band": closed_above_upper_band,
            "reentered_inside_band_long": reentered_inside_band_long,
            "reentered_inside_band_short": reentered_inside_band_short,
        },
        "momentum": {
            "rsi_14": as_str(current_rsi),
            "rsi_zone": rsi_zone,
            "rsi_slope": slope_label(current_rsi, previous_rsi),
            "macd_line": as_str(current_macd.get("macd_line")),
            "macd_signal": as_str(current_macd.get("signal_line")),
            "macd_histogram": as_str(current_macd.get("histogram")),
            "macd_state": macd_state,
            "macd_histogram_slope": slope_label(
                current_macd.get("histogram"),
                previous_macd.get("histogram"),
            ),
        },
        "volatility": {
            "atr_14": as_str(current_atr),
            "atr_regime": atr_regime,
            "candle_range": as_str(candle_range),
            "candle_range_vs_atr": as_str(candle_range_vs_atr),
        },
        "structure": {
            "market_structure": market_structure,
            "entry_location": classify_entry_location(
                market_structure=market_structure,
                close=current_candle.close,
                ema20=ema_values.get(20),
                lower_band=lower_band,
                upper_band=upper_band,
            ),
            "distance_to_recent_support": as_str(distance_to_recent_support(current_slice)),
            "distance_to_recent_resistance": as_str(distance_to_recent_resistance(current_slice)),
            "distance_to_ema_20": as_str(distance_to_level(current_candle.close, ema_values.get(20))),
            "distance_to_ema_40": as_str(distance_to_level(current_candle.close, ema_values.get(40))),
        },
        "trigger_candle": candle_stats,
        "patterns": {
            "bb_reentry_long": reentered_inside_band_long,
            "bb_reentry_short": reentered_inside_band_short,
            "ema_trend_confirmed_long": trend_confirmed_long,
            "ema_trend_confirmed_short": trend_confirmed_short,
            "rsi_recovery_long": bool(
                previous_rsi is not None
                and current_rsi is not None
                and previous_rsi <= Decimal("30")
                and current_rsi > previous_rsi
            ),
            "rsi_recovery_short": bool(
                previous_rsi is not None
                and current_rsi is not None
                and previous_rsi >= Decimal("70")
                and current_rsi < previous_rsi
            ),
            "macd_confirmation_long": macd_state in {"bullish_cross", "bullish_above_signal"},
            "macd_confirmation_short": macd_state in {"bearish_cross", "bearish_below_signal"},
            "countertrend_long": not trend_confirmed_long,
            "countertrend_short": not trend_confirmed_short,
        },
    }

    return snapshot


def as_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def slope_label(current: Decimal | None, previous: Decimal | None) -> str:
    if current is None or previous is None:
        return "unknown"
    if current > previous:
        return "up"
    if current < previous:
        return "down"
    return "flat"


def classify_ema_alignment(ema_values: dict[int, Decimal | None]) -> str:
    ema5 = ema_values.get(5)
    ema10 = ema_values.get(10)
    ema20 = ema_values.get(20)
    ema30 = ema_values.get(30)
    ema40 = ema_values.get(40)

    if None in {ema5, ema10, ema20, ema30, ema40}:
        return "unknown"

    if ema5 > ema10 > ema20 > ema30 > ema40:
        return "bullish"

    if ema5 < ema10 < ema20 < ema30 < ema40:
        return "bearish"

    return "mixed"


def classify_price_vs_average(price: Decimal, average: Decimal | None) -> str:
    if average is None:
        return "unknown"
    if price > average:
        return "above"
    if price < average:
        return "below"
    return "touching"


def classify_rsi_zone(rsi_value: Decimal | None) -> str:
    if rsi_value is None:
        return "unknown"
    if rsi_value <= Decimal("30"):
        return "oversold"
    if rsi_value < Decimal("40"):
        return "oversold_exit"
    if rsi_value >= Decimal("70"):
        return "overbought"
    if rsi_value > Decimal("60"):
        return "overbought_exit"
    return "neutral"


def classify_macd_state(
    current_macd: dict[str, Decimal | None],
    previous_macd: dict[str, Decimal | None],
) -> str:
    current_line = current_macd.get("macd_line")
    current_signal = current_macd.get("signal_line")
    previous_line = previous_macd.get("macd_line")
    previous_signal = previous_macd.get("signal_line")

    if (
        current_line is None
        or current_signal is None
        or previous_line is None
        or previous_signal is None
    ):
        return "unknown"

    if previous_line <= previous_signal and current_line > current_signal:
        return "bullish_cross"

    if previous_line >= previous_signal and current_line < current_signal:
        return "bearish_cross"

    if current_line > current_signal:
        return "bullish_above_signal"

    if current_line < current_signal:
        return "bearish_below_signal"

    return "neutral"


def calculate_band_position(
    close: Decimal,
    lower_band: Decimal | None,
    upper_band: Decimal | None,
) -> Decimal | None:
    if lower_band is None or upper_band is None:
        return None

    width = upper_band - lower_band
    if width == 0:
        return Decimal("0.5")

    return (close - lower_band) / width


def classify_session(hour: int) -> str:
    if 0 <= hour < 7:
        return "asia"
    if 7 <= hour < 12:
        return "london"
    if 12 <= hour < 17:
        return "new_york"
    if 17 <= hour < 21:
        return "us_late"
    return "off_hours"


def build_candle_stats(candle: Candle) -> dict:
    body = abs(candle.close - candle.open)
    candle_range = candle.high - candle.low

    upper_wick = candle.high - max(candle.open, candle.close)
    lower_wick = min(candle.open, candle.close) - candle.low

    body_ratio = None
    if candle_range > 0:
        body_ratio = body / candle_range

    candle_type = classify_candle_type(
        open_price=candle.open,
        close_price=candle.close,
        body=body,
        upper_wick=upper_wick,
        lower_wick=lower_wick,
        candle_range=candle_range,
    )

    return {
        "open": as_str(candle.open),
        "high": as_str(candle.high),
        "low": as_str(candle.low),
        "close": as_str(candle.close),
        "body_size": as_str(body),
        "upper_wick": as_str(upper_wick),
        "lower_wick": as_str(lower_wick),
        "body_ratio": as_str(body_ratio),
        "candle_type": candle_type,
    }


def classify_candle_type(
    open_price: Decimal,
    close_price: Decimal,
    body: Decimal,
    upper_wick: Decimal,
    lower_wick: Decimal,
    candle_range: Decimal,
) -> str:
    if candle_range == 0:
        return "flat"

    body_ratio = body / candle_range

    if body_ratio <= Decimal("0.15"):
        return "doji"

    if lower_wick > body * Decimal("1.5") and close_price > open_price:
        return "rejection"

    if upper_wick > body * Decimal("1.5") and close_price < open_price:
        return "rejection"

    if close_price > open_price and body_ratio >= Decimal("0.6"):
        return "bullish_impulse"

    if close_price < open_price and body_ratio >= Decimal("0.6"):
        return "bearish_impulse"

    return "balanced"


def classify_market_structure(candles: list[Candle]) -> str:
    if len(candles) < 5:
        return "unknown"

    recent = candles[-5:]
    closes = [item.close for item in recent]
    highs = [item.high for item in recent]
    lows = [item.low for item in recent]

    if closes[-1] > closes[0] and highs[-1] >= max(highs[:-1]) and lows[-1] >= min(lows[:-1]):
        return "bullish"

    if closes[-1] < closes[0] and lows[-1] <= min(lows[:-1]) and highs[-1] <= max(highs[:-1]):
        return "bearish"

    return "range"


def classify_entry_location(
    market_structure: str,
    close: Decimal,
    ema20: Decimal | None,
    lower_band: Decimal | None,
    upper_band: Decimal | None,
) -> str:
    if lower_band is not None and close <= lower_band:
        return "range_edge"

    if upper_band is not None and close >= upper_band:
        return "range_edge"

    if ema20 is not None:
        distance = abs(close - ema20)
        if distance <= Decimal("0.00030"):
            return "pullback"

    if market_structure == "bullish":
        return "pullback"

    if market_structure == "bearish":
        return "breakout"

    return "mid_range"


def distance_to_recent_support(candles: list[Candle]) -> Decimal | None:
    if not candles:
        return None
    current_close = candles[-1].close
    lowest = min(candle.low for candle in candles[-10:])
    return abs(current_close - lowest)


def distance_to_recent_resistance(candles: list[Candle]) -> Decimal | None:
    if not candles:
        return None
    current_close = candles[-1].close
    highest = max(candle.high for candle in candles[-10:])
    return abs(highest - current_close)


def distance_to_level(price: Decimal, level: Decimal | None) -> Decimal | None:
    if level is None:
        return None
    return abs(price - level)


def classify_atr_regime(
    candles: list[Candle],
    current_atr: Decimal | None,
    atr_period: int,
) -> str:
    if current_atr is None:
        return "unknown"

    series = average_true_range_series(candles, atr_period)
    recent_values = [item for item in series[-20:] if item is not None]

    if len(recent_values) < 5:
        return "normal"

    baseline = sum(recent_values) / Decimal(len(recent_values))

    if baseline == 0:
        return "normal"

    if current_atr < baseline * Decimal("0.85"):
        return "low"

    if current_atr > baseline * Decimal("1.15"):
        return "high"

    return "normal"