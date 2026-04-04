# app/strategies/analysis_snapshot_builder.py

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, Dict, List, Optional


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_mean(values: List[float], default: float = 0.0) -> float:
    clean = [v for v in values if isinstance(v, (int, float))]
    if not clean:
        return default
    return float(mean(clean))


def _ema(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None

    multiplier = 2 / (period + 1)
    ema_value = _safe_mean(values[:period], 0.0)

    for price in values[period:]:
        ema_value = ((price - ema_value) * multiplier) + ema_value

    return ema_value


def _sma(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None
    return _safe_mean(values[-period:], 0.0)


def _stddev(values: List[float], period: int) -> Optional[float]:
    if len(values) < period or period <= 0:
        return None

    window = values[-period:]
    avg = _safe_mean(window, 0.0)
    variance = _safe_mean([(v - avg) ** 2 for v in window], 0.0)
    return variance ** 0.5


def _true_range(current: Candle, previous_close: Optional[float]) -> float:
    if previous_close is None:
        return current.high - current.low

    return max(
        current.high - current.low,
        abs(current.high - previous_close),
        abs(current.low - previous_close),
    )


def _atr(candles: List[Candle], period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None

    trs: List[float] = []
    previous_close: Optional[float] = None

    for candle in candles[-(period + 1):]:
        trs.append(_true_range(candle, previous_close))
        previous_close = candle.close

    if len(trs) < 2:
        return None

    return _safe_mean(trs[1:], 0.0)


def _rsi(closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None

    gains: List[float] = []
    losses: List[float] = []

    for i in range(len(closes) - period, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0.0))
        losses.append(abs(min(diff, 0.0)))

    avg_gain = _safe_mean(gains, 0.0)
    avg_loss = _safe_mean(losses, 0.0)

    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _vwap(candles: List[Candle], period: int = 20) -> Optional[float]:
    if len(candles) < 1:
        return None

    window = candles[-period:] if len(candles) >= period else candles
    total_pv = 0.0
    total_volume = 0.0

    for candle in window:
        typical_price = (candle.high + candle.low + candle.close) / 3
        total_pv += typical_price * candle.volume
        total_volume += candle.volume

    if total_volume <= 0:
        return None

    return total_pv / total_volume


def _adx(candles: List[Candle], period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None

    plus_dm_list: List[float] = []
    minus_dm_list: List[float] = []
    tr_list: List[float] = []

    for i in range(len(candles) - period, len(candles)):
        current = candles[i]
        previous = candles[i - 1]

        up_move = current.high - previous.high
        down_move = previous.low - current.low

        plus_dm = up_move if up_move > down_move and up_move > 0 else 0.0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0.0

        tr = _true_range(current, previous.close)

        plus_dm_list.append(plus_dm)
        minus_dm_list.append(minus_dm)
        tr_list.append(tr)

    atr_value = _safe_mean(tr_list, 0.0)
    if atr_value == 0:
        return None

    plus_di = 100 * (_safe_mean(plus_dm_list, 0.0) / atr_value)
    minus_di = 100 * (_safe_mean(minus_dm_list, 0.0) / atr_value)

    denominator = plus_di + minus_di
    if denominator == 0:
        return 0.0

    dx = 100 * abs(plus_di - minus_di) / denominator
    return dx


def _volume_signal(volume_ratio: Optional[float]) -> str:
    if volume_ratio is None:
        return "unknown"
    if volume_ratio >= 1.5:
        return "high"
    if volume_ratio >= 1.0:
        return "normal"
    return "low"


def _vwap_state(side: str, last_close: float, vwap_value: Optional[float]) -> str:
    if vwap_value is None:
        return "unknown"

    if side == "buy":
        return "above" if last_close >= vwap_value else "below"

    if side == "sell":
        return "below" if last_close <= vwap_value else "above"

    return "unknown"


def _atr_regime(atr_value: Optional[float], atr_baseline: Optional[float]) -> str:
    if atr_value is None or atr_baseline is None or atr_baseline <= 0:
        return "normal"

    ratio = atr_value / atr_baseline

    if ratio >= 1.25:
        return "high"
    if ratio <= 0.85:
        return "low"
    return "normal"


def _macd_state(closes: List[float]) -> str:
    ema_12 = _ema(closes, 12)
    ema_26 = _ema(closes, 26)

    if ema_12 is None or ema_26 is None:
        return "neutral"

    macd_line = ema_12 - ema_26

    macd_series: List[float] = []
    for i in range(26, len(closes) + 1):
        partial = closes[:i]
        e12 = _ema(partial, 12)
        e26 = _ema(partial, 26)
        if e12 is not None and e26 is not None:
            macd_series.append(e12 - e26)

    signal = _ema(macd_series, 9) if len(macd_series) >= 9 else None
    if signal is None:
        return "neutral"

    return "above_signal" if macd_line >= signal else "below_signal"


def _ema_alignment(ema20: Optional[float], ema40: Optional[float], close: float) -> str:
    if ema20 is None or ema40 is None:
        return "mixed"

    if close > ema20 > ema40:
        return "bullish"

    if close < ema20 < ema40:
        return "bearish"

    return "mixed"


def _ema_slope_label(current_ema: Optional[float], previous_ema: Optional[float]) -> str:
    if current_ema is None or previous_ema is None:
        return "neutral"

    if current_ema > previous_ema:
        return "up"

    if current_ema < previous_ema:
        return "down"

    return "flat"


def _price_vs_level(close: float, level: Optional[float]) -> str:
    if level is None:
        return "neutral"
    return "above" if close >= level else "below"


def _candle_body_ratio(candle: Candle) -> float:
    total_range = candle.high - candle.low
    if total_range <= 0:
        return 0.0
    body = abs(candle.close - candle.open)
    return body / total_range


def _candle_type(candle: Candle) -> str:
    ratio = _candle_body_ratio(candle)
    if ratio >= 0.6:
        return "strong"
    if ratio >= 0.35:
        return "normal"
    return "weak"


def _wick_ratio(candle: Candle) -> Dict[str, float]:
    total_range = candle.high - candle.low
    if total_range <= 0:
        return {"upper_wick": 0.0, "lower_wick": 0.0}

    upper_wick = candle.high - max(candle.open, candle.close)
    lower_wick = min(candle.open, candle.close) - candle.low

    return {
        "upper_wick": max(0.0, upper_wick / total_range),
        "lower_wick": max(0.0, lower_wick / total_range),
    }


def _distance_to_support(candles: List[Candle], close: float, lookback: int = 20) -> Optional[float]:
    if not candles:
        return None

    lows = [c.low for c in candles[-lookback:]]
    if not lows:
        return None

    recent_support = min(lows)
    return abs(close - recent_support)


def _distance_to_resistance(candles: List[Candle], close: float, lookback: int = 20) -> Optional[float]:
    if not candles:
        return None

    highs = [c.high for c in candles[-lookback:]]
    if not highs:
        return None

    recent_resistance = max(highs)
    return abs(recent_resistance - close)


def _market_structure(candles: List[Candle], lookback: int = 6) -> str:
    if len(candles) < lookback:
        return "range"

    highs = [c.high for c in candles[-lookback:]]
    lows = [c.low for c in candles[-lookback:]]

    rising_highs = highs[-1] > highs[0]
    rising_lows = lows[-1] > lows[0]
    falling_highs = highs[-1] < highs[0]
    falling_lows = lows[-1] < lows[0]

    if rising_highs and rising_lows:
        return "uptrend"

    if falling_highs and falling_lows:
        return "downtrend"

    return "range"


def _next_candle_confirmation(side: str, trigger_candle: Candle, next_candle: Optional[Candle]) -> Optional[bool]:
    if next_candle is None:
        return None

    if side == "buy":
        return next_candle.close >= trigger_candle.close and next_candle.low >= trigger_candle.low

    if side == "sell":
        return next_candle.close <= trigger_candle.close and next_candle.high <= trigger_candle.high

    return None


def build_analysis_snapshot(
    candles_raw: List[Dict[str, Any]],
    trigger_index: int,
    side: str,
    bollinger_upper: Optional[float] = None,
    bollinger_lower: Optional[float] = None,
    bollinger_mid: Optional[float] = None,
) -> Dict[str, Any]:
    candles = [
        Candle(
            open=_to_float(c.get("open")),
            high=_to_float(c.get("high")),
            low=_to_float(c.get("low")),
            close=_to_float(c.get("close")),
            volume=_to_float(c.get("volume")),
        )
        for c in candles_raw
    ]

    if not candles:
        return {}

    if trigger_index < 0 or trigger_index >= len(candles):
        trigger_index = len(candles) - 1

    context_candles = candles[: trigger_index + 1]
    trigger_candle = candles[trigger_index]
    next_candle = candles[trigger_index + 1] if trigger_index + 1 < len(candles) else None

    closes = [c.close for c in context_candles]
    volumes = [c.volume for c in context_candles]

    last_close = trigger_candle.close

    ema20 = _ema(closes, 20)
    ema40 = _ema(closes, 40)
    prev_ema20 = _ema(closes[:-1], 20) if len(closes) > 20 else None

    atr14 = _atr(context_candles, 14)
    atr_baseline = _safe_mean(
        [
            v
            for v in [
                _atr(context_candles[:i], 14)
                for i in range(max(15, len(context_candles) - 10), len(context_candles) + 1)
            ]
            if v is not None
        ],
        0.0,
    )
    atr_regime = _atr_regime(atr14, atr_baseline if atr_baseline > 0 else None)

    rsi14 = _rsi(closes, 14)
    macd_state = _macd_state(closes)

    market_structure = _market_structure(context_candles, 6)
    ema_alignment = _ema_alignment(ema20, ema40, last_close)
    ema20_slope = _ema_slope_label(ema20, prev_ema20)
    price_vs_ema20 = _price_vs_level(last_close, ema20)
    price_vs_ema40 = _price_vs_level(last_close, ema40)

    support_distance = _distance_to_support(context_candles, last_close, 20)
    resistance_distance = _distance_to_resistance(context_candles, last_close, 20)

    candle_range = trigger_candle.high - trigger_candle.low
    candle_range_vs_atr = candle_range / atr14 if atr14 and atr14 > 0 else None

    candle_type = _candle_type(trigger_candle)
    body_ratio = _candle_body_ratio(trigger_candle)
    wick_data = _wick_ratio(trigger_candle)

    avg_volume_20 = _sma(volumes, 20)
    volume_ratio = (
        trigger_candle.volume / avg_volume_20
        if avg_volume_20 is not None and avg_volume_20 > 0
        else None
    )

    vwap_value = _vwap(context_candles, 20)
    vwap_state = _vwap_state(side, last_close, vwap_value)

    z_score: Optional[float] = None
    distance_outside_band: Optional[float] = None
    reentered_inside_band_long = False
    reentered_inside_band_short = False

    if bollinger_upper is not None and bollinger_lower is not None and bollinger_mid is not None:
        band_half = (bollinger_upper - bollinger_lower) / 2
        if band_half > 0:
            z_score = (last_close - bollinger_mid) / band_half

        if side == "buy" and last_close >= bollinger_lower:
            reentered_inside_band_long = True
        if side == "sell" and last_close <= bollinger_upper:
            reentered_inside_band_short = True

        if last_close > bollinger_upper:
            distance_outside_band = last_close - bollinger_upper
        elif last_close < bollinger_lower:
            distance_outside_band = bollinger_lower - last_close
        else:
            distance_outside_band = 0.0

    adx14 = _adx(context_candles, 14)
    next_confirmation = _next_candle_confirmation(side, trigger_candle, next_candle)

    return {
        "trend": {
            "ema_alignment": ema_alignment,
            "ema_20_slope": ema20_slope,
            "price_vs_ema_20": price_vs_ema20,
            "price_vs_ema_40": price_vs_ema40,
            "price_vs_vwap": vwap_state,
            "vwap_state": vwap_state,
            "adx_14": adx14,
        },
        "momentum": {
            "rsi_14": rsi14,
            "macd_state": macd_state,
            "volume_ratio": volume_ratio,
            "volume_signal": _volume_signal(volume_ratio),
        },
        "volatility": {
            "atr_14": atr14,
            "atr_regime": atr_regime,
            "candle_range_vs_atr": candle_range_vs_atr,
        },
        "structure": {
            "market_structure": market_structure,
            "distance_to_recent_support": support_distance,
            "distance_to_recent_resistance": resistance_distance,
            "price_vs_vwap": vwap_state,
            "adx_14": adx14,
        },
        "trigger_candle": {
            "body_ratio": body_ratio,
            "candle_type": candle_type,
            "upper_wick": wick_data["upper_wick"],
            "lower_wick": wick_data["lower_wick"],
            "next_candle_confirmation": next_confirmation,
        },
        "bollinger": {
            "reentered_inside_band_long": reentered_inside_band_long,
            "reentered_inside_band_short": reentered_inside_band_short,
            "close_position_in_band": None,
            "z_score": z_score,
            "distance_outside_band": distance_outside_band,
        },
        "volume": {
            "ratio": volume_ratio,
            "signal": _volume_signal(volume_ratio),
        },
        "vwap": {
            "state": vwap_state,
        },
        "post_trigger": {
            "next_candle_confirmation": next_confirmation,
        },
    }