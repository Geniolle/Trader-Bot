# C:\Trader-bot\app\services\candlestick_intelligence.py

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.models.domain.candle import Candle


DECIMAL_ZERO = Decimal("0")
DECIMAL_ONE = Decimal("1")
DECIMAL_TWO = Decimal("2")
DECIMAL_HALF = Decimal("0.5")

DECIMAL_POINT_15 = Decimal("0.15")
DECIMAL_POINT_20 = Decimal("0.20")
DECIMAL_POINT_25 = Decimal("0.25")
DECIMAL_POINT_30 = Decimal("0.30")
DECIMAL_POINT_35 = Decimal("0.35")
DECIMAL_POINT_40 = Decimal("0.40")
DECIMAL_POINT_50 = Decimal("0.50")
DECIMAL_POINT_55 = Decimal("0.55")
DECIMAL_POINT_60 = Decimal("0.60")
DECIMAL_POINT_65 = Decimal("0.65")
DECIMAL_POINT_70 = Decimal("0.70")
DECIMAL_POINT_75 = Decimal("0.75")
DECIMAL_POINT_80 = Decimal("0.80")


def decimal_to_str(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def safe_ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return DECIMAL_ZERO
    return numerator / denominator


def normalize_direction(direction: str | None) -> str:
    normalized = str(direction or "").strip().lower()
    if normalized in {"buy", "long", "bullish", "compradora"}:
        return "buy"
    if normalized in {"sell", "short", "bearish", "vendedora"}:
        return "sell"
    return "buy"


def candle_color(candle: Candle) -> str:
    if candle.close > candle.open:
        return "bullish"
    if candle.close < candle.open:
        return "bearish"
    return "neutral"


def candle_body(candle: Candle) -> Decimal:
    return abs(candle.close - candle.open)


def candle_range(candle: Candle) -> Decimal:
    return max(DECIMAL_ZERO, candle.high - candle.low)


def upper_wick(candle: Candle) -> Decimal:
    return max(DECIMAL_ZERO, candle.high - max(candle.open, candle.close))


def lower_wick(candle: Candle) -> Decimal:
    return max(DECIMAL_ZERO, min(candle.open, candle.close) - candle.low)


def body_ratio(candle: Candle) -> Decimal:
    return safe_ratio(candle_body(candle), candle_range(candle))


def upper_wick_ratio(candle: Candle) -> Decimal:
    return safe_ratio(upper_wick(candle), candle_range(candle))


def lower_wick_ratio(candle: Candle) -> Decimal:
    return safe_ratio(lower_wick(candle), candle_range(candle))


def close_position(candle: Candle) -> str:
    c_range = candle_range(candle)
    if c_range == 0:
        return "flat"

    distance_from_low = candle.close - candle.low
    ratio = safe_ratio(distance_from_low, c_range)

    if ratio >= DECIMAL_POINT_80:
        return "near_high"

    if ratio <= DECIMAL_POINT_20:
        return "near_low"

    if DECIMAL_POINT_40 <= ratio <= DECIMAL_POINT_60:
        return "mid"

    if ratio > DECIMAL_POINT_60:
        return "upper_half"

    return "lower_half"


def classify_single_candle_pattern(candle: Candle) -> str:
    c_body = candle_body(candle)
    c_range = candle_range(candle)
    c_body_ratio = body_ratio(candle)
    c_upper = upper_wick(candle)
    c_lower = lower_wick(candle)
    color = candle_color(candle)

    if c_range == 0:
        return "flat"

    if c_body_ratio <= DECIMAL_POINT_15:
        if c_lower >= c_body * DECIMAL_TWO and c_upper <= c_body:
            return "dragonfly_doji"
        if c_upper >= c_body * DECIMAL_TWO and c_lower <= c_body:
            return "gravestone_doji"
        if c_upper >= c_body and c_lower >= c_body:
            return "long_legged_doji"
        return "doji"

    if (
        c_body_ratio >= DECIMAL_POINT_75
        and c_upper <= c_body * DECIMAL_POINT_15
        and c_lower <= c_body * DECIMAL_POINT_15
    ):
        return "bullish_marubozu" if color == "bullish" else "bearish_marubozu"

    if c_body_ratio <= DECIMAL_POINT_35 and c_upper >= c_body * DECIMAL_TWO and c_lower >= c_body:
        return "spinning_top"

    if c_body <= c_range * DECIMAL_POINT_35 and c_lower >= c_body * DECIMAL_TWO and c_upper <= c_body * DECIMAL_HALF:
        return "hammer"

    if c_body <= c_range * DECIMAL_POINT_35 and c_upper >= c_body * DECIMAL_TWO and c_lower <= c_body * DECIMAL_HALF:
        return "shooting_star"

    if c_body_ratio >= DECIMAL_POINT_60:
        return "bullish_impulse" if color == "bullish" else "bearish_impulse"

    return "balanced"


def classify_strength_class(candle: Candle) -> str:
    pattern = classify_single_candle_pattern(candle)
    color = candle_color(candle)

    if pattern in {"bullish_marubozu", "bullish_impulse"}:
        return "bullish_force"

    if pattern in {"bearish_marubozu", "bearish_impulse"}:
        return "bearish_force"

    if pattern in {"dragonfly_doji", "gravestone_doji", "hammer", "shooting_star"}:
        return "rejection"

    if pattern in {"doji", "long_legged_doji", "spinning_top"}:
        return "indecision"

    if color == "bullish":
        return "bullish"

    if color == "bearish":
        return "bearish"

    return "neutral"


def build_candle_feature(candle: Candle, index_label: str) -> dict[str, Any]:
    return {
        "index_label": index_label,
        "open_time": candle.open_time.isoformat(),
        "close_time": candle.close_time.isoformat(),
        "open": decimal_to_str(candle.open),
        "high": decimal_to_str(candle.high),
        "low": decimal_to_str(candle.low),
        "close": decimal_to_str(candle.close),
        "color": candle_color(candle),
        "body_size": decimal_to_str(candle_body(candle)),
        "range_size": decimal_to_str(candle_range(candle)),
        "body_ratio": decimal_to_str(body_ratio(candle)),
        "upper_wick": decimal_to_str(upper_wick(candle)),
        "lower_wick": decimal_to_str(lower_wick(candle)),
        "upper_wick_ratio": decimal_to_str(upper_wick_ratio(candle)),
        "lower_wick_ratio": decimal_to_str(lower_wick_ratio(candle)),
        "close_position": close_position(candle),
        "pattern": classify_single_candle_pattern(candle),
        "strength_class": classify_strength_class(candle),
    }


def is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open


def body_midpoint(candle: Candle) -> Decimal:
    return (candle.open + candle.close) / DECIMAL_TWO


def detect_bullish_engulfing(prev_candle: Candle, current_candle: Candle) -> bool:
    return (
        is_bearish(prev_candle)
        and is_bullish(current_candle)
        and current_candle.open <= prev_candle.close
        and current_candle.close >= prev_candle.open
    )


def detect_bearish_engulfing(prev_candle: Candle, current_candle: Candle) -> bool:
    return (
        is_bullish(prev_candle)
        and is_bearish(current_candle)
        and current_candle.open >= prev_candle.close
        and current_candle.close <= prev_candle.open
    )


def detect_bullish_harami(prev_candle: Candle, current_candle: Candle) -> bool:
    prev_low_body = min(prev_candle.open, prev_candle.close)
    prev_high_body = max(prev_candle.open, prev_candle.close)
    curr_low_body = min(current_candle.open, current_candle.close)
    curr_high_body = max(current_candle.open, current_candle.close)

    return (
        is_bearish(prev_candle)
        and is_bullish(current_candle)
        and curr_low_body >= prev_low_body
        and curr_high_body <= prev_high_body
    )


def detect_bearish_harami(prev_candle: Candle, current_candle: Candle) -> bool:
    prev_low_body = min(prev_candle.open, prev_candle.close)
    prev_high_body = max(prev_candle.open, prev_candle.close)
    curr_low_body = min(current_candle.open, current_candle.close)
    curr_high_body = max(current_candle.open, current_candle.close)

    return (
        is_bullish(prev_candle)
        and is_bearish(current_candle)
        and curr_low_body >= prev_low_body
        and curr_high_body <= prev_high_body
    )


def detect_piercing_line(prev_candle: Candle, current_candle: Candle) -> bool:
    return (
        is_bearish(prev_candle)
        and is_bullish(current_candle)
        and current_candle.close > body_midpoint(prev_candle)
        and current_candle.close < prev_candle.open
    )


def detect_dark_cloud_cover(prev_candle: Candle, current_candle: Candle) -> bool:
    return (
        is_bullish(prev_candle)
        and is_bearish(current_candle)
        and current_candle.close < body_midpoint(prev_candle)
        and current_candle.close > prev_candle.open
    )


def detect_morning_star(a: Candle, b: Candle, c: Candle) -> bool:
    return (
        is_bearish(a)
        and candle_body(b) <= candle_body(a) * DECIMAL_HALF
        and is_bullish(c)
        and c.close > body_midpoint(a)
    )


def detect_evening_star(a: Candle, b: Candle, c: Candle) -> bool:
    return (
        is_bullish(a)
        and candle_body(b) <= candle_body(a) * DECIMAL_HALF
        and is_bearish(c)
        and c.close < body_midpoint(a)
    )


def detect_three_inside_up(a: Candle, b: Candle, c: Candle) -> bool:
    return detect_bullish_harami(a, b) and is_bullish(c) and c.close > max(a.open, a.close)


def detect_three_inside_down(a: Candle, b: Candle, c: Candle) -> bool:
    return detect_bearish_harami(a, b) and is_bearish(c) and c.close < min(a.open, a.close)


def detect_three_outside_up(a: Candle, b: Candle, c: Candle) -> bool:
    return detect_bullish_engulfing(a, b) and is_bullish(c) and c.close >= b.close


def detect_three_outside_down(a: Candle, b: Candle, c: Candle) -> bool:
    return detect_bearish_engulfing(a, b) and is_bearish(c) and c.close <= b.close


def detect_three_white_soldiers(window: list[Candle]) -> bool:
    if len(window) < 3:
        return False

    last_three = window[-3:]
    return all(
        is_bullish(candle)
        and body_ratio(candle) >= DECIMAL_POINT_55
        and upper_wick_ratio(candle) <= DECIMAL_POINT_25
        for candle in last_three
    )


def detect_three_black_crows(window: list[Candle]) -> bool:
    if len(window) < 3:
        return False

    last_three = window[-3:]
    return all(
        is_bearish(candle)
        and body_ratio(candle) >= DECIMAL_POINT_55
        and lower_wick_ratio(candle) <= DECIMAL_POINT_25
        for candle in last_three
    )


def detect_patterns(window: list[Candle]) -> dict[str, bool]:
    result = {
        "bullish_engulfing": False,
        "bearish_engulfing": False,
        "bullish_harami": False,
        "bearish_harami": False,
        "piercing_line": False,
        "dark_cloud_cover": False,
        "morning_star": False,
        "evening_star": False,
        "three_inside_up": False,
        "three_inside_down": False,
        "three_outside_up": False,
        "three_outside_down": False,
        "three_white_soldiers": False,
        "three_black_crows": False,
    }

    if len(window) >= 2:
        a = window[-2]
        b = window[-1]
        result["bullish_engulfing"] = detect_bullish_engulfing(a, b)
        result["bearish_engulfing"] = detect_bearish_engulfing(a, b)
        result["bullish_harami"] = detect_bullish_harami(a, b)
        result["bearish_harami"] = detect_bearish_harami(a, b)
        result["piercing_line"] = detect_piercing_line(a, b)
        result["dark_cloud_cover"] = detect_dark_cloud_cover(a, b)

    if len(window) >= 3:
        a = window[-3]
        b = window[-2]
        c = window[-1]
        result["morning_star"] = detect_morning_star(a, b, c)
        result["evening_star"] = detect_evening_star(a, b, c)
        result["three_inside_up"] = detect_three_inside_up(a, b, c)
        result["three_inside_down"] = detect_three_inside_down(a, b, c)
        result["three_outside_up"] = detect_three_outside_up(a, b, c)
        result["three_outside_down"] = detect_three_outside_down(a, b, c)
        result["three_white_soldiers"] = detect_three_white_soldiers(window)
        result["three_black_crows"] = detect_three_black_crows(window)

    return result


def active_pattern_names(patterns: dict[str, bool]) -> list[str]:
    return [name for name, active in patterns.items() if active]


def summarize_sequence_bias(window: list[Candle]) -> str:
    bullish_force = sum(
        1 for candle in window if classify_strength_class(candle) == "bullish_force"
    )
    bearish_force = sum(
        1 for candle in window if classify_strength_class(candle) == "bearish_force"
    )
    rejections = sum(
        1 for candle in window if classify_strength_class(candle) == "rejection"
    )

    if bullish_force >= bearish_force + 2:
        return "bullish_pressure"

    if bearish_force >= bullish_force + 2:
        return "bearish_pressure"

    if rejections >= 2:
        return "rejection_fight"

    return "mixed"


def detect_exhaustion(window: list[Candle], direction: str) -> bool:
    if len(window) < 4:
        return False

    previous_three = window[-4:-1]
    trigger_candle = window[-1]
    direction = normalize_direction(direction)

    if direction == "buy":
        previous_bearish_force = sum(
            1
            for candle in previous_three
            if classify_strength_class(candle) == "bearish_force"
        )
        trigger_pattern = classify_single_candle_pattern(trigger_candle)
        return previous_bearish_force >= 1 and trigger_pattern in {
            "hammer",
            "dragonfly_doji",
            "bullish_impulse",
            "bullish_marubozu",
        }

    previous_bullish_force = sum(
        1
        for candle in previous_three
        if classify_strength_class(candle) == "bullish_force"
    )
    trigger_pattern = classify_single_candle_pattern(trigger_candle)
    return previous_bullish_force >= 1 and trigger_pattern in {
        "shooting_star",
        "gravestone_doji",
        "bearish_impulse",
        "bearish_marubozu",
    }


def detect_impulsion(window: list[Candle], direction: str) -> bool:
    if not window:
        return False

    trigger_candle = window[-1]
    strength = classify_strength_class(trigger_candle)
    direction = normalize_direction(direction)

    if direction == "buy":
        return strength == "bullish_force"

    return strength == "bearish_force"


def detect_continuity(window: list[Candle], direction: str) -> bool:
    if len(window) < 3:
        return False

    direction = normalize_direction(direction)
    relevant = window[-4:-1]
    if len(relevant) < 2:
        return False

    if direction == "buy":
        bullish_force_count = sum(
            1
            for candle in relevant
            if candle_color(candle) == "bullish" and body_ratio(candle) >= DECIMAL_POINT_55
        )
        bullish_closes_higher = sum(
            1
            for i in range(1, len(relevant))
            if relevant[i].close >= relevant[i - 1].close
        )
        return bullish_force_count >= 2 and bullish_closes_higher >= 1

    bearish_force_count = sum(
        1
        for candle in relevant
        if candle_color(candle) == "bearish" and body_ratio(candle) >= DECIMAL_POINT_55
    )
    bearish_closes_lower = sum(
        1
        for i in range(1, len(relevant))
        if relevant[i].close <= relevant[i - 1].close
    )
    return bearish_force_count >= 2 and bearish_closes_lower >= 1


def detect_opposite_weakness(window: list[Candle], direction: str) -> bool:
    if len(window) < 3:
        return False

    previous_two = window[-3:-1]
    direction = normalize_direction(direction)

    if direction == "buy":
        return all(
            candle_color(candle) != "bearish"
            or upper_wick_ratio(candle) < lower_wick_ratio(candle)
            or body_ratio(candle) <= DECIMAL_POINT_40
            for candle in previous_two
        )

    return all(
        candle_color(candle) != "bullish"
        or lower_wick_ratio(candle) < upper_wick_ratio(candle)
        or body_ratio(candle) <= DECIMAL_POINT_40
        for candle in previous_two
    )


def build_force_reading(window: list[Candle], direction: str) -> dict[str, Any]:
    trigger_candle = window[-1]
    trigger_feature = build_candle_feature(trigger_candle, "trigger")

    prior_features = [
        build_candle_feature(candle, f"lookback_{index + 1}")
        for index, candle in enumerate(window[:-1])
    ]

    sequence_bias = summarize_sequence_bias(window)
    patterns = detect_patterns(window)

    exhaustion = detect_exhaustion(window, direction)
    impulsion = detect_impulsion(window, direction)
    continuity = detect_continuity(window, direction)
    opposite_weakness = detect_opposite_weakness(window, direction)

    active_patterns = active_pattern_names(patterns)
    dominant_pattern = active_patterns[0] if active_patterns else trigger_feature["pattern"]

    sequence_summary_parts: list[str] = [f"bias={sequence_bias}"]
    if exhaustion:
        sequence_summary_parts.append("exaustao")
    if impulsion:
        sequence_summary_parts.append("impulsao")
    if continuity:
        sequence_summary_parts.append("continuidade")
    if opposite_weakness:
        sequence_summary_parts.append("fraqueza_do_lado_oposto")
    if active_patterns:
        sequence_summary_parts.append(f"padrao={','.join(active_patterns)}")

    return {
        "window_size": len(window),
        "trigger_candle": trigger_feature,
        "prior_candles": prior_features,
        "sequence_bias": sequence_bias,
        "exhaustion_detected": exhaustion,
        "impulsion_detected": impulsion,
        "continuity_detected": continuity,
        "opposite_side_weakness": opposite_weakness,
        "patterns": patterns,
        "active_patterns": active_patterns,
        "dominant_pattern": dominant_pattern,
        "sequence_summary": " | ".join(sequence_summary_parts),
    }


def build_macro_context(
    direction: str,
    trend_alignment: str,
    price_vs_ema_20: str,
    price_vs_ema_40: str,
    macd_state: str,
    market_structure: str,
    continuity_detected: bool,
) -> dict[str, Any]:
    macro_points = 0
    macro_signals: list[str] = []

    if direction == "buy":
        if trend_alignment == "bullish":
            macro_points += 1
            macro_signals.append("alinhamento_ema_bullish")
        if price_vs_ema_20 == "above":
            macro_points += 1
            macro_signals.append("preco_acima_ema20")
        if price_vs_ema_40 == "above":
            macro_points += 1
            macro_signals.append("preco_acima_ema40")
        if macd_state in {"bullish_cross", "bullish_above_signal"}:
            macro_points += 1
            macro_signals.append("macd_comprador")
        if market_structure == "bullish":
            macro_points += 1
            macro_signals.append("estrutura_bullish")
    else:
        if trend_alignment == "bearish":
            macro_points += 1
            macro_signals.append("alinhamento_ema_bearish")
        if price_vs_ema_20 == "below":
            macro_points += 1
            macro_signals.append("preco_abaixo_ema20")
        if price_vs_ema_40 == "below":
            macro_points += 1
            macro_signals.append("preco_abaixo_ema40")
        if macd_state in {"bearish_cross", "bearish_below_signal"}:
            macro_points += 1
            macro_signals.append("macd_vendedor")
        if market_structure == "bearish":
            macro_points += 1
            macro_signals.append("estrutura_bearish")

    if continuity_detected:
        macro_points += 1
        macro_signals.append("continuidade_detectada")

    macro_is_strong = macro_points >= 4
    macro_is_moderate = macro_points >= 3

    return {
        "macro_points": macro_points,
        "macro_signals": macro_signals,
        "macro_is_strong": macro_is_strong,
        "macro_is_moderate": macro_is_moderate,
    }


def score_confirmation(
    setup_direction: str,
    force_reading: dict[str, Any],
    trend_alignment: str,
    price_vs_ema_20: str,
    price_vs_ema_40: str,
    macd_state: str,
    rsi_slope: str,
    market_structure: str,
    adx_value: Decimal | None,
) -> dict[str, Any]:
    direction = normalize_direction(setup_direction)

    score = 0
    reasons_for: list[str] = []
    reasons_against: list[str] = []

    trigger_pattern = str(force_reading.get("trigger_candle", {}).get("pattern", "")).strip()
    trigger_strength_class = str(
        force_reading.get("trigger_candle", {}).get("strength_class", "")
    ).strip()
    active_patterns = force_reading.get("active_patterns", [])
    exhaustion_detected = bool(force_reading.get("exhaustion_detected"))
    impulsion_detected = bool(force_reading.get("impulsion_detected"))
    continuity_detected = bool(force_reading.get("continuity_detected"))
    opposite_side_weakness = bool(force_reading.get("opposite_side_weakness"))

    bullish_patterns = {
        "bullish_engulfing",
        "piercing_line",
        "morning_star",
        "three_inside_up",
        "three_outside_up",
        "three_white_soldiers",
        "bullish_harami",
    }
    bearish_patterns = {
        "bearish_engulfing",
        "dark_cloud_cover",
        "evening_star",
        "three_inside_down",
        "three_outside_down",
        "three_black_crows",
        "bearish_harami",
    }

    macro_context = build_macro_context(
        direction=direction,
        trend_alignment=trend_alignment,
        price_vs_ema_20=price_vs_ema_20,
        price_vs_ema_40=price_vs_ema_40,
        macd_state=macd_state,
        market_structure=market_structure,
        continuity_detected=continuity_detected,
    )

    macro_points = int(macro_context["macro_points"])
    macro_is_strong = bool(macro_context["macro_is_strong"])
    macro_is_moderate = bool(macro_context["macro_is_moderate"])

    if direction == "buy":
        if trend_alignment == "bullish":
            score += 2
            reasons_for.append("alinhamento_ema_bullish")
        elif trend_alignment == "bearish":
            score -= 2
            reasons_against.append("alinhamento_ema_contra")

        if price_vs_ema_20 == "above":
            score += 2
            reasons_for.append("preco_acima_ema20")
        else:
            score -= 1
            reasons_against.append("preco_nao_acima_ema20")

        if price_vs_ema_40 == "above":
            score += 2
            reasons_for.append("preco_acima_ema40")
        else:
            score -= 1
            reasons_against.append("preco_nao_acima_ema40")

        if macd_state in {"bullish_cross", "bullish_above_signal"}:
            score += 2
            reasons_for.append("macd_comprador")

        if rsi_slope == "up":
            score += 1
            reasons_for.append("rsi_a_subir")
        elif rsi_slope == "down":
            score -= 1
            reasons_against.append("rsi_a_descer")

        if market_structure == "bullish":
            score += 2
            reasons_for.append("estrutura_bullish")
        elif market_structure == "bearish":
            score -= 2
            reasons_against.append("estrutura_contra")

        if trigger_pattern in {"hammer", "bullish_impulse", "bullish_marubozu", "dragonfly_doji"}:
            score += 2
            reasons_for.append(f"trigger_pattern={trigger_pattern}")
        elif trigger_strength_class == "bearish_force":
            penalty = 0 if macro_is_strong else 1 if macro_is_moderate else 2
            if penalty > 0:
                score -= penalty
                reasons_against.append("trigger_contra_o_setup")

    else:
        if trend_alignment == "bearish":
            score += 2
            reasons_for.append("alinhamento_ema_bearish")
        elif trend_alignment == "bullish":
            score -= 2
            reasons_against.append("alinhamento_ema_contra")

        if price_vs_ema_20 == "below":
            score += 2
            reasons_for.append("preco_abaixo_ema20")
        else:
            score -= 1
            reasons_against.append("preco_nao_abaixo_ema20")

        if price_vs_ema_40 == "below":
            score += 2
            reasons_for.append("preco_abaixo_ema40")
        else:
            score -= 1
            reasons_against.append("preco_nao_abaixo_ema40")

        if macd_state in {"bearish_cross", "bearish_below_signal"}:
            score += 2
            reasons_for.append("macd_vendedor")

        if rsi_slope == "down":
            score += 1
            reasons_for.append("rsi_a_descer")
        elif rsi_slope == "up":
            score -= 1
            reasons_against.append("rsi_a_subir")

        if market_structure == "bearish":
            score += 2
            reasons_for.append("estrutura_bearish")
        elif market_structure == "bullish":
            score -= 2
            reasons_against.append("estrutura_contra")

        if trigger_pattern in {"shooting_star", "bearish_impulse", "bearish_marubozu", "gravestone_doji"}:
            score += 2
            reasons_for.append(f"trigger_pattern={trigger_pattern}")
        elif trigger_strength_class == "bullish_force":
            penalty = 0 if macro_is_strong else 1 if macro_is_moderate else 2
            if penalty > 0:
                score -= penalty
                reasons_against.append("trigger_contra_o_setup")

    if adx_value is not None:
        if adx_value >= Decimal("25"):
            score += 1
            reasons_for.append("adx_forte")
        elif adx_value < Decimal("12"):
            penalty = 0 if macro_is_strong else 1
            if penalty > 0:
                score -= penalty
                reasons_against.append("adx_fraco")

    for pattern_name in active_patterns:
        if direction == "buy" and pattern_name in bullish_patterns:
            score += 2
            reasons_for.append(f"padrao_favoravel={pattern_name}")
        elif direction == "sell" and pattern_name in bearish_patterns:
            score += 2
            reasons_for.append(f"padrao_favoravel={pattern_name}")
        elif pattern_name in bullish_patterns or pattern_name in bearish_patterns:
            penalty = 0 if macro_is_strong else 1 if macro_is_moderate else 2
            if penalty > 0:
                score -= penalty
                reasons_against.append(f"padrao_contrario={pattern_name}")

    if exhaustion_detected:
        score += 1
        reasons_for.append("exaustao_detectada")

    if impulsion_detected:
        score += 2
        reasons_for.append("impulsao_detectada")

    if continuity_detected and "continuidade_detectada" not in reasons_for:
        score += 2
        reasons_for.append("continuidade_detectada")

    if opposite_side_weakness:
        score += 1
        reasons_for.append("fraqueza_do_lado_oposto")

    final_score = clamp(score, 0, 10)

    if final_score >= 8:
        label = "forte"
        action = "validar_entrada"
    elif final_score >= 6:
        label = "boa"
        action = "aceitar_com_confirmacao"
    elif final_score >= 4:
        label = "neutra"
        action = "ter_cautela"
    else:
        label = "fraca"
        action = "evitar_entrada"

    return {
        "setup_direction": direction,
        "macro_points": macro_points,
        "macro_is_strong": macro_is_strong,
        "macro_is_moderate": macro_is_moderate,
        "score": final_score,
        "score_label": label,
        "recommended_action": action,
        "reasons_for": reasons_for,
        "reasons_against": reasons_against,
    }


def build_candlestick_intelligence(
    candles: list[Candle],
    index: int,
    setup_direction: str,
    trend_alignment: str,
    price_vs_ema_20: str,
    price_vs_ema_40: str,
    macd_state: str,
    rsi_slope: str,
    market_structure: str,
    adx_value: Decimal | None,
    lookback: int = 5,
) -> dict[str, Any]:
    start_index = max(0, index - lookback + 1)
    window = candles[start_index : index + 1]

    if not window:
        return {
            "phase_1_candle_features": {},
            "phase_2_sequence_patterns": {},
            "phase_3_confirmation": {},
        }

    normalized_direction = normalize_direction(setup_direction)

    force_reading = build_force_reading(window, normalized_direction)
    confirmation = score_confirmation(
        setup_direction=normalized_direction,
        force_reading=force_reading,
        trend_alignment=trend_alignment,
        price_vs_ema_20=price_vs_ema_20,
        price_vs_ema_40=price_vs_ema_40,
        macd_state=macd_state,
        rsi_slope=rsi_slope,
        market_structure=market_structure,
        adx_value=adx_value,
    )

    trigger_candle = force_reading.get("trigger_candle", {})
    prior_candles = force_reading.get("prior_candles", [])

    phase_1 = {
        "objective": "classificar o candle de validação e os candles imediatamente anteriores",
        "setup_direction": normalized_direction,
        "trigger_pattern": trigger_candle.get("pattern"),
        "trigger_strength_class": trigger_candle.get("strength_class"),
        "trigger_close_position": trigger_candle.get("close_position"),
        "trigger_body_ratio": trigger_candle.get("body_ratio"),
        "trigger_upper_wick_ratio": trigger_candle.get("upper_wick_ratio"),
        "trigger_lower_wick_ratio": trigger_candle.get("lower_wick_ratio"),
        "candles": [*prior_candles, trigger_candle],
    }

    phase_2 = {
        "objective": "ler sequência anterior ao cruzamento: exaustão, impulsão, continuidade e padrão clássico",
        "setup_direction": normalized_direction,
        "window_size": force_reading.get("window_size"),
        "sequence_bias": force_reading.get("sequence_bias"),
        "exhaustion_detected": force_reading.get("exhaustion_detected"),
        "impulsion_detected": force_reading.get("impulsion_detected"),
        "continuity_detected": force_reading.get("continuity_detected"),
        "opposite_side_weakness": force_reading.get("opposite_side_weakness"),
        "dominant_pattern": force_reading.get("dominant_pattern"),
        "active_patterns": force_reading.get("active_patterns"),
        "sequence_summary": force_reading.get("sequence_summary"),
    }

    phase_3 = {
        "objective": "gerar score final de confirmação do cruzamento",
        "setup_direction": confirmation.get("setup_direction"),
        "macro_points": confirmation.get("macro_points"),
        "macro_is_strong": confirmation.get("macro_is_strong"),
        "macro_is_moderate": confirmation.get("macro_is_moderate"),
        "confirmation_score": confirmation.get("score"),
        "confirmation_label": confirmation.get("score_label"),
        "recommended_action": confirmation.get("recommended_action"),
        "reasons_for": confirmation.get("reasons_for"),
        "reasons_against": confirmation.get("reasons_against"),
    }

    return {
        "phase_1_candle_features": phase_1,
        "phase_2_sequence_patterns": phase_2,
        "phase_3_confirmation": phase_3,
    }